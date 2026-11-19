# Documentación del proyecto — EcoLearn Chile / EcoScan

Entregables de las fases 1 y 2, incorporados al repositorio para que todo quede
disponible desde un solo clone.

| Carpeta | Contenido |
|---|---|
| `crisp-dm/` | `capstone_CRISDM_limpio.ipynb` (notebook de referencia) y `CrispDM_Ecolearn.ipynb` (versión final con validación/test y métricas por clase). La credencial de Roboflow **no** está incrustada: se lee desde Secrets de Colab / variable de entorno `ROBOFLOW_API_KEY`. |
| `requisitos/` | `EcoScan_Requisitos_Funcionales.xlsx` — 100 requisitos (RF-01..RF-60, RNF-01..RNF-40). |
| `bpmn/` | `EcoScan_Procesos_BPMN_v4_extendidos.bpmn` — 14 procesos BPMN. |
| `modelo-datos/` | Modelo lógico/relacional (DOCX) y `diagrama_relacional.png` (14 tablas). |
| `pruebas/` | Informe de pruebas de base de datos, API y modelo de visión. |
| `bd/` | Scripts SQL originales de esquema y datos (el stack Docker usa además `docker/mysql/init/`). |

## Nota de seguridad

Los notebooks incorporados fueron revisados: no contienen la API key de
Roboflow filtrada en copias antiguas. Si necesitas volver a entrenar, crea la
variable `ROBOFLOW_API_KEY` en tu entorno o en los Secretos de Colab.
