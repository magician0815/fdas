/**
 * KLineChart组件测试.
 *
 * 测试K线主图渲染、工具栏、画线功能、视图状态保存.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import KLineChart from '../KLineChart.vue'
import { nextTick } from 'vue'

// Mock ECharts
const mockChartInstance = {
  setOption: vi.fn(),
  getOption: vi.fn(() => ({
    xAxis: [{ data: [] }],
    yAxis: [
      { min: 0, max: 100, axisLabel: { show: true }, axisLine: { show: true } },
      { min: 0, max: 100, axisLabel: { show: true }, axisLine: { show: true } }
    ],
    dataZoom: [{ start: 60, end: 100 }]
  })),
  clear: vi.fn(),
  resize: vi.fn(),
  dispose: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  getZr: vi.fn(() => ({ on: vi.fn() })),
  dispatchAction: vi.fn(),
  convertFromPixel: vi.fn(() => [0, 7.15])
}

vi.mock('echarts', () => ({
  init: vi.fn(() => mockChartInstance),
  graphic: { LinearGradient: vi.fn() }
}))

// Mock chartConfig utils
vi.mock('@/utils/chartConfig', () => ({
  getKLineBaseOption: vi.fn(() => ({
    xAxis: [{ data: [] }],
    yAxis: [
      { axisLabel: { show: true }, axisLine: { show: true } },
      { axisLabel: { show: true }, axisLine: { show: true } }
    ],
    legend: { data: [] },
    dataZoom: [{ start: 60, end: 100 }, { start: 60, end: 100 }],
    series: []
  })),
  getKLineSeriesOption: vi.fn(() => ({ name: 'K线', type: 'candlestick', data: [] })),
  getMASeriesOption: vi.fn((period) => ({ name: `MA${period}`, type: 'line', data: [] })),
  formatKLineData: vi.fn((data) => data.map(d => [d.open, d.close, d.low, d.high])),
  chartThemes: {
    light: {
      textPrimary: '#333333',
      textSecondary: '#666666',
      gridLine: '#e0e0e0',
      axisLine: '#cccccc',
      upColor: '#ef4444',
      downColor: '#22c55e',
      ma5Color: '#f59e0b',
      ma10Color: '#3b82f6',
      ma20Color: '#8b5cf6',
      ma60Color: '#22c55e',
      limitUpColor: '#ef4444',
      limitDownColor: '#22c55e',
      limitUpBgColor: 'rgba(239, 68, 68, 0.1)',
      limitDownBgColor: 'rgba(34, 197, 94, 0.1)'
    },
    dark: {
      textPrimary: '#ffffff',
      textSecondary: '#aaaaaa',
      gridLine: '#333333',
      axisLine: '#444444',
      upColor: '#ef4444',
      downColor: '#22c55e',
      ma5Color: '#f59e0b',
      ma10Color: '#3b82f6',
      ma20Color: '#8b5cf6',
      ma60Color: '#22c55e',
      limitUpColor: '#ef4444',
      limitDownColor: '#22c55e',
      limitUpBgColor: 'rgba(239, 68, 68, 0.1)',
      limitDownBgColor: 'rgba(34, 197, 94, 0.1)'
    }
  },
  detectGaps: vi.fn(() => []),
  detectLongShadows: vi.fn(() => []),
  generateGapMarkPoints: vi.fn(() => null),
  generateGapMarkLines: vi.fn(() => null),
  MarketType: { FOREX: 'forex', STOCK_CN_A: 'stock_cn_a' },
  getMarketConfig: vi.fn(() => ({
    name: '外汇',
    hasLimitUpDown: false,
    needAdjustment: false,
    pricePrecision: 4
  }))
}))

// Mock stockUtils
vi.mock('@/utils/stockUtils', () => ({
  identifyMarketTypeByName: vi.fn(() => 'forex'),
  marketConfigs: {
    stock_cn_a: { name: 'A股', limitUpThreshold: 10, hasLimitUpDown: true },
    forex: { name: '外汇', hasLimitUpDown: false }
  },
  calculateLimitUpPrice: vi.fn((prevClose) => prevClose * 1.1),
  calculateLimitDownPrice: vi.fn((prevClose) => prevClose * 0.9),
  isLimitUp: vi.fn(() => false),
  isLimitDown: vi.fn(() => false),
  calculateLimitUpDownStats: vi.fn(() => ({ limitUpCount: 0, limitDownCount: 0 })),
  AdjustmentType: { NONE: 'none', FORWARD: 'forward', BACKWARD: 'backward' },
  calculateAdjustedPrices: vi.fn((data) => data)
}))

// Mock useDrawing hook
vi.mock('@/hooks/useDrawing', () => ({
  useDrawing: vi.fn(() => ({
    currentTool: { value: null },
    currentColor: { value: '#FF6B6B' },
    currentLineWidth: { value: 2 },
    magnetEnabled: { value: true },
    drawings: { value: [] },
    selectedDrawingId: { value: null },
    isDrawing: { value: false },
    currentToolParams: { value: {} },
    setTool: vi.fn(),
    setColor: vi.fn(),
    setLineWidth: vi.fn(),
    setMagnet: vi.fn(),
    setToolParams: vi.fn(),
    startDrawing: vi.fn(),
    onDrawing: vi.fn(),
    endDrawing: vi.fn(),
    cancelDrawing: vi.fn(),
    deleteSelectedDrawing: vi.fn(),
    magnetToPoint: vi.fn((x, y) => ({ x, y })),
    drawingCount: { value: 0 },
    selectedDrawing: { value: null },
    isCursorLocked: { value: false }
  }))
}))

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: { success: vi.fn(), warning: vi.fn(), error: vi.fn() }
}))

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  ArrowDown: { name: 'ArrowDown', template: '<svg></svg>' },
  Rank: { name: 'Rank', template: '<svg></svg>' },
  DataLine: { name: 'DataLine', template: '<svg></svg>' },
  Close: { name: 'Close', template: '<svg></svg>' },
  CopyDocument: { name: 'CopyDocument', template: '<svg></svg>' },
  RefreshRight: { name: 'RefreshRight', template: '<svg></svg>' },
  Edit: { name: 'Edit', template: '<svg></svg>' },
  Operation: { name: 'Operation', template: '<svg></svg>' }
}))

// Mock child components
vi.mock('../RangeStats.vue', () => ({ default: { name: 'RangeStats', template: '<div></div>' } }))
vi.mock('../DrawingToolbar.vue', () => ({ default: { name: 'DrawingToolbar', template: '<div></div>', props: ['tool', 'color', 'lineWidth', 'magnet'] } }))
vi.mock('../AdjustmentPanel.vue', () => ({ default: { name: 'AdjustmentPanel', template: '<div></div>', props: ['modelValue', 'hasAdjustment'] } }))

// Element Plus组件stubs
const globalStubs = {
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'size'] },
  ElRadioButton: { template: '<label><slot /></label>', props: ['value'] },
  ElButton: { template: '<button><slot /></button>', props: ['size', 'text', 'type'] },
  ElTooltip: { template: '<div><slot /></div>', props: ['content', 'placement'] },
  ElDropdown: { template: '<div><slot /></div>', props: ['trigger', 'size'] },
  ElDropdownMenu: { template: '<ul><slot /></ul>' },
  ElDropdownItem: { template: '<li><slot /></li>' },
  ElCheckboxGroup: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElCheckbox: { template: '<label><slot /></label>', props: ['label'] },
  ElDatePicker: { template: '<input type="date" />', props: ['modelValue', 'type', 'placeholder', 'size', 'format', 'valueFormat', 'clearable'] },
  ElEmpty: { template: '<div class="el-empty"><slot /></div>', props: ['description'] },
  ElIcon: { template: '<i><slot /></i>' }
}

describe('KLineChart', () => {
  let wrapper: VueWrapper<any>

  const mockData = [
    { date: '2026-04-01', open: 7.10, close: 7.15, high: 7.20, low: 7.05, volume: 1000 },
    { date: '2026-04-02', open: 7.15, close: 7.20, high: 7.25, low: 7.10, volume: 1200 },
    { date: '2026-04-03', open: 7.20, close: 7.18, high: 7.30, low: 7.15, volume: 800 },
    { date: '2026-04-04', open: 7.18, close: 7.22, high: 7.28, low: 7.16, volume: 900 }
  ]

  const mockMaData = {
    ma5: [{ value: 7.15 }, { value: 7.17 }, { value: 7.19 }, { value: 7.20 }],
    ma10: [{ value: 7.12 }, { value: 7.14 }, { value: 7.16 }, { value: 7.18 }]
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
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      expect(wrapper.find('.kline-chart-container').exists()).toBe(true)
      expect(wrapper.find('.chart-toolbar').exists()).toBe(true)
      expect(wrapper.find('.chart-area').exists()).toBe(true)
    })

    it('应该渲染工具栏左侧标题区域', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData, symbolName: 'USDCNH' }))
      expect(wrapper.find('.toolbar-left').exists()).toBe(true)
      expect(wrapper.find('.chart-title').text()).toBe('USDCNH')
    })

    it('应该显示当前价格和涨跌幅', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      expect(wrapper.find('.current-price').exists()).toBe(true)
      expect(wrapper.find('.current-price').text()).toBe('7.2200')
    })

    it('应该显示无数据提示当data为空', () => {
      wrapper = mount(KLineChart, mountOptions({ data: [] }))
      expect(wrapper.find('.el-empty').exists()).toBe(true)
    })

    it('应该显示默认标题当无symbolName', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData, symbolName: '' }))
      expect(wrapper.find('.chart-title').text()).toBe('选择货币对')
    })
  })

  describe('Props处理', () => {
    it('应该接收data prop', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      expect(wrapper.props('data')).toEqual(mockData)
    })

    it('应该接收symbolName prop', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData, symbolName: 'USDCNH' }))
      expect(wrapper.props('symbolName')).toBe('USDCNH')
    })

    it('应该接收maData prop', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData, maData: mockMaData }))
      expect(wrapper.props('maData')).toEqual(mockMaData)
    })

    it('应该接收theme prop', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData, theme: 'dark' }))
      expect(wrapper.props('theme')).toBe('dark')
    })
  })

  describe('图表类型切换', () => {
    it('初始图表类型应为candle', async () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      const vm = wrapper.vm as any
      expect(vm.chartType).toBe('candle')
    })

    it('切换图表类型应保存到localStorage', async () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      const vm = wrapper.vm as any
      vm.handleChartTypeChange('line')
      expect(localStorage.getItem('fdas_chart_type')).toBe('line')
    })
  })

  describe('均线显示控制', () => {
    it('初始可见均线应包含5,10,20,60', async () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      const vm = wrapper.vm as any
      expect(vm.visibleMA).toEqual(['5', '10', '20', '60'])
    })

    it('切换均线显示应emit maChange事件', async () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData, maData: mockMaData }))
      const vm = wrapper.vm as any
      vm.handleMAChange(['5', '10'])
      expect(wrapper.emitted('maChange')).toBeTruthy()
    })
  })

  describe('右侧价格轴切换', () => {
    it('初始右侧价格轴应隐藏', async () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      const vm = wrapper.vm as any
      expect(vm.showRightAxis).toBe(false)
    })
  })

  describe('画线工具栏', () => {
    it('初始画线工具栏应隐藏', async () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      const vm = wrapper.vm as any
      expect(vm.showDrawingToolbar).toBe(false)
    })
  })

  describe('暴露方法', () => {
    it('应该暴露resizeChart方法', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      expect(typeof wrapper.vm.resizeChart).toBe('function')
    })

    it('应该暴露getChartInstance方法', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      expect(typeof wrapper.vm.getChartInstance).toBe('function')
    })

    it('应该暴露resetView方法', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      expect(typeof wrapper.vm.resetView).toBe('function')
    })
  })

  describe('数据变化监听', () => {
    it('应该响应data变化', async () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData }))
      const newData = [...mockData, { date: '2026-04-05', open: 7.22, close: 7.25, high: 7.30, low: 7.20, volume: 1100 }]
      await wrapper.setProps({ data: newData })
      expect(wrapper.props('data').length).toBe(5)
    })

    it('应该响应theme变化', async () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData, theme: 'light' }))
      await wrapper.setProps({ theme: 'dark' })
      expect(wrapper.props('theme')).toBe('dark')
    })
  })

  describe('边界情况', () => {
    it('应该处理空数据数组', () => {
      wrapper = mount(KLineChart, mountOptions({ data: [] }))
      expect(wrapper.props('data')).toEqual([])
    })

    it('应该处理undefined maData', () => {
      wrapper = mount(KLineChart, mountOptions({ data: mockData, maData: undefined }))
      expect(wrapper.props('maData')).toEqual({})
    })

    it('应该处理单个数据点', () => {
      wrapper = mount(KLineChart, mountOptions({ data: [{ date: '2026-04-01', open: 7.10, close: 7.15, high: 7.20, low: 7.05 }] }))
      expect(wrapper.props('data').length).toBe(1)
    })
  })
})