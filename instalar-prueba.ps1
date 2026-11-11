# ORIVEXY Verify · versión de prueba (pide una clave de licencia en lugar de cuenta)
# Uso:  powershell -c "irm https://orivexy.com/instalar-prueba.ps1 | iex"
$OrivexyVersion = "ORIVEXY-Verify-Setup-0.1.8-prueba.exe"
Invoke-Expression (Invoke-RestMethod "https://orivexy.com/instalar.ps1" -UseBasicParsing)
