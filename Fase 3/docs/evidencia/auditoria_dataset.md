# Auditoría del dataset YOLOv11 v1 (generada por `auditoria_dataset.py`)

- Dataset: `AppData/Local/Temp/opencode/dataset_capstone_v1i` (fuera del repositorio).
- Imágenes totales: **952**.

## 1. Splits y originales

| Split | Imágenes | Originales | Copias por original |
|---|---:|---:|---|
| train | 860 | 215 | {4: 215} |
| valid | 61 | 61 | {1: 61} |
| test | 31 | 31 | {1: 31} |

- Originales únicos totales: **307**.
- Train: **215** originales tienen exactamente 4 copias.

## 2. Instancias por clase

| Split | Aluminio | Carton | Plastico |
|---|---:|---:|---:|
| train | 316 | 572 | 568 |
| valid | 16 | 51 | 42 |
| test | 8 | 29 | 24 |

## 3. Nitidez (varianza del Laplaciano, 640×640)

| Split | <50 (movido) | 50–100 | >100 (nítido) |
|---|---:|---:|---:|
| train | 515 | 86 | 259 |
| valid | 1 | 3 | 57 |
| test | 0 | 2 | 29 |

Patrón dentro de cada original de train (movidas<50, nítidas>100):

- 3 movida(s), 1 nítida(s): 97 originales
- 2 movida(s), 1 nítida(s): 34 originales
- 2 movida(s), 2 nítida(s): 33 originales
- 3 movida(s), 0 nítida(s): 16 originales
- 1 movida(s), 2 nítida(s): 11 originales
- 1 movida(s), 1 nítida(s): 5 originales
- 4 movida(s), 0 nítida(s): 5 originales
- 1 movida(s), 3 nítida(s): 4 originales

## 4. Augmentations reales detectadas vs README

| Split | Imágenes con bloque negro rectangular | Fracción negra media | Imágenes gris >50 % |
|---|---:|---:|---:|
| train | 199 | 0.0328 | 86 |
| valid | 1 | 0.0192 | 0 |
| test | 1 | 0.0178 | 0 |

El `README.roboflow.txt` del ZIP declara sólo *flips* y brillo ±15 %.
La configuración real de la versión 1 (comunicada por el usuario) es:
Auto-Orient, Resize Stretch 640×640, 4 salidas por ejemplo, Flip
horizontal y vertical, Grayscale 15 %, brillo ±15 %, Cutout de 3 cajas
del 10 % y Motion Blur de 100 px (ángulo 0°). Las cifras de arriba son
la comprobación empírica de ese desajuste: train está aumentado y
valid/test no.

## 5. Fuga de escena

- Originales compartidos entre splits: **0**.
- Valid con número `IMG_NNNN` vecino de train (±1): **38/61**.
- Test con número `IMG_NNNN` vecino de train (±1): **16/31**.
- Pares HDR valid/test ↔ train a ≤10 s: **52**.

Ejemplos:

- `valid:IMG_8840_HEIC ↔ train:IMG_8841_HEIC`
- `valid:IMG_8853_HEIC ↔ train:IMG_8854_HEIC`
- `valid:IMG_8859_HEIC ↔ train:IMG_8858_HEIC`
- `valid:IMG_8861_HEIC ↔ train:IMG_8860_HEIC`
- `valid:IMG_8862_HEIC ↔ train:IMG_8863_HEIC`
- `valid:IMG_8865_HEIC ↔ train:IMG_8864_HEIC`
- `valid:IMG_8869_HEIC ↔ train:IMG_8868_HEIC`
- `valid:IMG_8881_HEIC ↔ train:IMG_8880_HEIC`
- `valid:IMG_8885_HEIC ↔ train:IMG_8884_HEIC`
- `valid:IMG_8886_HEIC ↔ train:IMG_8887_HEIC`
- `valid:IMG_8893_HEIC ↔ train:IMG_8892_HEIC`
- `valid:IMG_8894_HEIC ↔ train:IMG_8895_HEIC`

Ejemplos de ráfaga temporal:

- `valid:IMG_20260930_094828610_HDR_jpg ↔ train:IMG_20260930_094819681_HDR_jpg (9.0s)`
- `valid:IMG_20260930_094828610_HDR_jpg ↔ train:IMG_20260930_094821560_HDR_jpg (7.0s)`
- `valid:IMG_20260930_094828610_HDR_jpg ↔ train:IMG_20260930_094826097_HDR_jpg (2.0s)`
- `valid:IMG_20260930_094828610_HDR_jpg ↔ train:IMG_20260930_094836928_HDR_jpg (8.0s)`
- `valid:IMG_20260930_154220098_HDR_jpg ↔ train:IMG_20260930_154215614_HDR_jpg (5.0s)`
- `valid:IMG_20260930_154220098_HDR_jpg ↔ train:IMG_20260930_154225236_HDR_jpg (5.0s)`
- `valid:IMG_20260930_154341078_HDR_jpg ↔ train:IMG_20260930_154332635_HDR_jpg (9.0s)`
- `valid:IMG_20260930_154341078_HDR_jpg ↔ train:IMG_20260930_154346282_HDR_jpg (5.0s)`
- `valid:IMG_20260930_154423279_HDR_jpg ↔ train:IMG_20260930_154417210_HDR_jpg (6.0s)`
- `valid:IMG_20260930_154423279_HDR_jpg ↔ train:IMG_20260930_154426887_HDR_jpg (3.0s)`
- `valid:IMG_20260930_154439475_HDR_jpg ↔ train:IMG_20260930_154434822_HDR_jpg (5.0s)`
- `valid:IMG_20260930_154620574_HDR_jpg ↔ train:IMG_20260930_154623978_HDR_jpg (3.0s)`

## 6. Preprocesamiento y duplicados

- Tamaños observados (muestra): {'640x640': 30} → Resize 640×640 Stretch.
- Umbral de hash: **distancia de Hamming ≤ 10 sobre 64 bits de pHash O ≤ 12 sobre 64 bits de dHash** (se cumple cualquiera de los dos). Hashes calculados en
  escala de grises sobre las imágenes ya exportadas del dataset.
- Pares que cumplen el umbral: **339**. Desglose:

| Tipo de par | Pares | ¿Es fuga? |
|---|---:|---|
| (i) train–train (copias aumentadas) | 330 | No |
| (ii) train–valid | 4 | **Sí** |
| (iii) train–test | 4 | **Sí** |
| (iv) valid–test | 1 | **Sí** |
| valid–valid | 0 | No (evaluación) |
| test–test | 0 | No (evaluación) |

- De los pares train–train, **324/330** son copias del **mismo original** (mismo nombre base antes del sufijo `.rf.<hash>`): son el resultado
  de las 4 salidas por ejemplo de Roboflow, no fuga entre splits.
- **Fuga real entre splits: 9 pares** ((ii)+(iii)+(iv)).

Ejemplos por tipo:

- `train-train`: `train:IMG_20260930_094819681_HDR_jpg ↔ train:IMG_20260930_094819681_HDR_jpg (pHash=8, dHash=5)`
- `train-valid`: `train:IMG_8842_HEIC ↔ valid:IMG_8840_HEIC (pHash=13, dHash=10)`
- `train-test`: `train:IMG_8842_HEIC ↔ test:IMG_8843_HEIC (pHash=6, dHash=3)`
- `valid-test`: `valid:IMG_8840_HEIC ↔ test:IMG_8843_HEIC (pHash=15, dHash=7)`

- El Stretch del entrenamiento no coincide con el letterbox usado en
  inferencia; además Ultralytics ya aplica aumentos al vuelo, por lo que
  las 4 copias offline son en parte redundantes.
