# AcWing App (acapp) 实现计划

**AcWing 平台集成版本** - 纯 Vue3 CDN 方案

---

## 📋 基本信息

- **命名**：acapp = **Ac**Wing **App**（AcWing 平台集成端）
- **技术栈**：**纯 Vue3 CDN** + 可选 jQuery（无构建工具）
- **与 Web 端的区别**：
  - Web 端：Vite 构建，Bootstrap + Element Plus（多文件，代码分割）
  - AcWing 端：CDN 引入，无外部UI库（单文件，极简）
- **状态**：⏳ 未来计划（当前已实现 adapp + backend + web）

## 🌟 技术特色：纯原生开发，无构建工具

为了展示**技术多样性**，acapp 端采用完全不同的技术方案：

| 项目 | adapp | web | acapp |
|------|-------|-----|-------|
| **语言** | Kotlin | JavaScript | JavaScript |
| **框架** | Android SDK | Vue3 + Vite | **Vue3 CDN** |
| **UI库** | Material Design | Bootstrap + Element Plus | **纯手写CSS** |
| **构建** | Gradle | Vite（多文件） | **无构建工具** |
| **jQuery** | - | - | **可选（CDN）** |
| **特点** | 原生应用 | 现代化SPA | **极简轻量** |

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
| **Vue 3** | ✅ npm包 + Vite | ✅ **CDN 引入**（无打包） |
| **FullCalendar** | ✅ 可用 | ❌ 不用（手写日历组件） |
| **Element Plus** | ✅ 可用 | ❌ 不用 |
| **Bootstrap** | ✅ 可用 | ❌ 不用 |
| **jQuery** | ❌ 不用 | ✅ **可选 CDN**（DOM操作） |
| **Axios** | ✅ npm包 | ✅ **CDN 或 fetch** |
| **自定义 CSS** | ✅ 随意 | ✅ **纯手写，BEM命名** |
| **构建工具** | Vite | ❌ **无（直接写HTML）** |
| **构建目标** | SPA 应用 | **单HTML文件** |
| **主类** | - | `Calendar` 类导出 |

## 💡 为什么选择纯 Vue3 CDN？

### 优势
1. **技术多样性** ⭐
   - adapp: Gradle 构建
   - web: Vite 现代化构建
   - acapp: **无构建工具，回归本质**
   
2. **极简部署**
   - 一个 HTML 文件
   - 一个 JS 文件（只有业务逻辑）
   - 一个 CSS 文件（纯手写）
   - 无需 node_modules

3. **学习价值**
   - 展示如何不依赖构建工具开发
   - 理解 Vue3 的本质（Composition API）
   - 手写CSS的能力

4. **AcWing 平台友好**
   - Vue3 从 CDN 加载，不打包到文件中
   - 业务代码极小（<50KB）
   - 上传速度快

---

## 📁 项目结构（计划）

```
acapp/
├── index.html               # 开发预览（本地测试用）
├── src/
│   ├── app.js               # 主文件：Calendar 类 + Vue组件
│   ├── api.js               # API 调用（fetch 或 axios CDN）
│   └── app.css              # 样式（BEM 命名，如 .kc-calendar）
├── dist/                    # 手动压缩后上传（可选）
│   ├── app.min.js
│   └── app.min.css
└── README.md

无需：
❌ node_modules/
❌ package.json
❌ vite.config.js
❌ .vue 单文件组件（直接在 JS 中定义）
```

### 文件说明

#### `index.html`（本地测试）
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>KotlinCalendar - AcWing</title>
  <!-- Vue 3 CDN -->
  <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
  <!-- 可选：jQuery CDN -->
  <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
  <!-- 业务代码 -->
  <link rel="stylesheet" href="src/app.css">
</head>
<body>
  <div id="calendar-container"></div>
  <script src="src/app.js"></script>
  <script>
    // 本地测试
    const calendar = new Calendar(document.getElementById('calendar-container'));
  </script>
</body>
</html>
```

#### `src/app.js`（核心业务逻辑）
```javascript
// 使用 Vue3 全局 API（CDN 方式）
const { createApp, ref, computed, onMounted } = Vue;

// 导出 Calendar 类（AcWing 平台要求）
class Calendar {
  constructor(parent) {
    this.parent = parent;
    this.app = null;
    this.init();
  }
  
  init() {
    // 创建 Vue 应用
    this.app = createApp({
      setup() {
        const events = ref([]);
        const currentDate = ref(new Date());
        
        // 获取事件
        const fetchEvents = async () => {
          const response = await fetch('https://app7626.acapp.acwing.com.cn/api/events/');
          events.value = await response.json();
        };
        
        onMounted(() => {
          fetchEvents();
        });
        
        return {
          events,
          currentDate,
          fetchEvents
        };
      },
      
      // 模板（可以用字符串模板或 JSX）
      template: `
        <div class="kc-calendar">
          <div class="kc-header">
            <button class="kc-btn" @click="prevMonth">上月</button>
            <span class="kc-title">{{ currentMonth }}</span>
            <button class="kc-btn" @click="nextMonth">下月</button>
          </div>
          <div class="kc-grid">
            <!-- 日历网格 -->
          </div>
          <div class="kc-events">
            <div v-for="event in events" :key="event.id" class="kc-event-item">
              {{ event.title }}
            </div>
          </div>
        </div>
      `
    });
    
    this.app.mount(this.parent);
  }
  
  destroy() {
    if (this.app) {
      this.app.unmount();
    }
  }
}

// 如果不在 AcWing 平台，提供全局访问
if (typeof window !== 'undefined') {
  window.Calendar = Calendar;
}
```

#### `src/app.css`（纯手写样式）
```css
/* BEM 命名，kc = KotlinCalendar */
.kc-calendar {
  width: 100%;
  max-width: 800px;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.kc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.kc-btn {
  background: #409eff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.kc-btn:hover {
  background: #66b1ff;
}

.kc-title {
  font-size: 20px;
  font-weight: bold;
}

.kc-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #ddd;
  border: 1px solid #ddd;
}

.kc-event-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}

.kc-event-item:hover {
  background: #f5f7fa;
}
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

## 🚀 部署流程（极简）

### 开发阶段
```bash
# 1. 创建文件
acapp/
├── index.html      # 本地测试
├── src/
│   ├── app.js
│   ├── api.js
│   └── app.css

# 2. 本地测试
# 直接用浏览器打开 index.html
# 或使用 python 简单服务器
python -m http.server 8080
# 访问 http://localhost:8080
```

### 生产部署
```bash
# 1. 可选：压缩 JS/CSS（手动或使用在线工具）
# https://jscompress.com/
# https://cssminifier.com/

# 2. 上传到服务器
scp src/app.js src/app.css acs@app7626.acapp.acwing.com.cn:~/acapp/

# 3. AcWing 平台配置
# CSS 地址: https://app7626.acapp.acwing.com.cn/acapp/app.css
# JS 地址: https://app7626.acapp.acwing.com.cn/acapp/app.js
# 主类名: Calendar
```

### 压缩示例（可选）
```bash
# 使用 terser 压缩 JS（如果需要）
npx terser src/app.js -o dist/app.min.js -c -m

# 使用 cssnano 压缩 CSS（如果需要）
npx cssnano src/app.css dist/app.min.css
```


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

