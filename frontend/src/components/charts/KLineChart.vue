<template>
  <div class="kline-chart-container">
    <!-- 图表头部工具栏 -->
    <div class="chart-toolbar">
      <div class="toolbar-left">
        <span class="chart-title">行情走势</span>
        <span v-if="symbolName" class="symbol-name-tag">{{ symbolName }}</span>
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
        <!-- 重置视图按钮 -->
        <el-tooltip content="重置视图" placement="top">
          <el-button size="small" @click="resetViewState">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 缩放成交量副图按钮 -->
        <el-tooltip :content="props.volumeMaximized ? '恢复成交量' : '放大成交量'" placement="top">
          <el-button size="small" :type="props.volumeMaximized ? 'primary' : 'default'" @click="$emit('toggleVolume')">
            <el-icon><FullScreen /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 缩放MACD副图按钮 -->
        <el-tooltip :content="props.macdMaximized ? '恢复MACD' : '放大MACD'" placement="top">
          <el-button size="small" :type="props.macdMaximized ? 'primary' : 'default'" @click="$emit('toggleMacd')">
            <el-icon><FullScreen /></el-icon>
          </el-button>
        </el-tooltip>
        <!-- 画线工具按钮 -->
        <el-tooltip content="画线工具" placement="top">
          <el-button size="small" :type="showDrawingToolbar ? 'primary' : 'default'" @click="toggleDrawingToolbar">
            <el-icon><Edit /></el-icon>
          </el-button>
        </el-tooltip>
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
                  <el-checkbox label="30">MA30</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="60">MA60</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="120">MA120</el-checkbox>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-checkbox label="240">MA240</el-checkbox>
                </el-dropdown-item>
              </el-checkbox-group>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 图表容器 -->
    <div
      ref="chartRef"
      class="chart-area"
      :class="{ 'drawing-cursor': showDrawingToolbar && drawingState.currentTool.value }"
    ></div>

    <!-- 画线工具栏 -->
    <div v-if="showDrawingToolbar" class="drawing-toolbar-wrapper">
      <DrawingToolbar
        :tool="drawingState.currentTool.value"
        :color="drawingState.currentColor.value"
        :lineWidth="drawingState.currentLineWidth.value"
        @toolChange="drawingState.setTool"
        @colorChange="drawingState.setColor"
        @lineWidthChange="drawingState.setLineWidth"
        @clearAll="handleClearAllDrawings"
        @close="handleCloseDrawingToolbar"
      />
    </div>

    <!-- 复权参数面板（仅股票市场） -->
    <AdjustmentPanel
      v-if="showAdjustmentPanel && marketConfig.needAdjustment"
      v-model="adjustmentType"
      :hasAdjustment="marketConfig.needAdjustment"
      @close="showAdjustmentPanel = false"
    />

    <!-- 框选区间统计面板 -->
    <RangeStats
      v-if="showRangeStats"
      :rangeData="rangeStatsData"
      @close="closeRangeStats"
    />

    <!-- 无数据提示 -->
    <el-empty v-if="!data || !data.length" description="暂无数据" :image-size="60" class="empty-placeholder">
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
import { ArrowDown, Close, CopyDocument, RefreshRight, Edit, Operation, FullScreen } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  getKLineBaseOption,
  getKLineSeriesOption,
  getMASeriesOption,
  formatKLineData,
  chartThemes,
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
import DrawingToolbar from './DrawingToolbar.vue'
import AdjustmentPanel from './AdjustmentPanel.vue'
import RangeStats from './RangeStats.vue'
import { useDrawing } from '@/hooks/useDrawing'
import logger from '@/services/logger'

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
  /** 成交量副图是否最大化 */
  volumeMaximized?: boolean
  /** MACD副图是否最大化 */
  macdMaximized?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  maData: () => ({}),
  symbolName: '',
  symbolCode: '',
  symbolId: '',
  theme: 'light',
  marketType: undefined,
  volumeMaximized: false,
  macdMaximized: false
})

// Emits定义
const emit = defineEmits<{
  (e: 'fetchData'): void
  (e: 'chartTypeChange', type: 'candle' | 'line'): void
  (e: 'maChange', periods: string[]): void
  (e: 'toggleVolume'): void
  (e: 'toggleMacd'): void
  (e: 'adjustmentChange', type: AdjustmentType): void
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

// 快速定位日期
const jumpToDate = ref<string>('')

// 价格坐标模式 - 固定使用对数坐标
const priceAxisType = 'value'

// 画线工具状态
const showDrawingToolbar = ref(false)
const drawingState = useDrawing({
  chartInstance: () => chartInstance,
  data: () => props.data,
  initialColor: localStorage.getItem('fdas_drawing_color') || '#FF6B6B',
  initialLineWidth: parseInt(localStorage.getItem('fdas_drawing_width') || '4'),
  initialMagnet: localStorage.getItem('fdas_drawing_magnet') !== 'false'
})

// 组件内部的画线管理状态（独立于hook，用于渲染）
const drawingList = ref<any[]>([])  // 所有已完成的画线
const activeDrawingData = ref<any | null>(null)  // 正在绘制的临时画线
const drawingFirstPoint = ref<{ x: number; y: number } | null>(null)  // 点击-点击模式的第一个点
const drawingSecondPoint = ref<{ x: number; y: number } | null>(null)  // 平行通道三步模式的第二个点
const drawingStep = ref<number>(1)  // 当前点击步骤（1/2/3，用于平行通道）
const drawingWaitingSecond = ref(false)  // 是否等待第二次点击

// 复权面板状态
const showAdjustmentPanel = ref(false)
const adjustmentType = ref<AdjustmentType>(
  (localStorage.getItem('fdas_adjustment_type') as AdjustmentType) || AdjustmentType.NONE
)

// 处理复权类型变更
const handleAdjustmentChange = (type: AdjustmentType) => {
  adjustmentType.value = type
  // 存储用户偏好
  localStorage.setItem('fdas_adjustment_type', type)
  // 通知父组件获取复权数据
  emit('adjustmentChange', type)
}

// 切换复权面板显示
const toggleAdjustmentPanel = () => {
  showAdjustmentPanel.value = !showAdjustmentPanel.value
}

// 光标锁定状态
const isCursorLocked = ref(false)
const lockedDataIndex = ref<number | null>(null)
const lockedData = ref<any>(null)

// 框选统计状态
const showRangeStats = ref(false)
const rangeStatsData = ref<any>(null)
// 拖拽框选状态（记录矩形对角线两个点）
const isDragSelecting = ref(false)
const dragStartIndex = ref<number | null>(null)
const dragStartPrice = ref<number | null>(null)  // 起始点价格
const dragEndIndex = ref<number | null>(null)
const dragEndPrice = ref<number | null>(null)    // 结束点价格
// 记录mousedown时的屏幕坐标，用于区分单击和拖拽
const mouseDownScreenX = ref<number | null>(null)
const mouseDownScreenY = ref<number | null>(null)
// 标记是否真正开始了拖拽（移动距离超过阈值）
const hasStartedDrag = ref(false)
// 拖拽判定阈值（像素）
const DRAG_THRESHOLD = 5

// 当前DataZoom范围（用于切换时保持）
// 默认显示最近30个周期，不足则显示全部
let currentZoomRange = { start: 0, end: 100 }

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

  // 通过zrender监听鼠标事件（用于框选功能和边缘自动滚动）
  const zr = chartInstance.getZr()

  // mousedown事件
  zr.on('mousedown', (e: any) => {
    handleChartMouseDown(e)
  })

  // mousemove事件（包含边缘自动滚动检测）
  zr.on('mousemove', (e: any) => {
    handleChartMouseMove(e)
    handleEdgeAutoScroll(e)
  })

  // mouseup事件
  zr.on('mouseup', (e: any) => {
    handleChartMouseUp(e)
    stopEdgeAutoScroll()
  })

  // mouseout事件（离开图表时停止自动滚动）
  zr.on('mouseout', () => {
    stopEdgeAutoScroll()
  })
}

/**
 * 重置视图到默认状态 - 显示最近60周期.
 */
const resetView = () => {
  // 计算默认显示60周期的范围
  const totalData = props.data.length
  if (totalData <= 60) {
    // 数据不足60周期，显示全部
    currentZoomRange = { start: 0, end: 100 }
  } else {
    // 显示最近60周期
    const percentPerBar = 100 / totalData
    const startPercent = (totalData - 60) * percentPerBar
    currentZoomRange = { start: startPercent, end: 100 }
  }
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'dataZoom',
      start: currentZoomRange.start,
      end: currentZoomRange.end
    })
  }
}

/**
 * 处理键盘事件（ESC重置视图，Space锁定光标，方向键移动十字线，Ctrl+C复制，Delete删除画线）.
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
  // 方向键：移动十字线/光标位置（始终以十字线为中心）
  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    moveCursorByKline(-1)  // 向左移动一根K线
  } else if (e.key === 'ArrowRight') {
    e.preventDefault()
    moveCursorByKline(1)   // 向右移动一根K线
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    zoomAtCursor(-5)  // 以十字线为中心放大
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    zoomAtCursor(5)   // 以十字线为中心缩小
  }
  // Ctrl+方向键快速跳转视图
  if ((e.ctrlKey || e.metaKey) && !isCursorLocked.value) {
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
 * 按K线单位移动十字线（用于键盘导航）.
 * 十字线始终跟随键盘移动，到达可见区域边缘时自动移动视图.
 */
const moveCursorByKline = (delta: number) => {
  if (!props.data || !props.data.length || !chartInstance) return

  // 如果未锁定，则自动锁定到当前可见区域中心
  if (!isCursorLocked.value) {
    const visibleCenterIndex = getVisibleCenterIndex()
    lockCursorAt(visibleCenterIndex)
  }

  // 获取当前锁定的索引
  const currentIndex = lockedDataIndex.value ?? props.data.length - 1
  const newIndex = currentIndex + delta

  // 检查是否到达数据边界
  if (newIndex < 0) {
    return
  }
  if (newIndex >= props.data.length) {
    return
  }

  // 锁定到新位置
  lockCursorAt(newIndex)

  // 检查新位置是否在可见范围内，如果不在则移动视图
  const visibleRange = getVisibleRange()
  const viewWidth = visibleRange.end - visibleRange.start

  // 如果新索引在可见范围外，移动视图使其可见
  if (newIndex < visibleRange.start) {
    // 向左移动视图，新索引位于可见区域左侧10%位置
    const percentPerKline = 100 / props.data.length
    const newViewStart = newIndex * percentPerKline
    const newViewEnd = newViewStart + viewWidth
    shiftViewTo(newViewStart, newViewEnd)
  } else if (newIndex >= visibleRange.end) {
    // 向右移动视图，新索引位于可见区域右侧90%位置
    const percentPerKline = 100 / props.data.length
    const newViewEnd = (newIndex + 1) * percentPerKline
    const newViewStart = newViewEnd - viewWidth
    shiftViewTo(newViewStart, newViewEnd)
  }
}

/**
 * 以十字线为中心进行缩放.
 */
const zoomAtCursor = (delta: number) => {
  if (!chartInstance || !props.data.length) return

  // 如果未锁定，先锁定到可见区域中心
  if (!isCursorLocked.value) {
    const visibleCenterIndex = getVisibleCenterIndex()
    lockCursorAt(visibleCenterIndex)
  }

  const lockedIndex = lockedDataIndex.value ?? 0
  const percentPerKline = 100 / props.data.length
  const lockedPercent = lockedIndex * percentPerKline

  // 当前视图宽度
  const currentWidth = currentZoomRange.end - currentZoomRange.start
  let newWidth = currentWidth + delta

  // 限制宽度在5-100之间
  if (newWidth < 5) newWidth = 5
  if (newWidth > 100) newWidth = 100

  // 以锁定位置为中心计算新的起始和结束位置
  const lockedRatio = (lockedPercent - currentZoomRange.start) / currentWidth
  let newStart = lockedPercent - lockedRatio * newWidth
  let newEnd = lockedPercent + (1 - lockedRatio) * newWidth

  // 限制范围在0-100之间
  if (newStart < 0) {
    newStart = 0
    newEnd = newWidth
  }
  if (newEnd > 100) {
    newEnd = 100
    newStart = 100 - newWidth
  }

  currentZoomRange.start = newStart
  currentZoomRange.end = newEnd

  chartInstance.dispatchAction({
    type: 'dataZoom',
    start: newStart,
    end: newEnd
  })
}

/**
 * 获取当前可见区域的K线索引范围.
 */
const getVisibleRange = () => {
  const totalData = props.data.length
  const startIndex = Math.floor((currentZoomRange.start / 100) * totalData)
  const endIndex = Math.ceil((currentZoomRange.end / 100) * totalData)
  return { start: startIndex, end: endIndex }
}

/**
 * 获取当前可见区域中心的K线索引.
 */
const getVisibleCenterIndex = () => {
  const totalData = props.data.length
  const centerPercent = (currentZoomRange.start + currentZoomRange.end) / 2
  return Math.floor((centerPercent / 100) * totalData)
}

/**
 * 移动视图到指定百分比位置.
 */
const shiftViewTo = (start: number, end: number) => {
  // 限制范围在0-100之间
  if (start < 0) start = 0
  if (end > 100) end = 100
  if (end - start < 5) {
    // 最小宽度5%
    end = start + 5
    if (end > 100) {
      end = 100
      start = 95
    }
  }

  currentZoomRange.start = start
  currentZoomRange.end = end

  chartInstance.dispatchAction({
    type: 'dataZoom',
    start: start,
    end: end
  })
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
 * 左右移动视图（方向键）.
 */
const shiftView = (delta: number) => {
  if (!chartInstance) return

  const currentWidth = currentZoomRange.end - currentZoomRange.start
  let newStart = currentZoomRange.start + delta
  let newEnd = currentZoomRange.end + delta

  // 限制范围在0-100之间
  if (newStart < 0) {
    newStart = 0
    newEnd = currentWidth
  }
  if (newEnd > 100) {
    newEnd = 100
    newStart = 100 - currentWidth
  }

  currentZoomRange.start = newStart
  currentZoomRange.end = newEnd

  chartInstance.dispatchAction({
    type: 'dataZoom',
    start: newStart,
    end: newEnd
  })
}

/**
 * 缩放视图（上下键）.
 */
const zoomView = (delta: number) => {
  if (!chartInstance) return

  const currentWidth = currentZoomRange.end - currentZoomRange.start
  let newWidth = currentWidth + delta

  // 限制宽度在5-100之间
  if (newWidth < 5) newWidth = 5
  if (newWidth > 100) newWidth = 100

  // 保持中心点不变
  const center = (currentZoomRange.start + currentZoomRange.end) / 2
  let newStart = center - newWidth / 2
  let newEnd = center + newWidth / 2

  // 限制范围在0-100之间
  if (newStart < 0) {
    newStart = 0
    newEnd = newWidth
  }
  if (newEnd > 100) {
    newEnd = 100
    newStart = 100 - newWidth
  }

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
 * 关闭框选统计面板.
 * 清除矩形框和markArea并重新渲染图表.
 * 清除所有拖拽相关状态。
 */
const closeRangeStats = () => {
  showRangeStats.value = false
  rangeStatsData.value = null
  isDragSelecting.value = false
  dragStartIndex.value = null
  dragStartPrice.value = null
  dragEndIndex.value = null
  dragEndPrice.value = null
  mouseDownScreenX.value = null
  mouseDownScreenY.value = null
  hasStartedDrag.value = false
  // 清除矩形框
  clearDragRect()
  // 重新渲染图表以清除markArea
  renderChart()
}

/**
 * 渲染拖拽过程中的矩形框.
 * 使用ECharts graphic组件绘制矩形，更可靠。
 */
const renderDragRect = () => {
  if (!chartInstance || dragStartIndex.value === null || dragEndIndex.value === null ||
      dragStartPrice.value === null || dragEndPrice.value === null) return

  // 计算矩形的边界
  const leftIndex = Math.min(dragStartIndex.value, dragEndIndex.value)
  const rightIndex = Math.max(dragStartIndex.value, dragEndIndex.value)
  const topPrice = Math.max(dragStartPrice.value, dragEndPrice.value)
  const bottomPrice = Math.min(dragStartPrice.value, dragEndPrice.value)

  // 将图表坐标转换为像素坐标
  const leftPixel = chartInstance.convertToPixel('grid', [leftIndex, bottomPrice])
  const rightPixel = chartInstance.convertToPixel('grid', [rightIndex, topPrice])

  // 使用graphic绘制矩形
  const graphicElements = [
    {
      type: 'rect',
      z: 100,
      shape: {
        x: leftPixel[0],
        y: rightPixel[1],  // y坐标：topPrice对应的像素位置
        width: rightPixel[0] - leftPixel[0],
        height: leftPixel[1] - rightPixel[1]  // 高度：从bottom到top
      },
      style: {
        fill: 'rgba(59, 130, 246, 0.15)',
        stroke: '#3b82f6',
        lineWidth: 1
      }
    },
    {
      type: 'text',
      z: 101,
      style: {
        text: '选择区域',
        x: leftPixel[0] + 5,
        y: rightPixel[1] + 5,
        fontSize: 10,
        fill: '#3b82f6'
      }
    }
  ]

  chartInstance.setOption({
    graphic: graphicElements
  }, { silent: true })
}

/**
 * 清除拖拽过程中的矩形框.
 */
const clearDragRect = () => {
  if (!chartInstance) return
  chartInstance.setOption({
    graphic: []
  }, { silent: true })
}

/**
 * 渲染画线图形.
 * 使用组件内部的drawingList状态.
 */
const renderDrawingGraphics = () => {
  if (!chartInstance) return

  const graphicElements: any[] = []

  // 渲染所有已完成的画线（使用组件内部状态）
  for (const drawing of drawingList.value) {
    const elements = convertDrawingToGraphicElements(drawing, false)
    graphicElements.push(...elements)
  }

  // 渲染临时预览线（使用组件内部状态）
  if (activeDrawingData.value) {
    const tempElements = convertDrawingToGraphicElements(activeDrawingData.value, true)
    graphicElements.push(...tempElements)
  }

  chartInstance.setOption({
    graphic: graphicElements
  }, { silent: true })
}

/**
 * 清除所有画线图形.
 */
const clearDrawingGraphics = () => {
  if (!chartInstance) return
  chartInstance.setOption({
    graphic: []
  }, { silent: true })
}

/**
 * 处理清除所有画线.
 * 清空数据并重新渲染图表.
 */
const handleClearAllDrawings = () => {
  drawingList.value = []
  activeDrawingData.value = null
  drawingFirstPoint.value = null
  drawingSecondPoint.value = null
  drawingWaitingSecond.value = false
  drawingStep.value = 1
  // 重新渲染图表以清除graphic
  renderChart()
}

/**
 * 处理关闭画线工具栏.
 */
const handleCloseDrawingToolbar = () => {
  showDrawingToolbar.value = false
  drawingState.setTool(null)
  activeDrawingData.value = null
  drawingFirstPoint.value = null
  drawingSecondPoint.value = null
  drawingWaitingSecond.value = false
  drawingStep.value = 1
  // 重新渲染图表以清除graphic
  renderChart()
}

/**
 * 将画线数据转换为ECharts graphic元素.
 * 只保留line、rectangle、fibonacci、parallelChannel.
 */
const convertDrawingToGraphicElements = (drawing: any, isTemp: boolean): any[] => {
  const elements: any[] = []
  if (!chartInstance) return elements

  // 坐标转换函数
  const toPixel = (x: number, y: number): [number, number] => {
    try {
      return chartInstance!.convertToPixel('grid', [x, y])
    } catch (e) {
      return [x, y]
    }
  }

  // 直线
  if (drawing.type === 'line' && drawing.points.length >= 2) {
    const [x1, y1] = toPixel(drawing.points[0].x, drawing.points[0].y)
    const [x2, y2] = toPixel(drawing.points[1].x, drawing.points[1].y)
    elements.push({
      type: 'line',
      shape: { x1, y1, x2, y2 },
      style: { stroke: drawing.color, lineWidth: drawing.lineWidth },
      z: 100
    })
  }

  // 矩形
  if (drawing.type === 'rectangle' && drawing.points.length >= 2) {
    const [x1, y1] = toPixel(drawing.points[0].x, drawing.points[0].y)
    const [x2, y2] = toPixel(drawing.points[1].x, drawing.points[1].y)
    elements.push({
      type: 'rect',
      shape: {
        x: Math.min(x1, x2),
        y: Math.min(y1, y2),
        width: Math.abs(x2 - x1),
        height: Math.abs(y2 - y1)
      },
      style: { stroke: drawing.color, lineWidth: drawing.lineWidth, fill: drawing.color + '20' },
      z: 100
    })
  }

  // 黄金分割线（两步点击完成）
  if (drawing.type === 'fibonacci' && drawing.points.length >= 2) {
    const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    const startY = drawing.points[0].y
    const endY = drawing.points[1].y
    const priceRange = Math.abs(endY - startY)
    const baseY = Math.min(startY, endY)
    const chartWidth = chartInstance.getWidth() || 800

    levels.forEach((level) => {
      const levelY = baseY + priceRange * level
      const [, pixelY] = toPixel(0, levelY)
      elements.push({
        type: 'line',
        shape: { x1: 0, y1: pixelY, x2: chartWidth, y2: pixelY },
        style: {
          stroke: level === 0.5 ? '#f59e0b' : drawing.color,
          lineWidth: level === 0.5 ? drawing.lineWidth + 1 : drawing.lineWidth,
          opacity: 0.7
        },
        z: 99
      })
      elements.push({
        type: 'text',
        style: { text: `${(level * 100).toFixed(1)}%`, fill: drawing.color, fontSize: 11 },
        x: 5, y: pixelY - 5,
        z: 100
      })
    })
  }

  // 平行通道线（三步点击：第1、2点画主线，第3点确定平行线位置）
  if (drawing.type === 'parallelChannel') {
    const points = drawing.points
    // 已完成：3个点，主线+平行线
    if (points.length >= 3) {
      const [p1x, p1y] = toPixel(points[0].x, points[0].y)
      const [p2x, p2y] = toPixel(points[1].x, points[1].y)
      const [, p3y] = toPixel(0, points[2].y)  // 只取y坐标（第3点的高度）

      // 主线方向向量
      const dx = p2x - p1x
      const dy = p2y - p1y

      // 主线
      elements.push({
        type: 'line',
        shape: { x1: p1x, y1: p1y, x2: p2x, y2: p2y },
        style: { stroke: drawing.color, lineWidth: drawing.lineWidth },
        z: 100
      })
      // 平行线：左侧端点x坐标与主线起点对齐（垂直对齐），y坐标用第3点
      elements.push({
        type: 'line',
        shape: { x1: p1x, y1: p3y, x2: p1x + dx, y2: p3y + dy },
        style: { stroke: drawing.color, lineWidth: drawing.lineWidth, opacity: 0.7 },
        z: 99
      })
    }
    // 临时预览（第二步或第三步）
    else if (points.length >= 2 && isTemp) {
      const [p1x, p1y] = toPixel(points[0].x, points[0].y)
      const [p2x, p2y] = toPixel(points[1].x, points[1].y)
      // 主线（第二步和第三步都显示）
      elements.push({
        type: 'line',
        shape: { x1: p1x, y1: p1y, x2: p2x, y2: p2y },
        style: { stroke: drawing.color, lineWidth: drawing.lineWidth },
        z: 100
      })
      // 第三步预览：显示平行线预览（左侧端点x与主线起点垂直对齐）
      if (points.length >= 3) {
        const [, p3y] = toPixel(0, points[2].y)  // 只取y坐标
        const dx = p2x - p1x
        const dy = p2y - p1y
        elements.push({
          type: 'line',
          shape: { x1: p1x, y1: p3y, x2: p1x + dx, y2: p3y + dy },
          style: { stroke: drawing.color, lineWidth: drawing.lineWidth, opacity: 0.5 },
          z: 99
        })
      }
    }
  }

  return elements
}

/**
 * 结束拖拽框选并计算统计.
 * 统计矩形范围内的K线数据。
 * 清除临时矩形框，显示最终统计结果。
 */
const endDragSelect = () => {
  if (dragStartIndex.value === null || dragEndIndex.value === null ||
      dragStartPrice.value === null || dragEndPrice.value === null) {
    isDragSelecting.value = false
    clearDragRect()
    return
  }

  // 计算矩形的边界
  const leftIndex = Math.min(dragStartIndex.value, dragEndIndex.value)
  const rightIndex = Math.max(dragStartIndex.value, dragEndIndex.value)
  const topPrice = Math.max(dragStartPrice.value, dragEndPrice.value)
  const bottomPrice = Math.min(dragStartPrice.value, dragEndPrice.value)

  // 确保索引有效
  let startIndex = Math.max(0, leftIndex)
  let endIndex = Math.min(props.data.length - 1, rightIndex)

  // 清除临时矩形框
  clearDragRect()

  // 计算区间统计数据
  calculateRangeStatsInRect(startIndex, endIndex, bottomPrice, topPrice)

  // 重置拖拽状态
  isDragSelecting.value = false
}

/**
 * 计算矩形范围内的区间统计数据.
 * 只统计完全在矩形范围内的K线（高低价都在矩形内）.
 */
const calculateRangeStatsInRect = (startIndex: number, endIndex: number, bottomPrice: number, topPrice: number) => {
  if (!props.data.length || startIndex > endIndex) return

  const selectedData = props.data.slice(startIndex, endIndex + 1)
  if (selectedData.length === 0) return

  // 范围内最早的开盘价
  const startItem = selectedData[0]
  const startPrice = parseFloat(startItem.open as string)

  // 范围内最晚的收盘价
  const endItem = selectedData[selectedData.length - 1]
  const endPrice = parseFloat(endItem.close as string)

  // 涨跌幅度
  const changeAmount = endPrice - startPrice
  const changePercent = (changeAmount / startPrice) * 100

  // 范围内最高的最高价
  const highPrice = Math.max(...selectedData.map(d => parseFloat(d.high as string)))

  // 范围内最低的最低价
  const lowPrice = Math.min(...selectedData.map(d => parseFloat(d.low as string)))

  // 振幅
  const amplitude = ((highPrice - lowPrice) / lowPrice) * 100

  // 平均价格
  const avgPrice = selectedData.reduce((sum, d) => sum + parseFloat(d.close as string), 0) / selectedData.length

  // 构建统计数据对象，包含矩形边界信息用于markArea绘制
  rangeStatsData.value = {
    startDate: startItem.date,
    endDate: endItem.date,
    startIndex: startIndex,  // 用于markArea
    endIndex: endIndex,      // 用于markArea
    topPrice: topPrice,      // 矩形上边界（选择区域的最高价格）
    bottomPrice: bottomPrice, // 矩形下边界（选择区域的最低价格）
    periods: selectedData.length,
    startPrice: startPrice.toFixed(4),
    endPrice: endPrice.toFixed(4),
    changeAmount: changeAmount.toFixed(4),
    changePercent: changePercent.toFixed(2) + '%',
    highPrice: highPrice.toFixed(4),
    lowPrice: lowPrice.toFixed(4),
    amplitude: amplitude.toFixed(2) + '%',
    avgPrice: avgPrice.toFixed(4)
  }

  // 如果是股票市场，添加涨跌停统计
  if (hasLimitUpDown.value) {
    const limitStats = calculateLimitUpDownStats(selectedData, detectedMarketType.value)
    rangeStatsData.value.limitUpCount = limitStats.limitUpCount
    rangeStatsData.value.limitDownCount = limitStats.limitDownCount
    rangeStatsData.value.limitUpDates = limitStats.limitUpDates
    rangeStatsData.value.limitDownDates = limitStats.limitDownDates
    rangeStatsData.value.limitUpRatio = limitStats.limitUpRatio
    rangeStatsData.value.limitDownRatio = limitStats.limitDownRatio
  }

  showRangeStats.value = true
  // 重新渲染图表以显示markArea
  renderChart()
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
      currentZoomRange.start = state.zoomStart
      currentZoomRange.end = state.zoomEnd
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
      resetView()
    }
  } else {
    // 无保存状态，使用默认值（显示最近30周期）
    resetView()
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
  chartType.value = 'candle'
  visibleMA.value = ['5', '10', '20', '60']
  showRightAxis.value = false

  // 应用默认30周期显示
  resetView()

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
  const baseOption = getKLineBaseOption(props.theme, priceAxisType)

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

  // 设置图例 - 只显示均线
  baseOption.legend.data = []

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
          fontSize: 11,
          position: 'start'  // 标签在左端显示
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

    // 添加框选范围视觉指示（markArea）
    if (showRangeStats.value && rangeStatsData.value) {
      // 使用存储的矩形边界信息绘制markArea
      const startIndex = rangeStatsData.value.startIndex
      const endIndex = rangeStatsData.value.endIndex
      const topPrice = rangeStatsData.value.topPrice
      const bottomPrice = rangeStatsData.value.bottomPrice

      if (startIndex !== undefined && endIndex !== undefined &&
          topPrice !== undefined && bottomPrice !== undefined) {
        klineOption.markArea = {
          data: [
            [
              { xAxis: startIndex, yAxis: bottomPrice },
              { xAxis: endIndex, yAxis: topPrice }
            ]
          ],
          itemStyle: {
            color: 'rgba(59, 130, 246, 0.15)',
            borderColor: '#3b82f6',
            borderWidth: 1,
            borderType: 'solid'
          },
          label: {
            show: true,
            formatter: '框选范围',
            position: 'insideTopLeft',
            fontSize: 10,
            color: '#3b82f6'
          }
        }
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
      // 添加框选范围视觉指示（markArea）
      markArea: showRangeStats.value && rangeStatsData.value ? {
        data: [
          [
            { xAxis: rangeStatsData.value.startIndex, yAxis: rangeStatsData.value.bottomPrice },
            { xAxis: rangeStatsData.value.endIndex, yAxis: rangeStatsData.value.topPrice }
          ]
        ],
        itemStyle: {
          color: 'rgba(59, 130, 246, 0.15)',
          borderColor: '#3b82f6',
          borderWidth: 1,
          borderType: 'solid'
        },
        label: {
          show: true,
          formatter: '框选范围',
          position: 'insideTopLeft',
          fontSize: 10,
          color: '#3b82f6'
        }
      } : undefined,
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
          position: 'start',  // 标签在左端显示
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
  }

  // 添加均线（仅在K线模式下显示）
  if (chartType.value === 'candle') {
    visibleMA.value.forEach(period => {
      const periodNum = parseInt(period)
      if (props.maData && props.maData[`ma${period}`]) {
        const maOption = getMASeriesOption(periodNum, props.theme)
        maOption.data = props.maData[`ma${period}`].map(m => m.value)
        series.push(maOption)
        baseOption.legend.data.push(`MA${period}`)
      }
    })
  }

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
 * 切换画线工具栏显示.
 */
const toggleDrawingToolbar = () => {
  showDrawingToolbar.value = !showDrawingToolbar.value
  if (!showDrawingToolbar.value) {
    // 关闭工具栏时取消当前工具选择和清除画线
    drawingState.setTool(null)
    drawingState.cancelDrawing()
    clearDrawingGraphics()
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
 * 处理图表鼠标按下事件.
 * 所有画线工具在组件内直接处理.
 * line/rectangle/fibonacci: 两步点击模式
 * parallelChannel: 三步点击模式
 */
const handleChartMouseDown = (e: any) => {
  if (!chartInstance) return

  const pointInGrid = getMousePositionInGrid(e)
  if (!pointInGrid) return

  const tool = drawingState.currentTool.value
  const color = drawingState.currentColor.value
  const lineWidth = drawingState.currentLineWidth.value

  // 如果有画线工具
  if (tool) {
    // 两步点击模式的工具（line, rectangle, fibonacci）
    if (tool === 'line' || tool === 'rectangle' || tool === 'fibonacci') {
      if (drawingWaitingSecond.value && drawingFirstPoint.value) {
        // 第二次点击完成画线
        const drawing = {
          id: `drawing_${Date.now()}`,
          type: tool,
          points: [drawingFirstPoint.value, pointInGrid],
          color,
          lineWidth,
          createdAt: Date.now()
        }
        drawingList.value.push(drawing)
        // 清理临时状态，准备画下一条线
        drawingWaitingSecond.value = false
        drawingFirstPoint.value = null
        activeDrawingData.value = null
        // 渲染
        renderDrawingGraphics()
      } else {
        // 第一次点击
        drawingFirstPoint.value = pointInGrid
        drawingWaitingSecond.value = true
        activeDrawingData.value = {
          type: tool,
          points: [pointInGrid, pointInGrid],
          color,
          lineWidth
        }
        renderDrawingGraphics()
      }
    }
    // 平行通道：三步点击模式
    else if (tool === 'parallelChannel') {
      if (drawingStep.value === 1) {
        // 第一步：确定第一个端点
        drawingFirstPoint.value = pointInGrid
        drawingStep.value = 2
        activeDrawingData.value = {
          type: tool,
          points: [pointInGrid, pointInGrid],
          color,
          lineWidth,
          step: 1
        }
        renderDrawingGraphics()
      } else if (drawingStep.value === 2 && drawingFirstPoint.value) {
        // 第二步：确定第二个端点，画出第一条直线
        drawingSecondPoint.value = pointInGrid
        drawingStep.value = 3
        activeDrawingData.value = {
          type: tool,
          points: [drawingFirstPoint.value, pointInGrid],
          color,
          lineWidth,
          step: 2
        }
        renderDrawingGraphics()
      } else if (drawingStep.value === 3 && drawingFirstPoint.value && drawingSecondPoint.value) {
        // 第三步：确定平行线的位置，完成平行通道
        const drawing = {
          id: `drawing_${Date.now()}`,
          type: tool,
          points: [drawingFirstPoint.value, drawingSecondPoint.value, pointInGrid],
          color,
          lineWidth,
          createdAt: Date.now()
        }
        drawingList.value.push(drawing)
        // 清理临时状态，准备画下一个通道
        drawingStep.value = 1
        drawingFirstPoint.value = null
        drawingSecondPoint.value = null
        activeDrawingData.value = null
        renderDrawingGraphics()
      }
    }
    return
  }

  // 以下为区间统计的鼠标事件处理（画线工具未选中时执行）
  // 记录mousedown时的屏幕坐标（用于检测拖拽阈值）
  let screenX: number, screenY: number
  if (e.zrX !== undefined && e.zrY !== undefined) {
    screenX = e.zrX
    screenY = e.zrY
  } else if (e.offsetX !== undefined && e.offsetY !== undefined) {
    screenX = e.offsetX
    screenY = e.offsetY
  } else if (e.event && e.event.clientX !== undefined) {
    const rect = chartRef.value!.getBoundingClientRect()
    screenX = e.event.clientX - rect.left
    screenY = e.event.clientY - rect.top
  } else {
    return
  }
  mouseDownScreenX.value = screenX
  mouseDownScreenY.value = screenY

  const dataIndex = Math.round(pointInGrid.x)
  const price = pointInGrid.y
  if (dataIndex >= 0 && dataIndex < props.data.length) {
    dragStartIndex.value = dataIndex
    dragStartPrice.value = price
    dragEndIndex.value = dataIndex
    dragEndPrice.value = price
    hasStartedDrag.value = false
    lockCursorAt(dataIndex)
  }
}

/**
 * 处理图表鼠标移动事件.
 * 所有画线工具的预览在组件内直接处理.
 */
const handleChartMouseMove = (e: any) => {
  if (!chartInstance) return

  const pointInGrid = getMousePositionInGrid(e)
  if (!pointInGrid) return

  const tool = drawingState.currentTool.value

  // 画线工具预览
  if (tool) {
    // 两步点击模式（line, rectangle, fibonacci）
    if (tool === 'line' || tool === 'rectangle' || tool === 'fibonacci') {
      if (drawingWaitingSecond.value && drawingFirstPoint.value && activeDrawingData.value) {
        activeDrawingData.value.points = [drawingFirstPoint.value, pointInGrid]
        renderDrawingGraphics()
      }
    }
    // 平行通道三步点击模式
    else if (tool === 'parallelChannel' && drawingFirstPoint.value && activeDrawingData.value) {
      if (drawingStep.value === 2) {
        // 第二步预览：显示第一条直线
        activeDrawingData.value.points = [drawingFirstPoint.value, pointInGrid]
      } else if (drawingStep.value === 3 && drawingSecondPoint.value) {
        // 第三步预览：显示第一条直线和第二条平行线预览
        activeDrawingData.value.points = [drawingFirstPoint.value, drawingSecondPoint.value, pointInGrid]
      }
      renderDrawingGraphics()
    }
    return
  }

  // 如果有mousedown记录（可能要拖拽）- 区间统计功能
  if (mouseDownScreenX.value !== null && mouseDownScreenY.value !== null) {
    // 获取当前屏幕坐标
    let currentScreenX: number, currentScreenY: number
    if (e.zrX !== undefined && e.zrY !== undefined) {
      currentScreenX = e.zrX
      currentScreenY = e.zrY
    } else if (e.offsetX !== undefined && e.offsetY !== undefined) {
      currentScreenX = e.offsetX
      currentScreenY = e.offsetY
    } else if (e.event && e.event.clientX !== undefined) {
      const rect = chartRef.value!.getBoundingClientRect()
      currentScreenX = e.event.clientX - rect.left
      currentScreenY = e.event.clientY - rect.top
    } else {
      return
    }

    // 检测移动距离是否超过阈值
    const moveDistance = Math.sqrt(
      Math.pow(currentScreenX - mouseDownScreenX.value, 2) +
      Math.pow(currentScreenY - mouseDownScreenY.value, 2)
    )

    if (moveDistance > DRAG_THRESHOLD) {
      // 移动距离超过阈值，开始真正的拖拽
      hasStartedDrag.value = true
      isDragSelecting.value = true

      // 更新结束点坐标
      const dataIndex = Math.round(pointInGrid.x)
      const price = pointInGrid.y
      if (dataIndex >= 0 && dataIndex < props.data.length) {
        dragEndIndex.value = dataIndex
        dragEndPrice.value = price
        // 十字线跟随移动
        lockCursorAt(dataIndex)
        // 实时渲染矩形框
        renderDragRect()
      }
    }
  }

  // 边缘自动滚动处理
  handleEdgeAutoScroll(e)
}

/**
 * 处理图表鼠标抬起事件.
 * 支持画线结束和拖拽框选结束.
 * 对于点击-点击模式，不在此处理（由mousedown处理）.
 * 画线工具栏开启时禁止拖拽框选.
 */
const handleChartMouseUp = (e: any) => {
  const tool = drawingState.currentTool.value

  // 对于点击-点击模式的工具，mouseup不做处理（由mousedown处理）
  if (tool === 'line' || tool === 'rectangle' || tool === 'fibonacci' || tool === 'parallelChannel') {
    return
  }

  // 如果有mousedown记录 - 区间统计功能
  if (mouseDownScreenX.value !== null) {
    if (hasStartedDrag.value) {
      // 真正的拖拽：结束并计算统计
      endDragSelect()
    } else {
      // 单击：清除框选范围并关闭统计窗口
      closeRangeStats()
    }

    // 清除mousedown记录
    mouseDownScreenX.value = null
    mouseDownScreenY.value = null
    hasStartedDrag.value = false
  }
}

// 边缘自动滚动定时器
let edgeScrollTimer: number | null = null
// 边缘阈值（距离边缘多少像素触发滚动）
const EDGE_THRESHOLD = 50  // 50像素
// 滚动间隔（毫秒）
const SCROLL_INTERVAL = 100

/**
 * 处理边缘自动滚动.
 * 当鼠标接近图表边缘时，自动滚动显示更多K线.
 * 如果已到达数据边界，停止滚动，十字光标停留在最后一根有数据的K线上.
 * 画线工具栏开启时禁止滚动.
 */
const handleEdgeAutoScroll = (e: any) => {
  // 画线工具栏开启时禁止边缘滚动
  if (showDrawingToolbar.value) return
  if (!chartInstance || !chartRef.value || isDragSelecting.value || drawingState.isDrawing.value) return
  if (!props.data || props.data.length === 0) return

  // 获取鼠标屏幕坐标
  let mouseX: number
  if (e.zrX !== undefined) {
    mouseX = e.zrX
  } else if (e.offsetX !== undefined) {
    mouseX = e.offsetX
  } else if (e.event && e.event.clientX !== undefined) {
    const rect = chartRef.value.getBoundingClientRect()
    mouseX = e.event.clientX - rect.left
  } else {
    return
  }

  // 获取图表宽度
  const chartWidth = chartRef.value.clientWidth

  // 获取当前可见范围
  const option = chartInstance.getOption() as any
  const dataZoomOption = option?.dataZoom?.[0]
  if (!dataZoomOption) return

  const start = dataZoomOption.start ?? currentZoomRange.start
  const end = dataZoomOption.end ?? currentZoomRange.end
  const viewWidth = end - start

  // 计算每次滚动的百分比（滚动1个K线）
  const percentPerKline = 100 / props.data.length
  const scrollAmount = percentPerKline * 1.5  // 每次滚动1.5个K线单位

  // 判断是否接近边缘
  const nearLeftEdge = mouseX < EDGE_THRESHOLD
  const nearRightEdge = mouseX > chartWidth - EDGE_THRESHOLD

  // 检查是否已到达数据边界
  const atLeftBoundary = start <= 0.1  // 允许0.1%的误差
  const atRightBoundary = end >= 99.9  // 允许0.1%的误差

  // 清除之前的定时器
  if (edgeScrollTimer) {
    clearInterval(edgeScrollTimer)
    edgeScrollTimer = null
  }

  // 只有在有更多数据可显示时才滚动
  if (nearLeftEdge && !atLeftBoundary && start > 0) {
    // 接近左边缘且有更早的数据，向左滚动
    edgeScrollTimer = window.setInterval(() => {
      if (!chartInstance) {
        stopEdgeAutoScroll()
        return
      }
      // 重新检查边界
      const currentOption = chartInstance.getOption() as any
      const currentStart = currentOption?.dataZoom?.[0]?.start ?? 0
      if (currentStart <= 0.1) {
        stopEdgeAutoScroll()
        return
      }
      const newStart = Math.max(0, currentStart - scrollAmount)
      const newEnd = newStart + viewWidth
      chartInstance.dispatchAction({
        type: 'dataZoom',
        start: newStart,
        end: newEnd
      })
      currentZoomRange.start = newStart
      currentZoomRange.end = newEnd
    }, SCROLL_INTERVAL)
  } else if (nearRightEdge && !atRightBoundary && end < 100) {
    // 接近右边缘且有更新的数据，向右滚动
    edgeScrollTimer = window.setInterval(() => {
      if (!chartInstance) {
        stopEdgeAutoScroll()
        return
      }
      // 重新检查边界
      const currentOption = chartInstance.getOption() as any
      const currentEnd = currentOption?.dataZoom?.[0]?.end ?? 100
      if (currentEnd >= 99.9) {
        stopEdgeAutoScroll()
        return
      }
      const newEnd = Math.min(100, currentEnd + scrollAmount)
      const newStart = newEnd - viewWidth
      chartInstance.dispatchAction({
        type: 'dataZoom',
        start: newStart,
        end: newEnd
      })
      currentZoomRange.start = newStart
      currentZoomRange.end = newEnd
    }, SCROLL_INTERVAL)
  }
  // 如果已到达边界且鼠标仍在边缘，不执行任何操作
  // 十字光标会自然停留在最后一根有数据的K线上
}

/**
 * 停止边缘自动滚动.
 */
const stopEdgeAutoScroll = () => {
  if (edgeScrollTimer) {
    clearInterval(edgeScrollTimer)
    edgeScrollTimer = null
  }
}

/**
 * 获取鼠标在图表网格中的位置.
 * 支持DOM MouseEvent和zrender事件对象。
 */
const getMousePositionInGrid = (e: any): { x: number; y: number } | null => {
  if (!chartInstance || !chartRef.value) return null

  // 尝试多种方式获取鼠标坐标
  let mouseX: number, mouseY: number

  // zrender事件可能使用zrX/zrY或offsetX/offsetY
  if (e.zrX !== undefined && e.zrY !== undefined) {
    mouseX = e.zrX
    mouseY = e.zrY
  } else if (e.offsetX !== undefined && e.offsetY !== undefined) {
    mouseX = e.offsetX
    mouseY = e.offsetY
  } else if (e.clientX !== undefined && e.clientY !== undefined) {
    const rect = chartRef.value.getBoundingClientRect()
    mouseX = e.clientX - rect.left
    mouseY = e.clientY - rect.top
  } else if (e.event && e.event.clientX !== undefined) {
    // zrender包装的DOM事件
    const rect = chartRef.value.getBoundingClientRect()
    mouseX = e.event.clientX - rect.left
    mouseY = e.event.clientY - rect.top
  } else {
    logger.warn('无法获取鼠标坐标', e)
    return null
  }

  // 使用ECharts的convertFromPixel方法转换坐标（主图gridIndex: 0）
  try {
    const pointInGrid = chartInstance.convertFromPixel({ gridIndex: 0 }, [mouseX, mouseY])
    return { x: pointInGrid[0], y: pointInGrid[1] }
  } catch (err) {
    logger.warn('坐标转换失败', err)
    return null
  }
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
  gap: 8px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.symbol-name-tag {
  font-size: 12px;
  color: var(--fdas-text-muted);
  padding: 2px 6px;
  background: var(--fdas-gray-50);
  border-radius: 4px;
}

[data-theme="dark"] .symbol-name-tag {
  background: var(--fdas-gray-700);
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
  padding-left: 24px;
}

/* 图表区域 */
.chart-area {
  flex: 1;
  min-height: 300px;
}

/* 画线模式时的笔形光标 */
.chart-area.drawing-cursor {
  cursor: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="%233B82F6"/></svg>') 0 24, crosshair;
}

/* 无数据提示 */
.empty-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

/* 画线工具栏 */
.drawing-toolbar-wrapper {
  position: absolute;
  top: 60px;
  left: 12px;
  z-index: 20;
}
</style>