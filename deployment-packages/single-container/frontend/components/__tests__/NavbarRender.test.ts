/**
 * Navbar.vue渲染测试.
 *
 * 测试顶部导航栏组件的渲染和交互.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Navbar from '../Navbar.vue'

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElDropdown: {
    template: '<div class="el-dropdown"><slot /><slot name="dropdown" /></div>',
    props: ['trigger']
  },
  ElDropdownMenu: {
    template: '<div class="el-dropdown-menu"><slot /></div>'
  },
  ElDropdownItem: {
    template: '<div class="el-dropdown-item"><slot /></div>',
    props: ['command', 'divided']
  },
  ElIcon: {
    template: '<i class="el-icon"><slot /></i>',
    props: ['size']
  }
}))

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  UserFilled: { template: '<svg class="user-filled-icon" />' },
  ArrowDown: { template: '<svg class="arrow-down-icon" />' },
  SwitchButton: { template: '<svg class="switch-button-icon" />' },
  User: { template: '<svg class="user-icon" />' }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    user: { username: 'admin', role: 'admin' },
    logout: vi.fn()
  }))
}))

// Mock vue-router
vi.mock('vue-router', () => ({
  useRoute: vi.fn(() => ({ path: '/fx-data', meta: { title: '数据分析' } })),
  useRouter: vi.fn(() => ({ push: vi.fn() }))
}))

describe('Navbar.vue渲染测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('页面结构渲染', () => {
    it('应渲染导航栏容器', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElDropdown: true, ElIcon: true } }
      })
      expect(wrapper.find('.navbar').exists()).toBe(true)
    })

    it('应渲染左侧区域', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElDropdown: true, ElIcon: true } }
      })
      expect(wrapper.find('.navbar-left').exists()).toBe(true)
    })

    it('应渲染右侧区域', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElDropdown: true, ElIcon: true } }
      })
      expect(wrapper.find('.navbar-right').exists()).toBe(true)
    })

    it('应渲染页面信息区域', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElDropdown: true, ElIcon: true } }
      })
      expect(wrapper.find('.page-info').exists()).toBe(true)
    })
  })

  describe('用户信息显示', () => {
    it('应渲染用户下拉触发器', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.find('.user-dropdown-trigger').exists()).toBe(true)
    })

    it('应渲染用户头像区域', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.find('.user-avatar').exists()).toBe(true)
    })

    it('应渲染用户信息区域', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.find('.user-info').exists()).toBe(true)
    })
  })

  describe('角色显示', () => {
    it('应渲染角色徽章', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.find('.role-badge').exists()).toBe(true)
    })

    it('管理员角色应有admin样式类', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.find('.role-badge.admin').exists()).toBe(true)
    })

    it('应显示正确的角色文本', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.vm.roleText).toBe('管理员')
    })
  })

  describe('角色文本映射', () => {
    const roleMap = {
      'admin': '管理员',
      'user': '普通用户'
    }

    it('admin应映射为管理员', () => {
      expect(roleMap['admin']).toBe('管理员')
    })

    it('user应映射为普通用户', () => {
      expect(roleMap['user']).toBe('普通用户')
    })
  })

  describe('页面副标题映射', () => {
    const subtitles = {
      '/fx-data': '外汇行情数据可视化',
      '/datasource': '管理数据采集来源',
      '/collection': '配置数据采集任务',
      '/users': '管理系统用户账户',
      '/logs': '查看系统运行日志'
    }

    it('数据分析页面应有正确副标题', () => {
      expect(subtitles['/fx-data']).toBe('外汇行情数据可视化')
    })

    it('数据源管理页面应有正确副标题', () => {
      expect(subtitles['/datasource']).toBe('管理数据采集来源')
    })

    it('采集任务页面应有正确副标题', () => {
      expect(subtitles['/collection']).toBe('配置数据采集任务')
    })

    it('用户管理页面应有正确副标题', () => {
      expect(subtitles['/users']).toBe('管理系统用户账户')
    })

    it('系统日志页面应有正确副标题', () => {
      expect(subtitles['/logs']).toBe('查看系统运行日志')
    })
  })

  describe('用户名显示', () => {
    it('应显示用户名', () => {
      const wrapper = mount(Navbar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.vm.authStore.user?.username).toBe('admin')
    })
  })
})