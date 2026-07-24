<template>
  <div class="chart-dashboard" ref="dashboardEl">
    <ChartToolbar
      v-if="toolbarVisible"
      :profile="profile"
      :chart-ref="chartRef"
      :theme="theme"
      @theme-toggle="handleThemeToggle"
      @export-image="handleExportImage"
    />

    <div v-if="errorMsg" class="chart-error">{{ errorMsg }}</div>
    <div v-else :id="chartContainerId" class="klinechart-container" :class="{ dark: theme === 'dark' }" ref="chartContainerRef" />

    <RangeStatsPanel
      v-if="rangeStats"
      :stats="rangeStats"
      @close="rangeStats = null"
    />

    <div class="feature-controls">
      <div v-if="profile.features.adjustment" class="control-row">
        <el-radio-group v-model="adjustmentType" size="small" @change="handleAdjustmentChange">
          <el-radio-button value="none">不复权</el-radio-button>
          <el-radio-button value="forward">前复权</el-radio-button>
          <el-radio-button value="backward">后复权</el-radio-button>
        </el-radio-group>
      </div>
      <div v-if="profile.features.logScale" class="control-row">
        <el-button size="small" :type="logScale ? 'primary' : ''" @click="toggleLogScale">
          {{ logScale ? '对数坐标' : '线性坐标' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { init, dispose, type Chart, type KLineData, type Styles } from 'klinecharts'
import { useThemeStore } from '@/stores/theme'
import {
  getMarketProfile, identifyMarket, registerMarketPresets, getLimitThreshold,
  type MarketProfile, type AdjustmentType,
} from '@/composables/useMarketProfile'
import { convertToKLineData } from '@/composables/useDataLoader'
import { createChartStyles } from '@/composables/useKLineChart'
import { useKeyboardNav } from '@/composables/useKeyboardNav'
import { lightStyles, darkStyles } from '@/chartExtensions/themes'
import ChartToolbar from './ChartToolbar.vue'
import RangeStatsPanel from './RangeStatsPanel.vue'
import logger from '@/services/logger'

if (getMarketProfile('stock_cn') === undefined) registerMarketPresets()

const props = defineProps<{
  marketId: string; symbolId: string; symbolCode: string; symbolName?: string
  period?: string; data?: any[]; loading?: boolean; toolbarVisible?: boolean
}>()

const emit = defineEmits<{
  (e: 'adjustmentChange', type: AdjustmentType): void
  (e: 'fetchData', params: { symbolId: string; period: string }): void
}>()

const themeStore = useThemeStore()
const chartContainerRef = ref<HTMLElement | null>(null)
const chartContainerId = `kc-${crypto.randomUUID().slice(0, 6)}`
const theme = computed(() => themeStore.theme)
const adjustmentType = ref<AdjustmentType>('none')
const logScale = ref(false)
const rangeStats = ref<any>(null)
const chartRef = ref<Chart | null>(null)
const errorMsg = ref('')

// chartRef.value 为权威引用，chart 别名仅供内部便捷访问，两者必须同步
let chart: Chart | null = null

const profile = computed<MarketProfile>(() =>
  getMarketProfile(props.marketId) || identifyMarket(props.symbolCode, props.symbolName)
)

const currentStyles = computed<Styles>(() =>
  createChartStyles(theme.value === 'dark' ? darkStyles : lightStyles, profile.value)
)

// === init ===

function initChart(): void {
  if (!chartContainerRef.value) { errorMsg.value = '容器DOM未就绪'; return }
  const p = profile.value
  const dom = chartContainerRef.value
  if (chart) { dispose(dom); chart = null; chartRef.value = null }

  chart = init(dom, { styles: currentStyles.value, locale: 'zh-CN' })
  if (!chart) { errorMsg.value = 'KLineChart init() 返回 null (容器尺寸: '+dom.offsetWidth+'x'+dom.offsetHeight+')'; return }

  chart.setSymbol({ ticker: props.symbolCode || 'UNKNOWN', pricePrecision: p.pricePrecision, volumePrecision: 0 })
  chart.setPeriod({ type: 'day', span: 1 })
  chart.setOffsetRightDistance(p.features.continuousTrading ? 80 : 50)
  chartRef.value = chart

  if (props.data?.length) {
    setChartData(props.data, p)
  }

  // 默认指标 (v10: MA叠加主图, MACD用短参数适配小数据量)
  for (const ind of p.defaultIndicators) {
    try {
      if (ind === 'MA') {
        chart.createIndicator({ name: 'MA', paneId: 'candle_pane' })
      } else if (ind === 'MACD') {
        chart.createIndicator('MACD')
        chart.overrideIndicator({ name: 'MACD', styles: { bars: [{ style: 'fill' }] } })
      } else {
        chart.createIndicator(ind)
      }
    } catch { /* ignore */ }
  }

  applyFeatures(p)


  watch(() => props.data, (newData) => {
    if (newData?.length && chart) {
      setChartData(newData, p)
      applyFeatures(p)
    }
  }, { deep: true })
}

/** v10: 通过 setDataLoader + resetData 注入数据 */
function setChartData(data: any[], p: MarketProfile): void {
  if (!chart) return
  const klineData = convertToKLineData(data, p, { adjustmentType: adjustmentType.value })
  chart.setDataLoader({
    getBars: ({ callback }) => callback(klineData, { forward: false })
  })
  chart.resetData()
}

// === 市场特性 ===

function applyFeatures(p: MarketProfile): void {
  if (!chart || !props.data?.length) return
  const d = props.data

  if (p.features.limitUpDown) addLimitUpDown(d)
  if (p.features.gapDetection) addGaps(d)
  if (p.features.suspensionDetection) addSuspension(d)
  if (p.features.dividendMarkers) addDividends(d)
}

function addLimitUpDown(data: any[]): void {
  if (!chart || data.length < 2) return
  const p = profile.value
  const prevClose = Number(data[data.length - 1].close)
  const t = getLimitThreshold(p, props.symbolCode, props.symbolName)
  if (t <= 0) return
  chart.createOverlay({
    name: 'limitUpDown',
    extendData: {
      limitUpPrice: +(prevClose * (1 + t / 100)).toFixed(p.pricePrecision),
      limitDownPrice: +(prevClose * (1 - t / 100)).toFixed(p.pricePrecision),
      prevClose,
    },
    points: [],
  })
}

function addGaps(data: any[]): void {
  if (!chart || data.length < 2) return
  const gaps: any[] = []
  for (let i = 1; i < data.length; i++) {
    const ph = Number(data[i - 1].high), pl = Number(data[i - 1].low)
    const ch = Number(data[i].high), cl = Number(data[i].low)
    if (cl > ph) gaps.push({ x: i, y: ph, type: 'up', label: `+${((cl - ph) / ph * 100).toFixed(1)}%` })
    else if (ch < pl) gaps.push({ x: i, y: pl, type: 'down', label: `-${((pl - ch) / pl * 100).toFixed(1)}%` })
  }
  if (gaps.length) chart.createOverlay({ name: 'gapMarker', extendData: { gaps }, points: [] })
}

function addSuspension(data: any[]): void {
  if (!chart || data.length < 2) return
  const sorted = [...data].sort((a, b) =>
    new Date(a.date || a.timestamp).getTime() - new Date(b.date || b.timestamp).getTime()
  )
  const marks: any[] = []
  for (let i = 1; i < sorted.length; i++) {
    const diff = Math.floor((new Date(sorted[i].date || sorted[i].timestamp).getTime() -
      new Date(sorted[i - 1].date || sorted[i - 1].timestamp).getTime()) / 86400000)
    if (diff > 7) marks.push({ start: i - 1, end: i, days: diff, label: `停牌${diff}天` })
  }
  if (marks.length) chart.createOverlay({ name: 'simpleTag', extendData: { marks }, points: [] })
}

function addDividends(data: any[]): void {
  // 基于 >5% 跳空启发式检测除权事件，非真实除权数据，后续需对接除权因子 API
  if (!chart) return
  const divs: any[] = []
  for (let i = 1; i < data.length; i++) {
    const pc = Number(data[i - 1].close), cc = Number(data[i].close)
    if (pc > 0 && Math.abs(cc - pc) / pc > 0.05) {
      const coord = chart.convertFromPixel({ x: 0, y: pc })
      divs.push({ x: 0, y: coord?.price ?? pc, label: 'DR', date: data[i].date || data[i].timestamp })
    }
  }
  if (divs.length) chart.createOverlay({ name: 'dividendMarker', extendData: { dividends: divs }, points: [] })
}

// === 交互 ===

function toggleLogScale(): void {
  logScale.value = !logScale.value
  if (!chart || !props.data?.length) return
  const p = profile.value
  const raw = props.data
  if (logScale.value) {
    const logData = raw.map((d: any) => ({
      ...d, open: +d.open > 0 ? Math.log10(+d.open) : d.open,
      high: +d.high > 0 ? Math.log10(+d.high) : d.high,
      low: +d.low > 0 ? Math.log10(+d.low) : d.low,
      close: +d.close > 0 ? Math.log10(+d.close) : d.close,
    }))
    setChartData(logData, p)
  } else {
    setChartData(raw, p)
  }
  applyFeatures(p)
}

function handleAdjustmentChange(type: AdjustmentType): void {
  adjustmentType.value = type
  emit('adjustmentChange', type)
}

function handleThemeToggle(): void {
  themeStore.toggleTheme()
  if (chart) chart.setStyles(currentStyles.value)
}

function handleExportImage(): void {
  if (!chart) return
  const url = chart.getConvertPictureUrl(true, 'png')
  if (!url) return
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.symbolCode}_${new Date().toISOString().slice(0, 10)}.png`
  a.click()
}

useKeyboardNav(() => chart)

// 监听全局主题变化（Navbar触发时同步图表样式）
watch(currentStyles, (styles) => {
  if (chart) chart.setStyles(styles)
})

onMounted(async () => {
  await nextTick()
  try { initChart() } catch (e: any) {
    errorMsg.value = 'KLineChart 初始化失败: ' + (e?.message || String(e))
    logger.error('ChartDashboard初始化失败', e)
  }
})
onUnmounted(() => { if (chart && chartContainerRef.value) { dispose(chartContainerRef.value); chart = null; chartRef.value = null } })
</script>

<style scoped>
.chart-dashboard {
  display: flex; flex-direction: column; height: 100%; min-height: 400px;
  background: #ffffff;
}
.chart-dashboard:has(.klinechart-container.dark) { background: #1a1a2e; }
.klinechart-container { flex: 1; min-height: 300px; width: 100%; background: #ffffff; }
.klinechart-container.dark { background: #1a1a2e; }
.chart-error { flex: 1; min-height: 300px; display:flex; align-items:center; justify-content:center; color:#ef4444; font-size:14px; padding:20px; text-align:center; }
.feature-controls { display: flex; justify-content: center; gap: 8px; padding: 6px; border-top: 1px solid var(--border-color, #e5e7eb); flex-wrap: wrap; }
.control-row { display: flex; align-items: center; }
</style>
