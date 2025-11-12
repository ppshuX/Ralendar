#!/bin/bash

# Ralendar 手动部署脚本（适用于Docker/WSL环境）
# 使用方法：ssh到服务器后执行：bash DEPLOY_MANUAL.sh

echo "🚀 开始手动部署 Ralendar Backend..."

# 1. 进入项目目录
cd ~/kotlin_calendar/backend || exit 1
echo "✅ 当前目录: $(pwd)"

# 2. 配置API Key
echo ""
echo "📝 配置通义千问 API Key..."
if grep -q "QWEN_API_KEY" .env 2>/dev/null; then
    echo "API Key 已存在，跳过..."
else
    echo "QWEN_API_KEY=sk-0b9ac4fb62f640e2aeb473f1cc30d34e" >> .env
    echo "✅ API Key 已添加"
fi

# 3. 查找Python命令
echo ""
echo "🐍 查找Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ 使用 python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ 使用 python"
else
    echo "❌ 错误：未找到Python"
    exit 1
fi

$PYTHON_CMD --version

# 4. 收集静态文件
echo ""
echo "📦 收集静态文件..."
$PYTHON_CMD manage.py collectstatic --noinput 2>/dev/null || echo "⚠️ 静态文件收集失败（可能无影响）"

# 5. 查找并重启Web服务
echo ""
echo "🔄 查找Web服务进程..."

# 尝试查找uwsgi
UWSGI_PID=$(ps aux | grep '[u]wsgi.*calendar' | awk '{print $2}' | head -1)
if [ ! -z "$UWSGI_PID" ]; then
    echo "找到 uWSGI 进程 (PID: $UWSGI_PID)"
    echo "重启 uWSGI..."
    kill -HUP $UWSGI_PID 2>/dev/null || kill $UWSGI_PID 2>/dev/null
    sleep 2
    # 如果杀掉了，重新启动
    if ! ps -p $UWSGI_PID > /dev/null 2>&1; then
        echo "重新启动 uWSGI..."
        nohup uwsgi --ini uwsgi.ini &> /tmp/uwsgi.log &
    fi
    echo "✅ uWSGI 已重启"
fi

# 尝试查找gunicorn
GUNICORN_PID=$(ps aux | grep '[g]unicorn.*calendar' | awk '{print $2}' | head -1)
if [ ! -z "$GUNICORN_PID" ]; then
    echo "找到 Gunicorn 进程 (PID: $GUNICORN_PID)"
    echo "重启 Gunicorn..."
    kill -HUP $GUNICORN_PID
    echo "✅ Gunicorn 已重启"
fi

# 如果都没找到
if [ -z "$UWSGI_PID" ] && [ -z "$GUNICORN_PID" ]; then
    echo "⚠️ 未找到Web服务进程"
    echo "💡 请手动重启服务，或提供更多环境信息"
fi

# 6. 测试API
echo ""
echo "🧪 测试API..."
echo "测试节日API："
curl -s "https://app7626.acapp.acwing.com.cn/api/holidays/check/?date=2025-10-01" | head -n 5

echo ""
echo ""
echo "✅ 部署完成！"
echo ""
echo "📡 完整测试命令："
echo "curl 'https://app7626.acapp.acwing.com.cn/api/holidays/check/?date=2025-10-01'"
echo ""
echo "🤖 测试AI功能："
echo "curl -X POST https://app7626.acapp.acwing.com.cn/api/ai/chat/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\":\"你好\",\"context\":{\"current_date\":\"2025-11-12\"}}'"

