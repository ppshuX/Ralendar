"""
OAuth 2.0 相关路由
"""
from django.urls import path
from ..views import (
    oauth_authorize,
    oauth_token,
    oauth_userinfo,
    oauth_revoke,
    oauth_authorized_apps,
)
from ..views.oauth.login import (
    oauth_web_login,
    oauth_login_callback_acwing,
    oauth_login_callback_qq,
)

urlpatterns = [
    # 授权端点（用户授权页面）
    path('authorize', oauth_authorize, name='oauth_authorize'),
    
    # OAuth授权页面的登录（用于授权流程中的登录）
    path('login', oauth_web_login, name='oauth_web_login'),
    path('login/callback/acwing/', oauth_login_callback_acwing, name='oauth_login_callback_acwing'),
    # QQ回调：同时支持有斜杠和无斜杠，但实际使用无斜杠版本（QQ互联要求）
    path('login/callback/qq', oauth_login_callback_qq, name='oauth_login_callback_qq'),
    path('login/callback/qq/', oauth_login_callback_qq, name='oauth_login_callback_qq_slash'),  # 兼容性
    
    # Token 端点（获取/刷新访问令牌）
    path('token', oauth_token, name='oauth_token'),
    
    # UserInfo 端点（获取用户信息）
    path('userinfo', oauth_userinfo, name='oauth_userinfo'),
    
    # Token 撤销端点
    path('revoke', oauth_revoke, name='oauth_revoke'),
    
    # 已授权应用列表
    path('authorized-apps', oauth_authorized_apps, name='oauth_authorized_apps'),
]

