# ORIVEXY Verify · versión de prueba (pide una clave de licencia en lugar de cuenta)
# Uso:  powershell -c "irm https://orivexy.github.io/instalar-prueba.ps1 | iex"
$OrivexyVersion = "ORIVEXY-Verify-Setup-0.1.7-prueba.exe"
Invoke-Expression (Invoke-RestMethod "https://orivexy.github.io/instalar.ps1" -UseBasicParsing)
