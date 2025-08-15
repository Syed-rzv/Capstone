@echo off
REM Activate venv
call "C:\Users\97150\OneDrive\Documents\Capstone\crisislens-API\venv\Scripts\activate.bat"

REM Run forecast script with any args (like periods or anchor)
python "C:\Users\97150\OneDrive\Documents\Capstone\crisislens-API\forecast_service.py" --periods 30 --anchor

REM Pause or just exit
exit
