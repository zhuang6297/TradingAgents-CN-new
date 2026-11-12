#!/usr/bin/env python3
"""
调试导入问题
"""

import sys
import os

print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print(f"当前目录: {os.getcwd()}")
print(f"sys.path: {sys.path}")

# 检查是否可以导入langchain_nvidia_ai_endpoints
try:
    import langchain_nvidia_ai_endpoints
    print(f"✅ langchain_nvidia_ai_endpoints 版本: {langchain_nvidia_ai_endpoints.__version__}")
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    print("✅ ChatNVIDIA 导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    # 尝试查找包的位置
    import importlib.util
    spec = importlib.util.find_spec("langchain_nvidia_ai_endpoints")
    if spec:
        print(f"包规格: {spec}")
        print(f"包位置: {spec.origin}")
    else:
        print("找不到包规格")

print("\n🏁 调试完成")
