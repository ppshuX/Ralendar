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
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tool-btn {
  padding: 10px 16px;
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.tool-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.tool-btn.primary {
  background: #67c23a;
  color: white;
  border-color: #67c23a;
}

.tool-btn.primary:hover {
  background: #85ce61;
  border-color: #85ce61;
}

.tool-btn.fortune {
  background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
  color: #2d3436;
  border-color: #fdcb6e;
}

.tool-btn.fortune:hover {
  background: linear-gradient(135deg, #fdcb6e, #f39c12);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(253, 203, 110, 0.4);
}

.tool-btn.weather {
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
  border-color: #0984e3;
}

.tool-btn.weather:hover {
  background: linear-gradient(135deg, #0984e3, #0652dd);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(9, 132, 227, 0.4);
}

.tool-btn.ai {
  background: linear-gradient(135deg, #a29bfe, #6c5ce7);
  color: white;
  border-color: #6c5ce7;
}

.tool-btn.ai:hover {
  background: linear-gradient(135deg, #6c5ce7, #5f3dc4);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(108, 92, 231, 0.4);
}
</style>

