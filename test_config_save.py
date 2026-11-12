#!/usr/bin/env python3
"""
测试配置保存功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.config.config_manager import config_manager, ModelConfig

def test_save_models():
    """测试保存模型配置"""
    print("测试保存模型配置...")
    
    # 加载现有模型
    models = config_manager.load_models()
    print(f"现有模型数量: {len(models)}")
    
    # 修改第一个模型的API密钥
    if models:
        models[0].api_key = "test_api_key"
        models[0].enabled = True
        
        # 保存模型配置
        try:
            config_manager.save_models(models)
            print("✅ 模型配置保存成功！")
            
            # 重新加载模型配置
            reload_models = config_manager.load_models()
            print(f"重新加载后模型数量: {len(reload_models)}")
            if reload_models:
                print(f"第一个模型的API密钥: {reload_models[0].api_key}")
                print(f"第一个模型的启用状态: {reload_models[0].enabled}")
        except Exception as e:
            print(f"❌ 模型配置保存失败: {e}")
    else:
        print("❌ 没有找到模型配置")

def test_save_settings():
    """测试保存系统设置"""
    print("\n测试保存系统设置...")
    
    # 加载现有设置
    settings = config_manager.load_settings()
    print(f"现有设置: {settings.keys()}")
    
    # 修改设置
    settings["test_key"] = "test_value"
    
    # 保存设置
    try:
        config_manager.save_settings(settings)
        print("✅ 系统设置保存成功！")
        
        # 重新加载设置
        reload_settings = config_manager.load_settings()
        print(f"重新加载后设置: {reload_settings.get('test_key')}")
    except Exception as e:
        print(f"❌ 系统设置保存失败: {e}")

if __name__ == "__main__":
    test_save_models()
    test_save_settings()
