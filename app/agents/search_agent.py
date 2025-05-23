#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from typing import Dict, Any, List
from loguru import logger
from app.agents.base_agent import BaseAgent
from app.services.goofish_service import GoofishService
from app.services.deepseek_client import deepseek_client
from app.models.schemas import ProductInfo, UserCredentials

class SearchAgent(BaseAgent):
    """搜索Agent - 负责商品搜索和筛选"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "search_agent")
        self.goofish_service = GoofishService()
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行搜索任务
        
        Args:
            task_data: 包含搜索查询、最高价格、用户凭证等信息
            
        Returns:
            搜索结果
        """
        try:
            self.update_status("analyzing_requirement")
            
            query = task_data.get("query", "")
            max_price = task_data.get("max_price", 0)
            credentials = UserCredentials(**task_data.get("credentials", {}))
            
            # 分析用户需求
            logger.info(f"分析用户需求: {query}")
            requirement_analysis = await deepseek_client.analyze_product_requirement(query)
            
            # 登录咸鱼
            self.update_status("logging_in")
            login_success = await self.goofish_service.login(credentials)
            
            if not login_success:
                return {
                    "success": False,
                    "error": "登录失败",
                    "products": []
                }
            
            # 搜索商品
            self.update_status("searching_products")
            
            # 使用分析出的关键词进行搜索
            keywords = requirement_analysis.get("keywords", [query])
            all_products = []
            
            for keyword in keywords[:3]:  # 限制搜索关键词数量
                logger.info(f"搜索关键词: {keyword}")
                products = await self.goofish_service.search_products(keyword, max_price)
                all_products.extend(products)
            
            # 去重和筛选
            unique_products = self._deduplicate_products(all_products)
            filtered_products = self._filter_products(unique_products, requirement_analysis)
            
            self.update_status("completed")
            
            return {
                "success": True,
                "products": [product.dict() for product in filtered_products],
                "requirement_analysis": requirement_analysis,
                "total_found": len(filtered_products)
            }
            
        except Exception as e:
            logger.error(f"搜索Agent执行失败: {e}")
            self.update_status("failed")
            return {
                "success": False,
                "error": str(e),
                "products": []
            }
    
    def _deduplicate_products(self, products: List[ProductInfo]) -> List[ProductInfo]:
        """去重商品"""
        seen_titles = set()
        unique_products = []
        
        for product in products:
            # 简单的标题去重
            title_key = product.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_products.append(product)
        
        return unique_products
    
    def _filter_products(self, products: List[ProductInfo], analysis: Dict[str, Any]) -> List[ProductInfo]:
        """根据需求分析筛选商品"""
        # 这里可以根据分析结果进行更智能的筛选
        # 目前简单按价格排序
        return sorted(products, key=lambda x: x.price)[:10]  # 返回最便宜的10个
    
    def close(self):
        """关闭资源"""
        if self.goofish_service:
            self.goofish_service.close() 
