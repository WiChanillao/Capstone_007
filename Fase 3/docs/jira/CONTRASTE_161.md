# Contraste completo de los 161 issues de Jira REC contra el repositorio real

**Fecha:** 20-11-2026  
**Fuente:** exportación CSV real (161 filas, 190 campos) y código `main @ af7d14d`.  
**Criterios de aceptación:** ningún issue tiene campo de AC en Jira; la fuente vigente es `docs/pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx` (40 casos).
**Estado de esta tabla:** es la fotografía **anterior** a la aplicación del backlog. El 20-11-2026 se ejecutaron los 30 cambios autorizados; el estado vigente y la verificación están en el §4 de [`AUDITORIA_JIRA.md`](../AUDITORIA_JIRA.md) y en el §7 de [`BACKLOG_PROPUESTO.md`](BACKLOG_PROPUESTO.md).

Clasificaciones usadas: **Alineado**, **Alineado con matiz**, **Entregable documental/BPMN**,
**Deuda abierta coherente**, **Fuera de alcance declarado**, **Sustituido**, **Parcial**,
**Incongruencia** y **Histórico retirado**. Ninguna implica nueva funcionalidad.

| Clave | Estado | Clasificación | Resumen | Evidencia / observación | Acción propuesta |
|---|---|---|---|---|---|
| REC-1 | Finalizada | Alineado | Curación y etiquetado del dataset base en Roboflow (3 clases) | dataset 3 clases en README/CRISP-DM | Mantener |
| REC-2 | Finalizada | Duplicado probable | Entrenamiento YOLO11n - iteración 1 (dataset sin limpiar) | Mismo resumen que REC-34 | Ejecutado: vínculo Relates con REC-34 |
| REC-3 | Finalizada | Alineado | Endpoint REST de inferencia en FastAPI (/predict) | main.py POST /predict | Mantener |
| REC-4 | Finalizada | Incongruencia documental | Catálogo semántico y esquema relacional de residuos (14 tablas) | 01_schema.sql tiene 15 tablas, no 14 | Corregir resumen a 15 tablas |
| REC-5 | Finalizada | Alineado | Prototipo de interfaz web y arquitectura de componentes | React 19 + Vite + Tailwind en package.json | Mantener |
| REC-6 | Finalizada | Alineado | Docker y Docker Compose para el backend (validado) | docker-compose.yml + EVIDENCIA_DOCKER.md; 3 servicios healthy | Mantener; adjuntar evidencia vigente |
| REC-7 | Finalizada | Fuera de alcance declarado | Herramienta interactiva ligera (Streamlit) - no implementada | No hay Streamlit en main | Reclasificar como decisión documentada |
| REC-8 | Finalizada | Fuera de alcance declarado | Consultas de proximidad con PostGIS - no implementadas | Mapa usa Leaflet/OSM, no PostGIS | Reclasificar como decisión documentada |
| REC-9 | Finalizada | Alineado | Ampliación y balanceo del dataset (485 etiquetas +252 Aluminio) | CRISP-DM: 485 etiquetas, +252 Aluminio | Mantener |
| REC-10 | Finalizada | Entregable documental | Modelado de 14 procesos BPMN y 100 requisitos (ERS) | BPMN v4 + 100 RF/RNF en docs/ | Mantener; vincular paquete BPMN v3 |
| REC-11 | Finalizada | Fuera de alcance declarado | Arquitectura offline-first y React 18 (fuera de alcance real) | React 19 + Vite; sin offline-first | Reclasificar como decisión documentada |
| REC-12 | Finalizada | Fuera de alcance declarado | Módulo de árbol de decisión en 2 toques (no implementado) | Desafío Verde usa trivia.js, no árbol de decisión | Reclasificar como decisión documentada |
| REC-13 | Finalizada | Sustituido | Escáner con YOLOv8 en PWA (sustituido por YOLO11n) | YOLO11n best.pt en main.py | Reclasificar como sustituido por YOLO11n |
| REC-14 | Finalizada | Fuera de alcance declarado | Ficha educativa dual y geolocalización PostGIS (sustituida) | Sin PostGIS ni ficha dual | Reclasificar como decisión documentada |
| REC-15 | Finalizada | Alineado con matiz | Pruebas unitarias de componentes frontend (Vitest 4/4) | Vitest: 24 pruebas tras PR 2; el ticket dice 4/4 | Actualizar conteo a 24 |
| REC-16 | Finalizada | Fuera de alcance declarado | Panel analítico B2B/B2G y mapas de calor (no implementado) | Sin panel B2B/B2G | Reclasificar como decisión documentada |
| REC-17 | Finalizada | Alineado con matiz | Pruebas E2E con Cypress: 3 casos ejecutados (alcance reducido) | Cypress: 4 pruebas en cypress/e2e/app.cy.js | Actualizar conteo a 4 |
| REC-18 | Tareas por hacer | Deuda abierta coherente | UAT con usuarios reales y SUS (no ejecutada) | UAT/SUS no ejecutada | Ejecutado: vínculo Relates con REC-70; sigue abierta |
| REC-19 | Tareas por hacer | Deuda abierta coherente | Consolidación de la memoria técnica y preparación de defensa | Memoria/defensa en preparación | Mantener abierto |
| REC-20 | En curso | Épica vigente | Épica: Modelo de visión y dataset | 15 hijos; mAP pendiente | Mantener en curso |
| REC-21 | En curso | Épica vigente | Épica: Base de datos MySQL | 16 hijos; 15 tablas y puntos por validar | Mantener en curso |
| REC-22 | Finalizada | Épica cerrada con dato inválido | Épica: Backend e integración | 16 hijos; vencimiento anterior a creación | Ejecutado: vencimiento 30/nov/2026 |
| REC-23 | Finalizada | Épica cerrada con dato inválido | Épica: Frontend y experiencia de usuario | 41 hijos; vencimiento anterior a creación | Ejecutado: vencimiento 30/nov/2026 |
| REC-24 | En curso | Épica vigente | Épica: Documentación, pruebas y entrega | 56 hijos; UAT y defensa abiertas | Mantener en curso |
| REC-25 | Finalizada | Entregable documental | Análisis del negocio y problemática del reciclaje | docs/crisp-dm/ | Mantener |
| REC-26 | Finalizada | Entregable documental con matiz | Levantamiento de 100 requisitos funcionales y no funcionales | 100 RF/RNF; dos XLSX duplicados y parcialmente obsoletos | Consolidar XLSX de requisitos |
| REC-27 | Finalizada | Entregable documental | Modelado de 14 procesos BPMN v4 (extendidos e individuales) | BPMN v4 y paquete v3 de 14 modelos | Mantener; actualizar a v3 |
| REC-28 | Finalizada | Incongruencia documental | Modelo de datos lógico y relacional (14 tablas) | Modelo de datos dice 14 tablas; real 15 | Corregir a 15 tablas |
| REC-29 | Finalizada | Entregable documental | Selección de metodología CRISP-DM + Scrum | CRISP-DM + Scrum en docs/ | Mantener |
| REC-30 | Finalizada | Alineado | Adquisición y auditoría del dataset de Roboflow | Roboflow en CRISP-DM | Mantener |
| REC-31 | Finalizada | Alineado | Análisis exploratorio y caracterización morfológica (EDA) | EDA en CrispDM_Ecolearn.ipynb | Mantener |
| REC-32 | Finalizada | Alineado | Estandarización de 485 etiquetas poligonales a bounding boxes | 485 etiquetas a bounding boxes | Mantener |
| REC-33 | Finalizada | Alineado | Oversampling de la clase minoritaria Aluminio (+252 imágenes) | Oversampling +252 Aluminio | Mantener |
| REC-34 | Finalizada | Duplicado probable | Entrenamiento YOLO11n - iteración 1 (dataset sin limpiar) | Mismo resumen que REC-2 | Ejecutado: vínculo Relates con REC-2 |
| REC-35 | Finalizada | Alineado | Entrenamiento YOLO11n - iteración 2 (dataset limpio y balanceado) | Iteración 2, mAP 0,562 | Mantener |
| REC-36 | Finalizada | Alineado | Evaluación del modelo y matriz de confusión | Matriz de confusión en CRISP-DM | Mantener |
| REC-37 | Finalizada | Incongruencia documental | Diseño e implementación de la base MySQL ecoscan (14 tablas) | DDL crea 15 tablas | Corregir resumen a 15 tablas |
| REC-38 | Finalizada | Alineado | Conversión del modelo relacional de PostgreSQL a MySQL 8 | 01_schema.sql MySQL 8 | Mantener |
| REC-39 | Finalizada | Alineado | Carga de datos iniciales de la aplicación | 02_seed.sql: 48 escaneos, 35 puntos | Mantener |
| REC-40 | Finalizada | Alineado | Reglas de integridad: CHECK y claves foráneas | CHECK/FK en 01_schema.sql | Mantener |
| REC-41 | Finalizada | Alineado | API FastAPI: ruta /predict con CORS y carga de best.pt | main.py /predict + best.pt | Mantener |
| REC-42 | Finalizada | Alineado | Rutas /db/... para comunas, puntos, materiales, hábitos, banners, simulador e instrucciones | rutas_db.py /db/* | Mantener |
| REC-43 | Finalizada | Alineado con matiz | Registro de cada análisis en la tabla inferencia (30/30) | inferencia registra OK/CONFIANZA_BAJA/SIN_DETECCION/BORROSA | Mantener; aclarar que 30/30 es medición histórica |
| REC-44 | Finalizada | Alineado | Soporte de fotos HEIC de iPhone en el frontend | heic2any en package.json | Mantener |
| REC-45 | Finalizada | Alineado | Arquitectura base PWA React 19 + Vite + Tailwind | React 19 + Vite + Tailwind + PWA | Mantener |
| REC-46 | Finalizada | Alineado | Pestaña Escáner IA: subida/cámara, vista previa, resultado y pasos | App.jsx Escáner IA | Mantener |
| REC-47 | Finalizada | Alineado | Pestaña Puntos Limpios RM con filtro por comuna | App.jsx + /db/puntos | Mantener |
| REC-48 | Finalizada | Sustituido | Pestaña Eco-Simulador con deslizadores e impacto anual | REC-140 quitó sliders y escenarios | Marcar como sustituido por REC-140 |
| REC-49 | Finalizada | Alineado con matiz | Pestaña Desafío Verde con 4 hábitos y barra de progreso | Desafío Verde: 25 preguntas, 4 hábitos y avance automático | Mantener; actualizar resumen |
| REC-50 | Finalizada | Alineado con matiz | Navegación entre los 4 módulos y diseño mobile-first en español | Nav = Menú Principal + 4 módulos | Corregir "4 módulos" y evitar contar Impacto como pestaña |
| REC-51 | Finalizada | Alineado | Integración frontend ↔ MySQL demostrada en video (/predict, /db/inferencias, /db/puntos) | frontend ↔ /predict y /db/* | Mantener |
| REC-52 | Finalizada | Alineado con matiz | Pruebas del sistema: 8/8 humo, 30 fotos reales y 27/30 exactos | 27/30 fotos; métrica histórica por foto, no comparable con mAP | Mantener con fecha |
| REC-53 | Finalizada | Alineado | Medición de latencia de la API (promedio ~110 ms, P95 ~130 ms) | Latencia documentada en README | Mantener |
| REC-54 | Finalizada | Alineado | Corregir error 500 con archivo que no es imagen → respuesta 400 controlada | 400 controlado en main.py | Mantener |
| REC-55 | Finalizada | Alineado | README, .gitignore y estructura de carpetas del repositorio | README raíz y .gitignore | Mantener |
| REC-56 | Finalizada | Alineado | Crear requirements.txt y .env.example sin credenciales | Plantillas unificadas: UMBRAL_NITIDEZ=50 en ambas copias y en main.py | Cerrado |
| REC-57 | Finalizada | Alineado | Publicar repositorio en GitHub y subir toda la documentación | Repo público Capstone_007 | Mantener |
| REC-58 | Finalizada | Entregable documental | Grabar video de demostración end-to-end | Video referenciado en evidencia | Mantener |
| REC-59 | Finalizada | Entregable documental | Extraer capturas del video y nombrarlas por ticket | Capturas en docs/pruebas/evidencia_visual | Mantener |
| REC-60 | Finalizada | Entregable documental | Armar PPT final de fase 3 | PPT final Fase 3 | Mantener |
| REC-61 | Finalizada | Entregable documental | Retrospectiva del proyecto: problemas y soluciones | Retrospectiva en docs/ | Mantener |
| REC-62 | Tareas por hacer | Deuda abierta coherente | Enviar PPT al profesor con anticipación | Envío al profesor pendiente | Mantener abierto |
| REC-63 | Tareas por hacer | Deuda abierta coherente | Mejorar mAP@50 de 0.562 a ≥ 0.65 | mAP real 0,562 | Mantener abierto |
| REC-64 | En curso | Deuda abierta coherente | Seguridad: regenerar API key de Roboflow y mover credenciales a .env | Clave histórica a rotar; sin valores en repo | Mantener abierto; vincular REC-122 |
| REC-65 | En curso | Deuda abierta coherente | Validar direcciones de puntos limpios y quitar "Vidrio" donde no aplica | 25 puntos externos sin validar | Mantener abierto |
| REC-66 | Finalizada | Alineado | Unificar el nombre del producto en app, Jira y PPT | Nombre EcoLearn en app/docs | Mantener |
| REC-67 | Finalizada | Alineado | Docker y Docker Compose para el backend | 3 contenedores healthy + healthchecks | Mantener; actualizar evidencia |
| REC-68 | Finalizada | Fuera de alcance declarado | Panel B2B de reportes | Sin panel B2B en main | Reclasificar como decisión documentada |
| REC-69 | Finalizada | Alineado | Pruebas E2E con Cypress | 4 pruebas Cypress | Mantener |
| REC-70 | Tareas por hacer | Deuda abierta coherente | UAT con usuarios reales | Duplica REC-18 | Ejecutado: vínculo Relates con REC-18; sigue abierta |
| REC-71 | Finalizada | Alineado | Endpoint /health y logging estructurado | /health en main.py | Mantener |
| REC-72 | Finalizada | Entregable BPMN | BPMN 01 Escáner IA: escanear un residuo (cliente) | Modelo 01 en paquete v3 | Mantener; verificar importación Bizagi |
| REC-73 | Finalizada | Entregable BPMN | BPMN 02 Servicio de inferencia POST /predict | Modelo 02 en paquete v3 | Mantener; importar en Bizagi |
| REC-74 | Finalizada | Entregable BPMN | BPMN 03 Puntos Limpios RM: buscar un punto de reciclaje | Modelo 03 en paquete v3 | Mantener; importar en Bizagi |
| REC-75 | Finalizada | Entregable BPMN | BPMN 04 Eco-Simulador RM: calcular el aporte ecológico semanal | Modelo 04 en paquete v3 | Mantener; importar en Bizagi |
| REC-76 | Finalizada | Entregable BPMN | BPMN 05 Desafío Verde RM: completar los hábitos de la semana | Modelo 05 en paquete v3 | Mantener; importar en Bizagi |
| REC-77 | Finalizada | Entregable BPMN | BPMN 06 Ciclo de vida del modelo de clasificación (MLOps) | Modelo 06 en paquete v3 | Mantener; importar en Bizagi |
| REC-78 | Finalizada | Entregable BPMN | BPMN 07 Gestión del catálogo de materiales y contenedores | Modelo 07 en paquete v3 | Mantener; importar en Bizagi |
| REC-79 | Finalizada | Entregable BPMN | BPMN 08 Curaduría y actualización de puntos limpios | Modelo 08 en paquete v3 | Mantener; importar en Bizagi |
| REC-80 | Finalizada | Entregable BPMN | BPMN 09 Verificación periódica de enlaces externos | Modelo 09 en paquete v3 | Mantener; importar en Bizagi |
| REC-81 | Finalizada | Parcial | BPMN 10 Sesión anónima, consentimiento y cuenta opcional | Sesión anónima sí; no hay consentimiento ni cuenta opcional en main | Reclasificar: quitar cuenta opcional del alcance vigente |
| REC-82 | Finalizada | Entregable BPMN | BPMN 11 Feedback de clasificación y mejora continua | Modelo 11 en paquete v3 | Mantener; importar en Bizagi |
| REC-83 | Finalizada | Entregable BPMN | BPMN 12 Reporte mensual de trazabilidad | Modelo 12 corregido: decisión "¿Continuar con otra ronda?" | Mantener; usar v3 corregida |
| REC-84 | Finalizada | Entregable BPMN | BPMN 13 Despliegue continuo y monitoreo de salud | Modelo 13 en paquete v3 | Mantener; importar en Bizagi |
| REC-85 | Finalizada | Entregable BPMN | BPMN 14 Gestión de incidentes del servicio | Modelo 14 en paquete v3 | Mantener; importar en Bizagi |
| REC-86 | Finalizada | Entregable documental con matiz | RF del módulo Escáner IA (RF-01 a RF-11, RF-25 a RF-36) | XLSX RF-15..22/44 obsoleto tras REC-140 | Relabelar como sustituidos |
| REC-87 | Finalizada | Entregable documental | RF del módulo Puntos Limpios RM (RF-12 a RF-14, RF-37 a RF-43) | RF Puntos Limpios | Mantener |
| REC-88 | Finalizada | Entregable documental con matiz | RF del módulo Eco-Simulador RM (RF-15 a RF-18, RF-44 a RF-49) | RF sliders/casillas sustituidos | Relabelar como sustituidos |
| REC-89 | Finalizada | Entregable documental con matiz | RF del módulo Desafío Verde RM (RF-19 a RF-22, RF-50 a RF-55) | RF Desafío + avance automático | Mantener; alinear con REC-137 |
| REC-90 | Finalizada | Parcial / fuera de alcance | RF transversales, cuenta y administración (RF-23, RF-24, RF-56 a RF-60) | RF-23 dice 4 módulos; cuenta y administración no implementadas | Ajustar a Menú + 4 módulos y marcar cuenta fuera de alcance |
| REC-91 | Finalizada | Entregable documental con matiz | Requisitos no funcionales (RNF-01 a RNF-40) | RNF-03/RNF-11/RNF-21 obsoletos en XLSX | Actualizar estados a implementado |
| REC-92 | Finalizada | Alineado con matiz | Brecha B-1: detección de múltiples materiales en una misma imagen | main.py itera result.boxes y agrupa conteo_clases | Alinear XLSX que dice una sola etiqueta |
| REC-93 | En curso | Deuda abierta coherente | Brecha B-3: contenedor confirmado para Aluminio | Contenedor de Aluminio en discusión | Mantener en curso |
| REC-94 | Finalizada | Alineado | Brecha B-4: conservar progreso e insignias entre visitas | localStorage conserva progreso/insignias | Mantener |
| REC-95 | Finalizada | Alineado | Brecha B-5: enlace externo caído en puntos limpios | Enlaces externos revisados | Mantener |
| REC-96 | Finalizada | Alineado | Corregir fallbacks falsos del escáner cuando falla el backend | Sin fallbacks falsos; errores mapeados en App.jsx | Mantener |
| REC-97 | Finalizada | Alineado | Quitar asteriscos literales en los textos del JSX | Textos JSX limpios | Mantener |
| REC-98 | Finalizada | Alineado | Mostrar la confianza de la detección en pantalla | Confianza visible en Escáner IA | Mantener |
| REC-99 | Finalizada | Alineado | Cambiar lang="en" y título ecoscan-frontend en index.html | index.html en español | Mantener |
| REC-100 | Finalizada | Alineado | Cambiar ícono de la PWA a PNG de 192 y 512 px | Iconos PWA 192/512 | Mantener |
| REC-101 | Finalizada | Alineado | Agregar timeout de 10 s y botón de reintento en /predict | Timeout 10 s y reintento en App.jsx | Mantener |
| REC-102 | Finalizada | Alineado | Validar tipo y tamaño de archivo antes de enviarlo | Validación de archivo en main.py | Mantener |
| REC-103 | Finalizada | Alineado | Aplicar umbral mínimo de confianza antes de aceptar una clasificación | UMBRAL_CONFIANZA=0,50 global | Mantener; NO asumir umbrales por clase |
| REC-104 | Finalizada | Alineado | Rechazar imágenes borrosas o de baja calidad | Rechazo por nitidez sin detecciones | Mantener |
| REC-105 | En curso | Deuda abierta coherente | Definir política CORS explícita para producción | CORS por entorno; falta dominio producción | Mantener en curso |
| REC-106 | Finalizada | Alineado | Implementar rate limiting por IP o sesión en /predict | Rate limit 30/min en /predict | Mantener |
| REC-107 | Finalizada | Alineado con matiz | Agregar cabeceras de seguridad CSP, X-Content-Type-Options y HSTS | CSP con relajación sólo en /docs, /redoc y /docs/*; commiteada en d85d5cd | Verificado: commiteada y subida en d85d5cd |
| REC-108 | Finalizada | Alineado | Verificar consultas parametrizadas y escape de salida | Consultas parametrizadas y escape en mapa | Mantener |
| REC-109 | Finalizada | Alineado con matiz | Auditar dependencias en el pipeline de CI | pip-audit en CI; 4 CVE moderate por debajo de high | Mantener; documentar deuda |
| REC-110 | Finalizada | Documentado como cerrado; evidencia a reforzar | Prueba de carga: 50 solicitudes concurrentes a /predict | No se localizó salida de prueba de carga | Adjuntar medición o aclarar |
| REC-111 | Finalizada | Documentado como cerrado; evidencia a reforzar | Medir LCP de carga inicial (objetivo ≤ 2,5 s en 4G) | El estudio anterior lo marca pendiente | Adjuntar medición LCP |
| REC-112 | Finalizada | Documentado como cerrado; evidencia a reforzar | Medir tamaño del bundle JS inicial (objetivo ≤ 300 KB) | Hay warning de chunk >500 KB | Adjuntar medición de bundle |
| REC-113 | Finalizada | Documentado como cerrado; evidencia a reforzar | Prueba de accesibilidad: contraste 4,5:1 y operación con teclado | El estudio anterior lo marca pendiente | Adjuntar resultados de accesibilidad |
| REC-114 | Finalizada | Documentado como cerrado; evidencia a reforzar | Prueba responsive a 360 px y en navegador WebKit | verificar_webkit.mjs existe | Adjuntar resultado WebKit |
| REC-115 | Finalizada | Documentado como cerrado; evidencia a reforzar | Alcanzar cobertura unitaria ≥ 70 % del backend | pytest con cobertura en CI | Adjuntar porcentaje real |
| REC-116 | Finalizada | Alineado con matiz | Versionar cada versión del dataset y del modelo | /version y DATASET_VERSION en main.py | Mantener |
| REC-117 | Finalizada | Alineado | Generar reporte mensual CSV de inferencias por material | /db/reporte/inferencias.csv | Mantener |
| REC-118 | Finalizada | Parcial | Configurar respaldos diarios de MySQL con RPO ≤ 24 h | respaldar_mysql.py existe pero no programa la tarea | Aclarar que el respaldo es manual |
| REC-119 | Finalizada | Parcial | Definir retención y anonimización de inferencias a 12 meses | Endpoint de retención existe, sin scheduler | Aclarar que no está programado |
| REC-120 | Finalizada | Alineado con matiz | Estandarizar ramas main, develop y feature/<ticket> | Ramas reales: main y feature/*; develop no verificada | Ajustar Convención de ramas |
| REC-121 | Finalizada | Alineado | Usar commits con formato REC-xx: descripción corta | Historial con prefijos REC | Mantener; corregir prefijos inexistentes donde se documenten |
| REC-122 | En curso | Deuda abierta coherente | Revisar que no queden claves en cuaderno ni historial | Clave histórica a rotar | Mantener; vincular REC-64 |
| REC-123 | Finalizada | Alineado | Definir Git LFS o enlace para best.pt si supera 100 MB | best.pt presente; Git LFS no configurado | Mantener |
| REC-124 | Finalizada | Alineado | Filtro de puntos limpios por material aceptado | Filtro por material en /db/puntos | Mantener |
| REC-125 | Finalizada | Alineado con matiz | Indicar si un punto está abierto según su horario estructurado | Horario estructurado simple; REC-154 abre bloques múltiples | Mantener; vincular REC-154 |
| REC-126 | Finalizada | Alineado | Enlace “Cómo llegar” usando coordenadas del punto | Enlace "Cómo llegar" con coordenadas | Mantener |
| REC-127 | Finalizada | Alineado | Ordenar puntos por cercanía con geolocalización autorizada | Geolocalización autorizada en MapaPuntos.jsx | Mantener |
| REC-128 | Tareas por hacer | Corregido el 20-11-2026 | Guardar escenarios del simulador asociados a la sesión | No hay lógica de escenarios en frontend | Ejecutado: Tareas por hacer + resumen SUSTITUIDO |
| REC-129 | Tareas por hacer | Corregido el 20-11-2026 | Comparar dos escenarios guardados del simulador | No hay comparación de escenarios | Ejecutado: Tareas por hacer + resumen SUSTITUIDO |
| REC-130 | Finalizada | Alineado | Pantalla de Menú Principal (landing) de EcoLearn Chile | Menú Principal en App.jsx | Mantener |
| REC-131 | Finalizada | Alineado | Cámara en vivo (web/rear) y captura en el Escáner IA | Cámara web/rear en Escáner IA | Mantener |
| REC-132 | Finalizada | Alineado | Configuración de VS Code para ejecutar backend y frontend sin errores | .vscode/tasks.json y scripts/ | Mantener |
| REC-133 | Finalizada | Alineado | Regresión: el frontend actual ya no convierte fotos HEIC antes de enviarlas | Conversión HEIC vigente | Mantener |
| REC-134 | Finalizada | Histórico retirado | Panel de trazabilidad y coherencia entre Jira y la app | Panel de trazabilidad eliminado por REC-136 | Mantener como decisión histórica, no funcionalidad vigente |
| REC-135 | Finalizada | Alineado | Corrección de franja negra al desplazarse en la app | background-attachment: scroll | Mantener |
| REC-136 | Finalizada | Alineado | Limpieza visual: retirar trazabilidad y avisos internos de la app | Interfaz sin trazabilidad/avisos internos | Mantener |
| REC-137 | Finalizada | Alineado | Progreso automático del Desafío Verde y estadísticas por escaneo | Progreso automático y estadísticas por escaneo | Mantener; NO usarlo como REC-162 |
| REC-138 | Finalizada | Entregable documental | Evaluación como Proyecto de Título y auditoría Jira vs App | ESTUDIO_PROYECTO_TITULO.md + esta auditoría | Actualizar con datos de 20-11-2026 |
| REC-139 | Finalizada | Alineado | Regresión visual por blur residual y confirmación de estadísticas automáticas | Blur residual corregido en App.css/App.jsx | Mantener |
| REC-140 | Finalizada | Alineado | Impacto automático del Eco-Simulador desde MySQL (reemplaza sliders y escenarios) | Impacto 30 días desde ecoscan.escaneos | Mantener; ningún slider |
| REC-141 | Finalizada | Alineado | Verificación end-to-end del stack Docker (healthchecks + /predict → MySQL) | 3 contenedores healthy y /predict → MySQL | Mantener |
| REC-142 | Finalizada | Alineado | Corregir CI: test determinista de /health y actions v7 | CI estable y PR 1 mergeado | Mantener |
| REC-143 | Finalizada | Alineado | Reorganizar el repositorio en una carpeta Fase 3 | Estructura Fase 3/ en repo | Mantener |
| REC-144 | Finalizada | Alineado | Mapa interactivo de Puntos Limpios RM con Leaflet y OpenStreetMap | MapaPuntos.jsx Leaflet/OSM | Mantener |
| REC-145 | Finalizada | Alineado | Error: mapa base CARTO dark se mostraba como fondo gris sin detalle | Fallback tras tileerror | Mantener |
| REC-146 | Finalizada | Alineado | Ampliar el catalogo a 35 puntos limpios con procedencia explicita | 35 puntos en 02_seed.sql | Mantener |
| REC-147 | Finalizada | Alineado | Error: doble codificacion CP850 en el seed MySQL de puntos limpios | Seed con codificación UTF-8 | Mantener |
| REC-148 | Finalizada | Alineado | Exponer fuente, nota y coords_aproximadas en GET /db/puntos | fuente/nota/coords_aproximadas en /db/puntos | Mantener |
| REC-149 | Finalizada | Alineado | Error: Cypress fallaba por horario NULL en los puntos externos | Manejo de horario NULL | Mantener |
| REC-150 | Finalizada | Alineado | Error: FK bloqueaba el material Reciclables (por confirmar) | FK/CHECK de materiales | Mantener |
| REC-151 | Finalizada | Alineado | Error: comentario de codificacion publicado por error en REC-143 | Comentario de codificación corregido | Mantener |
| REC-152 | Finalizada | Alineado | Error: geocodificacion devolvia comuna incorrecta en algunas direcciones | Geocodificación por comuna | Mantener |
| REC-153 | Finalizada | Entregable documental | Registrar en Jira el trabajo nuevo y los errores encontrados | Registro de trabajo nuevo en Jira | Mantener |
| REC-154 | Tareas por hacer | Deuda abierta coherente | Soportar horarios con multiples bloques y cierres parciales en la app | Horarios con múltiples bloques no implementados | Mantener abierto |
| REC-155 | Tareas por hacer | Deuda abierta coherente | Validar en terreno las coordenadas de los 25 puntos externos | 25 puntos externos sin validar en terreno | Mantener abierto |
| REC-156 | Tareas por hacer | Deuda abierta coherente | Validar materiales de los puntos externos con fuentes oficiales | Materiales externos por confirmar | Mantener abierto |
| REC-157 | Finalizada | Corregido el 20-11-2026 | Error: la PWA sirve el bundle cacheado tras un despliegue | autoUpdate + cacheId + cleanupOutdatedCaches + sw.test.js | Ejecutado: Finalizada + comentario de evidencia |
| REC-158 | Finalizada | Alineado | Error: encabezado de Puntos Limpios desalineado (filtros y boton) | Encabezado de Puntos Limpios | Mantener |
| REC-159 | Finalizada | Alineado con matiz | Error: etiqueta de region se superponia a los controles de zoom del mapa | Etiqueta de región lejos del zoom | Mantener; no interpretar "región" como login |
| REC-160 | Finalizada | Alineado | Galería interactiva de consejos y videos en el Eco-Simulador RM | Galería de consejos/videos en App.jsx | Mantener |
| REC-161 | Finalizada | Alineado con matiz | Plan de pruebas documentado con trazabilidad RF/RNF | Plan de pruebas 40 casos | Mantener; AC viven aquí, no en Jira |

Versión CSV: [`CONTRASTE_161.csv`](CONTRASTE_161.csv).
