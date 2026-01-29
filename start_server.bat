@echo off
echo ====================================
echo  Crsh Macro Analytics Server
echo ====================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server...
echo Dashboard will be available at: http://localhost:8000
echo.
python main.py
pause
