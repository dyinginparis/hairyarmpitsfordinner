@echo off
setlocal
cd /d "%~dp0"

set "SERVICE_ID=PredictionMarketBot"
set "SERVICE_NAME=Prediction Market Bot Server"
set "SERVICE_EXE=%CD%\PredictionMarketBotService.exe"
set "SERVICE_XML=%CD%\PredictionMarketBotService.xml"

call :require_admin
if errorlevel 1 exit /b 1

call :ensure_python
if errorlevel 1 exit /b 1

call :ensure_env
if errorlevel 1 exit /b 1

call :ensure_node
if errorlevel 1 exit /b 1

call :ensure_winsw
if errorlevel 1 exit /b 1

call :write_service_xml
if errorlevel 1 exit /b 1

echo Installing Windows service "%SERVICE_ID%"...
"%SERVICE_EXE%" install
if errorlevel 1 (
  echo Service install failed. If the service already exists, run "Uninstall Windows Service.bat" first.
  pause
  exit /b 1
)

sc.exe config "%SERVICE_ID%" start= auto >nul
echo Starting service "%SERVICE_ID%"...
"%SERVICE_EXE%" start
if errorlevel 1 (
  echo Service was installed, but could not be started. Check logs in the logs folder.
  pause
  exit /b 1
)

echo.
echo Service installed and started.
echo Open http://127.0.0.1:5050 in your browser.
echo.
pause
exit /b 0

:require_admin
net session >nul 2>&1
if errorlevel 1 (
  echo This script must be run as Administrator.
  echo Right-click this file and choose "Run as administrator".
  pause
  exit /b 1
)
exit /b 0

:ensure_python
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    python -m venv .venv
  )
  if errorlevel 1 (
    echo Failed to create Python virtual environment.
    pause
    exit /b 1
  )
)

echo Installing Python dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt waitress
if errorlevel 1 exit /b 1

if not exist "logs" mkdir "logs"
if not exist "data" mkdir "data"
exit /b 0

:ensure_env
if not exist ".env" (
  if exist ".env.example" (
    echo Creating .env from .env.example...
    copy ".env.example" ".env" >nul
  ) else (
    echo .env is missing and .env.example was not found.
    pause
    exit /b 1
  )
)
exit /b 0

:ensure_node
if not exist node_modules (
  echo Installing desktop dependencies...
  call npm.cmd install
  if errorlevel 1 exit /b 1
)
exit /b 0

:ensure_winsw
if exist "%SERVICE_EXE%" exit /b 0

if exist "WinSW-x64.exe" (
  copy "WinSW-x64.exe" "%SERVICE_EXE%" >nul
  exit /b 0
)

if exist "winsw.exe" (
  copy "winsw.exe" "%SERVICE_EXE%" >nul
  exit /b 0
)

echo WinSW service wrapper is missing.
echo.
echo Download the WinSW x64 executable and place it in this folder as:
echo   %SERVICE_EXE%
echo.
echo Common source:
echo   https://github.com/winsw/winsw/releases
echo.
echo Then run this installer again.
pause
exit /b 1

:write_service_xml
echo Writing service configuration...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\windows-service\write-service-xml.ps1" -Root "%CD%"
if errorlevel 1 (
  echo Could not write PredictionMarketBotService.xml.
  pause
  exit /b 1
)
exit /b 0
