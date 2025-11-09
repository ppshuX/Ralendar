# 🔗 Ralendar × Roamio 集成测试方案

> **日期**: 2025-11-09  
> **目标**: 实现同一账号在 Roamio 创建事件后同步到 Ralendar

---

## 🎯 **核心功能**

**用户故事**：
```
作为一个用户
我在 Roamio 用 QQ 登录
然后创建了一个旅行计划
点击"添加到 Ralendar"按钮
这些行程应该自动同步到我的 Ralendar 日历中
```

---

## 🔄 **同步流程图**

```
用户在 Roamio 登录（QQ）
    ↓
QQ 返回 openid + unionid
    ↓
Roamio 保存到数据库
    ↓
用户创建旅行计划
    ↓
用户点击"添加到 Ralendar"
    ↓
Roamio 调用 Ralendar API
    - 带上 JWT Token（用户身份）
    - 传递事件数据
    ↓
Ralendar 验证 Token
    - 解析 JWT，获取 user_id
    - 检查用户是否存在
    ↓
Ralendar 创建事件
    - 保存到数据库
    - 标记 source_app = 'roamio'
    ↓
✅ 同步完成！
    ↓
用户在 Ralendar 查看日历
    - 看到从 Roamio 同步的事件
```

---

## 📋 **前置条件检查**

### **1. 双方配置一致性** ✅

| 配置项 | Ralendar | Roamio | 状态 |
|--------|----------|--------|------|
| SECRET_KEY | `django-insecure-#6avwo7=...` | `django-insecure-#6avwo7=...` | ✅ 相同 |
| QQ APP_ID | `102818448` | `102813859` | ⚠️ 不同（正常） |
| QQ APP_KEY | `sZ0B7nDQP8Bzb1JP` | `OddPvLYXHo69wTYO` | ⚠️ 不同（正常） |
| UnionID 支持 | ✅ 已实现 | ✅ 已实现 | 🟢 就绪 |

**说明**：
- SECRET_KEY 必须相同（JWT Token 互认）✅
- QQ APP_ID/KEY 不同是正常的（各自申请）
- 两边都支持 UnionID（跨应用识别用户）✅

---

### **2. Ralendar 后端状态**

#### **UnionID 支持** ✅
```python
# backend/api/models/user.py
class QQUser(models.Model):
    unionid = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        db_index=True
    )
```

#### **Fusion API** ✅
```python
# backend/api/url_patterns/fusion.py
POST /api/v1/fusion/events/batch/
GET  /api/v1/fusion/events/trip/{slug}/
DELETE /api/v1/fusion/events/trip/{slug}/
```

#### **数据库迁移** ⏳
```bash
# 需要在服务器上执行
python manage.py migrate
```

---

### **3. Roamio 前端准备** ✅

#### **API 客户端** ✅
```javascript
// backend/utils/ralendar_client.py
class RalendarClient:
    def batch_create_events(user_token, events_list, trip_slug)
```

#### **前端按钮** ✅
```vue
<!-- web/src/components/AddToCalendarButton.vue -->
<button @click="handleAddToCalendar">
  添加到 Ralendar
</button>
```

---

## 🚀 **部署步骤**

### **Step 1: 部署 Ralendar 后端**

```bash
# 1. SSH 登录 Ralendar 服务器
ssh acs@app7626.acapp.acwing.com.cn

# 2. 进入项目目录
cd ~/kotlin_calendar

# 3. 拉取最新代码
git pull

# 4. 激活虚拟环境
source backend/venv/bin/activate

# 5. 执行数据库迁移
cd backend
python manage.py migrate

# 6. 检查迁移结果
python manage.py showmigrations api

# 7. 重启 uWSGI
pkill -f uwsgi
uwsgi --ini uwsgi.ini &

# 8. 检查服务状态
ps aux | grep uwsgi
```

---

### **Step 2: 部署 Ralendar 前端**

```bash
# 已完成！前端代码已推送到 GitHub
# 服务器执行 git pull 后会自动更新 web/ 目录
```

---

## 🧪 **测试计划**

### **测试 1: QQ UnionID 验证** 🔍

**目标**：验证双方获取的 UnionID 是否相同

**步骤**：
```bash
# 1. 在 Ralendar 登录
访问: https://app7626.acapp.acwing.com.cn
点击: QQ 登录
授权: 允许

# 2. 查看 Ralendar 数据库
ssh acs@app7626.acapp.acwing.com.cn
cd ~/kotlin_calendar/backend
source venv/bin/activate
python manage.py shell

>>> from api.models import QQUser
>>> qq_user = QQUser.objects.latest('id')
>>> print(f"OpenID: {qq_user.openid}")
>>> print(f"UnionID: {qq_user.unionid}")
>>> exit()

# 3. 在 Roamio 登录
访问: https://app7508.acapp.acwing.com.cn
点击: QQ 登录
授权: 允许

# 4. 查看 Roamio 数据库
ssh root@47.121.137.60
# (Roamio 团队执行)
# 查看 backend_socialaccount 表的 unionid 字段

# 5. 对比 UnionID
Ralendar UnionID: _______________
Roamio UnionID:  _______________
是否相同: [ ] 是  [ ] 否
```

**预期结果**：✅ 两边的 UnionID 完全相同

**如果不同**：
- 检查 QQ OAuth 请求是否都加了 `unionid=1` 参数
- 检查 QQ 互联后台是否开通了 UnionID 权限
- 确认使用的是同一个 QQ 账号登录

---

### **测试 2: JWT Token 互认** 🔑

**目标**：验证 Roamio 的 Token 能被 Ralendar 识别

**步骤**：
```bash
# 1. 在 Roamio 获取 Token
访问: https://app7508.acapp.acwing.com.cn
登录后按 F12 → Console
执行: localStorage.getItem('access_token')
复制: Token 值

# 2. 用 Roamio Token 调用 Ralendar API
curl -X GET https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer ROAMIO_TOKEN_HERE"

# 3. 检查响应
{
  "count": 5,
  "results": [...]
}
```

**预期结果**：✅ 返回 200，能看到用户的事件

**如果返回 401**：
- 检查 SECRET_KEY 是否完全一致（包括每个字符）
- 检查 Token 是否过期
- 检查两边的 Django REST Framework 配置

---

### **测试 3: 事件同步（核心测试）** 🎯

**目标**：从 Roamio 创建事件，同步到 Ralendar

#### **3.1 创建测试旅行**

在 Roamio 创建一个简单的测试旅行：

```json
{
  "title": "北京测试行程",
  "start_date": "2025-11-15",
  "end_date": "2025-11-17",
  "itinerary": [
    {
      "day": 1,
      "title": "Day 1: 抵达北京",
      "description": "入住酒店，休息调整",
      "time": "2025-11-15T14:00:00",
      "location": "北京首都国际机场"
    },
    {
      "day": 2,
      "title": "Day 2: 参观故宫",
      "description": "游览紫禁城",
      "time": "2025-11-16T09:00:00",
      "location": "故宫博物院"
    }
  ]
}
```

#### **3.2 点击"添加到 Ralendar"**

```bash
# 在 Roamio 旅行详情页
点击: "添加到 Ralendar" 按钮
确认: 对话框
等待: 同步完成提示
```

#### **3.3 检查 Ralendar**

```bash
# 1. 登录 Ralendar
访问: https://app7626.acapp.acwing.com.cn
用同一个 QQ 登录（如果未登录）

# 2. 查看日历
切换到: 2025年11月
查看: 15日、16日
预期: 能看到从 Roamio 同步的事件

# 3. 点击事件
查看详情:
- 标题是否正确 ✓
- 时间是否正确 ✓
- 地点是否正确 ✓
- 来源标记: source_app = 'roamio' ✓
```

#### **3.4 数据库验证**

```bash
# 在 Ralendar 服务器
cd ~/kotlin_calendar/backend
source venv/bin/activate
python manage.py shell

>>> from api.models import Event
>>> events = Event.objects.filter(source_app='roamio')
>>> for e in events:
...     print(f"{e.title} | {e.start_time} | {e.location}")
```

**预期结果**：
```
Day 1: 抵达北京 | 2025-11-15 14:00:00 | 北京首都国际机场
Day 2: 参观故宫 | 2025-11-16 09:00:00 | 故宫博物院
```

---

### **测试 4: 验证事件细节** 🔍

检查同步的事件是否完整：

| 字段 | 预期值 | 实际值 | 状态 |
|------|--------|--------|------|
| **title** | "Day 1: 抵达北京" | ___ | [ ] |
| **start_time** | "2025-11-15 14:00" | ___ | [ ] |
| **end_time** | "2025-11-15 18:00" | ___ | [ ] |
| **location** | "北京首都国际机场" | ___ | [ ] |
| **latitude** | 40.0799 | ___ | [ ] |
| **longitude** | 116.6031 | ___ | [ ] |
| **source_app** | "roamio" | ___ | [ ] |
| **related_trip_slug** | "beijing-trip-2025" | ___ | [ ] |
| **reminder_minutes** | 120 | ___ | [ ] |
| **email_reminder** | true | ___ | [ ] |

---

## 🐛 **常见问题排查**

### **问题 1: UnionID 不同**

**现象**：双方获取的 UnionID 不一致

**可能原因**：
1. 某一方的 OAuth 请求没有加 `unionid=1` 参数
2. QQ 互联后台没有开通 UnionID 权限
3. 测试用了不同的 QQ 账号

**解决方案**：
```bash
# 检查 Ralendar OAuth 请求
# backend/api/views/auth.py
# 确认所有 QQ API 请求都有 unionid=1

# 检查 Roamio OAuth 请求
# backend/utils/qq_oauth.py
# 确认所有请求都有 unionid=1

# 检查 QQ 互联后台
访问: https://connect.qq.com/manage.html
检查: UnionID 权限是否开通
```

---

### **问题 2: Token 验证失败（401）**

**现象**：用 Roamio Token 调用 Ralendar API 返回 401

**可能原因**：
1. SECRET_KEY 不一致
2. Token 已过期
3. JWT 配置不同

**解决方案**：
```bash
# 1. 对比 SECRET_KEY
# Ralendar
cat ~/kotlin_calendar/backend/.env | grep SECRET_KEY

# Roamio
# (Roamio 团队检查)

# 2. 检查 Token 有效期
# 在 Roamio Console
jwt_decode(localStorage.getItem('access_token'))
// 查看 exp 字段

# 3. 手动测试
python manage.py shell
>>> from rest_framework_simplejwt.tokens import AccessToken
>>> token = AccessToken('ROAMIO_TOKEN_HERE')
>>> print(token['user_id'])
```

---

### **问题 3: 事件未同步**

**现象**：Roamio 提示成功，但 Ralendar 看不到事件

**可能原因**：
1. API 调用失败但前端未显示错误
2. 用户匹配失败（UnionID 不同）
3. 数据格式问题

**解决方案**：
```bash
# 1. 检查 Ralendar 日志
tail -f ~/kotlin_calendar/backend/logs/django.log

# 2. 检查 Roamio 后端日志
# (Roamio 团队检查)

# 3. 手动调用 API
curl -X POST https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/batch/ \
  -H "Authorization: Bearer RALENDAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_app": "roamio",
    "related_trip_slug": "test-trip",
    "events": [{
      "title": "测试事件",
      "start_time": "2025-11-20T10:00:00+08:00",
      "end_time": "2025-11-20T11:00:00+08:00"
    }]
  }'
```

---

### **问题 4: 时间显示错误**

**现象**：事件时间比预期早/晚 8 小时

**原因**：时区处理问题

**解决方案**：
```bash
# Roamio 发送时必须包含时区信息
"start_time": "2025-11-15T14:00:00+08:00"  # ✅ 正确
"start_time": "2025-11-15T14:00:00"        # ❌ 错误

# Ralendar 接收时会正确处理时区
```

---

## 📊 **测试检查表**

### **部署前检查**
- [ ] Ralendar 代码已推送到 GitHub
- [ ] Ralendar 服务器已执行 git pull
- [ ] 数据库迁移已执行（0008_add_qq_unionid）
- [ ] uWSGI 已重启
- [ ] SECRET_KEY 双方一致

### **UnionID 测试**
- [ ] Ralendar 能获取 UnionID
- [ ] Roamio 能获取 UnionID
- [ ] 同一 QQ 账号的 UnionID 相同

### **Token 测试**
- [ ] Roamio Token 能调用 Ralendar API
- [ ] 返回 200（不是 401）
- [ ] 能看到用户数据

### **事件同步测试**
- [ ] Roamio 能创建测试旅行
- [ ] "添加到 Ralendar" 按钮可点击
- [ ] 同步过程有提示
- [ ] Ralendar 能看到同步的事件

### **数据验证**
- [ ] 事件标题正确
- [ ] 事件时间正确（无时区偏移）
- [ ] 事件地点正确
- [ ] source_app = 'roamio'
- [ ] related_trip_slug 正确

---

## 🎯 **成功标准**

### **最低标准（MVP）**：
1. ✅ 同一 QQ 账号在两边都能登录
2. ✅ UnionID 相同（用户识别正确）
3. ✅ Roamio 能调用 Ralendar API
4. ✅ 事件能从 Roamio 同步到 Ralendar

### **理想标准**：
5. ✅ 时间显示正确（无时区问题）
6. ✅ 地点信息完整（经纬度、地址）
7. ✅ 提醒功能正常
8. ✅ 前端 UI 友好（同步过程有反馈）

---

## 📅 **测试时间表**

| 时间 | 任务 | 负责方 |
|------|------|--------|
| **11:00-11:30** | 部署 Ralendar | Ralendar |
| **11:30-12:00** | UnionID 验证 | 双方 |
| **12:00-14:00** | 午休 | - |
| **14:00-14:30** | Token 互认测试 | 双方 |
| **14:30-15:30** | 事件同步测试 | 双方 |
| **15:30-16:00** | 问题修复 | 双方 |
| **16:00-16:30** | 完整流程验收 | 双方 |

---

## 📞 **联系方式**

### **Ralendar**
- QQ: 2064747320
- 服务器: app7626.acapp.acwing.com.cn (81.71.138.122)

### **Roamio**
- QQ: 2064747320
- 服务器: app7508.acapp.acwing.com.cn (47.121.137.60)

---

**准备开始测试！** 🚀

