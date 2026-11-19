#!/usr/bin/env bash
# Arranque reproducible de EcoLearn Chile / EcoScan en Linux, macOS o Git Bash.
# Uso: bash scripts/run.sh
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

info() { echo "[EcoScan] $1"; }
ok()   { echo "[EcoScan] $1"; }

# Modo Docker: bash scripts/run.sh --docker
if [ "${1:-}" = "--docker" ] || [ "${DOCKER:-0}" = "1" ]; then
  command -v docker >/dev/null || { echo "[EcoScan] Falta Docker. Instálalo o usa el modo local." >&2; exit 1; }
  info "Modo Docker: construyendo y levantando el stack completo..."
  docker compose up --build -d
  info "Esperando a que backend y frontend respondan..."
  for i in $(seq 1 180); do
    if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1 && curl -fsS http://127.0.0.1:5173/ >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  if ! curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "[EcoScan] El stack Docker no respondió. Revisa: docker compose logs" >&2
    exit 1
  fi
  docker compose ps
  echo ""
  ok "=== EcoScan en Docker levantado ==="
  echo "  App:      http://localhost:5173/"
  echo "  API:      http://127.0.0.1:8000/"
  echo "  Docs:     http://127.0.0.1:8000/docs"
  echo "  Detener:  docker compose down"
  exit 0
fi

if [ ! -f .env ]; then
  cp .env.example .env
  info "Creado .env desde .env.example"
fi
set -a
# shellcheck disable=SC1091
source .env
set +a

PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null || { echo "Falta Python 3"; exit 1; }
command -v npm >/dev/null || { echo "Falta npm"; exit 1; }

BACKEND="$RAIZ/ecoscan-backend"
FRONTEND="$RAIZ/ecoscan-frontend"
VENV="$BACKEND/venv"
PYVENV="$VENV/bin/python"

if [ ! -x "$PYVENV" ]; then
  info "Creando entorno virtual..."
  "$PYTHON" -m venv "$VENV"
fi
info "Instalando dependencias Python..."
"$PYVENV" -m pip install --quiet --upgrade pip
"$PYVENV" -m pip install --quiet -r "$BACKEND/requirements.txt"

if [ ! -d "$FRONTEND/node_modules" ]; then
  info "Instalando dependencias Node..."
  (cd "$FRONTEND" && { [ -f package-lock.json ] && npm ci || npm install; })
fi

info "Verificando MySQL..."
"$PYVENV" "$RAIZ/scripts/init_local_db.py"

mkdir -p "$RAIZ/logs"
info "Levantando backend y frontend en segundo plano..."
(cd "$BACKEND" && nohup "$PYVENV" main.py > "$RAIZ/logs/backend.log" 2>&1 &)
(cd "$FRONTEND" && nohup npm run dev -- --host 0.0.0.0 > "$RAIZ/logs/frontend.log" 2>&1 &)

for i in $(seq 1 120); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1 && curl -fsS http://127.0.0.1:5173/ >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
  echo "[EcoScan] ERROR: el backend no respondió. Revisa logs/backend.log" >&2
  exit 1
fi
ok "Verificación: $(curl -fsS http://127.0.0.1:8000/db/impacto)"

if command -v code >/dev/null 2>&1; then
  code "$RAIZ" >/dev/null 2>&1 || true
  ok "VS Code abierto en la raíz del repositorio."
fi
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://127.0.0.1:5173/ >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open http://127.0.0.1:5173/ >/dev/null 2>&1 || true
fi

echo ""
ok "=== EcoScan levantado ==="
echo "  App:   http://localhost:5173/"
echo "  API:   http://127.0.0.1:8000/"
echo "  Docs:  http://127.0.0.1:8000/docs"
echo "  Logs:  $RAIZ/logs/"
echo "  Detener: pkill -f 'main.py' y pkill -f 'vite'"
