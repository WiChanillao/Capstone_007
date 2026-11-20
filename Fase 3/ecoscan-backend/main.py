import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
# Permite que el .env de la carpeta Fase 3 funcione aunque se lance el backend
# desde VS Code o desde otra carpeta (REC-64: secretos fuera del código).
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env', override=False)

import io
import json
import time
import hashlib
import datetime
import logging
import threading
from collections import defaultdict, deque
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
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


@app.middleware("http")
async def seguridad_y_limite(request: Request, call_next):
    ip = request.client.host if request.client else "desconocida"
    if request.url.path == "/predict":
        ahora = time.time()
        with _bloqueo:
            cola = _solicitudes[ip]
            while cola and ahora - cola[0] > 60:
                cola.popleft()
            if len(cola) >= _LIMIT_MINUTO:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Demasiadas predicciones. Espera un minuto e inténtalo de nuevo."},
                )
            cola.append(ahora)
    respuesta = await call_next(request)
    # REC-107: cabeceras de seguridad en todas las respuestas.
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    respuesta.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    respuesta.headers["Permissions-Policy"] = "camera=(self), geolocation=(self), microphone=()"
    respuesta.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data: blob:; "
        "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 "
        "http://localhost:5173 http://127.0.0.1:5173; "
        "style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'"
    )
    return respuesta


# Logging estructurado simple (REC-71): una línea JSON por evento relevante.
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ecoscan")

def log_evento(evento, **campos):
    logger.info(json.dumps({"evento": evento, **campos}, ensure_ascii=False, default=str))

# Rutas /db/... alimentadas desde MySQL ecoscan (REC-42, REC-47, REC-51)
from rutas_db import router as db_router, guardar_inferencia, Inferencia, ejecutar
app.include_router(db_router)

# Habilitar CORS para permitir peticiones desde React (http://localhost:5173)
# "*" con allow_credentials=True no es válido en navegadores; se declaran los orígenes reales.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        o.strip() for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",") if o.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 🗄️ CONFIGURACIÓN DE BASE DE DATOS MYSQL
# ----------------------------------------------------
# Ajusta el usuario, contraseña y nombre de BD según la configuración de tu compañero:
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "admin")  # Pongan aquí la clave de MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "ecoscan")

MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

db_activa = False
SessionLocal = None

try:
    engine = create_engine(MYSQL_URL, pool_pre_ping=True)
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

    db_activa = True
    print("🟢 Conexión exitosa a MySQL (Base de datos EcoScan activa).")
except Exception as e:
    print(f"⚠️ Aviso MySQL: No se pudo conectar a la BD ({e}). El backend continuará funcionando.")

# ----------------------------------------------------
# 🤖 SELECCIÓN DEL MODELO YOLO
# ----------------------------------------------------
MODEL_PATH = "best.pt" if os.path.exists("best.pt") else "yolov8n.pt"
UMBRAL_CONFIANZA = float(os.getenv("UMBRAL_CONFIANZA", "0.5"))
UMBRAL_NITIDEZ = float(os.getenv("UMBRAL_NITIDEZ", "100"))
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
            estado["escaneos_registrados"] = db.query(HistorialEscaneo).count()
            db.close()
        except Exception as err:
            estado["status"] = "degraded"
            estado["error_mysql"] = str(err)
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
async def predict(file: UploadFile = File(...), id_sesion: str = Form(None)):
    inicio = time.perf_counter()
    sesion = (id_sesion or "").strip() or None
    if db_activa and sesion:
        try:
            ejecutar("INSERT IGNORE INTO sesion (id_sesion) VALUES (%s)", (sesion,))
        except Exception:
            pass
    # Rechazar archivos > 10 MB antes de cargarlos en memoria. Se revisa la
    # cabecera Content-Length del parte y además se limita la lectura real,
    # porque la cabecera es declarada por el cliente y puede faltar o mentir.
    try:
        longitud = int((file.headers or {}).get("content-length") or 0)
    except (TypeError, ValueError):
        longitud = 0
    if longitud > MAX_TAMANO_ARCHIVO:
        raise HTTPException(
            status_code=413,
            detail={"codigo": "ARCHIVO_MUY_GRANDE",
                    "mensaje": "La imagen supera el límite de 10 MB."},
        )

    contents = await file.read(MAX_TAMANO_ARCHIVO + 1)
    if len(contents) > MAX_TAMANO_ARCHIVO:
        raise HTTPException(
            status_code=413,
            detail={"codigo": "ARCHIVO_MUY_GRANDE",
                    "mensaje": "La imagen supera el límite de 10 MB."},
        )

    # Whitelist de MIME: el tipo declarado debe ser una imagen soportada.
    mime = (file.content_type or "").split(";")[0].strip().lower()
    if mime not in MIME_IMAGENES_PERMITIDAS:
        raise HTTPException(status_code=400, detail=MENSAJE_IMAGEN_INVALIDA)

    # Validar que el archivo sea realmente una imagen (REC-54: 400 controlado, no 500).
    # verify() detecta contenido corrupto aunque el MIME declare lo contrario.
    try:
        imagen_cargada = Image.open(io.BytesIO(contents))
        imagen_cargada.verify()
    except Exception:
        raise HTTPException(status_code=400, detail=MENSAJE_IMAGEN_INVALIDA)

    # Abrir la imagen ajustando la rotación EXIF (Corrige fotos giradas de iPhone)
    image = Image.open(io.BytesIO(contents))
    image = ImageOps.exif_transpose(image).convert("RGB")
    if image.width > MAX_DIMENSION_IMAGEN or image.height > MAX_DIMENSION_IMAGEN:
        raise HTTPException(
            status_code=400,
            detail={"codigo": "DIMENSIONES_EXCEDIDAS",
                    "mensaje": "La imagen supera el tamaño máximo de 8000x8000 píxeles."},
        )

    # REC-104: rechazar fotos borrosas antes de clasificar.
    gris = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    nitidez = float(cv2.Laplacian(gris, cv2.CV_64F).var())
    if nitidez < UMBRAL_NITIDEZ:
        try:
            guardar_inferencia(Inferencia(
                id_sesion=(id_sesion or "").strip() or None,
                id_material=None,
                resultado="BORROSA",
                confianza=None,
                latencia_ms=int((time.perf_counter() - inicio) * 1000),
            ))
        except Exception:
            pass
        raise HTTPException(
            status_code=400,
            detail={"codigo": "BORROSA", "mensaje": "La foto salió borrosa. Toma otra con buena luz y sin movimiento."}
        )

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

    # Solo cuenta como escaneo real si hubo detecciones aceptadas.
    if db_activa and SessionLocal and detecciones:
        try:
            db = SessionLocal()
            materiales_str = ", ".join(list(clases_unicas))
            nuevo_registro = HistorialEscaneo(
                materiales_detectados=materiales_str,
                modelo_usado=MODEL_PATH,
                total_objetos=len(detecciones),
                id_sesion=(id_sesion or "").strip() or None,
                cant_carton=conteo_clases.get("Carton", 0),
                cant_aluminio=conteo_clases.get("Aluminio", 0),
                cant_plastico=conteo_clases.get("Plastico", 0),
            )
            db.add(nuevo_registro)
            db.commit()
            db.close()
        except Exception as err:
            print(f"⚠️ Error al guardar registro en MySQL: {err}")

    # REC-43: trazabilidad real de cada detección en la tabla inferencia.
    if db_activa:
        try:
            sesion = (id_sesion or "").strip() or None
            if sesion:
                ejecutar("INSERT IGNORE INTO sesion (id_sesion) VALUES (%s)", (sesion,))
            for det in detecciones:
                guardar_inferencia(Inferencia(
                    id_sesion=sesion,
                    id_material=id_material_por_clase.get(det["clase"]),
                    resultado="OK",
                    confianza=det["confianza"],
                    latencia_ms=latencia_ms,
                ))
            for det in detecciones_rechazadas:
                guardar_inferencia(Inferencia(
                    id_sesion=sesion,
                    id_material=id_material_por_clase.get(det["clase"]),
                    resultado="CONFIANZA_BAJA",
                    confianza=det["confianza"],
                    latencia_ms=latencia_ms,
                ))
            if not detecciones and not detecciones_rechazadas:
                guardar_inferencia(Inferencia(
                    id_sesion=sesion,
                    id_material=None,
                    resultado="SIN_DETECCION",
                    confianza=None,
                    latencia_ms=latencia_ms,
                ))
        except Exception as err:
            print(f"⚠️ Error al guardar inferencia en MySQL: {err}")

    log_evento("prediccion", sesion=id_sesion, aceptadas=len(detecciones),
               rechazadas=len(detecciones_rechazadas), latencia_ms=latencia_ms)

    return {
        "detecciones": detecciones,
        "detecciones_rechazadas": detecciones_rechazadas,
        "modelo_usado": MODEL_PATH,
        "id_sesion": id_sesion,
        "conteo_materiales": conteo_clases,
        "umbral_confianza": UMBRAL_CONFIANZA,
        "latencia_ms": latencia_ms,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)