# OpenWeatherMap 天气API配置指南

## 📌 为什么切换到 OpenWeatherMap？

由于和风天气API持续出现403错误（Invalid Host），即使配置了"不限制"仍然无法访问，我们已切换到更稳定可靠的 **OpenWeatherMap**。

## 🚀 快速开始

### 1. 注册 OpenWeatherMap 账户

访问：https://home.openweathermap.org/users/sign_up

填写信息：
- **用户名**：任意
- **邮箱**：你的邮箱
- **密码**：设置密码

勾选同意条款，点击 **Create Account**

### 2. 验证邮箱

- 检查邮箱收件箱（可能在垃圾邮件中）
- 点击验证链接激活账户

### 3. 获取 API Key

1. 登录后，点击右上角用户名 → **My API keys**
2. 默认会自动生成一个 **Default** API Key
3. **复制这个Key**（类似：`a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`）

⚠️ **注意**：新创建的API Key需要 **2小时左右才能激活**！

### 4. 配置到服务器

在服务器上执行：

```bash
cd ~/kotlin_calendar/backend

# 编辑 .env 文件
nano .env
```

添加或修改以下行：

```bash
# OpenWeatherMap API Key
OPENWEATHER_API_KEY=你的API_KEY
```

按 `Ctrl+O` 保存，`Ctrl+X` 退出

### 5. 重启服务

```bash
# 重启uWSGI
sudo pkill -9 uwsgi
uwsgi --ini uwsgi.ini --daemonize /tmp/uwsgi.log

# 等待3秒
sleep 3
```

### 6. 测试天气API

```bash
# 测试方法1：直接调用OpenWeatherMap
python3 << 'EOF'
import requests
url = 'https://api.openweathermap.org/data/2.5/weather'
params = {
    'q': 'Beijing',
    'appid': '你的API_KEY',
    'units': 'metric',
    'lang': 'zh_cn'
}
response = requests.get(url, params=params)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ 成功！温度: {data['main']['temp']}℃")
    print(f"天气: {data['weather'][0]['description']}")
else:
    print(f"❌ 失败: {response.text}")
EOF

# 测试方法2：调用我们的API
curl "https://app7626.acapp.acwing.com.cn/api/weather/?location=Beijing"
```

## 🌍 支持的城市名格式

OpenWeatherMap 支持多种城市名格式：

- **英文名**：`Beijing`, `Shanghai`, `Guangzhou`
- **中文拼音**：`beijing`, `shanghai`
- **带国家代码**：`Beijing,CN` （更准确）
- **城市ID**：`1816670`（最精确）

推荐使用**英文名**或**带国家代码**的格式！

## 🔄 Android端城市映射

由于Android端目前使用中文城市名，建议在 `WeatherManager.kt` 中添加映射：

```kotlin
private fun mapCityName(chineseName: String): String {
    return when (chineseName) {
        "北京" -> "Beijing,CN"
        "上海" -> "Shanghai,CN"
        "广州" -> "Guangzhou,CN"
        "深圳" -> "Shenzhen,CN"
        "杭州" -> "Hangzhou,CN"
        "南昌" -> "Nanchang,CN"
        else -> chineseName  // 保留原名，OpenWeatherMap会尝试识别
    }
}

// 在loadWeather中使用
val mappedCity = mapCityName(city)
val response = api.getWeather(mappedCity)
```

## 📊 API限制

OpenWeatherMap **免费版**限制：
- **60次/分钟**
- **1,000,000次/月**
- **足够个人项目使用**

## 🆚 与和风天气的区别

| 功能 | 和风天气 | OpenWeatherMap |
|------|---------|----------------|
| 风向文字 | ✅ 支持 | ❌ 不支持 |
| 风力等级 | ✅ 支持 | ❌ 不支持 |
| 更新时间 | ✅ 提供 | ❌ 不提供 |
| 中文描述 | ✅ 原生 | ✅ 翻译 |
| 稳定性 | ❌ 403错误 | ✅ 稳定 |
| 免费额度 | 1000次/天 | 60次/分 |

## ⚠️ 常见问题

### 1. API Key无效（401）

- 确认已验证邮箱
- 等待2小时API Key激活
- 检查复制的Key是否完整

### 2. 城市未找到（404）

- 使用英文城市名
- 添加国家代码：`Beijing,CN`
- 尝试访问 https://openweathermap.org/find 搜索正确名称

### 3. 超过限额（429）

- 免费版有60次/分钟限制
- 考虑添加缓存机制
- 升级到付费版

## 🎉 完成！

配置完成后，Android APP的天气功能应该能正常显示了！

如果还有问题，查看服务器日志：

```bash
tail -50 /tmp/uwsgi.log | grep -i weather
```

