#!/bin/bash
# 🚀 Ralendar 快速部署脚本
# 用于部署 UnionID 和 Fusion API 功能

echo "🚀 开始部署 Ralendar..."
echo ""

# 1. 更新代码
echo "📦 Step 1: 拉取最新代码..."
cd ~/kotlin_calendar
git pull
echo "✅ 代码已更新"
echo ""

# 2. 激活虚拟环境
echo "🐍 Step 2: 激活虚拟环境..."
source backend/venv/bin/activate
cd backend
echo "✅ 虚拟环境已激活"
echo ""

# 3. 执行数据库迁移
echo "🗄️  Step 3: 执行数据库迁移..."
python manage.py migrate
echo "✅ 数据库迁移完成"
echo ""

# 4. 检查迁移状态
echo "🔍 Step 4: 检查迁移状态..."
python manage.py showmigrations api | grep "0008_add_qq_unionid"
echo ""

# 5. 重启 uWSGI
echo "🔄 Step 5: 重启 uWSGI..."
pkill -f uwsgi
sleep 2
uwsgi --ini uwsgi.ini &
sleep 3
echo "✅ uWSGI 已重启"
echo ""

# 6. 检查服务状态
echo "✅ Step 6: 检查服务状态..."
ps aux | grep uwsgi | grep -v grep
echo ""

# 7. 验证 API
echo "🧪 Step 7: 验证 API..."
curl -s -o /dev/null -w "API Status: %{http_code}\n" https://app7626.acapp.acwing.com.cn/api/v1/events/
echo ""

echo "🎉 部署完成！"
echo ""
echo "📋 接下来："
echo "1. 测试 QQ 登录和 UnionID"
echo "2. 通知 Roamio 团队开始联调"
echo "3. 按照他们的测试指南进行测试"
echo ""

