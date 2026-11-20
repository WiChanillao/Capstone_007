# Diagnóstico de generalización del modelo EcoLearn

> Rama: `experimento/generalizacion`. **Sin push. Sin reentrenamiento.**
> No se modificaron `main.py`, `App.jsx`, `best.pt`, `docker-compose.yml` ni
> ningún archivo que afecte a la app en ejecución.
> Evidencia sanitizada: sin rutas personales, sin valores de credenciales.
> `mAP@50 = 0,562` se mantiene como métrica oficial intacta.

---

## Estado de los datos

El dataset etiquetado fue localizado y **extraído sólo en un directorio
temporal fuera del repositorio** (`data.yaml`, `train/`, `valid/`, `test/`).
No se usó API key, no se descargó nada de Roboflow y **no se versionó ninguna
imagen, etiqueta ni peso**. Se identificó con el proyecto `capstone-s2mpp`,
versión 1 de Roboflow; coincide con el que el notebook de entrenamiento
descargaba.

| Split | Imágenes | Originales | Copias por original | Instancias (Aluminio / Cartón / Plástico) |
|---|---:|---:|---:|---|
| train | 860 | 215 | 4 (todos) | 316 / 572 / 568 |
| valid | 61 | 61 | 1 | 16 / 51 / 42 |
| test | 31 | 31 | 1 | 8 / 29 / 24 |
| **Total** | **952** | **307** | — | 340 / 652 / 634 |

Reproducible con `Fase 3/docs/experimentos/auditoria_dataset.py`; detalle en
`Fase 3/docs/evidencia/auditoria_dataset.md` y `.json`.

### 860 vs 1112

- **860 / 61 / 31 es lo que efectivamente contiene el dataset v1** y lo que
  confirma el notebook que generó los pesos (`#celda4:18`, `#celda11:3`).
- La cifra **1112 / 61 / 31** aparece en
  `docs/pruebas/PLAN_DE_PRUEBAS_EcoLearn.md:163,214` como "auditoría previa".
  Es una **discrepancia documental** respecto del export v1 real, no una
  versión alternativa confirmada. Debe corregirse en ese documento.

---

## PARTE A — auditoría sin reentrenamiento (resumen)

### A1. Secretos

| Alcance | Coincidencias de texto | Valores literales de credencial |
|---|---:|---:|
| Árbol actual | 97 | **0** |
| Historial `git log -p --all` | 164 | **2** (históricos, ya eliminados del árbol) |
| `CrispDM_Ecolearn.ipynb` | 9 | **0** |

Único hallazgo real: un patrón de clave de Google en `Fase 2/CrisdmFinal.ipynb:776`,
añadido en `8c31ef7bc2` y eliminado en `8cb12ffc88`. Valor redactado como
`***`. **No se reescribió el historial.** Hoy no hay clave de Roboflow ni
token escrito en texto en el árbol.

### A2. Entrenamiento vs inferencia

| Parámetro | Notebook | Backend |
|---|---|---|
| Conf de decisión | 0,40 (modelo desde 0,10) | **0,50** (`main.py:323,493`) |
| Nitidez | 100 | **50** (`main.py:330`) |
| EXIF | `predict(source=ruta)` | `ImageOps.exif_transpose` (`main.py:478`) |
| `imgsz` | 640 fijado en entrenamiento | no pasado explícitamente a `model(image)` |
| Semilla | no fijada | — |
| Frontend | — | reescala a 1600 px (`App.jsx:30-44`) |

**Demostrado:** los desajustes existen en el código.
**Hipótesis:** que expliquen parte de la peor detección en producción; la
PARTE B separa ese efecto del sobreajuste a los datos.

### A3. CI

`.github/workflows/ci.yml` tiene los `working-directory` correctos,
`requirements-dev.txt` existe y `tests/conftest.py:9` define
`MYSQL_PASSWORD`. No se encontró un fallo estructural por falta de default
de MySQL. Riesgos no verificados en GitHub: versiones de las actions y fallos
de `pip-audit` / `npm audit` por CVEs nuevas.

---

## PARTE B — auditoría del dataset y medición de `best.pt`

### B1. Nitidez y augmentations: origen del desenfoque (HECHO DEMOSTRADO)

El origen del desenfoque **ya no es una hipótesis**. La configuración real de
la versión 1 de Roboflow es:

> **Auto-Orient; Resize Stretch 640×640; 4 salidas por ejemplo; Flip
> horizontal y vertical; Grayscale 15 %; brillo ±15 %; Cutout de 3 cajas del
> 10 %; Motion Blur de 100 px (ángulo 0°).**

El `README.roboflow.txt` incluido en el ZIP sólo declaraba *"50 % probability
of horizontal flip, 50 % probability of vertical flip, random brightness
between -15 and +15 percent"*. Estaba incompleto: no mencionaba Grayscale,
Cutout ni Motion Blur.

Consecuencias medidas (varianza del Laplaciano a 640 px):

| Split | < 50 (movido) | 50–100 | > 100 (nítido) | Imágenes con bloque negro rectangular | Imágenes gris > 50 % |
|---|---:|---:|---:|---:|---:|
| train | **515 / 860 (60 %)** | 86 | 259 | **199** | 86 |
| valid | 1 / 61 | 3 | 57 | 1 | 0 |
| test | 0 / 31 | 2 | 29 | 1 | 0 |

Dentro de cada original de train, el patrón más frecuente es **3 copias
movidas y 1 nítida** (97 de 215 originales); le siguen 2 movidas + 1 nítida
(34) y 2 movidas + 2 nítidas (33). En 16 originales las 4 copias están
movidas y en 5 no hay ninguna copia nítida.

**Conclusión demostrada:** la distribución de train (60 % de copias con motion
blur y cutout) **difiere radicalmente de valid y test**, que no recibieron
augmentationes. El modelo aprendió una mezcla de imágenes nítidas y degradadas
que no aparece en evaluación. Esto explica por qué train se mide tan por encima
de valid/test (sección B4), sin necesidad de apelar a hipótesis sobre el origen
del desenfoque.

### B2. Preprocesamiento: Stretch vs letterbox y aumentos redundantes

- **Stretch ≠ letterbox.** El dataset v1 redimensiona cada imagen a
  640×640 **estirando** (Resize Stretch), deformando la relación de aspecto.
  La inferencia de Ultralytics usa **letterbox** (resize conservando aspecto
  con relleno). El backend además recibe la imagen reescalada a 1600 px desde
  el frontend. Por tanto, la geometría que ve el modelo en producción no es
  la que vio en entrenamiento.
- **Augmentos duplicados.** Ultralytics ya aplica al vuelo `fliplr=0.5`,
  jitter HSV, escala, traslación y mosaico durante `train()`. Los flips de
  Roboflow y gran parte del brillo son, por eso, **en parte redundantes**: las
  4 copias offline repiten información que el entrenador ya genera. Sólo
  Grayscale, Cutout y Motion Blur aportan algo nuevo, y justo son los que
  generan el desajuste con valid/test.

### B3. Fuga de escena y duplicados

| Indicador | Resultado |
|---|---:|
| Originales compartidos entre splits | 0 |
| Valid con número `IMG_NNNN` vecino de train (±1) | **38 / 61** |
| Test con número `IMG_NNNN` vecino de train (±1) | **16 / 31** |
| Pares HDR valid/test ↔ train a ≤ 10 s | **52** |

**Umbral de hash declarado:** distancia de Hamming **≤ 10 sobre 64 bits de
pHash O ≤ 12 sobre 64 bits de dHash** (basta que se cumpla uno). Los hashes se
calculan en escala de grises sobre las imágenes ya exportadas.

Los **339 pares** que cumplen ese umbral se desglosan así:

| Tipo de par | Pares | ¿Fuga? |
|---|---:|---|
| (i) train–train (copias aumentadas del mismo original) | 330 | No |
| (ii) train–valid | 4 | **Sí** |
| (iii) train–test | 4 | **Sí** |
| (iv) valid–test | 1 | **Sí** |
| valid–valid / test–test | 0 / 0 | No (evaluación) |

De los 330 pares train–train, **324 son copias del mismo original** (mismo
nombre base antes del sufijo `.rf.<hash>`): son las 4 salidas por ejemplo de
Roboflow, no fuga. **La fuga real entre splits son 9 pares** ((ii)+(iii)+(iv)).

Ejemplos: `valid:IMG_8840_HEIC ↔ train:IMG_8841_HEIC`;
`valid:IMG_20260930_094828610_HDR ↔ train:IMG_20260930_094826097_HDR (2,0 s)`.
`train:IMG_8842_HEIC ↔ test:IMG_8843_HEIC` es uno de los pares casi duplicados
entre splits. Aunque no se repite el mismo archivo, sí se repite la **misma
escena** en splits distintos: las métricas de valid/test están infladas por
vecinos de ráfaga vistos en entrenamiento.

### B4. Medición de `best.pt`

Ejecutada con `Fase 3/docs/experimentos/medicion.py` sobre los cuatro subsets.
No se modificaron pesos ni imágenes. Detalle completo en
`Fase 3/docs/evidencia/medicion_generalizacion.md` y `.json`.

#### Global (P / R / F1 / mAP@50)

| conf | subset | P | R | F1 | mAP@50 | mAP@50-95 |
|---:|---|---:|---:|---:|---:|---:|
| **0,50** | train_nitido (259 imgs) | 0,974 | 0,898 | 0,934 | **0,896** | 0,746 |
| **0,50** | train_movido (515 imgs) | 0,951 | 0,842 | 0,892 | **0,840** | 0,688 |
| **0,50** | valid (61 imgs) | 0,728 | 0,474 | 0,564 | **0,445** | 0,309 |
| **0,50** | test (31 imgs) | 0,842 | 0,455 | 0,589 | **0,429** | 0,277 |
| 0,35 | train_nitido | 0,961 | 0,903 | 0,931 | 0,914 | 0,757 |
| 0,35 | train_movido | 0,959 | 0,834 | 0,892 | 0,871 | 0,706 |
| 0,35 | valid | 0,606 | 0,532 | 0,565 | 0,480 | 0,329 |
| 0,35 | test | 0,826 | 0,511 | 0,627 | 0,477 | 0,299 |
| 0,25 | train_nitido | 0,970 | 0,893 | 0,930 | 0,932 | 0,765 |
| 0,25 | train_movido | 0,959 | 0,834 | 0,892 | 0,891 | 0,719 |
| 0,25 | valid | 0,555 | 0,561 | 0,557 | 0,493 | 0,332 |
| 0,25 | test | 0,820 | 0,507 | 0,624 | 0,486 | 0,301 |
| **0,001** | test | 0,814 | 0,506 | 0,620 | **0,564** | 0,330 |

**Dos puntos de operación distintos, no dos métricas rivales.**

- **Punto oficial:** `val()` en test con conf por defecto **0,001** →
  **mAP@50 = 0,564**, que confirma el **0,562 oficial** (diferencia de
  redondeo/entorno). Es el número de referencia del modelo y **no se cambia**.
- **Punto de operación del backend:** conf **0,50** → 0,896 / 0,840 / 0,445 /
  0,429 en train_nitido / train_movido / valid / test. Estas cuatro cifras son
  **otro punto de operación**: `conf` recorta detecciones antes de la curva
  P-R. **Compárense sólo entre sí**, nunca contra el 0,562: no es una
  contradicción ni una corrección de la métrica oficial.
- 0,429 es el número que describe el comportamiento real del backend, porque
  ahí es donde decide. 0,562 sigue siendo la métrica oficial intacta.

#### Brechas medidas

- **train_nitido − test a conf=0,50: 0,896 − 0,429 = 0,467.** Es la brecha
  de generalización principal.
- **train_nitido − train_movido: 0,896 − 0,840 = 0,056.** El motion blur y el
  cutout cuestan ~5,6 puntos de mAP@50 dentro de train, pero **no explican**
  la caída a test: incluso las copias nítidas de train están muy por encima
  de valid/test.
- **valid − test a conf=0,50: 0,445 − 0,429 = 0,016.** Valid y test están
  casi al mismo nivel, coherente con que ambos comparten escenas con train.

#### Por clase a conf=0,50

| subset | Aluminio P/R/F1 | Cartón P/R/F1 | Plástico P/R/F1 |
|---|---|---|---|
| train_nitido | 0,986 / 0,921 / 0,952 | 0,994 / 0,928 / 0,960 | 0,941 / 0,845 / 0,890 |
| train_movido | 0,960 / 0,806 / 0,876 | 0,965 / 0,892 / 0,927 | 0,927 / 0,827 / 0,874 |
| valid | 0,857 / 0,375 / 0,522 | 0,791 / 0,667 / 0,723 | 0,537 / 0,381 / 0,446 |
| test | 0,800 / 0,500 / 0,615 | 0,929 / 0,448 / 0,605 | 0,798 / 0,417 / 0,547 |

Plástico es la clase más débil en valid (F1 0,446) y en test (0,547 pese a
tener la precisión más alta del trio). Aluminio tiene recall 0,375 en valid
con sólo 16 instancias y 0,500 en test con **8 instancias**.

**Inestabilidad de Aluminio en test:** 8 instancias. A conf=0,50, recall
0,500 con intervalo de Wilson 95 % [0,215 ; 0,785] y precision 0,800
([0,376 ; 0,964]). Una sola instancia cambia el resultado en 12,5 puntos;
no se debe tomar ninguna decisión definitiva de umbral con esta muestra.

#### AP50 por clase con IC 95 % (bootstrap, conf=0,50)

Remuestreo de **imágenes con reposición**, 1000 réplicas, semilla 42, AP50 de
101 puntos sobre el caché de detecciones (piso conf=0,01). El AP50 puntual de
esta tabla usa el mismo criterio de emparejamiento que el resto del script y
puede diferir del `ap50_clase` de `val()`; compárense sólo los valores de la
tabla.

| Subset | Clase | AP50 | IC 95 % | Instancias | Lectura |
|---|---|---:|---|---:|---|
| valid | Aluminio | 0,376 | [0,158 ; 0,614] | 16 | amplio |
| valid | Cartón | 0,607 | [0,472 ; 0,766] | 51 | el más estable |
| valid | Plástico | 0,265 | [0,122 ; 0,460] | 42 | bajo |
| test | Aluminio | 0,505 | [0,128 ; 0,832] | 8 | **NO CONCLUYENTE** |
| test | Cartón | 0,391 | [0,232 ; 0,618] | 29 | amplio |
| test | Plástico | 0,281 | [0,089 ; 0,469] | 24 | bajo y amplio |

Todos los intervalos son anchos; el de **Aluminio en test** abarca casi todo
el rango y confirma que sus 8 instancias no permiten afirmar superioridad ni
fijar un umbral. Fuente: `medicion_generalizacion.md` §2b y su `.json`.

### B5. Umbrales y errores

Las etiquetas del dataset son **polígonos de segmentación**; la caja
envolvente se reconstruyó desde el polígono para calcular P/R/F1 propios con
IoU > 0,5. La curva F1 global por confianza está en la sección 4 de
`medicion_generalizacion.md`.

| Clase | Umbral de máximo F1 en valid | F1 en valid | F1 en test a 0,50 | F1 en test con umbral por clase |
|---|---:|---:|---:|---:|
| Aluminio | 0,25 | 0,667 | 0,615 | 0,667 |
| Cartón | 0,45 | 0,750 | 0,558 | 0,533 |
| Plástico | 0,20 | 0,500 | 0,424 | 0,500 |

Bajar el umbral mejora Aluminio y Plástico en test pero empeora Cartón; con
8 instancias de Aluminio en test, cualquiera de estas diferencias está dentro
del ruido. **Los umbrales propuestos NO se aplicaron al backend.** `main.py`
sigue con conf=0,50 y nitidez=50. Son sólo una línea base para el plan de
entrenamiento.

Los 20 falsos negativos y 20 falsos positivos más confiados de test, con ruta
sanitizada, confianza, causa heurística y Laplaciano, están en las secciones 5
y 6 de `medicion_generalizacion.md`. Las causas se agrupan en:
desenfoque/movido (Laplaciano < 50), cutout (bloque negro), grayscale, objeto
pequeño, tamaño de escena y un último grupo **"revisar: fondo / reflejo /
transparencia / oclusión"** que concentra la mayoría de los casos y requiere
revisión visual. Son heurísticas automáticas, no conclusiones visuales.

### B6. Datasets experimentales preparados

Generados por `Fase 3/docs/experimentos/preparar_datasets.py`, semilla 42,
**fuera del repositorio**. No se entrenó con ellos. Detalle en
`Fase 3/docs/evidencia/datasets_experimentales.md`.

| Dataset | train | valid | test | Uso |
|---|---:|---:|---:|---|
| `train_nitido` | 215 (79/143/142) | 61 | 31 | E1: una copia nítida por original |
| `split_por_escenas` | 215 (79/169/129) | 61 | 31 | E3: 307 originales, 88 ventanas de ráfaga, 0 grupos repartidos entre splits |

El split por escenas cambia el reparto de clases en valid/test (Aluminio
20/4 frente a 16/8 del original), por lo que sus métricas no son comparables
directamente con las de E0–E2.

### B7. Plan de entrenamiento (no ejecutado)

Matriz en `Fase 3/docs/experimentos/plan_entrenamiento.md` y plantilla Colab
en `Fase 3/docs/experimentos/experimentos_yolo.ipynb`:

| # | Configuración |
|---|---|
| E0 | Baseline v1 (860 train, Stretch, augmentations de Roboflow) |
| E1 | `train_nitido` (sólo la copia más nítida de cada original) |
| E2 | Versión 2 sin augmentations de Roboflow, Resize Fit con bordes negros |
| E3 | Split por escenas sin fuga |

Cada una con **3 semillas**, selección por **valid**, **test una sola vez** y
latencia objetivo **< 100 ms**. El notebook **no contiene credenciales**: monta
Google Drive, descomprime los zips y usa rutas configurables.

### B8. Experimento Stretch vs letterbox (sin reentrenar)

Ejecutado con `Fase 3/docs/experimentos/exp_geometria.py`. Se emparejaron las
imágenes de valid/test del dataset con sus **fotos originales HEIC/JPG** por
nombre base (Roboflow convirtió `(1)` en `-1-`; se normalizó), con
**auto-orient EXIF**. Las etiquetas normalizadas valen sobre la foto original
y sobre la versión estirada. Detalle en `exp_geometria.md` y `.json`.

| Split | Imágenes | Emparejadas |
|---|---:|---:|
| valid | 61 | 61 |
| test | 31 | 31 |

| Condición | mAP@50 valid | mAP@50 test |
|---|---:|---:|
| A: dataset Stretch 640 (como hoy) | 0,4399 | 0,4369 |
| B: original + letterbox (producción) | 0,4078 | 0,4402 |
| C: original + Stretch 640 antes de inferir | 0,4513 | 0,4751 |

Regla pedida: si C se parece a A (±0,02) y B cae >0,02, el desajuste es real.

- **Valid cumple la regla** (ΔB−A = −0,032; ΔC−A = +0,011): desajuste real.
- **Test no la cumple** (ΔB−A = +0,003; ΔC−A = +0,038): B no cae y C mejora.
- C ≥ A en ambos splits, pero B ≤ A sólo en valid. Con 61/31 imágenes, la
  evidencia es **parcial**: no se descarta el desajuste, pero tampoco se afirma
  que sea la causa principal de la caída con fotos nuevas. Sigue siendo una
  **hipótesis medida**, no un hecho demostrado.

### B9. Paquetes para Colab (fuera del repo)

Generados por `Fase 3/docs/experimentos/empaquetar_colab.py` con `data.yaml`
portable (`path: '.'`, rutas relativas). No se subió nada a Drive.

| Paquete | Tamaño | Imágenes (train/valid/test) | sha256 (inicio) |
|---|---:|---|---|
| `train_nitido.zip` | 17,15 MB | 215 / 61 / 31 | `faad99aa…` |
| `split_por_escenas.zip` | 17,15 MB | 215 / 61 / 31 | `2625cd55…` |

Ubicación temporal: `AppData/Local/Temp/opencode/paquetes_colab/`. **Qué subir a
Drive:** esos dos zips a `MyDrive/EcoLearn/`, sin descomprimir; el notebook los
extrae solo. E0 necesita además el dataset v1 y E2 el export v2 (prepararlos
aparte). El notebook guarda por corrida `results.csv` y `best.pt` en
`MyDrive/EcoLearn/resultados/<experimento>_s<semilla>/`, más
`resumen_valid.csv` y `resumen_test.json`. Verificación automática: 7 celdas,
JSON y código válidos, sin `userdata`/`API_KEY`, Drive montado, semillas 0/1/2,
selección por valid, test una vez y latencia <100 ms.

---

## Conclusión

### Demostrado

- El dataset v1 tiene **860 / 61 / 31 imágenes** (215 originales ×4 en train);
  el 1112 de la documentación previa es una discrepancia, no un dato del ZIP.
- El desenfoque viene de **Motion Blur de 100 px (0°)** y el cutout de
  **3 cajas del 10 %**, configuración real de v1 que el README no declaraba.
  El 60 % de train está movido y 199 imágenes tienen bloques negros; valid y
  test no se aumentan.
- Existe **fuga de escena**: 38/61 valid y 16/31 test tienen vecinos de
  ráfaga en train, con 52 pares HDR a ≤10 s. De los 339 pares casi duplicados
  por hash, 330 son copias aumentadas dentro de train (324 del mismo original)
  y **9 son fuga real** entre splits.
- El Stretch 640×640 de entrenamiento no coincide con el letterbox de
  inferencia; las 4 copias offline son en parte redundantes con los aumentos
  al vuelo de Ultralytics. El experimento A/B/C da evidencia **parcial** de
  este desajuste (cumple en valid, no en test).
- `best.pt` mide **mAP@50 = 0,896 en train nítido** frente a **0,429 en test**
  a conf=0,50 (brecha 0,467). A conf=0,001 reproduce el **0,562 oficial**
  (0,564 medido).
- Plástico es la clase más débil en valid y Aluminio la más inestable en test
  (8 instancias).
- Los desajustes de umbrales, EXIF, resolución y semilla entre notebook y
  backend existen en el código. Hubo una credencial literal en el historial,
  ya eliminada del árbol actual.

### Hipótesis (no demostradas)

- Que la geometría Stretch/letterbox y el filtro de nitidez del backend
  expliquen una parte adicional de la caída en fotos nuevas. El experimento
  A/B/C se ejecutó sobre los originales del dataset y dio evidencia parcial;
  falta medirlo con fotos capturadas **fuera** del dataset.
- Que la escasez de plásticos aislados y de fondos neutros sea la causa
  principal del bajo recall de Plástico; los FN/FP apuntan ahí, pero las
  causas son heurísticas y requieren revisión visual.
- Que una nueva versión del dataset corrija la brecha. La matriz E0–E3 está
  diseñada para probarlo, pero **no se ejecutó**.
- Que la varianza entre semillas sea pequeña; no hay entrenamientos
  replicados todavía.

**No se cambió en esta rama:** `best.pt`, `main.py`, `App.jsx`, compose, el
mAP@50 oficial 0,562 ni ningún archivo de la app en ejecución. No se aplicaron
umbrales al backend. No se hizo push. El cambio de umbrales por clase se
desarrolla aparte, en la rama `feature/umbrales-por-clase` creada desde `main`,
y **no se mezcla** con `experimento/generalizacion`.
