# Desafío Verde — antes / después (REC-162)

Rama `fix/desafio-preguntas`, creada desde `main @ 62c73a2646e7d7b1cd4e420f88ba1706aa841d25`.
Commit del código: `88e72b1bb6b0e3a39ab3440774f4276a07c44094`.

## 1. Diagnóstico (sin endpoint ni tabla)

Las preguntas **no vienen de la API ni de una tabla**: estaban hardcodeadas en
el frontend, en `Fase 3/ecoscan-frontend/src/App.jsx`:

| Elemento | Ubicación antes | Detalle |
|---|---|---|
| Banco | `App.jsx:391-410` | `TRIVIA_VERDE` con **3** preguntas |
| Elección de la siguiente | `App.jsx:727-730` | `setTriviaIndice((i) => (i + 1) % TRIVIA_VERDE.length)` |
| Render | `App.jsx:1983-2029` | `TRIVIA_VERDE[triviaIndice]` para pregunta, opciones y explicación |

Al ser sólo 3 preguntas y avanzar con módulo 3, la secuencia de 9 respuestas
quedó `1-2-3, 1-2-3, 1-2-3`. No había baraje, reposición ni noción de ronda.
El desafío semanal automático (`App.jsx:710-716`, `desafiosAuto`) **no se tocó**;
la trivia es información educativa y no modifica estadísticas ni desafíos.

## 2. Corrección

- Nuevo módulo `src/trivia.js`: **25 preguntas**, cada una con respuesta
  correcta, explicación breve y campo `fuente` con las líneas de `App.jsx` que
  respaldan el dato.
- Rondas de **5 preguntas distintas**; baraje Fisher–Yates con PRNG
  `mulberry32` (semilla reproducible en tests).
- Entre rondas se priorizan las **no vistas**; el ciclo se reinicia sólo al
  agotar las 25.
- Al terminar la ronda se muestra **puntaje** y el botón **“Nueva ronda”**.
- `App.jsx` pasó a usar estado inmutable con `crearEstadoTrivia`,
  `responderEnTrivia`, `avanzarEnTrivia` e `iniciarRonda`.

### Honestidad de contenidos

No se inventaron cifras ni datos legales. Las afirmaciones salen del propio
código: guía de materiales (`App.jsx:64-177`), galería (`205-245`), Puntos
Limpios RM (`247-319`) y el banco original (`391-410`). Los colores de
contenedor son los de `CONTENEDORES_POR_DEFECTO` (`App.jsx:58-62`) y la app
misma enlaza `santiagorecicla.mma.gob.cl`; en las explicaciones se aclara que
el color **puede variar por comuna** y conviene revisar la señalización local.
No se añadió ninguna fuente externa nueva.

## 3. Evidencia visual (mismo navegador headless)

Chrome headless aislado con Playwright instalado en
`AppData/Local/Temp/opencode/headless`, sin pestañas ni caché del usuario,
sin datos personales.

| Momento | Ronda | Captura | Resultado |
|---|---|---|---|
| Antes (`main @ 62c73a2`) | 1 | `antes_desafio_ronda1.png` | Preguntas 1-2-3 |
| Antes (`main @ 62c73a2`) | 2 | `antes_desafio_ronda2.png` | Vuelve a 1-2-3 (FALLA) |
| Después (`fix/desafio-preguntas @ 88e72b1`) | 1 | `despues_desafio_ronda1.png`, `despues_desafio_ronda1_puntaje.png` | 5 distintas, puntaje 2/5 |
| Después | 2 | `despues_desafio_ronda2.png`, `despues_desafio_ronda2_puntaje.png` | 5 distintas, puntaje 2/5 |
| Después | 3 | `despues_desafio_ronda3.png`, `despues_desafio_ronda3_puntaje.png` | 5 distintas, puntaje 1/5 |

`sinRepeticionDentroDeRonda=true`, `rondasDistintas=true`, `consola=[]`.
Datos completos: `antes_resultados_navegador.json` (caso `g`) y
`despues_resultados_desafio.json`.

### Preguntas registradas por ronda (después)

| Ronda | Preguntas |
|---|---|
| 1 | ¿Dónde se muestran los horarios de los puntos limpios en la app? · ¿Qué contagio evita la guía al limpiar cartón y papel? · ¿Qué hacer con la tapa y la etiqueta de una botella si son de otro material? · ¿En qué comuna está el Punto Limpio Ciudad Satélite? · ¿Qué se debe retirar del cartón antes de reciclarlo? |
| 2 | ¿Cuántos materiales detecta el Eco-Scanner? · Según la configuración de esta app, ¿qué contenedor corresponde al plástico? · ¿Qué secuencia se indica para una lata de aluminio? · ¿Qué reutilización de latas aparece en la app? · ¿Qué reutilización de cartón sugiere la app para huertos? |
| 3 | ¿Cómo se llama el punto limpio de Santiago Centro en la app? · Según la configuración de esta app, ¿qué contenedor corresponde al cartón? · Según los enlaces de la app, ¿qué empresa es planta de reciclaje y transformación de plásticos? · ¿Qué organización ofrece talleres de suprarreciclaje para latas en los enlaces? · ¿Por qué se recomienda aplastar la botella antes de depositarla? |

## 4. Entorno aislado y pruebas

| Proyecto Docker | Web | API | DB | Health |
|---|---:|---:|---:|---|
| `ecolearn-desafio-aud` | 5176 | 8003 | 3310 | **3/3 healthy**, `/health` y `/` → 200 |

Detalle en `compose_ps_desafio.txt` y `health_desafio.txt`. El stack del
usuario (`ecolearn-*`, 5173/8000/3307) y los stacks de auditoría anteriores
quedaron intactos. Se usó `down -v` sólo sobre `ecolearn-desafio-aud`.

- `npm run build` + `npm run test:unit`: **24 passed** (14 base + 3 SW + 6 de
  trivia + 1 de integración). Salida en `vitest_desafio.txt`.
- Backend `pytest -q --cov=main --cov=rutas_db`: **36 passed**, cobertura 74 %.
- 0 errores de consola en el navegador.

No se abrió PR. El `ci.yml` de esta rama (heredado de `main`) no incluye el
patrón `fix/**`, así que este push no genera run automático; la verificación
local queda registrada arriba. El patrón `fix/**` sí se añadió en la rama
`fix/ci-orden-pasos` (REC-170), pendiente de integrar cuando desees.
