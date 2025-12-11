@echo off
REM Batch script to activate the UV virtual environment
REM Usage: activate.bat

set "PATH=C:\Users\spenc\.local\bin;%PATH%"
call .venv\Scripts\activate.bat

echo Virtual environment activated!
python --version
uv --version



