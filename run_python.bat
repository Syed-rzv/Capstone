@echo off
REM Activate the virtual environment inside crisislens-API
call "%~dp0crisislens-API\venv\Scripts\activate.bat"

REM Run the python command with all arguments passed to this batch file
python %*

REM Deactivate the virtual environment
deactivate
