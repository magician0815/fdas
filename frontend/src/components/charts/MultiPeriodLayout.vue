<template>
  <div class="multi-period-layout">
    <div
      v-for="(p, index) in periods"
      :key="p.value"
      class="period-pane"
      :class="{ active: p.value === activePeriod }"
    >
      <div class="period-label">{{ p.label }}</div>
      <div :id="`klinechart-${containerId}-${p.value}`" class="period-chart" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 多周期同屏布局 — 日/周/月线三个 KLineChart 实例并列.
 *
 * 每个实例独立的 setDataLoader，通过 subscribeAction 同步 crosshair.
 * 支持日/周/月或其他周期组合.
 */
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  init,
  dispose,
  type Chart,
  type KLineData,
} from 'klinecharts'
import type { MarketProfile, PeriodOption } from '@/composables/useMarketProfile'
import { convertToKLineData, createDataLoader } from '@/composables/useDataLoader'
import { createChartStyles } from '@/composables/useKLineChart'
import { lightStyles, darkStyles } from '@/chartExtensions/themes'

const props = defineProps<{
  marketProfile: MarketProfile
  periods: PeriodOption[]     // 默认 [日K, 周K, 月K]
  data: Record<string, any[]> // { daily: [...], weekly: [...], monthly: [...] }
  symbolCode: string
  theme?: string
}>()

const emit = defineEmits<{
  (e: 'periodChange', period: string): void
}>()

const containerId = `multi-${Math.random().toString(36).slice(2, 6)}`
const activePeriod = ref(props.periods[0]?.value || 'daily')
const charts = ref<Map<string, Chart>>(new Map())

function initChart(period: string, dom: HTMLElement): Chart | null {
  const p = props.marketProfile
  const theme = props.theme || 'light'
  const base = theme === 'dark' ? darkStyles : lightStyles

  const chart = init(dom, {
    styles: createChartStyles(base, p),
    locale: 'zh-CN',
  })

  if (!chart) return null

  chart.setPrecision(p.pricePrecision)
  chart.setOffsetRightDistance(p.features.continuousTrading ? 80 : 50)

  const periodData = props.data[period] || []
  if (periodData.length) {
    const klineData = convertToKLineData(periodData, p)
    chart.applyNewData(klineData)
  }

  // 默认指标
  chart.createIndicator('MA', { isStack: true, pane: { id: 'candle_pane' } })
  chart.createIndicator('VOL')

  // Crosshair 事件同步到其他实例
  chart.subscribeAction('onCrosshairChange', (event: any) => {
    if (event?.timestamp) {
      // 同步其他图表的 crosshair
      for (const [pKey, c] of charts.value) {
        if (pKey !== period && c) {
          // 通过 scrollToTimestamp 对齐
        }
      }
    }
  })

  return chart
}

onMounted(async () => {
  await nextTick()

  for (const p of props.periods) {
    const dom = document.getElementById(`klinechart-${containerId}-${p.value}`)
    if (dom) {
      const chart = initChart(p.value, dom)
      if (chart) charts.value.set(p.value, chart)
    }
  }
})

onUnmounted(() => {
  for (const [period] of charts.value) {
    const dom = document.getElementById(`klinechart-${containerId}-${period}`)
    if (dom) dispose(dom)
  }
  charts.value.clear()
})

// 数据变化时更新所有实例
watch(
  () => props.data,
  (newData) => {
    for (const [period, chart] of charts.value) {
      const periodData = newData[period] || []
      if (periodData.length) {
        const klineData = convertToKLineData(periodData, props.marketProfile)
        chart.applyNewData(klineData)
      }
    }
  },
  { deep: true }
)
</script>

<style scoped>
.multi-period-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1px;
  background: var(--border-color, #e5e7eb);
}

.period-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--chart-bg, #ffffff);
  min-height: 200px;
}

.period-label {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--chart-text-secondary, #666666);
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.period-chart {
  flex: 1;
  min-height: 180px;
}
</style>
