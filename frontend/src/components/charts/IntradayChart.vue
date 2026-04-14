<template>
  <div class="intraday-chart-container">
    <!-- 图表头部 -->
    <div class="chart-header">
      <div class="header-left">
        <span class="chart-title">{{ symbolName || '分时走势' }}</span>
        <span class="current-time">{{ currentTime }}</span>
      </div>
      <div class="header-right">
        <span class="current-price" :class="priceClass">{{ formatPrice(currentPrice) }}</span>
        <span class="change-percent" :class="priceClass">{{ formatChange(changePercent) }}</span>
      </div>
    </div>

    <!-- 图表区域 -->
    <div ref="chartRef" class="chart-area"></div>

    <!-- 昨收价基准线 -->
    <div class="baseline-info">
      <span class="baseline-label">昨收:</span>
      <span class="baseline-value">{{ formatPrice(prevClose) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 分时走势图组件.
 *
 * 显示当日价格走势和成交量，支持实时更新.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { chartThemes } from '@/utils/chartConfig'

// Props定义
interface Props {
  /** 分时数据数组 */
  data?: Array<{
    time: string          // 时间（HH:mm格式）
    price: number | string
    volume?: number | string
    avgPrice?: number | string  // 分时均价
  }>
  /** 标的名称 */
  symbolName?: string
  /** 昨日收盘价 */
  prevClose?: number
  /** 图表主题 */
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  symbolName: '',
  prevClose: 0,
  theme: 'light'
})

// 图表容器ref
const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 当前时间
const currentTime = computed(() => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

// 当前价格（最后一项）
const currentPrice = computed(() => {
  if (props.data && props.data.length > 0) {
    return parseFloat(props.data[props.data.length - 1].price) || props.prevClose
  }
  return props.prevClose
})

// 涨跌幅
const changePercent = computed(() => {
  if (props.prevClose > 0 && currentPrice.value > 0) {
    return ((currentPrice.value - props.prevClose) / props.prevClose * 100).toFixed(2)
  }
  return '0.00'
})

// 涨跌样式
const priceClass = computed(() => {
  const change = parseFloat(changePercent.value)
  if (change > 0) return 'up'
  if (change < 0) return 'down'
  return ''
})

// 格式化价格
const formatPrice = (price: number) => {
  return price.toFixed(4)
}

// 格式化涨跌幅
const formatChange = (change: string) => {
  const val = parseFloat(change)
  if (val >= 0) return '+' + val + '%'
  return val + '%'
}

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
  if (!chartInstance || !props.data || props.data.length === 0) {
    if (chartInstance) {
      chartInstance.clear()
    }
    return
  }

  const t = chartThemes[props.theme]

  // 准备数据
  const times = props.data.map(d => d.time)
  const prices = props.data.map(d => parseFloat(d.price) || 0)
  const volumes = props.data.map(d => parseFloat(d.volume) || 0)
  const avgPrices = props.data.map(d => parseFloat(d.avgPrice) || 0)

  // 计算涨跌色
  const priceColors = prices.map(p => {
    if (p >= props.prevClose) return t.upColor
    return t.downColor
  })

  // 计算成交量颜色（根据价格涨跌）
  const volumeColors = prices.map((p, i) => {
    if (i === 0) {
      return p >= props.prevClose ? t.volumeUpColor : t.volumeDownColor
    }
    return p >= prices[i - 1] ? t.volumeUpColor : t.volumeDownColor
  })

  // 构建图表配置
  const option = {
    animation: false,
    backgroundColor: t.background,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        lineStyle: {
          type: 'solid',
          width: 1,
          color: t.crosshairColor
        }
      },
      backgroundColor: props.theme === 'dark' ? '#2d2d4a' : '#ffffff',
      borderColor: t.axisLine,
      textStyle: {
        color: t.textPrimary
      },
      formatter: (params: any[]) => {
        const priceParam = params.find(p => p.seriesName === '分时价格')
        const volParam = params.find(p => p.seriesName === '成交量')

        if (!priceParam) return ''

        const time = priceParam.name
        const price = priceParam.value
        const vol = volParam?.value || 0
        const avg = avgPrices[priceParam.dataIndex] || 0
        const change = props.prevClose > 0 ? ((price - props.prevClose) / props.prevClose * 100).toFixed(2) : '0'

        return `
          <div style="font-size: 12px; line-height: 1.6;">
            <div style="font-weight: bold;">${time}</div>
            <div>价格: <span style="color: ${t.textPrimary}">${formatPrice(price)}</span></div>
            <div>均价: <span style="color: ${t.textSecondary}">${formatPrice(avg)}</span></div>
            <div>涨跌: <span style="color: ${change >= 0 ? t.upColor : t.downColor}">${change >= 0 ? '+' : ''}${change}%</span></div>
            <div>成交量: <span style="color: ${t.textSecondary}">${vol}</span></div>
          </div>
        `
      }
    },
    axisPointer: {
      link: [{ xAxisIndex: 'all' }]
    },
    grid: [
      // 价格图区域
      {
        left: '10%',
        right: '8%',
        top: '10%',
        height: '60%'
      },
      // 成交量区域
      {
        left: '10%',
        right: '8%',
        top: '75%',
        height: '20%'
      }
    ],
    xAxis: [
      // 价格图X轴
      {
        type: 'category',
        gridIndex: 0,
        boundaryGap: false,
        axisLine: { lineStyle: { color: t.axisLine } },
        axisTick: { show: false },
        axisLabel: {
          color: t.textSecondary,
          fontSize: 11,
          interval: 30  // 每30分钟显示一个标签
        },
        splitLine: { show: false },
        data: times
      },
      // 成交量X轴
      {
        type: 'category',
        gridIndex: 1,
        boundaryGap: false,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        splitLine: { show: false },
        data: times
      }
    ],
    yAxis: [
      // 价格Y轴
      {
        type: 'value',
        gridIndex: 0,
        scale: true,
        axisLine: { lineStyle: { color: t.axisLine } },
        axisTick: { show: false },
        axisLabel: {
          color: t.textSecondary,
          fontSize: 11,
          formatter: (value: number) => value.toFixed(4)
        },
        splitLine: {
          lineStyle: {
            color: t.gridLine,
            type: 'dashed'
          }
        },
        // 添加昨收价基准线
        splitArea: {
          show: true,
          areaStyle: {
            color: [
              // 高于昨收价区域（红色背景）
              props.prevClose > 0 ? {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(239, 68, 68, 0.05)' },
                  { offset: 1, color: 'rgba(239, 68, 68, 0.02)' }
                ]
              } : 'transparent',
              // 低于昨收价区域（绿色背景）
              props.prevClose > 0 ? {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(34, 197, 94, 0.02)' },
                  { offset: 1, color: 'rgba(34, 197, 94, 0.05)' }
                ]
              } : 'transparent'
            ]
          }
        }
      },
      // 成交量Y轴
      {
        type: 'value',
        gridIndex: 1,
        scale: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: t.textSecondary,
          fontSize: 10,
          formatter: (value: number) => value >= 1000 ? (value / 1000).toFixed(0) + 'K' : value.toFixed(0)
        },
        splitLine: { show: false }
      }
    ],
    series: [
      // 分时价格线
      {
        name: '分时价格',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: t.textPrimary
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(45, 90, 247, 0.1)' },
              { offset: 1, color: 'rgba(45, 90, 247, 0.01)' }
            ]
          }
        },
        data: prices,
        // 昨收价基准线
        markLine: {
          symbol: 'none',
          data: [
            {
              yAxis: props.prevClose,
              lineStyle: {
                type: 'solid',
                width: 1,
                color: '#f59e0b'
              },
              label: {
                show: true,
                formatter: `昨收: ${formatPrice(props.prevClose)}`,
                position: 'insideEndTop',
                color: '#f59e0b',
                fontSize: 11
              }
            }
          ]
        }
      },
      // 分时均价线
      {
        name: '分时均价',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: '#f59e0b',
          type: 'dashed'
        },
        data: avgPrices
      },
      // 成交量柱状图
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        barWidth: '80%',
        itemStyle: {
          color: (params: any) => volumeColors[params.dataIndex]
        },
        data: volumes
      }
    ]
  }

  chartInstance.setOption(option, true)
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
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', resizeChart)
})

// 暴露方法
defineExpose({
  resizeChart,
  renderChart
})
</script>

<style scoped>
.intraday-chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--fdas-border-light);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.current-time {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-price {
  font-size: 16px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.current-price.up {
  color: #ef4444;
}

.current-price.down {
  color: #22c55e;
}

.change-percent {
  font-size: 14px;
  font-weight: 500;
  color: var(--fdas-text-muted);
}

.change-percent.up {
  color: #ef4444;
}

.change-percent.down {
  color: #22c55e;
}

.chart-area {
  flex: 1;
  min-height: 200px;
}

.baseline-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--fdas-bg-hover);
  border-top: 1px solid var(--fdas-border-light);
}

.baseline-label {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.baseline-value {
  font-size: 12px;
  font-weight: 500;
  color: #f59e0b;
}
</style>