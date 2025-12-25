# QQ OAuth 登录问题修复指南

## 🔍 问题描述

**症状**：使用 Roamio 登录 Ralendar 时，QQ 授权登录出问题，但 AcWing 一键登录可以正常工作。

## 🎯 根本原因

### 1. **Nginx 路由配置缺失**（主要原因）

**问题**：
- `/qq/callback` 没有专门的 Nginx location 配置
- 请求被最后的 `location /` 匹配，被前端 Vue Router 拦截
- 导致回调无法到达后端处理函数

**对比**：
- ✅ AcWing 回调：`/oauth/login/callback/acwing/` 在 `/oauth/` 下，有专门的 location
- ❌ QQ 回调：`/qq/callback` 在根路径，没有专门配置，被前端拦截

### 2. **Session 跨域问题**（次要原因）

**问题**：
- QQ 授权跳转到 `graph.qq.com`，然后回调回来
- Session 在跨域过程中可能丢失
- `next_url` 无法从 Session 中恢复

**对比**：
- ✅ AcWing：虽然也是跨域，但 Session 配置可能更兼容
- ❌ QQ：跨域时 Session 丢失，导致 `next_url` 恢复失败

## ✅ 解决方案

### 修复 1：添加 Nginx `/qq/callback` 路由

**文件**：`backend/nginx.conf`

```nginx
# QQ回调地址（必须在OAuth之前，避免被前端路由拦截）
location = /qq/callback {
    include uwsgi_params;
    uwsgi_pass 127.0.0.1:8000;
    
    # 确保传递所有请求头（包括Referer，用于恢复next_url）
    uwsgi_pass_request_headers on;
    uwsgi_param HTTP_REFERER $http_referer;
}
```

**位置**：放在 `/oauth/` location 之前，确保优先匹配

### 修复 2：优化 Session 配置

**文件**：`backend/calendar_backend/settings.py`

```python
# ==================== Session 配置 ====================
# 确保跨域时Session能正常工作（QQ OAuth回调需要）
SESSION_COOKIE_SECURE = True  # HTTPS环境下启用
SESSION_COOKIE_HTTPONLY = True  # 防止XSS攻击
SESSION_COOKIE_SAMESITE = 'Lax'  # 允许跨站请求携带Cookie（QQ授权需要）
SESSION_COOKIE_AGE = 86400  # Session有效期24小时
SESSION_SAVE_EVERY_REQUEST = True  # 每次请求都保存Session（确保不丢失）
```

## 🔧 部署步骤

### 1. 更新 Nginx 配置

```bash
# 在服务器上
cd ~/Ralendar/backend
# 编辑 nginx.conf（已修改）
sudo cp nginx.conf /etc/nginx/sites-available/ralendar
sudo nginx -t  # 测试配置
sudo systemctl reload nginx  # 重新加载配置
```

### 2. 更新 Django 配置

```bash
# 在服务器上
cd ~/Ralendar/backend
# settings.py 已更新（Session配置）
source venv/bin/activate
python manage.py check  # 检查配置
sudo systemctl restart uwsgi  # 重启 uWSGI
```

### 3. 验证修复

1. **测试 QQ 登录流程**：
   - 从 Roamio 发起授权请求
   - 点击 QQ 登录
   - 确认回调能正常到达后端
   - 确认登录后能返回授权页面

2. **检查日志**：
   ```bash
   # 查看 Nginx 日志
   sudo tail -f /var/log/nginx/access.log | grep qq/callback
   
   # 查看 Django 日志
   sudo tail -f /var/log/uwsgi/app.log | grep "QQ Callback"
   ```

## 📊 技术对比

| 特性 | AcWing 登录 | QQ 登录（修复前） | QQ 登录（修复后） |
|------|-----------|-----------------|-----------------|
| **回调地址** | `/oauth/login/callback/acwing/` | `/qq/callback` | `/qq/callback` |
| **Nginx 路由** | ✅ 有专门 location | ❌ 被前端拦截 | ✅ 有专门 location |
| **Session 恢复** | ✅ 正常 | ❌ 可能丢失 | ✅ 优化配置 |
| **跨域支持** | ✅ 正常 | ❌ 有问题 | ✅ 正常 |

## 🔍 为什么 AcWing 可以但 QQ 不行？

### AcWing 登录流程
```
1. 用户点击 AcWing 登录
2. 跳转到 /oauth/login?provider=acwing&next=...
3. 后端保存 next_url 到 Session
4. 重定向到 AcWing 授权页面
5. AcWing 回调到 /oauth/login/callback/acwing/
   ✅ 这个路径在 /oauth/ 下，有专门的 Nginx location
6. 后端从 Session 恢复 next_url
7. 重定向回授权页面
```

### QQ 登录流程（修复前）
```
1. 用户点击 QQ 登录
2. 跳转到 /oauth/login?provider=qq&next=...
3. 后端保存 next_url 到 Session
4. 重定向到 QQ 授权页面（graph.qq.com）
5. QQ 回调到 /qq/callback
   ❌ 这个路径没有专门的 Nginx location
   ❌ 被前端 Vue Router 拦截
   ❌ Session 可能丢失
6. 无法恢复 next_url
7. 登录失败或跳转错误
```

### QQ 登录流程（修复后）
```
1. 用户点击 QQ 登录
2. 跳转到 /oauth/login?provider=qq&next=...
3. 后端保存 next_url 到 Session + 编码到 state 参数
4. 重定向到 QQ 授权页面（graph.qq.com）
5. QQ 回调到 /qq/callback
   ✅ 有专门的 Nginx location，直接代理到后端
   ✅ Session 配置优化，跨域也能保持
6. 从 Session 或 state 参数恢复 next_url
7. 重定向回授权页面 ✅
```

## 📝 注意事项

1. **Nginx 配置优先级**：
   - `location = /qq/callback` 必须放在 `location /` 之前
   - 使用精确匹配 `=` 确保优先匹配

2. **Session 配置**：
   - `SESSION_COOKIE_SAMESITE = 'Lax'` 允许跨站请求
   - `SESSION_SAVE_EVERY_REQUEST = True` 确保每次请求都保存

3. **备用机制**：
   - 代码中已有从 `state` 参数恢复 `next_url` 的备用机制
   - 从 `HTTP_REFERER` header 恢复的备用机制
   - 多个备用机制确保 `next_url` 能恢复

## 🐛 如果问题仍然存在

### 检查清单

1. ✅ Nginx 配置已更新并重新加载
2. ✅ Django settings.py 已更新并重启 uWSGI
3. ✅ 检查 Nginx 日志确认请求到达后端
4. ✅ 检查 Django 日志确认 Session 正常
5. ✅ 清除浏览器 Cookie 重新测试
6. ✅ 检查 QQ 开放平台回调地址配置

### 调试命令

```bash
# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/access.log | grep qq

# 查看 Django 日志
sudo tail -f /var/log/uwsgi/app.log | grep -i "qq\|oauth"

# 测试 Session
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.all().count()
```

## 📚 相关文档

- [OAuth 集成总结](../backend/OAUTH_INTEGRATION_SUMMARY.md)
- [QQ UnionID 集成指南](../integration/QQ_UNIONID_INTEGRATION.md)
- [Nginx 配置示例](../backend/nginx.conf.example)

---

**最后更新**：2025-11-XX  
**状态**：✅ 已修复

