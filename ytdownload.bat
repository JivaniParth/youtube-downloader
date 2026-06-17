@echo off
rem Portable launcher for the YouTube Downloader CLI.
rem Resolves paths relative to this file's own location (%~dp0),
rem so it keeps working even if the project folder is moved/renamed,
rem as long as this .bat stays in the project root next to main.py and venv\.

setlocal
set "SCRIPT_DIR=%~dp0"

if not exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    echo Could not find venv\Scripts\python.exe next to this script.
    echo Make sure ytdownload.bat stays in the project root folder.
    exit /b 1
)

"%SCRIPT_DIR%venv\Scripts\python.exe" "%SCRIPT_DIR%main.py" %*
endlocal
