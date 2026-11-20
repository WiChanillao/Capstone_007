# Criterios de aceptación — fuente vigente e incorporación a Jira (aplicada el 20-11-2026)

**Fecha:** 20-11-2026  
**Hecho verificable:** la exportación de Jira (190 campos) **no contiene** ningún campo de “criterios de aceptación”. Por tanto, no se inventan criterios nuevos: se reutilizan los del plan de pruebas oficial.

## 1. Fuente autoritativa

- [`../pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx`](../pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx), hoja `Plan de pruebas`, columna **“Criterios de aceptación”**, 40 casos (`001`…`040`).
- Equivalencia documentada en [`../pruebas/PLAN_DE_PRUEBAS_EcoLearn.md`](../pruebas/PLAN_DE_PRUEBAS_EcoLearn.md): los IDs `001`…`040` del Excel corresponden a `CP-01`…`CP-40` del Markdown (sección “Correspondencia con el Excel”).
- El corchete inicial del Excel (`[RF-03]`, `[RNF-02]`, `[REC-140]`) indica el requisito o ticket que verifica el caso; **`CP` significa caso de prueba, no requisito**.

## 2. Casos clave para el reconocimiento de residuos y el tablero REC

| Ticket Jira | Caso | Criterio de aceptación real (texto del plan) | Estado del caso | Acción en Jira (20-11-2026) |
|---|---|---|---|---|
| `REC-142`, `REC-71` | CP-01 | `GET /health` con MySQL disponible → 200, `mysql_conectado:true`, `modelo_activo:"best.pt"` | Ejecutado | Copiar como comentario/AC de evidencia. |
| `REC-142` | CP-02 | `GET /health` sin MySQL → 200 con estado `degraded`; **no** forzar 200 | Ejecutado | Copiar como AC; dejar claro que `degraded` es correcto. |
| `REC-140`, `REC-128`, `REC-129` | CP-24 | Simulador sin controles manuales: no existen `input[type=range]` ni “Guardar escenario” | Ejecutado | Usar como AC para justificar el cierre/reclasificación de `REC-128`/`REC-129`. |
| `REC-160` | CP-25 | Clic en flecha siguiente/anterior → cambian juntos foto, título y contador “Consejo N de 3” | Ejecutado | Copiar como AC. |
| `REC-160` | CP-26 | Abrir video → modal con `youtube-nocookie.com/embed/...`, sin autoplay, cierra con ✕ | Ejecutado | Copiar como AC. |
| `REC-140` | CP-28 | Abrir panel de impacto → cifras desde MySQL, texto «sin carga manual» | Ejecutado | Copiar como AC de `REC-140`. |
| `REC-105` | CP-36 | CORS con dominio de producción: orígenes explícitos, **sin `*`** | Pendiente | Mantener `REC-105` en curso hasta definir el dominio. |
| `REC-18`, `REC-70` | CP-40 | UAT y SUS con usuarios reales. El CSV de `n=14` **no** es SUS | Sin ejecutar | Mantener abiertas; no adjuntar ningún CSV de diagnóstico como SUS. |

## 3. Cambios de línea base que los AC ya reflejan

El plan de pruebas registra explícitamente qué requisitos del XLSX quedaron **sustituidos** y cuáles siguen vigentes:

| Requisitos | Situación real | Ticket |
|---|---|---|
| RF-15, RF-16, RF-17, RF-44 — deslizadores e impacto anual | **Sustituido** por impacto automático de los últimos 30 días desde `ecoscan.escaneos`; no hay sliders | `REC-140` |
| RF-45, RF-47, RF-48, RF-49 — rangos, guardar/comparar escenarios y reset | **Retirados** por decisión de diseño | `REC-140` |
| RF-19…RF-22 — casillas, progreso e insignia manual | **Sustituido** por desafíos que se activan solos con escaneos reales | `REC-137`, `REC-160` |
| RNF-03 — `GET /health` | **Implementado**; sin MySQL responde `degraded` | `REC-142` |

## 4. Reglas para cualquier incorporación a Jira

1. Copiar el texto del Excel/Markdown; **no reformular criterios nuevos**.
2. No se creó un field personalizado: los AC se pegaron como comentario con prefijo `AC (plan de pruebas) — CP-xx` en 17 tickets abiertos; las épicas llevaron la referencia al plan de pruebas.
3. Mantener el AC de `REC-105` como pendiente: no marcar CORS de producción como cerrado sin dominio real.
4. Mantener `REC-18`/`REC-70` abiertos: el artefacto de `n=14` es salida de `tests/diagnostico_400.py`, no una encuesta SUS.
5. No adjuntar valores de `.env`, tokens ni claves junto con la evidencia.

**Resultado aplicado:** los 17 tickets abiertos recibieron el comentario de AC; las épicas `REC-20`, `REC-21` y `REC-24` recibieron la referencia al plan. No se creó ningún campo personalizado y la verificación devolvió 0 anomalías.

> Nota de coherencia: el plan de pruebas no nombra el código de error de archivo
> pesado, pero `main.py` usa `ARCHIVO_MUY_PESADO` y una evidencia histórica
> (`EVIDENCIA_DOCKER.md`) decía `ARCHIVO_MUY_GRANDE`; cualquier AC que cite un
> código distinto debe ajustarse al código real antes de pegarse en Jira.
