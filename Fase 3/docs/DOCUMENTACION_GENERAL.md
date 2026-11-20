# Documentación general — EcoLearn Chile / EcoScan

**Versión vigente:** 20-11-2026  
**Referencia de código:** `main @ af7d14d` (PR 1 `092fc88` y PR 2 `af7d14d` mergeados).  
**Tablero:** proyecto Jira `REC`, 161 issues (`REC-1` … `REC-161`).  
**Uso:** este documento es la **fuente única de alcance, nombres, flujos y límites**. Si otro archivo dice algo distinto, prevalece lo que aquí se indica y la corrección queda registrada en [`AUDITORIA_JIRA.md`](AUDITORIA_JIRA.md).

---

## 1. Qué es EcoLearn

EcoLearn Chile / EcoScan es una **PWA académica** que reconoce residuos a partir de una foto y entrega orientación de reciclaje. El usuario es un **visitante anónimo**: no hay login, roles ni cuentas.

Flujo resumido:

1. El visitante elige una foto o usa la cámara en el **Escáner IA**.
2. El frontend reduce la imagen localmente y la envía a `POST /predict` con un `id_sesion` opcional.
3. El backend valida el archivo, ejecuta **YOLO11n (`best.pt`)** y aplica un **único umbral global de confianza `0,50`**.
4. Las detecciones aceptadas se agrupan por material, se guardan en MySQL y se muestran con instrucciones y confianza.
5. El **Eco-Simulador RM** calcula impacto de los **últimos 30 días** desde `ecoscan.escaneos`; el **Desafío Verde RM** deriva progreso, hábitos e insignias de esos escaneos.

**Métrica oficial del modelo:** `mAP@50 = 0,562` en validación (61 imágenes, 109 instancias). La meta `≥ 0,65` **no** está alcanzada.

---

## 2. Alcance real y límites explícitos

### 2.1 Sí está en `main`

| Elemento | Valor real |
|---|---|
| Modelo | YOLO11n, pesos `best.pt` (`MODEL_PATH`), fallback a `yolov8n.pt` si no existe |
| Clases | **Cartón, Plástico, Aluminio** (exactamente 3) |
| Umbral | `UMBRAL_CONFIANZA = 0,50`, global, una sola comparación en `/predict` |
| Visitante | Anónimo, `id_sesion` opcional con formato `^[A-Za-z0-9_-]{1,64}$` |
| Impacto | Últimos 30 días, desde `ecoscan.escaneos` + factores de `item_simulador` |
| Mapa | 35 puntos limpios, Leaflet + OpenStreetMap, sin API key |
| Desafío | 25 preguntas, 5 por ronda sin repetir, avance automático desde escaneos |
| Datos | MySQL 8, base `ecoscan`, **15 tablas** |
| Seguridad | CORS por entorno, CSP, rate limit 30/min por IP en `/predict`, límites de imagen |
| Entrega | Docker Compose con 3 servicios `healthy`, CI con GitHub Actions |

### 2.2 NO EN MAIN — no presentar como funcionalidad entregada

- Umbrales por clase, nivel **“Posible”** y `detecciones_posibles`: viven en la rama `feature/umbrales-por-clase`, **sin merge**. `REC-103` es sólo umbral global.
- Login, roles, cuentas, tokens y panel administrativo.
- Panel B2B/B2G y mapas de calor (`REC-16`, `REC-68`).
- PostGIS, consultas de proximidad en base de datos geoespacial (`REC-8`, `REC-14`).
- Arquitectura offline-first y React 18 (`REC-11`); la app usa React 19 + Vite + PWA online.
- Streamlit (`REC-7`), YOLOv8 (`REC-13`) y árbol de decisión en 2 toques (`REC-12`).
- Sliders, escenarios guardados/comparados e impacto anual manual (`REC-48`, `REC-128`, `REC-129`, sustituidos por `REC-140`).
- Cuenta opcional/consentimiento explícito de `REC-81`: sólo está implementada la sesión anónima.
- Panel de trazabilidad en la interfaz: existió históricamente (`REC-134`) y fue retirado por `REC-136`.
- Despliegue cloud (GCP, Cloud Run, Artifact Registry): **no existe**. El acceso público documentado es un túnel Cloudflare temporal.

Estos elementos se conservan en Jira y en la documentación histórica como decisiones o deuda, **sin borrarlos y sin inventar su implementación**.

---

## 3. Arquitectura

```text
Navegador / PWA React 19 + Vite + Tailwind
        │  fetch('/api/...')
        ▼
Nginx (frontend, puerto interno 8080)
        │  proxy_pass http://backend:8000/
        ▼
FastAPI (main.py + rutas_db.py)
   ├── YOLO11n best.pt  →  /predict
   ├── validación, CSP, CORS, rate limit
   └── MySQL 8 (ecoscan)
```

Puertos publicados en Docker: MySQL `127.0.0.1:3307`, backend `127.0.0.1:8000`, frontend `127.0.0.1:5173`. Los tres servicios tienen healthchecks y los contenedores no ejecutan como root (`appuser`, `nginx`).

Versiones principales: Python 3.13 en backend/CI, Node 22 en CI y `node:20-alpine` en la imagen frontend, MySQL 8.0, FastAPI 0.165.0, Ultralytics 8.4.215, React 19.2.x, Vite 8.3.x, Tailwind 3.4.x.

---

## 4. Módulos reales de la interfaz

La navegación es **Menú Principal + 4 módulos**. No hay pestaña separada de “Impacto”: está integrada en el Eco-Simulador RM.

| Módulo | Qué hace con datos reales |
|---|---|
| **Menú Principal** | Presentación del producto y accesos a los módulos (`REC-130`). |
| **Escáner IA** | Cámara web/rear o carga de imagen (incluye HEIC), vista previa, `POST /predict`, confianza visible, instrucciones de reciclaje/reutilización y pasos (`REC-46`, `REC-98`, `REC-101`, `REC-131`, `REC-133`). |
| **Puntos Limpios RM** | Mapa Leaflet/OSM, filtros por comuna y material, abierto/cerrado según horario, “Cómo llegar” y orden por cercanía con geolocalización autorizada (`REC-47`, `REC-124`–`REC-127`, `REC-144`, `REC-145`). |
| **Eco-Simulador RM** | Impacto automático de agua, CO₂ y residuos desde MySQL, más galería de consejos y videos (`REC-140`, `REC-160`). Sin sliders ni escenarios manuales. |
| **Desafío Verde RM** | Hábitos, estadísticas e insignias derivadas de los escaneos; 25 preguntas, 5 por ronda sin repetir (`REC-49`, `REC-137`, `REC-139`). |

La interfaz está en español, es mobile-first y no muestra códigos REC, pendientes ni avisos internos (`REC-66`, `REC-97`, `REC-99`, `REC-136`).

---

## 5. Flujo de reconocimiento de residuos

`POST /predict` (`ecoscan-backend/main.py`):

1. `id_sesion` opcional; si llega, se valida con `^[A-Za-z0-9_-]{1,64}$` y se inserta en `sesion` con `INSERT IGNORE`.
2. Límites: 10 MB por `Content-Length` y por lectura real; whitelist MIME (incluye `application/octet-stream` si el contenido valida como imagen); `Image.verify()`; EXIF; máximo 8000×8000.
3. Se calcula la nitidez, pero **no se rechaza antes de inferir**.
4. YOLO11n ejecuta la inferencia; cada caja con `confidence >= 0,50` se acepta. Las tres clases positivas son `Carton`, `Plastico`, `Aluminio`.
5. Si **no hay detecciones** y la imagen es borrosa, se devuelve rechazo por nitidez; si hay detecciones, se aceptan aunque la foto tenga poca nitidez.
6. `escaneos` se escribe sólo con detecciones aceptadas; `inferencia` registra `OK`, `CONFIANZA_BAJA`, `SIN_DETECCION` o `BORROSA`.
7. Errores controlados: `400` (archivo inválido), `413` (demasiado grande), `422` (falta archivo/campo), `429` (rate limit). Contrato con `codigo`, `mensaje` y `campo`.

El frontend muestra la confianza y advierte cuando una foto fue rechazada; el progreso del Desafío se actualiza con cada predicción exitosa.

---

## 6. Impacto, simulador y desafío

### Impacto

- Fuente: `GET /db/impacto` → `ecoscan.escaneos` de los **últimos 30 días**, con factores de `item_simulador`.
- Mapeo de factores en `rutas_db.py`: `item_simulador` `1 = plástico`, `2 = aluminio`, `3 = cartón`. Es distinto del `id_material` de la tabla `material` (`1 = Cartón`, `2 = Plástico`, `3 = Aluminio`) que usa `main.py` al registrar inferencias; no mezclarlos.
- Sin escaneos, todas las cifras son cero: **no hay valores por defecto ni entradas manuales**.
- Devuelve `agua_litros`, `co2_kg`, `residuos_kg`, equivalencias y factores.
- Filtro opcional por `id_sesion`.

### Desafío Verde

- Banco de 25 preguntas en `trivia.js`; rondas de 5 sin repetir, PRNG `mulberry32`, baraje Fisher–Yates, prioridad de preguntas no vistas y reinicio al agotar el banco.
- No usa API ni tabla de preguntas.
- El avance **ya no se marca manualmente**: cada escaneo incrementa totales y conteo por material en `localStorage`; de ahí se derivan 4 hábitos y la insignia “Guardián Verde” (`REC-137`).

---

## 7. Datos y persistencia

`docker/mysql/init/01_schema.sql` define **15 tablas**:

`banner_impacto`, `comuna`, `contenedor`, `escaneos`, `habito`, `habito_cumplido`, `inferencia`, `instruccion`, `item_simulador`, `material`, `paso_instruccion`, `punto_limpio`, `punto_material`, `recurso_externo`, `sesion`.

`02_seed.sql` carga 48 escaneos históricos, 3 ítems del simulador, 4 materiales de catálogo y 35 puntos limpios (10 propios y 25 externos con coordenada aproximada y procedencia visible). **25 puntos externos siguen pendientes de validación en terreno y de materiales oficiales** (`REC-155`, `REC-156`).

Retención y respaldos:

- `/db/mantenimiento/retencion` anonimiza a 6 meses y elimina a 12; **no está programado**.
- `respaldar_mysql.py` hace `mysqldump` + gzip; **tampoco programa la tarea**.

---

## 8. API principal

### Backend general

| Método | Ruta | Uso |
|---|---|---|
| `GET` | `/`, `/version`, `/health`, `/v1/models`, `/v1/models/{id}` | Estado, versión de modelo/dataset y healthcheck |
| `POST` | `/predict` | Reconocimiento de residuos |

### Router `/db`

`/db/materiales`, `/db/materiales/{id}/instrucciones`, `/db/banners`, `/db/inferencias`, `/db/reporte/inferencias.csv`, `/db/comunas`, `/db/puntos`, `/db/simulador`, `/db/impacto`, `/db/habitos`, `/db/mantenimiento/retencion`, `/db/sesiones`, `/db/sesiones/{id}/habitos`, `/db/sesiones/{id}/habitos/{id_habito}`.

Todas las consultas son parametrizadas y la salida HTML del mapa se escapa (`REC-108`). La API usa CORS por entorno, sin comodín (`REC-105`).

---

## 9. Configuración (sólo nombres de variables)

No se registran valores reales de `.env`. Nombres presentes en las plantillas y el código:

- Stack/MySQL: `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_DB`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST_PORT`, `BACKEND_MYSQL_HOST`.
- Backend: `CORS_ORIGINS`, `LIMITE_PREDICT_MINUTO`, `RED_PROXY_CONFIABLE`, `UMBRAL_CONFIANZA`, `UMBRAL_NITIDEZ`, `MODEL_PATH`, `DATASET_VERSION`, `DIRECTORIO_BACKUPS`.
- Frontend: `VITE_API_URL`.
- Entrenamiento: `ROBOFLOW_API_KEY`.

Plantillas: [`../.env.example`](../.env.example) y [`../ecoscan-backend/.env.example`](../ecoscan-backend/.env.example). **Unificadas el 20-11-2026:** ambas usan `UMBRAL_NITIDEZ=50`, igual que el valor por defecto de `main.py` y de `docker-compose.yml`.

Variables **obligatorias** para el compose: al menos `MYSQL_ROOT_PASSWORD` y `MYSQL_PASSWORD`; `MYSQL_DATABASE`/`MYSQL_DB` debe resolver a `ecoscan`. El compose falla explícitamente si falta la contraseña root.

---

## 10. Ejecución y pruebas

Desde `Fase 3/`:

```bash
copy .env.example .env        # editar credenciales propias
docker compose up --build -d
docker compose ps             # los 3 servicios "healthy"
```

Para apagar: `docker compose down`. **`docker compose down -v` borra volúmenes** y no forma parte de la operación habitual: sólo se usa si se decide expresamente reconstruir desde cero.

Backend local: `python -m venv venv`, `pip install -r requirements.txt`, `python main.py`.  
Frontend local: `npm install`, `npm run dev`.

Pruebas documentadas con fecha:

| Prueba | Estado vigente |
|---|---|
| `pytest -q` | 22 pruebas en evidencia local; 36 en CI/auditoría posterior |
| `npm run test:unit` | 24 pruebas tras PR 2 (`vitest_desafio.txt`) |
| `npm run test:e2e` | 4 pruebas Cypress (no corren en CI) |
| WebKit | verificación local con `scripts/verificar_webkit.mjs` |
| CI | backend: pytest + cobertura + `pip-audit`; frontend: `npm ci` → `build` → `test:unit` → `npm audit` |

El orden `build → test:unit` y el trigger `fix/**` son el fix de PR 1; no volver a describirlos como pendientes.

---

## 11. BPMN y entregables documentales

- Paquete v3: **14 modelos BPMN 2.0** (`01`…`14`), un archivo por modelo, corregidos sobre los mismos 8 `.diag` de la versión anterior. Validación: 0 solapes, 0 nodos aislados, 0 `BPMNShape`/`BPMNEdge` faltantes. Formato de entrega: **Bizagi Modeler 4.3.0008**.
- Modelo `12` usa la decisión **“¿Continuar con otra ronda?”**, coherente con `trivia.js`.
- Modelo `01` fue importado correctamente en Bizagi; la importación de `02`–`14` queda como tarea pendiente de entrega, no como funcionalidad de la app.
- Los tickets BPMN reales son `REC-72`…`REC-85`; los modelos v4 y las capturas antiguas son referencia histórica, no sustituyen al paquete v3.

---

## 12. Trazabilidad Jira y criterios de aceptación

| Recurso | Contenido |
|---|---|
| [`AUDITORIA_JIRA.md`](AUDITORIA_JIRA.md) | Auditoría completa, alineamientos e incongruencias |
| [`jira/CONTRASTE_161.md`](jira/CONTRASTE_161.md) / `.csv` | **Contraste de los 161 issues**, uno por uno, contra el repo |
| [`jira/INVENTARIO_REC.csv`](jira/INVENTARIO_REC.csv) | Inventario normalizado: 161 filas, épica, estado, fechas, sprint |
| [`jira/MAPEO_CLAVES_REALES.md`](jira/MAPEO_CLAVES_REALES.md) | Claves `REC-162`…`REC-170` inexistentes y su destino real |
| [`jira/BACKLOG_PROPUESTO.md`](jira/BACKLOG_PROPUESTO.md) | Propuesta original y **backlog ejecutado en Jira el 20-11-2026** (30 cambios) |
| [`jira/CAMBIOS_JIRA_PROPUESTOS.csv`](jira/CAMBIOS_JIRA_PROPUESTOS.csv) | 30 filas ejecutadas en Jira el 20-11-2026 |
| [`jira/CRITERIOS_ACEPTACION.md`](jira/CRITERIOS_ACEPTACION.md) | AC reales del plan de pruebas y dónde pegarlos |
| [`pruebas/MATRIZ_DE_PRUEBAS_EcoLearn_Oficial.xlsx`](pruebas/MATRIZ_DE_PRUEBAS_EcoLearn_Oficial.xlsx) | **Matriz oficial vigente**: 97 casos (6 de Infraestructura Docker), trazabilidad `REC-1`…`REC-161` y dashboard con 3 gráficos |
| [`pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx`](pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx) | 40 casos con columna “Criterios de aceptación” (fuente histórica de AC) |

**Ningún issue de Jira tiene campo de criterios de aceptación.** Los AC vigentes se toman del plan de pruebas; no se inventan criterios nuevos. El 20-11-2026 se aplicaron como comentarios en 17 tickets abiertos, con referencia al plan en las épicas `REC-20`, `REC-21` y `REC-24`. Las claves `REC-162`, `REC-167` y `REC-170` no existen: el máximo real es `REC-161`; se trataron como “verificado, sin cambio”. El bug del Desafío y el fix de CI están mergeados en PR 2 y PR 1 respectivamente; los umbrales por clase siguen fuera de `main`.

---

## 13. Deuda conocida (no ocultar en la defensa)

1. `mAP@50 = 0,562 < 0,65` (`REC-63`).
2. UAT con usuarios reales y SUS no ejecutadas (`REC-18`, `REC-70`).
3. CORS de producción sin dominio definitivo (`REC-105`).
4. Clave histórica de Roboflow pendiente de rotación (`REC-64`, `REC-122`); nunca se escriben valores en el repo ni en Jira.
5. 25 puntos externos con coordenadas y materiales por validar (`REC-155`, `REC-156`).
6. Horarios con bloques múltiples y cierres parciales no implementados (`REC-154`).
7. Respaldo y retención existen como código, pero no están programados.
8. Sin autenticación por diseño: `id_sesion` es controlado por el cliente. Aceptable para demo académica, no para datos reales.
9. Rate limit en memoria por IP: detrás de NAT/túnel varios visitantes comparten cuota.
10. `npm audit` reporta vulnerabilidades *moderate* por debajo del umbral `high`; no se aplicó el arreglo breaking.
11. **Resuelto:** los cambios de `docker-compose.yml` (`BACKEND_MYSQL_HOST`, `extra_hosts`) y `main.py` (CSP relajada sólo en `/docs`, `/redoc`, `/docs/*`) quedaron commiteados en `d85d5cd` y subidos a `origin/main`.
12. **Resuelto:** los dos XLSX byte-idénticos se consolidaron en `docs/requisitos/EcoScan_Requisitos_Funcionales.xlsx`; la copia de `Fase 2/Evidencia/` se eliminó y sustituyó por un README puntero.

---

## 14. Jerarquía documental

1. **Este documento** — alcance, nombres y flujos vigentes.
2. [`DECISIONES.md`](DECISIONES.md) — decisiones técnicas y su justificación (actualizar líneas citadas y número de tablas).
3. [`ENTREGA.md`](ENTREGA.md) — guía operativa de entrega (actualizar conteos de pruebas y nombres de módulos).
4. [`AUDITORIA_JIRA.md`](AUDITORIA_JIRA.md) y [`jira/`](jira/) — verdad del tablero y cambios aplicados (20-11-2026).
5. `ESTUDIO_PROYECTO_TITULO.md`, `evidencia/` y `pruebas/` — registros históricos con fecha; se conservan, pero no redefinen el alcance vigente.

Cualquier corrección futura debe actualizar primero este archivo y el contraste de Jira, y después los documentos históricos, para evitar que el tablero y la documentación vuelvan a divergir.
