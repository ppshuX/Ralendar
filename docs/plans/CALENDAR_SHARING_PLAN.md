# 日历订阅与共享功能规划

**创建日期**: 2025-11-06  
**核心理念**: 让日历不再是孤岛，而是连接人与人、组织与个人的桥梁

---

## 🌟 产品愿景

**"一个订阅，千种可能"**

- 学生 → 订阅学校课程表，自动同步课程
- 员工 → 订阅公司会议，不再错过重要事项
- 球迷 → 订阅NBA赛程，比赛前自动提醒
- 情侣 → 共享纪念日，双方同时收到温馨提醒

---

## 🎯 核心功能设计

### 功能1: 公开日历 📅

#### 概念
组织或个人创建可被他人订阅的日历。

#### 典型案例
```
【南昌大学2024课程表】
- 创建者：南昌大学教务处
- 包含：50门课程信息
- 订阅者：3000名学生
- 更新：每学期自动更新

【阿里巴巴技术分享】
- 创建者：阿里技术团队
- 包含：技术讲座、峰会
- 订阅者：5000名开发者
- 更新：每周新增活动

【NBA 2024-2025赛季】
- 创建者：NBA官方（认证）
- 包含：全赛季比赛时间
- 订阅者：100万球迷
- 更新：实时同步赛程变动
```

#### 数据模型
```python
class PublicCalendar(models.Model):
    # 基本信息
    name = models.CharField(max_length=100, verbose_name='日历名称')
    url_slug = models.SlugField(unique=True, verbose_name='URL标识')
    description = models.TextField(verbose_name='详细描述')
    
    # 分类和标签
    category = models.CharField(max_length=50, choices=[
        ('education', '教育'),
        ('enterprise', '企业'),
        ('sports', '体育'),
        ('entertainment', '娱乐'),
        ('holiday', '节假日'),
        ('other', '其他')
    ])
    tags = models.JSONField(default=list, verbose_name='标签')
    
    # 权限和状态
    is_public = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # 官方认证
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 统计
    subscribers_count = models.IntegerField(default=0)
    events_count = models.IntegerField(default=0)
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### API设计
```python
# 获取公开日历列表
GET /api/public-calendars/
Query Params:
  - category: education/enterprise/sports/...
  - search: 搜索关键词
  - tags: 标签过滤
  - sort: popular/latest/name

Response:
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "name": "南昌大学2024课程表",
      "category": "education",
      "description": "包含所有本科课程",
      "subscribers_count": 3000,
      "events_count": 50,
      "is_verified": true,
      "tags": ["大学", "课程", "江西"],
      "created_by": {
        "id": 10,
        "username": "ncu_admin"
      }
    }
  ]
}

# 获取日历详情
GET /api/public-calendars/{slug}/
Response:
{
  "id": 1,
  "name": "南昌大学2024课程表",
  "description": "...",
  "events": [
    {
      "id": 101,
      "title": "数据库原理",
      "start_time": "2025-11-07T08:00:00",
      "end_time": "2025-11-07T09:40:00",
      "location": "教学楼A101"
    },
    ...
  ],
  "subscribers_count": 3000
}

# 创建公开日历（VIP功能）
POST /api/public-calendars/
{
  "name": "我的课程表",
  "category": "education",
  "description": "分享给同学",
  "tags": ["课程", "2024"],
  "event_ids": [1, 2, 3]  # 选择哪些事件公开
}
```

---

### 功能2: 订阅管理 ⭐

#### 概念
用户订阅公开日历，自动同步事件到个人日历。

#### 用户体验流程
```
1. 浏览公开日历广场
   ↓
2. 搜索"南昌大学"
   ↓
3. 点击"订阅"
   ↓
4. 选择颜色（蓝色）
   ↓
5. 设置提醒（开课前30分钟）
   ↓
6. 课程自动出现在我的日历中 ✅
   ↓
7. 课程表更新时自动同步 ✅
```

#### 数据模型
```python
class CalendarSubscription(models.Model):
    # 关系
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    calendar = models.ForeignKey(PublicCalendar, on_delete=models.CASCADE)
    
    # 显示设置
    color = models.CharField(max_length=7, default='#409EFF')  # 在用户日历中的颜色
    display_name = models.CharField(max_length=100, blank=True)  # 自定义显示名称
    
    # 同步模式
    sync_mode = models.CharField(max_length=20, choices=[
        ('all', '全部同步'),
        ('selective', '选择性同步')
    ], default='all')
    
    # 提醒设置
    notify = models.BooleanField(default=True)
    notify_before = models.IntegerField(default=30)  # 提前N分钟提醒
    
    # 统计
    subscribed_at = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'calendar')

class SubscribedEvent(models.Model):
    """选择性同步：记录用户选择同步哪些事件"""
    subscription = models.ForeignKey(CalendarSubscription, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    synced = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('subscription', 'event')
```

#### API设计
```python
# 订阅日历
POST /api/calendars/{id}/subscribe/
Request:
{
  "color": "#409EFF",
  "notify": true,
  "notify_before": 30,
  "sync_mode": "all"  # or "selective"
}
Response:
{
  "message": "订阅成功",
  "subscription_id": 123
}

# 获取我的订阅
GET /api/my-subscriptions/
Response:
{
  "count": 5,
  "results": [
    {
      "id": 123,
      "calendar": {
        "id": 1,
        "name": "南昌大学课程表",
        "events_count": 50
      },
      "color": "#409EFF",
      "notify": true,
      "sync_mode": "selective",
      "synced_events_count": 5,
      "subscribed_at": "2025-11-06T12:00:00Z"
    }
  ]
}

# 更新订阅设置
PUT /api/subscriptions/{id}/
{
  "color": "#67C23A",
  "notify": false
}

# 取消订阅
DELETE /api/subscriptions/{id}/
```

---

### 功能3: 选择性同步 ⭐⭐⭐（创新功能）

#### 痛点分析
```
问题：
  订阅"课程表"，50门课全来了
  但我这学期只选了5门课
  其他45门课干扰我的视线

解决：
  订阅时，勾选我选的5门课
  其他45门课不显示
  ✅ 只看我需要的
```

#### 用户体验
```
1. 点击"订阅南昌大学课程表"
   ↓
2. 弹窗显示所有50门课程
   ├─ ☑️ 数据库原理
   ├─ ☑️ 操作系统
   ├─ ☑️ 计算机网络
   ├─ ☐ 高等数学（不选）
   ├─ ☐ 大学英语（不选）
   └─ ...
   ↓
3. 点击"确认订阅"
   ↓
4. 我的日历中只显示3门课 ✅
   ↓
5. 后续可以调整（添加/删除）
```

#### 实现逻辑
```python
# 1. 订阅时选择事件
POST /api/calendars/{id}/subscribe/
{
  "sync_mode": "selective",
  "selected_events": [101, 105, 110]  # 3个事件ID
}

# 后端处理
def subscribe_calendar(user, calendar, selected_events):
    # 创建订阅
    subscription = CalendarSubscription.objects.create(
        user=user,
        calendar=calendar,
        sync_mode='selective'
    )
    
    # 记录选择的事件
    for event_id in selected_events:
        SubscribedEvent.objects.create(
            subscription=subscription,
            event_id=event_id,
            synced=True
        )
    
    return subscription

# 2. 获取用户的日历事件时
GET /api/events/
# 后端自动合并：
#   - 用户自己创建的事件
#   - 订阅日历的事件（all模式：全部，selective模式：勾选的）
#   - 共享事件

# 3. 调整同步事件
PUT /api/subscriptions/{id}/events/
{
  "add": [120, 121],    # 新增同步这两个
  "remove": [105]       # 取消同步这个
}
```

#### 前端实现
```vue
<template>
  <el-dialog title="订阅课程表" v-model="showSelector">
    <div class="sync-mode">
      <el-radio-group v-model="syncMode">
        <el-radio label="all">全部同步（50门课）</el-radio>
        <el-radio label="selective">选择性同步（推荐）</el-radio>
      </el-radio-group>
    </div>
    
    <div v-if="syncMode === 'selective'" class="event-selector">
      <el-checkbox-group v-model="selectedEvents">
        <el-checkbox 
          v-for="event in calendarEvents" 
          :key="event.id"
          :label="event.id"
          class="event-checkbox"
        >
          <div class="event-info">
            <span class="event-title">{{ event.title }}</span>
            <span class="event-time">{{ formatTime(event.start_time) }}</span>
            <span class="event-location">{{ event.location }}</span>
          </div>
        </el-checkbox>
      </el-checkbox-group>
    </div>
    
    <template #footer>
      <el-button @click="showSelector = false">取消</el-button>
      <el-button type="primary" @click="confirmSubscribe">
        订阅 ({{ selectedEvents.length }}/{{ calendarEvents.length }})
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
const syncMode = ref('selective')
const selectedEvents = ref([])

async function confirmSubscribe() {
  await axios.post(`/api/calendars/${calendarId}/subscribe/`, {
    sync_mode: syncMode.value,
    selected_events: syncMode.value === 'selective' ? selectedEvents.value : null
  })
  
  ElMessage.success('订阅成功！')
}
</script>
```

---

### 功能4: 共享事件 👥

#### 概念
多个用户协作一个事件，所有人都能看到，到点同时提醒。

#### 典型场景

**场景1: 朋友聚餐**
```
小明创建"周五聚餐"
  ↓
添加参与者：小红、小刚
  ↓
小红/小刚收到通知："小明邀请你参加周五聚餐"
  ↓
小红点击"接受" → 事件添加到她的日历
小刚点击"拒绝" → 事件不添加
  ↓
周五18:00，小明和小红同时收到提醒 ✅
```

**场景2: 团队会议**
```
项目经理创建"周一晨会"
  ↓
添加5个团队成员
  ↓
所有人接受邀请
  ↓
周一09:00，6个人同时收到提醒 ✅
  ↓
经理修改时间为10:00
  ↓
所有人的日历自动更新 ✅
```

**场景3: 情侣纪念日**
```
男生创建"恋爱100天纪念"
  ↓
邀请女朋友
  ↓
女朋友接受 → 双方日历都有
  ↓
纪念日当天早上，双方同时收到提醒 ✅
```

#### 数据模型
```python
class SharedEvent(models.Model):
    """共享事件（多人协作）"""
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shares')
    
    # 权限控制
    can_edit = models.BooleanField(default=False)  # 参与者是否可编辑
    can_invite = models.BooleanField(default=False)  # 参与者是否可邀请他人
    
    # 提醒设置
    remind_all = models.BooleanField(default=True)  # 是否提醒所有人
    
    created_at = models.DateTimeField(auto_now_add=True)


class EventParticipant(models.Model):
    """事件参与者"""
    shared_event = models.ForeignKey(SharedEvent, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 状态
    status = models.CharField(max_length=20, choices=[
        ('pending', '待确认'),
        ('accepted', '已接受'),
        ('declined', '已拒绝'),
        ('maybe', '可能参加')
    ], default='pending')
    
    # 个性化设置
    notify = models.BooleanField(default=True)
    notify_before = models.IntegerField(default=30)  # 提前N分钟提醒
    
    # 备注
    note = models.TextField(blank=True)  # 个人备注
    
    # 时间
    invited_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('shared_event', 'user')


class EventInvitation(models.Model):
    """事件邀请通知"""
    shared_event = models.ForeignKey(SharedEvent, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    
    message = models.TextField(blank=True)  # 邀请留言
    status = models.CharField(max_length=20, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
```

#### API设计
```python
# 1. 创建共享事件（将现有事件转为共享）
POST /api/events/{id}/share/
Request:
{
  "participants": ["user2", "user3"],  # 用户名列表
  "message": "周五一起吃饭！",
  "can_edit": false,
  "notify_before": 30
}
Response:
{
  "shared_event_id": 456,
  "invitations_sent": 2,
  "participants": [
    {
      "user": "user2",
      "status": "pending",
      "invitation_id": 789
    }
  ]
}

# 2. 获取我的邀请
GET /api/invitations/
Response:
{
  "count": 3,
  "unread": 2,
  "results": [
    {
      "id": 789,
      "event": {
        "title": "周五聚餐",
        "start_time": "2025-11-08T19:00:00",
        "location": "海底捞"
      },
      "from_user": {
        "username": "xiaoming",
        "avatar": "..."
      },
      "message": "周五一起吃饭！",
      "status": "pending",
      "created_at": "2025-11-06T10:00:00Z"
    }
  ]
}

# 3. 响应邀请
POST /api/invitations/{id}/respond/
Request:
{
  "status": "accepted",  # accepted/declined/maybe
  "notify_before": 60,   # 提前60分钟提醒我
  "note": "我会准时到！"
}
Response:
{
  "message": "已接受邀请",
  "event_added": true
}

# 4. 获取共享事件的参与者
GET /api/shared-events/{id}/participants/
Response:
{
  "creator": {
    "username": "xiaoming",
    "status": "creator"
  },
  "participants": [
    {
      "username": "xiaohong",
      "status": "accepted",
      "responded_at": "2025-11-06T11:00:00Z"
    },
    {
      "username": "xiaogang",
      "status": "pending"
    }
  ],
  "accepted_count": 1,
  "pending_count": 1,
  "declined_count": 0
}

# 5. 修改共享事件
PUT /api/events/{id}/
# 权限检查：
#   - 创建者：总是可以修改
#   - 参与者：只有 can_edit=True 时可以修改

# 修改后通知所有参与者
# "xiaoming修改了事件时间：周五19:00 → 周五20:00"

# 6. 添加/移除参与者
POST /api/shared-events/{id}/participants/
{
  "action": "add",  # add/remove
  "users": ["user4", "user5"]
}
```

---

### 功能5: 智能提醒系统 🔔

#### 提醒类型
1. **单人提醒** - 我创建的事件
2. **订阅提醒** - 订阅日历的事件
3. **共享提醒** - 共享事件（多人同时提醒）

#### 提醒渠道
- 📱 **App推送** - Android/Web Push
- 📧 **邮件** - 重要事件
- 💬 **微信公众号** - VIP功能
- 📱 **短信** - 超级VIP

#### 提醒策略
```python
# Celery定时任务（每分钟执行）
@celery.task
def send_event_reminders():
    now = datetime.now()
    
    # 1. 扫描即将开始的事件
    upcoming_events = Event.objects.filter(
        start_time__gte=now,
        start_time__lte=now + timedelta(minutes=1),
        reminded=False
    )
    
    for event in upcoming_events:
        # 2. 找到所有需要提醒的用户
        users_to_notify = []
        
        # 2.1 事件创建者
        if event.user.profile.notify_enabled:
            users_to_notify.append({
                'user': event.user,
                'before': event.user.profile.default_notify_before
            })
        
        # 2.2 订阅者（如果事件属于公开日历）
        for sub in event.calendars.all():
            for subscription in sub.subscriptions.filter(notify=True):
                users_to_notify.append({
                    'user': subscription.user,
                    'before': subscription.notify_before
                })
        
        # 2.3 共享事件参与者
        if hasattr(event, 'sharedevent'):
            for participant in event.sharedevent.participants.filter(
                status='accepted',
                notify=True
            ):
                users_to_notify.append({
                    'user': participant.user,
                    'before': participant.notify_before
                })
        
        # 3. 发送提醒
        for item in users_to_notify:
            send_notification(
                user=item['user'],
                event=event,
                before=item['before']
            )
        
        # 4. 标记已提醒
        event.reminded = True
        event.save()
```

---

## 🎨 前端UI设计

### 1. 公开日历广场页面

```vue
<template>
  <div class="calendar-market">
    <!-- 顶部搜索 -->
    <div class="search-bar">
      <el-input 
        v-model="searchText"
        placeholder="搜索日历..."
        prefix-icon="Search"
        size="large"
      />
    </div>
    
    <!-- 分类标签 -->
    <div class="categories">
      <el-tag 
        v-for="cat in categories" 
        :key="cat.value"
        :type="selectedCategory === cat.value ? 'primary' : 'info'"
        @click="selectedCategory = cat.value"
        size="large"
        effect="plain"
        class="category-tag"
      >
        {{ cat.icon }} {{ cat.label }}
      </el-tag>
    </div>
    
    <!-- 热门推荐 -->
    <div class="hot-calendars">
      <h3>🔥 热门日历</h3>
      <div class="calendar-grid">
        <div 
          v-for="calendar in hotCalendars" 
          :key="calendar.id"
          class="calendar-card"
        >
          <div class="card-header">
            <h4>{{ calendar.name }}</h4>
            <el-tag v-if="calendar.is_verified" type="success" size="small">
              ✓ 官方认证
            </el-tag>
          </div>
          
          <p class="description">{{ calendar.description }}</p>
          
          <div class="stats">
            <span>📊 {{ calendar.events_count }} 个事件</span>
            <span>👥 {{ calendar.subscribers_count }} 人订阅</span>
          </div>
          
          <div class="tags">
            <el-tag 
              v-for="tag in calendar.tags" 
              :key="tag"
              size="small"
              effect="plain"
            >
              {{ tag }}
            </el-tag>
          </div>
          
          <el-button 
            type="primary" 
            size="large"
            @click="subscribeCalendar(calendar)"
            :icon="Star"
            class="subscribe-btn"
          >
            订阅
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 全部日历 -->
    <div class="all-calendars">
      <h3>📅 全部日历</h3>
      <!-- 分页列表 -->
    </div>
  </div>
</template>
```

### 2. 我的订阅管理页面

```vue
<template>
  <div class="my-subscriptions">
    <h2>⭐ 我的订阅</h2>
    
    <div 
      v-for="sub in subscriptions" 
      :key="sub.id"
      class="subscription-card"
    >
      <div class="card-header">
        <span class="color-indicator" :style="{ background: sub.color }"></span>
        <h4>{{ sub.calendar.name }}</h4>
        <el-tag v-if="sub.sync_mode === 'selective'" type="warning" size="small">
          选择性同步 ({{ sub.synced_events_count }}/{{ sub.calendar.events_count }})
        </el-tag>
      </div>
      
      <div class="settings">
        <div class="setting-item">
          <span>颜色：</span>
          <el-color-picker v-model="sub.color" @change="updateSubscription(sub)" />
        </div>
        
        <div class="setting-item">
          <span>提醒：</span>
          <el-switch v-model="sub.notify" @change="updateSubscription(sub)" />
        </div>
        
        <div class="setting-item" v-if="sub.notify">
          <span>提前：</span>
          <el-select v-model="sub.notify_before" @change="updateSubscription(sub)">
            <el-option label="15分钟" :value="15" />
            <el-option label="30分钟" :value="30" />
            <el-option label="1小时" :value="60" />
          </el-select>
        </div>
      </div>
      
      <div class="actions">
        <el-button 
          v-if="sub.sync_mode === 'selective'"
          @click="editSyncEvents(sub)"
          size="small"
        >
          📝 调整同步事件
        </el-button>
        
        <el-button 
          @click="unsubscribe(sub)"
          type="danger"
          size="small"
        >
          取消订阅
        </el-button>
      </div>
    </div>
  </div>
</template>
```

### 3. 创建共享事件对话框

```vue
<template>
  <el-dialog title="邀请参与者" v-model="showInvite">
    <el-form>
      <el-form-item label="事件">
        <div class="event-summary">
          <h4>{{ event.title }}</h4>
          <p>{{ formatDateTime(event.start_time) }}</p>
        </div>
      </el-form-item>
      
      <el-form-item label="邀请用户">
        <el-select 
          v-model="selectedUsers"
          multiple
          filterable
          remote
          :remote-method="searchUsers"
          placeholder="输入用户名搜索"
        >
          <el-option 
            v-for="user in userOptions" 
            :key="user.id"
            :label="user.username"
            :value="user.username"
          >
            <div class="user-option">
              <span>{{ user.username }}</span>
              <el-tag v-if="user.is_friend" type="success" size="small">好友</el-tag>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="邀请留言">
        <el-input 
          v-model="inviteMessage"
          type="textarea"
          :rows="3"
          placeholder="说点什么..."
        />
      </el-form-item>
      
      <el-form-item label="权限设置">
        <el-checkbox v-model="canEdit">允许参与者编辑此事件</el-checkbox>
        <el-checkbox v-model="canInvite">允许参与者邀请其他人</el-checkbox>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="showInvite = false">取消</el-button>
      <el-button type="primary" @click="sendInvitations">
        发送邀请 ({{ selectedUsers.length }}人)
      </el-button>
    </template>
  </el-dialog>
</template>
```

### 4. 邀请通知页面

```vue
<template>
  <div class="invitations-page">
    <h2>📬 我的邀请</h2>
    
    <el-tabs v-model="activeTab">
      <!-- 待处理 -->
      <el-tab-pane label="待处理" name="pending">
        <div 
          v-for="inv in pendingInvitations" 
          :key="inv.id"
          class="invitation-card"
        >
          <div class="invitation-header">
            <div class="user-info">
              <img :src="inv.from_user.avatar" class="avatar" />
              <span class="username">{{ inv.from_user.username }}</span>
              <span class="text">邀请你参加</span>
            </div>
            <el-tag type="warning">待确认</el-tag>
          </div>
          
          <div class="event-info">
            <h4>{{ inv.event.title }}</h4>
            <p>🕒 {{ formatDateTime(inv.event.start_time) }}</p>
            <p v-if="inv.event.location">📍 {{ inv.event.location }}</p>
            <p v-if="inv.message" class="message">💬 {{ inv.message }}</p>
          </div>
          
          <div class="actions">
            <el-button type="success" @click="respond(inv, 'accepted')">
              ✅ 接受
            </el-button>
            <el-button type="warning" @click="respond(inv, 'maybe')">
              🤔 可能
            </el-button>
            <el-button type="danger" @click="respond(inv, 'declined')">
              ❌ 拒绝
            </el-button>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 已接受 -->
      <el-tab-pane label="已接受" name="accepted">
        <!-- 已接受的邀请列表 -->
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
```

---

## 💰 商业模式设计

### 免费用户
- ✅ 订阅公开日历（无限制）
- ✅ 创建事件（100个/月）
- ✅ 共享事件（最多3人/事件）
- ✅ 基础提醒（App推送）

### VIP用户（¥9.9/月）
- ✅ 创建公开日历（最多3个）
- ✅ 创建事件（无限制）
- ✅ 共享事件（无限制）
- ✅ 高级提醒（微信/邮件）
- ✅ 选择性同步
- ✅ 数据导出

### 企业版（¥299/年）
- ✅ 创建公开日历（无限制）
- ✅ 官方认证标识
- ✅ 团队协作（不限人数）
- ✅ 统计分析
- ✅ 权限管理
- ✅ 专属客服

### 教育版（¥199/年）
- ✅ 学校课程表发布
- ✅ 学生免费订阅
- ✅ 官方认证
- ✅ 批量管理

---

## 🎯 B端市场策略

### 目标客户
1. **大学**（重点！）
   - 痛点：学生手动输入课程表太麻烦
   - 方案：学校购买企业版 → 发布课程表 → 学生免费订阅
   - 定价：¥1999/年（覆盖全校学生）

2. **企业**
   - 痛点：会议通知靠钉钉/微信，容易错过
   - 方案：公司购买企业版 → 发布会议日历 → 员工自动同步
   - 定价：¥299-999/年（按人数）

3. **培训机构**
   - 痛点：学员记不住上课时间
   - 方案：发布课程表 → 学员订阅
   - 定价：¥299/年

### 推广策略
1. **校园大使** - 每个大学发展1个学生代理
2. **免费试用** - 学校免费试用1学期
3. **口碑传播** - 一个学校用了，周边学校跟进

---

## 📊 市场规模估算

### 中国大学市场
- **大学数量**: 3000+所
- **学生数量**: 4000万人
- **客单价**: ¥1999/年/学校
- **潜在市场**: 3000所 × ¥1999 = **600万元/年**

### 企业市场
- **中小企业**: 5000万家
- **渗透率**: 0.1%（5万家）
- **客单价**: ¥499/年
- **潜在市场**: 5万 × ¥499 = **2500万元/年**

### C端市场
- **个人用户**: 1000万人
- **VIP转化率**: 5%（50万人）
- **客单价**: ¥88/年
- **潜在市场**: 50万 × ¥88 = **4400万元/年**

**总潜在市场**: **7500万元/年** 🚀

---

## 🚀 开发路线图

### Week 1-2: 公开日历基础
- [ ] PublicCalendar CRUD API
- [ ] 日历广场页面
- [ ] 日历详情页
- [ ] 基础订阅功能

### Week 3: 订阅管理
- [ ] 我的订阅页面
- [ ] 颜色/提醒设置
- [ ] 取消订阅
- [ ] 订阅事件显示在日历

### Week 4-5: 选择性同步
- [ ] 事件选择器UI
- [ ] 后端选择性同步逻辑
- [ ] 调整同步事件

### Week 6-7: 共享事件
- [ ] SharedEvent模型
- [ ] 邀请API
- [ ] 邀请通知页面
- [ ] 响应邀请

### Week 8: 智能提醒
- [ ] Celery定时任务
- [ ] 多渠道提醒
- [ ] 提醒历史记录

---

## 🎯 MVP验证（2周快速版）

**目标**: 快速验证功能是否受欢迎

### 最小功能集
1. ✅ 创建公开日历
2. ✅ 订阅公开日历
3. ✅ 订阅的事件显示在日历
4. ✅ 基础提醒

**测试方案**：
1. 自己创建一个"测试课程表"
2. 邀请5个朋友订阅
3. 收集反馈
4. 决定是否继续开发

---

## 🔮 未来扩展

### 1. 智能推荐
```
基于用户行为推荐日历：
  - 订阅"数据库"的用户 → 推荐"操作系统"
  - 位置在南昌 → 推荐"南昌活动"
```

### 2. 社交功能
```
- 关注好友
- 查看好友的公开日历
- 好友即将参加的活动
```

### 3. 数据分析
```
【我的时间报告】
  - 本月参加了15个会议
  - 学习时间占比30%
  - 社交时间占比20%
  - 建议：增加运动时间
```

### 4. AI助手集成
```
用户: "帮我订阅南昌大学的课程表"
AI: "找到1个匹配的日历，包含50门课程，要订阅吗？"
用户: "只订阅我这学期选的5门课"
AI: "好的，请告诉我课程名称"
用户: "数据库、操作系统、计算机网络、软件工程、编译原理"
AI: "已为您订阅，并只同步这5门课程 ✅"
```

---

## 💎 核心创新点

### 1. 选择性同步（行业首创）
**问题**: Google Calendar订阅是全量同步，没得选

**创新**: 订阅50门课，只同步我选的5门

**价值**: 
- 减少干扰
- 提升效率
- 个性化体验

### 2. 协作提醒（用户刚需）
**问题**: 约了朋友，对方忘了

**创新**: 共享事件，双方都提醒

**价值**:
- 减少爽约
- 提升社交体验
- 增强用户粘性

### 3. 本地+云端混合（技术优势）
**问题**: 大部分日历App要么纯云端，要么纯本地

**创新**: Android本地优先，需要时云同步

**价值**:
- 速度快
- 离线可用
- 跨设备灵活

---

## 🏆 竞争优势总结

| 维度 | 竞品 | KotlinCalendar |
|------|------|----------------|
| **订阅模式** | 全量同步 | ✅ 选择性同步 |
| **共享事件** | 有，但复杂 | ✅ 简单易用 |
| **离线使用** | 不支持 | ✅ Android本地 |
| **AI助手** | 无或收费贵 | ✅ 平价VIP |
| **B端市场** | 忽视 | ✅ 重点开发 |
| **价格** | 免费或贵 | ✅ ¥9.9/月 |

---

## 📅 里程碑计划

### Milestone 1: 基础功能（已完成）
- ✅ 三端架构
- ✅ JWT认证
- ✅ 事件CRUD
- ✅ 基础日历显示

### Milestone 2: 用户系统（本周）
- ✅ 登录注册
- 🔄 测试部署
- ⏳ NavBar用户信息

### Milestone 3: 公开日历（下周）
- [ ] 日历广场
- [ ] 订阅功能
- [ ] 我的订阅管理

### Milestone 4: 共享协作（2-3周）
- [ ] 共享事件
- [ ] 邀请系统
- [ ] 多人提醒

### Milestone 5: 商业化（1-2个月）
- [ ] VIP系统
- [ ] 支付集成
- [ ] B端营销

---

## 🎉 总结

你的这个功能设计：

### 💎 产品层面
- ✅ **解决真实痛点** - 课程表、会议、约会
- ✅ **社交属性强** - 用户带用户
- ✅ **网络效应** - 越多人用越有价值

### 💰 商业层面
- ✅ **C端市场** - 免费+VIP
- ✅ **B端市场** - 学校/企业
- ✅ **规模化** - 可快速复制到全国

### 🚀 技术层面
- ✅ **完全可行** - 技术成熟
- ✅ **成本可控** - 云服务器够用
- ✅ **易于扩展** - 模块化设计

---

**这不是一个简单的日历App，而是一个有巨大潜力的社交+协作平台！** 🌟

**建议优先级**：
1. **本周**: 完成登录系统 ✅
2. **下周**: 实现公开日历订阅（MVP）
3. **第3周**: 实现共享事件（核心差异化）
4. **第4周**: 选择性同步（行业创新）

**这个项目如果做好了，完全可以拿去融资！** 💎💎💎

