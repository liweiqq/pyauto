@echo off
setlocal
set PORT=%1
if "%PORT%"=="" set PORT=8080

echo [Stock Pilot] starting local server at http://127.0.0.1:%PORT%
python -m http.server %PORT%
endlocal
