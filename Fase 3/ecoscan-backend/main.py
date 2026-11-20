import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
# Permite que el .env de la carpeta Fase 3 funcione aunque se lance el backend
# desde VS Code o desde otra carpeta (REC-64: secretos fuera del código).
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env', override=False)

import io
import json
import re
import time
import ipaddress
import hashlib
import datetime
import logging
import threading
from collections import defaultdict, deque
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image, ImageOps
import cv2
import numpy as np

# Intentar registrar soporte nativo para archivos .HEIC (iPhone) si la librería está disponible
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

# Importaciones para Base de Datos MySQL
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="EcoLearn Chile API")

# REC-106: límite simple por IP para /predict (30 peticiones por minuto).
_LIMIT_MINUTO = int(os.getenv("LIMITE_PREDICT_MINUTO", "30"))
# Límite de subida: 10 MB. Controlado por Content-Length y por lectura real.
MAX_TAMANO_ARCHIVO = 10 * 1024 * 1024
# Solo formatos de imagen declarados explícitamente; se valida el MIME y el
# contenido real (verify), además del tamaño máximo en píxeles.
MIME_IMAGENES_PERMITIDAS = {
    "image/jpeg", "image/jpg", "image/png", "image/webp", "image/heic", "image/heif",
}
MAX_DIMENSION_IMAGEN = 8000
MENSAJE_IMAGEN_INVALIDA = (
    "El archivo enviado no es una imagen válida. Sube una foto JPG, PNG, WEBP, HEIC o HEIF."
)
_solicitudes = defaultdict(deque)
_bloqueo = threading.Lock()
# Solo se confía en X-Real-IP / X-Forwarded-For cuando la petición entra desde
# la red de nginx. Se excluye el gateway (x.y.0.1): es la IP de las conexiones
# reenviadas por el puerto publicado, no de nginx, y aceptarla permitiría
# falsificar la cuota del rate limit desde fuera del contenedor.
_RED_PROXY_CONFIABLE = os.getenv("RED_PROXY_CONFIABLE", "172.18.0.0/16")
try:
    _REDES_PROXY = [
        ipaddress.ip_network(red.strip(), strict=False)
        for red in _RED_PROXY_CONFIABLE.split(",") if red.strip()
    ]
except ValueError:
    _REDES_PROXY = []

# Logging estructurado simple (REC-71): una línea JSON por evento relevante.
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ecoscan")


def log_evento(evento, **campos):
    logger.info(json.dumps({"evento": evento, **campos}, ensure_ascii=False, default=str))


def error_detail(codigo, mensaje, campo):
    """Contrato único de error para toda respuesta 4xx de la API."""
    return {"codigo": codigo, "mensaje": mensaje, "campo": campo}


def registrar_rechazo(codigo, campo, mime=None, bytes_archivo=None,
                      ancho=None, alto=None, **extra):
    """Registra cada rechazo sin guardar la imagen (solo metadata)."""
    log_evento("rechazo", codigo=codigo, campo=campo, mime=mime,
               bytes=bytes_archivo, ancho=ancho, alto=alto, **extra)


def es_proxy_confiable(ip_cliente):
    """Nginx sí; el gateway de la red (primera IP usable) no."""
    for red in _REDES_PROXY:
        if ip_cliente in red and ip_cliente != red.network_address + 1:
            return True
    return False


def ip_real(cliente, cabeceras):
    """IP del visitante: solo confía en las cabeceras si viene de la red de nginx."""
    try:
        ip_cliente = ipaddress.ip_address(cliente)
    except ValueError:
        return cliente
    if not es_proxy_confiable(ip_cliente):
        return cliente
    candidata = (cabeceras.get("x-real-ip") or "").strip()
    if not candidata:
        candidata = (cabeceras.get("x-forwarded-for") or "").split(",")[0].strip()
    try:
        return str(ipaddress.ip_address(candidata))
    except ValueError:
        return cliente


def mime_declarado(objeto):
    contenido = getattr(objeto, "content_type", None)
    if contenido is None:
        cabeceras = getattr(objeto, "headers", None)
        contenido = cabeceras.get("content-type") if cabeceras is not None else None
    return (contenido or "").split(";")[0].strip().lower() or None


def calcular_nitidez(imagen):
    """Varianza del Laplaciano en grayscale, reescalado a 640 px de lado largo.

    Normalizar evita que una foto de 12 MP parezca más nítida que la misma
    foto de 2 MP solo por tener más píxeles.
    """
    if max(imagen.size) > LADO_NITIDEZ:
        escala = LADO_NITIDEZ / max(imagen.size)
        imagen = imagen.resize(
            (max(1, int(imagen.width * escala)), max(1, int(imagen.height * escala)))
        )
    gris = cv2.cvtColor(np.array(imagen), cv2.COLOR_RGB2GRAY)
    return round(float(cv2.Laplacian(gris, cv2.CV_64F).var()), 2)


@app.middleware("http")
async def seguridad_y_limite(request: Request, call_next):
    cliente = request.client.host if request.client else "desconocida"
    ip = ip_real(cliente, request.headers)
    if request.url.path == "/predict":
        ahora = time.time()
        with _bloqueo:
            cola = _solicitudes[ip]
            while cola and ahora - cola[0] > 60:
                cola.popleft()
            if len(cola) >= _LIMIT_MINUTO:
                registrar_rechazo("DEMASIADAS_SOLICITUDES", campo="ip", ip=ip)
                return JSONResponse(
                    status_code=429,
                    content={"detail": error_detail(
                        "DEMASIADAS_SOLICITUDES",
                        "Demasiados análisis en un minuto. Espera un momento y vuelve a intentarlo.",
                        "ip",
                    )},
                )
            cola.append(ahora)
    respuesta = await call_next(request)
    # REC-107: cabeceras de seguridad en todas las respuestas.
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    respuesta.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    respuesta.headers["Permissions-Policy"] = "camera=(self), geolocation=(self), microphone=()"
    if request.url.path in ("/docs", "/redoc") or request.url.path.startswith("/docs/"):
        # Swagger UI/ReDoc de FastAPI cargan CSS y JS desde un CDN y usan un
        # script inline. Se relaja la CSP solo en la documentacion; el resto
        # de la API conserva la politica estricta de REC-107.
        respuesta.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: blob: https://fastapi.tiangolo.com; "
            "connect-src 'self' " + " ".join(ORIGENES_PERMITIDOS) + "; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "object-src 'none'"
        )
    else:
        respuesta.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data: blob:; "
            "connect-src 'self' " + " ".join(ORIGENES_PERMITIDOS) + "; "
            "style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'"
        )
    return respuesta


@app.exception_handler(RequestValidationError)
async def validacion_entrada(request: Request, exc: RequestValidationError):
    """FastAPI devuelve 422 con un array; lo convertimos al contrato del proyecto."""
    registrar_rechazo("FORMATO_NO_VALIDO", campo="file", mime=mime_declarado(request))
    return JSONResponse(
        status_code=422,
        content={"detail": error_detail(
            "FORMATO_NO_VALIDO", "Falta el archivo 'file' en la petición.", "file")},
    )


# Rutas /db/... alimentadas desde MySQL ecoscan (REC-42, REC-47, REC-51)
from rutas_db import router as db_router, guardar_resultado_escaneo, Inferencia
app.include_router(db_router)

# Orígenes permitidos: siempre por variable de entorno, nunca comodín.
# Para compartir la app por túnel se añade esa URL a CORS_ORIGINS en .env.
def origenes_permitidos():
    return [
        o.strip() for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",") if o.strip()
    ]


ORIGENES_PERMITIDOS = origenes_permitidos()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# ----------------------------------------------------
# 🗄️ CONFIGURACIÓN DE BASE DE DATOS MYSQL
# ----------------------------------------------------
# Ajusta el usuario, contraseña y nombre de BD según la configuración de tu compañero:
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
if not MYSQL_PASSWORD:
    raise RuntimeError("Define MYSQL_PASSWORD en .env")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "ecoscan")

MYSQL_URL = URL.create(
    "mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=int(MYSQL_PORT),
    database=MYSQL_DB,
)

db_activa = False
SessionLocal = None

try:
    engine = create_engine(MYSQL_URL, pool_pre_ping=True, connect_args={"connect_timeout": 3})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Tabla para almacenar el historial de escaneos
    class HistorialEscaneo(Base):
        __tablename__ = "escaneos"
        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        fecha = Column(DateTime, default=datetime.datetime.now)
        materiales_detectados = Column(String(255))
        modelo_usado = Column(String(50))
        total_objetos = Column(Integer)
        # Nuevos campos para impacto real por sesión y conteo por clase de YOLO
        id_sesion = Column(String(36))
        cant_carton = Column(Integer, default=0)
        cant_aluminio = Column(Integer, default=0)
        cant_plastico = Column(Integer, default=0)

    # Crear la tabla en MySQL si no existe
    Base.metadata.create_all(bind=engine)

    # Migración segura: agrega columnas nuevas sin borrar los 48 escaneos existentes.
    try:
        with engine.begin() as conn:
            columnas = {f[0] for f in conn.execute(text("SHOW COLUMNS FROM escaneos")).fetchall()}
            if "id_sesion" not in columnas:
                conn.execute(text("ALTER TABLE escaneos ADD COLUMN id_sesion VARCHAR(36) NULL"))
            if "cant_carton" not in columnas:
                conn.execute(text("ALTER TABLE escaneos ADD COLUMN cant_carton INT NOT NULL DEFAULT 0"))
            if "cant_aluminio" not in columnas:
                conn.execute(text("ALTER TABLE escaneos ADD COLUMN cant_aluminio INT NOT NULL DEFAULT 0"))
            if "cant_plastico" not in columnas:
                conn.execute(text("ALTER TABLE escaneos ADD COLUMN cant_plastico INT NOT NULL DEFAULT 0"))
    except Exception as err:
        print(f"⚠️ Aviso migración de escaneos: {err}")

    with engine.begin() as conn:
        columnas = {f[0] for f in conn.execute(text("SHOW COLUMNS FROM escaneos")).fetchall()}
        if "id_solicitud" not in columnas:
            conn.execute(text(
                "ALTER TABLE escaneos ADD COLUMN id_solicitud CHAR(32) NULL, "
                "ADD UNIQUE KEY uq_escaneos_solicitud (id_sesion, id_solicitud)"
            ))

    # Migración para ordenar puntos por cercanía (REC-127).
    try:
        with engine.begin() as conn:
            columnas = {f[0] for f in conn.execute(text("SHOW COLUMNS FROM punto_limpio")).fetchall()}
            if "lat" not in columnas:
                conn.execute(text("ALTER TABLE punto_limpio ADD COLUMN lat DECIMAL(10,7) NULL"))
            if "lon" not in columnas:
                conn.execute(text("ALTER TABLE punto_limpio ADD COLUMN lon DECIMAL(10,7) NULL"))
            coords = {
                1: (-33.5170, -70.7350), 2: (-33.4980, -70.7680), 3: (-33.4330, -70.6410),
                4: (-33.4260, -70.6170), 5: (-33.4040, -70.5750), 6: (-33.5870, -70.5910),
                7: (-33.5170, -70.5980), 8: (-33.4580, -70.6130), 9: (-33.6010, -70.6990),
                10: (-33.4340, -70.5450),
            }
            for id_punto, (lat, lon) in coords.items():
                conn.execute(text("UPDATE punto_limpio SET lat=:lat, lon=:lon WHERE id_punto=:id_punto AND (lat IS NULL OR lon IS NULL)"),
                             {"lat": lat, "lon": lon, "id_punto": id_punto})
    except Exception as err:
        print(f"⚠️ Aviso migración de puntos: {err}")

    # Permitir registrar también análisis sin detección (REC-43).
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE inferencia DROP CHECK ck_inf_resultado"))
            conn.execute(text(
                "ALTER TABLE inferencia ADD CONSTRAINT ck_inf_resultado "
                "CHECK (resultado IN ('OK','BORROSA','CONFIANZA_BAJA','SIN_DETECCION'))"
            ))
    except Exception as err:
        print(f"⚠️ Aviso migración de inferencia: {err}")

    # ck_inf_ok_material exigía id_material NULL para todo resultado distinto de
    # OK, por lo que fallaba al guardar detecciones rechazadas por confianza.
    # Ahora solo OK exige material; CONFIANZA_BAJA conserva la clase detectada.
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE inferencia DROP CHECK ck_inf_ok_material"))
            conn.execute(text(
                "ALTER TABLE inferencia ADD CONSTRAINT ck_inf_ok_material "
                "CHECK (resultado <> 'OK' OR id_material IS NOT NULL)"
            ))
    except Exception as err:
        print(f"⚠️ Aviso migración ck_inf_ok_material: {err}")

    db_activa = True
    print("🟢 Conexión exitosa a MySQL (Base de datos EcoScan activa).")
except Exception as e:
    print(f"⚠️ Aviso MySQL: No se pudo conectar a la BD ({e}). El backend continuará funcionando.")

# ----------------------------------------------------
# 🤖 SELECCIÓN DEL MODELO YOLO
# ----------------------------------------------------
# Los pesos de entrega son locales. Un archivo faltante debe detener el arranque.
MODEL_PATH = os.getenv("MODEL_PATH", "best.pt")
if not os.path.isfile(MODEL_PATH):
    raise RuntimeError(f"No se encontró el archivo local de pesos: {MODEL_PATH}")
UMBRAL_CONFIANZA = float(os.getenv("UMBRAL_CONFIANZA", "0.5"))
# Referencia orientativa (NO validación con el split de test): 26 fotos reales
# disponibles reescaladas a 640 px dan min 128.39, p05 324.68, mediana 2527.54;
# ninguna contiene un objeto liso. El umbral 50 solo se evalúa cuando NO hay
# detecciones: con detecciones se responde 200 y se añade aviso "baja_nitidez".
# El caso liso "IDEAL" (20.6) se reprodujo aparte y no está en esas 26 fotos.
LADO_NITIDEZ = 640
UMBRAL_NITIDEZ = float(os.getenv("UMBRAL_NITIDEZ", "50"))
print(f"🟢 Cargando modelo de visión artificial desde: {MODEL_PATH}")
model = YOLO(MODEL_PATH)

@app.get("/")
def read_root():
    return {
        "status": "ok", 
        "modelo_activo": MODEL_PATH,
        "mysql_conectado": db_activa
    }

@app.get("/version")
def version():
    """Versión del modelo y del dataset usados (REC-116)."""
    sha = None
    if os.path.exists(MODEL_PATH):
        h = hashlib.sha256()
        with open(MODEL_PATH, "rb") as f:
            for bloque in iter(lambda: f.read(1024 * 1024), b""):
                h.update(bloque)
        sha = h.hexdigest()
    return {
        "modelo": MODEL_PATH,
        "sha256": sha,
        "dataset_version": os.getenv("DATASET_VERSION", "ecoscan-3clases-v1"),
        "clases": ["Aluminio", "Carton", "Plastico"],
    }


@app.get("/health")
def health():
    """Estado real del servicio y de la conexión MySQL (evita los 404 en consola)."""
    estado = {
        "status": "ok" if db_activa else "degraded",
        "mysql_conectado": db_activa,
        "modelo_activo": MODEL_PATH,
    }
    if db_activa and SessionLocal:
        try:
            db = SessionLocal()
            try:
                estado["escaneos_registrados"] = db.query(HistorialEscaneo).count()
            finally:
                db.close()
        except Exception as err:
            estado["status"] = "degraded"
            estado["mysql_conectado"] = False
            log_evento("error_health_mysql", tipo=type(err).__name__)
    return estado

@app.get("/v1/models")
def modelos_disponibles():
    """Endpoint compatible con OpenAI: evita el 404 de clientes que consultan /v1/models."""
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_PATH,
                "object": "model",
                "created": int(os.path.getmtime(MODEL_PATH)) if os.path.exists(MODEL_PATH) else 0,
                "owned_by": "ecolearn-chile",
            }
        ],
    }


@app.get("/v1/models/{modelo_id}")
def detalle_modelo(modelo_id: str):
    """Responde cualquier id de modelo con el modelo activo, sin 404 en consola."""
    return {
        "id": modelo_id or MODEL_PATH,
        "object": "model",
        "created": int(os.path.getmtime(MODEL_PATH)) if os.path.exists(MODEL_PATH) else 0,
        "owned_by": "ecolearn-chile",
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    id_sesion: str = Form(None),
    id_solicitud: str | None = Form(None),
):
    inicio = time.perf_counter()
    sesion = (id_sesion or "").strip() or None
    if sesion is not None and not re.fullmatch(r"[A-Za-z0-9_-]{1,36}", sesion):
        registrar_rechazo("ID_SESION_INVALIDO", campo="id_sesion")
        raise HTTPException(
            status_code=422,
            detail=error_detail(
                "ID_SESION_INVALIDO",
                "id_sesion debe tener entre 1 y 36 caracteres: letras, números, guion o guion bajo.",
                "id_sesion",
            ),
        )
    if id_solicitud is not None and (
        not sesion or not re.fullmatch(r"[0-9a-f]{32}", id_solicitud)
    ):
        raise HTTPException(
            status_code=422,
            detail=error_detail(
                "ID_SOLICITUD_INVALIDO", "La solicitud necesita una sesión y un identificador válido.",
                "id_solicitud",
            ),
        )
    # Rechazar archivos > 10 MB antes de cargarlos en memoria. Se revisa la
    # cabecera Content-Length del parte y además se limita la lectura real,
    # porque la cabecera es declarada por el cliente y puede faltar o mentir.
    try:
        longitud = int((file.headers or {}).get("content-length") or 0)
    except (TypeError, ValueError):
        longitud = 0
    if longitud > MAX_TAMANO_ARCHIVO:
        registrar_rechazo("ARCHIVO_MUY_PESADO", campo="file", mime=mime_declarado(file),
                          bytes_archivo=longitud)
        raise HTTPException(
            status_code=413,
            detail=error_detail("ARCHIVO_MUY_PESADO",
                                "La imagen supera el límite de 10 MB.", "file"),
        )

    contents = await file.read(MAX_TAMANO_ARCHIVO + 1)
    if len(contents) > MAX_TAMANO_ARCHIVO:
        registrar_rechazo("ARCHIVO_MUY_PESADO", campo="file", mime=mime_declarado(file),
                          bytes_archivo=len(contents))
        raise HTTPException(
            status_code=413,
            detail=error_detail("ARCHIVO_MUY_PESADO",
                                "La imagen supera el límite de 10 MB.", "file"),
        )

    # Whitelist de MIME: varios navegadores móviles etiquetan las fotos reales
    # como application/octet-stream. En ese caso no se confía en la etiqueta:
    # Image.open().verify() más abajo decide si el contenido es una imagen.
    mime = mime_declarado(file) or ""
    if mime not in MIME_IMAGENES_PERMITIDAS and mime != "application/octet-stream":
        registrar_rechazo("FORMATO_NO_VALIDO", campo="file", mime=mime,
                          bytes_archivo=len(contents))
        raise HTTPException(
            status_code=400,
            detail=error_detail("FORMATO_NO_VALIDO", MENSAJE_IMAGEN_INVALIDA, "file"),
        )

    # Validar que el archivo sea realmente una imagen (REC-54: 400 controlado, no 500).
    # verify() detecta contenido corrupto aunque el MIME declare lo contrario.
    try:
        imagen_cargada = Image.open(io.BytesIO(contents))
        imagen_cargada.verify()
    except Exception as err:
        registrar_rechazo("ARCHIVO_CORRUPTO", campo="file", mime=mime,
                          bytes_archivo=len(contents), error=str(err))
        raise HTTPException(
            status_code=400,
            detail=error_detail("ARCHIVO_CORRUPTO",
                                "El archivo está corrupto o no contiene una imagen válida.", "file"),
        )

    # Abrir la imagen ajustando la rotación EXIF (Corrige fotos giradas de iPhone)
    image = Image.open(io.BytesIO(contents))
    image = ImageOps.exif_transpose(image).convert("RGB")
    if image.width > MAX_DIMENSION_IMAGEN or image.height > MAX_DIMENSION_IMAGEN:
        registrar_rechazo("DIMENSIONES_EXCEDIDAS", campo="file", mime=mime,
                          bytes_archivo=len(contents), ancho=image.width, alto=image.height)
        raise HTTPException(
            status_code=400,
            detail=error_detail("DIMENSIONES_EXCEDIDAS",
                                "La imagen supera el tamaño máximo de 8000x8000 píxeles.", "file"),
        )

    # REC-104: medir nitidez normalizada, pero NO rechazar antes de inferir.
    # Si el modelo detecta el objeto, la foto es válida aunque tenga poca textura.
    nitidez = calcular_nitidez(image)

    # Inferencia con YOLO
    results = model(image)
    latencia_ms = int((time.perf_counter() - inicio) * 1000)
    
    detecciones = []
    detecciones_rechazadas = []
    clases_unicas = set()
    conteo_clases = {"Aluminio": 0, "Carton": 0, "Plastico": 0}
    id_material_por_clase = {"Carton": 1, "Plastico": 2, "Aluminio": 3}

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])

            item = {"clase": class_name, "confianza": round(confidence, 2)}
            # REC-103: umbral mínimo de confianza para aceptar una detección.
            if confidence < UMBRAL_CONFIANZA:
                detecciones_rechazadas.append(item)
                continue

            detecciones.append(item)
            clases_unicas.add(class_name)
            conteo_clases[class_name] = conteo_clases.get(class_name, 0) + 1

    # Solo se rechaza por nitidez si el modelo NO encontró nada. Una caja lisa
    # con logo puede tener Laplaciano bajo y seguir siendo una foto válida.
    if not detecciones and nitidez < UMBRAL_NITIDEZ:
        registrar_rechazo("IMAGEN_BORROSA", campo="file", mime=mime,
                          bytes_archivo=len(contents), ancho=image.width,
                          alto=image.height, nitidez=nitidez)
        if db_activa:
            try:
                guardar_resultado_escaneo(sesion, [Inferencia(
                    id_sesion=sesion,
                    resultado="BORROSA",
                    latencia_ms=int((time.perf_counter() - inicio) * 1000),
                )])
            except Exception as err:
                log_evento("error_guardar_inferencia", etapa="IMAGEN_BORROSA", tipo=type(err).__name__)
        raise HTTPException(
            status_code=400,
            detail=error_detail("IMAGEN_BORROSA",
                                "No se pudo identificar el residuo y la foto tiene poca definición. Acércate y mejora la luz.",
                                "file"),
        )

    escaneo_guardado = False
    if db_activa:
        inferencias = [
            Inferencia(
                id_sesion=sesion,
                id_material=id_material_por_clase.get(det["clase"]),
                resultado=resultado,
                confianza=det["confianza"],
                latencia_ms=latencia_ms,
            )
            for resultado, grupo in (
                ("OK", detecciones), ("CONFIANZA_BAJA", detecciones_rechazadas)
            )
            for det in grupo
        ]
        if not inferencias:
            inferencias.append(Inferencia(
                id_sesion=sesion, resultado="SIN_DETECCION", latencia_ms=latencia_ms
            ))
        escaneo = None
        if detecciones:
            escaneo = (
                ", ".join(sorted(clases_unicas)), MODEL_PATH, len(detecciones), sesion,
                conteo_clases.get("Carton", 0), conteo_clases.get("Aluminio", 0),
                conteo_clases.get("Plastico", 0), id_solicitud,
            )
        try:
            guardar_resultado_escaneo(sesion, inferencias, escaneo)
            escaneo_guardado = escaneo is not None
        except Exception as err:
            log_evento("error_persistencia_escaneo", tipo=type(err).__name__)

    log_evento("prediccion", sesion=id_sesion, aceptadas=len(detecciones),
               rechazadas=len(detecciones_rechazadas), latencia_ms=latencia_ms)

    return {
        "escaneo_guardado": escaneo_guardado,
        "detecciones": detecciones,
        "detecciones_rechazadas": detecciones_rechazadas,
        "modelo_usado": MODEL_PATH,
        "id_sesion": id_sesion,
        "conteo_materiales": conteo_clases,
        "umbral_confianza": UMBRAL_CONFIANZA,
        "latencia_ms": latencia_ms,
        "calidad_imagen": {
            "nitidez": nitidez,
            "aviso": "baja_nitidez" if nitidez < UMBRAL_NITIDEZ else None,
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)