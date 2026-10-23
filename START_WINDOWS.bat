@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3.12 scripts\setup.py
  if errorlevel 1 (
    pause
    exit /b 1
  )
)
py -3.12 scripts\start.py
pause
