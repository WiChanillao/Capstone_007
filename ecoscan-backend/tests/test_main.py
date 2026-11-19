"""Pruebas unitarias de la app FastAPI (main.py) para cobertura global del backend.

Las escrituras en MySQL se simulan con monkeypatch: las pruebas no modifican
las 48 filas reales de la base ecoscan.
"""
import io

import numpy as np
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


def test_health_informa_conexion_mysql():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["mysql_conectado"] is True
    assert body["escaneos_registrados"] >= 48


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


def test_predict_rechaza_archivo_que_no_es_imagen(monkeypatch):
    _sin_escritura(monkeypatch)
    r = client.post("/predict", files={"file": ("mal.txt", b"no imagen", "text/plain")})
    assert r.status_code == 400
    assert "no es una imagen válida" in r.json()["detail"]


def test_predict_rechaza_foto_borrosa(monkeypatch):
    _sin_escritura(monkeypatch)
    r = client.post(
        "/predict",
        files={"file": ("borrosa.png", _imagen(nitida=False), "image/png")},
    )
    assert r.status_code == 400
    assert r.json()["detail"]["codigo"] == "BORROSA"


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
