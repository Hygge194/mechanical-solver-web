@echo off

:loop
echo ===== Checking for updates =====

git fetch

timeout /t 86400 >nul
goto loop