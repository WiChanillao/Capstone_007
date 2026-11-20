# Plan de entrenamiento — generalización EcoLearn (NO EJECUTADO)

> Estado: propuesta. **No se reentrenó nada.** `best.pt` y `mAP@50 = 0,562`
> permanecen intactos. Los cuatro escenarios de la matriz son los que debe
> ejecutar el notebook `experimentos_yolo.ipynb` cuando se decida entrenar.
> Evidencia de los datos: `Fase 3/docs/evidencia/auditoria_dataset.md`.

## 1. Reglas obligatorias

1. **3 semillas por configuración** (0/1/2) y reportar **media ± desviación**
   de mAP@50, recall por clase y latencia.
2. Seleccionar siempre por **valid**; **test se evalúa una sola vez**, al
   final, con el modelo elegido por valid.
3. Descartar mejoras menores a la desviación entre semillas.
4. **Latencia < 100 ms** por imagen en CPU de referencia; si un modelo gana
   mAP pero rompe este límite, se descarta.
5. Eliminar fugas antes de reasignar splits: agrupar por ráfaga/número de
   captura y por hash perceptual; todos los vecinos de una escena quedan en
   el mismo split.
6. La clave de Roboflow se lee de **Colab Secrets** (`userdata.get`) o de una
   variable de entorno. **Nunca** escribirla en el notebook ni en reportes.
7. No subir dataset, fotos nuevas ni pesos al repositorio.

## 2. Matriz de experimentos

| # | Experimento | Datos / variable | Hipótesis que prueba | Métrica de decisión |
|---|---|---|---|---|
| **E0** | **Baseline v1** | Dataset v1 tal cual: 860 train (215 originales ×4), 61 valid, 31 test; Stretch 640×640; augmentations de Roboflow activas | Reproducir las condiciones con que se entrenó `best.pt` y medir la varianza real entre semillas | mAP@50 valid, media ± σ |
| **E1** | **train_nitido** | 215 train (sólo la copia de mayor Laplaciano por original); valid/test intactos | El desenfoque y el cutout del 60 % de las copias de train perjudican la generalización | mAP@50 valid + brecha train−valid |
| **E2** | **v2 sin augmentations** | Export propio sin Flip/Grayscale/Brillo/Cutout/Motion Blur de Roboflow; **Resize Fit con bordes negros**, no Stretch | El Stretch deforma los objetos y las augmentationes offline son redundantes con las de Ultralytics | mAP@50 valid + recall de Plástico/Aluminio |
| **E3** | **split por escenas** | 307 originales (copia más nítida de cada uno), reparto 215/61/31 por ventanas de ráfaga de 10 s, sin fuga | La fuga de escenas infla valid y explica parte de la caída en test | mAP@50 valid y test (una vez), brecha valid−test |

**Orden:** E0 → E1 → E2 → E3. E0 primero porque sin varianza no se puede
atribuir una mejora a los datos. E3 al final porque cambia el significado de
valid y test: sus cifras **no son comparables directamente** con E0–E2.

Hiperparámetros base comunes a los cuatro: YOLO11n desde `yolo11n.pt`,
`epochs=50`, `batch=16`, `patience=15`, `imgsz=640`, aumentos por defecto de
Ultralytics (`fliplr=0.5`, HSV, etc.), `seed` fijado por semilla.
**No aumentar épocas**: ya se midió 0,527 en test, peor que el 0,562 oficial.

### Extensiones opcionales (sólo después de E0–E3)

| # | Variable | Objetivo |
|---|---|---|
| E4 | `imgsz=800` | Recuperar plásticos pequeños/transparentes, con coste de latencia |
| E5 | YOLO11s vs YOLO11n | Comprobar si la nano se queda corta, respetando <100 ms |

## 3. Datos nuevos a capturar

| Clase | Fotos nuevas sugeridas | Tipo de escena | Prioridad |
|---|---:|---|---|
| Aluminio | 60–80 | Latas aisladas, fondo neutro, reflejos fuertes y suaves, 3 celulares | Alta |
| Cartón | 40–60 | Cajas enteras y aplastadas, cerca/lejos, luz natural/artificial | Media |
| Plástico | 100–150 | Botellas PET transparentes/opacas, arrugadas, con etiqueta y sin ella, fondo claro y oscuro | Alta |

Reparto por foto: **1–3 objetos por imagen**, al menos 20 fondos distintos por
clase, 2 condiciones de luz y 3 dispositivos. Evitar ráfagas mezcladas entre
splits. Estas fotos nuevas son un **evaluador independiente adicional**, no una
configuración de la matriz.

## 4. Augmentos: qué cambiar y por qué

El dataset v1 aplicó offline: Auto-Orient, Resize Stretch 640×640, 4 salidas
por ejemplo, Flip horizontal y vertical, Grayscale 15 %, brillo ±15 %, Cutout
de 3 cajas del 10 % y Motion Blur de 100 px (ángulo 0°). El README del ZIP
declaraba sólo flips y brillo.

- **E0** conserva todo eso tal cual, para reproducir el punto de partida.
- **E2** elimina *todas* esas augmentationes de Roboflow y usa Resize Fit con
  bordes negros. Ultralytics ya aplica por defecto `fliplr`, HSV, escala y
  mosaico **al vuelo**, así que las 4 copias offline son en parte redundantes.
- Mantener en E2 los aumentos al vuelo de Ultralytics; no desactivarlos.
- Blur/gaussian noise **sólo en pequeña proporción**: el backend rechaza fotos
  borrosas sin detecciones, así que no conviene entrenar demasiado con blur.

## 5. Salida esperada

Tabla comparativa por experimento y semilla con: mAP@50 valid, mAP@50 test
(una sola vez), P/R/F1 por clase, matriz de confusión, latencia media y p95,
y decisión `aceptar / descartar por debajo de la varianza`.

Ningún experimento de este plan se ejecutó en esta sesión.
