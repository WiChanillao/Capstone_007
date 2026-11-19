$ErrorActionPreference = 'Continue'
$Raiz = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $Raiz 'ecoscan-backend\venv\Scripts\python.exe'

Write-Host '=== EcoScan: verificacion de Docker ===' -ForegroundColor Cyan

$requeridos = @(
  'docker-compose.yml',
  'docker/mysql/init/01_schema.sql',
  'docker/mysql/init/02_seed.sql',
  'ecoscan-backend/Dockerfile',
  'ecoscan-backend/.dockerignore',
  'ecoscan-frontend/Dockerfile',
  'ecoscan-frontend/.dockerignore',
  '.dockerignore',
  '.env.example'
)
foreach ($f in $requeridos) {
  if (Test-Path (Join-Path $Raiz $f)) {
    Write-Host "[OK]     $f" -ForegroundColor Green
  } else {
    Write-Host "[FALTA]  $f" -ForegroundColor Red
  }
}

if (Test-Path $Py) {
  $env:YAML_PATH = ($Raiz -replace '\\', '/') + '/docker-compose.yml'
  & $Py -c "import os,yaml; d=yaml.safe_load(open(os.environ['YAML_PATH'],encoding='utf-8')); print('[OK]     YAML valido. Servicios:', ', '.join(d['services'].keys()))"
}

$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($docker) {
  Write-Host '[OK]     Docker CLI encontrado' -ForegroundColor Green
  Push-Location -LiteralPath $Raiz
  docker compose config --quiet
  if ($LASTEXITCODE -eq 0) {
    Write-Host '[OK]     docker compose config' -ForegroundColor Green
  } else {
    Write-Host '[ERROR]  docker compose config' -ForegroundColor Red
  }
  Pop-Location

  # ¿Está el stack en ejecución?
  Push-Location -LiteralPath $Raiz
  $enEjecucion = docker compose ps --format '{{.Name}} | {{.Status}}' 2>$null
  Pop-Location
  if ($enEjecucion) {
    Write-Host '[OK]     Contenedores en ejecucion:' -ForegroundColor Green
    $enEjecucion | ForEach-Object { Write-Host "         $_" -ForegroundColor Green }
    $ProgressPreference = 'SilentlyContinue'
    foreach ($u in @('http://127.0.0.1:8000/health','http://127.0.0.1:8000/v1/models','http://127.0.0.1:5173/')) {
      try {
        $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 8
        Write-Host "[OK]     $u -> $($r.StatusCode)" -ForegroundColor Green
      } catch {
        Write-Host "[FALLA]  $u" -ForegroundColor Red
      }
    }
  } else {
    Write-Host '[INFO]   El stack aun no esta levantado.' -ForegroundColor Yellow
    Write-Host 'Siguiente paso: docker compose up --build -d' -ForegroundColor Cyan
  }
} else {
  Write-Host '[PENDIENTE] Docker CLI/daemon no disponible en esta PC.' -ForegroundColor Yellow
  Write-Host '  Instala Docker Desktop y vuelve a ejecutar este script.' -ForegroundColor Yellow
}
