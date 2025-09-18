@echo off
REM Activate venv
call "C:\Capstone\crisislens-API\venv\Scripts\activate.bat"

REM Run forecast script with any args (like periods or anchor)
python "C:\Capstone\crisislens-API\forecast_service.py" --periods 30 --anchor

REM Pause or just exit
exit
