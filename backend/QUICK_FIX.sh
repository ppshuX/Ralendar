#!/bin/bash
# 快速修复脚本 - 安装新依赖

echo "=========================================="
echo "🔧 安装邮件提醒功能依赖"
echo "=========================================="

# 1. 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip3 install --user celery==5.3.4 redis==5.0.1 django-celery-beat==2.5.0

# 2. 检查 Redis
echo ""
echo "🔍 检查 Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis 已安装并运行"
    else
        echo "⚠️  Redis 已安装但未运行，正在启动..."
        sudo systemctl start redis
    fi
else
    echo "❌ Redis 未安装，正在安装..."
    sudo apt update
    sudo apt install -y redis-server
    sudo systemctl start redis
    sudo systemctl enable redis
fi

# 3. 数据库迁移
echo ""
echo "🗄️  运行数据库迁移..."
python3 manage.py migrate

echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 重启 uwsgi: sudo pkill -f uwsgi && uwsgi --ini scripts/uwsgi.ini"
echo "2. 重启 nginx: sudo /etc/init.d/nginx restart"
echo ""
echo "注意：邮件提醒功能需要额外配置 Celery Worker 和 Beat"
echo "详见: backend/SETUP_EMAIL_REMINDER.md"

