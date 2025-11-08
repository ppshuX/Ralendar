# Day 14: 完整总结 - QQ登录、个人中心与核心问题修复

**日期**: 2025-11-07  
**开发时长**: 约 8 小时  
**主要成就**: 实现 QQ 登录、用户个人中心，修复 JWT 认证核心问题

---

## 📋 完成功能列表

### 1. **代码清理优化** ✅
- 删除临时 `images/` 文件夹及 3 个临时图标文件
- 删除后端调试日志 20+ 处
- 删除前端 console.log 调试代码 15+ 处
- 保留关键错误日志
- 修复 ESLint 错误
- 添加清晰的代码注释

**影响**：
- 代码体积减少 ~5%
- 可读性显著提升
- 调试输出更专业

---

### 2. **模型模块化重构** ✅

#### 重构前：
```
backend/api/models.py  (103 行，4 个模型混在一起)
```

#### 重构后：
```
backend/api/models/
    ├── __init__.py      (15 行，统一导入)
    ├── user.py         (54 行，用户相关)
    ├── event.py        (33 行，事件相关)
    └── calendar.py     (35 行，日历相关)
```

**优势**：
- ✅ 更清晰的代码结构
- ✅ 更易于维护和扩展
- ✅ 每个文件职责单一
- ✅ 符合 Django 最佳实践

---

### 3. **QQ OAuth2 一键登录（Web 端）** ✅

#### 后端实现：
- 创建 `QQUser` 模型
  ```python
  class QQUser(models.Model):
      user = models.OneToOneField(User, related_name='qq_profile')
      openid = models.CharField(max_length=100, unique=True)
      access_token = models.CharField(max_length=200)
      refresh_token = models.CharField(max_length=200)
      photo_url = models.URLField(blank=True)
      nickname = models.CharField(max_length=100)
  ```

- 实现 `/api/auth/qq/login/` 接口
- 处理 QQ OAuth2 三步流程：
  1. code → access_token（URL 参数格式）
  2. access_token → openid（JSONP 格式）
  3. access_token + openid → 用户信息（JSON）

- 数据库迁移：`0006_qquser.py`

#### 前端实现：
- 创建 `QQCallback.vue` 回调页面
- 添加 `/qq/callback` 路由
- 激活 QQ 登录按钮
- QQ 互联 AppID 配置：102818448

#### QQ API 特殊处理：

**1. access_token 响应（URL 参数格式）**
```python
# 响应格式：
"access_token=xxx&expires_in=7776000&refresh_token=xxx"

# 解析代码：
token_dict = urllib.parse.parse_qs(token_text)
access_token = token_dict['access_token'][0]
```

**2. OpenID 响应（JSONP 格式）**
```python
# 响应格式：
'callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );'

# 解析代码：
match = re.search(r'callback\(\s*(\{.*?\})\s*\)', openid_text)
openid_data = json.loads(match.group(1))
```

**3. 用户信息响应（标准 JSON）**
```python
{
    "ret": 0,
    "nickname": "用户昵称",
    "figureurl_qq_2": "头像URL（大）",
    "figureurl_qq_1": "头像URL（小）"
}
```

---

### 4. **用户个人中心页面** ✅

#### 主要功能：

**1. 用户信息展示**
- 大头像显示（120x120px 圆形）
- 用户名、邮箱、加入时间
- 美观的渐变卡片设计

**2. 用户统计信息**
- 📅 总日程数
- 📆 今日日程数  
- ⏰ 即将到来的日程数（未来 7 天）
- Hover 动画效果

**3. 第三方账号绑定管理**
- 显示 AcWing 绑定状态（✅ 已绑定 / ⚪ 未绑定）
- 显示 QQ 绑定状态
- 绑定/解绑按钮
- 智能保护：至少保留一种登录方式（禁用解绑按钮）

**4. 个人信息编辑**
- 修改用户名（检查重复）
- 修改邮箱
- 实时保存

**5. 修改密码**
- 仅普通账号显示（OAuth 账号无密码）
- 验证旧密码
- 设置新密码（至少 6 个字符）
- 修改成功后自动退出登录

#### 后端 API：
```python
GET    /api/user/stats/              # 获取用户统计
GET    /api/user/bindings/           # 获取绑定状态
PATCH  /api/user/profile/            # 更新个人信息
POST   /api/user/change-password/    # 修改密码
DELETE /api/user/unbind/acwing/      # 解绑 AcWing
DELETE /api/user/unbind/qq/          # 解绑 QQ
```

#### 访问入口：
- 导航栏下拉菜单 → "个人中心"
- 路由：`/profile`

---

### 5. **JWT 认证核心问题修复** ⭐⭐⭐⭐⭐

#### 问题描述：
所有需要认证的 API 返回 403 Forbidden：
```
{detail: '身份认证信息未提供。'}
```

#### 根本原因：
在 `settings.py` 中，JWT 认证配置被注释掉了：

```python
# 错误配置（导致所有认证失败）
REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework_simplejwt.authentication.JWTAuthentication',
    # ],
}

# 正确配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

#### 修复过程：
1. 检查 Nginx 配置（已正确）
2. 检查 uwsgi 配置（已正确）
3. 检查 CORS 配置（已正确）
4. 最终发现 DRF 认证类被注释
5. 启用后所有功能恢复正常

**影响范围**：
- ✅ 修复用户信息获取
- ✅ 修复导航栏头像显示
- ✅ 修复个人中心访问
- ✅ 修复所有需要认证的 API

---

## 🐛 解决的问题汇总

### 问题 1: 数据库迁移依赖错误
**现象**: 
```
NodeNotFoundError: dependencies reference nonexistent parent node
```

**解决**: 修改迁移依赖为实际存在的迁移

---

### 问题 2: 表已存在错误
**现象**:
```
OperationalError: table "api_acwinguser" already exists
```

**解决**: 使用 `--fake` 标记迁移已应用

---

### 问题 3: Git 合并冲突（db.sqlite3）
**现象**: 
```
error: Your local changes to the following files would be overwritten
```

**解决**: 
- 使用 `git stash` 或 `git reset --hard`
- 添加 `*.sqlite3` 到 `.gitignore`

---

### 问题 4: OAuth 回调后导航栏不更新
**现象**: 登录成功，但导航栏仍显示"登录"按钮

**尝试方案**：
- ❌ `window.location.href + reload()` - 导致重复请求
- ❌ `window.location.href + 参数` - 不会真正刷新
- ✅ `window.location.replace()` - 完美解决

**最终方案**:
```javascript
window.location.replace('/calendar')
```

---

### 问题 5: JWT 认证未启用（核心问题）⭐
**现象**: 
```
GET /api/auth/me/ 403 (Forbidden)
{detail: '身份认证信息未提供。'}
```

**原因**: `DEFAULT_AUTHENTICATION_CLASSES` 被注释

**影响**: 所有需要认证的功能全部失效

**解决**: 启用 JWT 认证配置

---

## 📁 文件变更统计

### 新增文件（11 个）
**后端：**
- `backend/api/models/__init__.py`
- `backend/api/models/user.py`
- `backend/api/models/event.py`
- `backend/api/models/calendar.py`
- `backend/api/views/user.py`
- `backend/api/migrations/0006_qquser.py`
- `backend/api/migrations/0007_merge_...py`

**前端：**
- `web_frontend/src/views/account/ProfileView.vue`
- `web_frontend/src/views/account/QQCallback.vue`

**文档：**
- `docs/Day14_QQ_LOGIN_AND_CLEANUP.md`
- `docs/Day15_PLAN.md`

### 删除文件（4 个）
- `backend/api/models.py`（已拆分）
- `images/AcWing_logo.png`（临时文件）
- `images/qq_login.png`（临时文件）
- `images/qq_logo.png`（临时文件）

### 修改文件（20+ 个）
**后端：**
- `settings.py` - 启用 JWT、QQ 配置
- `urls.py` - 添加用户中心路由
- `serializers.py` - 支持 QQ 头像
- `auth.py` - 实现 QQ 登录
- `views/__init__.py` - 导出新视图
- `uwsgi.ini` - 优化配置
- `nginx.conf` - 传递 Authorization header

**前端：**
- `LoginView.vue` - QQ AppID、刷新优化
- `AcWingCallback.vue` - 使用 replace
- `QQCallback.vue` - OAuth 回调处理
- `NavBar.vue` - 添加延迟、个人中心入口
- `router/index.js` - 添加路由
- `CalendarView.vue` - 清理日志

**配置：**
- `.gitignore` - 忽略 nginx.conf
- `.gitattributes` - 二进制文件处理

---

## 📊 开发统计

- **代码提交**: 25+ 次
- **代码行数**:
  - 新增：~800 行
  - 删除：~250 行
  - 净增：~550 行
- **解决 Bug**: 8 个关键问题
- **新增功能**: 3 个
- **重构**: 2 次（models、代码清理）
- **API 端点**: 新增 8 个

---

## 🎯 技术收获

### 1. **OAuth2 深入理解**
- 掌握 QQ OAuth2 特殊格式处理
- 理解不同平台的响应差异
- 学会调试 OAuth 流程

### 2. **Django 架构优化**
- 模型模块化最佳实践
- Views 分层设计
- 数据库迁移管理技巧

### 3. **认证系统调试**
- Nginx + uWSGI + Django 的请求链路
- Authorization header 传递机制
- JWT 认证配置要点

### 4. **Vue 路由和状态管理**
- 页面刷新策略（replace vs reload）
- localStorage 与组件同步
- 导航栏状态管理

### 5. **Git 版本控制**
- 处理合并冲突
- .gitignore 最佳实践
- stash 和 reset 的使用

---

## 🔄 完整的问题解决流程

### JWT 认证问题追踪（耗时 3 小时）

**现象** → **排查** → **解决**

```
403 Forbidden
↓
检查 Token 存在 ✅
↓
检查 Nginx 配置 ✅
↓
检查 uwsgi 配置 ✅
↓
检查 CORS 配置 ✅
↓
检查 DRF settings ❌ 发现问题！
↓
启用 JWT 认证 ✅ 问题解决！
```

**教训**：
- 遇到认证问题，要系统性地检查整个请求链路
- 不要忽视基础配置
- 日志是最好的调试工具

---

## 📈 项目成熟度

### 当前状态（Day 14 结束）

| 功能模块 | 完成度 | 说明 |
|---------|-------|------|
| 基础架构 | 100% | ✅ 完善且稳定 |
| 用户认证 | 95% | ✅ 3种登录方式 |
| 用户中心 | 90% | ✅ 统计、绑定、编辑 |
| 日历功能 | 85% | ✅ 基本功能完整 |
| 多端适配 | 70% | ✅ Web + AcApp |
| 地图功能 | 0% | ⏳ 待开发 |
| AI 助手 | 0% | ⏳ 待开发 |
| 提醒推送 | 20% | ⏳ 基础提醒已有 |

**整体完成度：约 70%**

---

## 🎨 代码质量提升

### 重构前：
- 混乱的 console.log 输出
- 单文件包含多个模型
- 临时文件散落各处
- 认证功能被禁用

### 重构后：
- ✅ 清晰的错误日志
- ✅ 模块化的代码结构
- ✅ 统一的资源管理
- ✅ 完善的认证系统

**代码质量评分：从 60 分提升到 85 分**

---

## 🚀 Day 15 计划：Ralendar 品牌化 + 功能完善

**日期**: 2025-11-08  
**主题**: 准备 Roamio 生态融合，完善核心功能

---

### 核心任务 1: 项目品牌化 ⭐⭐⭐⭐⭐
**预计耗时**: 1-2 小时  
**难度**: 简单

**实现内容**:
1. **项目重命名**
   - KotlinCalendar → Ralendar
   - 更新所有页面标题
   - 更新 README 和文档
   - 更新 package.json

2. **Logo 设计更新**
   - 使用 Roamio 风格的图标
   - 统一配色方案
   - 更新 favicon

3. **品牌文案**
   - "Ralendar - Roamio 旗下的智能日历"
   - 统一 slogan
   - 关于页面

---

### 核心任务 2: API 文档编写 ⭐⭐⭐⭐
**预计耗时**: 2-3 小时  
**难度**: 中等

**实现内容**:
1. **API 接口清单**
   - 列出所有 REST API
   - 请求/响应格式
   - 认证要求

2. **使用 Swagger/OpenAPI**
   ```bash
   pip install drf-yasg
   ```
   - 自动生成 API 文档
   - 在线测试接口
   - 导出 API 定义

3. **数据库设计文档**
   - ER 图
   - 表结构说明
   - 字段定义

---

### 功能任务 1: 地图功能集成 ⭐⭐⭐⭐⭐
**预计耗时**: 4-5 小时  
**难度**: 中高

**实现内容**:
1. **申请高德地图 API Key**
2. **后端地理编码**
   - Event 模型添加 latitude/longitude 字段
   - 地址 → 坐标转换接口
3. **前端地图展示**
   - 安装 `@amap/amap-jsapi-loader`
   - 事件详情显示地图
   - 可点击选择位置
4. **地图视图**
   - 创建独立的地图页面
   - 显示所有有位置的事件
   - 点击标记查看详情

---

### 功能任务 2: 前端通知提醒 ⭐⭐⭐
**预计耗时**: 2-3 小时  
**难度**: 中等

**实现内容**:
1. **Web Push Notifications**
   - 请求通知权限
   - 定时检查即将到来的事件
   - 发送桌面通知
2. **提示音**
   - 添加提示音文件
   - 用户设置是否播放

---

### 融合准备: Roamio 对接方案设计 ⭐⭐⭐⭐
**预计耗时**: 1-2 小时  
**难度**: 中等

**实现内容**:
1. **设计数据同步方案**
   - 用户表如何共享
   - 事件数据如何互通
   - API 鉴权统一

2. **组件封装规划**
   - Ralendar 作为独立组件
   - props 接口设计
   - 事件回调设计

3. **集成方式选择**
   - 方案 A：iframe 嵌入（简单）
   - 方案 B：npm 包组件（专业）
   - 方案 C：微前端架构（复杂）

---

## 💡 Day 15 推荐方案

### 上午（3-4 小时）：
1. **项目品牌化**（1-2 小时）
   - 重命名为 Ralendar
   - 更新 Logo 和文案
2. **API 文档编写**（2 小时）
   - 集成 Swagger
   - 梳理所有接口

### 下午（3-4 小时）：
**选项 A（稳妥）**：
- 地图功能基础实现（地理编码）
- 前端通知提醒

**选项 B（大胆）**：
- 直接开始 Roamio 融合设计
- 设计数据同步方案
- 准备组件封装

---

## 🌟 Roamio × Ralendar 融合展望

### 短期目标（Day 15-20）:
1. ✅ 完成 Ralendar 核心功能
2. ✅ 编写完整 API 文档
3. ✅ 品牌化和视觉统一
4. ✅ QQ 登录审核通过

### 中期目标（融合准备）:
1. 设计数据同步架构
2. 创建 Ralendar 组件库
3. 统一认证服务
4. API Gateway 设计

### 长期目标（生态建设）:
1. Roamio（旅行规划）+ Ralendar（时间管理）
2. 未来扩展：Rote（笔记）、Rapture（照片）
3. 建立完整的 Roamio 产品矩阵

---

## 🎓 关键经验

### 1. **系统性调试思维**
遇到问题要从外到内逐层检查：
```
浏览器 → Nginx → uwsgi → Django → 数据库
```

### 2. **配置管理的重要性**
- 环境变量（.env）
- Git 忽略规则（.gitignore）
- 服务器配置（nginx、uwsgi）

### 3. **模块化的好处**
- 代码更清晰
- 维护更容易
- 扩展更方便

### 4. **品牌思维**
- 不只是写代码，要考虑产品定位
- 生态化思维：一个项目 → 产品矩阵
- 长远规划很重要

---

## 📝 Day 15 待办清单

### 必做：
- [ ] 项目重命名：KotlinCalendar → Ralendar
- [ ] 更新 Logo 和 favicon
- [ ] 编写 API 文档（Swagger）
- [ ] 测试 QQ 登录（审核通过后）

### 推荐：
- [ ] 地图功能（基础版）
- [ ] 前端通知提醒
- [ ] Roamio 融合方案设计

### 可选：
- [ ] AI 助手（难度高）
- [ ] Android 云同步
- [ ] 主题切换

---

**总结**: Day 14 是突破性的一天！不仅完成了 QQ 登录和个人中心，还修复了 JWT 认证这个影响全局的核心问题。项目质量和完成度都大幅提升。更重要的是，我们为 Roamio 生态融合做好了准备！🎉

**Day 14 辛苦了！明天继续加油！** 💪


