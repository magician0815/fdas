<template>
  <div class="macd-chart-container">
    <!-- 标题栏 -->
    <div class="chart-header">
      <span class="chart-title">MACD(12,26,9)</span>
      <div class="chart-controls">
        <el-button size="small" text @click="showParamDialog">
          <el-icon><Setting /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 图表容器 -->
    <div ref="chartRef" class="chart-area"></div>

    <!-- 参数设置对话框 -->
    <el-dialog v-model="paramDialogVisible" title="MACD参数设置" width="300px">
      <el-form :model="macdParams" label-width="80px" size="small">
        <el-form-item label="快线周期">
          <el-input-number v-model="macdParams.fast" :min="2" :max="50" />
        </el-form-item>
        <el-form-item label="慢线周期">
          <el-input-number v-model="macdParams.slow" :min="5" :max="100" />
        </el-form-item>
        <el-form-item label="信号周期">
          <el-input-number v-model="macdParams.signal" :min="2" :max="50" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="paramDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="applyParams">应用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * MACD副图组件.
 *
 * 实现MACD指标渲染，包含DIF线、DEA线、MACD柱.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Setting } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { chartThemes, getMACDSeriesOptions } from '@/utils/chartConfig'

// Props定义
interface Props {
  /** MACD数据 */
  data?: {
    dif?: number[]
    dea?: number[]
    macd?: number[]
  }
  /** 日期数组（与主图同步） */
  dates?: string[]
  /** 图表主题 */
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  data: () => ({ dif: [], dea: [], macd: [] }),
  dates: () => [],
  theme: 'light'
})

// Emits定义
const emit = defineEmits<{
  (e: 'paramChange', params: { fast: number; slow: number; signal: number }): void
}>()

// 图表容器ref
const chartRef = ref<HTMLDivElement | null>(null)
// 图表实例
let chartInstance: echarts.ECharts | null = null

// MACD参数
const macdParams = ref({
  fast: 12,
  slow: 26,
  signal: 9
})
// 参数对话框
const paramDialogVisible = ref(false)

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
  if (!chartInstance || !props.data) {
    if (chartInstance) {
      chartInstance.clear()
    }
    return
  }

  const t = chartThemes[props.theme]
  const dates = props.dates || []

  // 构建配置
  const option: echarts.EChartsOption = {
    animation: false,
    tooltip: {
      trigger: 'axis',
      backgroundColor: props.theme === 'dark' ? '#2d2d4a' : '#ffffff',
      borderColor: t.axisLine,
      textStyle: {
        color: t.textPrimary,
        fontSize: 11
      },
      formatter: (params: any) => {
        if (!params || !params.length) return ''
        const date = params[0].axisValue
        let result = `<div style="font-size: 11px;"><div style="font-weight: bold;">${date}</div>`

        params.forEach((item: any) => {
          const value = item.value !== undefined ? item.value.toFixed(4) : '--'
          let color = t.textPrimary
          if (item.seriesName === 'MACD') {
            color = item.value >= 0 ? t.macdUpColor : t.macdDownColor
          } else if (item.seriesName === 'DIF') {
            color = t.difColor
          } else if (item.seriesName === 'DEA') {
            color = t.deaColor
          }
          result += `<div><span style="color: ${color}">${item.seriesName}: ${value}</span></div>`
        })

        result += '</div>'
        return result
      }
    },
    legend: {
      data: ['DIF', 'DEA', 'MACD'],
      top: 0,
      left: 'center',
      textStyle: {
        color: t.textPrimary,
        fontSize: 10
      },
      itemWidth: 12,
      itemHeight: 8
    },
    grid: {
      left: '10%',
      right: '8%',
      top: '20%',
      bottom: '10%'
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
        formatter: (value: number) => value.toFixed(2)
      },
      splitLine: {
        lineStyle: {
          color: t.gridLine,
          type: 'dashed'
        }
      }
    },
    series: [
      // DIF线
      {
        name: 'DIF',
        type: 'line',
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: t.difColor
        },
        data: props.data.dif || []
      },
      // DEA线
      {
        name: 'DEA',
        type: 'line',
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: t.deaColor
        },
        data: props.data.dea || []
      },
      // MACD柱
      {
        name: 'MACD',
        type: 'bar',
        barWidth: '40%',
        itemStyle: {
          color: (params: any) => {
            return params.value >= 0 ? t.macdUpColor : t.macdDownColor
          },
          borderRadius: [2, 2, 0, 0]
        },
        data: props.data.macd || []
      }
    ]
  }

  chartInstance.setOption(option, true)
}

/**
 * 显示参数设置对话框.
 */
const showParamDialog = () => {
  paramDialogVisible.value = true
}

/**
 * 应用MACD参数.
 */
const applyParams = () => {
  emit('paramChange', {
    fast: macdParams.value.fast,
    slow: macdParams.value.slow,
    signal: macdParams.value.signal
  })
  paramDialogVisible.value = false
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

// 监听日期变化
watch(() => props.dates, () => {
  nextTick(() => {
    renderChart()
  })
})

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
.macd-chart-container {
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
</style>