<template>
  <div class="calendar-grid">
    <!-- 星期标题 -->
    <div v-for="day in weekDays" :key="day" class="week-day">
      {{ day }}
    </div>

    <!-- 日期格子 -->
    <div
      v-for="(day, index) in days"
      :key="index"
      class="day-cell"
      :class="{
        'day--other': day.isOtherMonth,
        'day--today': day.isToday,
        'day--weekend': day.isWeekend,
        'day--holiday': day.isHoliday
      }"
      @click="$emit('select', day)"
    >
      <div class="day-content">
        <div class="day-number">{{ day.date }}</div>
        <div v-if="day.holiday" class="day-festival">{{ day.holiday }}</div>
      </div>
      <!-- 事件小圆点 -->
      <div v-if="day.eventCount > 0" class="event-dots">
        <span 
          v-for="i in Math.min(day.eventCount, 3)" 
          :key="i" 
          class="dot"
        ></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CalendarGridView',
  props: {
    days: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      weekDays: ['日', '一', '二', '三', '四', '五', '六']
    }
  }
}
</script>

<style scoped>
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 3px;
  background: white;
  padding: 6px;
  border-radius: 8px;
}

.week-day {
  padding: 4px;
  text-align: center;
  font-weight: 600;
  color: #666;
  font-size: 11px;
}

.day-cell {
  min-height: 48px;
  padding: 4px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.day-cell:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.day--other {
  background: #fafafa;
  color: #bbb;
}

.day--other:hover {
  border-color: #e8e8e8;
  background: #fafafa;
}

.day--today {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-color: #667eea;
  border-width: 2px;
}

.day--today .day-number {
  color: #667eea;
  font-weight: bold;
}

.day--weekend:not(.day--other) {
  background: #fff8f8;
}

.day--holiday {
  background: #fff0f0;
}

.day--holiday .day-label {
  color: #f56c6c;
  font-weight: bold;
}

.day-content {
  flex: 1;
}

.day-number {
  font-size: 13px;
  font-weight: 500;
  line-height: 1.2;
}

.day-festival {
  font-size: 9px;
  margin-top: 2px;
  line-height: 1.2;
  color: #f56c6c;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

/* 事件小圆点 */
.event-dots {
  display: flex;
  gap: 2px;
  justify-content: center;
  margin-top: 2px;
}

.dot {
  width: 4px;
  height: 4px;
  background: #667eea;
  border-radius: 50%;
  display: inline-block;
}
</style>

