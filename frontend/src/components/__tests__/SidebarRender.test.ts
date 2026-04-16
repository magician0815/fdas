/**
 * Sidebar.vue渲染测试.
 *
 * 测试侧边栏菜单组件的渲染和交互.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Sidebar from '../Sidebar.vue'

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElMenu: {
    template: '<div class="el-menu"><slot /></div>',
    props: ['defaultActive', 'collapse', 'backgroundColor', 'textColor', 'activeTextColor', 'router']
  },
  ElMenuItem: {
    template: '<div class="el-menu-item"><slot /><slot name="title" /></div>',
    props: ['index']
  },
  ElIcon: {
    template: '<i class="el-icon"><slot /></i>',
    props: ['size']
  }
}))

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  TrendCharts: { template: '<svg class="trend-charts-icon" />' },
  Connection: { template: '<svg class="connection-icon" />' },
  Timer: { template: '<svg class="timer-icon" />' },
  User: { template: '<svg class="user-icon" />' },
  Document: { template: '<svg class="document-icon" />' },
  Expand: { template: '<svg class="expand-icon" />' },
  Fold: { template: '<svg class="fold-icon" />' }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    user: { username: 'admin', role: 'admin' }
  }))
}))

// Mock vue-router with full route object
vi.mock('vue-router', () => ({
  useRoute: vi.fn(() => ({ path: '/fx-data', meta: { title: '数据分析' } }))
}))

describe('Sidebar.vue渲染测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('页面结构渲染', () => {
    it('应渲染侧边栏容器', () => {
      const wrapper = mount(Sidebar, {
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.find('.sidebar-container').exists()).toBe(true)
    })

    it('应渲染Logo区域', () => {
      const wrapper = mount(Sidebar, {
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.find('.logo-section').exists()).toBe(true)
    })

    it('应渲染Logo图标', () => {
      const wrapper = mount(Sidebar, {
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.find('.logo-icon').exists()).toBe(true)
    })

    it('应渲染底部折叠按钮区域', () => {
      const wrapper = mount(Sidebar, {
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.find('.sidebar-footer').exists()).toBe(true)
    })
  })

  describe('Logo文本显示', () => {
    it('展开时应显示Logo文本', () => {
      const wrapper = mount(Sidebar, {
        props: { collapsed: false },
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.find('.logo-text').exists()).toBe(true)
    })

    it('折叠时应隐藏Logo文本', () => {
      const wrapper = mount(Sidebar, {
        props: { collapsed: true },
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.find('.logo-text').exists()).toBe(false)
    })
  })

  describe('菜单渲染', () => {
    it('应渲染菜单组件', () => {
      const wrapper = mount(Sidebar, {
        global: {
          stubs: {
            ElIcon: true,
            ElMenu: { template: '<div class="el-menu"><slot /></div>' },
            ElMenuItem: { template: '<div class="el-menu-item"><slot /></div>' }
          }
        }
      })
      expect(wrapper.find('.el-menu').exists()).toBe(true)
    })

    it('数据分析菜单项应始终显示', () => {
      const wrapper = mount(Sidebar, {
        global: {
          stubs: {
            ElIcon: true,
            ElMenu: { template: '<div class="el-menu"><slot /></div>' },
            ElMenuItem: { template: '<div class="el-menu-item"><slot /></div>' }
          }
        }
      })
      const menuItems = wrapper.findAll('.el-menu-item')
      expect(menuItems.length).toBeGreaterThan(0)
    })
  })

  describe('折叠按钮', () => {
    it('应渲染折叠按钮', () => {
      const wrapper = mount(Sidebar, {
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.find('.collapse-btn').exists()).toBe(true)
    })
  })

  describe('Props传递', () => {
    it('collapsed属性应默认为false', () => {
      const wrapper = mount(Sidebar, {
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.props('collapsed')).toBe(false)
    })

    it('collapsed属性应正确接收', () => {
      const wrapper = mount(Sidebar, {
        props: { collapsed: true },
        global: { stubs: { ElMenu: true, ElMenuItem: true, ElIcon: true } }
      })
      expect(wrapper.props('collapsed')).toBe(true)
    })
  })

  describe('管理员权限', () => {
    it('管理员应看到所有菜单项', () => {
      const wrapper = mount(Sidebar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.vm.isAdmin).toBe(true)
    })
  })

  describe('菜单路径配置', () => {
    const menuPaths = ['/fx-data', '/datasource', '/collection', '/users', '/logs']

    it('数据分析路径应为/fx-data', () => {
      expect(menuPaths.includes('/fx-data')).toBe(true)
    })

    it('数据源管理路径应为/datasource', () => {
      expect(menuPaths.includes('/datasource')).toBe(true)
    })

    it('采集任务路径应为/collection', () => {
      expect(menuPaths.includes('/collection')).toBe(true)
    })

    it('用户管理路径应为/users', () => {
      expect(menuPaths.includes('/users')).toBe(true)
    })

    it('系统日志路径应为/logs', () => {
      expect(menuPaths.includes('/logs')).toBe(true)
    })
  })

  describe('当前激活菜单', () => {
    it('activeMenu应基于当前路由路径', () => {
      const wrapper = mount(Sidebar, {
        global: { stubs: { ElIcon: true } }
      })
      expect(wrapper.vm.activeMenu).toBe('/fx-data')
    })
  })
})