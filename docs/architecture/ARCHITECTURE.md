# KotlinCalendar 三客户端架构说明

**完整的全栈日历应用系统** - 三客户端 + 统一后端

---

## 🏗️ 系统架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                     客户端层（三个客户端）                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │   Android    │  │     Web      │  │   AcWing     │        │
│   │   客户端      │  │   客户端      │  │   客户端      │        │
│   │   (adapp)    │  │    (web)     │  │   (acapp)    │        │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│          │ Retrofit         │ Axios           │ Axios          │
│          │                  │                 │                │
└──────────┼──────────────────┼─────────────────┼────────────────┘
           │                  │                 │
           └──────────────────┼─────────────────┘
                              │ HTTPS
                              ▼
           ┌─────────────────────────────────────┐
           │    统一后端 API（Django REST）        │
           │         (backend)                   │
           └──────────────────┬──────────────────┘
                              │
                              ▼
                      ┌──────────────┐
                      │  PostgreSQL  │
                      │   数据库      │
                      └──────────────┘

【三客户端】手机 + 浏览器 + AcWing平台
【一后端】   Django REST API（统一数据接口）
```

---

## 📱 客户端 1：Android 客户端（adapp）

### 基本信息
- **目录**：`adapp/`
- **技术栈**：Kotlin + Room + Retrofit + Material Design
- **运行环境**：Android 手机/平板
- **部署方式**：编译成 APK 安装到手机
- **命名含义**：**ad**app = **A**ndroid **D**evelopment App
- **后端调用**：通过 Retrofit 调用统一的 Django API

### 核心功能
- 📅 日历视图（月视图）
- ✏️ 日程管理（增删改查）
- 🔔 提醒通知（AlarmManager）
- 💾 本地存储（Room Database）
- 🌐 网络同步（Retrofit API 调用）
- 🏮 农历显示
- 📡 日历订阅

### 技术亮点
- ✅ Kotlin Coroutines 异步处理
- ✅ Room 本地数据持久化
- ✅ Retrofit 2 网络请求
- ✅ Material Design 3 UI
- ✅ MVVM 架构模式

### 使用方式
```bash
cd adapp
# 打开 Android Studio → Run
# 或生成 APK 安装到手机
./gradlew assembleDebug
```

📖 **详细文档**：[adapp/README.md](adapp/README.md)

---

## 🌐 客户端 2：Web 客户端（web）

### 基本信息
- **目录**：`web/`（构建产物）+ `web_frontend/`（源码）
- **技术栈**：Vue 3 + FullCalendar + Element Plus + Bootstrap
- **运行环境**：现代浏览器（Chrome/Firefox/Safari）
- **部署方式**：Nginx 静态文件托管
- **访问地址**：https://app7626.acapp.acwing.com.cn
- **类型**：独立 Web 应用（SPA）
- **后端调用**：通过 Axios 调用统一的 Django API

### 核心功能
- 🎨 现代化日历界面（FullCalendar）
- 📝 日程管理（可视化操作）
- 📊 事件列表侧边栏
- 📱 响应式设计（支持移动端）
- 🔄 实时 API 交互

### 技术亮点
- ✅ Vue 3 Composition API
- ✅ FullCalendar 专业日历组件
- ✅ Element Plus UI 框架
- ✅ Axios HTTP 客户端
- ✅ Bootstrap 5 响应式布局
- ✅ 单文件构建（app.js + app.css）

### 构建方式
```bash
cd web_frontend
npm run build
# 输出到 ../web/
# 生成 app.js (1.35MB) + app.css (657KB)
```

📖 **详细文档**：[AcWing_Platform_Config.md](AcWing_Platform_Config.md)

---

## 🎮 客户端 3：AcWing 客户端（acapp）⏳

### 基本信息
- **目录**：`acapp/`（未来计划）
- **技术栈**：**纯 Vue3 CDN** + 可选 jQuery（无构建工具）
- **运行环境**：AcWing 平台（沙箱环境）
- **部署方式**：直接上传 JS/CSS 文件
- **访问方式**：通过 AcWing 平台加载
- **后端调用**：通过 fetch/axios CDN 调用统一的 Django API

### 核心特点（技术多样性 ⭐）
- ❌ **无构建工具**（直接写HTML/JS/CSS）
- ❌ **无 Bootstrap**（纯手写CSS，BEM命名）
- ❌ **无 npm 依赖**（Vue3 CDN引入）
- ✅ **极简轻量**（业务代码 <50KB）
- ✅ **export class Calendar**（AcWing平台要求）
- ✅ **样式隔离**（.kc-* 前缀）

### 与 Web 端的区别（技术对比）

| 特性 | Web 端（独立） | AcWing 端（集成） |
|------|--------------|------------------|
| **页面环境** | 独占浏览器页面 | 共享 AcWing 平台页面 |
| **Vue3** | npm + Vite 构建 | **CDN 引入** |
| **Bootstrap** | ✅ 可用 | ❌ 不用 |
| **UI库** | Element Plus + FullCalendar | **纯手写** |
| **构建工具** | Vite | **无** |
| **构建目标** | SPA应用（多文件） | **单JS+单CSS** |
| **入口** | `createApp().mount('#app')` | `export class Calendar` |
| **部署** | `npm run build` + git push | **直接 scp 上传** |
| **体积** | ~1.35MB（含所有库） | **<50KB（纯业务）** |

📖 **详细计划**：[acapp/PLAN.md](acapp/PLAN.md)

---

## 🚀 统一后端：Django REST API（backend）

### 基本信息
- **目录**：`backend/`
- **技术栈**：Django + DRF + PostgreSQL/SQLite
- **运行环境**：Linux 服务器
- **部署方式**：uWSGI + Nginx
- **访问地址**：https://app7626.acapp.acwing.com.cn/api
- **服务对象**：为三个客户端提供统一的数据接口

### 核心功能
- 🔌 RESTful API（Django REST Framework）
- 📡 网络日历订阅（iCalendar 格式）
- 🏮 农历转换 API
- 🔐 CORS 跨域支持
- 📊 Django Admin 后台管理

### API 接口
| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/events/` | GET/POST/PUT/DELETE | 日程 CRUD |
| `/api/calendars/` | GET | 公开日历列表 |
| `/api/calendars/{slug}/feed/` | GET | iCalendar 订阅 |
| `/api/lunar/?date=2025-11-06` | GET | 农历转换 |

### 技术亮点
- ✅ Django 4.2 LTS 稳定版
- ✅ DRF ViewSet 自动生成 CRUD
- ✅ CORS 允许跨域请求
- ✅ uWSGI 高性能部署
- ✅ Nginx 反向代理

### 部署方式
```bash
cd backend
./deploy.sh
# uWSGI 启动在 127.0.0.1:8000
# Nginx 反向代理到 /api/
```

📖 **详细文档**：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---


## 🔄 三客户端交互流程

### 数据流向图

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户操作层                                  │
└──────────────────────────────────────────────────────────────────┘
      │                    │                    │
      │ 手机端操作           │ 浏览器操作          │ AcWing平台操作
      ▼                    ▼                    ▼
┌──────────┐         ┌──────────┐         ┌──────────┐
│ Android  │         │   Web    │         │  AcWing  │
│  Client  │         │  Client  │         │  Client  │
│ (adapp)  │         │  (web)   │         │ (acapp)  │
│  Kotlin  │         │  Vue3    │         │  Vue3    │
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │
     │ Retrofit           │ Axios              │ Axios
     │ HTTP Request       │ HTTP Request       │ HTTP Request
     │                    │                    │
     └────────────────────┼────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Django REST API │ ← 统一后端
                 │    (backend)     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   PostgreSQL    │
                 │     数据库       │
                 └─────────────────┘

【关键点】
✅ 三个客户端使用同一套 API
✅ 数据存储在统一的后端数据库
✅ 客户端之间数据自动同步
```

### 典型场景举例

#### 场景 1：添加日程
1. **Android 端**：用户点击"添加日程"按钮
2. **Android 端**：填写表单（标题、时间、地点）
3. **Android 端**：`Retrofit.post("/api/events/", eventData)`
4. **Backend**：接收请求，保存到数据库，返回 JSON
5. **Android 端**：更新本地 Room 数据库，刷新 UI
6. **Web 端**：同时访问时，自动获取最新数据

#### 场景 2：查看农历
1. **Android 端**：用户点击某个日期
2. **Android 端**：`Retrofit.get("/api/lunar/?date=2025-11-06")`
3. **Backend**：调用农历库计算
4. **Backend**：返回 `{ "lunar": "农历十月初七", "zodiac": "蛇" }`
5. **Android 端**：在对话框中显示农历信息

#### 场景 3：订阅日历
1. **Android 端**：选择订阅源（如"中国节假日"）
2. **Android 端**：`Retrofit.get("/api/calendars/holidays/feed/")`
3. **Backend**：生成 iCalendar 格式数据
4. **Android 端**：解析并导入到本地数据库

---

## 📂 项目目录结构

```
KotlinCalendar/
│
├── adapp/                        # 【Android 端】
│   ├── app/
│   │   └── src/main/
│   │       ├── java/             # Kotlin 源码
│   │       │   ├── MainActivity.kt
│   │       │   ├── Event.kt
│   │       │   ├── AppDatabase.kt
│   │       │   └── api/          # Retrofit 网络层
│   │       └── res/              # 资源文件
│   ├── build.gradle.kts
│   └── README.md                 # Android 端文档
│
├── backend/                      # 【后端 API】
│   ├── api/                      # Django App
│   │   ├── models.py             # 数据模型
│   │   ├── serializers.py        # DRF 序列化器
│   │   ├── views.py              # API 视图
│   │   └── urls.py               # 路由配置
│   ├── calendar_backend/         # Django 项目配置
│   │   ├── settings.py           # 核心配置
│   │   └── urls.py               # 主路由
│   ├── requirements.txt          # Python 依赖
│   ├── uwsgi.ini                 # uWSGI 配置
│   ├── nginx.conf                # Nginx 配置
│   └── deploy.sh                 # 部署脚本
│
├── web/                          # 【Web 端构建产物】
│   ├── index.html
│   └── assets/
│       ├── app.js                # 单个 JS 文件
│       └── app.css               # 单个 CSS 文件
│
├── web_frontend/                 # 【Web 端源码】（不提交 Git）
│   ├── src/
│   │   ├── views/
│   │   │   └── CalendarView.vue  # 日历主视图
│   │   ├── components/           # Vue 组件
│   │   │   ├── NavBar.vue
│   │   │   ├── ContentField.vue
│   │   │   ├── Toolbar.vue
│   │   │   ├── EventDialog.vue
│   │   │   └── EventDetail.vue
│   │   ├── api/
│   │   │   └── index.js          # Axios 封装
│   │   └── router/
│   ├── package.json
│   └── vite.config.js            # Vite 构建配置
│
├── README.md                     # 项目总览
├── ARCHITECTURE.md               # 本文档（三端架构说明）
├── DEPLOYMENT_GUIDE.md           # 部署指南
└── AcWing_Platform_Config.md     # AcWing 平台配置
```

---

## 🎯 三客户端技术对比（展示技术多样性）

### 已实现（2 个客户端 + 1 个后端）

| 特性 | Android 客户端 | Web 客户端 | 后端 API |
|------|--------------|-----------|---------|
| **目录** | `adapp/` | `web/` + `web_frontend/` | `backend/` |
| **语言** | Kotlin | JavaScript | Python |
| **框架** | Android SDK | Vue 3 + Vite | Django |
| **构建工具** | Gradle | **Vite** | - |
| **运行位置** | 手机 | 浏览器 | 服务器 |
| **部署方式** | APK 安装 | Nginx 静态托管 | uWSGI |
| **本地存储** | Room | 无 | PostgreSQL |
| **网络通信** | Retrofit | Axios (npm) | - |
| **UI 框架** | Material Design | **Bootstrap + Element Plus** | Django Admin |
| **构建产物** | APK | **多文件（代码分割）** | - |
| **后端调用** | ✅ 统一 API | ✅ 统一 API | - |
| **样式** | 原生 Android XML | **可用全局CSS** | - |

### 未来计划（第 3 个客户端 - 技术差异化）

| 特性 | AcWing 客户端（计划） | Web 客户端（已实现） | 技术差异 |
|------|---------------------|-------------------|---------|
| **目录** | `acapp/` | `web/` | - |
| **语言** | JavaScript | JavaScript | 相同 |
| **框架** | Vue 3 **CDN** | Vue 3 **npm** | ⭐ **差异** |
| **构建工具** | ❌ **无** | ✅ Vite | ⭐ **差异** |
| **UI库** | ❌ **纯手写CSS** | ✅ Bootstrap + Element Plus | ⭐ **差异** |
| **jQuery** | ✅ **可选CDN** | ❌ 不用 | ⭐ **差异** |
| **运行环境** | AcWing 平台（沙箱） | 独立浏览器页面 | ⭐ **差异** |
| **样式方案** | **BEM命名** (.kc-*) | Bootstrap classes | ⭐ **差异** |
| **构建产物** | **单JS+单CSS** | 多文件（代码分割） | ⭐ **差异** |
| **文件体积** | **<50KB**（纯业务） | ~1.35MB（含库） | ⭐ **差异** |
| **部署** | **scp直接上传** | `npm build` + git | ⭐ **差异** |
| **主类** | `export class Calendar` | 无 | ⭐ **差异** |
| **后端调用** | ✅ 统一 API | ✅ 统一 API | 相同 |

---

## 💡 核心架构理念

### 🎯 统一后端，多客户端，多技术栈

```
                    统一的 Django REST API
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    【客户端1】          【客户端2】          【客户端3】
    Android 手机         Web 浏览器        AcWing 平台
     (adapp)              (web)             (acapp)
   Gradle构建          Vite构建          无构建工具
   Material UI      Bootstrap UI        纯手写CSS
        │                   │                   │
        └───────── 同一套 API 接口 ────────────┘
```

**架构优势**：
- ✅ 数据统一存储，自动同步
- ✅ 业务逻辑集中在后端
- ✅ 客户端只负责展示和交互
- ✅ 新增客户端无需修改后端
- ✅ 三个客户端可独立开发和部署

**技术多样性** ⭐：
- ✅ **3种构建工具**：Gradle / Vite / 无构建
- ✅ **3种UI方案**：Material Design / Bootstrap / 纯手写
- ✅ **3种语言**：Kotlin / JavaScript(npm) / JavaScript(CDN)
- ✅ **展示全栈能力**：原生应用 / 现代化Web / 极简轻量

### 🔧 为什么 AcWing 端需要特殊处理？

```
┌────────────────────────────────────────────────────┐
│            AcWing 平台页面                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  日历 App    │  │  聊天 App    │  │  平台UI  │  │
│  │  (acapp)     │  │  (其他)      │  │          │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└────────────────────────────────────────────────────┘
       多个应用共存同一页面 → 必须样式隔离！
```

**如果使用 Bootstrap（全局CSS）会发生什么？**
- ❌ Bootstrap 的 CSS reset 影响其他应用
- ❌ `.btn`、`.card` 等类名冲突
- ❌ 破坏 AcWing 平台自身的 UI

**解决方案**：
- ✅ 使用 Vue 的 `<style scoped>`
- ✅ 自定义样式，BEM 命名（如 `.kc-btn`）
- ✅ CSS Modules
- ✅ 库模式构建（不污染全局）

📖 **AcWing 端详细计划**：[acapp/PLAN.md](acapp/PLAN.md)

---

## 🚢 部署总结

### Android 端（adapp）
```bash
# 不需要部署到服务器！
cd adapp
./gradlew assembleDebug
# 生成 APK → 安装到手机
```

### 后端（backend）
```bash
# 服务器上执行
cd ~/kotlin_calendar/backend
git pull
./deploy.sh
```

### Web 端（web）
```bash
# 本地构建
cd web_frontend
npm run build

# 提交到 Git
git add web/
git commit -m "build: update web bundle"
git push

# 服务器更新
ssh acs@app7626.acapp.acwing.com.cn
cd ~/kotlin_calendar
git pull
# Nginx 自动提供静态文件服务
```

---

## 🌟 技术亮点总结

### 1. **完整的全栈架构**
- ✅ 前端（Web + Android）+ 后端（Django）
- ✅ 真实的生产环境部署
- ✅ HTTPS 安全访问

### 2. **前后端分离**
- ✅ RESTful API 通信
- ✅ JSON 数据交换
- ✅ 三端共享同一套 API

### 3. **现代化技术栈**
- ✅ Kotlin（Android 官方推荐）
- ✅ Django REST Framework（Python 最流行）
- ✅ Vue 3（前端三大框架之一）

### 4. **数据持久化**
- ✅ Room（Android 本地）
- ✅ PostgreSQL/SQLite（服务器）
- ✅ 云端备份与同步

### 5. **实用功能**
- ✅ 提醒通知
- ✅ 农历显示
- ✅ 日历订阅
- ✅ 响应式设计

---

## 📊 项目统计

| 指标 | 数量 |
|------|------|
| **总代码行数** | ~8,000 行 |
| **Kotlin 代码** | ~1,500 行 |
| **Python 代码** | ~800 行 |
| **Vue/JS 代码** | ~2,000 行 |
| **配置文件** | ~500 行 |
| **文档** | ~3,000 行 |
| **Git 提交** | 50+ commits |
| **开发时长** | 2 周 |

---

## 🎓 学习价值

通过这个项目，你可以学到：

### Android 开发
- ✅ Kotlin 语言基础
- ✅ Android UI 开发（XML + Material Design）
- ✅ Room 数据库操作
- ✅ Retrofit 网络请求
- ✅ Kotlin Coroutines 异步编程
- ✅ AlarmManager 定时任务
- ✅ Notification 通知系统

### 后端开发
- ✅ Django 框架基础
- ✅ Django REST Framework
- ✅ RESTful API 设计
- ✅ 数据库 ORM 操作
- ✅ CORS 跨域处理
- ✅ uWSGI + Nginx 部署

### 前端开发
- ✅ Vue 3 Composition API
- ✅ FullCalendar 日历组件
- ✅ Axios HTTP 请求
- ✅ 响应式设计
- ✅ Vite 构建工具
- ✅ Bootstrap 5 布局

### DevOps
- ✅ Git 版本控制
- ✅ Linux 服务器管理
- ✅ Nginx 配置
- ✅ SSL 证书部署
- ✅ 自动化部署脚本

---

## 🔗 相关链接

- **GitHub 仓库**: https://github.com/ppshuX/kotline_calendar
- **生产环境**: https://app7626.acapp.acwing.com.cn
- **API 地址**: https://app7626.acapp.acwing.com.cn/api
- **AcWing 平台**: https://www.acwing.com/

---

## 👨‍💻 作者信息

**学校**: 南昌大学  
**课程**: Android 开发课程设计  
**开发时间**: 2025 年 11 月  
**技术栈**: Kotlin + Django + Vue3  

---

## 📜 许可证

MIT License

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**

这是一个完整的、可运行的、真实部署的全栈项目，展示了从移动端到 Web 端的完整开发流程。

