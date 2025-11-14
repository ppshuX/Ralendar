# 认证系统变更说明

## 重要变更：移除邮箱注册功能

**日期**: 2025-11-14  
**原因**: 与 Roamio 项目集成冲突，防止用户身份混乱

---

## 🚨 问题背景

### 用户身份冲突场景

```
用户小明：
1. 在 Ralendar 用邮箱 "xiaoming@qq.com" 注册
   → 创建账号 (User ID: 123, 无 UnionID)
   
2. 在 Roamio 用 QQ 登录 (UnionID: ABC123)
   → QQ 邮箱也是 "xiaoming@qq.com"
   
3. 结果：无法识别是同一人，数据无法同步！
```

### 核心问题
- **邮箱不是可靠的跨应用身份标识**
- **QQ UnionID 才是唯一可靠的用户标识**
- 邮箱可能重复、可能更换、无法保证唯一性

---

## ✅ 新的认证策略

### **只支持第三方 OAuth 登录：**
- ✅ AcWing 一键登录
- ✅ QQ 一键登录
- ❌ ~~邮箱+密码注册/登录~~ **已删除**

---

## 📝 代码变更清单

### 后端变更

#### 1. **删除注册接口**
- ❌ `backend/api/views/auth/auth.py::register()`
- ❌ `backend/api/serializers.py::UserRegisterSerializer`
- ❌ `backend/api/url_patterns/auth.py` - 删除 `/auth/register/` 路由
- ❌ `backend/api/views/__init__.py` - 删除 `register` 导出

#### 2. **保留的接口**
- ✅ `/api/auth/me/` - 获取当前用户信息
- ✅ `/api/auth/refresh/` - 刷新 JWT Token
- ✅ `/api/auth/acwing/login/` - AcWing OAuth URL
- ✅ `/api/auth/acwing/callback/` - AcWing 登录回调
- ✅ `/api/auth/qq/login/` - QQ OAuth URL
- ✅ `/api/auth/qq/callback/` - QQ 登录回调

### 前端变更

#### 1. **删除组件**
- ❌ `web_frontend/src/components/auth/RegisterForm.vue` - 注册表单
- ❌ `web_frontend/src/components/auth/LoginForm.vue` - 登录表单

#### 2. **简化登录页面**
- ✅ `web_frontend/src/views/account/LoginView.vue` - 只保留第三方登录按钮
- ✅ 新增 Logo 动画和欢迎文案
- ✅ 新增用户协议链接

---

## 🎨 新登录页面设计

```
┌────────────────────────────────┐
│                                │
│         📅 (浮动动画)           │
│                                │
│      欢迎使用 Ralendar          │
│    智能日程管理，随时随地同步     │
│                                │
├────────────────────────────────┤
│                                │
│  🟦 [ AcWing 一键登录 ]         │
│                                │
│  🟩 [  QQ 一键登录   ]          │
│                                │
├────────────────────────────────┤
│                                │
│  登录即代表您同意               │
│  《用户协议》和《隐私政策》       │
│                                │
└────────────────────────────────┘
```

---

## ⚠️ 数据迁移方案

### 对于已有邮箱注册用户

**方案 A：引导绑定 QQ（推荐）**
```python
# 检测邮箱用户
if user has no unionid:
    显示通知: "为了更好体验，请绑定 QQ"
    用户绑定 QQ后:
        - 更新 unionid
        - 可与 Roamio 跨应用识别
```

**方案 B：禁用邮箱登录**
```python
# 邮箱用户无法登录
if user tries email login:
    提示: "请使用 QQ 登录"
    if QQ email matches:
        自动关联账号
        合并数据
```

---

## 🔗 与 Roamio 集成

### 邮箱检查 API
**POST** `/api/fusion/users/check-email/`

现在会返回：
```json
{
  "exists": true,
  "provider": "qq",
  "owner": {
    "unionid": "ABC123",  ← 关键！
    "openid": "XXX",
    "user_id": 123
  }
}
```

- ✅ 有 `unionid`：可跨应用识别同一用户
- ❌ 无 `unionid`（旧邮箱用户）：需要引导迁移

---

## 📊 影响评估

### 新用户
- ✅ 必须用 QQ/AcWing 登录
- ✅ 自动获得 UnionID
- ✅ 可与 Roamio 无缝同步

### 老用户（邮箱注册）
- ⚠️ 需要引导绑定 QQ
- ⚠️ 绑定前无法与 Roamio 同步
- ✅ 绑定后数据自动关联

---

## 🚀 部署步骤

1. **后端部署**
   ```bash
   cd backend
   python manage.py check
   # 无需迁移，只是删除接口
   ```

2. **前端部署**
   ```bash
   cd web_frontend
   npm run build
   # 静态文件已更新
   ```

3. **通知用户**
   - 发送系统通知给邮箱注册用户
   - 引导绑定 QQ 账号

---

## 📞 技术支持

如有问题，请联系：
- **Ralendar Team**: dev@ralendar.example.com
- **Roamio Team**: dev@roamio.cn

---

**最后更新**: 2025-11-14

