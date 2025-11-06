# API 测试指南

快速测试 Django 后端 API

---

## 🧪 测试步骤

### 1. 启动服务器

```bash
cd backend
python manage.py runserver
```

访问：http://localhost:8000/api/

---

### 2. 测试日程 API

#### 获取所有日程（GET）

```bash
curl http://localhost:8000/api/events/
```

预期返回：

```json
[]  # 初始为空
```

---

#### 创建日程（POST）

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "团队会议",
    "description": "讨论项目进度",
    "date_time": "2025-11-06T14:00:00",
    "reminder_minutes": 15
  }'
```

预期返回：

```json
{
    "id": 1,
    "title": "团队会议",
    "description": "讨论项目进度",
    "date_time": "2025-11-06T14:00:00",
    "reminder_minutes": 15,
    "created_at": "2025-11-05T10:30:00.123456",
    "updated_at": "2025-11-05T10:30:00.123456"
}
```

---

#### 获取单个日程（GET）

```bash
curl http://localhost:8000/api/events/1/
```

---

#### 更新日程（PUT）

```bash
curl -X PUT http://localhost:8000/api/events/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "团队会议（已延期）",
    "description": "改为明天",
    "date_time": "2025-11-07T14:00:00",
    "reminder_minutes": 30
  }'
```

---

#### 删除日程（DELETE）

```bash
curl -X DELETE http://localhost:8000/api/events/1/
```

---

### 3. 测试农历 API

#### 公历转农历

```bash
curl "http://localhost:8000/api/lunar/?date=2025-11-05"
```

预期返回：

```json
{
    "lunar_date": "农历2025年十月初六",
    "year": 2025,
    "month": "十月",
    "day": "初六",
    "zodiac": "蛇",
    "solar_date": "2025-11-05"
}
```

---

#### 测试不同日期

```bash
# 春节
curl "http://localhost:8000/api/lunar/?date=2025-01-29"

# 中秋节
curl "http://localhost:8000/api/lunar/?date=2025-10-06"
```

---

### 4. 测试公开日历订阅（需要先创建数据）

#### 在 Django Admin 创建公开日历

1. 访问：http://localhost:8000/admin/
2. 创建超级用户：`python manage.py createsuperuser`
3. 登录后创建 PublicCalendar
4. 添加一些事件

#### 获取公开日历列表

```bash
curl http://localhost:8000/api/calendars/
```

#### 获取日历订阅

```bash
curl http://localhost:8000/api/calendars/china-holidays/feed/
```

预期返回：

```json
{
    "ics": "BEGIN:VCALENDAR\nVERSION:2.0\n...",
    "events_count": 11
}
```

---

## 🌐 浏览器测试

直接在浏览器访问：

1. **API 浏览器**：http://localhost:8000/api/
2. **日程列表**：http://localhost:8000/api/events/
3. **农历转换**：http://localhost:8000/api/lunar/?date=2025-11-05
4. **Admin 后台**：http://localhost:8000/admin/

Django REST Framework 提供了友好的网页界面，可以直接操作 API！

---

## 📱 Android 测试

### 1. 修改 Android 代码中的 BASE_URL

```kotlin
// api/RetrofitClient.kt
private const val BASE_URL = "http://10.0.2.2:8000/api/"  // 模拟器
// 或
private const val BASE_URL = "http://你的电脑IP:8000/api/"  // 真机
```

### 2. 在 AndroidManifest.xml 添加网络权限

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### 3. 测试订阅功能

点击"订阅网络日历"按钮，应该能从后端获取数据。

---

## ✅ 测试检查清单

- [ ] 启动服务器成功
- [ ] 访问 http://localhost:8000/api/ 看到 API 列表
- [ ] 创建日程成功
- [ ] 获取日程列表成功
- [ ] 更新日程成功
- [ ] 删除日程成功
- [ ] 农历转换正常
- [ ] 公开日历订阅正常
- [ ] Admin 后台可访问

---

## 🐛 常见问题

### 1. CORS 错误

如果从前端访问遇到 CORS 错误，检查 `settings.py` 中的配置：

```python
CORS_ALLOW_ALL_ORIGINS = True
```

### 2. 数据库未迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. 端口被占用

```bash
# 使用其他端口
python manage.py runserver 8001
```

---

**测试完成后，Django 后端就可以部署到云服务器了！** 🚀

