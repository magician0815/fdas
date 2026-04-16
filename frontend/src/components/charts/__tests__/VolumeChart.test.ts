/**
 * VolumeChart组件测试.
 *
 * 测试成交量副图渲染、均线显示、主题切换.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import VolumeChart from '../VolumeChart.vue'

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
    init: vi.fn(() => mockChartInstance),
    graphic: { LinearGradient: vi.fn() }
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
      volumeUpColor: '#ef4444',
      volumeDownColor: '#22c55e',
      ma5Color: '#f59e0b',
      ma10Color: '#3b82f6'
    },
    dark: {
      textPrimary: '#ffffff',
      textSecondary: '#aaaaaa',
      gridLine: '#333333',
      axisLine: '#444444',
      volumeUpColor: '#ef4444',
      volumeDownColor: '#22c55e',
      ma5Color: '#f59e0b',
      ma10Color: '#3b82f6'
    }
  },
  formatVolumeData: vi.fn((data) => data)
}))

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  Warning: { name: 'Warning', template: '<svg></svg>' }
}))

// Element Plus组件stubs
const globalStubs = {
  ElCheckboxGroup: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElCheckboxButton: { template: '<label><slot /></label>', props: ['label'] },
  ElIcon: { template: '<i><slot /></i>' }
}

describe('VolumeChart', () => {
  let wrapper: VueWrapper<any>

  const mockData = [
    { date: '2026-04-01', open: 7.10, close: 7.15, high: 7.20, low: 7.05, volume: 1000 },
    { date: '2026-04-02', open: 7.15, close: 7.20, high: 7.25, low: 7.10, volume: 1200 },
    { date: '2026-04-03', open: 7.20, close: 7.18, high: 7.30, low: 7.15, volume: 800 }
  ]

  const mountOptions = (props = {}) => ({
    props,
    global: { stubs: globalStubs }
  })

  beforeEach(() => vi.clearAllMocks())
  afterEach(() => wrapper?.unmount())

  describe('组件渲染', () => {
    it('应该正确渲染组件结构', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData }))
      expect(wrapper.find('.volume-chart-container').exists()).toBe(true)
      expect(wrapper.find('.chart-header').exists()).toBe(true)
      expect(wrapper.find('.chart-title').text()).toBe('成交量')
    })

    it('应该显示外汇无成交量提示当所有volume为0', () => {
      const zeroVolumeData = mockData.map(d => ({ ...d, volume: 0 }))
      wrapper = mount(VolumeChart, mountOptions({ data: zeroVolumeData }))
      expect(wrapper.find('.volume-warning').exists()).toBe(true)
    })

    it('应该隐藏提示当有volume数据', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData }))
      expect(wrapper.find('.volume-warning').exists()).toBe(false)
    })
  })

  describe('Props处理', () => {
    it('应该接收data prop', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData }))
      expect(wrapper.props('data')).toEqual(mockData)
    })

    it('应该使用默认theme为light', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData }))
      expect(wrapper.props('theme')).toBe('light')
    })

    it('应该接收dark主题', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData, theme: 'dark' }))
      expect(wrapper.props('theme')).toBe('dark')
    })

    it('应该处理空数据数组', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: [] }))
      expect(wrapper.props('data')).toEqual([])
    })
  })

  describe('暴露方法', () => {
    it('应该暴露resizeChart方法', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData }))
      expect(typeof wrapper.vm.resizeChart).toBe('function')
    })

    it('应该暴露renderChart方法', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData }))
      expect(typeof wrapper.vm.renderChart).toBe('function')
    })

    it('应该暴露getChartInstance方法', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData }))
      expect(typeof wrapper.vm.getChartInstance).toBe('function')
    })
  })

  describe('边界情况', () => {
    it('应该处理无数据状态', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: [] }))
      expect(wrapper.props('data')).toEqual([])
    })

    it('应该处理undefined volData', () => {
      wrapper = mount(VolumeChart, mountOptions({ data: mockData, volData: undefined }))
      expect(wrapper.props('volData')).toEqual({})
    })
  })
})