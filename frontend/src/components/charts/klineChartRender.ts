/**
 * K线图表渲染配置.
 *
 * 从KLineChart.vue提取的图表渲染配置和事件处理.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import type ECharts from 'echarts'
import {
  getKLineBaseOption,
  getKLineSeriesOption,
  getMASeriesOption,
  chartThemes,
  MarketType,
  getMarketConfig
} from '@/utils/chartConfig'
import {
  identifyMarketTypeByName,
  marketConfigs,
  calculateLimitUpPrice,
  calculateLimitDownPrice,
  isLimitUp,
  isLimitDown,
  calculateLimitUpDownStats,
  AdjustmentType,
  calculateAdjustedPrices
} from '@/utils/stockUtils'

// 图表主题配置
export interface ChartThemeConfig {
  textPrimary: string
  textSecondary: string
  gridLine: string
  axisLine: string
}

/**
 * 获取主题配置.
 */
export function getThemeConfig(theme: 'light' | 'dark'): ChartThemeConfig {
  return chartThemes[theme] || chartThemes.light
}

/**
 * 创建K线图表基础配置.
 */
export function createKLineChartOption(
  data: Array<{ date: string; open: number; close: number; high: number; low: number; volume?: number }>,
  maData: Record<string, Array<{ value: number }>>,
  theme: 'light' | 'dark',
  chartType: 'candle' | 'line',
  showRightAxis: boolean,
  priceAxisType: 'value' | 'log',
  marketType?: MarketType
): any {
  const themeConfig = getThemeConfig(theme)
  const dates = data.map(d => d.date)

  // 基础配置
  const baseOption = getKLineBaseOption(theme, dates)

  // K线数据格式化
  const klineData = data.map(d => [d.open, d.close, d.low, d.high])

  // K线系列配置
  const klineSeries = getKLineSeriesOption(
    chartType === 'candle' ? 'candlestick' : 'line',
    klineData,
    theme
  )

  // 均线系列配置
  const maSeries: any[] = []
  const maColors = ['#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899']

  for (const [period, values] of Object.entries(maData)) {
    if (values && values.length > 0) {
      maSeries.push({
        name: `MA${period}`,
        type: 'line',
        data: values.map(v => v.value),
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: maColors[parseInt(period) % maColors.length] },
        symbol: 'none'
      })
    }
  }

  // 合并配置
  const option = {
    ...baseOption,
    series: [klineSeries, ...maSeries],
    yAxis: {
      ...baseOption.yAxis,
      position: showRightAxis ? 'right' : 'left',
      type: priceAxisType
    }
  }

  return option
}

/**
 * 更新图表数据.
 */
export function updateChartData(
  chartInstance: ECharts | null,
  data: Array<{ date: string; open: number; close: number; high: number; low: number }>,
  maData: Record<string, Array<{ value: number }>>
): void {
  if (!chartInstance) return

  const klineData = data.map(d => [d.open, d.close, d.low, d.high])

  chartInstance.setOption({
    xAxis: { data: data.map(d => d.date) },
    series: [
      { data: klineData },
      ...Object.entries(maData).map(([period, values], index) => ({
        name: `MA${period}`,
        data: values.map(v => v.value)
      }))
    ]
  }, false, true)  // notMerge: false, lazyUpdate: true
}

/**
 * 处理图表类型切换.
 */
export function handleChartTypeChange(
  chartInstance: ECharts | null,
  newType: 'candle' | 'line',
  theme: 'light' | 'dark'
): void {
  if (!chartInstance) return

  chartInstance.setOption({
    series: [{
      type: newType === 'candle' ? 'candlestick' : 'line'
    }]
  }, false, true)
}

/**
 * 处理主题切换.
 */
export function handleThemeChange(
  chartInstance: ECharts | null,
  newTheme: 'light' | 'dark'
): void {
  if (!chartInstance) return

  const themeConfig = getThemeConfig(newTheme)

  chartInstance.setOption({
    backgroundColor: newTheme === 'dark' ? '#1a1a2e' : '#ffffff',
    xAxis: {
      axisLine: { lineStyle: { color: themeConfig.axisLine } },
      splitLine: { lineStyle: { color: themeConfig.gridLine } }
    },
    yAxis: {
      axisLine: { lineStyle: { color: themeConfig.axisLine } },
      splitLine: { lineStyle: { color: themeConfig.gridLine } }
    }
  }, false, true)
}

/**
 * 处理价格坐标模式切换.
 */
export function handlePriceAxisTypeChange(
  chartInstance: ECharts | null,
  newType: 'value' | 'log'
): void {
  if (!chartInstance) return

  chartInstance.setOption({
    yAxis: { type: newType }
  }, false, true)
}

/**
 * 处理右侧价格轴切换.
 */
export function handleRightAxisToggle(
  chartInstance: ECharts | null,
  show: boolean
): void {
  if (!chartInstance) return

  chartInstance.setOption({
    yAxis: { position: show ? 'right' : 'left' }
  }, false, true)
}

/**
 * 处理均线显示切换.
 */
export function handleMAVisibilityChange(
  chartInstance: ECharts | null,
  visibleMA: string[],
  allMaPeriods: string[]
): void {
  if (!chartInstance) return

  const seriesVisibility = allMaPeriods.map(period => ({
    name: `MA${period}`,
    visible: visibleMA.includes(period)
  }))

  for (const { name, visible } of seriesVisibility) {
    chartInstance.dispatchAction({
      type: visible ? 'show' : 'hide',
      seriesName: name
    })
  }
}

/**
 * 创建涨跌停标记点.
 */
export function createLimitUpDownMarks(
  data: Array<{ date: string; open: number; close: number; high: number; low: number }>,
  limitThreshold: number,
  marketType: string
): any[] {
  const marks: any[] = []

  for (let i = 0; i < data.length; i++) {
    const item = data[i]
    const prevClose = i > 0 ? data[i - 1].close : item.open

    const limitUpPrice = calculateLimitUpPrice(prevClose, limitThreshold)
    const limitDownPrice = calculateLimitDownPrice(prevClose, limitThreshold)

    if (isLimitUp(item.close, limitUpPrice, marketType)) {
      marks.push({
        name: '涨停',
        coord: [item.date, item.high],
        itemStyle: { color: '#ef4444' },
        label: { show: true, formatter: '停' }
      })
    }

    if (isLimitDown(item.close, limitDownPrice, marketType)) {
      marks.push({
        name: '跌停',
        coord: [item.date, item.low],
        itemStyle: { color: '#22c55e' },
        label: { show: true, formatter: '停' }
      })
    }
  }

  return marks
}

/**
 * 创建缺口标记.
 */
export function createGapMarks(
  data: Array<{ date: string; open: number; close: number; high: number; low: number }>
): any[] {
  const marks: any[] = []

  for (let i = 1; i < data.length; i++) {
    const prev = data[i - 1]
    const curr = data[i]

    // 缺口检测：当前开盘价与前一收盘价差距超过一定阈值
    const gapThreshold = Math.abs(prev.close - prev.open) * 0.5
    const gapUp = curr.open - prev.close > gapThreshold
    const gapDown = prev.close - curr.open > gapThreshold

    if (gapUp) {
      marks.push({
        name: '向上缺口',
        coord: [curr.date, curr.open],
        yAxis: curr.open,
        itemStyle: { color: '#f59e0b' },
        label: { show: true, formatter: '↑' }
      })
    }

    if (gapDown) {
      marks.push({
        name: '向下缺口',
        coord: [curr.date, curr.open],
        yAxis: curr.open,
        itemStyle: { color: '#3b82f6' },
        label: { show: true, formatter: '↓' }
      })
    }
  }

  return marks
}

/**
 * 获取市场类型配置.
 */
export function getMarketTypeConfig(
  symbolCode: string,
  symbolName: string
): {
  marketType: MarketType
  marketConfig: any
  hasLimitUpDown: boolean
  needAdjustment: boolean
} {
  const marketType = identifyMarketTypeByName(symbolCode, symbolName)
  const marketConfig = getMarketConfig(marketType)
  const config = marketConfigs[marketType] || {}

  return {
    marketType,
    marketConfig,
    hasLimitUpDown: config.hasLimitUpDown || false,
    needAdjustment: config.needAdjustment || false
  }
}