/**
 * K线图表状态管理Hook.
 *
 * 从KLineChart.vue提取的状态管理逻辑.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { ref, computed } from 'vue'
import { preferencesService, PreferenceKeys } from '@/services/preferences'

// 图表类型
export type ChartType = 'candle' | 'line'

// 价格坐标类型
export type PriceAxisType = 'value' | 'log'

// K线形态标记选项
export type MarkOption = 'gap' | 'shadow'

/**
 * K线图表状态Hook.
 *
 * 管理图表显示状态、用户偏好恢复和保存.
 */
export function useKLineChartState() {
  // 从偏好服务恢复用户设置
  const chartType = ref<ChartType>(
    preferencesService.get(PreferenceKeys.CHART_TYPE)
  )

  const visibleMA = ref<string[]>(
    preferencesService.get(PreferenceKeys.VISIBLE_MA)
  )

  const showRightAxis = ref<boolean>(
    preferencesService.get(PreferenceKeys.SHOW_RIGHT_AXIS)
  )

  const showGapMarks = ref<boolean>(
    preferencesService.get(PreferenceKeys.SHOW_GAP_MARKS)
  )

  const showLongShadowMarks = ref<boolean>(
    preferencesService.get(PreferenceKeys.SHOW_LONG_SHADOW_MARKS)
  )

  const priceAxisType = ref<PriceAxisType>(
    preferencesService.get(PreferenceKeys.PRICE_AXIS_TYPE)
  )

  const drawingColor = ref<string>(
    preferencesService.get(PreferenceKeys.DRAWING_COLOR)
  )

  const drawingWidth = ref<number>(
    preferencesService.get(PreferenceKeys.DRAWING_WIDTH)
  )

  const drawingMagnet = ref<boolean>(
    preferencesService.get(PreferenceKeys.DRAWING_MAGNET)
  )

  // K线形态标记选项（从偏好组合）
  const markOptions = ref<MarkOption[]>(
    [
      showGapMarks.value ? 'gap' : null,
      showLongShadowMarks.value ? 'shadow' : null
    ].filter(Boolean) as MarkOption[]
  )

  // 区间选择状态
  const isRangeSelectMode = ref(false)
  const rangeStatsData = ref<any>(null)

  // 画线工具状态
  const showDrawingToolbar = ref(false)

  // 复权面板状态
  const showAdjustmentPanel = ref(false)

  // 快速定位日期
  const jumpToDate = ref<string>('')

  // 价格数据（用于显示当前价格）
  const currentPrice = ref<string | null>(null)
  const changePercent = ref<string | null>(null)

  // 价格样式类
  const priceClass = computed(() => {
    if (!changePercent.value) return ''
    const change = parseFloat(changePercent.value)
    if (change > 0) return 'price-up'
    if (change < 0) return 'price-down'
    return 'price-neutral'
  })

  /**
   * 保存用户偏好到localStorage.
   */
  const savePreferences = () => {
    preferencesService.set(PreferenceKeys.CHART_TYPE, chartType.value)
    preferencesService.set(PreferenceKeys.VISIBLE_MA, visibleMA.value)
    preferencesService.set(PreferenceKeys.SHOW_RIGHT_AXIS, showRightAxis.value)
    preferencesService.set(PreferenceKeys.SHOW_GAP_MARKS, showGapMarks.value)
    preferencesService.set(PreferenceKeys.SHOW_LONG_SHADOW_MARKS, showLongShadowMarks.value)
    preferencesService.set(PreferenceKeys.PRICE_AXIS_TYPE, priceAxisType.value)
    preferencesService.set(PreferenceKeys.DRAWING_COLOR, drawingColor.value)
    preferencesService.set(PreferenceKeys.DRAWING_WIDTH, drawingWidth.value)
    preferencesService.set(PreferenceKeys.DRAWING_MAGNET, drawingMagnet.value)
  }

  /**
   * 更新形态标记选项并同步偏好.
   */
  const updateMarkOptions = (options: MarkOption[]) => {
    markOptions.value = options
    showGapMarks.value = options.includes('gap')
    showLongShadowMarks.value = options.includes('shadow')
    preferencesService.set(PreferenceKeys.SHOW_GAP_MARKS, showGapMarks.value)
    preferencesService.set(PreferenceKeys.SHOW_LONG_SHADOW_MARKS, showLongShadowMarks.value)
  }

  /**
   * 切换图表类型并保存偏好.
   */
  const toggleChartType = (type: ChartType) => {
    chartType.value = type
    preferencesService.set(PreferenceKeys.CHART_TYPE, type)
  }

  /**
   * 切换右侧价格轴并保存偏好.
   */
  const toggleRightAxis = () => {
    showRightAxis.value = !showRightAxis.value
    preferencesService.set(PreferenceKeys.SHOW_RIGHT_AXIS, showRightAxis.value)
  }

  /**
   * 切换价格坐标模式并保存偏好.
   */
  const togglePriceAxisType = () => {
    priceAxisType.value = priceAxisType.value === 'value' ? 'log' : 'value'
    preferencesService.set(PreferenceKeys.PRICE_AXIS_TYPE, priceAxisType.value)
  }

  return {
    // 状态
    chartType,
    visibleMA,
    showRightAxis,
    showGapMarks,
    showLongShadowMarks,
    priceAxisType,
    drawingColor,
    drawingWidth,
    drawingMagnet,
    markOptions,
    isRangeSelectMode,
    rangeStatsData,
    showDrawingToolbar,
    showAdjustmentPanel,
    jumpToDate,
    currentPrice,
    changePercent,
    priceClass,

    // 方法
    savePreferences,
    updateMarkOptions,
    toggleChartType,
    toggleRightAxis,
    togglePriceAxisType
  }
}