@echo off
chcp 65001 >nul
title TradingAgents-CN 服务监控

echo ==========================================
echo TradingAgents-CN 服务监控启动器
echo ==========================================
echo.
echo 功能说明:
echo - 自动检测服务状态 (每30秒检查一次)
echo - 服务不可用时自动重启
echo - 记录所有操作到 logs/service_monitor.log
echo.
echo 使用方法:
echo - 直接运行: 前台运行，显示实时日志
echo - 后台运行: 使用 start_monitor_background.bat
echo.
echo 按 Ctrl+C 停止监控
echo ==========================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 启动监控服务
cd /d "%~dp0"
python service_monitor.py

pause
