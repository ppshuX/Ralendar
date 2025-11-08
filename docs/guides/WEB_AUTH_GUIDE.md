# Web端登录注册使用指南

## 🎉 功能已完成

Web端用户认证系统已完整实现，包含以下功能：

### ✅ 已实现功能
1. **用户注册** - 创建新账号
2. **用户登录** - JWT Token认证
3. **自动刷新Token** - access token过期自动刷新
4. **用户信息显示** - NavBar显示当前登录用户
5. **退出登录** - 清除token
6. **权限控制** - 未登录只读，登录后可增删改查

---

## 🚀 服务器部署（已完成）

服务器端已经部署好JWT认证系统，执行 `git pull` 即可更新前端代码。

---

## 📱 使用方法

### 1. 访问登录页面
打开浏览器访问：
```
https://app7626.acapp.acwing.com.cn/login
```

### 2. 注册新用户
- 点击"立即注册"
- 输入用户名（3-20个字符）
- 输入邮箱（可选）
- 输入密码（至少6个字符）
- 确认密码
- 点击"注册"按钮

### 3. 登录
- 输入用户名
- 输入密码
- 点击"登录"按钮
- 登录成功后自动跳转到日历页面

### 4. 查看用户信息
- 登录后，右上角显示用户名
- 点击用户名查看下拉菜单
- 可以看到用户名和邮箱

### 5. 退出登录
- 点击用户名下拉菜单
- 点击"退出登录"
- 自动跳转到登录页面

---

## 🔐 Token机制

### Access Token（5分钟）
- 用于所有API请求
- 5分钟后自动过期
- 前端自动刷新，用户无感知

### Refresh Token（15天）
- 用于获取新的Access Token
- 15天后过期，需重新登录

### 自动刷新流程
```
1. 用户发起API请求
2. 后端检测Access Token过期（401）
3. 前端自动调用刷新接口
4. 获取新的Access Token
5. 重试原请求
6. 用户无感知
```

---

## 🎯 功能演示

### 未登录状态
- ✅ 可以查看日历
- ✅ 可以查看所有公开事件
- ❌ 无法创建事件
- ❌ 无法修改/删除事件

### 登录状态
- ✅ 可以查看自己的事件
- ✅ 可以创建新事件
- ✅ 可以修改/删除自己的事件
- ❌ 看不到其他用户的事件（数据隔离）

---

## 🔧 技术实现

### 1. Axios拦截器
```javascript
// 请求拦截器 - 自动添加Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 自动刷新Token
api.interceptors.response.use(
  response => response.data,
  async error => {
    if (error.response?.status === 401) {
      // 自动刷新token并重试请求
      ...
    }
  }
)
```

### 2. 登录组件
- 路径：`web_frontend/src/views/LoginView.vue`
- 功能：注册/登录切换、表单验证、API调用
- 样式：渐变紫色背景、圆角卡片

### 3. NavBar组件
- 路径：`web_frontend/src/components/NavBar.vue`
- 功能：显示用户信息、退出登录
- 状态：自动检测登录状态

### 4. API封装
- 路径：`web_frontend/src/api/index.js`
- 功能：authAPI（register/login/refresh/getCurrentUser）

---

## 📋 API端点

### 注册
```bash
POST /api/auth/register/
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456",
  "password_confirm": "123456"
}
```

### 登录
```bash
POST /api/auth/login/
{
  "username": "testuser",
  "password": "123456"
}

# 返回
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 刷新Token
```bash
POST /api/auth/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# 返回
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  # 可选
}
```

### 获取当前用户
```bash
GET /api/auth/me/
Header: Authorization: Bearer <access_token>

# 返回
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "date_joined": "2025-11-06T12:00:00Z"
}
```

---

## 🐛 常见问题

### Q1: 登录后立即被退出？
**A**: 检查服务器时间是否正确，JWT token依赖时间戳。

### Q2: 无法创建事件？
**A**: 确保已登录，检查浏览器控制台是否有401错误。

### Q3: Token刷新失败？
**A**: Refresh token可能已过期（15天），需要重新登录。

### Q4: 看不到其他用户的事件？
**A**: 正常现象，系统实现了数据隔离，每个用户只能看到自己的事件。

---

## 🎨 UI截图说明

### 登录页面
- 渐变紫色背景
- 白色圆角卡片
- 登录/注册切换
- Element Plus组件

### 已登录状态
- 右上角显示用户名
- 点击显示下拉菜单
- 用户信息 + 退出按钮

---

## 🚀 下一步计划

### 短期（1-2周）
- [ ] AcWing一键登录集成
- [ ] QQ一键登录集成
- [ ] 用户个人中心页面
- [ ] 修改密码功能
- [ ] 找回密码功能

### 中期（1个月）
- [ ] VIP会员系统
- [ ] 支付功能集成
- [ ] 用户偏好设置
- [ ] 头像上传

### 长期（2-3个月）
- [ ] AI智能助手
- [ ] 语音识别创建事件
- [ ] 智能提醒推送
- [ ] 团队协作功能

---

## 📞 测试账号

建议创建以下测试账号：

| 用户名 | 密码 | 用途 |
|--------|------|------|
| admin | admin123 | 管理员测试 |
| testuser | test123 | 普通用户测试 |
| demo | demo123 | 演示账号 |

---

## ✅ 功能清单

- [x] 用户注册
- [x] 用户登录
- [x] JWT Token认证
- [x] 自动刷新Token
- [x] 退出登录
- [x] NavBar用户信息显示
- [x] 权限控制（登录后可写）
- [x] 数据隔离（只看自己的事件）
- [x] Axios拦截器
- [x] 响应式设计（移动端适配）

---

**恭喜！Web端用户认证系统已全部完成！** 🎉

现在用户可以：
1. 注册新账号
2. 登录后创建私人日程
3. 数据自动同步
4. Token自动刷新
5. 安全的数据隔离

**服务器 `git pull` 后即可使用！** 🚀

