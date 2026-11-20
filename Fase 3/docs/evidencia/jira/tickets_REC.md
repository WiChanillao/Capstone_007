# Tickets REC — Fase 2 (2026-11-20)

**Modo importación:** no hay conector MCP de Atlassian ni variables
`JIRA_EMAIL` / `JIRA_API_TOKEN` en la sesión. **No se pidió el token.** Los
tickets nuevos llevan una clave **propuesta** (`REC-162` en adelante): Jira
asigna la clave real al importar. Los commits de esta entrega usan claves
**ya existentes y verificadas** (`REC-63`, `REC-64`, `REC-103`, `REC-140`) para
no inventar clave y no reescribir commits después.

## 0. Búsqueda de duplicados (hecha antes de crear)

- Revisado `git log --all` y `docs/` buscando `REC-\d+` y por palabra clave.
- **No se duplican:** REC-64 y REC-122 (clave expuesta → sólo vincular),
  REC-105 (CSP/CORS → sólo vincular), REC-140 (evidencia → ampliar),
  REC-63 (mAP/modelo → ampliar), REC-103 (umbral de confianza → ampliar y
  vincular la Historia), REC-67 (Docker), REC-104 (fotos borrosas),
  REC-106 (rate limiting), REC-57 (publicación en GitHub), REC-161 (plan de
  pruebas, ya existente).
- La clave más alta encontrada es **REC-161**, de ahí la numeración propuesta.

## 1. Actualizaciones a tickets existentes (pegar en cada uno)

### REC-67 — Docker
- **Descripción añadir:** verificación real de `docker compose down -v` +
  `up --build -d` y `docker compose ps` con 3/3 healthy. Hardening previo en
  `f987615` y relacionados (usuario no root, puertos 127.0.0.1, password
  obligatoria, healthchecks).
- **Rama:** `experimento/generalizacion` y `feature/umbrales-por-clase`.
- **Evidencia:** `docs/evidencia/docker_umbrales.txt`,
  `docs/evidencia/estado_pagina_2026-11-20/compose_ps_*.txt` y
  `health_*.txt`.
- **Pruebas:** `/health` 200 en 8000 y 5173; `/predict` 200 con las claves
  nuevas. Password local registrado como `***`.
- **Estado:** listo para cerrar con evidencia.

### REC-104 — Bug: mensaje genérico por filtro de nitidez
- **Causa:** doble. Backend con `UMBRAL_NITIDEZ=100` rechazaba por blur antes
  de YOLO; frontend sobrescribía el mensaje específico con “Revisa tu conexión”.
- **Corrección:** `86be6f7` (YOLO primero, 200 con aviso si hay detecciones),
  `69b4717` (`ErrorApi` + mapa de códigos), `6cded14` (mapa local gana),
  `cbd87b8` y `62c73a2` (umbral 50 documentado/inyectado).
- **Evidencia:** `docs/evidencia/diagnostico_400.md` y
  `docs/evidencia/estado_pagina_2026-11-20/main_d_baja_nitidez.png`.
- **Pruebas:** detección con laplaciano ≈30 < 50 → 200 + aviso; pytest 42
  passed en la rama feature; 0 errores de consola.
- **Estado:** corregido y verificado.

### REC-106 — Bug: rate limit por IP compartida / proxy
- **Causa:** todos los visitantes compartían la IP de nginx y el gateway
  publicado podía falsificar `X-Forwarded-For`.
- **Corrección:** `f82f420` (IP real sólo desde `RED_PROXY_CONFIABLE`) y
  `7b8750f` (excluye la primera IP usable de cada red confiable).
- **Evidencia:** `docs/evidencia/diagnostico_400.md` verificación 4.
- **Pruebas:** 30×422 + 429 en la 31.ª tanto desde el puerto publicado como
  desde nginx; 2 pruebas nuevas.
- **Estado:** corregido y verificado.

### REC-105 — CSP / CORS
- **Sólo vincular:** `8b9c194` (CORS y CSP por entorno sin comodines). No se
  crea ticket nuevo. Evidencia en `diagnostico_400.md` FASE 2.

### REC-64 / REC-122 — Rotación de claves Roboflow / Google
- **Sólo vincular:** no se escribe ningún valor de clave en repo, Jira ni
  chat. `README.md` ya documenta la rotación pendiente. Estado: **Por hacer**
  (no ejecutada desde esta sesión).

### REC-63 — Modelo / mAP
- **Descripción añadir:** análisis de generalización del `best.pt` sin
  reentrenar: 215 originales, 60 % de copias con motion blur/cutout, fuga de
  escena (38/61 valid, 16/31 test), 9 pares de fuga real por hash, bootstrap
  AP50 por clase y experimento A/B/C Stretch vs letterbox (evidencia parcial).
- **Rama:** `experimento/generalizacion`.
- **Evidencia:** `docs/evidencia/generalizacion.md`,
  `medicion_generalizacion.md`, `exp_geometria.md`,
  `auditoria_dataset.md/.json`, `datasets_experimentales.md/.json`.
- **Pruebas:** mAP@50 oficial 0,562 @ conf 0,001 intacto; 0,429 en test @
  conf 0,50 (otro punto de operación, no comparable).
- **Estado:** en curso, con evidencia nueva.

### REC-103 — Umbral de confianza
- **Descripción añadir:** evolución a umbrales por clase y nivel “posible” en
  `feature/umbrales-por-clase`. Vincular la Historia `REC-167` (propuesta).
- **Evidencia:** `docs/evidencia/umbrales_por_clase.md`,
  `evaluacion_umbrales_test.md/.json`.
- **Resultado:** defaults 0,50 y 0,20 sin cambios. Estado: en curso.

### REC-140 — Evidencia
- **Añadir:** carpeta `docs/evidencia/estado_pagina_2026-11-20/` (12 capturas
  sanitizadas, ~5,1 MB), `umbrales_por_clase.md`,
  `evaluacion_umbrales_test.*`, `docker_umbrales.txt`,
  `generalizacion.md`, `medicion_generalizacion.*`, `exp_geometria.*`.
- **Adjuntos:** las 12 capturas de la carpeta indicada.
- **Estado:** evidencia disponible; no marcar “Hecho” hasta importar y adjuntar.

### REC-57 — Publicar repositorio
- **Añadir:** push previsto de `experimento/generalizacion` y
  `feature/umbrales-por-clase`; **no se hace push de `main`**, sin PR sin OK.
- **Estado:** en curso.

### REC-161 — Plan de pruebas
- **Añadir:** evidencia visual de la Fase 1 (11 OK / 1 FALLA) y vínculo al
  Bug `REC-162` (propuesto). Estado: actualizado.

## 2. Tickets nuevos (texto listo para pegar; mismos datos en `tickets_REC.csv`)

### REC-162 (propuesta) — Bug — Desafío Verde repite preguntas
**Descripción:** en `main` @ 62c73a2, 9 respuestas seguidas (3 rondas) devuelven
1-2-3, 1-2-3, 1-2-3. **Causa:** `TRIVIA_VERDE` tiene 3 preguntas y
`siguienteTrivia()` usa `(i + 1) % TRIVIA_VERDE.length`, sin baraje ni
reposición. **Rama:** `main` (afecta también a `feature/umbrales-por-clase`).
**Evidencia:** `docs/evidencia/estado_pagina_2026-11-20/README.md`,
`resultados_navegador.json`. **Capturas adjuntas:**
`main_g_desafio_ronda1.png`, `main_g_desafio_ronda2.png`. **Pruebas:**
Playwright headless aislado, 3 rondas, 0 errores de consola. **Estado:**
Abierto, sin corrección.

### REC-163 (propuesta) — Bug — constraint `ck_inf_ok_material`
**Descripción/Causa:** el CHECK exigía `(resultado='OK') = (id_material IS NOT
NULL)` y fallaba al guardar `CONFIANZA_BAJA` con clase detectada (ERROR 3819).
**Corrección:** commit `9859e3e`. **Evidencia:** `diagnostico_400.md` FASE 2 y
verificación 2 (62 filas conservadas, constraint migrado, inserción ahora
correcta). **Pruebas:** pytest 36 passed en el momento del fix. **Estado:**
corrección aplicada, pendiente de cerrar.

### REC-164 (propuesta) — Tarea — Validación de `/predict`
**Descripción:** límite 10 MB (`eaf3187`), whitelist MIME y 8000×8000
(`1ab6a3a`, `47f2869`), `id_sesion` (`56ccaff`, `c6fa516`), contrato único de
errores (`045b9f7`). **Evidencia:** `diagnostico_400.md`, `tests/test_main.py`.
**Pruebas:** backend pytest 36 passed entonces; 42 passed ahora en la rama
feature. **Estado:** implementado y verificado.

### REC-165 (propuesta) — Bug/Tarea — caché del PWA con bundle viejo
**Descripción/Causa:** el SW servía bundle anterior y apuntaba a
`127.0.0.1:8000`. **Corrección:** `e0204ac` (`autoUpdate`, `ecolearn-v2-`,
`cleanupOutdatedCaches`). **Evidencia:** `diagnostico_400.md` verificación 3,
`src/sw.test.js` (3 pruebas). **Estado:** corregido, pendiente de cerrar.

### REC-166 (propuesta) — Tarea — plan de experimentos Colab E0-E3
**Descripción:** E0 baseline v1, E1 nitidez, E2 split por escenas, E3
geometría; 3 semillas por configuración, selección por valid, test una sola
vez, latencia <100 ms. Sin API key ni descargas de Roboflow. **Rama:**
`experimento/generalizacion`. **Evidencia:**
`docs/experimentos/experimentos_yolo.ipynb` (7 celdas verificadas),
`plan_entrenamiento.md`, `paquetes_colab.json`. **Vinculados:** REC-63, REC-64.
**Estado:** plantilla lista, ejecución en Colab pendiente.

### REC-167 (propuesta) — Historia — umbrales por clase y nivel “posible”
**Descripción:** `UMBRAL_ALUMINIO/CARTON/PLASTICO` default 0,50 y
`UMBRAL_POSIBLE` default 0,20; `detecciones_posibles` en campo aparte con
aviso “Posible \<material\> (confianza baja)”, sin sumar al conteo;
`imgsz=640`. **Rama:** `feature/umbrales-por-clase`. **Evidencia:**
`umbrales_por_clase.md`, `evaluacion_umbrales_test.md/.json`,
`docker_umbrales.txt`. **Pruebas:** pytest 42 passed, vitest 18 passed, Docker
3/3 healthy. **Resultado:** +0,082 recall total y +10 FP en test; defaults NO
aplicados. **Vinculado:** REC-103. **Estado:** en curso.

### REC-168 (propuesta) — Tarea — DECISIONES.md y ENTREGA.md
**Descripción:** documentos ya en `9ba3810` y `9821476`; revisar que reflejen
los dos puntos de operación, la generalización y los umbrales no aplicados.
**Evidencia:** `docs/evidencia/generalizacion.md`, `umbrales_por_clase.md`.
**Estado:** por verificar.

### REC-169 (propuesta) — Tarea — reglas permanentes en `AGENTS.md`
**Descripción:** Git sin `--force`/reescritura/mezcla de `main` sin OK; Jira
con ticket por cambio y sin duplicar REC-64/122/105/140; evidencia sin datos
personales y escaneo de secretos antes de commit; verificación con pytest,
vitest y stacks aislados. **Evidencia:** `AGENTS.md` en la raíz.
**Estado:** versionado en los commits `9616280` y `aa20fb8`.

### REC-170 (propuesta) — Bug — CI falla en pruebas unitarias del frontend
**Descripción:** en `main` @ 62c73a2 y en `feature/umbrales-por-clase` @
aa20fb8, el job `frontend` de *CI EcoLearn Chile* falla en el paso
“Pruebas unitarias” (`npm run test:unit`); el job `backend` pasa.
**Causa probable:** `.github/workflows/ci.yml` ejecuta `test:unit` en la línea
44 antes de `npm run build` en la línea 48, y `src/sw.test.js` lee
`dist/sw.js`, ausente en un checkout limpio. Localmente vitest pasa (18
pruebas) si se ejecuta `npm run build` primero. **Sin acceso a los logs** (403,
se requieren permisos de administrador). **Evidencia:** runs
`44657570481` (main) y `44667984006` (feature). **Estado:** En curso, sin
modificar el workflow sin autorización.

## 3. Tabla resumen

| Clave | Tipo | Resumen | Estado |
|---|---|---|---|
| REC-67 | Tarea | Docker hardening y verificación 3/3 healthy | Listo para cerrar con evidencia |
| REC-104 | Bug | Error genérico por filtro de nitidez y mensaje sobrescrito | Corregido y verificado |
| REC-106 | Bug | Rate limit por IP compartida / proxy confiable | Corregido y verificado |
| REC-105 | Bug | CSP/CORS (sólo vincular) | Sin duplicar; vincular |
| REC-64 / REC-122 | Tarea | Rotación de claves (sin valores) | Por hacer |
| REC-63 | Tarea | Análisis de generalización | En curso con evidencia |
| REC-103 | Tarea | Umbral de confianza → vincular REC-167 | En curso |
| REC-140 | Tarea | Evidencia y capturas | Evidencia disponible |
| REC-57 | Tarea | Publicación en GitHub | En curso (sin push de main) |
| REC-161 | Tarea | Plan de pruebas | Actualizado |
| REC-162 (prop.) | Bug | Desafío repite 3 preguntas | **Abierto (FALLA Fase 1)** |
| REC-163 (prop.) | Bug | Constraint `ck_inf_ok_material` | Corregido, por cerrar |
| REC-164 (prop.) | Tarea | Validación `/predict` | Implementado, por cerrar |
| REC-165 (prop.) | Bug | Caché PWA bundle viejo | Corregido, por cerrar |
| REC-166 (prop.) | Tarea | Plan Colab E0-E3 | Plantilla lista |
| REC-167 (prop.) | Historia | Umbrales por clase y “posible” | En curso |
| REC-168 (prop.) | Tarea | DECISIONES.md / ENTREGA.md | Por verificar |
| REC-169 (prop.) | Tarea | Reglas en AGENTS.md | Versionado |
| REC-170 (prop.) | Bug | CI falla en `test:unit` del frontend | **En curso (CI fallido)** |

## 4. Cómo importar en Jira

1. Abrir `capstone-reci-smart.atlassian.net` → **Configuración de proyecto →
   Importar tickets → CSV**.
2. Seleccionar `tickets_REC.csv` con codificación UTF-8 y delimitador coma.
3. Mapear columnas: `Summary`→Summary, `Issue Type`→Issue Type,
   `Description`→Description, `Labels`→Labels, `Priority`→Priority,
   `Status`→Status, `Epic Link`→Epic Link (el de REC-167 es REC-103; si el
   proyecto no permite épicos, dejarlo vacío).
4. **Antes de importar**, buscar `REC-162`…`REC-170` por si ya se crearon;
   si existen, no importar esa fila y vincular al existente.
5. Tras importar, anotar las claves reales y pegar el texto de la sección 1 en
   los tickets existentes. Adjuntar las capturas de
   `docs/evidencia/estado_pagina_2026-11-20/` a REC-140 y REC-162.
6. No marcar nada como “Hecho” sin adjuntar la captura o la salida real de
   prueba indicada en cada ticket.

## 5. Fase 4 — trazabilidad tras el push

Ramas publicadas (sin `--force`, sin reescribir historial, **sin push de
`main`**):

- `experimento/generalizacion` →
  https://github.com/WiChanillao/Capstone_007/tree/experimento/generalizacion
- `feature/umbrales-por-clase` →
  https://github.com/WiChanillao/Capstone_007/tree/feature/umbrales-por-clase

| Ticket | Rama | Commits | CI | Evidencia / estado |
|---|---|---|---|---|
| REC-63 | `experimento/generalizacion` | `8f93638` | No aplica: `ci.yml` sólo dispara en `main`, `develop` y `feature/**` | `generalizacion.md`, `medicion_generalizacion.*`, `exp_geometria.*` |
| REC-64 | `experimento/generalizacion` | `586fea9` | No aplica en esta rama | `docs/experimentos/*`, notebook de 7 celdas |
| REC-140 / REC-169 | ambas | `9616280`, `aa20fb8` | Ver filas de cada rama | 12 capturas en `estado_pagina_2026-11-20/`, `AGENTS.md`, `tickets_REC.*` |
| REC-103 / REC-167 | `feature/umbrales-por-clase` | `de3704e`, `aa20fb8` | Run `44667984006`: frontend **failure** en “Pruebas unitarias”, backend en curso | 42 pytest + 18 vitest locales, Docker 3/3 healthy → **En curso**, no cerrar con CI rojo |
| REC-67 | `feature/umbrales-por-clase` | `de3704e`, `aa20fb8` | Ídem | `docker_umbrales.txt`, `/health` 200, `/predict` 200 |
| REC-162 | sin commit (bug abierto) | — | — | 3 rondas repetidas en `resultados_navegador.json`; capturas `main_g_desafio_ronda1/2.png` |
| REC-170 | sin commit (bug del workflow) | — | Run `44657570481` en `main` y `44667984006` en feature: frontend failure en “Pruebas unitarias” | `.github/workflows/ci.yml` líneas 43-48 → **En curso** |
| REC-57 | ambas | pushes realizados | — | Sin PR abierta; pendiente del OK del usuario |

**CI en `main` @ 62c73a2:** run `44657570481`, job `frontend` fallido en
“Pruebas unitarias”, job `backend` correcto. Es un estado **preexistente** en
`main`, no introducido por estos cambios; se registra en REC-170.

**CI en `experimento/generalizacion`:** no se generó run porque el workflow no
incluye ese patrón de rama. No es un fallo, pero conviene añadir el patrón si
se quiere cobertura (cambio no realizado sin autorización).

Las capturas se adjuntan a REC-140 y REC-162; las salidas de prueba a
REC-103/REC-167, REC-104, REC-106 y REC-67. Ningún ticket se marca “Hecho”
mientras el CI del frontend esté en rojo.
