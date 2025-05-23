#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router
from config.settings import settings
from loguru import logger
import os

# 创建FastAPI应用
app = FastAPI(
    title="咸鱼比价助手",
    description="基于多Agent的智能咸鱼比价助手",
    version="1.0.0"
)

# 挂载静态文件
if not os.path.exists("app/static"):
    os.makedirs("app/static")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="templates")

# 注册路由
app.include_router(router)

if __name__ == "__main__":
    logger.info(f"启动咸鱼比价助手服务器 - {settings.APP_HOST}:{settings.APP_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    ) 