/**
 * ECharts图表配置工具测试.
 *
 * 测试图表主题、K线配置、均线配置等技术指标.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect } from 'vitest'
import {
  chartThemes,
  getKLineBaseOption,
  getKLineSeriesOption,
  getMASeriesOption,
  getVolumeSeriesOption,
  getMACDSeriesOptions,
  formatKLineData,
  calculateUpDown,
  formatVolumeData,
  detectGaps,
  detectLongShadows,
  generateGapMarkPoints,
  generateGapMarkLines
} from '../chartConfig'

describe('ChartConfig 图表配置工具', () => {
  describe('chartThemes 主题配置', () => {
    it('light主题应有完整配置', () => {
      const light = chartThemes.light
      expect(light.background).toBe('#ffffff')
      expect(light.textPrimary).toBe('#333333')
      expect(light.upColor).toBe('#ef4444')
      expect(light.downColor).toBe('#22c55e')
      expect(light.ma5Color).toBe('#f59e0b')
      expect(light.ma10Color).toBe('#3b82f6')
      expect(light.ma20Color).toBe('#8b5cf6')
      expect(light.ma60Color).toBe('#06b6d4')
    })

    it('dark主题应有完整配置', () => {
      const dark = chartThemes.dark
      expect(dark.background).toBe('#1a1a2e')
      expect(dark.textPrimary).toBe('#e0e0e0')
      expect(dark.upColor).toBe('#ff4d4f')
      expect(dark.downColor).toBe('#52c41a')
    })

    it('两个主题涨跌颜色应一致（红涨绿跌）', () => {
      // 涨跌配色标准：红色代表涨，绿色代表跌
      expect(chartThemes.light.upColor).toContain('44') // 红色
      expect(chartThemes.light.downColor).toContain('55') // 绿色
      expect(chartThemes.dark.upColor).toContain('4f') // 红色
      expect(chartThemes.dark.downColor).toContain('1a') // 绿色
    })

    it('涨跌停配色应醒目', () => {
      expect(chartThemes.light.limitUpColor).toBe('#ff6b6b')
      expect(chartThemes.light.limitDownColor).toBe('#4ade80')
      expect(chartThemes.dark.limitUpColor).toBe('#ff7875')
      expect(chartThemes.dark.limitDownColor).toBe('#73d13d')
    })
  })

  describe('getKLineBaseOption K线基础配置', () => {
    it('light主题默认配置应正确', () => {
      const option = getKLineBaseOption('light')
      expect(option.backgroundColor).toBe('#ffffff')
      expect(option.animation).toBe(false) // 关闭动画提升性能
      expect(option.tooltip.trigger).toBe('axis')
    })

    it('dark主题配置应正确', () => {
      const option = getKLineBaseOption('dark')
      expect(option.backgroundColor).toBe('#1a1a2e')
    })

    it('应包含三个grid区域（主图+成交量+MACD）', () => {
      const option = getKLineBaseOption('light')
      expect(option.grid).toHaveLength(3)
      expect(option.grid[0].height).toBe('55%') // 主图
      expect(option.grid[1].height).toBe('12%') // 成交量
      expect(option.grid[2].height).toBe('10%') // MACD
    })

    it('应包含三个X轴', () => {
      const option = getKLineBaseOption('light')
      expect(option.xAxis).toHaveLength(3)
      expect(option.xAxis[0].type).toBe('category')
      expect(option.xAxis[0].gridIndex).toBe(0)
    })

    it('应包含四个Y轴', () => {
      const option = getKLineBaseOption('light')
      expect(option.yAxis).toHaveLength(4)
      // 主图左Y轴
      expect(option.yAxis[0].gridIndex).toBe(0)
      expect(option.yAxis[0].position).toBe('left')
      // 主图右Y轴
      expect(option.yAxis[1].gridIndex).toBe(0)
      expect(option.yAxis[1].position).toBe('right')
      // 成交量Y轴
      expect(option.yAxis[2].gridIndex).toBe(1)
      // MACD Y轴
      expect(option.yAxis[3].gridIndex).toBe(2)
    })

    it('应支持对数坐标', () => {
      const option = getKLineBaseOption('light', 'log')
      expect(option.yAxis[0].type).toBe('log')
      expect(option.yAxis[1].type).toBe('log')
    })

    it('应包含两个dataZoom组件', () => {
      const option = getKLineBaseOption('light')
      expect(option.dataZoom).toHaveLength(2)
      expect(option.dataZoom[0].type).toBe('inside')
      expect(option.dataZoom[1].type).toBe('slider')
    })

    it('dataZoom默认应显示最近40%数据', () => {
      const option = getKLineBaseOption('light')
      expect(option.dataZoom[0].start).toBe(60)
      expect(option.dataZoom[0].end).toBe(100)
    })

    it('brush配置应正确', () => {
      const option = getKLineBaseOption('light')
      expect(option.brush.xAxisIndex).toBe(0)
      expect(option.brush.yAxisIndex).toBe(0)
      expect(option.brush.throttleType).toBe('debounce')
    })

    it('legend配置应正确', () => {
      const option = getKLineBaseOption('light')
      expect(option.legend.enabled).toBe(true)
      expect(option.legend.data).toEqual([])
    })
  })

  describe('getKLineSeriesOption K线系列配置', () => {
    it('应返回正确的K线系列配置', () => {
      const series = getKLineSeriesOption('light')
      expect(series.name).toBe('K线')
      expect(series.type).toBe('candlestick')
      expect(series.xAxisIndex).toBe(0)
      expect(series.yAxisIndex).toBe(0)
    })

    it('涨跌颜色应正确', () => {
      const series = getKLineSeriesOption('light')
      expect(series.itemStyle.color).toBe('#ef4444')
      expect(series.itemStyle.color0).toBe('#22c55e')
    })

    it('K线宽度应设置为60%', () => {
      const series = getKLineSeriesOption('light')
      expect(series.barWidth).toBe('60%')
    })

    it('dark主题K线颜色应正确', () => {
      const series = getKLineSeriesOption('dark')
      expect(series.itemStyle.color).toBe('#ff4d4f')
      expect(series.itemStyle.color0).toBe('#52c41a')
    })
  })

  describe('getMASeriesOption 均线系列配置', () => {
    it('MA5配置应正确', () => {
      const series = getMASeriesOption(5, 'light')
      expect(series.name).toBe('MA5')
      expect(series.type).toBe('line')
      expect(series.lineStyle.color).toBe('#f59e0b')
    })

    it('MA10配置应正确', () => {
      const series = getMASeriesOption(10, 'light')
      expect(series.name).toBe('MA10')
      expect(series.lineStyle.color).toBe('#3b82f6')
    })

    it('MA20配置应正确', () => {
      const series = getMASeriesOption(20, 'light')
      expect(series.name).toBe('MA20')
      expect(series.lineStyle.color).toBe('#8b5cf6')
    })

    it('MA60配置应正确', () => {
      const series = getMASeriesOption(60, 'light')
      expect(series.name).toBe('MA60')
      expect(series.lineStyle.color).toBe('#06b6d4')
    })

    it('未知周期应使用默认灰色', () => {
      const series = getMASeriesOption(30, 'light')
      expect(series.lineStyle.color).toBe('#999999')
    })

    it('均线不应显示symbol', () => {
      const series = getMASeriesOption(5, 'light')
      expect(series.symbol).toBe('none')
    })

    it('均线应为非平滑线', () => {
      const series = getMASeriesOption(5, 'light')
      expect(series.smooth).toBe(false)
    })
  })

  describe('getVolumeSeriesOption 成交量系列配置', () => {
    it('应返回正确的成交量系列配置', () => {
      const series = getVolumeSeriesOption('light')
      expect(series.name).toBe('成交量')
      expect(series.type).toBe('bar')
      expect(series.xAxisIndex).toBe(1)
      expect(series.yAxisIndex).toBe(1)
    })

    it('成交量柱宽度应为60%', () => {
      const series = getVolumeSeriesOption('light')
      expect(series.barWidth).toBe('60%')
    })

    it('应包含颜色函数', () => {
      const series = getVolumeSeriesOption('light')
      expect(series.itemStyle.color).toBeDefined()
      expect(typeof series.itemStyle.color).toBe('function')
    })
  })

  describe('getMACDSeriesOptions MACD系列配置', () => {
    it('应返回三个系列（DIF、DEA、MACD柱）', () => {
      const series = getMACDSeriesOptions('light')
      expect(series).toHaveLength(3)
    })

    it('DIF线配置应正确', () => {
      const series = getMACDSeriesOptions('light')
      expect(series[0].name).toBe('DIF')
      expect(series[0].type).toBe('line')
      expect(series[0].lineStyle.color).toBe('#f59e0b')
    })

    it('DEA线配置应正确', () => {
      const series = getMACDSeriesOptions('light')
      expect(series[1].name).toBe('DEA')
      expect(series[1].type).toBe('line')
      expect(series[1].lineStyle.color).toBe('#3b82f6')
    })

    it('MACD柱配置应正确', () => {
      const series = getMACDSeriesOptions('light')
      expect(series[2].name).toBe('MACD')
      expect(series[2].type).toBe('bar')
      expect(series[2].barWidth).toBe('40%')
    })

    it('MACD柱应使用副图坐标', () => {
      const series = getMACDSeriesOptions('light')
      expect(series[0].xAxisIndex).toBe(2)
      expect(series[0].yAxisIndex).toBe(2)
      expect(series[1].xAxisIndex).toBe(2)
      expect(series[1].yAxisIndex).toBe(2)
      expect(series[2].xAxisIndex).toBe(2)
      expect(series[2].yAxisIndex).toBe(2)
    })
  })

  describe('formatKLineData K线数据格式化', () => {
    it('应正确格式化K线数据', () => {
      const rawData = [
        { open: 7.25, close: 7.30, low: 7.20, high: 7.35 },
        { open: 7.30, close: 7.28, low: 7.25, high: 7.40 }
      ]
      const result = formatKLineData(rawData)
      expect(result).toHaveLength(2)
      expect(result[0]).toEqual([7.25, 7.30, 7.20, 7.35])
      expect(result[1]).toEqual([7.30, 7.28, 7.25, 7.40])
    })

    it('空数据应返回空数组', () => {
      expect(formatKLineData(null)).toEqual([])
      expect(formatKLineData(undefined)).toEqual([])
      expect(formatKLineData([])).toEqual([])
    })

    it('字符串数值应正确转换', () => {
      const rawData = [
        { open: '7.25', close: '7.30', low: '7.20', high: '7.35' }
      ]
      const result = formatKLineData(rawData)
      expect(result[0]).toEqual([7.25, 7.30, 7.20, 7.35])
    })

    it('无效数值应转换为0', () => {
      const rawData = [
        { open: 'invalid', close: null, low: undefined, high: 7.35 }
      ]
      const result = formatKLineData(rawData)
      expect(result[0]).toEqual([0, 0, 0, 7.35])
    })
  })

  describe('calculateUpDown 涨跌状态计算', () => {
    it('涨（阳线）应返回true', () => {
      const rawData = [{ open: 7.25, close: 7.30 }]
      const result = calculateUpDown(rawData)
      expect(result[0]).toBe(true)
    })

    it('跌（阴线）应返回false', () => {
      const rawData = [{ open: 7.30, close: 7.25 }]
      const result = calculateUpDown(rawData)
      expect(result[0]).toBe(false)
    })

    it('平盘应返回true（close >= open）', () => {
      const rawData = [{ open: 7.25, close: 7.25 }]
      const result = calculateUpDown(rawData)
      expect(result[0]).toBe(true)
    })

    it('空数据应返回空数组', () => {
      expect(calculateUpDown(null)).toEqual([])
      expect(calculateUpDown(undefined)).toEqual([])
      expect(calculateUpDown([])).toEqual([])
    })
  })

  describe('formatVolumeData 成交量数据格式化', () => {
    it('涨日成交量应为红色', () => {
      const rawData = [{ open: 7.25, close: 7.30, volume: 1000 }]
      const result = formatVolumeData(rawData)
      expect(result[0].value).toBe(1000)
      expect(result[0].itemStyle.color).toBe('#ef4444')
    })

    it('跌日成交量应为绿色', () => {
      const rawData = [{ open: 7.30, close: 7.25, volume: 1000 }]
      const result = formatVolumeData(rawData)
      expect(result[0].itemStyle.color).toBe('#22c55e')
    })

    it('空数据应返回空数组', () => {
      expect(formatVolumeData(null)).toEqual([])
      expect(formatVolumeData([])).toEqual([])
    })

    it('缺失volume应转换为0', () => {
      const rawData = [{ open: 7.25, close: 7.30 }]
      const result = formatVolumeData(rawData)
      expect(result[0].value).toBe(0)
    })
  })

  describe('detectGaps 跳空缺口检测', () => {
    it('向上跳空应正确检测', () => {
      const rawData = [
        { date: '2026-01-01', high: 7.30, low: 7.20 },
        { date: '2026-01-02', high: 7.50, low: 7.35 } // 今日最低 > 昨日最高
      ]
      const result = detectGaps(rawData)
      expect(result).toHaveLength(1)
      expect(result[0].type).toBe('gapUp')
      expect(result[0].index).toBe(1)
    })

    it('向下跳空应正确检测', () => {
      const rawData = [
        { date: '2026-01-01', high: 7.30, low: 7.20 },
        { date: '2026-01-02', high: 7.15, low: 7.10 } // 今日最高 < 昨日最低
      ]
      const result = detectGaps(rawData)
      expect(result).toHaveLength(1)
      expect(result[0].type).toBe('gapDown')
      expect(result[0].index).toBe(1)
    })

    it('无跳空应返回空数组', () => {
      const rawData = [
        { date: '2026-01-01', high: 7.30, low: 7.20 },
        { date: '2026-01-02', high: 7.35, low: 7.25 } // 价格重叠，无跳空
      ]
      const result = detectGaps(rawData)
      expect(result).toEqual([])
    })

    it('少于2条数据应返回空数组', () => {
      expect(detectGaps(null)).toEqual([])
      expect(detectGaps([])).toEqual([])
      expect(detectGaps([{ date: '2026-01-01' }])).toEqual([])
    })

    it('应检测多个跳空缺口', () => {
      const rawData = [
        { date: '2026-01-01', high: 7.30, low: 7.20 },
        { date: '2026-01-02', high: 7.50, low: 7.35 }, // 向上跳空
        { date: '2026-01-03', high: 7.55, low: 7.45 },
        { date: '2026-01-04', high: 7.30, low: 7.10 } // 向下跳空
      ]
      const result = detectGaps(rawData)
      expect(result).toHaveLength(2)
    })
  })

  describe('detectLongShadows 长影线检测', () => {
    it('阳线长上影线应正确检测', () => {
      // 阳线：收盘 > 开盘
      // 上影线 = high - max(open, close)
      // 实体 = |close - open|
      // 长上影线：上影线 > 实体 * 2
      const rawData = [
        { date: '2026-01-01', open: 7.20, close: 7.25, high: 7.50, low: 7.18 }
      ]
      // 实体 = 0.05，上影线 = 0.25，上影线 > 实体 * 2 (0.25 > 0.10)
      const result = detectLongShadows(rawData)
      expect(result).toHaveLength(1)
      expect(result[0].type).toBe('longUpperShadow')
    })

    it('阴线长下影线应正确检测', () => {
      // 阴线：收盘 < 开盘
      // 下影线 = min(open, close) - low
      // 长下影线：下影线 > 实体 * 2
      const rawData = [
        { date: '2026-01-01', open: 7.30, close: 7.25, high: 7.35, low: 7.00 }
      ]
      // 实体 = 0.05，下影线 = 0.25，下影线 > 实体 * 2
      const result = detectLongShadows(rawData)
      expect(result).toHaveLength(1)
      expect(result[0].type).toBe('longLowerShadow')
    })

    it('无长影线应返回空数组', () => {
      const rawData = [
        { date: '2026-01-01', open: 7.20, close: 7.25, high: 7.28, low: 7.18 }
      ]
      const result = detectLongShadows(rawData)
      expect(result).toEqual([])
    })

    it('空数据应返回空数组', () => {
      expect(detectLongShadows(null)).toEqual([])
      expect(detectLongShadows([])).toEqual([])
    })

    it('阈值参数应生效', () => {
      const rawData = [
        { date: '2026-01-01', open: 7.20, close: 7.25, high: 7.40, low: 7.18 }
      ]
      // 上影线 = 0.15，实体 = 0.05，比例 = 3
      // 阈值2时应检测到，阈值4时应不检测
      expect(detectLongShadows(rawData, 2)).toHaveLength(1)
      expect(detectLongShadows(rawData, 4)).toHaveLength(0)
    })

    it('实体为0时应不检测', () => {
      const rawData = [
        { date: '2026-01-01', open: 7.25, close: 7.25, high: 7.50, low: 7.00 }
      ]
      const result = detectLongShadows(rawData)
      expect(result).toEqual([])
    })
  })

  describe('generateGapMarkPoints 缺口标记点生成', () => {
    it('向上跳空标记点应正确', () => {
      const gaps = [{ index: 1, type: 'gapUp', startPrice: 7.30, endPrice: 7.35, date: '2026-01-02' }]
      const result = generateGapMarkPoints(gaps, 'light')
      expect(result).not.toBeNull()
      expect(result.data).toHaveLength(1)
      expect(result.data[0].symbol).toBe('arrow')
      expect(result.data[0].symbolRotate).toBe(0)
    })

    it('向下跳空标记点应正确', () => {
      const gaps = [{ index: 1, type: 'gapDown', startPrice: 7.20, endPrice: 7.15, date: '2026-01-02' }]
      const result = generateGapMarkPoints(gaps, 'light')
      expect(result).not.toBeNull()
      expect(result.data[0].symbolRotate).toBe(180)
    })

    it('空缺口数组应返回null', () => {
      expect(generateGapMarkPoints(null, 'light')).toBeNull()
      expect(generateGapMarkPoints([], 'light')).toBeNull()
    })

    it('应关闭动画', () => {
      const gaps = [{ index: 1, type: 'gapUp', startPrice: 7.30, endPrice: 7.35, date: '2026-01-02' }]
      const result = generateGapMarkPoints(gaps, 'light')
      expect(result.animation).toBe(false)
    })
  })

  describe('generateGapMarkLines 缺口标记线生成', () => {
    it('缺口标记线应正确生成', () => {
      const gaps = [{ index: 1, type: 'gapUp', startPrice: 7.30, endPrice: 7.35, date: '2026-01-02' }]
      const result = generateGapMarkLines(gaps, [])
      expect(result).not.toBeNull()
      expect(result.data).toHaveLength(1)
      expect(result.symbol).toBe('none')
    })

    it('空缺口数组应返回null', () => {
      expect(generateGapMarkLines(null, [])).toBeNull()
      expect(generateGapMarkLines([], [])).toBeNull()
    })

    it('向上跳空标记线颜色应为橙色', () => {
      const gaps = [{ index: 1, type: 'gapUp', startPrice: 7.30, endPrice: 7.35, date: '2026-01-02' }]
      const result = generateGapMarkLines(gaps, [])
      expect(result.data[0].lineStyle.color).toBe('#f59e0b')
    })

    it('向下跳空标记线颜色应为紫色', () => {
      const gaps = [{ index: 1, type: 'gapDown', startPrice: 7.20, endPrice: 7.15, date: '2026-01-02' }]
      const result = generateGapMarkLines(gaps, [])
      expect(result.data[0].lineStyle.color).toBe('#8b5cf6')
    })
  })
})