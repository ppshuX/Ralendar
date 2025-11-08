#!/bin/bash
# 后台启动 Celery Worker 和 Beat

echo "=========================================="
echo "🚀 启动 Celery 服务"
echo "=========================================="

# 创建日志目录
mkdir -p logs

# 停止已有的 Celery 进程
echo "🛑 停止现有的 Celery 进程..."
pkill -f "celery.*calendar_backend"
sleep 2

# 启动 Celery Worker
echo "📦 启动 Celery Worker..."
nohup celery -A calendar_backend worker --loglevel=info \
    > logs/celery_worker.log 2>&1 &
WORKER_PID=$!
echo "✅ Celery Worker 已启动 (PID: $WORKER_PID)"

# 等待 Worker 启动
sleep 3

# 启动 Celery Beat
echo "⏰ 启动 Celery Beat..."
nohup celery -A calendar_backend beat --loglevel=info \
    > logs/celery_beat.log 2>&1 &
BEAT_PID=$!
echo "✅ Celery Beat 已启动 (PID: $BEAT_PID)"

echo ""
echo "=========================================="
echo "✅ Celery 服务启动完成！"
echo "=========================================="
echo ""
echo "📊 查看日志："
echo "  Worker: tail -f logs/celery_worker.log"
echo "  Beat:   tail -f logs/celery_beat.log"
echo ""
echo "🛑 停止服务："
echo "  pkill -f 'celery.*calendar_backend'"
echo ""
echo "✅ 邮件提醒功能已激活！"
echo "   - 每分钟自动检查即将到来的事件"
echo "   - 提前 15 分钟发送邮件提醒"
echo ""

