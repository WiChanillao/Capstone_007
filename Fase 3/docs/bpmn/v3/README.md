# Paquete BPMN v3 — 14 modelos independientes

Versión vigente del modelado de procesos de **EcoLearn / EcoScan**, incorporada al repo el **21-11-2026**.

## Procedencia

- Archivo fuente: `Procesos bpm completo-20261121T001956Z-1-001.zip` (incluido en esta carpeta).
- SHA-256 del ZIP: `F7C823E3E77ED6DB74919CB1C3AA7F503C3A0CB38EDD80C0E46F77203A84358A`
- Tamaño del ZIP: 3,28 MB.
- Contenido original: 14 archivos `.bpmn` en `Archivo BPM/` y 14 `.png` en la raíz.
- Formato de entrega declarado: **BPMN 2.0 para Bizagi Modeler 4.3.0008**.
- Validación realizada al incorporarlos: 14/14 XML parseables, 14/14 PNG válidos, 0 errores.

> El modelo histórico `../EcoScan_Procesos_BPMN_v4_extendidos.bpmn` se conserva como referencia. **No sustituye a este paquete.**

## Estructura

```text
v3\
├── README.md
├── Procesos bpm completo-20261121T001956Z-1-001.zip
├── modelos\    ← 14 archivos .bpmn
└── diagramas\  ← 14 archivos .png
```

## Correspondencia con Jira

Los tickets BPMN reales del proyecto `REC` son **`REC-72`…`REC-85`** (uno por modelo).

| # | Jira | Modelo BPMN | Diagrama PNG | SHA-256 BPMN (16 chars) |
|---|---|---|---|---|
| 01 | REC-72 | `01_EscanerIA_cliente.bpmn` | `01_EscanerIA_cliente.png` | `090539e46f08fb87` |
| 02 | REC-73 | `02_ServicioInferencia_predict.bpmn` | `02_ServicioInferencia_predict.png` | `760f3a1fcc1735d5` |
| 03 | REC-74 | `03_PuntosLimpiosRM.bpmn` | `03_PuntosLimpiosRM.png` | `537340c2ea8bd3ef` |
| 04 | REC-75 | `04_EcoSimuladorRM.bpmn` | `04_EcoSimuladorRM.png` | `ed43259114c47334` |
| 05 | REC-76 | `05_DesafioVerdeRM_y_cierre_semanal.bpmn` | `05_DesafioVerdeRM_y_cierre_semanal.png` | `b8daafc3f2034149` |
| 06 | REC-77 | `06_CicloVida_ModeloML.bpmn` | `06_CicloVida_ModeloML.png` | `e2198f15261d64d6` |
| 07 | REC-78 | `07_Gestion_Catalogo_Materiales.bpmn` | `07_Gestion_Catalogo_Materiales.png` | `4a16e448244da51c` |
| 08 | REC-79 | `08_Curaduria_PuntosLimpios.bpmn` | `08_Curaduria_PuntosLimpios.png` | `69d692348ae0ed23` |
| 09 | REC-80 | `09_Verificacion_Enlaces.bpmn` | `09_Verificacion_Enlaces.png` | `9e4097b6e89a1490` |
| 10 | REC-81 | `10_Sesion_Consentimiento_Cuenta.bpmn` | `10_Sesion_Consentimiento_Cuenta.png` | `84cd0bfb59b7d844` |
| 11 | REC-82 | `11_Feedback_Clasificacion.bpmn` | `11_Feedback_Clasificacion.png` | `cca25534d0a3996a` |
| 12 | REC-83 | `12_Reporte_Trazabilidad_LeyREP.bpmn` | `12_Reporte_Trazabilidad_LeyREP.png` | `5721dd8cf70b0571` |
| 13 | REC-84 | `13_CICD_Despliegue_Monitoreo.bpmn` | `13_CICD_Despliegue_Monitoreo.png` | `4e0e9f422ae6451b` |
| 14 | REC-85 | `14_Gestion_Incidentes.bpmn` | `14_Gestion_Incidentes.png` | `361d3fee4132e06a` |

## Notas de alcance

- El modelo **12** usa la decisión **“¿Continuar con otra ronda?”**, coherente con `src/trivia.js`.
- El modelo **05** contiene 2 `process` (p05 dividido en dos pools), tal como aparece en el entregable original.
- El modelo **10 / REC-81** se sube como **entregable documental**. En el código vigente sólo existe sesión anónima (`localStorage`), sin consentimiento explícito ni cuenta opcional; ver `docs/CONTRASTE_161.md` y `docs/DOCUMENTACION_GENERAL.md`.
- Los modelos **13 y 14** documentan CI/monitoreo e incidentes. No implican que exista un job de deploy: el workflow real `.github/workflows/ci.yml` sólo valida.
