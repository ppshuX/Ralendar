"""
检查所有用户账号脚本
用于查看数据库中的所有用户信息
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import QQUser, AcWingUser, Event

def check_all_users():
    """检查所有用户"""
    print("=" * 60)
    print("所有用户账号检查")
    print("=" * 60)
    print()
    
    # 获取所有用户
    all_users = User.objects.all().order_by('id')
    
    if not all_users.exists():
        print("❌ 数据库中没有用户")
        return
    
    print(f"找到 {all_users.count()} 个用户:\n")
    
    for user in all_users:
        events_count = Event.objects.filter(user=user).count()
        qq_user = QQUser.objects.filter(user=user).first()
        acwing_user = AcWingUser.objects.filter(user=user).first()
        
        print(f"用户ID: {user.id}")
        print(f"  用户名: {user.username}")
        print(f"  邮箱: {user.email or '未设置'}")
        print(f"  注册时间: {user.date_joined}")
        print(f"  事件数量: {events_count}")
        
        if qq_user:
            print(f"  QQ登录: ✅")
            print(f"    OpenID: {qq_user.openid}")
            print(f"    UnionID: {qq_user.unionid or '未设置'}")
            print(f"    QQ昵称: {qq_user.nickname or '未设置'}")
        else:
            print(f"  QQ登录: ❌")
        
        if acwing_user:
            print(f"  AcWing登录: ✅")
            print(f"    OpenID: {acwing_user.openid}")
        else:
            print(f"  AcWing登录: ❌")
        
        print()
    
    # 检查是否有用户名相似的用户
    print("=" * 60)
    print("检查用户名相似的用户（可能的重复账号）:")
    print("=" * 60)
    
    usernames = [user.username for user in all_users]
    for i, name1 in enumerate(usernames):
        for name2 in usernames[i+1:]:
            # 检查是否是 name 和 name_1 这样的模式
            base1 = name1.rsplit('_', 1)[0] if '_' in name1 else name1
            base2 = name2.rsplit('_', 1)[0] if '_' in name2 else name2
            
            if base1 == base2 and name1 != name2:
                print(f"⚠️  可能的重复账号:")
                print(f"  - {name1}")
                print(f"  - {name2}")
                print()

if __name__ == '__main__':
    check_all_users()

