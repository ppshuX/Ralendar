"""
合并QQ用户账号脚本
用于将新创建的账号（WqH_1）的数据合并到旧账号（WqH）
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import QQUser, Event, PublicCalendar, UserMapping

def merge_qq_users(old_username, new_username, unionid=None):
    """
    合并两个QQ用户账号
    
    Args:
        old_username: 旧账号用户名（要保留的账号）
        new_username: 新账号用户名（要合并的账号，合并后会被删除）
        unionid: 可选的UnionID，用于验证
    """
    try:
        # 1. 查找两个用户
        old_user = User.objects.get(username=old_username)
        new_user = User.objects.get(username=new_username)
        
        print(f"找到旧账号: {old_user.username} (ID: {old_user.id})")
        print(f"找到新账号: {new_user.username} (ID: {new_user.id})")
        
        # 2. 验证QQ用户信息
        old_qq_user = QQUser.objects.filter(user=old_user).first()
        new_qq_user = QQUser.objects.filter(user=new_user).first()
        
        if not old_qq_user:
            print(f"❌ 错误: 旧账号 {old_username} 没有关联的QQ用户信息")
            return False
        
        if not new_qq_user:
            print(f"❌ 错误: 新账号 {new_username} 没有关联的QQ用户信息")
            return False
        
        # 3. 验证UnionID（如果提供）
        if unionid:
            if old_qq_user.unionid and old_qq_user.unionid != unionid:
                print(f"⚠️  警告: 旧账号的UnionID ({old_qq_user.unionid}) 与提供的UnionID ({unionid}) 不匹配")
            if new_qq_user.unionid and new_qq_user.unionid != unionid:
                print(f"⚠️  警告: 新账号的UnionID ({new_qq_user.unionid}) 与提供的UnionID ({unionid}) 不匹配")
        
        print(f"\n旧账号QQ信息: openid={old_qq_user.openid}, unionid={old_qq_user.unionid or 'None'}")
        print(f"新账号QQ信息: openid={new_qq_user.openid}, unionid={new_qq_user.unionid or 'None'}")
        
        # 4. 确认操作
        print(f"\n⚠️  即将执行以下操作:")
        print(f"  1. 将新账号 ({new_username}) 的所有事件转移到旧账号 ({old_username})")
        print(f"  2. 将新账号的公开日历转移到旧账号")
        print(f"  3. 更新旧账号的QQ信息（使用新账号的最新信息）")
        print(f"  4. 删除新账号的QQ用户信息")
        print(f"  5. 删除新账号")
        
        confirm = input("\n确认执行合并操作? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return False
        
        # 5. 迁移事件
        events_count = Event.objects.filter(user=new_user).count()
        if events_count > 0:
            Event.objects.filter(user=new_user).update(user=old_user)
            print(f"✅ 已迁移 {events_count} 个事件到旧账号")
        else:
            print("ℹ️  新账号没有事件需要迁移")
        
        # 6. 迁移公开日历
        calendars_count = PublicCalendar.objects.filter(created_by=new_user).count()
        if calendars_count > 0:
            PublicCalendar.objects.filter(created_by=new_user).update(created_by=old_user)
            print(f"✅ 已迁移 {calendars_count} 个公开日历来旧账号")
        else:
            print("ℹ️  新账号没有公开日历需要迁移")
        
        # 7. 更新旧账号的QQ信息（使用新账号的最新信息）
        # 保留旧账号的unionid（如果存在），否则使用新账号的unionid
        if not old_qq_user.unionid and new_qq_user.unionid:
            old_qq_user.unionid = new_qq_user.unionid
            print(f"✅ 已更新旧账号的UnionID: {new_qq_user.unionid}")
        
        # 更新openid（使用最新的）
        if new_qq_user.openid:
            old_qq_user.openid = new_qq_user.openid
            print(f"✅ 已更新旧账号的OpenID: {new_qq_user.openid}")
        
        # 更新其他信息（如果有更新）
        if new_qq_user.photo_url and not old_qq_user.photo_url:
            old_qq_user.photo_url = new_qq_user.photo_url
        if new_qq_user.nickname and not old_qq_user.nickname:
            old_qq_user.nickname = new_qq_user.nickname
        
        old_qq_user.save()
        print("✅ 已更新旧账号的QQ用户信息")
        
        # 8. 迁移用户映射（如果有）
        new_mapping = UserMapping.objects.filter(ralendar_user=new_user).first()
        if new_mapping:
            # 检查旧账号是否已有映射
            old_mapping = UserMapping.objects.filter(ralendar_user=old_user).first()
            if old_mapping:
                print(f"⚠️  旧账号已有用户映射，跳过迁移")
            else:
                new_mapping.ralendar_user = old_user
                new_mapping.save()
                print("✅ 已迁移用户映射到旧账号")
        
        # 9. 删除新账号的QQ用户信息
        new_qq_user.delete()
        print("✅ 已删除新账号的QQ用户信息")
        
        # 10. 删除新账号
        new_user.delete()
        print("✅ 已删除新账号")
        
        print(f"\n🎉 合并完成！现在请使用旧账号 ({old_username}) 登录")
        return True
        
    except User.DoesNotExist as e:
        print(f"❌ 错误: 找不到用户 - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("QQ用户账号合并工具")
    print("=" * 60)
    print()
    
    # 从命令行参数获取用户名
    if len(sys.argv) >= 3:
        old_username = sys.argv[1]
        new_username = sys.argv[2]
        unionid = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        print("用法: python merge_qq_users.py <旧用户名> <新用户名> [unionid]")
        print()
        print("示例:")
        print("  python merge_qq_users.py WqH WqH_1")
        print("  python merge_qq_users.py WqH WqH_1 YOUR_UNIONID")
        print()
        
        # 交互式输入
        old_username = input("请输入旧账号用户名（要保留的账号，如 WqH）: ").strip()
        new_username = input("请输入新账号用户名（要合并的账号，如 WqH_1）: ").strip()
        unionid_input = input("请输入UnionID（可选，按Enter跳过）: ").strip()
        unionid = unionid_input if unionid_input else None
    
    if not old_username or not new_username:
        print("❌ 错误: 用户名不能为空")
        sys.exit(1)
    
    if old_username == new_username:
        print("❌ 错误: 旧用户名和新用户名不能相同")
        sys.exit(1)
    
    success = merge_qq_users(old_username, new_username, unionid)
    sys.exit(0 if success else 1)

