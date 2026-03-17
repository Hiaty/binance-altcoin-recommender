@echo off
chcp 65001 >nul
title 币安山寨币智能推荐系统
color 0A

echo.
echo  ============================================
echo    币安山寨币智能推荐系统
echo  ============================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [错误] 未检测到Python!
    echo.
    echo  请先安装Python 3.8或更高版本:
    echo  https://www.python.org/downloads/
    echo.
    echo  安装时请务必勾选 "Add Python to PATH"
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo  [1/3] Python已就绪
echo.

REM 安装依赖
echo  [2/3] 检查依赖...
python -m pip install -q -r backend/requirements.txt
if errorlevel 1 (
    echo  [错误] 依赖安装失败
    pause
    exit /b 1
)
echo  [OK] 依赖已安装
echo.

REM 启动服务
echo  [3/3] 启动服务...
echo.
echo  服务启动后，浏览器会自动打开
echo  请稍候...
echo.

python backend/app.py

pause
