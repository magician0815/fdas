<template>
  <div class="volume-chart-container">
    <!-- 标题栏 -->
    <div class="chart-header">
      <span class="chart-title">成交量</span>
      <div class="chart-controls">
        <el-checkbox-group v-model="visibleVOL" size="small" @change="handleVOLChange">
          <el-checkbox-button label="5">VOL5</el-checkbox-button>
          <el-checkbox-button label="10">VOL10</el-checkbox-button>
        </el-checkbox-group>
      </div>
    </div>

    <!-- 图表容器 -->
    <div ref="chartRef" class="chart-area"></div>

    <!-- 外汇无成交量提示 -->
    <div v-if="hasZeroVolume" class="volume-warning">
      <el-icon><Warning /></el-icon>
      <span>外汇市场通常无成交量数据</span>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 成交量副图组件.
 *
 * 实现成交量柱状图渲染，颜色与K线涨跌同步.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { chartThemes, formatVolumeData } from '@/utils/chartConfig'

// Props定义
interface Props {
  /** 原始K线数据（用于获取涨跌状态和成交量） */
  data: Array<{
    date: string
    open: number | string
    close: number | string
    high: number | string
    low: number | string
    volume?: number | string
  }>
  /** 图表主题 */
  theme?: 'light' | 'dark'
  /** 成交量均线数据 */
  volData?: {
    vol5?: Array<{ value: number }>
    vol10?: Array<{ value: number }>
  }
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  theme: 'light',
  volData: () => ({})
})

// Emits定义
const emit = defineEmits<{
  (e: 'volChange', periods: string[]): void
}>()

// 图表容器ref
const chartRef = ref<HTMLDivElement | null>(null)
// 图表实例
let chartInstance: echarts.ECharts | null = null

// 状态
const visibleVOL = ref<string[]>([])

// 计算属性
const hasZeroVolume = computed(() => {
  if (!props.data || !props.data.length) return false
  // 检查是否所有成交量都是0或未定义
  return props.data.every(d => {
    const vol = parseFloat(d.volume as string) || 0
    return vol === 0
  })
})

/**
 * 初始化图表.
 */
const initChart = () => {
  if (!chartRef.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value, undefined, {
    renderer: 'canvas'
  })
}

/**
 * 渲染图表.
 */
const renderChart = () => {
  if (!chartInstance || !props.data || !props.data.length) {
    if (chartInstance) {
      chartInstance.clear()
    }
    return
  }

  const t = chartThemes[props.theme]
  const dates = props.data.map(d => d.date)

  // 成交量数据（根据涨跌设置颜色）
  const volumeData = props.data.map(item => {
    const open = parseFloat(item.open as string) || 0
    const close = parseFloat(item.close as string) || 0
    const volume = parseFloat(item.volume as string) || 0
    return {
      value: volume,
      itemStyle: {
        color: close >= open ? t.volumeUpColor : t.volumeDownColor
      }
    }
  })

  // 构建配置
  const option: echarts.EChartsOption = {
    animation: false,
    grid: {
      left: '10%',
      right: '8%',
      top: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      position: 'left',
      scale: true,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: t.textSecondary,
        fontSize: 10,
        formatter: (value: number) => {
          if (value >= 10000) return (value / 10000).toFixed(1) + '万'
          return value.toFixed(0)
        }
      },
      splitLine: {
        lineStyle: {
          color: t.gridLine,
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '成交量',
        type: 'bar',
        barWidth: '60%',
        data: volumeData,
        itemStyle: {
          borderRadius: [2, 2, 0, 0] // 顶部圆角
        }
      }
    ]
  }

  // 添加成交量均线
  if (props.volData) {
    if (visibleVOL.value.includes('5') && props.volData.vol5) {
      option.series!.push({
        name: 'VOL5',
        type: 'line',
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: t.ma5Color
        },
        data: props.volData.vol5.map(v => v.value)
      })
    }
    if (visibleVOL.value.includes('10') && props.volData.vol10) {
      option.series!.push({
        name: 'VOL10',
        type: 'line',
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: t.ma10Color
        },
        data: props.volData.vol10.map(v => v.value)
      })
    }
  }

  chartInstance.setOption(option, true)
}

/**
 * 处理成交量均线变化.
 */
const handleVOLChange = (periods: string[]) => {
  emit('volChange', periods)
  renderChart()
}

/**
 * Resize图表.
 */
const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    renderChart()
  })
}, { deep: true })

// 监听主题变化
watch(() => props.theme, () => {
  renderChart()
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initChart()
    renderChart()
    window.addEventListener('resize', resizeChart)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 暴露方法
defineExpose({
  resizeChart,
  renderChart,
  getChartInstance: () => chartInstance
})
</script>

<style scoped>
.volume-chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 12px;
  background: var(--fdas-bg-card);
  border-bottom: 1px solid var(--fdas-border-light);
}

.chart-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--fdas-text-secondary);
}

.chart-controls {
  display: flex;
  gap: 4px;
}

.chart-area {
  flex: 1;
  min-height: 80px;
}

/* 无成交量提示 */
.volume-warning {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--fdas-text-muted);
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
  border-radius: 4px;
  z-index: 5;
}

.volume-warning .el-icon {
  color: #f59e0b;
}
</style>