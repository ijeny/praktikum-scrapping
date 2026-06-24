@echo off 

:: Mengatur direktori kerja ke lokasi file bat ini berada 

cd /d "%~dp0" 

echo Menjalankan Script Otomasi Scraper STIKOM... 

:: Mengaktifkan virtual environment (pastikan folder venv ada di dalam folder yang sama) 

call venv\Scripts\activate 

:: Menjalankan file Python 

python index.py 

:: Menutup virtual environment 

deactivate 

echo Selesai! 

Pause 