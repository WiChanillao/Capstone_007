@echo off
title EcoScan FRONTEND - Vite puerto 5173
cd /d "%~dp0..\ecoscan-frontend"
echo === EcoScan FRONTEND ===
echo App: http://localhost:5173/
echo.
call npm run dev -- --host 0.0.0.0
