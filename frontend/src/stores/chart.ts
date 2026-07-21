/**
 * 图表全局状态管理 (Pinia Store).
 *
 * 借鉴 KLineChart ChartStore 的单向数据流设计:
 * API → Store (数据+指标) → Composables → Pane → Canvas
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { KLineData } from 'klinecharts'
import type { AdjustmentType } from '@/composables/useMarketProfile'

export type ChartType = 'candle' | 'line'
export type PriceAxisType = 'value' | 'log'

export const useChartStore = defineStore('chart', () => {
  // === 数据 ===
  const rawData = ref<KLineData[]>([])
  const symbolId = ref('')
  const symbolCode = ref('')
  const symbolName = ref('')
  const period = ref('daily')
  const loading = ref(false)
  const error = ref<string | null>(null)

  // === 视图状态 ===
  const chartType = ref<ChartType>('candle')
  const priceAxisType = ref<PriceAxisType>('value')
  const visibleMA = ref<string[]>(['5', '10', '20', '60'])
  const showRightAxis = ref(false)
  const adjustmentType = ref<AdjustmentType>('none')
  const adjustmentFactors = ref<any[]>([])

  // === 副图状态 ===
  const visibleSubCharts = ref<Record<string, boolean>>({})
  const maximizedSlot = ref<string | null>(null)

  // === 画线 ===
  const currentDrawingTool = ref<string | null>(null)
  const drawingColor = ref('#ef4444')
  const drawingLineWidth = ref(2)

  // === 十字光标 ===
  const cursorLocked = ref(false)
  const cursorTimestamp = ref<number | null>(null)

  // === 计算属性 ===
  const dates = computed(() => rawData.value.map(d => d.timestamp))

  // === Actions ===
  function setData(data: KLineData[]): void {
    rawData.value = data
  }

  function setSymbol(id: string, code: string, name?: string): void {
    symbolId.value = id
    symbolCode.value = code
    symbolName.value = name || code
  }

  function setPeriod(p: string): void {
    period.value = p
  }

  function toggleSubChart(id: string): void {
    visibleSubCharts.value[id] = !visibleSubCharts.value[id]
  }

  return {
    rawData, symbolId, symbolCode, symbolName, period, loading, error,
    chartType, priceAxisType, visibleMA, showRightAxis,
    adjustmentType, adjustmentFactors,
    visibleSubCharts, maximizedSlot,
    currentDrawingTool, drawingColor, drawingLineWidth,
    cursorLocked, cursorTimestamp,
    dates,
    setData, setSymbol, setPeriod, toggleSubChart,
  }
})
