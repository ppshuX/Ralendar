#!/bin/bash
# 邮件提醒功能分步配置脚本

echo "=========================================="
echo "📧 邮件提醒功能配置向导"
echo "=========================================="
echo ""

# 检查 Redis
echo "🔍 步骤 1: 检查 Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null 2>&1; then
        echo "✅ Redis 正在运行"
    else
        echo "⚠️  Redis 未运行，正在启动..."
        sudo systemctl start redis 2>/dev/null || sudo service redis-server start 2>/dev/null
        if redis-cli ping &> /dev/null 2>&1; then
            echo "✅ Redis 启动成功"
        else
            echo "❌ Redis 启动失败，请手动安装：sudo apt install redis-server"
            exit 1
        fi
    fi
else
    echo "❌ Redis 未安装"
    read -p "是否现在安装? (y/n): " install_redis
    if [ "$install_redis" = "y" ]; then
        sudo apt update
        sudo apt install -y redis-server
        sudo systemctl start redis
        sudo systemctl enable redis
        echo "✅ Redis 安装完成"
    else
        echo "邮件提醒功能需要 Redis，安装后再运行此脚本"
        exit 1
    fi
fi

echo ""
echo "🗄️  步骤 2: 数据库迁移..."
python3 manage.py migrate
echo "✅ 数据库迁移完成"

echo ""
echo "=========================================="
echo "📝 步骤 3: 配置邮箱 SMTP"
echo "=========================================="
echo ""
echo "请选择邮箱服务商："
echo "1) Gmail（推荐）"
echo "2) QQ邮箱"
echo "3) 163邮箱"
echo "4) 跳过（稍后手动配置）"
read -p "请选择 (1-4): " email_choice

case $email_choice in
    1)
        echo ""
        echo "📧 Gmail 配置"
        echo "----------------------------------------"
        echo "⚠️  重要：需要使用 Gmail 应用专用密码，不是邮箱密码！"
        echo ""
        echo "获取应用专用密码的步骤："
        echo "1. 访问: https://myaccount.google.com/security"
        echo "2. 开启"两步验证""
        echo "3. 搜索"应用专用密码""
        echo "4. 选择"邮件"和"其他（自定义名称）""
        echo "5. 生成 16 位密码"
        echo ""
        read -p "请输入你的 Gmail 地址: " gmail_user
        read -sp "请输入应用专用密码（16位）: " gmail_pass
        echo ""
        
        # 创建或更新 .env 文件
        cat >> .env << EOF

# ==================== 邮件配置 (Gmail) ====================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$gmail_user
EMAIL_HOST_PASSWORD=$gmail_pass
DEFAULT_FROM_EMAIL=$gmail_user

# ==================== Celery/Redis 配置 ====================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ==================== 提醒设置 ====================
REMINDER_ADVANCE_MINUTES=15
EOF
        echo "✅ Gmail 配置已写入 .env 文件"
        ;;
    2)
        echo ""
        echo "📧 QQ邮箱 配置"
        echo "----------------------------------------"
        echo "⚠️  需要使用 QQ邮箱授权码，不是QQ密码！"
        echo ""
        echo "获取授权码的步骤："
        echo "1. 登录 QQ邮箱网页版"
        echo "2. 设置 → 账户 → POP3/SMTP服务"
        echo "3. 开启服务，获取授权码"
        echo ""
        read -p "请输入你的 QQ邮箱地址: " qq_user
        read -sp "请输入授权码: " qq_pass
        echo ""
        
        cat >> .env << EOF

# ==================== 邮件配置 (QQ邮箱) ====================
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$qq_user
EMAIL_HOST_PASSWORD=$qq_pass
DEFAULT_FROM_EMAIL=$qq_user

# ==================== Celery/Redis 配置 ====================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ==================== 提醒设置 ====================
REMINDER_ADVANCE_MINUTES=15
EOF
        echo "✅ QQ邮箱 配置已写入 .env 文件"
        ;;
    3)
        echo ""
        echo "📧 163邮箱 配置"
        echo "----------------------------------------"
        echo "⚠️  需要使用 163邮箱授权码，不是邮箱密码！"
        echo ""
        read -p "请输入你的 163邮箱地址: " email_163_user
        read -sp "请输入授权码: " email_163_pass
        echo ""
        
        cat >> .env << EOF

# ==================== 邮件配置 (163邮箱) ====================
EMAIL_HOST=smtp.163.com
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=$email_163_user
EMAIL_HOST_PASSWORD=$email_163_pass
DEFAULT_FROM_EMAIL=$email_163_user

# ==================== Celery/Redis 配置 ====================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ==================== 提醒设置 ====================
REMINDER_ADVANCE_MINUTES=15
EOF
        echo "✅ 163邮箱 配置已写入 .env 文件"
        ;;
    4)
        echo "⚠️  跳过邮箱配置，请稍后手动编辑 .env 文件"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ 配置完成！"
echo "=========================================="
echo ""
echo "📋 下一步："
echo ""
echo "1. 测试邮件配置："
echo "   python3 manage.py shell"
echo "   >>> from django.core.mail import send_mail"
echo "   >>> send_mail('测试', '这是一封测试邮件', 'from@example.com', ['to@example.com'])"
echo ""
echo "2. 启动 Celery Worker (新终端):"
echo "   cd ~/kotlin_calendar/backend"
echo "   celery -A calendar_backend worker --loglevel=info"
echo ""
echo "3. 启动 Celery Beat (新终端):"
echo "   cd ~/kotlin_calendar/backend"
echo "   celery -A calendar_backend beat --loglevel=info"
echo ""
echo "或者使用后台启动脚本（推荐）："
echo "   ./start_celery.sh"
echo ""

