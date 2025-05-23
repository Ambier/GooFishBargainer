#!/usr/bin/env python3


# -*- coding: utf-8 -*-

import asyncio
import uuid
from typing import Dict, Any, List
from loguru import logger
from app.agents.base_agent import BaseAgent
from app.agents.search_agent import SearchAgent
from app.agents.negotiation_agent import NegotiationAgent
from app.models.schemas import TaskProgress, TaskStatus, ProductInfo
from config.settings import settings

class CoordinatorAgent(BaseAgent):
    """协调Agent - 负责整体任务协调和管理"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "coordinator_agent")
        self.task_progress = {}
        self.active_agents = {}
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行协调任务
        
        Args:
            task_data: 包含搜索请求的所有信息
            
        Returns:
            最终比价结果
        """
        try:
            task_id = str(uuid.uuid4())
            
            # 初始化任务进度
            progress = TaskProgress(
                task_id=task_id,
                status=TaskStatus.INITIALIZING,
                message="初始化比价任务..."
            )
            self.task_progress[task_id] = progress
            
            logger.info(f"开始执行比价任务: {task_id}")
            
            # 第一阶段：搜索商品
            await self._update_progress(task_id, TaskStatus.SEARCHING, "正在搜索商品...", 10)
            
            search_agent = SearchAgent(f"search_{task_id}")
            self.active_agents[search_agent.agent_id] = search_agent
            
            search_result = await search_agent.execute(task_data)
            
            if not search_result.get("success", False):
                await self._update_progress(task_id, TaskStatus.FAILED, f"搜索失败: {search_result.get('error', '')}", 0)
                return {"task_id": task_id, "success": False, "error": search_result.get("error", "")}
            
            products = [ProductInfo(**p) for p in search_result.get("products", [])]
            await self._update_progress(task_id, TaskStatus.SEARCHING, f"找到 {len(products)} 个商品", 30)
            
            if not products:
                await self._update_progress(task_id, TaskStatus.COMPLETED, "未找到符合条件的商品", 100)
                return {"task_id": task_id, "success": True, "products": [], "best_deal": None}
            
            # 第二阶段：并行谈判
            await self._update_progress(task_id, TaskStatus.COMMUNICATING, "开始与卖家沟通...", 40)
            
            negotiation_results = await self._parallel_negotiate(task_id, products, task_data)
            
            # 第三阶段：比价分析
            await self._update_progress(task_id, TaskStatus.COMPARING, "分析比价结果...", 80)
            
            best_deal = self._find_best_deal(products, negotiation_results)
            
            # 完成任务
            await self._update_progress(task_id, TaskStatus.COMPLETED, "比价完成", 100)
            
            # 清理资源
            search_agent.close()
            
            return {
                "task_id": task_id,
                "success": True,
                "products": [p.dict() for p in products],
                "negotiations": negotiation_results,
                "best_deal": best_deal.dict() if best_deal else None
            }
            
        except Exception as e:
            logger.error(f"协调Agent执行失败: {e}")
            if 'task_id' in locals():
                await self._update_progress(task_id, TaskStatus.FAILED, f"执行失败: {str(e)}", 0)
            return {"success": False, "error": str(e)}
    
    async def _parallel_negotiate(self, task_id: str, products: List[ProductInfo], task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        并行与多个卖家谈判
        
        Args:
            task_id: 任务ID
            products: 商品列表
            task_data: 任务数据
            
        Returns:
            谈判结果列表
        """
        max_price = task_data.get("max_price", 0)
        target_price = max_price * 0.8  # 目标价格为最高价格的80%
        
        # 限制并发谈判数量
        max_concurrent = min(len(products), settings.MAX_CONCURRENT_AGENTS)
        selected_products = products[:max_concurrent]
        
        # 创建谈判任务
        negotiation_tasks = []
        negotiation_agents = []
        
        # 这里需要共享咸鱼服务实例，实际实现中需要考虑线程安全
        from app.services.goofish_service import XianyuService
        shared_xianyu_service = XianyuService()
        
        for i, product in enumerate(selected_products):
            agent_id = f"negotiation_{task_id}_{i}"
            agent = NegotiationAgent(agent_id, product.seller_id)
            negotiation_agents.append(agent)
            
            task_data_copy = {
                "product_info": product.dict(),
                "target_price": target_price,
                "xianyu_service": shared_xianyu_service
            }
            
            task = agent.execute(task_data_copy)
            negotiation_tasks.append(task)
        
        # 并行执行谈判
        logger.info(f"开始并行谈判，共 {len(negotiation_tasks)} 个任务")
        
        try:
            # 设置超时时间
            results = await asyncio.wait_for(
                asyncio.gather(*negotiation_tasks, return_exceptions=True),
                timeout=settings.AGENT_TIMEOUT
            )
            
            # 处理结果
            negotiation_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"谈判任务 {i} 失败: {result}")
                    negotiation_results.append({
                        "success": False,
                        "error": str(result),
                        "seller_id": selected_products[i].seller_id
                    })
                else:
                    negotiation_results.append(result)
            
            return negotiation_results
            
        except asyncio.TimeoutError:
            logger.warning("谈判任务超时")
            return [{"success": False, "error": "谈判超时"} for _ in selected_products]
        
        finally:
            # 清理资源
            shared_xianyu_service.close()
    
    def _find_best_deal(self, products: List[ProductInfo], negotiations: List[Dict[str, Any]]) -> ProductInfo:
        """
        找到最佳交易
        
        Args:
            products: 商品列表
            negotiations: 谈判结果列表
            
        Returns:
            最佳商品
        """
        best_product = None
        best_price = float('inf')
        
        for i, product in enumerate(products):
            if i < len(negotiations):
                negotiation = negotiations[i]
                if negotiation.get("success", False):
                    final_price = negotiation.get("final_price", product.price)
                    if final_price < best_price:
                        best_price = final_price
                        best_product = product
                        # 更新商品价格为谈判后的价格
                        best_product.price = final_price
            
            # 如果没有谈判结果，使用原价格
            if product.price < best_price:
                best_price = product.price
                best_product = product
        
        return best_product
    
    async def _update_progress(self, task_id: str, status: TaskStatus, message: str, progress: float):
        """更新任务进度"""
        if task_id in self.task_progress:
            self.task_progress[task_id].status = status
            self.task_progress[task_id].message = message
            self.task_progress[task_id].progress = progress
            logger.info(f"任务 {task_id} 进度更新: {message} ({progress}%)")
    
    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """获取任务进度"""
        if task_id in self.task_progress:
            return self.task_progress[task_id].dict()
        return None 