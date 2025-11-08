#!/usr/bin/env python3
"""
手动测试邮件提醒功能
使用方法：
    cd ~/kotlin_calendar/backend
    python3 MANUAL_TEST_REMINDER.py
"""

import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from api.models import Event
from api.tasks import check_and_send_reminders, send_event_reminder_email
from django.contrib.auth.models import User

print("=" * 60)
print("📧 手动测试邮件提醒功能")
print("=" * 60)
print()

# 1. 检查当前用户信息
print("===== 1. 检查用户邮箱 =====")
user = User.objects.first()
if user:
    print(f"用户名: {user.username}")
    print(f"邮箱: {user.email if user.email else '❌ 未设置邮箱！'}")
    print()
else:
    print("❌ 没有找到用户！")
    exit(1)

# 2. 查询即将到来的事件
print("===== 2. 查询需要提醒的事件 =====")
now = timezone.now()
future_15min = now + timedelta(minutes=15)

events = Event.objects.filter(
    start_time__gte=now,
    start_time__lte=future_15min,
    email_reminder=True,
    notification_sent=False,
)

print(f"未来15分钟内需要提醒的事件数: {events.count()}")
for event in events:
    print(f"  - [{event.id}] {event.title}")
    print(f"    开始时间: {timezone.localtime(event.start_time)}")
    print(f"    提前提醒: {event.reminder_minutes}分钟")
    print(f"    用户: {event.user.username} ({event.user.email})")
    print(f"    已发送: {event.notification_sent}")
    print()

# 3. 手动触发检查任务
print("===== 3. 手动触发检查任务 =====")
try:
    count = check_and_send_reminders()
    print(f"✅ 检查任务执行成功，处理了 {count} 个事件")
except Exception as e:
    print(f"❌ 检查任务执行失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 4. 如果有事件但未发送，手动发送一个测试
if events.count() > 0:
    test_event = events.first()
    print(f"===== 4. 手动发送测试邮件（事件: {test_event.title}）=====")
    try:
        result = send_event_reminder_email(test_event.id)
        if result:
            print(f"✅ 邮件发送成功！请检查邮箱: {test_event.user.email}")
        else:
            print(f"❌ 邮件发送失败")
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 60)
print("测试完成")
print("=" * 60)

