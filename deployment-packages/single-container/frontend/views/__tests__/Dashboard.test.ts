/**
 * Dashboard页面测试.
 *
 * 测试首页核心逻辑：统计数据、角色判断、时间更新.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import Dashboard from '../Dashboard.vue'

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  TrendCharts: { name: 'TrendCharts', template: '<svg></svg>' },
  Connection: { name: 'Connection', template: '<svg></svg>' },
  Timer: { name: 'Timer', template: '<svg></svg>' },
  Document: { name: 'Document', template: '<svg></svg>' },
  Clock: { name: 'Clock', template: '<svg></svg>' },
  Top: { name: 'Top', template: '<svg></svg>' },
  CircleCheck: { name: 'CircleCheck', template: '<svg></svg>' },
  CircleClose: { name: 'CircleClose', template: '<svg></svg>' },
  Loading: { name: 'Loading', template: '<svg></svg>' }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    user: { username: 'admin', role: 'admin' }
  }))
}))

describe('Dashboard', () => {
  let wrapper: VueWrapper<any>

  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
    wrapper?.unmount()
  })

  describe('统计数据', () => {
    it('应该显示数据记录统计', () => {
      wrapper = mount(Dashboard, {
        global: { stubs: { ElIcon: true, ElEmpty: true } }
      })
      const vm = wrapper.vm as any
      expect(vm.stats.dataRecords).toBe('12,856')
      expect(vm.stats.datasources).toBe('5')
      expect(vm.stats.tasks).toBe('8')
      expect(vm.stats.logs).toBe('1,245')
      expect(vm.stats.successRate).toBe('98.5')
    })
  })

  describe('最近动态', () => {
    it('应该显示最近动态列表', () => {
      wrapper = mount(Dashboard, {
        global: { stubs: { ElIcon: true, ElEmpty: true } }
      })
      const vm = wrapper.vm as any
      expect(vm.recentActivities.length).toBe(3)
    })
  })

  describe('用户角色判断', () => {
    it('admin用户isAdmin应为true', async () => {
      wrapper = mount(Dashboard, {
        global: { stubs: { ElIcon: true, ElEmpty: true } }
      })
      const vm = wrapper.vm as any
      expect(vm.isAdmin).toBe(true)
    })
  })

  describe('时间更新', () => {
    it('应该显示当前时间', async () => {
      wrapper = mount(Dashboard, {
        global: { stubs: { ElIcon: true, ElEmpty: true } }
      })
      const vm = wrapper.vm as any
      vm.updateTime()
      expect(vm.currentTime).toBeTruthy()
      expect(vm.currentTime).toContain('2026')
    })

    it('挂载时应启动定时器', () => {
      wrapper = mount(Dashboard, {
        global: { stubs: { ElIcon: true, ElEmpty: true } }
      })
      const vm = wrapper.vm as any
      expect(vm.timeInterval).toBeDefined()
    })
  })

  describe('页面结构', () => {
    it('应该渲染dashboard页面', () => {
      wrapper = mount(Dashboard, {
        global: { stubs: { ElIcon: true, ElEmpty: true } }
      })
      expect(wrapper.find('.dashboard-page').exists()).toBe(true)
    })
  })
})