/**
 * ECharts图表管理Hook.
 *
 * 提供图表实例的创建、更新、销毁管理.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

/**
 * 图表Hook选项.
 */
interface UseChartOptions {
  /** 自动Resize */
  autoResize?: boolean
  /** 初始主题 */
  theme?: 'light' | 'dark'
}

/**
 * ECharts图表管理Hook.
 *
 * @param chartRef - 图表容器DOM ref
 * @param options - Hook选项
 * @returns 图表管理方法和状态
 */
export function useChart(chartRef, options: UseChartOptions = {}) {
  const { autoResize = true, theme = 'light' } = options

  // 图表实例
  const chartInstance = ref<echarts.ECharts | null>(null)
  // 当前主题
  const currentTheme = ref(theme)
  // 加载状态
  const loading = ref(false)

  /**
   * 初始化图表.
   */
  const initChart = () => {
    if (!chartRef.value) {
      return null
    }

    // 销毁旧实例
    if (chartInstance.value) {
      chartInstance.value.dispose()
    }

    // 创建新实例
    chartInstance.value = echarts.init(chartRef.value, undefined, {
      renderer: 'canvas' // 使用Canvas渲染器提升性能
    })

    return chartInstance.value
  }

  /**
   * 设置图表配置.
   *
   * @param option - ECharts配置对象
   * @param notMerge - 是否不合并配置
   */
  const setOption = (option: echarts.EChartsOption, notMerge = false) => {
    if (!chartInstance.value) {
      initChart()
    }

    if (chartInstance.value) {
      chartInstance.value.setOption(option, notMerge)
    }
  }

  /**
   * 清空图表.
   */
  const clearChart = () => {
    if (chartInstance.value) {
      chartInstance.value.clear()
    }
  }

  /**
   * Resize图表.
   */
  const resizeChart = () => {
    if (chartInstance.value) {
      chartInstance.value.resize()
    }
  }

  /**
   * 显示加载动画.
   */
  const showLoading = () => {
    loading.value = true
    if (chartInstance.value) {
      chartInstance.value.showLoading({
        text: '加载中...',
        color: '#3b82f6',
        textColor: '#999',
        maskColor: 'rgba(255, 255, 255, 0.8)'
      })
    }
  }

  /**
   * 隐藏加载动画.
   */
  const hideLoading = () => {
    loading.value = false
    if (chartInstance.value) {
      chartInstance.value.hideLoading()
    }
  }

  /**
   * 切换主题.
   *
   * @param newTheme - 新主题名称
   */
  const switchTheme = (newTheme: 'light' | 'dark') => {
    currentTheme.value = newTheme
    // ECharts不支持动态切换主题，需要重新初始化
    // 保存当前配置
    const currentOption = chartInstance.value?.getOption()
    initChart()
    if (currentOption && chartInstance.value) {
      chartInstance.value.setOption(currentOption as echarts.EChartsOption)
    }
  }

  /**
   * 获取图表实例.
   */
  const getChartInstance = () => chartInstance.value

  /**
   * 获取图表数据URL（用于导出图片）.
   *
   * @param type - 图片类型
   * @returns 图片数据URL
   */
  const getDataURL = (type: 'png' | 'jpeg' = 'png') => {
    if (chartInstance.value) {
      return chartInstance.value.getDataURL({
        type,
        pixelRatio: 2,
        backgroundColor: currentTheme.value === 'dark' ? '#1a1a2e' : '#fff'
      })
    }
    return ''
  }

  // 窗口Resize处理
  const handleResize = () => {
    resizeChart()
  }

  // 生命周期
  onMounted(() => {
    nextTick(() => {
      initChart()
      if (autoResize) {
        window.addEventListener('resize', handleResize)
      }
    })
  })

  onUnmounted(() => {
    if (autoResize) {
      window.removeEventListener('resize', handleResize)
    }
    if (chartInstance.value) {
      chartInstance.value.dispose()
      chartInstance.value = null
    }
  })

  // 监听主题变化
  watch(currentTheme, () => {
    // 主题变化时重新初始化
  })

  return {
    chartInstance,
    currentTheme,
    loading,
    initChart,
    setOption,
    clearChart,
    resizeChart,
    showLoading,
    hideLoading,
    switchTheme,
    getChartInstance,
    getDataURL
  }
}

/**
 * 多图表联动Hook.
 *
 * 用于管理主图、成交量、MACD等多个图表的联动.
 *
 * @param chartRefs - 图表容器DOM refs数组
 * @param options - Hook选项
 * @returns 联动图表管理方法
 */
export function useLinkedCharts(chartRefs, options: UseChartOptions = {}) {
  const charts = chartRefs.map(ref => useChart(ref, options))

  /**
   * 联动Resize.
   */
  const resizeAll = () => {
    charts.forEach(chart => chart.resizeChart())
  }

  /**
   * 联动清空.
   */
  const clearAll = () => {
    charts.forEach(chart => chart.clearChart())
  }

  /**
   * 联动显示加载.
   */
  const showLoadingAll = () => {
    charts.forEach(chart => chart.showLoading())
  }

  /**
   * 联动隐藏加载.
   */
  const hideLoadingAll = () => {
    charts.forEach(chart => chart.hideLoading())
  }

  /**
   * 联动切换主题.
   */
  const switchThemeAll = (newTheme: 'light' | 'dark') => {
    charts.forEach(chart => chart.switchTheme(newTheme))
  }

  /**
   * 绑定DataZoom联动.
   * 当一个图表缩放时，其他图表同步缩放.
   */
  const bindDataZoomLink = () => {
    // 使用ECharts的group功能实现联动
    charts.forEach((chart, index) => {
      const instance = chart.getChartInstance()
      if (instance) {
        instance.group = 'linked-charts'
      }
    })
    echarts.connect('linked-charts')
  }

  /**
   * 解绑DataZoom联动.
   */
  const unbindDataZoomLink = () => {
    echarts.disconnect('linked-charts')
  }

  // 生命周期
  onMounted(() => {
    nextTick(() => {
      bindDataZoomLink()
    })
  })

  onUnmounted(() => {
    unbindDataZoomLink()
  })

  return {
    charts,
    resizeAll,
    clearAll,
    showLoadingAll,
    hideLoadingAll,
    switchThemeAll,
    bindDataZoomLink,
    unbindDataZoomLink
  }
}