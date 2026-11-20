# Documentación del proyecto — EcoLearn Chile / EcoScan

Entregables de las fases 1 y 2, incorporados al repositorio para que todo quede
disponible desde un solo clone.

| Carpeta | Contenido |
|---|---|
| `crisp-dm/` | `capstone_CRISDM_limpio.ipynb` (notebook de referencia) y `CrispDM_Ecolearn.ipynb` (versión final con validación/test y métricas por clase). La credencial de Roboflow **no** está incrustada: se lee desde Secrets de Colab / variable de entorno `ROBOFLOW_API_KEY`. |
| `requisitos/` | `EcoScan_Requisitos_Funcionales.xlsx` — 100 requisitos (RF-01..RF-60, RNF-01..RNF-40). |
| `bpmn/` | `EcoScan_Procesos_BPMN_v4_extendidos.bpmn` — 14 procesos BPMN. |
| `modelo-datos/` | Modelo lógico/relacional (DOCX) y `diagrama_relacional.png` (14 tablas). |
| `pruebas/` | `PLAN_DE_PRUEBAS_EcoLearn.xlsx` (**formato oficial**: plantilla de 8 columnas, 40 casos, listas desplegables y hoja `Evidencia` con 14 capturas), `PLAN_DE_PRUEBAS_EcoLearn.md` (detalle técnico), `PLAN_DE_PRUEBAS_EcoLearn_CON_EVIDENCIA.docx`/`.pdf` (41 páginas con anexo visual) y `Informe_de_pruebas_EcoScan.docx` (resultados Fase 2). |
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
