/**
 * K线图表配置工具.
 *
 * 从KLineChart.vue提取的图表配置和数据处理函数.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import type ECharts from 'echarts'

// 价格样式类计算
export function getPriceClass(change: number | null): string {
  if (change === null) return ''
  if (change > 0) return 'price-up'
  if (change < 0) return 'price-down'
  return 'price-neutral'
}

// 格式化价格显示
export function formatPriceDisplay(
  close: number,
  prevClose: number,
  precision: number = 4
): {
  currentPrice: string
  changePercent: string
  priceClass: string
} {
  const change = close - prevClose
  const changePercentValue = (change / prevClose) * 100
  const priceClass = getPriceClass(change)

  return {
    currentPrice: close.toFixed(precision),
    changePercent: `${changePercentValue > 0 ? '+' : ''}${changePercentValue.toFixed(2)}%`,
    priceClass
  }
}

// 格式化数据为ECharts格式
export function formatKLineDataForChart(
  data: Array<{
    date: string
    open: number | string
    close: number | string
    high: number | string
    low: number | string
    volume?: number | string
  }>
): {
  dates: string[]
  klineData: [number, number, number, number][]
  volumes: number[]
} {
  const dates: string[] = []
  const klineData: [number, number, number, number][] = []
  const volumes: number[] = []

  for (const item of data) {
    dates.push(item.date)
    klineData.push([
      Number(item.open),
      Number(item.close),
      Number(item.low),
      Number(item.high)
    ])
    volumes.push(Number(item.volume || 0))
  }

  return { dates, klineData, volumes }
}

// 计算区间统计数据
export function calculateRangeStats(
  data: Array<{
    date: string
    open: number
    close: number
    high: number
    low: number
    volume?: number
  }>,
  startIndex: number,
  endIndex: number
): {
  startDate: string
  endDate: string
  startPrice: number
  endPrice: number
  change: number
  changePercent: number
  highPrice: number
  lowPrice: number
  amplitude: number
  avgVolume: number
  totalVolume: number
  count: number
} {
  const rangeData = data.slice(startIndex, endIndex + 1)
  if (rangeData.length === 0) {
    return {
      startDate: '',
      endDate: '',
      startPrice: 0,
      endPrice: 0,
      change: 0,
      changePercent: 0,
      highPrice: 0,
      lowPrice: 0,
      amplitude: 0,
      avgVolume: 0,
      totalVolume: 0,
      count: 0
    }
  }

  const startPrice = rangeData[0].open
  const endPrice = rangeData[rangeData.length - 1].close
  const change = endPrice - startPrice
  const changePercent = (change / startPrice) * 100

  const highPrice = Math.max(...rangeData.map(d => d.high))
  const lowPrice = Math.min(...rangeData.map(d => d.low))
  const amplitude = ((highPrice - lowPrice) / startPrice) * 100

  const volumes = rangeData.map(d => d.volume || 0)
  const totalVolume = volumes.reduce((a, b) => a + b, 0)
  const avgVolume = totalVolume / rangeData.length

  return {
    startDate: rangeData[0].date,
    endDate: rangeData[rangeData.length - 1].date,
    startPrice,
    endPrice,
    change,
    changePercent,
    highPrice,
    lowPrice,
    amplitude,
    avgVolume,
    totalVolume,
    count: rangeData.length
  }
}

// 重置图表视图状态
export function resetChartViewState(chartInstance: ECharts | null): void {
  if (!chartInstance) return

  // 重置数据缩放
  chartInstance.dispatchAction({
    type: 'restore'
  })

  // 清除选中的区域
  chartInstance.dispatchAction({
    type: 'clearSelect'
  })
}

// 定位到指定日期
export function jumpToDateAction(
  chartInstance: ECharts | null,
  dates: string[],
  targetDate: string
): boolean {
  if (!chartInstance || !targetDate) return false

  const index = dates.indexOf(targetDate)
  if (index === -1) return false

  // 使用dataZoom定位到指定日期
  chartInstance.dispatchAction({
    type: 'dataZoom',
    dataZoomIndex: 0,
    startValue: Math.max(0, index - 50),
    endValue: Math.min(dates.length - 1, index + 50)
  })

  return true
}

// 判断是否需要显示涨跌停相关功能
export function hasLimitUpDown(marketType: string): boolean {
  return ['stock_cn', 'stock_hk', 'stock_us', 'futures_cn'].includes(marketType)
}

// 判断是否需要复权功能
export function needsAdjustment(marketType: string): boolean {
  return ['stock_cn', 'stock_hk', 'stock_us'].includes(marketType)
}