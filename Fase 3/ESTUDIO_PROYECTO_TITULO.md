# Estudio de proyecto de título — EcoLearn Chile / EcoScan

**Fecha:** 18-11-2026  
**Proyecto:** EcoLearn Chile — clasificador inteligente de residuos para la Región Metropolitana  
**Tablero:** REC (Jira real, `https://capstone-reci-smart.atlassian.net/jira/software/projects/REC/boards/1`)  
**Estado del documento:** evaluación y auditoría basada en evidencia verificada directamente y en tickets con evidencia verificada por OCR.

> **Actualización 20-11-2026:** este estudio se conserva como registro histórico
> del 18-11-2026. El estado vigente del tablero es de **161 issues**
> (144 `Finalizada`, 8 `En curso`, 9 `Tareas por hacer`), con Docker 3/3
> `healthy`, PR 1 y PR 2 mergeados, `REC-103`/`REC-104` implementados y
> `REC-110`–`REC-115` marcados como finalizados en Jira. La referencia vigente
> es [`docs/DOCUMENTACION_GENERAL.md`](docs/DOCUMENTACION_GENERAL.md) y el
> contraste completo está en [`docs/AUDITORIA_JIRA.md`](docs/AUDITORIA_JIRA.md).

---

## 1. Resumen ejecutivo

El proyecto **sí cumple como proyecto de título** por su alcance técnico: integra visión por computadora, backend FastAPI, MySQL, PWA, trazabilidad documental en Jira y una interfaz de usuario funcional con **Menú Principal + 4 módulos**. Sin embargo, **no todo lo que aparece en Jira está implementado**, y parte de lo documentado corresponde a trabajo pendiente, fuera de alcance real o a tareas de proceso no ejecutadas.

La corrección más reciente separa claramente dos cosas:

- **Aplicación:** solo funciones para el usuario final. Ya no muestra pendientes, notas internas, códigos REC, nombres de tecnología internos ni el panel de trazabilidad.
- **Estudio / Jira:** auditoría, evaluación, brechas y prioridades viven aquí y en los tickets, no en la pantalla del usuario.

---

## 2. Alcance real verificado en la aplicación

La app expone **Menú Principal + 4 módulos de usuario** (el impacto está integrado en el Eco-Simulador RM):

| Módulo | Función real verificada | Origen de datos |
|---|---|---|
| Menú Principal | Presentación del producto y accesos a escáner/puntos | Contenido local de la app |
| Escáner IA | Cámara en vivo o carga de imagen; predicción real vía `/predict`; confianza visible; guía de reciclaje, reutilización y pasos | Backend FastAPI + modelo `best.pt` |
| Puntos Limpios RM | Filtro por comuna y material, estado abierto/cerrado, “cómo llegar” y geolocalización autorizada | `GET /db/puntos` (MySQL), con catálogo local solo como respaldo técnico |
| Eco-Simulador RM | Cálculo de agua ahorrada, CO₂ evitado y basura desviada; guardado y comparación de escenarios | Cálculo local + `localStorage` |
| Desafío Verde RM | Hábitos, estadísticas y avance calculados **automáticamente** desde los escaneos | `GET /db/habitos` + `localStorage` |

### Correcciones verificadas en esta entrega

- Se eliminó la pestaña **Trazabilidad**, el listado de pendientes y los textos internos de la interfaz.
- El progreso del Desafío Verde **ya no se marca manualmente**: cada predicción exitosa incrementa el total de escaneos y el contador por material.
- Las reglas automáticas completan hábitos e insignia al alcanzar las metas reales.
- Se corrigió la franja negra al hacer scroll (REC-135): `background-attachment: scroll`, sin `backdrop-filter` problemático y fondo continuo.

**Verificación directa realizada:**

- `npm run build`: correcto (solo advertencia no bloqueante de chunk > 500 kB).
- Backend `GET /`: HTTP 200 con `modelo_activo: best.pt` y `mysql_conectado: true`.
- `GET /db/puntos`, `/db/habitos`, `/db/comunas`, `/db/materiales`, `/db/simulador`, `/db/banners`: HTTP 200.
- `/predict` con `IMG_8834.jpg`: HTTP 200, `Aluminio`, confianza `0.94`.
- `/predict` con archivo de texto: HTTP 400 controlado.
- Prueba automática de progreso: 10 escaneos reales (1 cartón, 6 aluminio, 3 plástico) → **100 %**, insignia “Guardián Verde” y 4 hábitos completados.
- Prueba de una sola foto: al subir `IMG_8834.jpg` con el contador en cero, el resultado fue **1 escaneo, 1 aluminio y 0 % de progreso**; es decir, una foto suma una sola medición y no completa insignias por sí sola.
- Regresión visual corregida (REC-139): se eliminaron los `backdrop-filter`/`blur` residuales que quedaban en `.btn-secondary` y en la etiqueta “Cámara Activa”. Tras 3 ciclos de scroll a 1912×1068, la franja vacía máxima es de 160 px (antes era de ~860 px).

Evidencia visual: `APP_Limpia_Menu.png`, `APP_Desafio_auto_inicial.png`, `APP_Desafio_auto_100.png`, `APP_Una_Foto_Automatico.png`, `REG_Menu_Principal_top.png`, `BUG_Scroll_corregido.png`.

---

## 3. Auditoría Jira vs. App

### 3.1 Estado del tablero

La auditoría previa a esta entrega registró 135 tickets y luego 138. El
**estado vigente (20-11-2026)**, obtenido por exportación real desde Jira, es:

| Estado | Cantidad |
|---|---:|
| Finalizada | 144 |
| En curso | 8 |
| En revisión | 0 |
| Tareas por hacer | 9 |
| **Total** | **161** |

Los 161 tickets van de `REC-1` a `REC-161` sin huecos. El detalle está en
[`docs/jira/INVENTARIO_REC.csv`](docs/jira/INVENTARIO_REC.csv).

### 3.2 Qué significa “Jira al día”

Jira está **al día en la documentación de evidencia**: `REC-1` a `REC-161` están inventariados y contrastados contra el repositorio. Los cambios de aquella entrega se registraron en `REC-136`, `REC-137` y `REC-138`; las correcciones posteriores quedan propuestas en [`docs/jira/BACKLOG_PROPUESTO.md`](docs/jira/BACKLOG_PROPUESTO.md).

Jira **no está al día en el sentido de que todo esté terminado**. Hay tickets abiertos por tres razones distintas:

1. **Trabajo pendiente real:** por ejemplo `REC-63` (mejorar mAP a ≥ 0.65), `REC-105` (CORS de producción), `REC-65`/`REC-155`/`REC-156` (validación de puntos externos), `REC-154` (horarios con bloques múltiples) y UAT/SUS (`REC-18`/`REC-70`). `REC-103`/`REC-104`, `REC-106`/`REC-107` y `REC-110`–`REC-115` ya están finalizados en Jira; en estos dos últimos grupos hace falta adjuntar/actualizar la evidencia.
2. **Proceso o gestión:** Cypress ya ejecutado (`REC-17`/`REC-69`, 4 pruebas); UAT sigue pendiente (`REC-18`/`REC-70`). Repositorio publicado, capturas, PPT y retrospectiva cerrados (`REC-57`, `REC-59`–`REC-61`); envío al profesor abierto (`REC-62`).
3. **Fuera de alcance real / sustituido:** REC-11 (offline-first y React 18), REC-13 (YOLOv8, sustituido por YOLO11n), REC-16/68 (panel B2B/B2G), REC-8 (PostGIS), REC-7 (Streamlit), REC-12 (árbol de decisión en 2 toques), REC-14 (ficha dual con PostGIS).

### 3.3 Coherenencia entre Jira y la app

| Elemento documentado en Jira | ¿Reflejado en la app? | Observación |
|---|---|---|
| Modelo real y confianza visible | Sí | `/predict` + etiqueta de confianza |
| MySQL con puntos y hábitos | Sí | `/db/puntos` y `/db/habitos` |
| Escenarios guardados/comparados | Sí | Eco-Simulador RM |
| Persistencia del desafío | Sí, mejorado | Ahora es automática, no manual |
| Corrección de scroll | Sí | REC-135 |
| Menú Principal | Sí | REC-130 |
| Cámara en vivo | Sí | REC-131 |
| Docker | Sí, verificado | 3 contenedores `healthy` y `/predict → MySQL` (REC-67, REC-141) |
| Cypress / UAT | Cypress sí; UAT no | 4 pruebas Cypress; UAT/SUS pendiente (REC-17/69 vs REC-18/70) |
| Panel B2B/B2G, offline, YOLOv8, PostGIS | No | Fuera de alcance o sustituidos |
| mAP ≥ 0.65 | No | Métrica actual documentada: 0.562 |

**Conclusión de la auditoría:** la app refleja correctamente el núcleo funcional y las mejoras verificadas. No refleja —y no debe hacerlo— trabajo pendiente, fuera de alcance o no ejecutado. Esa información queda en Jira y en este estudio.

---

## 4. Evaluación como Proyecto de Título

### Veredicto

**Sí es apto como proyecto de título**, siempre que se presente con honestidad: como una solución funcional con evidencia real, no como un sistema completo con todas las metas de calidad alcanzadas.

### Fortalezas demostrables

- Problema real y local: clasificación de residuos y orientación de puntos limpios en la RM.
- Integración completa: frontend React/Vite/PWA, backend FastAPI, MySQL y modelo YOLO11n.
- Evidencia trazable en Jira: tickets, archivos, capturas y métricas.
- Interfaz limpia, en español y con funciones útiles para el usuario final.
- Estadísticas y progreso automáticos basados en interacciones reales.
- Corrección de regresiones verificadas (HEIC, confianza, scroll, rutas DB).

### Limitaciones que deben decirse en la defensa

- El modelo cumple la detección de 3 clases, pero **mAP@50 0.562 está por debajo del objetivo ≥ 0.65** (REC-63).
- **Cypress sí se ejecutó** (4 pruebas, `REC-17`/`REC-69`); **UAT con usuarios reales y SUS sigue pendiente** (`REC-18`/`REC-70`).
- **Docker sí se ejecutó**: 3 contenedores `healthy`, `/health` con MySQL conectado y `/api/db/puntos` con 35 puntos (`REC-67`, `REC-141`).
- **Repositorio publicado** en GitHub (`REC-55`/`REC-57`).
- Jira marca `REC-110`–`REC-115` como finalizados, pero las mediciones de LCP, bundle, accesibilidad, responsive WebKit y cobertura deben adjuntarse a los tickets para que la evidencia sea verificable.

### Prioridades para dejarlo bien presentado

**P1 — Antes de la defensa**

1. Cerrar o reclasificar los tickets fuera de alcance para que el tablero no parezca incompleto.
2. Ejecutar y evidenciar Cypress o, al menos, una prueba E2E manual guiada.
3. Verificar Docker en una máquina limpia y adjuntar evidencia a REC-67.
4. Congelar una versión del modelo/dataset y dejar claro el valor real de mAP@50.

**P2 — Si queda tiempo**

5. Verificar y documentar el umbral mínimo de confianza (`REC-103`) y el rechazo de fotos borrosas (`REC-104`), ya implementados en `main`.
6. Cerrar la política de CORS de producción (`REC-105`); rate limit y cabeceras (`REC-106`/`REC-107`) ya están implementados.
7. Adjuntar a `REC-111`–`REC-114` las mediciones de LCP, bundle, accesibilidad y responsive; no reabrirlas como trabajo nuevo sin evidencia.

**P3 —fuera del alcance del título**

8. Panel B2B/B2G, PostGIS, offline-first, YOLOv8 y Streamlit: mantenerlos documentados como no implementados/sustituidos, sin prometerlos en la demo.

---

## 5. Recomendación final de presentación

Mostrar la app en este orden:

1. Menú Principal (problema y propósito).
2. Escáner IA con una imagen real y confianza visible.
3. Cómo el escaneo actualiza automáticamente el Desafío Verde y las estadísticas.
4. Puntos Limpios RM desde MySQL con filtro y “cómo llegar”.
5. Eco-Simulador RM con guardado/comparación de escenarios.

Y decir explícitamente en la defensa:

> “Lo que aparece en Jira como pendiente, fuera de alcance o no ejecutado no se muestra en la aplicación; queda registrado en la trazabilidad del proyecto para no presentar como terminado lo que no lo está.”

---

## 6. Archivos de evidencia relacionados

- `APP_Limpia_Menu.png` — app sin notas internas ni pestaña de trazabilidad.
- `APP_Desafio_auto_inicial.png` — progreso en 0 antes de escanear.
- `APP_Desafio_auto_100.png` — progreso 100 % tras 10 escaneos reales.
- `APP_Una_Foto_Automatico.png` — una sola foto suma 1 escaneo y 0 % de progreso; sin carga manual.
- `REG_Menu_Principal_top.png` — menú sin franja negra tras la regresión.
- `BUG_Scroll_franja_negra.png` / `BUG_Scroll_corregido.png` — regresión visual y corrección original.
- `APP_Puntos_MySQL.png` / `APP_Desafio_MySQL.png` — datos reales desde MySQL.
- `COMO_EJECUTAR.md` — requisitos previos y comandos (Docker documentado, no ejecutado).
