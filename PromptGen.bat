@echo off
:: Path to the virtual environment
set VENV_PATH=.\.venv

:: Activate the virtual environment
call %VENV_PATH%\Scripts\activate

:: Run the Python script
python main.py

:: Deactivate the virtual environment
deactivate
