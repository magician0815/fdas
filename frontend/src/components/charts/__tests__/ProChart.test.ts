/**
 * ProChart组件测试.
 *
 * 测试专业行情图表面板组合、主题切换、图表联动.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import ProChart from '../ProChart.vue'
import { nextTick } from 'vue'

// Mock ECharts - 支持import * as echarts方式
vi.mock('echarts', () => {
  const mockChartInstance = {
    setOption: vi.fn(),
    clear: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    on: vi.fn(),
    getOption: vi.fn(() => ({})),
    group: 'test'
  }
  return {
    init: vi.fn(() => mockChartInstance),
    connect: vi.fn(),
    disconnect: vi.fn(),
    graphic: { LinearGradient: vi.fn() }
  }
})

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  FullScreen: { name: 'FullScreen', template: '<svg></svg>' },
  Aim: { name: 'Aim', template: '<svg></svg>' },
  Rank: { name: 'Rank', template: '<svg></svg>' },
  DataLine: { name: 'DataLine', template: '<svg></svg>' },
  ArrowDown: { name: 'ArrowDown', template: '<svg></svg>' },
  Close: { name: 'Close', template: '<svg></svg>' },
  RefreshRight: { name: 'RefreshRight', template: '<svg></svg>' },
  Edit: { name: 'Edit', template: '<svg></svg>' },
  Operation: { name: 'Operation', template: '<svg></svg>' },
  CopyDocument: { name: 'CopyDocument', template: '<svg></svg>' },
  Warning: { name: 'Warning', template: '<svg></svg>' },
  Setting: { name: 'Setting', template: '<svg></svg>' }
}))

// Mock chartConfig
vi.mock('@/utils/chartConfig', () => ({
  chartThemes: {
    light: {
      textPrimary: '#333333',
      textSecondary: '#666666',
      gridLine: '#e0e0e0',
      axisLine: '#cccccc'
    },
    dark: {
      textPrimary: '#ffffff',
      textSecondary: '#aaaaaa',
      gridLine: '#333333',
      axisLine: '#444444'
    }
  },
  getKLineBaseOption: vi.fn(() => ({ xAxis: [], yAxis: [], series: [] })),
  getKLineSeriesOption: vi.fn(() => ({ name: 'K线', type: 'candlestick', data: [] })),
  getMASeriesOption: vi.fn(() => ({ type: 'line', data: [] })),
  formatKLineData: vi.fn((data) => data),
  detectGaps: vi.fn(() => []),
  detectLongShadows: vi.fn(() => []),
  MarketType: { FOREX: 'forex' },
  getMarketConfig: vi.fn(() => ({ name: '外汇', hasLimitUpDown: false, needAdjustment: false, pricePrecision: 4 }))
}))

// Mock stockUtils
vi.mock('@/utils/stockUtils', () => ({
  identifyMarketTypeByName: vi.fn(() => 'forex'),
  marketConfigs: { forex: { name: '外汇', hasLimitUpDown: false } },
  calculateLimitUpPrice: vi.fn((p) => p * 1.1),
  calculateLimitDownPrice: vi.fn((p) => p * 0.9),
  isLimitUp: vi.fn(() => false),
  isLimitDown: vi.fn(() => false),
  calculateLimitUpDownStats: vi.fn(() => ({ limitUpCount: 0 })),
  AdjustmentType: { NONE: 'none' },
  calculateAdjustedPrices: vi.fn((d) => d)
}))

// Mock useDrawing
vi.mock('@/hooks/useDrawing', () => ({
  useDrawing: vi.fn(() => ({
    currentTool: { value: null },
    currentColor: { value: '#FF6B6B' },
    currentLineWidth: { value: 2 },
    magnetEnabled: { value: true },
    drawings: { value: [] },
    selectedDrawingId: { value: null },
    isDrawing: { value: false },
    setTool: vi.fn(),
    cancelDrawing: vi.fn(),
    setMagnet: vi.fn()
  }))
}))

// Mock element-plus
vi.mock('element-plus', () => ({
  ElMessage: { success: vi.fn(), warning: vi.fn(), error: vi.fn() }
}))

// Element Plus组件stubs
const globalStubs = {
  ElSwitch: { template: '<input type="checkbox" />', props: ['modelValue', 'size', 'activeText', 'inactiveText'] },
  ElButton: { template: '<button><slot /></button>', props: ['size', 'text'] },
  ElIcon: { template: '<i><slot /></i>' },
  // Stub子组件避免实际渲染
  KLineChart: {
    template: '<div class="kline-chart-mock"></div>',
    props: ['data', 'maData', 'symbolName', 'symbolId', 'theme'],
    methods: {
      resizeChart: vi.fn(),
      getChartInstance: vi.fn(() => ({ group: 'test' }))
    }
  },
  VolumeChart: {
    template: '<div class="volume-chart-mock"></div>',
    props: ['data', 'theme', 'volData'],
    methods: {
      resizeChart: vi.fn(),
      getChartInstance: vi.fn(() => ({ group: 'test' }))
    }
  },
  MACDChart: {
    template: '<div class="macd-chart-mock"></div>',
    props: ['data', 'dates', 'theme'],
    methods: {
      resizeChart: vi.fn(),
      getChartInstance: vi.fn(() => ({ group: 'test' }))
    }
  },
  RangeStats: { template: '<div></div>' },
  DrawingToolbar: { template: '<div></div>' },
  AdjustmentPanel: { template: '<div></div>' },
  // KLineChart内部的Element Plus组件
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'size'] },
  ElRadioButton: { template: '<label><slot /></label>', props: ['value'] },
  ElTooltip: { template: '<div><slot /></div>', props: ['content'] },
  ElDropdown: { template: '<div><slot /></div>' },
  ElDropdownMenu: { template: '<ul><slot /></ul>' },
  ElDropdownItem: { template: '<li><slot /></li>' },
  ElCheckboxGroup: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElCheckbox: { template: '<label><slot /></label>', props: ['label'] },
  ElDatePicker: { template: '<input />', props: ['modelValue'] },
  ElEmpty: { template: '<div class="el-empty"></div>' }
}

describe('ProChart', () => {
  let wrapper: VueWrapper<any>

  const mockData = [
    { date: '2026-04-01', open: 7.10, close: 7.15, high: 7.20, low: 7.05, volume: 1000 },
    { date: '2026-04-02', open: 7.15, close: 7.20, high: 7.25, low: 7.10, volume: 1200 },
    { date: '2026-04-03', open: 7.20, close: 7.18, high: 7.30, low: 7.15, volume: 800 }
  ]

  const mockIndicators = {
    ma: { ma5: [{ value: 7.15 }, { value: 7.17 }] },
    macd: { dif: [0.01, 0.02], dea: [0.008], macd: [0.002] },
    vol: { vol5: [{ value: 1000 }] }
  }

  const mountOptions = (props = {}) => ({
    props,
    global: { stubs: globalStubs }
  })

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  afterEach(() => wrapper?.unmount())

  describe('组件渲染', () => {
    it('应该正确渲染组件结构', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      expect(wrapper.find('.pro-chart-panel').exists()).toBe(true)
      expect(wrapper.find('.main-chart-section').exists()).toBe(true)
      expect(wrapper.find('.sub-chart-section').exists()).toBe(true)
    })

    it('应该渲染主题切换开关', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      expect(wrapper.find('.theme-switch').exists()).toBe(true)
    })

    it('应该渲染子组件stub', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      expect(wrapper.find('.kline-chart-mock').exists()).toBe(true)
      expect(wrapper.find('.volume-chart-mock').exists()).toBe(true)
      expect(wrapper.find('.macd-chart-mock').exists()).toBe(true)
    })

    it('应该渲染可拖拽分隔线', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      expect(wrapper.find('.chart-divider').exists()).toBe(true)
    })
  })

  describe('Props处理', () => {
    it('应该接收data prop', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      expect(wrapper.props('data')).toEqual(mockData)
    })

    it('应该接收indicators prop', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData, indicators: mockIndicators }))
      expect(wrapper.props('indicators')).toEqual(mockIndicators)
    })

    it('应该接收symbolName prop', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData, symbolName: 'USDCNH' }))
      expect(wrapper.props('symbolName')).toBe('USDCNH')
    })

    it('应该接收loading prop', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData, loading: true }))
      expect(wrapper.props('loading')).toBe(true)
    })
  })

  describe('加载状态', () => {
    it('应该显示加载骨架屏当loading为true', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData, loading: true }))
      expect(wrapper.find('.loading-overlay').exists()).toBe(true)
    })

    it('应该隐藏加载骨架屏当loading为false', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData, loading: false }))
      expect(wrapper.find('.loading-overlay').exists()).toBe(false)
    })
  })

  describe('主题切换', () => {
    it('初始主题应为light', async () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      const vm = wrapper.vm as any
      expect(vm.currentTheme).toBe('light')
    })

    it('应该从localStorage恢复dark主题', async () => {
      localStorage.setItem('fdas_theme', 'dark')
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      const vm = wrapper.vm as any
      expect(vm.isDarkTheme).toBe(true)
    })

    it('切换主题应保存到localStorage', async () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      const vm = wrapper.vm as any
      vm.handleThemeChange(true)
      expect(localStorage.getItem('fdas_theme')).toBe('dark')
    })
  })

  describe('暴露方法', () => {
    it('应该暴露resizeAll方法', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      expect(typeof wrapper.vm.resizeAll).toBe('function')
    })

    it('应该暴露cleanup方法', () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      expect(typeof wrapper.vm.cleanup).toBe('function')
    })
  })

  describe('数据变化监听', () => {
    it('应该响应data变化', async () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData }))
      const newData = [...mockData, { date: '2026-04-04', open: 7.18, close: 7.22, high: 7.28, low: 7.16, volume: 900 }]
      await wrapper.setProps({ data: newData })
      expect(wrapper.props('data').length).toBe(4)
    })

    it('应该响应loading变化', async () => {
      wrapper = mount(ProChart, mountOptions({ data: mockData, loading: false }))
      await wrapper.setProps({ loading: true })
      expect(wrapper.find('.loading-overlay').exists()).toBe(true)
    })
  })

  describe('边界情况', () => {
    it('应该处理空数据数组', () => {
      wrapper = mount(ProChart, mountOptions({ data: [] }))
      expect(wrapper.props('data')).toEqual([])
    })
  })
})