@echo off
pushd %~dp0

:: Check if venv exists
IF EXIST .venv (
    :: Change to the .venv's Scripts directory
    pushd .venv\Scripts
    
    :: Run your script using this venv's python.exe
    python.exe ../../main.py
    popd
) ELSE (
    :: Run your script using the system's python
    python main.py
)

pause
