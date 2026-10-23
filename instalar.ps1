# ORIVEXY Verify · instalador por orden (sin pasar por el navegador)
# Uso:  powershell -c "irm https://orivexy.github.io/instalar.ps1 | iex"
#       (versión de prueba: instalar-prueba.ps1)
$ErrorActionPreference = "Stop"
if (-not $OrivexyVersion) { $OrivexyVersion = "ORIVEXY-Verify-Setup-0.1.5.exe" }
$url = "https://github.com/Orivexy/orivexy.github.io/releases/download/v0.1.5/$OrivexyVersion"
$destino = Join-Path $env:TEMP $OrivexyVersion

Write-Host ""
Write-Host "  ORIVEXY Verify - descargando el instalador..." -ForegroundColor Cyan
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = "SilentlyContinue"
Invoke-WebRequest -Uri $url -OutFile $destino -UseBasicParsing

Write-Host "  Abriendo el instalador. Sigue los pasos de la ventana." -ForegroundColor Cyan
$argumentos = @()
if ($env:ORIVEXY_INSTALAR_SILENCIOSO) { $argumentos = @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART") }
if ($argumentos.Count) { $p = Start-Process $destino -ArgumentList $argumentos -Wait -PassThru } else { $p = Start-Process $destino -Wait -PassThru }
Remove-Item $destino -ErrorAction SilentlyContinue
if ($p.ExitCode -eq 0) {
    Write-Host "  Listo. Abre ORIVEXY Verify desde el menu Inicio." -ForegroundColor Green
} else {
    Write-Host "  La instalacion no se completo (codigo $($p.ExitCode))." -ForegroundColor Yellow
}
