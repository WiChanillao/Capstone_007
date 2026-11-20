# Backlog propuesto — EcoLearn / Jira REC

**Fecha:** 20-11-2026  
**Estado:** propuesta aprobada y **ejecutada en Jira el 20-11-2026** (30 cambios, 0 anomalías). Este archivo conserva la propuesta original; el resultado está en el §7.  
**Referencia:** [`../AUDITORIA_JIRA.md`](../AUDITORIA_JIRA.md), [`INVENTARIO_REC.csv`](INVENTARIO_REC.csv), [`CONTRASTE_161.md`](CONTRASTE_161.md), [`CAMBIOS_JIRA_PROPUESTOS.csv`](CAMBIOS_JIRA_PROPUESTOS.csv) y [`CRITERIOS_ACEPTACION.md`](CRITERIOS_ACEPTACION.md).

Los estados permitidos por el tablero en vivo son `Finalizada`, `En curso`, `Tareas por hacer` (y `En revisión`, actualmente sin issues). Las acciones son reclasificaciones, cierres o vinculaciones: **no se proponen funcionalidades nuevas ni se borran tickets**.

## 1. Reclasificar como “decisión documentada / fuera de alcance”

Mantener el estado `Finalizada` pero hacer explícito en el resumen o la resolución que **no implica funcionalidad entregada**.

| Clave | Resumen actual | Acción propuesta |
|---|---|---|
| `REC-7` | Streamlit — no implementada | Añadir sufijo `Fuera de alcance: decisión documentada`. |
| `REC-8` | PostGIS — no implementadas | Igual; vincular `REC-47`/`REC-144` (mapa real con Leaflet). |
| `REC-11` | Offline-first y React 18 — fuera de alcance | Igual; el stack real es React 19 + Vite + PWA online. |
| `REC-12` | Árbol de decisión en 2 toques — no implementado | Igual; no confundir con `REC-49`/`REC-50`. |
| `REC-13` | YOLOv8 sustituido por YOLO11n | Igual; vincular `REC-2`/`REC-34`. |
| `REC-14` | Ficha dual y PostGIS — sustituida | Igual; vincular `REC-7`/`REC-8`. |
| `REC-16` | Panel B2B/B2G y mapas de calor — no implementado | Igual. |
| `REC-68` | Panel B2B de reportes | Igual; etiqueta `b2b` debe entenderse como propuesto, no entregado. |

## 2. Ajustar tickets terminados que no coinciden con `main`

| Clave | Estado actual | Acción propuesta | Motivo |
|---|---|---|---|
| `REC-128` | Finalizada | Reabrir como `Tareas por hacer` **o** renombrar a `Decisión: sin escenarios (sustituido por REC-140)` | No existe lógica de guardar escenarios en `ecoscan-frontend/src`. |
| `REC-129` | Finalizada | Igual que `REC-128` | No existe comparación de escenarios; el impacto sale de MySQL. |
| `REC-157` | Tareas por hacer | Cerrar / marcar `Finalizada` y adjuntar `vite.config.js` + `sw.test.js` | `autoUpdate`, `cacheId ecolearn-v2-` y `cleanupOutdatedCaches` ya están en `main`. |
| `REC-110`–`REC-115` | Finalizada | Adjuntar evidencia de medición o aclarar alcance de la medición | El estudio anterior los lista como pendientes; Jira los da por hechos. |
| `REC-2`, `REC-34` | Finalizada | Comparar y, si corresponde, vincular como duplicados | Resumen idéntico: “Entrenamiento YOLO11n - iteración 1 (dataset sin limpiar)”. |
| `REC-18`, `REC-70` | Tareas por hacer | Fusionar o vincular como UAT (una con SUS) | Doble registro del mismo trabajo pendiente. |

## 3. Corregir fechas y metadatos

| Clave | Dato actual | Acción propuesta |
|---|---|---|
| `REC-22` | Creada `18/nov/26`, vence `18/oct/26` | Corregir vencimiento a una fecha posterior a la creación (p. ej. `30/nov/26`, como las demás épicas). |
| `REC-23` | Creada `18/nov/26`, vence `18/oct/26` | Igual. |
| Todas | Sin campo de AC | Copiar los criterios desde `docs/pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx` (columna “Criterios de aceptación”) en lugar de redactar otros nuevos. |
|Estado|`En revisión` sin issues|No crear estados nuevos durante importaciones; mapear `To Do`/`In Progress` a los estados reales.|

## 4. Claves que **no** deben crearse ni dejarse como pendientes

`REC-162` … `REC-170` no existen (máximo real: `REC-161`). No importarlas ni dejarlas en documentos como trabajo abierto:

- Fix del Desafío Verde → PR 2 / `af7d14d` (no `REC-162`; `REC-137` es otra historia).
- Validación de `/predict`, migración de BD y caché PWA → ya en `main` (no `REC-163`, `REC-164`, `REC-165`; `REC-157` fue cerrado el 20-11-2026).
- Experimentos Colab → vincular a `REC-63`/`REC-64` (no `REC-166`).
- Umbrales por clase y “Posible” → **NO EN MAIN**, rama `feature/umbrales-por-clase` sin merge (no `REC-167`, ni épica `REC-103`).
- Documentación y reglas → entregables reales en `docs/` (no `REC-168`/`REC-169`; `AGENTS.md` no está en `main`).
- CI → PR 1 / `092fc88`, run `44669949452` (no `REC-170`).

Detalle y hashes en [`MAPEO_CLAVES_REALES.md`](MAPEO_CLAVES_REALES.md).

## 5. Mantener abiertos (deuda real)

`REC-18`, `REC-19`, `REC-20`, `REC-21`, `REC-24`, `REC-62`, `REC-63`, `REC-64`, `REC-65`, `REC-70`, `REC-93`, `REC-105`, `REC-122`, `REC-154`, `REC-155`, `REC-156` (`REC-157` ya fue cerrado según §2).

Esta deuda es coherente con la documentación: mAP `0,562 < 0,65`, CORS de producción, rotación de clave, 25 puntos externos sin validar, horarios con bloques múltiples y UAT/SUS pendiente.

## 6. Orden ejecutado (autorizado el 20-11-2026)

1. Corregir fechas de `REC-22`/`REC-23`.
2. Cerrar `REC-157` y reclasificar `REC-128`/`REC-129`.
3. Añadir sufijo de “fuera de alcance” a los ocho tickets de §1.
4. Vincular duplicados (`REC-2`/`REC-34`, `REC-18`/`REC-70`).
5. Adjuntar AC desde el plan de pruebas.
6. Actualizar la documentación general para que no vuelva a citar claves inexistentes.

Ejecutado con autorización explícita; el detalle y la verificación están en el §7.

## 7. Resultado verificado en Jira (20-11-2026)

| Operación | Cantidad | Detalle |
|---|---:|---|
| Resúmenes editados | 10 | `REC-7`, `REC-8`, `REC-11`, `REC-12`, `REC-13`, `REC-14`, `REC-16`, `REC-68`, `REC-128`, `REC-129` |
| Estados | 3 | `REC-128`/`REC-129` → `Tareas por hacer`; `REC-157` → `Finalizada` |
| Vencimientos | 2 | `REC-22`, `REC-23` → `30/nov/2026` |
| Vínculos `Relates` | 2 | `REC-2` ↔ `REC-34`; `REC-18` ↔ `REC-70` (1 por par, sin borrados) |
| Comentarios de AC | 17 | tickets abiertos + referencia en épicas `REC-20`, `REC-21`, `REC-24` |
| Comentarios de acción | 7 | `REC-110`–`REC-115` y `REC-157` |
| Claves verificadas sin cambio | 3 | `REC-162`, `REC-167`, `REC-170` (no existen) |
| **Anomalías** | **0** | verificación por lectura de la API con la sesión de Brave |

Notas de interfaz: las transiciones del workflow se llaman **“Por hacer”** y **“Listo”** y mapean a `Tareas por hacer` y `Finalizada`. Jira no expone campo de criterios de aceptación, por lo que los AC quedaron como comentarios con prefijo. No se crearon estados, campos ni tickets nuevos.
