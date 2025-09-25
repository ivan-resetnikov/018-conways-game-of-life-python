@echo off

:: Can later be changed to the venv's binary
set PYTHON_BIN="python"

cd src
%PYTHON_BIN% __main__.py
cd ..