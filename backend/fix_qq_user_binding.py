"""
修复QQ用户绑定脚本
将新账号（W ૧ H_1）的QQ登录信息关联到旧账号（W ૧ H）
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

def fix_qq_user_binding(old_username, new_username):
    """
    将新账号的QQ登录信息关联到旧账号
    
    Args:
        old_username: 旧账号用户名（要保留的账号）
        new_username: 新账号用户名（要删除的账号）
    """
    try:
        # 1. 查找两个用户
        old_user = User.objects.get(username=old_username)
        new_user = User.objects.get(username=new_username)
        
        print(f"找到旧账号: {old_user.username} (ID: {old_user.id})")
        print(f"找到新账号: {new_user.username} (ID: {new_user.id})")
        
        # 2. 检查QQ用户信息
        old_qq_user = QQUser.objects.filter(user=old_user).first()
        new_qq_user = QQUser.objects.filter(user=new_user).first()
        
        if old_qq_user:
            print(f"⚠️  警告: 旧账号 {old_username} 已有QQ登录信息")
            print(f"   OpenID: {old_qq_user.openid}")
            print(f"   UnionID: {old_qq_user.unionid or 'None'}")
            confirm = input("是否继续？这将覆盖旧账号的QQ信息 (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ 操作已取消")
                return False
        
        if not new_qq_user:
            print(f"❌ 错误: 新账号 {new_username} 没有QQ登录信息")
            return False
        
        print(f"\n新账号QQ信息:")
        print(f"   OpenID: {new_qq_user.openid}")
        print(f"   UnionID: {new_qq_user.unionid or 'None'}")
        print(f"   QQ昵称: {new_qq_user.nickname or 'None'}")
        
        # 3. 检查数据
        old_events_count = Event.objects.filter(user=old_user).count()
        new_events_count = Event.objects.filter(user=new_user).count()
        old_calendars_count = PublicCalendar.objects.filter(created_by=old_user).count()
        new_calendars_count = PublicCalendar.objects.filter(created_by=new_user).count()
        
        print(f"\n数据统计:")
        print(f"  旧账号事件: {old_events_count}")
        print(f"  新账号事件: {new_events_count}")
        print(f"  旧账号日历: {old_calendars_count}")
        print(f"  新账号日历: {new_calendars_count}")
        
        # 4. 确认操作
        print(f"\n⚠️  即将执行以下操作:")
        print(f"  1. 将新账号 ({new_username}) 的QQ登录信息关联到旧账号 ({old_username})")
        if new_events_count > 0:
            print(f"  2. 将新账号的 {new_events_count} 个事件转移到旧账号")
        if new_calendars_count > 0:
            print(f"  3. 将新账号的 {new_calendars_count} 个公开日历转移到旧账号")
        print(f"  4. 删除新账号的QQ用户信息")
        print(f"  5. 删除新账号")
        
        confirm = input("\n确认执行? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return False
        
        # 5. 迁移事件
        if new_events_count > 0:
            Event.objects.filter(user=new_user).update(user=old_user)
            print(f"✅ 已迁移 {new_events_count} 个事件到旧账号")
        
        # 6. 迁移公开日历
        if new_calendars_count > 0:
            PublicCalendar.objects.filter(created_by=new_user).update(created_by=old_user)
            print(f"✅ 已迁移 {new_calendars_count} 个公开日历来旧账号")
        
        # 7. 迁移用户映射（如果有）
        new_mapping = UserMapping.objects.filter(ralendar_user=new_user).first()
        if new_mapping:
            old_mapping = UserMapping.objects.filter(ralendar_user=old_user).first()
            if old_mapping:
                print(f"⚠️  旧账号已有用户映射，跳过迁移")
            else:
                new_mapping.ralendar_user = old_user
                new_mapping.save()
                print("✅ 已迁移用户映射到旧账号")
        
        # 8. 删除旧账号的QQ用户信息（如果存在）
        if old_qq_user:
            old_qq_user.delete()
            print("✅ 已删除旧账号的QQ用户信息")
        
        # 9. 将新账号的QQ用户信息关联到旧账号
        new_qq_user.user = old_user
        new_qq_user.save()
        print("✅ 已将QQ登录信息关联到旧账号")
        
        # 10. 删除新账号
        new_user.delete()
        print("✅ 已删除新账号")
        
        print(f"\n🎉 修复完成！现在请使用旧账号 ({old_username}) 登录")
        print(f"   旧账号现在有QQ登录信息:")
        print(f"     OpenID: {new_qq_user.openid}")
        print(f"     UnionID: {new_qq_user.unionid or 'None'}")
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
    print("修复QQ用户绑定工具")
    print("=" * 60)
    print()
    
    # 从命令行参数获取用户名
    if len(sys.argv) >= 3:
        old_username = sys.argv[1]
        new_username = sys.argv[2]
    else:
        print("用法: python fix_qq_user_binding.py <旧用户名> <新用户名>")
        print()
        print("示例:")
        print("  python fix_qq_user_binding.py 'W ૧ H' 'W ૧ H_1'")
        print()
        
        # 交互式输入
        old_username = input("请输入旧账号用户名（要保留的账号，如 'W ૧ H'）: ").strip()
        new_username = input("请输入新账号用户名（要删除的账号，如 'W ૧ H_1'）: ").strip()
    
    if not old_username or not new_username:
        print("❌ 错误: 用户名不能为空")
        sys.exit(1)
    
    if old_username == new_username:
        print("❌ 错误: 旧用户名和新用户名不能相同")
        sys.exit(1)
    
    success = fix_qq_user_binding(old_username, new_username)
    sys.exit(0 if success else 1)

