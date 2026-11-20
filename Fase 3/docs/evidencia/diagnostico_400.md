# Diagnóstico y corrección de respuestas 400 en `/api/predict`

> Estado: **FASE 0, 1, 2, 4 y 5 completadas. FASE 3 pendiente del dataset real.**
> Evidencia sanitizada: sin rutas personales, sin valores de `.env`, sin secretos.
> Rutas relativas a `Fase 3/`. **No se hizo push.**

---

## Resumen ejecutivo

El 400 que veía el usuario tenía **doble causa**:

1. **Backend:** `UMBRAL_NITIDEZ=100` rechazaba por blur **antes** de llamar al modelo. Una caja lisa con logo tiene Laplaciano ~20 y nunca llegaba a YOLO (`ecoscan-backend/main.py:356-373` en la versión diagnosticada).
2. **Frontend:** el mensaje específico se lanzaba, pero el `catch` genérico lo sobrescribía con *"No se pudo analizar la imagen en este momento. Revisa tu conexión…"* (`ecoscan-frontend/src/App.jsx:718-721,754-758` en la versión diagnosticada).

Ambas están corregidas. Además se cerraron cuatro hallazgos secundarios: contrato único de errores, rate limit por IP real, logging de rechazos y un `CHECK` de MySQL que impedía guardar detecciones rechazadas.

---

## FASE 0 — Línea base

- Los contenedores corrían el código de `HEAD`: `sha256sum /app/main.py` dentro del contenedor = `Get-FileHash` del working tree = `f7e7155a07bf35e8fd356e0d66be23c889dbbaf1720a98620f2048bac112ebe4`.
- Historial del blur: `git log --follow -S 'Laplacian'` → `d69482a` (REC-13). El umbral `100` nunca cambió; `0198af2` solo movió el archivo a `Fase 3`.
- `origin/main = bafff77`. En ese momento `HEAD = 8b9c194` (2 commits locales: `6d48da9`, `8b9c194`).

---

## FASE 1 — Reproducción y causa raíz

### 1.1 Reproducción real

Foto sintética equivalente a la descrita (superficie lisa de cartón con logo), subida por el `input[type=file]` real en `http://127.0.0.1:5173`:

```
⚠️ No se pudo completar el análisis
No se pudo analizar la imagen en este momento. Revisa tu conexión y vuelve a intentarlo.
🔁 Reintentar
```

La petición `/api/predict` se ejecutó y devolvió 400; no hubo fallo de red ni de CORS.

### 1.2 Aislamiento de variables

Misma foto lisa, probada por directo (`8000`) y por proxy (`5173`):

| Variante | Laplaciano | Resultado |
|---|---|---|
| `carton_liso.jpg`, `image/jpeg` | 20.6 | 400 `BORROSA` (directo y proxy) |
| reescalada a 1280 px | 2.24 | 400 `BORROSA` |
| sin EXIF | 23.45 | 400 `BORROSA` |
| PNG RGB / RGBA | 20.6 | 400 `BORROSA` |
| `application/octet-stream` | 20.6 | 400 `BORROSA` |
| versión con ruido | 2904.68 | 200 |

**Solo cambia el resultado la varianza del Laplaciano.** MIME, formato, EXIF, escala y modo de color no influyen. La hipótesis inicial de MIME quedó descartada; el cambio de `octet-stream` ya realizado se conserva, pero no es la causa.

Rango observado en fotos reales con 200: **174.53 – 14873.57**. Las 3 fotos de `ecoscan-frontend/public/galeria/` daban 200 (Laplaciano 473.57 / 498.83 / 2604.7).

### 1.3 Hallazgos secundarios

- Los 429 aparecían porque **todos los visitantes comparten la IP de nginx** (`172.18.0.4`): `request.client.host` en `main.py:41,63-69` (versión anterior).
- `except: pass` al guardar la inferencia `BORROSA` ocultaba errores de BD.
- El `detail` de algunos 400 era un **string**, no `{"codigo","mensaje","campo"}`.
- `ck_inf_ok_material` en `Fase 2/Evidencia/BASE DE DATOS/01_EcoScan_Esquema_MySQL.sql:171` exigía `(resultado='OK') = (id_material IS NOT NULL)`, por lo que fallaba al guardar `CONFIANZA_BAJA` con la clase detectada.

---

## FASE 2 — Correcciones aplicadas

| Commit | Cambio | Evidencia |
|---|---|---|
| `6d48da9` | `application/octet-stream` solo se acepta si `Image.open()` valida el contenido | conserve; no es la causa del 400 |
| `8b9c194` | CORS/CSP por entorno, sin `"*"` | `main.py:167-170,201-205` |
| `045b9f7` | Contrato único `{"codigo","mensaje","campo"}` en todo 4xx; log de rechazo; `RequestValidationError` convertido | `main.py:79-89,152,175-181` |
| `86be6f7` | Nitidez normalizada a 640 px; **YOLO primero**; 200 con `calidad_imagen` si hay detecciones; 400 solo si no hay detecciones y nitidez < umbral | `main.py:124-137,329-330,493,520-538,605-608` |
| `f82f420` | Rate limit por IP real: `X-Real-IP`/`X-Forwarded-For` solo desde `RED_PROXY_CONFIABLE` | `main.py:57-66,91-113,139-149`; `nginx.conf:12-13`; `.env.example:22` |
| `9859e3e` | Migración de `ck_inf_ok_material`: solo `OK` exige `id_material` | `main.py:296-309` |
| `69b4717` | `ErrorApi` + mapa de 7 códigos; aviso `baja_nitidez`; resize a 1600 px; sin mensaje genérico | `App.jsx:9-27,29-53,434,766-816,1290-1293,1322` |
| `6cded14` | El mapa local gana sobre `detail.mensaje` (evita textos internos/genéricos) | `App.jsx:770-778` |
| `974560f` | Tests de los 9 cambios anteriores | ver FASE 4 |
| `48f2b52`, `c565005` | Informe consolidado y precisión de la calibración (26 fotos sin objetos lisos; umbral 50 solo sin detecciones; no es validación del split de test) | este documento |
| `e0204ac` | PWA: caché versionada `ecolearn-v2-` + `cleanupOutdatedCaches` | `vite.config.js:8-17`; `src/sw.test.js`; ver verificación 3 |
| `cbd87b8` | Comentario de nitidez alineado con la evidencia | `main.py:324-330` |
| `7b8750f` | El gateway del puerto publicado no puede falsificar el `X-Forwarded-For` | `main.py:57-60,91-113`; ver verificación 4 |

### Calibración del umbral (solo orientativa; NO es validación con el split de test)

Cálculo idéntico al del backend (grayscale, Laplaciano `CV_64F`, reescalado solo si el lado largo > 640 px) sobre **26 fotos reales disponibles**. **Ninguna de esas 26 fotos contiene un objeto liso como el caso reportado**: son fotos con textura, etiquetas o reflejos.

- mínimo **128.39**, p05 **324.68**, mediana **2527.54**, máximo **14873.57**.
- Con `UMBRAL_NITIDEZ=50`, **ninguna de esas 26 habría sido rechazada por la regla de nitidez**. El caso liso con logo "IDEAL" (Laplaciano 20.6) **no está incluido** en la muestra; se reprodujo por separado con una imagen sintética equivalente.
- **La regla de nitidez solo se evalúa cuando el modelo NO devuelve detecciones** (`main.py:520`): con detecciones se responde 200 y, como máximo, se añade `aviso: "baja_nitidez"` (`main.py:605-608`). Por eso el umbral 50 no puede rechazar una foto que el modelo sí clasificó.
- El valor anterior (100) también habría aceptado estas 26 fotos; bajarlo a 50 solo amplía el margen para fotos de poca textura **cuando no hay detecciones**. Esto **no sustituye** la evaluación con el split oficial de test, que sigue pendiente (FASE 3).

El valor es configurable por entorno (`main.py:330`, `.env.example:24`).

---

## Antes / después (evidencia real)

`carton_blur_1_2.jpg` y `carton_blur_1_5.jpg` son versiones atenuadas de `ecoscan-frontend/public/galeria/carton.jpg`, generadas solo para la verificación.

| Imagen | Nitidez | Antes | Después |
|---|---|---|---|
| `carton_liso.jpg` (sintética) | 20.6 | 400 `BORROSA` | 400 `IMAGEN_BORROSA` (sin detecciones) con mensaje accionable |
| `carton_blur_1_2.jpg` | 42.45 | habría sido 400 `BORROSA` | **200** + detección + `aviso: "baja_nitidez"` |
| `carton_blur_1_5.jpg` | 24.41 | habría sido 400 `BORROSA` | **200** + detección + `aviso: "baja_nitidez"` |
| `carton_suave.jpg` (sin detecciones) | < 50 | 400 `BORROSA` | 400 `IMAGEN_BORROSA` con "*Acércate y mejora la luz*" |

Salida real por proxy local (`/api/predict`):

```json
{"detecciones":[{"clase":"Aluminio","confianza":0.62}],
 "calidad_imagen":{"nitidez":42.45,"aviso":"baja_nitidez"}}
HTTP=200
```

```json
{"detail":{"codigo":"IMAGEN_BORROSA",
 "mensaje":"No se pudo identificar el residuo y la foto tiene poca definición. Acércate y mejora la luz.",
 "campo":"file"}}
HTTP=400
```

### Verificación en navegador

Con el bundle nuevo cargado:

- `/api/predict` → **200**; se muestran "Materiales Identificados (1)" y el aviso discreto *"La foto tiene poca definición; revisa el resultado."*; **sin** bloque de error.
- Foto sin detecciones → alert con el mensaje específico de `IMAGEN_BORROSA`; **ya no aparece** *"Revisa tu conexión y vuelve a intentarlo"*.
- Sin errores JavaScript de aplicación. El único mensaje de consola es el log esperado del navegador ante el HTTP 400.

> Nota histórica: el primer intento en navegador sirvió un bundle antiguo desde la caché del service worker (PWA) y apuntaba a `127.0.0.1:8000`. Ese riesgo quedó corregido en `e0204ac` (caché versionada + limpieza automática); la verificación 3 demuestra la actualización sin limpiar nada a mano. La petición correcta es `/api/predict` (mismo origen, puerto `5173`).

### Verificación por túnel

Túnel Cloudflare existente (URL temporal, no permanente):

- `GET /api/health` → 200, `mysql_conectado: true`, `modelo_activo: "best.pt"`.
- `POST /api/predict` con `carton_blur_1_2.jpg` → **200**, `nitidez 42.45`, `aviso "baja_nitidez"`.

---

## FASE 4 — Pruebas

```
backend:  pytest tests -q          → 36 passed, 1 warning  (EXIT=0)
frontend: npm run test:unit        → 17 passed (2 archivos) (EXIT=0)
frontend: npm run build            → build OK, 9 entradas precacheadas (EXIT=0)
```

Cobertura nueva: contrato de los 7 códigos, foto lisa con detección → 200 + aviso, foto normal sin aviso, log de rechazo (sin guardar imagen), IP falsificada, cuotas independientes por visitante, gateway del puerto publicado (2 pruebas), constraint de MySQL, PWA (3 pruebas) y 9 pruebas de UI (mapeo por código, 200 sin detecciones como aviso, baja nitidez con resultados).

---

## FASE 5 — Despliegue

```
docker compose down -v       → EXIT=0   (despliegue inicial, volumen nuevo)
docker compose up --build -d → EXIT=0
docker compose down          → EXIT=0   (sin -v, tras las correcciones)
docker compose up --build -d → EXIT=0
docker compose ps           → backend / frontend / mysql: Up (healthy)
```

- `sha256sum /app/main.py` en el contenedor = `Get-FileHash` local = `a14b829f5e6d3d2b1f927a1791ec5978645bec6313ff8fba6e330a2acd94115c`.
- `SHOW CREATE TABLE ecoscan.inferencia` tras el arranque confirma la migración:
  `CONSTRAINT ck_inf_ok_material CHECK (((resultado <> _utf8mb4'OK') or (id_material is not null)))`.
- `best.pt` sin cambios: `ca855386ebb5a45fe8eeb52f3d43a88d2f4c3fe830506ed31ceb4f21e1fbb9b7`.
- `ecoscan-frontend/src/App.jsx`: `debe0ae8f83d1b6be76c61706047e558c8d474a74785a136c9b33a7b2394749c`.

### Estado Git

```
HEAD        = 7b8750f
origin/main = bafff77
14 commits locales, sin push
```

Commits locales (en orden): `6d48da9`, `8b9c194`, `045b9f7`, `86be6f7`, `f82f420`, `9859e3e`, `69b4717`, `6cded14`, `974560f`, `48f2b52`, `c565005`, `e0204ac`, `cbd87b8`, `7b8750f`.

Sin versionar, creado solo para diagnóstico: `ecoscan-backend/tests/diagnostico_400.py`. **El dataset YOLO no se copió ni se versionó.**

---

## Verificaciones previas al push (solicitadas)

### 1. Foto lisa reportada por `/api/predict`

No se recibió el archivo original: se usó una imagen sintética equivalente (superficie lisa con logo, Laplaciano **20.6**, 640×480 sin reescalado).

- `POST http://127.0.0.1:5173/api/predict` → **HTTP 400**.
- JSON: `{"detail":{"codigo":"IMAGEN_BORROSA","mensaje":"No se pudo identificar el residuo y la foto tiene poca definición. Acércate y mejora la luz.","campo":"file"}}`.
- Detecciones: **0** (por eso se evalúa la nitidez y se devuelve 400).
- En pantalla: `⚠️ No se pudo completar el análisis`, el mensaje citado y el botón `🔁 Reintentar`. **No aparece** "Revisa tu conexión…". La pestaña de red confirma `/api/predict` → 400 (no es fallo de red).
- **Sí, devuelve 400 `IMAGEN_BORROSA`, tal cual.**

### 2. Actualización sobre base existente (sin `-v`)

Entorno aislado (red y volumen propios), sin tocar el volumen real:

1. Imagen del backend de `bafff77` (solo `main.py` difiere) sobre BD inicial → constraint viejo `(resultado='OK') = (id_material is not null)`. Insertar `CONFIANZA_BAJA` con `id_material` falla con **ERROR 3819** (bug reproducido).
2. Datos presentes: **62 filas** en `inferencia` (`OK 51`, `CONFIANZA_BAJA 10`, `BORROSA 1`). Con `bafff77` arriba, el constraint sigue viejo y las 62 filas siguen ahí.
3. Levantar **HEAD sobre el mismo volumen (sin `-v`)**: el constraint pasa a `(resultado <> 'OK' OR id_material IS NOT NULL)`, las **62 filas permanecen** y no hay avisos de migración en el log.
4. La inserción que antes fallaba ahora funciona (63 filas).
5. Reiniciar HEAD **dos veces más sin `-v`**: `Application startup complete`, **0 avisos/errores**, constraint nuevo y 63 filas intactas. El volumen conserva su fecha de creación original.

### 3. Service worker / PWA

- `registerSW.js` registra `/sw.js` con scope `/`.
- `vite.config.js:8-16`: `registerType: 'autoUpdate'`, `cacheId: 'ecolearn-v2-'`, `cleanupOutdatedCaches: true`.
- `dist/sw.js` generado y servido contiene `skipWaiting()`, `clientsClaim()`, `setCacheNameDetails({prefix:"ecolearn-v2-"})` y `cleanupOutdatedCaches()`.
- **Tests:** 3 pruebas nuevas (`src/sw.test.js`): 17 frontend en total.
- **Prueba manual sin limpiar nada:** cliente con bundle viejo `index-BELNuAx8.js` y caché `workbox-precache-v2-…`; se despliega el bundle nuevo en el **mismo origen**. Tras la navegación, el SW nuevo instala `ecolearn-v2--precache-v2-…`, **elimina la caché antigua** y en la navegación siguiente el DOM sirve `index-BdIWFyXa.js`. No se desregistró el SW ni se borraron cachés a mano. (La primera navegación activa el SW; la segunda ya entrega el `index.html` nuevo.)

### 4. Rate limit con `X-Forwarded-For`

**Hallazgo real corregido:** el gateway `172.18.0.1` está dentro de `RED_PROXY_CONFIABLE=172.18.0.0/16`, así que el XFF falsificado desde el puerto publicado **sí se respetaba**. `7b8750f` excluye la primera IP usable de cada red confiable (`main.py:57-60,91-113`).

Tras el arreglo, 31 `POST /predict` por grupo (sin body; el middleware cuenta antes de validar):

| Origen | Cabeceras | Resultado | IP registrada en el log |
|---|---|---|---|
| `127.0.0.1:8000` (publicado) | 31 XFF **distintos** | 30×422, **429** en la 31.ª | `172.18.0.1` (ignorados) |
| nginx `172.18.0.4` | XFF fijo `203.0.113.77` | 30×422, **429** en la 31.ª | `203.0.113.77` (respetado) |

2 pruebas nuevas; 36 backend en total.

### 5. Revisión de los commits antes de push

- `git log origin/main..HEAD --stat`: **14 commits**, 8 archivos tocados: `.env.example`, `docs/evidencia/diagnostico_400.md`, `backend/main.py`, `backend/tests/test_main.py`, `frontend/src/App.jsx`, `frontend/src/App.test.jsx`, `frontend/src/sw.test.js`, `frontend/vite.config.js`.
- Diff completo (1231 líneas): **0 coincidencias** de tokens de Google, claves de API, tokens de GitHub, credenciales de Roboflow, rutas personales de Windows ni carpetas de dependencias instaladas.
- `password=` aparece **1 vez** como contexto del hunk (placeholder `cambiar_esta_clave` en `.env.example`); ningún valor real de `MYSQL_PASSWORD` ni `MYSQL_ROOT_PASSWORD` figura en el diff. Los demás valores coincidentes son defaults públicos ya documentados en `.env.example`.
- No entran en el push: `diagnostico_400.py`, el dataset, `.env`, `node_modules`. `best.pt` no fue modificado ni aparece en el diff.
- Este informe: 0 rutas absolutas, 0 secretos, 0 valores de `.env`.

### 6. Redacción de la calibración

Corregida en este informe y en `main.py:324-330`: las 26 fotos **no incluyen objetos lisos**, el caso "IDEAL" se reprodujo aparte, el umbral 50 **solo se evalúa cuando no hay detecciones** y **no está validado con el split de test** (FASE 3 sigue pendiente).

---

## FASE 3 — Pendiente

No se ejecutó: el dataset real con `data.yaml` y `test/images` no está disponible en el repositorio ni en el entorno. El usuario eligió continuar sin él. La métrica oficial **mAP@50 = 0.562** no se tocó. Cuando se facilite la ruta fuera del repo, se calcularán métricas con el split oficial sin mover ni versionar las imágenes.

---

## Push

**Pendiente de autorización explícita.** No se hizo push, no se usó `--force` y no se reescribió historial.
