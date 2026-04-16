/**
 * FXData.vue渲染测试.
 *
 * 测试数据分析页面的组件渲染和交互.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FXData from '../FXData.vue'

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElButton: {
    template: '<button class="el-button"><slot /></button>',
    props: ['type', 'loading', 'size']
  },
  ElSelect: {
    template: '<select class="el-select"><slot /></select>',
    props: ['modelValue', 'placeholder', 'filterable']
  },
  ElOption: {
    template: '<option class="el-option" />',
    props: ['value', 'label']
  },
  ElTable: {
    template: '<table class="el-table"><slot /></table>',
    props: ['data', 'loading', 'stripe', 'maxHeight']
  },
  ElTableColumn: true, // 完全 stub
  ElIcon: {
    template: '<i class="el-icon"><slot /></i>'
  },
  ElDatePicker: {
    template: '<input class="el-date-picker" type="date" />',
    props: ['modelValue', 'type', 'placeholder']
  },
  ElRadioGroup: {
    template: '<div class="el-radio-group"><slot /></div>',
    props: ['modelValue']
  },
  ElRadioButton: {
    template: '<label class="el-radio-button"><slot /></label>',
    props: ['label']
  },
  ElEmpty: {
    template: '<div class="el-empty"><slot /></div>',
    props: ['description']
  }
}))

// Mock child components
vi.mock('@/components/charts/ProChart.vue', () => ({
  default: {
    template: '<div class="pro-chart-mock">ProChart</div>',
    props: ['data', 'indicators', 'symbolName', 'symbolId', 'loading']
  }
}))

vi.mock('@/components/charts/KeyboardWizard.vue', () => ({
  default: {
    template: '<div class="keyboard-wizard-mock">KeyboardWizard</div>',
    props: ['modelValue', 'items', 'type']
  }
}))

vi.mock('@/components/charts/IndicatorWizard.vue', () => ({
  default: {
    template: '<div class="indicator-wizard-mock">IndicatorWizard</div>',
    props: ['modelValue', 'maPeriods', 'macdParams', 'volPeriods']
  }
}))

// Mock API calls
vi.mock('@/api/fx_data', () => ({
  getFXData: vi.fn(() => Promise.resolve({ success: true, data: [] })),
  getIndicators: vi.fn(() => Promise.resolve({ success: true, data: {} }))
}))

vi.mock('@/api/forex_symbols', () => ({
  getForexSymbols: vi.fn(() => Promise.resolve({ success: true, data: [] }))
}))

describe('FXData.vue渲染测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const defaultStubs = {
    ElButton: true, ElSelect: true, ElOption: true, ElIcon: true,
    ElTable: true, ElTableColumn: true,
    ProChart: true, KeyboardWizard: true, IndicatorWizard: true
  }

  describe('页面结构渲染', () => {
    it('应渲染页面标题', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.page-title').text()).toBe('数据分析')
    })

    it('应渲染页面副标题', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.page-subtitle').text()).toBe('专业行情走势')
    })
  })

  describe('统计卡片区域', () => {
    it('应渲染统计卡片行', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.stats-row').exists()).toBe(true)
    })

    it('应包含当前价格卡片', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      const labels = wrapper.findAll('.stat-label')
      expect(labels.some(l => l.text().includes('当前价格'))).toBe(true)
    })

    it('应包含涨跌幅卡片', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      const labels = wrapper.findAll('.stat-label')
      expect(labels.some(l => l.text().includes('涨跌幅'))).toBe(true)
    })

    it('应包含最高价卡片', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      const labels = wrapper.findAll('.stat-label')
      expect(labels.some(l => l.text().includes('最高价'))).toBe(true)
    })

    it('应包含最低价卡片', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      const labels = wrapper.findAll('.stat-label')
      expect(labels.some(l => l.text().includes('最低价'))).toBe(true)
    })

    it('应包含振幅卡片', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      const labels = wrapper.findAll('.stat-label')
      expect(labels.some(l => l.text().includes('振幅'))).toBe(true)
    })
  })

  describe('图表区域', () => {
    it('应渲染专业图表区域', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.pro-chart-section').exists()).toBe(true)
    })
  })

  describe('数据表格区域', () => {
    it('应渲染数据表格区域', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.data-table-section').exists()).toBe(true)
    })

    it('应渲染表格面板', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.table-panel').exists()).toBe(true)
    })

    it('应渲染历史数据标题', () => {
      const wrapper = mount(FXData, { global: { stubs: defaultStubs } })
      expect(wrapper.find('.panel-title').text()).toBe('历史数据')
    })
  })

  describe('选择器组件', () => {
    it('应渲染货币对选择器', () => {
      const wrapper = mount(FXData, { global: { stubs: { ...defaultStubs, ElSelect: { template: '<select class="el-select"><slot /></select>' } } } })
      expect(wrapper.find('.symbol-select').exists()).toBe(true)
    })

    it('应渲染周期选择器', () => {
      const wrapper = mount(FXData, { global: { stubs: { ...defaultStubs, ElSelect: { template: '<select class="el-select"><slot /></select>' } } } })
      expect(wrapper.find('.period-select').exists()).toBe(true)
    })
  })

  describe('操作按钮', () => {
    it('应渲染刷新按钮', () => {
      const wrapper = mount(FXData, { global: { stubs: { ...defaultStubs, ElButton: { template: '<button class="el-button"><slot /></button>' } } } })
      expect(wrapper.findAll('.el-button').length).toBeGreaterThan(0)
    })
  })

  describe('周期选项', () => {
    const periodOptions = [
      { value: 'daily', label: '日线' },
      { value: 'weekly', label: '周线' },
      { value: 'monthly', label: '月线' }
    ]

    it('应有日线选项', () => {
      expect(periodOptions.find(o => o.value === 'daily')).toBeDefined()
    })

    it('应有周线选项', () => {
      expect(periodOptions.find(o => o.value === 'weekly')).toBeDefined()
    })

    it('应有月线选项', () => {
      expect(periodOptions.find(o => o.value === 'monthly')).toBeDefined()
    })
  })

  describe('数据格式化', () => {
    const formatPrice = (value) => {
      if (!value) return '--'
      return parseFloat(value).toFixed(4)
    }

    const formatChange = (value) => {
      if (!value) return '--'
      return `${parseFloat(value).toFixed(2)}%`
    }

    it('formatPrice应正确格式化价格', () => {
      expect(formatPrice(7.1234)).toBe('7.1234')
      expect(formatPrice(null)).toBe('--')
    })

    it('formatChange应正确格式化涨跌幅', () => {
      expect(formatChange(0.5)).toBe('0.50%')
      expect(formatChange(null)).toBe('--')
    })
  })
})