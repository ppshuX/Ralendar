<template>
  <div class="event-list-panel">
    <div class="panel-header">
      <h4>{{ selectedDate || '全部日程' }}</h4>
      <button class="add-btn" @click="$emit('add')">
        <i class="bi bi-plus-lg"></i>
      </button>
    </div>

    <div v-if="events.length === 0" class="empty-state">
      <i class="bi bi-calendar-x"></i>
      <p>暂无日程</p>
    </div>

    <div v-else class="event-list">
      <div v-for="event in events" :key="event.id" class="event-card" @click="$emit('select', event)">
        <div class="event-time">{{ formatEventTime(event.start_time) }}</div>
        <div class="event-title">{{ event.title }}</div>
        <div v-if="event.location" class="event-location">
          <i class="bi bi-geo-alt"></i> {{ event.location }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  events: {
    type: Array,
    default: () => []
  },
  formatEventTime: {
    type: Function,
    default: (dateTime) => dateTime
  },
  selectedDate: {
    type: String,
    default: ''
  }
})

defineEmits(['select', 'add'])
</script>

<style scoped>
.event-list-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.panel-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.add-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.add-btn:hover {
  transform: scale(1.1);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #c0c4cc;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-state p {
  font-size: 14px;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

.event-card {
  padding: 12px;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid #667eea;
}

.event-card:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.event-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.event-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.event-location {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
