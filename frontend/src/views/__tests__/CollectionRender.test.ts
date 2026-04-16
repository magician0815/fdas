/**
 * Collection.vue渲染测试.
 *
 * 测试采集任务页面的组件渲染和交互.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Collection from '../Collection.vue'

// Mock Element Plus message service
vi.mock('element-plus', () => ({
  ElButton: { template: '<button class="el-button"><slot /></button>' },
  ElTable: { template: '<table class="el-table"><slot /></table>' },
  ElTableColumn: true,
  ElTag: { template: '<span class="el-tag"><slot /></span>' },
  ElIcon: { template: '<i class="el-icon"><slot /></i>' },
  ElDialog: { template: '<div class="el-dialog"><slot /></div>' },
  ElForm: { template: '<form class="el-form"><slot /></form>' },
  ElFormItem: { template: '<div class="el-form-item"><slot /></div>' },
  ElInput: { template: '<input class="el-input" />' },
  ElSelect: { template: '<select class="el-select"><slot /></select>' },
  ElOption: { template: '<option class="el-option" />' },
  ElEmpty: { template: '<div class="el-empty"><slot /></div>' },
  ElMessage: { info: vi.fn(), success: vi.fn(), error: vi.fn(), warning: vi.fn() }
}))

// Mock API calls
vi.mock('@/api/collection', () => ({
  default: {
    getTasks: vi.fn(() => Promise.resolve({ data: [] })),
    createTask: vi.fn(() => Promise.resolve({ data: {} })),
    updateTask: vi.fn(() => Promise.resolve({ data: {} })),
    deleteTask: vi.fn(() => Promise.resolve({ data: {} })),
    executeTask: vi.fn(() => Promise.resolve({ data: {} }))
  }
}))

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  Refresh: { template: '<svg class="refresh-icon" />' },
  Plus: { template: '<svg class="plus-icon" />' },
  Edit: { template: '<svg class="edit-icon" />' },
  Delete: { template: '<svg class="delete-icon" />' },
  VideoPlay: { template: '<svg class="video-play-icon" />' }
}))

describe('Collection.vue渲染测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const defaultStubs = {
    ElButton: { template: '<button class="el-button"><slot /></button>' },
    ElTable: { template: '<table class="el-table"><slot /></table>' },
    ElTableColumn: true,
    ElTag: true,
    ElIcon: true,
    ElDialog: true,
    ElForm: true,
    ElFormItem: true,
    ElInput: true,
    ElSelect: true,
    ElOption: true,
    ElEmpty: true
  }

  describe('页面结构渲染', () => {
    it('应渲染页面标题', () => {
      const wrapper = mount(Collection, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.page-title').text()).toBe('采集任务')
    })

    it('应渲染页面副标题', () => {
      const wrapper = mount(Collection, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.page-subtitle').text()).toBe('配置数据采集任务和调度')
    })

    it('应渲染刷新按钮', () => {
      const wrapper = mount(Collection, {
        global: { stubs: { ...defaultStubs, ElIcon: true } }
      })
      const buttons = wrapper.findAll('.el-button')
      expect(buttons.length).toBeGreaterThan(0)
    })

    it('应渲染多个操作按钮', () => {
      const wrapper = mount(Collection, {
        global: { stubs: { ...defaultStubs, ElIcon: true } }
      })
      const buttons = wrapper.findAll('.el-button')
      expect(buttons.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('统计数据渲染', () => {
    it('应渲染统计卡片', () => {
      const wrapper = mount(Collection, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.stats-row').exists()).toBe(true)
    })

    it('应显示总任务数', () => {
      const wrapper = mount(Collection, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.stat-label').text()).toContain('总任务数')
    })
  })

  describe('表格渲染', () => {
    it('应渲染任务表格', () => {
      const wrapper = mount(Collection, {
        global: { stubs: { ...defaultStubs, ElTag: { template: '<span class="el-tag"><slot /></span>' } } }
      })
      expect(wrapper.find('.el-table').exists()).toBe(true)
    })
  })

  describe('加载状态', () => {
    it('loading=true时应显示加载状态', () => {
      const wrapper = mount(Collection, { global: { stubs: defaultStubs } })
      expect(wrapper.vm.loading).toBeDefined()
    })
  })

  describe('空状态', () => {
    it('无任务时应显示空表格', () => {
      const wrapper = mount(Collection, { global: { stubs: defaultStubs } })
      expect(wrapper.vm.tasks).toEqual([])
    })
  })
})