# Comentarios para tickets REC existentes (modo importación)

No hay conector MCP de Atlassian ni variables `JIRA_EMAIL`/`JIRA_API_TOKEN` en
la sesión; **no se pidió el token**. Este archivo contiene el texto listo para
pegar como comentario en los tickets que **ya existen**. Los tickets nuevos
están en `tickets_nuevos.csv` (claves propuestas `REC-162`…`REC-170`).

## Cómo importar sin duplicar

1. En `capstone-reci-smart.atlassian.net`, buscar primero `REC-162` … `REC-170`
   y, por palabra clave, *Desafío*, *constraint*, *predict*, *PWA*, *Colab*,
   *umbrales*, *DECISIONES*, *AGENTS*, *CI*. Si alguna clave o resumen ya
   existe, **no importar esa fila**: añadir el comentario de este archivo al
   ticket existente y vincularlo.
2. Configuración de proyecto → **Importar tickets → CSV**. Seleccionar
   `tickets_nuevos.csv` con codificación UTF-8 y delimitador coma.
3. Mapear `Summary`, `Issue Type`, `Description`, `Labels`, `Priority`,
   `Status` y `Epic Link`. La única fila con épico es `REC-167` → `REC-103`;
   si el proyecto no permite épicos, dejar el campo vacío.
4. Tras importar, anotar las claves reales en la **tabla de equivalencias** al
   final de este archivo. No se reescriben las claves propuestas en los
   comentarios: la tabla es la única fuente de correspondencia.
5. Adjuntar las capturas de `docs/evidencia/estado_pagina_2026-11-20/` a
   REC-140 y REC-162, y las salidas de prueba a REC-103/104/106/67/170.
6. No marcar nada como “Hecho” sin captura o salida real de prueba. Ningún
   secreto se escribe en Jira: la contraseña local aparece como `***`.

---

## REC-57 — Publicar repositorio

- **Ramas publicadas** (sin `--force`, sin reescritura, sin push de `main`):
  - `experimento/generalizacion` @ `17ffe8a` —
    https://github.com/WiChanillao/Capstone_007/tree/experimento/generalizacion
  - `feature/umbrales-por-clase` @ `aa20fb8` —
    https://github.com/WiChanillao/Capstone_007/tree/feature/umbrales-por-clase
  - `fix/ci-orden-pasos` @ `f3e13e5` —
    https://github.com/WiChanillao/Capstone_007/tree/fix/ci-orden-pasos
  - `fix/desafio-preguntas` @ `17ce4e5` —
    https://github.com/WiChanillao/Capstone_007/tree/fix/desafio-preguntas
- `main` sigue en `62c73a2646e7d7b1cd4e420f88ba1706aa841d25`.
- **Sin PR abierta**: pendiente del OK explícito del usuario.
- **Estado:** en curso.

## REC-63 — Modelo / mAP

- **Rama:** `experimento/generalizacion`. **Commit:** `8f93638`.
- Análisis del `best.pt` **sin reentrenar**. SHA-256
  `CA855386EBB5A45FE8EEB52F3D43A88D2F4C3FE830506ED31CEB4F21E1FBB9B7`.
- mAP@50 oficial **0,562 @ conf 0,001 intacto**; 0,429 en test @ conf 0,50 es
  otro punto de operación y no se compara con el oficial.
- Dataset: 215 originales ×4 en train, 860/61/31 train/valid/test, 307
  originales únicos, 9 pares de fuga real por hash; fuga de escena 38/61 valid
  y 16/31 test. Bootstrap AP50 Aluminio test 0,505, IC [0,128; 0,832], 8
  instancias: no concluyente.
- A/B/C Stretch vs letterbox: valid `0,4399 / 0,4078 / 0,4513`; test
  `0,4369 / 0,4402 / 0,4751` → evidencia parcial.
- **Evidencia:** `docs/evidencia/generalizacion.md`,
  `medicion_generalizacion.md/.json`, `exp_geometria.md/.json`,
  `auditoria_dataset.md/.json`, `datasets_experimentales.md/.json`.
- **Estado:** en curso con evidencia nueva; no marcar Hecho sin adjuntar.

## REC-64 — Revisión del Colab / rotación de claves

- **Rama:** `experimento/generalizacion`. **Commit:** `586fea9`.
- Plantilla `docs/experimentos/experimentos_yolo.ipynb` con 7 celdas
  verificadas: JSON y código válidos, sin `userdata`/`API_KEY`, Drive montado,
  semillas 0/1/2. **No se usó API key ni se descargó de Roboflow.**
- Zips entregados fuera del repo: `train_nitido.zip` (`faad99aa…`) y
  `split_por_escenas.zip` (`2625cd55…`) en
  `C:\Users\bruno diaz\Desktop\paquetes_colab`.
- Históricamente REC-64 también cubre la **rotación pendiente** (`e22a54f`);
  vincular con REC-122. **No se ejecutó la rotación y no se escribió ningún
  valor de clave en repo, Jira ni chat.**
- **Estado:** plantilla lista; ejecución en Colab y rotación pendientes.

## REC-67 — Docker

- Hardening previo en `f987615` (usuario no root, puertos en 127.0.0.1,
  password obligatoria, healthchecks).
- Verificación real con `docker compose down -v` + `up --build -d`: **3/3
  healthy** en los stacks aislados y en `ecolearn-desafio-aud`
  (5176/8003/3310). `/health` 200 y `/predict` 200. Stack del usuario intacto.
- **Ramas:** `experimento/generalizacion`, `feature/umbrales-por-clase`,
  `fix/desafio-preguntas`.
- **Evidencia:** `docs/evidencia/docker_umbrales.txt`,
  `estado_pagina_2026-11-20/compose_ps_*.txt` y `health_*.txt`.
- Contraseña local registrada como `***`. **Estado:** listo para cerrar con
  evidencia.

## REC-103 — Umbral de confianza

- **Rama:** `feature/umbrales-por-clase`. **Commits:** `de3704e`, `aa20fb8`.
- Evolución a umbrales por clase (`UMBRAL_ALUMINIO/CARTON/PLASTICO`, default
  0,50) y `UMBRAL_POSIBLE` default 0,20; `detecciones_posibles` en campo
  aparte, sin sumar al conteo; `imgsz=640` explícito.
- **Pruebas locales:** pytest 42 passed, vitest 18 passed, Docker 3/3 healthy.
- Evaluación en test (sólo reporte): +0,082 recall total y +10 FP; **defaults
  NO aplicados**.
- CI de esa rama: run `44667984006`, job frontend fallido por el orden de
  `sw.test.js` (explicado y corregido en REC-170); no se marcó Hecho con CI
  rojo. Vincular la Historia `REC-167` (propuesta).
- **Evidencia:** `umbrales_por_clase.md`, `evaluacion_umbrales_test.md/.json`.
- **Estado:** en curso.

## REC-104 — Mensaje genérico por filtro de nitidez

- **Causa doble:** backend con `UMBRAL_NITIDEZ=100` rechazaba por blur antes
  de YOLO; frontend sobrescribía el mensaje específico con “Revisa tu
  conexión”.
- **Correcciones:** `86be6f7`, `69b4717`, `6cded14`, `cbd87b8`, `62c73a2`.
- **Pruebas:** laplaciano ≈30 < 50 → 200 con aviso y detección; pytest 36
  passed; 0 errores de consola en la captura
  `main_d_baja_nitidez.png`.
- **Evidencia:** `docs/evidencia/diagnostico_400.md` y carpeta
  `estado_pagina_2026-11-20/`. **Estado:** corregido y verificado.

## REC-105 — CSP / CORS

- **Sólo vincular**, no crear ticket nuevo. Commit `8b9c194`: CORS y CSP por
  entorno, sin comodines. Evidencia en `diagnostico_400.md` FASE 2.
- **Estado:** sin duplicar; vincular.

## REC-106 — Rate limit por IP compartida / proxy

- **Causa:** los visitantes compartían la IP de nginx y el gateway publicado
  podía falsificar `X-Forwarded-For`.
- **Correcciones:** `f82f420` (IP real sólo desde `RED_PROXY_CONFIABLE`) y
  `7b8750f` (excluye la primera IP usable de cada red confiable).
- **Pruebas:** 30 respuestas 422 y 429 en la 31.ª, tanto desde el puerto
  publicado como desde nginx; 2 pruebas nuevas.
- **Evidencia:** `diagnostico_400.md` verificación 4. **Estado:** corregido y
  verificado.

## REC-140 — Evidencia y capturas

- **Commits:** `9616280`, `17ffe8a`, `aa20fb8`, `17ce4e5`.
- Fase 1: 12 capturas sanitizadas en
  `docs/evidencia/estado_pagina_2026-11-20/` (~5,1 MB, sin personas ni datos
  personales), `README.md` con tabla caso/rama/esperado/real/captura/OK-FALLA
  y `resultados_navegador.json` (11 OK / 1 FALLA).
- REC-162: capturas `antes_desafio_ronda1/2.png` y
  `despues_desafio_ronda1/2/3.png` más las de puntaje, con
  `despues_resultados_desafio.json`.
- Además: `umbrales_por_clase.md`, `evaluacion_umbrales_test.*`,
  `docker_umbrales.txt`, `generalizacion.md`, `medicion_generalizacion.*` y
  `exp_geometria.*`.
- **Adjuntos:** todas las capturas indicadas. **Estado:** evidencia
  disponible; no marcar Hecho sin adjuntar.

## REC-161 — Plan de pruebas

- Se añade la evidencia visual de la Fase 1: **11 OK / 1 FALLA**. La falla era
  el Desafío con `1-2-3, 1-2-3, 1-2-3`, ahora corregida y documentada en
  `REC-162` (propuesto) con capturas antes/después.
- **Evidencia:** `docs/evidencia/estado_pagina_2026-11-20/README.md` y
  `resultados_navegador.json`. **Estado:** actualizado.

---

## Tabla de equivalencias (sólo se actualiza esta tabla)

Cuando reciba las claves reales que Jira asigne a los tickets nuevos, se
modificará **únicamente** la columna “Clave real Jira”:

| Clave propuesta | Clave real Jira | Estado |
|---|---|---|
| REC-162 | _pendiente_ | Corregido y verificado; adjuntar capturas |
| REC-163 | _pendiente_ | Corregido, por cerrar |
| REC-164 | _pendiente_ | Implementado, por cerrar |
| REC-165 | _pendiente_ | Corregido, por cerrar |
| REC-166 | _pendiente_ | Plantilla lista |
| REC-167 | _pendiente_ | En curso (épico REC-103) |
| REC-168 | _pendiente_ | Por verificar |
| REC-169 | _pendiente_ | Versionado |
| REC-170 | _pendiente_ | Corregido y verificado en CI (`44669949452`) |
