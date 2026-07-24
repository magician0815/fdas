<template>
  <div class="chart-toolbar" :class="{ 'toolbar-dark': theme === 'dark' }">
    <!-- 副图开关 -->
    <el-button-group size="small" v-if="subChartSlots.length > 0">
      <el-button
        v-for="slot in subChartSlots"
        :key="slot.id"
        :type="visibleSubCharts[slot.id] ? 'primary' : ''"
        @click="toggleSubChart(slot.id, slot.indicatorName)"
      >
        {{ subChartLabels[slot.id] || slot.indicatorName }}
      </el-button>
    </el-button-group>

    <el-divider direction="vertical" />

    <!-- 画线工具 -->
    <el-dropdown v-if="drawingTools.length > 0" @command="handleDrawingTool">
      <el-button size="small">
        画线工具<el-icon class="el-icon--right"><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item
            v-for="tool in drawingTools"
            :key="tool"
            :command="tool"
          >
            {{ drawingToolLabels[tool] || tool }}
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <div class="toolbar-spacer" />

    <!-- 主题切换 -->
    <el-button size="small" @click="$emit('themeToggle')">
      <el-icon><Sunny v-if="theme === 'dark'" /><Moon v-else /></el-icon>
    </el-button>

    <!-- 导出 -->
    <el-button size="small" @click="$emit('exportImage')">
      <el-icon><Download /></el-icon>
    </el-button>

    <!-- 重置视图 -->
    <el-button size="small" @click="handleReset">
      <el-icon><RefreshRight /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
/**
 * 市场自适应工具栏 — 根据 MarketProfile 动态显示/隐藏功能按钮.
 *
 * 按钮点击映射到 KLineChart API 调用.
 */
import { ref, computed } from 'vue'
import {
  ArrowDown,
  Sunny,
  Moon,
  Download,
  RefreshRight,
} from '@element-plus/icons-vue'
import type { MarketProfile, SubChartSlot } from '@/composables/useMarketProfile'

const props = defineProps<{
  profile: MarketProfile
  chartRef: any        // KLineChart Chart 实例
  theme: string
}>()

const emit = defineEmits<{
  (e: 'themeToggle'): void
  (e: 'exportImage'): void
  (e: 'resetView'): void
}>()

const visibleSubCharts = ref<Record<string, boolean>>({})

// 初始化副图可见状态
for (const slot of props.profile.subChartSlots) {
  visibleSubCharts.value[slot.id] = slot.defaultVisible
}

const subChartSlots = computed(() => props.profile.subChartSlots)
const drawingTools = computed(() => {
  // KLineChart 内置的 15 种画线工具
  return [
    'segment', 'straightLine', 'rayLine',
    'horizontalStraightLine', 'horizontalRayLine', 'horizontalSegment',
    'verticalStraightLine', 'verticalRayLine', 'verticalSegment',
    'priceLine', 'priceChannelLine', 'parallelStraightLine',
    'fibonacciLine', 'simpleAnnotation', 'simpleTag',
  ]
})

const subChartLabels: Record<string, string> = {
  volume: '成交量',
  macd: 'MACD',
  open_interest: '持仓量',
  yield: '收益率',
  yield_spread: '中美利差',
}

const drawingToolLabels: Record<string, string> = {
  segment: '线段',
  straightLine: '直线',
  rayLine: '射线',
  horizontalStraightLine: '水平线',
  verticalStraightLine: '垂直线',
  priceLine: '价格线',
  fibonacciLine: '斐波那契',
  simpleAnnotation: '文字标注',
}

function toggleSubChart(id: string, indicatorName: string): void {
  visibleSubCharts.value[id] = !visibleSubCharts.value[id]
  const chart = props.chartRef
  if (!chart) return

  if (visibleSubCharts.value[id]) {
    if (indicatorName === 'MACD') {
      chart.createIndicator('MACD')
      chart.overrideIndicator({ name: 'MACD', styles: { bars: [{ style: 'fill' }] } })
    } else {
      chart.createIndicator(indicatorName)
    }
  } else {
    chart.removeIndicator({ name: indicatorName })
  }
}

function handleDrawingTool(toolName: string): void {
  const chart = props.chartRef
  if (!chart) return
  chart.createOverlay({ name: toolName })
}

function handleReset(): void {
  const chart = props.chartRef
  if (chart) {
    chart.scrollToRealTime()
  }
  emit('resetView')
}
</script>

<style scoped>
.chart-toolbar {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  gap: 6px;
  background: var(--chart-toolbar-bg, #fafafa);
  border-bottom: 1px solid var(--chart-toolbar-border, #e5e7eb);
  flex-wrap: wrap;
}

.toolbar-dark {
  background: #252540;
  border-color: #3a3a4e;
}

.toolbar-spacer {
  flex: 1;
}
</style>
