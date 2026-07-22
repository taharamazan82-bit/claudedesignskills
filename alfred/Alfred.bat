@echo off
REM Alfred one-click launcher for Windows.
REM Double-click this file to start Alfred (backend + 3D interface).
REM First run: creates a Python venv and installs backend deps automatically.

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [Alfred] Python bulunamadi. Once Python 3'u kur: https://python.org/downloads
  pause
  exit /b 1
)

if not exist ".venv" (
  echo [Alfred] Ilk kurulum: sanal ortam olusturuluyor...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  python -m pip install --quiet --upgrade pip
  python -m pip install --quiet -r backend\requirements.txt
) else (
  call .venv\Scripts\activate.bat
)

echo [Alfred] Baslatiliyor... Tarayicida http://127.0.0.1:5173 acilacak.
python start.py
pause
