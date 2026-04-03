/**
 * 用户认证状态管理.
 *
 * 使用Pinia管理用户登录状态、角色信息等.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/api/index'

export const useAuthStore = defineStore('auth', () => {
  // 用户信息
  const user = ref(null)

  // 是否已登录
  const isLoggedIn = computed(() => user.value !== null)

  // 是否是admin
  const isAdmin = computed(() => user.value?.role === 'admin')

  /**
   * 用户登录.
   *
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise<boolean>} - 登录是否成功
   */
  async function login(username, password) {
    try {
      const response = await axios.post('/api/v1/auth/login', {
        username,
        password
      })
      user.value = response.data.user
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  /**
   * 用户登出.
   *
   * @returns {Promise<void>}
   */
  async function logout() {
    try {
      await axios.post('/api/v1/auth/logout')
    } catch (error) {
      console.error('登出失败:', error)
    }
    user.value = null
  }

  /**
   * 获取当前用户信息.
   *
   * @returns {Promise<void>}
   */
  async function fetchUser() {
    try {
      const response = await axios.get('/api/v1/auth/me')
      user.value = response.data.user
    } catch (error) {
      user.value = null
    }
  }

  return {
    user,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    fetchUser
  }
})