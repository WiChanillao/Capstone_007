#!/usr/bin/env python3
"""Extrae hiperparámetros y menciones de métricas de un notebook. Solo lectura.

Omite líneas con patrones de credenciales para no imprimir valores sensibles.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CLAVE = re.compile(r"(?i)(api[\s_-]*key|token|secret|password|passwd|pwd|sk-|aiza|ghp_)")
INTERES = re.compile(
    r"(?i)(model\.train|\.train\(|YOLO\(|yolo11|epochs|imgsz|batch|patience|"
    r"seed|conf=|augment|mosaic|hsv|flip|degrees|scale|0\.562|0\.527|"
    r"1112|860|215|307|x4|aument|versi|roboflow|data\.yaml|"
    r"aluminio|carton|plastico|confusion|map|CONF_MIN|UMBRAL)"
)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("notebook", type=Path)
    ap.add_argument("--cell", type=int, help="Mostrar una celda completa (redactando credenciales).")
    args = ap.parse_args()
    nb = json.loads(args.notebook.read_text(encoding="utf-8", errors="replace"))

    if args.cell is not None:
        celdas = nb.get("cells", [])
        if not 0 <= args.cell < len(celdas):
            print(f"celda {args.cell} fuera de rango; total={len(celdas)}")
            return
        celda = celdas[args.cell]
        print(f"=== celda {args.cell} ({celda.get('cell_type')}) ===")
        for n, linea in enumerate("".join(celda.get("source", [])).splitlines(), 1):
            if CLAVE.search(linea):
                print(f"{n}: <linea redactada por contener credencial>")
            else:
                print(f"{n}: {linea[:300]}")
        return

    for i, celda in enumerate(nb.get("cells", [])):
        src = "".join(celda.get("source", []))
        hits = []
        for n, linea in enumerate(src.splitlines(), 1):
            if CLAVE.search(linea):
                continue
            if INTERES.search(linea):
                hits.append((n, linea.strip()[:220]))
        if hits:
            print(f"=== celda {i} ({celda.get('cell_type')}) ===")
            for n, linea in hits:
                print(f"{n}: {linea}")


if __name__ == "__main__":
    main()
