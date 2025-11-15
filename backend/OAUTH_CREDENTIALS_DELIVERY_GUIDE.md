# OAuth 客户端凭证安全交付指南

> **⚠️ 重要安全提醒**：此文档不包含实际凭证，仅说明如何安全地获取和发送凭证。

---

## 📋 概述

Ralendar OAuth 2.0 客户端凭证已成功生成，包含：
- ✅ Client ID
- ✅ Client Secret（敏感！）
- ✅ 回调地址白名单
- ✅ 权限范围配置

---

## 🔐 凭证获取方式

### 方式1：服务器端获取（推荐）

在 Ralendar 服务器上执行以下命令查看已创建的客户端：

```bash
cd ~/ralendar/backend
python3 manage.py shell

>>> from api.models import OAuthClient
>>> client = OAuthClient.objects.filter(client_name='Roamio').first()
>>> if client:
...     print(f"Client ID: {client.client_id}")
...     print(f"Redirect URIs: {client.redirect_uris}")
...     print(f"Allowed Scopes: {client.allowed_scopes}")
... else:
...     print("客户端未找到")
```

**注意**：`Client Secret` 在创建时已显示，且**仅显示一次**。如果遗失，需要重新生成。

### 方式2：重新生成凭证

如果 Client Secret 遗失，可以重新生成：

```bash
# 1. 删除旧客户端
python3 manage.py shell
>>> from api.models import OAuthClient
>>> OAuthClient.objects.filter(client_name='Roamio').delete()
>>> exit()

# 2. 重新创建
python3 manage.py init_oauth_client \
    --client-name "Roamio" \
    --redirect-uris "https://roamio.cn/auth/ralendar/callback,http://localhost:8080/auth/ralendar/callback"
```

---

## 📧 凭证安全发送方式

### ✅ 推荐方式

1. **加密邮件**
   - 使用 PGP/GPG 加密邮件内容
   - 或使用 ProtonMail 等端到端加密邮件服务

2. **私密消息平台**
   - 微信/企业微信（临时会话）
   - Telegram Secret Chat
   - Signal

3. **密码管理器共享**
   - 1Password 团队共享
   - Bitwarden 组织 Vault
   - LastPass 共享文件夹

4. **安全文件传输**
   - 使用临时文件共享服务（设置密码和过期时间）
   - 例：Firefox Send（已停用），可用替代品：
     - https://send.vis.ee/
     - https://upload.disroot.org/

### ❌ 不推荐方式

- ❌ 明文邮件
- ❌ 公开的 Git 仓库
- ❌ 未加密的聊天记录
- ❌ 公开的文档或 Wiki
- ❌ Slack/Discord 公开频道

---

## 🛡️ 凭证安全管理

### Roamio 团队收到凭证后

1. **立即保存到安全位置**
   ```bash
   # 添加到环境变量（不提交到 Git）
   echo "RALENDAR_OAUTH_CLIENT_ID=<client_id>" >> cloud_settings/.env
   echo "RALENDAR_OAUTH_CLIENT_SECRET=<client_secret>" >> cloud_settings/.env
   ```

2. **确保 .gitignore 正确配置**
   ```bash
   # 检查 .env 是否被忽略
   git check-ignore cloud_settings/.env
   # 应该输出：cloud_settings/.env
   ```

3. **定期轮换密钥**
   - 建议每 90 天轮换一次 Client Secret
   - 轮换前通知 Ralendar 团队

---

## 📊 已配置信息

### 回调地址白名单

- ✅ `https://roamio.cn/auth/ralendar/callback`（生产环境）
- ✅ `http://localhost:8080/auth/ralendar/callback`（测试环境）

### 权限范围

- ✅ `calendar:read` - 读取日历事件
- ✅ `calendar:write` - 创建/修改/删除事件
- ✅ `user:read` - 读取用户基本信息

### API 端点

- 授权端点：`https://app7626.acapp.acwing.com.cn/oauth/authorize`
- Token 端点：`https://app7626.acapp.acwing.com.cn/api/oauth/token`
- UserInfo 端点：`https://app7626.acapp.acwing.com.cn/api/oauth/userinfo`
- 撤销端点：`https://app7626.acapp.acwing.com.cn/api/oauth/revoke`

---

## 🧪 凭证验证

收到凭证后，可以使用以下命令快速验证：

```bash
# 测试生成授权 URL
curl -X GET "https://app7626.acapp.acwing.com.cn/oauth/authorize?client_id=<client_id>&redirect_uri=http://localhost:8080/auth/ralendar/callback&response_type=code&state=test&scope=calendar:read"
```

如果配置正确，应该返回 Ralendar 的授权页面。

---

## 📞 联系方式

如果有任何问题或需要重新生成凭证，请联系：

- **Ralendar 技术团队**
- **邮箱**: [开发团队邮箱]
- **紧急联系**: [技术负责人]

---

## ⚠️ 安全事件响应

如果怀疑凭证泄露：

1. **立即通知 Ralendar 团队**
2. **撤销所有相关的 OAuth Token**
   ```bash
   # Ralendar 服务器端执行
   python3 manage.py shell
   >>> from api.models import OAuthAccessToken, OAuthClient
   >>> client = OAuthClient.objects.get(client_name='Roamio')
   >>> OAuthAccessToken.objects.filter(client=client).update(is_revoked=True)
   ```
3. **重新生成新的 Client Secret**
4. **更新 Roamio 的环境变量**
5. **审查访问日志，确认是否有异常访问**

---

## 📝 变更日志

| 日期 | 操作 | 执行人 |
|------|------|--------|
| 2025-11-15 | 初始凭证生成 | Ralendar 团队 |
| | | |

---

**最后更新**: 2025-11-15  
**文档版本**: 1.0

