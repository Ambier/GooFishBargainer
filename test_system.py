#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
咸鱼比价助手系统测试脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_deepseek_client():
    """测试DeepSeek客户端"""
    print("🧪 测试DeepSeek客户端...")
    
    try:
        from app.services.deepseek_client import deepseek_client
        
        # 测试需求分析（模拟，不实际调用API）
        test_query = "想要一个二手iPhone 13，128G，成色较新"
        print(f"   测试查询: {test_query}")
        
        # 这里只是测试模块导入，不实际调用API
        print("   ✅ DeepSeek客户端模块导入成功")
        
    except Exception as e:
        print(f"   ❌ DeepSeek客户端测试失败: {e}")
        return False
    
    return True

async def test_agents():
    """测试Agent系统"""
    print("🤖 测试Agent系统...")
    
    try:
        from app.agents.coordinator_agent import CoordinatorAgent
        from app.agents.search_agent import SearchAgent
        from app.agents.negotiation_agent import NegotiationAgent
        
        # 创建测试Agent
        coordinator = CoordinatorAgent("test_coordinator")
        search_agent = SearchAgent("test_search")
        negotiation_agent = NegotiationAgent("test_negotiation", "test_seller")
        
        print("   ✅ 所有Agent类创建成功")
        print(f"   - 协调Agent: {coordinator.agent_type}")
        print(f"   - 搜索Agent: {search_agent.agent_type}")
        print(f"   - 谈判Agent: {negotiation_agent.agent_type}")
        
    except Exception as e:
        print(f"   ❌ Agent系统测试失败: {e}")
        return False
    
    return True

async def test_models():
    """测试数据模型"""
    print("📊 测试数据模型...")
    
    try:
        from app.models.schemas import (
            SearchRequest, UserCredentials, ProductInfo, 
            TaskProgress, TaskStatus
        )
        
        # 创建测试数据
        credentials = UserCredentials(username="test", password="test")
        search_request = SearchRequest(
            query="测试商品",
            max_price=1000.0,
            credentials=credentials
        )
        
        product = ProductInfo(
            id="test_product",
            title="测试商品",
            price=500.0,
            seller_name="测试卖家",
            seller_id="test_seller",
            location="测试地点",
            description="测试描述",
            url="http://test.com"
        )
        
        progress = TaskProgress(
            task_id="test_task",
            status=TaskStatus.PENDING,
            message="测试消息"
        )
        
        print("   ✅ 所有数据模型创建成功")
        print(f"   - 搜索请求: {search_request.query}")
        print(f"   - 商品信息: {product.title}")
        print(f"   - 任务进度: {progress.status}")
        
    except Exception as e:
        print(f"   ❌ 数据模型测试失败: {e}")
        return False
    
    return True

async def test_api_routes():
    """测试API路由"""
    print("🌐 测试API路由...")
    
    try:
        from app.api.routes import router
        
        # 检查路由是否正确导入
        print("   ✅ API路由模块导入成功")
        print(f"   - 路由对象类型: {type(router)}")
        
    except Exception as e:
        print(f"   ❌ API路由测试失败: {e}")
        return False
    
    return True

async def test_configuration():
    """测试配置"""
    print("⚙️  测试配置...")
    
    try:
        from config.settings import settings
        
        print("   ✅ 配置模块导入成功")
        print(f"   - 应用主机: {settings.APP_HOST}")
        print(f"   - 应用端口: {settings.APP_PORT}")
        print(f"   - 调试模式: {settings.DEBUG}")
        print(f"   - 最大并发Agent: {settings.MAX_CONCURRENT_AGENTS}")
        
    except Exception as e:
        print(f"   ❌ 配置测试失败: {e}")
        return False
    
    return True

async def main():
    """主测试函数"""
    print("🚀 开始系统测试...\n")
    
    tests = [
        test_configuration,
        test_models,
        test_deepseek_client,
        test_agents,
        test_api_routes,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ 测试异常: {e}\n")
    
    print("=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n📝 下一步:")
        print("1. 编辑 env.example 文件，填入您的DeepSeek API密钥")
        print("2. 将 env.example 重命名为 .env")
        print("3. 运行 python main.py 启动服务")
        print("4. 访问 http://localhost:8000 使用Web界面")
    else:
        print("⚠️  部分测试失败，请检查错误信息并修复。")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main()) 