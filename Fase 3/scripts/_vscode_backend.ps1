$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $Raiz 'ecoscan-backend\venv\Scripts\python.exe'

Set-Location -LiteralPath (Join-Path $Raiz 'ecoscan-backend')
Write-Host '[EcoScan] Inicializando/verificando MySQL desde el repo...' -ForegroundColor Cyan
& $Py (Join-Path $Raiz 'scripts\init_local_db.py')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo inicializar MySQL.' }

Write-Host '[EcoScan] Levantando FastAPI en el terminal integrado de VS Code...' -ForegroundColor Green
& $Py main.py
