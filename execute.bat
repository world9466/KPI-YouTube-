python channel_KPI.py 2>error.log
if %errorlevel% neq 0 pause exit
timeout /t 2

python program_KPI.py 2>error.log
if %errorlevel% neq 0 pause exit
timeout /t 2

python online_people.py 2>error.log
if %errorlevel% equ 0 (del /q error.log)
timeout /t 5