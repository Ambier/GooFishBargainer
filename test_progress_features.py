#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试比价进度页面新功能
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

# 模拟WebSocket消息发送
class MockWebSocketManager:
    def __init__(self):
        self.messages = []
    
    async def broadcast_message(self, message: str):
        """模拟广播消息"""
        data = json.loads(message)
        self.messages.append(data)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送消息: {data['type']}")
        if data['type'] == 'task_status':
            print(f"  状态: {data['data']['status']} - {data['data']['title']}")
        elif data['type'] == 'progress':
            print(f"  进度: {data['data']['percentage']}%")
            for step in data['data']['steps']:
                print(f"    - {step['title']}: {step['status']}")
        elif data['type'] == 'task_completed':
            print(f"  任务完成: {data['data'].get('execution_time', 'N/A')}")

# 模拟任务执行函数
async def simulate_comparison_task(task_data: Dict[str, Any], manager: MockWebSocketManager):
    """模拟比价任务执行"""
    task_id = task_data.get("task_id", "test_task")
    start_time = time.time()
    
    try:
        print(f"\n=== 开始模拟比价任务: {task_id} ===")
        
        # 1. 发送任务开始状态
        await send_task_status(manager, "initializing", "初始化中", "正在准备比价任务...", {
            "searchedCount": 0,
            "negotiatedCount": 0,
            "lowestPrice": 0,
            "savedAmount": 0
        })
        
        # 发送初始进度
        await send_progress_update(manager, [
            {
                "title": "任务初始化",
                "status": "running",
                "description": "正在准备比价任务...",
                "timestamp": datetime.now().isoformat()
            }
        ], 5)
        
        await asyncio.sleep(1)
        
        # 2. 搜索阶段
        await send_task_status(manager, "searching", "搜索中", "正在搜索符合条件的商品...", {
            "searchedCount": 0,
            "negotiatedCount": 0,
            "lowestPrice": 0,
            "savedAmount": 0
        })
        
        await send_progress_update(manager, [
            {
                "title": "任务初始化",
                "status": "completed",
                "description": "比价任务准备完成",
                "timestamp": datetime.fromtimestamp(start_time).isoformat(),
                "duration": "1秒"
            },
            {
                "title": "商品搜索",
                "status": "running",
                "description": "正在搜索商品...",
                "timestamp": datetime.now().isoformat()
            }
        ], 25)
        
        await asyncio.sleep(2)
        
        # 模拟找到商品
        products_found = 5
        await send_task_status(manager, "searching", "搜索中", f"找到 {products_found} 个符合条件的商品", {
            "searchedCount": products_found,
            "negotiatedCount": 0,
            "lowestPrice": 0,
            "savedAmount": 0
        })
        
        await send_progress_update(manager, [
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
                "description": f"找到 {products_found} 个符合条件的商品",
                "timestamp": datetime.fromtimestamp(start_time + 3).isoformat(),
                "duration": "3秒"
            },
            {
                "title": "价格谈判",
                "status": "running",
                "description": "正在与卖家进行价格谈判...",
                "timestamp": datetime.now().isoformat()
            }
        ], 50)
        
        await asyncio.sleep(2)
        
        # 3. 谈判阶段
        await send_task_status(manager, "negotiating", "谈判中", "正在与卖家进行价格谈判...", {
            "searchedCount": products_found,
            "negotiatedCount": 0,
            "lowestPrice": 0,
            "savedAmount": 0
        })
        
        await asyncio.sleep(3)
        
        # 模拟谈判进展
        negotiated_count = 3
        lowest_price = 850
        max_price = task_data.get("max_price", 1000)
        saved_amount = max_price - lowest_price
        
        await send_task_status(manager, "negotiating", "谈判中", f"已完成 {negotiated_count} 个商品的谈判", {
            "searchedCount": products_found,
            "negotiatedCount": negotiated_count,
            "lowestPrice": lowest_price,
            "savedAmount": saved_amount
        })
        
        await send_progress_update(manager, [
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
                "description": f"找到 {products_found} 个符合条件的商品",
                "timestamp": datetime.fromtimestamp(start_time + 3).isoformat(),
                "duration": "3秒"
            },
            {
                "title": "价格谈判",
                "status": "completed",
                "description": f"成功谈判 {negotiated_count} 个商品",
                "timestamp": datetime.fromtimestamp(start_time + 8).isoformat(),
                "duration": "5秒"
            },
            {
                "title": "结果分析",
                "status": "running",
                "description": "正在分析比价结果...",
                "timestamp": datetime.now().isoformat()
            }
        ], 85)
        
        await asyncio.sleep(1)
        
        # 4. 分析阶段
        await send_task_status(manager, "comparing", "分析中", "正在分析比价结果...", {
            "searchedCount": products_found,
            "negotiatedCount": negotiated_count,
            "lowestPrice": lowest_price,
            "savedAmount": saved_amount
        })
        
        await asyncio.sleep(1)
        
        # 5. 完成任务
        end_time = time.time()
        duration = f"{int(end_time - start_time)}秒"
        
        await send_task_status(manager, "completed", "已完成", "比价任务已成功完成", {
            "searchedCount": products_found,
            "negotiatedCount": negotiated_count,
            "lowestPrice": lowest_price,
            "savedAmount": saved_amount
        })
        
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
                "description": f"找到 {products_found} 个符合条件的商品",
                "timestamp": datetime.fromtimestamp(start_time + 3).isoformat(),
                "duration": "3秒"
            },
            {
                "title": "价格谈判",
                "status": "completed",
                "description": f"成功谈判 {negotiated_count} 个商品",
                "timestamp": datetime.fromtimestamp(start_time + 8).isoformat(),
                "duration": "5秒"
            },
            {
                "title": "结果分析",
                "status": "completed",
                "description": "比价分析完成，找到最佳选择",
                "timestamp": datetime.fromtimestamp(end_time).isoformat(),
                "duration": "2秒"
            }
        ]
        
        await send_progress_update(manager, final_steps, 100)
        
        # 发送任务完成消息
        result = {
            "success": True,
            "products": [
                {
                    "title": f"测试商品 {i+1}",
                    "price": 900 + i * 10,
                    "seller_name": f"卖家{i+1}",
                    "location": "上海",
                    "url": f"https://example.com/product/{i+1}",
                    "seller_id": f"seller_{i+1}",
                    "negotiated_price": 850 + i * 5 if i < negotiated_count else None
                }
                for i in range(products_found)
            ],
            "negotiations": [
                {"success": True, "final_price": 850 + i * 5}
                for i in range(negotiated_count)
            ],
            "best_deal": {
                "title": "测试商品 1",
                "price": lowest_price,
                "seller_name": "卖家1",
                "location": "上海",
                "url": "https://example.com/product/1",
                "seller_id": "seller_1"
            },
            "execution_time": duration,
            "task_id": task_id
        }
        
        await manager.broadcast_message(json.dumps({
            "type": "task_completed",
            "data": result
        }))
        
        print(f"\n=== 任务完成，耗时: {duration} ===")
        
    except Exception as e:
        print(f"任务执行失败: {e}")
        await manager.broadcast_message(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def send_task_status(manager: MockWebSocketManager, status: str, title: str, description: str, metrics: Dict[str, Any] = None):
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

async def send_progress_update(manager: MockWebSocketManager, steps: list, percentage: float):
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

async def main():
    """主测试函数"""
    print("开始测试比价进度页面新功能...")
    
    # 创建模拟WebSocket管理器
    manager = MockWebSocketManager()
    
    # 模拟任务数据
    task_data = {
        "task_id": "test_task_001",
        "query": "iPhone 14",
        "max_price": 1000,
        "credentials": {
            "username": "test_user",
            "password": "test_pass"
        }
    }
    
    # 执行模拟任务
    await simulate_comparison_task(task_data, manager)
    
    print(f"\n总共发送了 {len(manager.messages)} 条消息")
    print("\n消息类型统计:")
    message_types = {}
    for msg in manager.messages:
        msg_type = msg['type']
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
    
    for msg_type, count in message_types.items():
        print(f"  {msg_type}: {count} 条")

if __name__ == "__main__":
    asyncio.run(main()) 