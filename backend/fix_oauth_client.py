#!/usr/bin/env python
"""修复 OAuth 客户端配置"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from api.models import OAuthClient

print("=" * 60)
print("修复 OAuth 客户端配置")
print("=" * 60)

# 查找所有 Roamio 客户端
clients = OAuthClient.objects.filter(client_name="Roamio")
print(f"\n找到 {clients.count()} 个 Roamio 客户端:\n")

for client in clients:
    print(f"Client ID: {client.client_id}")
    print(f"创建时间: {client.created_at}")
    print(f"是否激活: {client.is_active}")
    print("-" * 60)

# 检查是否有使用占位符 secret 的客户端
old_client = OAuthClient.objects.filter(client_id="ralendar_client_CJjjv6N9prR6JpDGmWijgA").first()
new_client = OAuthClient.objects.filter(client_id="ralendar_client_D5Dc11zm0eeCcWHb3UlswA").first()

if old_client and new_client:
    print("\n⚠️  发现两个客户端，建议操作：")
    print("\n选项 1：删除旧的客户端（如果 Roamio 可以更新配置）")
    print("   - 保留新的: ralendar_client_D5Dc11zm0eeCcWHb3UlswA")
    print("   - 删除旧的: ralendar_client_CJjjv6N9prR6JpDGmWijgA")
    
    print("\n选项 2：更新旧客户端的 secret（如果 Roamio 仍在使用旧的 client_id）")
    print("   - 需要知道正确的 client_secret")
    print("   - 然后删除新的客户端")
    
    print("\n当前建议：")
    print("如果 Roamio 可以更新配置，建议使用新的客户端 ID")
    print("Client ID: ralendar_client_D5Dc11zm0eeCcWHb3UlswA")
    print("Client Secret: 4i3TggBbCD1B8H959hwX12ifen218VfYRaEjiT8S7UY")
    
    # 询问是否删除旧的
    print("\n是否删除旧的客户端 (ralendar_client_CJjjv6N9prR6JpDGmWijgA)?")
    print("(如果 Roamio 可以更新配置，建议删除旧的)")
    
    # 注意：这里不能交互式输入，所以只是显示建议
    print("\n💡 手动操作：")
    print("在 Django shell 中执行：")
    print("  from api.models import OAuthClient")
    print("  old = OAuthClient.objects.get(client_id='ralendar_client_CJjjv6N9prR6JpDGmWijgA')")
    print("  old.delete()")
    print("  print('旧客户端已删除')")

