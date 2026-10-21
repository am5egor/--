@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul && (py -3 launcher.py) || (python launcher.py)
if errorlevel 1 pause
