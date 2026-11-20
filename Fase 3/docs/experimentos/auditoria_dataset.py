#!/usr/bin/env python3
"""Auditoría reproducible del dataset YOLOv11 v1 (SOLO LECTURA).

Reproduce y documenta:
  * splits 860/61/31 y 215 originales x4 copias (307 originales);
  * nitidez (varianza del Laplaciano a 640 px): 515/860 en train <50;
  * cutout/bloques negros, gris y desenfoque (augmentations reales de v1);
  * fuga de escena por numeración IMG_NNNN vecina y por HDR <10 s;
  * instancias por clase y tamaño de imagen;
  * duplicados por pHash/dHash.

No copia ni versiona imágenes. Escribe sólo markdown/JSON en docs/evidencia.

Uso:
  python auditoria_dataset.py --dataset <carpeta_con_data.yaml> \
      [--reporte <md>] [--json <json>]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
CLASES = ("Aluminio", "Carton", "Plastico")
UMBRAL_P_H = 10          # pHash 64 bits
UMBRAL_D_H = 12          # dHash 64 bits
LAP_MOVIDA = 50.0
LAP_NITIDA = 100.0
SEG_RAFAGA = 10
ADYACENCIA = 1


def seguro(texto: str | Path) -> str:
    """Quita el prefijo del directorio personal del usuario."""
    s = str(texto).replace("\\", "/")
    s = re.sub(r"^[A-Za-z]:/Users/[^/]+/", "", s)
    s = re.sub(r"^/Users/[^/]+/", "", s)
    return s


def imagenes(split_dir: Path) -> list[Path]:
    if not split_dir.exists():
        return []
    return sorted(p for p in split_dir.rglob("*")
                  if p.is_file() and p.suffix.lower() in EXT)


def original(p: Path) -> str:
    """Quita el sufijo .rf.<hash>.jpg de Roboflow."""
    return re.sub(r"\.rf\.[0-9a-f]{16,}\.[A-Za-z]+$", "", p.name)


def identificador(clave: str) -> tuple[str, int]:
    """Devuelve (tipo, valor) para agrupar ráfagas por número o timestamp."""
    m = re.search(r"IMG_\d{8}_(\d{9})_HDR", clave)
    if m:
        return ("HDR", int(m.group(1)))
    m = re.search(r"IMG_(\d+)", clave)
    if m:
        return ("SEQ", int(m.group(1)))
    return ("OTRO", hash(clave) % (10 ** 9))


def tiempo_hdr(clave: str) -> datetime | None:
    m = re.search(r"IMG_(\d{8})_(\d{9})_HDR", clave)
    if not m:
        return None
    fecha, reloj = m.group(1), m.group(2)
    try:
        return datetime.strptime(
            f"{fecha}{reloj[:6]}", "%Y%m%d%H%M%S"
        )
    except ValueError:
        return None


def lap_gray(path: Path) -> float:
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if im is None:
        return float("nan")
    return float(cv2.Laplacian(im, cv2.CV_64F).var())


def phash(path: Path) -> np.ndarray | None:
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if im is None:
        return None
    im = cv2.resize(im, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    d = cv2.dct(im)[:8, :8]
    return (d > np.median(d[1:])).flatten()


def dhash(path: Path) -> np.ndarray | None:
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if im is None:
        return None
    im = cv2.resize(im, (9, 8), interpolation=cv2.INTER_AREA)
    return (im[:, 1:] > im[:, :-1]).flatten()


def dist(a, b) -> int:
    return int(np.count_nonzero(a != b))


def analizar_oscuridad(path: Path) -> tuple[float, int, float]:
    """(fracción near-black, componentes rectangulares grandes, fracción gris)."""
    im = cv2.imread(str(path))
    if im is None:
        return 0.0, 0, 0.0
    negro = np.all(im <= 10, axis=2).astype(np.uint8)
    fraccion_negro = float(negro.mean())
    n, etiquetas, stats, _ = cv2.connectedComponentsWithStats(negro, 8)
    bloques = 0
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area < 3000 or w < 20 or h < 20:
            continue
        if area / (w * h) >= 0.70:
            bloques += 1
    maxmin = im.max(axis=2).astype(np.int16) - im.min(axis=2).astype(np.int16)
    fraccion_gris = float((maxmin <= 4).mean())
    return fraccion_negro, bloques, fraccion_gris


def clases_yaml(root: Path) -> list[str]:
    import yaml
    y = yaml.safe_load((root / "data.yaml").read_text(encoding="utf-8"))
    n = y.get("names", {})
    return [n[i] for i in sorted(n)] if isinstance(n, dict) else list(n)


def instancias(path: Path, names: list[str]) -> Counter:
    c: Counter = Counter()
    lbl = path.parent.parent / "labels" / (path.stem + ".txt")
    if not lbl.exists():
        return c
    for linea in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
        q = linea.split()
        if len(q) < 5:
            continue
        try:
            idx = int(float(q[0]))
        except ValueError:
            continue
        if 0 <= idx < len(names):
            c[names[idx]] += 1
    return c


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", required=True, type=Path)
    ap.add_argument("--reporte", type=Path,
                    default=Path("Fase 3/docs/evidencia/auditoria_dataset.md"))
    ap.add_argument("--json", type=Path,
                    default=Path("Fase 3/docs/evidencia/auditoria_dataset.json"))
    args = ap.parse_args()

    root = args.dataset.resolve()
    if not (root / "data.yaml").exists():
        raise SystemExit("No se encontró data.yaml en --dataset")
    names = clases_yaml(root)

    registros: list[dict] = []
    for split, carpeta in (("train", "train/images"), ("valid", "valid/images"),
                           ("test", "test/images")):
        for p in imagenes(root / carpeta):
            registros.append({
                "split": split, "path": p, "key": original(p),
                "inst": instancias(p, names),
            })

    for r in registros:
        r["lap"] = lap_gray(r["path"])
        r["negro"], r["bloques"], r["gris"] = analizar_oscuridad(r["path"])
        r["p"] = phash(r["path"])
        r["d"] = dhash(r["path"])
        r["tipo"], r["id"] = identificador(r["key"])
        r["tiempo"] = tiempo_hdr(r["key"])

    totales = Counter(r["split"] for r in registros)
    inst_por_split = {s: Counter() for s in ("train", "valid", "test")}
    for r in registros:
        inst_por_split[r["split"]].update(r["inst"])

    orig_por_split = {s: {r["key"] for r in registros if r["split"] == s}
                      for s in ("train", "valid", "test")}
    copias = Counter()
    for r in registros:
        copias[(r["split"], r["key"])] += 1
    patron_copias = Counter(copias.values())

    nit = {s: {
        "lt50": sum(r["lap"] < LAP_MOVIDA for r in registros if r["split"] == s),
        "gt100": sum(r["lap"] > LAP_NITIDA for r in registros if r["split"] == s),
        "entre": sum(LAP_MOVIDA <= r["lap"] <= LAP_NITIDA
                     for r in registros if r["split"] == s),
    } for s in ("train", "valid", "test")}

    por_original = defaultdict(list)
    for r in registros:
        if r["split"] == "train":
            por_original[r["key"]].append(r["lap"])
    patron_lap = Counter()
    for clave, vals in por_original.items():
        patron_lap[(sum(v < LAP_MOVIDA for v in vals),
                    sum(v > LAP_NITIDA for v in vals))] += 1

    cutout = {s: {
        "imagenes_con_bloque": sum(r["bloques"] >= 1 for r in registros
                                   if r["split"] == s),
        "fraccion_black_promedio": round(float(np.mean([r["negro"] for r in registros
                                                        if r["split"] == s])), 4),
        "imagenes_gris": sum(r["gris"] > 0.5 for r in registros if r["split"] == s),
    } for s in ("train", "valid", "test")}

    # Fuga de escena: originales compartidos, números vecinos y HDR cercanos.
    compartidos = orig_por_split["train"] & (orig_por_split["valid"] | orig_por_split["test"])
    vecinos = {s: 0 for s in ("valid", "test")}
    pares_vecinos: list[str] = []
    for s in ("valid", "test"):
        for r in registros:
            if r["split"] != s or r["tipo"] != "SEQ":
                continue
            cercanos = [q for q in registros
                        if q["split"] == "train" and q["tipo"] == "SEQ"
                        and abs(q["id"] - r["id"]) <= ADYACENCIA]
            if cercanos:
                vecinos[s] += 1
                if len(pares_vecinos) < 12:
                    pares_vecinos.append(
                        f"{s}:{r['key']} ↔ train:{cercanos[0]['key']}"
                    )

    hdr_por_split = {s: {r["key"]: r["tiempo"] for r in registros
                         if r["split"] == s and r["tiempo"] is not None}
                     for s in ("train", "valid", "test")}
    rafaga_pares = 0
    ejemplos_rafaga: list[str] = []
    for s in ("valid", "test"):
        for clave_r, tr in hdr_por_split[s].items():
            for clave_q, tq in hdr_por_split["train"].items():
                if abs((tr - tq).total_seconds()) <= SEG_RAFAGA:
                    rafaga_pares += 1
                    if len(ejemplos_rafaga) < 12:
                        ejemplos_rafaga.append(
                            f"{s}:{clave_r} ↔ train:{clave_q} "
                            f"({abs((tr-tq).total_seconds()):.1f}s)"
                        )

    # Duplicados por hash perceptual, desglosados por combinación de splits.
    # Sólo los pares entre splits distintos son fuga; train-train son las
    # copias aumentadas del mismo original que Roboflow generó offline.
    orden_split = ("train", "valid", "test")
    claves_par = [f"{a}-{b}" for i, a in enumerate(orden_split)
                  for b in orden_split[i:]]
    pares_por_tipo = {k: 0 for k in claves_par}
    train_train_mismo_original = 0
    ejemplos_duplicados: dict[str, str] = {}
    for i in range(len(registros)):
        for j in range(i + 1, len(registros)):
            a, b = registros[i], registros[j]
            dp = dist(a["p"], b["p"])
            dd = dist(a["d"], b["d"])
            if dp <= UMBRAL_P_H or dd <= UMBRAL_D_H:
                par = tuple(sorted((a["split"], b["split"]),
                                   key=orden_split.index))
                clave = f"{par[0]}-{par[1]}"
                pares_por_tipo[clave] += 1
                if clave == "train-train" and a["key"] == b["key"]:
                    train_train_mismo_original += 1
                if clave not in ejemplos_duplicados:
                    ejemplos_duplicados[clave] = (
                        f"{a['split']}:{a['key']} ↔ {b['split']}:{b['key']} "
                        f"(pHash={dp}, dHash={dd})"
                    )
    pares = sum(pares_por_tipo.values())
    fuga_pares = (pares_por_tipo["train-valid"] +
                  pares_por_tipo["train-test"] +
                  pares_por_tipo["valid-test"])

    tamanos = Counter()
    for r in registros[:30]:
        im = cv2.imread(str(r["path"]))
        if im is not None:
            tamanos[f"{im.shape[1]}x{im.shape[0]}"] += 1

    datos = {
        "dataset": seguro(root),
        "clases": names,
        "total_imagenes": sum(totales.values()),
        "splits": dict(totales),
        "originales_por_split": {s: len(v) for s, v in orig_por_split.items()},
        "originales_totales": len(set().union(*orig_por_split.values())),
        "copias_por_original_train": dict(patron_copias),
        "instancias": {s: dict(c) for s, c in inst_por_split.items()},
        "nitidez": nit,
        "patron_lap_train": {f"movidas<50={k[0]},nitidas>100={k[1]}": v
                             for k, v in patron_lap.most_common()},
        "augmentations_detectadas": cutout,
        "fuga": {
            "originales_compartidos": len(compartidos),
            "valid_con_numero_vecino_en_train": vecinos["valid"],
            "test_con_numero_vecino_en_train": vecinos["test"],
            "pares_hdr_menos_10s": rafaga_pares,
            "ejemplos_vecinos": pares_vecinos,
            "ejemplos_rafaga": ejemplos_rafaga,
        },
        "pares_casi_duplicados": pares,
        "pares_casi_duplicados_por_tipo": pares_por_tipo,
        "pares_train_train_mismo_original": train_train_mismo_original,
        "pares_fuga_entre_splits": fuga_pares,
        "ejemplos_duplicados": ejemplos_duplicados,
        "tamanos_muestra": dict(tamanos),
        "umbrales": {"lap_movida": LAP_MOVIDA, "lap_nitida": LAP_NITIDA,
                     "phash": UMBRAL_P_H, "dhash": UMBRAL_D_H,
                     "rafaga_s": SEG_RAFAGA},
    }

    L = [
        "# Auditoría del dataset YOLOv11 v1 (generada por `auditoria_dataset.py`)",
        "",
        f"- Dataset: `{seguro(root)}` (fuera del repositorio).",
        f"- Imágenes totales: **{sum(totales.values())}**.",
        "",
        "## 1. Splits y originales",
        "",
        "| Split | Imágenes | Originales | Copias por original |",
        "|---|---:|---:|---|",
    ]
    for s in ("train", "valid", "test"):
        L.append(f"| {s} | {totales[s]} | {len(orig_por_split[s])} | "
                 f"{dict(Counter(copias[(s,k)] for k in orig_por_split[s]))} |")
    L += ["", f"- Originales únicos totales: **{datos['originales_totales']}**.",
          f"- Train: **{patron_copias.get(4,0)}** originales tienen exactamente "
          "4 copias.", "", "## 2. Instancias por clase", "",
          "| Split | " + " | ".join(names) + " |", "|---|---:|---:|---:|"]
    for s in ("train", "valid", "test"):
        L.append(f"| {s} | " + " | ".join(str(inst_por_split[s][c]) for c in names) + " |")

    L += ["", "## 3. Nitidez (varianza del Laplaciano, 640×640)", "",
          "| Split | <50 (movido) | 50–100 | >100 (nítido) |", "|---|---:|---:|---:|"]
    for s in ("train", "valid", "test"):
        L.append(f"| {s} | {nit[s]['lt50']} | {nit[s]['entre']} | {nit[s]['gt100']} |")
    L += ["", "Patrón dentro de cada original de train (movidas<50, nítidas>100):", ""]
    for k, v in sorted(patron_lap.items(), key=lambda x: -x[1])[:8]:
        L.append(f"- {k[0]} movida(s), {k[1]} nítida(s): {v} originales")

    L += ["", "## 4. Augmentations reales detectadas vs README", "",
          "| Split | Imágenes con bloque negro rectangular | Fracción negra media | Imágenes gris >50 % |",
          "|---|---:|---:|---:|"]
    for s in ("train", "valid", "test"):
        d = cutout[s]
        L.append(f"| {s} | {d['imagenes_con_bloque']} | "
                 f"{d['fraccion_black_promedio']:.4f} | {d['imagenes_gris']} |")
    L += [
        "",
        "El `README.roboflow.txt` del ZIP declara sólo *flips* y brillo ±15 %.",
        "La configuración real de la versión 1 (comunicada por el usuario) es:",
        "Auto-Orient, Resize Stretch 640×640, 4 salidas por ejemplo, Flip",
        "horizontal y vertical, Grayscale 15 %, brillo ±15 %, Cutout de 3 cajas",
        "del 10 % y Motion Blur de 100 px (ángulo 0°). Las cifras de arriba son",
        "la comprobación empírica de ese desajuste: train está aumentado y",
        "valid/test no.",
        "",
        "## 5. Fuga de escena",
        "",
        f"- Originales compartidos entre splits: **{len(compartidos)}**.",
        f"- Valid con número `IMG_NNNN` vecino de train (±1): **{vecinos['valid']}/{totales['valid']}**.",
        f"- Test con número `IMG_NNNN` vecino de train (±1): **{vecinos['test']}/{totales['test']}**.",
        f"- Pares HDR valid/test ↔ train a ≤{SEG_RAFAGA} s: **{rafaga_pares}**.",
        "",
    ]
    if pares_vecinos:
        L += ["Ejemplos:", ""] + [f"- `{x}`" for x in pares_vecinos] + [""]
    if ejemplos_rafaga:
        L += ["Ejemplos de ráfaga temporal:", ""] + [f"- `{x}`" for x in ejemplos_rafaga] + [""]
    L += ["## 6. Preprocesamiento y duplicados", "",
          f"- Tamaños observados (muestra): {dict(tamanos)} → Resize 640×640 Stretch.",
          "- Umbral de hash: **distancia de Hamming ≤ "
          f"{UMBRAL_P_H} sobre 64 bits de pHash O ≤ {UMBRAL_D_H} sobre 64 bits "
          "de dHash** (se cumple cualquiera de los dos). Hashes calculados en",
          "  escala de grises sobre las imágenes ya exportadas del dataset.",
          f"- Pares que cumplen el umbral: **{pares}**. Desglose:",
          "",
          "| Tipo de par | Pares | ¿Es fuga? |",
          "|---|---:|---|",
          f"| (i) train–train (copias aumentadas) | {pares_por_tipo['train-train']} | No |",
          f"| (ii) train–valid | {pares_por_tipo['train-valid']} | **Sí** |",
          f"| (iii) train–test | {pares_por_tipo['train-test']} | **Sí** |",
          f"| (iv) valid–test | {pares_por_tipo['valid-test']} | **Sí** |",
          f"| valid–valid | {pares_por_tipo['valid-valid']} | No (evaluación) |",
          f"| test–test | {pares_por_tipo['test-test']} | No (evaluación) |",
          "",
          f"- De los pares train–train, **{train_train_mismo_original}/"
          f"{pares_por_tipo['train-train']}** son copias del **mismo original** "
          "(mismo nombre base antes del sufijo `.rf.<hash>`): son el resultado",
          "  de las 4 salidas por ejemplo de Roboflow, no fuga entre splits.",
          f"- **Fuga real entre splits: {fuga_pares} pares** ((ii)+(iii)+(iv)).",
          ""]
    if ejemplos_duplicados:
        L += ["Ejemplos por tipo:", ""] + [
            f"- `{k}`: `{v}`" for k, v in ejemplos_duplicados.items()] + [""]
    L += ["- El Stretch del entrenamiento no coincide con el letterbox usado en",
          "  inferencia; además Ultralytics ya aplica aumentos al vuelo, por lo que",
          "  las 4 copias offline son en parte redundantes.",
          ""]

    args.reporte.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.reporte.write_text("\n".join(L), encoding="utf-8")
    args.json.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"reporte={seguro(args.reporte)}")
    print(f"json={seguro(args.json)}")
    print("resumen=" + json.dumps({
        "splits": dict(totales), "originales": datos["originales_totales"],
        "nitidez": nit, "instancias": {s: dict(c) for s, c in inst_por_split.items()},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
