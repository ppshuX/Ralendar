# Day 12: AcWing 一键登录实现

**日期**: 2025-11-07  
**主要任务**: 实现 AcApp 端 AcWing OAuth2 一键登录功能

---

## 📋 完成功能

### 1. **后端 OAuth2 集成**
- ✅ 创建 `AcWingUser` 模型，存储 AcWing 用户信息
- ✅ 实现 `/api/auth/acwing/login/` 接口
- ✅ 实现 `/api/oauth2/receive_code/` 回调接口
- ✅ 集成 JWT token 生成和返回
- ✅ 使用环境变量管理 AcWing AppID 和 Secret

### 2. **前端授权流程**
- ✅ 集成 AcWingOS OAuth2 API
- ✅ 实现自动登录检查和 token 验证
- ✅ 实现授权回调处理
- ✅ 正确处理 AcWing 回调的 JSON 响应
- ✅ Token 无效时自动触发重新授权

### 3. **Vuex Store 模块化**
- ✅ 将原有 store 拆分为 `user`、`events`、`router` 三个模块
- ✅ 修复所有组件的状态访问路径
- ✅ 保持向后兼容（未使用 `namespaced`）

---

## 🐛 遇到的问题和解决方案

### 问题 1: CORS 错误
**现象**: `Access-Control-Allow-Origin` 缺失

**原因**: `redirect_uri` 路径不正确，指向了前端路由而非 API 端点

**解决方案**:
```javascript
// 错误
const redirect_uri = 'https://app7626.acapp.acwing.com.cn/'

// 正确
const redirect_uri = 'https://app7626.acapp.acwing.com.cn/api/oauth2/receive_code/'
```

---

### 问题 2: 回调返回 HTML 而非 JSON
**现象**: `code` 和 `state` 为 `undefined`

**原因**: Django 视图返回了 HTML 页面，而 AcWingOS 需要纯 JSON 响应

**解决方案**:
```python
# backend/api/views/oauth_callback.py
from django.http import JsonResponse

def acwing_oauth_callback(request):
    code = request.GET.get('code', '')
    state = request.GET.get('state', '')
    return JsonResponse({
        'code': code,
        'state': state
    })
```

---

### 问题 3: 登录成功但无界面显示
**现象**: Token 存储成功，但页面空白

**原因**: Vuex 模块化后，`MainView.vue` 使用旧的状态路径

**解决方案**:
```vue
<!-- 错误 -->
<CalendarGrid v-if="$store.state.router_name === 'calendar'" />

<!-- 正确 -->
<CalendarGrid v-if="$store.state.router.router_name === 'calendar'" />
```

---

### 问题 4: EventList 显示空事件
**现象**: 列表显示 3 个空事件，新事件不显示

**原因**: `EventList.vue` 的 `mapState` 访问路径错误

**解决方案**:
```javascript
// 错误
...mapState(['events', 'loading'])

// 正确
...mapState({
  events: state => state.events.events,
  loading: state => state.events.loading
})
```

---

### 问题 5: 重装应用不触发重新授权
**现象**: 卸载重装后直接使用旧 token，不请求授权

**原因**: 没有验证 token 有效性

**解决方案**:
```javascript
async checkAndLogin() {
  const token = localStorage.getItem('access_token')
  if (!token) {
    this.requestAcWingLogin()
    return
  }
  
  // 验证 token 有效性
  try {
    const response = await fetch('https://app7626.acapp.acwing.com.cn/api/auth/me/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      const user = await response.json()
      console.log('✅ Token 有效，用户:', user.username)
      store.dispatch('fetchEvents')
    } else {
      console.log('❌ Token 无效，清除并重新授权...')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      this.requestAcWingLogin()
    }
  } catch (error) {
    console.error('Token 验证失败:', error)
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    this.requestAcWingLogin()
  }
}
```

---

## 🔧 关键技术要点

### 1. **AcWing OAuth2 流程**
```
1. 前端调用 AcWingOS.api.oauth2.authorize()
2. 用户授权后，AcWing 重定向到 redirect_uri，携带 code 和 state
3. 后端 receive_code 视图返回 JSON: {code, state}
4. 前端收到回调，调用 /api/auth/acwing/login/
5. 后端用 code 换取 access_token 和 openid
6. 后端用 access_token 获取用户信息
7. 后端创建/更新用户，生成 JWT token
8. 前端保存 token，跳转到主界面
```

### 2. **环境变量配置**
```python
# settings.py
import os
ACWING_APPID = os.environ.get('ACWING_APPID', '7626')
ACWING_SECRET = os.environ.get('ACWING_SECRET', '')
```

```bash
# .bashrc
export ACWING_SECRET="your_secret_here"
```

### 3. **Vuex 模块化最佳实践**
- 按功能拆分模块（user、events、router）
- 使用 `mapState`、`mapActions` 简化组件代码
- 模块间通过 `rootState` 访问其他模块
- 考虑向后兼容性，可选择不使用 `namespaced`

---

## 📁 主要代码变更

### 后端
- `backend/api/models.py`: 添加 `AcWingUser` 模型
- `backend/api/views/auth.py`: 添加 `acwing_login` 视图
- `backend/api/views/oauth_callback.py`: 添加回调处理
- `backend/api/urls.py`: 添加路由
- `backend/calendar_backend/settings.py`: 添加环境变量配置

### 前端
- `acapp_frontend/src/main.js`: 集成 OAuth2 授权流程和 token 验证
- `acapp_frontend/src/store/index.js`: 重构为模块化结构
- `acapp_frontend/src/store/modules/user.js`: 用户状态管理
- `acapp_frontend/src/store/modules/events.js`: 事件状态管理
- `acapp_frontend/src/store/modules/router.js`: 路由状态管理
- `acapp_frontend/src/views/MainView.vue`: 修复状态访问路径
- `acapp_frontend/src/components/EventList.vue`: 修复状态访问路径
- `acapp_frontend/src/components/CalendarGrid.vue`: 修复状态访问路径

### 配置
- `.gitignore`: 添加 `.env` 文件忽略

---

## 📊 开发统计

- **耗时**: ~3 小时
- **代码提交**: 5 次
- **解决的 Bug**: 5 个
- **新增文件**: 4 个
- **修改文件**: 10+ 个

---

## 🎯 技术收获

1. **OAuth2 实战经验**: 深入理解授权码模式的完整流程
2. **AcWingOS API**: 掌握 AcWing 平台的特殊回调处理方式
3. **Vuex 模块化**: 学会大型应用的状态管理最佳实践
4. **Token 验证**: 理解 JWT 生命周期和刷新机制
5. **调试技巧**: 使用 console.log 追踪 OAuth2 流程

---

## ✅ 测试验证

- ✅ 首次打开应用触发授权
- ✅ 授权成功后正确跳转
- ✅ Token 保存到 localStorage
- ✅ 用户信息正确显示
- ✅ 事件列表正常加载
- ✅ 创建/删除事件正常
- ✅ Token 失效后自动重新授权
- ✅ 重装应用后重新授权

---

## 🚀 下一步计划 (Day 13)

1. **QQ 一键登录（Web 端）** ⭐⭐⭐⭐
2. **地图功能集成** ⭐⭐⭐⭐
3. **AI 语音助手** ⭐⭐⭐⭐
4. **Android 端云同步** ⭐⭐⭐
5. **准备演示材料** ⭐⭐⭐

---

**总结**: Day 12 成功实现了 AcApp 端的 AcWing 一键登录功能，解决了多个状态管理和授权流程问题。现在用户可以在 AcWing 平台上无缝使用日历应用，体验流畅！🎉

