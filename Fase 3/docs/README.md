# Documentación del proyecto — EcoLearn Chile / EcoScan

Documentación vigente y entregables de las fases 1 y 2, incorporados al
repositorio para que todo quede disponible desde un solo clone.

## Documentación vigente (20-11-2026)

| Archivo | Contenido |
|---|---|
| [`RESUMEN_AUDITORIA_2026-11-20.md`](RESUMEN_AUDITORIA_2026-11-20.md) | Resumen ordenado de lo revisado, creado y corregido. |
| [`DOCUMENTACION_GENERAL.md`](DOCUMENTACION_GENERAL.md) | **Fuente única** de alcance real, nombres de módulos, flujos, API, datos y deuda conocida. |
| [`ARQUITECTURA.md`](ARQUITECTURA.md) | Diagrama Mermaid canónico auditado contra el código, flujo de inferencia y brechas del diagrama histórico. |
| [`AUDITORIA_JIRA.md`](AUDITORIA_JIRA.md) | Contraste del tablero REC (161 issues) contra `main @ af7d14d`. |
| [`jira/`](jira/) | Contraste issue por issue, inventario, mapa de claves y backlog **aplicado en Jira el 20-11-2026** (30 cambios verificados). |
| [`DECISIONES.md`](DECISIONES.md), [`ENTREGA.md`](ENTREGA.md) | Decisiones técnicas y guía de entrega; complementan la documentación general. |

| Carpeta | Contenido |
|---|---|
| `crisp-dm/` | `capstone_CRISDM_limpio.ipynb` (notebook de referencia) y `CrispDM_Ecolearn.ipynb` (versión final con validación/test y métricas por clase). La credencial de Roboflow **no** está incrustada: se lee desde Secrets de Colab / variable de entorno `ROBOFLOW_API_KEY`. |
| `requisitos/` | `EcoScan_Requisitos_Funcionales.xlsx` — **fuente única vigente** de los 100 requisitos (RF-01..RF-60, RNF-01..RNF-40), con estados reconciliados el 20-11-2026 contra `main @ af7d14d`. La copia de `Fase 2/Evidencia/` se consolidó aquí. |
| `bpmn/` | `EcoScan_Procesos_BPMN_v4_extendidos.bpmn` — 14 procesos BPMN (referencia histórica). El paquete vigente es v3, con 14 modelos BPMN 2.0 independientes para Bizagi Modeler 4.3.0008. |
| `modelo-datos/` | Modelo lógico/relacional (DOCX) y `diagrama_relacional.png` (documentan 14 tablas; el esquema real de `docker/mysql/init/01_schema.sql` tiene **15**). |
| `pruebas/` | [`MATRIZ_DE_PRUEBAS_EcoLearn_Oficial.xlsx`](pruebas/MATRIZ_DE_PRUEBAS_EcoLearn_Oficial.xlsx) (**matriz oficial vigente**: 97 casos —6 de Infraestructura Docker—, 4 hojas —`Resumen_QA`, `Casos_de_Prueba`, `Metricas_IA_y_Evidencias`, `Trazabilidad_Jira_161`—, 161 tickets y 3 gráficos) y `PLAN_DE_PRUEBAS_EcoLearn.md` (detalle técnico). `PLAN_DE_PRUEBAS_EcoLearn.xlsx` (v1.3, 40 casos) se conserva como **fuente histórica de criterios de aceptación**; `PLAN_DE_PRUEBAS_EcoLearn_CON_EVIDENCIA.docx`/`.pdf` (41 páginas) e `Informe_de_pruebas_EcoScan.docx` son instantáneas históricas: no redefinen el alcance actual. |
| `bd/` | Scripts SQL originales de esquema y datos (el stack Docker usa además `docker/mysql/init/`). |
| [`evidencia/`](evidencia/) | Ejecuciones y capturas. [`evidencia/capturas/`](evidencia/capturas/) reúne las imágenes que antes estaban sueltas en la raíz de `Fase 3/`; [`pruebas/evidencia_visual/`](pruebas/evidencia_visual/) contiene las capturas citadas por el plan de pruebas. |

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

## Revisi?n de la entrega

- [Trazabilidad de los 30 indicadores de la pauta APT](REVISION_PAUTA_APT.md).
- [Diagrama actualizado con el estilo visual de Fase 2](Arquitectura_EcoLearn_actualizada.png).
- [Cierre tecnico y matriz de riesgo](CIERRE_TECNICO.md).
