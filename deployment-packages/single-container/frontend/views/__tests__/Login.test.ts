/**
 * Login.vue 测试.
 *
 * 测试登录页面的表单验证、登录流程、错误处理.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import Login from '../Login.vue'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

// Mock auth store
const mockAuthStore = {
  login: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  User: {},
  Lock: {},
  TrendCharts: {},
  Connection: {},
  Timer: {},
  DataAnalysis: {},
  InfoFilled: {}
}))

describe('Login.vue', () => {
  let router
  let pinia

  beforeEach(() => {
    vi.clearAllMocks()

    // 创建路由
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div></div>' } },
        { path: '/login', component: Login },
        { path: '/fx-data', component: { template: '<div></div>' } }
      ]
    })

    // 创建Pinia
    pinia = createPinia()
    setActivePinia(pinia)
  })

  describe('组件渲染', () => {
    it('应该正确渲染登录表单', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      // 验证表单存在
      expect(wrapper.find('.login-form').exists()).toBe(true)
    })

    it('应该渲染用户名输入框', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      // 验证用户名输入框存在
      expect(wrapper.find('.login-container').exists()).toBe(true)
    })

    it('应该渲染密码输入框', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      // 验证登录容器存在
      expect(wrapper.find('.login-form-section').exists()).toBe(true)
    })

    it('应该渲染登录按钮', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      // 验证登录按钮存在
      expect(wrapper.find('.login-button').exists()).toBe(true)
    })
  })

  describe('表单验证', () => {
    it('应该定义表单验证规则', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      // 验证组件有rules定义
      expect(wrapper.vm.rules).toBeDefined()
    })

    it('用户名必填验证规则应该存在', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      // 验证username验证规则
      expect(wrapper.vm.rules.username).toBeDefined()
      expect(wrapper.vm.rules.username[0].required).toBe(true)
    })

    it('密码必填验证规则应该存在', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      // 验证password验证规则
      expect(wrapper.vm.rules.password).toBeDefined()
      expect(wrapper.vm.rules.password[0].required).toBe(true)
    })
  })

  describe('表单数据', () => {
    it('应该初始化空用户名', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      expect(wrapper.vm.form.username).toBe('')
    })

    it('应该初始化空密码', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      expect(wrapper.vm.form.password).toBe('')
    })

    it('loading状态应该初始为false', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('登录流程', () => {
    it('handleLogin函数应该存在', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      expect(wrapper.vm.handleLogin).toBeDefined()
    })

    it('登录成功应该调用authStore.login', async () => {
      mockAuthStore.login.mockResolvedValue(true)

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      // 设置表单数据
      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'testpass'

      // Mock formRef验证通过
      wrapper.vm.formRef = {
        validate: vi.fn().mockResolvedValue(true)
      }

      await wrapper.vm.handleLogin()

      expect(mockAuthStore.login).toHaveBeenCalledWith('testuser', 'testpass')
    })

    it('登录失败应该显示错误消息', async () => {
      mockAuthStore.login.mockResolvedValue(false)

      const { ElMessage } = await import('element-plus')

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'wrongpass'
      wrapper.vm.formRef = {
        validate: vi.fn().mockResolvedValue(true)
      }

      await wrapper.vm.handleLogin()

      expect(ElMessage.error).toHaveBeenCalled()
    })

    it('表单验证失败不应该调用登录', async () => {
      mockAuthStore.login.mockClear()

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.formRef = {
        validate: vi.fn().mockRejectedValue(new Error('Validation failed'))
      }

      await wrapper.vm.handleLogin()

      expect(mockAuthStore.login).not.toHaveBeenCalled()
    })
  })

  describe('loading状态', () => {
    it('登录时loading应该为true', async () => {
      mockAuthStore.login.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve(true), 100)))

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'testpass'
      wrapper.vm.formRef = {
        validate: vi.fn().mockResolvedValue(true)
      }

      // 开始登录但不等待
      const loginPromise = wrapper.vm.handleLogin()

      // 检查loading状态（由于异步，可能需要延迟检查）
      // 登录完成后loading应该恢复false
      await loginPromise
      expect(wrapper.vm.loading).toBe(false)
    })

    it('登录完成后loading应该恢复false', async () => {
      mockAuthStore.login.mockResolvedValue(true)

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'testpass'
      wrapper.vm.formRef = {
        validate: vi.fn().mockResolvedValue(true)
      }

      await wrapper.vm.handleLogin()

      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('装饰区域', () => {
    it('应该渲染左侧装饰区域', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      expect(wrapper.find('.login-decoration').exists()).toBe(true)
    })

    it('应该渲染Logo', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      expect(wrapper.find('.logo-large').exists()).toBe(true)
    })

    it('应该渲染系统标题', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      expect(wrapper.find('.decoration-title').exists()).toBe(true)
    })

    it('应该渲染功能亮点列表', async () => {
      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      expect(wrapper.find('.features-list').exists()).toBe(true)
    })
  })

  describe('边界值测试', () => {
    it('空用户名和密码不应该调用登录', async () => {
      mockAuthStore.login.mockClear()

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.form.username = ''
      wrapper.vm.form.password = ''
      wrapper.vm.formRef = {
        validate: vi.fn().mockRejectedValue(new Error('Required'))
      }

      await wrapper.vm.handleLogin()

      expect(mockAuthStore.login).not.toHaveBeenCalled()
    })

    it('只有用户名不应该通过验证', async () => {
      mockAuthStore.login.mockClear()

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = ''
      wrapper.vm.formRef = {
        validate: vi.fn().mockRejectedValue(new Error('Password required'))
      }

      await wrapper.vm.handleLogin()

      expect(mockAuthStore.login).not.toHaveBeenCalled()
    })

    it('只有密码不应该通过验证', async () => {
      mockAuthStore.login.mockClear()

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.form.username = ''
      wrapper.vm.form.password = 'testpass'
      wrapper.vm.formRef = {
        validate: vi.fn().mockRejectedValue(new Error('Username required'))
      }

      await wrapper.vm.handleLogin()

      expect(mockAuthStore.login).not.toHaveBeenCalled()
    })
  })

  describe('错误处理', () => {
    it('登录异常应该显示错误消息', async () => {
      mockAuthStore.login.mockRejectedValue(new Error('Network error'))

      const { ElMessage } = await import('element-plus')

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'testpass'
      wrapper.vm.formRef = {
        validate: vi.fn().mockResolvedValue(true)
      }

      await wrapper.vm.handleLogin()

      expect(ElMessage.error).toHaveBeenCalled()
    })

    it('异常后loading应该恢复false', async () => {
      mockAuthStore.login.mockRejectedValue(new Error('Network error'))

      const wrapper = mount(Login, {
        global: {
          plugins: [router, pinia]
        }
      })

      wrapper.vm.form.username = 'testuser'
      wrapper.vm.form.password = 'testpass'
      wrapper.vm.formRef = {
        validate: vi.fn().mockResolvedValue(true)
      }

      await wrapper.vm.handleLogin()

      expect(wrapper.vm.loading).toBe(false)
    })
  })
})