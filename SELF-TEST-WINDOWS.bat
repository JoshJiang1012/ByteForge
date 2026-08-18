@echo off
setlocal
cd /d "%~dp0"
title ByteForge v5.0 Self Test
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 server.py --self-test
) else (
  python server.py --self-test
)
echo.
pause
