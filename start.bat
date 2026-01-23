@echo off
cd /d "D:\Festplatte D\Programmieren\project_gpt_timestamp\script\gpt_time_stamp-1"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python src/gpt_time_stamp/app.py
pause
