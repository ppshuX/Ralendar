# 🔍 部署检查清单

## ❌ 你的对话框还是很窄？按照这个步骤检查！

### 步骤 1：确认服务器代码已更新

SSH 到服务器后执行：

```bash
cd ~/kotlin_calendar

# 查看当前 commit
git log -1 --oneline

# 应该显示：21a3eeb style: mobile form labels left-aligned with wider input fields
```

**如果不是最新的 commit，执行**：
```bash
git pull
```

---

### 步骤 2：检查前端文件是否存在

```bash
ls -lh ~/kotlin_calendar/web/assets/index-*.css | tail -1

# 应该看到：index-CaeHsAyt.css (最新的)
```

---

### 步骤 3：强制清除浏览器缓存

在浏览器中：
1. 按 **F12** 打开开发者工具
2. **右键点击刷新按钮**
3. 选择"**清空缓存并硬性重新加载**"

或者直接按：**Ctrl + Shift + Delete**，清除最近 1 小时的缓存

---

### 步骤 4：验证 CSS 是否生效

在浏览器 Console 中执行：

```javascript
// 打开对话框后，检查宽度
const dialog = document.querySelector('.event-dialog');
console.log('对话框宽度:', dialog.offsetWidth);
console.log('屏幕宽度:', window.innerWidth);
console.log('宽度百分比:', (dialog.offsetWidth / window.innerWidth * 100).toFixed(1) + '%');

// 应该显示接近 90%
```

---

### 步骤 5：检查 CSS 文件内容

在浏览器 Console 执行：

```javascript
// 查看加载的 CSS 文件
const links = document.querySelectorAll('link[rel="stylesheet"]');
links.forEach(link => console.log(link.href));

// 应该看到 index-CaeHsAyt.css
```

---

## 🐛 如果还是不行

### 可能原因 1：CSS 选择器优先级不够

在浏览器打开对话框，右键检查元素，看看 `width` 样式：
- 如果有删除线，说明被其他样式覆盖了
- 需要增加选择器优先级

### 可能原因 2：Element Plus 内联样式覆盖

检查 `<div class="el-dialog">` 元素的 `style` 属性：
- 如果有 `style="width: 500px"`，说明内联样式优先级更高
- 需要在 CSS 中使用更高优先级或 !important

---

## 📸 发给我看

如果以上都检查了还是不行，请：

1. 在服务器执行 `git log -1` 截图给我
2. 在浏览器打开对话框，按 F12，截图 Elements 面板给我
3. 告诉我 `window.innerWidth` 的值

我会立即帮你定位问题！

