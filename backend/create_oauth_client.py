#!/usr/bin/env python
"""创建 OAuth 客户端"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from api.models import OAuthClient

print("=" * 60)
print("创建 OAuth 客户端")
print("=" * 60)

# 检查是否已存在 Roamio 客户端
existing_client = OAuthClient.objects.filter(client_name="Roamio").first()
if existing_client:
    print(f"\n⚠️  Roamio 客户端已存在:")
    print(f"Client ID: {existing_client.client_id}")
    print(f"是否激活: {existing_client.is_active}")
    print(f"Redirect URIs: {existing_client.redirect_uris}")
    print(f"Allowed Scopes: {existing_client.allowed_scopes}")
    print("\n如果需要更新配置，请使用 Django shell 手动修改。")
else:
    # 生成客户端凭证
    client_id, client_secret = OAuthClient.generate_client_credentials()
    
    # 创建客户端
    client = OAuthClient.objects.create(
        client_name="Roamio",
        client_description="Roamio 旅行规划平台",
        redirect_uris=[
            "https://roamio.cn/auth/ralendar/callback",
            "http://localhost:8080/auth/ralendar/callback"
        ],
        allowed_scopes=["calendar:read", "calendar:write", "user:read"],
        is_active=True
    )
    client.set_secret(client_secret)
    client.save()
    
    print(f"\n✅ OAuth 客户端创建成功！")
    print(f"\n客户端信息:")
    print(f"  名称: {client.client_name}")
    print(f"  Client ID: {client.client_id}")
    print(f"  Client Secret: {client_secret}")
    print(f"  Redirect URIs: {client.redirect_uris}")
    print(f"  Allowed Scopes: {client.allowed_scopes}")
    print(f"\n⚠️  重要: 请保存 Client Secret，它只会显示一次！")
    print(f"    Client Secret: {client_secret}")

