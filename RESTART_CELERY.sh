#!/bin/bash

# ====================================
# 🔄 重启 Celery 服务脚本
# ====================================

echo "======================================"
echo "🔄 重启 Celery 服务"
echo "======================================"
echo ""

cd ~/kotlin_calendar/backend

# 1. 停止所有 Celery 进程
echo "===== 1. 停止旧的 Celery 进程 ====="
echo ""
sudo pkill -f 'celery worker'
sudo pkill -f 'celery beat'
sleep 2

# 检查是否还有进程
if ps aux | grep -v grep | grep 'celery' > /dev/null; then
    echo "⚠️ 仍有 Celery 进程在运行，强制终止..."
    sudo pkill -9 -f 'celery'
    sleep 1
fi

echo "✅ 旧进程已清理"
echo ""

# 2. 创建日志目录
echo "===== 2. 准备日志目录 ====="
mkdir -p logs
echo "✅ 日志目录准备完毕"
echo ""

# 3. 启动 Celery Worker
echo "===== 3. 启动 Celery Worker ====="
nohup python3 -m celery -A calendar_backend worker --loglevel=info > logs/celery_worker.log 2>&1 &
WORKER_PID=$!
echo "✅ Celery Worker 已启动 (PID: $WORKER_PID)"
echo ""

# 4. 启动 Celery Beat
echo "===== 4. 启动 Celery Beat ====="
nohup python3 -m celery -A calendar_backend beat --loglevel=info > logs/celery_beat.log 2>&1 &
BEAT_PID=$!
echo "✅ Celery Beat 已启动 (PID: $BEAT_PID)"
echo ""

# 5. 等待2秒后检查进程状态
sleep 2

echo "===== 5. 验证服务状态 ====="
echo ""

if ps -p $WORKER_PID > /dev/null; then
    echo "✅ Celery Worker 正在运行 (PID: $WORKER_PID)"
else
    echo "❌ Celery Worker 启动失败！请检查日志: logs/celery_worker.log"
fi

if ps -p $BEAT_PID > /dev/null; then
    echo "✅ Celery Beat 正在运行 (PID: $BEAT_PID)"
else
    echo "❌ Celery Beat 启动失败！请检查日志: logs/celery_beat.log"
fi

echo ""
echo "======================================"
echo "🎉 Celery 服务重启完成"
echo "======================================"
echo ""
echo "💡 查看实时日志："
echo "   Worker: tail -f ~/kotlin_calendar/backend/logs/celery_worker.log"
echo "   Beat:   tail -f ~/kotlin_calendar/backend/logs/celery_beat.log"
echo ""
echo "💡 手动测试提醒功能："
echo "   cd ~/kotlin_calendar/backend"
echo "   python3 MANUAL_TEST_REMINDER.py"
echo ""
echo "======================================"

