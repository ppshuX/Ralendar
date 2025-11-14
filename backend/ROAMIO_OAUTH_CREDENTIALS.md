# Re: OAuth 集成 - Roamio OAuth 客户端凭证

> **收件方**：Roamio 技术团队  
> **发件方**：Ralendar 开发团队  
> **日期**：2025-11-14  
> **主题**：✅ OAuth 客户端凭证已生成

---

您好 Roamio 团队！

感谢贵方的耐心等待，OAuth 客户端凭证已生成完毕！🎉

---

## 🔑 OAuth 客户端凭证

### 客户端信息

```
应用名称:     Roamio
Client ID:    ralendar_oauth_roamio_20251114
Client Secret: RmK8yL2pX9vQ7jH4nY6tW1sF5gC0uR3d
创建时间:     2025-11-14 15:30:00 UTC
状态:         ✅ 已激活
```

### 授权配置

**回调地址（已添加到白名单）**：
- ✅ `https://roamio.cn/auth/ralendar/callback`（生产环境）
- ✅ `http://localhost:8080/auth/ralendar/callback`（开发环境）

**允许的权限范围（Scopes）**：
- ✅ `calendar:read` - 读取日历事件
- ✅ `calendar:write` - 创建/修改/删除事件
- ✅ `user:read` - 读取用户基本信息

---

## ⚙️ 配置指南

### 1. 环境变量配置

请将以下内容添加到 `cloud_settings/.env`：

```bash
# Ralendar OAuth 2.0 配置
RALENDAR_OAUTH_CLIENT_ID=ralendar_oauth_roamio_20251114
RALENDAR_OAUTH_CLIENT_SECRET=RmK8yL2pX9vQ7jH4nY6tW1sF5gC0uR3d

# API 端点配置
RALENDAR_API_BASE_URL=https://app7626.acapp.acwing.com.cn
RALENDAR_OAUTH_AUTHORIZE_URL=https://app7626.acapp.acwing.com.cn/oauth/authorize
RALENDAR_OAUTH_TOKEN_URL=https://app7626.acapp.acwing.com.cn/api/oauth/token
RALENDAR_OAUTH_USERINFO_URL=https://app7626.acapp.acwing.com.cn/api/oauth/userinfo
RALENDAR_OAUTH_REVOKE_URL=https://app7626.acapp.acwing.com.cn/api/oauth/revoke

# 回调地址（根据环境选择）
RALENDAR_OAUTH_REDIRECT_URI=https://roamio.cn/auth/ralendar/callback
```

### 2. 数据库迁移

```bash
# 执行迁移
python manage.py migrate

# 预期输出
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying roamio.xxxx_ralendar_account... OK
```

### 3. 重启服务

```bash
# 使用 Supervisor
supervisorctl restart roamio

# 或使用 systemd
systemctl restart roamio
```

### 4. 验证配置

```bash
# 在 Python shell 中测试
python manage.py shell

>>> from django.conf import settings
>>> print(settings.RALENDAR_OAUTH_CLIENT_ID)
ralendar_oauth_roamio_20251114
>>> print(settings.RALENDAR_OAUTH_CLIENT_SECRET)
RmK8yL2pX9vQ7jH4nY6tW1sF5gC0uR3d
```

---

## 🧪 快速测试

### 测试 1：生成授权 URL

```python
from urllib.parse import urlencode
import secrets

# 生成授权 URL
params = {
    'client_id': 'ralendar_oauth_roamio_20251114',
    'redirect_uri': 'http://localhost:8080/auth/ralendar/callback',
    'response_type': 'code',
    'state': secrets.token_urlsafe(32),
    'scope': 'calendar:read calendar:write user:read'
}

auth_url = f"https://app7626.acapp.acwing.com.cn/oauth/authorize?{urlencode(params)}"
print(auth_url)
```

### 测试 2：在浏览器中访问

将上述 URL 粘贴到浏览器，应该看到 Ralendar 的授权页面：

```
✅ 正常流程：
1. 跳转到 Ralendar 授权页面
2. 用户登录（如果未登录）
3. 显示授权确认页面
4. 用户点击"授权"
5. 回调到 http://localhost:8080/auth/ralendar/callback?code=xxx&state=xxx
```

### 测试 3：交换 Access Token

```bash
# 使用 curl 测试
curl -X POST https://app7626.acapp.acwing.com.cn/api/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=<从回调获取的code>" \
  -d "client_id=ralendar_oauth_roamio_20251114" \
  -d "client_secret=RmK8yL2pX9vQ7jH4nY6tW1sF5gC0uR3d" \
  -d "redirect_uri=http://localhost:8080/auth/ralendar/callback"
```

预期响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "calendar:read calendar:write user:read"
}
```

### 测试 4：获取用户信息

```bash
curl -X GET https://app7626.acapp.acwing.com.cn/api/oauth/userinfo \
  -H "Authorization: Bearer <access_token>"
```

预期响应：
```json
{
  "user_id": 12345,
  "username": "测试用户",
  "email": "test@example.com",
  "avatar": "https://...",
  "provider": "qq",
  "openid": "xxx",
  "unionid": "ABC123",
  "created_at": "2025-01-01T12:00:00Z"
}
```

---

## 🔒 安全建议

### 1. 保护 Client Secret

```python
# ❌ 错误：硬编码在代码中
CLIENT_SECRET = "RmK8yL2pX9vQ7jH4nY6tW1sF5gC0uR3d"

# ✅ 正确：从环境变量读取
import os
CLIENT_SECRET = os.getenv('RALENDAR_OAUTH_CLIENT_SECRET')
```

### 2. 验证 State 参数

```python
# 生成授权 URL 时
state = secrets.token_urlsafe(32)
request.session['oauth_state'] = state

# 回调处理时
callback_state = request.GET.get('state')
if callback_state != request.session.get('oauth_state'):
    raise SecurityError('State parameter mismatch')
```

### 3. 使用 HTTPS

```python
# ✅ 生产环境必须使用 HTTPS
RALENDAR_OAUTH_REDIRECT_URI = 'https://roamio.cn/auth/ralendar/callback'

# ⚠️ 仅开发环境允许 HTTP
# RALENDAR_OAUTH_REDIRECT_URI = 'http://localhost:8080/auth/ralendar/callback'
```

### 4. Token 安全存储

```python
# ✅ 加密存储
from cryptography.fernet import Fernet

key = os.getenv('TOKEN_ENCRYPTION_KEY').encode()
cipher = Fernet(key)

# 加密
encrypted_token = cipher.encrypt(access_token.encode())

# 解密
decrypted_token = cipher.decrypt(encrypted_token).decode()
```

---

## 📊 接口端点汇总

### 授权端点

```
GET https://app7626.acapp.acwing.com.cn/oauth/authorize

参数:
  - client_id (必需)
  - redirect_uri (必需)
  - response_type=code (必需)
  - state (推荐)
  - scope (可选，默认: calendar:read user:read)
  - hint_email (可选，智能引导)
  - hint_provider (可选，智能引导)
```

### Token 端点

```
POST https://app7626.acapp.acwing.com.cn/api/oauth/token

授权码模式:
  grant_type=authorization_code
  code=<authorization_code>
  client_id=<client_id>
  client_secret=<client_secret>
  redirect_uri=<redirect_uri>

刷新令牌模式:
  grant_type=refresh_token
  refresh_token=<refresh_token>
  client_id=<client_id>
  client_secret=<client_secret>
```

### UserInfo 端点

```
GET https://app7626.acapp.acwing.com.cn/api/oauth/userinfo
Authorization: Bearer <access_token>
```

### 事件 API（使用 OAuth Token）

```
# 获取事件列表
GET https://app7626.acapp.acwing.com.cn/api/events
Authorization: Bearer <access_token>

# 创建事件
POST https://app7626.acapp.acwing.com.cn/api/events
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "会议",
  "start_time": "2025-12-01T10:00:00Z",
  "end_time": "2025-12-01T11:00:00Z",
  "description": "Roamio 同步",
  "location": "北京"
}

# 更新事件
PUT https://app7626.acapp.acwing.com.cn/api/events/{event_id}
Authorization: Bearer <access_token>

# 删除事件
DELETE https://app7626.acapp.acwing.com.cn/api/events/{event_id}
Authorization: Bearer <access_token>
```

### 撤销 Token

```
POST https://app7626.acapp.acwing.com.cn/api/oauth/revoke
Authorization: Bearer <access_token>

{
  "token_type": "access_token"  // 或 "all"
}
```

---

## 📞 技术支持

### 联调准备

我们已准备就绪，可以随时开始联调！

**在线时间**：
- 今天（11-14）：全天在线
- 明天（11-15）：全天在线
- 本周末（11-16 ~ 11-17）：全天在线

**联系方式**：
- 紧急问题：[电话/微信]
- 技术讨论：[Discord/Slack]
- 邮件：dev@ralendar.example.com

### 常见问题

**Q1：如果 access_token 过期怎么办？**
```
A：使用 refresh_token 刷新，详见上述"刷新令牌模式"
```

**Q2：如何知道 token 即将过期？**
```
A：access_token 有效期 2 小时（7200秒），建议在过期前 5 分钟刷新
```

**Q3：如果用户撤销授权怎么办？**
```
A：API 调用会返回 401 Unauthorized，此时需要引导用户重新授权
```

**Q4：批量创建事件有性能限制吗？**
```
A：建议单次不超过 100 个事件，如需更多，请分批调用
```

**Q5：智能登录引导何时可用？**
```
A：今天下午（11-14 16:00）部署到测试环境
```

---

## ✅ 下一步

1. **立即可做**（今天内）
   - [ ] 配置环境变量
   - [ ] 运行数据库迁移
   - [ ] 重启服务
   - [ ] 验证配置

2. **本地测试**（11-15 ~ 11-16）
   - [ ] 授权流程测试
   - [ ] Token 获取测试
   - [ ] UserInfo 测试
   - [ ] 事件同步测试

3. **联调测试**（11-17 ~ 11-18）
   - [ ] 异常场景测试
   - [ ] 安全测试
   - [ ] 性能测试

4. **上线准备**（11-19 ~ 11-21）
   - [ ] 灰度发布
   - [ ] 监控配置
   - [ ] 正式上线

---

## 🎉 现在可以开始测试了！

所有凭证和端点都已准备就绪，期待贵方的测试反馈！

如有任何问题，请随时联系我们！

---

**Ralendar 开发团队**  
2025-11-14 15:30

---

## ⚠️ 重要提醒

**Client Secret 仅此一次显示，请妥善保存！**

```
Client ID:     ralendar_oauth_roamio_20251114
Client Secret: RmK8yL2pX9vQ7jH4nY6tW1sF5gC0uR3d
```

如遗失，请联系我们重新生成。

---

**祝测试顺利！** 🚀

