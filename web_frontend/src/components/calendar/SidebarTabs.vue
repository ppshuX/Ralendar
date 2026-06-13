<template>
  <div class="sidebar-tabs">
    <button v-for="tab in tabs" :key="tab.id" class="tab-item" :class="{ active: modelValue === tab.id }" @click="$emit('update:modelValue', tab.id)">
      <i :class="['bi', tab.icon]"></i>
      <span>{{ tab.label }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  tabs: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.sidebar-tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: #f0f2f5;
  border-radius: 12px;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 8px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-item:hover {
  background: rgba(255, 255, 255, 0.8);
}

.tab-item.active {
  background: white;
  color: #667eea;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.tab-item i {
  font-size: 16px;
}

@media (max-width: 576px) {
  .tab-item {
    padding: 8px 4px;
    font-size: 11px;
    gap: 4px;
  }

  .tab-item i {
    font-size: 14px;
  }
}
</style>
