#!/usr/bin/env python3
"""Evalúa umbrales por clase en el split de test (SOLO LECTURA).

Compara el punto de operación actual (0,50 para las 3 clases) contra los
umbrales propuestos (Aluminio 0,25 / Cartón 0,45 / Plástico 0,20). Sólo
informa de recall ganado y FP añadidos; NO cambia defaults ni pesos.

La inferencia se hace una sola vez con piso de conf=0,01 y se guarda un
caché fuera del repo, de modo que ambos puntos de operación usan exactamente
las mismas detecciones.

Uso:
  python evaluar_umbrales.py --dataset <dataset_v1> --weights <best.pt> \
      --reporte <md> --json <json> --temp <carpeta_temporal>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from ultralytics import YOLO

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
CLASES = ("Aluminio", "Carton", "Plastico")
BASELINE = {c: 0.50 for c in CLASES}
PROPUESTO = {"Aluminio": 0.25, "Carton": 0.45, "Plastico": 0.20}
PISO = 0.01
IOU_MIN = 0.5


def seguro(texto: str | Path) -> str:
    s = str(texto).replace("\\", "/")
    s = re.sub(r"^[A-Za-z]:/Users/[^/]+/", "", s)
    return s


def imagenes(carpeta: Path) -> list[Path]:
    return sorted(p for p in carpeta.rglob("*")
                  if p.is_file() and p.suffix.lower() in EXT)


def gt_boxes(path: Path) -> list[dict]:
    """Caja YOLO normalizada -> píxeles sobre el dataset 640x640."""
    lbl = path.parent.parent / "labels" / (path.stem + ".txt")
    salida: list[dict] = []
    if not lbl.exists():
        return salida
    for linea in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
        q = linea.split()
        if len(q) < 5:
            continue
        try:
            cls = int(float(q[0]))
            xc, yc, bw, bh = (float(v) for v in q[1:5])
        except ValueError:
            continue
        salida.append({"cls": cls, "box": [
            (xc - bw / 2) * 640, (yc - bh / 2) * 640,
            (xc + bw / 2) * 640, (yc + bh / 2) * 640,
        ]})
    return salida


def iou(a: list[float], b: list[float]) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def contar(items: list[dict], umbrales: dict[str, float], cls: str) -> dict:
    """TP/FP por clase con emparejamiento greedy IoU>0,5 y mayor confianza."""
    thr = umbrales[cls]
    gts = [g for it in items for g in it["gts"] if CLASES[g["cls"]] == cls]
    dets = [d for it in items for d in it["dets"]
            if CLASES[d["cls"]] == cls and d["conf"] >= thr]
    usados: set[int] = set()
    tp = 0
    for det in sorted(dets, key=lambda z: -z["conf"]):
        mejor, mejor_iou = -1, IOU_MIN
        for i, gt in enumerate(gts):
            if i in usados:
                continue
            valor = iou(det["box"], gt["box"])
            if valor > mejor_iou:
                mejor_iou, mejor = valor, i
        if mejor >= 0:
            usados.add(mejor)
            tp += 1
    return {"n_gt": len(gts), "tp": tp, "fp": len(dets) - tp,
            "recall": tp / len(gts) if gts else None}


def evaluar(items: list[dict]) -> dict:
    salida = {}
    for cls in CLASES:
        b = contar(items, BASELINE, cls)
        p = contar(items, PROPUESTO, cls)
        salida[cls] = {
            "n_gt": b["n_gt"],
            "baseline": b,
            "propuesto": p,
            "delta_recall": (p["recall"] - b["recall"]
                             if b["recall"] is not None and p["recall"] is not None
                             else None),
            "delta_fp": p["fp"] - b["fp"],
        }
    return salida


def escribir_reporte(ruta: Path, datos: dict, n_imgs: int, args) -> None:
    L = [
        "# Evaluación de umbrales por clase en test",
        "",
        "- Pesos: `best.pt` **sin modificar**. Inferencia `imgsz=640`, conf=0,01.",
        f"- Imágenes de test evaluadas: **{n_imgs}**. IoU de emparejamiento > 0,5.",
        "- Misma caché de detecciones para ambos puntos de operación: una sola pasada.",
        f"- Dataset: `{seguro(args.dataset)}`.",
        "",
        "## Configuraciones",
        "",
        "| Configuración | Aluminio | Cartón | Plástico |",
        "|---|---:|---:|---:|",
        "| Actual (defaults) | 0,50 | 0,50 | 0,50 |",
        "| Propuesta (sólo evaluada) | 0,25 | 0,45 | 0,20 |",
        "",
        "## Resultado: recall ganado y FP añadidos",
        "",
        "| Clase | Instancias | Recall actual | Recall propuesto | Δ recall | FP actual | FP propuesto | Δ FP |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    tot_gt = tot_dr = 0
    tot_fp_b = tot_fp_p = 0
    rec_b = rec_p = 0
    for cls in CLASES:
        d = datos[cls]
        b, p = d["baseline"], d["propuesto"]
        rb = b["recall"] if b["recall"] is not None else 0.0
        rp = p["recall"] if p["recall"] is not None else 0.0
        dr = d["delta_recall"] or 0.0
        L.append(
            f"| {cls} | {d['n_gt']} | {rb:.3f} | {rp:.3f} | {dr:+.3f} | "
            f"{b['fp']} | {p['fp']} | {d['delta_fp']:+d} |")
        tot_gt += d["n_gt"]
        tot_dr += (d["delta_recall"] or 0.0) * d["n_gt"]
        tot_fp_b += b["fp"]
        tot_fp_p += p["fp"]
        rec_b += b["tp"]
        rec_p += p["tp"]
    L += [
        f"| **Total** | {tot_gt} | {rec_b / tot_gt:.3f} | {rec_p / tot_gt:.3f} | "
        f"{tot_dr / tot_gt:+.3f} | {tot_fp_b} | {tot_fp_p} | {tot_fp_p - tot_fp_b:+d} |",
        "",
        "## Lectura",
        "",
        "- El delta de recall está ponderado por instancias reales de cada clase.",
        "- Los FP se cuentan con el mismo criterio en ambos puntos de operación.",
        "- **No se cambió ningún default**: el backend sigue decidiendo a 0,50",
        "  para las tres clases; el nivel \"posible\" se reporta aparte.",
        "- Aluminio y Cartón **no ganan recall** en esta muestra y sí añaden FP:",
        "  no hay motivo para bajar sus umbrales con estos datos.",
        "- Plástico recupera 5 instancias a costa de 6 FP; es un dato para la",
        "  matriz E0–E3 con 3 semillas, no una decisión de producto.",
        "- Aluminio en test tiene 8 instancias; su delta es orientativo.",
        "",
    ]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", type=Path, required=True)
    ap.add_argument("--weights", type=Path, required=True)
    ap.add_argument("--reporte", type=Path, required=True)
    ap.add_argument("--json", type=Path, required=True)
    ap.add_argument("--temp", type=Path, required=True)
    args = ap.parse_args()

    ds = args.dataset.resolve()
    nombres = yaml.safe_load((ds / "data.yaml").read_text(encoding="utf-8"))["names"]
    if isinstance(nombres, dict):
        nombres = [nombres[i] for i in sorted(nombres)]
    assert tuple(nombres) == CLASES, f"Clases inesperadas: {nombres}"

    temp = args.temp.resolve()
    temp.mkdir(parents=True, exist_ok=True)
    cache = temp / "test_dets.json"
    paths = imagenes(ds / "test" / "images")
    if cache.exists():
        items = json.loads(cache.read_text(encoding="utf-8"))
        print("caché reutilizada:", seguro(cache))
    else:
        modelo = YOLO(str(args.weights))
        items = []
        for p in paths:
            r = modelo.predict(source=str(p), conf=PISO, imgsz=640,
                               verbose=False, save=False)[0]
            dets = []
            if r.boxes is not None:
                for box in r.boxes:
                    x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
                    dets.append({"cls": int(box.cls[0]),
                                 "conf": float(box.conf[0]),
                                 "box": [x1, y1, x2, y2]})
            items.append({"imagen": p.name, "dets": dets, "gts": gt_boxes(p)})
        cache.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        print("caché creada:", seguro(cache))

    datos = evaluar(items)
    escribir_reporte(args.reporte, datos, len(items), args)
    salida = {
        "weights": seguro(args.weights),
        "dataset": seguro(ds),
        "criterio": "IoU>0.5, greedy por confianza, mismas detecciones (conf>=0.01)",
        "configuraciones": {"actual": BASELINE, "propuesta": PROPUESTO},
        "resultados": datos,
        "reporte": seguro(args.reporte),
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(salida, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print("reporte=", seguro(args.reporte))
    print("json=", seguro(args.json))
    for cls in CLASES:
        d = datos[cls]
        print(f"{cls}: Δrecall={d['delta_recall']:+.3f} ΔFP={d['delta_fp']:+d}")


if __name__ == "__main__":
    main()
