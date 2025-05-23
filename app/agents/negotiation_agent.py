#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from typing import Dict, Any, List
from loguru import logger
from app.agents.base_agent import BaseAgent
from app.services.goofish_service import GoofishService
from app.services.deepseek_client import deepseek_client
from app.models.schema import ProductInfo, CommunicationRecord

class NegotiationAgent(BaseAgent):
    """谈判Agent - 负责与单个卖家进行价格谈判"""
    
    def __init__(self, agent_id: str, seller_id: str):
        super().__init__(agent_id, "negotiation_agent")
        self.seller_id = seller_id
        self.goofish_service = None
        self.conversation_history = []
        self.max_rounds = 3  # 最大谈判轮数
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行谈判任务
        
        Args:
            task_data: 包含商品信息、目标价格、卖家信息等
            
        Returns:
            谈判结果
        """
        try:
            self.update_status("initializing")
            
            product_info = task_data.get("product_info", {})
            target_price = task_data.get("target_price", 0)
            goofish_service = task_data.get("goofish_service")
            
            if not goofish_service:
                return {
                    "success": False,
                    "error": "缺少咸鱼服务实例",
                    "final_price": None
                }
            
            self.goofish_service = goofish_service
            
            logger.info(f"开始与卖家 {self.seller_id} 谈判商品: {product_info.get('title', '')}")
            
            # 开始谈判流程
            self.update_status("negotiating")
            final_price = await self._negotiate_with_seller(product_info, target_price)
            
            self.update_status("completed")
            
            return {
                "success": True,
                "seller_id": self.seller_id,
                "final_price": final_price,
                "conversation_history": self.conversation_history,
                "rounds": len(self.conversation_history) // 2  # 每轮包含发送和接收
            }
            
        except Exception as e:
            logger.error(f"谈判Agent执行失败: {e}")
            self.update_status("failed")
            return {
                "success": False,
                "error": str(e),
                "final_price": None
            }
    
    async def _negotiate_with_seller(self, product_info: Dict[str, Any], target_price: float) -> float:
        """
        与卖家进行谈判
        
        Args:
            product_info: 商品信息
            target_price: 目标价格
            
        Returns:
            最终谈判价格
        """
        current_price = product_info.get("price", 0)
        original_price = current_price
        
        for round_num in range(self.max_rounds):
            logger.info(f"谈判第 {round_num + 1} 轮")
            
            # 生成谈判消息
            seller_info = {"seller_id": self.seller_id}
            message = await deepseek_client.generate_negotiation_message(
                product_info, seller_info, self.conversation_history, target_price
            )
            
            # 发送消息给卖家
            success = await self.goofish_service.send_message_to_seller(self.seller_id, message)
            if success:
                self.conversation_history.append({
                    "type": "sent",
                    "message": message,
                    "timestamp": asyncio.get_event_loop().time()
                })
            
            # 等待卖家回复
            response = await self.goofish_service.get_seller_response(self.seller_id)
            if response:
                self.conversation_history.append({
                    "type": "received",
                    "message": response,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                # 分析回复中的价格信息
                new_price = self._extract_price_from_response(response, current_price)
                if new_price and new_price < current_price:
                    current_price = new_price
                    logger.info(f"卖家降价至: {current_price}")
                    
                    # 如果达到目标价格，结束谈判
                    if current_price <= target_price:
                        logger.info("达到目标价格，谈判成功")
                        break
            
            # 等待一段时间再进行下一轮
            await asyncio.sleep(2)
        
        return current_price
    
    def _extract_price_from_response(self, response: str, current_price: float) -> float:
        """
        从卖家回复中提取价格信息
        
        Args:
            response: 卖家回复
            current_price: 当前价格
            
        Returns:
            提取到的价格，如果没有则返回当前价格
        """
        import re
        
        # 查找价格模式
        price_patterns = [
            r'(\d+\.?\d*)元',
            r'(\d+\.?\d*)块',
            r'(\d+\.?\d*)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, response)
            if matches:
                try:
                    price = float(matches[0])
                    # 价格合理性检查
                    if 0 < price < current_price * 2:
                        return price
                except ValueError:
                    continue
        
        # 如果提到优惠但没有具体价格，假设优惠5-15元
        if any(keyword in response for keyword in ["优惠", "便宜", "减"]):
            import random
            discount = random.uniform(5, 15)
            return max(current_price - discount, current_price * 0.8)
        
        return current_price 