python videoID_search.py 2>error.log
if %errorlevel% neq 0 pause exit
if %errorlevel% equ 0 (del /q error.log)
timeout /t 5