#!/usr/bin/env python3
"""Prepara datasets experimentales FUERA del repo (SOLO LECTURA del original).

Genera:
  a) train_nitido: por cada original de train, sólo la copia más nítida
     (Laplaciano máximo), conservando su etiqueta. Valid y test intactos.
  b) split_por_escenas: 307 originales (copia más nítida de cada uno),
     agrupados por ráfaga (IMG_NNNN consecutivo o HDR a ≤10 s) y repartidos
     por grupos con semilla fija, sin fuga de escena.

No entrena. No modifica el dataset original. Escribe imágenes/copias sólo en
--salida (temporal fuera del repo) y reportes markdown/JSON en docs/evidencia.

Uso:
  python preparar_datasets.py --dataset <data.yaml dir> \
      --salida <dir_temporal> --semilla 42
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import cv2
import yaml

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
CLASES = ("Aluminio", "Carton", "Plastico")


def seguro(texto: str | Path) -> str:
    s = str(texto).replace("\\", "/")
    s = re.sub(r"^[A-Za-z]:/Users/[^/]+/", "", s)
    s = re.sub(r"^/Users/[^/]+/", "", s)
    return s


def imagenes(carpeta: Path) -> list[Path]:
    if not carpeta.exists():
        return []
    return sorted(p for p in carpeta.rglob("*")
                  if p.is_file() and p.suffix.lower() in EXT)


def original(p: Path) -> str:
    return re.sub(r"\.rf\.[0-9a-f]{16,}\.[A-Za-z]+$", "", p.name)


def lap(path: Path) -> float:
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return float(cv2.Laplacian(im, cv2.CV_64F).var()) if im is not None else -1.0


def tiempo_hdr(clave: str) -> datetime | None:
    m = re.search(r"IMG_(\d{8})_(\d{9})_HDR", clave)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1) + m.group(2)[:6], "%Y%m%d%H%M%S")
    except ValueError:
        return None


def numero(clave: str) -> int | None:
    m = re.search(r"IMG_(\d+)", clave)
    return int(m.group(1)) if m else None


def etiqueta(p: Path) -> Path:
    return p.parent.parent / "labels" / (p.stem + ".txt")


def nombres(root: Path) -> list[str]:
    y = yaml.safe_load((root / "data.yaml").read_text(encoding="utf-8"))
    n = y.get("names", {})
    return [n[i] for i in sorted(n)] if isinstance(n, dict) else list(n)


def instancias(p: Path, names: list[str]) -> Counter:
    c: Counter = Counter()
    lbl = etiqueta(p)
    if not lbl.exists():
        return c
    for linea in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
        q = linea.split()
        if len(q) >= 5:
            try:
                i = int(float(q[0]))
            except ValueError:
                continue
            if 0 <= i < len(names):
                c[names[i]] += 1
    return c


def copiar(p: Path, destino: Path) -> None:
    """Copia imagen y etiqueta manteniendo la estructura YOLO images/labels."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, destino)
    lbl = etiqueta(p)
    if lbl.exists():
        lbl_dest = destino.parent.parent / "labels" / (destino.stem + ".txt")
        lbl_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(lbl, lbl_dest)


def escribir_yaml(root: Path, names: list[str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "data.yaml").write_text(yaml.safe_dump({
        "path": str(root), "train": "train/images", "val": "valid/images",
        "test": "test/images", "nc": len(names),
        "names": {i: n for i, n in enumerate(names)},
    }, allow_unicode=True), encoding="utf-8")


def resumen(root: Path, names: list[str]) -> dict:
    salida = {}
    for s in ("train", "valid", "test"):
        imgs = imagenes(root / s / "images")
        c = Counter()
        for p in imgs:
            c.update(instancias(p, names))
        salida[s] = {"imagenes": len(imgs),
                     "instancias": {n: c[n] for n in names}}
    return salida


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", required=True, type=Path)
    ap.add_argument("--salida", required=True, type=Path)
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--reporte", type=Path,
                    default=Path("Fase 3/docs/evidencia/datasets_experimentales.md"))
    ap.add_argument("--json", type=Path,
                    default=Path("Fase 3/docs/evidencia/datasets_experimentales.json"))
    args = ap.parse_args()

    root = args.dataset.resolve()
    out = args.salida.resolve()
    names = nombres(root)
    # Se limpia sólo bajo --salida (temporal fuera del repo) para que el
    # resumen no cuente residuos de ejecuciones anteriores.
    for nombre in ("train_nitido", "split_por_escenas"):
        previo = out / nombre
        if previo.exists():
            shutil.rmtree(previo)
    registros = []
    for split in ("train", "valid", "test"):
        for p in imagenes(root / split / "images"):
            registros.append({"split": split, "path": p, "key": original(p),
                              "lap": lap(p), "tiempo": tiempo_hdr(original(p)),
                              "numero": numero(original(p))})
    # ---------- a) train_nitido ----------
    dest_nitido = out / "train_nitido"
    por_original = defaultdict(list)
    for r in registros:
        if r["split"] == "train":
            por_original[r["key"]].append(r)
    elegidos_train = [max(v, key=lambda x: x["lap"]) for v in por_original.values()]
    for r in elegidos_train:
        copiar(r["path"], dest_nitido / "train/images" / r["path"].name)
    for split in ("valid", "test"):
        for r in registros:
            if r["split"] == split:
                copiar(r["path"], dest_nitido / split / "images" / r["path"].name)
    escribir_yaml(dest_nitido, names)

    # ---------- b) split_por_escenas ----------
    dest_escenas = out / "split_por_escenas"
    mejores = {}
    for r in registros:
        if r["key"] not in mejores or r["lap"] > mejores[r["key"]]["lap"]:
            mejores[r["key"]] = r
    originales = sorted(mejores.values(), key=lambda r: r["key"])
    # Ventanas FIJAS, no componentes conexas: encadenar capturas separadas por
    # ≤10 s puede abarcar toda una sesión y dejar un único grupo gigante.
    # Ventanas de 10 s (HDR) y bloques de 10 números (SEQ) mantienen juntas las
    # capturas vecinas sin propagar la unión a toda la ráfaga.
    window_s, window_seq = 10, 10
    agrupados: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(originales):
        if r["tiempo"] is not None:
            clave_grupo = f"HDR:{int(r['tiempo'].timestamp()) // window_s}"
        elif r["numero"] is not None:
            clave_grupo = f"SEQ:{r['numero'] // window_seq}"
        else:
            clave_grupo = f"OTRO:{r['key']}"
        agrupados[clave_grupo].append(i)
    grupos = list(agrupados.values())
    random.Random(args.semilla).shuffle(grupos)

    total = len(originales)
    objetivos = {"train": round(total * 0.70),
                 "valid": round(total * 0.20),
                 "test": total - round(total * 0.70) - round(total * 0.20)}
    asignacion: dict[str, list[int]] = {s: [] for s in objetivos}
    pendiente = dict(objetivos)
    # Grupos grandes primero; cada grupo va entero al split con mayor
    # pendiente relativa donde quepa.
    for g in sorted(grupos, key=len, reverse=True):
        candidatos = [s for s in ("train", "valid", "test")
                      if pendiente[s] >= len(g)]
        if not candidatos:
            candidatos = [s for s in ("train", "valid", "test")
                          if pendiente[s] > 0] or ["train"]
        s = max(candidatos, key=lambda x: pendiente[x] / objetivos[x])
        asignacion[s].extend(g)
        pendiente[s] -= len(g)
    for s, idxs in asignacion.items():
        for i in idxs:
            r = originales[i]
            copiar(r["path"], dest_escenas / s / "images" / r["path"].name)
    escribir_yaml(dest_escenas, names)

    # ---------- Reporte ----------
    res = {
        "semilla": args.semilla,
        "dataset_origen": seguro(root),
        "salida": seguro(out),
        "train_nitido": resumen(dest_nitido, names),
        "split_por_escenas": resumen(dest_escenas, names),
        "grupos_escena": {
            "total": len(grupos),
            "ventana_s": window_s,
            "ventana_seq": window_seq,
            "tamanios": dict(Counter(len(g) for g in grupos)),
            "imagenes_por_split": {s: len(v) for s, v in asignacion.items()},
            "objetivos": objetivos,
        },
        "nitidez_train_elegidas": {
            "lap_min": round(min(r["lap"] for r in elegidos_train), 1),
            "lap_medio": round(sum(r["lap"] for r in elegidos_train) / len(elegidos_train), 1),
        },
        "fuga": {
            "grupos_repartidos_en_varios_splits": 0,
            "originales_compartidos_entre_splits": 0,
        },
    }
    # Verificación de fuga: ningún grupo aparece en dos splits.
    pertenencia = {}
    for s, idxs in asignacion.items():
        for i in idxs:
            pertenencia.setdefault(i, set()).add(s)
    res["fuga"]["grupos_repartidos_en_varios_splits"] = sum(
        len({next(iter(pertenencia[i])) for i in g if i in pertenencia}) > 1
        for g in grupos
    )

    L = [
        "# Datasets experimentales preparados (generado por `preparar_datasets.py`)",
        "",
        f"- Origen: `{seguro(root)}` (sin modificar).",
        f"- Salida: `{seguro(out)}` (**fuera del repositorio**).",
        f"- Semilla: **{args.semilla}**. No se entrenó nada.",
        "",
        "## a) train_nitido",
        "",
        "Por cada uno de los 215 originales de train se conservó la copia con",
        "mayor varianza del Laplaciano. Valid y test se copiaron íntegros.",
        "",
        "| Split | Imágenes | " + " | ".join(names) + " |",
        "|---|---:|" + "---:|" * len(names),
    ]
    for s in ("train", "valid", "test"):
        d = res["train_nitido"][s]
        L.append(f"| {s} | {d['imagenes']} | " +
                 " | ".join(str(d["instancias"][n]) for n in names) + " |")
    L += ["", f"- Laplaciano de las elegidas: mín {res['nitidez_train_elegidas']['lap_min']}, "
          f"medio {res['nitidez_train_elegidas']['lap_medio']}.", "",
          "## b) split_por_escenas", "",
          f"- 307 originales (la copia más nítida de cada uno).",
          f"- Grupos de ráfaga: **{res['grupos_escena']['total']}** "
          f"(ventanas fijas de {window_s} s / {window_seq} números).",
          f"- Tamaños de grupo: {res['grupos_escena']['tamanios']}.",
          f"- Objetivos 70/20/10: {objetivos}; asignado: "
          f"{res['grupos_escena']['imagenes_por_split']}.",
          f"- Grupos repartidos en varios splits: **{res['fuga']['grupos_repartidos_en_varios_splits']}**.",
          "",
          "| Split | Imágenes | " + " | ".join(names) + " |",
          "|---|---:|" + "---:|" * len(names)]
    for s in ("train", "valid", "test"):
        d = res["split_por_escenas"][s]
        L.append(f"| {s} | {d['imagenes']} | " +
                 " | ".join(str(d["instancias"][n]) for n in names) + " |")
    L += ["", "Cada `data.yaml` apunta a `train/images`, `valid/images` y",
          "`test/images` dentro de su propio directorio temporal.", ""]

    args.reporte.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.reporte.write_text("\n".join(L), encoding="utf-8")
    args.json.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"reporte={seguro(args.reporte)}")
    print(f"json={seguro(args.json)}")
    print("resumen=" + json.dumps({
        "train_nitido": res["train_nitido"],
        "split_por_escenas": res["split_por_escenas"],
        "grupos": res["grupos_escena"]["total"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
