/**
 * KLineChart 主题配置 — 映射 FDAS 现有 chartThemes 配色到 KLineChart Styles.
 *
 * 两个内置主题: light(浅色) / dark(深色).
 * 通过 registerStyles 注册后，使用 chart.setStyles(styles) 切换.
 */

import { registerStyles } from 'klinecharts'
import type { Styles } from 'klinecharts'

// ---- 浅色主题 ----

const lightStyles: Styles = {
  grid: {
    show: true,
    horizontal: {
      show: true,
      size: 1,
      color: '#e0e0e0',
      style: 'dashed',
      dashedValue: [4, 2],
    },
    vertical: {
      show: true,
      size: 1,
      color: '#e0e0e0',
      style: 'dashed',
      dashedValue: [4, 2],
    },
  },
  candle: {
    type: 'candle_solid',
    bar: {
      upColor: '#ef4444',
      downColor: '#22c55e',
      noChangeColor: '#999999',
      upBorderColor: '#ef4444',
      downBorderColor: '#22c55e',
      noChangeBorderColor: '#999999',
    },
    priceMark: { show: true },
    tooltip: {
      showRule: 'follow_cross',
      showType: 'standard',
      labels: ['时间: {time}', '开: {open}', '收: {close}', '高: {high}', '低: {low}', '量: {volume}'],
      values: [],
    },
  },
  indicator: {
    bars: [{ upColor: '#ef4444', downColor: '#22c55e', noChangeColor: '#999999' }],
    tooltip: {
      showRule: 'follow_cross',
      showType: 'standard',
    },
  },
  xAxis: {
    show: true,
    axisLine: { show: true, color: '#cccccc', size: 1 },
    tickLine: { show: true, color: '#cccccc', size: 1 },
    tickText: { show: true, color: '#666666', size: 10 },
  },
  yAxis: {
    show: true,
    axisLine: { show: true, color: '#cccccc', size: 1 },
    tickLine: { show: false },
    tickText: { show: true, color: '#666666', size: 10 },
  },
  crosshair: {
    show: true,
    horizontal: {
      show: true,
      line: { show: true, color: '#999999', style: 'dashed', size: 1, dashedValue: [4, 2] },
      text: {
        show: true,
        color: '#ffffff',
        size: 10,
        backgroundColor: '#999999',
        paddingLeft: 4,
        paddingTop: 2,
        paddingRight: 4,
        paddingBottom: 2,
      },
    },
    vertical: {
      show: true,
      line: { show: true, color: '#999999', style: 'dashed', size: 1, dashedValue: [4, 2] },
      text: {
        show: true,
        color: '#ffffff',
        size: 10,
        backgroundColor: '#999999',
        paddingLeft: 4,
        paddingTop: 2,
        paddingRight: 4,
        paddingBottom: 2,
      },
    },
  },
}

// ---- 深色主题 ----

const darkStyles: Styles = {
  grid: {
    show: true,
    horizontal: {
      show: true,
      size: 1,
      color: '#2d2d4a',
      style: 'dashed',
      dashedValue: [4, 2],
    },
    vertical: {
      show: true,
      size: 1,
      color: '#2d2d4a',
      style: 'dashed',
      dashedValue: [4, 2],
    },
  },
  candle: {
    type: 'candle_solid',
    bar: {
      upColor: '#ff4d4f',
      downColor: '#52c41a',
      noChangeColor: '#666666',
      upBorderColor: '#ff4d4f',
      downBorderColor: '#52c41a',
      noChangeBorderColor: '#666666',
    },
    priceMark: { show: true },
    tooltip: {
      showRule: 'follow_cross',
      showType: 'standard',
      labels: ['时间: {time}', '开: {open}', '收: {close}', '高: {high}', '低: {low}', '量: {volume}'],
      values: [],
    },
  },
  indicator: {
    bars: [{ upColor: '#ff4d4f', downColor: '#52c41a', noChangeColor: '#666666' }],
    tooltip: {
      showRule: 'follow_cross',
      showType: 'standard',
    },
  },
  xAxis: {
    show: true,
    axisLine: { show: true, color: '#3d3d5a', size: 1 },
    tickLine: { show: true, color: '#3d3d5a', size: 1 },
    tickText: { show: true, color: '#a0a0a0', size: 10 },
  },
  yAxis: {
    show: true,
    axisLine: { show: true, color: '#3d3d5a', size: 1 },
    tickLine: { show: false },
    tickText: { show: true, color: '#a0a0a0', size: 10 },
  },
  crosshair: {
    show: true,
    horizontal: {
      show: true,
      line: { show: true, color: '#666666', style: 'dashed', size: 1, dashedValue: [4, 2] },
      text: {
        show: true,
        color: '#e0e0e0',
        size: 10,
        backgroundColor: '#666666',
        paddingLeft: 4,
        paddingTop: 2,
        paddingRight: 4,
        paddingBottom: 2,
      },
    },
    vertical: {
      show: true,
      line: { show: true, color: '#666666', style: 'dashed', size: 1, dashedValue: [4, 2] },
      text: {
        show: true,
        color: '#e0e0e0',
        size: 10,
        backgroundColor: '#666666',
        paddingLeft: 4,
        paddingTop: 2,
        paddingRight: 4,
        paddingBottom: 2,
      },
    },
  },
}

// ---- 注册 ----

export function registerChartThemes(): void {
  registerStyles('light', lightStyles)
  registerStyles('dark', darkStyles)
}

export { lightStyles, darkStyles }
