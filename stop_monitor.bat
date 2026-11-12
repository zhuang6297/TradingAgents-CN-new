@echo off
chcp 65001 >nul
title TradingAgents-CN 停止监控

echo ==========================================
echo TradingAgents-CN 停止监控服务
echo ==========================================
echo.

REM 查找并终止 service_monitor.py 进程
echo 正在查找监控服务进程...

tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "service_monitor" >nul
if errorlevel 1 (
    echo 未找到正在运行的监控服务进程
) else (
    echo 找到监控服务进程，正在终止...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq TradingAgents-CN 服务监控*" 2>nul
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq TradingAgents-CN 服务监控 (后台模式)*" 2>nul
    echo 监控服务已停止
)

REM 同时检查并终止占用8502端口的进程
echo.
echo 检查端口 8502 占用情况...
netstat -ano | findstr ":8502" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo 端口 8502 未被占用
) else (
    echo 发现端口 8502 被占用，正在终止相关进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8502" ^| findstr "LISTENING"') do (
        echo 终止进程 PID: %%a
        taskkill /F /PID %%a 2>nul
    )
    echo 相关进程已终止
)

echo.
echo ==========================================
echo 操作完成
echo ==========================================
pause
