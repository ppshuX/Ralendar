# 📅 Ralendar 项目概览

**智能日历系统 - 让时间管理更轻松**

---

## 🎯 项目简介

Ralendar 是一个现代化的智能日历系统，集成了事件管理、节假日查询、邮件提醒等功能，并与 Roamio 旅行计划系统深度集成。

**核心特性：**
- 📅 日程事件管理（CRUD）
- 🎉 中国法定节假日数据（自动同步）
- 📧 智能邮件提醒（Celery 定时任务）
- 🔗 Fusion API（与 Roamio 集成）
- 🎨 Django Admin 可视化管理后台
- 🗺️ 地图导航集成（百度地图）
- 👤 QQ OAuth 认证（UnionID 跨应用识别）

---

## 🏗️ 项目架构

```
Ralendar/
├── backend/                    # Django 后端
│   ├── api/                   # 核心 API 应用
│   │   ├── models/           # 数据模型
│   │   │   ├── event.py      # 事件模型
│   │   │   ├── user.py       # 用户/QQ用户模型
│   │   │   └── calendar_data.py  # 节假日/黄历/运势模型
│   │   ├── views/            # 视图层
│   │   │   ├── events.py     # 事件 CRUD
│   │   │   ├── fusion.py     # Roamio 集成 API
│   │   │   ├── holidays.py   # 节假日查询
│   │   │   ├── auth.py       # QQ 认证
│   │   │   └── ...
│   │   ├── url_patterns/     # URL 路由
│   │   ├── utils/            # 工具模块
│   │   │   └── holiday_sync.py  # 节假日同步服务
│   │   ├── management/       # Django 命令
│   │   │   └── commands/
│   │   │       └── import_holidays.py  # 节假日导入命令
│   │   ├── admin.py          # Django Admin 配置
│   │   ├── tasks.py          # Celery 异步任务
│   │   └── ...
│   ├── calendar_backend/      # Django 项目配置
│   │   ├── settings.py       # 配置文件
│   │   ├── celery.py         # Celery 配置
│   │   └── urls.py           # 根 URL
│   ├── static/               # 静态文件（collectstatic 生成）
│   ├── manage.py             # Django 管理脚本
│   ├── requirements.txt      # Python 依赖
│   ├── deploy.sh             # 部署脚本
│   ├── start_celery.sh       # Celery 启动脚本
│   └── test_holiday_sync.sh  # 节假日同步测试脚本
│
├── web_frontend/              # Vue 3 前端（开发环境）
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── components/       # 可复用组件
│   │   ├── composables/      # 组合式函数
│   │   ├── store/            # Pinia 状态管理
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── web/                       # 前端生产构建（打包后）
│   ├── index.html
│   └── assets/
│
├── acapp_frontend/            # AcWing 平台应用前端
│   └── ...
│
├── acapp/                     # AcWing 平台应用构建
│   └── dist/
│
├── docs/                      # 项目文档
│   ├── architecture/         # 架构文档
│   │   ├── ARCHITECTURE.md
│   │   └── RALENDAR_ROAMIO_INTEGRATION.md
│   ├── standards/            # 技术标准
│   │   ├── API_NAMING.md
│   │   ├── AUTH_STANDARD.md
│   │   └── FUSION_API_GUIDE.md
│   ├── features/             # 功能指南
│   │   ├── HOLIDAY_SYNC_GUIDE.md
│   │   └── DJANGO_ADMIN_GUIDE.md
│   ├── database/             # 数据库文档
│   │   └── CALENDAR_DATA_MODELS.md
│   ├── guides/               # 开发指南
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   └── ...
│   ├── daily_logs/           # 开发日志
│   ├── collaboration/        # 协作文档
│   │   └── RALENDAR_UPDATE_TO_ROAMIO.md
│   └── PROJECT_OVERVIEW.md   # 本文档
│
└── README.md                  # 项目说明
```

---

## 🔧 技术栈

### 后端
- **框架**：Django 4.x + Django REST Framework
- **Web 服务器**：Nginx（反向代理）
- **应用服务器**：uWSGI
- **数据库**：SQLite（开发/生产）
- **任务队列**：Celery + Redis
- **认证**：QQ OAuth 2.0 + JWT
- **邮件**：163 SMTP

### 前端
- **框架**：Vue 3 + Vite
- **状态管理**：Pinia
- **UI 组件**：FullCalendar（日历）
- **HTTP 客户端**：Axios
- **构建工具**：Vite

### 第三方服务
- **节假日数据**：Timor API
- **地图服务**：百度地图 API
- **用户认证**：QQ 互联 OAuth

---

## 📊 数据模型

### 核心模型

#### User（用户）
Django 自带用户模型

#### QQUser（QQ 用户）
- `user`：关联 User
- `openid`：QQ OpenID
- `unionid`：QQ UnionID（跨应用识别）
- `photo_url`：头像 URL
- `nickname`：昵称

#### Event（事件）
- `user`：所属用户
- `title`：标题
- `description`：描述
- `start_time`：开始时间
- `end_time`：结束时间
- `location`：地点
- `latitude/longitude`：坐标
- `source_app`：来源（ralendar/roamio）
- `source_id`：来源对象 ID
- `related_trip_slug`：关联旅行计划
- `email_reminder`：邮件提醒开关
- `reminder_minutes`：提前提醒分钟数
- `notification_sent`：提醒已发送标记

#### Holiday（节假日）
- `date`：日期
- `name`：节日名称
- `type`：类型（major/vacation/traditional/international）
- `is_legal_holiday`：是否法定假日
- `is_rest_day`：是否休息日
- `holiday_group`：假期组
- `emoji`：表情符号

#### LunarCalendar（黄历）*（待实现）*
- 农历日期、生肖、宜忌等

#### DailyFortune（运势）*（待实现）*
- 星座/生肖运势

---

## 🔗 API 端点

### Ralendar 自有 API

```
# 事件管理
GET    /api/v1/events/                      # 获取事件列表
POST   /api/v1/events/                      # 创建事件
GET    /api/v1/events/{id}/                 # 获取事件详情
PUT    /api/v1/events/{id}/                 # 更新事件
DELETE /api/v1/events/{id}/                 # 删除事件

# 节假日
GET    /api/v1/holidays/?year=2025          # 查询年份节假日
GET    /api/v1/holidays/check/?date=xxx     # 检查指定日期
GET    /api/v1/holidays/today/              # 查询今日

# 用户认证
GET    /api/auth/qq/login/                  # QQ 登录
GET    /api/auth/qq/callback/               # QQ 回调
```

### Fusion API（与 Roamio 集成）

```
# 批量事件管理（需要 Roamio JWT Token）
POST   /api/v1/fusion/events/               # 批量创建事件
GET    /api/v1/fusion/events/               # 查询用户事件

# 单个事件管理
GET    /api/v1/fusion/events/{id}/          # 获取事件详情
PUT    /api/v1/fusion/events/{id}/          # 更新事件
DELETE /api/v1/fusion/events/{id}/          # 删除事件
```

---

## 🚀 部署

### 生产环境

**服务器地址：** `app7626.acapp.acwing.com.cn`

**服务架构：**
```
用户请求
    ↓
Nginx (443) - SSL/TLS
    ├─ /admin/    → Django Admin (uWSGI:8000)
    ├─ /api/      → Django API (uWSGI:8000)
    ├─ /static/   → 静态文件
    └─ /          → Vue 前端
```

**后台服务：**
- uWSGI：运行 Django 应用
- Celery Worker：处理异步任务
- Celery Beat：定时任务调度
- Redis：任务队列

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Celery
celery -A calendar_backend worker --loglevel=info
celery -A calendar_backend beat --loglevel=info

# 前端
cd web_frontend
npm install
npm run dev
```

---

## 📈 功能状态

### ✅ 已完成

- [x] 用户认证（QQ OAuth）
- [x] 事件 CRUD 操作
- [x] 邮件提醒系统
- [x] Fusion API（Roamio 集成）
- [x] 节假日数据同步
- [x] Django Admin 管理后台
- [x] 地图导航集成
- [x] UnionID 跨应用识别

### 🚧 进行中

- [ ] 黄历功能
- [ ] 每日运势
- [ ] 前端 UI 优化

### 📋 计划中

- [ ] 智能推荐系统
- [ ] 数据统计分析
- [ ] 微信/短信通知
- [ ] 多地区支持
- [ ] AI 智能助手
- [ ] 社交功能

---

## 📚 文档索引

### 快速开始
- 📖 [README.md](../README.md) - 项目介绍
- 🚀 [部署指南](guides/DEPLOYMENT_GUIDE.md)

### 架构设计
- 🏗️ [系统架构](architecture/ARCHITECTURE.md)
- 🔗 [Ralendar-Roamio 集成架构](architecture/RALENDAR_ROAMIO_INTEGRATION.md)

### 开发规范
- 📝 [API 命名规范](standards/API_NAMING.md)
- 🔐 [认证标准](standards/AUTH_STANDARD.md)
- 🔗 [Fusion API 指南](standards/FUSION_API_GUIDE.md)

### 功能文档
- 📅 [节假日同步指南](features/HOLIDAY_SYNC_GUIDE.md)
- 🎨 [Django Admin 使用指南](features/DJANGO_ADMIN_GUIDE.md)

### 数据库
- 🗄️ [数据模型文档](database/CALENDAR_DATA_MODELS.md)

### 协作
- 🤝 [给 Roamio 团队的更新](collaboration/RALENDAR_UPDATE_TO_ROAMIO.md)

---

## 🎯 项目目标

**短期目标（1 个月）**
- 完成黄历和运势功能
- 优化前端用户体验
- 完善数据分析功能

**中期目标（3 个月）**
- 实现智能推荐系统
- 增强通知系统（微信/短信）
- 探索商业化可能性

**长期愿景（6 个月+）**
- 多地区/多语言支持
- AI 驱动的智能助手
- 构建"智能生活"生态系统

---

## 👥 团队

**Ralendar 开发团队**

*让时间管理更智能，让生活更美好！* ⏰✨

---

## 📞 联系方式

- **项目地址**：https://github.com/ppshuX/Ralendar
- **在线 Demo**：https://app7626.acapp.acwing.com.cn
- **管理后台**：https://app7626.acapp.acwing.com.cn/admin/

---

*最后更新：2025年11月10日*

