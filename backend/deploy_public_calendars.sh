#!/bin/bash

# 部署公开日历订阅功能
# 用法：./deploy_public_calendars.sh

echo "🚀 部署公开日历订阅功能..."

# 1. 拉取最新代码
echo "📥 拉取代码..."
git pull

# 2. 初始化公开日历数据
echo "📅 初始化公开日历..."
python3 manage.py init_public_calendars

# 3. 重启服务
echo "🔄 重启服务..."
pkill -HUP uwsgi

echo "✅ 部署完成！"
echo ""
echo "📊 可用的订阅日历："
echo "  - china-holidays: 中国法定节假日 (7个)"
echo "  - lunar-festivals: 农历传统节日 (8个)"
echo "  - world-days: 国际纪念日 (10个)"
echo ""
echo "🧪 测试URL："
echo "  https://app7626.acapp.acwing.com.cn/api/calendars/china-holidays/feed/"

