@echo off
setlocal enabledelayedexpansion

REM -------------------------
REM Logs folder
REM -------------------------
set LOG_DIR=%~dp0logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM -------------------------
REM Timestamp for logging (YYYYMMDD_HHMMSS)
REM -------------------------
for /f "tokens=1-6 delims=/:. " %%a in ("%date% %time%") do (
    set DD=%%a
    set MM=%%b
    set YYYY=%%c
    set HH=%%d
    set Min=%%e
    set Sec=%%f
)
set LOGFILE=%LOG_DIR%\forecast_run_%YYYY%%MM%%DD%_%HH%%Min%%Sec%.txt

echo ============================= >> "%LOGFILE%"
echo Run started at %date% %time% >> "%LOGFILE%"
echo ============================= >> "%LOGFILE%"

REM -------------------------
REM Run forecast service using virtual environment Python directly
REM -------------------------
"C:\Capstone\crisislens-API\venv\Scripts\python.exe" "%~dp0crisislens-API\forecast_service.py" --periods 30 --anchor %* >> "%LOGFILE%" 2>&1
set EXITCODE=%ERRORLEVEL%

REM -------------------------
REM Log success/failure
REM -------------------------
if %EXITCODE%==0 (
    echo SUCCESS: Forecast run completed at %date% %time% >> "%LOGFILE%"
) else (
    echo ERROR: Forecast run failed with exit code %EXITCODE% at %date% %time% >> "%LOGFILE%"
)

echo. >> "%LOGFILE%"
endlocal
