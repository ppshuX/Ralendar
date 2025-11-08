# 地图功能集成规划

**创建日期**: 2025-11-06  
**核心理念**: 让日历不仅告诉你"什么时候"，还告诉你"在哪里"和"怎么去"

---

## 🌟 产品愿景

**"永远不迟到的日历"**

- 📍 知道在哪 - 地图显示地点
- 🚗 知道怎么去 - 一键导航
- ⏰ 知道何时走 - 智能出发提醒
- 🗺️ 看到全局 - 地图视图查看所有日程

---

## 🎯 核心功能设计

### 功能1: 地点搜索与选择 📍

#### 用户体验
```
创建事件 → 点击"地点"
    ↓
输入"南昌大学"
    ↓
下拉显示：
  - 南昌大学（前湖校区）📏 5km
  - 南昌大学（青山湖校区）📏 12km
  - 南昌大学科学技术学院 📏 20km
    ↓
点击"前湖校区"
    ↓
自动保存：
  - 地点名称: "南昌大学（前湖校区）"
  - 详细地址: "江西省南昌市红谷滩区学府大道999号"
  - 经纬度: (28.6891, 115.8289)
    ↓
事件详情中显示小地图 ✅
```

#### 技术实现
```vue
<el-form-item label="地点">
  <el-autocomplete
    v-model="formData.location"
    :fetch-suggestions="searchLocation"
    placeholder="搜索地点..."
    :trigger-on-focus="false"
    @select="handleSelectLocation"
  >
    <template #default="{ item }">
      <div class="location-suggestion">
        <div class="loc-name">📍 {{ item.name }}</div>
        <div class="loc-address">{{ item.address }}</div>
        <div class="loc-distance">📏 {{ item.distance }}</div>
      </div>
    </template>
  </el-autocomplete>
  
  <el-button @click="showMapPicker = true" size="small" style="margin-top: 8px">
    🗺️ 地图选点
  </el-button>
</el-form-item>

<script setup>
import axios from 'axios'

// 搜索地点（调用后端API，后端调用高德）
const searchLocation = async (queryString, callback) => {
  if (!queryString) {
    callback([])
    return
  }
  
  try {
    const { data } = await axios.get('/api/map/search/', {
      params: { 
        keyword: queryString,
        city: '南昌'  // 可从用户位置获取
      }
    })
    
    callback(data)
  } catch (error) {
    console.error('搜索地点失败:', error)
    callback([])
  }
}

// 选择地点
const handleSelectLocation = (item) => {
  formData.value.location = item.name
  formData.value.location_name = item.name
  formData.value.location_address = item.address
  formData.value.location_lat = item.lat
  formData.value.location_lng = item.lng
}
</script>
```

---

### 功能2: 事件详情地图显示 🗺️

#### 用户体验
```
点击事件"团队会议"
    ↓
详情对话框显示：
  📝 标题: 团队会议
  🕒 时间: 2025-11-07 14:00
  📍 地点: XX科技园A座
  🗺️ [地图显示]
  
  [🧭 打开导航] [🚗 查看路线] [📤 分享位置]
    ↓
点击"查看路线"
    ↓
显示：
  📏 距离: 15.2公里
  ⏱️ 驾车时间: 32分钟
  🚦 红绿灯: 8个
  💡 建议13:20出发
  
  [📱 发送出发提醒]
```

#### 技术实现
```vue
<template>
  <el-dialog title="📋 日程详情">
    <div class="event-detail">
      <p><strong>📝 标题：</strong>{{ event.title }}</p>
      <p><strong>🕒 时间：</strong>{{ formatDateTime(event.start_time) }}</p>
      
      <!-- 地点信息 -->
      <div v-if="event.location" class="location-section">
        <p><strong>📍 地点：</strong>{{ event.location }}</p>
        
        <!-- 小地图预览 -->
        <div id="event-map" class="map-preview"></div>
        
        <!-- 操作按钮 -->
        <div class="map-actions">
          <el-button 
            @click="openNavigation" 
            type="primary" 
            size="small"
            :icon="Position"
          >
            打开导航
          </el-button>
          
          <el-button 
            @click="calculateRoute" 
            size="small"
            :loading="calculating"
          >
            查看路线
          </el-button>
          
          <el-button 
            @click="shareLocation" 
            size="small"
          >
            分享位置
          </el-button>
        </div>
        
        <!-- 路线信息 -->
        <div v-if="routeInfo" class="route-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="📏 距离">
              {{ routeInfo.distance }}
            </el-descriptions-item>
            <el-descriptions-item label="⏱️ 时间">
              {{ routeInfo.duration }}分钟
            </el-descriptions-item>
            <el-descriptions-item label="🚦 红绿灯">
              {{ routeInfo.traffic }}个
            </el-descriptions-item>
            <el-descriptions-item label="🚗 建议出发">
              {{ routeInfo.departureTime }}
            </el-descriptions-item>
          </el-descriptions>
          
          <el-alert 
            type="info" 
            :closable="false"
            style="margin-top: 10px"
          >
            💡 建议提前{{ Math.ceil(routeInfo.duration + 10) }}分钟出发，留出缓冲时间
          </el-alert>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import axios from 'axios'

const routeInfo = ref(null)
const calculating = ref(false)

// 初始化地图
const initMap = async () => {
  if (!props.event?.location_lat || !props.event?.location_lng) return
  
  const AMap = await AMapLoader.load({
    key: 'YOUR_AMAP_KEY',
    version: '2.0'
  })
  
  const map = new AMap.Map('event-map', {
    zoom: 15,
    center: [props.event.location_lng, props.event.location_lat]
  })
  
  new AMap.Marker({
    position: [props.event.location_lng, props.event.location_lat],
    title: props.event.location
  }).setMap(map)
}

// 打开导航
const openNavigation = () => {
  const url = `https://uri.amap.com/navigation?to=${props.event.location_lng},${props.event.location_lat},${props.event.location}`
  window.open(url, '_blank')
}

// 计算路线
const calculateRoute = async () => {
  calculating.value = true
  
  try {
    // 获取用户当前位置
    const userLocation = await getCurrentLocation()
    
    // 调用后端API计算路线
    const { data } = await axios.post('/api/map/route/', {
      origin_lat: userLocation.lat,
      origin_lng: userLocation.lng,
      dest_lat: props.event.location_lat,
      dest_lng: props.event.location_lng
    })
    
    // 计算建议出发时间
    const arrivalTime = new Date(props.event.start_time)
    const travelMinutes = data.duration
    const bufferMinutes = 10
    const departureTime = new Date(arrivalTime - (travelMinutes + bufferMinutes) * 60000)
    
    routeInfo.value = {
      distance: (data.distance / 1000).toFixed(1) + 'km',
      duration: data.duration,
      traffic: data.traffic || 0,
      departureTime: formatTime(departureTime)
    }
  } catch (error) {
    console.error('计算路线失败:', error)
    ElMessage.error('无法计算路线，请检查网络')
  } finally {
    calculating.value = false
  }
}

// 获取当前位置
const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        position => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          })
        },
        error => reject(error)
      )
    } else {
      reject(new Error('浏览器不支持定位'))
    }
  })
}
</script>

<style scoped>
.map-preview {
  width: 100%;
  height: 250px;
  margin: 15px 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
}

.map-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.route-info {
  margin-top: 15px;
}
</style>
```

---

### 功能3: 地图视图 🗺️

#### 用户体验
```
日历页面 → 切换"地图视图"
    ↓
地图显示所有有地点的事件
  - 🔴 红色标记: 今天的事件
  - 🔵 蓝色标记: 本周的事件
  - ⚪ 灰色标记: 过去的事件
    ↓
点击标记 → 显示事件详情
    ↓
点击"导航" → 打开高德地图App
```

#### 技术实现
```vue
<template>
  <div class="calendar-with-map">
    <!-- 视图切换 -->
    <el-radio-group v-model="viewMode" class="view-switcher">
      <el-radio-button label="calendar">
        <i class="bi bi-calendar3"></i> 日历
      </el-radio-button>
      <el-radio-button label="map">
        <i class="bi bi-map"></i> 地图
      </el-radio-button>
      <el-radio-button label="split">
        <i class="bi bi-layout-split"></i> 分屏
      </el-radio-button>
    </el-radio-group>
    
    <!-- 日历视图 -->
    <div v-show="viewMode === 'calendar'" class="calendar-view">
      <FullCalendar :options="calendarOptions" />
    </div>
    
    <!-- 地图视图 -->
    <div v-show="viewMode === 'map'" class="map-view">
      <div id="events-map" class="full-map"></div>
      
      <!-- 侧边栏：事件列表 -->
      <div class="map-sidebar">
        <h4>📍 本月有地点的事件 ({{ eventsWithLocation.length }})</h4>
        
        <el-scrollbar height="calc(100vh - 200px)">
          <div 
            v-for="event in eventsWithLocation" 
            :key="event.id"
            @click="focusOnEvent(event)"
            :class="['event-marker-item', { active: selectedEventId === event.id }]"
          >
            <div class="marker-color" :style="{ background: getEventColor(event) }"></div>
            <div class="event-info">
              <h5>{{ event.title }}</h5>
              <p class="time">🕒 {{ formatTime(event.start_time) }}</p>
              <p class="location">📍 {{ event.location }}</p>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </div>
    
    <!-- 分屏视图 -->
    <div v-show="viewMode === 'split'" class="split-view">
      <div class="split-calendar">
        <FullCalendar :options="calendarOptions" />
      </div>
      <div class="split-map">
        <div id="events-map-split"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AMapLoader from '@amap/amap-jsapi-loader'

const viewMode = ref('calendar')
const selectedEventId = ref(null)
let map = null
let markers = []

// 有地点的事件
const eventsWithLocation = computed(() => {
  return eventsList.value.filter(e => e.location_lat && e.location_lng)
})

// 初始化地图
const initEventsMap = async () => {
  const AMap = await AMapLoader.load({
    key: 'YOUR_AMAP_KEY',
    version: '2.0',
    plugins: ['AMap.Marker', 'AMap.InfoWindow']
  })
  
  map = new AMap.Map('events-map', {
    zoom: 12,
    center: [115.8289, 28.6891]  // 默认中心（可改为用户位置）
  })
  
  // 添加标记
  eventsWithLocation.value.forEach(event => {
    const marker = new AMap.Marker({
      position: [event.location_lng, event.location_lat],
      title: event.title,
      icon: getMarkerIcon(event),
      extData: { eventId: event.id }
    })
    
    // 点击标记显示信息窗口
    marker.on('click', () => {
      const infoWindow = new AMap.InfoWindow({
        content: `
          <div style="padding: 10px">
            <h4>${event.title}</h4>
            <p>🕒 ${formatTime(event.start_time)}</p>
            <p>📍 ${event.location}</p>
            <button onclick="openEventDetail(${event.id})">查看详情</button>
          </div>
        `
      })
      infoWindow.open(map, marker.getPosition())
      selectedEventId.value = event.id
    })
    
    marker.setMap(map)
    markers.push(marker)
  })
}

// 获取标记图标（根据时间不同颜色）
const getMarkerIcon = (event) => {
  const now = new Date()
  const eventTime = new Date(event.start_time)
  
  let color
  if (eventTime < now) {
    color = 'gray'  // 过去
  } else if (eventTime.toDateString() === now.toDateString()) {
    color = 'red'   // 今天
  } else {
    color = 'blue'  // 未来
  }
  
  return new AMap.Icon({
    size: new AMap.Size(25, 34),
    image: `//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-${color}.png`
  })
}

// 聚焦到事件
const focusOnEvent = (event) => {
  selectedEventId.value = event.id
  map.setZoomAndCenter(16, [event.location_lng, event.location_lat])
}
</script>

<style scoped>
.view-switcher {
  margin-bottom: 20px;
  text-align: center;
}

.map-view {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.full-map {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
}

.map-sidebar {
  width: 300px;
  background: white;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.event-marker-item {
  display: flex;
  gap: 10px;
  padding: 12px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.event-marker-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.event-marker-item.active {
  background: #ecf5ff;
  border: 2px solid #409eff;
}

.marker-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

.split-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  height: calc(100vh - 200px);
}

.split-calendar,
.split-map > div {
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
}
</style>
```

---

### 功能4: 智能出发提醒 🚗⏰

#### 概念
根据实时路况自动计算出发时间，提前提醒用户。

#### 用户体验
```
事件: 14:00 在XX科技园开会
用户位置: 家里（15km外）
    ↓
系统自动监控：
  - 12:00 检查路况 → 预计30分钟 → 无需提醒
  - 13:00 检查路况 → 预计35分钟（堵车）→ 无需提醒
  - 13:20 检查路况 → 预计40分钟（严重堵车）
    ↓
立即推送：
  "🚨 路况拥堵！
   去'XX科技园'现在需要40分钟
   建议立即出发，否则可能迟到
   [打开导航] [推迟会议]"
```

#### 技术实现
```python
# 后端 Celery任务

@celery.task
def smart_departure_reminder():
    """智能出发提醒（每10分钟执行一次）"""
    now = datetime.now()
    
    # 找到2小时内开始的事件
    upcoming_events = Event.objects.filter(
        start_time__gte=now,
        start_time__lte=now + timedelta(hours=2),
        location_lat__isnull=False,
        auto_departure_remind=True,
        departure_reminded=False
    )
    
    for event in upcoming_events:
        # 获取用户最后已知位置
        user_location = get_user_last_location(event.user)
        
        if not user_location:
            continue
        
        # 调用高德API计算实时路况
        route = calculate_route_realtime(
            origin=(user_location['lng'], user_location['lat']),
            destination=(event.location_lng, event.location_lat),
            strategy='fastest'  # 最快路线
        )
        
        # 计算应该出发的时间
        travel_minutes = route['duration'] / 60
        buffer_minutes = 10
        ideal_departure = event.start_time - timedelta(minutes=travel_minutes + buffer_minutes)
        
        # 如果当前时间已经晚于或接近理想出发时间（±5分钟）
        time_diff = (ideal_departure - now).total_seconds() / 60
        
        if -5 <= time_diff <= 5:
            # 发送出发提醒
            send_push_notification(
                user=event.user,
                title=f"🚗 该出发了！",
                body=f"去'{event.location}'需要{int(travel_minutes)}分钟，现在出发可准时到达",
                data={
                    'event_id': event.id,
                    'action': 'navigate',
                    'destination': f"{event.location_lng},{event.location_lat}"
                }
            )
            
            event.departure_reminded = True
            event.save()
        
        # 如果路况严重拥堵，提前预警
        if route['traffic_status'] == 'heavy' and time_diff > 10:
            send_push_notification(
                user=event.user,
                title=f"🚨 路况拥堵提醒",
                body=f"去'{event.location}'的路上严重拥堵，建议提前出发",
                type='warning'
            )


def calculate_route_realtime(origin, destination, strategy='fastest'):
    """调用高德路线规划API（实时路况）"""
    response = requests.get(
        'https://restapi.amap.com/v3/direction/driving',
        params={
            'key': settings.AMAP_KEY,
            'origin': f'{origin[0]},{origin[1]}',
            'destination': f'{destination[0]},{destination[1]}',
            'strategy': {
                'fastest': 0,      # 速度最快
                'shortest': 1,     # 距离最短
                'avoid_jam': 4,    # 躲避拥堵
            }.get(strategy, 0),
            'extensions': 'all'    # 返回详细信息
        }
    )
    
    data = response.json()
    route = data['route']['paths'][0]
    
    return {
        'distance': int(route['distance']),       # 米
        'duration': int(route['duration']) // 60, # 分钟
        'traffic': int(route.get('traffic_lights', 0)),
        'traffic_status': route.get('traffic_status', 'normal'),  # 路况
        'tolls': int(route.get('tolls', 0)),      # 过路费（元）
    }
```

---

### 功能5: 附近事件 📍

#### 用户体验
```
打开App → 切换到"附近"标签
    ↓
显示当前位置500米内的事件：
  📍 咖啡厅约会（距离你200米）
     步行约3分钟
     [🚶 步行导航]
  
  📍 健身房（距离你450米）
     步行约6分钟
     [🚶 步行导航]
```

---

## 💾 数据库设计

### 扩展Event模型
```python
class Event(models.Model):
    # 现有字段
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    reminder_minutes = models.IntegerField(default=15)
    
    # 新增：地图相关字段
    location_name = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='地点名称'
    )
    location_address = models.CharField(
        max_length=500, 
        blank=True, 
        verbose_name='详细地址'
    )
    location_lat = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name='纬度'
    )
    location_lng = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name='经度'
    )
    
    # 新增：智能提醒字段
    auto_departure_remind = models.BooleanField(
        default=False, 
        verbose_name='自动出发提醒'
    )
    departure_reminded = models.BooleanField(
        default=False, 
        verbose_name='已提醒出发'
    )
    
    # 新增：统计字段
    navigation_count = models.IntegerField(
        default=0, 
        verbose_name='导航次数'
    )
```

### 用户位置记录
```python
class UserLocation(models.Model):
    """用户位置记录（用于智能出发提醒）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=500, blank=True)
    location_type = models.CharField(
        max_length=20,
        choices=[
            ('home', '家'),
            ('work', '公司'),
            ('current', '当前位置')
        ]
    )
    updated_at = models.DateTimeField(auto_now=True)
```

---

## 🔧 后端API设计

### 1. 地点搜索
```python
GET /api/map/search/
Query Params:
  - keyword: 搜索关键词
  - city: 城市名称
  - location: 当前位置（lat,lng）用于排序

Response:
{
  "results": [
    {
      "id": "B000A83M56",
      "name": "南昌大学（前湖校区）",
      "address": "江西省南昌市红谷滩区学府大道999号",
      "lat": 28.6891,
      "lng": 115.8289,
      "distance": 5200,  # 距离当前位置（米）
      "category": "教育培训;高等院校;高等院校"
    }
  ]
}
```

### 2. 路线规划
```python
POST /api/map/route/
Request:
{
  "origin_lat": 28.6800,
  "origin_lng": 115.8200,
  "dest_lat": 28.6891,
  "dest_lng": 115.8289,
  "strategy": "fastest"  # fastest/shortest/avoid_jam
}

Response:
{
  "distance": 5200,        # 米
  "duration": 18,          # 分钟
  "traffic_lights": 3,     # 红绿灯数量
  "traffic_status": "smooth",  # smooth/slow/heavy
  "tolls": 0,              # 过路费（元）
  "polyline": [...],       # 路线坐标点
  "steps": [               # 导航步骤
    {
      "instruction": "向东行驶500米",
      "road": "学府大道",
      "distance": 500
    }
  ]
}
```

### 3. 保存用户位置
```python
POST /api/map/save-location/
Request:
{
  "lat": 28.6800,
  "lng": 115.8200,
  "type": "home",  # home/work/current
  "address": "江西省南昌市..."
}
```

### 4. 批量地理编码（补全旧数据）
```python
POST /api/map/geocode-batch/
Request:
{
  "addresses": [
    "南昌大学",
    "江西师范大学",
    "南昌市人民政府"
  ]
}

Response:
{
  "results": [
    {
      "address": "南昌大学",
      "lat": 28.6891,
      "lng": 115.8289,
      "formatted_address": "江西省南昌市红谷滩区学府大道999号"
    }
  ]
}
```

---

## 💰 成本分析

### 高德地图API费用

| 服务 | 免费额度 | 超出后价格 | 预估使用 |
|------|---------|-----------|---------|
| 地点搜索 | 30万次/天 | ¥0.001/次 | 1000次/天 ✅ |
| 路线规划 | 30万次/天 | ¥0.01/次 | 500次/天 ✅ |
| 地理编码 | 30万次/天 | ¥0.001/次 | 2000次/天 ✅ |

**100个活跃用户/天**：
- 搜索：100人 × 10次 = 1000次 ✅ 免费
- 路线：100人 × 5次 = 500次 ✅ 免费
- **月成本**: ¥0（完全在免费额度内）

**1000个活跃用户/天**：
- 搜索：1万次 ✅ 免费
- 路线：5千次 ✅ 免费
- **月成本**: ¥0

**免费额度非常充足！** 🎉

---

## 🎯 开发路线图

### Phase 1: 基础地图（1周）
**Day 1-2: 后端API**
- [ ] 高德API密钥申请
- [ ] 地点搜索接口
- [ ] 地理编码接口
- [ ] 路线规划接口

**Day 3-5: 前端基础**
- [ ] 安装@amap/amap-jsapi-loader
- [ ] 地点搜索组件
- [ ] 事件详情地图显示
- [ ] 一键导航

**Day 6-7: 测试优化**
- [ ] 地址补全测试
- [ ] 地图显示优化
- [ ] 移动端适配

---

### Phase 2: 地图视图（1周）
**Day 8-10: 地图视图**
- [ ] 地图视图页面
- [ ] 所有事件标记显示
- [ ] 点击标记查看详情
- [ ] 分屏视图

**Day 11-12: 交互优化**
- [ ] 聚类显示（事件太多时）
- [ ] 过滤功能（今天/本周/本月）
- [ ] 路线规划显示

**Day 13-14: 移动端**
- [ ] 移动端地图适配
- [ ] 手势操作
- [ ] 底部抽屉

---

### Phase 3: 智能提醒（1周）
**Day 15-17: 路线计算**
- [ ] 实时路况监控
- [ ] 出发时间计算
- [ ] 路况预警

**Day 18-19: 推送通知**
- [ ] Web Push集成
- [ ] Android推送
- [ ] 提醒历史

**Day 20-21: 优化**
- [ ] 学习用户习惯
- [ ] 个性化缓冲时间
- [ ] 交通方式选择（驾车/公交/步行）

---

## 🎨 UI设计要点

### 1. 地点搜索下拉
```
┌─────────────────────────────┐
│ 📍 南昌大学                  │
├─────────────────────────────┤
│ 📍 南昌大学（前湖校区）      │
│    江西省南昌市红谷滩区...   │
│    📏 5.2km                 │
├─────────────────────────────┤
│ 📍 南昌大学（青山湖校区）    │
│    江西省南昌市青山湖区...   │
│    📏 12.5km                │
└─────────────────────────────┘
```

### 2. 事件详情地图
```
┌─────────────────────────────┐
│ 📝 团队会议                  │
│ 🕒 2025-11-07 14:00        │
│ 📍 XX科技园A座              │
├─────────────────────────────┤
│ [     地图显示位置     ]     │
│         🔴                  │
│    (缩放、拖动地图)          │
├─────────────────────────────┤
│ [🧭 导航] [🚗 路线] [📤 分享]│
├─────────────────────────────┤
│ 📏 距离: 15.2km             │
│ ⏱️ 时间: 32分钟             │
│ 💡 建议: 13:20出发           │
└─────────────────────────────┘
```

### 3. 地图视图
```
┌─────────────────────────────┐
│ [📅 日历] [🗺️ 地图] [📊 分屏] │
├─────────────────────────────┤
│             地图             │
│         🔴 🔵 🔴            │
│      🔵       🔴            │
│    🔴    🔵                │
└─────────────────────────────┘
```

---

## 🚀 与其他功能的协同

### 地图 + AI助手
```
用户: "帮我找个离公司近的餐厅，明天中午约饭"
AI: "为您搜索公司附近的餐厅...
    
    推荐：
    1. 海底捞(CBD店) - 500米，步行7分钟
    2. 麦当劳(金融街店) - 300米，步行4分钟
    3. 星巴克(国贸店) - 200米，步行3分钟
    
    选哪一个？"
    
用户: "麦当劳"
AI: "已创建日程：
    📅 明天12:00
    📍 麦当劳(金融街店)
    🗺️ 距离300米
    [查看地图]"
```

### 地图 + 共享事件
```
小明创建"周五聚餐"
  ↓
地点: "海底捞(万达店)"
  ↓
邀请小红、小刚
  ↓
他们收到邀请 → 点击查看
  ↓
显示地图 + "距离你8km，开车15分钟"
  ↓
接受邀请 → 18:40自动收到提醒："该出发了！"
```

### 地图 + 公开日历
```
学校发布"校园导览"
  ↓
包含50个地点（图书馆、食堂、教学楼）
  ↓
每个地点都有坐标
  ↓
学生订阅 → 切换地图视图
  ↓
看到整个校园的建筑分布 ✅
  ↓
新生入学必备！
```

---

## 💡 创新功能

### 1. 一周路线优化
```
分析用户一周的事件地点
  ↓
智能建议：
  "💡 周一的会议和午餐在同一区域，可以顺路
   💡 周三需要跨城区2次，建议调整时间
   💡 周五的聚餐地点距离公司15km，建议提前1小时出发"
```

### 2. 地点热力图
```
统计用户最常去的地方
  ↓
生成热力图：
  - 🔥🔥🔥 公司（50次）
  - 🔥🔥 健身房（20次）
  - 🔥 咖啡厅（15次）
  ↓
根据热力图推荐：
  "您经常去健身房，要创建每周三晚上的固定日程吗？"
```

### 3. 路线记录
```
记录每次导航的路线
  ↓
分析：
  - 最常走的路线
  - 平均耗时
  - 最拥堵时段
  ↓
个性化建议：
  "去公司通常需要35分钟，
   但周一早上会堵车，建议提前50分钟出发"
```

---

## 💎 核心价值

### 1. 解决迟到问题（刚需）
**痛点**: 不知道路程，经常迟到

**解决**: 自动计算路程 + 智能提醒

**价值**: 提升守时率 80% → 95%

### 2. 降低认知负担
**痛点**: 要记住地点、查路线、算时间

**解决**: 一切自动化

**价值**: 用户体验质的飞跃

### 3. 社交属性增强
**痛点**: 和朋友约会，对方找不到地方

**解决**: 共享事件 + 地图 + 导航

**价值**: 减少约会爽约率

---

## 📊 商业化

### 免费用户
- ✅ 地点搜索（每天10次）
- ✅ 查看地图
- ✅ 打开导航
- ❌ 路线规划
- ❌ 智能出发提醒
- ❌ 地图视图

### VIP用户（¥9.9/月）
- ✅ 所有免费功能
- ✅ 路线规划（无限制）
- ✅ 智能出发提醒
- ✅ 地图视图
- ✅ 路线记录
- ✅ 地点热力图
- ✅ 一周路线优化建议

---

## 🏆 竞争优势

| 功能 | Google Calendar | Apple Calendar | **KotlinCalendar** |
|------|----------------|----------------|-------------------|
| 地点搜索 | ✅ | ✅ | ✅ |
| 地图显示 | ✅ | ✅ | ✅ |
| 导航 | ✅ | ✅ | ✅ |
| **智能出发提醒** | ❌ | ⚠️ 基础 | ✅ **实时路况** |
| **地图视图** | ❌ | ❌ | ✅ **创新** |
| **路线优化建议** | ❌ | ❌ | ✅ **创新** |
| 价格 | 免费 | 免费 | ✅ **¥9.9/月** |

**你的优势**: 智能出发提醒 + 地图视图 + 路线优化！

---

## 🎉 总结

地图功能 + 日历 = **永远不迟到的智能助手**

### 核心价值
1. **解决真实痛点** - 迟到、找不到地方
2. **技术完全可行** - 高德API成熟
3. **成本极低** - 免费额度足够
4. **VIP强理由** - 用户愿意为便利付费

### 杀手级功能组合
```
AI助手 + 地图 + 智能提醒 = 完美体验

"明天下午3点在XX大厦开会"
  ↓ AI创建事件
  ↓ 自动搜索地点
  ↓ 计算路程30分钟
  ↓ 明天14:20推送："该出发了！"
  ↓ 一键打开导航
  ↓ 准时到达 ✅
```

**这是一个完整的闭环！** 🚀

---

**要不要我先实现基础的地点搜索和地图显示？（1-2天就能完成MVP）** 😊

