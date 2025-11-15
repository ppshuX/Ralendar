# OAuth 2.0 集成总结

> **完成日期：** 2025-11-15  
> **状态：** ✅ 已完成并测试通过

## 📋 概述

本文档总结了 Ralendar 与 Roamio 的 OAuth 2.0 集成过程，包括遇到的问题、解决方案和最终实现。

## ✅ 完成的功能

### 1. OAuth 2.0 授权流程

完整的 OAuth 2.0 Authorization Code Flow 已实现并测试通过：

```
1. Roamio 发起授权请求
   GET /oauth/authorize?client_id=xxx&redirect_uri=xxx&response_type=code&state=xxx
   ↓
2. Ralendar 显示授权页面（如果未登录，显示登录选项）
   ↓
3. 用户点击 QQ 登录 → 跳转到 QQ 授权页面
   ↓
4. QQ 登录成功 → 返回 Ralendar 授权页面（带原始参数）
   ↓
5. 用户点击"授权"按钮
   ↓
6. 生成授权码，重定向回 Roamio
   redirect_uri?code=xxx&state=xxx
   ↓
7. Roamio 用授权码换取 access_token
   POST /oauth/token
   ↓
8. Roamio 用 access_token 获取用户信息
   GET /oauth/userinfo
```

### 2. 实现的 OAuth 端点

| 端点 | 方法 | 用途 | 状态 |
|------|------|------|------|
| `/oauth/authorize` | GET | 显示授权页面 | ✅ 正常工作 |
| `/oauth/authorize` | POST | 处理授权决定 | ✅ 正常工作 |
| `/oauth/login` | GET | 跳转到第三方登录 | ✅ 正常工作 |
| `/oauth/token` | POST | 换取 access_token | ✅ 正常工作 |
| `/oauth/userinfo` | GET | 获取用户信息 | ✅ 正常工作 |
| `/oauth/revoke` | POST | 撤销授权 | ✅ 可用 |
| `/oauth/authorized-apps` | GET | 查看已授权应用 | ✅ 可用 |

**Base URL：** `https://app7626.acapp.acwing.com.cn`

### 3. 客户端配置

- **Client ID：** `ralendar_client_CJjjv6N9prR6JpDGmWijgA`
- **Client Name：** Roamio
- **Redirect URIs：**
  - `https://roamio.cn/auth/ralendar/callback`
  - `http://localhost:8080/auth/ralendar/callback`（开发环境）
- **Allowed Scopes：** `calendar:read`, `calendar:write`, `user:read`

## 🔧 修复的问题

### 问题 1：前端路由拦截 OAuth 回调

**症状：** QQ 回调后被前端 Vue Router 拦截，导致循环重定向

**原因：** 
- `/qq/callback` 在前端路由中配置，被 Vue Router 拦截
- 前端 `QQCallback.vue` 组件总是发送 POST 到 `/api/auth/qq/callback/`（普通登录流程）

**解决方案：**
1. 在 Nginx 中添加 `location /qq/callback`，直接代理到后端，绕过前端路由
2. 在 `QQCallback.vue` 中检测 OAuth 流程（`state` 以 `qq_oauth_` 开头），直接重定向到服务器端
3. 在路由守卫中检测 OAuth 流程，直接重定向到服务器端

**修改文件：**
- `backend/nginx.conf` - 添加 `/qq/callback` location
- `web_frontend/src/views/account/QQCallback.vue` - 检测 OAuth 流程
- `web_frontend/src/router/index.js` - 路由守卫检测

### 问题 2：登录后没有返回授权页面

**症状：** QQ 登录成功后，跳转到 `/calendar` 而不是返回授权页面

**原因：**
- Session 在跨域名时可能丢失（QQ 授权在 `graph.qq.com`，回调回到我们的域名）
- `next_url` 丢失导致无法重定向回授权页面

**解决方案：**
1. 将 `next_url` 编码到 `state` 参数中（base64 编码）
2. 从 `state` 参数中恢复 `next_url`
3. 从 `HTTP_REFERER` header 中恢复 `next_url`（备用方案）
4. 添加多个备用机制确保 `next_url` 可以恢复

**修改文件：**
- `backend/api/views/oauth/login.py` - 改进 `next_url` 恢复逻辑

### 问题 3：授权后没有跳转回 Roamio

**症状：** 用户点击"授权"后，停留在 Ralendar 授权页面，没有跳转到 Roamio

**原因：**
1. 使用 `redirect()` 可能在某些情况下不执行
2. `redirect_uri` 验证可能失败
3. POST 请求中参数可能丢失

**解决方案：**
1. 使用 `HttpResponseRedirect` 确保重定向执行
2. 验证 `redirect_uri` 必须是完整的 URL（以 `http://` 或 `https://` 开头）
3. POST 请求中优先使用 POST 参数，备用 GET 参数
4. 添加详细日志记录重定向流程

**修改文件：**
- `backend/api/views/oauth/authorize.py` - 改进重定向逻辑和参数处理

### 问题 4：用户信息获取失败

**症状：** Roamio 调用 `/oauth/userinfo` 时返回 500 错误

**原因：** 用户可能没有关联的 QQ 或 AcWing 账号信息

**解决方案：**
1. 添加异常处理，避免访问不存在的关联对象时出错
2. 改进错误日志记录
3. 确保即使没有第三方账号信息也能正常返回用户信息

**修改文件：**
- `backend/api/views/oauth/userinfo.py` - 改进错误处理

## 📁 修改的文件

### 后端文件

1. **`backend/api/views/oauth/authorize.py`**
   - 使用 `HttpResponseRedirect` 确保重定向执行
   - 验证 `redirect_uri` 必须是完整 URL
   - 改进 POST 参数处理（优先 POST，备用 GET）
   - 清理调试日志，保留必要日志

2. **`backend/api/views/oauth/login.py`**
   - 改进 `next_url` 恢复逻辑（从 session、state、referer）
   - 使用 `HttpResponseRedirect` 确保重定向执行
   - 清理调试日志，保留必要日志

3. **`backend/api/views/oauth/userinfo.py`**
   - 改进错误处理，避免访问不存在的关联对象时出错
   - 添加异常处理

4. **`backend/nginx.conf`**
   - 添加 `location /qq/callback`，直接代理到后端

### 前端文件

1. **`web_frontend/src/views/account/QQCallback.vue`**
   - 检测 OAuth 流程（`state` 以 `qq_oauth_` 开头）
   - OAuth 流程直接重定向到服务器端，绕过前端处理

2. **`web_frontend/src/router/index.js`**
   - 在路由守卫中检测 OAuth 流程
   - OAuth 流程直接重定向到服务器端

## 🚀 部署说明

### 服务器部署步骤

1. **拉取最新代码**
   ```bash
   cd ~/ralendar
   git pull origin master
   ```

2. **更新 Nginx 配置**
   ```bash
   sudo cp backend/nginx.conf /etc/nginx/nginx.conf
   sudo nginx -t
   sudo /etc/init.d/nginx restart
   ```

3. **重启 uwsgi**
   ```bash
   cd ~/ralendar/backend
   pkill -f uwsgi
   sleep 2
   uwsgi --ini uwsgi.ini --daemonize /tmp/uwsgi.log
   ```

4. **验证部署**
   - 访问 `https://app7626.acapp.acwing.com.cn/oauth/authorize?client_id=ralendar_client_CJjjv6N9prR6JpDGmWijgA&redirect_uri=https://roamio.cn/auth/ralendar/callback&response_type=code`
   - 应该显示授权页面

## 📝 API 使用示例

### 1. 获取授权码（用户授权后）

用户点击"授权"后，Roamio 会收到重定向：
```
https://roamio.cn/auth/ralendar/callback?code=AUTHORIZATION_CODE&state=STATE
```

### 2. 用授权码换取 access_token

```bash
curl -X POST https://app7626.acapp.acwing.com.cn/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "authorization_code",
    "code": "AUTHORIZATION_CODE",
    "client_id": "ralendar_client_CJjjv6N9prR6JpDGmWijgA",
    "client_secret": "CLIENT_SECRET",
    "redirect_uri": "https://roamio.cn/auth/ralendar/callback"
  }'
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

### 3. 获取用户信息

```bash
curl -X GET https://app7626.acapp.acwing.com.cn/oauth/userinfo \
  -H "Authorization: Bearer ACCESS_TOKEN"
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

## 🔐 安全注意事项

1. **Client Secret**
   - 已加密存储在数据库中，无法直接查看
   - 如需重置，使用 `python manage.py init_oauth_client` 命令
   - 通过安全渠道提供给 Roamio 团队

2. **Redirect URI 验证**
   - 必须在客户端配置的 `redirect_uris` 白名单中
   - 必须是完整的 URL（以 `http://` 或 `https://` 开头）

3. **授权码**
   - 只能使用一次
   - 10 分钟内有效
   - 必须与 `redirect_uri` 匹配

4. **Access Token**
   - 2 小时有效
   - 使用 JWT 格式
   - 包含用户信息和客户端信息

## 📊 测试结果

### 测试场景 1：完整授权流程

1. ✅ Roamio 发起授权请求 → 显示授权页面
2. ✅ 用户未登录 → 显示登录选项
3. ✅ 用户点击 QQ 登录 → 跳转到 QQ 授权页面
4. ✅ QQ 登录成功 → 返回授权页面（带原始参数）
5. ✅ 用户点击"授权" → 生成授权码，重定向回 Roamio
6. ✅ Roamio 用授权码换取 token（标准流程）
7. ✅ Roamio 用 token 获取用户信息（标准流程）

### 测试场景 2：参数恢复

1. ✅ Session 丢失时，从 `state` 参数恢复 `next_url`
2. ✅ State 参数解析失败时，从 `HTTP_REFERER` 恢复 `next_url`
3. ✅ 多个备用机制确保 `next_url` 可以恢复

### 测试场景 3：错误处理

1. ✅ 无效的 `redirect_uri` → 返回错误信息
2. ✅ 过期的授权码 → 返回错误信息
3. ✅ 未登录用户 → 返回 401 错误
4. ✅ 无效的客户端 → 返回错误信息

## 🔍 日志记录

保留的必要日志：
- OAuth 授权请求（用户 ID、客户端名称）
- OAuth token 交换（用户 ID、客户端名称）
- OAuth 用户信息请求（用户 ID）
- 错误和警告信息

已清理的调试日志：
- 详细的 GET/POST 参数
- CSRF token 信息
- 详细的重定向 URL
- 模板路径检查信息
- 过多的 `next_url` 恢复日志

## 📞 联系方式

如有问题，请联系 Ralendar 开发团队。

---

**最后更新：** 2025-11-15  
**状态：** ✅ 已完成并测试通过

