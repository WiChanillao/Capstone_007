# Decisiones técnicas — EcoLearn Chile / EcoScan

Documento de decisiones (ADR resumido). Cada decisión se apoya en código o
documentación **real** del repositorio; se indican las rutas y líneas relevantes.
La métrica oficial sigue siendo `mAP@50 = 0.562` y la presentación no se modificó.

> **Actualizado 20-11-2026:** el alcance canónico y los nombres vigentes están en
> [`DOCUMENTACION_GENERAL.md`](DOCUMENTACION_GENERAL.md); las referencias de línea
> de este ADR son históricas y pueden diferir del working tree. El esquema real
> de `01_schema.sql` tiene **15 tablas**, no 14.

## 1. MySQL 8 en lugar de PostGIS

**Decisión:** usar MySQL 8.0 con el esquema relacional `ecoscan` cargado desde
`docker/mysql/init/01_schema.sql` y `02_seed.sql`.

**Justificación:** el modelo de datos es relacional (15 tablas: `escaneos`,
`inferencia`, `material`, `contenedor`, `punto_limpio`, etc.) y no necesita
operaciones geométricas en servidor. Las coordenadas de los puntos limpios se
guardan como columnas `lat`/`lon` y Leaflet las consume en el cliente, por lo
que no se requiere la extensión espacial de PostGIS. MySQL ya estaba en los
entregables de Fases 1 y 2 y tiene imagen oficial para Docker.

**Evidencia:** [`../README.md`](../README.md) (arquitectura, línea 23: `MySQL 8
(base 'ecoscan')`), [`../docker-compose.yml`](../docker-compose.yml) (servicio
`mysql:8.0`), [`../ecoscan-frontend/src/MapaPuntos.jsx`](../ecoscan-frontend/src/MapaPuntos.jsx)
(marcadores construidos con lat/lon del lado cliente).

## 2. YOLO11n con `best.pt` como modelo de producción

**Decisión:** usar YOLO11n por transfer learning, con `best.pt` como peso
entrenado y `MODEL_PATH` configurable.

**Justificación:** es el modelo documentado en el CRISP-DM y en el README;
prioriza latencia baja (~21 ms en GPU, ~110 ms en API) para una demo interactiva
en navegador. El reentrenamiento del 19-11-2026 (100 épocas, `patience=20`) dio
`0.622` en validación y `0.527` en test, peor que la cifra oficial, por lo que
se descartó y **no** se actualizó la tabla de métricas.

**Evidencia:** [`../README.md`](../README.md) líneas 3, 9, 20, 120, 129 y
171–176; [`../ecoscan-backend/main.py`](../ecoscan-backend/main.py) líneas 209–211
(`MODEL_PATH = os.getenv("MODEL_PATH", "best.pt")`).

## 3. Acceso anónimo por `id_sesion`

**Decisión:** no hay login; el frontend envía un `id_sesion` opcional que se
usa como clave de agrupación de escaneos e impacto.

**Justificación:** es una demo académica con Menú Principal + 4 módulos; el objetivo es mostrar
el flujo foto → detección → impacto sin fricción de registro. Para evitar
inyección o valores arbitrarios en MySQL se valida con
`^[A-Za-z0-9_-]{1,64}$` y se devuelve 422 si no cumple.

**Evidencia:** [`../ecoscan-backend/main.py`](../ecoscan-backend/main.py)
líneas 290–301; [`../README.md`](../README.md) línea 98 (`POST /predict` con
`id_sesion` opcional). Ver también la limitación de autenticación más abajo.

## 4. Mapa base OpenStreetMap

**Decisión:** mapa Leaflet con teselas estándar de OpenStreetMap por defecto,
más alternativas "Calles claras" (CARTO Voyager) y "Satélite" (Esri), con
respaldo automático entre proveedores.

**Justificación:** no requiere API key ni costo, muestra Santiago con calles y
rotulos, y permite identificar visualmente los 35 puntos limpios. Los 25 puntos
externos se geocodificaron con Nominatim y se marcan como coordenada
aproximada; no se inventaron direcciones ni materiales. El mapa no añade una
sexta pestaña.

**Evidencia:** [`../ecoscan-frontend/src/MapaPuntos.jsx`](../ecoscan-frontend/src/MapaPuntos.jsx)
líneas 12–21 (URLs y atribución de OSM/CARTO);
[`../README.md`](../README.md) línea 36; secciones 16–19 de
[`EVIDENCIA_DOCKER.md`](evidencia/EVIDENCIA_DOCKER.md).

## 5. Contenedores no root y secretos fuera del código

**Decisión:** backend corre como `appuser` (uid 10001) y frontend como `nginx`
(uid 101); el compose exige `MYSQL_ROOT_PASSWORD` y publica los puertos solo en
`127.0.0.1`; `.env*` está en los `.dockerignore`.

**Justificación:** reduce superficie de ataque y evita que un proceso del
contenedor escriba como root en el volumen o en el sistema de archivos. La
contraseña obligatoria (`${MYSQL_ROOT_PASSWORD:?...}`) impide levantar el stack
con un default conocido. Los códigos Python también exigen `MYSQL_PASSWORD` y
fallan con `Define MYSQL_PASSWORD en .env` si falta.

**Evidencia:** [`../ecoscan-backend/Dockerfile`](../ecoscan-backend/Dockerfile)
líneas 20–25; [`../ecoscan-frontend/Dockerfile`](../ecoscan-frontend/Dockerfile)
líneas 23–25; [`../docker-compose.yml`](../docker-compose.yml) líneas 8, 11, 29
y 33–52; [`../ecoscan-backend/main.py`](../ecoscan-backend/main.py) líneas
119–121; [`../README.md`](../README.md) líneas 59–61 y 156–160;
[`evidencia/usuarios_no_root.txt`](evidencia/usuarios_no_root.txt).

## 6. Límites de seguridad en `/predict`

**Decisión:** whitelist de MIME (JPG/JPEG/PNG/WEBP/HEIC/HEIF), `Image.verify()`
para contenido corrupto, máximo de 10 MB y 8000×8000 px, validación de
`id_sesion`, 30 peticiones/minuto por IP y cabeceras de seguridad en todas las
respuestas.

**Justificación:** `/predict` es la única ruta que recibe datos del usuario.
Leer el archivo completo antes de validarlo permitía un DoS por memoria; un MIME
declarado falso o una imagen excesivamente grande podía llegar al modelo. El
rate limit y las cabeceras (`nosniff`, `X-Frame-Options`, CSP, etc.) cubren el
abuso básico y el navegador. CORS declara orígenes explícitos en lugar de `*`.

**Evidencia:** [`../ecoscan-backend/main.py`](../ecoscan-backend/main.py)
líneas 40–85 (rate limit y cabeceras), 101–112 (CORS) y 290–330 (validaciones);
[`../ecoscan-backend/tests/test_main.py`](../ecoscan-backend/tests/test_main.py)
casos de corrupto, >10 MB, MIME no permitido, dimensiones e `id_sesion`;
[`evidencia/pytest.txt`](evidencia/pytest.txt) (22 pruebas).

## Limitaciones conocidas

- **Sin autenticación por diseño.** `id_sesion` es solo un identificador;
  cualquier cliente puede enviar uno. No hay usuarios, roles ni tokens. Aceptable
  para una demo académica, pero no para un despliegue público con datos reales.
- **Rate limit por IP y en memoria.** Se aplica solo a `/predict`
  (`_solicitudes`, `main.py:40–71`); detrás de NAT o proxy varios clientes
  comparten la cuenta, no es distribuido y se reinicia con el proceso.
  `/db/*` y `/health` no están limitados.
- **CSP con orígenes fijos.** La política estricta vive en `main.py` (cabeceras
  de seguridad para todas las respuestas). En el working tree hay una relajación
  **sólo para `/docs`, `/redoc` y `/docs/*`** que aún no está commiteada: decidir
  si se incorpora antes de congelar la entrega. Habrá que parametrizar los
  orígenes cuando se defina un dominio de producción (`REC-105`).
- **Métrica no alcanzada.** `mAP@50 = 0.562` frente a la meta `0.65`. No se
  afirmó el objetivo ni se modificó la presentación; la recomendación abierta
  es mejorar etiquetado/datos antes que repetir entrenamientos.
- **Fallback del modelo requiere internet.** Si no existe `best.pt`, `main.py`
  usa `yolov8n.pt`, que Ultralytics descarga automáticamente; sin conexión el
  backend no arranca. `best.pt` sí está versionado.
- **Datos externos sin validar.** Coordenadas aproximadas y materiales por
  confirmar en los 25 puntos agregados desde un listado externo.
