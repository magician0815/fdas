/**
 * 用户认证状态管理.
 *
 * 使用Pinia管理用户登录状态、角色信息等.
 * 使用sessionStorage存储session_id，浏览器关闭后自动清除，降低安全风险.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-16 - 改用sessionStorage存储session_id，改用logger服务
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/api/index'
import logger from '@/services/logger'

export const useAuthStore = defineStore('auth', () => {
  // 用户信息
  const user = ref(null)

  // 登录错误消息
  const loginError = ref(null)

  // 是否已登录
  const isLoggedIn = computed(() => user.value !== null)

  // 是否是admin
  const isAdmin = computed(() => user.value?.role === 'admin')

  /**
   * 用户登录.
   *
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise<{success: boolean, message?: string}>} - 登录结果
   */
  async function login(username, password) {
    loginError.value = null
    try {
      const response = await axios.post('/api/v1/auth/login', {
        username,
        password
      })
      // 注意：axios拦截器已返回response.data，所以response直接是API响应体
      // API响应格式：{success, data: {user, session_id}, message, error}
      user.value = response.data.user
      // 存储session_id到sessionStorage（浏览器关闭后自动清除）
      if (response.data.session_id) {
        sessionStorage.setItem('session_id', response.data.session_id)
      }
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || error.response?.data?.message || '登录失败'
      loginError.value = message
      logger.error('登录失败', error)
      return { success: false, message }
    }
  }

  /**
   * 用户登出.
   *
   * @returns {Promise<{success: boolean}>}
   */
  async function logout() {
    try {
      const sessionId = sessionStorage.getItem('session_id')
      if (sessionId) {
        await axios.post('/api/v1/auth/logout', null, {
          headers: { 'X-Session-ID': sessionId }
        })
        sessionStorage.removeItem('session_id')
      }
    } catch (error) {
      logger.error('登出失败', error)
    }
    user.value = null
    return { success: true }
  }

  /**
   * 获取当前用户信息.
   *
   * @returns {Promise<void>}
   */
  async function fetchUser() {
    try {
      const response = await axios.get('/api/v1/auth/me')
      // axios拦截器已返回response.data
      user.value = response.data.user
    } catch (error) {
      user.value = null
      sessionStorage.removeItem('session_id')
    }
  }

  return {
    user,
    loginError,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    fetchUser
  }
})