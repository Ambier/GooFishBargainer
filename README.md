# 咸鱼比价侠 (GooFishBargainer)
<img width="1787" alt="截屏2025-05-23 14 07 05" src="https://github.com/user-attachments/assets/df51b566-d802-43bd-b446-2d74e8529b85" />
95%+的代码完全基于Claude 4，辅助人工微调

> 🐟 智能搜索 · 自动谈判 · 找到最优价格

一个基于多Agent架构的智能咸鱼比价助手，使用DeepSeek-R1模型和自定义多Agent框架，为用户提供全自动的商品搜索、价格谈判和比价服务。

![项目状态](https://img.shields.io/badge/状态-开发中-yellow)
![Python版本](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![许可证](https://img.shields.io/badge/许可证-MIT-blue)

## ✨ 核心特性

### 🤖 多Agent智能架构
- **协调Agent**: 统筹管理整个比价流程
- **搜索Agent**: 智能搜索符合条件的商品
- **谈判Agent**: 自动与卖家进行价格谈判
- **分析Agent**: 深度分析商品性价比

### 🎯 智能比价功能
- **自然语言搜索**: 支持自然语言描述商品需求
- **智能价格谈判**: 基于AI的自动谈判策略
- **多维度比较**: 价格、质量、信誉综合评估
- **最优推荐**: 智能推荐最具性价比的商品

### 📊 实时进度展示
- **任务状态跟踪**: 实时显示当前执行阶段
- **进度可视化**: 动态进度条和百分比显示
- **执行指标**: 搜索数量、谈判结果、节省金额
- **历史记录**: 自动保存最近10次执行记录

### 🎨 现代化界面
- **响应式设计**: 完美适配桌面和移动设备
- **玻璃拟态风格**: 现代化的视觉设计
- **实时动画**: 流畅的交互动画效果
- **深色模式**: 支持系统深色模式

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 高性能异步Web框架
- **WebSocket**: 实时双向通信
- **DeepSeek-R1**: 大语言模型支持
- **MetaGPT**: 多Agent框架基础
- **Loguru**: 结构化日志记录

### 前端技术栈
- **HTML5/CSS3**: 现代化标准
- **JavaScript ES6+**: 原生JavaScript实现
- **Bootstrap 5.3**: 响应式UI框架
- **WebSocket API**: 实时通信

### 核心组件
```
app/
├── agents/           # 多Agent实现
│   ├── coordinator_agent.py    # 协调Agent
│   ├── search_agent.py        # 搜索Agent
│   ├── negotiation_agent.py   # 谈判Agent
│   └── analysis_agent.py      # 分析Agent
├── api/             # API路由
│   └── routes.py    # 主要路由和WebSocket处理
├── models/          # 数据模型
│   └── schemas.py   # Pydantic数据模型
├── services/        # 业务服务
└── static/          # 静态资源
    └── style.css    # 样式文件
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 或 conda
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/xXiaoyu.git
cd xXiaoyu
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 复制配置文件
cp config/config.example.yaml config/config.yaml

# 编辑配置文件，添加必要的API密钥
vim config/config.yaml
```

4. **启动服务**
```bash
# 使用启动脚本
./start.sh

# 或直接运行
python main.py
```

5. **访问应用**
打开浏览器访问: http://localhost:8000

### Docker 部署 (可选)
```bash
# 构建镜像
docker build -t goo-fish-bargainer .

# 运行容器
docker run -p 8000:8000 goo-fish-bargainer
```

## 📖 使用指南

### 基本使用流程

1. **填写商品需求**
   - 在左侧面板输入商品描述
   - 设置最高价格预算
   - 填写咸鱼账号信息

2. **启动智能比价**
   - 点击"开始智能比价"按钮
   - 系统自动执行搜索和谈判

3. **查看实时进度**
   - 右侧面板显示实时执行状态
   - 查看任务指标和进度百分比
   - 观察各阶段执行详情

4. **获取比价结果**
   - 查看找到的所有商品
   - 查看最佳推荐商品
   - 查看节省金额统计

### 高级功能

#### 自定义搜索策略
```python
# 在配置文件中自定义搜索参数
search_config:
  max_results: 20
  price_range_tolerance: 0.1
  quality_threshold: 4.0
```

#### 谈判策略配置
```python
# 配置谈判参数
negotiation_config:
  max_rounds: 3
  discount_target: 0.15
  timeout_seconds: 30
```

## 🔧 配置说明

### 主配置文件 (config/config.yaml)
```yaml
# 应用配置
app:
  host: "0.0.0.0"
  port: 8000
  debug: false

# DeepSeek配置
deepseek:
  api_key: "your-api-key"
  model: "deepseek-chat"
  base_url: "https://api.deepseek.com"

# 咸鱼配置
xianyu:
  base_url: "https://2.taobao.com"
  timeout: 30
  retry_times: 3

# 日志配置
logging:
  level: "INFO"
  file: "logs/app.log"
```

### 环境变量
```bash
# 必需的环境变量
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export XIANYU_USERNAME="your-xianyu-username"
export XIANYU_PASSWORD="your-xianyu-password"
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python test_progress_features.py

# 运行系统测试
python test_system.py
```

### 功能测试
```bash
# 测试进度功能
python test_progress_features.py

# 测试修复功能
python test_fixes.py
```

## 📊 项目状态

### 已完成功能 ✅
- [x] 多Agent架构设计
- [x] 基础比价功能
- [x] 实时进度展示
- [x] WebSocket通信
- [x] 现代化UI界面
- [x] 响应式设计
- [x] 执行历史记录
- [x] 任务状态管理

### 开发中功能 🚧
- [ ] 高级谈判策略
- [ ] 商品图片识别
- [ ] 价格趋势分析
- [ ] 用户偏好学习

### 计划功能 📋
- [ ] 移动端APP
- [ ] 微信小程序
- [ ] 批量比价功能
- [ ] 价格预警系统

## 🤝 贡献指南

### 开发环境设置
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 运行代码检查
flake8 app/
black app/
```

### 提交规范
```bash
# 功能开发
git commit -m "feat: 添加新的搜索算法"

# 问题修复
git commit -m "fix: 修复WebSocket连接问题"

# 文档更新
git commit -m "docs: 更新API文档"
```

### Pull Request流程
1. Fork项目到个人仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m "feat: 添加新功能"`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的AI模型支持
- [MetaGPT](https://github.com/geekan/MetaGPT) - 多Agent框架基础
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Web框架
- [Bootstrap](https://getbootstrap.com/) - 响应式UI框架

## 📞 联系我们

- 项目主页:

## 📈 更新日志

### v1.2.0 (2024-01-XX)
- ✨ 新增实时进度展示功能
- 🎨 优化用户界面设计
- 🐛 修复WebSocket连接问题
- 📚 完善文档和测试

### v1.1.0 (2024-01-XX)
- ✨ 新增多Agent架构
- 🚀 提升比价性能
- 🔧 优化配置管理

### v1.0.0 (2024-01-XX)
- 🎉 首次发布
- ✨ 基础比价功能
- 🎨 现代化界面设计

---

<div align="center">
  <p>如果这个项目对您有帮助，请给我们一个 ⭐️</p>
  <p>Made with ❤️ by GooFishBargainer Team</p>
</div> 
