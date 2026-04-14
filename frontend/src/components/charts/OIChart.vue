<template>
  <div class="oi-chart-wrapper">
    <div ref="chartRef" class="oi-chart"></div>
    <!-- 持仓量信息提示 -->
    <div v-if="showTooltip" class="oi-tooltip" :style="tooltipStyle">
      <div class="tooltip-row">
        <span class="label">日期:</span>
        <span class="value">{{ tooltipData.date }}</span>
      </div>
      <div class="tooltip-row">
        <span class="label">持仓量:</span>
        <span class="value">{{ formatOI(tooltipData.oi) }}</span>
      </div>
      <div class="tooltip-row">
        <span class="label">OI变化:</span>
        <span class="value" :class="tooltipData.oiChange >= 0 ? 'positive' : 'negative'">
          {{ formatOIChange(tooltipData.oiChange) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 持仓量(OI)副图组件.
 *
 * 显示期货持仓量变化趋势，支持柱状图和线图两种显示模式.
 * 持仓量是期货特有的指标，反映市场参与程度.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useChartTheme } from '@/hooks/useChartTheme'

// Props定义
interface Props {
  /** 持仓量数据 */
  data: Array<{
    date: string
    open_interest: number
    oi_change?: number
    close?: number
    change_pct?: number
  }>
  /** 副图高度 */
  height?: number
  /** 显示模式：bar(柱状图) / line(线图) */
  displayMode?: 'bar' | 'line'
  /** 是否显示OI变化 */
  showOiChange?: boolean
  /** 主图索引范围（用于联动） */
  visibleRange?: [number, number]
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  height: 80,
  displayMode: 'bar',
  showOiChange: true,
  visibleRange: () => [0, 100]
})

// Emits定义
const emit = defineEmits<{
  (e: 'oiClick', data: { date: string; oi: number }): void
}>()

// 状态
const chartRef = ref<HTMLDivElement>()
const chartInstance = ref<echarts.ECharts | null>(null)
const showTooltip = ref(false)
const tooltipData = ref({ date: '', oi: 0, oiChange: 0 })
const tooltipStyle = ref({ left: '0px', top: '0px' })

// 主题
const { currentTheme } = useChartTheme()

// 格式化持仓量
const formatOI = (oi: number): string => {
  if (oi >= 10000) {
    return `${(oi / 10000).toFixed(2)}万手`
  }
  return `${oi.toFixed(0)}手`
}

// 格式化持仓量变化
const formatOIChange = (change: number): string => {
  const prefix = change >= 0 ? '+' : ''
  return `${prefix}${formatOI(Math.abs(change))}`
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance.value = echarts.init(chartRef.value)
  updateChart()

  // 监听鼠标事件
  chartInstance.value.on('mousemove', handleMouseMove)
  chartInstance.value.on('mouseout', () => {
    showTooltip.value = false
  })
}

// 更新图表
const updateChart = () => {
  if (!chartInstance.value) return

  const theme = currentTheme.value
  const [startIndex, endIndex] = props.visibleRange
  const visibleData = props.data.slice(startIndex, endIndex + 1)

  // 准备数据
  const dates = visibleData.map(d => d.date)
  const oiValues = visibleData.map(d => d.open_interest || 0)
  const oiChanges = visibleData.map(d => d.oi_change || 0)

  // 计算涨跌颜色（基于价格涨跌或OI变化）
  const colors = visibleData.map((d, idx) => {
    // 使用OI变化判断颜色
    if (props.showOiChange && d.oi_change !== undefined) {
      return d.oi_change >= 0 ? theme.colors.up : theme.colors.down
    }
    // 或者使用价格涨跌判断
    if (d.change_pct !== undefined) {
      return d.change_pct >= 0 ? theme.colors.up : theme.colors.down
    }
    return theme.colors.textMuted
  })

  const option: echarts.EChartsOption = {
    animation: false,
    grid: {
      left: 60,
      right: 40,
      top: 10,
      bottom: 20
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        show: false
      },
      splitLine: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      position: 'right',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: theme.colors.textMuted,
        fontSize: 10,
        formatter: (value: number) => {
          if (value >= 10000) {
            return `${(value / 10000).toFixed(0)}万`
          }
          return value.toString()
        }
      },
      splitLine: {
        lineStyle: {
          color: theme.colors.gridLine,
          type: 'dashed'
        }
      }
    },
    series: props.displayMode === 'bar' ? [
      {
        name: '持仓量',
        type: 'bar',
        data: oiValues.map((value, idx) => ({
          value,
          itemStyle: {
            color: colors[idx],
            opacity: 0.8
          }
        })),
        barWidth: '60%',
        emphasis: {
          itemStyle: {
            opacity: 1
          }
        }
      }
    ] : [
      {
        name: '持仓量',
        type: 'line',
        data: oiValues,
        lineStyle: {
          color: theme.colors.primary,
          width: 1.5
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: theme.colors.primary + '40' },
            { offset: 1, color: theme.colors.primary + '10' }
          ])
        },
        symbol: 'none',
        smooth: true
      },
      {
        name: 'OI变化',
        type: 'bar',
        data: oiChanges.map((value, idx) => ({
          value,
          itemStyle: {
            color: value >= 0 ? theme.colors.up : theme.colors.down,
            opacity: 0.6
          }
        })),
        barWidth: '40%'
      }
    ]
  }

  chartInstance.value.setOption(option, { notMerge: true })
}

// 处理鼠标移动
const handleMouseMove = (params: any) => {
  if (params.componentType === 'series') {
    const dataIndex = params.dataIndex
    const data = props.data[dataIndex + props.visibleRange[0]]

    tooltipData.value = {
      date: data.date,
      oi: data.open_interest || 0,
      oiChange: data.oi_change || 0
    }

    tooltipStyle.value = {
      left: `${params.event.offsetX + 10}px`,
      top: `${params.event.offsetY - 60}px`
    }

    showTooltip.value = true
  }
}

// 联动缩放
const syncZoom = (start: number, end: number) => {
  if (!chartInstance.value) return

  const startIndex = Math.floor(start / 100 * props.data.length)
  const endIndex = Math.floor(end / 100 * props.data.length)

  updateChart()
}

// 监听数据变化
watch(() => props.data, () => {
  updateChart()
}, { deep: true })

watch(() => props.visibleRange, () => {
  updateChart()
}, { deep: true })

watch(currentTheme, () => {
  updateChart()
})

// 窗口大小变化处理
const handleResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

// 导出方法供父组件调用
defineExpose({
  syncZoom,
  resize: handleResize
})
</script>

<style scoped>
.oi-chart-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.oi-chart {
  width: 100%;
  height: 100%;
}

.oi-tooltip {
  position: absolute;
  background: var(--fdas-bg-card);
  border: 1px solid var(--fdas-border-light);
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 12px;
  z-index: 100;
  box-shadow: var(--fdas-shadow-card);
  pointer-events: none;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.tooltip-row:last-child {
  margin-bottom: 0;
}

.label {
  color: var(--fdas-text-muted);
  margin-right: 8px;
}

.value {
  color: var(--fdas-text-primary);
  font-weight: 500;
}

.value.positive {
  color: var(--fdas-color-up);
}

.value.negative {
  color: var(--fdas-color-down);
}
</style>