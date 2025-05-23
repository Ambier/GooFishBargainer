# 咸鱼比价助手

基于多Agent的智能咸鱼比价助手，通过自然语言输入需求，自动登录咸鱼并与多个卖家沟通，找到最便宜的商品。

## 功能特性

- 🤖 基于DeepSeek-R1模型的智能对话
- 🔄 自定义多Agent协作框架
- 🌐 实时Web界面展示比价过程
- 🔍 自动搜索和筛选商品
- 💬 并行与多个卖家沟通
- 📊 智能比价和推荐

## 安装和运行

### 快速开始

1. **安装依赖**：
```bash
pip install -r requirements.txt
```

> ⚠️ **依赖说明**: 项目已修复所有依赖冲突问题。如果遇到安装问题，请参考下方的故障排除部分。

2. **配置环境变量**：
```bash
cp .env.example .env
# 编辑 .env 文件，填入DeepSeek API密钥
```

3. **运行应用**：
```bash
python main.py
# 或使用启动脚本
chmod +x start.sh
./start.sh
```

4. **访问应用**: 打开浏览器访问 http://localhost:8000

### 故障排除

如果遇到依赖安装问题：

1. **清理环境**：
```bash
pip cache purge
pip uninstall -r requirements.txt -y
```

2. **重新安装**：
```bash
pip install -r requirements.txt
```

3. **使用conda环境（推荐）**：
```bash
conda create -n xianyu_helper python=3.9
conda activate xianyu_helper
pip install -r requirements.txt
```

### MetaGPT安装（可选）

项目使用自定义Agent系统，不强制依赖MetaGPT。如需使用MetaGPT，请参考 [METAGPT_INSTALL.md](METAGPT_INSTALL.md)。

## 项目结构

```
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖列表（已修复冲突）
├── METAGPT_INSTALL.md     # MetaGPT安装说明
├── app/
│   ├── api/               # API路由
│   ├── agents/            # 多Agent实现
│   ├── services/          # 业务服务
│   ├── models/            # 数据模型
│   └── static/            # 静态文件
├── templates/             # HTML模板
└── config/               # 配置文件
```

## 使用说明

1. 在左侧输入框填写商品需求（自然语言）
2. 设置最高价格预算
3. 配置咸鱼账号和密码
4. 点击开始比价
5. 右侧实时查看比价过程和结果 