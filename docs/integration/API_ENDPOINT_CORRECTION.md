# ⚠️ 重要：Ralendar API 端点纠正

> **发送方**: Ralendar 团队  
> **接收方**: Roamio 团队  
> **日期**: 2025-11-09  
> **紧急程度**: 🔴 高（影响集成测试）

---

## 🐛 **发现的问题**

### **错误日志**：
```
POST https://app7508.acapp.acwing.com.cn/api/v1/ralendar/trips/events/ 500
创建事件失败: 401 Unauthorized for url: https://app7626.acapp.acwing.com.cn/api/v1/events/
```

### **问题分析**：

Roamio 目前调用的是：
```
❌ POST https://app7626.acapp.acwing.com.cn/api/v1/events/
```

应该调用的是：
```
✅ POST https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/batch/
```

---

## 🔄 **API 端点对比**

### **1. 错误的端点（Roamio 目前使用的）**

```
POST /api/v1/events/
```

**用途**：创建**单个**事件（Ralendar 用户自己创建日程时使用）

**数据格式**：
```json
{
  "title": "测试事件",
  "start_time": "2025-11-20T10:00:00+08:00",
  "end_time": "2025-11-20T11:00:00+08:00"
}
```

**问题**：
- ❌ 不支持批量创建
- ❌ 没有 `source_app` 字段
- ❌ 没有 `related_trip_slug` 字段
- ❌ 不适合跨应用集成

---

### **2. 正确的端点（Roamio 应该使用的）**

```
POST /api/v1/fusion/events/batch/
```

**用途**：**批量**创建事件（专为跨应用集成设计）

**数据格式**：
```json
{
  "source_app": "roamio",
  "related_trip_slug": "xiamen-trip-2025",
  "events": [
    {
      "title": "厦门五日游 - Day 1: 抵达厦门",
      "description": "14:00 抵达厦门高崎国际机场，入住酒店",
      "start_time": "2025-11-15T14:00:00+08:00",
      "end_time": "2025-11-15T18:00:00+08:00",
      "location": "厦门高崎国际机场",
      "latitude": 24.5440,
      "longitude": 118.1278,
      "reminder_minutes": 120,
      "email_reminder": true
    },
    {
      "title": "厦门五日游 - Day 2: 鼓浪屿",
      "description": "09:00 游览鼓浪屿，参观日光岩",
      "start_time": "2025-11-16T09:00:00+08:00",
      "end_time": "2025-11-16T17:00:00+08:00",
      "location": "鼓浪屿",
      "latitude": 24.4472,
      "longitude": 118.0656,
      "reminder_minutes": 60,
      "email_reminder": false
    }
  ]
}
```

**优点**：
- ✅ 支持批量创建（一次创建多个事件）
- ✅ 自动添加 `source_app` 标记
- ✅ 关联 `related_trip_slug`（便于管理）
- ✅ 返回详细的成功/失败信息

**响应格式**：
```json
{
  "success": true,
  "created_count": 2,
  "skipped_count": 0,
  "created_events": [
    {
      "id": 123,
      "title": "厦门五日游 - Day 1: 抵达厦门",
      "start_time": "2025-11-15T14:00:00+08:00"
    },
    {
      "id": 124,
      "title": "厦门五日游 - Day 2: 鼓浪屿",
      "start_time": "2025-11-16T09:00:00+08:00"
    }
  ],
  "errors": []
}
```

---

## 🔧 **Roamio 需要修改的代码**

### **文件：`backend/utils/ralendar_client.py`**

```python
class RalendarClient:
    def __init__(self):
        self.base_url = 'https://app7626.acapp.acwing.com.cn/api/v1'
    
    def batch_create_events(self, user_token, events_list, trip_slug):
        """批量创建事件（正确的端点）"""
        url = f"{self.base_url}/fusion/events/batch/"  # ✅ 使用 fusion API
        
        data = {
            "source_app": "roamio",
            "related_trip_slug": trip_slug,
            "events": events_list
        }
        
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
```

---

## 📋 **完整的 Ralendar Fusion API 列表**

### **1. 批量创建事件**
```
POST /api/v1/fusion/events/batch/
```

### **2. 获取旅行事件**
```
GET /api/v1/fusion/events/trip/{trip_slug}/
```

### **3. 删除旅行事件**
```
DELETE /api/v1/fusion/events/trip/{trip_slug}/
```

---

## 🎯 **侧边栏"添加待办"功能**

### **场景 1：侧边栏快速创建单个待办**

如果 Roamio 侧边栏是创建**单个待办**，可以使用：

```
POST /api/v1/fusion/events/single/
```

**数据格式**：
```json
{
  "source_app": "roamio",
  "title": "测试待办",
  "description": "这是一个测试",
  "start_time": "2025-11-20T10:00:00+08:00",
  "end_time": "2025-11-20T11:00:00+08:00"
}
```

**或者使用批量端点（events 数组只有 1 个元素）**：
```json
{
  "source_app": "roamio",
  "related_trip_slug": "sidebar-todo",
  "events": [
    {
      "title": "测试待办",
      "start_time": "2025-11-20T10:00:00+08:00"
    }
  ]
}
```

---

## 📊 **两种场景的 API 使用**

| 场景 | API 端点 | 数据格式 |
|------|---------|---------|
| **侧边栏添加待办** | `/fusion/events/batch/` | 1 个事件的数组 |
| **旅行计划同步** | `/fusion/events/batch/` | 多个事件的数组 |

**统一使用** `/fusion/events/batch/` 端点最简单！

---

## ⚠️ **关于 401 错误**

```
401 Unauthorized for url: https://app7626.acapp.acwing.com.cn/api/v1/events/
```

**可能原因**：
1. ✅ Roamio Token 格式正确（能通过 JWT 验证）
2. ❌ 但用户不存在或 UnionID 不匹配
3. ❌ 或者调用了错误的端点（基础端点权限更严格）

**使用 Fusion API 后应该能解决**！

---

## 🚀 **下一步行动**

### **Ralendar 侧（我们）**：
```bash
# 部署最新代码
ssh acs@app7626.acapp.acwing.com.cn
cd ~/kotlin_calendar
git pull
source backend/venv/bin/activate
cd backend
python manage.py migrate
pkill -f uwsgi
uwsgi --ini uwsgi.ini &
```

### **Roamio 侧（他们）**：
```python
# 修改 RalendarClient
# 把所有调用改为：
url = f"{self.base_url}/fusion/events/batch/"
```

---

## 📞 **给 Roamio 团队的回复**

```
嗨！我们发现了问题：

1. ⚠️ Ralendar 服务器还没部署最新代码
   - 正在部署中（预计 10 分钟）
   
2. ⚠️ Roamio 调用了错误的 API 端点
   - 当前: POST /api/v1/events/  (❌ 错误)
   - 应该: POST /api/v1/fusion/events/batch/  (✅ 正确)

请检查你们的 backend/utils/ralendar_client.py，
确保使用的是 fusion API 端点。

我们马上部署，10 分钟后重新测试！
```

---

## 🎯 **立即行动**

### **我需要部署 Ralendar！**

你现在可以：
1. **执行部署命令**（我提供的）
2. **给我服务器访问权**（我帮你部署）
3. **先通知 Roamio 团队修改端点**

---

**哪个选项？** 🚀
