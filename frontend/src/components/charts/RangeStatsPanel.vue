<template>
  <div class="range-stats-panel" :class="{ 'panel-dark': isDark }">
    <div class="panel-header">
      <span class="panel-title">区间统计</span>
      <el-button size="small" text @click="$emit('close')">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>
    <div class="panel-body">
      <div class="stat-row" v-if="stats">
        <div class="stat-item">
          <span class="stat-label">开盘</span>
          <span class="stat-value">{{ stats.open }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">收盘</span>
          <span class="stat-value" :class="stats.closeClass">{{ stats.close }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">最高</span>
          <span class="stat-value">{{ stats.high }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">最低</span>
          <span class="stat-value">{{ stats.low }}</span>
        </div>
      </div>
      <div class="stat-row" v-if="stats">
        <div class="stat-item">
          <span class="stat-label">区间涨幅</span>
          <span class="stat-value" :class="stats.changeClass">{{ stats.changePercent }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">区间振幅</span>
          <span class="stat-value">{{ stats.amplitude }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总成交量</span>
          <span class="stat-value">{{ stats.totalVolume }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 区间统计浮层面板 — 显示框选区间内的价格统计信息.
 *
 * 从 Canvas 事件获取框选范围，通过 chart.convertFromPixel 转换为数据坐标后计算.
 */
import { computed } from 'vue'
import { Close } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'

const props = defineProps<{
  stats: {
    open: string
    close: string
    high: string
    low: string
    changePercent: string
    amplitude: string
    totalVolume: string
    closeClass: string
    changeClass: string
  } | null
}>()

defineEmits<{
  (e: 'close'): void
}>()

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
</script>

<style scoped>
.range-stats-panel {
  position: absolute;
  top: 8px;
  right: 60px;
  width: 220px;
  background: var(--chart-bg, #ffffff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.panel-dark {
  background: #1a1a2e;
  border-color: #3a3a4e;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.panel-title {
  font-size: 12px;
  font-weight: 600;
}

.panel-body {
  padding: 8px 10px;
}

.stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 0;
}

.stat-label {
  font-size: 11px;
  color: var(--chart-text-secondary, #666666);
}

.stat-value {
  font-size: 12px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
</style>
