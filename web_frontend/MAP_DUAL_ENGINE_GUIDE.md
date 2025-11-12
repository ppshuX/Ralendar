# 地图双引擎使用指南

## 🗺️ **功能说明**

已创建支持百度/高德双引擎切换的新地图组件 `MapPickerDual.vue`

### **特性：**
- ✅ **一键切换**：百度地图 ⇄ 高德地图
- ✅ **记忆功能**：自动记住用户上次选择的引擎
- ✅ **统一接口**：无论使用哪个引擎，返回的数据格式完全一致
- ✅ **搜索功能**：支持两种地图的POI搜索
- ✅ **点击选点**：支持地图点击选择位置
- ✅ **地理编码**：自动获取地址信息

---

## 📝 **使用方法**

### **方案1：替换现有组件（推荐）**

在 `EventDialog.vue` 中，将：

```vue
<MapPicker
  :initial-location="editingEvent?.location"
  :initial-lat="editingEvent?.latitude"
  :initial-lng="editingEvent?.longitude"
  @update:location="updateLocation"
/>
```

替换为：

```vue
<MapPickerDual
  :initial-location="editingEvent?.location"
  :initial-lat="editingEvent?.latitude"
  :initial-lng="editingEvent?.longitude"
  @update:location="updateLocation"
/>
```

同时更新import：

```javascript
import MapPickerDual from './map/MapPickerDual.vue'
```

### **方案2：保留两个版本**

保留原有的 `MapPicker.vue`（百度地图），新增 `MapPickerDual.vue` 供用户选择。

---

## 🔑 **API Key配置**

### **百度地图**
- **Key**: `i8UmOotWSekjTJlPbydOk1xQZuUeGeE1`
- **位置**: `web_frontend/index.html` 第15行

### **高德地图**
- **Key**: `53b6a185427e97b53e16c8786a272f62`
- **位置**: `web_frontend/index.html` 第18行

两个SDK已在 `index.html` 中同时加载，无需额外配置。

---

## 🎨 **UI效果**

### **引擎切换器**
```
┌──────────────────────────┐
│  [百度地图]  高德地图     │  ← 点击切换
└──────────────────────────┘
```

### **搜索框**
```
┌──────────────────────────────────────┐
│  🔍 搜索地点（当前：百度地图）  [搜索] │
└──────────────────────────────────────┘
```

### **地图容器**
- 百度地图：蓝色主题，熟悉的控件
- 高德地图：简洁风格，现代设计

---

## 💾 **记忆功能**

用户选择的地图引擎会保存在 `localStorage`:

```javascript
localStorage.getItem('map_engine')  // 'baidu' 或 'amap'
```

下次打开自动使用上次选择的引擎。

---

## 🔄 **返回数据格式**

无论使用哪个引擎，`@update:location` 事件返回的数据格式完全一致：

```javascript
{
  name: '天安门',        // 地点名称
  address: '...',       // 完整地址
  lng: 116.404,         // 经度
  lat: 39.915           // 纬度
}
```

---

## 🛠️ **开发说明**

### **百度地图API**
- **全局对象**: `BMap`
- **坐标系**: BD09（百度坐标）
- **主要类**:
  - `BMap.Map` - 地图
  - `BMap.Marker` - 标记
  - `BMap.Geocoder` - 地理编码
  - `BMap.LocalSearch` - 本地搜索

### **高德地图API**
- **全局对象**: `AMap`
- **坐标系**: GCJ02（火星坐标）
- **主要类**:
  - `AMap.Map` - 地图
  - `AMap.Marker` - 标记
  - `AMap.Geocoder` - 地理编码
  - `AMap.PlaceSearch` - 地点搜索

### **坐标系说明**
- 两种地图使用不同坐标系
- 如果需要坐标转换，请使用专业工具
- 我们的实现中**不需要**手动转换，各自SDK会处理

---

## 🎯 **未来优化方向**

1. **添加地图主题切换**（白天/夜间模式）
2. **支持离线地图**
3. **添加路径规划**
4. **支持更多地图引擎**（如腾讯地图）

---

## 📚 **相关文档**

- **百度地图API文档**: https://lbsyun.baidu.com/index.php?title=jspopularGL
- **高德地图API文档**: https://lbs.amap.com/api/javascript-api/summary

---

**现在就去试试双引擎地图吧！** 🗺️✨

