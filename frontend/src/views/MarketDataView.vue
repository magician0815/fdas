<template>
  <div class="market-data-page" :class="{ 'page-dark': isDark }">
    <!-- 标头区域 -->
    <div class="page-header">
      <div class="symbol-info" v-if="symbolName">
        <span class="symbol-name">{{ symbolName }}</span>
        <span class="symbol-code">{{ symbolCode }}</span>
        <el-tag
          v-if="priceChange.show"
          :type="priceChange.type"
          size="small"
          class="price-tag"
        >
          {{ priceChange.text }}
        </el-tag>
      </div>

      <div class="header-controls">
        <!-- 标的搜索 -->
        <div class="symbol-search">
          <el-select
            v-model="symbolId"
            filterable
            remote
            :remote-method="searchSymbols"
            :loading="searchLoading"
            placeholder="搜索标的..."
            size="small"
            style="width: 220px"
            @change="handleSymbolChange"
          >
            <el-option
              v-for="s in searchResults"
              :key="s.id"
              :label="`${s.code} ${s.name || ''}`"
              :value="s.id"
            />
          </el-select>
        </div>

        <!-- 周期选择 -->
        <el-select
          v-model="period"
          size="small"
          style="width: 100px"
          @change="handlePeriodChange"
        >
          <el-option
            v-for="p in profile.periodOptions"
            :key="p.value"
            :label="p.label"
            :value="p.value"
          />
        </el-select>

        <el-divider direction="vertical" />

        <el-button size="small" @click="fetchData" :loading="loading">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 图表区域 -->
    <ChartDashboard
      :market-id="marketId"
      :symbol-id="symbolId"
      :symbol-code="symbolCode"
      :symbol-name="symbolName"
      :period="period"
      :data="chartData"
      :loading="loading"
      :toolbar-visible="true"
      @adjustment-change="handleAdjustmentChange"
      @fetch-data="handleFetchDataRequest"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 统一行情数据页面 — 替代 StockData.vue / FXData.vue / FuturesData.vue / BondData.vue.
 *
 * 通过 route props 传入 marketId，由 MarketProfile 驱动所有市场差异化行为.
 * 数据通过 FastAPI 后端获取，完全离线.
 *
 * Author: FDAS Team
 * Created: 2026-07-21
 */
import { ref, computed, onMounted, watch } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'
import {
  getMarketProfile,
  registerMarketPresets,
  type MarketProfile,
  type AdjustmentType,
} from '@/composables/useMarketProfile'
import ChartDashboard from '@/components/charts/ChartDashboard.vue'

// 确保市场预设已注册
if (getMarketProfile('stock_cn') === undefined) {
  registerMarketPresets()
}

// ---- Props (从路由传入) ----

const props = defineProps<{
  marketId: string
}>()

// ---- 状态 ----

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)

const profile = computed<MarketProfile>(() => {
  return getMarketProfile(props.marketId) || getMarketProfile('forex')!
})

const symbolId = ref('')
const symbolCode = ref('')
const symbolName = ref('')
const period = ref('daily')
const loading = ref(false)
const chartData = ref<any[]>([])
const searchLoading = ref(false)
const searchResults = ref<any[]>([])

// ---- 标头信息 ----

const priceChange = computed(() => {
  if (!chartData.value.length) return { show: false, type: '', text: '' }
  const last = chartData.value[chartData.value.length - 1]
  const prev = chartData.value[chartData.value.length - 2]
  if (!prev) return { show: false, type: '', text: '' }

  const change = Number(last.close) - Number(prev.close)
  const pct = (change / Number(prev.close)) * 100
  const sign = change >= 0 ? '+' : ''
  return {
    show: true,
    type: change >= 0 ? 'danger' : 'success',
    text: `${sign}${change.toFixed(profile.value.pricePrecision)} (${sign}${pct.toFixed(2)}%)`,
  }
})

// ---- 方法 ----

async function searchSymbols(query: string): Promise<void> {
  if (!query || query.length < 1) {
    searchResults.value = []
    return
  }
  searchLoading.value = true
  try {
    // 调用对应市场的 API
    const { searchSymbols: apiSearch } = await import(`@/api/${profile.value.apiNamespace}.js`)
    const response = await apiSearch?.(query)
    searchResults.value = response?.data || []
  } catch {
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

async function fetchData(): Promise<void> {
  if (!symbolId.value) return
  loading.value = true
  try {
    const { getChartData: apiGetChart } = await import(`@/api/${profile.value.apiNamespace}.js`)
    const response = await apiGetChart?.(symbolId.value, period.value)
    chartData.value = response?.data || []
  } catch (err) {
    console.error('[MarketDataView] 数据加载失败:', err)
  } finally {
    loading.value = false
  }
}

function handleSymbolChange(id: string): void {
  const selected = searchResults.value.find((s: any) => s.id === id)
  if (selected) {
    symbolCode.value = selected.code
    symbolName.value = selected.name || selected.code
    symbolId.value = id
    fetchData()
  }
}

function handlePeriodChange(): void {
  fetchData()
}

function handleAdjustmentChange(type: AdjustmentType): void {
  // 复权变更 — 数据预处理后刷新
  fetchData()
}

function handleFetchDataRequest(params: { symbolId: string; period: string }): void {
  symbolId.value = params.symbolId
  period.value = params.period
  fetchData()
}

// ---- 生命周期 ----

onMounted(() => {
  if (period.value) {
    // 首次加载等待 symbolId 选择
  }
})
</script>

<style scoped>
.market-data-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  padding: 16px;
  background: var(--page-bg, #f5f7fa);
}

.page-dark {
  background: #111827;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.symbol-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.symbol-name {
  font-size: 18px;
  font-weight: 600;
}

.symbol-code {
  font-size: 14px;
  color: var(--chart-text-secondary, #666666);
}

.price-tag {
  font-variant-numeric: tabular-nums;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
