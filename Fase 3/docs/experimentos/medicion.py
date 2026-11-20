#!/usr/bin/env python3
"""Medición honesta de best.pt sobre el dataset v1 (SOLO LECTURA).

Evalúa:
  * test, valid, train_nitido (Laplaciano>100) y train_movido (<50)
    a conf 0,5 / 0,35 / 0,25 (+ 0,001 en test para comparar con el 0,562);
  * P/R/F1 por clase, mAP@50, mAP@50-95 y matriz de confusión;
  * curva F1 vs confianza en valid, umbral propuesto por clase y efecto en test;
  * 20 FN y 20 FP más confiados en test, agrupados por causa.

No modifica pesos, imágenes ni etiquetas. Escribe sólo markdown/JSON en
docs/evidencia y un caché de detecciones en un temporal fuera del repo.

Uso:
  python medicion.py --dataset <carpeta_con_data.yaml> --weights <best.pt> \
      --conf 0.5 0.35 0.25
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
import yaml
from ultralytics import YOLO

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
CLASES = ("Aluminio", "Carton", "Plastico")
LAP_MOVIDA, LAP_NITIDA = 50.0, 100.0
CONF_OFICIAL = 0.001


def seguro(texto: str | Path) -> str:
    s = str(texto).replace("\\", "/")
    s = re.sub(r"^[A-Za-z]:/Users/[^/]+/", "", s)
    s = re.sub(r"^/Users/[^/]+/", "", s)
    return s


def rel(path: Path, root: Path) -> str:
    try:
        return seguro(path.relative_to(root))
    except ValueError:
        return seguro(path.name)


def imagenes(carpeta: Path) -> list[Path]:
    if not carpeta.exists():
        return []
    return sorted(p for p in carpeta.rglob("*")
                  if p.is_file() and p.suffix.lower() in EXT)


def nombres(root: Path) -> list[str]:
    y = yaml.safe_load((root / "data.yaml").read_text(encoding="utf-8"))
    n = y.get("names", {})
    return [n[i] for i in sorted(n)] if isinstance(n, dict) else list(n)


def lap(path: Path) -> float:
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return float(cv2.Laplacian(im, cv2.CV_64F).var()) if im is not None else float("nan")


def senales_imagen(path: Path) -> dict:
    im = cv2.imread(str(path))
    if im is None:
        return {"lap": 0.0, "black": 0.0, "bloques": 0, "gray": 0.0}
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    negro = np.all(im <= 10, axis=2).astype(np.uint8)
    n, _, stats, _ = cv2.connectedComponentsWithStats(negro, 8)
    bloques = sum(1 for i in range(1, n)
                  if stats[i, 4] >= 3000 and stats[i, 2] >= 20
                  and stats[i, 3] >= 20
                  and stats[i, 4] / (stats[i, 2] * stats[i, 3]) >= 0.70)
    mm = im.max(axis=2).astype(np.int16) - im.min(axis=2).astype(np.int16)
    return {
        "lap": float(cv2.Laplacian(g, cv2.CV_64F).var()),
        "black": float(negro.mean()),
        "bloques": int(bloques),
        "gray": float((mm <= 4).mean()),
    }


def escribir_yaml_lista(dest: Path, paths: list[Path], names: list[str]) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    lista = dest / "imagenes.txt"
    lista.write_text("\n".join(str(p.resolve()) for p in paths) + "\n", encoding="utf-8")
    y = dest / "data.yaml"
    y.write_text(yaml.safe_dump({
        "path": str(dest), "train": str(lista), "val": str(lista),
        "test": str(lista), "nc": len(names),
        "names": {i: n for i, n in enumerate(names)},
    }, allow_unicode=True), encoding="utf-8")
    return y


def a_lista(x) -> np.ndarray:
    if x is None:
        return np.array([])
    try:
        return np.asarray(x).reshape(-1)
    except Exception:
        return np.array([])


def medir_val(model: YOLO, data: Path, split: str, conf: float) -> dict:
    r = model.val(data=str(data), split=split, conf=conf, imgsz=640,
                  verbose=False, plots=False, save_json=False)
    b = r.box
    p, rr = a_lista(getattr(b, "p", None)), a_lista(getattr(b, "r", None))
    ap50 = a_lista(getattr(b, "ap50", None))
    f1 = 2 * p * rr / (p + rr + 1e-9) if p.size and rr.size else np.array([])
    # La matriz de Ultralytics no se conserva con plots=False en esta versión;
    # se calcula aparte desde el caché de detecciones (ver matriz_confusion).
    cm = None
    return {
        "precision": float(getattr(b, "mp", 0.0)),
        "recall": float(getattr(b, "mr", 0.0)),
        "f1": float(np.mean(f1)) if f1.size else None,
        "map50": float(getattr(b, "map50", 0.0)),
        "map50_95": float(getattr(b, "map", 0.0)),
        "p_clase": p.tolist(), "r_clase": rr.tolist(),
        "f1_clase": f1.tolist(), "ap50_clase": ap50.tolist(),
        "confusion": cm,
    }


def gt_boxes(path: Path, names: list[str]) -> list[dict]:
    lbl = path.parent.parent / "labels" / (path.stem + ".txt")
    salida = []
    if not lbl.exists():
        return salida
    h = w = 640
    for linea in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
        q = linea.split()
        if len(q) < 5:
            continue
        try:
            cls = int(float(q[0]))
            vals = [float(v) for v in q[1:]]
        except ValueError:
            continue
        if len(vals) == 4:  # caja YOLO: xc, yc, ancho, alto (normalizado)
            xc, yc, bw, bh = vals
            box = [(xc - bw / 2) * w, (yc - bh / 2) * h,
                   (xc + bw / 2) * w, (yc + bh / 2) * h]
        else:  # polígono de segmentación: x1,y1,x2,y2,... (normalizado)
            if len(vals) < 6 or len(vals) % 2:
                continue
            xs, ys = vals[0::2], vals[1::2]
            box = [min(xs) * w, min(ys) * h, max(xs) * w, max(ys) * h]
        salida.append({"cls": cls, "box": box})
    return salida


def iou(a: list[float], b: list[float]) -> float:
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
    x2 = min(a[2], b[2]); y2 = min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def emparejar(dets: list[dict], gts: list[dict], cls: int | None,
              thr: float) -> tuple[list[dict], list[dict], list[dict]]:
    """Devuelve (detecciones emparejadas, sobrantes, GT sin emparejar)."""
    d = [x for x in dets if x["conf"] >= thr and (cls is None or x["cls"] == cls)]
    g = [x for x in gts if cls is None or x["cls"] == cls]
    usados = [False] * len(g)
    emparejadas = []
    for det in sorted(d, key=lambda z: -z["conf"]):
        mejor, mejor_iou = -1, 0.5
        for i, gt in enumerate(g):
            if usados[i]:
                continue
            v = iou(det["box"], gt["box"])
            if v > mejor_iou:
                mejor_iou, mejor = v, i
        if mejor >= 0:
            usados[mejor] = True
            emparejadas.append(det)
    ids_emp = {id(x) for x in emparejadas}
    sobrantes = [x for x in d if id(x) not in ids_emp]
    sin_gt = [gt for i, gt in enumerate(g) if not usados[i]]
    return emparejadas, sobrantes, sin_gt


def metricas_clase(items: list[dict], cls: int | None, thr: float) -> dict:
    emp, sobr, sin_gt = emparejar(
        items.get("dets", []), items.get("gts", []), cls, thr)
    tp, fp, fn = len(emp), len(sobr), len(sin_gt)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "p": p, "r": r,
            "f1": 2 * p * r / (p + r + 1e-9),
            "_emp": emp, "_sobr": sobr, "_sin_gt": sin_gt}


def matriz_confusion(items: list[dict], thr: float, n: int) -> list[list[int]]:
    """Matriz fila=real, columna=predicho; última fila/columna=fondo.

    Emparejamiento global por IoU>0,5 y mayor confianza, igual criterio que
    se usa para P/R/F1 en este script. Se calcula aquí porque la matriz de
    Ultralytics no se conserva con plots=False en esta versión.
    """
    cm = [[0] * (n + 1) for _ in range(n + 1)]
    for it in items:
        dets = [d for d in it["dets"] if d["conf"] >= thr]
        gts = it["gts"]
        usados = [False] * len(gts)
        emparejadas: set[int] = set()
        for det in sorted(dets, key=lambda z: -z["conf"]):
            mejor, mejor_iou = -1, 0.5
            for i, gt in enumerate(gts):
                if usados[i]:
                    continue
                v = iou(det["box"], gt["box"])
                if v > mejor_iou:
                    mejor_iou, mejor = v, i
            if mejor >= 0:
                usados[mejor] = True
                emparejadas.add(id(det))
                cm[gts[mejor]["cls"]][det["cls"]] += 1
        for i, gt in enumerate(gts):
            if not usados[i]:
                cm[gt["cls"]][n] += 1
        for det in dets:
            if id(det) not in emparejadas:
                cm[n][det["cls"]] += 1
    return cm


def ap50_desde(pares: list[tuple[float, int]], n_gt: int) -> float:
    """AP50 (101 puntos, interpolación COCO) desde pares (conf, es_tp)."""
    if not pares or n_gt == 0:
        return 0.0
    pares.sort(key=lambda z: -z[0])
    tp = fp = 0
    prec: list[float] = []
    rec: list[float] = []
    for _conf, es_tp in pares:
        tp += es_tp
        fp += 1 - es_tp
        prec.append(tp / (tp + fp))
        rec.append(tp / n_gt)
    sufijo = [0.0] * (len(prec) + 1)
    for i in range(len(prec) - 1, -1, -1):
        sufijo[i] = max(prec[i], sufijo[i + 1])
    ap = 0.0
    for j in range(101):
        k = bisect.bisect_left(rec, j / 100)
        ap += sufijo[k] if k < len(sufijo) else 0.0
    return ap / 101


def pares_por_imagen(items: list[dict], cls: int, thr: float
                     ) -> list[tuple[list[tuple[float, int]], int]]:
    """Pares (conf, es_tp) ya emparejados por IoU>0,5, una entrada por imagen."""
    salida = []
    for it in items:
        gts = [g for g in it["gts"] if g["cls"] == cls]
        usados = [False] * len(gts)
        arr: list[tuple[float, int]] = []
        for d in sorted((x for x in it["dets"]
                         if x["cls"] == cls and x["conf"] >= thr),
                        key=lambda z: -z["conf"]):
            mejor, mejor_iou = -1, 0.5
            for i, gt in enumerate(gts):
                if usados[i]:
                    continue
                v = iou(d["box"], gt["box"])
                if v > mejor_iou:
                    mejor_iou, mejor = v, i
            es_tp = mejor >= 0
            if es_tp:
                usados[mejor] = True
            arr.append((d["conf"], int(es_tp)))
        salida.append((arr, len(gts)))
    return salida


def bootstrap_ap50(items: list[dict], cls: int, thr: float,
                   n_boot: int = 1000, semilla: int = 42) -> dict:
    """AP50 por clase con IC 95 % bootstrap remuestreando imágenes."""
    por_img = pares_por_imagen(items, cls, thr)
    n_inst = sum(ng for _arr, ng in por_img)
    punto = ap50_desde([p for arr, _ in por_img for p in arr], n_inst)
    if not por_img or n_inst == 0:
        return {"ap50": punto, "ic95": [punto, punto], "n_instancias": n_inst}
    rng = np.random.default_rng(semilla)
    valores = []
    n = len(por_img)
    for _ in range(n_boot):
        eleitas = rng.integers(0, n, size=n)
        pares: list[tuple[float, int]] = []
        total_gt = 0
        for k in eleitas:
            arr, ng = por_img[k]
            pares.extend(arr)
            total_gt += ng
        valores.append(ap50_desde(pares, total_gt))
    lo, hi = np.percentile(valores, [2.5, 97.5])
    return {"ap50": punto, "ic95": [float(lo), float(hi)],
            "n_imagenes": n, "n_instancias": n_inst,
            "n_boot": n_boot, "semilla": semilla}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    ph = k / n
    den = 1 + z * z / n
    ctr = (ph + z * z / (2 * n)) / den
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (max(0.0, ctr - half), min(1.0, ctr + half))


def causa(item: dict, senal: dict, es_fp: bool) -> str:
    if senal["lap"] < LAP_MOVIDA:
        return "desenfoque / movido (Laplaciano<50)"
    if senal["bloques"] >= 1:
        return "cutout (bloque negro)"
    if senal["gray"] > 0.5:
        return "grayscale"
    area = (item["box"][2] - item["box"][0]) * (item["box"][3] - item["box"][1])
    if area < 8000:
        return "objeto pequeño"
    if area > 250000:
        return "escena completa / tamaño"
    return "revisar: fondo / reflejo / transparencia / oclusión"


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", required=True, type=Path)
    ap.add_argument("--weights", type=Path, default=Path("Fase 3/ecoscan-backend/best.pt"))
    ap.add_argument("--conf", nargs="+", type=float, default=[0.5, 0.35, 0.25])
    ap.add_argument("--reporte", type=Path,
                    default=Path("Fase 3/docs/evidencia/medicion_generalizacion.md"))
    ap.add_argument("--json", type=Path,
                    default=Path("Fase 3/docs/evidencia/medicion_generalizacion.json"))
    ap.add_argument("--temp", type=Path,
                    default=Path(tempfile.gettempdir()) / "ecolearn_medicion")
    args = ap.parse_args()

    root = args.dataset.resolve()
    pesos = args.weights.resolve()
    names = nombres(root)
    if not pesos.exists():
        raise SystemExit(f"No existen los pesos: {seguro(pesos)}")
    temp = args.temp.resolve()
    temp.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(pesos))

    train = imagenes(root / "train/images")
    subsets: dict[str, list[Path]] = {
        "train_nitido": [p for p in train if lap(p) > LAP_NITIDA],
        "train_movido": [p for p in train if lap(p) < LAP_MOVIDA],
        "valid": imagenes(root / "valid/images"),
        "test": imagenes(root / "test/images"),
    }
    yamls: dict[str, Path] = {}
    for s in ("train_nitido", "train_movido"):
        yamls[s] = escribir_yaml_lista(temp / s, subsets[s], names)
    yamls["valid"] = root / "data.yaml"
    yamls["test"] = root / "data.yaml"
    splits = {"train_nitido": "val", "train_movido": "val",
              "valid": "val", "test": "test"}

    confs = list(dict.fromkeys(args.conf + [CONF_OFICIAL]))
    resultados: dict[str, dict[float, dict]] = {}
    for c in confs:
        resultados[c] = {}
        for s, paths in subsets.items():
            if c == CONF_OFICIAL and s != "test":
                continue
            resultados[c][s] = medir_val(model, yamls[s], splits[s], c)
            print(f"val {s} conf={c}: map50={resultados[c][s]['map50']:.4f}", flush=True)

    # --- Caché de detecciones para curvas, umbrales y errores ---
    cache_path = temp / "detecciones.json"
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        print("usando caché de detecciones", flush=True)
    else:
        cache = {}
        todas = []
        for paths in subsets.values():
            todas.extend(paths)
        for i, p in enumerate(todas):
            r = model.predict(source=p, imgsz=640, conf=0.01, verbose=False)[0]
            dets = []
            for b in r.boxes:
                x1, y1, x2, y2 = [float(v) for v in b.xyxy[0].tolist()]
                dets.append({"cls": int(b.cls[0]), "conf": float(b.conf[0]),
                             "box": [x1, y1, x2, y2]})
            cache[str(p)] = dets
            if (i + 1) % 100 == 0:
                print(f"detectadas {i+1}/{len(todas)}", flush=True)
        cache_path.write_text(json.dumps(cache), encoding="utf-8")

    items_por_subset: dict[str, list[dict]] = {}
    for s, paths in subsets.items():
        items_por_subset[s] = []
        for p in paths:
            items_por_subset[s].append({
                "path": p,
                "dets": cache.get(str(p), []),
                "gts": gt_boxes(p, names),
                "senal": senales_imagen(p),
            })

    # --- Curva F1 vs confianza en valid ---
    def f1_global(items: list[dict], cls: int, thr: float) -> float:
        """F1 global acumulando TP/FP/FN, no media por imagen."""
        tp = fp = fn = 0
        for it in items:
            m = metricas_clase(it, cls, thr)
            tp += m["tp"]
            fp += m["fp"]
            fn += m["fn"]
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        return 2 * p * r / (p + r + 1e-9)

    curva: dict[float, dict[str, float]] = {}
    for i in range(1, 20):
        thr = round(i * 0.05, 2)
        fila = {}
        for cidx, cname in enumerate(names):
            fila[cname] = f1_global(items_por_subset["valid"], cidx, thr)
        curva[thr] = fila
    propuestos = {c: max(curva, key=lambda t: curva[t][c]) for c in names}

    # --- Efecto en test: global 0,5 vs umbrales propuestos ---
    def resumen_test(thrs: dict[str, float]) -> dict:
        salida = {}
        for cidx, cname in enumerate(names):
            tp = fp = fn = 0
            for it in items_por_subset["test"]:
                m = metricas_clase(it, cidx, thrs[cname])
                tp += m["tp"]; fp += m["fp"]; fn += m["fn"]
            p = tp / (tp + fp) if tp + fp else 0.0
            r = tp / (tp + fn) if tp + fn else 0.0
            salida[cname] = {"tp": tp, "fp": fp, "fn": fn, "p": p, "r": r,
                             "f1": 2 * p * r / (p + r + 1e-9)}
        return salida

    globales = {c: 0.5 for c in names}
    efecto = {"global_0.5": resumen_test(globales),
              "por_clase": resumen_test(propuestos)}

    # --- Top FN/FP en test a conf=0,5 ---
    falsos_neg: list[dict] = []
    falsos_pos: list[dict] = []
    for it in items_por_subset["test"]:
        for cidx, cname in enumerate(names):
            m = metricas_clase(it, cidx, 0.5)
            for gt in m["_sin_gt"]:
                conf_modelo = max([d["conf"] for d in it["dets"]], default=0.0)
                falsos_neg.append({
                    "archivo": rel(it["path"], root), "real": cname,
                    "conf": conf_modelo, "causa": causa(gt, it["senal"], False),
                    "lap": round(it["senal"]["lap"], 1),
                })
            for det in m["_sobr"]:
                falsos_pos.append({
                    "archivo": rel(it["path"], root), "pred": cname,
                    "conf": det["conf"], "causa": causa(det, it["senal"], True),
                    "lap": round(it["senal"]["lap"], 1),
                })
    falsos_neg.sort(key=lambda z: -z["conf"])
    falsos_pos.sort(key=lambda z: -z["conf"])

    # IC de Wilson para Aluminio en test (8 instancias).
    alu = efecto["global_0.5"]["Aluminio"]
    icRecall = wilson(alu["tp"], alu["tp"] + alu["fn"])
    icPrecision = wilson(alu["tp"], alu["tp"] + alu["fp"])

    # --- IC 95 % bootstrap del AP50 por clase (conf=0,50) ---
    bootstrap = {
        "conf": 0.5,
        "piso_cache_conf": 0.01,
        "subsets": {
            s: {cn: bootstrap_ap50(items_por_subset[s], i, 0.5)
                for i, cn in enumerate(names)}
            for s in ("valid", "test")
        },
    }

    payload = {
        "weights": seguro(pesos.name), "dataset": seguro(root),
        "confs": confs, "subsets": {s: len(v) for s, v in subsets.items()},
        "resultados": resultados,
        "confusion_calc": {
            str(c): {s: matriz_confusion(items_por_subset[s], c, len(names))
                     for s in subsets}
            for c in args.conf
        },
        "curva_f1_valid": curva,
        "umbrales_propuestos": propuestos, "efecto_test": efecto,
        "fn_top": falsos_neg[:20], "fp_top": falsos_pos[:20],
        "ic_aluminio_test": {"recall_95": icRecall, "precision_95": icPrecision,
                             "n_instancias": alu["tp"] + alu["fn"]},
        "bootstrap_ap50": bootstrap,
    }

    # --- Reporte markdown ---
    L = [
        "# Medición de `best.pt` con el dataset v1 (generada por `medicion.py`)",
        "",
        f"- Pesos: `{seguro(pesos.name)}` (sin modificar).",
        f"- Dataset: `{seguro(root)}` (fuera del repo).",
        "- Subsets: " + ", ".join(f"{s}={len(v)}" for s, v in subsets.items()) + ".",
        "- conf evaluados: " + ", ".join(str(c) for c in args.conf) +
        f"; además {CONF_OFICIAL} en test para comparar con el oficial.",
        "- Las etiquetas `.txt` son **polígonos de segmentación**; `val()` de",
        "  Ultralytics usa la caja envolvente. Para P/R/F1 propios se",
        "  reconstruye esa misma envolvente desde el polígono.",
        "",
        "## 1. Métricas globales",
        "",
        "| conf | subset | P | R | F1 | mAP@50 | mAP@50-95 |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    orden = ["test", "valid", "train_nitido", "train_movido"]
    for c in confs:
        for s in orden:
            d = resultados[c].get(s)
            if not d:
                continue
            L.append(f"| {c} | {s} | {d['precision']:.3f} | {d['recall']:.3f} | "
                     f"{d['f1']:.3f} | {d['map50']:.3f} | {d['map50_95']:.3f} |")

    L += ["", "### Comparación con el mAP@50 oficial 0,562", ""]
    base = resultados[CONF_OFICIAL]["test"]["map50"]
    L += [
        f"- `val()` en test con conf por defecto ({CONF_OFICIAL}): **{base:.3f}**.",
        "- El 0,562 oficial procede de `val()` con ajustes por defecto; el",
        "  `conf` no es el umbral de decisión del backend (0,50). Al subir",
        "  `conf` a 0,50/0,35/0,25 el mAP@50 calculado baja porque se descartan",
        "  detecciones de baja confianza antes de calcular la curva P-R. Eso",
        "  **no contradice** la métrica oficial: es otro punto de operación.",
        "- train_nitido y train_movido no son el conjunto de validación: son",
        "  particiones artificiales de train y sólo sirven para diagnosticar.",
        "",
        "## 2. Métricas por clase",
        "",
        "| conf | subset | clase | P | R | F1 | AP50 |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for c in confs:
        for s in orden:
            d = resultados[c].get(s)
            if not d:
                continue
            for i, cn in enumerate(names):
                p = d["p_clase"][i] if i < len(d["p_clase"]) else float("nan")
                r = d["r_clase"][i] if i < len(d["r_clase"]) else float("nan")
                f = d["f1_clase"][i] if i < len(d["f1_clase"]) else float("nan")
                a = d["ap50_clase"][i] if i < len(d["ap50_clase"]) else float("nan")
                L.append(f"| {c} | {s} | {cn} | {p:.3f} | {r:.3f} | {f:.3f} | {a:.3f} |")

    L += ["", "## 2b. IC 95 % bootstrap del AP50 por clase (conf=0,50)", "",
          "Remuestreo de **imágenes con reposición**, 1000 réplicas, semilla 42.",
          "AP50 con 101 puntos e interpolación COCO sobre el caché de",
          "detecciones (piso de conf=0,01; no afecta al punto de operación 0,50).",
          "El AP50 puntual puede diferir del `ap50_clase` de `val()` por el",
          "criterio de emparejamiento; compárense sólo los valores de esta tabla.",
          "",
          "| subset | clase | AP50 | IC 95 % | instancias | lectura |",
          "|---|---|---:|---|---:|---|"]
    for s in ("valid", "test"):
        for cn in names:
            b = bootstrap["subsets"][s][cn]
            nota = ("NO CONCLUYENTE (sólo "
                    f"{b['n_instancias']} instancias)" if s == "test" and
                    b["n_instancias"] < 10 else "")
            L.append(f"| {s} | {cn} | {b['ap50']:.3f} | "
                     f"[{b['ic95'][0]:.3f} ; {b['ic95'][1]:.3f}] | "
                     f"{b['n_instancias']} | {nota} |")
    L += ["", "Aluminio en test tiene 8 instancias: una sola detección mueve",
          "el resultado 12,5 puntos. Su intervalo es amplio y **no permite",
          "elegir umbral ni afirmar superioridad** frente a las otras clases.",
          ""]

    L += ["", "## 3. Matrices de confusión (filas=real, columnas=predicho)", "",
          "Calculadas del caché de detecciones con IoU>0,5 y emparejamiento",
          "por confianza; última fila/columna = fondo.", ""]
    for c in args.conf:
        for s in orden:
            cm = payload["confusion_calc"][str(c)][s]
            L += [f"- conf={c}, {s}:"]
            L += ["", "| | " + " | ".join(names + ["fondo"]) + " |",
                  "|---|" + "---:|" * (len(names) + 1)]
            for i, fila in enumerate(cm):
                etiqueta = names[i] if i < len(names) else "fondo"
                L.append(f"| {etiqueta} | " +
                         " | ".join(str(int(v)) for v in fila) + " |")
            L.append("")

    L += ["## 4. Curva F1 vs confianza en valid", "",
          "F1 global (TP/FP/FN acumulados en todas las imágenes), no media",
          "por imagen.", "",
          "| conf | " + " | ".join(names) + " |", "|---:|" + "---:|" * len(names)]
    for t, fila in curva.items():
        L.append(f"| {t:.2f} | " + " | ".join(f"{fila[c]:.3f}" for c in names) + " |")
    L += ["", "Umbrales propuestos por clase (máximo F1 en valid):", ""]
    for c in names:
        L.append(f"- {c}: **{propuestos[c]:.2f}** (F1={curva[propuestos[c]][c]:.3f}).")
    L += ["", "### Efecto en test (sólo reporte; NO aplicado al backend)", "",
          "| configuración | clase | TP | FP | FN | P | R | F1 |",
          "|---|---|---:|---:|---:|---:|---:|---:|"]
    for cfg, datos in efecto.items():
        for cn in names:
            d = datos[cn]
            L.append(f"| {cfg} | {cn} | {d['tp']} | {d['fp']} | {d['fn']} | "
                     f"{d['p']:.3f} | {d['r']:.3f} | {d['f1']:.3f} |")
    L += [
        "",
        f"**Inestabilidad de Aluminio en test:** sólo {alu['tp']+alu['fn']} instancias.",
        f"Recall {alu['r']:.3f}, IC 95 % Wilson [{icRecall[0]:.3f}, {icRecall[1]:.3f}];",
        f"precision {alu['p']:.3f}, IC 95 % [{icPrecision[0]:.3f}, {icPrecision[1]:.3f}].",
        "Cualquier diferencia de una sola instancia cambia el resultado; no se",
        "debe elegir umbral definitivo con este tamaño de muestra.",
        "",
        "## 5. 20 falsos negativos más confiados (test, conf=0,5)",
        "",
        "| archivo | real | conf | causa | Laplaciano |",
        "|---|---|---:|---|---:|",
    ]
    for z in falsos_neg[:20]:
        L.append(f"| `{z['archivo']}` | {z['real']} | {z['conf']:.2f} | "
                 f"{z['causa']} | {z['lap']:.1f} |")
    L += ["", "## 6. 20 falsos positivos más confiados (test, conf=0,5)", "",
          "| archivo | predicho | conf | causa | Laplaciano |",
          "|---|---|---:|---|---:|"]
    for z in falsos_pos[:20]:
        L.append(f"| `{z['archivo']}` | {z['pred']} | {z['conf']:.2f} | "
                 f"{z['causa']} | {z['lap']:.1f} |")
    L += ["", "Las causas son **heurísticas automáticas**; requieren revisión visual.", ""]

    args.reporte.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.reporte.write_text("\n".join(L), encoding="utf-8")
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"reporte={seguro(args.reporte)}")
    print(f"json={seguro(args.json)}")
    print(f"cache={seguro(cache_path)} (fuera del repo)")


if __name__ == "__main__":
    main()
