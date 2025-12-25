#!/usr/bin/env python
"""检查 OAuth 客户端配置"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from api.models import OAuthClient

print("=" * 60)
print("OAuth 客户端配置检查")
print("=" * 60)

clients = OAuthClient.objects.all()
print(f"\n总共有 {clients.count()} 个 OAuth 客户端:\n")

for client in clients:
    print(f"客户端名称: {client.client_name}")
    print(f"Client ID: {client.client_id}")
    print(f"是否激活: {client.is_active}")
    print(f"Redirect URIs: {client.redirect_uris}")
    print(f"Allowed Scopes: {client.allowed_scopes}")
    print(f"创建时间: {client.created_at}")
    print("-" * 60)

if clients.count() == 0:
    print("\n⚠️  警告: 没有配置任何 OAuth 客户端！")
    print("需要创建一个 OAuth 客户端才能使用 OAuth 授权功能。")

