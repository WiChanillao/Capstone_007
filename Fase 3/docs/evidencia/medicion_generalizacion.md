# Medición de `best.pt` con el dataset v1 (generada por `medicion.py`)

- Pesos: `best.pt` (sin modificar).
- Dataset: `AppData/Local/Temp/opencode/dataset_capstone_v1i` (fuera del repo).
- Subsets: train_nitido=259, train_movido=515, valid=61, test=31.
- conf evaluados: 0.5, 0.35, 0.25; además 0.001 en test para comparar con el oficial.
- Las etiquetas `.txt` son **polígonos de segmentación**; `val()` de
  Ultralytics usa la caja envolvente. Para P/R/F1 propios se
  reconstruye esa misma envolvente desde el polígono.

## 1. Métricas globales

| conf | subset | P | R | F1 | mAP@50 | mAP@50-95 |
|---:|---|---:|---:|---:|---:|---:|
| 0.5 | test | 0.842 | 0.455 | 0.589 | 0.429 | 0.277 |
| 0.5 | valid | 0.728 | 0.474 | 0.564 | 0.445 | 0.309 |
| 0.5 | train_nitido | 0.974 | 0.898 | 0.934 | 0.896 | 0.746 |
| 0.5 | train_movido | 0.951 | 0.842 | 0.892 | 0.840 | 0.688 |
| 0.35 | test | 0.826 | 0.511 | 0.627 | 0.477 | 0.299 |
| 0.35 | valid | 0.606 | 0.532 | 0.565 | 0.480 | 0.329 |
| 0.35 | train_nitido | 0.961 | 0.903 | 0.931 | 0.914 | 0.757 |
| 0.35 | train_movido | 0.959 | 0.834 | 0.892 | 0.871 | 0.706 |
| 0.25 | test | 0.820 | 0.507 | 0.624 | 0.486 | 0.301 |
| 0.25 | valid | 0.555 | 0.561 | 0.557 | 0.493 | 0.332 |
| 0.25 | train_nitido | 0.970 | 0.893 | 0.930 | 0.932 | 0.765 |
| 0.25 | train_movido | 0.959 | 0.834 | 0.892 | 0.891 | 0.719 |
| 0.001 | test | 0.814 | 0.506 | 0.620 | 0.564 | 0.330 |

### Comparación con el mAP@50 oficial 0,562

- `val()` en test con conf por defecto (0.001): **0.564**.
- El 0,562 oficial procede de `val()` con ajustes por defecto; el
  `conf` no es el umbral de decisión del backend (0,50). Al subir
  `conf` a 0,50/0,35/0,25 el mAP@50 calculado baja porque se descartan
  detecciones de baja confianza antes de calcular la curva P-R. Eso
  **no contradice** la métrica oficial: es otro punto de operación.
- train_nitido y train_movido no son el conjunto de validación: son
  particiones artificiales de train y sólo sirven para diagnosticar.

## 2. Métricas por clase

| conf | subset | clase | P | R | F1 | AP50 |
|---:|---|---|---:|---:|---:|---:|
| 0.5 | test | Aluminio | 0.800 | 0.500 | 0.615 | 0.471 |
| 0.5 | test | Carton | 0.929 | 0.448 | 0.605 | 0.445 |
| 0.5 | test | Plastico | 0.798 | 0.417 | 0.547 | 0.371 |
| 0.5 | valid | Aluminio | 0.857 | 0.375 | 0.522 | 0.366 |
| 0.5 | valid | Carton | 0.791 | 0.667 | 0.723 | 0.658 |
| 0.5 | valid | Plastico | 0.537 | 0.381 | 0.446 | 0.310 |
| 0.5 | train_nitido | Aluminio | 0.986 | 0.921 | 0.952 | 0.924 |
| 0.5 | train_nitido | Carton | 0.994 | 0.928 | 0.960 | 0.925 |
| 0.5 | train_nitido | Plastico | 0.941 | 0.845 | 0.890 | 0.838 |
| 0.5 | train_movido | Aluminio | 0.960 | 0.806 | 0.876 | 0.804 |
| 0.5 | train_movido | Carton | 0.965 | 0.892 | 0.927 | 0.894 |
| 0.5 | train_movido | Plastico | 0.927 | 0.827 | 0.874 | 0.822 |
| 0.35 | test | Aluminio | 0.833 | 0.625 | 0.714 | 0.583 |
| 0.35 | test | Carton | 0.867 | 0.448 | 0.591 | 0.445 |
| 0.35 | test | Plastico | 0.778 | 0.458 | 0.577 | 0.402 |
| 0.35 | valid | Aluminio | 0.583 | 0.438 | 0.500 | 0.405 |
| 0.35 | valid | Carton | 0.735 | 0.706 | 0.720 | 0.688 |
| 0.35 | valid | Plastico | 0.500 | 0.452 | 0.475 | 0.346 |
| 0.35 | train_nitido | Aluminio | 0.972 | 0.921 | 0.946 | 0.924 |
| 0.35 | train_nitido | Carton | 0.981 | 0.939 | 0.960 | 0.945 |
| 0.35 | train_nitido | Plastico | 0.929 | 0.850 | 0.888 | 0.874 |
| 0.35 | train_movido | Aluminio | 0.966 | 0.796 | 0.873 | 0.833 |
| 0.35 | train_movido | Carton | 0.977 | 0.880 | 0.926 | 0.922 |
| 0.35 | train_movido | Plastico | 0.934 | 0.827 | 0.877 | 0.858 |
| 0.25 | test | Aluminio | 0.833 | 0.625 | 0.714 | 0.583 |
| 0.25 | test | Carton | 0.846 | 0.448 | 0.586 | 0.445 |
| 0.25 | test | Plastico | 0.782 | 0.449 | 0.571 | 0.430 |
| 0.25 | valid | Aluminio | 0.533 | 0.500 | 0.516 | 0.437 |
| 0.25 | valid | Carton | 0.667 | 0.706 | 0.686 | 0.688 |
| 0.25 | valid | Plastico | 0.465 | 0.476 | 0.471 | 0.355 |
| 0.25 | train_nitido | Aluminio | 0.978 | 0.921 | 0.949 | 0.942 |
| 0.25 | train_nitido | Carton | 0.994 | 0.928 | 0.960 | 0.954 |
| 0.25 | train_nitido | Plastico | 0.940 | 0.830 | 0.882 | 0.899 |
| 0.25 | train_movido | Aluminio | 0.966 | 0.796 | 0.873 | 0.860 |
| 0.25 | train_movido | Carton | 0.977 | 0.880 | 0.926 | 0.931 |
| 0.25 | train_movido | Plastico | 0.934 | 0.827 | 0.877 | 0.883 |
| 0.001 | test | Aluminio | 0.811 | 0.625 | 0.706 | 0.604 |
| 0.001 | test | Carton | 0.851 | 0.448 | 0.587 | 0.583 |
| 0.001 | test | Plastico | 0.780 | 0.444 | 0.566 | 0.505 |

## 2b. IC 95 % bootstrap del AP50 por clase (conf=0,50)

Remuestreo de **imágenes con reposición**, 1000 réplicas, semilla 42.
AP50 con 101 puntos e interpolación COCO sobre el caché de
detecciones (piso de conf=0,01; no afecta al punto de operación 0,50).
El AP50 puntual puede diferir del `ap50_clase` de `val()` por el
criterio de emparejamiento; compárense sólo los valores de esta tabla.

| subset | clase | AP50 | IC 95 % | instancias | lectura |
|---|---|---:|---|---:|---|
| valid | Aluminio | 0.376 | [0.158 ; 0.614] | 16 |  |
| valid | Carton | 0.607 | [0.472 ; 0.766] | 51 |  |
| valid | Plastico | 0.265 | [0.122 ; 0.460] | 42 |  |
| test | Aluminio | 0.505 | [0.128 ; 0.832] | 8 | NO CONCLUYENTE (sólo 8 instancias) |
| test | Carton | 0.391 | [0.232 ; 0.618] | 29 |  |
| test | Plastico | 0.281 | [0.089 ; 0.469] | 24 |  |

Aluminio en test tiene 8 instancias: una sola detección mueve
el resultado 12,5 puntos. Su intervalo es amplio y **no permite
elegir umbral ni afirmar superioridad** frente a las otras clases.


## 3. Matrices de confusión (filas=real, columnas=predicho)

Calculadas del caché de detecciones con IoU>0,5 y emparejamiento
por confianza; última fila/columna = fondo.

- conf=0.5, test:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 4 | 0 | 0 | 4 |
| Carton | 0 | 12 | 0 | 17 |
| Plastico | 0 | 0 | 7 | 17 |
| fondo | 1 | 2 | 2 | 0 |

- conf=0.5, valid:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 6 | 0 | 2 | 8 |
| Carton | 0 | 32 | 0 | 19 |
| Plastico | 1 | 0 | 14 | 27 |
| fondo | 0 | 4 | 10 | 0 |

- conf=0.5, train_nitido:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 70 | 0 | 0 | 6 |
| Carton | 0 | 164 | 0 | 17 |
| Plastico | 0 | 0 | 169 | 37 |
| fondo | 2 | 2 | 18 | 0 |

- conf=0.5, train_movido:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 160 | 0 | 0 | 46 |
| Carton | 0 | 297 | 1 | 45 |
| Plastico | 0 | 0 | 222 | 55 |
| fondo | 7 | 9 | 15 | 0 |

- conf=0.35, test:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 5 | 0 | 0 | 3 |
| Carton | 0 | 12 | 0 | 17 |
| Plastico | 0 | 1 | 10 | 13 |
| fondo | 1 | 4 | 4 | 0 |

- conf=0.35, valid:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 8 | 0 | 2 | 6 |
| Carton | 0 | 33 | 0 | 18 |
| Plastico | 1 | 0 | 18 | 23 |
| fondo | 2 | 8 | 15 | 0 |

- conf=0.35, train_nitido:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 71 | 0 | 0 | 5 |
| Carton | 0 | 166 | 0 | 15 |
| Plastico | 0 | 0 | 179 | 27 |
| fondo | 3 | 4 | 39 | 0 |

- conf=0.35, train_movido:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 169 | 0 | 1 | 36 |
| Carton | 0 | 307 | 2 | 34 |
| Plastico | 0 | 0 | 234 | 43 |
| fondo | 12 | 23 | 28 | 0 |

- conf=0.25, test:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 5 | 0 | 0 | 3 |
| Carton | 1 | 12 | 0 | 16 |
| Plastico | 0 | 1 | 11 | 12 |
| fondo | 1 | 8 | 6 | 0 |

- conf=0.25, valid:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 8 | 1 | 2 | 5 |
| Carton | 0 | 34 | 0 | 17 |
| Plastico | 1 | 0 | 21 | 20 |
| fondo | 2 | 13 | 21 | 0 |

- conf=0.25, train_nitido:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 72 | 0 | 0 | 4 |
| Carton | 0 | 167 | 0 | 14 |
| Plastico | 0 | 0 | 185 | 21 |
| fondo | 4 | 8 | 67 | 0 |

- conf=0.25, train_movido:

| | Aluminio | Carton | Plastico | fondo |
|---|---:|---:|---:|---:|
| Aluminio | 171 | 0 | 1 | 34 |
| Carton | 0 | 310 | 2 | 31 |
| Plastico | 0 | 0 | 246 | 31 |
| fondo | 18 | 38 | 59 | 0 |

## 4. Curva F1 vs confianza en valid

F1 global (TP/FP/FN acumulados en todas las imágenes), no media
por imagen.

| conf | Aluminio | Carton | Plastico |
|---:|---:|---:|---:|
| 0.05 | 0.512 | 0.613 | 0.359 |
| 0.10 | 0.571 | 0.643 | 0.459 |
| 0.15 | 0.645 | 0.648 | 0.495 |
| 0.20 | 0.643 | 0.673 | 0.500 |
| 0.25 | 0.667 | 0.687 | 0.488 |
| 0.30 | 0.667 | 0.701 | 0.494 |
| 0.35 | 0.667 | 0.717 | 0.468 |
| 0.40 | 0.615 | 0.733 | 0.444 |
| 0.45 | 0.640 | 0.750 | 0.457 |
| 0.50 | 0.522 | 0.736 | 0.412 |
| 0.55 | 0.522 | 0.736 | 0.424 |
| 0.60 | 0.545 | 0.706 | 0.444 |
| 0.65 | 0.545 | 0.714 | 0.433 |
| 0.70 | 0.545 | 0.683 | 0.386 |
| 0.75 | 0.400 | 0.658 | 0.393 |
| 0.80 | 0.316 | 0.575 | 0.333 |
| 0.85 | 0.118 | 0.455 | 0.167 |
| 0.90 | 0.118 | 0.241 | 0.047 |
| 0.95 | 0.000 | 0.000 | 0.000 |

Umbrales propuestos por clase (máximo F1 en valid):

- Aluminio: **0.25** (F1=0.667).
- Carton: **0.45** (F1=0.750).
- Plastico: **0.20** (F1=0.500).

### Efecto en test (sólo reporte; NO aplicado al backend)

| configuración | clase | TP | FP | FN | P | R | F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| global_0.5 | Aluminio | 4 | 1 | 4 | 0.800 | 0.500 | 0.615 |
| global_0.5 | Carton | 12 | 2 | 17 | 0.857 | 0.414 | 0.558 |
| global_0.5 | Plastico | 7 | 2 | 17 | 0.778 | 0.292 | 0.424 |
| por_clase | Aluminio | 5 | 2 | 3 | 0.714 | 0.625 | 0.667 |
| por_clase | Carton | 12 | 4 | 17 | 0.750 | 0.414 | 0.533 |
| por_clase | Plastico | 11 | 9 | 13 | 0.550 | 0.458 | 0.500 |

**Inestabilidad de Aluminio en test:** sólo 8 instancias.
Recall 0.500, IC 95 % Wilson [0.215, 0.785];
precision 0.800, IC 95 % [0.376, 0.964].
Cualquier diferencia de una sola instancia cambia el resultado; no se
debe elegir umbral definitivo con este tamaño de muestra.

## 5. 20 falsos negativos más confiados (test, conf=0,5)

| archivo | real | conf | causa | Laplaciano |
|---|---|---:|---|---:|
| `test/images/IMG_8909_HEIC.rf.28bf43a30ab5acfd839cbf52d995221d.jpg` | Carton | 0.88 | revisar: fondo / reflejo / transparencia / oclusión | 243.7 |
| `test/images/IMG_20260930_154429511_HDR_jpg.rf.c24f2e93123879d7a054b85a8f882694.jpg` | Carton | 0.85 | revisar: fondo / reflejo / transparencia / oclusión | 684.0 |
| `test/images/IMG_20260930_154429511_HDR_jpg.rf.c24f2e93123879d7a054b85a8f882694.jpg` | Carton | 0.85 | objeto pequeño | 684.0 |
| `test/images/IMG_20260930_154429511_HDR_jpg.rf.c24f2e93123879d7a054b85a8f882694.jpg` | Carton | 0.85 | revisar: fondo / reflejo / transparencia / oclusión | 684.0 |
| `test/images/IMG_20260930_154429511_HDR_jpg.rf.c24f2e93123879d7a054b85a8f882694.jpg` | Carton | 0.85 | revisar: fondo / reflejo / transparencia / oclusión | 684.0 |
| `test/images/IMG_8942_HEIC.rf.4c7ee920ddd7253851ca35603ffd69d6.jpg` | Plastico | 0.85 | revisar: fondo / reflejo / transparencia / oclusión | 4759.4 |
| `test/images/IMG_20260930_154454557_HDR_jpg.rf.da4d25f71eee0ebf0825b33204f0419c.jpg` | Carton | 0.81 | revisar: fondo / reflejo / transparencia / oclusión | 168.9 |
| `test/images/IMG_20260930_154432333_HDR_jpg.rf.9c04691ea7864d317c21313f9563cefe.jpg` | Carton | 0.79 | objeto pequeño | 366.5 |
| `test/images/IMG_20260930_154432333_HDR_jpg.rf.9c04691ea7864d317c21313f9563cefe.jpg` | Carton | 0.79 | revisar: fondo / reflejo / transparencia / oclusión | 366.5 |
| `test/images/IMG_8952_HEIC.rf.7d150a0ec021e11782c634e295680807.jpg` | Plastico | 0.75 | objeto pequeño | 1891.6 |
| `test/images/IMG_8952_HEIC.rf.7d150a0ec021e11782c634e295680807.jpg` | Plastico | 0.75 | revisar: fondo / reflejo / transparencia / oclusión | 1891.6 |
| `test/images/IMG_8952_HEIC.rf.7d150a0ec021e11782c634e295680807.jpg` | Plastico | 0.75 | objeto pequeño | 1891.6 |
| `test/images/IMG_8961_HEIC.rf.e0a4ae20b274fee9c830ddc7982d46f9.jpg` | Carton | 0.70 | revisar: fondo / reflejo / transparencia / oclusión | 1613.3 |
| `test/images/IMG_8961_HEIC.rf.e0a4ae20b274fee9c830ddc7982d46f9.jpg` | Carton | 0.70 | revisar: fondo / reflejo / transparencia / oclusión | 1613.3 |
| `test/images/IMG_8961_HEIC.rf.e0a4ae20b274fee9c830ddc7982d46f9.jpg` | Carton | 0.70 | revisar: fondo / reflejo / transparencia / oclusión | 1613.3 |
| `test/images/IMG_9020-1-_HEIC.rf.004bb3d68df25e5767c25d2817abc8ff.jpg` | Plastico | 0.69 | objeto pequeño | 1286.4 |
| `test/images/IMG_8996_HEIC.rf.41714c438c620a7254f591f9d4477e32.jpg` | Aluminio | 0.66 | revisar: fondo / reflejo / transparencia / oclusión | 430.8 |
| `test/images/IMG_8996_HEIC.rf.41714c438c620a7254f591f9d4477e32.jpg` | Carton | 0.66 | revisar: fondo / reflejo / transparencia / oclusión | 430.8 |
| `test/images/IMG_8996_HEIC.rf.41714c438c620a7254f591f9d4477e32.jpg` | Plastico | 0.66 | revisar: fondo / reflejo / transparencia / oclusión | 430.8 |
| `test/images/IMG_8996_HEIC.rf.41714c438c620a7254f591f9d4477e32.jpg` | Plastico | 0.66 | objeto pequeño | 430.8 |

## 6. 20 falsos positivos más confiados (test, conf=0,5)

| archivo | predicho | conf | causa | Laplaciano |
|---|---|---:|---|---:|
| `test/images/IMG_20260930_154454557_HDR_jpg.rf.da4d25f71eee0ebf0825b33204f0419c.jpg` | Carton | 0.81 | escena completa / tamaño | 168.9 |
| `test/images/IMG_20260930_154432333_HDR_jpg.rf.9c04691ea7864d317c21313f9563cefe.jpg` | Carton | 0.72 | revisar: fondo / reflejo / transparencia / oclusión | 366.5 |
| `test/images/IMG_8961_HEIC.rf.e0a4ae20b274fee9c830ddc7982d46f9.jpg` | Plastico | 0.70 | revisar: fondo / reflejo / transparencia / oclusión | 1613.3 |
| `test/images/IMG_8879_HEIC.rf.25586fc38e738359ac794e1de42f5637.jpg` | Aluminio | 0.58 | revisar: fondo / reflejo / transparencia / oclusión | 153.8 |
| `test/images/IMG_8888_HEIC.rf.a835c08c683c106ad0aa78ca3aa4ebdf.jpg` | Plastico | 0.51 | revisar: fondo / reflejo / transparencia / oclusión | 227.8 |

Las causas son **heurísticas automáticas**; requieren revisión visual.
