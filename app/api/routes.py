#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Dict, Any
from loguru import logger
import json
import time
from datetime import datetime

from app.models.schemas import SearchRequest
from app.agents.coordinator_agent import CoordinatorAgent

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 全局协调Agent实例
coordinator = CoordinatorAgent("main_coordinator")

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket连接建立: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket连接断开: {client_id}")

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                self.disconnect(client_id)

    async def broadcast_message(self, message: str):
        """广播消息给所有连接的客户端"""
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)

manager = ConnectionManager()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/api/start_comparison")
async def start_comparison(search_request: SearchRequest):
    """开始比价"""
    try:
        logger.info(f"收到比价请求: {search_request.query}")
        
        # 生成任务ID
        task_id = f"task_{int(time.time() * 1000)}"
        
        # 准备任务数据
        task_data = {
            "task_id": task_id,
            "query": search_request.query,
            "max_price": search_request.max_price,
            "credentials": {
                "username": search_request.credentials.username,
                "password": search_request.credentials.password
            }
        }
        
        # 异步执行比价任务
        asyncio.create_task(execute_comparison_task(task_data))
        
        return {
            "success": True,
            "message": "比价任务已启动",
            "task_id": task_id
        }
        
    except Exception as e:
        logger.error(f"启动比价任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_comparison_task(task_data: Dict[str, Any]):
    """执行比价任务"""
    task_id = task_data.get("task_id", "unknown")
    start_time = time.time()
    
    try:
        # 发送任务开始状态
        await send_task_status("initializing", "初始化中", "正在准备比价任务...", {
            "searchedCount": 0,
            "negotiatedCount": 0,
            "lowestPrice": 0,
            "savedAmount": 0
        })
        
        # 发送初始进度
        await send_progress_update([
            {
                "title": "任务初始化",
                "status": "running",
                "description": "正在准备比价任务...",
                "timestamp": datetime.now().isoformat()
            }
        ], 5)
        
        await asyncio.sleep(1)  # 模拟初始化时间
        
        # 执行协调Agent
        result = await coordinator.execute(task_data)
        
        if result.get("success", False):
            # 发送完成状态
            await send_task_status("completed", "已完成", "比价任务已成功完成", {
                "searchedCount": len(result.get("products", [])),
                "negotiatedCount": len([n for n in result.get("negotiations", []) if n.get("success", False)]),
                "lowestPrice": result.get("best_deal", {}).get("price", 0),
                "savedAmount": task_data.get("max_price", 0) - result.get("best_deal", {}).get("price", 0)
            })
            
            # 发送最终进度
            end_time = time.time()
            duration = f"{int(end_time - start_time)}秒"
            
            final_steps = [
                {
                    "title": "任务初始化",
                    "status": "completed",
                    "description": "比价任务准备完成",
                    "timestamp": datetime.fromtimestamp(start_time).isoformat(),
                    "duration": "1秒"
                },
                {
                    "title": "商品搜索",
                    "status": "completed",
                    "description": f"找到 {len(result.get('products', []))} 个符合条件的商品",
                    "timestamp": datetime.fromtimestamp(start_time + 10).isoformat(),
                    "duration": "8秒"
                },
                {
                    "title": "价格谈判",
                    "status": "completed",
                    "description": f"成功谈判 {len([n for n in result.get('negotiations', []) if n.get('success', False)])} 个商品",
                    "timestamp": datetime.fromtimestamp(start_time + 25).isoformat(),
                    "duration": "15秒"
                },
                {
                    "title": "结果分析",
                    "status": "completed",
                    "description": "比价分析完成，找到最佳选择",
                    "timestamp": datetime.fromtimestamp(end_time).isoformat(),
                    "duration": "2秒"
                }
            ]
            
            await send_progress_update(final_steps, 100)
            
            # 发送任务完成消息
            await manager.broadcast_message(json.dumps({
                "type": "task_completed",
                "data": {
                    **result,
                    "execution_time": duration,
                    "task_id": task_id
                }
            }))
            
        else:
            # 发送失败状态
            await send_task_status("failed", "失败", f"任务执行失败: {result.get('error', '未知错误')}")
            
            await manager.broadcast_message(json.dumps({
                "type": "error",
                "message": result.get("error", "任务执行失败")
            }))
            
    except Exception as e:
        logger.error(f"执行比价任务失败: {e}")
        
        # 发送失败状态
        await send_task_status("failed", "失败", f"任务执行失败: {str(e)}")
        
        # 发送错误消息
        await manager.broadcast_message(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def send_task_status(status: str, title: str, description: str, metrics: Dict[str, Any] = None):
    """发送任务状态更新"""
    message = {
        "type": "task_status",
        "data": {
            "status": status,
            "title": title,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    if metrics:
        message["data"]["metrics"] = metrics
    
    await manager.broadcast_message(json.dumps(message))

async def send_progress_update(steps: list, percentage: float):
    """发送进度更新"""
    message = {
        "type": "progress",
        "data": {
            "steps": steps,
            "percentage": percentage,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.broadcast_message(json.dumps(message))

@router.get("/api/task_progress/{task_id}")
async def get_task_progress(task_id: str):
    """获取任务进度"""
    try:
        progress = coordinator.get_task_progress(task_id)
        if progress:
            return {"success": True, "progress": progress}
        else:
            return {"success": False, "error": "任务不存在"}
    except Exception as e:
        logger.error(f"获取任务进度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket端点"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                # 心跳检测
                await manager.send_personal_message(
                    json.dumps({"type": "pong"}), 
                    client_id
                )
            elif message.get("type") == "start_comparison":
                # 开始比价
                search_data = message.get("data", {})
                task_id = f"task_{int(time.time() * 1000)}"
                search_data["task_id"] = task_id
                
                asyncio.create_task(execute_comparison_task(search_data))
                
                await manager.send_personal_message(
                    json.dumps({
                        "type": "task_started",
                        "data": {
                            "message": "比价任务已启动",
                            "task_id": task_id
                        }
                    }),
                    client_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(client_id)

# 模拟进度更新的辅助函数
async def send_progress_update_legacy(client_id: str, status: str, message: str, progress: float):
    """发送进度更新（兼容旧版本）"""
    update_message = {
        "type": "progress_update",
        "data": {
            "status": status,
            "message": message,
            "progress": progress
        }
    }
    await manager.send_personal_message(json.dumps(update_message), client_id) 
