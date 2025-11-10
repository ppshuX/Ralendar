# 🗄️ Ralendar 多数据库配置指南

> **架构**: 部分共享 - 用户数据与 Roamio 共享，业务数据独立

---

## 🎯 架构说明

### **数据分布**

```
┌─────────────────────────────────────────────────────────┐
│         roamio_production (共享数据库)                   │
├─────────────────────────────────────────────────────────┤
│  ✅ auth_user              - Django 用户                │
│  ✅ auth_group             - 用户组                     │
│  ✅ allauth_socialaccount  - OAuth 账号（QQ/AcWing）    │
│  ✅ api_acwinguser         - AcWing 用户信息            │
│  ✅ api_qquser             - QQ 用户信息                │
│  ✅ api_usermapping        - Roamio-Ralendar 用户映射   │
│                                                         │
│  📦 roamio_*               - Roamio 的业务数据          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│        ralendar_production (Ralendar 独立数据库)         │
├─────────────────────────────────────────────────────────┤
│  📅 api_event              - 日程事件                   │
│  📅 api_publiccalendar     - 公共日历                   │
│  📅 calendar_holidays      - 节假日数据                 │
│  📅 calendar_lunar_calendars - 黄历数据                 │
│  📅 calendar_fortunes      - 运势数据                   │
│  📅 calendar_user_fortunes - 用户运势配置               │
│  📅 calendar_data_sync_logs - 数据同步日志              │
└─────────────────────────────────────────────────────────┘
```

### **为什么这样设计？**

1. **用户数据共享**：一个账号可以同时登录 Roamio 和 Ralendar
2. **业务数据隔离**：Ralendar 的事件、节假日等数据独立存储
3. **灵活扩展**：未来可以轻松迁移或拆分服务
4. **跨应用调用**：Roamio 通过 Fusion API + UnionID 访问 Ralendar 数据

---

## 🚀 操作步骤

### **第一步：SSH 连接服务器**

```bash
ssh acs@app7626.acapp.acwing.com.cn
```

---

### **第二步：创建 Ralendar 独立数据库**

```bash
# 登录 MySQL（使用 root 用户）
mysql -u root -p
```

**在 MySQL 中执行：**

```sql
-- 1. 创建 Ralendar 独立数据库
CREATE DATABASE ralendar_production 
  DEFAULT CHARACTER SET utf8mb4 
  DEFAULT COLLATE utf8mb4_unicode_ci;

-- 2. 授予 ralendar_user 访问权限
GRANT ALL PRIVILEGES ON ralendar_production.* TO 'ralendar_user'@'localhost';

-- 3. 刷新权限
FLUSH PRIVILEGES;

-- 4. 验证
SHOW DATABASES;

-- 5. 退出
EXIT;
```

**⚠️ 注意：不需要创建新用户，复用 roamio_production 的 ralendar_user**

---

### **第三步：测试数据库连接**

```bash
# 测试共享数据库
mysql -u ralendar_user -p roamio_production -e "SELECT COUNT(*) FROM auth_user;"

# 测试 Ralendar 独立数据库
mysql -u ralendar_user -p ralendar_production -e "SHOW TABLES;"
```

✅ **如果都能连接成功，继续下一步**

---

### **第四步：更新 .env 文件**

```bash
cd ~/kotlin_calendar/backend
vim .env
```

**完整配置（重要部分）：**

```bash
# ==================== Django Config ====================
DEBUG=False
SECRET_KEY=你的SECRET_KEY
ENVIRONMENT=production  # ← 启用生产环境

# ==================== Database Config (多数据库配置) ====================
# 共享数据库（与 Roamio 共享）：用户、OAuth 等
SHARED_DB_NAME=roamio_production
SHARED_DB_USER=ralendar_user
SHARED_DB_PASSWORD=你的数据库密码
SHARED_DB_HOST=localhost
SHARED_DB_PORT=3306

# Ralendar 独立数据库：事件、节假日、黄历、运势
RALENDAR_DB_NAME=ralendar_production
RALENDAR_DB_USER=ralendar_user
RALENDAR_DB_PASSWORD=你的数据库密码  # ← 可以与共享数据库相同
RALENDAR_DB_HOST=localhost
RALENDAR_DB_PORT=3306

# ... 其他配置 ...
```

**保存并退出：** `:wq`

---

### **第五步：运行数据库迁移**

```bash
cd ~/kotlin_calendar/backend

# 1. 生成迁移文件
python3 manage.py makemigrations

# 预期输出：
# Migrations for 'api':
#   api/migrations/0009_calendar_data_models.py
#     - Create model Holiday
#     - Create model LunarCalendar
#     - ...

# 2. 在 default 数据库执行迁移（共享数据）
python3 manage.py migrate --database=default

# 预期输出：
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, ...
# Running migrations:
#   No migrations to apply. (如果之前已迁移过)

# 3. 在 ralendar 数据库执行迁移（Ralendar 独立数据）
python3 manage.py migrate --database=ralendar

# 预期输出：
# Operations to perform:
#   Apply all migrations: api
# Running migrations:
#   Applying api.0009_calendar_data_models... OK
```

---

### **第六步：验证数据库表**

```bash
# 查看共享数据库（应该有用户表）
mysql -u ralendar_user -p roamio_production -e "SHOW TABLES LIKE 'auth%';"

# 预期输出：
# +-------------------------+
# | Tables_in_roamio        |
# +-------------------------+
# | auth_group              |
# | auth_user               |
# | ...                     |
# +-------------------------+

# 查看 Ralendar 独立数据库（应该有日历表）
mysql -u ralendar_user -p ralendar_production -e "SHOW TABLES;"

# 预期输出：
# +-------------------------------+
# | Tables_in_ralendar_production |
# +-------------------------------+
# | api_event                     |
# | api_publiccalendar            |
# | calendar_holidays             |
# | calendar_lunar_calendars      |
# | calendar_fortunes             |
# | calendar_user_fortunes        |
# | calendar_data_sync_logs       |
# +-------------------------------+
```

✅ **如果看到这些表，说明迁移成功！**

---

### **第七步：数据迁移（如果需要）**

**如果你之前的事件数据在 roamio_production：**

```sql
-- 方案 1：使用 MySQL 命令迁移数据
INSERT INTO ralendar_production.api_event 
SELECT * FROM roamio_production.api_event;

-- 方案 2：使用 Django 管理命令（推荐）
```

**或者使用 Python 脚本：**

```python
# 在 Django shell 中执行
python3 manage.py shell

from api.models import Event

# 查看当前事件数量
events_in_default = Event.objects.using('default').count()
events_in_ralendar = Event.objects.using('ralendar').count()

print(f"共享数据库事件数：{events_in_default}")
print(f"Ralendar数据库事件数：{events_in_ralendar}")

# 如果需要迁移（谨慎！）
# for event in Event.objects.using('default').all():
#     event.save(using='ralendar')
```

---

### **第八步：重启服务**

```bash
# 1. 重启 uWSGI
pkill -HUP uwsgi

# 2. 重启 Celery
pkill -f "celery -A calendar_backend"
cd ~/kotlin_calendar/backend
bash start_celery.sh
```

---

### **第九步：测试 Fusion API**

#### **测试场景：Roamio 用户调用 Ralendar API**

**1. 模拟 Roamio 发送请求：**

```bash
# 获取你的 JWT Token（先在 Ralendar 登录）
# 假设 token = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

curl -X POST "https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "unionid": "UID_YOUR_UNIONID",
    "title": "测试跨应用事件",
    "start_time": "2025-11-12T14:00:00Z",
    "description": "从 Roamio 创建的事件"
  }'
```

**2. 预期响应：**

```json
{
  "id": 123,
  "title": "测试跨应用事件",
  "start_time": "2025-11-12T14:00:00Z",
  "description": "从 Roamio 创建的事件",
  "source_app": "roamio",
  "created_at": "2025-11-10T10:00:00Z"
}
```

**3. 验证数据存储：**

```sql
-- 查看事件存储在哪个数据库
mysql -u ralendar_user -p ralendar_production

SELECT id, title, source_app, user_id FROM api_event ORDER BY id DESC LIMIT 5;

-- 预期看到刚创建的事件
-- +-----+------------------+------------+---------+
-- | id  | title            | source_app | user_id |
-- +-----+------------------+------------+---------+
-- | 123 | 测试跨应用事件   | roamio     | 2       |
-- +-----+------------------+------------+---------+
```

**4. 验证用户来自共享数据库：**

```sql
mysql -u ralendar_user -p roamio_production

SELECT id, username, email FROM auth_user WHERE id = 2;

-- 预期看到用户信息
-- +----+-----------+---------------------+
-- | id | username  | email               |
-- +----+-----------+---------------------+
-- | 2  | W ૧ H     | 2064747320@qq.com   |
-- +----+-----------+---------------------+
```

✅ **如果数据正确分布，说明多数据库配置成功！**

---

## 🎯 工作流程示意

### **场景：Roamio 用户创建日程**

```
1. Roamio 前端
   ↓ POST /api/v1/fusion/events/
   ↓ Header: Authorization: Bearer {token}
   ↓ Body: { unionid: "UID_123", title: "会议", ... }

2. Ralendar 后端 (fusion.py)
   ↓ 解析 Token，提取 unionid
   ↓ 从 roamio_production.allauth_socialaccount 查找用户
   ↓ 找到 user_id = 2

3. 创建事件
   ↓ Event.objects.create(user_id=2, title="会议", ...)
   ↓ 自动路由到 ralendar_production.api_event (通过 Router)

4. 返回响应
   ← { id: 123, title: "会议", user: { id: 2, username: "W ૧ H" } }
```

**关键点：**
- User 数据从 `roamio_production` 读取（共享）
- Event 数据写入 `ralendar_production`（独立）
- 通过 Django 的 Database Router 自动路由

---

## 🔍 故障排查

### **问题 1：找不到用户**

**错误：**
```
{"error": "用户未找到", "code": "USER_NOT_FOUND"}
```

**解决：**
1. 检查 `roamio_production` 是否有该用户
2. 检查 `allauth_socialaccount` 是否有 `unionid`
3. 确认 `.env` 中 `SHARED_DB_*` 配置正确

---

### **问题 2：事件写入失败**

**错误：**
```
django.db.utils.OperationalError: (1049, "Unknown database 'ralendar_production'")
```

**解决：**
1. 检查数据库是否已创建：
   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```
2. 检查 `.env` 中 `RALENDAR_DB_*` 配置

---

### **问题 3：迁移冲突**

**错误：**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**解决：**
1. 删除冲突的迁移记录：
   ```sql
   DELETE FROM django_migrations WHERE app='api' AND name='0009_calendar_data_models';
   ```
2. 重新运行迁移

---

## ✅ 验证清单

完成后，请确认：

- [ ] 两个数据库都已创建且可连接
- [ ] `.env` 文件已正确配置（2 组数据库配置）
- [ ] 迁移在两个数据库都执行成功
- [ ] `auth_user` 在 `roamio_production`
- [ ] `api_event` 在 `ralendar_production`
- [ ] Fusion API 测试成功（跨应用创建事件）
- [ ] 用户数据和事件数据正确分布

---

## 📊 数据一致性检查

```sql
-- 1. 检查用户数量一致性
-- 应该只在 roamio_production 有数据
SELECT COUNT(*) AS user_count FROM roamio_production.auth_user;

-- 2. 检查事件数量
-- 应该只在 ralendar_production 有数据（迁移后）
SELECT COUNT(*) AS event_count FROM ralendar_production.api_event;

-- 3. 检查外键关系
-- 事件的 user_id 应该对应 roamio_production 的用户
SELECT 
  e.id AS event_id,
  e.title,
  e.user_id,
  u.username
FROM ralendar_production.api_event e
LEFT JOIN roamio_production.auth_user u ON e.user_id = u.id
LIMIT 10;

-- 预期：所有事件都能找到对应用户
```

---

## 🔮 未来扩展

### **如果要完全独立（不共享用户）**

只需修改路由器，将 `user`, `socialaccount` 也加入 `ralendar_models`。

### **如果要添加更多共享数据**

在 `db_router.py` 的 `shared_models` 中添加即可。

---

## 📞 联系方式

**遇到问题？**
- 在项目根目录创建 Issue
- 或联系核心团队

---

**🎉 恭喜！Ralendar 多数据库架构已配置完成！**

**现在 Roamio 可以通过 Fusion API 调用 Ralendar 来创建日程了！** ✨

