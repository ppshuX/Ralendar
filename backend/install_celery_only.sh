#!/bin/bash
# 只安装 Celery 相关依赖（跳过已安装的包）

echo "=========================================="
echo "📦 安装 Celery 依赖（最小化安装）"
echo "=========================================="

# 只安装新增的包
pip3 install --user celery redis django-celery-beat --timeout=120

echo ""
echo "✅ 安装完成！"
echo ""
echo "验证安装："
pip3 list | grep -E "celery|redis"
echo ""
echo "下一步："
echo "python3 manage.py migrate"
echo "sudo pkill -f uwsgi && uwsgi --ini scripts/uwsgi.ini &"

