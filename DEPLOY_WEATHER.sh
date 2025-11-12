#!/bin/bash
# 天气功能部署脚本
# 使用方法：在云服务器上执行 bash DEPLOY_WEATHER.sh

echo "🚀 开始部署天气功能..."

# 进入项目目录
cd ~/kotlin_calendar/backend || exit 1

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin master

# 检查.env中是否已有QWEATHER_API_KEY
if grep -q "QWEATHER_API_KEY" .env; then
    echo "✅ .env中已有QWEATHER_API_KEY"
else
    echo "❌ .env中缺少QWEATHER_API_KEY，请手动添加！"
    echo ""
    echo "执行以下命令："
    echo "echo 'QWEATHER_API_KEY=fba41fcef20e47ddaf3efe73dfc77d4b' >> ~/kotlin_calendar/backend/.env"
    echo ""
fi

# 检查Django配置
echo "🔍 检查Django配置..."
python3 << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()
from django.conf import settings
key = getattr(settings, 'QWEATHER_API_KEY', '')
if key:
    print(f"✅ QWEATHER_API_KEY已加载: {key[:10]}...")
else:
    print("❌ QWEATHER_API_KEY未加载！")
EOF

# 重启uWSGI
echo "🔄 重启uWSGI服务..."
pkill -f uwsgi
sleep 2
uwsgi --ini scripts/uwsgi.ini --daemonize /tmp/uwsgi.log

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 测试天气API
echo "🌤️ 测试天气API..."
echo ""
echo "测试1：获取北京天气"
curl -s "https://app7626.acapp.acwing.com.cn/api/weather/?location=北京" | python3 -m json.tool

echo ""
echo "✅ 部署完成！"
echo ""
echo "📡 如果看到天气数据，说明部署成功！"
echo "❌ 如果看到500错误，请检查.env中的QWEATHER_API_KEY"

