# Experimento Stretch vs letterbox (sin reentrenar)

- Pesos: `best.pt` (sin modificar). Conf usada: **0.5**.
- Originales: `Desktop/Nueva carpeta (2)/Capstone-20261005T193438Z-1-001/Capstone/fotos entrenamiento` (fuera del repo).
- Auto-orient EXIF aplicado con `ImageOps.exif_transpose`.
- Emparejamiento por nombre base: se quitó `.rf.<hash>.<ext>` y los
  sufijos `_jpg` / `_HEIC` hasta encontrar el original (HEIC o JPG).

## 1. Imágenes emparejadas

| Split | Imágenes del dataset | Emparejadas | Sin emparejar |
|---|---:|---:|---:|
| valid | 61 | 61 | 0 |
| test | 31 | 31 | 0 |

## 2. Resultados (mAP@50 y recall por clase)

### valid

| Condición | mAP@50 | Aluminio | Carton | Plastico (recall) |
|---|---:|---:|---:|---:|
| A: dataset Stretch 640 | 0.440 | 0.371 | 0.647 | 0.286 |
| B: original + letterbox | 0.408 | 0.375 | 0.608 | 0.357 |
| C: original + Stretch 640 | 0.451 | 0.375 | 0.647 | 0.452 |

- Δ(B−A) = -0.032; Δ(C−A) = +0.011 (tolerancia ±0.02).
- C ≈ A: **True**; B cae: **True** → desajuste real: **SÍ**.

### test

| Condición | mAP@50 | Aluminio | Carton | Plastico (recall) |
|---|---:|---:|---:|---:|
| A: dataset Stretch 640 | 0.437 | 0.500 | 0.448 | 0.417 |
| B: original + letterbox | 0.440 | 0.500 | 0.517 | 0.375 |
| C: original + Stretch 640 | 0.475 | 0.625 | 0.448 | 0.458 |

- Δ(B−A) = +0.003; Δ(C−A) = +0.038 (tolerancia ±0.02).
- C ≈ A: **False**; B cae: **False** → desajuste real: **NO**.

## 3. Criterio y lectura global

Regla: si C se parece a A (±0,02) y B cae más de 0,02, el desajuste
Stretch/letterbox es real; si no, se descarta.

- Splits que cumplen la regla estricta: **valid**.
- Dirección C ≥ A ≥ B en ambos splits: **False**.
- C ≥ A en los dos splits: **True**; B ≤ A en los dos splits: **False**.
- Con 61/31 imágenes emparejadas, la evidencia es **parcial**: en
  valid el patrón encaja y en test no, así que no se descarta el
  desajuste pero tampoco se afirma que sea la causa principal de la
  caída en fotos nuevas.
- Esta medición no cambia pesos, umbrales ni el mAP@50 oficial 0,562.
