# 组件结构图

## 📂 完整组件目录结构

```
web_frontend/src/
├── components/
│   ├── auth/                    # 认证相关组件
│   │   ├── LoginForm.vue        # 登录表单 (93 行)
│   │   ├── RegisterForm.vue     # 注册表单 (135 行)
│   │   └── OAuthButtons.vue     # 第三方登录按钮 (104 行)
│   │
│   ├── profile/                 # 个人中心组件
│   │   ├── UserHeader.vue       # 用户头部 (114 行)
│   │   ├── UserStats.vue        # 用户统计 (68 行)
│   │   ├── AccountBindings.vue  # 账号绑定 (167 行)
│   │   ├── ProfileEditor.vue    # 信息编辑 (135 行)
│   │   └── PasswordChanger.vue  # 密码修改 (146 行)
│   │
│   ├── calendar/                # 日历相关组件
│   │   ├── Toolbar.vue          # 工具栏
│   │   ├── EventDialog.vue      # 日程对话框
│   │   └── EventDetail.vue      # 日程详情
│   │
│   ├── NavBar.vue               # 导航栏
│   └── ContentField.vue         # 内容容器
│
└── views/
    ├── account/
    │   ├── LoginView.vue        # 登录/注册页 (180 行) ✅ 重构
    │   ├── ProfileView.vue      # 个人中心页 (280 行) ✅ 重构
    │   ├── AcWingCallback.vue   # AcWing 回调
    │   └── QQCallback.vue       # QQ 回调
    │
    └── CalendarView.vue         # 日历主页 (360 行) ✅ 已优化
```

## 🔄 LoginView 组件关系图

```
┌─────────────────────────────────────┐
│         LoginView.vue               │
│         (主视图 - 180行)             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  判断: isLogin = true/false  │   │
│  └─────────────────────────────┘   │
│             ↓                      │
│    ┌────────┴────────┐             │
│    ↓                 ↓             │
│  ┌──────────┐   ┌──────────┐       │
│  │ LoginForm│   │ Register │       │
│  │   (93行) │   │   Form   │       │
│  │          │   │  (135行) │       │
│  └──────────┘   └──────────┘       │
│                                    │
│  ┌─────────────────────────────┐   │
│  │     OAuthButtons.vue        │   │
│  │         (104行)             │   │
│  │  ┌──────────┬──────────┐   │    │
│  │  │  AcWing  │   QQ     │   │   │
│  │  │  Button  │  Button  │   │   │
│  │  └──────────┴──────────┘   │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘

事件流:
  LoginForm/RegisterForm
      ↓ @submit
  LoginView (处理登录/注册)
      ↓ 成功
  跳转到 CalendarView

  OAuthButtons
      ↓ @acwing-login / @qq-login
  LoginView (跳转到第三方授权)
```

## 👤 ProfileView 组件关系图

```
┌──────────────────────────────────────────────────┐
│              ProfileView.vue                     │
│              (主视图 - 280行)                     │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │         UserHeader.vue (114行)            │ │
│  │  ┌──────────┐  ┌──────────────────────┐   │ │
│  │  │   头像    │  │ 用户名/邮箱/加入时间  │   │ │
│  │  └──────────┘  └──────────────────────┘   │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │         UserStats.vue (68行)              │ │
│  │  ┌──────┐  ┌──────┐  ┌──────────────┐    │ │
│  │  │日程数│  │今日  │  │即将到来      │    │ │
│  │  └──────┘  └──────┘  └──────────────┘    │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │      AccountBindings.vue (167行)          │ │
│  │  ┌──────────────┐  ┌──────────────┐       │ │
│  │  │   AcWing     │  │     QQ       │       │ │
│  │  │ [绑定/解绑]   │  │  [绑定/解绑]  │       │ │
│  │  └──────────────┘  └──────────────┘       │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │      ProfileEditor.vue (135行)            │ │
│  │  [用户名] [邮箱] [头像URL]                  │ │
│  │  [保存] [重置]                              │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │     PasswordChanger.vue (146行)           │ │
│  │  [当前密码] [新密码] [确认密码]             │ │
│  │  [修改密码] [重置]                          │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘

事件流:
  AccountBindings
      ↓ @bind / @unbind
  ProfileView (处理绑定/解绑逻辑)
      ↓
  调用后端 API

  ProfileEditor
      ↓ @submit
  ProfileView (更新用户信息)
      ↓
  调用后端 API

  PasswordChanger
      ↓ @submit
  ProfileView (修改密码)
      ↓
  调用后端 API → 跳转登录页
```

## 📅 CalendarView 组件关系图

```
┌─────────────────────────────────────────────────┐
│           CalendarView.vue (360行)              │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │         Toolbar.vue                     │   │
│  │  [添加] [刷新] [农历测试]                 │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌───────────────┬───────────────────────────┐ │
│  │               │                           │ │
│  │  FullCalendar │    日程列表侧边栏          │ │
│  │               │                           │ │
│  │  [日历视图]    │  ┌─────────────────────┐ │ │
│  │               │  │ 📋 日程 1           │ │ │
│  │               │  ├─────────────────────┤ │ │
│  │               │  │ 📋 日程 2           │ │ │
│  │               │  ├─────────────────────┤ │ │
│  │               │  │ 📋 日程 3           │ │ │
│  │               │  └─────────────────────┘ │ │
│  └───────────────┴───────────────────────────┘ │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │     EventDialog.vue (对话框)            │   │
│  │  [标题] [描述] [时间]                     │   │
│  │  [保存] [取消]                           │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │     EventDetail.vue (对话框)            │   │
│  │  显示日程详情 + 农历信息                  │   │
│  │  [编辑] [删除] [关闭]                     │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘

事件流:
  Toolbar
      ↓ @add / @refresh / @testLunar
  CalendarView

  EventDialog
      ↓ @save
  CalendarView (保存日程)
      ↓
  调用后端 API → 刷新日历

  EventDetail
      ↓ @edit / @delete
  CalendarView (编辑/删除日程)
      ↓
  调用后端 API → 刷新日历
```

## 🎯 组件设计原则

### 1. 单一职责 (Single Responsibility)
每个组件只负责一个明确的功能：
- ✅ `UserHeader` 只负责显示用户头部信息
- ✅ `LoginForm` 只负责登录表单
- ✅ `OAuthButtons` 只负责第三方登录按钮

### 2. 松耦合 (Loose Coupling)
组件之间通过 Props 和 Events 通信，不直接依赖：
```javascript
// 父组件
<AccountBindings 
  :bindings="bindings"
  @bind="handleBind"
  @unbind="handleUnbind"
/>

// 子组件
defineProps({ bindings: Object })
defineEmits(['bind', 'unbind'])
```

### 3. 高内聚 (High Cohesion)
相关的功能和样式都在同一个组件内：
```vue
<template>
  <!-- 模板 -->
</template>

<script setup>
  // 逻辑
</script>

<style scoped>
  /* 样式 */
</style>
```

### 4. 可复用性 (Reusability)
组件设计为通用的，可以在多个地方使用：
- `OAuthButtons` 可用于登录页、注册页、绑定页
- `PasswordChanger` 可独立用于密码修改功能

### 5. 易测试性 (Testability)
小组件更容易编写单元测试：
```javascript
import { mount } from '@vue/test-utils'
import LoginForm from '@/components/auth/LoginForm.vue'

test('LoginForm validates username', async () => {
  const wrapper = mount(LoginForm)
  // ... 测试逻辑
})
```

## 📊 组件大小统计

### Auth 组件
| 组件 | 行数 | 职责 |
|------|------|------|
| LoginForm | 93 | 登录表单 |
| RegisterForm | 135 | 注册表单 |
| OAuthButtons | 104 | 第三方登录 |
| **小计** | **332** | |

### Profile 组件
| 组件 | 行数 | 职责 |
|------|------|------|
| UserHeader | 114 | 用户头部 |
| UserStats | 68 | 统计信息 |
| AccountBindings | 167 | 账号绑定 |
| ProfileEditor | 135 | 信息编辑 |
| PasswordChanger | 146 | 密码修改 |
| **小计** | **630** | |

### 总计
- **8 个新组件**
- **平均每个组件 120 行**
- **所有组件都在 200 行以内** ✅

## 🚀 性能优势

### 1. 按需加载
可以使用 Vue 的异步组件功能：
```javascript
const ProfileEditor = defineAsyncComponent(() =>
  import('@/components/profile/ProfileEditor.vue')
)
```

### 2. 更好的代码分割
Vite 会自动将组件分割到不同的 chunk，优化加载速度。

### 3. 更小的热更新范围
修改单个组件时，只需要热更新该组件，提升开发体验。

## 📝 命名规范

### 组件命名
- **PascalCase**: `UserHeader.vue`, `LoginForm.vue`
- **语义化**: 名称要清晰表达组件职责
- **避免缩写**: 使用完整单词，如 `Password` 而不是 `Pwd`

### Props 命名
- **camelCase**: `userInfo`, `isLoading`
- **类型明确**: 使用 TypeScript 或 Props 验证

### Events 命名
- **kebab-case**: `@acwing-login`, `@submit`
- **动词开头**: `@bind`, `@unbind`, `@save`

## 🎨 样式规范

### 1. Scoped CSS
所有组件样式都使用 `<style scoped>`，避免样式污染。

### 2. 统一变量
使用 CSS 变量定义主题色：
```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
}
```

### 3. 响应式设计
使用媒体查询适配移动端：
```css
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
```

---

**创建日期**: 2025-11-07  
**维护者**: AI Assistant  
**版本**: 1.0

