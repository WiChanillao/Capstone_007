# Auditoría del tablero Jira REC contra el código real — EcoLearn Chile / EcoScan

**Fecha de la auditoría:** 20-11-2026  
**Fuente del tablero:** exportación real desde la sesión del usuario en Brave  
(`Más acciones → Exportar → CSV: todos los campos`), 161 filas y 190 columnas.  
**Referencia de código:** `main @ af7d14d` (PR 1 y PR 2 mergeados).  
**Tipo de intervención:** solo lectura y exportación. **No se creó, editó ni cerró ningún issue en Jira.**

El inventario normalizado queda en [`jira/INVENTARIO_REC.csv`](jira/INVENTARIO_REC.csv).

---

## 1. Fotografía del tablero en vivo

| Concepto | Valor real |
|---|---:|
| Issues totales | 161 (`REC-1` … `REC-161`, sin huecos) |
| Historias | 92 |
| Tareas | 38 |
| Errores | 26 |
| Épicas | 5 |
| Finalizada / `Listo` | 144 |
| En curso | 8 |
| Tareas por hacer | 9 |
| En revisión | 0 |
| Prioridad `Medium` / `High` / `Low` | 109 / 6 / 46 |
| Issues con padres (no épicas) | 161/161: ningún huérfano |
| Campo “criterios de aceptación” en Jira | **No existe**; los AC están en el plan de pruebas, no en el CSV |

### Épicas reales

| Épica | Estado | Creada | Vencimiento | Hijos |
|---|---|---|---|---:|
| `REC-20` — Modelo de visión y dataset | En curso | 18/nov/26 | 30/nov/26 | 15 |
| `REC-21` — Base de datos MySQL | En curso | 18/nov/26 | 30/nov/26 | 16 |
| `REC-22` — Backend e integración | Finalizada | 18/nov/26 | **18/oct/26** | 28 |
| `REC-23` — Frontend y experiencia de usuario | Finalizada | 18/nov/26 | **18/oct/26** | 41 |
| `REC-24` — Documentación, pruebas y entrega | En curso | 18/nov/26 | 30/nov/26 | 56 |

`REC-22` y `REC-23` tienen **fecha de vencimiento anterior a la fecha de creación**. Es un dato del tablero a corregir, no una inferencia.

---

## 2. Lo que sí está alineado con `main @ af7d14d`

| Ticket | Estado real | Contraste con el código |
|---|---|---|
| `REC-103` | Finalizada | Umbral global `UMBRAL_CONFIANZA=0,50` aplicado en `POST /predict`. **No** es umbral por clase. |
| `REC-104` | Finalizada | Rechazo por nitidez cuando no hay detecciones, en `main.py`. |
| `REC-105` | En curso | CORS por entorno ya implementado; falta cerrar la política de **producción**. |
| `REC-106` | Finalizada | Rate limit 30/min por IP en `/predict`. |
| `REC-107` | Finalizada | Cabeceras de seguridad/CSP en el API (la relajación local para `/docs` está sin commitear). |
| `REC-137` | Finalizada | Progreso automático del Desafío Verde y estadísticas por escaneo; coincide con `trivia.js` y `App.jsx`. |
| `REC-140` | Finalizada | Impacto de los últimos 30 días desde `ecoscan.escaneos`; sustituye sliders/escenarios. |
| `REC-144`, `REC-145`, `REC-149`, `REC-152` | Finalizada | Mapa Leaflet/OpenStreetMap, corrección de capa gris, horarios NULL y geocodificación; `/api/db/puntos` responde 35 puntos. |
| `REC-160` | Finalizada | Galería de consejos y videos en el Eco-Simulador RM. |
| `REC-161` | Finalizada | Plan de pruebas con trazabilidad RF/RNF (40 casos en XLSX/MD). |
| `REC-63` | Tareas por hacer | `mAP@50 = 0,562` real, meta `≥ 0,65` no alcanzada. |
| `REC-64`, `REC-122` | En curso | Rotación de clave histórica y revisión del cuaderno; no se registran valores de credenciales. |
| `REC-65` | En curso | 25 puntos externos con coordenadas/materiales pendientes de validación. |
| `REC-18`, `REC-70`, `REC-19`, `REC-62` | Tareas por hacer | UAT/SUS, memoria/defensa y envío del PPT siguen abiertos. |

También están correctamente marcados como sustituidos o no implementados **en el resumen**: `REC-7` (Streamlit), `REC-8` (PostGIS), `REC-11` (offline-first/React 18), `REC-12` (árbol de decisión), `REC-13` (YOLOv8), `REC-14` (ficha dual con PostGIS), `REC-16`/`REC-68` (panel B2B/B2G).

---

## 3. Incongruencias detectadas

### 3.1 “Finalizada” donde el propio resumen dice “no implementada” o “sustituida”

| Clave | Resumen literal | Riesgo de lectura |
|---|---|---|
| `REC-7` | Herramienta interactiva ligera (Streamlit) - **no implementada** | `Finalizada` parece entrega de funcionalidad. |
| `REC-8` | Consultas de proximidad con PostGIS - **no implementadas** | Igual. |
| `REC-11` | Arquitectura offline-first y React 18 (**fuera de alcance real**) | Igual. |
| `REC-12` | Módulo de árbol de decisión en 2 toques (**no implementado**) | Igual. |
| `REC-13` | Escáner con YOLOv8 en PWA (**sustituido por YOLO11n**) | Igual. |
| `REC-14` | Ficha educativa dual y geolocalización PostGIS (**sustituida**) | Igual. |
| `REC-16` | Panel analítico B2B/B2G y mapas de calor (**no implementado**) | Igual. |
| `REC-68` | Panel B2B de reportes | Marcado `Finalizada` con etiqueta `b2b`, sin módulo en la app. |

**Interpretación correcta:** en estos casos “Finalizada” significa *decisión documentada/cerrada como fuera de alcance*, nunca *funcionalidad entregada*. Debe hacerse explícito en el estado, la resolución o el resumen.

### 3.2 Terminado en Jira, ausente en `main`

| Clave | Estado | Situación real |
|---|---|---|
| `REC-128` | Finalizada | “Guardar escenarios del simulador asociados a la sesión”: no hay lógica de escenarios en `ecoscan-frontend/src`; el impacto se calcula desde MySQL. |
| `REC-129` | Finalizada | “Comparar dos escenarios guardados del simulador”: mismo caso. |
| `REC-157` | Tareas por hacer | “La PWA sirve el bundle cacheado tras un despliegue”: `main` ya tiene `registerType: 'autoUpdate'`, `cacheId: 'ecolearn-v2-'` y `cleanupOutdatedCaches: true` con prueba en `sw.test.js`. El ticket está **atrasado**, no el código. |
| `REC-110`–`REC-115` | Finalizada | Jira las da por ejecutadas, pero el `ESTUDIO_PROYECTO_TITULO.md` anterior las sigue listando como pendientes. Falta adjuntar/actualizar la evidencia o corregir el estudio. |

### 3.3 Claves inexistente en el tablero real

El máximo real es `REC-161`. Por tanto **no existen** `REC-162`, `REC-163`, `REC-164`, `REC-165`, `REC-166`, `REC-167`, `REC-168`, `REC-169` ni `REC-170`.

| Clave usada en documentación/commits | Situación | Destino real |
|---|---|---|
| `REC-162` — bug del Desafío Verde que repetía preguntas | No existe. El arreglo está en el PR 2 mergeado (`af7d14d`). El ticket real `REC-137` cubre **progreso automático**, no la repetición de preguntas. | No asignar clave nueva sin crearla en Jira; documentar el fix como PR 2 / commit `88e72b1` + `17ce4e5`. |
| `REC-167` — “umbrales por clase y nivel Posible” | No existe. `REC-103` es sólo umbral global `0,50`. | Fuera de alcance: rama `feature/umbrales-por-clase` **no mergeada**. No mapear como si estuviera entregado. |
| `REC-170` — CI fallaba en `test:unit` antes de `build` | No existe. El fix ya está en `main` (`092fc88`, PR 1; trigger `fix/**` y orden `build → test:unit`). | Documentar como PR 1, no como ticket abierto ni clave nueva. |
| `REC-163`–`REC-166`, `REC-168`, `REC-169` | No existen; corresponden a un CSV histórico de propuestas que nunca se importaron. | Ver [`jira/MAPEO_CLAVES_REALES.md`](jira/MAPEO_CLAVES_REALES.md). |

### 3.4 Otros datos del tablero a corregir

- `REC-22` y `REC-23`: vencimiento `18/oct/26` anterior a creación `18/nov/26`.
- `REC-2` y `REC-34` tienen el **mismo resumen**: “Entrenamiento YOLO11n - iteración 1 (dataset sin limpiar)”. No está claro si son duplicados o dos ejecuciones; requiere decisión, no borrado automático.
- `REC-18` y `REC-70` duplican UAT con usuarios reales (una añade SUS). Consolidar o vincular.
- No hay campo de criterios de aceptación en la exportación. Los AC vigentes están en `docs/pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx` (columna “Criterios de aceptación”, 40 casos) y en su versión Markdown; no en Jira.
- Hay estados en documentos históricos (`Abierto`, `Corregido y verificado`, `Por cerrar`, `Plantilla lista`) que no existen en el pipeline real (`Finalizada`, `En curso`, `Tareas por hacer`). Una importación literal podría crear estados inválidos.

### 3.5 Documentación desactualizada detectada (corregida en esta revisión salvo los puntos marcados)

- `ESTUDIO_PROYECTO_TITULO.md` (18-11-2026) reportaba 135/138 tickets, “Docker no ejecutado”, REC-103/104 como pendientes y REC-110–115 abiertos. **Corregido**: 161 tickets, Docker 3/3 `healthy`, REC-103/104 y REC-110–115 finalizados en Jira (con evidencia a reforzar en estos últimos).
- `docs/ENTREGA.md` hablaba de “5 pestañas” e “Impacto” como pestaña separada. **Corregido**: Menú Principal + 4 módulos, impacto integrado en el Eco-Simulador RM.
- `docs/DECISIONES.md` y `docs/README.md` citaban 14 tablas. **Corregido**: el esquema real tiene **15** (`banner_impacto`, `comuna`, `contenedor`, `escaneos`, `habito`, `habito_cumplido`, `inferencia`, `instruccion`, `item_simulador`, `material`, `paso_instruccion`, `punto_limpio`, `punto_material`, `recurso_externo`, `sesion`).
- El plan de pruebas (XLSX y Markdown) y `EVIDENCIA_DOCKER.md` citaban códigos y estados obsoletos (`BORROSA`, `ARCHIVO_MUY_GRANDE`, RF-05 pendiente, RF-25 “fuera de alcance”). **Corregido en v1.3**: `IMAGEN_BORROSA`, `ARCHIVO_MUY_PESADO`, umbral `0,50` y multi-detección del backend, sin cambiar los 40 IDs de caso.
- **Pendiente:** los XLSX de requisitos siguen marcando RF-05/RF-06, RNF-03, RNF-11 y RNF-21 como “A verificar/Pendiente/Propuesto” mientras Jira y el código los dan por implementados; RF-15–22/RF-44 siguen como “Implementado” aunque los sliders/casillas fueron sustituidos por REC-140.
- **Pendiente:** existen dos XLSX de requisitos byte-idénticos (`docs/requisitos/` y `Fase 2/Evidencia/`); actualizar sólo uno deja el otro contradictorio.
- `AGENTS.md` se cita como versionado en artefactos históricos, pero **no existe en `main`**.

---

## 4. Backlog propuesto (pendiente de aprobación; **no aplicado en Jira**)

El detalle operativo está en [`jira/BACKLOG_PROPUESTO.md`](jira/BACKLOG_PROPUESTO.md). Resumen:

1. **Conservar** `REC-1`…`REC-161` tal como están en estado, salvo los casos indicados a continuación.
2. **Reclasificar como “fuera de alcance / decisión documentada”** `REC-7`, `REC-8`, `REC-11`, `REC-12`, `REC-13`, `REC-14`, `REC-16`, `REC-68`.
3. **Reabrir o reclasificar** `REC-128`/`REC-129` (escenarios no presentes en `main`) y **cerrar** `REC-157` (fix ya en `main`).
4. **Cerrar o vincular** `REC-18`/`REC-70` (UAT duplicada) manteniendo `REC-19` y `REC-62` abiertos hasta la defensa.
5. **Corregir fechas** de `REC-22` y `REC-23`.
6. **No crear** tickets con las claves `REC-162`…`REC-170`: las correcciones ya están en PR 1/PR 2 o son trabajo fuera de alcance. Si se quiere trazabilidad, crear tickets nuevos con la numeración real que Jira asigne y enlazar los commits.
7. **Adjuntar AC** a los tickets desde el plan de pruebas en vez de inventar criterios nuevos.
8. **No borrar** tickets: toda corrección es una aclaración de estado, resumen o vínculo.

---

## 5. Entregables de esta auditoría

| Archivo | Uso |
|---|---|
| `jira/CONTRASTE_161.md` / `.csv` | Contraste **issue por issue** de los 161 tickets contra el código real: clasificación, evidencia y acción propuesta. |
| `jira/INVENTARIO_REC.csv` | 161 issues normalizados: clave, tipo, resumen, estado, resolución, prioridad, épica, sprint, fechas y flag de AC. |
| `jira/MAPEO_CLAVES_REALES.md` | equivalencia entre claves históricas inexistentes y evidencia real. |
| `jira/BACKLOG_PROPUESTO.md` | cambios sugeridos, **sin ejecutar en Jira**. |
| `jira/CAMBIOS_JIRA_PROPUESTOS.csv` | filas listas para aplicar manualmente: clave, campo, valor actual, valor propuesto y motivo. |
| `jira/CRITERIOS_ACEPTACION.md` | AC reales del plan de pruebas y dónde pegarlos, sin redactar criterios nuevos. |
| `AUDITORIA_JIRA.md` | este documento. |
| `DOCUMENTACION_GENERAL.md` | documento único de alcance, arquitectura y funcionamiento real. |

> El CSV exportado quedó en la carpeta temporal de la sesión (`jira_export_real.csv`) y no se versiona: contiene todos los campos del tenant. Sólo se versiona el inventario reducido y anonimizado de comportamiento.
