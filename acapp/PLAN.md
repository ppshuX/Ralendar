# AcWing App (acapp) 实现计划

**AcWing 平台集成版本** - 未来计划

---

## 📋 基本信息

- **命名**：acapp = **Ac**Wing **App**（AcWing 平台集成端）
- **与 Web 端的区别**：运行在 AcWing 平台沙箱环境中，需要样式隔离
- **状态**：⏳ 未来计划（当前已实现 adapp + backend + web）

---

## 🎯 核心要求

### 1. **样式隔离**（最重要！）

❌ **不能使用的技术**：
- Bootstrap（全局 CSS 框架）
- 任何修改全局样式的库
- 直接操作 `document.body`
- 全局 CSS reset

✅ **必须使用的方案**：
- Vue 3 的 `<style scoped>`
- CSS Modules
- CSS-in-JS（如 Vue 的内联样式）
- BEM 命名规范（自定义前缀，如 `.kc-*`）

### 2. **DOM 隔离**

```javascript
// ❌ 错误：污染全局
new Vue({
  el: '#app',  // 可能冲突
})

// ✅ 正确：使用平台分配的容器
export class Calendar {
  constructor(parent) {
    this.parent = parent;  // AcWing 平台传入的容器
    this.root = document.createElement('div');
    this.root.id = 'kc-calendar-root';
    this.parent.appendChild(this.root);
    
    // 在隔离容器中渲染
    new Vue({
      el: this.root,
      // ...
    })
  }
}
```

### 3. **单文件构建**

```javascript
// vite.config.js for acapp
export default defineConfig({
  build: {
    lib: {
      entry: 'src/main.js',
      name: 'Calendar',  // 主类名
      fileName: 'app',
      formats: ['iife'],  // 立即执行函数，避免污染全局
    },
    rollupOptions: {
      output: {
        // 单个 JS 文件
        entryFileNames: 'app.js',
        // 单个 CSS 文件（所有样式都是 scoped）
        assetFileNames: 'app.css',
      },
    },
  },
})
```

---

## 🏗️ 技术栈对比

| 技术 | Web 端（独立） | AcWing 端（集成） |
|------|--------------|------------------|
| **Vue 3** | ✅ 使用 | ✅ 使用 |
| **FullCalendar** | ✅ 可用 | ⚠️ 需检查是否污染全局 |
| **Element Plus** | ✅ 可用 | ❌ 全局样式，不能用 |
| **Bootstrap** | ✅ 可用 | ❌ 全局样式，不能用 |
| **Axios** | ✅ 可用 | ✅ 可用（不污染） |
| **自定义 CSS** | ✅ 随意 | ✅ 必须 scoped |
| **构建目标** | SPA 应用 | Library（库模式） |
| **主类** | - | `Calendar` 类导出 |

---

## 📁 项目结构（计划）

```
acapp/
├── src/
│   ├── main.js              # 入口：导出 Calendar 类
│   ├── App.vue              # 根组件（全部 scoped）
│   ├── components/
│   │   ├── CalendarGrid.vue # 日历网格（scoped）
│   │   ├── EventList.vue    # 事件列表（scoped）
│   │   └── EventDialog.vue  # 事件对话框（scoped）
│   ├── api/
│   │   └── index.js         # API 调用（同 web）
│   └── assets/
│       └── styles.css       # 自定义样式（BEM 命名）
├── vite.config.js           # 库模式构建配置
├── package.json
└── README.md
```

---

## 🎨 样式隔离示例

### ❌ **错误示例（Web 端可以，AcWing 端不行）**

```vue
<!-- 全局污染 -->
<style>
body {
  margin: 0;
  font-family: Arial;
}

.btn {  /* 可能冲突 */
  padding: 10px;
}
</style>
```

### ✅ **正确示例（AcWing 端必须）**

```vue
<!-- 方式 1: scoped 样式 -->
<template>
  <div class="calendar-container">
    <button class="kc-btn">添加日程</button>
  </div>
</template>

<style scoped>
.calendar-container {
  /* 自动添加唯一属性选择器，不会污染全局 */
  padding: 20px;
}

.kc-btn {
  /* kc- 前缀防止冲突 */
  background: #409eff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
```

```vue
<!-- 方式 2: CSS Modules -->
<template>
  <div :class="$style.container">
    <button :class="$style.button">添加日程</button>
  </div>
</template>

<style module>
.container {
  padding: 20px;
}

.button {
  background: #409eff;
  color: white;
}
</style>
```

---

## 🔌 主类导出示例

```javascript
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'

// AcWing 平台要求导出一个类
export class Calendar {
  constructor(parent) {
    this.parent = parent;  // AcWing 传入的容器 DOM
    this.app = null;
    
    // 创建隔离的根容器
    this.root = document.createElement('div');
    this.root.className = 'kc-app-root';  // kc = KotlinCalendar
    this.parent.appendChild(this.root);
    
    // 挂载 Vue 应用
    this.app = createApp(App);
    this.app.mount(this.root);
  }
  
  // 销毁方法（AcWing 平台可能调用）
  destroy() {
    if (this.app) {
      this.app.unmount();
      this.root.remove();
    }
  }
  
  // 其他 AcWing 平台可能需要的方法
  resize() {
    // 响应容器大小变化
  }
}
```

---

## 🚀 构建配置

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    // 库模式：生成可被其他应用引用的库
    lib: {
      entry: 'src/main.js',
      name: 'Calendar',  // 全局变量名（UMD 模式）
      fileName: 'app',
      formats: ['iife'],  // 立即执行函数表达式
    },
    rollupOptions: {
      // 外部化 Vue（AcWing 平台可能提供）
      // 如果平台不提供，则打包进去
      // external: ['vue'],
      output: {
        // 单文件输出
        entryFileNames: 'app.js',
        assetFileNames: 'app.css',
        // IIFE 格式，不污染全局
        format: 'iife',
        globals: {
          // vue: 'Vue'  // 如果外部化
        },
      },
    },
  },
})
```

---

## 📋 AcWing 平台集成步骤

### 1. **本地开发**
```bash
cd acapp
npm install
npm run dev
```

### 2. **构建**
```bash
npm run build
# 输出: dist/app.js + dist/app.css
```

### 3. **上传到服务器**
```bash
scp dist/* acs@app7626.acapp.acwing.com.cn:~/acapp/
```

### 4. **AcWing 平台配置**
- CSS 地址: `https://app7626.acapp.acwing.com.cn/acapp/app.css`
- JS 地址: `https://app7626.acapp.acwing.com.cn/acapp/app.js`
- 主类名: `Calendar`

---

## ⚠️ 常见陷阱

### 1. **全局样式污染**
```css
/* ❌ 危险：会影响整个 AcWing 平台 */
* {
  box-sizing: border-box;
}

body {
  background: #f0f0f0;
}

/* ✅ 安全：scoped 或带前缀 */
.kc-app-root * {
  box-sizing: border-box;
}

.kc-app-root {
  background: #f0f0f0;
}
```

### 2. **DOM 操作越界**
```javascript
// ❌ 危险：可能影响其他应用
document.body.style.overflow = 'hidden';

// ✅ 安全：只操作自己的容器
this.root.style.overflow = 'hidden';
```

### 3. **事件监听泄漏**
```javascript
// ❌ 危险：没有清理
window.addEventListener('resize', this.handleResize);

// ✅ 安全：在 destroy 时清理
constructor() {
  this.handleResize = this.handleResize.bind(this);
  window.addEventListener('resize', this.handleResize);
}

destroy() {
  window.removeEventListener('resize', this.handleResize);
  // ...
}
```

---

## 🎯 与现有 Web 端的关系

| 端 | 用途 | 环境 | 样式 |
|----|------|------|------|
| **Web 端** | 独立 Web 应用 | 独占页面 | 可用 Bootstrap |
| **AcWing 端** | 集成到 AcWing | 共享页面 | 必须隔离 |

**代码复用策略**：
- ✅ 组件逻辑可以复用（Vue 组件）
- ✅ API 调用可以复用（axios）
- ❌ 样式需要重写（去掉 Bootstrap，改用 scoped）
- ⚠️ 入口文件不同（Web: SPA，AcWing: Class）

---

## 📝 开发优先级

1. **Phase 1** ✅ 已完成
   - Android 端（adapp）
   - Django 后端（backend）
   - 独立 Web 端（web）

2. **Phase 2** ⏳ 未来计划
   - AcWing 端（acapp）
   - 用户认证系统
   - 多人协作功能

---

## 🔗 参考资料

- [AcWing 应用开发文档](https://www.acwing.com/blog/content/1150/)
- [Vue 3 Scoped CSS](https://vuejs.org/api/sfc-css-features.html#scoped-css)
- [Vite Library Mode](https://vitejs.dev/guide/build.html#library-mode)
- [微前端样式隔离方案](https://qiankun.umijs.org/zh/guide/tutorial#%E6%A0%B7%E5%BC%8F%E9%9A%94%E7%A6%BB)

---

## 💡 总结

**AcWing 端的核心原则**：
1. ✅ **样式隔离**：scoped CSS + BEM 命名
2. ✅ **DOM 隔离**：只操作 parent 容器内的元素
3. ✅ **单文件构建**：app.js + app.css
4. ✅ **类导出**：export class Calendar
5. ❌ **避免全局污染**：不用 Bootstrap 等全局框架

---

**最后更新**: 2025-11-06

