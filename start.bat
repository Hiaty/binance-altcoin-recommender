@echo off
chcp 65001 >nul
echo ==========================================
echo 币安山寨币智能推荐系统
echo ==========================================
echo.
echo 正在启动后台服务...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 检查依赖...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖检查完成
echo.

REM 启动服务
echo [2/3] 启动后台服务...
echo [3/3] 服务已启动，请在浏览器访问: http://localhost:5000
echo.
echo 按Ctrl+C停止服务
echo ==========================================
python src/app.py

pause
