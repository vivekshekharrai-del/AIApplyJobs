@echo off
setlocal
set APPLYPILOT_DIR=%~dp0
set APPLYPILOT_DIR=%APPLYPILOT_DIR:~0,-1%
call "%~dp0venv\Scripts\activate.bat"
applypilot %*
