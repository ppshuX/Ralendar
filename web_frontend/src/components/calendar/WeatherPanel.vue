<template>
  <div class="weather-content">
    <div class="sidebar-header text-center mb-3">
      <h4>🌤️ 今日天气</h4>
      <p class="text-secondary small mb-0">
        {{ displayCity }}
      </p>
    </div>

    <!-- 加载中状态 -->
    <div v-if="loading" class="loading-state text-center py-5">
      <div class="spinner-border text-primary mb-3" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
      <p class="text-muted">正在获取天气信息...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state text-center py-5">
      <div class="error-icon mb-3">⚠️</div>
      <p class="text-danger mb-3">{{ error }}</p>
      <el-button type="primary" size="small" @click="loadWeather">
        <i class="bi bi-arrow-clockwise"></i> 重试
      </el-button>
    </div>

    <!-- 天气信息 -->
    <div v-else-if="weatherData" class="weather-info">
      <!-- 主要天气卡片 -->
      <div class="weather-card main">
        <div class="weather-main-info">
          <div class="weather-icon">{{ getWeatherIcon(weatherData.weather) }}</div>
          <div class="temperature-info">
            <div class="temperature">{{ weatherData.temperature }}°C</div>
            <div class="weather-desc">{{ weatherData.weather }}</div>
          </div>
        </div>
      </div>

      <!-- 详细信息 -->
      <div class="weather-details">
        <h5 class="section-title">
          <i class="bi bi-info-circle"></i> 详细信息
        </h5>
        
        <div class="detail-grid">
          <div class="detail-item" v-if="weatherData.humidity !== '--'">
            <div class="detail-icon">💧</div>
            <div class="detail-info">
              <div class="detail-label">湿度</div>
              <div class="detail-value">{{ weatherData.humidity }}%</div>
            </div>
          </div>

          <div class="detail-item" v-if="weatherData.windDir !== '--'">
            <div class="detail-icon">🍃</div>
            <div class="detail-info">
              <div class="detail-label">风向</div>
              <div class="detail-value">{{ weatherData.windDir }}</div>
            </div>
          </div>

          <div class="detail-item" v-if="weatherData.windScale !== '--'">
            <div class="detail-icon">💨</div>
            <div class="detail-info">
              <div class="detail-label">风力</div>
              <div class="detail-value">{{ weatherData.windScale }}级</div>
            </div>
          </div>

          <div class="detail-item" v-if="weatherData.feelsLike !== '--'">
            <div class="detail-icon">🌡️</div>
            <div class="detail-info">
              <div class="detail-label">体感</div>
              <div class="detail-value">{{ weatherData.feelsLike }}°C</div>
            </div>
          </div>
        </div>

        <!-- 更新时间 -->
        <div v-if="weatherData.updateTime" class="update-time">
          <i class="bi bi-clock"></i> 更新于 {{ weatherData.updateTime }}
        </div>
      </div>

      <!-- 城市切换按钮 -->
      <div class="city-selector">
        <button 
          @click="showCityPanel = !showCityPanel"
          class="change-city-btn"
        >
          <i class="bi bi-geo-alt"></i> 切换城市
          <i :class="showCityPanel ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
        </button>
      </div>

      <!-- 城市选择面板（展开/收起） -->
      <div v-show="showCityPanel" class="city-panel">
        <div class="city-panel-title">选择城市</div>
        
        <div class="city-grid">
          <button
            v-for="cityOption in popularCities"
            :key="cityOption"
            :class="['city-chip', { active: city === cityOption }]"
            @click="changeCity(cityOption)"
          >
            {{ cityOption }}
          </button>
        </div>
        
        <div class="custom-city-input">
          <input
            v-model="customCity"
            type="text"
            placeholder="输入其他城市名称"
            @keyup.enter="changeCity(customCity)"
            class="city-input"
          />
          <button @click="changeCity(customCity)" class="city-confirm-btn">
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { weatherAPI } from '@/api'

// 数据
const weatherData = ref(null)
const loading = ref(false)
const error = ref(null)
const city = ref('北京')
const customCity = ref('')
const showCityPanel = ref(false)

// 热门城市列表
const popularCities = [
  '北京', '上海', '广州', '深圳', 
  '杭州', '南京', '成都', '西安',
  '武汉', '重庆', '天津', '苏州'
]

// 显示的城市名称
const displayCity = computed(() => {
  if (weatherData.value) {
    return weatherData.value.location
  }
  return city.value
})

// 加载天气
const loadWeather = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await weatherAPI.getWeather(city.value)
    
    if (response.success) {
      weatherData.value = response.data
      // 保存到localStorage
      localStorage.setItem('weather_city', city.value)
    } else {
      error.value = response.error || '获取天气失败'
    }
  } catch (err) {
    console.error('获取天气失败:', err)
    error.value = err.response?.data?.error || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 切换城市
const changeCity = (newCity) => {
  if (!newCity || !newCity.trim()) {
    ElMessage.warning('请输入城市名称')
    return
  }
  
  city.value = newCity.trim()
  showCityPanel.value = false
  customCity.value = ''
  loadWeather()
  ElMessage.success('已切换到 ' + newCity)
}

// 根据天气状况返回图标
const getWeatherIcon = (weather) => {
  const iconMap = {
    '晴': '☀️',
    '多云': '⛅',
    '阴': '☁️',
    '小雨': '🌦️',
    '中雨': '🌧️',
    '大雨': '⛈️',
    '雷暴': '⚡',
    '雪': '❄️',
    '雾': '🌫️',
    '霾': '😷',
    '沙尘暴': '🌪️'
  }
  
  for (const [key, icon] of Object.entries(iconMap)) {
    if (weather && weather.includes(key)) {
      return icon
    }
  }
  
  return '🌤️'
}

// 组件挂载时加载天气
onMounted(() => {
  // 从localStorage恢复上次选择的城市
  const savedCity = localStorage.getItem('weather_city')
  if (savedCity) {
    city.value = savedCity
  }
  
  loadWeather()
})
</script>

<style scoped>
.weather-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

.sidebar-header h4 {
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
}

.loading-state, .error-state {
  padding: 40px 20px;
}

.error-icon {
  font-size: 48px;
  opacity: 0.5;
}

.weather-card.main {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
  border-radius: 16px;
  padding: 24px;
  border-left: 4px solid #667eea;
}

.weather-main-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.weather-icon {
  font-size: 64px;
}

.temperature-info {
  flex: 1;
}

.temperature {
  font-size: 48px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 8px;
}

.weather-desc {
  font-size: 20px;
  color: var(--text-secondary);
  font-weight: 500;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  font-size: 18px;
  color: var(--primary-color);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: var(--bg-secondary);
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.detail-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.detail-icon {
  font-size: 28px;
}

.detail-info {
  flex: 1;
}

.detail-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 2px;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.update-time {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-tertiary);
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.city-selector {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.change-city-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--primary-color);
  background: transparent;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.change-city-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
}

.city-panel {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.city-panel-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  text-align: center;
}

.city-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.city-chip {
  padding: 8px 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.city-chip:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.city-chip.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-color: transparent;
}

.custom-city-input {
  display: flex;
  gap: 8px;
}

.city-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;
}

.city-input:focus {
  border-color: var(--primary-color);
}

.city-confirm-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.city-confirm-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .sidebar-header h4 {
    font-size: 18px;
  }
  
  .weather-icon {
    font-size: 56px;
  }
  
  .temperature {
    font-size: 40px;
  }
  
  .weather-desc {
    font-size: 18px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .city-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .city-chip {
    font-size: 13px;
    padding: 6px 10px;
  }
}

@media (max-width: 576px) {
  .weather-card.main {
    padding: 20px;
  }
  
  .weather-icon {
    font-size: 48px;
  }
  
  .temperature {
    font-size: 36px;
  }
  
  .weather-desc {
    font-size: 16px;
  }
  
  .detail-item {
    padding: 12px;
  }
  
  .detail-icon {
    font-size: 24px;
  }
}
</style>

