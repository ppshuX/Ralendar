# Day 14: QQ 一键登录 + 代码清理

**日期**: 2025-11-07  
**主要任务**: 实现 Web 端 QQ OAuth2 登录，重构模型模块化，清理代码

---

## 📋 完成功能

### 1. **代码清理优化**
- ✅ 删除临时 `images/` 文件夹
- ✅ 删除后端调试日志（20+ 处）
- ✅ 删除前端 console.log 调试代码（15+ 处）
- ✅ 保留关键错误日志
- ✅ 优化代码注释
- ✅ 修复 lint 错误

### 2. **模型模块化重构**
- ✅ 将 `models.py` 拆分为模块化结构：
  - `models/user.py` - AcWingUser 和 QQUser
  - `models/event.py` - Event
  - `models/calendar.py` - PublicCalendar
  - `models/__init__.py` - 统一导入
- ✅ 提升代码可维护性和扩展性

### 3. **QQ OAuth2 一键登录（Web 端）**
- ✅ 创建 `QQUser` 数据库模型
- ✅ 实现 `/api/auth/qq/login/` 接口
- ✅ 创建 `/qq/callback` 回调页面
- ✅ 激活 QQ 登录按钮（登录+注册界面）
- ✅ 配置 QQ AppID 和 AppKey
- ✅ 支持 QQ 头像和昵称显示

### 4. **环境配置**
- ✅ `.env` 文件配置 QQ 凭证
- ✅ 添加 `.gitattributes` 处理二进制文件
- ✅ 更新 `.gitignore` 忽略敏感文件

---

## 🔧 QQ OAuth2 实现细节

### QQ 登录流程
```
1. 用户点击 "QQ 登录"
2. 跳转到 QQ 授权页面
   URL: https://graph.qq.com/oauth2.0/authorize
   参数: response_type=code, client_id, redirect_uri, state, scope
3. 用户授权后，QQ 重定向到 redirect_uri
   携带: code, state
4. 前端回调页面调用后端 /api/auth/qq/login/
   发送: code
5. 后端三步流程：
   Step 1: 用 code 换取 access_token
   Step 2: 用 access_token 获取 openid
   Step 3: 用 access_token + openid 获取用户信息
6. 后端创建/更新用户，生成 JWT token
7. 前端保存 token，跳转到日历页面
```

### QQ API 特殊处理

#### 1. access_token 响应格式（URL 参数）
```python
# QQ 返回格式
"access_token=xxx&expires_in=7776000&refresh_token=xxx"

# 需要解析
import urllib.parse
token_dict = urllib.parse.parse_qs(token_text)
access_token = token_dict['access_token'][0]
```

#### 2. OpenID 响应格式（JSONP）
```python
# QQ 返回格式
'callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );'

# 需要正则提取
import re
match = re.search(r'callback\(\s*(\{.*?\})\s*\)', openid_text)
openid_data = json.loads(match.group(1))
```

#### 3. 用户信息响应格式（JSON）
```python
{
    "ret": 0,
    "msg": "",
    "nickname": "用户昵称",
    "figureurl_qq_1": "http://...",  # 小头像
    "figureurl_qq_2": "http://...",  # 大头像（优先使用）
}
```

---

## 📁 主要代码变更

### 后端模型重构
```python
# 旧结构
backend/api/models.py  # 所有模型在一个文件

# 新结构
backend/api/models/
    __init__.py         # 统一导入
    user.py            # AcWingUser, QQUser
    event.py           # Event
    calendar.py        # PublicCalendar
```

### QQUser 模型
```python
class QQUser(models.Model):
    user = models.OneToOneField(User, related_name='qq_profile')
    openid = models.CharField(max_length=100, unique=True)
    access_token = models.CharField(max_length=200, blank=True)
    refresh_token = models.CharField(max_length=200, blank=True)
    photo_url = models.URLField(blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 后端 QQ 登录接口
```python
@api_view(['POST'])
@permission_classes([AllowAny])
def qq_login(request):
    code = request.data.get('code')
    
    # Step 1: 获取 access_token
    token_response = requests.get(token_url, params=token_params)
    
    # Step 2: 获取 openid
    openid_response = requests.get(openid_url)
    
    # Step 3: 获取用户信息
    userinfo_response = requests.get(userinfo_url, params=userinfo_params)
    
    # 创建或更新用户
    qq_user = QQUser.objects.filter(openid=openid).first()
    
    # 生成 JWT token
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {...}
    })
```

### 前端 QQ 登录
```javascript
// LoginView.vue
const handleQQLogin = () => {
  const appid = '102814915'
  const redirect_uri = encodeURIComponent(`${window.location.origin}/qq/callback`)
  const state = Math.random().toString(36).substring(2)
  
  localStorage.setItem('qq_state', state)
  
  const authUrl = `https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=${appid}&redirect_uri=${redirect_uri}&state=${state}&scope=get_user_info`
  window.location.href = authUrl
}
```

---

## 🐛 遇到的问题和解决方案

### 问题 1: 数据库迁移依赖错误
**现象**: 
```
NodeNotFoundError: Migration api.0005_acwinguser dependencies reference nonexistent parent node ('api', '0004_merge_20251107_0811')
```

**原因**: 本地和服务器的迁移历史不一致

**解决方案**: 修改迁移依赖为已存在的迁移
```python
dependencies = [
    ('api', '0002_event_reminder_minutes_alter_event_end_time_and_more'),
]
```

---

### 问题 2: 表已存在错误
**现象**:
```
django.db.utils.OperationalError: table "api_acwinguser" already exists
```

**原因**: 表已在数据库中存在，但迁移记录未同步

**解决方案**: 使用 fake migration
```bash
python3 manage.py migrate api 0005_acwinguser --fake
```

---

### 问题 3: Git 合并冲突（db.sqlite3）
**现象**: 
```
error: Your local changes to the following files would be overwritten by merge:
        backend/db.sqlite3
```

**原因**: 数据库文件不应该被提交到 Git

**解决方案**:
```bash
# 暂存本地修改
git stash

# 拉取代码
git pull

# 确保 .gitignore 包含 *.sqlite3
```

---

## 📊 开发统计

- **耗时**: ~3 小时
- **代码提交**: 8 次
- **新增文件**: 7 个
- **删除文件**: 4 个（临时文件）
- **修改文件**: 15+ 个
- **代码清理**: 删除 35+ 处调试输出
- **模型重构**: 1 个大文件拆分为 4 个模块

---

## 🎯 技术收获

1. **模型模块化**: 学会大型项目的模型组织方式
2. **QQ OAuth2 流程**: 掌握 QQ 特殊的响应格式处理
3. **代码清理技巧**: 区分哪些日志应该保留，哪些应该删除
4. **迁移管理**: 处理迁移依赖和冲突问题
5. **Git 最佳实践**: .gitignore 和 .gitattributes 的使用

---

## 🔄 模型重构对比

### 重构前：
```
backend/api/
    models.py  (103 行，混杂 4 个模型)
```

### 重构后：
```
backend/api/models/
    __init__.py     (15 行，统一导入)
    user.py        (54 行，用户相关)
    event.py       (33 行，事件相关)
    calendar.py    (35 行，日历相关)
```

**优势**：
- ✅ 更清晰的代码结构
- ✅ 更易于维护和扩展
- ✅ 每个文件职责单一
- ✅ 符合 Django 最佳实践

---

## ✅ 测试验证

### AcWing 登录（复测）
- ✅ Web 端 AcWing 登录正常
- ✅ AcApp 端 AcWing 登录正常
- ✅ 用户头像显示正常
- ✅ 导航栏更新正常

### QQ 登录（新功能）
- ⏳ 等待用户测试
- 后端接口已实现
- 前端界面已完成
- 需要实际 QQ 授权测试

---

## 📁 项目结构优化

```
backend/
  ├── api/
  │   ├── models/              ⭐ NEW! 模块化
  │   │   ├── __init__.py
  │   │   ├── user.py
  │   │   ├── event.py
  │   │   └── calendar.py
  │   ├── views/               ✅ 已模块化
  │   │   ├── __init__.py
  │   │   ├── auth.py
  │   │   ├── events.py
  │   │   ├── calendars.py
  │   │   ├── lunar.py
  │   │   └── oauth_callback.py
  │   ├── migrations/
  │   │   ├── 0001_initial.py
  │   │   ├── 0002_event_...py
  │   │   ├── 0005_acwinguser.py
  │   │   └── 0006_qquser.py
  │   ├── serializers.py
  │   └── urls.py
  ├── static/images/          ⭐ 统一资源管理
  │   ├── AcWing_logo.png
  │   └── qq_login.png
  └── .env                    ⭐ 环境变量

web_frontend/
  └── src/
      └── views/account/
          ├── LoginView.vue
          ├── AcWingCallback.vue
          └── QQCallback.vue      ⭐ NEW!
```

---

## 🚀 下一步计划 (Day 15)

### 已完成的登录方式：
- ✅ 普通账号注册登录
- ✅ AcWing 一键登录（Web + AcApp）
- ✅ QQ 一键登录（Web）

### 可选功能：
1. **用户个人中心** ⭐⭐⭐⭐
2. **账号绑定管理** ⭐⭐⭐⭐
3. **地图功能集成** ⭐⭐⭐⭐⭐
4. **AI 语音助手** ⭐⭐⭐⭐⭐
5. **Android 端云同步** ⭐⭐⭐
6. **日历分享订阅** ⭐⭐⭐⭐

---

**总结**: Day 14 成功实现了 Web 端 QQ 一键登录，完成了模型的模块化重构，并进行了全面的代码清理。项目结构更清晰，代码质量显著提升！🎉

