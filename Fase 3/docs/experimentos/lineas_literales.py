#!/usr/bin/env python3
"""Muestra sólo número de línea y patrón redactado de un archivo en un commit."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys

PAT = re.compile(r"(AIza[0-9A-Za-z_\-]{30,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,})")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--git", default=shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe")
    a = ap.parse_args()
    p = subprocess.run([a.git, "-C", a.repo, "show", f"{a.commit}:{a.path}"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, errors="replace", check=False)
    if p.returncode != 0:
        print("NO_DISPONIBLE", p.stderr.strip()[:160])
        return
    for n, linea in enumerate(p.stdout.splitlines(), 1):
        if PAT.search(linea):
            print(f"linea={n} valor=***")


if __name__ == "__main__":
    main()
