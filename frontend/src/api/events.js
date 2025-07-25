import { API_CONFIG } from '@/config/api'
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 自动添加认证头
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url)
    return response.data
  },
  (error) => {
    console.error('响应错误:', error)
    
    // 处理认证错误
    if (error.response?.status === 401) {
      // Token过期，清除本地存储并跳转到登录页
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      
      // 如果不在登录页，则跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    const message = error.response?.data?.detail || error.message || '网络错误'
    throw new Error(message)
  }
)

// 事件API
export const eventAPI = {
  // 创建事件
  async createEvent(eventData) {
    return await api.post('/api/events/', eventData)
  },

  // 获取时间线
  async getTimeline(params = {}) {
    const { page = 1, size = 20, category } = params
    const query = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
      ...(category && { category })
    })
    return await api.get(`/api/events/timeline?${query}`)
  },

  // 搜索事件
  async searchEvents(params = {}) {
    const { query, tags, category, start_date, end_date } = params
    const searchParams = new URLSearchParams()
    
    if (query) searchParams.append('query', query)
    if (tags) searchParams.append('tags', Array.isArray(tags) ? tags.join(',') : tags)
    if (category) searchParams.append('category', category)
    if (start_date) searchParams.append('start_date', start_date)
    if (end_date) searchParams.append('end_date', end_date)
    
    return await api.get(`/api/events/search?${searchParams}`)
  },

  // 获取事件详情
  async getEvent(eventId) {
    return await api.get(`/api/events/${eventId}`)
  },

  // 更新事件
  async updateEvent(eventId, eventData) {
    return await api.put(`/api/events/${eventId}`, eventData)
  },

  // 删除事件
  async deleteEvent(eventId) {
    return await api.delete(`/api/events/${eventId}`)
  },

  // 获取分类统计
  async getCategoriesStats() {
    return await api.get('/api/events/stats/categories')
  },

  // 获取时间线统计
  async getTimelineStats() {
    return await api.get('/api/events/stats/timeline')
  },

  // 微信公众号内容提取
  async extractWechatContent(url) {
    return await api.post('/api/events/extract-wechat', { url })
  }
}

export default api 