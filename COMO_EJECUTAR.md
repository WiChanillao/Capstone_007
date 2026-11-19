# Cómo ejecutar EcoScan en Visual Studio Code

## Problema que tenías

VS Code estaba usando un **Python 3.14 global** (`C:\Users\Grove\...`) en vez del entorno virtual del proyecto. Por eso salía:

```
ModuleNotFoundError: No module named 'fastapi'
```

Además, el entorno virtual estaba copiado de otra computadora y apuntaba a esa ruta inexistente.

## Lo que ya quedó corregido

- Se recreó `ecoscan-backend\venv` con tu Python 3.13.
- Se instalaron: `fastapi`, `uvicorn`, `ultralytics`, `pillow`, `pillow-heif`, `sqlalchemy`, `pymysql`, `python-multipart`.
- Se corrigió el nombre de la base de datos: `ecoscan` (antes decía `ecoscan_db`).
- Se crearon `.vscode\launch.json`, `.vscode\settings.json` y `.vscode\tasks.json`.

## Cómo darle Run

1. Abre en VS Code esta carpeta: **`...\version del ema capstone\Capstone`** (la carpeta `Capstone`, no `ecoscan-backend` sola).
2. Presiona **F5**.
3. En el desplegable elige **"EcoScan: Backend (F5)"** (o **"EcoScan: Full Stack (Backend + Frontend)"** si quieres ambos).
4. Si VS Code pregunta por el intérprete, selecciona:
   `Capstone\ecoscan-backend\venv\Scripts\python.exe`

También puedes ir a **Terminal → Run Task…** y elegir:
- `EcoScan: Backend (FastAPI)`
- `EcoScan: Frontend (Vite)`

## Comandos manuales (por si prefieres la terminal)

Backend:
```powershell
cd ecoscan-backend
.\venv\Scripts\python.exe main.py
```

Frontend (en otra terminal):
```powershell
cd ecoscan-frontend
npm run dev
```

## URLs

- Backend / API: http://127.0.0.1:8000 → debe responder `{"status":"ok","modelo_activo":"best.pt","mysql_conectado":true}`
- Documentación de la API: http://127.0.0.1:8000/docs
- Frontend: http://localhost:5173

## Ejecución con Docker (opción para otro computador)

La ventaja de Docker es que **no hay que instalar Python, Node.js, React ni las librerías del proyecto**: las dependencias se descargan y se arman dentro de las imágenes. Pero **Docker Desktop sí es obligatorio**.

### Requisitos previos

1. **Instalar y abrir Docker Desktop** en Windows. Si no está instalado, el comando `docker` no se reconoce. Durante la instalación dejar seleccionada la opción **WSL 2**. Si ya está instalado, abrir Docker Desktop y esperar a que esté corriendo antes de ejecutar cualquier comando.
2. **Virtualización activada en la BIOS/UEFI**. Si Docker Desktop muestra el aviso rojo *“Virtualization is disabled in firmware”*, hay que habilitar la virtualización en la BIOS/UEFI del computador y reiniciar.
3. **Descomprimir el proyecto**. Si se recibió un `.zip` o `.rar`, extraerlo primero. Ejecutar Docker desde dentro del archivo comprimido hará que no encuentre los archivos.
4. **Ubicarse en la carpeta raíz `Capstone`**, la que contiene `docker-compose.yml`.

### Comando

```bash
docker compose up --build
```

El `--build` es importante la primera vez: descarga las imágenes base y construye los contenedores del backend y del frontend.

Para detenerlo:

```bash
docker compose down
```

Para revisar logs si algo falla:

```bash
docker compose logs -f
```

> Estado real: los archivos `docker-compose.yml` y los `Dockerfile` están entregados en el proyecto. **La ejecución de Docker Compose no ha sido verificada en esta máquina**; por eso REC-67 sigue documentado como pendiente.

## Verificación ya realizada

- `import main` → OK
- Backend HTTP 200 con MySQL conectado y modelo `best.pt` cargado
- Frontend Vite HTTP 200 en el puerto 5173
