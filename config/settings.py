#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    # DeepSeek API配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # 应用配置
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 咸鱼相关配置
    XIANYU_BASE_URL: str = "https://2.taobao.com"
    XIANYU_LOGIN_URL: str = "https://login.taobao.com"
    
    # Agent配置
    MAX_CONCURRENT_AGENTS: int = 5
    AGENT_TIMEOUT: int = 300  # 5分钟超时

settings = Settings() 