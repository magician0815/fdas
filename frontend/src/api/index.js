/**
 * Axios请求配置模块.
 *
 * 配置请求拦截器、响应拦截器、错误处理等.
 */

import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '',
  timeout: 10000,
  withCredentials: true, // Session认证需要携带Cookie
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可添加请求日志等
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
      // 重定向到登录页
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api