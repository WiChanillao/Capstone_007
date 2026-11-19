<#
.SYNOPSIS
  Arranca EcoLearn Chile / EcoScan desde un clone del repositorio.
  Uso: powershell -ExecutionPolicy Bypass -File scripts\run.ps1
#>
param(
  [switch]$SinNavegador,
  [switch]$SinVSCode,
  [switch]$Docker
)

$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Raiz

function Info($msg) { Write-Host "[EcoScan] $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "[EcoScan] $msg" -ForegroundColor Green }
function Error($msg){ Write-Host "[EcoScan] $msg" -ForegroundColor Red }

# ---------- 0. Modo Docker (docker compose) ----------
if ($Docker) {
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker no está instalado. Ejecuta scripts\instalar_docker.ps1 o instala Docker Desktop.'
  }
  Info 'Modo Docker: construyendo y levantando el stack completo...'
  docker compose up --build -d
  if ($LASTEXITCODE -ne 0) { throw 'docker compose up falló. Revisa la salida anterior.' }

  Info 'Esperando a que backend y frontend respondan...'
  $listo = $false
  for ($i = 0; $i -lt 180; $i++) {
    try {
      $h = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 2
      $w = Invoke-WebRequest -Uri 'http://127.0.0.1:5173/' -UseBasicParsing -TimeoutSec 2
      if ($h.status -eq 'ok' -and $w.StatusCode -eq 200) { $listo = $true; break }
    } catch { }
    Start-Sleep -Seconds 1
  }
  if (-not $listo) { throw 'El stack Docker no respondió en 180 s. Revisa: docker compose logs' }

  docker compose ps
  Ok '=== EcoScan en Docker levantado ==='
  Write-Host '  App:      http://localhost:5173/' -ForegroundColor White
  Write-Host '  API:      http://127.0.0.1:8000/' -ForegroundColor White
  Write-Host '  Docs:     http://127.0.0.1:8000/docs' -ForegroundColor White
  Write-Host '  Detener:  docker compose down' -ForegroundColor DarkGray
  if (-not $SinNavegador) { Start-Process 'http://127.0.0.1:5173/' | Out-Null }
  exit 0
}

# ---------- 1. Configuración ----------
$envFile = Join-Path $Raiz '.env'
if (-not (Test-Path $envFile)) {
  Copy-Item (Join-Path $Raiz '.env.example') $envFile
  Info 'Creado .env desde .env.example (edítalo si tu MySQL usa otra clave).'
}
foreach ($linea in (Get-Content $envFile)) {
  $linea = $linea.Trim()
  if (-not $linea -or $linea.StartsWith('#') -or -not $linea.Contains('=')) { continue }
  $k, $v = $linea.Split('=', 2)
  if (-not (Test-Path "env:$($k.Trim())")) { Set-Item "env:$($k.Trim())" $v.Trim().Trim('"').Trim("'") }
}

# ---------- 2. Prerrequisitos ----------
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) { throw 'No se encontró Python. Instala Python 3.10+ y vuelve a ejecutar.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'No se encontró Node.js. Instala Node 20+.' }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'No se encontró npm.' }
Ok "Python: $python"
Ok "Node: $((Get-Command node).Source)"

# ---------- 3. Backend ----------
$backend = Join-Path $Raiz 'ecoscan-backend'
$venv = Join-Path $backend 'venv'
$pyVenv = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $pyVenv)) {
  Info 'Creando entorno virtual del backend...'
  & $python -m venv $venv
}
Info 'Instalando dependencias Python (requirements.txt)...'
& $pyVenv -m pip install --upgrade pip --quiet
& $pyVenv -m pip install -r (Join-Path $backend 'requirements.txt') --quiet

# ---------- 4. Frontend ----------
$frontend = Join-Path $Raiz 'ecoscan-frontend'
if (-not (Test-Path (Join-Path $frontend 'node_modules'))) {
  Info 'Instalando dependencias Node...'
  Push-Location $frontend
  if (Test-Path (Join-Path $frontend 'package-lock.json')) { npm ci } else { npm install }
  Pop-Location
} else {
  Ok 'node_modules ya presente.'
}

# ---------- 5. Base de datos ----------
Info 'Verificando / inicializando MySQL (sin borrar datos)...'
& $pyVenv (Join-Path $Raiz 'scripts\init_local_db.py')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo conectar/inicializar MySQL. Revisa .env (MYSQL_USER / MYSQL_PASSWORD).' }
Ok 'MySQL listo.'

# ---------- 6. Servicios en terminales visibles ----------
$batBackend = Join-Path $PSScriptRoot '_serve_backend.bat'
$batFrontend = Join-Path $PSScriptRoot '_serve_frontend.bat'
Start-Process -FilePath 'cmd.exe' -ArgumentList @('/k', ('"' + $batBackend + '"')) -WindowStyle Normal | Out-Null
Start-Process -FilePath 'cmd.exe' -ArgumentList @('/k', ('"' + $batFrontend + '"')) -WindowStyle Normal | Out-Null
Ok 'Backend y frontend abiertos en dos terminales visibles.'

# ---------- 7. Herramientas ----------
if (-not $SinVSCode) {
  $code = (Get-Command code -ErrorAction SilentlyContinue).Source
  if ($code) {
    Start-Process -FilePath $code -ArgumentList @('-n', ('"' + $Raiz + '"')) -WindowStyle Normal | Out-Null
    Ok 'Visual Studio Code abierto en la raíz del repositorio.'
  } else {
    Info 'VS Code no está en PATH; omiendo este paso (instálalo o abre la carpeta manualmente).'
  }
}
if (-not $SinNavegador) {
  Start-Process 'http://127.0.0.1:5173/' | Out-Null
  Ok 'Navegador abierto en la aplicación.'
}

# ---------- 8. Verificación real ----------
Info 'Esperando a que backend y frontend respondan...'
$listo = $false
$health = $null
for ($i = 0; $i -lt 180; $i++) {
  try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 2
    $web = Invoke-WebRequest -Uri 'http://127.0.0.1:5173/' -UseBasicParsing -TimeoutSec 2
    if ($health.status -eq 'ok' -and $web.StatusCode -eq 200) { $listo = $true; break }
  } catch { }
  Start-Sleep -Seconds 1
}
if (-not $listo) {
  throw 'Los servicios no respondieron en 180 s. Revisa las dos terminales abiertas.'
}
$impacto = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/db/impacto' -TimeoutSec 5
Ok "Verificado: MySQL=$($health.mysql_conectado), modelo=$($health.modelo_activo), $($impacto.escaneos) escaneos, $($impacto.impacto.agua_litros) L, $($impacto.impacto.co2_kg) kg CO2."

Write-Host ''
Ok '=== EcoScan levantado ==='
Write-Host '  App:       http://localhost:5173/' -ForegroundColor White
Write-Host '  API:       http://127.0.0.1:8000/' -ForegroundColor White
Write-Host '  Docs:      http://127.0.0.1:8000/docs' -ForegroundColor White
Write-Host ("  MySQL:     {0}:{1} / {2}" -f $env:MYSQL_HOST, $env:MYSQL_PORT, $env:MYSQL_DB) -ForegroundColor White
Write-Host '  Para detener: cierra las dos ventanas de terminal.' -ForegroundColor DarkGray
