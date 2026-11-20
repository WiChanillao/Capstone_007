# Evaluación de umbrales por clase en test

- Pesos: `best.pt` **sin modificar**. Inferencia `imgsz=640`, conf=0,01.
- Imágenes de test evaluadas: **31**. IoU de emparejamiento > 0,5.
- Misma caché de detecciones para ambos puntos de operación: una sola pasada.
- Dataset: `AppData/Local/Temp/opencode/dataset_capstone_v1i`.

## Configuraciones

| Configuración | Aluminio | Cartón | Plástico |
|---|---:|---:|---:|
| Actual (defaults) | 0,50 | 0,50 | 0,50 |
| Propuesta (sólo evaluada) | 0,25 | 0,45 | 0,20 |

## Resultado: recall ganado y FP añadidos

| Clase | Instancias | Recall actual | Recall propuesto | Δ recall | FP actual | FP propuesto | Δ FP |
|---|---:|---:|---:|---:|---:|---:|---:|
| Aluminio | 8 | 0.125 | 0.125 | +0.000 | 4 | 6 | +2 |
| Carton | 29 | 0.138 | 0.138 | +0.000 | 10 | 12 | +2 |
| Plastico | 24 | 0.292 | 0.500 | +0.208 | 2 | 8 | +6 |
| **Total** | 61 | 0.197 | 0.279 | +0.082 | 16 | 26 | +10 |

## Lectura

- El delta de recall está ponderado por instancias reales de cada clase.
- Los FP se cuentan con el mismo criterio en ambos puntos de operación.
- **No se cambió ningún default**: el backend sigue decidiendo a 0,50
  para las tres clases; el nivel "posible" se reporta aparte.
- Aluminio y Cartón **no ganan recall** en esta muestra y sí añaden FP:
  no hay motivo para bajar sus umbrales con estos datos.
- Plástico recupera 5 instancias a costa de 6 FP; es un dato para la
  matriz E0–E3 con 3 semillas, no una decisión de producto.
- Aluminio en test tiene 8 instancias; su delta es orientativo.
