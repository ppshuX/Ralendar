# 📚 Ralendar 项目文档

> **Ralendar** = Roamio + Calendar  
> Roamio 生态旗下的智能日历与时间管理工具

---

## 🚀 快速开始

### 对于用户
- **Web 端访问**: https://app7626.acapp.acwing.com.cn
- **AcWing 平台**: 搜索 "Ralendar" 或 App ID 7626
- **功能**: 日程管理、多端同步、一键登录、农历显示

### 对于开发者
1. **查看架构**: [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **阅读 API 文档**: [api/ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md](./api/ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md)
3. **部署指南**: [guides/DEPLOYMENT_GUIDE.md](./guides/DEPLOYMENT_GUIDE.md)
4. **开发日志**: [daily_logs/](./daily_logs/)

---

## 📂 文档导航

| 分类 | 说明 | 入口 |
|-----|------|------|
| 📘 **技术指南** | OAuth、认证、部署、迁移 | [guides/](./guides/) |
| 🌐 **API 文档** | Roamio 生态统一 API | [api/](./api/) |
| 📝 **开发日志** | 每日开发记录和总结 | [daily_logs/](./daily_logs/) |
| 📋 **未来计划** | 功能规划和产品路线图 | [plans/](./plans/) |
| 📦 **归档文档** | 过期或冗余的旧文档 | [archive/](./archive/) |

**完整索引**: [INDEX.md](./INDEX.md) 📍

---

## 🎯 核心功能

### 已完成 ✅
- 多端支持（Web、AcApp、Android）
- 三种登录方式（普通、AcWing、QQ）
- 日程 CRUD（增删改查）
- 农历显示
- 事件提醒
- 用户个人中心
- 账号绑定管理

### 开发中 🚧
- QQ 登录审核中
- 地图功能规划中
- AI 助手设计中

### 未来规划 ⏳
- 与 Roamio 生态融合
- 旅行计划 ↔ 日程同步
- 智能推荐
- 数据分析

---

## 📊 项目进展

**当前完成度**: 70%

| 模块 | 进度 |
|-----|------|
| 基础架构 | ████████████ 100% |
| 用户认证 | ███████████░ 95% |
| 日历功能 | █████████░░░ 85% |
| 多端适配 | ████████░░░░ 70% |
| 生态融合 | ██░░░░░░░░░░ 20% |

---

## 🛠️ 技术栈

**后端**:
- Django 4.2.16
- Django REST Framework
- Simple JWT
- python-dotenv
- lunarcalendar

**Web 前端**:
- Vue 3
- Vite
- Element Plus
- FullCalendar
- Axios

**AcApp 前端**:
- Vue 3
- Vuex
- AcWing SDK

**Android**:
- Kotlin
- Room Database
- Material Design

**部署**:
- Nginx
- uWSGI
- Linux (Ubuntu)

---

## 📞 联系方式

- **GitHub**: https://github.com/ppshuX/kotline_calendar
- **问题反馈**: GitHub Issues
- **邮箱**: 2064747320@qq.com

---

## 🎓 致谢

感谢以下平台的支持：
- [AcWing](https://www.acwing.com) - 提供平台和授权服务
- [腾讯 QQ](https://connect.qq.com) - QQ 互联 OAuth
- [腾讯云](https://cloud.tencent.com) - 云服务支持

---

**最后更新**: 2025-11-07  
**© 2025 Ralendar Team. Part of Roamio Ecosystem.**

**📍 查看完整文档索引**: [INDEX.md](./INDEX.md)
