# Inicio rápido — EcoLearn Chile / EcoScan

Este documento explica cómo levantar el proyecto **desde un clone/descarga del repositorio**, sin comandos sueltos ni rutas absolutas de una PC concreta.

## Requisitos previos

| Modo | Necesitas |
|---|---|
| **A. Local (recomendado en la PC actual)** | Python 3.10+, Node.js 20+ con npm, MySQL 8.0 en `localhost:3306`, Visual Studio Code (opcional) |
| **B. Docker** | Docker Desktop con Compose v2 (no es obligatorio) |

Antes de levantar, copia `.env.example` a `.env` y **define una contraseña propia** en `MYSQL_ROOT_PASSWORD` (y `MYSQL_PASSWORD`). El ejemplo trae el placeholder `cambiar_esta_clave`: no sirve para usar tal cual. El compose falla con un mensaje claro si `MYSQL_ROOT_PASSWORD` no está definida.

> `.env` está ignorado por Git. Nunca subas credenciales reales.

---

## Opción A — Arranque local (un solo comando)

Desde la carpeta **`Capstone\Fase 3`** (donde están `scripts/` y `docker-compose.yml`):

**Windows:**
```bat
scripts\run.bat
```

**Linux / macOS / Git Bash:**
```bash
bash scripts/run.sh
```

El script hace todo esto automáticamente:

1. Copia `.env.example` → `.env` si no existe y cargó sus variables.
2. Detecta Python y Node.
3. Crea `ecoscan-backend/venv` e instala `requirements.txt`.
4. Instala dependencias del frontend con `npm ci` (o `npm install` si no hay lock).
5. Verifica/inicializa MySQL con `scripts/init_local_db.py`:
   - crea la base si falta;
   - aplica `docker/mysql/init/01_schema.sql` y `02_seed.sql` **solo si no hay datos**;
   - **nunca borra datos existentes**.
6. Abre dos terminales visibles: backend FastAPI (8000) y frontend Vite (5173).
7. Abre Visual Studio Code en la carpeta `Fase 3` y el navegador en la app.
8. Espera a `/health` y `/db/impacto` e imprime la verificación real.

Salida esperada al final:

```text
[EcoScan] Verificado: MySQL=True, modelo=best.pt, 48 escaneos, 237.0 L, 7.86 kg CO2.
[EcoScan] === EcoScan levantado ===
  App:       http://localhost:5173/
  API:       http://127.0.0.1:8000/
  Docs:      http://127.0.0.1:8000/docs
```

> Con una base recién sembrada son 48 escaneos / 237,0 L. Si ya se registraron escaneos reales desde la app, el script imprime el valor actual (por ejemplo 49 / 239,0 L); es el comportamiento correcto porque el impacto se calcula desde MySQL en vivo.

Si quieres abrir solo los servicios sin ventanas extra:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run.ps1 -SinNavegador -SinVSCode
```

### Probar desde cero con una base vacía

1. Edita `.env` y cambia solo `MYSQL_DB=ecoscan_prueba`.
2. Ejecuta `scripts\run.bat`.
3. El script crea `ecoscan_prueba`, siembra los 48 escaneos y levanta todo apuntando a esa base.
4. Verifica en el navegador: `http://127.0.0.1:8000/db/impacto` → `escaneos: 48`, `agua_litros: 237.0`.
5. Para volver a la original, restaura `MYSQL_DB=ecoscan` y ejecuta el script otra vez.

Para borrar solo la base de prueba:

```sql
DROP DATABASE IF EXISTS ecoscan_prueba;
```

---

## Opción B — Arranque con Docker (MySQL incluido)

El `docker-compose.yml` levanta **MySQL + backend + frontend**, sin depender del MySQL instalado en Windows. El MySQL del contenedor publica el puerto **3307** para no chocar con el local 3306.

Desde la carpeta **`Capstone\Fase 3`**:

```bash
copy .env.example .env      # Windows
# o: cp .env.example .env   # Linux/macOS

# IMPORTANTE: editar .env y reemplazar cambiar_esta_clave por una clave propia
# en MYSQL_ROOT_PASSWORD y MYSQL_PASSWORD antes del siguiente comando.

docker compose up --build -d
docker compose ps
```

Los SQL de `docker/mysql/init` se ejecutan automáticamente la primera vez que se crea el volumen `mysql_data`, así que la BD queda con los 48 escaneos de demostración.

URLs:

- App: http://localhost:5173/
- API: http://127.0.0.1:8000/
- Docs: http://127.0.0.1:8000/docs
- Impacto: http://127.0.0.1:8000/db/impacto
- MySQL Docker: `localhost:3307`, usuario `root`, clave de `MYSQL_ROOT_PASSWORD`

Para abrir VS Code con el proyecto ordenado:

```bash
code .        # estando dentro de Capstone\Fase 3
```

Para reiniciar **realmente desde cero** en Docker (esto borra el volumen de datos):

```bash
docker compose down -v
docker compose up --build -d
```

Para detener sin borrar datos:

```bash
docker compose down
```

---

## Solo desde Visual Studio Code (sin CMD)

Abre la carpeta **`Capstone\Fase 3`** en VS Code y pulsa **`Ctrl+Shift+B`**. Se ejecuta la tarea de build por defecto:

- **EcoScan: FULL STACK (solo VS Code, sin CMD)**

Esta tarea levanta, en **terminales integradas de VS Code** (sin ventanas CMD externas):

1. `EcoScan: Backend (FastAPI)` → ejecuta `scripts/_vscode_backend.ps1`, que primero verifica/inicializa MySQL y luego arranca `main.py`.
2. `EcoScan: Frontend (Vite)` → `npm run dev -- --host 0.0.0.0`.

Cuando veas `Uvicorn running on http://0.0.0.0:8000` y `VITE ... ready`, abre:

- App: **http://127.0.0.1:5173/**
- API: **http://127.0.0.1:8000/**
- Docs: **http://127.0.0.1:8000/docs**

> Usa `127.0.0.1` en vez de `localhost` para evitar el timeout IPv6 que se detectó en este equipo.

Otras tareas disponibles (`Ctrl+Shift+P` → `Tasks: Run Task`):

- **EcoScan: Inicializar MySQL** (solo BD, una vez).
- **EcoScan: Instalar dependencias** (para un clone nuevo).
- **EcoScan: Arrancar todo (script externo / Docker)** (opción alternativa, abre terminales propias).

También hay `.vscode/launch.json` con la configuración **EcoScan: Full Stack (Backend + Frontend)** para `F5`.

---

## Archivos añadidos/ajustados para que esto funcione

| Archivo | Para qué sirve |
|---|---|
| `scripts/run.ps1`, `scripts/run.bat`, `scripts/run.sh` | Arranque único y reproducible |
| `scripts/init_local_db.py` | Inicialización idempotente de MySQL desde SQL versionado |
| `scripts/_serve_backend.bat`, `scripts/_serve_frontend.bat` | Terminales visibles con logs |
| `docker/mysql/init/01_schema.sql`, `02_seed.sql` | Esquema + datos semilla sin nombre de BD fijo ni `DROP DATABASE` |
| `docker-compose.yml` | MySQL + backend + frontend en contenedores |
| `ecoscan-backend/Dockerfile`, `ecoscan-frontend/Dockerfile` | Imágenes que usan `requirements.txt` / `package-lock.json` y reciben `VITE_API_URL` |
| `.dockerignore` en cada app | Evita copiar `venv`, `node_modules`, `.env` y temporales |
| `.env.example`, `.gitignore`, `.gitattributes` | Configuración limpia, secretos fuera del repo y finales de línea correctos |
| `.vscode/tasks.json` | Arranque desde VS Code |
| `ecoscan-backend/main.py` | Carga también el `.env` de la carpeta `Fase 3` |
| `INICIO_RAPIDO.md` | Esta guía |

---

## Estado real de Git, Docker y CI (19-11-2026)

- Git 2.56.0.4 instalado y en PATH; repo: <https://github.com/WiChanillao/Capstone_007>.
- Todo el proyecto está agrupado en `Fase 3/`. En la raíz solo quedan `.github/`,
  `.gitignore`, `.gitattributes` y este README índice (GitHub/Git los necesitan).
- Docker Compose **sí se ejecutó y se verificó**: 3 contenedores `healthy`,
  `/health`, `/v1/models`, `/docs` y `/` → 200, y `POST /predict` incrementó
  inferencias en MySQL de 60 a 61.
- CI de GitHub Actions **sí se ejecutó**: tras corregir el test de `/health`
  (REC-142), los jobs `backend` y `frontend` pasaron; además se actualizaron
  `actions/checkout`, `actions/setup-python` y `actions/setup-node` a v7 para
  quitar los avisos de Node.js 20.
- Si descargas el ZIP en vez de clonar, las opciones A y B funcionan igual desde
  `Capstone\Fase 3`.
