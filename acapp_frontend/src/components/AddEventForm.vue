<template>
  <div class="add-event-form">
    <div class="header">
      <button class="back-btn" @click="goBack">◀ 返回</button>
      <h2>添加日程</h2>
      <button class="save-btn" @click="submitForm" :disabled="submitting">
        {{ submitting ? '保存中...' : '✓ 保存' }}
      </button>
    </div>

    <div class="form-content">
      <div class="form-card">
        <div class="form-group">
          <label class="form-label">📅 标题 <span class="required">*</span></label>
          <input 
            v-model="form.title" 
            type="text" 
            class="form-input" 
            placeholder="请输入日程标题"
          />
        </div>

        <div class="form-group">
          <label class="form-label">🕐 开始时间 <span class="required">*</span></label>
          <input 
            v-model="form.start_time" 
            type="datetime-local" 
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">🔚 结束时间</label>
          <input 
            v-model="form.end_time" 
            type="datetime-local" 
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">📍 地点</label>
          <input 
            v-model="form.location" 
            type="text" 
            class="form-input" 
            placeholder="请输入地点（可选）"
          />
        </div>

        <div class="form-group">
          <label class="form-label">⏰ 提前提醒</label>
          <select v-model="form.reminder_minutes" class="form-input">
            <option :value="0">不提醒</option>
            <option :value="5">5 分钟前</option>
            <option :value="10">10 分钟前</option>
            <option :value="15">15 分钟前</option>
            <option :value="30">30 分钟前</option>
            <option :value="60">1 小时前</option>
            <option :value="1440">1 天前</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">📝 备注</label>
          <textarea 
            v-model="form.description" 
            class="form-textarea" 
            placeholder="请输入备注信息（可选）"
            rows="4"
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddEventForm',
  
  data() {
    return {
      submitting: false,
      form: {
        title: '',
        start_time: '',
        end_time: '',
        location: '',
        description: '',
        reminder_minutes: 15
      }
    }
  },
  
  mounted() {
    const params = this.$store.state.router.router_params
    if (params.date) {
      this.form.start_time = `${params.date}T09:00`
    }
  },
  
  methods: {
    goBack() {
      this.$store.commit('updateRouterName', 'calendar')
      this.$store.commit('updateRouterParams', {})
    },
    
    async submitForm() {
      if (!this.form.title.trim()) {
        alert('请输入标题')
        return
      }
      
      if (!this.form.start_time) {
        alert('请选择开始时间')
        return
      }
      
      this.submitting = true
      
      try {
        const eventData = {
          title: this.form.title.trim(),
          start_time: this.form.start_time,
          location: this.form.location.trim() || null,
          description: this.form.description.trim() || null,
          reminder_minutes: this.form.reminder_minutes
        }
        
        if (this.form.end_time) {
          eventData.end_time = this.form.end_time
        }
        
        const success = await this.$store.dispatch('createEvent', eventData)
        
        if (success) {
          alert('创建成功！')
          this.goBack()
        } else {
          alert('创建失败，请重试')
        }
      } catch (error) {
        console.error('创建事件失败:', error)
        alert('创建失败：' + error.message)
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.add-event-form {
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
.save-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-card {
  background: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.form-group {
  margin-bottom: 12px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 6px;
}

.required {
  color: #f56c6c;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1.5px solid #dcdfe6;
  border-radius: 6px;
  font-size: 13px;
  color: #303133;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

select.form-input {
  cursor: pointer;
  background: white;
}
</style>
