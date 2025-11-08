#!/usr/bin/env python3
"""
邮件功能测试脚本
快速测试邮件配置是否正确
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

def test_email_config():
    """测试邮件配置"""
    print("=" * 60)
    print("📧 邮件配置测试")
    print("=" * 60)
    print()
    
    # 显示当前配置
    print("📋 当前配置：")
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # 获取测试收件人
    User = get_user_model()
    users_with_email = User.objects.exclude(email='').exclude(email__isnull=True)
    
    if not users_with_email.exists():
        print("⚠️  警告：数据库中没有用户设置了邮箱地址")
        print("   请先登录网站并在个人资料中设置邮箱")
        print()
        recipient = input("请输入测试邮箱地址（或按 Enter 跳过）: ").strip()
        if not recipient:
            print("❌ 测试取消")
            return
    else:
        user = users_with_email.first()
        recipient = user.email
        print(f"📬 测试收件人: {recipient} (用户: {user.username})")
        print()
    
    # 发送测试邮件
    print("📤 正在发送测试邮件...")
    try:
        send_mail(
            subject='Ralendar 邮件提醒测试',
            message='这是一封测试邮件。\n\n如果你收到这封邮件，说明邮件提醒功能配置成功！\n\n-- Ralendar 日历系统',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("✅ 邮件发送成功！")
        print()
        print(f"请检查 {recipient} 的收件箱（可能在垃圾邮件中）")
    except Exception as e:
        print(f"❌ 邮件发送失败：{str(e)}")
        print()
        print("🔧 常见问题：")
        print("  1. 检查邮箱密码/授权码是否正确")
        print("  2. Gmail 需要使用应用专用密码，不是邮箱密码")
        print("  3. 检查网络连接和防火墙设置")
        print("  4. 确认 .env 文件中的配置正确")

def test_celery_task():
    """测试 Celery 任务"""
    print()
    print("=" * 60)
    print("🔄 Celery 任务测试")
    print("=" * 60)
    print()
    
    try:
        from api.tasks import check_and_send_reminders
        from datetime import timedelta
        from django.utils import timezone
        from api.models import Event
        
        # 查找即将到来的事件
        now = timezone.now()
        upcoming_events = Event.objects.filter(
            start_time__gte=now,
            start_time__lte=now + timedelta(minutes=15),
            email_reminder=True,
            notification_sent=False,
        ).count()
        
        print(f"📊 未来 15 分钟内需要提醒的事件：{upcoming_events} 个")
        
        if upcoming_events > 0:
            print()
            print("💡 提示：如果 Celery Worker 和 Beat 正在运行，")
            print("   这些事件将在未来几分钟内自动发送邮件提醒")
        else:
            print()
            print("💡 提示：当前没有即将到来的事件")
            print("   可以创建一个 15 分钟后的测试事件来测试提醒功能")
        
        print()
        print("✅ Celery 任务模块加载成功")
        
    except Exception as e:
        print(f"❌ Celery 任务测试失败：{str(e)}")

if __name__ == '__main__':
    test_email_config()
    test_celery_task()
    
    print()
    print("=" * 60)
    print("📚 更多信息")
    print("=" * 60)
    print()
    print("📖 详细文档: backend/SETUP_EMAIL_REMINDER.md")
    print("🚀 启动 Celery: ./start_celery.sh")
    print("📊 查看日志: tail -f logs/celery_worker.log")
    print()

