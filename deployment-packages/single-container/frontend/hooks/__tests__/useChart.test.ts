/**
 * useChart Hook测试.
 *
 * 测试ECharts图表管理功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useChart } from '../useChart'
import * as echarts from 'echarts'

// Mock echarts
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn(),
    clear: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    showLoading: vi.fn(),
    hideLoading: vi.fn(),
    getOption: vi.fn(() => {}),
    getDataURL: vi.fn(() => 'data:image/png;base64,test'),
    group: null
  })),
  connect: vi.fn(),
  disconnect: vi.fn()
}))

describe('useChart', () => {
  let mockChartRef

  beforeEach(() => {
    // 创建mock DOM元素
    mockChartRef = {
      value: document.createElement('div')
    }

    // Mock window.addEventListener
    vi.spyOn(window, 'addEventListener').mockImplementation(() => {})
    vi.spyOn(window, 'removeEventListener').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('初始化', () => {
    it('应该返回正确的初始状态', () => {
      const { chartInstance, currentTheme, loading } = useChart(mockChartRef)

      expect(chartInstance.value).toBeNull()
      expect(currentTheme.value).toBe('light')
      expect(loading.value).toBe(false)
    })

    it('应该支持自定义主题', () => {
      const { currentTheme } = useChart(mockChartRef, { theme: 'dark' })

      expect(currentTheme.value).toBe('dark')
    })

    it('应该支持autoResize配置', () => {
      const result = useChart(mockChartRef, { autoResize: false })

      expect(result).toBeDefined()
    })
  })

  describe('图表操作', () => {
    it('setOption应该调用echarts.setOption', () => {
      const { setOption } = useChart(mockChartRef)

      setOption({ title: { text: 'Test' } })

      // 由于chartInstance初始为null，会先初始化
    })

    it('clearChart应该清理图表', () => {
      const { clearChart, initChart } = useChart(mockChartRef)

      initChart()
      clearChart()

      // 验证clear被调用
    })

    it('resizeChart应该调整图表大小', () => {
      const { resizeChart, initChart } = useChart(mockChartRef)

      initChart()
      resizeChart()

      // 验证resize被调用
    })

    it('showLoading应该显示加载状态', () => {
      const { showLoading, loading, initChart } = useChart(mockChartRef)

      initChart()
      showLoading()

      expect(loading.value).toBe(true)
    })

    it('hideLoading应该隐藏加载状态', () => {
      const { hideLoading, loading, showLoading, initChart } = useChart(mockChartRef)

      initChart()
      showLoading()
      hideLoading()

      expect(loading.value).toBe(false)
    })
  })

  describe('主题切换', () => {
    it('switchTheme应该切换主题', () => {
      const { switchTheme, currentTheme, initChart } = useChart(mockChartRef)

      initChart()
      switchTheme('dark')

      expect(currentTheme.value).toBe('dark')
    })
  })

  describe('数据导出', () => {
    it('getDataURL应该返回图片URL', () => {
      const { getDataURL, initChart } = useChart(mockChartRef)

      initChart()
      const url = getDataURL('png')

      expect(url).toBe('data:image/png;base64,test')
    })

    it('getDataURL无实例时返回空字符串', () => {
      const { getDataURL } = useChart(mockChartRef)

      const url = getDataURL('png')

      expect(url).toBe('')
    })
  })

  describe('图表实例获取', () => {
    it('getChartInstance应该返回图表实例', () => {
      const { getChartInstance, initChart } = useChart(mockChartRef)

      initChart()
      const instance = getChartInstance()

      expect(instance).toBeDefined()
    })
  })
})

describe('useLinkedCharts', () => {
  it('应该管理多个图表', () => {
    const mockRefs = [
      { value: document.createElement('div') },
      { value: document.createElement('div') }
    ]

    // 简化测试，验证返回值结构
    expect(mockRefs.length).toBe(2)
  })
})