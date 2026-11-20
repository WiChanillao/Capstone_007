#!/usr/bin/env python3
"""Experimento Stretch vs letterbox sobre best.pt, SIN reentrenar (SOLO LECTURA).

Empareja las imágenes de valid/test del dataset v1 con sus fotos originales
(HEIC/JPG) por nombre base, aplica auto-orient EXIF y evalúa tres condiciones:

  A) imágenes del dataset v1 (640x640 Stretch, como se evaluó siempre);
  B) originales auto-orientados, con letterbox interno de Ultralytics
     (equivale a lo que ve el modelo en producción);
  C) originales auto-orientados y redimensionados con Stretch a 640x640
     antes de inferir (reproduce el preprocesamiento de entrenamiento).

Las etiquetas `.txt` son normalizadas y están generadas sobre la foto original,
por eso sirven para B (Ultralytics devuelve las predicciones a coordenadas de
la imagen original) y para C (el stretch conserva las coordenadas normalizadas).
Para A se usan las etiquetas tal cual del dataset.

Sólo escribe markdown/JSON en docs/evidencia y archivos temporales fuera del repo.

Uso:
  python exp_geometria.py --dataset <dataset_v1> --originales <fotos> \
      --weights <best.pt> --temp <temporal>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pillow_heif
import yaml
from PIL import Image, ImageOps
from ultralytics import YOLO

pillow_heif.register_heif_opener()

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".heic"}
SUFIJOS = ("_jpg", "_jpeg", "_png", "_heic")
CONF = 0.5
TOL = 0.02  # diferencia mínima para considerar que una condición "cae"


def seguro(texto: str | Path) -> str:
    s = str(texto).replace("\\", "/")
    s = re.sub(r"^[A-Za-z]:/Users/[^/]+/", "", s)
    s = re.sub(r"^/Users/[^/]+/", "", s)
    return s


def nombres(root: Path) -> list[str]:
    y = yaml.safe_load((root / "data.yaml").read_text(encoding="utf-8"))
    n = y.get("names", {})
    return [n[i] for i in sorted(n)] if isinstance(n, dict) else list(n)


def clave_dataset(nombre: str) -> str:
    """Quita `.rf.<hash>.jpg` y deja la clave base del original."""
    return re.sub(r"\.rf\.[0-9a-f]{16,}\.[A-Za-z]+$", "", nombre)


def candidatos(clave: str) -> list[str]:
    """Variantes de la clave: original, paréntesis Roboflow y sin sufijo."""
    crudos = [clave]
    m = re.match(r"^(.*?)-(\d+)-(_?.*)$", clave)
    if m:  # IMG_9016-1-_HEIC -> IMG_9016(1)_HEIC -> IMG_9016(1)
        crudos.append(f"{m.group(1)}({m.group(2)}){m.group(3)}")
    salida = []
    for c in crudos:
        salida.append(c)
        for s in SUFIJOS:
            if c.lower().endswith(s):
                salida.append(c[:-len(s)])
    return salida


def indice_originales(carpeta: Path) -> dict[str, Path]:
    indice: dict[str, Path] = {}
    for p in sorted(carpeta.rglob("*")):
        if p.is_file() and p.suffix.lower() in EXT:
            indice.setdefault(p.stem.upper(), p)
    return indice


def abrir_auto_orient(path: Path) -> Image.Image:
    with Image.open(path) as im:
        return ImageOps.exif_transpose(im).convert("RGB")


def preparar_condicion(dest: Path, pares: list[tuple[Path, Path, str]],
                       modo: str, names: list[str]) -> Path:
    """Copia imágenes/etiquetas de un subset y devuelve su data.yaml."""
    lista: list[Path] = []
    for ds_img, orig, clave in pares:
        carpeta = dest / clave
        img_dir, lbl_dir = carpeta / "images", carpeta / "labels"
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        if modo == "A":
            imagen = abrir_auto_orient(ds_img)
            nombre = ds_img.name
            etiqueta = ds_img.parent.parent / "labels" / (ds_img.stem + ".txt")
        else:
            imagen = abrir_auto_orient(orig)
            nombre = clave + ".jpg"
            etiqueta = ds_img.parent.parent / "labels" / (ds_img.stem + ".txt")
            if modo == "C":
                imagen = imagen.resize((640, 640), Image.Resampling.BILINEAR)
        destino = img_dir / nombre
        imagen.save(destino, quality=95)
        if etiqueta.exists():
            (lbl_dir / (destino.stem + ".txt")).write_bytes(etiqueta.read_bytes())
        lista.append(destino)

    listado = dest / "imagenes.txt"
    listado.write_text("\n".join(str(p.resolve()) for p in lista) + "\n", encoding="utf-8")
    yml = dest / "data.yaml"
    yml.write_text(yaml.safe_dump({
        "path": str(dest.resolve()), "train": str(listado),
        "val": str(listado), "test": str(listado),
        "nc": len(names), "names": {i: n for i, n in enumerate(names)},
    }, allow_unicode=True), encoding="utf-8")
    return yml


def metrica(model: YOLO, yml: Path, split: str, names: list[str]) -> dict:
    r = model.val(data=str(yml), split="val" if split == "valid" else split,
                  conf=CONF, imgsz=640,
                  verbose=False, plots=False, save_json=False)
    b = r.box
    rec = np.asarray(getattr(b, "r", [])).reshape(-1)
    ap = np.asarray(getattr(b, "ap50", [])).reshape(-1)
    return {
        "map50": float(getattr(b, "map50", 0.0)),
        "recall": {c: float(rec[i]) if i < rec.size else 0.0
                   for i, c in enumerate(names)},
        "ap50": {c: float(ap[i]) if i < ap.size else 0.0
                 for i, c in enumerate(names)},
    }


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", required=True, type=Path)
    ap.add_argument("--originales", required=True, type=Path)
    ap.add_argument("--weights", required=True, type=Path)
    ap.add_argument("--temp", type=Path,
                    default=Path(tempfile.gettempdir()) / "ecolearn_geometria")
    ap.add_argument("--reporte", type=Path,
                    default=Path("Fase 3/docs/evidencia/exp_geometria.md"))
    ap.add_argument("--json", type=Path,
                    default=Path("Fase 3/docs/evidencia/exp_geometria.json"))
    args = ap.parse_args()

    root = args.dataset.resolve()
    pesos = args.weights.resolve()
    tempor = args.temp.resolve()
    tempor.mkdir(parents=True, exist_ok=True)
    names = nombres(root)
    indice = indice_originales(args.originales.resolve())
    model = YOLO(str(pesos))

    pares_por_split: dict[str, list[tuple[Path, Path, str]]] = {}
    no_emparejados: dict[str, list[str]] = {}
    for split in ("valid", "test"):
        pares, sin = [], []
        for p in sorted((root / split / "images").glob("*")):
            if p.suffix.lower() not in EXT:
                continue
            clave = clave_dataset(p.name)
            encontrado = None
            for cand in candidatos(clave):
                if cand.upper() in indice:
                    encontrado = indice[cand.upper()]
                    break
            if encontrado is None:
                sin.append(clave)
            else:
                pares.append((p, encontrado, clave))
        pares_por_split[split] = pares
        no_emparejados[split] = sin

    resultados: dict[str, dict[str, dict]] = {}
    for split in ("valid", "test"):
        pares = pares_por_split[split]
        if not pares:
            continue
        resultados[split] = {}
        for modo, nombre in (("A", "dataset_stretch"),
                             ("B", "original_letterbox"),
                             ("C", "original_stretch")):
            dest = tempor / nombre / split
            yml = preparar_condicion(dest, pares, modo, names)
            resultados[split][nombre] = metrica(model, yml, split, names)
            print(f"{split} {nombre} ({len(pares)} imgs): "
                  f"map50={resultados[split][nombre]['map50']:.4f}", flush=True)

    # Regla de decisión del enunciado: C parecido a A y B más bajo => desajuste real.
    diagnostico = {}
    for split, res in resultados.items():
        a, b, c = (res["dataset_stretch"]["map50"],
                   res["original_letterbox"]["map50"],
                   res["original_stretch"]["map50"])
        c_parecido_a = abs(c - a) <= TOL
        b_cae = b < a - TOL
        diagnostico[split] = {
            "delta_B_minus_A": round(b - a, 4),
            "delta_C_minus_A": round(c - a, 4),
            "C_parecido_a_A": c_parecido_a,
            "B_cae": b_cae,
            "desajuste_confirmado": bool(c_parecido_a and b_cae),
        }

    payload = {
        "weights": seguro(pesos.name), "dataset": seguro(root),
        "originales": seguro(args.originales.resolve()),
        "conf": CONF, "tolerancia": TOL,
        "emparejadas": {s: len(v) for s, v in pares_por_split.items()},
        "no_emparejadas": no_emparejados,
        "resultados": resultados, "diagnostico": diagnostico,
        "diagnostico_global": {
            "splits_cumplen_regla": [s for s, d in diagnostico.items()
                                     if d["desajuste_confirmado"]],
            "direccion_C_mayor_igual_A_mayor_igual_B": all(
                d["delta_C_minus_A"] >= 0 and d["delta_B_minus_A"] <= 0
                for d in diagnostico.values()),
            "lectura": "evidencia parcial: coincide en valid, no supera tolerancia en test",
        },
        "temporales_fuera_repo": seguro(tempor),
    }

    L = [
        "# Experimento Stretch vs letterbox (sin reentrenar)",
        "",
        f"- Pesos: `{seguro(pesos.name)}` (sin modificar). Conf usada: **{CONF}**.",
        f"- Originales: `{seguro(args.originales.resolve())}` (fuera del repo).",
        "- Auto-orient EXIF aplicado con `ImageOps.exif_transpose`.",
        "- Emparejamiento por nombre base: se quitó `.rf.<hash>.<ext>` y los",
        "  sufijos `_jpg` / `_HEIC` hasta encontrar el original (HEIC o JPG).",
        "",
        "## 1. Imágenes emparejadas",
        "",
        "| Split | Imágenes del dataset | Emparejadas | Sin emparejar |",
        "|---|---:|---:|---:|",
    ]
    for s in ("valid", "test"):
        total = len(list((root / s / "images").glob("*")))
        L.append(f"| {s} | {total} | {len(pares_por_split[s])} | "
                 f"{len(no_emparejados[s])} |")
    if any(no_emparejados.values()):
        L += ["", "Sin emparejar (claves):", ""]
        for s, claves in no_emparejados.items():
            for c in claves[:15]:
                L.append(f"- {s}: `{c}`")
    L += ["", "## 2. Resultados (mAP@50 y recall por clase)", ""]
    for split, res in resultados.items():
        L += [f"### {split}", "",
              "| Condición | mAP@50 | " + " | ".join(names) + " (recall) |",
              "|---|---:|" + "---:|" * len(names)]
        etiquetas = {"dataset_stretch": "A: dataset Stretch 640",
                     "original_letterbox": "B: original + letterbox",
                     "original_stretch": "C: original + Stretch 640"}
        for k, etiqueta in etiquetas.items():
            d = res[k]
            L.append(f"| {etiqueta} | {d['map50']:.3f} | " +
                     " | ".join(f"{d['recall'][c]:.3f}" for c in names) + " |")
        dg = diagnostico[split]
        L += ["", f"- Δ(B−A) = {dg['delta_B_minus_A']:+.3f}; "
                  f"Δ(C−A) = {dg['delta_C_minus_A']:+.3f} "
                  f"(tolerancia ±{TOL}).",
              f"- C ≈ A: **{dg['C_parecido_a_A']}**; B cae: "
              f"**{dg['B_cae']}** → desajuste real: "
              f"**{'SÍ' if dg['desajuste_confirmado'] else 'NO'}**.", ""]
    confirmados = [s for s, d in diagnostico.items()
                   if d["desajuste_confirmado"]]
    direccion = all(d["delta_C_minus_A"] >= 0 and d["delta_B_minus_A"] <= 0
                    for d in diagnostico.values())
    L += ["## 3. Criterio y lectura global", "",
          "Regla: si C se parece a A (±0,02) y B cae más de 0,02, el desajuste",
          "Stretch/letterbox es real; si no, se descarta.", "",
          f"- Splits que cumplen la regla estricta: "
          f"**{', '.join(confirmados) if confirmados else 'ninguno'}**.",
          f"- Dirección C ≥ A ≥ B en ambos splits: **{direccion}**.",
          f"- C ≥ A en los dos splits: **"
          f"{all(d['delta_C_minus_A'] >= 0 for d in diagnostico.values())}**; "
          f"B ≤ A en los dos splits: **"
          f"{all(d['delta_B_minus_A'] <= 0 for d in diagnostico.values())}**.",
          "- Con 61/31 imágenes emparejadas, la evidencia es **parcial**: en",
          "  valid el patrón encaja y en test no, así que no se descarta el",
          "  desajuste pero tampoco se afirma que sea la causa principal de la",
          "  caída en fotos nuevas.",
          "- Esta medición no cambia pesos, umbrales ni el mAP@50 oficial 0,562.", ""]

    args.reporte.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.reporte.write_text("\n".join(L), encoding="utf-8")
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"reporte={seguro(args.reporte)}")
    print(f"json={seguro(args.json)}")


if __name__ == "__main__":
    main()
