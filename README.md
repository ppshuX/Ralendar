# 📅 Ralendar - Roamio 生态智能日历

> **Ralendar** = **R**oamio + C**alendar**  
> 让每一个时刻都有意义，让每一次旅行都有计划。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9+-purple.svg)](https://kotlinlang.org/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-green.svg)](https://vuejs.org/)

**Ralendar** 是一个现代化的智能日历应用，集成了日程管理、AI助手、地图定位、天气查询等丰富功能，支持 Android、Web、AcWing 三端同步，是 **Roamio 生态系统**的核心组件之一。

---

## 📋 目录

- [核心功能](#-核心功能)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [在线演示](#-在线演示)
- [项目结构](#-项目结构)
- [API 文档](#-api-文档)
- [部署指南](#-部署指南)
- [开发文档](#-开发文档)
- [项目进度](#-项目进度)
- [贡献指南](#-贡献指南)

---

## ✨ 核心功能

### 📅 日历视图

- **月视图**：整月日历网格，支持日期标记、节日显示、日程预览
- **周视图**：横向7天选择器 + 24小时时间线，便于查看一周安排
- **日视图**：详细时间线视图，精确到小时级别
- **流畅切换**：三种视图模式一键切换，动画过渡自然

### ✏️ 日程管理

- **完整 CRUD**：添加、编辑、查看、删除日程
- **丰富信息**：标题、描述、日期时间、提醒设置、地点位置
- **智能提醒**：基于 AlarmManager 的系统级提醒，支持自定义提前时间（5分钟/15分钟/30分钟/1小时/1天）
- **地图集成**：支持地点搜索、地图选点、经纬度定位、一键导航
- **重复事件**：支持重复日程设置

### 🤖 AI 智能助手

- **自然语言解析**：支持自然语言输入创建日程
  - 示例："明天下午3点开会" → 自动解析为结构化日程
- **智能日程总结**：AI 自动总结日程安排，提供时间管理建议
- **对话式管理**：支持与 AI 对话查询日程、创建日程、获取建议
- **节日问答**：向 AI 提问节日相关问题，获取节日历史、习俗、美食等信息

### 🌐 多端同步

- **Android 原生应用**：Kotlin + Room 数据库，Material Design 3 设计
- **Web 管理界面**：Vue 3 + Element Plus，现代化响应式设计
- **AcWing 平台集成**：Vue 3 + Vuex，无缝集成 AcWing 生态
- **数据同步**：本地优先策略，云端自动备份，离线可用

### 🔐 多种登录方式

- **普通账号**：邮箱注册登录
- **AcWing 一键登录**：OAuth 2.0 集成
- **QQ 互联登录**：UnionID 跨应用识别
- **账号绑定管理**：支持绑定/解绑多个账号

### 🏮 特色功能

- **农历显示**：支持中国传统节日、农历日期转换
- **网络订阅**：公共日历订阅、节日订阅、订阅管理
- **天气查询**：实时天气信息、自动定位、体感温度
- **运势查询**：每日运势（综合/爱情/事业/财运/健康）
- **个人中心**：用户信息管理、账号绑定、统计数据
- **生态融合**：与 Roamio 旅行平台深度集成，旅行计划自动同步为日程

---

## 🏗️ 技术架构

### 系统架构图

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
    │  - 阿里云通义千问 (AI 服务)                         │
    │  - 百度地图 / 高德地图 (地图服务)                   │
    └─────────────────────────────────────────────────────┘
```

### 技术栈

#### 后端技术栈

- **框架**：Django 4.2 + Django REST Framework 3.15
- **认证**：JWT (Simple JWT) + OAuth 2.0
- **数据库**：SQLite (生产) / PostgreSQL (可选)
- **异步任务**：Celery 5.2 + Redis 4.3
- **API 文档**：Django REST Framework 自动生成
- **部署**：Docker + Nginx + uWSGI

#### Android 技术栈

- **语言**：Kotlin 1.9+
- **架构**：MVVM + Repository 模式
- **数据库**：Room Database (SQLite)
- **网络**：Retrofit 2 + OkHttp
- **UI**：Material Design 3
- **异步**：Kotlin Coroutines + Flow
- **地图**：百度地图 SDK

#### Web 前端技术栈

- **框架**：Vue 3 + Vite
- **UI 组件**：Element Plus
- **日历组件**：FullCalendar
- **HTTP 客户端**：Axios
- **状态管理**：Vuex (AcApp) / Pinia (Web)

#### AcApp 前端技术栈

- **框架**：Vue 3 + Vue CLI
- **状态管理**：Vuex
- **平台集成**：AcWing SDK

### 设计模式

- **Repository 模式**：统一数据访问接口，支持本地/云端切换
- **Manager 模式**：业务逻辑封装，职责清晰
- **Facade 模式**：统一 API 接口，简化调用
- **MVVM 架构**：UI 与业务逻辑分离

---

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Node.js 20+
- Android Studio (Android 开发)
- Git

### 1. 克隆项目

```bash
git clone https://github.com/ppshuX/Ralendar.git
cd Ralendar
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
# 编辑 .env 文件，填入你的配置（数据库、OAuth、API密钥等）

# 数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

后端将运行在 http://localhost:8000

### 3. Web 前端设置

```bash
cd web_frontend

# 安装依赖
npm install

# 配置环境变量（可选）
# 创建 .env 文件，配置 API 地址等

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

### 5. Android 应用设置

1. 使用 Android Studio 打开 `adapp` 目录
2. 配置 `local.properties`，设置 SDK 路径
3. 同步 Gradle 依赖
4. 运行应用

**注意**：Android 应用需要配置百度地图 API Key（可选，用于地图功能）

---

## 🌐 在线演示

- **Web 端**: https://app7626.acapp.acwing.com.cn
- **AcApp**: 在 AcWing 平台搜索 "Ralendar" 或 App ID: 7626
- **API 地址**: https://app7626.acapp.acwing.com.cn/api
- **API 文档**: https://app7626.acapp.acwing.com.cn/api/docs/ (如果配置了 DRF 文档)

### 部署信息

- **服务器**：阿里云 ECS (Ubuntu 20.04)
- **部署方式**：Docker 容器化部署
- **域名**：AcWing 云应用平台托管
- **数据库**：SQLite (生产环境) / PostgreSQL (可选)
- **反向代理**：Nginx + uWSGI
- **SSL 证书**：AcWing 平台自动配置

---

## 📁 项目结构

```
Ralendar/
├── adapp/                    # Android 应用
│   ├── app/                  # 应用主模块
│   │   └── src/main/
│   │       ├── java/         # Kotlin 源代码
│   │       │   └── com/ncu/kotlincalendar/
│   │       │       ├── data/          # 数据层
│   │       │       │   ├── managers/  # Manager 类
│   │       │       │   ├── repository/# Repository 类
│   │       │       │   └── database/  # Room 数据库
│   │       │       ├── ui/            # UI 层
│   │       │       │   └── dialogs/   # 对话框组件
│   │       │       ├── api/           # 网络层
│   │       │       │   └── services/  # API 服务接口
│   │       │       └── utils/          # 工具类
│   │       └── res/          # 资源文件
│   └── 产品报告/             # 产品报告文档
│
├── backend/                  # Django 后端
│   ├── api/                  # API 应用
│   │   ├── models/          # 数据模型
│   │   ├── views/           # 视图层
│   │   │   ├── auth/        # 认证相关
│   │   │   ├── calendar/   # 日历核心
│   │   │   ├── external/   # 外部服务（农历、节假日、天气）
│   │   │   ├── ai/         # AI 助手
│   │   │   ├── integration/# 第三方集成（Roamio）
│   │   │   └── oauth/      # OAuth 2.0 服务器
│   │   ├── url_patterns/   # URL 路由
│   │   ├── serializers.py  # 序列化器
│   │   └── tasks.py        # Celery 异步任务
│   ├── calendar_backend/    # Django 项目配置
│   │   ├── settings.py     # 配置文件
│   │   ├── urls.py         # 主路由
│   │   └── celery.py       # Celery 配置
│   └── requirements.txt    # Python 依赖
│
├── web_frontend/            # Web 前端
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   └── api/            # API 调用
│   └── package.json
│
├── acapp_frontend/          # AcApp 前端
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── views/          # 页面视图
│   │   └── store/          # Vuex 状态管理
│   └── package.json
│
└── docs/                    # 项目文档
    ├── api/                # API 文档
    ├── guides/             # 开发指南
    ├── architecture/       # 架构文档
    └── integration/        # 集成文档
```

---

## 📚 API 文档

### 主要 API 端点

#### 认证相关
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/refresh/` - 刷新 Token
- `GET /api/auth/me/` - 获取当前用户信息
- `GET /api/auth/acwing/login/` - 获取 AcWing 登录 URL
- `GET /api/auth/qq/login/` - 获取 QQ 登录 URL

#### 日程管理
- `GET /api/events/` - 获取日程列表
- `POST /api/events/` - 创建日程
- `GET /api/events/{id}/` - 获取日程详情
- `PUT /api/events/{id}/` - 更新日程
- `DELETE /api/events/{id}/` - 删除日程

#### AI 助手
- `POST /api/ai/parse-event/` - 自然语言解析日程
- `POST /api/ai/summarize/` - 智能总结日程
- `POST /api/ai/chat/` - AI 对话

#### 外部服务
- `GET /api/lunar/` - 获取农历信息
- `GET /api/holidays/check/` - 检查节假日
- `GET /api/fortune/` - 获取每日运势
- `GET /api/weather/` - 获取天气信息

#### 融合功能 (Roamio)
- `POST /api/fusion/events/batch/` - 批量创建日程
- `GET /api/fusion/events/by-trip/{slug}/` - 按旅行查询日程
- `POST /api/fusion/sync/from-roamio/` - 从 Roamio 同步

完整 API 文档请查看：[API 文档](./docs/api/ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md)

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

### 第三方服务
- **阿里云通义千问** - AI 智能助手服务
- **百度地图 / 高德地图** - 地图定位和导航服务
- **OpenWeatherMap / 高德天气** - 天气查询服务

### 数据同步策略
- **本地优先** - Android 端使用 Room 数据库本地存储
- **云端备份** - 通过 REST API 同步到云端服务器
- **离线支持** - 本地数据可离线访问，联网时自动同步

---

## 📖 开发文档

完整文档位于 [docs/](./docs/) 目录：

### 快速开始
- 📖 [文档入口](./docs/README.md)
- 🚀 [快速开始指南](./docs/guides/QUICK_START.md)

### API 文档
- 🌐 [完整 API 文档](./docs/api/ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md)
- 🔗 [融合 API 指南](./docs/standards/FUSION_API_GUIDE.md)

### 开发指南
- 🏗️ [系统架构](./docs/architecture/ARCHITECTURE.md)
- 🔐 [认证指南](./docs/guides/ACWING_LOGIN_GUIDE.md)
- 🗺️ [地图配置](./docs/guides/BAIDU_MAP_SETUP.md)
- 📧 [邮件提醒](./docs/guides/EMAIL_REMINDER_GUIDE.md)
- 🚀 [部署指南](./docs/guides/DEPLOYMENT_GUIDE.md)

### 集成文档
- 🔗 [Roamio 集成指南](./docs/integration/ROAMIO_INTEGRATION_GUIDE.md)
- 🔐 [OAuth 集成](./docs/integration/QQ_UNIONID_INTEGRATION.md)

### 产品报告
- 📋 [产品功能介绍](./adapp/产品报告/①产品功能介绍.md)
- 🏗️ [程序概要设计](./adapp/产品报告/②程序概要设计.md)
- 📊 [软件架构图](./adapp/产品报告/③软件架构图.md)
- 💡 [技术亮点](./adapp/产品报告/④技术亮点及其实现原理.md)
- 🗄️ [数据库建模](./adapp/产品报告/⑤数据库建模报告.md)
- 📝 [开发文档](./adapp/产品报告/⑥开发文档.md)

---

## 📊 项目进度

**当前版本**: v1.0.0  
**完成度**: 约 88%

| 模块 | 状态 | 完成度 |
|-----|------|--------|
| 基础架构 | ✅ 完成 | 100% |
| 用户认证 | ✅ 完成 | 98% |
| 日程管理 | ✅ 完成 | 90% |
| 多端适配 | ✅ 完成 | 85% |
| 个人中心 | ✅ 完成 | 95% |
| 地图功能 | ✅ 完成 | 85% |
| AI 助手 | ✅ 完成 | 80% |
| 生态融合 | 🚧 进行中 | 40% |

### 已完成功能 ✅

- ✅ 日历视图（月/周/日三种视图）
- ✅ 日程 CRUD（增删改查）
- ✅ 提醒功能（AlarmManager）
- ✅ 网络订阅（公共日历、节日订阅）
- ✅ 农历显示
- ✅ AI 智能助手（自然语言解析、日程总结、对话）
- ✅ 地图定位（地点搜索、地图选点、导航）
- ✅ 天气查询
- ✅ 运势查询
- ✅ 多端同步（Android/Web/AcApp）
- ✅ OAuth 登录（AcWing/QQ）
- ✅ 云端部署

### 进行中 🚧

- 🚧 Roamio 生态融合（部分完成）
- 🚧 ICS 格式导入导出（规划中）

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

- ✅ 完整的后端 API 服务（Django REST Framework）
- ✅ Web 端管理界面（Vue 3）
- ✅ AcWing 平台集成
- ✅ 多种 OAuth 登录（AcWing、QQ）
- ✅ AI 智能助手（通义千问集成）
- ✅ 地图定位功能（百度地图 SDK）
- ✅ 云端部署上线（Docker + Nginx）
- ✅ 生态化产品设计（Roamio 融合）

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

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发规范

- **代码风格**：
  - Python: 遵循 PEP 8
  - Kotlin: 遵循 Kotlin 官方编码规范
  - JavaScript/Vue: 遵循 Vue Style Guide
- **提交信息**：使用语义化的 commit message
  - `feat:` 新功能
  - `fix:` 修复 bug
  - `docs:` 文档更新
  - `style:` 代码格式调整
  - `refactor:` 代码重构
  - `test:` 测试相关
  - `chore:` 构建/工具相关
- **分支策略**：
  - `main` - 主分支（稳定版本）
  - `develop` - 开发分支
  - `feature/xxx` - 功能分支
  - `bugfix/xxx` - Bug 修复分支
  - `hotfix/xxx` - 紧急修复分支

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 联系方式

- **GitHub**: https://github.com/ppshuX/Ralendar
- **问题反馈**: [GitHub Issues](https://github.com/ppshuX/Ralendar/issues)
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
- [Room](https://developer.android.com/training/data-storage/room) - Android 数据库框架
- [Retrofit](https://square.github.io/retrofit/) - 类型安全的 HTTP 客户端

---

## 📄 License

MIT License

Copyright (c) 2025 Ralendar Team (Part of Roamio Ecosystem)

---

**© 2025 Ralendar. Part of Roamio Ecosystem.**

**用心打造有温度的时间管理工具。** 💙

---

**🔗 相关项目**: [Roamio - 旅行规划平台](https://github.com/yourusername/roamio)
