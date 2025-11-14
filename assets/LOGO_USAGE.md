# Ralendar Logo 使用指南

## 📁 文件位置

Logo文件已放置在以下位置：

### 共享资源
- `assets/images/Ralendar_logo.png` - PNG版本（原始文件）
- `assets/images/Ralendar_logo.webp` - WEBP版本（较小体积）

### Web前端
- `web_frontend/public/logo.png` - Web端使用
- `web_frontend/public/favicon.ico` - 浏览器标签图标

### AcWing App前端
- `acapp_frontend/public/logo.png` - AcApp端使用
- `acapp_frontend/public/favicon.ico` - 浏览器标签图标

### Android端
- `adapp/app/src/main/res/mipmap-*/ic_launcher.png` - 应用图标（各种分辨率）
- `adapp/app/src/main/res/mipmap-*/ic_launcher_round.png` - 圆形应用图标（各种分辨率）

---

## 🎨 使用方式

### Web端 (`web_frontend`)

**NavBar组件** (`src/components/NavBar.vue`):
```vue
<img src="/logo.png" alt="Ralendar" class="brand-logo" />
```

**HTML头部** (`index.html`):
```html
<link rel="icon" href="/logo.png" type="image/png">
<link rel="apple-touch-icon" href="/logo.png">
```

### AcWing App端 (`acapp_frontend`)

**在组件中使用**:
```vue
<img src="/logo.png" alt="Ralendar" />
```

### Android端 (`adapp`)

**当前配置**:
- 图标已复制到所有mipmap目录
- 适配图标配置在 `res/mipmap-anydpi-v26/ic_launcher.xml`
- 使用 `drawable/ic_launcher_foreground.xml` 作为前景层

**如需使用实际logo图片作为图标**，需要：
1. 将logo.png转换为vector drawable，或
2. 使用Android Studio的Image Asset工具生成适配图标

**建议使用Android Studio的Image Asset工具**:
1. 右键 `res` → New → Image Asset
2. 选择 `Launcher Icons (Adaptive and Legacy)`
3. Foreground Layer → Image → 选择 `assets/images/Ralendar_logo.png`
4. Background Layer → Color → 选择淡紫色 `#E1BEE7`
5. 生成所有分辨率的图标

---

## 📐 图标尺寸要求

### Android图标尺寸
- **mdpi**: 48×48 dp
- **hdpi**: 72×72 dp
- **xhdpi**: 96×96 dp
- **xxhdpi**: 144×144 dp
- **xxxhdpi**: 192×192 dp

### Web图标尺寸
- **favicon**: 32×32 或 16×16
- **apple-touch-icon**: 180×180
- **logo**: 建议 200×200 以上

---

## 🔄 更新Logo流程

如果logo文件更新：

1. **更新共享资源**:
   ```bash
   # 复制新logo到共享目录
   cp new_logo.png assets/images/Ralendar_logo.png
   cp new_logo.webp assets/images/Ralendar_logo.webp
   ```

2. **更新Web端**:
   ```bash
   cp assets/images/Ralendar_logo.png web_frontend/public/logo.png
   ```

3. **更新AcApp端**:
   ```bash
   cp assets/images/Ralendar_logo.png acapp_frontend/public/logo.png
   ```

4. **更新Android端**:
   - 使用Android Studio的Image Asset工具重新生成
   - 或手动复制到各个mipmap目录（不推荐）

---

## 💡 注意事项

1. **文件格式**:
   - PNG: 通用格式，适合所有平台
   - WEBP: 体积更小，但需要支持（Android和现代浏览器支持）

2. **透明度**:
   - Logo支持透明背景
   - Android适配图标需要前景和背景层分离

3. **版权**:
   - Logo版权归Ralendar项目所有
   - 请勿用于商业用途（除非明确授权）

