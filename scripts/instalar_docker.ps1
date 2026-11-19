# EcoScan / EcoLearn Chile - Instalador de Docker en Windows
# Ejecuta: powershell -ExecutionPolicy Bypass -File scripts\instalar_docker.ps1
# Pide permisos de administrador (UAC) automaticamente.

$ErrorActionPreference = 'Stop'

function Test-Admin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
  Write-Host 'Se necesitan permisos de administrador. Abriendo ventana elevada...' -ForegroundColor Yellow
  $argList = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
  Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList $argList
  exit
}

Write-Host '=== [1/3] Instalando WSL2 (requisito de Docker Desktop) ===' -ForegroundColor Cyan
wsl --install --no-distribution

Write-Host '=== [2/3] Instalando Docker Desktop con winget ===' -ForegroundColor Cyan
winget install --id Docker.DockerDesktop -e --accept-source-agreements --accept-package-agreements

Write-Host '=== [3/3] Terminado ===' -ForegroundColor Green
Write-Host ''
Write-Host 'SIGUIENTE PASO OBLIGATORIO:' -ForegroundColor Yellow
Write-Host '  1) Reinicia el PC (WSL2 lo necesita).' -ForegroundColor Yellow
Write-Host '  2) Abre "Docker Desktop" y espera a que diga "Engine running".' -ForegroundColor Yellow
Write-Host '  3) Vuelve al repo y ejecuta:  .\scripts\verificar_docker.ps1' -ForegroundColor Yellow
Write-Host '  4) Levanta todo con:          docker compose up --build -d' -ForegroundColor Yellow
Write-Host ''
Read-Host 'Pulsa Enter para cerrar esta ventana'
