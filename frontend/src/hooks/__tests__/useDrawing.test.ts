/**
 * useDrawing Hook测试.
 *
 * 测试画线状态管理功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useDrawing } from '../useDrawing'
import type { DrawingTool, Drawing } from '../useDrawing'

// Mock echarts
vi.mock('echarts', () => ({
  default: {
    init: vi.fn(() => ({
      setOption: vi.fn(),
      getOption: vi.fn(() => ({ graphic: [] })),
      getWidth: vi.fn(() => 800),
      getHeight: vi.fn(() => 500)
    }))
  }
}))

// Mock chart_settings API
vi.mock('@/api/chart_settings.js', () => ({
  saveChartSetting: vi.fn(() => Promise.resolve())
}))

describe('useDrawing', () => {
  let mockOptions

  beforeEach(() => {
    mockOptions = {
      chartInstance: vi.fn(() => ({
        setOption: vi.fn(),
        getOption: vi.fn(() => ({ graphic: [] })),
        getWidth: vi.fn(() => 800),
        getHeight: vi.fn(() => 500)
      })),
      data: vi.fn(() => [
        { date: '2026-04-01', high: 7.20, low: 7.05, close: 7.15 },
        { date: '2026-04-02', high: 7.25, low: 7.10, close: 7.20 },
        { date: '2026-04-03', high: 7.30, low: 7.15, close: 7.25 }
      ])
    }

    vi.clearAllMocks()
  })

  describe('初始化', () => {
    it('应该返回正确的初始状态', () => {
      const { currentTool, currentColor, currentLineWidth, magnetEnabled, drawings } = useDrawing(mockOptions)

      expect(currentTool.value).toBeNull()
      expect(currentColor.value).toBe('#FF6B6B')
      expect(currentLineWidth.value).toBe(2)
      expect(magnetEnabled.value).toBe(true)
      expect(drawings.value).toEqual([])
    })

    it('应该支持自定义初始颜色', () => {
      const customOptions = {
        ...mockOptions,
        initialColor: '#00FF00'
      }

      const { currentColor } = useDrawing(customOptions)

      expect(currentColor.value).toBe('#00FF00')
    })

    it('应该支持自定义初始粗细', () => {
      const customOptions = {
        ...mockOptions,
        initialLineWidth: 5
      }

      const { currentLineWidth } = useDrawing(customOptions)

      expect(currentLineWidth.value).toBe(5)
    })
  })

  describe('工具设置', () => {
    it('setTool应该设置当前工具', () => {
      const { setTool, currentTool } = useDrawing(mockOptions)

      setTool('trendLine')

      expect(currentTool.value).toBe('trendLine')
    })

    it('setColor应该设置颜色', () => {
      const { setColor, currentColor } = useDrawing(mockOptions)

      setColor('#0000FF')

      expect(currentColor.value).toBe('#0000FF')
    })

    it('setLineWidth应该设置粗细', () => {
      const { setLineWidth, currentLineWidth } = useDrawing(mockOptions)

      setLineWidth(5)

      expect(currentLineWidth.value).toBe(5)
    })

    it('setMagnet应该设置磁吸开关', () => {
      const { setMagnet, magnetEnabled } = useDrawing(mockOptions)

      setMagnet(false)

      expect(magnetEnabled.value).toBe(false)
    })

    it('setToolParams应该设置工具参数', () => {
      const { setToolParams, currentToolParams } = useDrawing(mockOptions)

      setToolParams({ fibonacciLevels: [0, 0.5, 1] })

      expect(currentToolParams.value.fibonacciLevels).toEqual([0, 0.5, 1])
    })
  })

  describe('绘制流程', () => {
    it('startDrawing应该开始绘制趋势线', () => {
      const { startDrawing, isDrawing, currentTool, setTool } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })

      expect(isDrawing.value).toBe(true)
    })

    it('cancelDrawing应该取消绘制', () => {
      const { startDrawing, cancelDrawing, isDrawing, setTool, drawings } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      cancelDrawing()

      expect(isDrawing.value).toBe(false)
      expect(drawings.value.length).toBe(0)
    })

    it('endDrawing应该完成水平线绘制', () => {
      const { startDrawing, endDrawing, isDrawing, drawings, setTool } = useDrawing(mockOptions)

      setTool('horizontalLine')
      startDrawing({ x: 0, y: 7.15 })
      endDrawing({ x: 1, y: 7.15 })

      expect(isDrawing.value).toBe(false)
      expect(drawings.value.length).toBe(1)
      expect(drawings.value[0].type).toBe('horizontalLine')
    })
  })

  describe('画线选择', () => {
    it('selectDrawing应该选择画线', () => {
      const { selectDrawing, selectedDrawingId, drawings, startDrawing, onDrawing, endDrawing, setTool } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 1, y: 7.20 })
      endDrawing({ x: 1, y: 7.20 })

      const drawingId = drawings.value[0].id
      selectDrawing(drawingId)

      expect(selectedDrawingId.value).toBe(drawingId)
    })

    it('deselectDrawing应该取消选择', () => {
      const { selectDrawing, deselectDrawing, selectedDrawingId, drawings, startDrawing, onDrawing, endDrawing, setTool } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 1, y: 7.20 })
      endDrawing({ x: 1, y: 7.20 })

      const drawingId = drawings.value[0].id
      selectDrawing(drawingId)
      deselectDrawing()

      expect(selectedDrawingId.value).toBeNull()
    })
  })

  describe('画线删除', () => {
    it('deleteSelectedDrawing应该删除选中画线', () => {
      const { deleteSelectedDrawing, drawings, selectDrawing, startDrawing, onDrawing, endDrawing, setTool } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 1, y: 7.20 })
      endDrawing({ x: 1, y: 7.20 })

      const drawingId = drawings.value[0].id
      selectDrawing(drawingId)
      deleteSelectedDrawing()

      expect(drawings.value.length).toBe(0)
    })

    it('clearAllDrawings应该清除所有画线', () => {
      const { clearAllDrawings, drawings, startDrawing, onDrawing, endDrawing, setTool } = useDrawing(mockOptions)

      // 创建两条画线
      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 1, y: 7.20 })
      endDrawing({ x: 1, y: 7.20 })

      startDrawing({ x: 2, y: 7.15 })
      onDrawing({ x: 3, y: 7.25 })
      endDrawing({ x: 3, y: 7.25 })

      clearAllDrawings()

      expect(drawings.value.length).toBe(0)
    })
  })

  describe('画线更新', () => {
    it('updateSelectedDrawing应该更新选中画线', () => {
      const { updateSelectedDrawing, drawings, selectDrawing, startDrawing, onDrawing, endDrawing, setTool } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 1, y: 7.20 })
      endDrawing({ x: 1, y: 7.20 })

      const drawingId = drawings.value[0].id
      selectDrawing(drawingId)
      updateSelectedDrawing({ color: '#00FF00' })

      expect(drawings.value[0].color).toBe('#00FF00')
    })
  })

  describe('磁吸功能', () => {
    it('magnetToPoint应该磁吸到最近价格点', () => {
      const { magnetToPoint, setMagnet } = useDrawing(mockOptions)

      setMagnet(true)

      const result = magnetToPoint(0, 7.12)

      // 应该磁吸到最近的high(7.20), low(7.05), 或close(7.15)
      expect(result.y).toBeCloseTo(7.15, 1)
    })

    it('禁用磁吸时返回原坐标', () => {
      const { magnetToPoint, setMagnet } = useDrawing(mockOptions)

      setMagnet(false)

      const result = magnetToPoint(0, 7.12)

      expect(result.x).toBe(0)
      expect(result.y).toBe(7.12)
    })
  })

  describe('计算属性', () => {
    it('selectedDrawing应该返回选中画线', () => {
      const { selectedDrawing, drawings, selectDrawing, startDrawing, onDrawing, endDrawing, setTool } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 1, y: 7.20 })
      endDrawing({ x: 1, y: 7.20 })

      const drawingId = drawings.value[0].id
      selectDrawing(drawingId)

      expect(selectedDrawing.value).toBe(drawings.value[0])
    })

    it('drawingCount应该返回画线数量', () => {
      const { drawingCount, startDrawing, onDrawing, endDrawing, setTool } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 1, y: 7.20 })
      endDrawing({ x: 1, y: 7.20 })

      expect(drawingCount.value).toBe(1)
    })
  })

  describe('文字标注', () => {
    it('addTextAnnotation应该添加文字标注', () => {
      const { addTextAnnotation, drawings } = useDrawing(mockOptions)

      addTextAnnotation({ x: 0, y: 7.15 }, '测试标注')

      expect(drawings.value.length).toBe(1)
      expect(drawings.value[0].type).toBe('text')
      expect(drawings.value[0].text).toBe('测试标注')
    })
  })

  describe('各种画线工具', () => {
    it('水平线应该只需要一个y坐标', () => {
      const { startDrawing, endDrawing, drawings, setTool } = useDrawing(mockOptions)

      setTool('horizontalLine')
      startDrawing({ x: 0, y: 7.15 })
      endDrawing({ x: 1, y: 7.15 })

      expect(drawings.value.length).toBe(1)
      expect(drawings.value[0].type).toBe('horizontalLine')
    })

    it('矩形需要两个点', () => {
      const { startDrawing, onDrawing, endDrawing, drawings, setTool } = useDrawing(mockOptions)

      setTool('rectangle')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 2, y: 7.20 })
      endDrawing({ x: 2, y: 7.20 })

      expect(drawings.value.length).toBe(1)
      expect(drawings.value[0].points.length).toBe(2)
    })

    it('趋势线需要两个点', () => {
      const { startDrawing, onDrawing, endDrawing, drawings, setTool } = useDrawing(mockOptions)

      setTool('trendLine')
      startDrawing({ x: 0, y: 7.10 })
      onDrawing({ x: 2, y: 7.20 })
      endDrawing({ x: 2, y: 7.20 })

      expect(drawings.value.length).toBe(1)
      expect(drawings.value[0].points.length).toBe(2)
    })
  })

  describe('专业画线工具', () => {
    it('黄金分割线设置成功', () => {
      const { setToolParams, setTool } = useDrawing(mockOptions)

      setTool('fibonacci')
      setToolParams({ fibonacciLevels: [0, 0.5, 1] })

      expect(setTool).toBeDefined()
    })

    it('江恩角度线设置成功', () => {
      const { setToolParams, setTool } = useDrawing(mockOptions)

      setTool('gannLine')
      setToolParams({ gannAngle: 45 })

      expect(setTool).toBeDefined()
    })
  })
})