#!/usr/bin/env python3
"""
TradingAgents-CN 服务监控脚本
自动检测服务状态并在服务不可用时重启
"""

import os
import sys
import time
import subprocess
import socket
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "service_monitor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('service_monitor')

# 配置
CONFIG = {
    'host': 'localhost',
    'port': 8502,
    'check_interval': 30,  # 检查间隔（秒）
    'max_failures': 2,     # 连续失败次数才重启
    'start_delay': 5,      # 启动后等待时间（秒）
    'project_root': Path(__file__).parent,
    'start_script': 'start_web.py'
}


def check_service(host='localhost', port=8502, timeout=5):
    """
    检查服务是否可用
    
    Args:
        host: 主机地址
        port: 端口号
        timeout: 超时时间（秒）
        
    Returns:
        bool: 服务是否可用
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"检查服务时出错: {e}")
        return False


def start_service():
    """
    启动服务
    
    Returns:
        subprocess.Popen: 启动的进程对象
    """
    try:
        project_root = CONFIG['project_root']
        start_script = project_root / CONFIG['start_script']
        
        if not start_script.exists():
            logger.error(f"启动脚本不存在: {start_script}")
            return None
        
        # 设置环境变量
        env = os.environ.copy()
        current_path = env.get('PYTHONPATH', '')
        if current_path:
            env['PYTHONPATH'] = f"{project_root}{os.pathsep}{current_path}"
        else:
            env['PYTHONPATH'] = str(project_root)
        
        logger.info(f"正在启动服务...")
        logger.info(f"工作目录: {project_root}")
        logger.info(f"启动脚本: {start_script}")
        
        # 启动服务
        process = subprocess.Popen(
            [sys.executable, str(start_script)],
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        logger.info(f"服务进程已启动，PID: {process.pid}")
        return process
        
    except Exception as e:
        logger.error(f"启动服务失败: {e}")
        return None


def kill_existing_service(port=8502):
    """
    终止占用指定端口的进程
    
    Args:
        port: 端口号
    """
    try:
        if os.name == 'nt':  # Windows
            # 使用netstat查找占用端口的进程
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        logger.info(f"发现占用端口 {port} 的进程，PID: {pid}")
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                            logger.info(f"已终止进程 {pid}")
                            time.sleep(2)  # 等待进程完全终止
                        except subprocess.CalledProcessError:
                            logger.warning(f"无法终止进程 {pid}")
        else:  # Linux/Mac
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                pid = result.stdout.strip()
                logger.info(f"发现占用端口 {port} 的进程，PID: {pid}")
                try:
                    subprocess.run(['kill', '-9', pid], check=True)
                    logger.info(f"已终止进程 {pid}")
                    time.sleep(2)
                except subprocess.CalledProcessError:
                    logger.warning(f"无法终止进程 {pid}")
                    
    except Exception as e:
        logger.error(f"终止进程时出错: {e}")


def monitor_loop():
    """
    主监控循环
    """
    logger.info("=" * 60)
    logger.info("TradingAgents-CN 服务监控启动")
    logger.info("=" * 60)
    logger.info(f"监控地址: {CONFIG['host']}:{CONFIG['port']}")
    logger.info(f"检查间隔: {CONFIG['check_interval']}秒")
    logger.info(f"最大失败次数: {CONFIG['max_failures']}")
    logger.info("=" * 60)
    
    service_process = None
    consecutive_failures = 0
    last_restart_time = None
    restart_count = 0
    
    # 初始启动
    logger.info("正在初始启动服务...")
    kill_existing_service(CONFIG['port'])
    service_process = start_service()
    
    if service_process:
        logger.info(f"等待服务启动（{CONFIG['start_delay']}秒）...")
        time.sleep(CONFIG['start_delay'])
        last_restart_time = datetime.now()
    else:
        logger.error("初始启动失败")
        return
    
    try:
        while True:
            # 检查服务状态
            is_running = check_service(CONFIG['host'], CONFIG['port'])
            
            if is_running:
                if consecutive_failures > 0:
                    logger.info(f"服务已恢复正常（连续失败{consecutive_failures}次后）")
                    consecutive_failures = 0
                else:
                    logger.debug("服务运行正常")
            else:
                consecutive_failures += 1
                logger.warning(f"服务不可用（连续失败{consecutive_failures}次）")
                
                if consecutive_failures >= CONFIG['max_failures']:
                    logger.error(f"服务连续失败{consecutive_failures}次，准备重启...")
                    
                    # 终止现有进程
                    if service_process:
                        logger.info("终止现有服务进程...")
                        try:
                            service_process.terminate()
                            service_process.wait(timeout=5)
                        except:
                            try:
                                service_process.kill()
                            except:
                                pass
                    
                    # 确保端口被释放
                    kill_existing_service(CONFIG['port'])
                    
                    # 重新启动服务
                    logger.info("重新启动服务...")
                    service_process = start_service()
                    
                    if service_process:
                        logger.info(f"等待服务启动（{CONFIG['start_delay']}秒）...")
                        time.sleep(CONFIG['start_delay'])
                        
                        # 验证启动是否成功
                        if check_service(CONFIG['host'], CONFIG['port']):
                            logger.info("服务重启成功！")
                            consecutive_failures = 0
                            restart_count += 1
                            last_restart_time = datetime.now()
                        else:
                            logger.error("服务重启后仍不可用")
                    else:
                        logger.error("服务重启失败")
            
            # 显示状态信息
            if restart_count > 0 and (restart_count % 10 == 0 or consecutive_failures > 0):
                logger.info(f"统计信息: 已重启{restart_count}次，最后重启时间: {last_restart_time}")
            
            # 等待下一次检查
            time.sleep(CONFIG['check_interval'])
            
    except KeyboardInterrupt:
        logger.info("=" * 60)
        logger.info("服务监控已停止（用户中断）")
        logger.info(f"统计: 总共重启{restart_count}次")
        logger.info("=" * 60)
        
        # 清理进程
        if service_process:
            try:
                service_process.terminate()
                service_process.wait(timeout=5)
            except:
                pass
                
    except Exception as e:
        logger.error(f="监控循环出错: {e}", exc_info=True)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TradingAgents-CN 服务监控')
    parser.add_argument('--interval', '-i', type=int, default=30,
                        help='检查间隔（秒），默认30秒')
    parser.add_argument('--max-failures', '-f', type=int, default=2,
                        help='最大失败次数，默认2次')
    parser.add_argument('--daemon', '-d', action='store_true',
                        help='以守护进程模式运行（后台运行）')
    
    args = parser.parse_args()
    
    # 更新配置
    CONFIG['check_interval'] = args.interval
    CONFIG['max_failures'] = args.max_failures
    
    if args.daemon and os.name != 'nt':
        # Linux/Mac 守护进程模式
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            logger.error(f"创建守护进程失败: {e}")
            sys.exit(1)
        
        os.chdir('/')
        os.setsid()
        os.umask(0)
        
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            logger.error(f"创建守护进程失败: {e}")
            sys.exit(1)
        
        # 重定向标准输入输出
        sys.stdout.flush()
        sys.stderr.flush()
        
        with open('/dev/null', 'r') as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())
    
    # 启动监控
    monitor_loop()


if __name__ == "__main__":
    main()
