# 🚀 QQ UnionID 集成 - 下一步行动指南

**状态**: ✅ 两边都已获取 UnionID 权限  
**更新时间**: 2025-11-08 23:45

---

## ✅ 当前状态确认

### Roamio QQ 应用
```
APP ID:  102813859
APP Key: OddPvLYXHo69wTYO
UnionID: ✅ 已获取
```

### Ralendar QQ 应用
```
APP ID:  102818448
APP Key: sZ0B7nDQP8Bzb1JP
UnionID: ✅ 已获取
```

**结论**: 🎉 两边权限都已就绪，可以开始代码实现！

---

## 🎯 立即行动清单

### 📝 第一步：Ralendar 后端代码修改（30分钟）

#### 1.1 数据库迁移（添加 unionid 字段）

**创建迁移文件**:
```bash
cd backend
python manage.py makemigrations
```

**编辑迁移文件** `backend/api/migrations/0008_add_qq_unionid.py`:
```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0007_add_fusion_fields'),  # 根据实际情况调整
    ]

    operations = [
        migrations.AddField(
            model_name='qquser',
            name='unionid',
            field=models.CharField(max_length=100, blank=True, null=True, db_index=True),
        ),
    ]
```

**执行迁移**:
```bash
python manage.py migrate
```

**验证**:
```bash
python manage.py dbshell
> DESCRIBE api_qquser;
# 应该看到 unionid 字段
```

---

#### 1.2 修改 QQ 登录视图（添加 unionid 获取）

**文件**: `backend/api/views/auth.py`

**查找这段代码**:
```python
@api_view(['POST'])
def qq_login(request):
    code = request.data.get('code')
    
    # 1. 获取 access_token
    token_url = 'https://graph.qq.com/oauth2.0/token'
    # ...
```

**修改为**:
```python
@api_view(['POST'])
def qq_login(request):
    code = request.data.get('code')
    
    # 1. 获取 access_token（添加 unionid=1）
    token_url = 'https://graph.qq.com/oauth2.0/token'
    token_params = {
        'grant_type': 'authorization_code',
        'client_id': settings.QQ_APPID,
        'client_secret': settings.QQ_APPKEY,
        'code': code,
        'redirect_uri': settings.QQ_REDIRECT_URI,
        'unionid': 1  # ← 添加这行
    }
    
    # 2. 获取 openid（添加 unionid=1）
    openid_url = 'https://graph.qq.com/oauth2.0/me'
    openid_params = {
        'access_token': access_token,
        'unionid': 1  # ← 添加这行
    }
    
    # 3. 获取用户信息（添加 unionid=1）
    user_info_url = 'https://graph.qq.com/user/get_user_info'
    user_info_params = {
        'access_token': access_token,
        'oauth_consumer_key': settings.QQ_APPID,
        'openid': openid,
        'unionid': 1  # ← 添加这行
    }
    
    response = requests.get(user_info_url, params=user_info_params)
    user_info = response.json()
    
    # ← 新增：获取 unionid
    unionid = user_info.get('unionid', '')
    print(f'[QQ Login] OpenID: {openid}, UnionID: {unionid}')  # 调试日志
    
    # 4. 查找或创建用户（优先使用 unionid）
    if unionid:
        # 先通过 unionid 查找（跨应用识别）
        try:
            qq_user = QQUser.objects.get(unionid=unionid)
            user = qq_user.user
            
            # 更新当前应用的 openid（因为不同应用 openid 不同）
            qq_user.openid = openid
            qq_user.access_token = access_token
            qq_user.save()
            
            print(f'[QQ Login] Found existing user by UnionID: {user.username}')
            
        except QQUser.DoesNotExist:
            # 通过 openid 查找（同应用内）
            try:
                qq_user = QQUser.objects.get(openid=openid)
                user = qq_user.user
                
                # 补充 unionid
                qq_user.unionid = unionid
                qq_user.save()
                
                print(f'[QQ Login] Updated existing user with UnionID: {user.username}')
                
            except QQUser.DoesNotExist:
                # 首次登录，创建新用户
                username = f'qq_{openid[:8]}'
                user = User.objects.create_user(
                    username=username,
                    email=f'{openid}@ralendar.user'
                )
                
                qq_user = QQUser.objects.create(
                    user=user,
                    openid=openid,
                    unionid=unionid,  # ← 保存 UnionID
                    access_token=access_token,
                    nickname=user_info.get('nickname', ''),
                    photo_url=user_info.get('figureurl_qq_2', '')
                )
                
                print(f'[QQ Login] Created new user: {user.username}, UnionID: {unionid}')
    else:
        # 没有 unionid 的情况（向后兼容）
        try:
            qq_user = QQUser.objects.get(openid=openid)
            user = qq_user.user
        except QQUser.DoesNotExist:
            # 创建新用户...
            pass
    
    # 5. 生成 JWT Token
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })
```

---

#### 1.3 前端修改（添加 unionid=1 参数）

**文件**: `web_frontend/src/views/account/LoginView.vue`

**查找 QQ 登录链接**:
```javascript
const qqLoginUrl = computed(() => {
  const redirectUri = encodeURIComponent(
    `${window.location.origin}/qq/callback`
  )
  return `https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=${QQ_APPID}&redirect_uri=${redirectUri}&state=${state.value}`
})
```

**修改为**:
```javascript
const qqLoginUrl = computed(() => {
  const redirectUri = encodeURIComponent(
    `${window.location.origin}/qq/callback`
  )
  return `https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=${QQ_APPID}&redirect_uri=${redirectUri}&state=${state.value}&unionid=1`
  //                                                                                                                                                        ^^^^^^^^^^^^ 添加这个
})
```

---

### 📝 第二步：Roamio 确认配置（让 Roamio 团队做）

需要 Roamio 团队确认：

#### 2.1 检查代码是否已添加 unionid 参数

```python
# 检查这些地方是否有 unionid=1
# 1. OAuth 授权 URL
# 2. 获取 openid 请求
# 3. 获取用户信息请求
```

#### 2.2 检查数据库

```sql
-- 查看是否有 unionid 字段和数据
SELECT id, user_id, openid, unionid, provider 
FROM social_account 
WHERE provider = 'qq' 
LIMIT 5;
```

#### 2.3 检查保存逻辑

```python
# 确认登录时保存了 unionid
social_account.unionid = user_info.get('unionid', '')
social_account.save()
```

---

### 📝 第三步：测试验证（双方都要做）

#### 3.1 测试 UnionID 获取

**Ralendar 测试**:
```bash
cd backend
python manage.py shell
```

```python
# 1. 查看现有 QQ 用户
from api.models import QQUser
users = QQUser.objects.all()
print(f"共有 {users.count()} 个 QQ 用户")

for u in users:
    print(f"User: {u.user.username}")
    print(f"  OpenID: {u.openid[:15]}...")
    print(f"  UnionID: {u.unionid[:15] if u.unionid else 'None'}")
    print()

# 2. 清空测试（可选）
# QQUser.objects.all().delete()
```

**Roamio 测试**:
```python
# 类似的测试，使用 SocialAccount 模型
from backend.models import SocialAccount
accounts = SocialAccount.objects.filter(provider='qq')

for acc in accounts:
    print(f"User: {acc.user.username}")
    print(f"  OpenID: {acc.openid[:15]}...")
    print(f"  UnionID: {acc.unionid[:15] if acc.unionid else 'None'}")
    print()
```

---

#### 3.2 完整登录测试

**测试流程**:
1. 清空测试环境（或使用新 QQ 账号）
2. 在 Ralendar 用 QQ 登录 → 记录 unionid
3. 在 Roamio 用同一个 QQ 登录 → 检查 unionid 是否相同
4. （理想情况）两边识别为同一用户

**验证 SQL**:
```sql
-- Ralendar
SELECT user_id, openid, unionid FROM api_qquser WHERE unionid IS NOT NULL;

-- Roamio
SELECT user_id, openid, unionid FROM social_account WHERE provider='qq' AND unionid IS NOT NULL;

-- 检查 unionid 是否相同
```

---

#### 3.3 用户匹配测试

**场景 1: 不共享数据库**
```
预期：两边各有一个用户，但 unionid 相同
结果：可以通过 API 交互，但不是同一个 user_id
```

**场景 2: 共享数据库**（推荐）
```
预期：两边共享同一个用户记录
结果：user_id 相同，完美互通！
```

---

### 📝 第四步：部署上线

#### 4.1 Ralendar 部署

```bash
# 本地提交代码
git add backend/api/views/auth.py
git add backend/api/migrations/0008_add_qq_unionid.py
git add web_frontend/src/views/account/LoginView.vue
git commit -m "feat: add QQ UnionID support for cross-app user recognition"
git push

# 服务器部署
ssh acs@app7626.acapp.acwing.com.cn
cd ~/kotlin_calendar
git pull

# 执行迁移
cd backend
python manage.py migrate

# 重启服务
pkill -f uwsgi
uwsgi --ini uwsgi.ini &

# 重新构建前端
cd ../web_frontend
npm run build
```

#### 4.2 Roamio 部署

（让 Roamio 团队确认并部署）

---

## 🧪 验收标准

完成以下验证，确认集成成功：

- [ ] Ralendar 数据库有 `unionid` 字段
- [ ] Ralendar QQ 登录获取到 `unionid`（非空）
- [ ] Roamio QQ 登录获取到 `unionid`（非空）
- [ ] 同一个 QQ 用户在两边的 `unionid` 相同
- [ ] 前端 QQ 登录按钮正常工作
- [ ] API 可以通过 UnionID 识别用户
- [ ] （可选）共享数据库后 user_id 相同

---

## 🎉 预期效果

完成后：
- ✅ 用户在 Roamio 用 QQ 登录 → 在 Ralendar 自动识别
- ✅ 用户在 Ralendar 用 QQ 登录 → 在 Roamio 自动识别
- ✅ 旅行计划可以无缝添加到日历
- ✅ 两个应用共享用户身份

---

## 📞 需要帮助？

**Ralendar 技术支持**:
- QQ/邮箱: 2064747320@qq.com
- 文档: [QQ_UNIONID_INTEGRATION.md](./QQ_UNIONID_INTEGRATION.md)

---

**预计完成时间**: 
- 代码修改: 30-60 分钟
- 测试验证: 30 分钟
- 部署上线: 30 分钟
- **总计**: 2 小时内完成！🚀

