# 📧 发送给 Roamio 团队的 OAuth 集成问题说明

## 主题
Ralendar OAuth 集成：授权流程已成功，需要修复 token 交换端点

---

## 邮件正文

### 主题行（建议）
```
【重要】Ralendar OAuth 集成：授权流程已成功，需要修复 token 交换实现
```

### 邮件内容

**亲爱的 Roamio 团队：**

你们好！

我们在测试 Ralendar 和 Roamio 的 OAuth 集成时，发现授权流程已经成功完成，但 Roamio 端在处理授权码换取 token 时遇到了问题。

## ✅ 已成功的部分

1. **授权流程正常**：用户点击"连接 Ralendar"后，成功跳转到 Ralendar 授权页面
2. **用户登录成功**：QQ 登录流程正常，用户成功登录到 Ralendar
3. **授权页面显示**：授权页面正确显示，用户可以看到权限列表
4. **授权码返回**：用户点击"授权"后，成功返回 Roamio，URL 中包含 `code=xxx&state=xxx`

## ❌ 当前问题

在 Roamio 收到授权码后，尝试调用以下端点时失败：
```
POST https://roamio.cn/api/v1/ralendar-oauth/callback/
```

**错误信息：**
```
获取用户信息失败: 用户信息请求失败: 500
```

**问题分析：** Roamio 端实现了一个自定义的回调端点，但这个端点应该调用 Ralendar 的标准 OAuth 端点来换取 token 和获取用户信息。

## 📋 正确的 OAuth 2.0 流程

根据 OAuth 2.0 标准，正确的流程应该是：

### 步骤 1：用户授权（已完成 ✅）
```
GET /oauth/authorize?client_id=xxx&redirect_uri=xxx&response_type=code&state=xxx
→ 返回授权码到 redirect_uri?code=xxx&state=xxx
```

### 步骤 2：用授权码换取 access_token（需要修复 ⚠️）
```
POST https://app7626.acapp.acwing.com.cn/oauth/token
Content-Type: application/json

{
  "grant_type": "authorization_code",
  "code": "授权码（从步骤 1 的 URL 参数中获取）",
  "client_id": "ralendar_client_CJjjv6N9prR6JpDGmWijgA",
  "client_secret": "客户端密钥（请联系我们获取）",
  "redirect_uri": "https://roamio.cn/auth/ralendar/callback"
}
```

**成功响应：**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "scope": "calendar:read calendar:write user:read"
}
```

### 步骤 3：用 access_token 获取用户信息
```
GET https://app7626.acapp.acwing.com.cn/oauth/userinfo
Authorization: Bearer {access_token}
```

**成功响应：**
```json
{
  "user_id": 123,
  "username": "W_q_H",
  "email": "user@example.com",
  "provider": "qq",
  "openid": "xxx",
  "unionid": "xxx",
  "avatar": "https://...",
  "created_at": "2025-01-01T00:00:00Z"
}
```

## 🔧 需要修改的内容

1. **删除或修改 `/api/v1/ralendar-oauth/callback/` 端点**
   - 这个端点在 Ralendar 中不存在，不应该调用

2. **实现标准的 OAuth token 交换流程**
   - 在收到授权码后，调用 `POST /oauth/token` 换取 access_token
   - 然后用 access_token 调用 `GET /oauth/userinfo` 获取用户信息

3. **配置客户端密钥**
   - 需要 Ralendar 提供的 `client_secret`
   - 请通过安全渠道（如加密邮件或私密聊天）获取

## 📝 Ralendar OAuth 端点列表

| 端点 | 方法 | 用途 | 状态 |
|------|------|------|------|
| `/oauth/authorize` | GET | 显示授权页面 | ✅ 正常工作 |
| `/oauth/token` | POST | 换取 access_token | ✅ 正常工作 |
| `/oauth/userinfo` | GET | 获取用户信息 | ✅ 正常工作 |
| `/oauth/revoke` | POST | 撤销授权 | ✅ 可用 |
| `/oauth/authorized-apps` | GET | 查看已授权应用 | ✅ 可用 |

**Base URL：** `https://app7626.acapp.acwing.com.cn`

## 🔑 客户端凭证

- **Client ID：** `ralendar_client_CJjjv6N9prR6JpDGmWijgA`
- **Client Secret：** [已在数据库中配置，请联系我们通过安全渠道获取]
- **Redirect URI：** `https://roamio.cn/auth/ralendar/callback`
- **Allowed Scopes：** `calendar:read`, `calendar:write`, `user:read`

**⚠️ 重要：** Client Secret 已加密存储在数据库中，无法直接查看。如需重新设置，我们可以：
1. 重置 Client Secret（会生成新的密钥）
2. 或通过私密渠道发送（如果之前有记录）

## 📞 联系方式

如有任何问题，请随时联系我们：
- 技术问题：可以通过 GitHub Issues 或直接联系我们
- 客户端密钥：请通过安全渠道获取

感谢配合！

---

**Ralendar 开发团队**

---

## 📋 邮件发送前检查清单

- [ ] 确认客户端密钥已准备好（需要从数据库获取）
- [ ] 确认所有端点 URL 正确
- [ ] 添加测试账号信息（如果需要）
- [ ] 检查是否有其他需要说明的内容

