#!/usr/bin/env python3
"""Verifica sintaxis Python sin generar __pycache__. Solo lectura."""
import ast
import sys

for ruta in sys.argv[1:]:
    ast.parse(open(ruta, encoding="utf-8").read(), filename=ruta)
    print("OK", ruta)
