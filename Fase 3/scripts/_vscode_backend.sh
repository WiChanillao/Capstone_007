#!/usr/bin/env bash
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$RAIZ/ecoscan-backend/venv/bin/python"

cd "$RAIZ/ecoscan-backend"
echo "[EcoScan] Inicializando/verificando MySQL desde el repo..."
"$PY" "$RAIZ/scripts/init_local_db.py"
echo "[EcoScan] Levantando FastAPI en el terminal integrado de VS Code..."
exec "$PY" main.py
