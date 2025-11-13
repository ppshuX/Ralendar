<template>
  <div class="toolbar">
    <button class="tool-btn primary" @click="$emit('show-list')">
      📝 我的日程 ({{ eventCount }})
    </button>
    <button class="tool-btn" @click="$emit('today')">
      📅 今天
    </button>
    <button class="tool-btn fortune" @click="$emit('show-fortune')">
      🔮 今日运势
    </button>
    <button class="tool-btn weather" @click="$emit('show-weather')">
      🌤️ 天气
    </button>
    <button class="tool-btn ai" @click="$emit('show-ai')">
      🤖 AI助手
    </button>
  </div>
</template>

<script>
export default {
  name: 'ToolBar',
  props: {
    eventCount: {
      type: Number,
      default: 0
    }
  }
}
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  padding: 0 10px;
}

.tool-btn {
  flex: 1;
  min-width: 80px;
  max-width: 120px;
  padding: 10px 12px;
  background: white;
  color: #606266;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tool-btn:hover {
  background: #f5f7fa;
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.15);
}

.tool-btn.primary {
  background: #667eea;
  color: white;
  border-color: #667eea;
  font-weight: 500;
}

.tool-btn.primary:hover {
  background: #5568d3;
  border-color: #5568d3;
}

.tool-btn.fortune,
.tool-btn.weather,
.tool-btn.ai {
  background: white;
  color: #606266;
  border-color: #e0e0e0;
}

.tool-btn.fortune:hover {
  border-color: #fbbf24;
  color: #fbbf24;
}

.tool-btn.weather:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.tool-btn.ai:hover {
  border-color: #8b5cf6;
  color: #8b5cf6;
}
</style>

