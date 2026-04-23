<template>
  <div class="futures-data-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <!-- 标的信息：名称、代码、价格、涨跌幅 -->
        <div class="symbol-info">
          <span class="symbol-name">{{ selectedSymbolName || '----' }}</span>
          <span class="symbol-code">{{ selectedSymbolCode || '----' }}</span>
          <span class="price-value" :class="priceClass">{{ currentPrice || '---' }}</span>
          <span class="price-value change" :class="priceClass">{{ changePercent || '---' }}</span>
          <el-tag v-if="isMainContract" type="success" size="small" class="main-tag">主力</el-tag>
        </div>
      </div>
      <div class="header-right">
        <!-- 金融标的搜索 -->
        <el-select
          v-model="selectedSymbolId"
          placeholder="输入合约代码"
          class="symbol-select"
          filterable
          remote
          :remote-method="handleSymbolSearch"
          :loading="symbolSearchLoading"
          @change="fetchData"
        >
          <el-option
            v-for="s in filteredSymbols"
            :key="s.id"
            :label="`${s.name} (${s.code})`"
            :value="s.id"
          />
        </el-select>

        <!-- 周期切换 -->
        <el-select
          v-model="periodType"
          placeholder="周期"
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
        <el-button size="small" type="primary" @click="fetchData" :loading="loading">
          <el-icon><Refresh /></el-icon>
        </el-button>
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
        :showVolume="true"
        :showPosition="true"
        @fetchData="fetchData"
      />
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
 * 期货行情数据页面.
 *
 * 展示期货专业行情走势图表，支持持仓量副图.
 *
 * Author: FDAS Team
 * Created: 2026-04-23
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getFuturesDailyData } from '@/api/futures_data'
import { getFuturesVarieties } from '@/api/futures_varieties'
import ProChart from '@/components/charts/ProChart.vue'
import KeyboardWizard from '@/components/charts/KeyboardWizard.vue'
import IndicatorWizard from '@/components/charts/IndicatorWizard.vue'


// 数据状态
const loading = ref(false)
const chartData = ref([])
const indicatorsData = ref({ ma: {}, macd: { dif: [], dea: [], macd: [] } })
const symbols = ref([])
const filteredSymbols = ref([])
const symbolSearchLoading = ref(false)

// 周期类型状态
const periodType = ref<string>(
  localStorage.getItem('fdas_futures_period_type') || 'daily'
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
  localStorage.setItem('fdas_futures_period_type', period)
  fetchData()
}

// 选择状态
const selectedSymbolId = ref(null)
const showKeyboardWizard = ref(false)
const showIndicatorWizard = ref(false)

// 合约状态
const isMainContract = ref(false)

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

const selectedSymbolCode = computed(() => {
  if (!selectedSymbolId.value) return ''
  const symbol = symbols.value.find(s => s.id === selectedSymbolId.value)
  return symbol ? symbol.code : ''
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

const priceClass = computed(() => {
  if (!selectedSymbolId.value || !changePercent.value) return ''
  const value = parseFloat(changePercent.value)
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return ''
})

// 键盘精灵数据（使用完整列表）
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
  return parseFloat(value).toFixed(2)
}

// 格式化涨跌幅
const formatChange = (value) => {
  if (!value) return '--'
  return `${parseFloat(value).toFixed(2)}%`
}

// 标的远程搜索
const handleSymbolSearch = async (query: string) => {
  if (!query) {
    filteredSymbols.value = []
    return
  }

  symbolSearchLoading.value = true
  try {
    const res = await getFuturesVarieties({ search: query })
    if (res.success) {
      symbols.value = res.data || []
      // 根据输入的代码或名称过滤
      const lowerQuery = query.toLowerCase()
      filteredSymbols.value = symbols.value.filter(s =>
        s.code.toLowerCase().includes(lowerQuery) ||
        s.name.toLowerCase().includes(lowerQuery)
      )
    }
  } catch (e) {
    ElMessage.error('获取期货品种列表失败')
  } finally {
    symbolSearchLoading.value = false
  }
}

// 获取数据
const fetchData = async () => {
  if (!selectedSymbolId.value) return

  loading.value = true
  try {
    // 获取期货行情数据
    const dataRes = await getFuturesDailyData({
      contract_id: selectedSymbolId.value,
      limit: periodType.value === 'daily' ? 1000 : (periodType.value === 'weekly' ? 208 : 48)
    })
    if (dataRes.success) {
      chartData.value = dataRes.data || []
    }
  } catch (e) {
    ElMessage.error('获取期货数据失败')
  } finally {
    loading.value = false
  }
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
}

// 处理MACD变化
const handleMACDChange = (params: { fast: number; slow: number; signal: number }) => {
  macdParams.value = params
}

// 处理VOL变化
const handleVOLChange = (periods: string[]) => {
  volPeriods.value = periods
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  proChartRef.value?.cleanup()
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
.futures-data-page {
  max-width: 1400px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--fdas-spacing-md);
}

.header-left {
  display: flex;
  flex-direction: column;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
}

/* 标的信息展示 */
.symbol-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.symbol-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.symbol-code {
  color: var(--fdas-primary);
  font-weight: 500;
}

.price-value {
  font-weight: 500;
  color: var(--fdas-text-muted);
}

.price-value.change {
  padding-left: 4px;
}

.price-value.positive { color: #ef4444; }
.price-value.negative { color: #22c55e; }

.main-tag {
  margin-left: 8px;
}

[data-theme="dark"] .symbol-name {
  color: var(--fdas-text-primary);
}

[data-theme="dark"] .price-value {
  color: var(--fdas-text-muted);
}

[data-theme="dark"] .price-value.positive { color: #ef4444; }
[data-theme="dark"] .price-value.negative { color: #22c55e; }

.symbol-select {
  width: 200px;
}

.period-select {
  width: 80px;
}

/* 专业图表区域 */
.pro-chart-section {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  box-shadow: var(--fdas-shadow-card);
  height: 500px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .pro-chart-section {
    height: 400px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--fdas-spacing-sm);
  }

  .header-right {
    flex-wrap: wrap;
    width: 100%;
  }

  .symbol-select {
    width: 100%;
  }

  .pro-chart-section {
    height: 350px;
  }
}
</style>