<template>
  <el-dialog :model-value="visible" title="事件详情" width="500px" @close="$emit('update:visible', false)">
    <div v-if="event" class="event-detail">
      <div class="detail-header">
        <h3>{{ event.title }}</h3>
      </div>
      <div class="detail-body">
        <div class="detail-item">
          <span class="label"><i class="bi bi-clock"></i> 时间</span>
          <span class="value">{{ formatTime(event.start_time) }} - {{ formatTime(event.end_time) }}</span>
        </div>
        <div v-if="event.location" class="detail-item">
          <span class="label"><i class="bi bi-geo-alt"></i> 地点</span>
          <span class="value">{{ event.location }}</span>
        </div>
        <div v-if="event.description" class="detail-item">
          <span class="label"><i class="bi bi-text-left"></i> 描述</span>
          <span class="value">{{ event.description }}</span>
        </div>
        <div v-if="lunarDate" class="detail-item">
          <span class="label"><i class="bi bi-calendar3"></i> 农历</span>
          <span class="value">{{ lunarDate }}</span>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button @click="$emit('edit', event)">编辑</el-button>
      <el-button type="danger" @click="$emit('delete', event)">删除</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
defineProps({
  visible: Boolean,
  event: Object,
  lunarDate: {
    type: String,
    default: ''
  }
})

defineEmits(['update:visible', 'edit', 'delete'])

const formatTime = (dateTime) => {
  if (!dateTime) return ''
  const d = new Date(dateTime)
  const month = d.getMonth() + 1
  const day = d.getDate()
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${hour}:${minute}`
}
</script>

<style scoped>
.event-detail {
  padding: 0;
}

.detail-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  gap: 12px;
}

.detail-item .label {
  color: #909399;
  font-size: 14px;
  min-width: 70px;
}

.detail-item .value {
  color: #303133;
  font-size: 14px;
}
</style>
