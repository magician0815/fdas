/**
 * 画线状态管理Hook.
 *
 * 管理图表画线数据、工具状态、绘制逻辑.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, computed, watch } from 'vue'
import * as echarts from 'echarts'
import { saveChartSetting } from '@/api/chart_settings.js'
import logger from '@/services/logger'

// 画线类型定义（基础 + 专业画线工具）
export type DrawingTool =
  | 'line'            // 直线（点击两点画线）
  | 'trendLine'        // 趋势线（拖拽画线）
  | 'horizontalLine'   // 水平线
  | 'verticalLine'     // 垂直线
  | 'rectangle'        // 矩形（点击两点画框）
  | 'text'             // 文字标注
  | 'arrowUp'          // 向上箭头
  | 'arrowDown'        // 向下箭头
  | 'fibonacci'        // 黄金分割线
  | 'gannLine'         // 江恩角度线
  | 'pitchfork'        // 安德鲁音叉线
  | 'fibonacciFan'     // 斐波那契扇形线
  | 'parallelChannel'  // 平行通道线
  | 'waveMark'         // 波浪线标注
  | null

// 画线数据结构
export interface Drawing {
  id: string
  type: DrawingTool
  points: Array<{ x: number; y: number }>
  color: string
  lineWidth: number
  text?: string  // 文字标注内容
  params?: {     // 专业画线工具参数
    fibonacciLevels?: number[]  // 黄金分割比例（默认[0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]）
    gannAngle?: number          // 江恩角度（默认45度）
    channelWidth?: number       // 通道宽度比例
    waveLevel?: number          // 波浪级别
  }
  createdAt: number
}

// Hook配置
export interface UseDrawingOptions {
  chartInstance: () => echarts.ECharts | null
  data: () => Array<{ date: string; high: number; low: number; close: number }>
  initialColor?: string
  initialLineWidth?: number
  initialMagnet?: boolean
}

/**
 * 画线状态管理Hook.
 */
export function useDrawing(options: UseDrawingOptions) {
  // 当前工具
  const currentTool = ref<DrawingTool>(null)
  // 当前颜色
  const currentColor = ref<string>(options.initialColor || '#FF6B6B')
  // 当前粗细
  const currentLineWidth = ref<number>(options.initialLineWidth || 4)
  // 磁吸开关
  const magnetEnabled = ref<boolean>(options.initialMagnet || true)
  // 当前工具参数
  const currentToolParams = ref<Record<string, any>>({})
  // 所有画线数据
  const drawings = ref<Drawing[]>([])
  // 当前正在绘制的画线
  const activeDrawing = ref<Drawing | null>(null)
  // 是否正在绘制
  const isDrawing = ref<boolean>(false)
  // 选中的画线ID
  const selectedDrawingId = ref<string | null>(null)
  // 绘制临时点位
  const tempPoints = ref<Array<{ x: number; y: number }>>([])
  // 点击-点击模式：第一个点击点（用于line和rectangle的点击两次画线）
  const firstClickPoint = ref<{ x: number; y: number } | null>(null)
  // 是否等待第二次点击
  const waitingForSecondClick = ref<boolean>(false)

  // 计算属性：选中的画线
  const selectedDrawing = computed(() => {
    if (!selectedDrawingId.value) return null
    return drawings.value.find(d => d.id === selectedDrawingId.value)
  })

  // 计算属性：画线数量
  const drawingCount = computed(() => drawings.value.length)

  /**
   * 生成唯一ID.
   */
  const generateId = () => `drawing_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

  /**
   * 磁吸到最近的K线价格点.
   */
  const magnetToPoint = (x: number, y: number): { x: number; y: number } => {
    if (!magnetEnabled.value) return { x, y }

    const data = options.data()
    if (!data || !data.length) return { x, y }

    // 找到最近的K线索引
    const dataIndex = Math.round(x)
    if (dataIndex < 0 || dataIndex >= data.length) return { x, y }

    const candle = data[dataIndex]
    const high = parseFloat(candle.high as any)
    const low = parseFloat(candle.low as any)
    const close = parseFloat(candle.close as any)

    // 判断y更接近high还是low
    const distanceToHigh = Math.abs(y - high)
    const distanceToLow = Math.abs(y - low)
    const distanceToClose = Math.abs(y - close)

    // 磁吸到最近的价格点
    if (distanceToHigh <= distanceToLow && distanceToHigh <= distanceToClose) {
      return { x: dataIndex, y: high }
    } else if (distanceToLow <= distanceToClose) {
      return { x: dataIndex, y: low }
    } else {
      return { x: dataIndex, y: close }
    }
  }

  /**
   * 开始绘制.
   * 对于line和rectangle使用点击-点击模式，其他工具使用拖拽模式.
   */
  const startDrawing = (point: { x: number; y: number }) => {
    if (!currentTool.value) return

    // 磁吸处理
    const magnetPoint = magnetToPoint(point.x, point.y)

    // 点击-点击模式的工具（line, rectangle）
    if (currentTool.value === 'line' || currentTool.value === 'rectangle') {
      if (!waitingForSecondClick.value) {
        // 第一次点击：记录起点，等待第二次点击
        firstClickPoint.value = magnetPoint
        waitingForSecondClick.value = true
        tempPoints.value = [magnetPoint]

        // 创建临时画线对象用于预览
        activeDrawing.value = {
          id: generateId(),
          type: currentTool.value,
          points: [magnetPoint],
          color: currentColor.value,
          lineWidth: currentLineWidth.value,
          params: currentToolParams.value,
          createdAt: Date.now()
        }
        isDrawing.value = true
      }
      return
    }

    // 拖拽模式的工具
    isDrawing.value = true
    tempPoints.value = []

    tempPoints.value.push(magnetPoint)

    // 创建临时画线对象（包含工具参数）
    activeDrawing.value = {
      id: generateId(),
      type: currentTool.value,
      points: tempPoints.value,
      color: currentColor.value,
      lineWidth: currentLineWidth.value,
      params: currentToolParams.value,
      createdAt: Date.now()
    }
  }

  /**
   * 绘制过程（鼠标移动）.
   * 用于显示预览线和处理第二次点击.
   */
  const onDrawing = (point: { x: number; y: number }) => {
    if (!currentTool.value) return

    // 磁吸处理
    const magnetPoint = magnetToPoint(point.x, point.y)

    // 点击-点击模式：显示预览
    if (waitingForSecondClick.value && firstClickPoint.value) {
      if (currentTool.value === 'line' || currentTool.value === 'rectangle') {
        // 更新临时画线的第二个点用于预览
        tempPoints.value = [firstClickPoint.value, magnetPoint]
        if (activeDrawing.value) {
          activeDrawing.value.points = [...tempPoints.value]
        }
        renderActiveDrawing()
      }
      return
    }

    if (!isDrawing.value) return

    // 根据工具类型处理（拖拽模式）
    if (currentTool.value === 'horizontalLine') {
      // 水平线只需要一个y坐标
      tempPoints.value = [{ x: 0, y: magnetPoint.y }]
    } else if (currentTool.value === 'verticalLine') {
      // 垂直线只需要一个x坐标
      tempPoints.value = [{ x: magnetPoint.x, y: 0 }]
    } else if (currentTool.value === 'trendLine') {
      // 趋势线需要两个点
      if (tempPoints.value.length === 1) {
        tempPoints.value = [tempPoints.value[0], magnetPoint]
      } else {
        tempPoints.value[1] = magnetPoint
      }
    } else if (currentTool.value === 'fibonacci' || currentTool.value === 'fibonacciFan' || currentTool.value === 'parallelChannel') {
      // 黄金分割线、斐波那契扇形线、平行通道需要两个点
      if (tempPoints.value.length === 1) {
        tempPoints.value = [tempPoints.value[0], magnetPoint]
      } else {
        tempPoints.value[1] = magnetPoint
      }
    } else if (currentTool.value === 'gannLine') {
      // 江恩角度线只需要一个点作为起点
      tempPoints.value = [magnetPoint]
    } else if (currentTool.value === 'pitchfork') {
      // 安德鲁音叉线需要三个点
      if (tempPoints.value.length < 3) {
        tempPoints.value.push(magnetPoint)
      } else {
        tempPoints.value[2] = magnetPoint
      }
    } else if (currentTool.value === 'waveMark') {
      // 波浪线标注支持多个点（最多8个波浪点）
      if (tempPoints.value.length < 8) {
        // 每次点击添加新的波浪点
        tempPoints.value.push(magnetPoint)
      }
    }

    // 更新临时画线
    if (activeDrawing.value) {
      activeDrawing.value.points = [...tempPoints.value]
    }

    // 渲染临时画线
    renderActiveDrawing()
  }

  /**
   * 处理第二次点击（完成画线）.
   */
  const handleSecondClick = (point: { x: number; y: number }) => {
    if (!waitingForSecondClick.value || !firstClickPoint.value || !currentTool.value) return

    // 磁吸处理
    const magnetPoint = magnetToPoint(point.x, point.y)

    // 完成画线
    const drawing: Drawing = {
      id: generateId(),
      type: currentTool.value,
      points: [firstClickPoint.value, magnetPoint],
      color: currentColor.value,
      lineWidth: currentLineWidth.value,
      params: currentToolParams.value,
      createdAt: Date.now()
    }

    drawings.value.push(drawing)
    renderDrawings()

    // 清理临时状态
    waitingForSecondClick.value = false
    firstClickPoint.value = null
    tempPoints.value = []
    activeDrawing.value = null
    isDrawing.value = false
    clearActiveDrawing()
  }

  /**
   * 结束绘制.
   * 对于点击-点击模式的工具，处理第二次点击.
   * 对于拖拽模式的工具，完成画线.
   */
  const endDrawing = (point?: { x: number; y: number }) => {
    // 点击-点击模式：处理第二次点击
    if (waitingForSecondClick.value && point) {
      handleSecondClick(point)
      return
    }

    if (!isDrawing.value) return

    // 如果有最终点，添加到临时点（拖拽模式）
    if (point) {
      const magnetPoint = magnetToPoint(point.x, point.y)

      if (currentTool.value === 'horizontalLine') {
        tempPoints.value = [{ x: 0, y: magnetPoint.y }]
      } else if (currentTool.value === 'verticalLine') {
        tempPoints.value = [{ x: magnetPoint.x, y: 0 }]
      } else if (currentTool.value === 'gannLine') {
        // 江恩角度线只需起点
        tempPoints.value = [magnetPoint]
      } else if (currentTool.value === 'waveMark') {
        // 波浪线标注每次点击添加点，不需要最后添加
      } else if (currentTool.value === 'pitchfork') {
        // 安德鲁音叉线需要3个点
        if (tempPoints.value.length < 3) {
          tempPoints.value.push(magnetPoint)
        }
      } else if (currentTool.value === 'trendLine') {
        // 趋势线需要2个点
        if (tempPoints.value.length === 1) {
          tempPoints.value.push(magnetPoint)
        } else if (tempPoints.value.length >= 2) {
          tempPoints.value[tempPoints.value.length - 1] = magnetPoint
        }
      } else {
        // 其他工具需要2个点
        if (tempPoints.value.length === 1) {
          tempPoints.value.push(magnetPoint)
        } else if (tempPoints.value.length >= 2) {
          tempPoints.value[tempPoints.value.length - 1] = magnetPoint
        }
      }
    }

    // 完成画线（检查是否满足各工具的最小点数要求）
    let minPoints = 1
    if (currentTool.value === 'trendLine' ||
        currentTool.value === 'fibonacci' || currentTool.value === 'fibonacciFan' ||
        currentTool.value === 'parallelChannel') {
      minPoints = 2
    } else if (currentTool.value === 'pitchfork') {
      minPoints = 3
    }

    if (activeDrawing.value && tempPoints.value.length >= minPoints) {
      activeDrawing.value.points = [...tempPoints.value]
      drawings.value.push(activeDrawing.value)
      renderDrawings()
    }

    // 清理临时状态
    isDrawing.value = false
    tempPoints.value = []
    activeDrawing.value = null
    waitingForSecondClick.value = false
    firstClickPoint.value = null
    clearActiveDrawing()
  }

  /**
   * 取消绘制.
   */
  const cancelDrawing = () => {
    isDrawing.value = false
    tempPoints.value = []
    activeDrawing.value = null
    waitingForSecondClick.value = false
    firstClickPoint.value = null
    clearActiveDrawing()
  }

  /**
   * 选择画线.
   */
  const selectDrawing = (id: string) => {
    selectedDrawingId.value = id
    highlightDrawing(id)
  }

  /**
   * 取消选择.
   */
  const deselectDrawing = () => {
    selectedDrawingId.value = null
    renderDrawings()
  }

  /**
   * 删除选中画线.
   */
  const deleteSelectedDrawing = () => {
    if (!selectedDrawingId.value) return

    drawings.value = drawings.value.filter(d => d.id !== selectedDrawingId.value)
    selectedDrawingId.value = null
    renderDrawings()
  }

  /**
   * 删除所有画线.
   */
  const clearAllDrawings = () => {
    drawings.value = []
    selectedDrawingId.value = null
    renderDrawings()
  }

  /**
   * 更新选中画线.
   */
  const updateSelectedDrawing = (updates: Partial<Drawing>) => {
    if (!selectedDrawing.value) return

    const index = drawings.value.findIndex(d => d.id === selectedDrawingId.value)
    if (index > -1) {
      drawings.value[index] = { ...drawings.value[index], ...updates }
      renderDrawings()
    }
  }

  /**
   * 移动选中画线的端点.
   */
  const moveDrawingPoint = (pointIndex: number, newPoint: { x: number; y: number }) => {
    if (!selectedDrawing.value) return

    const magnetPoint = magnetToPoint(newPoint.x, newPoint.y)
    const index = drawings.value.findIndex(d => d.id === selectedDrawingId.value)
    if (index > -1) {
      drawings.value[index].points[pointIndex] = magnetPoint
      renderDrawings()
    }
  }

  /**
   * 渲染所有画线到图表.
   */
  const renderDrawings = () => {
    const chart = options.chartInstance()
    if (!chart) return

    // 清除所有graphic元素
    const existingGraphics = chart.getOption().graphic || []
    const filteredGraphics = existingGraphics.filter(g => !g.id?.startsWith('drawing_'))

    // 构建新的graphic元素
    const graphicElements: any[] = [...filteredGraphics]

    for (const drawing of drawings.value) {
      const elements = convertDrawingToGraphic(drawing)
      graphicElements.push(...elements)
    }

    chart.setOption({ graphic: graphicElements }, { notMerge: false })
  }

  /**
   * 渲染临时画线.
   */
  const renderActiveDrawing = () => {
    if (!activeDrawing.value) return

    const chart = options.chartInstance()
    if (!chart) return

    // 清除临时画线
    clearActiveDrawing()

    // 添加临时画线
    const elements = convertDrawingToGraphic(activeDrawing.value, true)
    const graphic = chart.getOption().graphic || []
    chart.setOption({ graphic: [...graphic, ...elements] }, { notMerge: false })
  }

  /**
   * 清除临时画线.
   */
  const clearActiveDrawing = () => {
    const chart = options.chartInstance()
    if (!chart) return

    const graphic = chart.getOption().graphic || []
    const filteredGraphics = graphic.filter(g => !g.id?.startsWith('temp_drawing_'))
    chart.setOption({ graphic: filteredGraphics }, { notMerge: false })
  }

  /**
   * 高亮选中画线.
   */
  const highlightDrawing = (id: string) => {
    const chart = options.chartInstance()
    if (!chart) return

    const graphic = chart.getOption().graphic || []
    const newGraphics = graphic.map((g: any) => {
      if (g.id?.startsWith(`drawing_${id}`)) {
        return {
          ...g,
          style: {
            ...g.style,
            stroke: '#FFD700', // 高亮颜色
            lineWidth: g.style?.lineWidth + 1
          }
        }
      }
      return g
    })

    chart.setOption({ graphic: newGraphics }, { notMerge: false })
  }

  /**
   * 将数据坐标转换为像素坐标.
   * 使用主图（gridIndex: 0）的坐标系.
   */
  const convertToPixel = (x: number, y: number): [number, number] => {
    const chart = options.chartInstance()
    if (!chart) return [x, y]

    try {
      // 指定主图的坐标系（gridIndex: 0）
      return chart.convertToPixel({ gridIndex: 0 }, [x, y])
    } catch (e) {
      logger.warn('坐标转换失败', e)
      return [x, y]
    }
  }

  /**
   * 将画线转换为ECharts graphic元素.
   */
  const convertDrawingToGraphic = (drawing: Drawing, isTemp: boolean = false): any[] => {
    const elements: any[] = []
    const idPrefix = isTemp ? 'temp_drawing_' : 'drawing_'
    const chart = options.chartInstance()

    switch (drawing.type) {
      case 'line':
        // 直线：两点画线
        if (drawing.points.length >= 2) {
          const [x1, y1] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
          const [x2, y2] = convertToPixel(drawing.points[1].x, drawing.points[1].y)
          elements.push({
            id: `${idPrefix}${drawing.id}`,
            type: 'line',
            shape: {
              x1: x1,
              y1: y1,
              x2: x2,
              y2: y2
            },
            style: {
              stroke: drawing.color,
              lineWidth: drawing.lineWidth
            },
            z: 100
          })
        }
        break

      case 'trendLine':
        if (drawing.points.length >= 2) {
          const [x1, y1] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
          const [x2, y2] = convertToPixel(drawing.points[1].x, drawing.points[1].y)
          elements.push({
            id: `${idPrefix}${drawing.id}`,
            type: 'line',
            shape: {
              x1: x1,
              y1: y1,
              x2: x2,
              y2: y2
            },
            style: {
              stroke: drawing.color,
              lineWidth: drawing.lineWidth
            },
            z: 100
          })
        }
        break

      case 'horizontalLine':
        // 水平线需要跨整个图表宽度
        const chartWidth = chart?.getWidth() || 800
        const [, yPixel] = convertToPixel(0, drawing.points[0].y)
        elements.push({
          id: `${idPrefix}${drawing.id}`,
          type: 'line',
          shape: {
            x1: 0,
            y1: yPixel,
            x2: chartWidth,
            y2: yPixel
          },
          style: {
            stroke: drawing.color,
            lineWidth: drawing.lineWidth
          },
          z: 100
        })
        break

      case 'verticalLine':
        // 垂直线需要跨整个图表高度
        const chartHeight = chart?.getHeight() || 500
        const [xPixel] = convertToPixel(drawing.points[0].x, 0)
        elements.push({
          id: `${idPrefix}${drawing.id}`,
          type: 'line',
          shape: {
            x1: xPixel,
            y1: 0,
            x2: xPixel,
            y2: chartHeight
          },
          style: {
            stroke: drawing.color,
            lineWidth: drawing.lineWidth
          },
          z: 100
        })
        break

      case 'rectangle':
        if (drawing.points.length >= 2) {
          const [px1, py1] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
          const [px2, py2] = convertToPixel(drawing.points[1].x, drawing.points[1].y)
          elements.push({
            id: `${idPrefix}${drawing.id}`,
            type: 'rect',
            shape: {
              x: Math.min(px1, px2),
              y: Math.min(py1, py2),
              width: Math.abs(px2 - px1),
              height: Math.abs(py2 - py1)
            },
            style: {
              stroke: drawing.color,
              lineWidth: drawing.lineWidth,
              fill: drawing.color + '20' // 半透明填充
            },
            z: 100
          })
        }
        break

      case 'text':
        const [textX, textY] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
        elements.push({
          id: `${idPrefix}${drawing.id}`,
          type: 'text',
          style: {
            text: drawing.text || '标注',
            fill: drawing.color,
            fontSize: 14,
            fontWeight: 'bold'
          },
          x: textX,
          y: textY,
          z: 100
        })
        break

      case 'arrowUp':
        const [arrowUpX, arrowUpY] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
        elements.push({
          id: `${idPrefix}${drawing.id}`,
          type: 'path',
          shape: {
            pathData: 'M0 10 L5 0 L10 10 M5 0 L5 20'
          },
          style: {
            stroke: drawing.color,
            lineWidth: drawing.lineWidth,
            fill: 'none'
          },
          x: arrowUpX,
          y: arrowUpY,
          scale: [drawing.lineWidth, drawing.lineWidth],
          z: 100
        })
        break

      case 'arrowDown':
        const [arrowDownX, arrowDownY] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
        elements.push({
          id: `${idPrefix}${drawing.id}`,
          type: 'path',
          shape: {
            pathData: 'M0 0 L5 10 L10 0 M5 10 L5 -10'
          },
          style: {
            stroke: drawing.color,
            lineWidth: drawing.lineWidth,
            fill: 'none'
          },
          x: arrowDownX,
          y: arrowDownY,
          scale: [drawing.lineWidth, drawing.lineWidth],
          z: 100
        })
        break

      // ===== 专业画线工具 =====

      case 'fibonacci':
        // 黄金分割线：从起点到终点绘制多条水平比例线
        if (drawing.points.length >= 2) {
          const levels = drawing.params?.fibonacciLevels || [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
          const startY = drawing.points[0].y
          const endY = drawing.points[1].y
          const priceRange = Math.abs(endY - startY)
          const baseY = Math.min(startY, endY)
          const cw = chart?.getWidth() || 800

          // 绘制起始线（连接起点和终点）
          const [fibX1, fibY1] = convertToPixel(drawing.points[0].x, startY)
          const [fibX2, fibY2] = convertToPixel(drawing.points[1].x, endY)
          elements.push({
            id: `${idPrefix}${drawing.id}_base`,
            type: 'line',
            shape: {
              x1: fibX1,
              y1: fibY1,
              x2: fibX2,
              y2: fibY2
            },
            style: {
              stroke: drawing.color,
              lineWidth: drawing.lineWidth
            },
            z: 100
          })

          // 绘制各比例水平线
          levels.forEach((level, idx) => {
            const levelY = baseY + priceRange * level
            const [, levelPixelY] = convertToPixel(0, levelY)
            elements.push({
              id: `${idPrefix}${drawing.id}_level_${idx}`,
              type: 'line',
              shape: {
                x1: 0,
                y1: levelPixelY,
                x2: cw,
                y2: levelPixelY
              },
              style: {
                stroke: level === 0.5 ? '#f59e0b' : drawing.color,
                lineWidth: level === 0.5 ? drawing.lineWidth + 1 : drawing.lineWidth,
                opacity: 0.7
              },
              z: 99
            })
            // 添加比例标注文字
            elements.push({
              id: `${idPrefix}${drawing.id}_label_${idx}`,
              type: 'text',
              style: {
                text: `${(level * 100).toFixed(1)}%`,
                fill: drawing.color,
                fontSize: 11
              },
              x: 5,
              y: levelPixelY - 5,
              z: 100
            })
          })
        }
        break

      case 'gannLine':
        // 江恩角度线：从起点发散的多条角度线（像素坐标空间）
        if (drawing.points.length >= 1) {
          const angles = [15, 30, 45, 60, 75, 90, 105, 120, 135, 150]
          const [originPx, originPy] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
          const cw = chart?.getWidth() || 800
          const ch = chart?.getHeight() || 500

          angles.forEach((angle, idx) => {
            const radian = (angle * Math.PI) / 180
            const length = Math.max(cw, ch) * 2
            const endPx = originPx + Math.cos(radian) * length
            const endPy = originPy - Math.sin(radian) * length

            const isMainLine = angle === 45

            elements.push({
              id: `${idPrefix}${drawing.id}_angle_${idx}`,
              type: 'line',
              shape: {
                x1: originPx,
                y1: originPy,
                x2: endPx,
                y2: endPy
              },
              style: {
                stroke: isMainLine ? '#f59e0b' : drawing.color,
                lineWidth: isMainLine ? drawing.lineWidth + 1 : drawing.lineWidth,
                opacity: isMainLine ? 1 : 0.5
              },
              z: 99
            })
          })

          // 添加起点标记
          elements.push({
            id: `${idPrefix}${drawing.id}_origin`,
            type: 'circle',
            shape: {
              cx: originPx,
              cy: originPy,
              r: 5
            },
            style: {
              fill: drawing.color,
              stroke: drawing.color
            },
            z: 100
          })
        }
        break

      case 'pitchfork':
        // 安德鲁音叉线
        if (drawing.points.length >= 3) {
          const [p1x, p1y] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
          const [p2x, p2y] = convertToPixel(drawing.points[1].x, drawing.points[1].y)
          const [p3x, p3y] = convertToPixel(drawing.points[2].x, drawing.points[2].y)

          const midPx = (p2x + p3x) / 2
          const midPy = (p2y + p3y) / 2
          const extX = midPx + (midPx - p1x) * 2
          const extY = midPy + (midPy - p1y) * 2

          // 绘制中线
          elements.push({
            id: `${idPrefix}${drawing.id}_median`,
            type: 'line',
            shape: {
              x1: p1x,
              y1: p1y,
              x2: extX,
              y2: extY
            },
            style: {
              stroke: drawing.color,
              lineWidth: drawing.lineWidth + 1
            },
            z: 100
          })

          // 上平行线
          elements.push({
            id: `${idPrefix}${drawing.id}_upper`,
            type: 'line',
            shape: {
              x1: p2x,
              y1: p2y,
              x2: extX,
              y2: extY + (p2y - midPy)
            },
            style: {
              stroke: drawing.color,
              lineWidth: drawing.lineWidth,
              opacity: 0.7
            },
            z: 99
          })

          // 下平行线
          elements.push({
            id: `${idPrefix}${drawing.id}_lower`,
            type: 'line',
            shape: {
              x1: p3x,
              y1: p3y,
              x2: extX,
              y2: extY + (p3y - midPy)
            },
            style: {
              stroke: drawing.color,
              lineWidth: drawing.lineWidth,
              opacity: 0.7
            },
            z: 99
          })

          // 锚点标记
          [[p1x, p1y], [p2x, p2y], [p3x, p3y]].forEach(([px, py], idx) => {
            elements.push({
              id: `${idPrefix}${drawing.id}_anchor_${idx}`,
              type: 'circle',
              shape: { cx: px, cy: py, r: 4 },
              style: {
                fill: idx === 0 ? '#f59e0b' : drawing.color,
                stroke: '#ffffff',
                lineWidth: 1
              },
              z: 100
            })
          })
        }
        break

      case 'fibonacciFan':
        // 斐波那契扇形线
        if (drawing.points.length >= 2) {
          const [originPx, originPy] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
          const [targetPx, targetPy] = convertToPixel(drawing.points[1].x, drawing.points[1].y)
          const cw = chart?.getWidth() || 800

          const priceChange = targetPy - originPy
          const timeChange = targetPx - originPx
          const ratios = [0.382, 0.5, 0.618, 1]

          ratios.forEach((ratio, idx) => {
            const endPx = originPx + timeChange * ratio
            const endPy = originPy + priceChange * ratio

            elements.push({
              id: `${idPrefix}${drawing.id}_fan_${idx}`,
              type: 'line',
              shape: {
                x1: originPx,
                y1: originPy,
                x2: endPx,
                y2: endPy
              },
              style: {
                stroke: ratio === 0.618 ? '#f59e0b' : drawing.color,
                lineWidth: ratio === 0.618 ? drawing.lineWidth + 1 : drawing.lineWidth,
                opacity: 0.8
              },
              z: 99
            })

            // 延长线
            const slope = priceChange / timeChange
            const extPx = cw
            const extPy = originPy + slope * (extPx - originPx) * ratio
            elements.push({
              id: `${idPrefix}${drawing.id}_fan_ext_${idx}`,
              type: 'line',
              shape: { x1: endPx, y1: endPy, x2: extPx, y2: extPy },
              style: {
                stroke: drawing.color,
                lineWidth: drawing.lineWidth,
                opacity: 0.4,
                lineDash: [4, 4]
              },
              z: 98
            })
          })
        }
        break

      case 'parallelChannel':
        // 平行通道线
        if (drawing.points.length >= 2) {
          const [p1x, p1y] = convertToPixel(drawing.points[0].x, drawing.points[0].y)
          const [p2x, p2y] = convertToPixel(drawing.points[1].x, drawing.points[1].y)

          const channelWidth = drawing.params?.channelWidth || 30
          const dx = p2x - p1x
          const dy = p2y - p1y
          const length = Math.sqrt(dx * dx + dy * dy)
          const perpX = (-dy / length) * channelWidth
          const perpY = (dx / length) * channelWidth

          // 主线
          elements.push({
            id: `${idPrefix}${drawing.id}_main`,
            type: 'line',
            shape: { x1: p1x, y1: p1y, x2: p2x, y2: p2y },
            style: { stroke: drawing.color, lineWidth: drawing.lineWidth },
            z: 100
          })

          // 上平行线
          elements.push({
            id: `${idPrefix}${drawing.id}_upper`,
            type: 'line',
            shape: { x1: p1x + perpX, y1: p1y + perpY, x2: p2x + perpX, y2: p2y + perpY },
            style: { stroke: drawing.color, lineWidth: drawing.lineWidth, opacity: 0.7 },
            z: 99
          })

          // 下平行线
          elements.push({
            id: `${idPrefix}${drawing.id}_lower`,
            type: 'line',
            shape: { x1: p1x - perpX, y1: p1y - perpY, x2: p2x - perpX, y2: p2y - perpY },
            style: { stroke: drawing.color, lineWidth: drawing.lineWidth, opacity: 0.7 },
            z: 99
          })

          // 填充区域
          elements.push({
            id: `${idPrefix}${drawing.id}_fill`,
            type: 'polygon',
            shape: {
              points: [
                [p1x + perpX, p1y + perpY],
                [p2x + perpX, p2y + perpY],
                [p2x - perpX, p2y - perpY],
                [p1x - perpX, p1y - perpY]
              ]
            },
            style: { fill: drawing.color + '10', stroke: 'none' },
            z: 97
          })
        }
        break

      case 'waveMark':
        // 波浪线标注
        if (drawing.points.length >= 1) {
          const labels = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'A', 'B', 'C']

          drawing.points.forEach((p, idx) => {
            const [wx, wy] = convertToPixel(p.x, p.y)
            const label = labels[idx % labels.length]

            elements.push({
              id: `${idPrefix}${drawing.id}_wave_${idx}`,
              type: 'circle',
              shape: { cx: wx, cy: wy, r: 6 },
              style: {
                fill: idx < 5 ? '#ef4444' : '#22c55e',
                stroke: '#ffffff',
                lineWidth: 1
              },
              z: 100
            })

            elements.push({
              id: `${idPrefix}${drawing.id}_label_${idx}`,
              type: 'text',
              style: {
                text: label,
                fill: '#ffffff',
                fontSize: 12,
                fontWeight: 'bold',
                textAlign: 'center',
                textVerticalAlign: 'middle'
              },
              x: wx,
              y: wy,
              z: 101
            })
          })

          // 连接线
          if (drawing.points.length >= 2) {
            for (let i = 0; i < drawing.points.length - 1; i++) {
              const [lx1, ly1] = convertToPixel(drawing.points[i].x, drawing.points[i].y)
              const [lx2, ly2] = convertToPixel(drawing.points[i + 1].x, drawing.points[i + 1].y)
              const isImpulse = i < 4
              elements.push({
                id: `${idPrefix}${drawing.id}_line_${i}`,
                type: 'line',
                shape: { x1: lx1, y1: ly1, x2: lx2, y2: ly2 },
                style: {
                  stroke: isImpulse ? '#ef4444' : '#22c55e',
                  lineWidth: drawing.lineWidth,
                  opacity: 0.6,
                  lineDash: isImpulse ? [] : [4, 4]
                },
                z: 98
              })
            }
          }
        }
        break
    }

    return elements
  }

  /**
   * 设置工具.
   */
  const setTool = (tool: DrawingTool) => {
    currentTool.value = tool
  }

  /**
   * 设置颜色并保存到服务端.
   */
  const setColor = (color: string) => {
    currentColor.value = color
    // 保存到localStorage和服务端
    localStorage.setItem('fdas_drawing_color', color)
    saveChartSetting('drawing_tools', 'color', { color }).catch(() => {
      // 服务端保存失败时忽略，已保存到localStorage
    })
  }

  /**
   * 设置粗细并保存到服务端.
   */
  const setLineWidth = (width: number) => {
    currentLineWidth.value = width
    // 保存到localStorage和服务端
    localStorage.setItem('fdas_drawing_width', String(width))
    saveChartSetting('drawing_tools', 'lineWidth', { lineWidth: width }).catch(() => {
      // 服务端保存失败时忽略，已保存到localStorage
    })
  }

  /**
   * 设置磁吸并保存到服务端.
   */
  const setMagnet = (enabled: boolean) => {
    magnetEnabled.value = enabled
    // 保存到localStorage和服务端
    localStorage.setItem('fdas_drawing_magnet', String(enabled))
    saveChartSetting('drawing_tools', 'magnet', { magnetEnabled: enabled }).catch(() => {
      // 服务端保存失败时忽略，已保存到localStorage
    })
  }

  /**
   * 设置工具参数.
   */
  const setToolParams = (params: Record<string, any>) => {
    currentToolParams.value = params
  }

  /**
   * 添加文字标注.
   */
  const addTextAnnotation = (point: { x: number; y: number }, text: string) => {
    const magnetPoint = magnetToPoint(point.x, point.y)
    const drawing: Drawing = {
      id: generateId(),
      type: 'text',
      points: [magnetPoint],
      color: currentColor.value,
      lineWidth: currentLineWidth.value,
      text,
      createdAt: Date.now()
    }
    drawings.value.push(drawing)
    renderDrawings()
  }

  return {
    // 状态
    currentTool,
    currentColor,
    currentLineWidth,
    magnetEnabled,
    currentToolParams,
    drawings,
    activeDrawing,
    isDrawing,
    selectedDrawingId,
    selectedDrawing,
    drawingCount,
    waitingForSecondClick,
    firstClickPoint,

    // 方法
    setTool,
    setColor,
    setLineWidth,
    setMagnet,
    setToolParams,
    startDrawing,
    onDrawing,
    endDrawing,
    cancelDrawing,
    selectDrawing,
    deselectDrawing,
    deleteSelectedDrawing,
    clearAllDrawings,
    updateSelectedDrawing,
    moveDrawingPoint,
    addTextAnnotation,
    renderDrawings,
    magnetToPoint,
    handleSecondClick
  }
}