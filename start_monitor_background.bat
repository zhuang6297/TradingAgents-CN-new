@echo off
chcp 65001 >nul
title TradingAgents-CN 服务监控 (后台模式)

echo ==========================================
echo TradingAgents-CN 服务监控启动器 (后台模式)
echo ==========================================
echo.
echo 监控服务将在后台运行，不显示窗口
echo 日志文件: logs/service_monitor.log
echo.
echo 停止方法:
echo 1. 打开任务管理器，结束 python.exe 进程
echo 2. 或者运行 stop_monitor.bat
echo ==========================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 使用vbscript在后台运行Python脚本，不显示窗口
cd /d "%~dp0"

REM 创建临时vbscript文件
echo Set WshShell = CreateObject("WScript.Shell") > "%temp%\start_monitor.vbs"
echo WshShell.Run "python ""%~dp0service_monitor.py""", 0, False >> "%temp%\start_monitor.vbs"
echo Set WshShell = Nothing >> "%temp%\start_monitor.vbs"

REM 执行vbscript
wscript "%temp%\start_monitor.vbs"

REM 删除临时文件
del "%temp%\start_monitor.vbs" 2>nul

echo 监控服务已在后台启动
echo 查看日志: logs/service_monitor.log
echo.
pause
