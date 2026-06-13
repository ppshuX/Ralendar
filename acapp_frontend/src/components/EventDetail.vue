<template>
  <div class="event-detail">
    <div class="header">
      <button class="back-btn" @click="goBack">◀ 返回</button>
      <h2>事件详情</h2>
      <div class="header-actions">
        <button class="edit-btn" @click="goToEdit">✏️</button>
        <button class="delete-btn" @click="confirmDelete">🗑️</button>
      </div>
    </div>

    <div v-if="loading" class="loading">⏳ 加载中...</div>
    
    <div v-else-if="!event" class="empty">
      📭 事件不存在
    </div>

    <div v-else class="detail-content">
      <div class="detail-card">
        <div class="detail-title">{{ event.title }}</div>
        
        <div class="detail-row">
          <span class="detail-icon">🕐</span>
          <span class="detail-label">时间</span>
          <span class="detail-value">{{ formatDateTime(event.start_time) }}</span>
        </div>

        <div v-if="event.end_time" class="detail-row">
          <span class="detail-icon">🔚</span>
          <span class="detail-label">结束时间</span>
          <span class="detail-value">{{ formatDateTime(event.end_time) }}</span>
        </div>

        <div v-if="event.location" class="detail-row">
          <span class="detail-icon">📍</span>
          <span class="detail-label">地点</span>
          <span class="detail-value">{{ event.location }}</span>
        </div>

        <div v-if="event.reminder_minutes" class="detail-row">
          <span class="detail-icon">⏰</span>
          <span class="detail-label">提前提醒</span>
          <span class="detail-value">{{ event.reminder_minutes }} 分钟</span>
        </div>

        <div v-if="event.description" class="detail-section">
          <div class="section-title">📝 备注</div>
          <div class="detail-desc">{{ event.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'EventDetail',
  
  data() {
    return {
      loading: false,
      event: null
    }
  },
  
  computed: {
    ...mapGetters(['getEventById']),
    
    eventId() {
      return this.$store.state.router.router_params.id
    }
  },
  
  mounted() {
    this.loadEvent()
  },
  
  methods: {
    loadEvent() {
      if (this.eventId) {
        this.event = this.getEventById(this.eventId)
      }
    },
    
    goBack() {
      this.$store.commit('updateRouterName', 'event_list')
      this.$store.commit('updateRouterParams', {})
    },
    
    goToEdit() {
      this.$store.commit('updateRouterName', 'edit_event')
      this.$store.commit('updateRouterParams', { id: this.eventId })
    },
    
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return ''
      const date = new Date(dateTimeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}`
    },
    
    async confirmDelete() {
      if (!confirm('确定删除这个事件吗？')) return
      
      const success = await this.$store.dispatch('deleteEvent', this.eventId)
      if (success) {
        alert('删除成功！')
        this.goBack()
      } else {
        alert('删除失败！')
      }
    }
  }
}
</script>

<style scoped>
.event-detail {
  width: 100%;
  height: 100%;
  padding: 8px;
  background: #f8f9fa;
  overflow-y: auto;
  font-size: 12px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  padding: 8px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  color: white;
}

.header h2 {
  flex: 1;
  text-align: center;
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.back-btn,
.edit-btn,
.delete-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.back-btn:hover,
.edit-btn:hover,
.delete-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.header-actions {
  display: flex;
  gap: 4px;
}

.loading,
.empty {
  text-align: center;
  padding: 30px 15px;
  background: white;
  border-radius: 6px;
  color: #999;
  font-size: 13px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-card {
  background: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f5f7fa;
}

.detail-row:last-of-type {
  border-bottom: none;
}

.detail-icon {
  font-size: 14px;
}

.detail-label {
  color: #909399;
  font-size: 12px;
  width: 70px;
  flex-shrink: 0;
}

.detail-value {
  color: #303133;
  font-size: 13px;
  font-weight: 500;
}

.detail-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.detail-desc {
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
}
</style>
