<template>
  <div class="fortune-panel">
    <div class="header">
      <button class="back-btn" @click="$store.commit('updateRouterName', 'calendar')">
        ← 返回
      </button>
      <h2>🔮 今日运势</h2>
    </div>

    <div class="content">
      <div class="date">{{ currentDate }}</div>

      <!-- 运势指数 -->
      <div class="fortune-card score-card">
        <div class="card-title">
          <span class="icon">📊</span> 运势指数
        </div>
        <div class="score-content">
          <div class="stars">{{ getStars() }}</div>
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
            <span class="lucky-label">幸运方位：</span>
            <span class="lucky-value">{{ luckyDirection }}</span>
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
    </div>
  </div>
</template>

<script>
export default {
  name: 'FortunePanel',
  data() {
    return {
      fortuneScore: 0,
      fortuneDescription: '',
      goodThings: [],
      badThings: [],
      luckyColor: '',
      luckyNumber: '',
      luckyDirection: '',
      weekdayTip: ''
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
      return `${year}年${month}月${day}日 ${weekday}`
    }
  },
  mounted() {
    this.generateFortune()
  },
  methods: {
    generateFortune() {
      const date = new Date()
      const seed = date.getFullYear() * 10000 + (date.getMonth() + 1) * 100 + date.getDate()
      
      // 简单的伪随机数生成器
      const random = (min, max) => {
        const x = Math.sin(seed + min * 100) * 10000
        return Math.floor((x - Math.floor(x)) * (max - min + 1)) + min
      }

      // 运势指数
      this.fortuneScore = random(60, 95)
      
      // 运势描述
      const descriptions = [
        '诸事顺利，心情愉悦。',
        '贵人相助，事半功倍。',
        '好运连连，万事如意。',
        '平稳度过，顺心如意。',
        '机会多多，把握当下。'
      ]
      this.fortuneDescription = descriptions[random(0, descriptions.length - 1)]

      // 宜忌
      const goodThingsList = ['出行', '会友', '开市', '祈福', '求财', '签约', '面试', '学习', '运动', '社交']
      const badThingsList = ['争执', '熬夜', '暴饮暴食', '冲动消费', '懒散', '抱怨', '拖延', '负能量']
      
      this.goodThings = []
      for (let i = 0; i < 4; i++) {
        const index = random(0, goodThingsList.length - 1)
        if (!this.goodThings.includes(goodThingsList[index])) {
          this.goodThings.push(goodThingsList[index])
        }
      }
      
      this.badThings = []
      for (let i = 0; i < 3; i++) {
        const index = random(0, badThingsList.length - 1)
        if (!this.badThings.includes(badThingsList[index])) {
          this.badThings.push(badThingsList[index])
        }
      }

      // 幸运元素
      const colors = ['红色', '蓝色', '紫色', '绿色', '黄色', '橙色', '粉色']
      this.luckyColor = colors[random(0, colors.length - 1)]
      this.luckyNumber = random(1, 9)
      const directions = ['东方', '南方', '西方', '北方', '东南', '东北', '西南', '西北']
      this.luckyDirection = directions[random(0, directions.length - 1)]

      // 工作日提示
      const dayOfWeek = date.getDay()
      const tips = [
        '今天是周日，好好休息，为新的一周做准备！',
        '周一加油！新的一周开始了，保持积极的心态。',
        '周二继续努力，保持专注和高效。',
        '周三已经过半，坚持就是胜利！',
        '周四啦，离周末又近了一步！',
        '周五到了，本周即将圆满结束！',
        '周六愉快！享受休闲时光！'
      ]
      this.weekdayTip = tips[dayOfWeek]
    },
    getStars() {
      if (this.fortuneScore >= 90) return '⭐⭐⭐⭐⭐'
      if (this.fortuneScore >= 80) return '⭐⭐⭐⭐'
      if (this.fortuneScore >= 70) return '⭐⭐⭐'
      if (this.fortuneScore >= 60) return '⭐⭐'
      return '⭐'
    }
  }
}
</script>

<style scoped>
.fortune-panel {
  padding: 20px;
  background: #f5f7fa;
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
  font-size: 24px;
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

.fortune-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
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
  background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
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
  color: #e17055;
  margin-bottom: 10px;
}

.score-desc {
  font-size: 16px;
  color: #d63031;
  font-weight: 500;
}

/* 黄历卡片 */
.almanac-card {
  background: linear-gradient(135deg, #a29bfe, #6c5ce7);
}

.almanac-card .card-title {
  color: white;
}

.almanac-section {
  margin-bottom: 12px;
  font-size: 15px;
  line-height: 1.8;
}

.almanac-section:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: white;
}

.items {
  color: rgba(255, 255, 255, 0.95);
}

/* 幸运元素卡片 */
.lucky-card {
  background: linear-gradient(135deg, #81ecec, #00b894);
}

.lucky-card .card-title {
  color: white;
}

.lucky-item {
  margin-bottom: 10px;
  font-size: 15px;
}

.lucky-item:last-child {
  margin-bottom: 0;
}

.lucky-label {
  font-weight: 600;
  color: white;
}

.lucky-value {
  color: #2d3436;
  font-weight: 500;
}

/* 提示卡片 */
.tip-card {
  background: linear-gradient(135deg, #fab1a0, #e17055);
}

.tip-card .card-title {
  color: white;
}

.tip-content {
  font-size: 15px;
  color: white;
  line-height: 1.8;
}
</style>

