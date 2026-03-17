@echo off
chcp 65001 >nul
title 币安山寨币智能推荐系统 - 环境检查
color 0A

echo.
echo  ============================================
echo    币安山寨币智能推荐系统
echo  ============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo  [警告] 未检测到Python环境
    echo.
    echo  正在尝试使用内置Python...
    echo.
    
    REM 检查是否有内置Python
    if exist "python\python.exe" (
        echo  [OK] 找到内置Python
        set PYTHON=python\python.exe
    ) else (
        echo  [错误] 未找到Python环境
        echo.
        echo  请安装Python 3.8或更高版本：
        echo  https://www.python.org/downloads/
        echo.
        echo  安装时请务必勾选 "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
) else (
    echo  [OK] Python环境已就绪
    set PYTHON=python
)

echo.
echo  [1/3] 检查依赖...
%PYTHON% -m pip install -q -r backend/requirements.txt
if errorlevel 1 (
    echo  [错误] 依赖安装失败
    pause
    exit /b 1
)
echo  [OK] 依赖检查完成

echo.
echo  [2/3] 启动后端服务...
echo.

REM 启动服务
%PYTHON% start.py

pause
