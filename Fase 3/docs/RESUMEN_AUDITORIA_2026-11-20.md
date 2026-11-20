# Resumen ejecutivo — Auditoría Jira y documentación general (20-11-2026)

## 1. Qué se revisó

- **Jira en vivo:** exportación real desde la sesión de Brave (`CSV: todos los campos`), **161 issues**, `REC-1` … `REC-161`, 190 columnas. No se modificó ningún ticket.
- **Repositorio real:** `main @ af7d14d`, PR 1 (`092fc88`) y PR 2 (`af7d14d`) mergeados; rama `feature/umbrales-por-clase` sin merge.
- **Código contrastado:** `main.py`, `rutas_db.py`, `docker-compose.yml`, `01_schema.sql`, `02_seed.sql`, `App.jsx`, `trivia.js`, `MapaPuntos.jsx`, `vite.config.js`, `ci.yml`, plan de pruebas y evidencia Docker/CI/Colab.
- **Inventario local y Git:** artefactos Jira en `docs/`, XLSX/PPTX/DOCX, commits históricos y worktrees.

## 2. Qué está bien

- Alcance real coherente: **YOLO11n `best.pt`**, 3 clases, **umbral global `0,50`**, impacto de **30 días desde `ecoscan.escaneos`**, visitante anónimo con `id_sesion`.
- Docker 3/3 `healthy`, `/health` con MySQL conectado, `/api/db/puntos` con 35 marcadores.
- Swagger `/docs` respondiendo 200 con CSP ajustada sólo en rutas de documentación (cambio local aún no commiteado).
- Mapa Leaflet/OpenStreetMap con filtros, procedencia y coordenadas aproximadas visibles.
- Desafío Verde con 25 preguntas, rondas sin repetir y avance automático desde escaneos.
- CI corregido: `build → test:unit`, trigger `fix/**`, PR 1 mergeado.
- Fix del Desafío repetido mergeado en PR 2.

## 3. Incongruencias principales

1. **Claves inexistentes:** `REC-162` … `REC-170` no están en Jira (máximo `REC-161`). El bug del Desafío está en PR 2; `REC-137` es otra historia. El fix de CI está en PR 1. Los umbrales por clase y “Posible” siguen **NO EN MAIN**.
2. **Fuera de alcance como “Finalizada”:** `REC-7`, `REC-8`, `REC-11`, `REC-12`, `REC-13`, `REC-14`, `REC-16`, `REC-68`.
3. **Terminado en Jira pero no en `main`:** `REC-128`, `REC-129` (escenarios).
4. **Ticket abierto con fix ya en `main`:** `REC-157` (caché PWA).
5. **Fechas inválidas:** `REC-22` y `REC-23` vencen antes de haber sido creadas.
6. **Duplicados/ambigüedad:** `REC-2`/`REC-34` (mismo resumen) y `REC-18`/`REC-70` (UAT duplicada).
7. **Criterios de aceptación:** no hay campo de AC en Jira; la fuente es el plan de pruebas (40 casos).
8. **Documentación obsoleta:** 5 pestañas/Impacto como pestaña, 14 tablas, conteos de pruebas, PRs “pendientes”, XLSX de requisitos desactualizados y dos copias idénticas del XLSX.

## 4. Archivos creados

| Archivo | Contenido |
|---|---|
| `docs/DOCUMENTACION_GENERAL.md` | Documento canónico de alcance, módulos, flujos, API, datos, CI y deuda. |
| `docs/AUDITORIA_JIRA.md` | Auditoría completa y clasificación de incongruencias. |
| `docs/RESUMEN_AUDITORIA_2026-11-20.md` | Este resumen. |
| `docs/jira/CONTRASTE_161.md` / `.csv` | Contraste **uno por uno** de los 161 issues. |
| `docs/jira/INVENTARIO_REC.csv` | Inventario normalizado de 161 filas. |
| `docs/jira/MAPEO_CLAVES_REALES.md` | Destino real de las claves `REC-162`…`REC-170`. |
| `docs/jira/BACKLOG_PROPUESTO.md` | Cambios sugeridos para Jira, **sin aplicar**. |
| `docs/jira/CAMBIOS_JIRA_PROPUESTOS.csv` | Filas listas para aplicar manualmente en Jira (campo, valor actual, propuesto y motivo). |
| `docs/jira/CRITERIOS_ACEPTACION.md` | AC reales del plan de pruebas y su destino en los tickets. |

## 5. Archivos actualizados

- `README.md` (raíz): alcance de frontend y accesos a los nuevos documentos.
- `Fase 3/README.md`: nombres reales de módulos, orden de CI, rutas de Colab inexistentes y enlace a documentación vigente.
- `Fase 3/docs/README.md`: índice con documentación vigente y carpeta `jira/`.
- `Fase 3/docs/ENTREGA.md`: Menú + 4 módulos, conteos de pruebas y `docker compose down` sin borrar volúmenes.
- `Fase 3/docs/DECISIONES.md`: 15 tablas, CSP vigente y nota de actualización.
- `Fase 3/ESTUDIO_PROYECTO_TITULO.md`: 161 tickets, Docker/Cypress/GitHub verificados y deuda real.
- `Fase 3/INICIO_RAPIDO.md`: Python 3.12/3.13.
- `Fase 3/COMO_EJECUTAR.md`: ruta de evidencia vigente.
- `Fase 3/ecoscan-frontend/README.md`: Menú + 4 módulos y default de `VITE_API_URL`.
- `Fase 3/docs/evidencia/estado_pagina_2026-11-20/README.md`: `REC-162` histórico y PR 2 mergeado.
- `Fase 3/docs/evidencia/ci_orden_pasos.md`: `REC-170` histórico y PR 1 mergeado.
- `Fase 3/docs/evidencia/diagnostico_400.md`: contexto de la FASE 3 pendiente.
- `Fase 3/docs/evidencia/EVIDENCIA_DOCKER.md`: código de error `ARCHIVO_MUY_PESADO` vigente.
- `Fase 3/docs/pruebas/PLAN_DE_PRUEBAS_EcoLearn.md` **y `.xlsx`** (v1.3): Menú + 4 módulos, 15 tablas, `IMAGEN_BORROSA`, umbral `0,50` y estados de `REC-92`/`REC-103`/`REC-104` corregidos sin cambiar los 40 IDs de caso.
- `Fase 3/docs/requisitos/EcoScan_Requisitos_Funcionales.xlsx`: estados reconciliados con `main` (RF-05/06, RNF-03/11/21 implementados; RF-15/16/18/20/22/RF-44 ajustados por `REC-140`); se eliminó la copia duplicada de `Fase 2/Evidencia/`.
- `Fase 3/ecoscan-backend/.env.example`: `UMBRAL_NITIDEZ=50`, alineado con `main.py`, `docker-compose.yml` y la plantilla raíz.

## 6. Estado final y pendientes de autorización

- **Commit `d85d5cd` subido a `origin/main`** (sin PR ni merge adicionales; PR 3 intacto).
- No se modificó Jira: el backlog propuesto sigue listo para revisar y aplicar sólo si se autoriza.
- No se borraron volúmenes ni se ejecutó `docker compose down -v`.
- No se escribieron credenciales ni tokens; sólo se listan nombres de variables.
- `tests/diagnostico_400.py` continúa sin versionarse, según su propia cabecera «NO versionar».
- Pendiente de decisión: aplicar los 30 cambios propuestos en Jira e importar en Bizagi los modelos `02`–`14`.
