<template>
  <div class="weather-panel">
    <div class="header">
      <button class="back-btn" @click="$store.commit('updateRouterName', 'calendar')">
        ← 返回
      </button>
      <h2>🌤️ 今日天气</h2>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="weather-info">
        <!-- 当前天气 -->
        <div class="current-weather">
          <div class="city-name">{{ city }}</div>
          <div class="temp-large">{{ weather.temperature }}°C</div>
          <div class="weather-desc">{{ weather.weather }}</div>
          <div class="weather-icon">{{ getWeatherIcon(weather.weather) }}</div>
        </div>

        <!-- 详细信息 -->
        <div class="weather-details">
          <div class="detail-item">
            <span class="detail-icon">🌡️</span>
            <span class="detail-label">体感温度</span>
            <span class="detail-value">{{ weather.feelsLike }}°C</span>
          </div>
          <div class="detail-item">
            <span class="detail-icon">💧</span>
            <span class="detail-label">湿度</span>
            <span class="detail-value">{{ weather.humidity }}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-icon">💨</span>
            <span class="detail-label">风力</span>
            <span class="detail-value">{{ weather.windDirection }} {{ weather.windPower }}级</span>
          </div>
        </div>

        <!-- 切换城市 -->
        <div class="city-selector">
          <button class="city-btn" @click="changeCity('北京市')">北京</button>
          <button class="city-btn" @click="changeCity('上海市')">上海</button>
          <button class="city-btn" @click="changeCity('广州市')">广州</button>
          <button class="city-btn" @click="changeCity('深圳市')">深圳</button>
          <button class="city-btn" @click="changeCity('成都市')">成都</button>
          <button class="city-btn" @click="changeCity('南昌市')">南昌</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WeatherPanel',
  data() {
    return {
      city: '南昌市',
      weather: {},
      loading: false,
      error: null
    }
  },
  mounted() {
    this.loadWeather()
  },
  methods: {
    async loadWeather() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch(`https://app7626.acapp.acwing.com.cn/api/weather/?location=${encodeURIComponent(this.city)}`)
        
        if (!response.ok) {
          throw new Error('获取天气失败')
        }

        const data = await response.json()
        this.weather = data
      } catch (err) {
        console.error('天气加载错误:', err)
        this.error = '获取天气信息失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    changeCity(cityName) {
      this.city = cityName
      this.loadWeather()
    },
    getWeatherIcon(weather) {
      if (!weather) return '☁️'
      const w = weather.toLowerCase()
      if (w.includes('晴')) return '☀️'
      if (w.includes('云')) return '☁️'
      if (w.includes('雨')) return '🌧️'
      if (w.includes('雪')) return '❄️'
      if (w.includes('雾') || w.includes('霾')) return '🌫️'
      if (w.includes('风')) return '💨'
      return '🌤️'
    }
  }
}
</script>

<style scoped>
.weather-panel {
  padding: 20px;
  background: linear-gradient(to bottom, #4facfe, #00f2fe);
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.back-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.back-btn:hover {
  background: white;
  transform: translateY(-2px);
}

h2 {
  font-size: 24px;
  color: white;
  margin: 0;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  color: white;
}

.error {
  background: rgba(255, 0, 0, 0.1);
  border-radius: 8px;
}

/* 当前天气 */
.current-weather {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  text-align: center;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.city-name {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}

.temp-large {
  font-size: 64px;
  font-weight: 700;
  color: #667eea;
  line-height: 1;
  margin-bottom: 10px;
}

.weather-desc {
  font-size: 20px;
  color: #606266;
  margin-bottom: 15px;
}

.weather-icon {
  font-size: 48px;
}

/* 详细信息 */
.weather-details {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 10px;
  background: #f5f7fa;
  border-radius: 10px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-icon {
  font-size: 24px;
}

.detail-label {
  flex: 1;
  font-size: 15px;
  color: #606266;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 城市选择器 */
.city-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.city-btn {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid transparent;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  transition: all 0.3s;
}

.city-btn:hover {
  background: white;
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
}
</style>

