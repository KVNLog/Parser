@echo off
chcp 866 >nul
setlocal

REM Define virtual environment name
set VENV_DIR=.venv

REM Check if virtual environment exists
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%

    REM Activate virtual environment
    call %VENV_DIR%\Scripts\activate

    REM Check if requirements.txt exists and install dependencies
    if exist requirements.txt (
        echo Installing dependencies from requirements.txt...
        pip install -r requirements.txt
    )
) else (
    REM Activate virtual environment
    call %VENV_DIR%\Scripts\activate
)

REM Run parser.py
echo Running parserZakupki.py...
python parserZakupki.py

REM Pause to keep console open
REM echo Press any key to exit...
REM pause

REM End process
deactivate
endlocal