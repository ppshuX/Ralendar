# 📧 邮件提醒功能部署指南

> **创建日期**: 2025-11-08  
> **版本**: v1.0  
> **状态**: ✅ 已完成开发，待测试部署

---

## 📋 目录

1. [功能概述](#功能概述)
2. [技术架构](#技术架构)
3. [安装依赖](#安装依赖)
4. [配置说明](#配置说明)
5. [部署步骤](#部署步骤)
6. [测试指南](#测试指南)
7. [常见问题](#常见问题)

---

## 🎯 功能概述

### 核心功能

- ✅ **自动提醒**：事件开始前自动发送邮件提醒
- ✅ **精美模板**：HTML 格式邮件，美观易读
- ✅ **智能过滤**：只提醒启用了邮件功能且未发送的事件
- ✅ **地图集成**：邮件中包含地图导航链接
- ✅ **异步处理**：使用 Celery 异步发送，不阻塞主线程
- ✅ **定时检查**：每分钟自动检查即将到来的事件

### 使用场景

1. 📅 **日常日程提醒**：会议、约会、生日等
2. ✈️ **Roamio 旅行提醒**：旅行计划中的重要事件
3. 🗺️ **带地点的事件**：自动附带地图导航链接

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                   Django Application                    │
│  ┌──────────────┐         ┌──────────────┐            │
│  │  Event Model │────────▶│  Celery Beat │            │
│  │  (数据库)     │         │  (定时任务)   │            │
│  └──────────────┘         └──────┬───────┘            │
│                                   │                     │
│                           每分钟触发                     │
│                                   │                     │
│                          ┌────────▼────────┐           │
│                          │ check_reminders │           │
│                          │   (检查任务)     │           │
│                          └────────┬────────┘           │
│                                   │                     │
│                          创建异步任务                     │
│                                   │                     │
│  ┌───────────────────────────────▼─────────┐          │
│  │         Celery Worker                    │          │
│  │  ┌──────────────────────────────────┐   │          │
│  │  │  send_event_reminder_email()     │   │          │
│  │  │  - 构建邮件内容                   │   │          │
│  │  │  - 发送 SMTP 邮件                │   │          │
│  │  │  - 标记 notification_sent        │   │          │
│  │  └──────────────────────────────────┘   │          │
│  └──────────────────┬────────────────────────          │
└────────────────────┼───────────────────────────────────┘
                     │
             ┌───────▼────────┐
             │  Redis Broker  │
             │  (消息队列)     │
             └────────────────┘
                     │
             ┌───────▼────────┐
             │  SMTP Server   │
             │  (邮件服务器)   │
             └────────────────┘
                     │
                     ▼
               📧 用户邮箱
```

---

## 📦 安装依赖

### 1. Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

新增的依赖：
```
celery==5.3.4
redis==5.0.1
django-celery-beat==2.5.0
```

### 2. Redis 安装

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**验证 Redis:**
```bash
redis-cli ping
# 输出: PONG
```

---

## ⚙️ 配置说明

### 1. 环境变量配置

复制示例文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下内容：

```bash
# ==================== 邮件配置 ====================
# 选择邮件服务商（Gmail/163/QQ）

# Gmail（推荐）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password  # ⚠️ 不是邮箱密码！
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 提醒设置
REMINDER_ADVANCE_MINUTES=15  # 提前 15 分钟提醒
```

### 2. Gmail 应用专用密码

⚠️ **重要**：Gmail 不能直接使用邮箱密码，需要生成应用专用密码！

**步骤**：
1. 访问 https://myaccount.google.com/security
2. 开启"两步验证"
3. 搜索"应用专用密码"
4. 选择"邮件"和"其他（自定义名称）"
5. 生成 16 位密码
6. 将密码填入 `EMAIL_HOST_PASSWORD`

### 3. 数据库迁移

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

这会创建 Celery Beat 所需的数据库表。

---

## 🚀 部署步骤

### 方案 A：开发环境（简单测试）

**启动 Redis:**
```bash
sudo systemctl start redis
```

**启动 Django:**
```bash
python manage.py runserver 0.0.0.0:8000
```

**启动 Celery Worker（新终端）:**
```bash
celery -A calendar_backend worker --loglevel=info
```

**启动 Celery Beat（新终端）:**
```bash
celery -A calendar_backend beat --loglevel=info
```

---

### 方案 B：生产环境（推荐）

#### 1. 创建 Celery 启动脚本

**`backend/start_celery_worker.sh`:**
```bash
#!/bin/bash
cd "$(dirname "$0")"
celery -A calendar_backend worker --loglevel=info --logfile=logs/celery_worker.log
```

**`backend/start_celery_beat.sh`:**
```bash
#!/bin/bash
cd "$(dirname "$0")"
celery -A calendar_backend beat --loglevel=info --logfile=logs/celery_beat.log
```

授予执行权限：
```bash
chmod +x start_celery_worker.sh start_celery_beat.sh
```

#### 2. 使用 Supervisor 管理进程

安装 Supervisor：
```bash
sudo apt install supervisor
```

创建配置文件：`/etc/supervisor/conf.d/ralendar_celery.conf`
```ini
[program:ralendar_celery_worker]
command=/path/to/backend/start_celery_worker.sh
directory=/path/to/backend
user=your-username
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/path/to/backend/logs/celery_worker_err.log
stdout_logfile=/path/to/backend/logs/celery_worker_out.log

[program:ralendar_celery_beat]
command=/path/to/backend/start_celery_beat.sh
directory=/path/to/backend
user=your-username
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/path/to/backend/logs/celery_beat_err.log
stdout_logfile=/path/to/backend/logs/celery_beat_out.log
```

启动服务：
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ralendar_celery_worker
sudo supervisorctl start ralendar_celery_beat
```

查看状态：
```bash
sudo supervisorctl status
```

---

## 🧪 测试指南

### 1. 手动测试单个邮件

进入 Django Shell：
```bash
python manage.py shell
```

执行测试：
```python
from api.tasks import send_event_reminder_email
from api.models import Event

# 获取一个事件
event = Event.objects.first()
print(f"测试事件: {event.title}")
print(f"用户邮箱: {event.user.email}")

# 发送测试邮件
result = send_event_reminder_email.delay(event.id)
print(f"任务 ID: {result.id}")

# 查看任务结果
result.get()  # 等待任务完成
```

### 2. 测试定时检查任务

```python
from api.tasks import check_and_send_reminders
from datetime import timedelta
from django.utils import timezone

# 创建一个即将开始的测试事件
from api.models import Event
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

event = Event.objects.create(
    user=user,
    title="测试提醒事件",
    start_time=timezone.now() + timedelta(minutes=10),
    end_time=timezone.now() + timedelta(minutes=60),
    email_reminder=True,  # ✅ 启用邮件提醒
    notification_sent=False,
)

# 手动触发检查
count = check_and_send_reminders.delay()
print(f"发现 {count.get()} 个需要提醒的事件")
```

### 3. 检查 Celery 日志

```bash
# Worker 日志
tail -f logs/celery_worker.log

# Beat 日志
tail -f logs/celery_beat.log
```

---

## ❓ 常见问题

### Q1: 邮件发送失败："Authentication failed"

**原因**：邮箱密码错误或未开启 SMTP 服务

**解决**：
- Gmail: 使用应用专用密码，不是邮箱密码
- 163/QQ: 使用授权码，在邮箱设置中开启 SMTP 并获取

---

### Q2: Celery Worker 无法启动

**检查 Redis 是否运行**：
```bash
redis-cli ping
```

**检查 Redis 连接**：
```python
python manage.py shell
>>> import redis
>>> r = redis.Redis(host='localhost', port=6379, db=0)
>>> r.ping()
True
```

---

### Q3: 没有收到提醒邮件

**检查清单**：
1. ✅ 用户邮箱已设置
2. ✅ Event.email_reminder = True
3. ✅ Event.notification_sent = False
4. ✅ start_time 在未来 15 分钟内
5. ✅ Celery Beat 正在运行
6. ✅ Celery Worker 正在运行
7. ✅ 邮件配置正确

**调试命令**：
```bash
# 检查即将提醒的事件
python manage.py shell
>>> from api.models import Event
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> now = timezone.now()
>>> Event.objects.filter(
...     start_time__gte=now,
...     start_time__lte=now + timedelta(minutes=15),
...     email_reminder=True,
...     notification_sent=False
... ).values('title', 'start_time', 'user__email')
```

---

### Q4: 如何修改提醒时间？

编辑 `.env` 文件：
```bash
REMINDER_ADVANCE_MINUTES=30  # 改为提前 30 分钟
```

重启 Celery：
```bash
sudo supervisorctl restart ralendar_celery_beat
```

---

## 📊 监控和维护

### 1. 查看任务执行情况

```bash
# 进入 Django Shell
python manage.py shell

# 查看 Celery Beat 定时任务
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.all()

# 查看已发送的提醒
>>> from api.models import Event
>>> Event.objects.filter(notification_sent=True).count()
```

### 2. 清理旧数据

定期清理已完成的事件：
```bash
python manage.py shell
>>> from api.models import Event
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> old_date = timezone.now() - timedelta(days=30)
>>> Event.objects.filter(
...     end_time__lt=old_date,
...     notification_sent=True
... ).delete()
```

---

## 🎉 完成检查清单

部署完成后，确认以下内容：

- [ ] Redis 正常运行
- [ ] Celery Worker 正常运行
- [ ] Celery Beat 正常运行
- [ ] 邮件配置正确（发送测试邮件）
- [ ] 环境变量已设置
- [ ] 数据库已迁移
- [ ] Supervisor 配置完成（生产环境）
- [ ] 日志文件可写
- [ ] 防火墙允许 SMTP 端口（587/465）

---

## 📞 技术支持

如有问题，请查看：
- 📖 [Django Email 文档](https://docs.djangoproject.com/en/4.2/topics/email/)
- 🔧 [Celery 文档](https://docs.celeryq.dev/)
- 🗄️ [Redis 文档](https://redis.io/docs/)

---

**祝你部署顺利！** 🚀

