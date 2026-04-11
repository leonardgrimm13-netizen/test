@echo off
setlocal
cd /d "%~dp0"
if not exist "config.json" (
  echo [INFO] config.json nicht gefunden, kopiere config.example.json ...
  copy "config.example.json" "config.json" >nul
)
py -3 app.py
endlocal
