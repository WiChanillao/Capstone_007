"""Pruebas unitarias de la app FastAPI (main.py) para cobertura global del backend.

Las escrituras en MySQL se simulan con monkeypatch: las pruebas no modifican
las 48 filas reales de la base ecoscan.
"""
import io
from collections import defaultdict, deque

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

import main

client = TestClient(main.app)


def _imagen(nitida: bool) -> bytes:
    """Devuelve PNG en bytes: plano (borrosa) o con ruido (nítida)."""
    if nitida:
        rng = np.random.default_rng(7)
        arr = rng.integers(0, 256, size=(224, 224, 3), dtype=np.uint8)
    else:
        arr = np.full((224, 224, 3), 128, dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


class _Caja:
    def __init__(self, clase, confianza):
        self.cls = [clase]
        self.conf = [confianza]


class _ModeloFalso:
    """Modelo determinista para probar el flujo sin depender de la inferencia real."""
    names = {0: "Aluminio", 1: "Carton", 2: "Plastico"}

    def __init__(self, cajas):
        self.cajas = cajas

    def __call__(self, imagen):
        return [type("Resultado", (), {"boxes": self.cajas})()]


def _sin_escritura(monkeypatch):
    """Aísla las pruebas de la BD real."""
    monkeypatch.setattr(main, "ejecutar", lambda *a, **k: None)
    monkeypatch.setattr(main, "guardar_inferencia", lambda *a, **k: None)
    # /predict inserta en escaneos usando SessionLocal directamente: se anula
    # para que ninguna prueba altere las 48 filas reales de MySQL.
    monkeypatch.setattr(main, "SessionLocal", None)


def test_raiz_expone_modelo_y_estado():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["modelo_activo"] == main.MODEL_PATH


def test_version_expone_sha256_y_dataset():
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert body["modelo"] == main.MODEL_PATH
    assert len(body["sha256"]) == 64
    assert body["dataset_version"] == "ecoscan-3clases-v1"
    assert body["clases"] == ["Aluminio", "Carton", "Plastico"]


def test_health_informa_conexion_mysql(monkeypatch):
    """Simula MySQL: en CI no hay base de datos y /health debe seguir siendo 'ok'
    cuando la conexión está disponible. Comprobar el estado real de la BD
    corresponde a las pruebas de integración con Docker."""

    class _Consulta:
        def count(self):
            return 48

    class _Sesion:
        def query(self, *_args, **_kwargs):
            return _Consulta()

        def close(self):
            pass

    monkeypatch.setattr(main, "db_activa", True)
    monkeypatch.setattr(main, "SessionLocal", lambda: _Sesion())

    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["mysql_conectado"] is True
    assert body["escaneos_registrados"] >= 48


def test_health_reporta_degraded_sin_mysql(monkeypatch):
    """Sin MySQL el servicio sigue respondiendo 200, pero marca 'degraded'."""
    monkeypatch.setattr(main, "db_activa", False)
    monkeypatch.setattr(main, "SessionLocal", None)

    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "degraded"
    assert body["mysql_conectado"] is False


def test_cabeceras_de_seguridad_en_todas_las_respuestas():
    r = client.get("/health")
    esperadas = (
        "x-content-type-options",
        "x-frame-options",
        "referrer-policy",
        "strict-transport-security",
        "permissions-policy",
        "content-security-policy",
    )
    for cabecera in esperadas:
        assert cabecera in r.headers


def test_origenes_se_leen_de_variable_incluido_un_tunel(monkeypatch):
    """La URL del túnel se configura por entorno; nunca con comodín."""
    monkeypatch.setenv(
        "CORS_ORIGINS", "https://demo.trycloudflare.com, http://localhost:5173"
    )
    origenes = main.origenes_permitidos()
    assert origenes == ["https://demo.trycloudflare.com", "http://localhost:5173"]
    assert "*" not in origenes


def test_cors_acepta_solo_origen_configurado():
    origen = main.ORIGENES_PERMITIDOS[0]
    r = client.get("/health", headers={"Origin": origen})
    assert r.headers.get("access-control-allow-origin") == origen

    r = client.get(
        "/health", headers={"Origin": "https://no-configurado.trycloudflare.com"}
    )
    assert r.status_code == 200
    assert "access-control-allow-origin" not in r.headers


def test_csp_sin_comodin_y_con_origenes_de_entorno():
    r = client.get("/health")
    connect = r.headers["content-security-policy"].split("connect-src ")[1].split(";")[0]
    assert connect.startswith("'self'")
    assert "*" not in connect
    for origen in main.ORIGENES_PERMITIDOS:
        assert origen in connect


def test_ip_real_confia_en_cabecera_solo_desde_la_red_de_nginx():
    """Desde la red de nginx se usa X-Real-IP; desde fuera se ignora."""
    assert main.ip_real("172.18.0.4", {"x-real-ip": "10.0.0.7"}) == "10.0.0.7"
    assert main.ip_real(
        "172.18.0.4", {"x-forwarded-for": "10.0.0.8, 172.18.0.4"}
    ) == "10.0.0.8"
    # Origen externo: la cabecera falsificada no altera la clave.
    assert main.ip_real("203.0.113.9", {"x-real-ip": "10.0.0.7"}) == "203.0.113.9"
    # Cabecera mal formada: se conserva la IP del socket.
    assert main.ip_real("172.18.0.4", {"x-real-ip": "no-es-una-ip"}) == "172.18.0.4"


def test_rate_limit_no_comparte_cuota_entre_ips_reales(monkeypatch):
    """Dos visitantes distintos detrás del mismo proxy tienen cuota independiente."""
    monkeypatch.setattr(main, "_solicitudes", defaultdict(deque))
    monkeypatch.setattr(main, "_LIMIT_MINUTO", 2)
    monkeypatch.setattr(
        main, "ip_real", lambda cliente, cabeceras: cabeceras.get("x-real-ip", cliente)
    )
    imagen = _imagen(nitida=True)
    cuota_agotada = None
    for _ in range(2):
        cuota_agotada = client.post(
            "/predict", files={"file": ("a.png", imagen, "image/png")},
            headers={"x-real-ip": "10.0.0.7"},
        )
    assert cuota_agotada.status_code == 200
    rechazada = client.post(
        "/predict", files={"file": ("a.png", imagen, "image/png")},
        headers={"x-real-ip": "10.0.0.7"},
    )
    assert rechazada.status_code == 429
    assert rechazada.json()["detail"]["codigo"] == "DEMASIADAS_SOLICITUDES"
    # La otra IP conserva su cuota a pesar de venir por el mismo proxy.
    otra = client.post(
        "/predict", files={"file": ("b.png", imagen, "image/png")},
        headers={"x-real-ip": "10.0.0.8"},
    )
    assert otra.status_code == 200


def test_predict_rechaza_archivo_que_no_es_imagen(monkeypatch):
    _sin_escritura(monkeypatch)
    r = client.post("/predict", files={"file": ("mal.txt", b"no imagen", "text/plain")})
    assert r.status_code == 400
    detalle = r.json()["detail"]
    assert detalle["codigo"] == "FORMATO_NO_VALIDO"
    assert detalle["campo"] == "file"


def test_deteccion_rechazada_guarda_material_compatible_con_constraint(monkeypatch):
    """CONFIANZA_BAJA conserva id_material: ck_inf_ok_material ya lo permite."""
    guardados = []
    monkeypatch.setattr(main, "db_activa", True)
    monkeypatch.setattr(main, "ejecutar", lambda *a, **k: None)
    monkeypatch.setattr(main, "guardar_inferencia", lambda dato: guardados.append(dato))
    monkeypatch.setattr(main, "model", _ModeloFalso([_Caja(1, 0.27)]))
    r = client.post(
        "/predict",
        data={"id_sesion": "sesion-rechazada"},
        files={"file": ("foto.png", _imagen(nitida=True), "image/png")},
    )
    assert r.status_code == 200
    assert any(g.resultado == "CONFIANZA_BAJA" and g.id_material == 1 for g in guardados)


def test_predict_rechaza_foto_borrosa(monkeypatch):
    _sin_escritura(monkeypatch)
    r = client.post(
        "/predict",
        files={"file": ("borrosa.png", _imagen(nitida=False), "image/png")},
    )
    assert r.status_code == 400
    detalle = r.json()["detail"]
    assert detalle["codigo"] == "IMAGEN_BORROSA"
    assert detalle["campo"] == "file"


def test_predict_devuelve_estructura_con_imagen_nitida(monkeypatch):
    _sin_escritura(monkeypatch)
    r = client.post(
        "/predict",
        data={"id_sesion": "sesion-de-prueba-unitaria"},
        files={"file": ("nitida.png", _imagen(nitida=True), "image/png")},
    )
    assert r.status_code == 200
    body = r.json()
    for clave in ("detecciones", "detecciones_rechazadas", "conteo_materiales",
                  "modelo_usado", "id_sesion", "umbral_confianza", "latencia_ms"):
        assert clave in body
    assert body["id_sesion"] == "sesion-de-prueba-unitaria"
    assert body["umbral_confianza"] == main.UMBRAL_CONFIANZA


def test_predict_rechaza_archivo_corrupto(monkeypatch):
    """MIME válido pero contenido corrupto: verify() debe dar 400, no 500."""
    _sin_escritura(monkeypatch)
    r = client.post(
        "/predict",
        files={"file": ("corrupto.png", b"contenido que no es una imagen", "image/png")},
    )
    assert r.status_code == 400
    detalle = r.json()["detail"]
    assert detalle["codigo"] == "ARCHIVO_CORRUPTO"
    assert detalle["campo"] == "file"


def test_predict_rechaza_archivo_mayor_a_10mb(monkeypatch):
    """La cabecera Content-Length y la lectura limitada deben dar 413."""
    _sin_escritura(monkeypatch)
    datos = b"x" * (main.MAX_TAMANO_ARCHIVO + 1)
    r = client.post(
        "/predict",
        files={"file": ("grande.png", datos, "image/png")},
    )
    assert r.status_code == 413
    detalle = r.json()["detail"]
    assert detalle["codigo"] == "ARCHIVO_MUY_PESADO"
    assert detalle["campo"] == "file"


@pytest.mark.parametrize("sesion_invalida", ["sesion con espacio", "mala!", "x" * 65])
def test_predict_rechaza_id_sesion_invalido(monkeypatch, sesion_invalida):
    """Caracteres no permitidos y longitud > 64 se rechazan con 422."""
    _sin_escritura(monkeypatch)
    r = client.post(
        "/predict",
        data={"id_sesion": sesion_invalida},
        files={"file": ("nitida.png", _imagen(nitida=True), "image/png")},
    )
    assert r.status_code == 422
    assert r.json()["detail"]["codigo"] == "ID_SESION_INVALIDO"


def test_predict_rechaza_mime_no_permitido(monkeypatch):
    """Un PDF con MIME application/pdf se rechaza con 400 antes de abrirlo."""
    _sin_escritura(monkeypatch)
    r = client.post(
        "/predict",
        files={"file": ("documento.pdf", b"%PDF-1.7 contenido de prueba", "application/pdf")},
    )
    assert r.status_code == 400
    detalle = r.json()["detail"]
    assert detalle["codigo"] == "FORMATO_NO_VALIDO"
    assert detalle["campo"] == "file"


def test_predict_acepta_octet_stream_si_el_contenido_es_imagen(monkeypatch):
    """Fotos reales de celular pueden llegar como application/octet-stream."""
    _sin_escritura(monkeypatch)
    r = client.post(
        "/predict",
        data={"id_sesion": "sesion-octet-stream"},
        files={"file": ("foto_celular.jpg", _imagen(nitida=True), "application/octet-stream")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["id_sesion"] == "sesion-octet-stream"
    for clave in ("detecciones", "detecciones_rechazadas", "conteo_materiales"):
        assert clave in body


def test_predict_rechaza_octet_stream_si_el_contenido_no_es_imagen(monkeypatch):
    """La etiqueta octet-stream no abre la puerta a archivos que no son imágenes."""
    _sin_escritura(monkeypatch)
    r = client.post(
        "/predict",
        files={"file": ("falso.jpg", b"esto no es una imagen", "application/octet-stream")},
    )
    assert r.status_code == 400
    detalle = r.json()["detail"]
    assert detalle["codigo"] == "ARCHIVO_CORRUPTO"
    assert detalle["campo"] == "file"


def test_predict_rechaza_dimensiones_excedidas(monkeypatch):
    """Una imagen por encima del limite de 8000x8000 se rechaza con 400."""
    _sin_escritura(monkeypatch)
    assert main.MAX_DIMENSION_IMAGEN == 8000
    # Se baja el limite durante la prueba para no asignar ~192 MB: la imagen
    # de 224x224 excede el limite reducido y recorre el mismo codigo de error.
    monkeypatch.setattr(main, "MAX_DIMENSION_IMAGEN", 100)
    r = client.post(
        "/predict",
        files={"file": ("gran_de.png", _imagen(nitida=True), "image/png")},
    )
    assert r.status_code == 400
    assert r.json()["detail"]["codigo"] == "DIMENSIONES_EXCEDIDAS"
