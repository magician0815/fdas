<template>
  <div class="market-overview-page" :class="{ 'page-dark': isDark }">
    <!-- 标头区域 -->
    <div class="page-header">
      <div class="header-left">
        <!-- 标的搜索（跨市场全局搜索） -->
        <el-select
          v-model="symbolId"
          filterable
          remote
          :remote-method="searchSymbols"
          :loading="searchLoading"
          placeholder="搜索标的（代码/名称）..."
          size="small"
          style="width: 260px"
          @change="handleSymbolChange"
        >
          <el-option
            v-for="s in searchResults"
            :key="`${s._market}-${s.id}`"
            :label="`${s.code} ${s.name || ''}`"
            :value="s.id"
          >
            <div class="search-option">
              <span class="search-option-code">{{ s.code }}</span>
              <span class="search-option-name">{{ s.name || '' }}</span>
              <el-tag size="small" type="info" class="search-option-market">
                {{ getMarketDisplayName(s._market) }}
              </el-tag>
            </div>
          </el-option>
        </el-select>

        <!-- 当前市场标签 -->
        <el-tag v-if="currentMarketId" size="small" effect="dark" type="warning">
          {{ getMarketDisplayName(currentMarketId) }}
        </el-tag>

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

      <div class="symbol-info" v-if="symbolName">
        <span v-if="latestPrice !== null" class="symbol-price" :style="{ color: priceColor }">
          {{ latestPrice }}
        </span>
        <span v-if="dailyChange !== null" class="symbol-change" :class="changeClass">
          {{ dailyChange }}
        </span>
        <span class="symbol-name">{{ symbolName }}</span>
        <span class="symbol-code">{{ symbolCode }}</span>
        <el-tag
          v-if="dataFreshness.show"
          :type="dataFreshness.type"
          size="small"
          class="price-tag"
        >
          {{ dataFreshness.text }}
        </el-tag>
      </div>
    </div>

    <!-- 图表区域 -->
    <ChartDashboard
      :market-id="currentMarketId"
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
 * 统一行情数据页面 — 跨市场全局搜索 + market_id 自动识别.
 *
 * 搜索时并发查询所有市场 API，选中标的后根据 market_id 自动切换市场配置，
 * 无需手动选择市场。ChartDashboard 由 MarketProfile 驱动自适应.
 *
 * Author: FDAS Team
 * Created: 2026-07-23
 */
import { ref, computed, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'
import { getMarkets } from '@/api/markets'
import {
  getMarketProfile,
  registerMarketPresets,
  getAllMarkets,
  type MarketProfile,
  type AdjustmentType,
} from '@/composables/useMarketProfile'
import ChartDashboard from '@/components/charts/ChartDashboard.vue'
import logger from '@/services/logger'

// 确保市场预设已注册
if (getMarketProfile('stock_cn') === undefined) {
  registerMarketPresets()
}

// ---- 跨市场搜索配置 ----

/** 搜索源：每个 API 命名空间对应一个或多个市场代码 */
const SEARCH_SOURCES = [
  { namespace: 'fx_data', market: 'forex' },
  { namespace: 'stock_data', market: 'stock_cn' },    // 含 stock_cn/us/hk（通过 market_id 区分）
  { namespace: 'futures_data', market: 'futures_cn' },
  { namespace: 'bond_data', market: 'bond_cn' },      // 含 bond_cn/us（通过 market_id 区分）
]

// ---- 状态 ----

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)

const currentMarketId = ref<string>('forex')
const profile = computed<MarketProfile>(() => {
  return getMarketProfile(currentMarketId.value) || getMarketProfile('forex')!
})

const symbolId = ref('')
const symbolCode = ref('')
const symbolName = ref('')
const period = ref('daily')
const loading = ref(false)
const chartData = ref<any[]>([])
const searchLoading = ref(false)
const searchResults = ref<any[]>([])

/** market UUID → market_code 映射缓存 */
const marketIdMap = ref<Map<string, string>>(new Map())

/** market_code → displayName 映射 */
const marketDisplayMap = ref<Map<string, string>>(new Map())

function getMarketDisplayName(code: string): string {
  return marketDisplayMap.value.get(code) || code
}

// ---- 标头信息 ----

const latestPrice = computed(() => {
  if (!chartData.value.length) return null
  const last = chartData.value[chartData.value.length - 1]
  return Number(last.close).toFixed(profile.value.pricePrecision)
})

const dailyChange = computed(() => {
  if (chartData.value.length < 2) return null
  const last = chartData.value[chartData.value.length - 1]
  const prev = chartData.value[chartData.value.length - 2]
  if (!prev) return null
  const change = Number(last.close) - Number(prev.close)
  const pct = (change / Number(prev.close)) * 100
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(profile.value.pricePrecision)} (${sign}${pct.toFixed(2)}%)`
})

const priceColor = computed(() => {
  if (chartData.value.length < 2) return '#666666'
  const last = chartData.value[chartData.value.length - 1]
  const prev = chartData.value[chartData.value.length - 2]
  if (!prev) return '#666666'
  return Number(last.close) >= Number(prev.close) ? '#ef4444' : '#22c55e'
})

const changeClass = computed(() => {
  if (chartData.value.length < 2) return ''
  const last = chartData.value[chartData.value.length - 1]
  const prev = chartData.value[chartData.value.length - 2]
  if (!prev) return ''
  return Number(last.close) >= Number(prev.close) ? 'up' : 'down'
})

const dataFreshness = computed(() => {
  if (!chartData.value.length) return { show: false, type: 'info', text: '' }
  const last = chartData.value[chartData.value.length - 1]
  const lastDate = new Date(last.date || last.timestamp)
  const now = new Date()
  const daysDiff = Math.floor((now.getTime() - lastDate.getTime()) / 86400000)
  if (daysDiff > 7) return { show: true, type: 'danger', text: `数据过期(${daysDiff}天前)` }
  if (daysDiff > 2) return { show: true, type: 'warning', text: `数据较旧(${daysDiff}天前)` }
  return { show: false, type: 'info', text: '' }
})

// ---- 方法 ----

/** 通过 market_id UUID 解析 market_code */
function resolveMarketCode(item: any, sourceMarket: string): string {
  // 优先用 API 返回的 market_id 查找
  if (item.market_id) {
    const code = marketIdMap.value.get(item.market_id)
    if (code) return code
  }
  // 回退到搜索源映射
  return sourceMarket
}

async function searchSymbols(query: string): Promise<void> {
  if (!query || query.length < 1) {
    searchResults.value = []
    return
  }
  searchLoading.value = true
  try {
    // 并行搜索所有市场 API
    const searches = SEARCH_SOURCES.map(async ({ namespace, market }) => {
      try {
        const mod = await import(`@/api/${namespace}.js`)
        const response = await mod.searchSymbols?.(query)
        const items = response?.data || []
        return items.map((item: any) => ({
          ...item,
          _market: resolveMarketCode(item, market),
        }))
      } catch {
        return []
      }
    })

    const allResults = await Promise.all(searches)
    // 合并并按代码排序
    const merged = allResults.flat().sort((a: any, b: any) =>
      (a.code || '').localeCompare(b.code || '')
    )
    // 去重（同一标的可能出现在多个 API，保留 market 优先匹配）
    const seen = new Set<string>()
    searchResults.value = merged.filter((r: any) => {
      const key = r.code
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  } catch {
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

async function fetchData(): Promise<void> {
  if (!symbolId.value) return
  const ns = profile.value.apiNamespace
  loading.value = true
  try {
    const { getChartData: apiGetChart } = await import(`@/api/${ns}.js`)
    const response = await apiGetChart?.(symbolId.value, period.value)
    chartData.value = response?.data || []
  } catch (err) {
    logger.error('MarketOverview数据加载失败', err)
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

    // 根据标的的 market_id（来自 API 响应）自动切换市场
    const marketCode = selected._market || 'forex'
    if (marketCode !== currentMarketId.value) {
      currentMarketId.value = marketCode
    }

    fetchData()
  }
}

function handlePeriodChange(): void {
  fetchData()
}

function handleAdjustmentChange(_type: AdjustmentType): void {
  fetchData()
}

function handleFetchDataRequest(params: { symbolId: string; period: string }): void {
  symbolId.value = params.symbolId
  period.value = params.period
  fetchData()
}

// ---- 初始化 ----

onMounted(async () => {
  // 构建 market UUID → code 映射
  try {
    const res = await getMarkets()
    const markets = res?.data || []
    const uuidMap = new Map<string, string>()
    const displayMap = new Map<string, string>()
    for (const m of markets) {
      uuidMap.set(m.id, m.code)
      displayMap.set(m.code, m.name || m.code)
    }
    marketIdMap.value = uuidMap

    // 同时也注册所有市场配置的 displayName
    for (const p of getAllMarkets()) {
      if (!displayMap.has(p.id)) {
        displayMap.set(p.id, p.displayName)
      }
    }
    marketDisplayMap.value = displayMap
  } catch {
    // 回退：使用 MarketProfile 的 displayName
    const displayMap = new Map<string, string>()
    for (const p of getAllMarkets()) {
      displayMap.set(p.id, p.displayName)
    }
    marketDisplayMap.value = displayMap
  }
})
</script>

<style scoped>
.market-overview-page {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.symbol-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.symbol-name {
  font-size: 20px;
  font-weight: 700;
}

.symbol-price {
  font-size: 22px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.symbol-change {
  font-size: 14px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.symbol-change.up {
  color: #ef4444;
}

.symbol-change.down {
  color: #22c55e;
}

.symbol-code {
  font-size: 14px;
  color: var(--chart-text-secondary, #666666);
}

.price-tag {
  font-variant-numeric: tabular-nums;
}

/* 搜索结果选项样式 */
.search-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.search-option-code {
  font-weight: 600;
  min-width: 80px;
}

.search-option-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--chart-text-secondary, #666666);
}

.search-option-market {
  flex-shrink: 0;
}
</style>
