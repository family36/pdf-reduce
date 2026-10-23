@echo off
rem Usage: reduce.bat [low^|medium^|high]   (default: medium)
cd /d "%~dp0"
set PYTHONUTF8=1

where python >nul 2>nul
if errorlevel 1 (
    echo Python not found. Please install Python from https://www.python.org/
    pause
    exit /b 1
)

python -c "import pymupdf" >nul 2>nul
if errorlevel 1 (
    echo Installing PyMuPDF...
    python -m pip install --user pymupdf
)

python "%~dp0reduce_pdf.py" %*
pause
