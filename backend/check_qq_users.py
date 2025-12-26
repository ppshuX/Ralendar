"""
检查QQ用户账号脚本
用于查看数据库中的QQ用户信息
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import QQUser, Event

def check_qq_users():
    """检查所有QQ用户"""
    print("=" * 60)
    print("QQ用户账号检查")
    print("=" * 60)
    print()
    
    # 获取所有QQ用户
    qq_users = QQUser.objects.all().select_related('user')
    
    if not qq_users.exists():
        print("❌ 数据库中没有QQ用户")
        return
    
    print(f"找到 {qq_users.count()} 个QQ用户:\n")
    
    for qq_user in qq_users:
        user = qq_user.user
        events_count = Event.objects.filter(user=user).count()
        
        print(f"用户名: {user.username}")
        print(f"  用户ID: {user.id}")
        print(f"  邮箱: {user.email or '未设置'}")
        print(f"  OpenID: {qq_user.openid}")
        print(f"  UnionID: {qq_user.unionid or '未设置'}")
        print(f"  QQ昵称: {qq_user.nickname or '未设置'}")
        print(f"  事件数量: {events_count}")
        print(f"  创建时间: {qq_user.created_at}")
        print()
    
    # 检查是否有重复的用户名
    print("=" * 60)
    print("检查重复用户名:")
    print("=" * 60)
    
    from collections import Counter
    usernames = [qq.user.username for qq in qq_users]
    username_counts = Counter(usernames)
    
    duplicates = {name: count for name, count in username_counts.items() if count > 1}
    if duplicates:
        print("⚠️  发现重复的用户名:")
        for name, count in duplicates.items():
            print(f"  {name}: {count} 个账号")
    else:
        print("✅ 没有重复的用户名")
    
    # 检查是否有相似的用户名（可能是重复账号）
    print()
    print("=" * 60)
    print("检查可能的重复账号（用户名相似）:")
    print("=" * 60)
    
    username_list = sorted(usernames)
    for i, name1 in enumerate(username_list):
        for name2 in username_list[i+1:]:
            # 检查是否是 name 和 name_1 这样的模式
            if name1 == name2.rsplit('_', 1)[0] or name2 == name1.rsplit('_', 1)[0]:
                print(f"⚠️  可能的重复账号:")
                print(f"  - {name1}")
                print(f"  - {name2}")
                print()

if __name__ == '__main__':
    check_qq_users()

