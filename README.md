# 🗺️ 校园数字游民活地图 V3.0 | Campus Digital Nomad Map

> **Flask 全栈 + AI 智能预测的校园实时地图系统，帮助数字游民找到最佳学习和工作空间。**
>
> *A Flask full-stack campus real-time map system with AI intelligent prediction, helping digital nomads find the best study and work spaces.*

---

## 📌 项目简介 | Overview

校园数字游民活地图是一个基于 Flask 全栈架构的校园空间导航与拥挤度预测系统。系统集成了 AI 机器学习模型，能够实时预测校园各区域的拥挤程度，帮助学生和数字游民找到最舒适的学习、工作和休息空间。V3.0 版本在原有基础上进行了全面升级，优化了预测算法和用户体验。

Campus Digital Nomad Map is a campus space navigation and crowding prediction system based on Flask full-stack architecture. The system integrates AI machine learning models to predict the crowding level of each campus area in real-time, helping students and digital nomads find the most comfortable study, work, and rest spaces. Version 3.0 has been comprehensively upgraded, optimizing prediction algorithms and user experience.

---

## ✨ 核心特性 | Features

| 特性 | Feature | 说明 |
|------|---------|------|
| 🤖 AI 拥挤度预测 | AI Crowding Prediction | 基于机器学习模型，实时预测各区域拥挤程度 |
| 🗺️ 实时地图 | Real-time Map | 交互式校园地图，可视化展示空间信息 |
| 📍 空间导航 | Space Navigation | 快速定位图书馆、自习室、咖啡厅等学习空间 |
| 📊 数据可视化 | Data Visualization | 拥挤度趋势图表，历史数据分析 |
| 🔍 智能搜索 | Smart Search | 按类型、位置、拥挤度筛选最佳空间 |
| 📱 响应式设计 | Responsive Design | 适配桌面和移动端 |
| 🚀 一键部署 | One-Click Deploy | 附带部署脚本，支持多种环境 |
| 📝 完整文档 | Complete Docs | 功能详解、快速开始、项目报告等完整文档 |

---

## 📂 项目结构 | Project Structure

```
Campus-Digital-Nomad-Map/
├── app.py                           # Flask 应用主入口
├── run.py                           # 运行脚本
├── wsgi.py                          # WSGI 入口（生产部署）
├── config.py                        # 配置文件
├── requirements.txt                 # Python 依赖
├── init_db.py                       # 数据库初始化
├── deploy.py                        # 部署脚本
├── demo_v3.py                       # V3.0 演示脚本
├── start.bat                        # Windows 启动脚本
├── start.sh                         # Linux/Mac 启动脚本
├── .env                             # 环境变量
├── README.md                        # 项目说明
├── 功能详解.md                      # 功能详细说明
├── 快速开始指南.md                  # 快速开始指南
├── 项目完成报告.md                  # 项目完成报告
├── 项目说明.md                      # 项目说明文档
├── 爆款博客.md                      # 博客文章
├── 修复总结.md                      # 修复总结
├── ✅完成总结.md                    # 完成总结
├── campus_map/                      # 核心应用包
│   ├── __init__.py                  # 包初始化
│   └── config.py                    # 应用配置
├── models/                          # AI 模型
│   └── crowding_model.pkl           # 拥挤度预测模型
├── templates/                       # HTML 模板 (Jinja2)
├── static/                          # 静态资源
│   ├── css/                         # 样式文件
│   ├── js/                          # 前端脚本
│   └── images/                      # 图片资源
├── instance/                        # 实例目录（数据库等）
├── uploads/                         # 用户上传文件
└── tests/                           # 测试文件
```

---

## 🚀 快速开始 | Quick Start

### 环境要求 | Requirements

- Python >= 3.8
- pip >= 20.0.0

### 安装依赖 | Install Dependencies

```bash
pip install -r requirements.txt
```

### 初始化数据库 | Initialize Database

```bash
python init_db.py
```

### 启动服务 | Start Server

```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# 或直接运行
python run.py
```

服务默认运行在 `http://localhost:5000`

### 生产部署 | Production Deployment

```bash
# 使用 WSGI 服务器（如 Gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# 或使用 deploy.py 一键部署
python deploy.py
```

---

## 🔬 AI 预测模型 | AI Prediction Model

### 拥挤度预测 | Crowding Prediction

系统使用预训练的机器学习模型（`crowding_model.pkl`）对校园各区域的拥挤程度进行实时预测。模型基于历史人流数据、时间特征、天气因素等多维度特征进行训练，能够准确预测不同时段的拥挤程度。

The system uses a pre-trained machine learning model (`crowding_model.pkl`) to predict the crowding level of each campus area in real-time. The model is trained based on multi-dimensional features such as historical foot traffic data, time features, and weather factors, and can accurately predict crowding levels at different times.

### 预测维度 | Prediction Dimensions

| 维度 | Dimension | 说明 |
|------|-----------|------|
| ⏰ 时间特征 | Time Features | 小时、星期、节假日等 |
| 🌤️ 天气因素 | Weather Factors | 温度、降水、空气质量等 |
| 📍 区域特征 | Area Features | 区域类型、容量、位置等 |
| 📈 历史数据 | Historical Data | 过去人流趋势 |

---

## 🛠️ 技术栈 | Tech Stack

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | Flask | 轻量级 Python Web 框架 |
| 模板引擎 | Jinja2 | Flask 内置模板引擎 |
| 数据库 | SQLite | 轻量级关系型数据库 |
| AI 模型 | scikit-learn | 机器学习模型（.pkl） |
| 前端 | HTML/CSS/JS | 原生前端，无框架依赖 |
| 部署 | Gunicorn / WSGI | 生产环境部署 |
| 地图 | 交互式地图 | 校园空间可视化 |

---

## 📖 文档 | Documentation

项目附带完整的文档体系：

| 文档 | 说明 |
|------|------|
| `功能详解.md` | 系统功能详细说明 |
| `快速开始指南.md` | 快速上手指南 |
| `项目完成报告.md` | 项目完成总结报告 |
| `项目说明.md` | 项目整体说明 |
| `爆款博客.md` | 项目介绍博客文章 |
| `修复总结.md` | Bug 修复总结 |
| `✅完成总结.md` | 最终完成总结 |

---

## 🎯 应用场景 | Use Cases

- 📚 **学生自习**：找到最不拥挤的自习室和图书馆
- 💻 **远程办公**：数字游民寻找最佳工作空间
- ☕ **休闲社交**：发现校园内的咖啡厅和休息区
- 📊 **校园管理**：校方了解人流分布，优化资源配置
- 🎓 **新生导航**：帮助新生快速熟悉校园空间

---

## 📄 License

MIT License — 自由使用、修改和分发。
