# 🌏 Ralendar × Roamio 生态融合技术方案

> **项目目标**: 将 Ralendar（日历系统）与 Roamio（旅行平台）深度融合，实现数据互通、功能协同
> 
> **更新日期**: 2025-11-08  
> **版本**: v1.0  
> **优先级**: ⭐⭐⭐⭐⭐

---

## 🎯 一、融合目标

### 核心价值

```
用户在 Roamio 规划旅行 
    ↓
自动生成行程日程
    ↓
同步到 Ralendar 日历
    ↓
智能提醒 + 地图导航
    ↓
无缝的旅行体验
```

### 功能愿景

1. **在 Roamio 旅行详情页添加"创建日程"功能**
   - 用户可以将旅行计划转换为日程事件
   - 自动同步到 Ralendar 日历

2. **地图集成**
   - 选择地点时可在地图上选点
   - 事件详情显示地图位置
   - 一键导航到目的地

3. **智能提醒**
   - 邮件提醒
   - Web 桌面通知
   - 未来支持微信/短信提醒

4. **本地与云端双轨系统**
   - 未登录：本地事项（localStorage）
   - 已登录：云端事项（数据库）
   - 自由互传，用户自主控制

---

## 🗄️ 二、数据库设计

### 2.1 Ralendar Event 模型扩展

```python
# backend/api/models/event.py

class Event(models.Model):
    """日程事件（扩展版）"""
    
    # === 原有字段 ===
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    location = models.CharField(max_length=200, blank=True, verbose_name='地点名称')
    reminder_minutes = models.IntegerField(default=15, verbose_name='提前提醒分钟数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # === 新增字段：来源追踪 ===
    source_app = models.CharField(
        max_length=50, 
        choices=[('ralendar', 'Ralendar'), ('roamio', 'Roamio')],
        default='ralendar',
        verbose_name='来源应用'
    )
    source_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='来源对象ID'
    )
    related_trip_slug = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='关联旅行计划Slug'
    )
    
    # === 新增字段：地图信息 ===
    latitude = models.FloatField(null=True, blank=True, verbose_name='纬度')
    longitude = models.FloatField(null=True, blank=True, verbose_name='经度')
    map_provider = models.CharField(
        max_length=20,
        choices=[('baidu', '百度地图'), ('amap', '高德地图'), ('tencent', '腾讯地图')],
        default='baidu',
        verbose_name='地图服务商'
    )
    
    # === 新增字段：提醒配置 ===
    email_reminder = models.BooleanField(default=False, verbose_name='邮件提醒')
    notification_sent = models.BooleanField(default=False, verbose_name='提醒已发送')
    
    class Meta:
        ordering = ['start_time']
        verbose_name = '日程'
        verbose_name_plural = '日程列表'
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['source_app', 'source_id']),
            models.Index(fields=['related_trip_slug']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def map_url(self):
        """生成地图 URL"""
        if not (self.latitude and self.longitude):
            return None
        
        if self.map_provider == 'baidu':
            return f"https://api.map.baidu.com/marker?location={self.latitude},{self.longitude}&title={self.title}"
        elif self.map_provider == 'amap':
            return f"https://uri.amap.com/marker?position={self.longitude},{self.latitude}&name={self.title}"
        
        return None
```

### 2.2 数据库迁移

```python
# backend/api/migrations/0008_event_add_fusion_fields.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0007_merge_...'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='event',
            name='source_app',
            field=models.CharField(
                max_length=50, 
                choices=[('ralendar', 'Ralendar'), ('roamio', 'Roamio')],
                default='ralendar'
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='source_id',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='related_trip_slug',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='latitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='longitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='map_provider',
            field=models.CharField(max_length=20, default='baidu'),
        ),
        migrations.AddField(
            model_name='event',
            name='email_reminder',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='notification_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['user', 'start_time'], name='api_event_user_start_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['source_app', 'source_id'], name='api_event_source_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['related_trip_slug'], name='api_event_trip_idx'),
        ),
    ]
```

---

## 🔌 三、跨项目 API 设计

### 3.1 API 接口规范

#### 接口 1: 批量创建事件（Roamio → Ralendar）

```python
# backend/api/views/events.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_create_events(request):
    """
    批量创建事件（用于 Roamio 同步）
    
    POST /api/events/batch/
    
    Body:
    {
        "source_app": "roamio",
        "source_id": "trip_123",
        "related_trip_slug": "yunnan-trip-2025",
        "events": [
            {
                "title": "抵达昆明",
                "start_time": "2025-11-15T10:00:00Z",
                "end_time": "2025-11-15T12:00:00Z",
                "location": "昆明长水国际机场",
                "latitude": 25.1019,
                "longitude": 102.9292,
                "description": "飞机 CA1234，提前2小时到达",
                "reminder_minutes": 120,
                "email_reminder": true
            },
            {
                "title": "入住酒店",
                "start_time": "2025-11-15T14:00:00Z",
                "location": "昆明希尔顿酒店",
                "latitude": 25.0406,
                "longitude": 102.7124
            }
        ]
    }
    
    Response:
    {
        "success": true,
        "created_count": 2,
        "events": [
            {
                "id": 123,
                "title": "抵达昆明",
                "start_time": "2025-11-15T10:00:00Z",
                "map_url": "https://api.map.baidu.com/..."
            },
            ...
        ]
    }
    """
    data = request.data
    source_app = data.get('source_app', 'roamio')
    source_id = data.get('source_id', '')
    related_trip_slug = data.get('related_trip_slug', '')
    events_data = data.get('events', [])
    
    if not events_data:
        return Response(
            {'error': '事件列表不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    created_events = []
    
    for event_data in events_data:
        # 合并来源信息
        event_data['user'] = request.user.id
        event_data['source_app'] = source_app
        event_data['source_id'] = source_id
        event_data['related_trip_slug'] = related_trip_slug
        
        # 序列化并保存
        serializer = EventSerializer(data=event_data)
        if serializer.is_valid():
            event = serializer.save()
            created_events.append(event)
            
            # 如果需要邮件提醒，加入任务队列
            if event_data.get('email_reminder'):
                schedule_email_reminder(event)
        else:
            # 记录错误但继续处理其他事件
            print(f"Event creation failed: {serializer.errors}")
    
    # 序列化返回
    result_serializer = EventSerializer(created_events, many=True)
    
    return Response({
        'success': True,
        'created_count': len(created_events),
        'events': result_serializer.data
    }, status=status.HTTP_201_CREATED)
```

#### 接口 2: 查询旅行关联事件

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_events(request, trip_slug):
    """
    获取旅行计划关联的所有事件
    
    GET /api/events/by-trip/{trip_slug}/
    
    Response:
    {
        "trip_slug": "yunnan-trip-2025",
        "events_count": 5,
        "events": [
            {
                "id": 123,
                "title": "抵达昆明",
                "start_time": "2025-11-15T10:00:00Z",
                ...
            }
        ]
    }
    """
    events = Event.objects.filter(
        user=request.user,
        related_trip_slug=trip_slug
    ).order_by('start_time')
    
    serializer = EventSerializer(events, many=True)
    
    return Response({
        'trip_slug': trip_slug,
        'events_count': events.count(),
        'events': serializer.data
    })
```

#### 接口 3: 更新事件状态（已发送提醒）

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_sent(request, event_id):
    """
    标记事件提醒已发送
    
    POST /api/events/{id}/mark-notified/
    """
    try:
        event = Event.objects.get(id=event_id, user=request.user)
        event.notification_sent = True
        event.save()
        
        return Response({'success': True})
    except Event.DoesNotExist:
        return Response(
            {'error': '事件不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
```

### 3.2 API 路由配置

```python
# backend/api/urls.py

urlpatterns = [
    # ... 原有路由 ...
    
    # 融合相关 API
    path('events/batch/', batch_create_events, name='batch_create_events'),
    path('events/by-trip/<slug:trip_slug>/', get_trip_events, name='get_trip_events'),
    path('events/<int:event_id>/mark-notified/', mark_notification_sent, name='mark_notification_sent'),
]
```

---

## 🗺️ 四、地图集成方案

### 4.1 百度地图 API 申请

**步骤**:

1. 访问 [百度地图开放平台](https://lbsyun.baidu.com/)
2. 注册开发者账号
3. 控制台 → 创建应用
   - 应用类型: **浏览器端**
   - 应用名称: Ralendar
   - Referer白名单: `*.acapp.acwing.com.cn`
4. 获取 **AK (Access Key)**

**配置环境变量**:

```bash
# backend/.env

BAIDU_MAP_AK=your_baidu_map_ak_here
```

```python
# backend/calendar_backend/settings.py

BAIDU_MAP_AK = os.environ.get('BAIDU_MAP_AK', '')
```

### 4.2 前端地图选点组件

```vue
<!-- web_frontend/src/components/map/MapPicker.vue -->

<template>
  <div class="map-picker">
    <div class="search-box">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索地点"
        @keyup.enter="searchLocation"
      >
        <template #append>
          <el-button icon="Search" @click="searchLocation">搜索</el-button>
        </template>
      </el-input>
    </div>
    
    <div id="baidu-map" style="width: 100%; height: 400px"></div>
    
    <div v-if="selectedLocation" class="selected-info">
      <p><strong>已选择:</strong> {{ selectedLocation.name }}</p>
      <p><strong>地址:</strong> {{ selectedLocation.address }}</p>
      <p><strong>坐标:</strong> {{ selectedLocation.lat }}, {{ selectedLocation.lng }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  modelValue: Object,  // { lat, lng, name, address }
  center: {
    type: Object,
    default: () => ({ lat: 39.915, lng: 116.404 })  // 默认北京
  }
})

const emit = defineEmits(['update:modelValue'])

const searchKeyword = ref('')
const selectedLocation = ref(props.modelValue || null)
let map = null
let marker = null

onMounted(() => {
  loadBaiduMapScript()
})

function loadBaiduMapScript() {
  if (window.BMapGL) {
    initMap()
    return
  }
  
  const script = document.createElement('script')
  script.src = `https://api.map.baidu.com/api?v=1.0&type=webgl&ak=${import.meta.env.VITE_BAIDU_MAP_AK}`
  script.onload = initMap
  document.head.appendChild(script)
}

function initMap() {
  const BMapGL = window.BMapGL
  
  // 创建地图
  map = new BMapGL.Map('baidu-map')
  const point = new BMapGL.Point(props.center.lng, props.center.lat)
  map.centerAndZoom(point, 15)
  map.enableScrollWheelZoom(true)
  
  // 添加控件
  map.addControl(new BMapGL.NavigationControl())
  map.addControl(new BMapGL.ScaleControl())
  
  // 点击地图选点
  map.addEventListener('click', (e) => {
    const clickPoint = e.latlng
    addMarker(clickPoint)
    getLocationInfo(clickPoint)
  })
  
  // 如果有初始位置，添加标记
  if (selectedLocation.value) {
    const initPoint = new BMapGL.Point(
      selectedLocation.value.lng,
      selectedLocation.value.lat
    )
    addMarker(initPoint)
  }
}

function addMarker(point) {
  const BMapGL = window.BMapGL
  
  // 清除旧标记
  if (marker) {
    map.removeOverlay(marker)
  }
  
  // 添加新标记
  marker = new BMapGL.Marker(point)
  map.addOverlay(marker)
  map.panTo(point)
}

function getLocationInfo(point) {
  const BMapGL = window.BMapGL
  const geocoder = new BMapGL.Geocoder()
  
  geocoder.getLocation(point, (result) => {
    if (result) {
      selectedLocation.value = {
        lat: point.lat,
        lng: point.lng,
        name: result.addressComponents.street || result.addressComponents.district,
        address: result.address
      }
      
      emit('update:modelValue', selectedLocation.value)
    }
  })
}

function searchLocation() {
  if (!searchKeyword.value) return
  
  const BMapGL = window.BMapGL
  const localSearch = new BMapGL.LocalSearch(map, {
    onSearchComplete: (results) => {
      if (localSearch.getStatus() === window.BMAP_STATUS_SUCCESS) {
        const poi = results.getPoi(0)
        const point = poi.point
        
        addMarker(point)
        selectedLocation.value = {
          lat: point.lat,
          lng: point.lng,
          name: poi.title,
          address: poi.address
        }
        
        emit('update:modelValue', selectedLocation.value)
        map.centerAndZoom(point, 16)
      }
    }
  })
  
  localSearch.search(searchKeyword.value)
}
</script>

<style scoped>
.map-picker {
  width: 100%;
}

.search-box {
  margin-bottom: 10px;
}

.selected-info {
  margin-top: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.selected-info p {
  margin: 5px 0;
}
</style>
```

### 4.3 事件表单集成地图

```vue
<!-- web_frontend/src/components/calendar/EventDialog.vue -->

<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑日程' : '新建日程'"
    width="600px"
  >
    <el-form :model="form" label-width="100px">
      <!-- 原有字段 -->
      <el-form-item label="标题">
        <el-input v-model="form.title" />
      </el-form-item>
      
      <el-form-item label="开始时间">
        <el-date-picker
          v-model="form.start_time"
          type="datetime"
          placeholder="选择开始时间"
        />
      </el-form-item>
      
      <!-- 新增：地点选择 -->
      <el-form-item label="地点">
        <el-input v-model="form.location" placeholder="请输入地点或在地图上选择">
          <template #append>
            <el-button @click="showMapPicker = true">
              <i class="el-icon-location"></i> 地图选点
            </el-button>
          </template>
        </el-input>
      </el-form-item>
      
      <!-- 新增：邮件提醒 -->
      <el-form-item label="提醒方式">
        <el-checkbox v-model="form.email_reminder">邮件提醒</el-checkbox>
        <el-checkbox v-model="form.notification_reminder">桌面通知</el-checkbox>
      </el-form-item>
      
      <el-form-item label="提前提醒">
        <el-select v-model="form.reminder_minutes">
          <el-option label="不提醒" :value="0" />
          <el-option label="准时" :value="0" />
          <el-option label="提前5分钟" :value="5" />
          <el-option label="提前15分钟" :value="15" />
          <el-option label="提前30分钟" :value="30" />
          <el-option label="提前1小时" :value="60" />
          <el-option label="提前1天" :value="1440" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
  
  <!-- 地图选点对话框 -->
  <el-dialog
    v-model="showMapPicker"
    title="选择地点"
    width="700px"
  >
    <MapPicker v-model="mapLocation" />
    
    <template #footer>
      <el-button @click="showMapPicker = false">取消</el-button>
      <el-button type="primary" @click="confirmMapLocation">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import MapPicker from '../map/MapPicker.vue'

const visible = ref(false)
const showMapPicker = ref(false)
const mapLocation = ref(null)

const form = ref({
  title: '',
  start_time: null,
  end_time: null,
  location: '',
  latitude: null,
  longitude: null,
  description: '',
  reminder_minutes: 15,
  email_reminder: false,
  notification_reminder: true
})

function confirmMapLocation() {
  if (mapLocation.value) {
    form.value.location = mapLocation.value.name || mapLocation.value.address
    form.value.latitude = mapLocation.value.lat
    form.value.longitude = mapLocation.value.lng
  }
  showMapPicker.value = false
}

async function handleSave() {
  // 保存逻辑...
  const response = await axios.post('/api/events/', form.value)
  visible.value = false
}
</script>
```

### 4.4 地图导航功能

```javascript
// web_frontend/src/utils/mapNavigation.js

/**
 * 跳转到地图 App 进行导航
 */
export function navigateToMap(location) {
  const { latitude, longitude, name } = location
  
  // 检测设备类型
  const isAndroid = /Android/i.test(navigator.userAgent)
  const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent)
  
  if (isAndroid) {
    // Android: 优先尝试百度地图 App
    const baiduUrl = `baidumap://map/direction?destination=name:${encodeURIComponent(name)}&coord_type=gcj02&location=${latitude},${longitude}`
    
    // 尝试打开，失败则跳转网页版
    window.location.href = baiduUrl
    
    setTimeout(() => {
      // 如果没有安装 App，跳转网页版
      window.open(`https://api.map.baidu.com/direction?destination=${latitude},${longitude}&mode=driving&src=Ralendar`)
    }, 1500)
  } else if (isIOS) {
    // iOS: 高德地图
    const amapUrl = `iosamap://path?sourceApplication=Ralendar&dlat=${latitude}&dlon=${longitude}&dname=${encodeURIComponent(name)}&dev=0&t=0`
    
    window.location.href = amapUrl
    
    setTimeout(() => {
      window.open(`https://uri.amap.com/navigation?to=${longitude},${latitude},${encodeURIComponent(name)}&mode=car&src=Ralendar`)
    }, 1500)
  } else {
    // PC 浏览器：直接打开百度地图网页版
    window.open(`https://api.map.baidu.com/direction?destination=${latitude},${longitude}&mode=driving&src=Ralendar`)
  }
}
```

---

## 🔐 五、账号互通方案

### 方案 A: 统一 User ID 映射（推荐）

```python
# backend/api/models/user.py

class UserMapping(models.Model):
    """
    用户账号映射表
    实现 Roamio 和 Ralendar 用户的关联
    """
    ralendar_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_mapping',
        verbose_name='Ralendar 用户'
    )
    roamio_user_id = models.IntegerField(
        unique=True,
        verbose_name='Roamio 用户ID'
    )
    roamio_username = models.CharField(
        max_length=150,
        verbose_name='Roamio 用户名'
    )
    
    # QQ OpenID（作为统一标识）
    qq_unionid = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='QQ UnionID'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '用户映射'
        verbose_name_plural = '用户映射表'
    
    def __str__(self):
        return f"Ralendar({self.ralendar_user.id}) <-> Roamio({self.roamio_user_id})"
```

### 方案 B: JWT Token 共享

```python
# 两个项目使用相同的 SECRET_KEY

# Roamio settings.py
SECRET_KEY = 'roamio-ralendar-shared-secret-key-2025'

# Ralendar settings.py
SECRET_KEY = 'roamio-ralendar-shared-secret-key-2025'  # 相同！

# 这样 Roamio 生成的 JWT Token 可以在 Ralendar 中验证
```

### 跨项目 Token 验证中间件

```python
# backend/api/middleware/roamio_auth.py

import requests
from django.contrib.auth.models import User
from api.models import UserMapping

class RoamioAuthMiddleware:
    """
    验证来自 Roamio 的请求
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查是否来自 Roamio
        if request.META.get('HTTP_X_SOURCE_APP') == 'roamio':
            roamio_token = request.META.get('HTTP_X_ROAMIO_TOKEN')
            roamio_user_id = request.META.get('HTTP_X_ROAMIO_USER_ID')
            
            if roamio_token and roamio_user_id:
                # 验证 Token（可以调用 Roamio API 或使用共享 SECRET_KEY）
                user = self.get_or_create_mapped_user(roamio_user_id)
                if user:
                    request.user = user
        
        return self.get_response(request)
    
    def get_or_create_mapped_user(self, roamio_user_id):
        """
        获取或创建映射用户
        """
        try:
            mapping = UserMapping.objects.get(roamio_user_id=roamio_user_id)
            return mapping.ralendar_user
        except UserMapping.DoesNotExist:
            # 如果不存在，可以调用 Roamio API 获取用户信息并创建
            return None
```

---

## 📦 六、本地与云端双轨系统

### 6.1 本地事项存储

```javascript
// web_frontend/src/stores/localEvents.js

import { defineStore } from 'pinia'

export const useLocalEventsStore = defineStore('localEvents', {
  state: () => ({
    events: []
  }),
  
  getters: {
    sortedEvents: (state) => {
      return [...state.events].sort((a, b) => 
        new Date(a.start_time) - new Date(b.start_time)
      )
    }
  },
  
  actions: {
    loadFromLocalStorage() {
      const stored = localStorage.getItem('ralendar_local_events')
      if (stored) {
        this.events = JSON.parse(stored)
      }
    },
    
    saveToLocalStorage() {
      localStorage.setItem('ralendar_local_events', JSON.stringify(this.events))
    },
    
    addEvent(event) {
      event.id = `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      event.is_local = true
      this.events.push(event)
      this.saveToLocalStorage()
    },
    
    updateEvent(id, updates) {
      const index = this.events.findIndex(e => e.id === id)
      if (index !== -1) {
        this.events[index] = { ...this.events[index], ...updates }
        this.saveToLocalStorage()
      }
    },
    
    deleteEvent(id) {
      this.events = this.events.filter(e => e.id !== id)
      this.saveToLocalStorage()
    },
    
    clearAll() {
      this.events = []
      localStorage.removeItem('ralendar_local_events')
    }
  }
})
```

### 6.2 本地与云端列表组件

```vue
<!-- web_frontend/src/components/calendar/EventListPanel.vue -->

<template>
  <div class="event-list-panel">
    <el-tabs v-model="activeTab">
      <!-- 本地事项 -->
      <el-tab-pane label="本地事项" name="local">
        <div class="event-section">
          <div class="section-header">
            <span>📱 本地存储（{{ localEvents.length }}）</span>
            <el-button size="small" @click="addLocalEvent">+ 新建</el-button>
          </div>
          
          <el-empty v-if="localEvents.length === 0" description="暂无本地事项" />
          
          <div v-else class="event-list">
            <div
              v-for="event in localEvents"
              :key="event.id"
              class="event-item local"
              @click="viewEventDetail(event)"
            >
              <div class="event-time">
                {{ formatTime(event.start_time) }}
              </div>
              <div class="event-title">{{ event.title }}</div>
              <div class="event-actions">
                <el-button
                  v-if="isLoggedIn"
                  size="small"
                  type="primary"
                  link
                  @click.stop="pushToCloud(event)"
                >
                  ☁️ 推送到云端
                </el-button>
                <el-button
                  size="small"
                  type="default"
                  link
                  @click.stop="editEvent(event)"
                >
                  编辑
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 云端事项 -->
      <el-tab-pane label="云端事项" name="cloud" :disabled="!isLoggedIn">
        <div class="event-section">
          <div class="section-header">
            <span>☁️ 云端同步（{{ cloudEvents.length }}）</span>
            <el-button size="small" type="primary" @click="addCloudEvent">+ 新建</el-button>
          </div>
          
          <el-alert
            v-if="!isLoggedIn"
            title="请先登录以使用云端功能"
            type="info"
            :closable="false"
          />
          
          <el-empty v-else-if="cloudEvents.length === 0" description="暂无云端事项" />
          
          <div v-else class="event-list">
            <div
              v-for="event in cloudEvents"
              :key="event.id"
              class="event-item cloud"
              @click="viewEventDetail(event)"
            >
              <div class="event-time">
                {{ formatTime(event.start_time) }}
              </div>
              <div class="event-title">
                {{ event.title }}
                <el-tag v-if="event.source_app === 'roamio'" size="small">来自旅行</el-tag>
              </div>
              <div v-if="event.location" class="event-location">
                📍 {{ event.location }}
              </div>
              <div class="event-actions">
                <el-button
                  size="small"
                  type="default"
                  link
                  @click.stop="pullToLocal(event)"
                >
                  📱 拉到本地
                </el-button>
                <el-button
                  size="small"
                  type="default"
                  link
                  @click.stop="editEvent(event)"
                >
                  编辑
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useLocalEventsStore } from '@/stores/localEvents'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const localEventsStore = useLocalEventsStore()
const userStore = useUserStore()

const activeTab = ref('local')
const cloudEvents = ref([])

const isLoggedIn = computed(() => userStore.isLoggedIn)
const localEvents = computed(() => localEventsStore.sortedEvents)

// 推送到云端
async function pushToCloud(localEvent) {
  try {
    await ElMessageBox.confirm(
      '确定要将此事项推送到云端吗？推送后本地副本将被删除。',
      '推送确认',
      { type: 'info' }
    )
    
    // 创建云端事项
    const response = await axios.post('/api/events/', {
      title: localEvent.title,
      start_time: localEvent.start_time,
      end_time: localEvent.end_time,
      location: localEvent.location,
      description: localEvent.description,
      reminder_minutes: localEvent.reminder_minutes
    })
    
    // 删除本地事项
    localEventsStore.deleteEvent(localEvent.id)
    
    // 刷新云端列表
    await fetchCloudEvents()
    
    ElMessage.success('已推送到云端')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('推送失败')
    }
  }
}

// 拉到本地
async function pullToLocal(cloudEvent) {
  try {
    await ElMessageBox.confirm(
      '确定要将此事项拉到本地吗？将创建一个本地副本。',
      '拉取确认',
      { type: 'info' }
    )
    
    // 创建本地副本
    localEventsStore.addEvent({
      title: cloudEvent.title,
      start_time: cloudEvent.start_time,
      end_time: cloudEvent.end_time,
      location: cloudEvent.location,
      description: cloudEvent.description,
      reminder_minutes: cloudEvent.reminder_minutes
    })
    
    ElMessage.success('已拉到本地')
    activeTab.value = 'local'
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('拉取失败')
    }
  }
}

// 获取云端事项
async function fetchCloudEvents() {
  if (!isLoggedIn.value) return
  
  try {
    const response = await axios.get('/api/events/')
    cloudEvents.value = response.data
  } catch (error) {
    ElMessage.error('获取云端事项失败')
  }
}
</script>

<style scoped>
.event-list-panel {
  height: 100%;
}

.event-section {
  padding: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.event-list {
  max-height: 500px;
  overflow-y: auto;
}

.event-item {
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.event-item.local {
  background: #f0f9ff;
  border-left: 4px solid #3b82f6;
}

.event-item.cloud {
  background: #f0fdf4;
  border-left: 4px solid #22c55e;
}

.event-item:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.event-time {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.event-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.event-location {
  font-size: 12px;
  color: #888;
  margin-bottom: 8px;
}

.event-actions {
  display: flex;
  gap: 8px;
}
</style>
```

---

## 📧 七、提醒机制

### 7.1 邮件提醒

```python
# backend/api/tasks/email_reminder.py

from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta

def schedule_email_reminder(event):
    """
    安排邮件提醒任务
    """
    if not event.email_reminder:
        return
    
    # 计算提醒时间
    reminder_time = event.start_time - timedelta(minutes=event.reminder_minutes)
    
    # 如果提醒时间已过，不发送
    if reminder_time < datetime.now():
        return
    
    # 这里应该使用 Celery 等任务队列
    # 暂时简化为立即检查
    send_event_reminder_email(event)

def send_event_reminder_email(event):
    """
    发送事件提醒邮件
    """
    subject = f'📅 日程提醒：{event.title}'
    
    message = f"""
    您好！
    
    您有一个即将到来的日程：
    
    📌 事件：{event.title}
    ⏰ 时间：{event.start_time.strftime('%Y年%m月%d日 %H:%M')}
    📍 地点：{event.location or '无'}
    
    {event.description if event.description else ''}
    
    ---
    来自 Ralendar 智能日历
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [event.user.email],
            fail_silently=False,
        )
        
        # 标记已发送
        event.notification_sent = True
        event.save()
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
```

### 7.2 Django 邮件配置

```python
# backend/calendar_backend/settings.py

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 或其他 SMTP 服务器
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', 'your-email@qq.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your-smtp-password')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### 7.3 Web 桌面通知

```javascript
// web_frontend/src/utils/notifications.js

/**
 * 请求通知权限
 */
export async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.warn('浏览器不支持通知')
    return false
  }
  
  if (Notification.permission === 'granted') {
    return true
  }
  
  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission()
    return permission === 'granted'
  }
  
  return false
}

/**
 * 发送桌面通知
 */
export function sendNotification(event) {
  if (Notification.permission !== 'granted') {
    return
  }
  
  const notification = new Notification('📅 日程提醒', {
    body: `${event.title}\n⏰ ${formatTime(event.start_time)}\n📍 ${event.location || '无地点'}`,
    icon: '/logo.png',
    tag: `event-${event.id}`,
    requireInteraction: true,
    vibrate: [200, 100, 200]
  })
  
  notification.onclick = () => {
    window.focus()
    // 跳转到事件详情
    notification.close()
  }
}

/**
 * 定时检查即将到来的事件
 */
export function startReminderCheck(events) {
  setInterval(() => {
    const now = new Date()
    
    events.forEach(event => {
      if (event.notification_sent) return
      
      const eventTime = new Date(event.start_time)
      const reminderTime = new Date(eventTime - event.reminder_minutes * 60 * 1000)
      
      // 如果到了提醒时间
      if (now >= reminderTime && now < eventTime) {
        sendNotification(event)
        // 标记已提醒
        event.notification_sent = true
      }
    })
  }, 60000) // 每分钟检查一次
}
```

---

## 🎯 八、开发优先级与时间规划

### Phase 1: 基础准备（1-2天）✅ 高优先级

- [x] 数据库模型扩展
- [x] 数据库迁移
- [x] API 接口设计

### Phase 2: 地图集成（2-3天）⭐⭐⭐⭐⭐

- [ ] 申请百度地图 API Key
- [ ] 创建地图选点组件
- [ ] 事件表单集成地图
- [ ] 实现地图导航功能

### Phase 3: 本地与云端双轨（2-3天）⭐⭐⭐⭐

- [ ] 实现本地事项存储
- [ ] 实现云端事项展示
- [ ] 实现互传功能

### Phase 4: 提醒机制（1-2天）⭐⭐⭐

- [ ] 配置邮件服务
- [ ] 实现邮件提醒
- [ ] 实现桌面通知

### Phase 5: 账号互通（2-3天）⭐⭐⭐⭐

- [ ] 设计用户映射表
- [ ] 实现 Token 共享
- [ ] 跨项目认证

### Phase 6: Roamio 集成（1-2天）⭐⭐⭐⭐⭐

- [ ] 创建事件表单组件
- [ ] 调用 Ralendar API
- [ ] 端到端测试

---

## 📋 完整任务清单 Checklist

### 数据库相关

- [ ] Event 模型添加 `source_app`, `source_id`, `related_trip_slug` 字段
- [ ] Event 模型添加 `latitude`, `longitude`, `map_provider` 字段
- [ ] Event 模型添加 `email_reminder`, `notification_sent` 字段
- [ ] 创建 UserMapping 模型
- [ ] 执行数据库迁移

### API 相关

- [ ] 实现 `POST /api/events/batch/` 批量创建事件
- [ ] 实现 `GET /api/events/by-trip/{slug}/` 查询旅行关联事件
- [ ] 实现 `POST /api/events/{id}/mark-notified/` 标记提醒已发送
- [ ] 配置 API 路由

### 地图相关

- [ ] 申请百度地图 API Key
- [ ] 创建 MapPicker.vue 组件
- [ ] EventDialog.vue 集成地图选择
- [ ] 实现地图导航功能
- [ ] 创建 MapView.vue 地图视图页面

### 本地与云端

- [ ] 创建 localEvents store
- [ ] 实现本地事项 CRUD
- [ ] 创建 EventListPanel.vue 双列表组件
- [ ] 实现推送到云端功能
- [ ] 实现拉到本地功能

### 提醒机制

- [ ] 配置 Django 邮件服务
- [ ] 实现邮件提醒任务
- [ ] 实现 Web Notifications API
- [ ] 实现定时检查功能

### 账号互通

- [ ] 设计账号映射方案
- [ ] 创建 UserMapping 模型
- [ ] 实现跨项目 Token 验证
- [ ] 测试账号互通

### 文档

- [ ] 编写 API 对接文档
- [ ] 编写部署指南
- [ ] 更新用户手册

---

## 🎉 预期效果

实现完成后，用户体验：

1. **在 Roamio 规划旅行**：
   - 创建"云南6日游"旅行计划
   - 添加每日行程（抵达、游览、住宿等）

2. **一键同步到 Ralendar**：
   - 点击"同步到日历"按钮
   - 所有行程自动创建为日程事件
   - 带有地图坐标和提醒

3. **智能提醒**：
   - 提前1小时收到邮件提醒
   - 桌面弹窗通知
   - 点击可查看地图导航

4. **无缝体验**：
   - 未登录也能用本地事项
   - 登录后自动同步云端
   - 自由选择本地或云端存储

---

## 🚀 下一步行动

**建议从以下任务开始**：

1. ✅ **数据库模型扩展** (30分钟) - 最基础
2. ✅ **申请百度地图 API Key** (10分钟) - 需要审核时间
3. 🚀 **创建地图选点组件** (2-3小时) - 核心功能
4. 🚀 **实现批量创建事件 API** (1小时) - 后端支持

---

**准备好开始了吗？我们从哪个任务开始？** 🎯

