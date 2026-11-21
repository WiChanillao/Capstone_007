# Trazabilidad integral — datos, API, BD, frontend, BPMN y Jira

Este documento cierra la revisión del **20-11-2026**. Describe el recorrido real
de la información en `main @ 6608c70`, con rutas verificables. No incorpora
funcionalidades que no estén en el código.

## 1. Cadena de datos de extremo a extremo

| Etapa | Evidencia real | Resultado |
|---|---|---|
| Origen y entrenamiento | [`crisp-dm/CrispDM_Ecolearn.ipynb`](crisp-dm/CrispDM_Ecolearn.ipynb) y [`crisp-dm/capstone_CRISDM_limpio.ipynb`](crisp-dm/capstone_CRISDM_limpio.ipynb) | Roboflow `capstone-s2mpp` v1 en formato `yolov11`; 485 polígonos convertidos a bounding boxes; oversampling de Aluminio (+252 imágenes); particiones 1112 train / 61 valid / 31 test; 3 clases: `Aluminio`, `Carton`, `Plastico`. |
| Métrica oficial | [`crisp-dm/CrispDM_Ecolearn.ipynb`](crisp-dm/CrispDM_Ecolearn.ipynb) y [`pruebas/PLAN_DE_PRUEBAS_EcoLearn.md`](pruebas/PLAN_DE_PRUEBAS_EcoLearn.md) | `mAP@50 = 0,562` en validación (61 imágenes / 109 instancias). La meta `≥ 0,65` **no** está alcanzada; deuda abierta en `REC-63`. |
| Modelo versionado | [`../ecoscan-backend/best.pt`](../ecoscan-backend/best.pt), cargado en [`../ecoscan-backend/main.py`](../ecoscan-backend/main.py) (`MODEL_PATH`, `model.names`) | Checkpoint YOLO11n, 5.506.586 bytes, SHA-256 `CA855386EBB5A45FE8EEB52F3D43A88D2F4C3FE830506ED31CEB4F21E1FBB9B7`, `nc=3`, `names={0:Aluminio, 1:Carton, 2:Plastico}`, entrenado con Ultralytics 8.4.175; runtime declarado 8.4.215. |
| Inferencia | [`../ecoscan-backend/main.py`](../ecoscan-backend/main.py) (`/predict`) | Umbral global `0,50`; rate limit 30/IP/min; validación real de imagen (MIME, 10 MB, 8000 px, EXIF); aviso de baja nitidez sin rechazo si hay detecciones; conteo por clase y latencia. |
| Persistencia | [`../ecoscan-backend/main.py`](../ecoscan-backend/main.py) y [`../ecoscan-backend/rutas_db.py`](../ecoscan-backend/rutas_db.py) (`guardar_resultado_escaneo`) | `/predict` escribe en una transacción `sesion`, `escaneos` e `inferencia` con `id_sesion` anónimo. La imagen **no** se persiste: sólo metadata. `POST /db/inferencias` existe para cargas de prueba. |
| Base de datos | [`../docker/mysql/init/01_schema.sql`](../docker/mysql/init/01_schema.sql) y [`../docker/mysql/init/02_seed.sql`](../docker/mysql/init/02_seed.sql) | MySQL 8, base `ecoscan`, **15 tablas**; 14 con filas semilla (`habito_cumplido` no se siembra). Incluye 48 escaneos y 60 inferencias semilla históricas. |
| Consultas y agregación | [`../ecoscan-backend/rutas_db.py`](../ecoscan-backend/rutas_db.py) (`/db/*`) | Materiales, instrucciones, banners, comunas, 35 puntos limpios, simulador, impacto de 30 días, hábitos y sesiones. |
| Frontend | [`../ecoscan-frontend/src/App.jsx`](../ecoscan-frontend/src/App.jsx), [`../ecoscan-frontend/src/MapaPuntos.jsx`](../ecoscan-frontend/src/MapaPuntos.jsx) y [`../ecoscan-frontend/src/trivia.js`](../ecoscan-frontend/src/trivia.js) | Cuatro módulos: Escáner IA, Puntos Limpios RM, Eco-Simulador RM y Desafío Verde RM. `localStorage.ecolearn_id_sesion` + `/db/sesiones`; el resto de datos viene de `/db/impacto`, `/db/materiales`, `/db/puntos` y `/db/habitos`. |
| Pruebas | [`pruebas/MATRIZ_DE_PRUEBAS_EcoLearn_Oficial.xlsx`](pruebas/MATRIZ_DE_PRUEBAS_EcoLearn_Oficial.xlsx), [`evidencia/estado_pagina_2026-11-20/README.md`](evidencia/estado_pagina_2026-11-20/README.md) y [`../ecoscan-backend/tests/`](../ecoscan-backend/tests/) | Matriz oficial de 97 casos. La evidencia documental reporta **36 pruebas backend** (cobertura 74 %) y **24 frontend**; Cypress 4/4. Los conteos antiguos del plan (15/15 y 4/4) son instantáneas, no el estado final. |
| Procesos | [`bpmn/v3/README.md`](bpmn/v3/README.md) | 14 modelos BPMN vigentes, `REC-72`…`REC-85`; el histórico `v4_extendidos` se conserva como referencia. |
| Requisitos | [`jira/CONTRASTE_161.md`](jira/CONTRASTE_161.md), [`AUDITORIA_JIRA.md`](AUDITORIA_JIRA.md) §4, [`jira/BACKLOG_PROPUESTO.md`](jira/BACKLOG_PROPUESTO.md) §7 | 100 RF/RNF y `REC-1`…`REC-161`; fotografía anterior y estado vigente posterior al backlog aplicado (30 cambios verificados). |

## 2. API y base de datos

- **20 endpoints reales**: 6 en `main.py` (`/`, `/version`, `/health`, `/v1/models`,
  `/v1/models/{modelo_id}`, `/predict`) y 14 en `rutas_db.py` bajo `/db`.
- **15 tablas** en el esquema Docker canónico. La copia histórica
  [`bd/01_EcoScan_Esquema_MySQL.sql`](bd/01_EcoScan_Esquema_MySQL.sql) tiene 14 y
  no es la fuente de despliegue. El docstring de `rutas_db.py` ya distingue
  15 tablas de 14 tablas sembradas.
- Escrituras reales: `sesion` (`INSERT IGNORE`), `escaneos`, `inferencia`,
  `habito_cumplido`, anonimización a 6 meses y borrado a 12 meses.
- **Dos mapas de id distintos**: `material` 1=Cartón, 2=Plástico, 3=Aluminio;
  `item_simulador` 1=plástico, 2=aluminio, 3=cartón. No se deben mezclar.
- `/db/reporte/inferencias.csv` expone `materiales_detectados`,
  `total_objetos` y los campos de `escaneos`.

## 3. Alcance confirmado en la app

- La sesión es **anónima**: el único valor en `localStorage` es
  `ecolearn_id_sesion`; no hay login, cuenta opcional ni consentimiento
  explícito. `REC-81` se entrega como documento.
- El progreso y las insignias se derivan de `GET /db/impacto`, no de un
  `localStorage` de estadísticas.
- No hay marketplace, rutas optimizadas, PostGIS, Redis, colas ni deploy
  automático. El CI valida el repositorio en cada push; el despliegue local se
  documenta en [`../COMO_EJECUTAR.md`](../COMO_EJECUTAR.md).
- El alcance vigente está en [`DOCUMENTACION_GENERAL.md`](DOCUMENTACION_GENERAL.md);
  la arquitectura canónica en [`ARQUITECTURA.md`](ARQUITECTURA.md).

## 4. Riesgos y deuda declarada

| Riesgo | Estado |
|---|---|
| `mAP@50 = 0,562 < 0,65` | Deuda abierta (`REC-63`); no se disfraza como cumplida. |
| UAT/SUS | Protocolo documentado en [`pruebas/PROTOCOLO_UAT_SUS.md`](pruebas/PROTOCOLO_UAT_SUS.md); **no ejecutado**. El CSV de n=14 no es SUS. |
| Claves `REC-162`…`REC-170` | No existen en Jira; se documentan como históricas en [`jira/MAPEO_CLAVES_REALES.md`](jira/MAPEO_CLAVES_REALES.md). |
| Umbrales por clase / nivel “Posible” | Viven en una rama sin merge; `REC-103` es sólo umbral global. |
| 30 fotos y `data.yaml` con `test/images` | No están versionados; la medición con split oficial no se reprodujo dentro del repo. |
| Inferencias semilla del 2026-10-09 | Preceden al peso actual (2026-10-10): son datos históricos, no generados por este `best.pt`. |
| CORS de producción, rotación de clave Roboflow, puntos externos sin validar, horarios multi-bloque, respaldos y retención sin programar | Declarados en [`DOCUMENTACION_GENERAL.md`](DOCUMENTACION_GENERAL.md) §8. |

## 5. Presentación del repositorio

- Las capturas vigentes están en [`evidencia/capturas/`](evidencia/capturas/);
  las iteraciones superadas en `evidencia/capturas/historial/`.
- El DOCX duplicado `PLAN_DE_PRUEBAS_EcoLearn_CON_EVIDENCIA.docx` se movió a
  [`pruebas/historial/`](pruebas/historial/): su contenido es idéntico a
  `PLAN_DE_PRUEBAS_EcoLearn.docx` y la versión PDF histórica se conserva en
  `pruebas/`.
- `ecoscan-backend/tests/diagnostico_400.py` es una herramienta local de
  diagnóstico; se mantiene fuera del commit y se ignora explícitamente.
- El último chequeo público fue CI #54 en verde para `6608c70`.
