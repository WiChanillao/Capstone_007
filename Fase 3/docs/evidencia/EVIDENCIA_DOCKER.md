# Evidencia de Docker, despliegue y endurecimiento — EcoLearn Chile / EcoScan

**Fecha:** 19-11-2026 · **Repositorio:** `https://github.com/WiChanillao/Capstone_007.git` · **Rama:** `main`

Este documento es la versión ordenada y sanitizada del registro de evidencia de Docker.
Contiene comandos ejecutados y resultados reales. Las rutas personales, valores del
`.env`, claves y tokens se han eliminado: aquí solo aparecen nombres de variables,
placeholders y hashes públicos de commits.

> **Nota de vigencia.** Las secciones 1–5 registran el estado inicial del despliegue
> (incluye puertos `0.0.0.0` y `5173:80`, que corresponden a esa versión). La
> **configuración final vigente** está en las secciones 6–7: puertos ligados a
> `127.0.0.1`, frontend en `5173:8080`, usuarios no root y sin contraseñas por
> defecto. La métrica oficial sigue siendo `mAP@50 = 0.562` (meta `0.65` no
> alcanzada); este documento no modifica el PPT ni las métricas.

## Índice

| Sección | Contenido |
|---|---|
| 1 | Entorno y verificación de archivos |
| 2 | Contenedores y endpoints (estado inicial) |
| 3 | Base de datos sembrada y arranque del backend |
| 4 | Incidencia resuelta durante el despliegue |
| 5 | Prueba end-to-end inicial |
| 6 | **Sección 29** — correcciones de auditoría Docker |
| 7 | **Sección 30** — endurecimiento de la API y limpieza de pesos |
| 8 | Prueba desde cero (resultado final) |
| 9 | Salidas de comandos guardadas |
| 10 | Evidencia visual |
| 11 | Historial de correcciones funcionales (resumen) |
| 12 | Estado honesto de pendientes |

---

## 1. Entorno y verificación de archivos

Comando de verificación: `scripts\verificar_docker.ps1`.

```
Docker CLI:       Docker version 29.9.3, build 5457199
Docker Compose:   v5.7.0
Engine:           Docker Desktop (running)
WSL2:             distro "docker-desktop" en estado Running

[OK] docker-compose.yml
[OK] docker/mysql/init/01_schema.sql
[OK] docker/mysql/init/02_seed.sql
[OK] ecoscan-backend/Dockerfile
[OK] ecoscan-backend/.dockerignore
[OK] ecoscan-frontend/Dockerfile
[OK] ecoscan-frontend/.dockerignore
[OK] .dockerignore
[OK] .env.example
[OK] YAML válido. Servicios: mysql, backend, frontend
[OK] docker compose config
```

Tras la reorganización del repositorio, todos estos archivos quedaron bajo `Fase 3/`.
Se conservó `name: capstone` en el compose para reutilizar el volumen
`capstone_mysql_data` y no perder la base de datos.

## 2. Contenedores y endpoints (estado inicial)

```
docker compose ps

ecolearn-backend    Up (healthy)   0.0.0.0:8000->8000/tcp
ecolearn-frontend   Up (healthy)   0.0.0.0:5173->80/tcp
ecolearn-mysql      Up (healthy)   0.0.0.0:3307->3306/tcp
```

```
http://127.0.0.1:8000/health    -> 200
  {"status":"ok","mysql_conectado":true,"modelo_activo":"best.pt","escaneos_registrados":48}
http://127.0.0.1:8000/v1/models -> 200
  {"object":"list","data":[{"id":"best.pt","object":"model","owned_by":"ecolearn-chile"}]}
http://127.0.0.1:8000/docs      -> 200
http://127.0.0.1:5173/          -> 200 (frontend Nginx)
```

Logs de arranque del backend: conexión exitosa a MySQL y carga de `best.pt`, sin errores.

## 3. Base de datos sembrada y arranque del backend

Filas por tabla después de aplicar `01_schema.sql` y `02_seed.sql`:

```
banner_impacto 4 | comuna 9 | contenedor 3 | escaneos 48 | habito 4
inferencia 60 | instruccion 6 | item_simulador 3 | material 3
paso_instruccion 18 | punto_limpio 0 | sesion 0
```

Los 3 servicios declaran `healthcheck`:

```
ecolearn-mysql     healthy  (mysqladmin ping)
ecolearn-backend   healthy  (python urlopen /health)
ecolearn-frontend  healthy  (wget --spider http://127.0.0.1/)
```

El frontend espera a que el backend esté `healthy` (`depends_on` con condición).
Comandos útiles: `docker compose up --build -d`, `docker compose ps`,
`docker compose down`, `docker compose logs -f backend`.

## 4. Incidencia resuelta durante el despliegue

Fallo inicial: el Dockerfile del backend usaba `python:3.11-slim`, pero
`requirements.txt` fija `numpy==2.5.5` (requiere Python ≥ 3.12):

```
ERROR: Could not find a version that satisfies the requirement numpy==2.5.5
```

Solución aplicada en `ecoscan-backend/Dockerfile`:
`FROM python:3.11-slim` → `FROM python:3.13-slim`. Resultado: build completo y
3 contenedores en ejecución.

## 5. Prueba end-to-end inicial

```
POST http://127.0.0.1:8000/predict  (imagen + id_sesion=e2e-docker-test)
-> 200 {"detecciones":[],"modelo_usado":"best.pt","id_sesion":"e2e-docker-test",...}

SELECT resultado, COUNT(*) FROM inferencia WHERE id_sesion='e2e-docker-test';
-> SIN_DETECCION 1
Total inferencia: 61 (antes 60) -> la escritura en BD funciona.
```

Tras la reorganización se repitió con `id_sesion=e2e-reorg-150144` → 200, clase
`Cartón` con confianza 0.53; `COUNT(*) FROM inferencia` pasó de 63 a 64. Los runs
de CI `44583062804`, `44583203309` y `44586047654` terminaron en `SUCCESS`.

## 6. Sección 29 — correcciones de auditoría Docker

Commit `f987615`, pusheado sin `--force`. Cuatro cambios:

1. **Sin password por defecto en el compose.** Las líneas 8 y 29 usan
   `${MYSQL_ROOT_PASSWORD:?Definir MYSQL_ROOT_PASSWORD en .env}`. El
   `.env.example` usa el placeholder `cambiar_esta_clave` y advierte que no
   sirve tal cual; `README` e `INICIO_RAPIDO.md` exigen definir la clave.
2. **Contenedores no root.** Backend: `useradd -m -u 10001 appuser`, `chown -R
   /app` y `USER appuser`. Frontend: Nginx corre como `USER nginx`, con
   `chown` de `html`, `cache` y `/var/run`; `nginx.conf` propio con `listen
   8080` y `try_files` para SPA. El `pid` del nginx base se cambió a
   `/tmp/nginx.pid` porque `/run` no era escribible para el usuario no root.
3. **Puertos ligados a `127.0.0.1`:** 3307, 8000 y 5173. El compose publica
   `127.0.0.1:5173:8080` y el healthcheck del frontend consulta el puerto 8080.
4. **`.env.*` en el `.dockerignore` del backend.** El `.env.example` aclara que
   `MYSQL_HOST=localhost` / `MYSQL_PORT=3306` son solo para ejecutar sin Docker.

Verificación: `docker compose config --quiet` → exit 0 tras cada cambio;
`docker exec … id` → `uid=10001(appuser)` en backend y `uid=101(nginx)` en
frontend (ver `usuarios_no_root.txt`).

## 7. Sección 30 — endurecimiento de la API y limpieza de pesos

Commits separados, pusheados sin `--force` (`f987615..b62aec4`):

| Commit | Cambio |
|---|---|
| `eaf3187` | Rechazo con **413** para imágenes > 10 MB |
| `1ab6a3a` | Whitelist MIME, corrupto y límite 8000×8000 |
| `56ccaff` | `id_sesion` validado → **422** |
| `268691a` | `docs/README.md`: puerto `127.0.0.1:5173:8080` |
| `c6fa516` | 3 tests nuevos (corrupto 400, >10 MB 413, `id_sesion` 422) |
| `b62aec4` | `git rm yolov8n.pt` + fallback sin archivo versionado |

Detalle de las validaciones de `/predict` (`ecoscan-backend/main.py`):

- `MAX_TAMANO_ARCHIVO = 10 * 1024 * 1024`. Se revisa `Content-Length` y además
  se hace `file.read(MAX + 1)`; si excede, responde 413 con código
  `ARCHIVO_MUY_GRANDE`.
- Whitelist MIME: `image/jpeg`, `image/jpg`, `image/png`, `image/webp`,
  `image/heic`, `image/heif`. `Image.verify()` detecta contenido corrupto y el
  límite `MAX_DIMENSION_IMAGEN = 8000` produce `DIMENSIONES_EXCEDIDAS`. Tipo o
  contenido inválido → 400.
- `id_sesion` con `^[A-Za-z0-9_-]{1,64}$` → 422 `ID_SESION_INVALIDO`.
- Se eliminó `yolov8n.pt` (6.549.796 bytes) del repositorio. `MODEL_PATH` lee
  la variable de entorno (por defecto `best.pt`); si falta el archivo se usa el
  baseline que Ultralytics descarga automáticamente. `best.pt` sigue siendo el
  modelo activo.

Cobertura resultante: 20 pruebas (`15` originales + `5` nuevas).

Ronda posterior (commits `f6246be` y `47f2869`):

- Se quitaron los valores por defecto de contraseña en `main.py`,
  `respaldar_mysql.py`, `rutas_db.py` y `scripts/init_local_db.py`. Si falta
  `MYSQL_PASSWORD`, se falla con `RuntimeError: Define MYSQL_PASSWORD en .env`.
  Los tests definen su propia variable en `tests/conftest.py`.
- Dos pruebas nuevas: MIME `application/pdf` → 400 e imagen sobre el límite de
  dimensiones → 400. Total: **22 pruebas** (ver `pytest.txt`).

## 8. Prueba desde cero

Comandos ejecutados desde `Fase 3/`:

```
docker compose config --quiet        -> exit 0
docker compose down -v               -> contenedores, red y volumen
                                        capstone_mysql_data eliminados; exit 0
docker compose up --build -d         -> exit 0; rebuild de backend y frontend
```

Espera activa de healthchecks: los 3 servicios quedaron `(healthy)`.

```
NAME                STATUS                        PORTS
ecolearn-backend    Up ... (healthy)              127.0.0.1:8000->8000/tcp
ecolearn-frontend   Up ... (healthy)              127.0.0.1:5173->8080/tcp
ecolearn-mysql      Up ... (healthy)              127.0.0.1:3307->3306/tcp

curl http://127.0.0.1:8000/health
{"status":"ok","mysql_conectado":true,"modelo_activo":"best.pt","escaneos_registrados":48}
HTTP=200

curl http://127.0.0.1:5173/
HTTP=200 SIZE=825
```

También se verificó el backend recreado sin el peso versionado: `/health` → 200
con `modelo_activo: best.pt`.

## 9. Salidas de comandos guardadas

| Archivo | Contenido |
|---|---|
| [`docker-compose-ps.txt`](docker-compose-ps.txt) | `docker compose ps` con los 3 servicios healthy y sus puertos |
| [`health.txt`](health.txt) | `curl /health` → HTTP 200 con MySQL conectado y `best.pt` |
| [`frontend.txt`](frontend.txt) | `curl` al frontend en `127.0.0.1:5173` → HTTP 200 |
| [`pytest.txt`](pytest.txt) | `pytest -q` → 22 pruebas superadas |
| [`usuarios_no_root.txt`](usuarios_no_root.txt) | `docker exec … id` en backend y frontend |

## 10. Evidencia visual

La captura real de Docker Desktop con el proyecto `capstone` y sus 3 contenedores
está en [`../ESTRUCTURA_PROYECTO_DOCKER.png`](../ESTRUCTURA_PROYECTO_DOCKER.png),
ya versionada en el repositorio; no se duplica aquí. Otras capturas de la
aplicación en ejecución están en `Fase 3/` y en `docs/pruebas/evidencia_visual/`.

La captura fue verificada por OCR: pestañas `Containers Images Logs Volumes`,
proyecto `capstone`, puertos `3307`, `8000` y `5173`, y logs `GET /health HTTP/1.1
200 OK`, `GET /v1/models 200 OK`. Los puertos que muestra esa captura antigua
corresponden al estado previo a la sección 6; el estado final es `127.0.0.1` y
`5173:8080`.

## 11. Historial de correcciones funcionales (resumen)

| Sección original | Hecho verificado | Commit |
|---|---|---|
| 15 | Doble codificación CP850 en el seed MySQL corregida en 8 tablas y 37 filas | `ea68c5d` |
| 16 | Mapa interactivo Leaflet + OSM, 10 marcadores, sin sexta pestaña | `8119d07` |
| 17 | Capa base OSM estándar, Calles claras y Satélite, respaldo automático | `41df579` |
| 18 | Nota honesta de cobertura: 10 puntos en 9 comunas de la RM | `0b4fcf6` |
| 19 | Catálogo ampliado a 35 puntos, 15 comunas y categoría "Reciclables (por confirmar)" | `325f2af`, `4b5fe77` |
| 20–21 | Registro en Jira y 14 tickets reales, con paginación por `nextPageToken` | — |
| 22 | Alineación del encabezado de Puntos Limpios en 1920–360 px | `b16b975` |
| 23 | Etiqueta de región que tapaba el zoom, eliminada | `135d08b` |
| 24 | Galería de consejos con flechas y videos `youtube-nocookie` sin autoplay | `fc78d50` |
| 25–27 | Plan de pruebas Markdown, DOCX/PDF y Excel oficial (40 casos, 24 imágenes) | `4ce8eda`, `9407d92`, `a1223a8`, `ab9b758`, `a47224e` |
| 28 | Diagrama sustituido por captura real de Docker Desktop | — |

En todas las verificaciones: `npm run build` OK, Vitest 4/4, Cypress 4/4,
pytest 15/15 (luego 20 y finalmente 22), Lighthouse 1,00 en 4 categorías y
0 errores de consola.

## 12. Estado honesto de pendientes

- `mAP@50 = 0.562` es la métrica oficial; la meta `0.65` **no** está alcanzada.
  El reentrenamiento con T4, 100 épocas y `patience=20` dio `0.622` en
  validación y `0.527` en test, por lo que se descartó.
- UAT/SUS con usuarios reales y dominio de producción/CORS quedan pendientes.
- Las direcciones, horarios y materiales de los 25 puntos externos están en
  validación; las coordenadas son aproximadas y están marcadas como tales.
- Existe una clave de API histórica de Google en commits antiguos ya borrados
  del árbol actual. Requiere rotación; el historial no se reescribió.
