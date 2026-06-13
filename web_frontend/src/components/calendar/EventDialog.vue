<template>
  <el-dialog :model-value="visible" :title="event ? '编辑事件' : '新建事件'" width="500px" @close="$emit('update:visible', false)">
    <el-form :model="form" label-width="80px">
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="请输入事件标题" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入事件描述" />
      </el-form-item>
      <el-form-item label="开始时间">
        <el-date-picker v-model="form.start_time" type="datetime" placeholder="选择开始时间" style="width: 100%" />
      </el-form-item>
      <el-form-item label="结束时间">
        <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择结束时间" style="width: 100%" />
      </el-form-item>
      <el-form-item label="地点">
        <el-input v-model="form.location" placeholder="请输入地点" />
      </el-form-item>
      <el-form-item label="提醒">
        <el-select v-model="form.reminder_minutes" placeholder="选择提醒时间">
          <el-option :value="0" label="不提醒" />
          <el-option :value="5" label="5分钟前" />
          <el-option :value="15" label="15分钟前" />
          <el-option :value="30" label="30分钟前" />
          <el-option :value="60" label="1小时前" />
          <el-option :value="1440" label="1天前" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  event: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'save'])

const form = ref({
  title: '',
  description: '',
  start_time: '',
  end_time: '',
  location: '',
  reminder_minutes: 15
})

watch(() => props.event, (val) => {
  if (val) {
    form.value = { ...val }
  } else {
    form.value = {
      title: '',
      description: '',
      start_time: '',
      end_time: '',
      location: '',
      reminder_minutes: 15
    }
  }
}, { immediate: true })

const handleSave = () => {
  emit('save', { ...form.value })
  emit('update:visible', false)
}
</script>
