"""
用户中心相关路由
包括：用户统计、绑定管理、个人信息、密码修改
"""
from django.urls import path
from ..views import (
    get_user_stats,
    get_bindings,
    update_profile,
    change_password,
    unbind_acwing,
    unbind_qq,
)

urlpatterns = [
    # 用户统计
    path('stats/', get_user_stats, name='user_stats'),
    
    # 绑定管理
    path('bindings/', get_bindings, name='user_bindings'),
    path('unbind/acwing/', unbind_acwing, name='unbind_acwing'),
    path('unbind/qq/', unbind_qq, name='unbind_qq'),
    
    # 个人信息
    path('profile/', update_profile, name='update_profile'),
    path('change-password/', change_password, name='change_password'),
]

