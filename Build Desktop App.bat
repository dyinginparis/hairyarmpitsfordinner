@echo off
setlocal
cd /d "%~dp0"

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
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  pause
  exit /b 1
)

if not exist ".env" (
  if exist ".env.example" (
    copy ".env.example" ".env" >nul
  )
)

if not exist node_modules (
  echo Installing desktop dependencies...
  call npm.cmd install
  if errorlevel 1 (
    pause
    exit /b 1
  )
)

call npm.cmd run package:win
pause
