/**
 * Auth Store 测试.
 *
 * 测试Pinia认证状态管理的核心逻辑.
 * 使用sessionStorage存储session_id.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'

// Mock axios
vi.mock('@/api/index', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
vi.stubGlobal('sessionStorage', sessionStorageMock)

import axios from '@/api/index'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('初始user应为null', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
    })

    it('初始isLoggedIn应为false', () => {
      const store = useAuthStore()
      expect(store.isLoggedIn).toBe(false)
    })

    it('初始isAdmin应为false', () => {
      const store = useAuthStore()
      expect(store.isAdmin).toBe(false)
    })
  })

  describe('login函数', () => {
    it('登录成功应返回success:true并设置user', async () => {
      const mockUser = { id: '1', username: 'admin', role: 'admin' }
      axios.post.mockResolvedValue({ data: { data: { user: mockUser, session_id: 'test-session' } } })

      const store = useAuthStore()
      const result = await store.login('admin', 'password')

      expect(result.success).toBe(true)
      expect(store.user).toEqual(mockUser)
      expect(axios.post).toHaveBeenCalledWith('/api/v1/auth/login', {
        username: 'admin',
        password: 'password'
      })
    })

    it('登录失败应返回success:false且user为null', async () => {
      axios.post.mockRejectedValue({ response: { data: { message: '登录失败' } } })

      const store = useAuthStore()
      const result = await store.login('wrong', 'wrong')

      expect(result.success).toBe(false)
      expect(store.user).toBeNull()
    })

    it('登录成功后isLoggedIn应为true', async () => {
      const mockUser = { id: '1', username: 'user', role: 'user' }
      axios.post.mockResolvedValue({ data: { data: { user: mockUser, session_id: 'test-session' } } })

      const store = useAuthStore()
      await store.login('user', 'password')

      expect(store.isLoggedIn).toBe(true)
    })

    it('登录成功后isAdmin应根据role判断', async () => {
      // admin角色
      axios.post.mockResolvedValue({ data: { data: { user: { role: 'admin' }, session_id: 'test-session' } } })
      const adminStore = useAuthStore()
      await adminStore.login('admin', 'password')
      expect(adminStore.isAdmin).toBe(true)

      // 重置
      setActivePinia(createPinia())

      // user角色
      axios.post.mockResolvedValue({ data: { data: { user: { role: 'user' }, session_id: 'test-session' } } })
      const userStore = useAuthStore()
      await userStore.login('user', 'password')
      expect(userStore.isAdmin).toBe(false)
    })

    it('登录失败后isLoggedIn应为false', async () => {
      axios.post.mockRejectedValue({ response: { data: { message: '登录失败' } } })

      const store = useAuthStore()
      await store.login('wrong', 'wrong')

      expect(store.isLoggedIn).toBe(false)
    })

    it('网络错误时应返回success:false', async () => {
      axios.post.mockRejectedValue({ response: { data: { message: 'Network Error' } } })

      const store = useAuthStore()
      const result = await store.login('admin', 'password')

      expect(result.success).toBe(false)
    })
  })

  describe('logout函数', () => {
    it('登出应清除user', async () => {
      sessionStorageMock.getItem.mockReturnValue('test-session')
      const store = useAuthStore()
      store.user = { id: '1', username: 'admin' }

      axios.post.mockResolvedValue({ data: { success: true } })
      await store.logout()

      expect(store.user).toBeNull()
    })

    it('登出应调用API带session header', async () => {
      sessionStorageMock.getItem.mockReturnValue('test-session')
      axios.post.mockResolvedValue({ data: { success: true } })

      const store = useAuthStore()
      await store.logout()

      expect(axios.post).toHaveBeenCalled()
    })

    it('登出失败也应清除user', async () => {
      sessionStorageMock.getItem.mockReturnValue('test-session')
      axios.post.mockRejectedValue({ response: { data: { message: '登出失败' } } })

      const store = useAuthStore()
      store.user = { id: '1', username: 'admin' }
      await store.logout()

      expect(store.user).toBeNull()
    })

    it('登出后isLoggedIn应为false', async () => {
      sessionStorageMock.getItem.mockReturnValue('test-session')
      const store = useAuthStore()
      store.user = { id: '1', username: 'admin' }

      axios.post.mockResolvedValue({ data: { success: true } })
      await store.logout()

      expect(store.isLoggedIn).toBe(false)
    })
  })

  describe('fetchUser函数', () => {
    it('获取用户成功应设置user', async () => {
      const mockUser = { id: '1', username: 'admin', role: 'admin' }
      axios.get.mockResolvedValue({ data: { data: { user: mockUser } } })

      const store = useAuthStore()
      await store.fetchUser()

      expect(store.user).toEqual(mockUser)
      expect(axios.get).toHaveBeenCalledWith('/api/v1/auth/me')
    })

    it('获取用户失败应清除user', async () => {
      axios.get.mockRejectedValue(new Error('未登录'))

      const store = useAuthStore()
      store.user = { id: '1', username: 'admin' }
      await store.fetchUser()

      expect(store.user).toBeNull()
    })

    it('未登录时fetchUser应返回null', async () => {
      axios.get.mockRejectedValue(new Error('Unauthorized'))

      const store = useAuthStore()
      await store.fetchUser()

      expect(store.user).toBeNull()
    })
  })

  describe('computed属性', () => {
    it('user为null时isLoggedIn应为false', () => {
      const store = useAuthStore()
      store.user = null
      expect(store.isLoggedIn).toBe(false)
    })

    it('user有值时isLoggedIn应为true', () => {
      const store = useAuthStore()
      store.user = { id: '1', username: 'test' }
      expect(store.isLoggedIn).toBe(true)
    })

    it('role为admin时isAdmin应为true', () => {
      const store = useAuthStore()
      store.user = { role: 'admin' }
      expect(store.isAdmin).toBe(true)
    })

    it('role不为admin时isAdmin应为false', () => {
      const store = useAuthStore()
      store.user = { role: 'user' }
      expect(store.isAdmin).toBe(false)
    })

    it('user为null时isAdmin应为false', () => {
      const store = useAuthStore()
      store.user = null
      expect(store.isAdmin).toBe(false)
    })

    it('user无role属性时isAdmin应为false', () => {
      const store = useAuthStore()
      store.user = { id: '1', username: 'test' }
      expect(store.isAdmin).toBe(false)
    })
  })

  describe('状态变化', () => {
    it('登录后再登出应清除所有状态', async () => {
      axios.post.mockResolvedValue({ data: { data: { user: { id: '1', role: 'admin' }, session_id: 'test-session' } } })

      const store = useAuthStore()
      await store.login('admin', 'password')

      expect(store.user).toBeTruthy()
      expect(store.isLoggedIn).toBe(true)
      expect(store.isAdmin).toBe(true)

      axios.post.mockResolvedValue({})
      await store.logout()

      expect(store.user).toBeNull()
      expect(store.isLoggedIn).toBe(false)
      expect(store.isAdmin).toBe(false)
    })

    it('连续登录应更新user', async () => {
      axios.post.mockResolvedValue({ data: { data: { user: { id: '1', username: 'user1' }, session_id: 'test-session' } } })

      const store = useAuthStore()
      await store.login('user1', 'password')
      expect(store.user.username).toBe('user1')

      axios.post.mockResolvedValue({ data: { data: { user: { id: '2', username: 'user2' }, session_id: 'test-session' } } })
      await store.login('user2', 'password')
      expect(store.user.username).toBe('user2')
    })
  })
})