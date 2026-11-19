# Estudio de proyecto de título — EcoLearn Chile / EcoScan

**Fecha:** 18-11-2026  
**Proyecto:** EcoLearn Chile — clasificador inteligente de residuos para la Región Metropolitana  
**Tablero:** REC (Jira real, `https://capstone-reci-smart.atlassian.net/jira/software/projects/REC/boards/1`)  
**Estado del documento:** evaluación y auditoría basada en evidencia verificada directamente y en tickets con evidencia verificada por OCR.

---

## 1. Resumen ejecutivo

El proyecto **sí cumple como proyecto de título** por su alcance técnico: integra visión por computadora, backend FastAPI, MySQL, PWA, trazabilidad documental en Jira y una interfaz de usuario funcional con cinco módulos. Sin embargo, **no todo lo que aparece en Jira está implementado**, y parte de lo documentado corresponde a trabajo pendiente, fuera de alcance real o a tareas de proceso no ejecutadas.

La corrección más reciente separa claramente dos cosas:

- **Aplicación:** solo funciones para el usuario final. Ya no muestra pendientes, notas internas, códigos REC, nombres de tecnología internos ni el panel de trazabilidad.
- **Estudio / Jira:** auditoría, evaluación, brechas y prioridades viven aquí y en los tickets, no en la pantalla del usuario.

---

## 2. Alcance real verificado en la aplicación

La app expone **5 módulos de usuario**:

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

Al momento de la auditoría previa a esta entrega, el tablero REC tenía **135 tickets**:

| Estado | Cantidad |
|---|---:|
| Finalizada | 83 |
| En curso | 9 |
| En revisión | 4 |
| Tareas por hacer | 39 |
| **Total** | **135** |

Con los tres tickets creados para esta entrega (limpieza visual, progreso automático y estudio/auditoría), el tablero queda en **138 tickets**.

### 3.2 Qué significa “Jira al día”

Jira está **al día en la documentación de evidencia**: REC-1 a REC-135 tienen evidencia verificada y enlaces directos a archivos reales. Los cambios de esta entrega se registran en REC-136, REC-137 y REC-138.

Jira **no está al día en el sentido de que todo esté terminado**. Hay tickets abiertos por tres razones distintas:

1. **Trabajo pendiente real:** por ejemplo REC-63 (mejorar mAP a ≥ 0.65), REC-103/104 (umbral de confianza y fotos borrosas), REC-105/106/107 (CORS de producción, rate limiting y cabeceras), REC-110–115 (carga, LCP, bundle, accesibilidad, responsive y cobertura), REC-127 (orden por cercanía).
2. **Proceso o gestión no ejecutado:** REC-17/18 y REC-69/70 (Cypress y UAT), REC-57 (publicar repositorio), REC-59/60/61/62 (capturas, PPT, retrospectiva y envío al profesor).
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
| Docker | No como ejecución verificada | Solo archivos y guía de requisitos (REC-67) |
| Cypress / UAT | No | No ejecutados |
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
- **No se ejecutaron Cypress ni UAT con usuarios reales** (REC-17/18, REC-69/70).
- **Docker no se ejecutó**: existen archivos y guía, pero no hay verificación de `docker compose up --build` (REC-67).
- **No se verificó publicación en GitHub** desde este entorno (REC-55/57).
- La medición de LCP, bundle, accesibilidad, responsive WebKit y cobertura sigue pendiente (REC-110–115).

### Prioridades para dejarlo bien presentado

**P1 — Antes de la defensa**

1. Cerrar o reclasificar los tickets fuera de alcance para que el tablero no parezca incompleto.
2. Ejecutar y evidenciar Cypress o, al menos, una prueba E2E manual guiada.
3. Verificar Docker en una máquina limpia y adjuntar evidencia a REC-67.
4. Congelar una versión del modelo/dataset y dejar claro el valor real de mAP@50.

**P2 — Si queda tiempo**

5. Aplicar umbral mínimo de confianza (REC-103) y rechazo de fotos borrosas (REC-104).
6. Definir CORS de producción, rate limiting y cabeceras de seguridad (REC-105–107).
7. Medir LCP, tamaño de bundle, accesibilidad y responsive (REC-111–114).

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
