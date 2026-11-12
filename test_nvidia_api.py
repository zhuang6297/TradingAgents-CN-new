#!/usr/bin/env python3
"""
测试 NVIDIA API 接入功能
"""

import os
import sys
from tradingagents.llm_adapters import (
    test_nvidia_openai_connection,
    test_nvidia_openai_function_calling,
    get_available_nvidia_models
)

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('test_nvidia_api')

def main():
    """测试 NVIDIA API 接入功能"""
    logger.info(f"\n🧪 开始测试 NVIDIA API 接入功能")
    logger.info(f"=" * 60)
    
    # 检查环境变量
    nvidia_api_key = os.getenv("NVIDIA_API_KEY")
    if not nvidia_api_key:
        logger.warning(f"⚠️ NVIDIA_API_KEY 环境变量未设置")
        logger.warning(f"请先设置 NVIDIA_API_KEY 环境变量，或在测试时传入")
        logger.warning(f"获取 API 密钥的方法：")
        logger.warning(f"1. 访问 https://build.nvidia.com/")
        logger.warning(f"2. 创建免费账户并登录")
        logger.warning(f"3. 点击个人资料图标 → API Keys → Generate API Key")
        logger.warning(f"4. 复制生成的密钥并设置为 NVIDIA_API_KEY 环境变量")
    else:
        logger.info(f"✅ NVIDIA_API_KEY 环境变量已设置")
    
    # 显示可用的 NVIDIA 模型
    logger.info(f"\n📋 可用的 NVIDIA 模型：")
    logger.info(f"-" * 60)
    
    try:
        models = get_available_nvidia_models()
        for model_name, model_info in models.items():
            logger.info(f"📦 模型: {model_name}")
            logger.info(f"   描述: {model_info.get('description', '无描述')}")
            logger.info(f"   上下文长度: {model_info.get('context_length', '未知')}")
            logger.info(f"   支持函数调用: {model_info.get('supports_function_calling', False)}")
            logger.info(f"   推荐用途: {', '.join(model_info.get('recommended_for', ['通用任务']))}")
            logger.info(f"")
    except Exception as e:
        logger.error(f"❌ 获取模型列表失败: {e}")
    
    # 测试连接
    logger.info(f"\n🔌 测试 NVIDIA API 连接")
    logger.info(f"-" * 60)
    
    try:
        connection_ok = test_nvidia_openai_connection()
        if connection_ok:
            logger.info(f"✅ NVIDIA API 连接测试通过")
        else:
            logger.error(f"❌ NVIDIA API 连接测试失败")
    except Exception as e:
        logger.error(f"❌ 连接测试异常: {e}")
    
    # 测试函数调用
    logger.info(f"\n🧰 测试 NVIDIA API 函数调用")
    logger.info(f"-" * 60)
    
    try:
        function_calling_ok = test_nvidia_openai_function_calling()
        if function_calling_ok:
            logger.info(f"✅ NVIDIA API 函数调用测试通过")
        else:
            logger.error(f"❌ NVIDIA API 函数调用测试失败")
    except Exception as e:
        logger.error(f"❌ 函数调用测试异常: {e}")
    
    logger.info(f"\n🏁 测试完成")
    logger.info(f"=" * 60)
    
    # 总结
    if 'connection_ok' in locals() and connection_ok:
        logger.info(f"🎉 NVIDIA API 接入功能测试成功！")
        logger.info(f"\n📝 接下来可以：")
        logger.info(f"1. 在配置文件中设置默认使用 NVIDIA 模型")
        logger.info(f"2. 在代码中使用 create_nvidia_openai_llm() 创建 LLM 实例")
        logger.info(f"3. 开始使用 NVIDIA AI 模型进行交易分析")
    else:
        logger.info(f"⚠️ NVIDIA API 接入功能测试未完全通过")
        logger.info(f"请检查 NVIDIA_API_KEY 是否正确设置，以及网络连接是否正常")

if __name__ == "__main__":
    main()
