#!/usr/bin/env python3
"""Clasifica menciones de credenciales en un notebook sin imprimir valores.

Solo lectura. Salida: celda, línea, clasificación. Nunca muestra el texto
original de la línea cuando contiene una credencial o patrón sensible.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CLAVE = re.compile(r"(?i)(api[\s_-]*key|apikey|token|secret|password|passwd|pwd)")
SEGURO = re.compile(
    r"(?i)(userdata\.get|os\.environ|environ\.get|getpass|input\(|obtener_api_key|"
    r"secret|variable|entorno|environment|no est|sin clave|redact)"
)
LITERAL = re.compile(
    r"(?i)((?:api[\s_-]*key|apikey|token|secret|password|passwd|pwd)\s*[:=]\s*"
    r"['\"][^'\"]{4,}['\"]|roboflow\s*\(\s*api_key\s*=\s*['\"][^'\"]{4,}['\"])"
)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("notebook", type=Path)
    args = ap.parse_args()
    nb = json.loads(args.notebook.read_text(encoding="utf-8", errors="replace"))

    conteo: dict[str, int] = {}
    for i, celda in enumerate(nb.get("cells", [])):
        src = "".join(celda.get("source", []))
        for n, linea in enumerate(src.splitlines(), 1):
            if not CLAVE.search(linea):
                continue
            if LITERAL.search(linea):
                clase = "POSIBLE_VALOR_LITERAL"
            elif SEGURO.search(linea):
                clase = "LECTURA_SEGURA_O_MENCION"
            else:
                clase = "REVISAR_MANUALMENTE"
            conteo[clase] = conteo.get(clase, 0) + 1
            print(f"celda={i} linea={n} clase={clase}")
    print("RESUMEN", json.dumps(conteo, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
