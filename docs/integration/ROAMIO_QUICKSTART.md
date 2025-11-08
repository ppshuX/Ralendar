# 🚀 Roamio × Ralendar 集成快速启动指南

**目标读者**: Roamio 开发团队  
**集成时间**: 约 2-3 小时  
**最后更新**: 2025-11-08

---

## 📋 准备清单

在开始之前，请确认：

- [ ] 有权访问 Roamio 的代码库
- [ ] 有权访问 Roamio 的服务器/生产环境
- [ ] 有 Aliyun RDS MySQL 数据库访问权限
- [ ] 理解 Django REST Framework 基础

---

## ⚡ 5 分钟快速集成

### 步骤 1: 配置环境变量

在 Roamio 的 `.env` 文件中添加：

```bash
# ==================== Ralendar 集成配置 ====================

# Ralendar API 端点
RALENDAR_API_URL=https://app7626.acapp.acwing.com.cn/api/v1

# 共享密钥（用于 JWT Token 验证）
SHARED_SECRET_KEY=your-shared-secret-key-here

# 数据库配置（如果要使用共享数据库）
USE_SHARED_DB=True
DB_HOST=your-mysql-host.rds.aliyuncs.com
DB_PORT=3306
DB_NAME=roamio_production
DB_USER=ralendar_user
DB_PASSWORD=your-secure-database-password-here
```

### 步骤 2: 安装依赖

```bash
pip install requests  # 用于 API 调用
```

### 步骤 3: 创建 API 客户端

在 Roamio 项目中创建 `ralendar_client.py`：

```python
import requests
from django.conf import settings

class RalendarClient:
    """Ralendar API 客户端"""
    
    def __init__(self):
        self.base_url = settings.RALENDAR_API_URL
        self.timeout = 10
    
    def get_headers(self, user_token):
        """构造请求头（使用用户的 JWT Token）"""
        return {
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
    
    def create_event(self, user_token, event_data):
        """
        为旅行计划创建日程事件
        
        参数:
            user_token (str): 用户的 JWT access_token
            event_data (dict): 事件数据
                {
                    "title": "行程标题",
                    "description": "详细描述",
                    "start_time": "2025-11-20T10:00:00+08:00",
                    "end_time": "2025-11-20T12:00:00+08:00",
                    "location": "北京故宫",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                    "email_reminder": True,
                    "source_app": "roamio",
                    "related_trip_slug": "beijing-trip-2025"
                }
        
        返回:
            dict: 创建成功的事件数据
        """
        url = f"{self.base_url}/events/"
        headers = self.get_headers(user_token)
        
        response = requests.post(url, json=event_data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def batch_create_events(self, user_token, events_list, trip_slug):
        """
        批量创建多个事件
        
        参数:
            user_token (str): 用户的 JWT Token
            events_list (list): 事件列表
            trip_slug (str): 旅行计划的 slug
        
        返回:
            dict: {"created": [...], "failed": [...]}
        """
        url = f"{self.base_url}/fusion/events/batch/"
        headers = self.get_headers(user_token)
        
        data = {
            "events": events_list,
            "source_app": "roamio",
            "related_trip_slug": trip_slug
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def get_trip_events(self, user_token, trip_slug):
        """
        获取某个旅行计划的所有事件
        
        参数:
            user_token (str): 用户的 JWT Token
            trip_slug (str): 旅行计划的 slug
        
        返回:
            list: 事件列表
        """
        url = f"{self.base_url}/fusion/events/trip/{trip_slug}/"
        headers = self.get_headers(user_token)
        
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def delete_trip_events(self, user_token, trip_slug):
        """
        删除某个旅行计划的所有事件
        
        参数:
            user_token (str): 用户的 JWT Token
            trip_slug (str): 旅行计划的 slug
        
        返回:
            dict: {"deleted_count": 5}
        """
        url = f"{self.base_url}/fusion/events/trip/{trip_slug}/"
        headers = self.get_headers(user_token)
        
        response = requests.delete(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
```

### 步骤 4: 在 Django View 中使用

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .ralendar_client import RalendarClient

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_trip_to_calendar(request, trip_slug):
    """
    将旅行计划添加到 Ralendar 日历
    
    前端调用示例:
    POST /api/trips/beijing-trip-2025/add-to-calendar/
    {
        "events": [
            {
                "title": "参观故宫",
                "start_time": "2025-11-20T09:00:00+08:00",
                "end_time": "2025-11-20T12:00:00+08:00",
                "location": "北京故宫",
                "latitude": 39.9163,
                "longitude": 116.3972,
                "email_reminder": true
            },
            {
                "title": "游览长城",
                "start_time": "2025-11-21T08:00:00+08:00",
                "end_time": "2025-11-21T16:00:00+08:00",
                "location": "八达岭长城"
            }
        ]
    }
    """
    # 获取用户的 JWT Token
    user_token = request.auth.token if hasattr(request.auth, 'token') else str(request.auth)
    
    # 获取事件列表
    events = request.data.get('events', [])
    
    if not events:
        return JsonResponse({'error': '事件列表不能为空'}, status=400)
    
    # 调用 Ralendar API
    client = RalendarClient()
    
    try:
        result = client.batch_create_events(user_token, events, trip_slug)
        
        return JsonResponse({
            'success': True,
            'created_count': len(result.get('created', [])),
            'failed_count': len(result.get('failed', [])),
            'details': result
        })
    
    except requests.exceptions.HTTPError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'status_code': e.response.status_code
        }, status=e.response.status_code)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'创建事件失败: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_calendar_events(request, trip_slug):
    """
    获取旅行计划关联的日历事件
    
    前端调用示例:
    GET /api/trips/beijing-trip-2025/calendar-events/
    """
    user_token = str(request.auth)
    client = RalendarClient()
    
    try:
        events = client.get_trip_events(user_token, trip_slug)
        return JsonResponse({'events': events})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

---

## 🎨 前端集成示例

### Vue.js 示例

在旅行详情页添加"添加到日历"按钮：

```vue
<template>
  <div class="trip-detail">
    <!-- 旅行信息 -->
    <div class="trip-info">
      <h1>{{ trip.title }}</h1>
      <p>{{ trip.description }}</p>
    </div>
    
    <!-- 添加到日历按钮 -->
    <el-button 
      type="primary" 
      @click="showAddToCalendarDialog"
      :loading="addingToCalendar"
    >
      <i class="bi bi-calendar-plus"></i>
      添加到日历
    </el-button>
    
    <!-- 事件编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="添加旅行计划到日历"
      width="600px"
    >
      <div v-for="(event, index) in calendarEvents" :key="index" class="event-item">
        <el-form :model="event" label-width="100px">
          <el-form-item label="事件标题">
            <el-input v-model="event.title" />
          </el-form-item>
          
          <el-form-item label="开始时间">
            <el-date-picker 
              v-model="event.start_time" 
              type="datetime"
              format="YYYY-MM-DD HH:mm"
            />
          </el-form-item>
          
          <el-form-item label="结束时间">
            <el-date-picker 
              v-model="event.end_time" 
              type="datetime"
              format="YYYY-MM-DD HH:mm"
            />
          </el-form-item>
          
          <el-form-item label="地点">
            <el-input v-model="event.location" />
          </el-form-item>
          
          <el-form-item label="邮件提醒">
            <el-checkbox v-model="event.email_reminder">
              开始前 15 分钟提醒我
            </el-checkbox>
          </el-form-item>
        </el-form>
        
        <el-button 
          type="danger" 
          size="small" 
          @click="removeEvent(index)"
        >
          删除
        </el-button>
      </div>
      
      <el-button type="success" @click="addNewEvent">
        <i class="bi bi-plus"></i> 添加更多事件
      </el-button>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitToCalendar" :loading="submitting">
          确认添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  trip: Object
})

const dialogVisible = ref(false)
const addingToCalendar = ref(false)
const submitting = ref(false)
const calendarEvents = ref([])

const showAddToCalendarDialog = () => {
  // 根据旅行计划初始化事件
  calendarEvents.value = [
    {
      title: props.trip.title,
      start_time: props.trip.start_date,
      end_time: props.trip.end_date,
      location: props.trip.destination,
      email_reminder: true
    }
  ]
  
  dialogVisible.value = true
}

const addNewEvent = () => {
  calendarEvents.value.push({
    title: '',
    start_time: null,
    end_time: null,
    location: '',
    email_reminder: false
  })
}

const removeEvent = (index) => {
  calendarEvents.value.splice(index, 1)
}

const submitToCalendar = async () => {
  submitting.value = true
  
  try {
    const response = await api.post(
      `/trips/${props.trip.slug}/add-to-calendar/`,
      { events: calendarEvents.value }
    )
    
    ElMessage.success(`成功添加 ${response.created_count} 个事件到日历！`)
    dialogVisible.value = false
    
  } catch (error) {
    ElMessage.error('添加到日历失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.event-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}
</style>
```

---

## 🔑 关键概念

### 1. Token 共享机制

由于两个项目共享 `SECRET_KEY`，JWT Token 可以在两个系统间互通：

```python
# Roamio 生成的 Token 可以直接用于 Ralendar API
# Ralendar 生成的 Token 也可以用于 Roamio API

# 只需确保两边的 SECRET_KEY 完全相同
SECRET_KEY = 'django-insecure-*il-h$$9=73a(2g5g_edot=!#$je=r@ey7(ov0s1uyitc@@o9m'
```

### 2. 用户匹配

通过 QQ UnionID 或共享数据库中的 `User` 表自动匹配用户：

```python
# 用户在 Roamio 登录 → 获取 QQ UnionID
# 用户在 Ralendar 登录 → 使用相同的 QQ UnionID
# → 系统自动识别为同一用户
```

### 3. 数据关联

通过 `source_app` 和 `related_trip_slug` 字段关联数据：

```python
Event.objects.filter(
    source_app='roamio',
    related_trip_slug='beijing-trip-2025'
)
# 返回该旅行计划的所有事件
```

---

## 📡 完整 API 端点列表

### 基础端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/events/` | 创建单个事件 |
| GET | `/api/v1/events/` | 获取用户的所有事件 |
| GET | `/api/v1/events/{id}/` | 获取事件详情 |
| PUT | `/api/v1/events/{id}/` | 更新事件 |
| DELETE | `/api/v1/events/{id}/` | 删除事件 |

### 融合端点（专为 Roamio 设计）

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/fusion/events/batch/` | 批量创建事件 |
| POST | `/api/v1/fusion/events/sync/` | 同步 Roamio 事件 |
| GET | `/api/v1/fusion/events/trip/{slug}/` | 获取旅行计划事件 |
| DELETE | `/api/v1/fusion/events/trip/{slug}/` | 删除旅行计划事件 |
| GET | `/api/v1/fusion/events/with-location/` | 获取有位置的事件 |
| GET | `/api/v1/fusion/events/from-roamio/` | 获取来自 Roamio 的事件 |

---

## 🧪 测试步骤

### 1. 测试 Token 互通

```bash
# 在 Roamio 中获取用户的 access_token
TOKEN="<用户的 JWT Token>"

# 测试调用 Ralendar API
curl -X GET \
  https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer $TOKEN"

# 应该返回用户的事件列表
```

### 2. 测试创建事件

```bash
curl -X POST \
  https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试事件（来自 Roamio）",
    "start_time": "2025-11-20T10:00:00+08:00",
    "end_time": "2025-11-20T12:00:00+08:00",
    "source_app": "roamio",
    "related_trip_slug": "test-trip-123"
  }'
```

### 3. 测试批量创建

```bash
curl -X POST \
  https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/batch/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "title": "事件1",
        "start_time": "2025-11-20T10:00:00+08:00",
        "end_time": "2025-11-20T12:00:00+08:00"
      },
      {
        "title": "事件2",
        "start_time": "2025-11-21T14:00:00+08:00",
        "end_time": "2025-11-21T16:00:00+08:00"
      }
    ],
    "source_app": "roamio",
    "related_trip_slug": "test-trip-123"
  }'
```

---

## ❓ 常见问题

### Q1: Token 验证失败？

**检查**:
1. 两边的 `SECRET_KEY` 是否完全相同
2. Token 是否已过期（默认 24 小时）
3. 请求头格式是否正确: `Authorization: Bearer <token>`

### Q2: 用户匹配失败？

**检查**:
1. 用户是否在两边都登录过 QQ
2. QQ UnionID 是否正确获取
3. 共享数据库连接是否正常

### Q3: 事件创建成功但不显示？

**检查**:
1. `source_app` 字段是否设置为 'roamio'
2. `related_trip_slug` 是否正确
3. 查询时是否过滤了正确的字段

---

## 📞 技术支持

如有问题，请联系 Ralendar 团队：

- **技术文档**: `docs/ROAMIO_INTEGRATION_GUIDE.md` (详细版)
- **API 文档**: `https://app7626.acapp.acwing.com.cn/api/v1/`
- **数据库**: 共享 Aliyun RDS MySQL

---

## ✅ 集成检查清单

完成以下步骤后，集成即可上线：

- [ ] 配置环境变量（`.env` 文件）
- [ ] 安装依赖（`requests`）
- [ ] 创建 `ralendar_client.py`
- [ ] 添加 Django View（`add_trip_to_calendar`）
- [ ] 前端添加"添加到日历"按钮
- [ ] 测试 Token 互通
- [ ] 测试创建事件
- [ ] 测试批量创建
- [ ] 测试事件查询
- [ ] 测试事件删除
- [ ] 生产环境部署

---

🎉 **恭喜！集成完成后，Roamio 的旅行计划将无缝同步到 Ralendar 日历！**

