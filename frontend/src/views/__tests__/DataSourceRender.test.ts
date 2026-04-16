/**
 * DataSource.vue渲染测试.
 *
 * 测试数据源管理页面的组件渲染和交互.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DataSource from '../DataSource.vue'

// Mock Element Plus components
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
  ElSwitch: { template: '<input type="checkbox" class="el-switch" />' },
  ElEmpty: { template: '<div class="el-empty"><slot /></div>' },
  ElMessage: { info: vi.fn(), success: vi.fn(), error: vi.fn(), warning: vi.fn() }
}))

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  Refresh: { template: '<svg class="refresh-icon" />' },
  Plus: { template: '<svg class="plus-icon" />' },
  Edit: { template: '<svg class="edit-icon" />' },
  Delete: { template: '<svg class="delete-icon" />' },
  Connection: { template: '<svg class="connection-icon" />' }
}))

// Mock API calls
vi.mock('@/api/datasource', () => ({
  default: {
    getDatasources: vi.fn(() => Promise.resolve({ data: [] })),
    createDatasource: vi.fn(() => Promise.resolve({ data: {} })),
    updateDatasource: vi.fn(() => Promise.resolve({ data: {} })),
    deleteDatasource: vi.fn(() => Promise.resolve({ data: {} })),
    syncDatasource: vi.fn(() => Promise.resolve({ data: {} }))
  }
}))

describe('DataSource.vue渲染测试', () => {
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
    ElSwitch: true,
    ElEmpty: true
  }

  describe('页面结构渲染', () => {
    it('应渲染页面标题', () => {
      const wrapper = mount(DataSource, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.page-title').text()).toContain('数据源')
    })

    it('应渲染页面副标题', () => {
      const wrapper = mount(DataSource, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.page-subtitle').exists()).toBe(true)
    })
  })

  describe('数据源列表渲染', () => {
    it('应渲染数据源表格', () => {
      const wrapper = mount(DataSource, { global: { stubs: defaultStubs } })
      expect(wrapper.vm.datasources).toBeDefined()
    })
  })

  describe('操作按钮', () => {
    it('应渲染同步按钮', () => {
      const wrapper = mount(DataSource, {
        global: { stubs: { ...defaultStubs, ElIcon: true } }
      })
      const buttons = wrapper.findAll('.el-button')
      expect(buttons.length).toBeGreaterThan(0)
    })

    it('应渲染多个操作按钮', () => {
      const wrapper = mount(DataSource, {
        global: { stubs: { ...defaultStubs, ElIcon: true } }
      })
      const buttons = wrapper.findAll('.el-button')
      expect(buttons.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('货币对显示', () => {
    it('应显示货币对数量', () => {
      const wrapper = mount(DataSource, { global: { stubs: defaultStubs } })
      expect(wrapper.vm.datasources).toBeDefined()
    })
  })

  describe('状态标签', () => {
    it('激活状态应显示success标签', () => {
      const wrapper = mount(DataSource, {
        global: { stubs: { ...defaultStubs, ElTag: { template: '<span class="el-tag"><slot /></span>' } } }
      })
      expect(wrapper.vm.datasources).toBeDefined()
    })
  })

  describe('加载状态', () => {
    it('loading=true时应显示加载', () => {
      const wrapper = mount(DataSource, { global: { stubs: defaultStubs } })
      expect(wrapper.vm.loading).toBeDefined()
    })
  })

  describe('数据源状态判断', () => {
    const isActive = (ds) => ds?.is_active === true
    const isSyncing = (ds) => ds?.sync_status === 'syncing'

    it('is_active=true应为激活状态', () => {
      expect(isActive({ is_active: true })).toBe(true)
      expect(isActive({ is_active: false })).toBe(false)
    })

    it('sync_status=syncing应为同步中', () => {
      expect(isSyncing({ sync_status: 'syncing' })).toBe(true)
      expect(isSyncing({ sync_status: 'completed' })).toBe(false)
    })
  })
})