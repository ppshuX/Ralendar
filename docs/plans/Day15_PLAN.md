# Day 15 工作计划

**日期**: 2025-11-08  
**目标**: 完善用户体验，实现特色功能

---

## 🎯 推荐任务（按优先级）

### 任务 1: 用户个人中心 ⭐⭐⭐⭐
**预计耗时**: 2-3 小时  
**难度**: 中等

**实现内容**:
1. **个人中心页面**
   - 显示用户基本信息
   - 显示头像（可点击放大）
   - 显示已绑定的第三方账号
   - 显示用户统计（事件数、日历数等）

2. **个人信息编辑**
   - 修改用户名
   - 修改邮箱
   - 修改密码（仅普通账号）
   - 上传自定义头像（可选）

3. **账号绑定状态显示**
   - ✅ 已绑定 AcWing
   - ✅ 已绑定 QQ
   - 绑定/解绑按钮

4. **页面路由**
   - `/profile` - 个人中心主页
   - 在导航栏下拉菜单添加入口

**技术要点**:
- Element Plus 表单组件
- 文件上传（头像）
- 表单验证

---

### 任务 2: 账号绑定和解绑 ⭐⭐⭐⭐
**预计耗时**: 2-3 小时  
**难度**: 中等

**实现内容**:
1. **绑定功能**
   - 普通账号绑定 AcWing
   - 普通账号绑定 QQ
   - AcWing 账号绑定 QQ
   - QQ 账号绑定 AcWing

2. **解绑功能**
   - 解绑 AcWing
   - 解绑 QQ
   - 防护机制：至少保留一种登录方式

3. **后端 API**
   ```python
   POST /api/user/bind/acwing/    # 绑定 AcWing
   POST /api/user/bind/qq/        # 绑定 QQ
   DELETE /api/user/unbind/acwing/  # 解绑 AcWing
   DELETE /api/user/unbind/qq/      # 解绑 QQ
   GET /api/user/bindings/        # 获取绑定状态
   ```

4. **业务逻辑**
   - 绑定时验证用户身份
   - 防止重复绑定
   - 防止绑定冲突（一个 OpenID 只能绑定一个用户）
   - 解绑前检查至少有一种登录方式

**技术要点**:
- OAuth 状态管理（区分登录和绑定）
- 数据库完整性检查
- 用户友好的错误提示

---

### 任务 3: 地图功能集成 ⭐⭐⭐⭐⭐
**预计耗时**: 4-5 小时  
**难度**: 中高

**实现内容**:
1. **选择地图服务**
   - 高德地图（推荐，国内稳定）
   - 申请高德地图 Web API Key

2. **后端地理编码**
   - Event 模型添加经纬度字段
   ```python
   latitude = models.FloatField(null=True, blank=True)
   longitude = models.FloatField(null=True, blank=True)
   ```
   - 地址 → 经纬度转换 API
   - 数据库迁移

3. **事件创建时选择地点**
   - 在 EventDialog 添加地图组件
   - 搜索地点
   - 点击地图选择位置
   - 自动填充地址

4. **地图视图**
   - 创建 MapView 页面
   - 显示所有有地点的事件
   - 点击标记显示事件详情
   - 导航到地点（调用地图 APP）

5. **日历视图集成**
   - 事件详情显示小地图
   - 点击可跳转到大地图

**技术要点**:
```bash
# 安装高德地图 SDK
npm install @amap/amap-jsapi-loader
```

```vue
<!-- 地图组件示例 -->
<template>
  <div id="map" style="width: 100%; height: 400px"></div>
</template>

<script setup>
import AMapLoader from '@amap/amap-jsapi-loader'
import { onMounted } from 'vue'

const props = defineProps({
  location: String,
  latitude: Number,
  longitude: Number
})

onMounted(() => {
  AMapLoader.load({
    key: 'your_amap_key',
    version: '2.0',
  }).then((AMap) => {
    const map = new AMap.Map('map', {
      zoom: 15,
      center: [props.longitude, props.latitude]
    })
    
    // 添加标记
    new AMap.Marker({
      position: [props.longitude, props.latitude],
      map: map
    })
  })
})
</script>
```

**参考文档**:
- 高德地图 Web API: https://lbs.amap.com/api/javascript-api/summary

---

### 任务 4: 前端提醒推送 ⭐⭐⭐
**预计耗时**: 2-3 小时  
**难度**: 中等

**实现内容**:
1. **浏览器通知权限**
   - 页面加载时请求通知权限
   - 用户设置页面控制通知开关

2. **定时检查**
   - 使用 `setInterval` 每分钟检查一次
   - 查找即将到来的事件（根据 reminder_minutes）
   - 发送桌面通知

3. **通知内容**
   - 事件标题
   - 开始时间
   - 地点（如果有）
   - 点击通知跳转到事件详情

4. **提示音**
   - 添加提示音文件
   - 用户可选择是否播放

**技术要点**:
```javascript
// 请求通知权限
if (Notification.permission === 'default') {
  await Notification.requestPermission()
}

// 发送通知
if (Notification.permission === 'granted') {
  new Notification('事件提醒', {
    body: event.title,
    icon: '/logo.png',
    tag: event.id
  })
}

// 定时检查
setInterval(() => {
  checkUpcomingEvents()
}, 60000)  // 每分钟
```

---

### 任务 5: AI 智能助手 ⭐⭐⭐⭐⭐
**预计耗时**: 5-6 小时  
**难度**: 高

**实现内容**:
1. **选择 AI 服务**
   - 讯飞星火（推荐，免费额度多）
   - 通义千问
   - ChatGLM

2. **自然语言理解**
   - 时间提取："明天下午3点" → 2025-11-08 15:00
   - 意图识别：创建/查询/删除/修改
   - 实体提取：标题、地点、时间

3. **AI 对话界面**
   - 聊天输入框
   - 对话历史显示
   - 快捷命令按钮

4. **智能功能**
   ```
   用户: "明天下午3点在图书馆开会"
   AI: 已为您创建事件：
       📅 标题：开会
       🕐 时间：2025-11-08 15:00
       📍 地点：图书馆
       
   用户: "下周一有什么安排"
   AI: 您在 2025-11-11 有以下安排：
       - 09:00 团队会议
       - 14:00 项目评审
   ```

**技术要点**:
- 正则表达式提取时间
- AI API 调用
- Prompt 工程
- 流式响应（可选）

---

### 任务 6: Android 端云同步 ⭐⭐⭐
**预计耗时**: 3-4 小时  
**难度**: 中等

**实现内容**:
1. **Android 网络库集成**
   ```kotlin
   // build.gradle
   implementation 'com.squareup.retrofit2:retrofit:2.9.0'
   implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
   ```

2. **登录界面**
   - 用户名密码登录
   - JWT Token 存储

3. **数据同步**
   - 上传本地事件到云端
   - 下载云端事件到本地
   - 增量同步（只同步变化的数据）
   - 冲突处理（最后修改时间优先）

4. **离线模式**
   - 离线时使用本地数据
   - 上线后自动同步
   - 显示同步状态

**技术要点**:
- Retrofit + Kotlin Coroutines
- Room + 网络同步
- SharedPreferences 存储 Token

---

### 任务 7: 日历分享功能 ⭐⭐⭐⭐
**预计耗时**: 3-4 小时  
**难度**: 中高

**实现内容**:
1. **日历导出**
   - 导出为 .ics 文件（iCalendar 格式）
   - 支持单个事件导出
   - 支持整个日历导出

2. **日历导入**
   - 上传 .ics 文件
   - 解析并导入事件
   - 防止重复导入

3. **分享链接**
   - 生成公开日历链接
   - 权限设置（只读/可编辑）
   - 二维码分享

4. **日历订阅**
   - 订阅他人的公开日历
   - 订阅外部日历（节假日、体育赛事）
   - WebCal 协议支持

**技术要点**:
- iCalendar 标准 (RFC 5545)
- Python icalendar 库
- 二维码生成

---

### 任务 8: 界面主题切换 ⭐⭐⭐
**预计耗时**: 1-2 小时  
**难度**: 简单

**实现内容**:
1. **主题系统**
   - 亮色主题（默认）
   - 暗色主题
   - 自动跟随系统

2. **主题切换按钮**
   - 导航栏添加切换按钮
   - 本地存储用户偏好

3. **CSS 变量**
   ```css
   :root {
     --primary-color: #667eea;
     --bg-color: #ffffff;
     --text-color: #303133;
   }
   
   [data-theme="dark"] {
     --primary-color: #8b9cfc;
     --bg-color: #1a1a1a;
     --text-color: #e0e0e0;
   }
   ```

4. **Element Plus 主题适配**
   - 使用 Element Plus 的暗色模式

**技术要点**:
- CSS 变量
- localStorage 持久化
- prefers-color-scheme 媒体查询

---

## 💡 Day 15 建议

### 上午（3-4 小时）：
**推荐：用户个人中心 + 账号绑定**
- 提升用户体验
- 完善账号管理功能
- 相对简单，容易完成

### 下午（3-4 小时）：
**推荐：地图功能集成**
- 最实用的功能
- 差异化优势
- 用户需求强

### 晚上（可选，2-3 小时）：
- 前端提醒推送
- 或者 AI 助手的前期准备
- 或者休息，准备明天

---

## 📝 开发建议

1. **优先完成核心功能**，再考虑扩展
2. **每个功能独立测试**，确保稳定性
3. **注重用户体验**，功能简单易用
4. **及时提交代码**，commit 信息清晰
5. **遇到困难先做简单的**，保持开发节奏

---

## 🎓 学习目标

- 掌握地图 SDK 集成（高德地图）
- 理解多账号绑定的数据库设计
- 学习 iCalendar 标准
- 了解 Web Notifications API
- 提升 UI/UX 设计能力

---

## 📅 里程碑目标

### 已完成（Day 1-14）：
- ✅ 基础架构（Django + Vue）
- ✅ 日历 CRUD 功能
- ✅ 多端登录（Web + AcApp）
- ✅ 多种登录方式（普通/AcWing/QQ）
- ✅ 代码模块化和清理

### 待完成（Day 15-20）：
- ⏳ 用户个人中心
- ⏳ 地图功能
- ⏳ 提醒推送
- ⏳ AI 助手
- ⏳ Android 云同步
- ⏳ 日历分享

### 未来规划：
- 📱 小程序端
- 🔔 微信推送
- 🌐 国际化（多语言）
- 🎨 自定义主题
- 📊 数据统计和可视化

---

## 🎯 Day 15 建议行动

**如果时间充裕（6+ 小时）**：
1. 用户个人中心（2-3 小时）
2. 账号绑定管理（2-3 小时）
3. 地图功能（开始，2 小时）

**如果时间有限（3-4 小时）**：
1. 用户个人中心（2-3 小时）
2. 主题切换（1-2 小时）

**如果想挑战**：
直接上地图功能或 AI 助手（高难度，高回报）

---

## 📊 项目成熟度评估

| 功能模块 | 完成度 | 优先级 |
|---------|-------|-------|
| 基础架构 | 100% | ⭐⭐⭐⭐⭐ |
| 用户认证 | 90% | ⭐⭐⭐⭐⭐ |
| 日历功能 | 85% | ⭐⭐⭐⭐⭐ |
| 多端适配 | 70% | ⭐⭐⭐⭐ |
| 地图功能 | 0% | ⭐⭐⭐⭐⭐ |
| AI 助手 | 0% | ⭐⭐⭐⭐ |
| 提醒推送 | 20% | ⭐⭐⭐ |
| 数据分享 | 10% | ⭐⭐⭐ |

**当前项目完成度：约 65%**

---

**准备好开始 Day 15 了吗？选择一个任务，我们开工吧！** 🚀

