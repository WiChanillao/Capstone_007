# Publica el historial local en GitHub.
# Requiere que la cuenta con acceso al repo WiChanillao/Capstone_007 tenga
# sesion iniciada en el Credential Manager de Windows o use un token de acceso.
# No fuerza ni sobrescribe el historial remoto: crea una rama nueva.
$ErrorActionPreference = 'Stop'

$git = 'C:\Program Files\Git\cmd\git.exe'
if (-not (Test-Path $git)) { $git = 'git' }

$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo

Write-Host 'Repo local:' (Get-Location).Path
Write-Host 'Rama actual:' (& $git branch --show-current)
Write-Host 'Remoto:' (& $git remote get-url origin)

# Con GIT_TERMINAL_PROMPT=0 falla rapidamente si no hay credenciales.
$env:GIT_TERMINAL_PROMPT = '1'
& $git push -u origin feature/REC-57-git

if ($LASTEXITCODE -eq 0) {
    Write-Host '[OK] Rama feature/REC-57-git publicada.'
    Write-Host 'Siguiente paso: abrir un Pull Request hacia main en GitHub.'
} else {
    Write-Host '[PENDIENTE] No se pudo autenticar contra GitHub.'
    Write-Host 'Opciones:'
    Write-Host '  1) Iniciar sesion en GitHub desde el navegador y volver a ejecutar.'
    Write-Host '  2) git config --global credential.helper manager y repetir.'
    Write-Host '  3) Usar un Personal Access Token como password de HTTPS.'
    Write-Host '  4) Aplicar el bundle de evidencia con: git bundle verify / git fetch.'
}
