<template>
  <div class="week-view">
    <div class="day-selector">
      <button v-for="day in weekDays" :key="day.date" class="day-btn" :class="{ active: day.date === selectedDate }" @click="selectDate(day.date)">
        <span class="weekday">{{ day.weekday }}</span>
        <span class="day-num" :class="{ today: day.isToday }">{{ day.dayNum }}</span>
      </button>
    </div>

    <div class="time-grid" ref="timeGridRef">
      <div v-for="hour in 24" :key="hour" class="time-row">
        <div class="time-label">{{ String(hour - 1).padStart(2, '0') }}:00</div>
        <div class="time-cell" :class="{ 'has-event': hasEventAtHour(hour - 1) }">
          <div v-for="event in getEventsAtHour(hour - 1)" :key="event.id" class="event-block" @click="$emit('event-click', { event: { extendedProps: event, start: event.start_time } })">
            {{ event.title }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  selectedDate: {
    type: String,
    default: ''
  },
  events: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['date-select', 'event-click', 'date-click', 'switch-view'])

const weekDays = computed(() => {
  const today = new Date()
  const currentDay = today.getDay()
  const monday = new Date(today)
  monday.setDate(today.getDate() - (currentDay === 0 ? 6 : currentDay - 1))

  const days = []
  const weekdays = ['一', '二', '三', '四', '五', '六', '日']

  for (let i = 0; i < 7; i++) {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    days.push({
      date: dateStr,
      weekday: weekdays[i],
      dayNum: date.getDate(),
      isToday: dateStr === `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
    })
  }

  return days
})

const hasEventAtHour = (hour) => {
  return props.events.some(event => {
    const start = new Date(event.start_time)
    return start.getHours() === hour
  })
}

const getEventsAtHour = (hour) => {
  return props.events.filter(event => {
    const start = new Date(event.start_time)
    return start.getHours() === hour
  })
}

const selectDate = (dateStr) => {
  emit('date-select', dateStr)
  emit('date-click', { dateStr })
}
</script>

<style scoped>
.week-view {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.day-selector {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  padding: 8px;
  gap: 4px;
}

.day-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  border: none;
  background: transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.day-btn:hover {
  background: #f5f7fa;
}

.day-btn.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.day-btn.active .weekday,
.day-btn.active .day-num {
  color: white;
}

.weekday {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.day-num {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.day-num.today {
  background: #667eea;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-grid {
  max-height: 500px;
  overflow-y: auto;
}

.time-row {
  display: flex;
  border-bottom: 1px solid #f5f5f5;
  min-height: 48px;
}

.time-label {
  width: 60px;
  padding: 12px 8px;
  font-size: 12px;
  color: #909399;
  text-align: right;
  flex-shrink: 0;
}

.time-cell {
  flex: 1;
  padding: 4px 8px;
  position: relative;
  min-height: 48px;
}

.time-cell.has-event {
  background: rgba(102, 126, 234, 0.05);
}

.event-block {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.event-block:hover {
  transform: scale(1.02);
}
</style>
