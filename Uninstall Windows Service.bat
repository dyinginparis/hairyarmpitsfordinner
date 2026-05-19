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
  "PredictionMarketBotService.exe" stop
  "PredictionMarketBotService.exe" uninstall
) else (
  sc.exe stop PredictionMarketBot
  sc.exe delete PredictionMarketBot
)

echo.
echo Service uninstalled. Local files, .env, logs, and data were not deleted.
pause
