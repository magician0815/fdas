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
        <span class="stats-label">开盘</span>
        <span class="stats-value">{{ rangeData.startPrice }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">收盘</span>
        <span class="stats-value">{{ rangeData.endPrice }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">涨跌</span>
        <span class="stats-value" :class="changeClass">{{ rangeData.changePercent }}</span>
      </div>
      <div class="stats-divider"></div>
      <div class="stats-row">
        <span class="stats-label">最高</span>
        <span class="stats-value high">{{ rangeData.highPrice }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">最低</span>
        <span class="stats-value low">{{ rangeData.lowPrice }}</span>
      </div>
      <div class="stats-row">
        <span class="stats-label">期数</span>
        <span class="stats-value">{{ rangeData.periods }}</span>
      </div>
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
    periods: number
    startPrice: string
    endPrice: string
    changeAmount: string
    changePercent: string
    highPrice: string
    lowPrice: string
    amplitude: string
    avgPrice: string
  }
}

const props = defineProps<Props>()

// Emits定义
defineEmits<{
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
  top: 8px;
  right: 8px;
  width: 140px;
  background: var(--fdas-bg-card);
  border-radius: 6px;
  box-shadow: var(--fdas-shadow-sm);
  z-index: 20;
  border: 1px solid var(--fdas-border-light);
  font-size: 11px;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 6px;
  border-bottom: 1px solid var(--fdas-border-light);
}

.stats-title {
  font-size: 10px;
  font-weight: 600;
  color: var(--fdas-primary);
}

.stats-body {
  padding: 4px 6px;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 0;
}

.stats-label {
  font-size: 10px;
  color: var(--fdas-text-muted);
}

.stats-value {
  font-size: 10px;
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
  margin: 3px 0;
}
</style>