@echo off
title EcoScan BACKEND - FastAPI puerto 8000
cd /d "%~dp0..\ecoscan-backend"
echo === EcoScan BACKEND ===
echo MySQL: %MYSQL_HOST%:%MYSQL_PORT%/%MYSQL_DB%
echo Docs: http://127.0.0.1:8000/docs
echo.
"%~dp0..\ecoscan-backend\venv\Scripts\python.exe" main.py
