#!/usr/bin/env python3
"""Busca VALORES literales de credenciales en árbol e historial. Solo lectura.

No imprime el valor: solo archivo, línea/commit y el tipo de patrón.
Los números de teléfono, hashes de imágenes y placeholders no se consideran
credenciales.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PATRONES = {
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    "openai_sk": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "github_pat": re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    "api_key_asignado": re.compile(
        r"(?i)(api[\s_-]*key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]|"
        r"roboflow\s*\(\s*api_key\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"])"
    ),
}
EXCLUIR_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist"}
EXCLUIR_SUF = {".png", ".jpg", ".jpeg", ".webp", ".pt", ".ico", ".woff", ".woff2"}
EXCLUIR_NOMBRES = {".env", "buscar_literales.py", "auditoria_seguridad.py"}


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--git", default=shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe")
    args = ap.parse_args()

    hallazgos: list[tuple[str, str, str, str]] = []

    def revisar(texto: str, origen: str, ubicacion: str) -> None:
        for nombre, pat in PATRONES.items():
            if pat.search(texto):
                hallazgos.append((origen, ubicacion, nombre, "***"))

    for p in sorted(args.repo.rglob("*")):
        if not p.is_file() or p.suffix.lower() in EXCLUIR_SUF or p.name in EXCLUIR_NOMBRES:
            continue
        if EXCLUIR_DIRS & set(p.parts):
            continue
        try:
            texto = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for n, linea in enumerate(texto.splitlines(), 1):
            revisar(linea, "arbol", f"{p.relative_to(args.repo).as_posix()}:{n}")

    proc = subprocess.run(
        [args.git, "-C", str(args.repo), "log", "--all", "-p", "--no-ext-diff",
         "--no-color", "--format=commit %H"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, errors="replace", check=False,
    )
    commit, archivo = "?", "?"
    for crudo in proc.stdout.splitlines():
        if crudo.startswith("commit "):
            commit = crudo.split()[1][:10]
        elif crudo.startswith("diff --git "):
            m = re.match(r"^diff --git a/(?:.+/)?(.+) b/(.+)$", crudo)
            archivo = m.group(2) if m else "?"
        elif crudo.startswith(("+", "-", " ")) and not crudo.startswith(("+++", "---")):
            revisar(crudo[1:], "historial", f"{commit}:{archivo}")

    print(f"# valores_literales={len(hallazgos)}")
    for h in hallazgos[:200]:
        print(" | ".join(h))


if __name__ == "__main__":
    main()
