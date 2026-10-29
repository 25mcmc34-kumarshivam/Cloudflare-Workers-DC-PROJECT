@echo off
setlocal
cd /d "%~dp0"
python demo.py
if errorlevel 1 (
  echo.
  echo Demo failed. Confirm that Python 3.10 or later is installed.
  pause
  exit /b 1
)
echo.
echo Demo completed successfully.
pause

