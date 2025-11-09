# 🔐 Roamio 大家族 - 统一认证规范

> **版本**: v1.0  
> **更新日期**: 2025-11-09  
> **适用范围**: Ralendar, Roamio, Rote, Routes, Rapture 及所有未来项目

---

## 📋 目录

1. [认证方式](#认证方式)
2. [UnionID 和 OpenID](#unionid-和-openid)
3. [JWT Token 规范](#jwt-token-规范)
4. [跨应用认证流程](#跨应用认证流程)
5. [错误处理](#错误处理)

---

## 🎯 认证方式

### **支持的认证方式**

| 方式 | 用途 | 优先级 |
|------|------|--------|
| QQ OAuth2 | 主要登录方式 | ⭐⭐⭐ |
| AcWing OAuth2 | 备用登录方式 | ⭐⭐ |
| 邮箱验证码 | 未来扩展 | ⭐ |

### **选择原则**

- **QQ OAuth2**: 所有项目默认使用，获取 UnionID 进行跨应用识别
- **AcWing OAuth2**: 用于 AcApp 环境
- **邮箱验证码**: 用于不方便使用 OAuth 的场景

---

## 🔗 UnionID 和 OpenID

### **定义**

```
UnionID: 用户在同一 QQ 开放平台账号下的唯一标识（跨应用通用）
OpenID:  用户在单个 QQ 应用内的唯一标识（应用内唯一）
```

### **存储规范**

所有项目的 `SocialAccount` 模型必须包含：

```python
class SocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50)  # 'qq', 'acwing'
    openid = models.CharField(max_length=255, unique=True)
    unionid = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### **获取 UnionID**

在 QQ 登录回调中：

```python
# 1. 获取 access_token 后，调用 /oauth2.0/me 获取 openid
me_response = requests.get('https://graph.qq.com/oauth2.0/me', params={
    'access_token': access_token,
    'unionid': 1  # ⚠️ 必须传递 unionid=1
})

# 2. 解析响应获取 unionid
data = json.loads(me_response.text.split('(')[1].split(')')[0])
openid = data.get('openid')
unionid = data.get('unionid')  # ⚠️ 必须保存

# 3. 保存到数据库
social_account, created = SocialAccount.objects.get_or_create(
    provider='qq',
    openid=openid,
    defaults={
        'user': user,
        'unionid': unionid,  # ⚠️ 必须保存
        'access_token': access_token,
    }
)
```

---

## 🎫 JWT Token 规范

### **Token 格式**

```json
{
  "user_id": 123,
  "username": "张三",
  "openid": "OPENID_12345",
  "unionid": "UID_67890",  // ⚠️ 必须包含
  "exp": 1699999999
}
```

### **Token 传递方式**

**标准方式（推荐）：**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**备用方式（AcApp）：**
```http
Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Token 生成代码**

```python
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user, social_account):
    refresh = RefreshToken.for_user(user)
    
    # ⚠️ 添加自定义字段
    refresh['openid'] = social_account.openid
    refresh['unionid'] = social_account.unionid  # ⚠️ 必须包含
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
```

---

## 🔄 跨应用认证流程

### **场景：Roamio 用户访问 Ralendar**

```mermaid
sequenceDiagram
    participant User as 用户
    participant Roamio as Roamio 前端
    participant Ralendar as Ralendar 后端
    
    User->>Roamio: 点击"日历"功能
    Roamio->>Roamio: 获取当前用户的 JWT Token
    Roamio->>Ralendar: POST /api/v1/fusion/events/<br/>Header: Authorization: Bearer {token}
    Ralendar->>Ralendar: 解析 Token，提取 unionid
    Ralendar->>Ralendar: 根据 unionid 查找/创建用户
    Ralendar->>Roamio: 返回事件数据
```

### **用户匹配优先级**

```python
# Fusion API 中的用户匹配逻辑
def get_user_from_request(request):
    # 优先级 1: UnionID（最可靠）
    unionid = request.data.get('unionid') or request.GET.get('unionid')
    if unionid:
        social = SocialAccount.objects.filter(unionid=unionid).first()
        if social:
            return social.user
    
    # 优先级 2: OpenID（应用内唯一）
    openid = request.data.get('openid') or request.GET.get('openid')
    if openid:
        social = SocialAccount.objects.filter(openid=openid).first()
        if social:
            return social.user
    
    # 优先级 3: JWT Token 中的 user_id
    if hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    
    return None
```

---

## ⚠️ 错误处理

### **标准错误响应**

```json
{
  "error": "用户未找到",
  "code": "USER_NOT_FOUND",
  "details": {
    "unionid": "UID_12345",
    "openid": null,
    "user_id": null
  }
}
```

### **错误码规范**

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| `USER_NOT_FOUND` | 400 | 无法通过 UnionID/OpenID 找到用户 |
| `TOKEN_INVALID` | 401 | Token 无效或已过期 |
| `TOKEN_MISSING` | 401 | 缺少 Authorization Header |
| `UNIONID_MISSING` | 400 | 跨应用调用时缺少 UnionID |

---

## ✅ 检查清单

每个新项目接入时，必须确认：

- [ ] 数据库中有 `SocialAccount` 模型，包含 `unionid` 字段
- [ ] QQ 登录时正确获取并保存 `unionid`
- [ ] JWT Token 中包含 `unionid`
- [ ] Fusion API 支持通过 `unionid` 进行用户匹配
- [ ] 错误处理遵循统一规范

---

## 📞 联系方式

**规范维护者**: Roamio 核心团队  
**问题反馈**: 在项目根目录创建 Issue

---

## 📝 更新日志

### v1.0 (2025-11-09)
- 初始版本
- 基于 Ralendar + Roamio 实践经验整理

