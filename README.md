# 📅 Ralendar - Roamio 生态智能日历

> **Ralendar** = **R**oamio + C**alendar**  
> Roamio 生态旗下的时间管理与日程助手

**让每一个时刻都有意义，让每一次旅行都有计划。** 🌟

---

## 🌏 关于 Roamio 生态

**Ralendar** 是 [Roamio](https://github.com/yourusername/roamio) 生态系统的重要组成部分：

- **Roamio** 🗺️ - 旅行规划与内容分享平台
- **Ralendar** 📅 - 智能日历与时间管理（本项目）
- **Rote** 📝 - 笔记与知识管理（规划中）
- **Rapture** 📸 - 照片与回忆记录（规划中）

### 生态协同
- 在 Roamio 中规划旅行 → 自动同步到 Ralendar 日程
- Ralendar 提醒即将到来的行程 → 推送到 Roamio 提前准备
- 统一的账号体系（QQ、AcWing 一键登录）
- 无缝的数据互通

---

## ✨ 核心功能

### 🎯 日程管理
- ✅ 可视化日历（月/周/日视图）
- ✅ 日程增删改查
- ✅ 拖拽调整时间
- ✅ 多颜色标签
- ✅ 重复事件支持

### 🔔 智能提醒
- ✅ 自定义提前提醒时间
- ✅ 桌面通知推送
- ✅ 邮件提醒（规划中）
- ✅ 微信推送（规划中）

### 🌐 多端支持
- ✅ **Web 端** - 现代化的网页应用
- ✅ **AcApp 端** - AcWing 平台集成
- ✅ **Android 端** - 原生 Kotlin 应用
- ⏳ **小程序** - 微信小程序（规划中）

### 🔐 多种登录方式
- ✅ 普通账号注册登录
- ✅ AcWing 一键登录
- ✅ QQ 互联一键登录
- ⏳ 微信登录（规划中）

### 🏮 特色功能
- ✅ 农历显示（支持中国传统节日）
- ✅ 用户个人中心
- ✅ 账号绑定管理
- ⏳ 地图定位（规划中）
- ⏳ AI 语音助手（规划中）

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     Ralendar 架构                        │
└─────────────────────────────────────────────────────────┘

    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Web 端   │  │ AcApp端  │  │Android端 │
    │ (Vue 3)  │  │ (Vue 3)  │  │ (Kotlin) │
    └────┬─────┘  └────┬─────┘  └────┬─────┘
         │             │             │
         └─────────────┼─────────────┘
                       │ HTTPS / REST API
                       │ (app7626.acapp.acwing.com.cn)
                       ▼
    ┌─────────────────────────────────────────────────────┐
    │            ☁️ 阿里云 ECS 服务器                      │
    │         (47.121.137.60 / Ubuntu 20.04)             │
    ├─────────────────────────────────────────────────────┤
    │  ┌──────────────────────────────────────────────┐   │
    │  │         Nginx (反向代理 + SSL)               │   │
    │  └──────────────────┬───────────────────────────┘   │
    │                     ▼                               │
    │  ┌──────────────────────────────────────────────┐   │
    │  │         Docker 容器化部署                     │   │
    │  │  ┌────────────────────────────────────────┐  │   │
    │  │  │  Django REST Framework + uWSGI         │  │   │
    │  │  │  ┌────────────────────────────────────┐│  │   │
    │  │  │  │ Events │ Auth │ OAuth │ Lunar │ API││  │   │
    │  │  │  └──────────────┬─────────────────────┘│  │   │
    │  │  └──────────────────┼───────────────────────┘  │   │
    │  └──────────────────────┼───────────────────────────┘   │
    │                         ▼                               │
    │  ┌──────────────────────────────────────────────┐   │
    │  │    SQLite (生产) / PostgreSQL (可选)          │   │
    │  └──────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────┘
                       ▲
                       │ 数据同步
                       │
    ┌─────────────────────────────────────────────────────┐
    │              Android 本地存储                        │
    │  ┌──────────────────────────────────────────────┐   │
    │  │         Room Database (SQLite)                │   │
    │  │  - 离线优先策略                               │   │
    │  │  - 自动云端同步                               │   │
    │  └──────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────┐
    │               ☁️ 其他云服务                         │
    │  - 腾讯云 COS (文件存储，可选)                      │
    │  - AcWing 云平台 (域名 + HTTPS + CDN)              │
    └─────────────────────────────────────────────────────┘
```

### 技术栈

**后端**:
- Django 4.2 + Django REST Framework
- JWT Authentication (Simple JWT)
- OAuth2 (AcWing, QQ)
- python-dotenv (环境变量)
- lunarcalendar (农历转换)

**Web 前端**:
- Vue 3 + Vite
- Element Plus UI
- FullCalendar (日历组件)
- Axios (HTTP 客户端)

**AcApp 前端**:
- Vue 3 + Vuex
- AcWing SDK

**Android**:
- Kotlin
- Room Database
- Retrofit 2
- Material Design 3

**部署**:
- Docker (容器化部署)
- Nginx (反向代理 + 静态文件)
- uWSGI (WSGI 服务器)
- Linux (Ubuntu 20.04)

---

## ☁️ 云资源使用

本项目使用了以下云服务资源：

### 云服务器
- **阿里云 ECS** - 后端 API 服务部署
  - 服务器 IP: 47.121.137.60
  - 操作系统: Ubuntu 20.04
  - 部署方式: Docker 容器化部署
  - 用途: Django 后端服务、Nginx 反向代理

### 云数据库
- **SQLite** - 本地数据库（开发/测试环境）
- **PostgreSQL** - 云端数据库（生产环境，可选）
  - 支持数据持久化和高并发访问

### 云存储
- **腾讯云 COS** - 对象存储服务（可选）
  - 用于存储用户上传的文件、图片等静态资源

### 云平台
- **AcWing 云应用平台** - 应用托管和域名服务
  - 域名: https://app7626.acapp.acwing.com.cn
  - 提供 HTTPS 证书和 CDN 加速

### 数据同步策略
- **本地优先** - Android 端使用 Room 数据库本地存储
- **云端备份** - 通过 REST API 同步到云端服务器
- **离线支持** - 本地数据可离线访问，联网时自动同步

---

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Node.js 20+
- Git

### 1. 克隆项目

```bash
git clone https://github.com/ppshuX/kotline_calendar.git
cd kotline_calendar
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

后端将运行在 http://localhost:8000

### 3. Web 前端设置

```bash
cd web_frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

Web 前端将运行在 http://localhost:5173

### 4. AcApp 前端设置

```bash
cd acapp_frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

---

## 🌐 在线演示

- **Web 端**: https://app7626.acapp.acwing.com.cn
- **AcApp**: 在 AcWing 平台搜索 "Ralendar" 或 App ID: 7626
- **API 地址**: https://app7626.acapp.acwing.com.cn/api

### 部署信息
- **服务器**: 阿里云 ECS (Ubuntu 20.04)
- **部署方式**: Docker 容器化部署
- **域名**: AcWing 云应用平台托管
- **数据库**: SQLite (生产环境) / PostgreSQL (可选)
- **反向代理**: Nginx + uWSGI

---

## 📚 文档

完整文档位于 [docs/](./docs/) 目录：

- 📖 [文档入口](./docs/README.md)
- 🌐 [API 文档](./docs/api/ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md)
- 📘 [技术指南](./docs/guides/)
- 📝 [开发日志](./docs/daily_logs/)
- 🏗️ [系统架构](./docs/ARCHITECTURE.md)

---

## 📊 项目进度

**当前版本**: v1.0.0  
**完成度**: 约 85%

| 模块 | 状态 | 完成度 |
|-----|------|--------|
| 基础架构 | ✅ 完成 | 100% |
| 用户认证 | ✅ 完成 | 98% |
| 日程管理 | ✅ 完成 | 90% |
| 多端适配 | ✅ 完成 | 85% |
| 个人中心 | ✅ 完成 | 95% |
| 地图功能 | 🚧 规划中 | 0% |
| AI 助手 | 🚧 规划中 | 0% |
| 生态融合 | 🚧 进行中 | 40% |

---

## 🎓 项目背景

本项目最初作为**南昌大学 Android 开发课程的大作业**开发，现已发展成为 **Roamio 生态系统**的核心组件之一。

### 课程要求
- ✅ Kotlin 原生开发
- ✅ Material Design 设计规范
- ✅ Room 数据库
- ✅ 提醒功能
- ✅ 扩展功能（网络订阅、农历）

### 实际完成
不仅完成了所有课程要求，还额外实现了：
- ✅ 完整的后端 API 服务
- ✅ Web 端管理界面
- ✅ AcWing 平台集成
- ✅ 多种 OAuth 登录
- ✅ 云端部署上线
- ✅ 生态化产品设计

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发规范
- 代码风格：遵循 PEP 8 (Python) 和 Vue Style Guide
- 提交信息：使用语义化的 commit message
- 分支策略：feature/xxx, bugfix/xxx, hotfix/xxx

---

## 📞 联系方式

- **GitHub**: https://github.com/ppshuX/kotline_calendar
- **问题反馈**: [GitHub Issues](https://github.com/ppshuX/kotline_calendar/issues)
- **邮箱**: 2064747320@qq.com

---

## 🎖️ 致谢

感谢以下平台和开源项目的支持：

- [AcWing](https://www.acwing.com) - 平台和授权服务
- [腾讯 QQ 互联](https://connect.qq.com) - OAuth 登录支持
- [Django](https://www.djangoproject.com/) - 强大的 Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式前端框架
- [Element Plus](https://element-plus.org/) - 优秀的 UI 组件库
- [FullCalendar](https://fullcalendar.io/) - 专业的日历组件

---

## 📄 License

MIT License

Copyright (c) 2025 Ralendar Team (Part of Roamio Ecosystem)

---

**© 2025 Ralendar. Part of Roamio Ecosystem.**

**用心打造有温度的时间管理工具。** 💙

---

**🔗 相关项目**: [Roamio - 旅行规划平台](https://github.com/yourusername/roamio)
