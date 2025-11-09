# 📚 Roamio 大家族 - 技术规范中心

> **让每个新项目都站在巨人的肩膀上**

---

## 🎯 为什么需要规范？

随着 Roamio 大家族的成长（Ralendar、Roamio、Rote、Routes...），我们需要：

- ✅ **统一的认证方式**：所有应用共享用户身份
- ✅ **一致的 API 设计**：降低学习成本，提升开发效率
- ✅ **标准化的代码风格**：易于维护和交接
- ✅ **可复用的最佳实践**：避免重复踩坑

**规范不是限制，而是加速器！** 🚀

---

## 📋 规范目录

### **🔴 核心规范（必读）**

| 规范 | 说明 | 状态 | 优先级 |
|------|------|------|--------|
| [**AUTH_STANDARD.md**](./AUTH_STANDARD.md) | 统一认证规范（UnionID/OpenID/JWT） | ✅ 已完成 | P0 |
| [**API_NAMING.md**](./API_NAMING.md) | API 命名和 RESTful 规范 | ✅ 已完成 | P0 |
| [**FUSION_API_GUIDE.md**](./FUSION_API_GUIDE.md) | 跨应用集成指南 | ✅ 已完成 | P0 |

### **🟡 补充规范（推荐）**

| 规范 | 说明 | 状态 | 优先级 |
|------|------|------|--------|
| **DATABASE_STANDARD.md** | 数据库设计规范 | 🚧 待编写 | P1 |
| **FRONTEND_STANDARD.md** | 前端组件和状态管理规范 | 🚧 待编写 | P1 |
| **DEPLOYMENT_STANDARD.md** | 部署和环境变量规范 | 🚧 待编写 | P1 |

### **🟢 高级规范（可选）**

| 规范 | 说明 | 状态 | 优先级 |
|------|------|------|--------|
| **MICROSERVICE_COMMUNICATION.md** | 微服务通信规范 | 📝 待编写 | P2 |
| **MONITORING_STANDARD.md** | 监控和日志规范 | 📝 待编写 | P2 |

---

## 🚀 快速开始

### **场景 1：我要开发一个新应用（如 Rote）**

**第一步：** 阅读核心规范
```bash
cat docs/standards/AUTH_STANDARD.md       # 了解认证方式
cat docs/standards/API_NAMING.md          # 了解 API 命名
cat docs/standards/FUSION_API_GUIDE.md    # 了解如何接入 Fusion
```

**第二步：** 复制代码模板
```bash
# 复制 Ralendar 的认证代码作为起点
cp -r backend/api/views/auth.py my_project/api/views/
cp -r backend/api/views/fusion.py my_project/api/views/
```

**第三步：** 修改为自己的业务逻辑
```python
# 示例：将 Event 模型改为 Note 模型
from api.models import Note  # 你的模型

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_notes(request):
    user = get_user_by_unionid_or_openid(request)
    # ... 你的业务逻辑
```

**第四步：** 测试 API
```bash
curl -X GET "https://your-app.com/api/v1/fusion/notes/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"unionid": "UID_12345"}'
```

---

### **场景 2：我要在 Roamio 中调用 Ralendar 的日历**

**第一步：** 确保 Roamio 的 JWT Token 包含 `unionid`

**第二步：** 在 Roamio 前端调用 Fusion API
```javascript
// Roamio 前端代码
import axios from 'axios';

async function createEventInRalendar(eventData) {
  const token = localStorage.getItem('jwt_token');
  const unionid = localStorage.getItem('unionid');  // 登录时保存
  
  const response = await axios.post(
    'https://ralendar.example.com/api/v1/fusion/events/',
    {
      unionid: unionid,
      title: eventData.title,
      start_time: eventData.start_time,
      end_time: eventData.end_time,
    },
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    }
  );
  
  return response.data;
}
```

**第三步：** 处理响应和错误
```javascript
try {
  const event = await createEventInRalendar({
    title: '会议',
    start_time: '2025-11-10T14:00:00Z',
    end_time: '2025-11-10T15:00:00Z',
  });
  console.log('✅ 事件创建成功：', event);
} catch (error) {
  if (error.response?.data?.code === 'USER_NOT_FOUND') {
    console.error('❌ 用户未找到，请先登录');
  } else {
    console.error('❌ 创建失败：', error.message);
  }
}
```

---

### **场景 3：我要修改现有的 API**

**第一步：** 检查是否会破坏兼容性

- ✅ 添加新字段（向后兼容）
- ✅ 添加新接口（向后兼容）
- ❌ 删除字段（不兼容，需要升级到 v2）
- ❌ 修改字段类型（不兼容，需要升级到 v2）

**第二步：** 如果不兼容，创建新版本

```python
# 保留旧版本
urlpatterns = [
    path('api/v1/events/', views_v1.get_events),  # 旧版本
    path('api/v2/events/', views_v2.get_events),  # 新版本
]
```

**第三步：** 通知其他团队

在项目 README 或 Slack 中告知：
```
🚨 API 变更通知：
- /api/v1/events/ 将于 2026-01-01 下线
- 请迁移到 /api/v2/events/
- 变更详情：字段 'time' 拆分为 'start_time' 和 'end_time'
```

---

## 🛠️ 开发工具

### **API 测试工具**

```bash
# 使用 curl
curl -X GET "https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"unionid": "UID_12345"}'

# 使用 Postman
# 导入 docs/postman/Roamio_API_Collection.json
```

### **代码检查工具**

```bash
# Python 代码风格检查
flake8 backend/

# JavaScript 代码风格检查
npm run lint
```

---

## 🎓 最佳实践

### **1. 认证相关**

✅ **好的做法：**
```python
# 优先使用 UnionID 进行跨应用用户匹配
unionid = request.data.get('unionid')
social = SocialAccount.objects.filter(unionid=unionid).first()
```

❌ **不好的做法：**
```python
# 不要直接使用 user_id（不同应用的 user_id 不同）
user_id = request.data.get('user_id')
user = User.objects.get(id=user_id)  # ❌ 错误！
```

### **2. API 设计**

✅ **好的做法：**
```python
# RESTful 风格
GET    /api/v1/events/       # 列表
POST   /api/v1/events/       # 创建
GET    /api/v1/events/123/   # 详情
PUT    /api/v1/events/123/   # 更新
DELETE /api/v1/events/123/   # 删除
```

❌ **不好的做法：**
```python
# 不要使用动词
GET /api/v1/getEvents/
POST /api/v1/createEvent/
```

### **3. 错误处理**

✅ **好的做法：**
```python
return Response({
    'error': '事件未找到',
    'code': 'EVENT_NOT_FOUND',
    'details': {'event_id': 999}
}, status=status.HTTP_404_NOT_FOUND)
```

❌ **不好的做法：**
```python
return Response({'error': 'not found'}, status=404)  # 缺少 code 和 details
```

---

## 📞 联系和贡献

### **有问题？**

1. **查阅规范文档**：大多数问题都能在规范中找到答案
2. **在 Slack/微信群提问**：@核心团队成员
3. **创建 Issue**：在 GitHub 提交问题

### **发现规范不合理？**

1. **提出改进建议**：在项目中创建 Issue
2. **讨论方案**：核心团队会评审
3. **更新规范**：达成共识后更新文档

### **贡献新规范**

1. **Fork 项目**
2. **编写规范**（参考现有格式）
3. **提交 Pull Request**
4. **等待 Review**

---

## 📈 规范更新流程

```
1. 提出问题/建议 → 2. 核心团队讨论 → 3. 更新规范 → 4. 通知所有团队
```

**规范版本号：**
- **v1.0 → v1.1**：小修改（修正错误、补充示例）
- **v1.x → v2.0**：重大变更（不兼容的修改）

---

## 🎯 下一步计划

### **近期（1 个月内）**

- [ ] 完成数据库设计规范（`DATABASE_STANDARD.md`）
- [ ] 完成前端组件规范（`FRONTEND_STANDARD.md`）
- [ ] 为 Rote 接入 Fusion API

### **中期（3 个月内）**

- [ ] 完成部署规范（`DEPLOYMENT_STANDARD.md`）
- [ ] 建立 CI/CD 流程
- [ ] 接入更多应用（Routes、Rapture）

### **长期（6 个月内）**

- [ ] 完善监控和日志规范
- [ ] 建立微服务架构
- [ ] 开发者工具和 SDK

---

## 📝 文档贡献者

- **Ralendar Team**: 认证规范、API 规范、Fusion API
- **Roamio Team**: 跨应用集成实践

---

**🚀 让我们一起建设一个规范、高效、可扩展的技术生态！**

