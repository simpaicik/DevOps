@echo off
REM GymLog: sanal ortam kurar, bagimliliklari yukler, uygulamayi baslatir.
cd /d "%~dp0"
if not exist .venv (
  echo Sanal ortam olusturuluyor...
  python -m venv .venv || (echo Python bulunamadi. && pause && exit /b 1)
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
start "" http://127.0.0.1:5000
echo GymLog calisiyor: http://127.0.0.1:5000  (durdurmak icin Ctrl+C)
flask --app gymlog run
pause
