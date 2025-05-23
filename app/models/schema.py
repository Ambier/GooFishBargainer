#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    LOGGING_IN = "logging_in"
    SEARCHING = "searching"
    COMMUNICATING = "communicating"
    COMPARING = "comparing"
    COMPLETED = "completed"
    FAILED = "failed"

class UserCredentials(BaseModel):
    """用户凭证"""
    username: str = Field(..., description="咸鱼用户名")
    password: str = Field(..., description="咸鱼密码")

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="商品需求描述")
    max_price: float = Field(..., description="最高价格")
    credentials: UserCredentials = Field(..., description="用户凭证")

class ProductInfo(BaseModel):
    """商品信息"""
    id: str = Field(..., description="商品ID")
    title: str = Field(..., description="商品标题")
    price: float = Field(..., description="商品价格")
    seller_name: str = Field(..., description="卖家名称")
    seller_id: str = Field(..., description="卖家ID")
    location: str = Field(..., description="商品位置")
    description: str = Field(..., description="商品描述")
    images: List[str] = Field(default=[], description="商品图片")
    url: str = Field(..., description="商品链接")

class CommunicationRecord(BaseModel):
    """沟通记录"""
    seller_id: str = Field(..., description="卖家ID")
    seller_name: str = Field(..., description="卖家名称")
    messages: List[Dict[str, Any]] = Field(default=[], description="消息记录")
    final_price: Optional[float] = Field(None, description="最终价格")
    status: str = Field(default="pending", description="沟通状态")

class TaskProgress(BaseModel):
    """任务进度"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: float = Field(default=0.0, description="进度百分比")
    message: str = Field(default="", description="当前状态描述")
    products_found: List[ProductInfo] = Field(default=[], description="找到的商品")
    communications: List[CommunicationRecord] = Field(default=[], description="沟通记录")
    best_deal: Optional[ProductInfo] = Field(None, description="最佳交易")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class AgentMessage(BaseModel):
    """Agent消息"""
    agent_type: str = Field(..., description="Agent类型")
    message: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据") 
