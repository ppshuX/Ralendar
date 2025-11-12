import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
    baseURL: 'https://app7626.acapp.acwing.com.cn/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 是否正在刷新token
let isRefreshing = false
// 刷新token期间的请求队列
let requestQueue = []

// 请求拦截器 - 自动添加Token（公开API除外）
api.interceptors.request.use(
    config => {
        // 如果明确标记为跳过认证，则不添加Token
        if (config.skipAuth) {
            delete config.skipAuth  // 删除自定义属性，避免传递给服务器
            return config
        }
        
        // 从localStorage获取token
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 响应拦截器 - 自动刷新Token
api.interceptors.response.use(
    response => {
        return response.data
    },
    async error => {
        const originalRequest = error.config
        
        // 如果是401错误且不是登录请求，尝试刷新token
        if (error.response?.status === 401 && !originalRequest._retry) {
            if (originalRequest.url.includes('/auth/login')) {
                return Promise.reject(error)
            }
            
            // 标记请求已重试过
            originalRequest._retry = true
            
            if (!isRefreshing) {
                isRefreshing = true
                const refreshToken = localStorage.getItem('refresh_token')
                
                if (!refreshToken) {
                    // 没有refresh token，跳转到登录页
                    localStorage.clear()
                    window.location.href = '/login'
                    return Promise.reject(error)
                }
                
                try {
                    // 刷新token
                    const { data } = await axios.post(
                        'https://app7626.acapp.acwing.com.cn/api/auth/refresh/',
                        { refresh: refreshToken }
                    )
                    
                    // 保存新token
                    localStorage.setItem('access_token', data.access)
                    if (data.refresh) {
                        localStorage.setItem('refresh_token', data.refresh)
                    }
                    
                    // 更新原请求的token
                    originalRequest.headers.Authorization = `Bearer ${data.access}`
                    
                    // 重试队列中的所有请求
                    requestQueue.forEach(cb => cb(data.access))
                    requestQueue = []
                    
                    isRefreshing = false
                    
                    // 重试原请求
                    return api(originalRequest)
                } catch (refreshError) {
                    // 刷新失败，清除token并跳转登录
                    localStorage.clear()
                    window.location.href = '/login'
                    isRefreshing = false
                    return Promise.reject(refreshError)
                }
            }
            
            // 如果正在刷新token，将请求加入队列
            return new Promise(resolve => {
                requestQueue.push((token) => {
                    originalRequest.headers.Authorization = `Bearer ${token}`
                    resolve(api(originalRequest))
                })
            })
        }
        
        return Promise.reject(error)
    }
)

// 日程 API
export const eventAPI = {
    // 获取所有日程
    async getAll() {
        const response = await api.get('/events/')
        // Django REST Framework 分页格式：{ count, next, previous, results }
        // 返回 results 数组
        return response.results || response || []
    },

    // 创建日程
    create(data) {
        return api.post('/events/', data)
    },

    // 更新日程
    update(id, data) {
        return api.put(`/events/${id}/`, data)
    },

    // 删除日程
    delete(id) {
        return api.delete(`/events/${id}/`)
    }
}

// 农历 API（公开接口，不需要Token）
export const lunarAPI = {
    // 获取农历日期
    getLunarDate(date) {
        return api.get('/lunar/', { 
            params: { date },
            skipAuth: true  // 标记为跳过认证
        })
    }
}

// 节假日 API（公开接口，不需要Token）
export const holidayAPI = {
    // 获取指定年份的节假日列表
    getHolidays(year) {
        return api.get('/holidays/', { 
            params: { year },
            skipAuth: true  // 标记为跳过认证
        })
    },
    
    // 检查指定日期是否是节假日
    checkHoliday(date) {
        return api.get('/holidays/check/', { 
            params: { date },
            skipAuth: true  // 标记为跳过认证
        })
    },
    
    // 获取今日节假日和节日信息
    getTodayHolidays() {
        return api.get('/holidays/today/', {
            skipAuth: true  // 标记为跳过认证
        })
    }
}

// 公开日历 API
export const calendarAPI = {
    // 获取公开日历列表
    getAll() {
        return api.get('/calendars/')
    },

    // 获取日历订阅
    getFeed(slug) {
        return api.get(`/calendars/${slug}/feed/`)
    }
}

// 天气 API（公开接口，不需要Token）
export const weatherAPI = {
    // 获取指定城市的天气
    getWeather(city) {
        return api.get('/weather/', { 
            params: { location: city },
            skipAuth: true  // 标记为跳过认证
        })
    }
}

// 用户认证 API
export const authAPI = {
    // 用户注册
    register(data) {
        return api.post('/auth/register/', data)
    },

    // 用户登录
    login(data) {
        return api.post('/auth/login/', data)
    },

    // 刷新token
    refresh(refreshToken) {
        return api.post('/auth/refresh/', { refresh: refreshToken })
    },

    // 获取当前用户信息
    getCurrentUser() {
        return api.get('/auth/me/')
    }
}

export default api

