# Datasets experimentales preparados (generado por `preparar_datasets.py`)

- Origen: `AppData/Local/Temp/opencode/dataset_capstone_v1i` (sin modificar).
- Salida: `AppData/Local/Temp/opencode/datasets_experimentales` (**fuera del repositorio**).
- Semilla: **42**. No se entrenó nada.

## a) train_nitido

Por cada uno de los 215 originales de train se conservó la copia con
mayor varianza del Laplaciano. Valid y test se copiaron íntegros.

| Split | Imágenes | Aluminio | Carton | Plastico |
|---|---:|---:|---:|---:|
| train | 215 | 79 | 143 | 142 |
| valid | 61 | 16 | 51 | 42 |
| test | 31 | 8 | 29 | 24 |

- Laplaciano de las elegidas: mín 10.9, medio 832.2.

## b) split_por_escenas

- 307 originales (la copia más nítida de cada uno).
- Grupos de ráfaga: **88** (ventanas fijas de 10 s / 10 números).
- Tamaños de grupo: {1: 30, 2: 28, 6: 1, 10: 16, 3: 10, 7: 1, 9: 2}.
- Objetivos 70/20/10: {'train': 215, 'valid': 61, 'test': 31}; asignado: {'train': 215, 'valid': 61, 'test': 31}.
- Grupos repartidos en varios splits: **0**.

| Split | Imágenes | Aluminio | Carton | Plastico |
|---|---:|---:|---:|---:|
| train | 215 | 79 | 169 | 129 |
| valid | 61 | 20 | 29 | 49 |
| test | 31 | 4 | 25 | 30 |

Cada `data.yaml` apunta a `train/images`, `valid/images` y
`test/images` dentro de su propio directorio temporal.
