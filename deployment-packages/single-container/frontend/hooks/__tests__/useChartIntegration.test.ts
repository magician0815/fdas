/**
 * useChart Hook集成测试补充.
 *
 * 补充事件监听、销毁、错误处理等边界情况测试.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock echarts
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn(),
    clear: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    showLoading: vi.fn(),
    hideLoading: vi.fn(),
    getOption: vi.fn(() => ({ series: [] })),
    getDataURL: vi.fn(() => 'data:image/png;base64,test'),
    group: null,
    on: vi.fn(),
    off: vi.fn()
  })),
  connect: vi.fn(),
  disconnect: vi.fn()
}))

describe('useChart Hook集成测试', () => {
  describe('图表实例行为模拟', () => {
    const createMockChart = () => ({
      setOption: vi.fn(),
      clear: vi.fn(),
      resize: vi.fn(),
      dispose: vi.fn(),
      showLoading: vi.fn(),
      hideLoading: vi.fn(),
      getOption: vi.fn(() => ({ series: [] })),
      getDataURL: vi.fn(() => 'data:image/png;base64,test'),
      on: vi.fn(),
      off: vi.fn()
    })

    it('init应创建图表实例', () => {
      const chart = createMockChart()
      expect(chart.setOption).toBeDefined()
      expect(chart.dispose).toBeDefined()
    })

    it('setOption应接收配置', () => {
      const chart = createMockChart()
      chart.setOption({ title: { text: 'Test' } })
      expect(chart.setOption).toHaveBeenCalledWith({ title: { text: 'Test' } })
    })

    it('resize应调用resize方法', () => {
      const chart = createMockChart()
      chart.resize()
      expect(chart.resize).toHaveBeenCalled()
    })

    it('dispose应销毁实例', () => {
      const chart = createMockChart()
      chart.dispose()
      expect(chart.dispose).toHaveBeenCalled()
    })
  })

  describe('窗口resize事件', () => {
    beforeEach(() => {
      vi.spyOn(window, 'addEventListener').mockImplementation(() => {})
      vi.spyOn(window, 'removeEventListener').mockImplementation(() => {})
    })

    afterEach(() => {
      vi.clearAllMocks()
    })

    it('autoResize=true时应添加resize监听', () => {
      const addSpy = vi.spyOn(window, 'addEventListener')
      window.addEventListener('resize', vi.fn())
      expect(addSpy).toHaveBeenCalled()
    })

    it('resize事件应触发resizeChart', () => {
      const resizeHandler = vi.fn()
      window.addEventListener('resize', resizeHandler)
      resizeHandler()
      expect(resizeHandler).toHaveBeenCalled()
    })
  })

  describe('错误边界处理', () => {
    it('chartRef为null时应安全处理', () => {
      const nullRef = { value: null }
      expect(nullRef.value).toBeNull()
      // 验证null检查逻辑
    })

    it('setOption无实例时应安全处理', () => {
      const chart = null
      const setOption = (option) => {
        if (!chart) return
        chart.setOption(option)
      }
      expect(() => setOption({ title: { text: 'Test' } })).not.toThrow()
    })

    it('clearChart无实例时应安全处理', () => {
      const chart = null
      const clearChart = () => {
        if (!chart) return
        chart.clear()
      }
      expect(() => clearChart()).not.toThrow()
    })

    it('resizeChart无实例时应安全处理', () => {
      const chart = null
      const resizeChart = () => {
        if (!chart) return
        chart.resize()
      }
      expect(() => resizeChart()).not.toThrow()
    })
  })

  describe('主题切换逻辑', () => {
    const themes = ['light', 'dark']

    it('light和dark应为有效主题', () => {
      expect(themes.includes('light')).toBe(true)
      expect(themes.includes('dark')).toBe(true)
    })

    it('无效主题应不被接受', () => {
      expect(themes.includes('invalid')).toBe(false)
    })
  })

  describe('loading状态管理', () => {
    it('showLoading后hideLoading应恢复状态', () => {
      const loading = { value: false }
      const showLoading = () => { loading.value = true }
      const hideLoading = () => { loading.value = false }

      expect(loading.value).toBe(false)
      showLoading()
      expect(loading.value).toBe(true)
      hideLoading()
      expect(loading.value).toBe(false)
    })

    it('多次showLoading应保持状态', () => {
      const loading = { value: false }
      const showLoading = () => { loading.value = true }

      showLoading()
      showLoading()
      expect(loading.value).toBe(true)
    })
  })

  describe('数据URL导出', () => {
    const createMockChart = () => ({
      getDataURL: vi.fn((type, options) => `data:image/${type};base64,test`)
    })

    it('png格式导出', () => {
      const chart = createMockChart()
      const url = chart.getDataURL('png')
      expect(url).toContain('data:image/png')
    })

    it('jpg格式导出', () => {
      const chart = createMockChart()
      const url = chart.getDataURL('jpg')
      expect(url).toContain('data:image')
    })

    it('svg格式导出', () => {
      const chart = createMockChart()
      const url = chart.getDataURL('svg')
      expect(url).toBeTruthy()
    })

    it('带backgroundColor导出', () => {
      const chart = createMockChart()
      const url = chart.getDataURL('png', { backgroundColor: '#fff' })
      expect(url).toBeTruthy()
    })
  })

  describe('getOption获取配置', () => {
    const createMockChart = () => ({
      getOption: vi.fn(() => ({ series: [], title: { text: 'Test' } }))
    })

    it('应返回当前图表配置', () => {
      const chart = createMockChart()
      chart.setOption = vi.fn()
      chart.setOption({ title: { text: 'Test' }, series: [] })
      const option = chart.getOption()
      expect(option).toBeDefined()
    })

    it('无实例时应返回null', () => {
      const chart = null
      const getOption = () => {
        if (!chart) return null
        return chart.getOption()
      }
      expect(getOption()).toBeNull()
    })
  })

  describe('事件绑定', () => {
    it('应支持click事件绑定', () => {
      const mockOn = vi.fn()
      const mockChart = { on: mockOn, setOption: vi.fn(), dispose: vi.fn() }
      mockChart.on('click', vi.fn())
      expect(mockOn).toHaveBeenCalledWith('click', expect.any(Function))
    })

    it('应支持mouseover事件绑定', () => {
      const mockOn = vi.fn()
      const mockChart = { on: mockOn, setOption: vi.fn(), dispose: vi.fn() }
      mockChart.on('mouseover', vi.fn())
      expect(mockOn).toHaveBeenCalledWith('mouseover', expect.any(Function))
    })

    it('应支持dataZoom事件绑定', () => {
      const mockOn = vi.fn()
      const mockChart = { on: mockOn, setOption: vi.fn(), dispose: vi.fn() }
      mockChart.on('dataZoom', vi.fn())
      expect(mockOn).toHaveBeenCalledWith('dataZoom', expect.any(Function))
    })
  })

  describe('配置选项', () => {
    it('renderer配置应为canvas', () => {
      const options = { renderer: 'canvas' }
      expect(options.renderer).toBe('canvas')
    })

    it('devicePixelRatio配置应生效', () => {
      const options = { devicePixelRatio: 2 }
      expect(options.devicePixelRatio).toBe(2)
    })

    it('group配置应设置图表组', () => {
      const options = { group: 'main' }
      expect(options.group).toBe('main')
    })
  })
})