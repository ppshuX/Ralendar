# Day 13: Web 端 AcWing 一键登录实现

**日期**: 2025-11-07  
**主要任务**: 实现 Web 端 AcWing OAuth2 一键登录功能，解决多个技术难题

---

## 📋 完成功能

### 1. **Web 端 AcWing OAuth2 登录**
- ✅ 在登录页面添加 AcWing 登录按钮（带图标）
- ✅ 在注册页面也添加 AcWing 登录（无需单独注册）
- ✅ 实现 OAuth2 授权跳转流程
- ✅ 创建 `/acwing/callback` 回调页面
- ✅ 处理授权成功和失败场景
- ✅ 自动保存 JWT token 并跳转

### 2. **用户界面优化**
- ✅ 导航栏显示用户头像（AcWing 头像）
- ✅ 导航栏显示用户名
- ✅ 下拉菜单显示用户信息
- ✅ 登录后自动刷新页面更新导航栏状态
- ✅ 第三方登录按钮使用实际图标（不是 emoji）

### 3. **后端数据模型**
- ✅ 完善 `UserSerializer`，添加 `photo` 字段
- ✅ 通过 `acwing_profile` 关联获取头像
- ✅ 处理用户名冲突（当 AcWing 用户名已存在）
- ✅ 防止更新用户名时的 UNIQUE 约束冲突

### 4. **静态资源管理**
- ✅ 统一管理 OAuth 图标到 `backend/static/images/`
- ✅ 配置 Nginx 提供静态文件服务
- ✅ 添加 `.gitattributes` 确保二进制文件正确处理
- ✅ 设置静态文件缓存（30 天）

### 5. **环境变量管理**
- ✅ 添加 `python-dotenv` 支持
- ✅ 创建 `.env` 文件存储敏感信息
- ✅ 在 `settings.py` 中加载环境变量
- ✅ 从环境变量读取 `ACWING_SECRET`

---

## 🐛 遇到的问题和解决方案

### 问题 1: 后端 500 错误，看不到错误日志
**现象**: AcWing 登录返回 500，uwsgi 日志不显示详细信息

**原因**: `print()` 输出不会被 uwsgi 捕获

**解决方案**:
```python
import logging
logger = logging.getLogger(__name__)
logger.error(f"[AcWing Login] Message")
```

---

### 问题 2: Unicode 编码错误
**现象**: 
```
UnicodeEncodeError: 'ascii' codec can't encode characters
```

**原因**: 日志中使用了中文，uwsgi 默认 ASCII 编码

**解决方案**: 将所有日志改为英文
```python
logger.error(f"[AcWing Login] Received code: {code}")  # 英文
```

---

### 问题 3: ACWING_SECRET 为空
**现象**: 
```
[AcWing Login] AppID: 7626, Secret: 
[AcWing Login] Token response: {'errcode': '40002', 'errmsg': 'args invalid'}
```

**原因**: uwsgi 进程没有继承 shell 的环境变量

**解决方案**: 使用 `.env` 文件
```python
# settings.py
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# .env 文件
ACWING_SECRET=7030aff130bd41c9876413211fe406af
```

---

### 问题 4: 用户名冲突导致 IntegrityError
**现象**:
```
django.db.utils.IntegrityError: UNIQUE constraint failed: auth_user.username
```

**原因**: 更新已存在用户的用户名时，新用户名已被其他用户占用

**解决方案**:
```python
if user.username != username:
    # 检查新用户名是否已被其他用户占用
    if not User.objects.filter(username=username).exclude(id=user.id).exists():
        user.username = username
        user.save()
```

---

### 问题 5: 静态文件（图标）无法访问
**现象**: 浏览器访问 `/static/images/AcWing_logo.png` 显示渐变背景，图片不显示

**原因**: Nginx 配置缺少静态文件路径

**解决方案**:
```nginx
# 静态文件
location /static/ {
    alias /home/acs/kotlin_calendar/backend/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

### 问题 6: 登录成功但导航栏不更新
**现象**: AcWing 登录成功，但导航栏仍显示"登录"按钮

**原因**: 使用 `router.push()` 跳转，NavBar 的 `onMounted` 不会重新执行

**解决方案**:
```javascript
// 使用 window.location 强制刷新页面
window.location.href = '/calendar'
```

---

## 🔧 关键技术要点

### 1. **AcWing Web OAuth2 流程**
```
1. 用户点击 "AcWing 登录"
2. 跳转到 AcWing 授权页面
   URL: https://www.acwing.com/third_party/api/oauth2/web/authorize/
   参数: appid, redirect_uri, scope, state
3. 用户授权后，AcWing 重定向到 redirect_uri
   携带: code, state
4. 前端回调页面调用后端 /api/auth/acwing/login/
   发送: code
5. 后端用 code 换取 access_token 和 openid
6. 后端用 access_token 获取用户信息
7. 后端创建/更新用户，生成 JWT token
8. 前端保存 token，跳转到日历页面
```

### 2. **环境变量最佳实践**
```python
# 1. 安装 python-dotenv
pip install python-dotenv

# 2. 在 settings.py 加载
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# 3. 创建 .env 文件
ACWING_SECRET=your_secret_here

# 4. 添加到 .gitignore
.env
*.env
!.env.example
```

### 3. **静态文件服务**
```nginx
# Nginx 配置
location /static/ {
    alias /path/to/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

```python
# Django settings.py
STATIC_URL = 'static/'

# Django urls.py
from django.conf.urls.static import static
urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
```

---

## 📁 主要代码变更

### 后端
- `backend/api/views/auth.py`: 添加详细的英文日志
- `backend/api/serializers.py`: UserSerializer 添加 photo 字段
- `backend/calendar_backend/settings.py`: 集成 python-dotenv
- `backend/requirements.txt`: 添加 python-dotenv 和 requests
- `backend/.env`: 存储敏感信息（不提交到 Git）
- `backend/nginx.conf`: 添加 /static/ 路径配置
- `backend/static/images/`: 存放 OAuth 图标

### 前端
- `web_frontend/src/views/account/LoginView.vue`: 
  - 添加 AcWing/QQ 登录按钮（登录+注册）
  - 使用后端静态文件的图标
  - 登录成功后使用 window.location 刷新
- `web_frontend/src/views/account/AcWingCallback.vue`: 
  - 处理 AcWing 授权回调
  - 显示加载动画和状态
- `web_frontend/src/components/NavBar.vue`:
  - 显示用户头像
  - 显示用户名和下拉菜单
- `web_frontend/src/router/index.js`: 添加 /acwing/callback 路由

### 配置
- `.gitattributes`: 确保二进制文件正确处理

---

## 📊 开发统计

- **耗时**: ~6 小时（包含大量调试）
- **代码提交**: 15+ 次
- **解决的 Bug**: 6 个关键问题
- **新增文件**: 5 个
- **修改文件**: 15+ 个
- **添加的依赖**: 2 个（python-dotenv, requests）

---

## 🎯 技术收获

1. **uwsgi 日志调试**: 学会使用 Python logging 模块而非 print
2. **环境变量管理**: 掌握 python-dotenv 的使用
3. **Nginx 静态文件服务**: 理解 location 和 alias 的配置
4. **Django ORM 高级查询**: exclude() 防止更新冲突
5. **Vue 页面刷新策略**: window.location vs router.push 的区别
6. **OAuth2 Web 流程**: 完整实现 Web 端的 OAuth2 授权

---

## ✅ 测试验证

- ✅ 登录页面显示 AcWing 和 QQ 按钮（带图标）
- ✅ 注册页面也显示 AcWing 和 QQ 按钮
- ✅ 点击 AcWing 按钮跳转到授权页面
- ✅ 授权成功后正确返回并登录
- ✅ 导航栏显示用户头像和用户名
- ✅ 下拉菜单显示用户信息
- ✅ 退出登录功能正常
- ✅ 静态文件（图标）正常访问
- ✅ 用户名冲突时不会报错

---

## 🚀 下一步计划 (Day 14)

### 优先级高：
1. **QQ 一键登录（Web 端）** - 完善多端登录体系
2. **清理临时文件** - 删除 images 文件夹
3. **Day 13 总结文档** - 记录开发过程

### 可选功能：
- 地图功能集成
- AI 语音助手
- Android 端云同步
- 日历分享订阅

---

**总结**: Day 13 成功实现了 Web 端的 AcWing 一键登录，解决了环境变量、日志编码、静态文件服务等多个技术难题。现在用户可以在 Web 端使用 AcWing 账号无缝登录，体验与 AcApp 端一致的授权流程！🎉

