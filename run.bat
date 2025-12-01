@echo off
cd /d "%~dp0"
echo ================================================
echo  PLAY BEACH TENNIS - SISTEMA FLASK EM EXECUÇÃO
echo ================================================
echo.

REM Ativa o ambiente virtual
call venv\Scripts\activate

REM Executa o app Python
echo Iniciando servidor Flask...
python app.py

REM Mantém a janela aberta se houver erro
pause