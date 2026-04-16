/**
 * MACDChart组件测试.
 *
 * 测试MACD副图渲染、参数设置、主题切换.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import MACDChart from '../MACDChart.vue'
import { nextTick } from 'vue'

// Mock ECharts - 支持import * as echarts方式
vi.mock('echarts', () => {
  const mockChartInstance = {
    setOption: vi.fn(),
    getOption: vi.fn(() => ({ xAxis: [{ data: [] }] })),
    clear: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn()
  }
  return {
    init: vi.fn(() => mockChartInstance)
  }
})

// Mock chartConfig utils
vi.mock('@/utils/chartConfig', () => ({
  chartThemes: {
    light: {
      textPrimary: '#333333',
      textSecondary: '#666666',
      gridLine: '#e0e0e0',
      axisLine: '#cccccc',
      difColor: '#f59e0b',
      deaColor: '#3b82f6',
      macdUpColor: '#ef4444',
      macdDownColor: '#22c55e'
    },
    dark: {
      textPrimary: '#ffffff',
      textSecondary: '#aaaaaa',
      gridLine: '#333333',
      axisLine: '#444444',
      difColor: '#f59e0b',
      deaColor: '#3b82f6',
      macdUpColor: '#ef4444',
      macdDownColor: '#22c55e'
    }
  },
  getMACDSeriesOptions: vi.fn(() => ({ name: 'MACD', type: 'bar', data: [] }))
}))

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  Setting: { name: 'Setting', template: '<svg></svg>' }
}))

// Element Plus组件stubs
const globalStubs = {
  ElButton: { template: '<button><slot /></button>', props: ['size', 'text', 'type'] },
  ElIcon: { template: '<i><slot /></i>' },
  ElDialog: { template: '<div class="el-dialog"><slot /></div>', props: ['modelValue', 'title', 'width'] },
  ElForm: { template: '<form><slot /></form>', props: ['model', 'labelWidth', 'size'] },
  ElFormItem: { template: '<div class="form-item"><slot /></div>', props: ['label'] },
  ElInputNumber: { template: '<input type="number" />', props: ['modelValue', 'min', 'max'] }
}

describe('MACDChart', () => {
  let wrapper: VueWrapper<any>

  const mockData = {
    dif: [0.01, 0.02, 0.015, 0.025, 0.03],
    dea: [0.008, 0.012, 0.014, 0.018, 0.022],
    macd: [0.002, 0.008, 0.001, 0.007, 0.008]
  }

  const mockDates = ['2026-04-01', '2026-04-02', '2026-04-03', '2026-04-04', '2026-04-05']

  const mountOptions = (props = {}) => ({
    props,
    global: { stubs: globalStubs }
  })

  beforeEach(() => vi.clearAllMocks())
  afterEach(() => wrapper?.unmount())

  describe('组件渲染', () => {
    it('应该正确渲染组件结构', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      expect(wrapper.find('.macd-chart-container').exists()).toBe(true)
      expect(wrapper.find('.chart-header').exists()).toBe(true)
      expect(wrapper.find('.chart-title').text()).toBe('MACD(12,26,9)')
    })

    it('应该渲染参数设置按钮', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      expect(wrapper.find('.chart-controls').exists()).toBe(true)
      expect(wrapper.find('button').exists()).toBe(true)
    })
  })

  describe('Props处理', () => {
    it('应该接收data prop', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      expect(wrapper.props('data')).toEqual(mockData)
    })

    it('应该接收dates prop', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      expect(wrapper.props('dates')).toEqual(mockDates)
    })

    it('应该使用默认theme为light', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      expect(wrapper.props('theme')).toBe('light')
    })

    it('应该接收dark主题', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates, theme: 'dark' }))
      expect(wrapper.props('theme')).toBe('dark')
    })

    it('应该处理空数据', () => {
      wrapper = mount(MACDChart, mountOptions({ data: {}, dates: [] }))
      expect(wrapper.props('data')).toEqual({})
      expect(wrapper.props('dates')).toEqual([])
    })
  })

  describe('参数设置', () => {
    it('默认MACD参数应为(12, 26, 9)', async () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      const vm = wrapper.vm as any
      expect(vm.macdParams.fast).toBe(12)
      expect(vm.macdParams.slow).toBe(26)
      expect(vm.macdParams.signal).toBe(9)
    })

    it('应用参数应emit paramChange事件', async () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      const vm = wrapper.vm as any
      vm.macdParams = { fast: 10, slow: 20, signal: 8 }
      vm.applyParams()
      await nextTick()
      expect(wrapper.emitted('paramChange')).toBeTruthy()
      expect(wrapper.emitted('paramChange')[0]).toEqual([{ fast: 10, slow: 20, signal: 8 }])
    })
  })

  describe('主题切换', () => {
    it('应该处理dark主题', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates, theme: 'dark' }))
      expect(wrapper.props('theme')).toBe('dark')
    })
  })

  describe('暴露方法', () => {
    it('应该暴露resizeChart方法', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      expect(typeof wrapper.vm.resizeChart).toBe('function')
    })

    it('应该暴露renderChart方法', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      expect(typeof wrapper.vm.renderChart).toBe('function')
    })

    it('应该暴露getChartInstance方法', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: mockDates }))
      expect(typeof wrapper.vm.getChartInstance).toBe('function')
    })
  })

  describe('边界情况', () => {
    it('应该处理空数组数据', () => {
      wrapper = mount(MACDChart, mountOptions({ data: { dif: [], dea: [], macd: [] }, dates: [] }))
      expect(wrapper.props('data').dif).toEqual([])
    })

    it('应该处理undefined data', () => {
      wrapper = mount(MACDChart, mountOptions({ data: undefined, dates: mockDates }))
      expect(wrapper.props('data')).toEqual({ dif: [], dea: [], macd: [] })
    })

    it('应该处理undefined dates', () => {
      wrapper = mount(MACDChart, mountOptions({ data: mockData, dates: undefined }))
      expect(wrapper.props('dates')).toEqual([])
    })
  })
})