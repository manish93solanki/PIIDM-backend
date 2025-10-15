@echo off
echo Installing PIIDM Backend...

REM Create virtual environment
python -m venv .venv

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Set Flask app
set FLASK_APP=app.py

REM Run database migrations
flask db upgrade

echo Installation complete!
echo Run 'start.bat' to start the application
