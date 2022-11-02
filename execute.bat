python channel_KPI.py>error.log

python videoID_search.py>error.log
if %errorlevel% equ 0 (del /q error.log)
timeout /t 5