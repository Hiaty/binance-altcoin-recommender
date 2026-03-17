@echo off
chcp 65001 >nul
title 币安山寨币智能推荐系统 - 一键安装
color 0A
cls

echo.
echo  ============================================
echo    币安山寨币智能推荐系统
echo    一键安装启动器
echo  ============================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [X] 未检测到Python
    echo.
    echo  ============================================
    echo    请先安装Python 3.8或更高版本
    echo  ============================================
    echo.
    echo  安装步骤：
    echo  1. 访问 https://www.python.org/downloads/
    echo  2. 点击 "Download Python 3.11.x"
    echo  3. 下载后双击安装
    echo  4. 【重要】勾选 "Add Python to PATH"
    echo  5. 点击 "Install Now"
    echo.
    echo  安装完成后，重新运行此文件
    echo.
    echo  是否现在打开Python下载页面？(Y/N)
    set /p openpage=
    if /i "%openpage%"=="Y" (
        start https://www.python.org/downloads/
    )
    pause
    exit /b 1
)

echo  [OK] Python已安装
python --version
echo.

REM 安装依赖
echo  [1/3] 正在安装依赖（首次需要几分钟）...
echo  如果卡住请耐心等待...
python -m pip install -q --upgrade pip
python -m pip install -q -r backend/requirements.txt
if errorlevel 1 (
    echo  [X] 依赖安装失败
    echo  请检查网络连接
    pause
    exit /b 1
)
echo  [OK] 依赖安装完成
echo.

REM 启动服务
echo  [2/3] 正在启动服务...
echo  [3/3] 服务启动成功！
echo.
echo  ============================================
echo    系统已启动！
echo    浏览器将自动打开...
echo  ============================================
echo.
echo  如果浏览器没有自动打开，请手动访问：
echo  http://localhost:5000
echo.
echo  按 Ctrl+C 可以停止服务
echo.

REM 启动后端并打开浏览器
start http://localhost:5000
python backend/app.py

pause
