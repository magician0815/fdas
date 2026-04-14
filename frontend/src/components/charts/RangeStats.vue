<template>
  <div class="range-stats-panel" v-if="rangeData">
    <div class="stats-header">
      <span class="stats-title">区间统计</span>
      <el-button size="small" text @click="$emit('close')">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>
    <div class="stats-body">
      <div class="stats-row">
        <span class="stats-label">区间范围</span>
        <span class="stats-value">{{ rangeData.startDate }} ~ {{ rangeData.endDate }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">交易天数</span>
        <span class="stats-value">{{ rangeData.days }}天</span>
      </div>
      <div class="stats-divider"></div>
      <div class="stats-row">
        <span class="stats-label">起始价格</span>
        <span class="stats-value">{{ rangeData.startPrice }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">结束价格</span>
        <span class="stats-value">{{ rangeData.endPrice }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">涨跌额</span>
        <span class="stats-value" :class="changeClass">{{ rangeData.changeAmount }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">涨跌幅</span>
        <span class="stats-value" :class="changeClass">{{ rangeData.changePercent }}</span>
      </div>
      <div class="stats-divider"></div>
      <div class="stats-row">
        <span class="stats-label">最高价</span>
        <span class="stats-value high">{{ rangeData.highPrice }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">最低价</span>
        <span class="stats-value low">{{ rangeData.lowPrice }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">振幅</span>
        <span class="stats-value">{{ rangeData.amplitude }}</span>
      </div>
      <div class="stats-divider"></div>
      <div class="stats-row">
        <span class="stats-label">平均价格</span>
        <span class="stats-value">{{ rangeData.avgPrice }}</span>
      </div>
      <!-- 涨跌停统计（仅股票市场显示） -->
      <template v-if="rangeData.limitUpCount !== undefined">
        <div class="stats-divider"></div>
        <div class="stats-row limit-row">
          <span class="stats-label">涨停次数</span>
          <span class="stats-value limit-up">{{ rangeData.limitUpCount }}次</span>
        </div>
        <div class="stats-row limit-row">
          <span class="stats-label">跌停次数</span>
          <span class="stats-value limit-down">{{ rangeData.limitDownCount }}次</span>
        </div>
        <div class="stats-row limit-row" v-if="rangeData.limitUpDates && rangeData.limitUpDates.length > 0">
          <span class="stats-label">涨停日期</span>
          <span class="stats-value limit-up small">{{ rangeData.limitUpDates.join(', ') }}</span>
        </div>
        <div class="stats-row limit-row" v-if="rangeData.limitDownDates && rangeData.limitDownDates.length > 0">
          <span class="stats-label">跌停日期</span>
          <span class="stats-value limit-down small">{{ rangeData.limitDownDates.join(', ') }}</span>
        </div>
        <div class="stats-row limit-row">
          <span class="stats-label">涨停占比</span>
          <span class="stats-value limit-up">{{ (rangeData.limitUpRatio * 100).toFixed(1) }}%</span>
        </div>
        <div class="stats-row limit-row">
          <span class="stats-label">跌停占比</span>
          <span class="stats-value limit-down">{{ (rangeData.limitDownRatio * 100).toFixed(1) }}%</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 区间统计面板组件.
 *
 * 显示选定区间的统计数据（涨跌幅、振幅、最高最低价等）.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { computed } from 'vue'
import { Close } from '@element-plus/icons-vue'

// Props定义
interface Props {
  /** 区间统计数据 */
  rangeData?: {
    startDate: string
    endDate: string
    days: number
    startPrice: string
    endPrice: string
    changeAmount: string
    changePercent: string
    highPrice: string
    lowPrice: string
    amplitude: string
    avgPrice: string
    /** 涨停次数（可选，仅股票市场） */
    limitUpCount?: number
    /** 跌停次数（可选，仅股票市场） */
    limitDownCount?: number
    /** 涨停日期列表（可选） */
    limitUpDates?: string[]
    /** 跌停日期列表（可选） */
    limitDownDates?: string[]
    /** 涨停占比（可选） */
    limitUpRatio?: number
    /** 跌停占比（可选） */
    limitDownRatio?: number
  }
}

const props = defineProps<Props>()

// Emits定义
const emit = defineEmits<{
  (e: 'close'): void
}>()

// 计算涨跌样式
const changeClass = computed(() => {
  if (!props.rangeData) return ''
  const change = parseFloat(props.rangeData.changePercent)
  if (change > 0) return 'up'
  if (change < 0) return 'down'
  return ''
})
</script>

<style scoped>
.range-stats-panel {
  position: absolute;
  top: 50px;
  right: 12px;
  width: 200px;
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-md);
  box-shadow: var(--fdas-shadow-card);
  z-index: 20;
  border: 1px solid var(--fdas-border-light);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--fdas-border-light);
}

.stats-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.stats-body {
  padding: 8px 12px;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.stats-label {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.stats-value {
  font-size: 12px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.stats-value.up {
  color: #ef4444;
}

.stats-value.down {
  color: #22c55e;
}

.stats-value.high {
  color: #ef4444;
}

.stats-value.low {
  color: #22c55e;
}

.stats-divider {
  height: 1px;
  background: var(--fdas-border-light);
  margin: 6px 0;
}

.stats-value.limit-up {
  color: #ef4444;
}

.stats-value.limit-down {
  color: #22c55e;
}

.stats-value.small {
  font-size: 10px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.limit-row {
  background: rgba(245, 158, 11, 0.05);
  border-radius: 2px;
  padding: 4px 4px;
}
</style>