#!/bin/bash

# 咸鱼比价助手启动脚本

echo "🚀 启动咸鱼比价助手..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装，请先安装pip3"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖包..."
pip3 install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，复制示例文件..."
    cp env.example .env
    echo "📝 请编辑.env文件，填入您的DeepSeek API密钥"
    echo "   DEEPSEEK_API_KEY=your_api_key_here"
    read -p "按回车键继续..."
fi

# 创建必要的目录
mkdir -p app/static
mkdir -p templates
mkdir -p logs

# 启动应用
echo "🌟 启动Web服务器..."
python3 main.py 