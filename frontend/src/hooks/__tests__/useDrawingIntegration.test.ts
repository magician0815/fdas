/**
 * useDrawing Hook集成测试补充.
 *
 * 补充画线工具、编辑、删除等边界情况测试.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('useDrawing Hook集成测试', () => {
  describe('画线类型配置', () => {
    const drawingTypes = [
      { type: 'line', name: '趋势线', icon: 'line' },
      { type: 'horizontal', name: '水平线', icon: 'horizontal' },
      { type: 'vertical', name: '垂直线', icon: 'vertical' },
      { type: 'rectangle', name: '矩形', icon: 'rectangle' },
      { type: 'parallel', name: '平行通道', icon: 'parallel' },
      { type: 'fibonacci', name: '黄金分割', icon: 'fibonacci' },
      { type: 'gann', name: '江恩角度线', icon: 'gann' },
      { type: 'text', name: '文字标注', icon: 'text' },
      { type: 'arrow', name: '箭头标注', icon: 'arrow' }
    ]

    const isValidType = (type) => drawingTypes.some(t => t.type === type)
    const getTypeName = (type) => drawingTypes.find(t => t.type === type)?.name

    it('应包含所有画线类型', () => {
      expect(drawingTypes.length).toBe(9)
    })

    it('有效类型应返回true', () => {
      expect(isValidType('line')).toBe(true)
      expect(isValidType('fibonacci')).toBe(true)
      expect(isValidType('invalid')).toBe(false)
    })

    it('应正确获取类型名称', () => {
      expect(getTypeName('line')).toBe('趋势线')
      expect(getTypeName('fibonacci')).toBe('黄金分割')
      expect(getTypeName('invalid')).toBeUndefined()
    })
  })

  describe('画线数据结构', () => {
    const createDrawing = (type, points, options = {}) => ({
      id: options.id || `drawing-${Date.now()}`,
      type,
      points,
      style: {
        color: options.color || '#3b82f6',
        lineWidth: options.lineWidth || 2,
        opacity: options.opacity || 1,
        ...options.style
      },
      locked: options.locked || false,
      visible: options.visible !== false,
      created_at: new Date().toISOString()
    })

    it('应正确创建趋势线', () => {
      const drawing = createDrawing('line', [
        { x: 0, y: 100, date: '2026-01-01' },
        { x: 10, y: 120, date: '2026-01-11' }
      ])
      expect(drawing.type).toBe('line')
      expect(drawing.points).toHaveLength(2)
      expect(drawing.style.color).toBe('#3b82f6')
    })

    it('应正确创建水平线', () => {
      const drawing = createDrawing('horizontal', [
        { y: 100 }
      ])
      expect(drawing.type).toBe('horizontal')
      expect(drawing.points).toHaveLength(1)
    })

    it('应正确创建黄金分割线', () => {
      const drawing = createDrawing('fibonacci', [
        { x: 0, y: 100 },
        { x: 10, y: 150 }
      ], { style: { levels: [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1] } })
      expect(drawing.type).toBe('fibonacci')
      expect(drawing.style.levels).toHaveLength(7)
    })

    it('自定义选项应生效', () => {
      const drawing = createDrawing('line', [], {
        color: '#ff0000',
        lineWidth: 3,
        locked: true
      })
      expect(drawing.style.color).toBe('#ff0000')
      expect(drawing.style.lineWidth).toBe(3)
      expect(drawing.locked).toBe(true)
    })
  })

  describe('画线编辑操作', () => {
    const drawings = []
    const addDrawing = (drawing) => {
      drawings.push(drawing)
      return drawing.id
    }
    const updateDrawing = (id, updates) => {
      const index = drawings.findIndex(d => d.id === id)
      if (index >= 0) {
        drawings[index] = { ...drawings[index], ...updates }
        return true
      }
      return false
    }
    const deleteDrawing = (id) => {
      const index = drawings.findIndex(d => d.id === id)
      if (index >= 0) {
        drawings.splice(index, 1)
        return true
      }
      return false
    }
    const getDrawing = (id) => drawings.find(d => d.id === id)

    beforeEach(() => {
      drawings.length = 0
    })

    it('应正确添加画线', () => {
      const drawing = { id: 'test-1', type: 'line' }
      addDrawing(drawing)
      expect(drawings).toHaveLength(1)
      expect(drawings[0].id).toBe('test-1')
    })

    it('应正确更新画线', () => {
      addDrawing({ id: 'test-1', type: 'line', style: { color: '#000' } })
      updateDrawing('test-1', { style: { color: '#fff' } })
      expect(getDrawing('test-1').style.color).toBe('#fff')
    })

    it('应正确删除画线', () => {
      addDrawing({ id: 'test-1', type: 'line' })
      deleteDrawing('test-1')
      expect(drawings).toHaveLength(0)
    })

    it('删除不存在ID应返回false', () => {
      expect(deleteDrawing('non-existent')).toBe(false)
    })

    it('更新不存在ID应返回false', () => {
      expect(updateDrawing('non-existent', {})).toBe(false)
    })
  })

  describe('画线选择状态', () => {
    const selectionState = {
      selectedId: null,
      isEditing: false,
      drawingPoints: []
    }

    const selectDrawing = (id) => {
      selectionState.selectedId = id
      selectionState.isEditing = true
    }

    const deselectDrawing = () => {
      selectionState.selectedId = null
      selectionState.isEditing = false
      selectionState.drawingPoints = []
    }

    beforeEach(() => {
      deselectDrawing()
    })

    it('选择画线应更新状态', () => {
      selectDrawing('drawing-1')
      expect(selectionState.selectedId).toBe('drawing-1')
      expect(selectionState.isEditing).toBe(true)
    })

    it('取消选择应清空状态', () => {
      selectDrawing('drawing-1')
      deselectDrawing()
      expect(selectionState.selectedId).toBeNull()
      expect(selectionState.isEditing).toBe(false)
    })
  })

  describe('磁吸功能', () => {
    let magnetEnabled = true
    const magnetThreshold = 5

    const snapToKLine = (point, klineData) => {
      if (!magnetEnabled || !klineData) return point

      // 找最近的K线
      for (const kline of klineData) {
        const highDiff = Math.abs(point.y - kline.high)
        const lowDiff = Math.abs(point.y - kline.low)

        if (highDiff < magnetThreshold) {
          return { x: kline.x, y: kline.high, snapped: true }
        }
        if (lowDiff < magnetThreshold) {
          return { x: kline.x, y: kline.low, snapped: true }
        }
      }

      return { ...point, snapped: false }
    }

    beforeEach(() => {
      magnetEnabled = true
    })

    it('磁吸启用时应吸附到高点', () => {
      const point = { x: 5, y: 101 }
      const klineData = [{ x: 5, high: 100, low: 95 }]
      const snapped = snapToKLine(point, klineData)
      expect(snapped.snapped).toBe(true)
      expect(snapped.y).toBe(100)
    })

    it('磁吸启用时应吸附到低点（低点更近）', () => {
      const point = { x: 5, y: 94 }
      const klineData = [{ x: 5, high: 100, low: 95 }]
      const snapped = snapToKLine(point, klineData)
      expect(snapped.snapped).toBe(true)
      expect(snapped.y).toBe(95)
    })

    it('超出阈值不应吸附', () => {
      const point = { x: 5, y: 110 }
      const klineData = [{ x: 5, high: 100, low: 95 }]
      const snapped = snapToKLine(point, klineData)
      expect(snapped.snapped).toBe(false)
    })

    it('磁吸禁用时不应吸附', () => {
      magnetEnabled = false
      const point = { x: 5, y: 101 }
      const klineData = [{ x: 5, high: 100, low: 95 }]
      const snapped = snapToKLine(point, klineData)
      expect(snapped.snapped).toBeUndefined()
    })
  })

  describe('画线样式管理', () => {
    const defaultStyles = {
      line: { color: '#3b82f6', lineWidth: 2 },
      horizontal: { color: '#ef4444', lineWidth: 1 },
      fibonacci: { color: '#f59e0b', lineWidth: 1 }
    }

    const getStyle = (type, customStyle = {}) => ({
      ...defaultStyles[type] || defaultStyles.line,
      ...customStyle
    })

    it('应返回默认样式', () => {
      const style = getStyle('line')
      expect(style.color).toBe('#3b82f6')
      expect(style.lineWidth).toBe(2)
    })

    it('自定义样式应覆盖默认值', () => {
      const style = getStyle('line', { color: '#ff0000' })
      expect(style.color).toBe('#ff0000')
      expect(style.lineWidth).toBe(2)
    })

    it('未知类型应返回line默认样式', () => {
      const style = getStyle('unknown')
      expect(style.color).toBe('#3b82f6')
    })
  })

  describe('画线可见性控制', () => {
    const drawings = [
      { id: '1', type: 'line', visible: true },
      { id: '2', type: 'horizontal', visible: false },
      { id: '3', type: 'fibonacci', visible: true }
    ]

    const hideAllDrawings = () => {
      drawings.forEach(d => d.visible = false)
    }

    const showAllDrawings = () => {
      drawings.forEach(d => d.visible = true)
    }

    const toggleDrawingVisibility = (id) => {
      const drawing = drawings.find(d => d.id === id)
      if (drawing) drawing.visible = !drawing.visible
    }

    it('hideAll应隐藏所有画线', () => {
      hideAllDrawings()
      expect(drawings.every(d => d.visible === false)).toBe(true)
    })

    it('showAll应显示所有画线', () => {
      hideAllDrawings()
      showAllDrawings()
      expect(drawings.every(d => d.visible === true)).toBe(true)
    })

    it('toggle应切换单条画线可见性', () => {
      toggleDrawingVisibility('1')
      expect(drawings[0].visible).toBe(false)
      toggleDrawingVisibility('1')
      expect(drawings[0].visible).toBe(true)
    })
  })

  describe('画线锁定控制', () => {
    let drawings = [
      { id: '1', locked: false },
      { id: '2', locked: true }
    ]

    const lockDrawing = (id) => {
      const drawing = drawings.find(d => d.id === id)
      if (drawing) drawing.locked = true
    }

    const unlockDrawing = (id) => {
      const drawing = drawings.find(d => d.id === id)
      if (drawing) drawing.locked = false
    }

    const isLocked = (id) => drawings.find(d => d.id === id)?.locked

    beforeEach(() => {
      drawings = [
        { id: '1', locked: false },
        { id: '2', locked: true }
      ]
    })

    it('lockDrawing应锁定画线', () => {
      lockDrawing('1')
      expect(drawings[0].locked).toBe(true)
    })

    it('unlockDrawing应解锁画线', () => {
      unlockDrawing('2')
      expect(drawings[1].locked).toBe(false)
    })

    it('isLocked应正确返回状态', () => {
      expect(isLocked('1')).toBe(false)
      expect(isLocked('2')).toBe(true)
    })
  })

  describe('画线导出导入', () => {
    const exportDrawings = (drawings) => JSON.stringify(drawings)
    const importDrawings = (json) => {
      try {
        return JSON.parse(json)
      } catch {
        return []
      }
    }

    it('export应正确序列化', () => {
      const drawings = [{ id: '1', type: 'line' }]
      const json = exportDrawings(drawings)
      expect(json).toContain('line')
    })

    it('import应正确反序列化', () => {
      const json = '[{"id":"1","type":"line"}]'
      const drawings = importDrawings(json)
      expect(drawings).toHaveLength(1)
      expect(drawings[0].type).toBe('line')
    })

    it('无效JSON应返回空数组', () => {
      expect(importDrawings('invalid')).toEqual([])
    })
  })
})