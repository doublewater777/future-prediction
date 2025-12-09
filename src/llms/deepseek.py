"""
DeepSeek LLM实现
使用DeepSeek API进行文本生成
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from .base import BaseLLM


class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM实现类"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥，如果不提供则从环境变量读取
            model_name: 模型名称，默认使用deepseek-chat
        """
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DeepSeek API Key未找到！请设置DEEPSEEK_API_KEY环境变量或在初始化时提供")
        
        super().__init__(api_key, model_name)
        
        # 初始化OpenAI客户端，使用DeepSeek的endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        self.default_model = model_name or self.get_default_model()
    
    def get_default_model(self) -> str:
        """获取默认模型名称"""
        return "deepseek-chat"
    
    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        调用DeepSeek API生成回复
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入
            **kwargs: 其他参数，如temperature、max_tokens等
            
        Returns:
            DeepSeek生成的回复文本
        """
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 设置默认参数
            params = {
                "model": self.default_model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": False
            }
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 提取回复内容
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return self.validate_response(content)
            else:
                return ""
                
        except Exception as e:
            error_message = str(e)
            
            # 处理特定的错误类型
            if "402" in error_message or "Insufficient Balance" in error_message:
                detailed_error = (
                    "❌ DeepSeek API 余额不足！\n"
                    "📋 解决方案：\n"
                    "1. 请访问 https://platform.deepseek.com/ 充值账户\n"
                    "2. 或者切换到 OpenAI 模型（在 config.py 中设置 OPENAI_API_KEY 和 DEFAULT_LLM_PROVIDER='openai'）\n"
                    "3. 检查 API Key 是否正确配置\n"
                    f"错误详情: {error_message}"
                )
                print(detailed_error)
                raise ValueError(detailed_error) from e
            elif "401" in error_message or "Invalid API Key" in error_message or "Unauthorized" in error_message:
                detailed_error = (
                    "❌ DeepSeek API Key 无效或未授权！\n"
                    "📋 解决方案：\n"
                    "1. 检查 config.py 中的 DEEPSEEK_API_KEY 是否正确\n"
                    "2. 访问 https://platform.deepseek.com/ 获取有效的 API Key\n"
                    "3. 确保 API Key 没有过期或被撤销\n"
                    f"错误详情: {error_message}"
                )
                print(detailed_error)
                raise ValueError(detailed_error) from e
            elif "429" in error_message or "Rate limit" in error_message:
                detailed_error = (
                    "❌ DeepSeek API 请求频率超限！\n"
                    "📋 解决方案：\n"
                    "1. 请稍后再试\n"
                    "2. 减少并发请求数量\n"
                    "3. 考虑升级 API 套餐以提高速率限制\n"
                    f"错误详情: {error_message}"
                )
                print(detailed_error)
                raise ValueError(detailed_error) from e
            else:
                detailed_error = f"DeepSeek API调用错误: {error_message}"
                print(detailed_error)
                raise e
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "provider": "DeepSeek",
            "model": self.default_model,
            "api_base": "https://api.deepseek.com"
        }
