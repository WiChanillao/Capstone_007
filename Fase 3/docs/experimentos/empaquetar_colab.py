#!/usr/bin/env python3
"""Empaqueta train_nitido y split_por_escenas para Colab (SOLO LECTURA del origen).

Genera un .zip por dataset con `data.yaml` portable (path: '.', rutas
relativas). Toda la salida queda FUERA del repositorio. No sube nada a Drive.

Uso:
  python empaquetar_colab.py --origen <datasets_experimentales> \
      --salida <paquetes_colab>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import yaml

SUBSETS = ("train_nitido", "split_por_escenas")
NOMBRES = {0: "Aluminio", 1: "Carton", 2: "Plastico"}


def seguro(texto: str | Path) -> str:
    return str(texto).replace("\\", "/")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def empaquetar(origen: Path, salida: Path, nombre: str) -> dict:
    staging = salida / "staging" / nombre
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    conteo = {}
    for split in ("train", "valid", "test"):
        shutil.copytree(origen / nombre / split, staging / split)
        conteo[split] = sum(1 for p in (staging / split / "images").iterdir()
                            if p.is_file())
    (staging / "data.yaml").write_text(yaml.safe_dump({
        "path": ".", "train": "train/images", "val": "valid/images",
        "test": "test/images", "nc": len(NOMBRES), "names": NOMBRES,
    }, allow_unicode=True), encoding="utf-8")

    destino = salida / f"{nombre}.zip"
    if destino.exists():
        destino.unlink()
    shutil.make_archive(str(destino.with_suffix("")), "zip", root_dir=staging)
    return {
        "zip": seguro(destino),
        "bytes": destino.stat().st_size,
        "MB": round(destino.stat().st_size / (1024 * 1024), 2),
        "sha256": sha256(destino),
        "imagenes": conteo,
        "data_yaml": "path: '.' + train/valid/test relativos",
    }


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--origen", type=Path, required=True)
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    origen = args.origen.resolve()
    salida = args.salida.resolve()
    salida.mkdir(parents=True, exist_ok=True)
    info = {n: empaquetar(origen, salida, n) for n in SUBSETS}

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(info, ensure_ascii=False, indent=2),
                             encoding="utf-8")
    for n, d in info.items():
        print(f"{n}: {d['MB']} MB  imagenes={d['imagenes']}  zip={d['zip']}")
        print(f"  sha256={d['sha256']}")


if __name__ == "__main__":
    main()
