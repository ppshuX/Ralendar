# 🔗 Roamio 大家族 - Fusion API 扩展指南

> **版本**: v1.0  
> **更新日期**: 2025-11-09  
> **适用范围**: 所有需要跨应用集成的项目

---

## 📋 目录

1. [什么是 Fusion API](#什么是-fusion-api)
2. [架构设计](#架构设计)
3. [接入新应用](#接入新应用)
4. [标准 CRUD 接口](#标准-crud-接口)
5. [数据同步策略](#数据同步策略)
6. [安全性](#安全性)

---

## 🎯 什么是 Fusion API

**Fusion API** 是 Roamio 大家族的**跨应用数据集成层**，允许：

- Roamio 访问 Ralendar 的日历事件
- Rote 访问 Roamio 的笔记
- Routes 访问 Ralendar 的地点信息
- 所有应用共享用户身份（通过 UnionID）

### **设计原则**

1. **中心化认证，去中心化数据**：用户身份统一，数据各应用独立存储
2. **RESTful 设计**：遵循标准 REST API 规范
3. **最小权限**：只暴露必要的数据和操作
4. **向后兼容**：新版本不破坏旧版本

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    Roamio 前端                          │
│  (用户登录，获取 JWT Token，包含 UnionID)               │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ 1. 携带 JWT Token + UnionID
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Ralendar 后端 - Fusion API                 │
│  /api/v1/fusion/events/                                 │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │  1. 验证 JWT Token                       │          │
│  │  2. 提取 UnionID                         │          │
│  │  3. 查找/创建本地用户                    │          │
│  │  4. 执行 CRUD 操作                       │          │
│  │  5. 返回数据                             │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

### **关键流程**

1. **Roamio 用户登录 QQ**，获取包含 `unionid` 的 JWT Token
2. **Roamio 前端调用 Ralendar 的 Fusion API**，携带 Token 和 `unionid`
3. **Ralendar 验证 Token**，提取 `unionid`
4. **Ralendar 查找本地用户**：
   - 如果有 `unionid` 匹配的 `SocialAccount`，使用该用户
   - 如果没有，创建新用户并关联 `unionid`
5. **执行 CRUD 操作**，返回数据给 Roamio

---

## 🚀 接入新应用

### **场景：为 Rote（笔记应用）接入 Fusion API**

#### **第一步：确认 Rote 已实现统一认证**

参考 [`AUTH_STANDARD.md`](./AUTH_STANDARD.md)：

- [ ] Rote 支持 QQ 登录
- [ ] Rote 正确获取并保存 `unionid`
- [ ] Rote 的 JWT Token 中包含 `unionid`

#### **第二步：在 Rote 后端创建 Fusion API 目录**

```bash
mkdir -p backend/api/views/
mkdir -p backend/api/url_patterns/
```

#### **第三步：创建 Fusion API 视图**

**文件：** `backend/api/views/fusion.py`

```python
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from api.models import Note  # Rote 的笔记模型

logger = logging.getLogger('django')

def get_user_by_unionid_or_openid(request):
    """
    3-tier user matching logic:
    1. UnionID (from request.data or request.GET or token.payload)
    2. OpenID (from request.data or request.GET or token.payload)
    3. Authenticated user (from JWT Token)
    """
    # Try UnionID first (most reliable for cross-app)
    unionid = (request.data.get('unionid') or 
               request.GET.get('unionid') or 
               (hasattr(request.user, 'auth') and getattr(request.user.auth, 'unionid', None)))
    
    if unionid:
        social = SocialAccount.objects.filter(unionid=unionid).first()
        if social:
            logger.info(f"✅ User matched by UnionID: {unionid}")
            return social.user
    
    # Try OpenID (app-specific)
    openid = (request.data.get('openid') or 
              request.GET.get('openid') or 
              (hasattr(request.user, 'auth') and getattr(request.user.auth, 'openid', None)))
    
    if openid:
        social = SocialAccount.objects.filter(openid=openid).first()
        if social:
            logger.info(f"✅ User matched by OpenID: {openid}")
            return social.user
    
    # Fallback to authenticated user
    if request.user.is_authenticated:
        logger.info(f"✅ User matched by JWT Token: {request.user.id}")
        return request.user
    
    return None

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_notes(request):
    """
    GET:  获取用户的所有笔记
    POST: 创建新笔记
    """
    user = get_user_by_unionid_or_openid(request)
    if not user:
        return Response({
            'error': '用户未找到',
            'code': 'USER_NOT_FOUND'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        # 获取笔记列表
        notes = Note.objects.filter(user=user).order_by('-created_at')
        data = [
            {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat(),
            }
            for note in notes
        ]
        return Response({'notes': data}, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # 创建笔记
        title = request.data.get('title')
        content = request.data.get('content')
        
        if not title:
            return Response({
                'error': '标题不能为空',
                'code': 'NOTE_CREATE_INVALID_TITLE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        note = Note.objects.create(
            user=user,
            title=title,
            content=content or ''
        )
        
        return Response({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_note(request, note_id):
    """
    GET:    获取单个笔记详情
    PUT:    更新笔记
    DELETE: 删除笔记
    """
    user = get_user_by_unionid_or_openid(request)
    if not user:
        return Response({
            'error': '用户未找到',
            'code': 'USER_NOT_FOUND'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        note = Note.objects.get(id=note_id, user=user)
    except Note.DoesNotExist:
        return Response({
            'error': '笔记未找到',
            'code': 'NOTE_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        note.title = request.data.get('title', note.title)
        note.content = request.data.get('content', note.content)
        note.save()
        
        return Response({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'updated_at': note.updated_at.isoformat(),
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

#### **第四步：配置 URL 路由**

**文件：** `backend/api/url_patterns/fusion.py`

```python
from django.urls import path
from api.views.fusion import manage_notes, manage_note

urlpatterns = [
    path('notes/', manage_notes, name='manage_notes'),
    path('notes/<int:note_id>/', manage_note, name='manage_note'),
]
```

**主 URL 配置：** `backend/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    # ... 其他路由
    path('api/v1/fusion/', include('api.url_patterns.fusion')),
]
```

#### **第五步：测试 API**

```bash
# 获取笔记列表
curl -X GET "https://rote.example.com/api/v1/fusion/notes/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"unionid": "UID_12345"}'

# 创建笔记
curl -X POST "https://rote.example.com/api/v1/fusion/notes/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "unionid": "UID_12345",
    "title": "我的第一篇笔记",
    "content": "今天天气真好"
  }'
```

---

## 📚 标准 CRUD 接口

### **接口设计模板**

| 操作 | 方法 | URL | 说明 |
|------|------|-----|------|
| 列表 | `GET` | `/api/v1/fusion/{resource}/` | 获取用户的所有资源 |
| 创建 | `POST` | `/api/v1/fusion/{resource}/` | 创建新资源 |
| 详情 | `GET` | `/api/v1/fusion/{resource}/{id}/` | 获取单个资源 |
| 更新 | `PUT` | `/api/v1/fusion/{resource}/{id}/` | 更新资源 |
| 删除 | `DELETE` | `/api/v1/fusion/{resource}/{id}/` | 删除资源 |
| 批量创建 | `POST` | `/api/v1/fusion/{resource}/batch/` | 批量创建 |

### **请求示例**

**创建事件（POST）：**
```json
{
  "unionid": "UID_12345",
  "title": "会议",
  "start_time": "2025-11-10T14:00:00Z",
  "end_time": "2025-11-10T15:00:00Z"
}
```

**更新事件（PUT）：**
```json
{
  "unionid": "UID_12345",
  "title": "项目讨论会议"
}
```

**删除事件（DELETE）：**
```
DELETE /api/v1/fusion/events/123/?unionid=UID_12345
```

---

## 🔄 数据同步策略

### **策略 1：实时同步（推荐）**

- Roamio 创建事件时，直接调用 Ralendar 的 Fusion API
- 优点：数据实时一致
- 缺点：依赖网络，需要处理失败重试

### **策略 2：定时同步**

- Roamio 本地创建事件，每 5 分钟同步到 Ralendar
- 优点：离线可用
- 缺点：数据延迟

### **策略 3：双向同步**

- Roamio 和 Ralendar 都有本地数据库
- 定时双向同步，解决冲突
- 优点：两端都可离线使用
- 缺点：复杂度高

### **推荐方案**

对于 Roamio + Ralendar：
- **Roamio → Ralendar**: 实时同步（创建/更新/删除时立即调用 Fusion API）
- **Ralendar → Roamio**: 不同步（Ralendar 是主应用）

---

## 🔒 安全性

### **1. JWT Token 验证**

所有 Fusion API 必须使用 `@permission_classes([IsAuthenticated])`

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notes(request):
    # Token 已验证，request.user 可用
    pass
```

### **2. UnionID 验证**

```python
def get_user_by_unionid_or_openid(request):
    unionid = request.data.get('unionid')
    
    # 验证 UnionID 格式
    if unionid and not unionid.startswith('UID_'):
        return None
    
    # 查找用户
    social = SocialAccount.objects.filter(unionid=unionid).first()
    return social.user if social else None
```

### **3. 权限检查**

```python
# 确保用户只能访问自己的数据
try:
    note = Note.objects.get(id=note_id, user=user)  # ⚠️ 必须加 user 过滤
except Note.DoesNotExist:
    return Response({'error': '笔记未找到'}, status=404)
```

### **4. 速率限制**

在 `settings.py` 中配置：

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',  # 每天最多 1000 次请求
        'anon': '100/day',   # 匿名用户每天 100 次
    }
}
```

---

## ✅ 检查清单

接入新应用时，确认：

- [ ] 实现了 `get_user_by_unionid_or_openid` 函数
- [ ] 所有 Fusion API 使用 `@permission_classes([IsAuthenticated])`
- [ ] URL 遵循 `/api/v1/fusion/{resource}/` 格式
- [ ] 支持标准 CRUD 操作（GET/POST/PUT/DELETE）
- [ ] 错误响应包含 `error` 和 `code`
- [ ] 权限检查（用户只能访问自己的数据）
- [ ] 有完整的 API 文档

---

## 📞 联系方式

**规范维护者**: Roamio 核心团队  
**问题反馈**: 在项目根目录创建 Issue

---

## 📝 更新日志

### v1.0 (2025-11-09)
- 初始版本
- 基于 Ralendar + Roamio 实践经验整理

