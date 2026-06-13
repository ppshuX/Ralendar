<template>
  <div class="calendar-page">
    <ContentField>
      <!-- 天气横条：始终显示 -->
      <WeatherBar />
      
      <div class="row g-3 justify-content-center">
        <!-- 日历：桌面端左侧，移动端上方全宽 -->
        <div class="col-lg-6 col-md-6 col-12">
          <!-- 月视图和日视图 -->
          <div v-if="currentView !== 'week'" class="calendar-wrapper">
            <FullCalendar ref="fullCalendarRef" :options="calendarOptions" />
          </div>
          
          <!-- 周视图（自定义） -->
          <div v-else class="calendar-wrapper">
            <WeekView 
              ref="weekViewRef"
              :selected-date="selectedDateForFilter"
              :events="eventsList"
              @date-select="handleWeekDateSelect"
              @event-click="handleEventClick"
              @date-click="handleDateClick"
              @switch-view="handleViewSwitch"
            />
          </div>
        </div>
        
        <!-- 侧边栏：桌面端右侧，移动端下方全宽 -->
        <div class="col-lg-6 col-md-6 col-12">
          <CalendarSidebar
            :tabs="tabs"
            v-model:activeTab="activeTab"
            :events="filteredEvents"
            :selected-date="selectedDateLabel"
            :format-event-time="formatEventTime"
            :today-holidays="todayHolidays"
            :selected-date-iso="selectedDateForFilter"
            :holidays-map="holidaysMap"
            @select-event="handleEventCardSelect"
            @add-event="openAddDialogForSelectedDate"
          />
        </div>
      </div>
      
      <!-- 浮动添加按钮：仅登录后显示 -->
      <button v-if="isLoggedIn" class="floating-add-btn" @click="openAddDialog">
        <i class="bi bi-plus-lg"></i>
      </button>
      
      <!-- AI创建按钮：登录后显示 -->
      <button v-if="isLoggedIn" class="floating-ai-btn" @click="showAIDialog = true">
        <i class="bi bi-magic"></i>
      </button>
      
      <!-- 未登录引导按钮 -->
      <button v-else class="floating-login-btn" @click="router.push('/login')">
        <i class="bi bi-box-arrow-in-right"></i>
        <span class="login-text">登录</span>
      </button>
    </ContentField>

    <EventDialog
      v-model:visible="showAddDialog"
      :event="editingEvent"
      @save="saveEvent"
    />

    <EventDetail
      v-model:visible="showDetailDialog"
      :event="selectedEvent"
      :lunar-date="lunarDateText"
      @edit="editEvent"
      @delete="deleteEvent"
    />

    <AIEventDialog
      v-model="showAIDialog"
      @create="handleAICreate"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import WeekView from '@/components/calendar/WeekView.vue'
import ContentField from '../components/ContentField.vue'
import WeatherBar from '../components/calendar/WeatherBar.vue'
import EventDialog from '../components/calendar/EventDialog.vue'
import EventDetail from '../components/calendar/EventDetail.vue'
import CalendarSidebar from '../components/calendar/CalendarSidebar.vue'
import AIEventDialog from '../components/calendar/AIEventDialog.vue'
import { useCalendarEvents } from '../composables/useCalendarEvents'
import { useHolidayData } from '../composables/useHolidayData'
import { useSidebarTabs } from '../composables/useSidebarTabs'

const router = useRouter()

// FullCalendar 组件引用
const fullCalendarRef = ref(null)
const weekViewRef = ref(null)
const currentView = ref('month') // 'month', 'week', 'day'

// 检查登录状态
const isLoggedIn = ref(false)
const checkLoginStatus = () => {
  const token = localStorage.getItem('access_token')
  isLoggedIn.value = !!token
  return isLoggedIn.value
}

// 未登录提示并跳转登录
const requireLogin = (action = '该操作') => {
  ElMessage.warning({
    message: `${action}需要登录，请先登录`,
    duration: 3000
  })
  setTimeout(() => {
    router.push({ name: 'login', query: { redirect: '/calendar' } })
  }, 500)
  return false
}

const {
  holidaysMap,
  todayHolidays,
  loadHolidays,
  loadTodayHolidays,
  getHolidaysForDate,
  applyHolidayEvents
} = useHolidayData()

// 日期选择回调
const handleDateSelected = (dateStr) => {
  selectedDateForFilter.value = dateStr
  selectedDateLabel.value = new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
  
  // 立即加载选中日期的节假日（不管当前在哪个标签页）⭐
  loadHolidaysForSelectedDate(dateStr)
  
  // 如果当前在节假日标签页，需要立即更新显示
  // 注意：数据已经在 loadHolidaysForSelectedDate 中更新，这里只是确保响应式更新
  // 如果当前在节假日标签页，数据会自动通过响应式更新
  // 无需额外日志输出
  
  // 只有登录后才自动切换到日程列表标签
  if (checkLoginStatus()) {
    activeTab.value = 'events'
  }
}

// 加载指定日期的节假日数据
const loadHolidaysForSelectedDate = async (dateStr) => {
  if (!dateStr) {
    await loadTodayHolidays()
    return
  }
  
  // 先清空旧数据，避免显示上一个日期的节日信息
  todayHolidays.value = null
  
  // 提取日期部分（YYYY-MM-DD），去掉时间和时区
  const dateOnly = dateStr.split('T')[0]
  
  const holidays = await getHolidaysForDate(dateOnly)
  todayHolidays.value = holidays
  
  // 强制刷新日历显示
  if (fullCalendarRef.value) {
    setTimeout(() => {
      refreshEventDots()
      fullCalendarRef.value.getApi().render()
    }, 100)
  }
}

const {
  calendarOptions,
  showAddDialog,
  showDetailDialog,
  selectedEvent,
  editingEvent,
  lunarDateText,
  eventsList,
  selectedDate,
  openAddDialog,
  handleDateClick,
  handleEventClick,
  formatEventTime,
  loadEvents,
  saveEvent,
  editEvent,
  deleteEvent,
  testLunar,
  updateCalendarEvents,
  getEventsCountForDate
} = useCalendarEvents({ 
  applyHolidayEvents,
  onDateSelect: handleDateSelected
})

const { activeTab, tabs } = useSidebarTabs('fortune', isLoggedIn)

// 选中的日期（用于过滤日程列表）
const selectedDateForFilter = ref('')
const selectedDateLabel = ref('')

// AI创建日程对话框
const showAIDialog = ref(false)

// 注意：节日数据在 onMounted 中统一加载，避免重复调用

// 过滤后的日程列表（根据选中日期）
const filteredEvents = computed(() => {
  if (!selectedDateForFilter.value) {
    return eventsList.value
  }
  
  return eventsList.value.filter(event => {
    const eventDate = event.start_time.split('T')[0]
    return eventDate === selectedDateForFilter.value
  })
})

// 配置日期点击事件
calendarOptions.value.dateClick = handleDateClick

// 配置事件点击事件
calendarOptions.value.eventClick = handleEventClick

// 周视图日期选择处理
const handleWeekDateSelect = async (dateStr) => {
  selectedDateForFilter.value = dateStr
  selectedDateLabel.value = new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
  
  // 加载选中日期的节假日
  await loadHolidaysForSelectedDate(dateStr)
}

// 处理视图切换
const handleViewSwitch = (viewType) => {
  if (viewType === 'month') {
    currentView.value = 'month'
    if (fullCalendarRef.value) {
      fullCalendarRef.value.getApi().changeView('dayGridMonth')
    }
  } else if (viewType === 'day') {
    currentView.value = 'day'
    if (fullCalendarRef.value) {
      fullCalendarRef.value.getApi().changeView('timeGridDay')
    }
  }
}

// 定义"今天"按钮的处理函数
const handleTodayClick = async () => {
  const todayStr = new Date().toISOString().split('T')[0]
  
  if (currentView.value === 'week') {
    // 周视图：选中今天
    handleWeekDateSelect(todayStr)
  } else if (fullCalendarRef.value) {
    // 月视图/日视图：使用 FullCalendar API
    const calendarApi = fullCalendarRef.value.getApi()
    calendarApi.today()
    calendarApi.unselect()
  }
  
  selectedDateForFilter.value = todayStr  // 设置为今天的日期（显示今天的日程）
  const todayDate = new Date(todayStr)
  selectedDateLabel.value = todayDate.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
  selectedDate.value = todayStr  // 设为今天的日期字符串
  
  // 重新加载今天的节假日
  await loadTodayHolidays()
}

// 配置自定义按钮（今天 + 周视图）
calendarOptions.value.customButtons = {
  myToday: {
    text: '今天',
    click: handleTodayClick
  },
  customWeek: {
    text: '周',
    click: () => {
      currentView.value = 'week'
      // 如果没有选中日期，默认选中今天
      if (!selectedDateForFilter.value) {
        const today = new Date().toISOString().split('T')[0]
        handleWeekDateSelect(today)
      }
    }
  }
}

// 替换工具栏中的按钮
calendarOptions.value.headerToolbar = {
  left: 'prev,next myToday',
  center: 'title',
  right: 'dayGridMonth,customWeek,timeGridDay'
}

// 监听视图变化
calendarOptions.value.viewDidMount = (info) => {
  const viewType = info.view.type
  if (viewType === 'dayGridMonth') {
    currentView.value = 'month'
  } else if (viewType === 'timeGridDay') {
    currentView.value = 'day'
  }
}

// 配置日期单元格渲染（添加圆点指示器和节日文字）
calendarOptions.value.dayCellDidMount = (arg) => {
  // 使用本地日期，避免时区问题
  const year = arg.date.getFullYear()
  const month = String(arg.date.getMonth() + 1).padStart(2, '0')
  const day = String(arg.date.getDate()).padStart(2, '0')
  const dateStr = `${year}-${month}-${day}`
  
  // 确保单元格是相对定位
  arg.el.style.position = 'relative'
  
  // 检查是否有节日，添加节日标签
  const holiday = holidaysMap.value[dateStr]
  if (holiday) {
    // 移除可能存在的旧标签
    const oldLabel = arg.el.querySelector('.holiday-label')
    if (oldLabel) oldLabel.remove()
    
    // 创建节日标签
    const holidayLabel = document.createElement('div')
    holidayLabel.className = 'holiday-label'
    holidayLabel.textContent = `${holiday.emoji || '🎉'} ${holiday.name}`
    holidayLabel.style.cssText = `
      position: absolute;
      bottom: 3px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 10px;
      line-height: 1.2;
      color: #e74c3c;
      font-weight: 700;
      text-shadow: 0 0 3px rgba(255, 255, 255, 1), 1px 1px 0 rgba(255, 255, 255, 1);
      z-index: 100;
      background: rgba(255, 255, 255, 0.85);
      border-radius: 3px;
      padding: 2px 4px;
      white-space: nowrap;
      max-width: 90%;
      overflow: hidden;
      text-overflow: ellipsis;
      pointer-events: none;
      display: block;
      visibility: visible;
    `
    arg.el.appendChild(holidayLabel)
  }
  
  const count = getEventsCountForDate(dateStr)
  
  if (count > 0) {
    // 创建圆点元素
    const dot = document.createElement('div')
    dot.className = 'event-dot'
    
    // 根据事件数量设置颜色深浅（GitHub 热力图风格）
    let bgColor
    if (count === 1) {
      bgColor = 'rgba(102, 126, 234, 0.3)'  // 浅色 - 1 个事件
    } else if (count === 2) {
      bgColor = 'rgba(102, 126, 234, 0.5)'  // 中浅 - 2 个事件
    } else if (count <= 4) {
      bgColor = 'rgba(102, 126, 234, 0.7)'  // 中深 - 3-4 个事件
    } else {
      bgColor = 'rgba(102, 126, 234, 0.9)'  // 深色 - 5+ 个事件
    }
    
    dot.style.cssText = `
      position: absolute;
      bottom: 4px;
      right: 4px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: ${bgColor};
      z-index: 10;
      transition: transform 0.2s ease;
      cursor: pointer;
    `
    
    // 创建 GitHub 风格的 tooltip
    const tooltip = document.createElement('div')
    tooltip.className = 'event-dot-tooltip'
    tooltip.textContent = `${count} 个日程`
    tooltip.style.cssText = `
      position: absolute;
      bottom: 100%;
      right: 0;
      margin-bottom: 8px;
      padding: 6px 10px;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      font-size: 12px;
      border-radius: 4px;
      white-space: nowrap;
      pointer-events: none;
      opacity: 0;
      transform: translateY(4px);
      transition: opacity 0.2s ease, transform 0.2s ease;
      z-index: 1000;
    `
    
    // 添加三角箭头
    const arrow = document.createElement('div')
    arrow.style.cssText = `
      position: absolute;
      top: 100%;
      right: 4px;
      width: 0;
      height: 0;
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-top: 4px solid rgba(0, 0, 0, 0.8);
    `
    tooltip.appendChild(arrow)
    dot.appendChild(tooltip)
    
    // 悬停显示 tooltip（GitHub 风格）
    dot.addEventListener('mouseenter', () => {
      dot.style.transform = 'scale(1.3)'
      tooltip.style.opacity = '1'
      tooltip.style.transform = 'translateY(0)'
    })
    dot.addEventListener('mouseleave', () => {
      dot.style.transform = 'scale(1)'
      tooltip.style.opacity = '0'
      tooltip.style.transform = 'translateY(4px)'
    })
    
    // 添加到日期单元格
    arg.el.style.position = 'relative'
    arg.el.appendChild(dot)
  }
}

const handleEventCardSelect = (event) => {
  // 事件卡片只在登录后才显示，所以这里不需要检查
  handleEventClick({
    event: {
      extendedProps: event,
      start: event.start_time
    }
  })
}

// 为选中的日期添加日程
const openAddDialogForSelectedDate = () => {
  if (!checkLoginStatus()) {
    requireLogin('创建事件')
    return
  }
  if (selectedDate.value) {
    editingEvent.value = {
      start_time: selectedDate.value
    }
  } else {
    editingEvent.value = null
  }
  showAddDialog.value = true
}

// 刷新圆点的函数（提取出来，避免重复代码）
const refreshEventDots = () => {
  setTimeout(() => {
    const dayCells = document.querySelectorAll('.fc-daygrid-day')
    
    dayCells.forEach(cell => {
      // 移除旧圆点
      const oldDot = cell.querySelector('.event-dot')
      if (oldDot) oldDot.remove()
      
      // 移除旧节日标签
      const oldHolidayLabel = cell.querySelector('.holiday-label')
      if (oldHolidayLabel) oldHolidayLabel.remove()
      
      // 获取日期属性
      const dateAttr = cell.getAttribute('data-date')
      if (!dateAttr) {
        // 如果没有 data-date，尝试从其他属性获取
        const fcDate = cell.getAttribute('data-fc-date')
        if (fcDate) {
          // FullCalendar 的日期格式可能是 ISO 字符串，提取日期部分
          const dateStr = fcDate.split('T')[0]
          if (holidaysMap.value[dateStr]) {
            const holiday = holidaysMap.value[dateStr]
            cell.style.position = 'relative'
            const holidayLabel = document.createElement('div')
            holidayLabel.className = 'holiday-label'
            holidayLabel.textContent = `${holiday.emoji || '🎉'} ${holiday.name}`
            holidayLabel.style.cssText = `
              position: absolute;
              top: 1px;
              left: 2px;
              font-size: 8px;
              line-height: 1.1;
              color: #e74c3c;
              font-weight: 700;
              text-shadow: 0 0 3px rgba(255, 255, 255, 1), 1px 1px 0 rgba(255, 255, 255, 0.9);
              z-index: 3;
              background: rgba(255, 255, 255, 0.7);
              border-radius: 2px;
              padding: 1px 2px;
              white-space: nowrap;
              max-width: calc(100% - 4px);
              overflow: hidden;
              text-overflow: ellipsis;
              pointer-events: none;
            `
            cell.appendChild(holidayLabel)
          }
        }
        return
      }
      
      // 标准化日期格式（处理可能的时区信息）
      const dateStr = dateAttr.split('T')[0]
      
      // 重新创建圆点
      const count = getEventsCountForDate(dateAttr)
      if (count > 0) {
        const dot = document.createElement('div')
        dot.className = 'event-dot'
        
        let bgColor
        if (count === 1) bgColor = 'rgba(102, 126, 234, 0.3)'
        else if (count === 2) bgColor = 'rgba(102, 126, 234, 0.5)'
        else if (count <= 4) bgColor = 'rgba(102, 126, 234, 0.7)'
        else bgColor = 'rgba(102, 126, 234, 0.9)'
        
        dot.style.cssText = `
          position: absolute; bottom: 4px; right: 4px;
          width: 8px; height: 8px; border-radius: 50%;
          background: ${bgColor}; z-index: 10;
          transition: transform 0.2s ease; cursor: pointer;
        `
        
        const tooltip = document.createElement('div')
        tooltip.textContent = `${count} 个日程`
        tooltip.style.cssText = `
          position: absolute; bottom: 100%; right: 0; margin-bottom: 8px;
          padding: 6px 10px; background: rgba(0, 0, 0, 0.8); color: white;
          font-size: 12px; border-radius: 4px; white-space: nowrap;
          pointer-events: none; opacity: 0; transform: translateY(4px);
          transition: opacity 0.2s ease, transform 0.2s ease; z-index: 1000;
        `
        dot.appendChild(tooltip)
        
        dot.addEventListener('mouseenter', () => {
          dot.style.transform = 'scale(1.3)'
          tooltip.style.opacity = '1'
          tooltip.style.transform = 'translateY(0)'
        })
        dot.addEventListener('mouseleave', () => {
          dot.style.transform = 'scale(1)'
          tooltip.style.opacity = '0'
          tooltip.style.transform = 'translateY(4px)'
        })
        
        cell.style.position = 'relative'
        cell.appendChild(dot)
      }
      
      // 添加节日标签（使用标准化的日期字符串）
      if (holidaysMap.value[dateStr]) {
        const holiday = holidaysMap.value[dateStr]
        // 确保单元格是相对定位
        cell.style.position = 'relative'
        
        // 创建节日标签
        const holidayLabel = document.createElement('div')
        holidayLabel.className = 'holiday-label'
        holidayLabel.textContent = `${holiday.emoji || '🎉'} ${holiday.name}`
        holidayLabel.style.cssText = `
          position: absolute;
          bottom: 3px;
          left: 50%;
          transform: translateX(-50%);
          font-size: 10px;
          line-height: 1.2;
          color: #e74c3c;
          font-weight: 700;
          text-shadow: 0 0 3px rgba(255, 255, 255, 1), 1px 1px 0 rgba(255, 255, 255, 1);
          z-index: 100;
          background: rgba(255, 255, 255, 0.85);
          border-radius: 3px;
          padding: 2px 4px;
          white-space: nowrap;
          max-width: 90%;
          overflow: hidden;
          text-overflow: ellipsis;
          pointer-events: none;
          display: block;
          visibility: visible;
        `
        cell.appendChild(holidayLabel)
      }
    })
  }, 100)
}

// 监听事件列表变化（只在变化时触发一次，不会频繁刷新）
watch(eventsList, () => {
  updateCalendarEvents()
  refreshEventDots()
})

// 监听节假日数据变化，自动更新日历和节日标签
watch(holidaysMap, () => {
  updateCalendarEvents()
  setTimeout(() => {
    refreshEventDots()  // 刷新时也会更新节日标签
    // 强制刷新日历
    if (fullCalendarRef.value) {
      fullCalendarRef.value.getApi().render()
    }
  }, 150)
}, { deep: true })

// 监听标签页切换，当切换到节假日标签时加载对应日期的数据
watch(activeTab, async (newTab) => {
  if (newTab === 'holiday') {
    // 如果有选中的日期，加载该日期的节假日；否则加载今天的
    if (selectedDateForFilter.value) {
      const dateOnly = selectedDateForFilter.value.split('T')[0]
      // 检查是否已经有对应日期的数据，避免重复加载
      if (!todayHolidays.value || todayHolidays.value.date !== dateOnly) {
        await loadHolidaysForSelectedDate(selectedDateForFilter.value)
      }
    } else {
      // 没有选中日期时，检查是否已经有今天的数据
      const todayStr = new Date().toISOString().split('T')[0]
      if (!todayHolidays.value || todayHolidays.value.date !== todayStr) {
        await loadTodayHolidays()
      }
    }
  }
})

// 监听选中日期变化，如果当前在节假日标签页，需要重新加载数据
// 注意：handleDateSelected 已经会调用 loadHolidaysForSelectedDate，这里只处理非直接点击的情况
watch(
  selectedDateForFilter,
  async (newDate, oldDate) => {
    // 只有当切换到节假日标签页时，且日期确实变化了，才加载
    // 避免与 handleDateSelected 中的调用重复
    if (activeTab.value === 'holiday' && newDate && newDate !== oldDate) {
      // 检查是否已经有对应日期的数据，避免重复加载
      const dateOnly = newDate.split('T')[0]
      if (!todayHolidays.value || todayHolidays.value.date !== dateOnly) {
        await loadHolidaysForSelectedDate(newDate)
      }
    }
  }
)

onMounted(async () => {
  checkLoginStatus()
  await loadHolidays()
  await loadTodayHolidays()
  
  // 节假日加载后更新日历
  updateCalendarEvents()
  
  // 强制刷新日历显示节日标签
  setTimeout(() => {
    refreshEventDots()
    if (fullCalendarRef.value) {
      fullCalendarRef.value.getApi().render()
    }
  }, 300)
  
  // 只有登录后才加载用户事件
  if (isLoggedIn.value) {
    await loadEvents()
  }
})

// 处理AI创建的日程
const handleAICreate = async (eventData) => {
  if (!checkLoginStatus()) {
    return
  }
  
  // 构建完整的日程数据
  const newEvent = {
    title: eventData.title,
    start_time: eventData.time 
      ? `${eventData.date}T${eventData.time}:00` 
      : `${eventData.date}T09:00:00`,  // 默认早上9点
    end_time: eventData.time 
      ? `${eventData.date}T${eventData.time}:00` 
      : `${eventData.date}T10:00:00`,  // 默认1小时
    description: eventData.description || '',
    location: '',
    all_day: !eventData.time,  // 没有时间就是全天事件
    reminder_minutes: eventData.reminder_minutes || 15
  }
  
  // 调用保存方法
  await saveEvent(newEvent)
}
</script>

<style>
/* 导入日历样式（已优化，移除大量 !important） */
@import '@/styles/calendar.css';
</style>

<style scoped>
/* ==================== 组件特有样式 ==================== */

/* 日历页面容器 */
.calendar-page {
  min-height: 100vh;
  background: var(--color-background-soft);
}

/* 桌面端日历完全自适应容器大小 - 仅桌面端应用 */
@media (min-width: 768px) {
  .calendar-wrapper :deep(.fc) {
    height: 100%;
    width: 100%;
  }

  /* 月视图 - 自适应，不固定高度 */
  .calendar-wrapper :deep(.fc-dayGridMonth-view) {
    height: 100%;
  }

  /* 日历内容自适应缩放 */
  .calendar-wrapper :deep(.fc-view-harness) {
    height: 100% !important;
  }

  /* 周/日时间轴视图 - 自适应高度 */
  .calendar-wrapper :deep(.fc-timeGridWeek-view),
  .calendar-wrapper :deep(.fc-timeGridDay-view) {
    height: 100%;
    max-height: none;
  }

  /* 时间轴滚动区域 */
  .calendar-wrapper :deep(.fc-timegrid-body) {
    max-height: 500px;
    overflow-y: auto;
  }
}

/* PC端容器 */
.row {
  max-width: 1400px;
  margin: 0 auto;
}

/* 确保两列完全等宽等高 */
.row > div {
  display: flex;
}

/* 桌面端：左侧日历占 60%，右侧 40% */
@media (min-width: 768px) {
  .row > div:first-child {
    flex: 0 0 60%;
    max-width: 60%;
  }

  .row > div:last-child {
    flex: 0 0 40%;
    max-width: 40%;
  }
}

/* 移动端：上下布局，日历和侧边栏都全宽 */
@media (max-width: 767px) {
  .row {
    margin-left: 0;
    margin-right: 0;
  }
  
  .row > div {
    flex: 0 0 100%;
    max-width: 100%;
    padding-left: 4px;
    padding-right: 4px;
  }
  
  /* 日历高度大幅增加，确保所有日期完整显示 */
  .calendar-page .calendar-wrapper {
    height: auto;
    max-height: none;
    min-height: 600px;
    margin: 0 0 16px 0;
    width: 100%;
    padding: 20px;
  }
  
  /* 日期单元格 - 显著增大以完整显示内容 */
  .calendar-page :deep(.fc-daygrid-day) {
    min-height: 65px;
  }
  
  .calendar-page :deep(.fc-daygrid-day-frame) {
    min-height: 65px;
    overflow: visible;
  }
  
  /* 周标题 */
  .calendar-page :deep(.fc-col-header-cell) {
    padding: 8px 2px;
    font-size: 14px;
    font-weight: 600;
  }
  
  /* 工具栏 */
  .calendar-page :deep(.fc-header-toolbar) {
    margin-bottom: 10px;
  }
  
  .calendar-page :deep(.fc-toolbar-title) {
    font-size: 18px;
    font-weight: 700;
  }
  
  .calendar-page :deep(.fc-button) {
    padding: 6px 10px;
    font-size: 14px;
  }
  
  /* 日期数字 - 显著增大字体 */
  .calendar-page :deep(.fc-daygrid-day-number) {
    padding: 8px;
    font-size: 17px;
    font-weight: 700;
  }
}

/* 桌面端日历容器 - 必须放在移动端media query之后 */
@media (min-width: 768px) {
  .calendar-page .calendar-wrapper {
    height: 650px;
    max-height: 650px;
    min-height: 650px;
    /* 确保内容包裹在容器内 */
    overflow: hidden;
    position: relative;
  }
}

.calendar-page .calendar-wrapper {
  width: 100%;
  max-width: 100%;
  /* 确保内容不会溢出 */
  overflow: hidden;
  position: relative;
  box-sizing: border-box;
}

.right-sidebar {
  flex: 1;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

/* 浮动添加按钮 */
.floating-add-btn {
  position: fixed;
  left: 24px;
  bottom: 24px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  font-size: 26px;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-add-btn:hover {
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

.floating-add-btn:active {
  transform: scale(0.95);
}

/* AI创建按钮 */
.floating-ai-btn {
  position: fixed;
  left: 24px;
  bottom: 100px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
  border: none;
  font-size: 22px;
  box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-ai-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(245, 87, 108, 0.5);
}

.floating-ai-btn:active {
  transform: scale(0.95);
}

/* 未登录引导按钮 */
.floating-login-btn {
  position: fixed;
  left: 24px;
  bottom: 24px;
  height: 60px;
  padding: 0 24px;
  border-radius: 30px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.floating-login-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

.floating-login-btn:active {
  transform: translateY(-2px);
}

.floating-login-btn i {
  font-size: 18px;
}

.login-text {
  white-space: nowrap;
}

/* ==================== 移动端适配 ==================== */
@media (max-width: 768px) {
  /* 确保移动端日历居中 */
  .calendar-wrapper {
    max-width: 100%;
    margin-left: auto;
    margin-right: auto;
  }
  
  .floating-add-btn {
    left: 16px;
    bottom: 16px;
    width: 50px;
    height: 50px;
    font-size: 22px;
  }
  
  .floating-ai-btn {
    left: 16px;
    bottom: 84px;
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .floating-login-btn {
    left: 16px;
    bottom: 16px;
    height: 50px;
    padding: 0 20px;
    font-size: 15px;
  }
  
  .floating-login-btn i {
    font-size: 16px;
  }
}

/* ==================== PC 端完美对称布局 ==================== */
@media (min-width: 992px) {
  .row {
    display: flex;
    align-items: stretch;
  }
  
  .row > div {
    flex: 1 1 0;  /* 完全等宽 */
    max-width: 50%;
  }
  
  .calendar-wrapper,
  .right-sidebar {
    min-height: 650px;
    height: 100%;
  }
}
</style>

