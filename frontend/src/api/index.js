/**
 * Axios请求配置模块.
 *
 * 配置请求拦截器、响应拦截器、错误处理等.
 * 使用sessionStorage存储session_id，浏览器关闭后自动清除.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-16 - 添加Session ID header拦截器，改用sessionStorage
 */

import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '',
  timeout: 10000,
  withCredentials: true, // Session认证需要携带Cookie
})

// 请求拦截器：自动添加Session ID header
api.interceptors.request.use(
  (config) => {
    // 从sessionStorage获取session_id并添加到header
    const sessionId = sessionStorage.getItem('session_id')
    if (sessionId) {
      config.headers['X-Session-ID'] = sessionId
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 处理401未授权错误
    if (error.response?.status === 401) {
      // 清除sessionStorage
      sessionStorage.removeItem('session_id')
      // 重定向到登录页
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api