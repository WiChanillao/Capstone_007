# Documentación del proyecto — EcoLearn Chile / EcoScan

Documentación vigente y entregables de las fases 1 y 2, incorporados al
repositorio para que todo quede disponible desde un solo clone.

## Documentación vigente (20-11-2026)

| Archivo | Contenido |
|---|---|
| [`RESUMEN_AUDITORIA_2026-11-20.md`](RESUMEN_AUDITORIA_2026-11-20.md) | Resumen ordenado de lo revisado, creado y corregido. |
| [`DOCUMENTACION_GENERAL.md`](DOCUMENTACION_GENERAL.md) | **Fuente única** de alcance real, nombres de módulos, flujos, API, datos y deuda conocida. |
| [`AUDITORIA_JIRA.md`](AUDITORIA_JIRA.md) | Contraste del tablero REC (161 issues) contra `main @ af7d14d`. |
| [`jira/`](jira/) | Contraste issue por issue, inventario, mapa de claves y backlog **aplicado en Jira el 20-11-2026** (30 cambios verificados). |
| [`DECISIONES.md`](DECISIONES.md), [`ENTREGA.md`](ENTREGA.md) | Decisiones técnicas y guía de entrega; complementan la documentación general. |

| Carpeta | Contenido |
|---|---|
| `crisp-dm/` | `capstone_CRISDM_limpio.ipynb` (notebook de referencia) y `CrispDM_Ecolearn.ipynb` (versión final con validación/test y métricas por clase). La credencial de Roboflow **no** está incrustada: se lee desde Secrets de Colab / variable de entorno `ROBOFLOW_API_KEY`. |
| `requisitos/` | `EcoScan_Requisitos_Funcionales.xlsx` — **fuente única vigente** de los 100 requisitos (RF-01..RF-60, RNF-01..RNF-40), con estados reconciliados el 20-11-2026 contra `main @ af7d14d`. La copia de `Fase 2/Evidencia/` se consolidó aquí. |
| `bpmn/` | `EcoScan_Procesos_BPMN_v4_extendidos.bpmn` — 14 procesos BPMN (referencia histórica). El paquete vigente es v3, con 14 modelos BPMN 2.0 independientes para Bizagi Modeler 4.3.0008. |
| `modelo-datos/` | Modelo lógico/relacional (DOCX) y `diagrama_relacional.png` (documentan 14 tablas; el esquema real de `docker/mysql/init/01_schema.sql` tiene **15**). |
| `pruebas/` | `PLAN_DE_PRUEBAS_EcoLearn.xlsx` (**formato oficial**, v1.3: 8 columnas, 40 casos, hoja `Evidencia` con 14 capturas) y `PLAN_DE_PRUEBAS_EcoLearn.md` (detalle técnico, v1.3): son la **fuente vigente de criterios de aceptación**. `PLAN_DE_PRUEBAS_EcoLearn_CON_EVIDENCIA.docx`/`.pdf` (41 páginas) e `Informe_de_pruebas_EcoScan.docx` son instantáneas históricas: no redefinen el alcance actual. |
| `bd/` | Scripts SQL originales de esquema y datos (el stack Docker usa además `docker/mysql/init/`). |

## Diagrama de estructura y Docker

`ESTRUCTURA_PROYECTO_DOCKER.png` es una **captura real de Docker Desktop** (no
un diagrama diseñado), tomada de la ventana del proyecto `capstone`. Muestra
los tres contenedores en ejecución con sus puertos (`mysql 3307:3306`,
`backend 8000:8000`, `frontend 127.0.0.1:5173:8080`), el estado del motor y los logs de
`/health` y `/v1/models` respondiendo `200 OK`. El texto de la captura se
verificó por OCR, no por inspección visual.

## Nota de seguridad

Los notebooks incorporados fueron revisados: no contienen la API key de
Roboflow filtrada en copias antiguas. Si necesitas volver a entrenar, crea la
variable `ROBOFLOW_API_KEY` en tu entorno o en los Secretos de Colab.
