# Estado de la página — 2026-11-20 (antes de subir nada)

Evidencia visual tomada con **Chrome headless nuevo y aislado** (Playwright
instalado en `AppData/Local/Temp/opencode/headless`, **sin agregar
dependencias al proyecto**), sin pestañas ni caché del usuario.

## Entornos aislados

| Rama | Proyecto Docker | Web | API | DB | Health |
|---|---|---:|---:|---:|---|
| `main` @ `62c73a2` | `ecolearn-main-aud` | 5174 | 8001 | 3308 | 3/3 healthy, `/health` 200 |
| `feature/umbrales-por-clase` @ `62c73a2` | `ecolearn-feat-aud` | 5175 | 8002 | 3309 | 3/3 healthy, `/health` 200 |

El stack del usuario (`ecolearn-*`, 5173/8000/3307) quedó intacto.
Detalle: `compose_ps_main.txt`, `health_main.txt`, `compose_ps_feature.txt`,
`health_feature.txt`.

## Resultado por caso

| Caso | Rama | Resultado esperado | Resultado real | Captura | OK / FALLA |
|---|---|---|---|---|---|
| a) Menú principal | `main` | Menú con 5 pestañas | Menú Principal, Escáner IA, Puntos Limpios RM, Eco-Simulador RM y Desafío Verde RM visibles | `main_a_menu.png` | **OK** |
| a) Menú principal | `feature` | Menú con 5 pestañas | Ídem, sin cambios | `feature_a_menu.png` | **OK** |
| b) Escáner, lata nítida | `main` | Detección y resultado | "Materiales Identificados" presente | `main_b_lata_nitida.png` | **OK** |
| b) Escáner, lata nítida | `feature` | Detección y resultado | "Materiales Identificados" presente | `feature_b_lata_nitida.png` | **OK** |
| c) Foto sin objetos | `main` | Mensaje claro, sin "revisa tu conexión" | "No detecté residuos; acércate, mejora la luz o cambia el ángulo." | `main_c_sin_objetos.png` | **OK** |
| c) Foto sin objetos | `feature` | Mensaje claro, sin "revisa tu conexión" | Ídem | `feature_c_sin_objetos.png` | **OK** |
| d) Baja nitidez con detección | `main` | Detección + aviso de baja nitidez | Detectado y "La foto tiene poca definición; revisa el resultado." (laplaciano ≈30 < umbral 50) | `main_d_baja_nitidez.png` | **OK** |
| e) Confianza baja | `feature` | "Posible \<material\> (confianza baja)" sin sumar al conteo | `⚠️ Posible Cartón (confianza baja) · 35%`, sin "Materiales Identificados" | `feature_e_posible.png` | **OK** |
| f) Puntos Limpios RM | `main` | Listado de puntos | Listado con filtro de comuna y mapa | `main_f_puntos_limpios.png` | **OK** |
| f) Puntos Limpios RM | `feature` | Listado de puntos | Ídem | `feature_f_puntos_limpios.png` | **OK** |
| g) Desafío, 3 rondas | `main` | Preguntas distintas por ronda | **Se repiten las mismas 3 preguntas** en la ronda 1, 2 y 3 | `main_g_desafio_ronda1.png`, `main_g_desafio_ronda2.png` | **FALLA** |

### Detalle de la FALLA g

Secuencia registrada (9 respuestas, 3 por ronda), en `resultados_navegador.json`:

| Ronda | Pregunta 1 | Pregunta 2 | Pregunta 3 |
|---|---|---|---|
| 1 | ¿Qué material se debe enjuagar y aplastar antes de reciclar? | ¿Dónde se entregan las tapitas plásticas en este proyecto? | ¿Cuántos materiales detecta el Eco-Scanner? |
| 2 | ¿Qué material se debe enjuagar y aplastar antes de reciclar? | ¿Dónde se entregan las tapitas plásticas en este proyecto? | ¿Cuántos materiales detecta el Eco-Scanner? |
| 3 | ¿Qué material se debe enjuagar y aplastar antes de reciclar? | ¿Dónde se entregan las tapitas plásticas en este proyecto? | ¿Cuántos materiales detecta el Eco-Scanner? |

Causa aparente en `src/App.jsx`: `TRIVIA_VERDE` tiene **3 preguntas** y
`siguienteTrivia()` avanza con `(i + 1) % TRIVIA_VERDE.length`, por lo que tras
la tercera pregunta vuelve a la primera. No hay baraje ni reposición del banco
de preguntas, así que la secuencia de 9 queda 1-2-3, 1-2-3, 1-2-3. Se convierte
en ticket **Bug** en la Fase 2.

## Notas de honestidad y sanitización

- Primera corrida descartada: el script truncaba el texto a 400 caracteres
  **antes** de evaluar los booleanos, lo que generaba falsos negativos en b/c/d.
  Se corrigió (`completo()` para evaluar, `slice()` sólo para mostrar) y se
  repitió. La tabla usa la segunda corrida.
- Sin errores de consola en ninguno de los dos stacks (`consola: []`).
- Las fotos de prueba son imágenes de residuos del split de test y una imagen
  sintética de ruido; **sin personas ni datos personales**. Las capturas muestran
  sólo la interfaz y esos residuos. No se versiona ninguna foto original.
- Peso total de la carpeta: **~5,1 MB** en 12 PNG (el más grande, el mapa de
  Puntos Limpios, ~1,1 MB).
