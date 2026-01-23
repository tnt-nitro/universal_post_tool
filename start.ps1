# PowerShell Startskript für GPT Time Stamp
Set-Location "D:\Festplatte D\Programmieren\project_gpt_timestamp\script\gpt_time_stamp-1"

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

python src/gpt_time_stamp/app.py

Read-Host "Drücken Sie Enter zum Beenden"
