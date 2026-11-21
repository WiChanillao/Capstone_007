# Capstone 007 — EcoLearn Chile / EcoScan

Proyecto de título organizado por etapas. El recorrido se lee de arriba abajo:
**Fase 1 → Fase 2 → Fase 3**. La implementación vigente y la entrega final
están en [`Fase 3/`](Fase%203/).

## Progreso por etapas

| Etapa | Carpeta | Qué contiene | Estado |
|---|---|---|---|
| 1 — Definición | [`Fase 1/`](Fase%201/) | Guía y formatos del proyecto, autoevaluaciones, diarios y presentación de definición | Entregable histórico, conservado sin cambios |
| 2 — Desarrollo | [`Fase 2/`](Fase%202/) | Guías, diarios, arquitectura, SQL y CRISP-DM originales | Entregable histórico; la fuente vigente de requisitos está en Fase 3 |
| 3 — Implementación y entrega | [`Fase 3/`](Fase%203/) | Código, Docker, documentación canónica, auditoría Jira, pruebas y presentación final | **Vigente** |

Cada etapa tiene su propio `README.md` de entrada. Las carpetas `Fase 1` y
`Fase 2` se elevaron a la raíz desde `Fase 3/` sin reescribir el historial:
Git las registra como renombrados en commits nuevos.

## Estructura

```text
.github/                 CI de GitHub Actions (permanece en la raíz)
Fase 1/                  Definición del proyecto (entregables originales)
Fase 2/                  Desarrollo y evidencia histórica
Fase 3/
├── ecoscan-backend/     API FastAPI, YOLO11n, MySQL y pruebas
├── ecoscan-frontend/    App React + Vite + Tailwind (Menú Principal + 4 módulos)
├── docs/                Documentación canónica, requisitos, BPMN, pruebas, auditoría Jira
├── docs/evidencia/      Ejecuciones y capturas de la app (capturas/)
├── docs/pruebas/        Matriz oficial de pruebas (Excel, 97 casos + 161 tickets) y evidencia visual (evidencia_visual/)
├── docker/              Scripts de inicialización de MySQL
├── scripts/             Arranque reproducible y verificación Docker
├── .vscode/             Configuración: abre la carpeta Fase 3 en VS Code
├── docker-compose.yml   MySQL 8 + backend + frontend con healthchecks
└── README.md            Guía completa de instalación, uso y evidencia
```

`.gitignore` y `.gitattributes` permanecen en la raíz porque Git los aplica a
todo el repositorio. `.gitattributes` además indica a GitHub Linguist qué
archivos son evidencia o datos, para que el desglose de lenguajes refleje el
código real del proyecto.

## Acceso rápido

- **Alcance y documento general:** [`Fase 3/docs/DOCUMENTACION_GENERAL.md`](Fase%203/docs/DOCUMENTACION_GENERAL.md)
- Auditoría Jira vs. código (161 issues): [`Fase 3/docs/AUDITORIA_JIRA.md`](Fase%203/docs/AUDITORIA_JIRA.md)
- **Trazabilidad de datos y decisiones:** [`Fase 3/docs/TRAZABILIDAD_DATOS.md`](Fase%203/docs/TRAZABILIDAD_DATOS.md)
- **Entrega para evaluación:** [`Fase 3/docs/ENTREGA.md`](Fase%203/docs/ENTREGA.md)
- Guía completa: [`Fase 3/README.md`](Fase%203/README.md)
- Arranque rápido: [`Fase 3/INICIO_RAPIDO.md`](Fase%203/INICIO_RAPIDO.md)
- Presentación final: [`Fase 3/docs/presentacion/EcoLearn_Presentacion_Final_Fase3.pptx`](Fase%203/docs/presentacion/EcoLearn_Presentacion_Final_Fase3.pptx)
- Repo: <https://github.com/WiChanillao/Capstone_007>
