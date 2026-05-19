@echo off
setlocal
cd /d "%~dp0"

net session >nul 2>&1
if errorlevel 1 (
  echo This script must be run as Administrator.
  echo Right-click this file and choose "Run as administrator".
  pause
  exit /b 1
)

if exist "PredictionMarketBotService.exe" (
  "PredictionMarketBotService.exe" restart
) else (
  sc.exe stop PredictionMarketBot
  timeout /t 3 /nobreak >nul
  sc.exe start PredictionMarketBot
)

echo.
sc.exe query PredictionMarketBot
echo.
echo Healthcheck:
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod http://127.0.0.1:5050/api/config | ConvertTo-Json -Depth 4 } catch { Write-Host $_.Exception.Message; exit 1 }"
pause
