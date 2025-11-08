"""
认证相关路由
包括：用户注册、登录、AcWing OAuth、QQ OAuth
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ..views import (
    register,
    get_current_user,
    acwing_login,
    get_acwing_login_url,
    acwing_oauth_callback,
    qq_login,
    get_qq_login_url,
)

urlpatterns = [
    # 基础认证
    path('register/', register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', get_current_user, name='current_user'),
    
    # AcWing OAuth2 登录
    path('acwing/login/', get_acwing_login_url, name='get_acwing_login_url'),
    path('acwing/callback/', acwing_login, name='acwing_login'),
    
    # QQ OAuth2 登录
    path('qq/login/', get_qq_login_url, name='get_qq_login_url'),
    path('qq/callback/', qq_login, name='qq_login'),
]

