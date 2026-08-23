# 🗺️ 校园数字游民活地图 V3.0 | Campus Digital Nomad Map

> **Flask 全栈 + AI 拥挤度预测的校园空间导航系统——实时告诉你哪里人少、哪里有座，帮数字游民找到最佳工作空间。**
>
> *Flask full-stack campus space navigation with AI crowding prediction — real-time info on where's quiet and available, helping digital nomads find the best workspace.*

---

## ⭐ 核心卖点 | Why Star This

| 卖点 | Feature | 一句话 |
|------|---------|--------|
| 🤖 **AI 拥挤度预测** | AI Crowding Prediction | 机器学习模型实时预测各区域拥挤程度 |
| 🗺️ **交互式地图** | Interactive Map | 校园地图可视化，一键查看各空间状态 |
| 📍 **空间导航** | Space Navigation | 图书馆、自习室、咖啡厅快速定位 |
| 📅 **预约系统** | Reservation | 在线预约座位，到点提醒 |
| 🏆 **成就系统** | Achievements | 打卡激励，学习时长统计 |
| 📱 **响应式设计** | Responsive | 手机/平板/桌面全适配 |

---

## 🏆 技术栈 | Tech Stack

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3.30+-blue?logo=sqlite)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0+-orange?logo=scikit-learn)
![Jinja2](https://img.shields.io/badge/Jinja2-3.0+-red?logo=jinja)

---

## 📊 系统模块 | System Modules

| 模块 | 功能 | API 版本 |
|------|------|---------|
| 🗺️ 地图导航 | 校园地图 + 空间搜索 | v1 / v2 |
| 🤖 拥挤度预测 | AI 模型实时预测 | v1 / v2 |
| 📅 预约管理 | 座位预约 + 提醒 | v1 / v2 |
| 👤 用户系统 | 注册/登录/个人中心 | v1 |
| 🏆 成就系统 | 打卡 + 学习统计 | v1 |
| 📊 数据看板 | 使用数据可视化 | v2 |

---

## 🚀 快速开始 | Quick Start

```bash
git clone https://github.com/Windyhhh/Campus-Digital-Nomad-Map.git
cd Campus-Digital-Nomad-Map
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动服务
python run.py
# 或 Windows
start.bat
```

访问 `http://localhost:5000`

---

## 📂 项目结构 | Project Structure

```
Campus-Digital-Nomad-Map/
├── app.py                     # Flask 应用工厂
├── run.py                     # 运行入口
├── wsgi.py                    # WSGI 入口 (生产部署)
├── init_db.py                 # 数据库初始化
├── deploy.py                  # 部署脚本
├── requirements.txt           # 依赖
├── campus_map/                # 核心应用包
│   ├── __init__.py            # 应用工厂
│   ├── config.py              # 配置
│   ├── ml/
│   │   └── predictor.py       # 拥挤度预测模型
│   ├── models/                # 数据模型
│   ├── routes/
│   │   ├── api_v1.py          # API v1
│   │   ├── api_v2.py          # API v2
│   │   ├── auth.py            # 认证路由
│   │   ├── pages.py           # 页面路由
│   │   ├── predictions.py     # 预测路由
│   │   └── reservations.py    # 预约路由
│   └── utils/
│       ├── achievements.py    # 成就系统
│       └── sample_data.py     # 示例数据
├── models/
│   └── crowding_model.pkl     # 预训练模型
├── templates/                 # Jinja2 模板
├── static/                    # 静态资源
├── instance/                  # 实例目录 (数据库)
├── uploads/                   # 用户上传
└── tests/                     # 测试
```

---

## 🔬 AI 预测模型 | AI Prediction Model

### 拥挤度预测 | Crowding Prediction

```
输入特征:
  - 时间特征: 小时、星期、是否节假日
  - 区域特征: 区域类型、容量、位置
  - 历史特征: 过去同时段平均人流

模型: scikit-learn (预训练 .pkl)
输出: 拥挤度等级 (空闲/较少/一般/较多/拥挤)
```

### 预测流程 | Prediction Pipeline

```
用户请求某区域拥挤度
  ↓
加载时间 + 区域特征
  ↓
预训练模型推理
  ↓
返回拥挤度等级 + 建议
  ↓
地图上颜色标注 (绿→黄→红)
```

---

## 🎯 应用场景 | Use Cases

- 📚 **学生自习**：找到最不拥挤的自习室和图书馆
- 💻 **远程办公**：校园数字游民寻找最佳工作空间
- ☕ **休闲社交**：发现校园内的咖啡厅和休息区
- 🏫 **新生导航**：帮助新生快速熟悉校园空间
- 🏢 **校园管理**：校方了解人流分布，优化资源配置

---

## 📖 API 文档 | API Docs

### v1 API

```
GET  /api/v1/spaces              # 获取所有空间
GET  /api/v1/spaces/<id>         # 获取空间详情
GET  /api/v1/predict/<space_id>  # 预测拥挤度
POST /api/v1/reservations        # 创建预约
GET  /api/v1/reservations        # 获取预约列表
```

### v2 API (增强版)

```
GET  /api/v2/dashboard           # 数据看板
GET  /api/v2/spaces/nearby       # 附近空间搜索
GET  /api/v2/predict/batch       # 批量预测
```

---

## 📄 License

MIT License — 自由使用、修改和分发。

---

> 💡 **AI 驱动的校园空间导航，Star ⭐ 支持开源校园项目！**
