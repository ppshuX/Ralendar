# 🎮 游戏地图等比例缩放逻辑应用于日历

> **灵感来源**: 贪吃蛇游戏的地图自适应算法  
> **核心公式**: `cellSize = Math.min(containerWidth / cols, containerHeight / rows)`  
> **实现日期**: 2025-11-09  

---

## 📚 **背景：游戏地图的等比例缩放**

### **游戏地图的核心逻辑**

```javascript
// 游戏地图的 update_size() 方法
update_size() {
    // 关键：取宽高比例的最小值
    this.L = parseInt(Math.min(
        this.parent.clientWidth / this.cols,   // 宽度方向
        this.parent.clientHeight / this.rows    // 高度方向
    ));
    
    // 设置 Canvas 尺寸
    this.ctx.canvas.width = this.L * this.cols;
    this.ctx.canvas.height = this.L * this.rows;
}
```

### **为什么取最小值？**

```
假设：
- 容器：1400px × 650px
- 地图：13 行 × 14 列

计算过程：
宽度比例：1400 / 14 = 100px
高度比例：650 / 13 = 50px

取最小值：min(100, 50) = 50px

如果取 100px（宽度比例）：
  Canvas 高度 = 100 × 13 = 1300px  → 超出容器 ❌
  
如果取 50px（高度比例）：
  Canvas 宽度 = 50 × 14 = 700px   → ✅ 在容器内
  Canvas 高度 = 50 × 13 = 650px   → ✅ 刚好填满

结论：取最小值确保不溢出！
```

---

## 📅 **应用到 Ralendar 日历**

### **日历的配置**

```javascript
// 日历是一个 7 列 × 7 行的网格
const rows = 7  // 1行标题 + 6行日期（最多）
const cols = 7  // 星期日 - 星期六
```

### **核心实现代码**

```javascript
// CalendarView.vue
const updateCalendarSize = () => {
  if (!calendarContainer.value) return

  const container = calendarContainer.value
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight

  // 日历配置：7 行 × 7 列
  const rows = 7  // 包含标题行
  const cols = 7  // 星期日到星期六

  // ============ 游戏地图同款逻辑 ============
  const cellWidth = containerWidth / cols
  const cellHeight = containerHeight / rows
  const cellSize = Math.floor(Math.min(cellWidth, cellHeight))
  
  console.log('[日历自适应] 容器:', containerWidth, 'x', containerHeight)
  console.log('[日历自适应] 计算格子大小:', cellSize)
  console.log('[日历自适应] 最终日历:', cellSize * cols, 'x', cellSize * rows)

  // 更新 CSS 变量
  document.documentElement.style.setProperty('--calendar-cell-size', `${cellSize}px`)
  
  // 通知 FullCalendar 重新渲染
  if (fullCalendar.value) {
    const calendarApi = fullCalendar.value.getApi()
    calendarApi.updateSize()
  }
}
```

---

## 🔍 **详细对比**

### **游戏地图 vs 日历**

| 特性 | 游戏地图 | Ralendar 日历 |
|------|---------|---------------|
| **行列配置** | 13 行 × 14 列 | 7 行 × 7 列 |
| **单位名称** | `this.L` (格子边长) | `cellSize` (日期格子) |
| **渲染方式** | Canvas 绘制 | HTML + CSS |
| **更新频率** | 每帧 (60fps) | resize 事件时 |
| **监听方式** | `requestAnimationFrame` | `ResizeObserver` + `window.resize` |
| **核心公式** | `Math.min(w/cols, h/rows)` | **完全相同** ✅ |

---

## 📐 **数学原理**

### **公式推导**

```
给定容器尺寸：W × H
给定网格配置：rows × cols

目标：计算最大的格子大小 cellSize，使得：
  - cellSize × cols ≤ W  (宽度不超出)
  - cellSize × rows ≤ H  (高度不超出)

求解：
  cellSize ≤ W / cols  (宽度约束)
  cellSize ≤ H / rows  (高度约束)
  
  → cellSize = min(W / cols, H / rows)  ✅
```

### **实际案例**

#### **桌面端 (1400px × 650px)**

```
容器：1400px × 650px
行列：7 × 7

宽度比例：1400 / 7 = 200px
高度比例：650 / 7 ≈ 92.86px

cellSize = min(200, 92.86) = 92px

最终日历：92 × 7 = 644px (宽)
         92 × 7 = 644px (高)

结果：日历 644×644，居中显示在 1400×650 容器中 ✅
```

#### **移动端 (375px × 450px)**

```
容器：375px × 450px
行列：7 × 7

宽度比例：375 / 7 ≈ 53.57px
高度比例：450 / 7 ≈ 64.29px

cellSize = min(53.57, 64.29) = 53px

最终日历：53 × 7 = 371px (宽)
         53 × 7 = 371px (高)

结果：日历 371×371，适配移动端 ✅
```

---

## 🚀 **实时更新机制**

### **游戏地图的方式**

```javascript
update() {
    this.update_size();  // 每帧都重新计算
    if (this.check_ready()) {
        this.next_step();
    }
    this.render();
}
```

### **Ralendar 的方式**

```javascript
onMounted(async () => {
  // ... 其他初始化 ...

  // 初始计算
  updateCalendarSize()

  // 方法1：ResizeObserver（现代浏览器）
  const resizeObserver = new ResizeObserver(() => {
    updateCalendarSize()
  })
  resizeObserver.observe(calendarContainer.value)

  // 方法2：window resize（兼容性）
  window.addEventListener('resize', updateCalendarSize)
})
```

**区别**：
- 游戏：每帧更新（60fps）→ 实时性极高
- 日历：resize 时更新 → 性能更优

---

## 🎯 **优势**

### **1. 完美自适应**

```
容器变化 → 自动重新计算 → 日历自动适配

┌─────────────────────────────────┐
│  浏览器窗口缩放                 │
│         ↓                        │
│  容器尺寸改变                   │
│         ↓                        │
│  ResizeObserver 触发            │
│         ↓                        │
│  updateCalendarSize()           │
│         ↓                        │
│  重新计算 cellSize              │
│         ↓                        │
│  FullCalendar.updateSize()      │
│         ↓                        │
│  ✅ 日历完美适配新尺寸          │
└─────────────────────────────────┘
```

### **2. 不会溢出**

```
取最小值 → 确保宽高都不超出

如果容器很窄：
  cellSize = min(窄宽度/7, 高度/7) = 窄宽度/7
  → 日历宽度刚好填满，高度有余
  
如果容器很扁：
  cellSize = min(宽度/7, 矮高度/7) = 矮高度/7
  → 日历高度刚好填满，宽度居中

永远不会溢出 ✅
```

### **3. 等比例缩放**

```
所有格子都使用相同的 cellSize
→ 整个日历等比例缩放
→ 保持视觉比例一致
→ 不会变形 ✅
```

---

## 🔧 **技术细节**

### **CSS 配合**

```css
/* 容器使用 flex 居中 */
.calendar-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* FullCalendar 占满可用空间 */
.calendar-wrapper .fc {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 表格自适应 */
.calendar-wrapper .fc-view-harness {
  flex: 1;
  position: relative;
}
```

### **CSS 变量（可选）**

```javascript
// 设置 CSS 变量
document.documentElement.style.setProperty('--calendar-cell-size', `${cellSize}px`)
```

```css
/* 使用 CSS 变量 */
.calendar-cell {
  width: var(--calendar-cell-size);
  height: var(--calendar-cell-size);
}
```

---

## 📊 **性能对比**

| 方面 | 游戏地图 | Ralendar 日历 |
|------|---------|---------------|
| **更新频率** | 60fps (每秒60次) | resize 时 (按需) |
| **CPU 占用** | 较高 | 极低 |
| **内存占用** | Canvas 缓冲区 | DOM 元素 |
| **适用场景** | 实时游戏 | 静态展示 |
| **性能评价** | 适合游戏 ✅ | 适合UI ✅ |

---

## 🎮 **游戏地图的完整流程**

```
1. 初始化
   ↓
2. 每帧执行 update()
   ↓
3. update_size() 计算格子大小
   ↓
4. render() 绘制地图
   ↓
5. requestAnimationFrame() 下一帧
   ↓
6. 回到步骤 2
```

---

## 📅 **Ralendar 的完整流程**

```
1. 组件挂载 (onMounted)
   ↓
2. 初始调用 updateCalendarSize()
   ↓
3. ResizeObserver 监听容器
   ↓
4. 容器尺寸改变
   ↓
5. 触发 updateCalendarSize()
   ↓
6. 计算新的 cellSize
   ↓
7. FullCalendar.updateSize()
   ↓
8. 日历重新渲染 ✅
```

---

## 🧮 **公式汇总**

### **核心公式**

```javascript
cellSize = Math.floor(Math.min(
  containerWidth / cols,
  containerHeight / rows
))
```

### **扩展公式**

```javascript
// 最终日历宽度
calendarWidth = cellSize × cols

// 最终日历高度
calendarHeight = cellSize × rows

// 左右边距（宽度有余时）
marginLeft = marginRight = (containerWidth - calendarWidth) / 2

// 上下边距（高度有余时）
marginTop = marginBottom = (containerHeight - calendarHeight) / 2
```

---

## 📝 **代码结构**

### **文件修改**

```
web_frontend/src/views/CalendarView.vue
  ├── 添加 ref: calendarContainer, fullCalendar
  ├── 添加 updateCalendarSize() 函数
  └── onMounted 中启动监听

web_frontend/src/composables/useCalendarEvents.js
  └── 移除 aspectRatio（改用容器计算）

web_frontend/src/styles/calendar.css
  ├── 添加 flex 布局
  └── 添加 fc-view-harness 样式
```

---

## 🎯 **总结**

### **游戏地图的智慧**

```javascript
// 一行代码解决所有自适应问题
this.L = Math.min(width / cols, height / rows)
```

### **应用到日历**

```javascript
// 同样的智慧，同样的优雅
const cellSize = Math.min(width / cols, height / rows)
```

### **核心优势**

- ✅ **简单**: 一行公式解决问题
- ✅ **优雅**: 数学原理清晰
- ✅ **通用**: 适用所有网格布局
- ✅ **高效**: 计算量极小
- ✅ **可靠**: 永不溢出

---

## 🌟 **致敬游戏开发**

> *"好的游戏算法，也是好的UI算法"*

游戏开发中的性能优化和精确计算，给了我们很多启发。

这次把贪吃蛇游戏的地图缩放逻辑应用到日历组件，完美展示了：

**算法的本质是解决问题，而不是局限于特定领域。**

---

## 🔗 **参考资源**

- 游戏地图源码：`GameMap.js` 的 `update_size()` 方法
- Ralendar 实现：`CalendarView.vue` 的 `updateCalendarSize()` 函数
- FullCalendar API：`updateSize()` 方法

---

**实现日期**: 2025-11-09  
**作者**: ppshuX  
**项目**: Ralendar  
**灵感来源**: 贪吃蛇游戏地图算法 🎮

