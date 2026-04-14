<template>
  <div class="fx-data-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据分析</h1>
        <p class="page-subtitle">专业行情走势</p>
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

        <!-- 周期切换 -->
        <el-select
          v-model="periodType"
          placeholder="选择周期"
          class="period-select"
          @change="handlePeriodChange"
        >
          <el-option
            v-for="opt in periodOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
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

    <!-- 专业图表区域 -->
    <div class="pro-chart-section">
      <ProChart
        ref="proChartRef"
        :data="chartData"
        :indicators="indicatorsData"
        :symbolName="selectedSymbolName"
        :symbolId="selectedSymbolId"
        :loading="loading"
        @fetchData="fetchData"
        @themeChange="handleThemeChange"
      />
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
  <!-- 键盘精灵 -->
    <KeyboardWizard
      v-model="showKeyboardWizard"
      :items="keyboardItems"
      type="symbol"
      @select="handleKeyboardSelect"
    />

    <!-- 指标精灵 -->
    <IndicatorWizard
      v-model="showIndicatorWizard"
      :maPeriods="maPeriods"
      :macdParams="macdParams"
      :volPeriods="volPeriods"
      @maChange="handleMAChange"
      @macdChange="handleMACDChange"
      @volChange="handleVOLChange"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 数据分析页面.
 *
 * 展示专业行情走势图表和历史数据表格.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-14 - 使用专业图表组件ProChart
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getFXData, getIndicators } from '@/api/fx_data'
import { getForexSymbols } from '@/api/forex_symbols'
import ProChart from '@/components/charts/ProChart.vue'
import KeyboardWizard from '@/components/charts/KeyboardWizard.vue'
import IndicatorWizard from '@/components/charts/IndicatorWizard.vue'

const router = useRouter()

// 数据状态
const loading = ref(false)
const chartData = ref([])
const indicatorsData = ref({ ma: {}, macd: { dif: [], dea: [], macd: [] } })
const tableData = ref([])
const symbols = ref([])

// 周期类型状态
const periodType = ref<string>(
  localStorage.getItem('fdas_period_type') || 'daily'
)

// 周期类型选项
const periodOptions = [
  { value: 'daily', label: '日线' },
  { value: 'weekly', label: '周线' },
  { value: 'monthly', label: '月线' }
]

// 处理周期切换
const handlePeriodChange = (period: string) => {
  periodType.value = period
  localStorage.setItem('fdas_period_type', period)
  fetchData()
}

// 选择状态
const selectedSymbolId = ref(null)
const showKeyboardWizard = ref(false)
const showIndicatorWizard = ref(false)

// 指标参数状态
const maPeriods = ref<string[]>(['5', '10', '20', '60'])
const macdParams = ref({ fast: 12, slow: 26, signal: 9 })
const volPeriods = ref<string[]>(['5', '10'])

// 图表组件ref
const proChartRef = ref(null)

// 计算属性
const selectedSymbolName = computed(() => {
  if (!selectedSymbolId.value) return ''
  const symbol = symbols.value.find(s => s.id === selectedSymbolId.value)
  return symbol ? symbol.name : ''
})

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

// 键盘精灵数据
const keyboardItems = computed(() => {
  return symbols.value.map(s => ({
    id: s.id,
    name: s.name,
    code: s.code,
  }))
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
    // 获取行情数据（添加周期参数）
    const dataRes = await getFXData({
      symbol_id: selectedSymbolId.value,
      period: periodType.value,
      limit: periodType.value === 'daily' ? 100 : (periodType.value === 'weekly' ? 52 : 24)
    })
    if (dataRes.success) {
      chartData.value = dataRes.data || []
      tableData.value = (dataRes.data || []).slice(0, 20)
    }

    // 获取技术指标（添加周期参数）
    const indicatorsRes = await getIndicators({
      symbol_id: selectedSymbolId.value,
      period: periodType.value
    })
    if (indicatorsRes.success) {
      indicatorsData.value = indicatorsRes.data || { ma: {}, macd: { dif: [], dea: [], macd: [] } }
    }
  } catch (e) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 处理主题变化
const handleThemeChange = (theme) => {
  // 主题变化处理，可保存到用户配置
}

// 处理键盘精灵选择
const handleKeyboardSelect = (item) => {
  selectedSymbolId.value = item.id
}

// 处理键盘快捷键
const handleKeydown = (e) => {
  // Ctrl+K 打开键盘精灵
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    showKeyboardWizard.value = true
  }
  // Ctrl+I 打开指标精灵
  if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
    e.preventDefault()
    showIndicatorWizard.value = true
  }
}

// 处理MA变化
const handleMAChange = (periods: string[]) => {
  maPeriods.value = periods
  // TODO: 重新获取指标数据或通知ProChart
}

// 处理MACD变化
const handleMACDChange = (params: { fast: number; slow: number; signal: number }) => {
  macdParams.value = params
  // TODO: 重新获取指标数据或通知ProChart
}

// 处理VOL变化
const handleVOLChange = (periods: string[]) => {
  volPeriods.value = periods
  // TODO: 重新获取指标数据或通知ProChart
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

onMounted(() => {
  fetchSymbols()
  // 注册键盘快捷键
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  proChartRef.value?.cleanup()
  // 移除键盘快捷键监听
  window.removeEventListener('keydown', handleKeydown)
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

/* 专业图表区域 */
.pro-chart-section {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  box-shadow: var(--fdas-shadow-card);
  height: 500px;
  margin-bottom: var(--fdas-spacing-lg);
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
  .pro-chart-section {
    height: 400px;
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

  .pro-chart-section {
    height: 350px;
  }
}
</style>