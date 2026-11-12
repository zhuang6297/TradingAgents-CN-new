#!/usr/bin/env python3
"""
测试股票数据获取
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.utils.stock_validator import prepare_stock_data
from tradingagents.dataflows.data_source_manager import get_data_source_manager

# 测试股票 000539
try:
    print("=== 测试股票验证 ===")
    result = prepare_stock_data('000539', 'A股')
    print(f"验证结果: {result.is_valid}")
    print(f"错误信息: {result.error_message}")
    print(f"股票名称: {result.stock_name}")
    print(f"缓存状态: {result.cache_status}")
    
    print("\n=== 测试数据源管理器 ===")
    manager = get_data_source_manager()
    print(f"当前数据源: {manager.get_current_source().value}")
    print(f"可用数据源: {[s.value for s in manager.available_sources]}")
    
    # 测试获取数据
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"\n=== 测试获取数据 ({start_date} 到 {end_date}) ===")
    data = manager.get_stock_data('000539', start_date, end_date)
    print(f"数据获取结果长度: {len(data)}")
    print(f"数据预览: {data[:500]}...")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
