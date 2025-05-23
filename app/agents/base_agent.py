#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

class BaseAgent(ABC):
    """基础Agent类"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "idle"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
    @abstractmethod
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            执行结果
        """
        pass
    
    def update_status(self, status: str):
        """更新Agent状态"""
        self.status = status
        self.last_activity = datetime.now()
        logger.info(f"Agent {self.agent_id} 状态更新: {status}")
    
    def get_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        } 