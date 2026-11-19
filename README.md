# EcoLearn Chile — Clasificador Inteligente de Residuos (EcoScan)

Proyecto Capstone. El usuario sube una foto de un residuo, un modelo **YOLO11n**
detecta el material (**Aluminio, Cartón, Plástico**), el backend responde con
instrucciones de reciclaje y guarda el análisis en **MySQL 8**. La app además
ofrece puntos limpios de la Región Metropolitana, un simulador educativo y un
desafío verde.

- **Backend:** FastAPI + Ultralytics (YOLO11n, `best.pt`) + MySQL.
- **Frontend:** React 19 + Vite + Tailwind (PWA, 5 pestañas).
- **Despliegue:** Docker Compose (MySQL + backend + frontend Nginx).
- **Calidad:** pytest, Vitest, Cypress, oxlint, GitHub Actions.

## Arquitectura

```
Frontend (React 19 + Vite + PWA)
        │  HTTP (JSON / multipart)
        ▼
Backend FastAPI  ── /predict ──▶  Modelo YOLO11n (best.pt)
        │  /db/...  /impacto  /sesiones  /health  /v1/models
        ▼
MySQL 8  (base `ecoscan`)
```

El frontend consume la API en `VITE_API_URL` (por defecto `http://127.0.0.1:8000`).

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `ecoscan-backend/` | API FastAPI (`main.py`), rutas de datos (`rutas_db.py`), `best.pt`, `Dockerfile`, pruebas (`tests/`) |
| `ecoscan-frontend/` | App React + Vite + Tailwind (pestañas Escáner IA, Puntos Limpios, Eco-Simulador, Desafío Verde, Impacto), `Dockerfile`, Cypress y Vitest |
| `docker/mysql/init/` | `01_schema.sql` (esquema `ecoscan`) y `02_seed.sql` (datos iniciales) |
| `docker-compose.yml` | Stack completo: MySQL 8.0 (host 3307), backend (8000), frontend Nginx (5173) con *healthchecks* |
| `scripts/` | `run.ps1` / `run.sh` / `run.bat` (arranque reproducible), `verificar_docker.ps1`, `instalar_docker.ps1`, `init_local_db.py` |
| `docs/` | CRISP-DM, requisitos (100 RF/RNF), BPMN, modelo de datos, informe de pruebas |
| `.github/workflows/ci.yml` | CI: pytest + cobertura + pip-audit, y Vitest + npm audit + build |
| `.env.example` | Variables de entorno (copiar a `.env`) |

## Puesta en marcha

### Opción A — Docker (recomendada)

Requisitos: Docker Desktop con WSL2 (en Windows, `scripts/instalar_docker.ps1`
lo instala si falta).

```bash
docker compose up --build -d     # MySQL 3307, backend 8000, frontend 5173
docker compose ps                # los 3 servicios deben verse "healthy"
```

- App: http://localhost:5173/
- API: http://127.0.0.1:8000/ · Docs: http://127.0.0.1:8000/docs

Atajos de arranque: `scripts\run.ps1 -Docker` (Windows) o `bash scripts/run.sh --docker`.
En VS Code: tarea **"EcoScan: DOCKER (compose up)"**. Para detener: `docker compose down`.

> El backend y el frontend locales (puertos 8000 y 5173) deben estar detenidos
> para que Docker use esos puertos.

### Opción B — Local

```bash
# 1) Variables de entorno
cp .env.example .env            # completar credenciales de MySQL

# 2) Base de datos (MySQL 8 local en 3306)
#    Crear la base `ecoscan` y ejecutar docker/mysql/init/01_schema.sql y 02_seed.sql

# 3) Backend
cd ecoscan-backend
python -m venv venv
venv\Scripts\activate           # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
python main.py                  # http://localhost:8000

# 4) Frontend
cd ../ecoscan-frontend
npm install
npm run dev                     # http://localhost:5173
```

## API principal

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/predict` | Sube una imagen (`file`) y opcionalmente `id_sesion`; devuelve detecciones y conteo por material |
| `GET` | `/health` | Estado del servicio, conexión MySQL y modelo activo |
| `GET` | `/v1/models` | Modelo activo en formato tipo OpenAI |
| `GET` | `/db/puntos?comuna=...` | Puntos limpios filtrados por comuna |
| `GET` | `/db/*`, `/impacto`, `/sesiones` | Datos de materiales, hábitos, impacto y sesiones |

## CRISP-DM

Notebook completo: [`docs/crisp-dm/`](docs/crisp-dm/) (fases 1 a 6 y cierre).

| Fase | Estado |
|---|---|
| 1. Entendimiento del negocio | Hecho |
| 2. Entendimiento de los datos (EDA) | Hecho |
| 3. Preparación (485 etiquetas corregidas, +252 imágenes de aluminio por *oversampling*) | Hecho |
| 4. Modelado (YOLO11n, 50 épocas, transfer learning) | Hecho |
| 5. Evaluación | Hecho; criterio **mAP@50 = 0.65 no alcanzado** |
| 6. Despliegue | Backend + MySQL + frontend en Docker funcionando |

### Resultados (validación: 61 imágenes, 109 instancias)

| Iteración | Precisión | Recall | mAP@50 | mAP@50-95 |
|---|---|---|---|---|
| 1 — dataset sin limpiar | 0.798 | 0.561 | 0.638 | 0.357 |
| 2 — limpio + balanceo | 0.681 | 0.521 | 0.562 | 0.323 |

Por clase (iteración 2): Aluminio 0.493 · Cartón 0.737 · Plástico 0.454.
Pruebas de sistema con fotos reales: **27 de 30** correctas (métrica por foto,
no comparable con mAP). Latencia: modelo ~21 ms/imagen (GPU), API ~110 ms
promedio (P95 ~130 ms).

## Pruebas

```bash
# Backend (pytest + cobertura)
cd ecoscan-backend && venv\Scripts\python.exe -m pytest -q

# Frontend (Vitest)
cd ecoscan-frontend && npm run test:unit

# E2E (Cypress)
cd ecoscan-frontend && npm run test:e2e

# Pruebas de humo del modelo con fotos reales
cd ecoscan-backend && venv\Scripts\python.exe pruebas\probar_modelo.py
```

El pipeline de CI (`.github/workflows/ci.yml`) ejecuta pytest con cobertura y
`pip-audit` en el backend, y `npm run test:unit`, `npm audit` y `npm run build`
en el frontend.

## Seguridad

Nunca subir claves al repositorio. Las credenciales de MySQL y los secretos van
en `.env` (ignorado por Git y por los `.dockerignore`); la API key de Roboflow
se inyecta por variable de entorno o en los Secretos de Colab. Ver `.env.example`.

## Equipo y gestión

Jira: tablero **EcoLearn** (proyecto **REC**). Ramas: `main` (estable), `develop`,
`feature/<ticket>`. Commits: `REC-xx: descripción corta`.

Repo público de documentación y evidencia de fases:
<https://github.com/WiChanillao/Capstone_007> (Fase 1 y Fase 2: guías, diarios,
PPT, CRISP-DM, requisitos, BPMN, SQL e informe de pruebas). Ese repo **no contiene
el código de la app**, que se trabaja localmente en esta carpeta.
