<template>
  <div
    class="mobile-chart-wrapper"
    :class="deviceClass"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
    @touchcancel="handleTouchEnd"
  >
    <!-- 移动端图表头部 -->
    <div class="mobile-chart-header" v-if="isMobile">
      <div class="header-top">
        <span class="symbol-name">{{ symbolName || '选择标的' }}</span>
        <div class="price-info">
          <span class="current-price" :class="priceClass">{{ currentPrice }}</span>
          <span class="change-percent" :class="priceClass">{{ changePercent }}</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button
          size="small"
          :icon="showControls ? ArrowUp : ArrowDown"
          @click="toggleControls"
          circle
        />
      </div>
    </div>

    <!-- 简化工具栏（移动端可折叠） -->
    <div class="mobile-toolbar" :class="{ collapsed: !showControls && isMobile }">
      <div class="toolbar-row" v-if="!isMobile || showControls">
        <!-- 图表类型切换 -->
        <el-radio-group v-model="chartType" size="small">
          <el-radio-button value="candle">K线</el-radio-button>
          <el-radio-button value="line">折线</el-radio-button>
        </el-radio-group>

        <!-- 周期选择（移动端简化） -->
        <el-select v-model="period" size="small" placeholder="周期" class="period-select">
          <el-option label="日线" value="daily" />
          <el-option label="周线" value="weekly" />
          <el-option label="月线" value="monthly" />
        </el-select>

        <!-- 功能按钮（桌面端显示更多） -->
        <template v-if="!isMobile">
          <el-tooltip content="显示右侧价格轴" placement="top">
            <el-button size="small" :type="showRightAxis ? 'primary' : 'default'" @click="toggleRightAxis" circle>
              <el-icon><Rank /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="区间统计" placement="top">
            <el-button size="small" :type="isRangeSelectMode ? 'primary' : 'default'" @click="toggleRangeSelect" circle>
              <el-icon><DataLine /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="画线工具" placement="top">
            <el-button size="small" :type="showDrawingToolbar ? 'primary' : 'default'" @click="toggleDrawingToolbar" circle>
              <el-icon><Edit /></el-icon>
            </el-button>
          </el-tooltip>
        </template>

        <!-- 主题切换 -->
        <el-button size="small" @click="toggleTheme" circle>
          <el-icon>
            <component :is="theme === 'dark' ? Sunny : Moon" />
          </el-icon>
        </el-button>

        <!-- 重置视图 -->
        <el-button size="small" @click="resetView" circle>
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>

      <!-- 移动端快速操作栏 -->
      <div class="mobile-quick-actions" v-if="isMobile && showControls">
        <el-button size="small" text @click="showMoreOptions = true">
          更多 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 图表容器（动态高度） -->
    <div
      ref="chartContainerRef"
      class="chart-container"
      :style="chartContainerStyle"
    >
      <slot
        :chartInstance="chartInstance"
        :isMobile="isMobile"
        :touchState="touchState"
        :onZoomIn="handleZoomIn"
        :onZoomOut="handleZoomOut"
        :onPanStart="handlePanStart"
        :onPanMove="handlePanMove"
        :onPanEnd="handlePanEnd"
      />
    </div>

    <!-- 移动端更多选项弹窗 -->
    <el-drawer
      v-if="isMobile"
      v-model="showMoreOptions"
      direction="btt"
      title="更多选项"
      size="50%"
    >
      <div class="options-content">
        <!-- 均线设置 -->
        <div class="option-group">
          <div class="option-title">均线显示</div>
          <el-checkbox-group v-model="visibleMA">
            <el-checkbox label="5">MA5</el-checkbox>
            <el-checkbox label="10">MA10</el-checkbox>
            <el-checkbox label="20">MA20</el-checkbox>
            <el-checkbox label="60">MA60</el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 形态标记 -->
        <div class="option-group">
          <div class="option-title">形态标记</div>
          <el-checkbox-group v-model="markOptions">
            <el-checkbox label="gap">跳空缺口</el-checkbox>
            <el-checkbox label="shadow">长影线</el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 功能开关 -->
        <div class="option-group">
          <div class="option-title">功能开关</div>
          <el-switch v-model="showRightAxis" active-text="右侧价格轴" />
          <el-switch v-model="showDrawingToolbar" active-text="画线工具" />
          <el-switch v-model="isRangeSelectMode" active-text="区间统计" />
        </div>

        <!-- 价格坐标模式 -->
        <div class="option-group">
          <div class="option-title">价格坐标</div>
          <el-radio-group v-model="priceAxisType">
            <el-radio value="value">线性坐标</el-radio>
            <el-radio value="log">对数坐标</el-radio>
          </el-radio-group>
        </div>

        <!-- 快速定位 -->
        <div class="option-group">
          <div class="option-title">快速定位</div>
          <el-date-picker
            v-model="jumpToDate"
            type="date"
            placeholder="定位日期"
            size="small"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :clearable="false"
            @change="handleJumpToDate"
            style="width: 100%"
          />
        </div>
      </div>
    </el-drawer>

    <!-- 触摸缩放指示器 -->
    <div class="zoom-indicator" v-if="showZoomIndicator && isMobile">
      <span class="zoom-level">{{ zoomLevel }}x</span>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 移动端图表容器组件.
 *
 * 功能：
 * - 响应式布局适配
 * - 触摸手势处理（捏合缩放、滑动平移）
 * - 移动端简化工具栏
 * - 设备类型检测
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, computed, watch, onMounted, onUnmounted, provide } from 'vue'
import {
  ArrowDown, ArrowUp, ArrowRight, Rank, DataLine, Edit,
  RefreshRight, Sunny, Moon
} from '@element-plus/icons-vue'
import {
  useDeviceDetection,
  useTouchInteraction,
  useResponsiveSize,
  useMobileZoom,
  useMobileSwipe,
  DeviceType,
  TouchState
} from '@/utils/responsive'

// Props定义
interface Props {
  /** 标的名称 */
  symbolName?: string
  /** 标的代码 */
  symbolCode?: string
  /** 当前价格 */
  currentPrice?: string
  /** 涨跌幅 */
  changePercent?: string
  /** 图表实例（从子组件传入） */
  chartInstance?: any
  /** 图表主题 */
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  symbolName: '',
  symbolCode: '',
  currentPrice: '',
  changePercent: '',
  chartInstance: null,
  theme: 'light'
})

// Emits定义
const emit = defineEmits<{
  (e: 'chartTypeChange', type: 'candle' | 'line'): void
  (e: 'periodChange', period: string): void
  (e: 'themeChange', theme: 'light' | 'dark'): void
  (e: 'resetView'): void
  (e: 'jumpToDate', date: string): void
  (e: 'zoomChange', level: number): void
  (e: 'panStart'): void
  (e: 'panMove', delta: { x: number; y: number }): void
  (e: 'panEnd'): void
}>()

// 图表容器ref
const chartContainerRef = ref<HTMLDivElement | null>(null)

// 设备检测
const { deviceType, isMobile, isTablet, deviceClass } = useDeviceDetection()

// 响应式尺寸
const { chartHeight, buttonSize, fontSize } = useResponsiveSize()

// 触摸交互
const touchInteraction = useTouchInteraction()
const touchState = ref<TouchState>(touchInteraction.touchState.value)

// 移动端缩放
const mobileZoom = useMobileZoom()
const zoomLevel = ref(1)
const showZoomIndicator = ref(false)

// 移动端滑动
const mobileSwipe = useMobileSwipe()

// UI状态
const showControls = ref(!isMobile.value)
const showMoreOptions = ref(false)
const chartType = ref<'candle' | 'line'>('candle')
const period = ref('daily')
const showRightAxis = ref(false)
const showDrawingToolbar = ref(false)
const isRangeSelectMode = ref(false)
const visibleMA = ref(['5', '10', '20', '60'])
const markOptions = ref([])
const priceAxisType = ref<'value' | 'log'>('value')
const jumpToDate = ref('')

// 计算属性
const priceClass = computed(() => {
  if (!props.changePercent) return ''
  return parseFloat(props.changePercent) >= 0 ? 'up' : 'down'
})

const chartContainerStyle = computed(() => {
  return {
    height: isMobile.value ? `${chartHeight.value}px` : 'auto',
    minHeight: isMobile.value ? '250px' : '300px'
  }
})

const chartInstance = computed(() => props.chartInstance)

// 方法
const toggleControls = () => {
  showControls.value = !showControls.value
}

const toggleRightAxis = () => {
  showRightAxis.value = !showRightAxis.value
}

const toggleDrawingToolbar = () => {
  showDrawingToolbar.value = !showDrawingToolbar.value
}

const toggleRangeSelect = () => {
  isRangeSelectMode.value = !isRangeSelectMode.value
}

const toggleTheme = () => {
  const newTheme = props.theme === 'light' ? 'dark' : 'light'
  emit('themeChange', newTheme)
}

const resetView = () => {
  emit('resetView')
}

const handleJumpToDate = (date: string) => {
  emit('jumpToDate', date)
  showMoreOptions.value = false
}

// 触摸事件处理
const handleTouchStart = (e: TouchEvent) => {
  if (!isMobile.value) return

  const result = touchInteraction.handleTouchStart(e)
  touchState.value = result

  // 单指触摸开始平移
  if (result.touches === 1) {
    emit('panStart')
  }

  // 双指触摸开始缩放
  if (result.touches === 2) {
    mobileZoom.startZoom(result.center, result.distance)
  }
}

const handleTouchMove = (e: TouchEvent) => {
  if (!isMobile.value) return

  const result = touchInteraction.handleTouchMove(e)
  touchState.value = result

  // 单指移动处理平移
  if (result.touches === 1 && result.state === 'move') {
    const delta = {
      x: result.delta?.x || 0,
      y: result.delta?.y || 0
    }
    emit('panMove', delta)
  }

  // 双指移动处理缩放
  if (result.touches === 2) {
    const zoomResult = mobileZoom.handleZoomMove(result.distance)
    if (zoomResult) {
      zoomLevel.value = zoomResult.level
      showZoomIndicator.value = true
      emit('zoomChange', zoomResult.level)
    }
  }
}

const handleTouchEnd = (e: TouchEvent) => {
  if (!isMobile.value) return

  const result = touchInteraction.handleTouchEnd(e)
  touchState.value = result

  // 平移结束
  if (result.state === 'end') {
    emit('panEnd')
  }

  // 缩放结束
  if (result.touches === 0 && showZoomIndicator.value) {
    setTimeout(() => {
      showZoomIndicator.value = false
    }, 500)
  }

  // 检测滑动手势
  if (result.state === 'end' && result.type === 'swipe') {
    const swipeDirection = result.direction
    // 左右滑动可以切换周期或品种
    if (swipeDirection === 'left' || swipeDirection === 'right') {
      mobileSwipe.handleSwipe(swipeDirection, 'horizontal')
    }
    // 上下滑动可以切换指标显示
    if (swipeDirection === 'up' || swipeDirection === 'down') {
      mobileSwipe.handleSwipe(swipeDirection, 'vertical')
    }
  }

  // 双击处理
  if (result.type === 'double-tap') {
    // 双击重置视图
    resetView()
  }
}

// 缩放控制（用于子组件调用）
const handleZoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value * 1.2, 5)
  emit('zoomChange', zoomLevel.value)
}

const handleZoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value / 1.2, 0.5)
  emit('zoomChange', zoomLevel.value)
}

// 平移控制（用于子组件调用）
const handlePanStart = () => {
  emit('panStart')
}

const handlePanMove = (delta: { x: number; y: number }) => {
  emit('panMove', delta)
}

const handlePanEnd = () => {
  emit('panEnd')
}

// 监听图表类型变化
watch(chartType, (newType) => {
  emit('chartTypeChange', newType)
})

// 监听周期变化
watch(period, (newPeriod) => {
  emit('periodChange', newPeriod)
})

// 提供响应式上下文给子组件
provide('deviceType', deviceType)
provide('isMobile', isMobile)
provide('chartHeight', chartHeight)

// 生命周期
onMounted(() => {
  // 初始化显示控制状态
  showControls.value = !isMobile.value
})

onUnmounted(() => {
  // 清理
})

// 暴露方法和状态
defineExpose({
  isMobile,
  deviceType,
  touchState,
  zoomLevel,
  showControls,
  toggleControls,
  handleZoomIn,
  handleZoomOut
})
</script>

<style scoped>
.mobile-chart-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--fdas-bg-card);
}

/* 设备类型标识 */
.mobile-chart-wrapper.mobile {
  --chart-toolbar-height: 50px;
}

.mobile-chart-wrapper.tablet {
  --chart-toolbar-height: 48px;
}

.mobile-chart-wrapper.desktop {
  --chart-toolbar-height: 40px;
}

/* 移动端图表头部 */
.mobile-chart-header {
  display: flex;
  flex-direction: column;
  padding: 8px 12px;
  background: var(--fdas-bg-card);
  border-bottom: 1px solid var(--fdas-border-light);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.symbol-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.price-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
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
  font-size: 12px;
  font-weight: 500;
}

.change-percent.up {
  color: #ef4444;
}

.change-percent.down {
  color: #22c55e;
}

.header-actions {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

/* 工具栏 */
.mobile-toolbar {
  padding: 8px 12px;
  background: var(--fdas-bg-card);
  border-bottom: 1px solid var(--fdas-border-light);
  transition: all var(--fdas-transition-normal);
}

.mobile-toolbar.collapsed {
  padding: 4px 12px;
  height: 40px;
  overflow: hidden;
}

.toolbar-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.period-select {
  width: 80px;
}

.mobile-quick-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

/* 图表容器 */
.chart-container {
  flex: 1;
  position: relative;
  min-height: 250px;
}

/* 缩放指示器 */
.zoom-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  z-index: 100;
  pointer-events: none;
}

.zoom-level {
  font-weight: 700;
}

/* 更多选项弹窗内容 */
.options-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-group {
  padding: 12px;
  background: var(--fdas-gray-50);
  border-radius: 8px;
}

.option-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--fdas-text-primary);
  margin-bottom: 8px;
}

.option-group .el-checkbox-group,
.option-group .el-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.option-group .el-switch {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

/* 移动端适配 */
@media (max-width: 576px) {
  .mobile-chart-header {
    padding: 6px 8px;
  }

  .symbol-name {
    font-size: 13px;
  }

  .current-price {
    font-size: 14px;
  }

  .toolbar-row {
    gap: 4px;
  }

  .toolbar-row .el-button {
    min-width: 36px;
    padding: 6px;
  }
}
</style>