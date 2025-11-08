# 🌏 Ralendar × Roamio 融合进度报告

> **更新时间**: 2025-11-08  
> **当前状态**: Phase 1 完成，准备开始 Phase 2

---

## ✅ 已完成任务

### Phase 1: 数据库与 API 基础（100% 完成）

#### 1. 数据库模型扩展 ✅

**Event 模型新增字段**:
- ✅ `source_app` - 来源应用（ralendar/roamio）
- ✅ `source_id` - 来源对象ID
- ✅ `related_trip_slug` - 关联旅行计划Slug
- ✅ `latitude` - 纬度坐标
- ✅ `longitude` - 经度坐标
- ✅ `map_provider` - 地图服务商（baidu/amap/tencent）
- ✅ `email_reminder` - 邮件提醒开关
- ✅ `notification_sent` - 提醒发送状态

**新增属性方法**:
- ✅ `map_url` - 生成地图导航链接（支持百度/高德/腾讯）
- ✅ `has_location` - 是否有地理位置
- ✅ `is_from_roamio` - 是否来自 Roamio

**新增数据库索引**:
- ✅ `event_user_start_idx` - 用户+开始时间索引
- ✅ `event_source_idx` - 来源应用+来源ID索引
- ✅ `event_trip_idx` - 旅行Slug索引

#### 2. UserMapping 模型 ✅

创建了用户账号映射表，支持 Roamio 和 Ralendar 用户关联：
- ✅ `ralendar_user` - Ralendar 用户ID
- ✅ `roamio_user_id` - Roamio 用户ID
- ✅ `roamio_username` - Roamio 用户名
- ✅ `qq_unionid` - QQ UnionID（统一标识）
- ✅ `sync_enabled` - 同步开关
- ✅ `last_sync_time` - 最后同步时间

#### 3. 数据库迁移 ✅

**迁移文件**: `backend/api/migrations/0007_add_fusion_fields.py`

**迁移内容**:
- ✅ 创建 UserMapping 表
- ✅ Event 表添加 8 个新字段
- ✅ 创建 3 个新索引
- ✅ 迁移已成功应用到数据库

#### 4. Serializer 更新 ✅

**EventSerializer 扩展**:
- ✅ 支持所有新字段的序列化和反序列化
- ✅ 添加字段验证（经纬度范围验证）
- ✅ 支持派生字段（map_url, has_location, is_from_roamio）

#### 5. 跨项目 API 接口 ✅

创建了 7 个融合相关的 API 接口：

| 接口 | 方法 | 路径 | 功能 |
|------|------|------|------|
| ✅ batch_create_events | POST | `/api/events/batch/` | 批量创建事件 |
| ✅ sync_from_roamio | POST | `/api/sync/from-roamio/` | 从 Roamio 同步旅行计划 |
| ✅ get_trip_events | GET | `/api/events/by-trip/{slug}/` | 查询旅行关联事件 |
| ✅ delete_trip_events | DELETE | `/api/events/by-trip/{slug}/delete/` | 删除旅行关联事件 |
| ✅ get_events_with_location | GET | `/api/events/with-location/` | 获取有地理位置的事件 |
| ✅ get_roamio_events | GET | `/api/events/from-roamio/` | 获取来自 Roamio 的事件 |
| ✅ mark_notification_sent | POST | `/api/events/{id}/mark-notified/` | 标记提醒已发送 |

**API 特性**:
- ✅ 完整的请求/响应文档（Docstring）
- ✅ 数据验证
- ✅ 错误处理
- ✅ 权限控制（IsAuthenticated）

---

## 📋 待办任务

### Phase 2: 地图集成（优先级：⭐⭐⭐⭐⭐）

- [ ] 申请百度地图 API Key
- [ ] 创建 MapPicker.vue 组件（地图选点）
- [ ] EventDialog.vue 集成地图选择
- [ ] 实现地图导航功能（navigateToMap）
- [ ] 创建 MapView.vue 页面（地图视图）

### Phase 3: 提醒机制（优先级：⭐⭐⭐）

- [ ] 配置 Django 邮件服务（SMTP）
- [ ] 实现邮件提醒任务（send_event_reminder_email）
- [ ] 实现 Web Notifications API
- [ ] 实现定时检查功能（startReminderCheck）

### Phase 4: 本地与云端双轨（优先级：⭐⭐⭐⭐）

- [ ] 创建 localEvents store（Pinia）
- [ ] 实现本地事项 CRUD（localStorage）
- [ ] 创建 EventListPanel.vue（双列表组件）
- [ ] 实现推送到云端功能（pushToCloud）
- [ ] 实现拉到本地功能（pullToLocal）

### Phase 5: 账号互通实现（优先级：⭐⭐⭐）

- [ ] 实现 RoamioAuthMiddleware（跨项目认证）
- [ ] 实现用户映射创建逻辑
- [ ] 测试跨项目 Token 验证

### Phase 6: Roamio 集成（优先级：⭐⭐⭐⭐⭐）

- [ ] 创建 TripEventForm.vue（Roamio 端）
- [ ] 调用 Ralendar API 同步事件
- [ ] 端到端测试

---

## 📊 进度统计

| 类别 | 完成 | 总计 | 进度 |
|------|------|------|------|
| 数据库设计 | 2 | 2 | 100% ✅ |
| 数据库迁移 | 1 | 1 | 100% ✅ |
| Serializer 更新 | 1 | 1 | 100% ✅ |
| API 接口实现 | 7 | 7 | 100% ✅ |
| 地图集成 | 0 | 5 | 0% ⏳ |
| 提醒机制 | 0 | 4 | 0% ⏳ |
| 本地双轨 | 0 | 5 | 0% ⏳ |
| 账号互通 | 0 | 3 | 0% ⏳ |
| Roamio 集成 | 0 | 2 | 0% ⏳ |

**总体进度**: **4/12** 阶段完成 (**33%**)

---

## 🎯 API 使用示例

### 1. 批量创建事件（Roamio → Ralendar）

```bash
POST https://app7626.acapp.acwing.com.cn/api/events/batch/
Authorization: Bearer <token>

{
  "source_app": "roamio",
  "related_trip_slug": "yunnan-trip-2025",
  "events": [
    {
      "title": "抵达昆明",
      "start_time": "2025-11-15T10:00:00Z",
      "location": "昆明长水国际机场",
      "latitude": 25.1019,
      "longitude": 102.9292,
      "reminder_minutes": 120,
      "email_reminder": true
    }
  ]
}
```

### 2. 查询旅行关联事件

```bash
GET https://app7626.acapp.acwing.com.cn/api/events/by-trip/yunnan-trip-2025/
Authorization: Bearer <token>

Response:
{
  "trip_slug": "yunnan-trip-2025",
  "events_count": 8,
  "events": [...]
}
```

### 3. 获取有地理位置的事件（用于地图视图）

```bash
GET https://app7626.acapp.acwing.com.cn/api/events/with-location/
Authorization: Bearer <token>

Response:
{
  "count": 15,
  "events": [
    {
      "id": 123,
      "title": "抵达昆明",
      "latitude": 25.1019,
      "longitude": 102.9292,
      "map_url": "https://api.map.baidu.com/marker?...",
      "has_location": true,
      ...
    }
  ]
}
```

---

## 🔥 下一步建议

### 最高优先级：地图集成 ⭐⭐⭐⭐⭐

**为什么优先做地图**:
1. **差异化功能** - 地图是项目的特色功能
2. **用户价值高** - 旅行规划必备功能
3. **技术依赖低** - 不依赖其他模块
4. **完成后可见** - 有明显的视觉效果

**预计时间**: 4-5 小时

**实现步骤**:
1. 申请百度地图 API Key（10分钟）
2. 创建 MapPicker.vue 组件（2小时）
3. 集成到 EventDialog（1小时）
4. 创建 MapView 页面（1-2小时）
5. 实现导航功能（30分钟）

### 第二优先级：本地与云端双轨 ⭐⭐⭐⭐

**为什么重要**:
1. **用户体验提升** - 未登录也能用
2. **独特设计** - 区别于其他日历应用
3. **技术挑战** - 展示技术能力

**预计时间**: 3-4 小时

---

## 📚 相关文档

- [完整融合方案](./plans/RALENDAR_ROAMIO_FUSION_PLAN.md)
- [API 文档](./api/ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md)
- [数据库设计](./ARCHITECTURE.md)

---

**准备好继续了吗？建议从地图集成开始！** 🗺️

