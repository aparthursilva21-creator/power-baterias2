@echo off
title Sistema Power Baterias
cd /d "%~dp0"
echo A iniciar o Sistema Power Baterias...
python -m streamlit run app.py
pause