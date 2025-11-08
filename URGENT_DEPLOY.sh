#!/bin/bash
# 紧急部署脚本 - 更新服务器上的前端静态文件

echo "=========================================="
echo "🚀 紧急部署：更新前端静态文件"
echo "=========================================="

# 1. SSH 登录服务器并更新代码
ssh acs@app7626.acapp.acwing.com.cn << 'ENDSSH'
cd ~/kotlin_calendar

echo "📥 拉取最新代码..."
git pull

echo "📦 构建前端..."
cd web_frontend
npm run build

echo "✅ 前端文件已更新到 ../web/assets/"

cd ~/kotlin_calendar/backend
echo "🔄 重启服务..."
sudo pkill -f uwsgi
uwsgi --ini scripts/uwsgi.ini &
sudo /etc/init.d/nginx restart

echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "现在请："
echo "1. 强制刷新浏览器：Ctrl + Shift + R"
echo "2. 或清除浏览器缓存后刷新"
echo ""
ENDSSH

