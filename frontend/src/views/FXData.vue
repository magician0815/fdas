<template>
  <div class="fx-data-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据分析</h1>
        <p class="page-subtitle">外汇行情数据可视化</p>
      </div>
      <div class="header-right">
        <!-- 货币对选择 -->
        <el-select
          v-model="selectedSymbolId"
          placeholder="选择货币对"
          class="symbol-select"
          filterable
          @change="fetchData"
        >
          <el-option
            v-for="s in symbols"
            :key="s.id"
            :label="`${s.name} (${s.code})`"
            :value="s.id"
          />
        </el-select>

        <!-- 刷新按钮 -->
        <el-button type="primary" @click="fetchData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          <span>刷新数据</span>
        </el-button>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-row">
      <div class="stat-card mini">
        <span class="stat-label">当前价格</span>
        <span class="stat-value primary">{{ currentPrice || '--' }}</span>
      </div>
      <div class="stat-card mini">
        <span class="stat-label">涨跌幅</span>
        <span class="stat-value" :class="changeClass">{{ changePercent || '--' }}</span>
      </div>
      <div class="stat-card mini">
        <span class="stat-label">最高价</span>
        <span class="stat-value">{{ highPrice || '--' }}</span>
      </div>
      <div class="stat-card mini">
        <span class="stat-label">最低价</span>
        <span class="stat-value">{{ lowPrice || '--' }}</span>
      </div>
      <div class="stat-card mini">
        <span class="stat-label">振幅</span>
        <span class="stat-value">{{ amplitude || '--' }}</span>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-section">
      <!-- K线图 -->
      <div class="chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">价格走势图</h2>
          <div class="panel-actions">
            <el-radio-group v-model="chartType" size="small" @change="renderChart">
              <el-radio-button label="line">折线图</el-radio-button>
              <el-radio-button label="candle">K线图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-container" ref="mainChartRef">
          <el-empty v-if="!chartData.length" description="暂无数据">
            <el-button type="primary" size="small" @click="$router.push('/collection')">
              配置采集任务
            </el-button>
          </el-empty>
        </div>
      </div>

      <!-- 技术指标图 -->
      <div class="chart-panel indicators">
        <div class="panel-header">
          <h2 class="panel-title">技术指标</h2>
          <div class="panel-actions">
            <el-checkbox-group v-model="selectedIndicators" size="small" @change="renderIndicatorChart">
              <el-checkbox-button label="ma">MA均线</el-checkbox-button>
              <el-checkbox-button label="macd">MACD</el-checkbox-button>
            </el-checkbox-group>
          </div>
        </div>
        <div class="chart-container indicators-chart" ref="indicatorChartRef">
          <el-empty v-if="!indicatorsData.ma?.length" description="暂无技术指标数据" :image-size="80" />
        </div>
      </div>
    </div>

    <!-- 数据表格区域 -->
    <div class="data-table-section">
      <div class="table-panel">
        <div class="panel-header">
          <h2 class="panel-title">历史数据</h2>
          <div class="panel-actions">
            <el-button size="small" @click="exportData" :disabled="!chartData.length">
              <el-icon><Download /></el-icon>
              <span>导出数据</span>
            </el-button>
          </div>
        </div>
        <el-table
          :data="tableData"
          stripe
          style="width: 100%"
          max-height="400"
          v-loading="loading"
        >
          <el-table-column prop="date" label="日期" width="120" fixed />
          <el-table-column prop="open" label="开盘价" width="100">
            <template #default="{ row }">
              <span class="price-cell">{{ formatPrice(row.open) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="high" label="最高价" width="100">
            <template #default="{ row }">
              <span class="price-cell high">{{ formatPrice(row.high) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="low" label="最低价" width="100">
            <template #default="{ row }">
              <span class="price-cell low">{{ formatPrice(row.low) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="close" label="收盘价" width="100">
            <template #default="{ row }">
              <span class="price-cell">{{ formatPrice(row.close) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="change_pct" label="涨跌幅" width="100">
            <template #default="{ row }">
              <span class="change-cell" :class="getChangeClass(row.change_pct)">
                {{ formatChange(row.change_pct) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="amplitude" label="振幅" width="100">
            <template #default="{ row }">
              {{ formatChange(row.amplitude) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 数据分析页面.
 *
 * 展示K线图、均线图、MACD图和历史数据表格.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-11 - 完整ECharts图表实现
 */
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getFXData, getIndicators } from '@/api/fx_data'
import { getForexSymbols } from '@/api/forex_symbols'

const router = useRouter()

// 数据状态
const loading = ref(false)
const chartData = ref([])
const indicatorsData = ref({ ma: [], macd: {} })
const tableData = ref([])
const symbols = ref([])

// 选择状态
const selectedSymbolId = ref(null)
const chartType = ref('line')
const selectedIndicators = ref(['ma'])

// 图表实例
const mainChartRef = ref(null)
const indicatorChartRef = ref(null)
let mainChart = null
let indicatorChart = null

// 统计数据
const currentPrice = computed(() => {
  if (chartData.value.length) {
    const latest = chartData.value[chartData.value.length - 1]
    return formatPrice(latest.close)
  }
  return null
})

const changePercent = computed(() => {
  if (chartData.value.length >= 2) {
    const latest = chartData.value[chartData.value.length - 1]
    return latest.change_pct ? formatChange(latest.change_pct) : null
  }
  return null
})

const changeClass = computed(() => {
  if (!changePercent.value) return ''
  const value = parseFloat(changePercent.value)
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return ''
})

const highPrice = computed(() => {
  if (chartData.value.length) {
    const max = Math.max(...chartData.value.map(d => parseFloat(d.high) || 0))
    return formatPrice(max)
  }
  return null
})

const lowPrice = computed(() => {
  if (chartData.value.length) {
    const min = Math.min(...chartData.value.map(d => parseFloat(d.low) || 0))
    return formatPrice(min)
  }
  return null
})

const amplitude = computed(() => {
  if (chartData.value.length) {
    const latest = chartData.value[chartData.value.length - 1]
    return latest.amplitude ? formatChange(latest.amplitude) : null
  }
  return null
})

// 格式化价格
const formatPrice = (value) => {
  if (!value) return '--'
  return parseFloat(value).toFixed(4)
}

// 格式化涨跌幅
const formatChange = (value) => {
  if (!value) return '--'
  return `${parseFloat(value).toFixed(2)}%`
}

// 获取涨跌样式类
const getChangeClass = (change) => {
  if (!change) return ''
  const value = parseFloat(change)
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return ''
}

// 获取标的列表
const fetchSymbols = async () => {
  try {
    const res = await getForexSymbols()
    if (res.success) {
      symbols.value = res.data
      if (symbols.value.length && !selectedSymbolId.value) {
        selectedSymbolId.value = symbols.value[0].id
      }
    }
  } catch (e) {
    ElMessage.error('获取货币对列表失败')
  }
}

// 获取数据
const fetchData = async () => {
  if (!selectedSymbolId.value) return

  loading.value = true
  try {
    // 获取日线数据
    const dataRes = await getFXData({ symbol_id: selectedSymbolId.value, limit: 100 })
    if (dataRes.success) {
      chartData.value = dataRes.data || []
      tableData.value = (dataRes.data || []).slice(0, 20)
    }

    // 获取技术指标
    const indicatorsRes = await getIndicators({ symbol_id: selectedSymbolId.value })
    if (indicatorsRes.success) {
      indicatorsData.value = indicatorsRes.data || { ma: [], macd: {} }
    }

    // 渲染图表
    await nextTick()
    renderChart()
    renderIndicatorChart()
  } catch (e) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 渲染主图表
const renderChart = () => {
  if (!mainChartRef.value || !chartData.value.length) {
    if (mainChart) {
      mainChart.clear()
    }
    return
  }

  if (!mainChart) {
    mainChart = echarts.init(mainChartRef.value)
  }

  const dates = chartData.value.map(d => d.date)
  const closes = chartData.value.map(d => parseFloat(d.close) || 0)
  const highs = chartData.value.map(d => parseFloat(d.high) || 0)
  const lows = chartData.value.map(d => parseFloat(d.low) || 0)
  const opens = chartData.value.map(d => parseFloat(d.open) || 0)

  let option

  if (chartType.value === 'candle') {
    // K线图
    const klineData = chartData.value.map(d => [
      parseFloat(d.open) || 0,
      parseFloat(d.close) || 0,
      parseFloat(d.low) || 0,
      parseFloat(d.high) || 0
    ])

    option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: { data: ['K线'] },
      grid: { left: '10%', right: '10%', bottom: '15%' },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { onZero: false }
      },
      yAxis: {
        type: 'value',
        scale: true,
        splitArea: { show: true }
      },
      dataZoom: [
        { type: 'inside', start: 50, end: 100 },
        { show: true, type: 'slider', top: '90%', start: 50, end: 100 }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: klineData,
          itemStyle: {
            color: '#ef4444',
            color0: '#22c55e',
            borderColor: '#ef4444',
            borderColor0: '#22c55e'
          }
        }
      ]
    }
  } else {
    // 折线图
    option = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['收盘价'] },
      grid: { left: '10%', right: '10%', bottom: '15%' },
      xAxis: { type: 'category', data: dates, boundaryGap: false },
      yAxis: { type: 'value', scale: true },
      dataZoom: [
        { type: 'inside', start: 50, end: 100 },
        { show: true, type: 'slider', top: '90%', start: 50, end: 100 }
      ],
      series: [
        {
          name: '收盘价',
          type: 'line',
          data: closes,
          smooth: true,
          lineStyle: { width: 2, color: '#2d5af7' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(45, 90, 247, 0.3)' },
              { offset: 1, color: 'rgba(45, 90, 247, 0.05)' }
            ])
          }
        }
      ]
    }
  }

  // 添加MA均线（如果选择）
  if (selectedIndicators.value.includes('ma') && indicatorsData.value.ma?.length) {
    const maData = indicatorsData.value.ma
    option.legend.data.push('MA5')
    option.series.push({
      name: 'MA5',
      type: 'line',
      data: maData.map(m => m.value),
      lineStyle: { width: 1, color: '#f59e0b' },
      symbol: 'none'
    })
  }

  mainChart.setOption(option)
}

// 渲染指标图表
const renderIndicatorChart = () => {
  if (!indicatorChartRef.value) {
    return
  }

  if (!indicatorChart) {
    indicatorChart = echarts.init(indicatorChartRef.value)
  }

  if (!indicatorsData.value.ma?.length && !indicatorsData.value.macd?.macd?.length) {
    indicatorChart.clear()
    return
  }

  const dates = chartData.value.map(d => d.date)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: selectedIndicators.value.includes('ma') ? ['MA'] : [] },
    grid: { left: '10%', right: '10%', bottom: '15%' },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value' },
    dataZoom: [{ type: 'inside', start: 50, end: 100 }],
    series: []
  }

  // MA均线
  if (selectedIndicators.value.includes('ma') && indicatorsData.value.ma?.length) {
    option.series.push({
      name: 'MA',
      type: 'line',
      data: indicatorsData.value.ma.map(m => m.value),
      lineStyle: { width: 2, color: '#2d5af7' },
      symbol: 'circle',
      symbolSize: 4
    })
  }

  indicatorChart.setOption(option)
}

// 导出数据
const exportData = () => {
  if (!chartData.value.length) return

  const headers = ['日期', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅', '振幅']
  const rows = chartData.value.map(d => [
    d.date, formatPrice(d.open), formatPrice(d.high), formatPrice(d.low),
    formatPrice(d.close), formatChange(d.change_pct), formatChange(d.amplitude)
  ])

  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  const symbol = symbols.value.find(s => s.id === selectedSymbolId.value)
  link.download = `${symbol?.code || 'data'}_${new Date().toISOString().split('T')[0]}.csv`
  link.click()

  ElMessage.success('数据导出成功')
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  mainChart?.resize()
  indicatorChart?.resize()
}

onMounted(() => {
  fetchSymbols()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  mainChart?.dispose()
  indicatorChart?.dispose()
})

// 标的选择变化时获取数据
watch(selectedSymbolId, (val) => {
  if (val) {
    fetchData()
  }
})
</script>

<style scoped>
.fx-data-page {
  max-width: 1400px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--fdas-spacing-lg);
}

.header-left {
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--fdas-text-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 13px;
  color: var(--fdas-text-muted);
  margin-top: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-md);
}

.symbol-select {
  width: 200px;
}

/* 统计卡片行 */
.stats-row {
  display: flex;
  gap: var(--fdas-spacing-md);
  margin-bottom: var(--fdas-spacing-lg);
}

.stat-card.mini {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-md);
  padding: var(--fdas-spacing-md) var(--fdas-spacing-lg);
  display: flex;
  flex-direction: column;
  min-width: 120px;
  box-shadow: var(--fdas-shadow-card);
}

.stat-label {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--fdas-text-primary);
  margin-top: 4px;
}

.stat-value.primary { color: var(--fdas-primary); }
.stat-value.positive { color: var(--fdas-success); }
.stat-value.negative { color: var(--fdas-danger); }

/* 图表区域 */
.chart-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--fdas-spacing-lg);
  margin-bottom: var(--fdas-spacing-lg);
}

.chart-panel {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-lg);
  box-shadow: var(--fdas-shadow-card);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--fdas-spacing-md);
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--fdas-text-primary);
  margin: 0;
}

.chart-container {
  height: 350px;
  background: var(--fdas-gray-50);
  border-radius: var(--fdas-radius-md);
}

.chart-container.indicators-chart {
  height: 280px;
}

/* 数据表格区域 */
.data-table-section {
  margin-bottom: var(--fdas-spacing-lg);
}

.table-panel {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-lg);
  box-shadow: var(--fdas-shadow-card);
}

/* 表格单元格样式 */
.price-cell { font-weight: 500; }
.price-cell.high { color: var(--fdas-success); }
.price-cell.low { color: var(--fdas-danger); }

.change-cell { font-weight: 500; }
.change-cell.positive { color: var(--fdas-success); }
.change-cell.negative { color: var(--fdas-danger); }

/* 响应式设计 */
@media (max-width: 1200px) {
  .chart-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--fdas-spacing-md);
  }

  .header-right {
    flex-wrap: wrap;
    width: 100%;
  }

  .symbol-select {
    width: 100%;
  }

  .stats-row {
    flex-wrap: wrap;
  }

  .stat-card.mini {
    min-width: calc(50% - var(--fdas-spacing-sm));
  }
}
</style>