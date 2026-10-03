@echo off
cd /d "%~dp0"
py -3 main.py
if errorlevel 1 (
  echo Could not launch. Install Python 3.11 or newer with Tcl/Tk support.
  pause
)
