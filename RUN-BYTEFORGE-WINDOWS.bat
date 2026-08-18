@echo off
setlocal
cd /d "%~dp0"
title ByteForge v5.0

echo ============================================================
echo  BYTEFORGE v5.0 - CYBER ACADEMY
echo ============================================================
echo.
echo This window IS the ByteForge local server.
echo Keep it open while you play.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 server.py
    set EXITCODE=%errorlevel%
    goto :done
)

where python >nul 2>nul
if %errorlevel%==0 (
    python server.py
    set EXITCODE=%errorlevel%
    goto :done
)

echo [ERROR] Python 3 was not found.
echo Install Python 3.10+ and enable "Add Python to PATH".
set EXITCODE=2

:done
echo.
if not "%EXITCODE%"=="0" echo ByteForge stopped with error code %EXITCODE%.
echo Press any key to close this window.
pause >nul
exit /b %EXITCODE%
