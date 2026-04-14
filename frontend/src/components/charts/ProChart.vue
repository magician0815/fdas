<template>
  <div class="pro-chart-panel" :class="themeClass">
    <!-- 主题切换 -->
    <div class="theme-switch">
      <el-switch
        v-model="isDarkTheme"
        size="small"
        active-text="夜间"
        inactive-text="白天"
        @change="handleThemeChange"
      />
    </div>

    <!-- 主图区域 -->
    <div class="main-chart-section">
      <KLineChart
        ref="klineChartRef"
        :data="chartData"
        :maData="maData"
        :symbolName="symbolName"
        :theme="currentTheme"
        @fetchData="$emit('fetchData')"
        @chartTypeChange="handleChartTypeChange"
        @maChange="handleMAChange"
      />
    </div>

    <!-- 副图区域 -->
    <div class="sub-chart-section">
      <!-- 成交量 -->
      <div class="volume-chart-wrapper">
        <VolumeChart
          ref="volumeChartRef"
          :data="chartData"
          :theme="currentTheme"
          :volData="volData"
          @volChange="handleVOLChange"
        />
      </div>

      <!-- MACD -->
      <div class="macd-chart-wrapper">
        <MACDChart
          ref="macdChartRef"
          :data="macdData"
          :dates="dates"
          :theme="currentTheme"
          @paramChange="handleMACDParamChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 专业行情图表面板组件.
 *
 * 组合K线主图、成交量副图、MACD副图，实现联动交互.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import KLineChart from './KLineChart.vue'
import VolumeChart from './VolumeChart.vue'
import MACDChart from './MACDChart.vue'

// Props定义
interface Props {
  /** 原始K线数据 */
  data: Array<{
    date: string
    open: number | string
    close: number | string
    high: number | string
    low: number | string
    volume?: number | string
    change_pct?: number | string
    amplitude?: number | string
  }>
  /** 技术指标数据 */
  indicators?: {
    ma?: Record<string, Array<{ value: number }>>
    macd?: {
      dif: number[]
      dea: number[]
      macd: number[]
    }
  }
  /** 标的名称 */
  symbolName?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  indicators: () => ({ ma: {}, macd: { dif: [], dea: [], macd: [] } }),
  symbolName: ''
})

// Emits定义
const emit = defineEmits<{
  (e: 'fetchData'): void
  (e: 'themeChange', theme: 'light' | 'dark'): void
  (e: 'chartTypeChange', type: 'candle' | 'line'): void
  (e: 'maChange', periods: string[]): void
  (e: 'macdParamChange', params: { fast: number; slow: number; signal: number }): void
}>()

// 子组件refs
const klineChartRef = ref<InstanceType<typeof KLineChart> | null>(null)
const volumeChartRef = ref<InstanceType<typeof VolumeChart> | null>(null)
const macdChartRef = ref<InstanceType<typeof MACDChart> | null>(null)

// 主题状态 - 从localStorage恢复用户偏好
const isDarkTheme = ref<boolean>(
  localStorage.getItem('fdas_theme') === 'dark'
)
const currentTheme = computed<'light' | 'dark'>(() => isDarkTheme.value ? 'dark' : 'light')
const themeClass = computed(() => `theme-${currentTheme.value}`)

// 图表类型
const chartType = ref<'candle' | 'line'>('candle')

// 均线显示设置
const visibleMA = ref<string[]>(['5', '10', '20', '60'])

// 计算属性
const chartData = computed(() => props.data)
const dates = computed(() => props.data.map(d => d.date))

const maData = computed(() => {
  if (!props.indicators?.ma) return {}
  return props.indicators.ma
})

const macdData = computed(() => {
  if (!props.indicators?.macd) return { dif: [], dea: [], macd: [] }
  return props.indicators.macd
})

const volData = computed(() => {
  // 成交量均线需要单独计算（暂不实现）
  return {}
})

const symbolName = computed(() => props.symbolName)

/**
 * 处理主题切换.
 */
const handleThemeChange = (isDark: boolean) => {
  // 保存主题设置到localStorage
  localStorage.setItem('fdas_theme', isDark ? 'dark' : 'light')
  emit('themeChange', isDark ? 'dark' : 'light')
  // 子组件会通过watch自动响应主题变化
}

/**
 * 处理图表类型切换.
 */
const handleChartTypeChange = (type: 'candle' | 'line') => {
  chartType.value = type
  emit('chartTypeChange', type)
}

/**
 * 处理均线显示变化.
 */
const handleMAChange = (periods: string[]) => {
  visibleMA.value = periods
  emit('maChange', periods)
}

/**
 * 处理成交量均线变化.
 */
const handleVOLChange = (periods: string[]) => {
  // 暂不处理
}

/**
 * 处理MACD参数变化.
 */
const handleMACDParamChange = (params: { fast: number; slow: number; signal: number }) => {
  emit('macdParamChange', params)
}

/**
 * 绑定图表联动.
 */
const bindChartsLink = () => {
  const klineInstance = klineChartRef.value?.getChartInstance()
  const volumeInstance = volumeChartRef.value?.getChartInstance()
  const macdInstance = macdChartRef.value?.getChartInstance()

  if (klineInstance && volumeInstance) {
    klineInstance.group = 'pro-charts'
    volumeInstance.group = 'pro-charts'
    if (macdInstance) {
      macdInstance.group = 'pro-charts'
    }
    echarts.connect('pro-charts')
  }
}

/**
 * 解绑图表联动.
 */
const unbindChartsLink = () => {
  echarts.disconnect('pro-charts')
}

/**
 * Resize所有图表.
 */
const resizeAll = () => {
  klineChartRef.value?.resizeChart()
  volumeChartRef.value?.resizeChart()
  macdChartRef.value?.resizeChart()
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    bindChartsLink()
  })
}, { deep: true })

// 生命周期
onMounted(() => {
  nextTick(() => {
    bindChartsLink()
    window.addEventListener('resize', resizeAll)
  })
})

// 清理（需要在父组件手动调用或通过onUnmounted）
const cleanup = () => {
  unbindChartsLink()
  window.removeEventListener('resize', resizeAll)
}

// 暴露方法
defineExpose({
  resizeAll,
  bindChartsLink,
  unbindChartsLink,
  cleanup
})
</script>

<style scoped>
.pro-chart-panel {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  overflow: hidden;
}

/* 主题相关 */
.theme-light {
  background: #ffffff;
}

.theme-dark {
  background: #1a1a2e;
}

/* 主题切换按钮 */
.theme-switch {
  position: absolute;
  top: 8px;
  right: 12px;
  z-index: 10;
}

/* 主图区域 */
.main-chart-section {
  flex: 1;
  min-height: 300px;
  max-height: 400px;
  border-bottom: 1px solid var(--fdas-border-light);
}

/* 副图区域 */
.sub-chart-section {
  display: flex;
  flex-direction: column;
  height: 200px;
  min-height: 150px;
}

.volume-chart-wrapper {
  height: 50%;
  border-bottom: 1px solid var(--fdas-border-light);
}

.macd-chart-wrapper {
  height: 50%;
}
</style>