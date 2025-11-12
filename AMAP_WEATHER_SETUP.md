# 高德地图天气API配置指南

## 📌 为什么选择高德地图？

- ✅ **国内服务，稳定快速**
- ✅ **直接支持中文城市名**（北京、上海等）
- ✅ **免费额度超大**（100万次/天，5000次/分钟）
- ✅ **完整天气信息**（包括风向、风力等级）
- ✅ **即刻可用，无需等待**
- ✅ **文档清晰友好**

## 🚀 快速开始（5分钟搞定）

### 1. 注册高德开放平台账号

访问：**https://lbs.amap.com/**

点击右上角 **"注册"** → 填写信息：
- **手机号**：你的手机号
- **验证码**：获取并填入
- **密码**：设置密码

### 2. 创建应用

登录后：

1. 点击右上角 **"控制台"**
2. 进入 **"应用管理"** → **"我的应用"**
3. 点击 **"创建新应用"**
   - **应用名称**：`Ralendar日历`
   - **应用类型**：`Web服务`
4. 点击 **"提交"**

### 3. 添加Key

在创建的应用下：

1. 点击 **"添加Key"**
2. 填写信息：
   - **Key名称**：`天气服务`
   - **服务平台**：选择 **"Web服务"**
3. 点击 **"提交"**
4. **复制显示的Key**（类似：`a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`）

⚡ **无需等待，立即可用！**

### 4. 配置到服务器

在服务器上执行：

```bash
cd ~/kotlin_calendar/backend

# 编辑 .env 文件
nano .env
```

添加这一行：

```bash
# 高德地图 API Key
AMAP_API_KEY=你刚复制的KEY
```

按 `Ctrl+O` 保存，`Ctrl+X` 退出

### 5. 拉取最新代码并重启

```bash
# 拉取代码
git pull

# 重启uWSGI
sudo pkill -9 uwsgi
uwsgi --ini uwsgi.ini --daemonize /tmp/uwsgi.log

# 等待3秒
sleep 3
```

### 6. 测试天气API（立即可用）

```bash
# 测试方法1：直接调用高德API
python3 << 'EOF'
import requests
url = 'https://restapi.amap.com/v3/weather/weatherInfo'
params = {
    'city': '北京',
    'key': '你的KEY',  # 替换这里
    'extensions': 'base'
}
response = requests.get(url, params=params)
print(f"状态码: {response.status_code}")
data = response.json()
print(f"API状态: {data.get('status')} - {data.get('info')}")
if data.get('status') == '1':
    live = data['lives'][0]
    print(f"✅ 成功！")
    print(f"城市: {live['city']}")
    print(f"温度: {live['temperature']}℃")
    print(f"天气: {live['weather']}")
    print(f"风向: {live['winddirection']}")
    print(f"风力: {live['windpower']}级")
    print(f"湿度: {live['humidity']}%")
else:
    print(f"❌ 失败: {data}")
EOF

# 测试方法2：调用我们的API
curl "https://app7626.acapp.acwing.com.cn/api/weather/?location=北京"
```

## 🌍 支持的城市名格式

高德地图支持以下格式：

### 方式1：中文城市名（推荐）
```
北京、上海、广州、深圳、杭州、南昌
```

### 方式2：城市编码（adcode）
```
110000（北京）
310000（上海）
440100（广州）
```

### 获取adcode的方法
访问：https://lbs.amap.com/api/webservice/guide/api/district

或者直接使用中文名，高德会自动识别！

## 📊 高德地图API返回的完整天气数据

```json
{
  "status": "1",
  "info": "OK",
  "lives": [
    {
      "province": "北京",
      "city": "北京市",
      "adcode": "110000",
      "weather": "晴",
      "temperature": "20",
      "winddirection": "西北",
      "windpower": "≤3",
      "humidity": "45",
      "reporttime": "2025-11-12 14:30:00"
    }
  ]
}
```

我们使用的字段：
- `city` → `location`（城市名称）
- `temperature` → `temperature`（温度）
- `weather` → `weather`（天气状况）
- `winddirection` → `windDir`（风向）
- `windpower` → `windScale`（风力等级）
- `humidity` → `humidity`（湿度）
- `reporttime` → `updateTime`（更新时间）

## 📱 Android端完美兼容

高德API直接支持中文城市名，Android端无需修改：
- ✅ "北京" → 直接可用
- ✅ "上海" → 直接可用
- ✅ "广州" → 直接可用
- ✅ "深圳" → 直接可用
- ✅ "杭州" → 直接可用
- ✅ "南昌" → 直接可用

**无需任何映射或转换！**

## 📊 API限制

高德地图 **个人开发者免费版**：
- ✅ **100万次/天**
- ✅ **5000次/分钟**
- ✅ **足够任何个人项目使用**

## 🆚 与其他天气服务对比

| 功能 | 和风天气 | OpenWeatherMap | 高德地图 |
|------|---------|----------------|---------|
| 国内速度 | ❌ 403错误 | ⚠️ 较慢 | ✅ 快速 |
| 中文支持 | ✅ 原生 | ⚠️ 需翻译 | ✅ 原生 |
| 风向风力 | ✅ 支持 | ❌ 不完整 | ✅ 完整 |
| 更新时间 | ✅ 提供 | ❌ 不提供 | ✅ 提供 |
| 体感温度 | ✅ 提供 | ✅ 提供 | ❌ 不提供 |
| 免费额度 | 1000次/天 | 60次/分 | **100万次/天** |
| 即刻可用 | ❌ 需等待 | ⚠️ 需等2小时 | ✅ 立即可用 |
| 稳定性 | ❌ 不稳定 | ✅ 稳定 | ✅ 非常稳定 |

**高德地图完胜！** 🏆

## ⚠️ 常见问题

### 1. 提示"INVALID_USER_KEY"

- 检查Key是否完整复制
- 确认Key的服务类型是"Web服务"
- 重新生成一个Key试试

### 2. 找不到城市

- 确认城市名称正确（如"北京"而不是"北京市"也可以）
- 尝试使用adcode
- 检查是否有拼写错误

### 3. 超过配额

- 免费版100万次/天，基本不会超
- 如果超了，说明可能有异常调用
- 考虑添加缓存机制

## 🎉 配置完成！

配置高德地图后，你的Ralendar日历天气功能将：
- ✅ **秒速响应**
- ✅ **完整数据**（包括风向、风力）
- ✅ **完美中文**
- ✅ **稳定可靠**

## 📚 相关文档

- **高德地图天气API文档**：https://lbs.amap.com/api/webservice/guide/api/weatherinfo
- **错误码说明**：https://lbs.amap.com/api/webservice/guide/tools/info
- **控制台**：https://console.amap.com/

---

**现在就去注册高德地图，5分钟内完成配置！** 🚀✨

