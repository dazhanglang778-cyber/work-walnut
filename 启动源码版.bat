@echo off
setlocal
cd /d "%~dp0"
python app\wallnut_pet.py
if errorlevel 1 (
  echo.
  echo 启动失败。请确认已安装 Python 3.10 或更高版本，并执行：
  echo python -m pip install -r requirements.txt
  echo.
  pause
)

