# 🚀 Ralendar 部署检查清单

> **部署时间**: 2025-11-09 上午  
> **状态**: 🔄 进行中

---

## ✅ **部署前确认**

### **代码状态**
- [x] UnionID 功能已实现
- [x] Fusion API 已实现
- [x] 数据库迁移文件已创建（0008_add_qq_unionid.py）
- [x] 时间轴视图已实现
- [x] 登录权限功能已实现
- [x] 所有代码已推送到 GitHub

### **配置检查**
- [x] SECRET_KEY 与 Roamio 一致
- [x] QQ OAuth 配置正确
- [x] API 端点已准备就绪

---

## 📋 **部署步骤**

### **Step 1: 登录服务器**
```bash
ssh acs@app7626.acapp.acwing.com.cn
```

### **Step 2: 更新代码**
```bash
cd ~/kotlin_calendar
git pull
```

### **Step 3: 执行数据库迁移**
```bash
cd backend
source venv/bin/activate
python manage.py migrate
```

### **Step 4: 检查迁移结果**
```bash
python manage.py showmigrations api
```

### **Step 5: 重启 uWSGI**
```bash
pkill -f uwsgi
uwsgi --ini uwsgi.ini &
```

### **Step 6: 验证服务状态**
```bash
ps aux | grep uwsgi
tail -f ~/kotlin_calendar/backend/logs/django.log
```

---

## 🧪 **部署后验证**

### **1. API 可用性**
```bash
curl -X GET https://app7626.acapp.acwing.com.cn/api/v1/events/
```

### **2. UnionID 字段**
```bash
python manage.py shell
>>> from api.models import QQUser
>>> QQUser.objects.filter(unionid__isnull=False).count()
```

### **3. Fusion API**
```bash
curl -X GET https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/trip/test-trip/
```

---

## ✅ **完成标志**

- [ ] 代码已更新
- [ ] 数据库迁移成功
- [ ] uWSGI 已重启
- [ ] API 端点可访问
- [ ] 准备好联调测试

