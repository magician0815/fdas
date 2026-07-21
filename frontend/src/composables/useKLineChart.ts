/**
 * KLineChart 实例管理 — 封装 KLineChart 生命周期.
 *
 * 管理 init/dispose/样式/精度/事件配置.
 * 完全离线，所有数据通过 DataLoader 本地回调提供.
 */

import {
  init,
  dispose,
  type Chart,
  type Styles,
  type KLineData,
} from 'klinecharts'
import { onUnmounted, shallowRef } from 'vue'
import type { MarketProfile } from './useMarketProfile'
import { createDataLoader } from './useDataLoader'

// ---- 样式工厂 ----

/** 根据市场颜色方向翻转涨跌配色 */
export function createChartStyles(
  baseStyles: Styles,
  profile: MarketProfile
): Styles {
  if (profile.colorDirection === 'green-up-red-down') {
    // 美股：交换涨跌色
    const candleBar = baseStyles.candle as any
    return {
      ...baseStyles,
      candle: {
        ...baseStyles.candle,
        bar: {
          ...(candleBar?.bar || {}),
          upColor: candleBar?.bar?.downColor || '#22c55e',
          downColor: candleBar?.bar?.upColor || '#ef4444',
        },
      },
    } as Styles
  }
  return baseStyles
}

// ---- 实例管理 ----

/**
 * KLineChart 实例管理 composable.
 *
 * 用法:
 *   const { chartRef, initChart } = useKLineChart()
 *   // 在 onMounted 中: initChart(dom, profile, data, styles)
 *   // Chart 实例在 onUnmounted 时自动销毁
 */
export function useKLineChart() {
  const chartRef = shallowRef<Chart | null>(null)

  /** 初始化 KLineChart 实例 */
  function initChart(
    container: HTMLElement | string,
    profile: MarketProfile,
    data: KLineData[],
    styles: Styles
  ): Chart | null {
    // 如果已有实例先销毁
    if (chartRef.value) {
      dispose(chartRef.value as any)
    }

    const dataLoader = createDataLoader(data)

    const chart = init(container, {
      styles,
      locale: 'zh-CN',
    })

    if (!chart) {
      console.error('[useKLineChart] 初始化 KLineChart 失败')
      return null
    }

    chart.setDataLoader(dataLoader)
    chart.setPrecision(profile.pricePrecision)
    chart.setOffsetRightDistance(profile.features.continuousTrading ? 80 : 50)

    chartRef.value = chart
    return chart
  }

  /** 销毁当前实例 */
  function destroyChart(): void {
    if (chartRef.value) {
      dispose(chartRef.value as any)
      chartRef.value = null
    }
  }

  // 组件卸载时自动清理
  onUnmounted(() => {
    destroyChart()
  })

  return {
    chartRef,
    initChart,
    destroyChart,
  }
}
