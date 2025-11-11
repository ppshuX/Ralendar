#!/bin/bash

# 部署 JSON API 到服务器
# 使用方法：ssh到服务器后执行：bash deploy_json_api.sh

echo "🚀 开始部署 JSON Events API..."

# 1. 进入项目目录
cd ~/Ralendar || exit 1

# 2. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin master

# 3. 激活虚拟环境
echo "🐍 激活虚拟环境..."
source venv/bin/activate

# 4. 进入后端目录
cd backend || exit 1

# 5. 收集静态文件（如果需要）
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput

# 6. 重启服务
echo "🔄 重启 Gunicorn 服务..."
sudo systemctl restart gunicorn

# 7. 检查服务状态
echo "✅ 检查服务状态..."
sudo systemctl status gunicorn --no-pager | head -n 10

echo ""
echo "✅ 部署完成！"
echo ""
echo "📡 测试 API："
echo "curl https://app7626.acapp.acwing.com.cn/api/calendars/china-holidays/events-json/"
echo ""
echo "🔍 查看日志："
echo "tail -f /var/log/gunicorn/error.log"

