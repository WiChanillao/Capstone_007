# Mapa de claves históricas / propuestas frente al tablero REC real

**Fecha:** 20-11-2026  
**Regla:** el tablero en vivo contiene `REC-1` … `REC-161`. Toda clave superior no existe.  
**Uso:** explicar prefijos `REC-xx` que aparecen en commits, documentos o ramas sin reescribir el historial ni inventar tickets.  
**Verificación 20-11-2026:** `REC-162`, `REC-167` y `REC-170` se trataron en el backlog como **“verificado, sin cambio”**: no existen y no se crearon.

| Clave citada históricamente | Origen del prefijo | Situación en Jira hoy | Evidencia real / destino |
|---|---|---|---|
| `REC-162` — Desafío Verde repetía 3 preguntas por ronda | CSV/artefactos de la rama `experimento/generalizacion` (`tickets_nuevos.csv`, `tickets_REC.md`) | **No existe** | Fix mergeado en PR 2 (`af7d14d`); commits `88e72b1`, `17ce4e5`. El ticket real `REC-137` cubre progreso automático/estadísticas, **no** la repetición de preguntas: no presentarlo como equivalente funcional. |
| `REC-163` — migración `ck_inf_ok_material` | Ídem | **No existe** | Commit `9859e3e`; 62 filas conservadas. Documentar como tarea de BD ya aplicada, sin clave nueva hasta que Jira la asigne. |
| `REC-164` — validación de `/predict` (10 MB, MIME, 8000×8000, `id_sesion`) | Ídem | **No existe** | Commits `eaf3187`, `1ab6a3a`, `47f2869`, `56ccaff`, `c6fa516`, `045b9f7`; contrato 4xx `codigo/mensaje/campo`. Cubierto por código y pruebas en `main`. |
| `REC-165` — caché PWA servía bundle viejo | Ídem | **No existe** | Commit `e0204ac`; en `main` están `registerType: 'autoUpdate'`, `cacheId: 'ecolearn-v2-'`, `cleanupOutdatedCaches` y `sw.test.js`. El ticket real `REC-157` fue cerrado (`Finalizada`) el 20-11-2026 con comentario de evidencia; no crear `REC-165`. |
| `REC-166` — plan de experimentos Colab E0–E3 | Ídem | **No existe** | Relacionado con `REC-63` y `REC-64` (mAP y rotación de clave). La ejecución en Colab sigue pendiente; no marcar como terminada. |
| `REC-167` — umbrales por clase y nivel “Posible” | Ídem; se etiquetó erróneamente como épica de `REC-103` | **No existe** | `REC-103` es **sólo umbral global `0,50`**. Los umbrales por clase y “Posible” viven en `feature/umbrales-por-clase`, **no mergeada**: son **NO EN MAIN** y deben permanecer fuera del alcance. Commits de rama: `de3704e`, `aa20fb8`, `d153d4c`, `6601c37`. |
| `REC-168` — documentación para el profesor | Ídem | **No existe** | Trabajo real: `docs/DECISIONES.md`, `docs/ENTREGA.md`, `ESTUDIO_PROYECTO_TITULO.md` y este paquete de auditoría. |
| `REC-169` — reglas permanentes en `AGENTS.md` | Ídem | **No existe** | `AGENTS.md` **no está en `main`**; sólo aparece en commits históricos y en la worktree de `feature/umbrales-por-clase`. No citarlo como archivo vigente. |
| `REC-170` — CI ejecutaba `test:unit` antes de `build` | Ídem | **No existe** | Fix mergeado en PR 1 (`092fc88`); commit `4e1118a`, run `44669949452` en verde. `ci.yml` ya tiene trigger `fix/**` y orden `build → test:unit`. No abrir ni dejar pendiente este ticket. |

## Reglas para cualquier importación futura

1. Buscar por **resumen**, nunca por clave: las claves `REC-162`…`REC-170` son inválidas en este tenant.
2. Usar únicamente estados reales: `Finalizada`, `En curso`, `Tareas por hacer` (y `En revisión` si se habilita). No importar `To Do`, `In Progress`, `Abierto`, etc.
3. Dejar `Epic Link` vacío cuando la épica destino no admita la historia; en particular, **no** colgar “umbrales por clase” de `REC-103`.
4. Adjuntar los criterios de aceptación desde `docs/pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx`; no redactar criterios nuevos.
5. No escribir credenciales ni tokens en comentarios de Jira.
