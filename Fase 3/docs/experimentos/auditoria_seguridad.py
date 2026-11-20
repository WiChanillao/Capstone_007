#!/usr/bin/env python3
"""Auditoría SOLO LECTURA de secretos en árbol, historial y notebook.

Nunca imprime el valor encontrado: todo hallazgo se redacta como `***`.
Uso:
  python auditoria_seguridad.py --repo <raiz_git> --notebook <ipynb>
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SENSITIVE = re.compile(
    r"(?i)("
    r"api[\s_-]*key|apikey|token|secret|"
    r"sk-[A-Za-z0-9_-]{6,}|AIza[0-9A-Za-z_-]{8,}|ghp_[A-Za-z0-9]{6,}|"
    r"roboflow[\s_-]*api[\s_-]*key|password|passwd|pwd"
    r")"
)

EXCLUDED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build",
    ".pytest_cache", ".mypy_cache", "coverage_html",
}
EXCLUDED_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".heic", ".pt", ".onnx",
    ".zip", ".tar", ".gz", ".woff", ".woff2", ".ttf", ".ico", ".ipynb",
}
EXCLUDED_NAMES = {
    ".env", "auditoria_seguridad.py", "generalizacion.md", "plan_entrenamiento.md",
}


def redact(line: str) -> str:
    if re.search(r"(?i)(image/png|base64|ivbor)", line) and len(line) > 200:
        return "<blob base64 omitido>"
    m = SENSITIVE.search(line)
    if not m:
        return line.strip()
    prefijo = line[: m.start()]
    if len(prefijo) > 100:
        prefijo = "..." + prefijo[-100:]
    return (prefijo + m.group(0) + "=***").strip()


def hallazgo(origen: str, archivo: str, linea: str, texto: str, commit: str = "") -> dict:
    return {
        "origen": origen,
        "archivo": archivo,
        "linea": linea,
        "commit": commit,
        "texto_redactado": redact(texto)[:240],
    }


def es_texto(ruta: Path) -> bool:
    return ruta.suffix.lower() not in EXCLUDED_SUFFIXES and ruta.name not in EXCLUDED_NAMES


def escanar_arbol(repo: Path) -> list[dict]:
    resultados: list[dict] = []
    for ruta in sorted(repo.rglob("*")):
        if not ruta.is_file() or not es_texto(ruta):
            continue
        partes = set(ruta.parts)
        if partes & EXCLUDED_DIRS:
            continue
        try:
            texto = ruta.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = ruta.relative_to(repo).as_posix()
        for n, linea in enumerate(texto.splitlines(), 1):
            if SENSITIVE.search(linea):
                resultados.append(hallazgo("arbol", rel, str(n), linea))
    return resultados


def escanar_historial(repo: Path, git: str) -> list[dict]:
    proc = subprocess.run(
        [git, "-C", str(repo), "log", "--all", "-p", "--no-ext-diff",
         "--no-color", "--find-renames", "--format=commit %H"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, errors="replace", check=False,
    )
    if proc.returncode != 0:
        return [hallazgo("historial", "git log", "-", proc.stderr.strip()[:200])]

    resultados: list[dict] = []
    commit = "?"
    archivo = "?"
    vieja = 0
    nueva = 0
    hunk = re.compile(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    diff = re.compile(r"^diff --git a/(?:.+/)?(.+) b/(.+)$")

    for crudo in proc.stdout.splitlines():
        if crudo.startswith("commit "):
            commit = crudo.split()[1][:10]
        elif crudo.startswith("diff --git "):
            m = diff.match(crudo)
            archivo = m.group(2) if m else "?"
        elif crudo.startswith("@@"):
            m = hunk.search(crudo)
            if m:
                vieja, nueva = int(m.group(1)), int(m.group(2))
        elif crudo.startswith("+") and not crudo.startswith("+++"):
            contenido = crudo[1:]
            if SENSITIVE.search(contenido):
                resultados.append(
                    hallazgo("historial", archivo, f"+{nueva}", contenido, commit)
                )
            nueva += 1
        elif crudo.startswith("-") and not crudo.startswith("---"):
            contenido = crudo[1:]
            if SENSITIVE.search(contenido):
                resultados.append(
                    hallazgo("historial", archivo, f"-{vieja}", contenido, commit)
                )
            vieja += 1
        elif crudo.startswith(" "):
            contenido = crudo[1:]
            if SENSITIVE.search(contenido):
                resultados.append(
                    hallazgo("historial", archivo, f" {nueva}", contenido, commit)
                )
            nueva += 1
            vieja += 1
    return resultados


def escanar_notebook(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return [hallazgo("notebook", str(ruta), "-", "NO ENCONTRADO")]
    nb = json.loads(ruta.read_text(encoding="utf-8", errors="replace"))
    resultados: list[dict] = []
    for i, celda in enumerate(nb.get("cells", [])):
        origen = "".join(celda.get("source", []))
        for n, linea in enumerate(origen.splitlines(), 1):
            if SENSITIVE.search(linea):
                resultados.append(
                    hallazgo("notebook", f"{ruta.name}#celda{i}", str(n), linea)
                )
    return resultados


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--notebook", type=Path)
    ap.add_argument(
        "--git",
        default=shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe",
        help="Ruta al ejecutable git (necesario en Windows si no está en PATH).",
    )
    args = ap.parse_args()

    todo = []
    todo += escanar_arbol(args.repo)
    todo += escanar_historial(args.repo, args.git)
    if args.notebook:
        todo += escanar_notebook(args.notebook)

    print(f"# hallazgos={len(todo)} (valores siempre redactados)")
    for item in todo[:400]:
        print(json.dumps(item, ensure_ascii=False, sort_keys=True))
    if len(todo) > 400:
        print(f"# truncado: {len(todo) - 400} hallazgos adicionales")


if __name__ == "__main__":
    main()
