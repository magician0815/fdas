<template>
  <div class="kline-chart-container">
    <!-- 图表头部工具栏 -->
    <div class="chart-toolbar">
      <div class="toolbar-left">
        <span class="chart-title">{{ symbolName || '选择货币对' }}</span>
        <span v-if="currentPrice" class="current-price" :class="priceClass">
          {{ currentPrice }}
        </span>
        <span v-if="changePercent" class="change-percent" :class="priceClass">
          {{ changePercent }}
        </span>
      </div>
      <div class="toolbar-right">
        <!-- 图表类型切换 -->
        <el-radio-group v-model="chartType" size="small" @change="handleChartTypeChange">
          <el-radio-button value="candle">K线</el-radio-button>
          <el-radio-button value="line">折线</el-radio-button>
        </el-radio-group>
        <!-- 右侧价格轴开关 -->
        <el-tooltip content="显示右侧价格轴" placement="top">
          <el-button size="small" :type="showRightAxis ? 'primary' : 'default'" @click="toggleRightAxis">
            <el-icon><Rank /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 价格坐标模式切换 -->
        <el-tooltip :content="priceAxisType === 'log' ? '对数坐标' : '线性坐标'" placement="top">
          <el-button size="small" :type="priceAxisType === 'log' ? 'primary' : 'default'" @click="togglePriceAxisType">
            <el-icon><DataLine /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 区间统计按钮 -->
        <el-tooltip content="区间统计" placement="top">
          <el-button size="small" :type="isRangeSelectMode ? 'primary' : 'default'" @click="toggleRangeSelect">
            <el-icon><DataLine /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 重置视图按钮 -->
        <el-tooltip content="重置视图" placement="top">
          <el-button size="small" @click="resetViewState">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 画线工具按钮 -->
        <el-tooltip content="画线工具" placement="top">
          <el-button size="small" :type="showDrawingToolbar ? 'primary' : 'default'" @click="toggleDrawingToolbar">
            <el-icon><Edit /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- K线形态标记按钮 -->
        <el-dropdown trigger="click" size="small">
          <el-button size="small">
            形态 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-checkbox-group v-model="markOptions">
                <el-dropdown-item>
                  <el-checkbox label="gap">跳空缺口</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="shadow">长影线</el-checkbox>
                </el-dropdown-item>
              </el-checkbox-group>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <!-- 涨跌停阈值切换（仅股票市场显示） -->
        <el-dropdown v-if="hasLimitUpDown" trigger="click" size="small">
          <el-button size="small">
            涨跌停 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="(config, key) in marketConfigs"
                :key="key"
                v-if="config.hasLimitUpDown"
                @click="handleLimitThresholdChange(key)"
              >
                <span :class="{ 'is-active': limitThresholdType === key }">
                  {{ config.name }} {{ config.limitUpThreshold }}%
                </span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <!-- 复权设置按钮（仅股票市场显示） -->
        <el-tooltip v-if="marketConfig.needAdjustment" :content="adjustmentType === 'none' ? '不复权' : adjustmentType === 'forward' ? '前复权' : '后复权'" placement="top">
          <el-button size="small" :type="adjustmentType !== 'none' ? 'primary' : 'default'" @click="toggleAdjustmentPanel">
            <el-icon><Operation /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 快速定位日期 -->
        <el-tooltip content="定位日期" placement="top">
          <el-date-picker
            v-model="jumpToDate"
            type="date"
            placeholder="定位日期"
            size="small"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :clearable="false"
            @change="handleJumpToDate"
            style="width: 120px"
          />
        </el-tooltip>
        <!-- 均线显示控制 -->
        <el-dropdown trigger="click" size="small">
          <el-button size="small">
            均线 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-checkbox-group v-model="visibleMA" @change="handleMAChange">
                <el-dropdown-item>
                  <el-checkbox label="5">MA5</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="10">MA10</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="20">MA20</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="60">MA60</el-checkbox>
                </el-dropdown-item>
              </el-checkbox-group>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 图表容器 -->
    <div ref="chartRef" class="chart-area" @mousedown="handleChartMouseDown" @mousemove="handleChartMouseMove" @mouseup="handleChartMouseUp"></div>

    <!-- 画线工具栏 -->
    <div v-if="showDrawingToolbar" class="drawing-toolbar-wrapper">
      <DrawingToolbar
        :tool="drawingState.currentTool.value"
        :color="drawingState.currentColor.value"
        :lineWidth="drawingState.currentLineWidth.value"
        :magnet="drawingState.magnetEnabled.value"
        @toolChange="drawingState.setTool"
        @colorChange="drawingState.setColor"
        @lineWidthChange="drawingState.setLineWidth"
        @magnetChange="drawingState.setMagnet"
        @toolConfigChange="handleToolConfigChange"
      />
    </div>

    <!-- 复权参数面板（仅股票市场） -->
    <AdjustmentPanel
      v-if="showAdjustmentPanel && marketConfig.needAdjustment"
      v-model="adjustmentType"
      :hasAdjustment="marketConfig.needAdjustment"
      @close="showAdjustmentPanel = false"
    />

    <!-- 区间统计面板 -->
    <RangeStats
      :rangeData="rangeStatsData"
      @close="clearRangeSelection"
    />

    <!-- 光标锁定数据面板 -->
    <div v-if="isCursorLocked && lockedData" class="cursor-lock-panel">
      <div class="lock-header">
        <span class="lock-title">光标锁定</span>
        <div class="lock-actions">
          <el-tooltip content="复制数据" placement="top">
            <el-button size="small" text @click="copyLockedData">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </el-tooltip>
          <el-button size="small" text @click="unlockCursor">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="lock-data">
        <div class="lock-row">
          <span class="lock-label">日期</span>
          <span class="lock-value">{{ lockedData.date }}</span>
        </div>
        <div class="lock-row">
          <span class="lock-label">开盘</span>
          <span class="lock-value">{{ formatPrice(lockedData.open) }}</span>
        </div>
        <div class="lock-row">
          <span class="lock-label">最高</span>
          <span class="lock-value high">{{ formatPrice(lockedData.high) }}</span>
        </div>
        <div class="lock-row">
          <span class="lock-label">最低</span>
          <span class="lock-value low">{{ formatPrice(lockedData.low) }}</span>
        </div>
        <div class="lock-row">
          <span class="lock-label">收盘</span>
          <span class="lock-value">{{ formatPrice(lockedData.close) }}</span>
        </div>
      </div>
      <div class="lock-hint">← → 微调 | Space 解锁 | Ctrl+C 复制</div>
    </div>

    <!-- 无数据提示 -->
    <el-empty v-if="!data || !data.length" description="暂无数据" class="empty-placeholder">
      <el-button type="primary" size="small" @click="$emit('fetchData')">
        获取数据
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
/**
 * K线主图组件.
 *
 * 实现专业K线蜡烛图渲染，支持均线叠加、图表类型切换.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 * Updated: 2026-04-14 - F002: 平滑切换动画、数据范围保持、记住用户选择
 */
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ArrowDown, Rank, DataLine, Close, CopyDocument, RefreshRight, Edit, Operation } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  getKLineBaseOption,
  getKLineSeriesOption,
  getMASeriesOption,
  formatKLineData,
  chartThemes,
  detectGaps,
  detectLongShadows,
  generateGapMarkPoints,
  generateGapMarkLines,
  MarketType,
  getMarketConfig
} from '@/utils/chartConfig'
import {
  identifyMarketTypeByName,
  marketConfigs,
  calculateLimitUpPrice,
  calculateLimitDownPrice,
  isLimitUp,
  isLimitDown,
  calculateLimitUpDownStats,
  AdjustmentType,
  calculateAdjustedPrices,
  AdjustmentFactor
} from '@/utils/stockUtils'
import RangeStats from './RangeStats.vue'
import DrawingToolbar from './DrawingToolbar.vue'
import AdjustmentPanel from './AdjustmentPanel.vue'
import { useDrawing } from '@/hooks/useDrawing'

// Props定义
interface Props {
  /** 原始K线数据 */
  data: Array<{
    date: string
    open: number | string
    close: number | string
    high: number | string
    low: number | string
    volume?: number | string
  }>
  /** 均线数据 */
  maData?: Record<string, Array<{ value: number }>>
  /** 标的名称 */
  symbolName?: string
  /** 标的代码 */
  symbolCode?: string
  /** 标的ID（用于视图记忆） */
  symbolId?: string
  /** 图表主题 */
  theme?: 'light' | 'dark'
  /** 市场类型（可选，默认自动识别） */
  marketType?: MarketType
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  maData: () => ({}),
  symbolName: '',
  symbolCode: '',
  symbolId: '',
  theme: 'light',
  marketType: undefined
})

// Emits定义
const emit = defineEmits<{
  (e: 'fetchData'): void
  (e: 'chartTypeChange', type: 'candle' | 'line'): void
  (e: 'maChange', periods: string[]): void
}>()

// 图表容器ref
const chartRef = ref<HTMLDivElement | null>(null)
// 图表实例
let chartInstance: echarts.ECharts | null = null

// 状态 - 从localStorage恢复用户偏好
const chartType = ref<'candle' | 'line'>(
  (localStorage.getItem('fdas_chart_type') as 'candle' | 'line') || 'candle'
)
const visibleMA = ref<string[]>(
  JSON.parse(localStorage.getItem('fdas_visible_ma') || '["5","10","20","60"]')
)
const showRightAxis = ref<boolean>(
  localStorage.getItem('fdas_right_axis') === 'true'
)
const showGapMarks = ref<boolean>(
  localStorage.getItem('fdas_gap_marks') !== 'false'
)
const showLongShadowMarks = ref<boolean>(
  localStorage.getItem('fdas_shadow_marks') !== 'false'
)

// K线形态标记选项
const markOptions = ref<string[]>([
  showGapMarks.value ? 'gap' : '',
  showLongShadowMarks.value ? 'shadow' : ''
].filter(Boolean))

// 快速定位日期
const jumpToDate = ref<string>('')

// 价格坐标模式
const priceAxisType = ref<'value' | 'log'>(
  localStorage.getItem('fdas_price_axis_type') === 'log' ? 'log' : 'value'
)

// 区间选择状态
const isRangeSelectMode = ref(false)
const rangeStatsData = ref<any>(null)
let selectedRange: { startIndex: number; endIndex: number } | null = null

// 画线工具状态
const showDrawingToolbar = ref(false)
const drawingState = useDrawing({
  chartInstance: () => chartInstance,
  data: () => props.data,
  initialColor: localStorage.getItem('fdas_drawing_color') || '#FF6B6B',
  initialLineWidth: parseInt(localStorage.getItem('fdas_drawing_width') || '2'),
  initialMagnet: localStorage.getItem('fdas_drawing_magnet') !== 'false'
})

// 复权面板状态
const showAdjustmentPanel = ref(false)
const adjustmentType = ref<AdjustmentType>(
  (localStorage.getItem('fdas_adjustment_type') as AdjustmentType) || AdjustmentType.NONE
)

// 处理复权类型变更
const handleAdjustmentChange = (type: AdjustmentType) => {
  adjustmentType.value = type
  renderChart(true)
}

// 切换复权面板显示
const toggleAdjustmentPanel = () => {
  showAdjustmentPanel.value = !showAdjustmentPanel.value
}

// 光标锁定状态
const isCursorLocked = ref(false)
const lockedDataIndex = ref<number | null>(null)
const lockedData = ref<any>(null)

// 当前DataZoom范围（用于切换时保持）
let currentZoomRange = { start: 60, end: 100 }

// 计算属性
const currentPrice = computed(() => {
  if (props.data && props.data.length > 0) {
    const latest = props.data[props.data.length - 1]
    return parseFloat(latest.close as string).toFixed(4)
  }
  return null
})

const changePercent = computed(() => {
  if (props.data && props.data.length >= 2) {
    const latest = props.data[props.data.length - 1]
    const prev = props.data[props.data.length - 2]
    const change = ((parseFloat(latest.close as string) - parseFloat(prev.close as string)) /
                    parseFloat(prev.close as string) * 100).toFixed(2)
    return change.startsWith('-') ? change : '+' + change
  }
  return null
})

const priceClass = computed(() => {
  if (!changePercent.value) return ''
  return parseFloat(changePercent.value) >= 0 ? 'up' : 'down'
})

// 市场类型识别（自动或手动指定）
const detectedMarketType = computed(() => {
  if (props.marketType) return props.marketType
  return identifyMarketTypeByName(props.symbolCode || '', props.symbolName)
})

// 市场配置
const marketConfig = computed(() => getMarketConfig(detectedMarketType.value))

// 是否有涨跌停功能
const hasLimitUpDown = computed(() => marketConfig.value.hasLimitUpDown)

// 涨停价计算（基于昨日收盘价）
const limitUpPrice = computed(() => {
  if (!hasLimitUpDown.value || !props.data || props.data.length < 2) return null
  const prevClose = parseFloat(props.data[props.data.length - 2].close as string)
  return calculateLimitUpPrice(prevClose, detectedMarketType.value)
})

// 跌停价计算（基于昨日收盘价）
const limitDownPrice = computed(() => {
  if (!hasLimitUpDown.value || !props.data || props.data.length < 2) return null
  const prevClose = parseFloat(props.data[props.data.length - 2].close as string)
  return calculateLimitDownPrice(prevClose, detectedMarketType.value)
})

// 当前是否涨停
const isCurrentLimitUp = computed(() => {
  if (!limitUpPrice.value || !props.data || props.data.length < 1) return false
  const currentClose = parseFloat(props.data[props.data.length - 1].close as string)
  return isLimitUp(currentClose, limitUpPrice.value, detectedMarketType.value)
})

// 当前是否跌停
const isCurrentLimitDown = computed(() => {
  if (!limitDownPrice.value || !props.data || props.data.length < 1) return false
  const currentClose = parseFloat(props.data[props.data.length - 1].close as string)
  return isLimitDown(currentClose, limitDownPrice.value, detectedMarketType.value)
})

// 涨跌停阈值类型（用于切换）
const limitThresholdType = ref<string>(
  localStorage.getItem('fdas_limit_threshold') || detectedMarketType.value
)

// 监听市场类型变化，更新阈值类型
watch(detectedMarketType, (newType) => {
  if (!localStorage.getItem('fdas_limit_threshold')) {
    limitThresholdType.value = newType
  }
})

// 切换涨跌停阈值类型
const handleLimitThresholdChange = (type: string) => {
  limitThresholdType.value = type
  localStorage.setItem('fdas_limit_threshold', type)
  renderChart(false)
}

/**
 * 初始化图表.
 */
const initChart = () => {
  if (!chartRef.value) return

  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新实例
  chartInstance = echarts.init(chartRef.value, undefined, {
    renderer: 'canvas'
  })

  // 监听DataZoom变化以保存范围（按品种存储）
  chartInstance.on('datazoom', (params: any) => {
    if (!props.symbolId) return

    if (params && params.batch) {
      // 滑块缩放
      const batch = params.batch[0]
      currentZoomRange.start = batch.start
      currentZoomRange.end = batch.end
    } else if (params && params.start !== undefined) {
      // 内置缩放
      currentZoomRange.start = params.start
      currentZoomRange.end = params.end
    }

    // 保存该品种的视图状态
    saveViewState()
  })

  // 监听brush选择事件
  chartInstance.on('brush', (params: any) => {
    if (params && params.brushType === 'rect' && params.areas && params.areas.length > 0) {
      const area = params.areas[0]
      if (area.coordRange && area.coordRange.length >= 2) {
        // 获取选中的索引范围
        const xRange = area.coordRange[0]
        if (xRange && xRange.length >= 2) {
          const startIndex = Math.floor(xRange[0])
          const endIndex = Math.floor(xRange[1])
          selectedRange = { startIndex, endIndex }
          rangeStatsData.value = calculateRangeStats(startIndex, endIndex)
        }
      }
    } else if (params && params.brushType === 'clear') {
      clearRangeSelection()
    }
  })

  // 监听鼠标移动，记录当前位置索引（用于光标锁定）
  chartInstance.on('mousemove', (params: any) => {
    if (params && params.dataIndex !== undefined && !isCursorLocked.value) {
      lockedDataIndex.value = params.dataIndex
    }
  })

  // 双击重置视图
  chartInstance.getZr().on('dblclick', () => {
    resetView()
  })
}

/**
 * 重置视图到默认状态.
 */
const resetView = () => {
  currentZoomRange = { start: 60, end: 100 }
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'dataZoom',
      start: 60,
      end: 100
    })
  }
}

/**
 * 处理键盘事件（ESC重置视图，Space锁定光标，方向键微调，Ctrl+C复制，Delete删除画线）.
 */
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    resetView()
    if (isCursorLocked.value) {
      unlockCursor()
    }
    // ESC取消画线选择和绘制
    if (drawingState.selectedDrawingId.value) {
      drawingState.deselectDrawing()
    } else if (drawingState.isDrawing.value) {
      drawingState.cancelDrawing()
    }
  }
  if (e.key === ' ' || e.code === 'Space') {
    e.preventDefault()
    toggleCursorLock()
  }
  // Ctrl+C 复制锁定数据
  if ((e.ctrlKey || e.metaKey) && e.key === 'c' && isCursorLocked.value) {
    e.preventDefault()
    copyLockedData()
  }
  // Delete 删除选中画线
  if (e.key === 'Delete' && drawingState.selectedDrawingId.value) {
    e.preventDefault()
    drawingState.deleteSelectedDrawing()
    ElMessage.success('画线已删除')
  }
  // 方向键微调光标位置
  if (isCursorLocked.value) {
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      moveCursor(-1)
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      moveCursor(1)
    }
  }
  // Ctrl+方向键快速跳转（不锁定光标时）
  if (!isCursorLocked.value && (e.ctrlKey || e.metaKey)) {
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      fastJump(-100)  // 向左跳转100根K线
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      fastJump(100)   // 向右跳转100根K线
    }
  }
}

/**
 * 格式化价格.
 */
const formatPrice = (value: number | string) => {
  if (!value) return '--'
  return parseFloat(value as string).toFixed(4)
}

/**
 * 切换光标锁定.
 */
const toggleCursorLock = () => {
  if (isCursorLocked.value) {
    unlockCursor()
  } else {
    // 锁定当前鼠标位置的数据（如果没有鼠标位置，锁定最后一条）
    lockCursorAt(lockedDataIndex.value ?? props.data.length - 1)
  }
}

/**
 * 锁定光标到指定索引.
 */
const lockCursorAt = (index: number) => {
  if (!props.data || index < 0 || index >= props.data.length) return

  isCursorLocked.value = true
  lockedDataIndex.value = index
  lockedData.value = props.data[index]

  // 高亮锁定的数据点
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'showTip',
      seriesIndex: 0,
      dataIndex: index
    })
  }
}

/**
 * 解锁光标.
 */
const unlockCursor = () => {
  isCursorLocked.value = false
  lockedDataIndex.value = null
  lockedData.value = null

  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'hideTip'
    })
  }
}

/**
 * 移动光标位置（键盘微调）.
 */
const moveCursor = (delta: number) => {
  if (!lockedDataIndex.value) return

  const newIndex = lockedDataIndex.value + delta
  if (newIndex >= 0 && newIndex < props.data.length) {
    lockCursorAt(newIndex)
  }
}

/**
 * 快速跳转（Ctrl+方向键）.
 */
const fastJump = (delta: number) => {
  if (!chartInstance) return

  // 计算当前DataZoom范围
  const currentStart = currentZoomRange.start
  const currentEnd = currentZoomRange.end
  const totalData = props.data.length

  // 计算每根K线对应的百分比
  const percentPerKline = 100 / totalData
  const jumpPercent = delta * percentPerKline

  // 计算新的DataZoom范围
  let newStart = currentStart - jumpPercent
  let newEnd = currentEnd - jumpPercent

  // 限制范围在0-100之间
  if (newStart < 0) {
    newStart = 0
    newEnd = Math.min(currentEnd - currentStart, 100)
  }
  if (newEnd > 100) {
    newEnd = 100
    newStart = Math.max(100 - (currentEnd - currentStart), 0)
  }

  // 应用新的DataZoom范围
  currentZoomRange.start = newStart
  currentZoomRange.end = newEnd

  chartInstance.dispatchAction({
    type: 'dataZoom',
    start: newStart,
    end: newEnd
  })
}

/**
 * 快速定位到指定日期.
 */
const handleJumpToDate = (dateStr: string) => {
  if (!dateStr || !chartInstance || !props.data.length) return

  // 找到该日期对应的索引
  const index = props.data.findIndex(d => d.date === dateStr)
  if (index === -1) {
    ElMessage.warning('未找到该日期的数据')
    return
  }

  // 计算该索引对应的百分比位置
  const totalData = props.data.length
  const indexPercent = (index / totalData) * 100

  // 计算DataZoom范围，以该日期为中心
  const zoomWidth = currentZoomRange.end - currentZoomRange.start
  let newStart = indexPercent - zoomWidth / 2
  let newEnd = indexPercent + zoomWidth / 2

  // 限制范围在0-100之间
  if (newStart < 0) {
    newStart = 0
    newEnd = zoomWidth
  }
  if (newEnd > 100) {
    newEnd = 100
    newStart = 100 - zoomWidth
  }

  // 应用新的DataZoom范围
  currentZoomRange.start = newStart
  currentZoomRange.end = newEnd

  chartInstance.dispatchAction({
    type: 'dataZoom',
    start: newStart,
    end: newEnd
  })

  // 高亮该日期的K线
  chartInstance.dispatchAction({
    type: 'showTip',
    seriesIndex: 0,
    dataIndex: index
  })

  ElMessage.success(`已定位到 ${dateStr}`)
}

/**
 * 处理滚轮事件（Alt+滚轮纵向缩放）.
 */
const handleWheel = (e: WheelEvent) => {
  // 仅在按住Alt键时处理
  if (!e.altKey) return

  e.preventDefault()

  if (!chartInstance || !props.data.length) return

  // 获取当前Y轴范围
  const option = chartInstance.getOption() as any
  const yAxis = option.yAxis[0]

  if (!yAxis || yAxis.type === 'log') {
    // 对数坐标暂不支持纵向缩放
    return
  }

  // 获取当前Y轴的最小和最大值
  const currentMin = yAxis.min || 0
  const currentMax = yAxis.max || 100

  // 计算缩放比例（滚轮向上放大，向下缩小）
  const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1  // 向下缩小范围（放大视图），向上增大范围（缩小视图）

  // 计算新的Y轴范围
  const center = (currentMin + currentMax) / 2
  const range = (currentMax - currentMin) * zoomFactor / 2
  const newMin = center - range
  const newMax = center + range

  // 应用新的Y轴范围
  chartInstance.setOption({
    yAxis: [{
      ...yAxis,
      min: newMin,
      max: newMax
    }]
  }, { notMerge: false })
}

/**
 * 复制锁定数据到剪贴板.
 */
const copyLockedData = async () => {
  if (!lockedData.value) return

  const text = `日期: ${lockedData.value.date}
开盘: ${formatPrice(lockedData.value.open)}
最高: ${formatPrice(lockedData.value.high)}
最低: ${formatPrice(lockedData.value.low)}
收盘: ${formatPrice(lockedData.value.close)}`

  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('数据已复制到剪贴板')
  } catch (err) {
    // 降级方案：使用传统复制方法
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success('数据已复制到剪贴板')
  }
}

/**
 * 保存视图状态到localStorage.
 */
const saveViewState = () => {
  if (!props.symbolId) return

  const key = `fdas_view_${props.symbolId}`
  const state = {
    zoomStart: currentZoomRange.start,
    zoomEnd: currentZoomRange.end,
    chartType: chartType.value,
    visibleMA: visibleMA.value,
    showRightAxis: showRightAxis.value
  }
  localStorage.setItem(key, JSON.stringify(state))
}

/**
 * 从localStorage恢复视图状态.
 */
const restoreViewState = () => {
  if (!props.symbolId) return

  const key = `fdas_view_${props.symbolId}`
  const saved = localStorage.getItem(key)
  if (saved) {
    try {
      const state = JSON.parse(saved)
      currentZoomRange.start = state.zoomStart || 60
      currentZoomRange.end = state.zoomEnd || 100
      chartType.value = state.chartType || 'candle'
      visibleMA.value = state.visibleMA || ['5', '10', '20', '60']
      showRightAxis.value = state.showRightAxis || false

      // 应用zoom范围
      if (chartInstance) {
        chartInstance.dispatchAction({
          type: 'dataZoom',
          start: currentZoomRange.start,
          end: currentZoomRange.end
        })
      }
    } catch (e) {
      // 解析失败，使用默认值
      currentZoomRange = { start: 60, end: 100 }
    }
  } else {
    // 无保存状态，使用默认值
    currentZoomRange = { start: 60, end: 100 }
  }
}

/**
 * 重置视图状态到默认.
 */
const resetViewState = () => {
  // 清除localStorage保存的状态
  if (props.symbolId) {
    const key = `fdas_view_${props.symbolId}`
    localStorage.removeItem(key)
  }

  // 恢复默认值
  currentZoomRange = { start: 60, end: 100 }
  chartType.value = 'candle'
  visibleMA.value = ['5', '10', '20', '60']
  showRightAxis.value = false

  // 应用到图表
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'dataZoom',
      start: 60,
      end: 100
    })
  }

  // 重新渲染
  renderChart(false)

  ElMessage.success('视图已重置')
}

/**
 * 渲染图表.
 */
const renderChart = (animate = false) => {
  if (!chartInstance || !props.data || !props.data.length) {
    if (chartInstance) {
      chartInstance.clear()
    }
    return
  }

  // 获取基础配置
  const baseOption = getKLineBaseOption(props.theme, priceAxisType.value)

  // 复权数据处理（仅股票市场且有复权需求时）
  let processedData = props.data
  if (marketConfig.value.needAdjustment && adjustmentType.value !== AdjustmentType.NONE) {
    // 使用前端复权计算（如果没有后端复权因子数据，使用默认因子1）
    // TODO: 从后端获取复权因子数据
    const adjustmentFactors: AdjustmentFactor[] = [] // 当前无复权因子数据
    processedData = calculateAdjustedPrices(
      props.data,
      adjustmentFactors,
      adjustmentType.value,
      marketConfig.value.pricePrecision
    )
  }

  const dates = processedData.map(d => d.date)

  // 设置X轴数据
  baseOption.xAxis[0].data = dates

  // 设置图例
  baseOption.legend.data = ['K线']

  // 设置动画 - 切换时启用平滑动画
  baseOption.animation = animate
  baseOption.animationDuration = animate ? 300 : 0
  baseOption.animationEasing = 'cubicOut'

  // 创建系列数组
  const series: any[] = []

  // K线或折线图
  if (chartType.value === 'candle') {
    const klineOption = getKLineSeriesOption(props.theme)
    klineOption.data = formatKLineData(processedData)

    // 构建markLine数据数组
    const markLineData: any[] = []
    const t = chartThemes[props.theme]

    // 添加昨收价基准线
    if (props.data.length >= 2) {
      const prevClose = parseFloat(props.data[props.data.length - 2].close as string)
      markLineData.push({
        yAxis: prevClose,
        name: '昨收价',
        lineStyle: {
          type: 'dashed',
          color: '#f59e0b',
          width: 1
        },
        label: {
          formatter: `昨收: ${prevClose.toFixed(marketConfig.value.pricePrecision)}`,
          color: '#f59e0b',
          fontSize: 11
        }
      })
    }

    // 添加涨跌停价格线（仅股票市场）
    if (hasLimitUpDown.value && props.data.length >= 2) {
      const prevClose = parseFloat(props.data[props.data.length - 2].close as string)
      // 使用当前选择的阈值类型计算涨跌停价格
      const currentThresholdType = limitThresholdType.value as MarketType
      const upPrice = calculateLimitUpPrice(prevClose, currentThresholdType)
      const downPrice = calculateLimitDownPrice(prevClose, currentThresholdType)

      // 涨停价线
      markLineData.push({
        yAxis: upPrice,
        name: '涨停价',
        lineStyle: {
          type: 'dashed',
          color: t.limitUpColor,
          width: 1
        },
        label: {
          formatter: `涨停: ${upPrice.toFixed(marketConfig.value.pricePrecision)}`,
          color: t.limitUpColor,
          fontSize: 11,
          backgroundColor: t.limitUpBgColor,
          padding: [2, 4]
        }
      })

      // 跌停价线
      markLineData.push({
        yAxis: downPrice,
        name: '跌停价',
        lineStyle: {
          type: 'dashed',
          color: t.limitDownColor,
          width: 1
        },
        label: {
          formatter: `跌停: ${downPrice.toFixed(marketConfig.value.pricePrecision)}`,
          color: t.limitDownColor,
          fontSize: 11,
          backgroundColor: t.limitDownBgColor,
          padding: [2, 4]
        }
      })
    }

    // 设置markLine
    if (markLineData.length > 0) {
      klineOption.markLine = {
        symbol: 'none',
        data: markLineData
      }
    }

    // 添加涨跌停K线特殊标记（仅股票市场）
    if (hasLimitUpDown.value && props.data.length >= 2) {
      const currentThresholdType = limitThresholdType.value as MarketType
      // 构建涨跌停标记的markPoint数据
      const limitMarkPoints: any[] = []

      // 遍历K线数据，检测涨跌停
      for (let i = 1; i < props.data.length; i++) {
        const prevClose = parseFloat(props.data[i - 1].close as string)
        const currClose = parseFloat(props.data[i].close as string)
        const currHigh = parseFloat(props.data[i].high as string)
        const currLow = parseFloat(props.data[i].low as string)

        const upPrice = calculateLimitUpPrice(prevClose, currentThresholdType)
        const downPrice = calculateLimitDownPrice(prevClose, currentThresholdType)

        // 涨停检测
        if (isLimitUp(currClose, upPrice, currentThresholdType)) {
          limitMarkPoints.push({
            coord: [i, currHigh],
            symbol: 'pin',
            symbolSize: 30,
            itemStyle: {
              color: t.limitUpColor
            },
            label: {
              show: true,
              formatter: '涨停',
              color: '#ffffff',
              fontSize: 10,
              fontWeight: 'bold'
            }
          })
        }

        // 跌停检测
        if (isLimitDown(currClose, downPrice, currentThresholdType)) {
          limitMarkPoints.push({
            coord: [i, currLow],
            symbol: 'pin',
            symbolSize: 30,
            symbolRotate: 180,
            itemStyle: {
              color: t.limitDownColor
            },
            label: {
              show: true,
              formatter: '跌停',
              color: '#ffffff',
              fontSize: 10,
              fontWeight: 'bold'
            }
          })
        }
      }

      // 合并到markPoint
      if (limitMarkPoints.length > 0) {
        if (klineOption.markPoint) {
          klineOption.markPoint.data = [...klineOption.markPoint.data, ...limitMarkPoints]
        } else {
          klineOption.markPoint = {
            data: limitMarkPoints,
            animation: false
          }
        }
      }
    }

    // 添加缺口标记
    if (showGapMarks.value && props.data.length >= 2) {
      const gaps = detectGaps(props.data)
      const gapMarkPoints = generateGapMarkPoints(gaps, props.theme)
      if (gapMarkPoints) {
        klineOption.markPoint = gapMarkPoints
      }
    }

    // 添加长影线标记
    if (showLongShadowMarks.value && props.data.length >= 1) {
      const longShadows = detectLongShadows(props.data)
      if (longShadows.length > 0) {
        // 为长影线K线添加特殊样式
        const styledData = formatKLineData(props.data).map((item, index) => {
          const shadow = longShadows.find(s => s.index === index)
          if (shadow) {
            return {
              value: item,
              itemStyle: {
                borderColor: shadow.type === 'longUpperShadow' ? '#f59e0b' : '#8b5cf6',
                borderWidth: 2
              }
            }
          }
          return item
        })
        klineOption.data = styledData
      }
    }

    series.push(klineOption)
  } else {
    // 折线图
    const lineSeries = {
      name: '收盘价',
      type: 'line',
      xAxisIndex: 0,
      yAxisIndex: 0,
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2,
        color: '#2d5af7'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(45, 90, 247, 0.3)' },
          { offset: 1, color: 'rgba(45, 90, 247, 0.05)' }
        ])
      },
      data: props.data.map(d => parseFloat(d.close as string) || 0),
      // 添加昨收价基准线
      markLine: props.data.length >= 2 ? {
        symbol: 'none',
        lineStyle: {
          type: 'dashed',
          color: '#f59e0b',
          width: 1
        },
        label: {
          show: true,
          position: 'end',
          formatter: (params) => `昨收: ${params.value.toFixed(4)}`,
          color: '#f59e0b',
          fontSize: 11
        },
        data: [
          {
            yAxis: parseFloat(props.data[props.data.length - 2].close as string),
            name: '昨收价'
          }
        ]
      } : undefined
    }
    series.push(lineSeries)
    baseOption.legend.data.push('收盘价')
  }

  // 添加均线
  visibleMA.value.forEach(period => {
    const periodNum = parseInt(period)
    if (props.maData && props.maData[`ma${period}`]) {
      const maOption = getMASeriesOption(periodNum, props.theme)
      maOption.data = props.maData[`ma${period}`].map(m => m.value)
      series.push(maOption)
      baseOption.legend.data.push(`MA${period}`)
    }
  })

  // 保持DataZoom范围
  if (baseOption.dataZoom && baseOption.dataZoom.length > 0) {
    baseOption.dataZoom[0].start = currentZoomRange.start
    baseOption.dataZoom[0].end = currentZoomRange.end
    if (baseOption.dataZoom.length > 1) {
      baseOption.dataZoom[1].start = currentZoomRange.start
      baseOption.dataZoom[1].end = currentZoomRange.end
    }
  }

  // 控制右侧价格轴显示
  if (baseOption.yAxis && baseOption.yAxis.length > 1) {
    baseOption.yAxis[1].axisLabel.show = showRightAxis.value
    baseOption.yAxis[1].axisLine.show = showRightAxis.value
  }

  // 设置配置 - 使用notMerge确保切换时完全替换
  baseOption.series = series
  chartInstance.setOption(baseOption, true)
}

/**
 * 处理图表类型切换.
 * 实现平滑切换动画和数据范围保持.
 */
const handleChartTypeChange = (type: 'candle' | 'line') => {
  // 保存用户偏好到localStorage
  localStorage.setItem('fdas_chart_type', type)

  // 触发事件
  emit('chartTypeChange', type)

  // 使用动画重新渲染图表
  renderChart(true)
}

/**
 * 处理均线显示变化.
 */
const handleMAChange = (periods: string[]) => {
  // 保存到localStorage
  localStorage.setItem('fdas_visible_ma', JSON.stringify(periods))
  emit('maChange', periods)
  renderChart(false)
}

/**
 * 切换右侧价格轴显示.
 */
const toggleRightAxis = () => {
  showRightAxis.value = !showRightAxis.value
  localStorage.setItem('fdas_right_axis', showRightAxis.value.toString())
  renderChart(false)
}

/**
 * 切换价格坐标模式.
 */
const togglePriceAxisType = () => {
  priceAxisType.value = priceAxisType.value === 'value' ? 'log' : 'value'
  localStorage.setItem('fdas_price_axis_type', priceAxisType.value)
  renderChart(false)
}

/**
 * 切换画线工具栏显示.
 */
const toggleDrawingToolbar = () => {
  showDrawingToolbar.value = !showDrawingToolbar.value
  if (!showDrawingToolbar.value) {
    // 关闭工具栏时取消当前工具选择
    drawingState.setTool(null)
    drawingState.cancelDrawing()
  }
}

/**
 * 处理工具配置变更.
 */
const handleToolConfigChange = (config: { tool: string; params: Record<string, any> }) => {
  // 将配置参数传递给画线系统
  drawingState.setToolParams(config.params)
}

/**
 * 处理图表鼠标按下事件（画线开始）.
 */
const handleChartMouseDown = (e: MouseEvent) => {
  if (!drawingState.currentTool.value || !chartInstance) return

  // 获取鼠标位置对应的图表坐标
  const pointInGrid = getMousePositionInGrid(e)
  if (pointInGrid) {
    drawingState.startDrawing(pointInGrid)
  }
}

/**
 * 处理图表鼠标移动事件（画线过程）.
 */
const handleChartMouseMove = (e: MouseEvent) => {
  if (!drawingState.isDrawing.value || !drawingState.currentTool.value || !chartInstance) return

  // 更新光标位置（用于磁吸显示）
  if (!drawingState.isCursorLocked.value) {
    const pointInGrid = getMousePositionInGrid(e)
    if (pointInGrid) {
      lockedDataIndex.value = Math.floor(pointInGrid.x)
    }
  }

  const pointInGrid = getMousePositionInGrid(e)
  if (pointInGrid) {
    drawingState.onDrawing(pointInGrid)
  }
}

/**
 * 处理图表鼠标抬起事件（画线结束）.
 */
const handleChartMouseUp = (e: MouseEvent) => {
  if (!drawingState.isDrawing.value) return

  const pointInGrid = getMousePositionInGrid(e)
  drawingState.endDrawing(pointInGrid)
}

/**
 * 获取鼠标在图表网格中的位置.
 */
const getMousePositionInGrid = (e: MouseEvent): { x: number; y: number } | null => {
  if (!chartInstance || !chartRef.value) return null

  const rect = chartRef.value.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top

  // 使用ECharts的convertFromPixel方法转换坐标
  const pointInGrid = chartInstance.convertFromPixel('grid', [mouseX, mouseY])
  return { x: pointInGrid[0], y: pointInGrid[1] }
}

/**
 * 切换区间选择模式.
 */
const toggleRangeSelect = () => {
  isRangeSelectMode.value = !isRangeSelectMode.value
  if (!isRangeSelectMode.value) {
    clearRangeSelection()
  }
}

/**
 * 清除区间选择.
 */
const clearRangeSelection = () => {
  selectedRange = null
  rangeStatsData.value = null
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'brush',
      areas: []
    })
  }
}

/**
 * 计算区间统计数据.
 */
const calculateRangeStats = (startIndex: number, endIndex: number) => {
  if (!props.data || startIndex < 0 || endIndex >= props.data.length) return null

  const rangeData = props.data.slice(startIndex, endIndex + 1)
  if (!rangeData.length) return null

  const startItem = rangeData[0]
  const endItem = rangeData[rangeData.length - 1]

  const startPrice = parseFloat(startItem.close as string)
  const endPrice = parseFloat(endItem.close as string)
  const changeAmount = endPrice - startPrice
  const changePercent = (changeAmount / startPrice * 100).toFixed(2)

  const highs = rangeData.map(d => parseFloat(d.high as string) || 0)
  const lows = rangeData.map(d => parseFloat(d.low as string) || 0)
  const highPrice = Math.max(...highs)
  const lowPrice = Math.min(...lows)
  const amplitude = ((highPrice - lowPrice) / startPrice * 100).toFixed(2)

  const closes = rangeData.map(d => parseFloat(d.close as string) || 0)
  const avgPrice = (closes.reduce((a, b) => a + b, 0) / closes.length).toFixed(4)

  // 基础统计数据
  const stats = {
    startDate: startItem.date,
    endDate: endItem.date,
    days: rangeData.length,
    startPrice: startPrice.toFixed(marketConfig.value.pricePrecision),
    endPrice: endPrice.toFixed(marketConfig.value.pricePrecision),
    changeAmount: changeAmount.toFixed(marketConfig.value.pricePrecision),
    changePercent: changePercent.startsWith('-') ? changePercent + '%' : '+' + changePercent + '%',
    highPrice: highPrice.toFixed(marketConfig.value.pricePrecision),
    lowPrice: lowPrice.toFixed(marketConfig.value.pricePrecision),
    amplitude: amplitude + '%',
    avgPrice: avgPrice
  }

  // 涨跌停统计（仅股票市场）
  if (hasLimitUpDown.value) {
    const limitStats = calculateLimitUpDownStats(rangeData, limitThresholdType.value as MarketType)
    return {
      ...stats,
      ...limitStats
    }
  }

  return stats
}

/**
 * Resize图表.
 */
const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

/**
 * 获取当前DataZoom范围.
 */
const getZoomRange = () => {
  return currentZoomRange
}

/**
 * 设置DataZoom范围.
 */
const setZoomRange = (start: number, end: number) => {
  currentZoomRange.start = start
  currentZoomRange.end = end
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'dataZoom',
      start: start,
      end: end
    })
  }
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    renderChart(false)
    // 数据变化后恢复该品种的视图状态
    restoreViewState()
  })
}, { deep: true })

// 监听品种ID变化，恢复对应品种的视图状态
watch(() => props.symbolId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    // 保存旧品种的视图状态
    if (oldId) {
      saveViewState()
    }
    // 恢复新品种的视图状态
    restoreViewState()
  }
})

// 监听均线数据变化
watch(() => props.maData, () => {
  nextTick(() => {
    renderChart(false)
  })
}, { deep: true })

// 监听markOptions变化，更新形态标记显示
watch(markOptions, (options) => {
  showGapMarks.value = options.includes('gap')
  showLongShadowMarks.value = options.includes('shadow')
  // 保存到localStorage
  localStorage.setItem('fdas_gap_marks', showGapMarks.value.toString())
  localStorage.setItem('fdas_shadow_marks', showLongShadowMarks.value.toString())
  // 重新渲染图表
  renderChart(false)
}, { deep: true })

// 监听主题变化
watch(() => props.theme, () => {
  // 重新渲染图表以应用新主题
  renderChart(false)
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initChart()
    renderChart(false)
    window.addEventListener('resize', resizeChart)
    window.addEventListener('keydown', handleKeydown)
    // Alt+滚轮纵向缩放
    if (chartRef.value) {
      chartRef.value.addEventListener('wheel', handleWheel, { passive: false })
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  window.removeEventListener('keydown', handleKeydown)
  if (chartRef.value) {
    chartRef.value.removeEventListener('wheel', handleWheel)
  }
  window.removeEventListener('keydown', handleKeydown)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 暴露方法供父组件调用
defineExpose({
  resizeChart,
  renderChart,
  getChartInstance: () => chartInstance,
  getZoomRange,
  setZoomRange,
  resetView
})
</script>

<style scoped>
.kline-chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 工具栏 */
.chart-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--fdas-bg-card);
  border-bottom: 1px solid var(--fdas-border-light);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.current-price {
  font-size: 16px;
  font-weight: 700;
}

.current-price.up {
  color: #ef4444;
}

.current-price.down {
  color: #22c55e;
}

.change-percent {
  font-size: 13px;
  font-weight: 500;
}

.change-percent.up {
  color: #ef4444;
}

.change-percent.down {
  color: #22c55e;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 图表区域 */
.chart-area {
  flex: 1;
  min-height: 300px;
}

/* 无数据提示 */
.empty-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

/* 光标锁定面板 */
.cursor-lock-panel {
  position: absolute;
  top: 60px;
  right: 12px;
  background: var(--fdas-bg-card);
  border: 1px solid var(--fdas-border-light);
  border-radius: 8px;
  padding: 12px;
  min-width: 150px;
  box-shadow: var(--fdas-shadow-card);
  z-index: 20;
}

.lock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.lock-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--fdas-primary);
}

.lock-actions {
  display: flex;
  gap: 4px;
}

.lock-data {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lock-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.lock-label {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.lock-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.lock-value.high {
  color: #ef4444;
}

.lock-value.low {
  color: #22c55e;
}

.lock-hint {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--fdas-border-light);
  font-size: 11px;
  color: var(--fdas-text-muted);
  text-align: center;
}

/* 画线工具栏 */
.drawing-toolbar-wrapper {
  position: absolute;
  top: 60px;
  left: 12px;
  z-index: 20;
}
</style>