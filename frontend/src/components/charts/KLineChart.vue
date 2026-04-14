<template>
  <div class="kline-chart-container">
    <!-- 图表头部工具栏 -->
    <div class="chart-toolbar">
      <div class="toolbar-left">
        <span class="chart-title">{{ symbolName || '选择货币对' }}</span>
        <span v-if="currentPrice" class="current-price" :class="priceClass">
          {{ currentPrice }}
        </span>
        <span v-if="changePercent" class="change-percent" :class="priceClass">
          {{ changePercent }}
        </span>
      </div>
      <div class="toolbar-right">
        <!-- 图表类型切换 -->
        <el-radio-group v-model="chartType" size="small" @change="handleChartTypeChange">
          <el-radio-button value="candle">K线</el-radio-button>
          <el-radio-button value="line">折线</el-radio-button>
        </el-radio-group>
        <!-- 右侧价格轴开关 -->
        <el-tooltip content="显示右侧价格轴" placement="top">
          <el-button size="small" :type="showRightAxis ? 'primary' : 'default'" @click="toggleRightAxis">
            <el-icon><Rank /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 均线显示控制 -->
        <el-dropdown trigger="click" size="small">
          <el-button size="small">
            均线 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-checkbox-group v-model="visibleMA" @change="handleMAChange">
                <el-dropdown-item>
                  <el-checkbox label="5">MA5</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="10">MA10</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="20">MA20</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="60">MA60</el-checkbox>
                </el-dropdown-item>
              </el-checkbox-group>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 图表容器 -->
    <div ref="chartRef" class="chart-area"></div>

    <!-- 无数据提示 -->
    <el-empty v-if="!data || !data.length" description="暂无数据" class="empty-placeholder">
      <el-button type="primary" size="small" @click="$emit('fetchData')">
        获取数据
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
/**
 * K线主图组件.
 *
 * 实现专业K线蜡烛图渲染，支持均线叠加、图表类型切换.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 * Updated: 2026-04-14 - F002: 平滑切换动画、数据范围保持、记住用户选择
 */
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ArrowDown, Rank } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import {
  getKLineBaseOption,
  getKLineSeriesOption,
  getMASeriesOption,
  formatKLineData,
  chartThemes
} from '@/utils/chartConfig'

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
  }>
  /** 均线数据 */
  maData?: Record<string, Array<{ value: number }>>
  /** 标的名称 */
  symbolName?: string
  /** 图表主题 */
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  maData: () => ({}),
  symbolName: '',
  theme: 'light'
})

// Emits定义
const emit = defineEmits<{
  (e: 'fetchData'): void
  (e: 'chartTypeChange', type: 'candle' | 'line'): void
  (e: 'maChange', periods: string[]): void
}>()

// 图表容器ref
const chartRef = ref<HTMLDivElement | null>(null)
// 图表实例
let chartInstance: echarts.ECharts | null = null

// 状态 - 从localStorage恢复用户偏好
const chartType = ref<'candle' | 'line'>(
  (localStorage.getItem('fdas_chart_type') as 'candle' | 'line') || 'candle'
)
const visibleMA = ref<string[]>(['5', '10', '20', '60'])
const showRightAxis = ref<boolean>(
  localStorage.getItem('fdas_right_axis') === 'true'
)

// 当前DataZoom范围（用于切换时保持）
let currentZoomRange = { start: 60, end: 100 }

// 计算属性
const currentPrice = computed(() => {
  if (props.data && props.data.length > 0) {
    const latest = props.data[props.data.length - 1]
    return parseFloat(latest.close as string).toFixed(4)
  }
  return null
})

const changePercent = computed(() => {
  if (props.data && props.data.length >= 2) {
    const latest = props.data[props.data.length - 1]
    const prev = props.data[props.data.length - 2]
    const change = ((parseFloat(latest.close as string) - parseFloat(prev.close as string)) /
                    parseFloat(prev.close as string) * 100).toFixed(2)
    return change.startsWith('-') ? change : '+' + change
  }
  return null
})

const priceClass = computed(() => {
  if (!changePercent.value) return ''
  return parseFloat(changePercent.value) >= 0 ? 'up' : 'down'
})

/**
 * 初始化图表.
 */
const initChart = () => {
  if (!chartRef.value) return

  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新实例
  chartInstance = echarts.init(chartRef.value, undefined, {
    renderer: 'canvas'
  })

  // 绑定事件 - 监听DataZoom变化以保存范围
  chartInstance.on('datazoom', (params: any) => {
    if (params && params.batch) {
      // 滑块缩放
      const batch = params.batch[0]
      currentZoomRange.start = batch.start
      currentZoomRange.end = batch.end
    } else if (params && params.start !== undefined) {
      // 内置缩放
      currentZoomRange.start = params.start
      currentZoomRange.end = params.end
    }
  })

  // 双击重置视图
  chartInstance.getZr().on('dblclick', () => {
    resetView()
  })
}

/**
 * 重置视图到默认状态.
 */
const resetView = () => {
  currentZoomRange = { start: 60, end: 100 }
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'dataZoom',
      start: 60,
      end: 100
    })
  }
}

/**
 * 处理键盘事件（ESC重置视图）.
 */
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    resetView()
  }
}

/**
 * 渲染图表.
 */
const renderChart = (animate = false) => {
  if (!chartInstance || !props.data || !props.data.length) {
    if (chartInstance) {
      chartInstance.clear()
    }
    return
  }

  // 获取基础配置
  const baseOption = getKLineBaseOption(props.theme)
  const dates = props.data.map(d => d.date)

  // 设置X轴数据
  baseOption.xAxis[0].data = dates

  // 设置图例
  baseOption.legend.data = ['K线']

  // 设置动画 - 切换时启用平滑动画
  baseOption.animation = animate
  baseOption.animationDuration = animate ? 300 : 0
  baseOption.animationEasing = 'cubicOut'

  // 创建系列数组
  const series: any[] = []

  // K线或折线图
  if (chartType.value === 'candle') {
    const klineOption = getKLineSeriesOption(props.theme)
    klineOption.data = formatKLineData(props.data)

    // 添加昨收价基准线
    if (props.data.length >= 2) {
      const prevClose = parseFloat(props.data[props.data.length - 2].close as string)
      klineOption.markLine = {
        symbol: 'none',
        lineStyle: {
          type: 'dashed',
          color: '#f59e0b',
          width: 1
        },
        label: {
          show: true,
          position: 'end',
          formatter: (params) => `昨收: ${params.value.toFixed(4)}`,
          color: '#f59e0b',
          fontSize: 11
        },
        data: [
          {
            yAxis: prevClose,
            name: '昨收价'
          }
        ]
      }
    }

    series.push(klineOption)
  } else {
    // 折线图
    const lineSeries = {
      name: '收盘价',
      type: 'line',
      xAxisIndex: 0,
      yAxisIndex: 0,
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2,
        color: '#2d5af7'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(45, 90, 247, 0.3)' },
          { offset: 1, color: 'rgba(45, 90, 247, 0.05)' }
        ])
      },
      data: props.data.map(d => parseFloat(d.close as string) || 0),
      // 添加昨收价基准线
      markLine: props.data.length >= 2 ? {
        symbol: 'none',
        lineStyle: {
          type: 'dashed',
          color: '#f59e0b',
          width: 1
        },
        label: {
          show: true,
          position: 'end',
          formatter: (params) => `昨收: ${params.value.toFixed(4)}`,
          color: '#f59e0b',
          fontSize: 11
        },
        data: [
          {
            yAxis: parseFloat(props.data[props.data.length - 2].close as string),
            name: '昨收价'
          }
        ]
      } : undefined
    }
    series.push(lineSeries)
    baseOption.legend.data.push('收盘价')
  }

  // 添加均线
  visibleMA.value.forEach(period => {
    const periodNum = parseInt(period)
    if (props.maData && props.maData[`ma${period}`]) {
      const maOption = getMASeriesOption(periodNum, props.theme)
      maOption.data = props.maData[`ma${period}`].map(m => m.value)
      series.push(maOption)
      baseOption.legend.data.push(`MA${period}`)
    }
  })

  // 保持DataZoom范围
  if (baseOption.dataZoom && baseOption.dataZoom.length > 0) {
    baseOption.dataZoom[0].start = currentZoomRange.start
    baseOption.dataZoom[0].end = currentZoomRange.end
    if (baseOption.dataZoom.length > 1) {
      baseOption.dataZoom[1].start = currentZoomRange.start
      baseOption.dataZoom[1].end = currentZoomRange.end
    }
  }

  // 控制右侧价格轴显示
  if (baseOption.yAxis && baseOption.yAxis.length > 1) {
    baseOption.yAxis[1].axisLabel.show = showRightAxis.value
    baseOption.yAxis[1].axisLine.show = showRightAxis.value
  }

  // 设置配置 - 使用notMerge确保切换时完全替换
  baseOption.series = series
  chartInstance.setOption(baseOption, true)
}

/**
 * 处理图表类型切换.
 * 实现平滑切换动画和数据范围保持.
 */
const handleChartTypeChange = (type: 'candle' | 'line') => {
  // 保存用户偏好到localStorage
  localStorage.setItem('fdas_chart_type', type)

  // 触发事件
  emit('chartTypeChange', type)

  // 使用动画重新渲染图表
  renderChart(true)
}

/**
 * 处理均线显示变化.
 */
const handleMAChange = (periods: string[]) => {
  emit('maChange', periods)
  renderChart(false)
}

/**
 * 切换右侧价格轴显示.
 */
const toggleRightAxis = () => {
  showRightAxis.value = !showRightAxis.value
  localStorage.setItem('fdas_right_axis', showRightAxis.value.toString())
  renderChart(false)
}

/**
 * Resize图表.
 */
const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

/**
 * 获取当前DataZoom范围.
 */
const getZoomRange = () => {
  return currentZoomRange
}

/**
 * 设置DataZoom范围.
 */
const setZoomRange = (start: number, end: number) => {
  currentZoomRange.start = start
  currentZoomRange.end = end
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'dataZoom',
      start: start,
      end: end
    })
  }
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    renderChart(false)
  })
}, { deep: true })

// 监听均线数据变化
watch(() => props.maData, () => {
  nextTick(() => {
    renderChart(false)
  })
}, { deep: true })

// 监听主题变化
watch(() => props.theme, () => {
  // 重新渲染图表以应用新主题
  renderChart(false)
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initChart()
    renderChart(false)
    window.addEventListener('resize', resizeChart)
    window.addEventListener('keydown', handleKeydown)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  window.removeEventListener('keydown', handleKeydown)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 暴露方法供父组件调用
defineExpose({
  resizeChart,
  renderChart,
  getChartInstance: () => chartInstance,
  getZoomRange,
  setZoomRange,
  resetView
})
</script>

<style scoped>
.kline-chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 工具栏 */
.chart-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--fdas-bg-card);
  border-bottom: 1px solid var(--fdas-border-light);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.current-price {
  font-size: 16px;
  font-weight: 700;
}

.current-price.up {
  color: #ef4444;
}

.current-price.down {
  color: #22c55e;
}

.change-percent {
  font-size: 13px;
  font-weight: 500;
}

.change-percent.up {
  color: #ef4444;
}

.change-percent.down {
  color: #22c55e;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 图表区域 */
.chart-area {
  flex: 1;
  min-height: 300px;
}

/* 无数据提示 */
.empty-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}
</style>