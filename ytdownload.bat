@echo off
rem Portable launcher for the YouTube Downloader CLI.
rem Resolves paths relative to this file's own location (%~dp0),
rem so it keeps working even if the project folder is moved/renamed,
rem as long as this .bat stays in the project root next to main.py.
rem
rem Prefers the project's venv if present; otherwise falls back to
rem whatever "python" is on PATH (make sure yt-dlp is installed there).

setlocal
set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Could not find a Python interpreter.
        echo Either create a venv here with "python -m venv venv" in %SCRIPT_DIR%,
        echo or make sure "python" is available on PATH.
        exit /b 1
    )
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" "%SCRIPT_DIR%main.py" %*
endlocal