#!/bin/bash

# ====================================
# 📧 邮件提醒系统诊断脚本
# ====================================

echo "======================================"
echo "📧 Ralendar 邮件提醒系统诊断"
echo "======================================"
echo ""

cd ~/kotlin_calendar/backend

echo "===== 1. 检查 Celery 进程 ====="
echo ""
echo "🔍 Celery Worker 进程："
ps aux | grep 'celery worker' | grep -v grep
if [ $? -eq 0 ]; then
    echo "✅ Celery Worker 正在运行"
else
    echo "❌ Celery Worker 未运行！"
fi
echo ""

echo "🔍 Celery Beat 进程："
ps aux | grep 'celery beat' | grep -v grep
if [ $? -eq 0 ]; then
    echo "✅ Celery Beat 正在运行"
else
    echo "❌ Celery Beat 未运行！这是导致提醒失败的主要原因！"
fi
echo ""

echo "===== 2. 检查 Redis 连接 ====="
echo ""
redis-cli ping
if [ $? -eq 0 ]; then
    echo "✅ Redis 正常运行"
else
    echo "❌ Redis 未运行或无法连接！"
fi
echo ""

echo "===== 3. 检查环境变量 ====="
echo ""
if [ -f ".env" ]; then
    echo "✅ .env 文件存在"
    echo ""
    echo "📧 邮件配置："
    grep "USE_REAL_EMAIL" .env
    grep "EMAIL_HOST=" .env
    grep "EMAIL_PORT=" .env
    grep "EMAIL_HOST_USER=" .env
    echo ""
else
    echo "❌ .env 文件不存在！"
fi
echo ""

echo "===== 4. 检查 Celery Beat 定时任务 ====="
echo ""
echo "🔍 查询 Django 中注册的定时任务："
python3 manage.py shell << 'PYEOF'
from django_celery_beat.models import PeriodicTask
tasks = PeriodicTask.objects.all()
print(f"定时任务总数: {tasks.count()}")
for task in tasks:
    print(f"  - {task.name}: {task.task} (启用: {task.enabled}, 间隔: {task.interval})")
PYEOF
echo ""

echo "===== 5. 检查最近的 Celery 日志 ====="
echo ""
if [ -f "logs/celery.log" ]; then
    echo "🔍 Celery 最近的日志（最后20行）："
    tail -n 20 logs/celery.log
    echo ""
else
    echo "❌ 找不到 logs/celery.log"
fi
echo ""

if [ -f "logs/celery_worker.log" ]; then
    echo "🔍 Celery Worker 最近的日志（最后20行）："
    tail -n 20 logs/celery_worker.log
    echo ""
else
    echo "❌ 找不到 logs/celery_worker.log"
fi
echo ""

if [ -f "logs/celery_beat.log" ]; then
    echo "🔍 Celery Beat 最近的日志（最后20行）："
    tail -n 20 logs/celery_beat.log
    echo ""
else
    echo "❌ 找不到 logs/celery_beat.log"
fi
echo ""

echo "===== 6. 测试邮件发送 ====="
echo ""
echo "🔍 尝试手动发送测试邮件："
python3 << 'PYEOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

try:
    send_mail(
        subject='Ralendar 测试邮件',
        message='这是一封测试邮件，用于验证邮件配置是否正确。',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['2064747320@qq.com'],  # 你的邮箱
        fail_silently=False,
    )
    print("✅ 测试邮件发送成功！请检查邮箱收件箱（可能在垃圾邮件中）。")
except Exception as e:
    print(f"❌ 测试邮件发送失败: {e}")
PYEOF
echo ""

echo "===== 7. 查询需要发送提醒的事件 ====="
echo ""
python3 manage.py shell << 'PYEOF'
from api.models import Event
from django.utils import timezone
from datetime import timedelta

now = timezone.now()
upcoming = now + timedelta(minutes=15)

events = Event.objects.filter(
    start_time__gte=now,
    start_time__lte=upcoming,
    email_reminder=True,
    email_sent=False
)

print(f"未来15分钟内需要发送提醒的事件数: {events.count()}")
for event in events:
    print(f"  - [{event.id}] {event.title}")
    print(f"    开始时间: {event.start_time}")
    print(f"    提前提醒: {event.reminder_minutes}分钟")
    print(f"    用户邮箱: {event.user.email}")
    print(f"    邮件已发送: {event.email_sent}")
    print("")
PYEOF
echo ""

echo "======================================"
echo "🔧 诊断完成"
echo "======================================"
echo ""
echo "💡 常见问题修复："
echo "   1. 如果 Celery Beat 未运行，执行："
echo "      cd ~/kotlin_calendar/backend && bash start_celery.sh"
echo ""
echo "   2. 如果定时任务未注册，执行："
echo "      cd ~/kotlin_calendar/backend"
echo "      python3 manage.py shell -c \"from api.tasks import setup_periodic_tasks; setup_periodic_tasks()\""
echo ""
echo "   3. 查看实时日志："
echo "      tail -f ~/kotlin_calendar/backend/logs/celery_worker.log"
echo ""
echo "======================================"

