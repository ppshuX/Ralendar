import { ref } from 'vue'
import { holidayAPI } from '../api'

export function useHolidayData() {
  const holidaysMap = ref({})
  const todayHolidays = ref(null)

  const loadHolidays = async (year) => {
    try {
      const data = await holidayAPI.getHolidays(year || new Date().getFullYear())
      const holidays = data.results || data || []
      holidays.forEach(holiday => {
        if (holiday.date) {
          holidaysMap.value[holiday.date] = holiday
        }
      })
    } catch (error) {
      console.error('加载节假日数据失败:', error)
    }
  }

  const loadTodayHolidays = async () => {
    try {
      const data = await holidayAPI.getTodayHolidays()
      todayHolidays.value = data.results || data || null
    } catch (error) {
      console.error('加载今日节假日失败:', error)
      todayHolidays.value = null
    }
  }

  const getHolidaysForDate = async (dateStr) => {
    const dateOnly = dateStr.split('T')[0]

    // 优先从本地缓存获取
    if (holidaysMap.value[dateOnly]) {
      return holidaysMap.value[dateOnly]
    }

    // 从 API 获取
    try {
      const data = await holidayAPI.checkHoliday(dateOnly)
      if (data && data.is_holiday) {
        holidaysMap.value[dateOnly] = data
        return data
      }
    } catch (error) {
      console.error('获取节假日信息失败:', error)
    }

    return null
  }

  const applyHolidayEvents = (events) => {
    const holidayEvents = []
    Object.values(holidaysMap.value).forEach(holiday => {
      const isWeekend = new Date(holiday.date).getDay() === 0 || new Date(holiday.date).getDay() === 6
      if (!isWeekend) {
        holidayEvents.push({
          title: holiday.name,
          start: holiday.date,
          allDay: true,
          display: 'background',
          classNames: ['holiday-event']
        })
      }
    })
    return [...events, ...holidayEvents]
  }

  return {
    holidaysMap,
    todayHolidays,
    loadHolidays,
    loadTodayHolidays,
    getHolidaysForDate,
    applyHolidayEvents
  }
}
