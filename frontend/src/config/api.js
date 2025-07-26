/**
 * API 配置文件
 * 统一管理不同环境下的API地址
 */

// 获取API基础URL
const getApiBaseUrl = () => {
  // Vercel部署时使用环境变量
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // 开发环境
  if (import.meta.env.DEV) {
    return 'http://localhost:8000'
  }
  
  // 生产环境默认使用相对路径（通过nginx代理）
  return '/api'
}

export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: 10000,
  
  // 不同环境的特殊配置
  HEADERS: {
    'Content-Type': 'application/json',
  }
}

// 导出用于其他模块的常量
export const API_BASE_URL = API_CONFIG.BASE_URL

console.log('API Base URL:', API_BASE_URL, 'Environment:', import.meta.env.MODE) 