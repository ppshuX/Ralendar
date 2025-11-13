<template>
  <div class="fortune-panel">
    <div class="header">
      <button class="back-btn" @click="$store.commit('updateRouterName', 'calendar')">
        ← 返回
      </button>
      <h2>🔮 今日运势</h2>
    </div>

    <div class="scroll-container">
      <div class="content-card">
        <div v-if="loading" class="loading-state">加载中...</div>

        <template v-else>
          <div class="date">{{ currentDate }}</div>

          <!-- 运势指数 -->
          <div class="fortune-card score-card">
            <div class="card-title">
              <span class="icon">📊</span> 运势指数
            </div>
            <div class="score-content">
              <div class="stars">{{ starDisplay }}</div>
              <div class="score-value">({{ fortuneScore }}分)</div>
              <div class="score-desc">{{ fortuneDescription }}</div>
            </div>
          </div>

          <!-- 黄历宜忌 -->
          <div class="fortune-card almanac-card">
            <div class="card-title">
              <span class="icon">📖</span> 黄历宜忌
            </div>
            <div class="almanac-content">
              <div class="almanac-section good">
                <span class="label">宜：</span>
                <span class="items">{{ goodThings.join('、') }}</span>
              </div>
              <div class="almanac-section bad">
                <span class="label">忌：</span>
                <span class="items">{{ badThings.join('、') }}</span>
              </div>
            </div>
          </div>

          <!-- 幸运元素 -->
          <div class="fortune-card lucky-card">
            <div class="card-title">
              <span class="icon">✨</span> 幸运元素
            </div>
            <div class="lucky-content">
              <div class="lucky-item">
                <span class="lucky-label">幸运颜色：</span>
                <span class="lucky-value">{{ luckyColor }}</span>
              </div>
              <div class="lucky-item">
                <span class="lucky-label">幸运数字：</span>
                <span class="lucky-value">{{ luckyNumber }}</span>
              </div>
              <div class="lucky-item">
                <span class="lucky-label">五行：</span>
                <span class="lucky-value">{{ luckyElement }}</span>
              </div>
            </div>
          </div>

          <!-- 温馨提示 -->
          <div class="fortune-card tip-card">
            <div class="card-title">
              <span class="icon">💡</span> 温馨提示
            </div>
            <div class="tip-content">
              {{ weekdayTip }}
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FortunePanel',
  data() {
    return {
      loading: true,
      fortuneScore: 0,
      starDisplay: '',
      fortuneDescription: '',
      goodThings: [],
      badThings: [],
      luckyColor: '',
      luckyNumber: 0,
      luckyElement: '',
      weekdayTip: '',
      solarTerm: null
    }
  },
  computed: {
    currentDate() {
      const date = new Date()
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const day = date.getDate()
      const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
      const weekday = weekdays[date.getDay()]
      
      if (this.solarTerm) {
        return `${year}年${month}月${day}日 ${weekday} • ${this.solarTerm}`
      }
      return `${year}年${month}月${day}日 ${weekday}`
    }
  },
  async mounted() {
    await this.loadFortune()
  },
  methods: {
    async loadFortune() {
      this.loading = true
      try {
        const response = await fetch('https://app7626.acapp.acwing.com.cn/api/fortune/today/?city=南昌市')
        const data = await response.json()
        
        // 设置运势数据
        this.fortuneScore = data.fortune_score
        this.starDisplay = data.star_display
        this.fortuneDescription = data.description
        this.goodThings = data.good_things
        this.badThings = data.bad_things
        this.luckyColor = data.lucky_color
        this.luckyNumber = data.lucky_number
        this.luckyElement = data.lucky_element
        this.weekdayTip = data.weekday_tip
        this.solarTerm = data.solar_term
        
      } catch (error) {
        console.error('获取运势失败:', error)
        this.fortuneDescription = '获取运势数据失败，请稍后重试'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.fortune-panel {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
}

.content-card {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  font-size: 16px;
  color: #909399;
}

.back-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

h2 {
  font-size: 22px;
  color: #303133;
  margin: 0;
}

.date {
  text-align: center;
  font-size: 16px;
  color: #606266;
  margin-bottom: 20px;
  font-weight: 500;
}

.fortune-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.fortune-card:last-child {
  margin-bottom: 0;
}

.fortune-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon {
  font-size: 20px;
}

/* 运势指数卡片 */
.score-card {
  border-left: 4px solid #fbbf24;
}

.score-content {
  text-align: center;
}

.stars {
  font-size: 24px;
  margin-bottom: 10px;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: #fbbf24;
  margin-bottom: 10px;
}

.score-desc {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

/* 黄历卡片 */
.almanac-card {
  border-left: 4px solid #667eea;
}

.almanac-section {
  margin-bottom: 12px;
  font-size: 15px;
  line-height: 1.8;
  color: #606266;
}

.almanac-section:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #303133;
}

.items {
  color: #606266;
}

/* 幸运元素卡片 */
.lucky-card {
  border-left: 4px solid #10b981;
}

.lucky-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lucky-item {
  font-size: 15px;
  color: #606266;
}

.lucky-label {
  font-weight: 600;
  color: #303133;
}

.lucky-value {
  color: #667eea;
  font-weight: 500;
}

/* 提示卡片 */
.tip-card {
  border-left: 4px solid #f59e0b;
}

.tip-content {
  font-size: 15px;
  color: #606266;
  line-height: 1.8;
}
</style>
