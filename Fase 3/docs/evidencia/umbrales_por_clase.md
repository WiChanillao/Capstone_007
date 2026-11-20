# Umbrales por clase y nivel "posible" (bloque 4)

Rama: `feature/umbrales-por-clase`, creada desde `main` (`62c73a2`).
Trabajo en worktree separado: **no se mezcla** con `experimento/generalizacion`.
Sin push. `best.pt` sin modificar (SHA-256
`CA855386EBB5A45FE8EEB52F3D43A88D2F4C3FE830506ED31CEB4F21E1FBB9B7`).

## 1. Backend (`ecoscan-backend/main.py`)

- Nuevas variables, **defaults que no cambian el comportamiento**:
  `UMBRAL_ALUMINIO`, `UMBRAL_CARTON`, `UMBRAL_PLASTICO` = `0,50`;
  `UMBRAL_POSIBLE` = `0,20`.
- `umbral_para(clase)` aplica el umbral de la clase; si la clase no está en el
  mapa, cae al `UMBRAL_CONFIANZA` global.
- Inferencia con **`model(image, imgsz=640)`** explícito.
- Una detección se acepta sólo si `conf >= umbral_para(clase)`. Si no llega al
  umbral pero sí a `UMBRAL_POSIBLE`, se devuelve en `detecciones_posibles`:
  **nunca** entra en `detecciones`, `conteo_materiales` ni en el aviso de
  baja nitidez como residuo confirmado.
- La respuesta `/predict` añade `detecciones_posibles`, `umbrales_por_clase` y
  `umbral_posible`. El log de predicción registra `posibles`.

## 2. Frontend (`ecoscan-frontend/src/App.jsx`)

- `detecciones_posibles` se normaliza por material y se deduplica.
- Aviso aparte con `role="note"`: **"Posible <material> (confianza baja) · NN%"**,
  con el texto "No se consideran seguros. Acércate y mejora la luz."
- No altera `elementosDetectados`, confianzas ni conteos: un "posible" no
  aumenta el impacto simulado.

## 3. Configuración

- `Fase 3/.env.example` y `ecoscan-backend/.env.example`: nuevas variables
  documentadas con los defaults `0,5` / `0,2`. Se corrige además el ejemplo de
  `UMBRAL_NITIDEZ` de 100 a 50 para igualar el default real del backend.
- `docker-compose.yml`: pasa `UMBRAL_CONFIANZA`, `UMBRAL_ALUMINIO`,
  `UMBRAL_CARTON`, `UMBRAL_PLASTICO` y `UMBRAL_POSIBLE` al contenedor.
- El `.env` real del worktree es local, está en `.gitignore` y su valor se
  genera al azar; **nunca se muestra** (se reporta como `***`).

## 4. Evaluación en test (sólo reporte, sin aplicar)

Script: `Fase 3/docs/experimentos/evaluar_umbrales.py`.
Una sola pasada de inferencia con conf=0,01 e `imgsz=640`; mismas detecciones
para ambos puntos de operación; IoU > 0,5. Detalle en
`evaluacion_umbrales_test.md` y `.json`.

| Clase | Instancias | Δ recall | Δ FP |
|---|---:|---:|---:|
| Aluminio | 8 | +0,000 | +2 |
| Cartón | 29 | +0,000 | +2 |
| Plástico | 24 | +0,208 | +6 |
| **Total** | 61 | **+0,082** | **+10** |

Lectura: Aluminio y Cartón no ganan recall y añaden FP; Plástico recupera 5
instancias a costa de 6 FP. **No se aplican los umbrales propuestos**: los
defaults siguen en 0,50 y la decisión pertenece a la matriz E0–E3 con 3
semillas y valid. Test se evaluó aquí una sola vez con fines de reporte.

## 5. Pruebas

- Backend: `python -m pytest tests -q` → **42 passed** (6 nuevos casos:
  `imgsz=640` explícito, defaults, `umbral_para`, decisión por clase, nivel
  "posible" separado y exposición de la configuración en la respuesta).
- Frontend: `npm run build` y `npm run test:unit` → **18 passed** en 2 archivos
  (nuevo caso: aviso "Posible Cartón (confianza baja)" sin contarlo como
  detectado). El build previo es necesario porque `sw.test.js` lee
  `dist/sw.js`.

## 6. Verificación Docker

Ejecutado desde el worktree de la rama: `docker compose down -v` y
`docker compose up --build -d`. Detalle en `docker_umbrales.txt`.

- `docker compose ps`: **3/3 healthy** (`ecolearn-backend`,
  `ecolearn-frontend`, `ecolearn-mysql`).
- `GET /health` en `127.0.0.1:8000/health` y `127.0.0.1:5173/api/health`:
  **200**, `status=ok`, `mysql_conectado=true`, `modelo_activo=best.pt`,
  `escaneos_registrados=48`.
- `POST /predict` sobre una foto de test: **200**, respuesta con
  `detecciones`, `detecciones_rechazadas`, `detecciones_posibles`,
  `umbral_confianza=0,5`, `umbrales_por_clase` = 0,5 / 0,5 / 0,5 y
  `umbral_posible=0,2`.
- Contraseña MySQL local del `.env`: `***` (aleatoria, no versionada).

## 7. Sin cambios

No se tocó el mAP@50 oficial 0,562, los pesos, las imágenes ni el dataset.
No se hicieron commits ni push.
