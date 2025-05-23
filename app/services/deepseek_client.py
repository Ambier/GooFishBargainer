#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openai
import asyncio
from typing import List, Dict, Any, Optional
from config.settings import settings
from loguru import logger

class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self):
        # 检查API密钥配置
        if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
            logger.warning("DeepSeek API密钥未配置，将使用模拟模式")
            self.client = None
            self.mock_mode = True
        else:
            try:
                self.client = openai.OpenAI(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url=settings.DEEPSEEK_BASE_URL,
                    timeout=30.0  # 设置30秒超时
                )
                self.mock_mode = False
                logger.info("DeepSeek API客户端初始化成功")
            except Exception as e:
                logger.error(f"DeepSeek API客户端初始化失败: {e}")
                self.client = None
                self.mock_mode = True
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-reasoner",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        调用DeepSeek聊天完成API
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: 最大重试次数
            
        Returns:
            生成的回复文本
        """
        # 如果是模拟模式，返回模拟响应
        if self.mock_mode:
            return await self._mock_response(messages)
        
        for attempt in range(max_retries):
            try:
                # 使用asyncio.to_thread来异步调用同步API
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                if response.choices:
                    content = response.choices[0].message.content
                    logger.info("DeepSeek API调用成功")
                    return content
                return None
                
            except openai.APIConnectionError as e:
                logger.warning(f"DeepSeek API连接错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error("DeepSeek API连接失败，切换到模拟模式")
                    self.mock_mode = True
                    return await self._mock_response(messages)
                    
            except openai.APIError as e:
                logger.error(f"DeepSeek API错误: {e}")
                return await self._mock_response(messages)
                
            except Exception as e:
                logger.error(f"DeepSeek API调用失败: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    return await self._mock_response(messages)
        
        return None
    
    async def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        """生成模拟响应"""
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # 根据用户消息类型生成不同的模拟响应
        if "分析" in user_message and "商品需求" in user_message:
            return '''
            {
                "keywords": ["iPhone", "13", "二手", "手机"],
                "category": "数码产品",
                "features": ["128G", "成色较新", "功能正常"],
                "price_sensitivity": "medium",
                "quality_requirements": "良好"
            }
            '''
        elif "谈判" in user_message or "价格" in user_message:
            return "您好！我对这个商品很感兴趣，请问价格还能优惠一些吗？我是诚心想要的。"
        else:
            return "好的，我明白了。"
    
    async def analyze_product_requirement(self, user_query: str) -> Dict[str, Any]:
        """
        分析用户商品需求
        
        Args:
            user_query: 用户输入的需求描述
            
        Returns:
            分析结果字典
        """
        messages = [
            {
                "role": "system",
                "content": """你是一个专业的商品需求分析助手。请分析用户的商品需求，提取关键信息。
                
                请返回JSON格式的分析结果，包含：
                - keywords: 搜索关键词列表
                - category: 商品类别
                - features: 重要特征列表
                - price_sensitivity: 价格敏感度(high/medium/low)
                - quality_requirements: 质量要求
                """
            },
            {
                "role": "user",
                "content": f"请分析这个商品需求：{user_query}"
            }
        ]
        
        response = await self.chat_completion(messages)
        if response:
            try:
                import json
                # 清理响应中的多余字符
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:]
                if response.endswith('```'):
                    response = response[:-3]
                response = response.strip()
                
                return json.loads(response)
            except Exception as e:
                logger.warning(f"无法解析DeepSeek返回的JSON: {e}，使用默认分析")
                
        # 默认分析结果
        keywords = user_query.split()
        return {
            "keywords": keywords,
            "category": "未知",
            "features": [],
            "price_sensitivity": "medium",
            "quality_requirements": "标准"
        }
    
    async def generate_negotiation_message(
        self,
        product_info: Dict[str, Any],
        seller_info: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        target_price: float
    ) -> str:
        """
        生成与卖家的谈判消息
        
        Args:
            product_info: 商品信息
            seller_info: 卖家信息
            conversation_history: 对话历史
            target_price: 目标价格
            
        Returns:
            生成的谈判消息
        """
        messages = [
            {
                "role": "system",
                "content": """你是一个专业的商品谈判助手。请根据商品信息、卖家信息和对话历史，生成合适的谈判消息。
                
                谈判原则：
                1. 礼貌友好，建立信任
                2. 突出商品价值和自己的诚意
                3. 合理议价，不要过于激进
                4. 考虑商品状况和市场价格
                5. 保持专业和耐心
                
                请直接返回要发送的消息内容，不要包含其他格式。
                """
            },
            {
                "role": "user",
                "content": f"""
                商品信息：{product_info}
                卖家信息：{seller_info}
                对话历史：{conversation_history}
                目标价格：{target_price}
                
                请生成下一条谈判消息。
                """
            }
        ]
        
        response = await self.chat_completion(messages, temperature=0.8)
        return response or "您好，我对这个商品很感兴趣，请问价格还能优惠一些吗？"

# 全局客户端实例
deepseek_client = DeepSeekClient() 
