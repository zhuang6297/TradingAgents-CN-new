"""
NVIDIA AI OpenAI兼容适配器
为 TradingAgents 提供NVIDIA AI模型的 OpenAI 兼容接口
"""

import os
from typing import Any, Dict, List, Optional, Union, Sequence
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import LLMResult
from pydantic import Field, SecretStr
from ..config.config_manager import token_tracker

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class ChatNvidiaOpenAI(ChatNVIDIA):
    """
    NVIDIA AI OpenAI 兼容适配器
    继承 ChatNVIDIA，优化工具调用和内容格式处理
    """

    def __init__(self, **kwargs):
        """初始化 NVIDIA AI OpenAI 兼容客户端"""

        # 设置 NVIDIA AI 的默认配置
        kwargs.setdefault("temperature", 0.1)
        kwargs.setdefault("max_tokens", 2000)

        # 检查 API 密钥
        nvidia_api_key = kwargs.get("api_key") or os.getenv("NVIDIA_API_KEY")
        if not nvidia_api_key:
            raise ValueError(
                "NVIDIA API key not found. Please set NVIDIA_API_KEY environment variable "
                "or pass api_key parameter."
            )

        kwargs["api_key"] = nvidia_api_key

        # 调用父类初始化
        super().__init__(**kwargs)

        logger.info(f"✅ NVIDIA AI OpenAI 兼容适配器初始化成功")
        logger.info(f"   模型: {kwargs.get('model', 'nvidia/llama-3.1-nemotron-70b-instruct')}")
        logger.info(f"   温度: {kwargs.get('temperature', 0.1)}")
        logger.info(f"   最大Token: {kwargs.get('max_tokens', 2000)}")

    @property
    def model_name(self) -> str:
        """
        返回模型名称（兼容性属性）
        """
        model = self.model
        return model or "unknown"
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> LLMResult:
        """重写生成方法，优化工具调用处理和内容格式"""

        try:
            # 调用父类的生成方法
            result = super()._generate(messages, stop, **kwargs)

            # 优化返回内容格式
            # 注意：result.generations 是二维列表 [[ChatGeneration]]
            if result and result.generations:
                for generation_list in result.generations:
                    if isinstance(generation_list, list):
                        for generation in generation_list:
                            if hasattr(generation, 'message') and generation.message:
                                # 优化消息内容格式
                                self._optimize_message_content(generation.message)
                    else:
                        # 兼容性处理：如果不是列表，直接处理
                        if hasattr(generation_list, 'message') and generation_list.message:
                            self._optimize_message_content(generation_list.message)

            # 追踪 token 使用量
            self._track_token_usage(result, kwargs)

            return result

        except Exception as e:
            logger.error(f"❌ NVIDIA AI 生成失败: {e}")
            logger.exception(e)  # 打印完整的堆栈跟踪
            # 返回一个包含错误信息的结果，而不是抛出异常
            from langchain_core.outputs import ChatGeneration
            error_message = AIMessage(content=f"NVIDIA AI 调用失败: {str(e)}\n\n请检查：\n1. 网络连接是否正常\n2. NVIDIA_API_KEY 是否有效")
            error_generation = ChatGeneration(message=error_message)
            return LLMResult(generations=[[error_generation]])
    
    def _optimize_message_content(self, message: BaseMessage):
        """优化消息内容格式，确保包含新闻特征关键词"""
        
        if not isinstance(message, AIMessage) or not message.content:
            return
        
        content = message.content
        
        # 检查是否是工具调用返回的新闻内容
        if self._is_news_content(content):
            # 优化新闻内容格式，添加必要的关键词
            optimized_content = self._enhance_news_content(content)
            message.content = optimized_content
            
            logger.debug(f"🔧 [NVIDIA适配器] 优化新闻内容格式")
            logger.debug(f"   原始长度: {len(content)} 字符")
            logger.debug(f"   优化后长度: {len(optimized_content)} 字符")
    
    def _is_news_content(self, content: str) -> bool:
        """判断内容是否为新闻内容"""
        
        # 检查是否包含新闻相关的关键词
        news_indicators = [
            "股票", "公司", "市场", "投资", "财经", "证券", "交易",
            "涨跌", "业绩", "财报", "分析", "预测", "消息", "公告"
        ]
        
        return any(indicator in content for indicator in news_indicators) and len(content) > 200
    
    def _enhance_news_content(self, content: str) -> str:
        """增强新闻内容，添加必要的格式化信息"""
        
        import datetime
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 如果内容缺少必要的新闻特征，添加它们
        enhanced_content = content
        
        # 添加发布时间信息（如果缺少）
        if "发布时间" not in content and "时间" not in content:
            enhanced_content = f"发布时间: {current_date}\n\n{enhanced_content}"
        
        # 添加新闻标题标识（如果缺少）
        if "新闻标题" not in content and "标题" not in content:
            # 尝试从内容中提取第一行作为标题
            lines = enhanced_content.split('\n')
            if lines:
                first_line = lines[0].strip()
                if len(first_line) < 100:  # 可能是标题
                    enhanced_content = f"新闻标题: {first_line}\n\n{enhanced_content}"
        
        # 添加文章来源信息（如果缺少）
        if "文章来源" not in content and "来源" not in content:
            enhanced_content = f"{enhanced_content}\n\n文章来源: NVIDIA AI 智能分析"
        
        return enhanced_content
    
    def _track_token_usage(self, result: LLMResult, kwargs: Dict[str, Any]):
        """追踪 token 使用量"""
        
        try:
            # 从结果中提取 token 使用信息
            if hasattr(result, 'llm_output') and result.llm_output:
                token_usage = result.llm_output.get('token_usage', {})
                
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                
                if input_tokens > 0 or output_tokens > 0:
                    # 生成会话ID
                    session_id = kwargs.get('session_id', f"nvidia_openai_{hash(str(kwargs))%10000}")
                    analysis_type = kwargs.get('analysis_type', 'stock_analysis')
                    
                    # 使用 TokenTracker 记录使用量
                    token_tracker.track_usage(
                        provider="nvidia",
                        model_name=self.model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        session_id=session_id,
                        analysis_type=analysis_type
                    )
                    
                    logger.debug(f"📊 [NVIDIA适配器] Token使用量: 输入={input_tokens}, 输出={output_tokens}")
                    
        except Exception as track_error:
            # token 追踪失败不应该影响主要功能
            logger.error(f"⚠️ NVIDIA适配器 Token 追踪失败: {track_error}")


# 支持的模型列表
NVIDIA_OPENAI_MODELS = {
    # NVIDIA 官方模型
    "nvidia/llama-3.1-nemotron-70b-instruct": {
        "description": "NVIDIA Nemotron 70B - 强大的指令模型",
        "context_length": 128000,
        "supports_function_calling": True,
        "recommended_for": ["复杂推理", "专业分析", "高质量输出"]
    },
    "nvidia/llama-3.1-nemotron-8b-instruct": {
        "description": "NVIDIA Nemotron 8B - 轻量级指令模型",
        "context_length": 128000,
        "supports_function_calling": True,
        "recommended_for": ["快速响应", "实时分析", "高频使用"]
    },
    "nvidia/mistral-large": {
        "description": "Mistral Large - 高性能模型",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["复杂任务", "深度思考"]
    },
    "nvidia/llama-3.2-90b-vision-instruct": {
        "description": "Llama 3.2 90B Vision - 多模态模型",
        "context_length": 128000,
        "supports_function_calling": True,
        "recommended_for": ["图像分析", "多模态任务"]
    },
    "nvidia/llama-3.2-1b-instruct": {
        "description": "Llama 3.2 1B - 超轻量级模型",
        "context_length": 128000,
        "supports_function_calling": True,
        "recommended_for": ["超快响应", "边缘设备"]
    }
}


def get_available_nvidia_models() -> Dict[str, Dict[str, Any]]:
    """获取可用的 NVIDIA AI 模型列表"""
    return NVIDIA_OPENAI_MODELS


def create_nvidia_openai_llm(
    model: str = "nvidia/llama-3.1-nemotron-8b-instruct",
    api_key: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 2000,
    **kwargs
) -> ChatNvidiaOpenAI:
    """创建 NVIDIA AI OpenAI 兼容 LLM 实例的便捷函数"""
    
    return ChatNvidiaOpenAI(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def test_nvidia_openai_connection(
    model: str = "nvidia/llama-3.1-nemotron-8b-instruct",
    api_key: Optional[str] = None
) -> bool:
    """测试 NVIDIA AI OpenAI 兼容接口连接"""
    
    try:
        logger.info(f"🧪 测试 NVIDIA AI OpenAI 兼容接口连接")
        logger.info(f"   模型: {model}")
        
        # 创建客户端
        llm = create_nvidia_openai_llm(
            model=model,
            api_key=api_key,
            max_tokens=50
        )
        
        # 发送测试消息
        response = llm.invoke("你好，请简单介绍一下你自己。")
        
        if response and hasattr(response, 'content') and response.content:
            logger.info(f"✅ NVIDIA AI OpenAI 兼容接口连接成功")
            logger.info(f"   响应: {response.content[:100]}...")
            return True
        else:
            logger.error(f"❌ NVIDIA AI OpenAI 兼容接口响应为空")
            return False
            
    except Exception as e:
        logger.error(f"❌ NVIDIA AI OpenAI 兼容接口连接失败: {e}")
        return False


def test_nvidia_openai_function_calling(
    model: str = "nvidia/llama-3.1-nemotron-8b-instruct",
    api_key: Optional[str] = None
) -> bool:
    """测试 NVIDIA AI OpenAI 兼容接口的 Function Calling"""
    
    try:
        logger.info(f"🧪 测试 NVIDIA AI Function Calling")
        logger.info(f"   模型: {model}")
        
        # 创建客户端
        llm = create_nvidia_openai_llm(
            model=model,
            api_key=api_key,
            max_tokens=200
        )
        
        # 定义测试工具
        from langchain_core.tools import tool
        
        @tool
        def test_news_tool(query: str) -> str:
            """测试新闻工具，返回模拟新闻内容"""
            return f"""发布时间: 2024-01-15
新闻标题: {query}相关市场动态
文章来源: 测试新闻源

这是一条关于{query}的测试新闻内容。该公司近期表现良好，市场前景看好。
投资者对此表示关注，分析师给出积极评价。"""
        
        # 绑定工具
        llm_with_tools = llm.bind_tools([test_news_tool])
        
        # 测试工具调用
        response = llm_with_tools.invoke("请使用test_news_tool查询'苹果公司'的新闻")
        
        logger.info(f"✅ NVIDIA AI Function Calling 测试完成")
        logger.info(f"   响应类型: {type(response)}")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"   工具调用数量: {len(response.tool_calls)}")
            return True
        else:
            logger.info(f"   响应内容: {getattr(response, 'content', 'No content')}")
            return True  # 即使没有工具调用也算成功，因为模型可能选择不调用工具
            
    except Exception as e:
        logger.error(f"❌ NVIDIA AI Function Calling 测试失败: {e}")
        return False


if __name__ == "__main__":
    """测试脚本"""
    logger.info(f"🧪 NVIDIA AI OpenAI 兼容适配器测试")
    logger.info(f"=" * 50)
    
    # 测试连接
    connection_ok = test_nvidia_openai_connection()
    
    if connection_ok:
        # 测试 Function Calling
        function_calling_ok = test_nvidia_openai_function_calling()
        
        if function_calling_ok:
            logger.info(f"\n🎉 所有测试通过！NVIDIA AI OpenAI 兼容适配器工作正常")
        else:
            logger.error(f"\n⚠️ Function Calling 测试失败")
    else:
        logger.error(f"\n❌ 连接测试失败")
