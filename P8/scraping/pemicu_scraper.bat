@echo off
cd /d "%~dp0"

echo Menjalankan Script Otomasi Scraper STIKOM...

call ..\..\.venv\Scripts\activate
python index.py
deactivate

echo Selesai!
pause
