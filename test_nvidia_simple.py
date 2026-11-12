#!/usr/bin/env python3
"""
简单测试 NVIDIA API 接入功能
"""

import os
import sys
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# 检查环境变量
nvidia_api_key = os.getenv("NVIDIA_API_KEY")

if not nvidia_api_key:
    print("⚠️ NVIDIA_API_KEY 环境变量未设置")
    print("请先设置 NVIDIA_API_KEY 环境变量")
    print("获取 API 密钥的方法：")
    print("1. 访问 https://build.nvidia.com/")
    print("2. 创建免费账户并登录")
    print("3. 点击个人资料图标 → API Keys → Generate API Key")
    print("4. 复制生成的密钥并设置为 NVIDIA_API_KEY 环境变量")
    sys.exit(1)

print("✅ NVIDIA_API_KEY 环境变量已设置")
print("\n🧪 测试 NVIDIA API 连接...")

try:
    # 创建 NVIDIA 客户端
    llm = ChatNVIDIA(
        model="nvidia/llama-3.1-nemotron-8b-instruct",
        api_key=nvidia_api_key,
        temperature=0.1,
        max_tokens=100
    )
    
    print("✅ NVIDIA 客户端创建成功")
    print(f"   模型: {llm.model}")
    
    # 发送测试消息
    print("\n📝 发送测试消息...")
    response = llm.invoke("你好，请简单介绍一下你自己。")
    
    if response and hasattr(response, 'content') and response.content:
        print("✅ 测试消息响应成功")
        print(f"   响应: {response.content}")
        print("\n🎉 NVIDIA API 接入测试成功！")
    else:
        print("❌ 测试消息响应为空")
        
except Exception as e:
    print(f"❌ NVIDIA API 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 测试完成")
