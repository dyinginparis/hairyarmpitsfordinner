@echo off
setlocal
cd /d "%~dp0"

echo Service status:
sc.exe query PredictionMarketBot
echo.
echo Port 5050:
netstat -ano | findstr ":5050"
echo.
echo Healthcheck:
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod http://127.0.0.1:5050/api/config | ConvertTo-Json -Depth 4 } catch { Write-Host $_.Exception.Message; exit 1 }"
pause
