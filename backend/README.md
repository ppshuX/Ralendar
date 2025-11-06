# KotlinCalendar Backend API

Django REST Framework 后端服务

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

### 启动服务器

```bash
python manage.py runserver
```

服务器地址：http://localhost:8000

---

## 📡 API 接口

### 基础 URL

```
http://localhost:8000/api/
```

### 日程管理

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/events/` | 获取所有日程 |
| POST | `/api/events/` | 创建日程 |
| GET | `/api/events/{id}/` | 获取单个日程 |
| PUT | `/api/events/{id}/` | 更新日程 |
| PATCH | `/api/events/{id}/` | 部分更新日程 |
| DELETE | `/api/events/{id}/` | 删除日程 |

**创建日程示例：**

```json
POST /api/events/
{
    "title": "团队会议",
    "description": "讨论项目进度",
    "date_time": "2025-11-06T14:00:00",
    "reminder_minutes": 15
}
```

**响应示例：**

```json
{
    "id": 1,
    "title": "团队会议",
    "description": "讨论项目进度",
    "date_time": "2025-11-06T14:00:00",
    "reminder_minutes": 15,
    "created_at": "2025-11-05T10:30:00",
    "updated_at": "2025-11-05T10:30:00"
}
```

---

### 网络日历订阅

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/calendars/` | 获取公开日历列表 |
| GET | `/api/calendars/{slug}/` | 获取单个日历详情 |
| GET | `/api/calendars/{slug}/feed/` | 获取日历订阅（iCalendar格式） |

**订阅示例：**

```bash
GET /api/calendars/china-holidays/feed/
```

**响应示例：**

```json
{
    "ics": "BEGIN:VCALENDAR\nVERSION:2.0\n...",
    "events_count": 11
}
```

---

### 农历转换

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/lunar/?date=YYYY-MM-DD` | 公历转农历 |

**请求示例：**

```bash
GET /api/lunar/?date=2025-11-05
```

**响应示例：**

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

## 📊 Admin 后台

访问：http://localhost:8000/admin/

使用超级用户账号登录后可以：
- 管理日程
- 创建公开日历
- 查看用户

---

## 🔧 配置说明

### CORS 配置

开发环境已允许所有源访问，生产环境需要在 `settings.py` 中配置：

```python
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
]
```

### 数据库配置

默认使用 SQLite，生产环境可切换为 PostgreSQL：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'calendar_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 🎯 API 测试

### 使用 curl

```bash
# 获取所有日程
curl http://localhost:8000/api/events/

# 创建日程
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"title":"测试日程","date_time":"2025-11-06T15:00:00"}'

# 获取农历
curl http://localhost:8000/api/lunar/?date=2025-11-05
```

### 使用 Postman / Insomnia

导入 API 集合或直接访问：
```
http://localhost:8000/api/
```

Django REST Framework 提供了可视化 API 浏览器！

---

## 📦 部署

### 使用 Gunicorn

```bash
gunicorn calendar_backend.wsgi:application --bind 0.0.0.0:8000
```

### 使用 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/static/;
    }
}
```

---

## 🏗️ 项目结构

```
backend/
├── api/
│   ├── models.py          # 数据模型
│   ├── serializers.py     # 序列化器
│   ├── views.py           # API 视图
│   └── urls.py            # API 路由
├── calendar_backend/
│   ├── settings.py        # 配置文件
│   └── urls.py            # 主路由
├── manage.py
└── requirements.txt
```

---

## ✅ 功能清单

- [x] 日程 CRUD API
- [x] 网络日历订阅
- [x] 农历转换
- [x] CORS 跨域支持
- [x] Django Admin 管理后台
- [ ] 用户认证（JWT）
- [ ] 权限控制
- [ ] 数据缓存
- [ ] 定时任务

---

**开发者**: KotlinCalendar Team  
**技术栈**: Django 5.0 + Django REST Framework 3.15  
**License**: MIT

