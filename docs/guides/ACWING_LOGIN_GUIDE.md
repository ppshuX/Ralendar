# AcWing 一键登录部署指南

**日期**: 2025-11-07  
**功能**: AcWing OAuth2 一键登录

---

## 🎯 功能概述

实现了 AcWing 平台的一键登录功能：
- ✅ 打开 acapp 自动检查登录状态
- ✅ 未登录自动弹出 AcWing 授权窗口
- ✅ 授权成功自动创建/登录账号
- ✅ 使用 JWT token 保持登录状态
- ✅ 自动关联用户的日程数据

---

## 📋 部署步骤

### 1. **后端部署**

#### 1.1 配置 AcWing 应用信息（重要！）

**⚠️ 安全警告**: 不要在代码中硬编码 Secret！

编辑 `backend/api/views.py`，将以下代码：

```python
ACWING_APPID = '7626'
ACWING_SECRET = 'ec47efb862a14b72ac1134e43b3edb9f'  # 需要替换为你的真实 Secret
```

**替换为环境变量方式**：

```python
import os
from django.conf import settings

ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
ACWING_SECRET = os.environ.get('ACWING_SECRET', '')  # 从环境变量读取
```

然后在服务器上设置环境变量：

```bash
# 在服务器的 .bashrc 或 .profile 中添加
export ACWING_SECRET="你的真实Secret"
```

或者在 `backend/calendar_backend/settings.py` 中添加：

```python
# AcWing 配置（从环境变量读取）
ACWING_APPID = '7626'
ACWING_SECRET = os.environ.get('ACWING_SECRET', '')
```

#### 1.2 执行数据库迁移

```bash
cd backend
python3 manage.py migrate
```

#### 1.3 重启后端服务

**使用 uWSGI**:

```bash
uwsgi --ini calendar_backend/uwsgi.ini
```

或者**开发模式**:

```bash
python3 manage.py runserver 0.0.0.0:8000
```

---

### 2. **前端部署**

#### 2.1 确认 AppID 配置

编辑 `acapp_frontend/src/main.js`，确认 AppID 正确：

```javascript
requestAcWingLogin() {
  const appid = '7626'  // 你的 AppID
  const redirect_uri = encodeURIComponent('https://app7626.acapp.acwing.com.cn/')
  // ...
}
```

#### 2.2 构建前端代码

```bash
cd acapp_frontend
npm run build
```

#### 2.3 上传到服务器

将生成的 `acapp/dist/` 目录下的文件上传到服务器的静态文件目录：

```bash
# 示例：使用 scp 上传
scp acapp/dist/* user@your-server:/path/to/acapp/
```

或者直接在 AcWing 平台的 "编辑 AcApp" 页面上传 `app.js` 和 `app.css`。

---

## 🧪 测试流程

### 1. **打开 AcWing App**

访问你的 AcWing App 页面（例如：https://www.acwing.com/file_system/file/content/whole/index/content/7626628/）

### 2. **观察控制台日志**

按 `F12` 打开浏览器开发者工具，查看控制台输出：

```
Calendar 构造函数被调用
未登录，发起 AcWing 授权...
调用 AcWing 授权 API...
AppID: 7626
Redirect URI: https://app7626.acapp.acwing.com.cn/
```

### 3. **授权流程**

- 应该会弹出 AcWing 授权窗口
- 点击"同意授权"
- 观察控制台日志：

```
AcWing 授权回调: {code: "xxx", state: "xxx"}
处理 AcWing 授权码: xxx
AcWing 登录成功: {username: "你的用户名", ...}
✅ AcWing 登录成功！
```

### 4. **验证登录状态**

- 刷新页面，不应该再弹出授权窗口
- 控制台应该显示：

```
已登录，Token: eyJ0eXAiOiJKV1QiLCJh...
```

### 5. **测试创建日程**

- 点击"添加日程"按钮
- 填写日程信息并保存
- 检查日程是否成功创建并关联到你的账号

---

## 🔍 常见问题

### 问题 1: 授权窗口不弹出

**原因**: `AcWingOS` 对象未正确传递

**解决**:
- 确认代码在 AcWing 平台上运行（不是本地开发环境）
- 检查 `Calendar` 构造函数是否接收到 `AcWingOS` 参数

### 问题 2: 授权成功但登录失败

**原因**: 后端 API 调用失败

**排查步骤**:
1. 检查后端日志：`tail -f /path/to/uwsgi.log`
2. 检查 Secret 是否正确配置
3. 测试后端 API：

```bash
curl -X POST https://app7626.acapp.acwing.com.cn/api/auth/acwing/login/ \
  -H "Content-Type: application/json" \
  -d '{"code": "测试授权码"}'
```

### 问题 3: Token 过期

**现象**: 一段时间后无法访问 API

**原因**: JWT token 过期（默认 5 分钟）

**解决**: 
- 前端应该实现 token 自动刷新机制（未来优化）
- 或者延长 token 有效期（在 `settings.py` 中修改 `ACCESS_TOKEN_LIFETIME`）

### 问题 4: 用户拒绝授权

**现象**: 用户点击"拒绝"

**处理**: 
- 代码已处理此情况，会切换到匿名模式
- 用户仍可查看公共日程，但不能创建/编辑自己的日程

---

## 📊 数据库变化

新增了 `api_acwinguser` 表：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| user_id | int | 关联 Django User |
| openid | varchar(100) | AcWing OpenID（唯一） |
| access_token | varchar(200) | AcWing 访问令牌 |
| refresh_token | varchar(200) | AcWing 刷新令牌 |
| photo_url | varchar(200) | 用户头像 URL |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

---

## 🔐 安全建议

### 1. **不要泄露 Secret**
- ❌ 不要提交到 Git
- ❌ 不要硬编码在代码中
- ✅ 使用环境变量
- ✅ 使用配置文件（加入 `.gitignore`）

### 2. **State 参数防 CSRF**
- ✅ 已实现随机 state 生成
- 🔄 未来可以验证 state 一致性

### 3. **HTTPS 传输**
- ✅ AcWing 平台强制 HTTPS
- ✅ 后端 API 使用 HTTPS

---

## 🎊 成功标志

如果看到以下输出，说明一切正常：

```
✅ 打开 acapp → 自动弹出授权窗口
✅ 点击授权 → 控制台显示"AcWing 登录成功"
✅ 刷新页面 → 不再弹出授权，显示"已登录"
✅ 创建日程 → 成功保存，关联到当前用户
✅ Web 端登录同一账号 → 可以看到 acapp 端创建的日程
```

---

## 📈 下一步优化

- [ ] Token 自动刷新机制
- [ ] 退出登录功能
- [ ] 显示用户头像和昵称
- [ ] 绑定已有账号功能
- [ ] OAuth2 安全加固（state 验证、PKCE 等）

---

**部署完成后，记得测试完整流程！** 🚀

