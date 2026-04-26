<template>
  <div class="pro-chart-panel" :class="themeClass">
    <!-- 加载状态遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="skeleton-chart">
        <div class="skeleton-header"></div>
        <div class="skeleton-body">
          <div class="skeleton-line"></div>
          <div class="skeleton-bars"></div>
        </div>
      </div>
    </div>

    <!-- 主图区域 -->
    <div class="main-chart-section">
      <KLineChart
        ref="klineChartRef"
        :data="chartData"
        :maData="maData"
        :symbolName="symbolName"
        :symbolId="symbolId"
        :theme="currentTheme"
        :volumeMaximized="volumeMaximized"
        :macdMaximized="macdMaximized"
        @fetchData="$emit('fetchData')"
        @chartTypeChange="handleChartTypeChange"
        @maChange="handleMAChange"
        @toggleVolume="toggleVolumeMaximize"
        @toggleMacd="toggleMacdMaximize"
        @adjustmentChange="(type) => $emit('adjustmentChange', type)"
      />
    </div>

    <!-- 副图区域 -->
    <div class="sub-chart-section" :style="{ height: `${subChartHeight}px` }">
      <!-- 成交量 -->
      <div class="volume-chart-wrapper" :style="{ height: `${volumeHeight}%` }">
        <VolumeChart
          ref="volumeChartRef"
          :data="chartData"
          :theme="currentTheme"
          :volData="volData"
          :minimized="macdMaximized"
          @volChange="handleVOLChange"
        />
      </div>

      <!-- 可拖拽分隔线 -->
      <div
        class="chart-divider"
        v-show="!volumeMaximized && !macdMaximized"
        @mousedown="startDragDivider"
      >
        <span class="divider-line"></span>
      </div>

      <!-- MACD -->
      <div class="macd-chart-wrapper" :style="{ height: `${100 - volumeHeight}%` }">
        <MACDChart
          ref="macdChartRef"
          :data="macdData"
          :dates="dates"
          :theme="currentTheme"
          :minimized="volumeMaximized"
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
 * 使用全局主题store管理主题切换.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 * Updated: 2026-04-17 - 使用全局主题store，移除独立主题切换按钮
 */
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { FullScreen, Aim } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import KLineChart from './KLineChart.vue'
import VolumeChart from './VolumeChart.vue'
import MACDChart from './MACDChart.vue'
import { useThemeStore } from '@/stores/theme'

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
  /** 标的ID */
  symbolId?: string
  /** 加载状态 */
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  indicators: () => ({ ma: {}, macd: { dif: [], dea: [], macd: [] } }),
  symbolName: '',
  symbolId: '',
  loading: false
})

// Emits定义
const emit = defineEmits<{
  (e: 'fetchData'): void
  (e: 'chartTypeChange', type: 'candle' | 'line'): void
  (e: 'maChange', periods: string[]): void
  (e: 'macdParamChange', params: { fast: number; slow: number; signal: number }): void
  (e: 'adjustmentChange', type: string): void
}>()

// 子组件refs
const klineChartRef = ref<InstanceType<typeof KLineChart> | null>(null)
const volumeChartRef = ref<InstanceType<typeof VolumeChart> | null>(null)
const macdChartRef = ref<InstanceType<typeof MACDChart> | null>(null)

// 使用全局主题store
const themeStore = useThemeStore()
const currentTheme = computed<'light' | 'dark'>(() => themeStore.theme)
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
  if (!props.indicators?.vol) return {}
  return props.indicators.vol
})

const symbolName = computed(() => props.symbolName)
const symbolId = computed(() => props.symbolId)

// 副图高度状态
const subChartHeight = ref<number>(200)
const volumeHeight = ref<number>(50)  // 成交量占比百分比
const volumeMaximized = ref<boolean>(false)
const macdMaximized = ref<boolean>(false)
const isDragging = ref<boolean>(false)

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
 * 切换成交量副图最大化.
 */
const toggleVolumeMaximize = () => {
  volumeMaximized.value = !volumeMaximized.value
  if (volumeMaximized.value) {
    volumeHeight.value = 95
    macdMaximized.value = false
  } else {
    volumeHeight.value = 50
  }
  resizeAll()
}

/**
 * 切换MACD副图最大化.
 */
const toggleMacdMaximize = () => {
  macdMaximized.value = !macdMaximized.value
  if (macdMaximized.value) {
    volumeHeight.value = 5
    volumeMaximized.value = false
  } else {
    volumeHeight.value = 50
  }
  resizeAll()
}

/**
 * 开始拖拽分隔线.
 */
const startDragDivider = (e: MouseEvent) => {
  isDragging.value = true
  e.preventDefault()

  document.addEventListener('mousemove', handleDragDivider)
  document.addEventListener('mouseup', stopDragDivider)
}

/**
 * 处理分隔线拖拽.
 */
const handleDragDivider = (e: MouseEvent) => {
  if (!isDragging.value) return

  // 获取副图区域的边界
  const subSection = document.querySelector('.sub-chart-section')
  if (!subSection) return

  const rect = subSection.getBoundingClientRect()
  const relativeY = e.clientY - rect.top
  const newHeight = (relativeY / rect.height) * 100

  // 限制范围在10%到90%之间
  volumeHeight.value = Math.min(90, Math.max(10, newHeight))

  // 重置最大化状态
  volumeMaximized.value = false
  macdMaximized.value = false

  resizeAll()
}

/**
 * 停止拖拽分隔线.
 */
const stopDragDivider = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleDragDivider)
  document.removeEventListener('mouseup', stopDragDivider)
}

/**
 * 绑定图表联动.
 * 使用echarts.connect实现主副图dataZoom同步.
 */
const bindChartsLink = () => {
  const klineInstance = klineChartRef.value?.getChartInstance()
  const volumeInstance = volumeChartRef.value?.getChartInstance()
  const macdInstance = macdChartRef.value?.getChartInstance()

  if (!klineInstance) return

  // 设置相同的group，实现联动
  klineInstance.group = 'pro-charts'
  if (volumeInstance) volumeInstance.group = 'pro-charts'
  if (macdInstance) macdInstance.group = 'pro-charts'

  // 连接所有图表
  echarts.connect('pro-charts')
}

/**
 * 解绑图表联动.
 */
const unbindChartsLink = () => {
  echarts.disconnect('pro-charts')
}

/**
 * Resize所有图表.
 * 添加延迟确保DOM更新完成.
 */
const resizeAll = () => {
  nextTick(() => {
    klineChartRef.value?.resizeChart()
    volumeChartRef.value?.resizeChart()
    macdChartRef.value?.resizeChart()
  })
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

/* 加载状态遮罩 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 100;
}

.theme-dark .loading-overlay {
  background: rgba(26, 26, 46, 0.9);
}

/* 骨架屏 */
.skeleton-chart {
  width: 90%;
  height: 80%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-header {
  height: 40px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.theme-dark .skeleton-header {
  background: linear-gradient(90deg, #2a2a3e 25%, #3a3a4e 50%, #2a2a3e 75%);
  background-size: 200% 100%;
}

.skeleton-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  height: 60%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.theme-dark .skeleton-line {
  background: linear-gradient(90deg, #2a2a3e 25%, #3a3a4e 50%, #2a2a3e 75%);
  background-size: 200% 100%;
}

.skeleton-bars {
  height: 40%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.theme-dark .skeleton-bars {
  background: linear-gradient(90deg, #2a2a3e 25%, #3a3a4e 50%, #2a2a3e 75%);
  background-size: 200% 100%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 主题相关 */
.theme-light {
  background: #ffffff;
}

.theme-dark {
  background: #1a1a2e;
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

/* 副图控制按钮 */
.sub-chart-controls {
  position: absolute;
  top: 4px;
  right: 8px;
  z-index: 5;
  display: flex;
  gap: 4px;
}

.sub-chart-controls .el-button {
  padding: 4px;
  color: var(--fdas-text-secondary);
  opacity: 0.6;
  transition: opacity 0.2s;
}

.sub-chart-controls .el-button:hover {
  opacity: 1;
}

.theme-dark .sub-chart-controls .el-button {
  color: #8b8b9b;
}

/* 可拖拽分隔线 */
.chart-divider {
  position: relative;
  height: 12px;
  cursor: row-resize;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.chart-divider:hover .divider-line {
  background-color: var(--fdas-primary);
  opacity: 1;
}

.divider-line {
  width: 60%;
  height: 2px;
  background-color: var(--fdas-border-light);
  opacity: 0.5;
  transition: all 0.2s;
  border-radius: 1px;
}

.theme-dark .divider-line {
  background-color: #3a3a4e;
}
</style>