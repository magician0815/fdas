<template>
  <div class="multi-period-layout" :class="layoutClass">
    <!-- 布局控制栏 -->
    <div class="layout-control">
      <div class="period-selector">
        <el-select v-model="layoutMode" size="small" @change="handleLayoutChange">
          <el-option label="双周期（上下）" value="2-vertical" />
          <el-option label="双周期（左右）" value="2-horizontal" />
          <el-option label="三周期（上二下一）" value="3-top" />
          <el-option label="三周期（上一下二）" value="3-bottom" />
          <el-option label="四周期（2x2网格）" value="4-grid" />
        </el-select>
      </div>
      <div class="period-configs">
        <div v-for="(config, index) in periodConfigs" :key="index" class="period-config-item">
          <span class="period-label">周期{{ index + 1 }}:</span>
          <el-select v-model="config.period" size="small" @change="handlePeriodConfigChange(index)">
            <el-option label="日线" value="daily" />
            <el-option label="周线" value="weekly" />
            <el-option label="月线" value="monthly" />
            <el-option label="60分钟" value="60" />
            <el-option label="30分钟" value="30" />
            <el-option label="15分钟" value="15" />
            <el-option label="5分钟" value="5" />
            <el-option label="1分钟" value="1" />
          </el-select>
          <el-checkbox v-model="config.syncEnabled" size="small" :disabled="index === 0">
            同步
          </el-checkbox>
        </div>
      </div>
      <div class="sync-control">
        <el-switch
          v-model="globalSync"
          size="small"
          active-text="时间同步"
          inactive-text="独立"
          @change="handleGlobalSyncChange"
        />
      </div>
    </div>

    <!-- 多周期图表区域 -->
    <div class="charts-container" :class="containerClass">
      <div
        v-for="(config, index) in visiblePeriodConfigs"
        :key="index"
        class="chart-panel"
        :style="getPanelStyle(index)"
      >
        <div class="chart-header">
          <span class="chart-title">{{ getPeriodTitle(config.period) }}</span>
          <div class="chart-actions">
            <el-button size="small" text @click="togglePanelFullscreen(index)">
              <el-icon><FullScreen v-if="!config.isFullscreen" /><Close v-else /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="chart-content">
          <KLineChart
            :ref="el => chartRefs[index] = el"
            :symbolCode="symbolCode"
            :data="chartDatas[index]"
            :period="config.period"
            :visibleRange="config.visibleRange"
            :syncEnabled="config.syncEnabled"
            :height="getChartHeight(index)"
            :showToolbar="!config.isFullscreen"
            :syncMarker="syncMarker"
            @rangeChange="handleRangeChange(index, $event)"
            @dateClick="handleDateClick(index, $event)"
          />
        </div>
      </div>
    </div>

    <!-- 同步时间线指示器 -->
    <div v-if="globalSync && syncMarker.visible" class="sync-indicator">
      <div class="sync-date">{{ syncMarker.date }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 多周期同屏布局组件.
 *
 * 支持多个周期K线图同时显示，时间轴同步，独立缩放.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { FullScreen, Close } from '@element-plus/icons-vue'
import KLineChart from './KLineChart.vue'

// Props定义
interface Props {
  /** 标的代码 */
  symbolCode?: string
  /** 初始布局模式 */
  initialLayout?: string
  /** 初始周期配置 */
  initialPeriods?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  symbolCode: 'USDCNY',
  initialLayout: '2-vertical',
  initialPeriods: () => ['daily', 'weekly']
})

// Emits定义
const emit = defineEmits<{
  (e: 'layoutChange', layout: string): void
  (e: 'periodChange', periods: string[]): void
  (e: 'syncClick', data: { date: string; periods: string[] }): void
}>()

// 状态
const layoutMode = ref<string>(props.initialLayout)
const globalSync = ref<boolean>(true)
const chartRefs = ref<any[]>([])
const syncMarker = ref<{ visible: boolean; date: string; x: number }>({
  visible: false,
  date: '',
  x: 0
})

// 周期配置
interface PeriodConfig {
  period: string
  syncEnabled: boolean
  visibleRange: [number, number] | null
  isFullscreen: boolean
  data: any[]
}

const periodConfigs = ref<PeriodConfig[]>([
  { period: 'daily', syncEnabled: true, visibleRange: null, isFullscreen: false, data: [] },
  { period: 'weekly', syncEnabled: true, visibleRange: null, isFullscreen: false, data: [] },
  { period: 'monthly', syncEnabled: false, visibleRange: null, isFullscreen: false, data: [] },
  { period: '60', syncEnabled: false, visibleRange: null, isFullscreen: false, data: [] }
])

// 图表数据（模拟，实际应从API获取）
const chartDatas = ref<any[]>([[], [], [], []])

// 计算布局类
const layoutClass = computed(() => {
  return `layout-${layoutMode.value}`
})

// 计算容器类
const containerClass = computed(() => {
  const classes = ['charts-container']
  if (periodConfigs.value.some(c => c.isFullscreen)) {
    classes.push('has-fullscreen')
  }
  return classes.join(' ')
})

// 计算可见的周期配置数量
const visibleCount = computed(() => {
  const mode = layoutMode.value
  if (mode.startsWith('2')) return 2
  if (mode.startsWith('3')) return 3
  if (mode.startsWith('4')) return 4
  return 2
})

// 计算可见的周期配置
const visiblePeriodConfigs = computed(() => {
  return periodConfigs.value.slice(0, visibleCount.value)
})

// 获取周期标题
const getPeriodTitle = (period: string): string => {
  const titles: Record<string, string> = {
    'daily': '日K',
    'weekly': '周K',
    'monthly': '月K',
    '60': '60分钟',
    '30': '30分钟',
    '15': '15分钟',
    '5': '5分钟',
    '1': '1分钟'
  }
  return titles[period] || period
}

// 获取面板样式
const getPanelStyle = (index: number): Record<string, string> => {
  const config = visiblePeriodConfigs.value[index]
  if (config.isFullscreen) {
    return {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100vw',
      height: '100vh',
      zIndex: '9999'
    }
  }

  const mode = layoutMode.value

  // 根据布局模式计算样式
  if (mode === '2-vertical') {
    return {
      width: '100%',
      height: '50%'
    }
  } else if (mode === '2-horizontal') {
    return {
      width: '50%',
      height: '100%'
    }
  } else if (mode === '3-top') {
    if (index < 2) {
      return {
        width: '50%',
        height: '50%'
      }
    } else {
      return {
        width: '100%',
        height: '50%'
      }
    }
  } else if (mode === '3-bottom') {
    if (index === 0) {
      return {
        width: '100%',
        height: '50%'
      }
    } else {
      return {
        width: '50%',
        height: '50%'
      }
    }
  } else if (mode === '4-grid') {
    return {
      width: '50%',
      height: '50%'
    }
  }

  return {}
}

// 获取图表高度
const getChartHeight = (index: number): number => {
  const config = visiblePeriodConfigs.value[index]
  if (config.isFullscreen) {
    return window.innerHeight - 60
  }

  // 根据布局计算高度
  const mode = layoutMode.value
  const baseHeight = 500 // 基础高度

  if (mode === '2-vertical') {
    return baseHeight / 2 - 30
  } else if (mode === '2-horizontal') {
    return baseHeight - 30
  } else if (mode === '3-top' || mode === '3-bottom') {
    return index === 0 ? baseHeight / 2 - 30 : baseHeight / 4 - 30
  } else if (mode === '4-grid') {
    return baseHeight / 2 - 30
  }

  return baseHeight - 30
}

// 处理布局变化
const handleLayoutChange = (layout: string) => {
  emit('layoutChange', layout)
  // 重置图表引用
  chartRefs.value = []
}

// 处理周期配置变化
const handlePeriodConfigChange = (index: number) => {
  const periods = visiblePeriodConfigs.value.map(c => c.period)
  emit('periodChange', periods)

  // 重新获取数据
  loadChartData(index)
}

// 处理全局同步变化
const handleGlobalSyncChange = (enabled: boolean) => {
  if (enabled) {
    // 启用同步，同步所有图表到第一个图表的时间范围
    syncAllCharts()
  }
}

// 处理范围变化
const handleRangeChange = (index: number, range: [number, number]) => {
  periodConfigs.value[index].visibleRange = range

  // 如果启用同步，同步其他图表
  if (globalSync.value) {
    syncOtherCharts(index, range)
  }
}

// 处理日期点击
const handleDateClick = (index: number, data: { date: string; x: number }) => {
  if (globalSync.value) {
    syncMarker.value = {
      visible: true,
      date: data.date,
      x: data.x
    }

    // 通知其他图表同步到该日期
    syncToDate(data.date)
  }

  emit('syncClick', {
    date: data.date,
    periods: visiblePeriodConfigs.value.map(c => c.period)
  })
}

// 同步所有图表
const syncAllCharts = () => {
  const firstRange = periodConfigs.value[0].visibleRange
  if (!firstRange) return

  for (let i = 1; i < visiblePeriodConfigs.value.length; i++) {
    if (chartRefs.value[i] && periodConfigs.value[i].syncEnabled) {
      chartRefs.value[i].syncZoom?.(firstRange[0], firstRange[1])
    }
  }
}

// 同步其他图表
const syncOtherCharts = (sourceIndex: number, range: [number, number]) => {
  for (let i = 0; i < visiblePeriodConfigs.value.length; i++) {
    if (i !== sourceIndex && chartRefs.value[i] && periodConfigs.value[i].syncEnabled) {
      chartRefs.value[i].syncZoom?.(range[0], range[1])
    }
  }
}

// 同步到指定日期
const syncToDate = (date: string) => {
  for (let i = 0; i < visiblePeriodConfigs.value.length; i++) {
    if (chartRefs.value[i] && periodConfigs.value[i].syncEnabled) {
      chartRefs.value[i].highlightDate?.(date)
    }
  }
}

// 切换面板全屏
const togglePanelFullscreen = (index: number) => {
  periodConfigs.value[index].isFullscreen = !periodConfigs.value[index].isFullscreen
}

// 加载图表数据
const loadChartData = async (index: number) => {
  // 模拟数据加载，实际应调用API
  const period = periodConfigs.value[index].period

  // TODO: 调用API获取对应周期的数据
  // const response = await fetchFxData({ symbolCode: props.symbolCode, period })
  // chartDatas.value[index] = response.data
}

// 键盘事件处理
const handleKeyDown = (e: KeyboardEvent) => {
  // ESC退出全屏
  if (e.key === 'Escape') {
    const fullscreenIndex = periodConfigs.value.findIndex(c => c.isFullscreen)
    if (fullscreenIndex !== -1) {
      periodConfigs.value[fullscreenIndex].isFullscreen = false
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)

  // 初始化加载所有图表数据
  for (let i = 0; i < visibleCount.value; i++) {
    loadChartData(i)
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.multi-period-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--fdas-bg-secondary);
}

/* 控制栏 */
.layout-control {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--fdas-bg-card);
  border-bottom: 1px solid var(--fdas-border-light);
  flex-wrap: wrap;
  gap: 8px;
}

.period-selector {
  display: flex;
  align-items: center;
}

.period-configs {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.period-config-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.period-label {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.sync-control {
  display: flex;
  align-items: center;
}

/* 图表容器 */
.charts-container {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.layout-2-vertical .charts-container {
  flex-direction: column;
}

.layout-2-horizontal .charts-container {
  flex-direction: row;
}

.layout-3-top .charts-container {
  flex-direction: column;
}

.layout-3-bottom .charts-container {
  flex-direction: column;
}

.layout-4-grid .charts-container {
  flex-direction: row;
  flex-wrap: wrap;
}

.has-fullscreen .charts-container {
  overflow: visible;
}

/* 图表面板 */
.chart-panel {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--fdas-border-light);
  overflow: hidden;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  background: var(--fdas-bg-card);
  border-bottom: 1px solid var(--fdas-border-light);
}

.chart-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.chart-actions {
  display: flex;
  gap: 4px;
}

.chart-content {
  flex: 1;
  overflow: hidden;
}

/* 同步指示器 */
.sync-indicator {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--fdas-primary);
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 9999;
  box-shadow: var(--fdas-shadow-card);
}

.sync-date {
  font-weight: 500;
}
</style>