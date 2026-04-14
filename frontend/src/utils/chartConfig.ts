/**
 * ECharts图表配置工具.
 *
 * 提供专业行情图表的配色方案、样式配置.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

/**
 * 图表主题配色.
 */
export const chartThemes = {
  // 白天主题（浅色背景）
  light: {
    background: '#ffffff',
    textPrimary: '#333333',
    textSecondary: '#666666',
    gridLine: '#e0e0e0',
    axisLine: '#cccccc',
    // K线配色（红涨绿跌 - 中国市场标准）
    upColor: '#ef4444',       // 涨 - 红色
    upBorderColor: '#ef4444',
    downColor: '#22c55e',     // 跌 - 绿色
    downBorderColor: '#22c55e',
    // 均线配色
    ma5Color: '#f59e0b',      // MA5 - 橙色
    ma10Color: '#3b82f6',     // MA10 - 蓝色
    ma20Color: '#8b5cf6',     // MA20 - 紫色
    ma60Color: '#06b6d4',     // MA60 - 青色
    // MACD配色
    difColor: '#f59e0b',      // DIF线 - 橙色
    deaColor: '#3b82f6',      // DEA线 - 蓝色
    macdUpColor: '#ef4444',   // MACD柱正值 - 红色
    macdDownColor: '#22c55e', // MACD柱负值 - 绿色
    // 成交量配色
    volumeUpColor: '#ef4444',
    volumeDownColor: '#22c55e',
    // 十字光标
    crosshairColor: '#999999',
    crosshairTextColor: '#333333',
  },
  // 夜间主题（深色背景）
  dark: {
    background: '#1a1a2e',
    textPrimary: '#e0e0e0',
    textSecondary: '#a0a0a0',
    gridLine: '#2d2d4a',
    axisLine: '#3d3d5a',
    // K线配色（红涨绿跌 - 深色版本）
    upColor: '#ff4d4f',
    upBorderColor: '#ff4d4f',
    downColor: '#52c41a',
    downBorderColor: '#52c41a',
    // 均线配色
    ma5Color: '#faad14',
    ma10Color: '#1890ff',
    ma20Color: '#722ed1',
    ma60Color: '#13c2c2',
    // MACD配色
    difColor: '#faad14',
    deaColor: '#1890ff',
    macdUpColor: '#ff4d4f',
    macdDownColor: '#52c41a',
    // 成交量配色
    volumeUpColor: '#ff4d4f',
    volumeDownColor: '#52c41a',
    // 十字光标
    crosshairColor: '#666666',
    crosshairTextColor: '#e0e0e0',
  }
}

/**
 * 获取K线图基础配置.
 *
 * @param theme - 主题名称 ('light' | 'dark')
 * @returns ECharts配置对象
 */
export function getKLineBaseOption(theme = 'light') {
  const t = chartThemes[theme]

  return {
    backgroundColor: t.background,
    animation: false, // 关闭动画提升性能
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: t.crosshairColor
        },
        // 精准对齐K线中心
        snap: true,
        lineStyle: {
          type: 'solid',
          width: 1,
          color: t.crosshairColor
        }
      },
      backgroundColor: theme === 'dark' ? '#2d2d4a' : '#ffffff',
      borderColor: t.axisLine,
      textStyle: {
        color: t.textPrimary
      },
      // 数据框固定位置（不随光标移动）
      position: (point, params, dom, rect, size) => {
        // 固定在图表左上角
        return ['10%', '10%']
      },
      formatter: (params) => {
        // 自定义tooltip格式化
        const klineData = params.find(p => p.seriesType === 'candlestick')
        if (!klineData) return ''

        const data = klineData.data
        const date = klineData.name
        const open = data[1]
        const close = data[2]
        const low = data[3]
        const high = data[4]
        const change = ((close - open) / open * 100).toFixed(2)
        const changeColor = close >= open ? t.upColor : t.downColor

        return `
          <div style="font-size: 12px; line-height: 1.6;">
            <div style="font-weight: bold; margin-bottom: 4px;">${date}</div>
            <div>开盘: <span style="color: ${t.textPrimary}">${open.toFixed(4)}</span></div>
            <div>收盘: <span style="color: ${t.textPrimary}">${close.toFixed(4)}</span></div>
            <div>最高: <span style="color: ${t.upColor}">${high.toFixed(4)}</span></div>
            <div>最低: <span style="color: ${t.downColor}">${low.toFixed(4)}</span></div>
            <div>涨跌: <span style="color: ${changeColor}">${change}%</span></div>
          </div>
        `
      }
    },
    axisPointer: {
      link: [{ xAxisIndex: 'all' }], // 主副图联动
      label: {
        backgroundColor: t.crosshairColor
      }
    },
    grid: [
      // 主图区域
      {
        left: '10%',
        right: '8%',
        top: '8%',
        height: '55%'
      },
      // 成交量副图区域
      {
        left: '10%',
        right: '8%',
        top: '68%',
        height: '12%'
      },
      // MACD副图区域
      {
        left: '10%',
        right: '8%',
        top: '85%',
        height: '10%'
      }
    ],
    xAxis: [
      // 主图X轴
      {
        type: 'category',
        gridIndex: 0,
        axisLine: { lineStyle: { color: t.axisLine } },
        axisTick: { show: false },
        axisLabel: {
          color: t.textSecondary,
          fontSize: 11
        },
        splitLine: { show: false },
        data: []
      },
      // 成交量X轴（隐藏，与主图同步）
      {
        type: 'category',
        gridIndex: 1,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        splitLine: { show: false },
        data: []
      },
      // MACD X轴（隐藏，与主图同步）
      {
        type: 'category',
        gridIndex: 2,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        splitLine: { show: false },
        data: []
      }
    ],
    yAxis: [
      // 主图左Y轴（价格）
      {
        type: 'value',
        gridIndex: 0,
        position: 'left',
        scale: true, // 自适应价格范围
        axisLine: { lineStyle: { color: t.axisLine } },
        axisTick: { show: false },
        axisLabel: {
          color: t.textSecondary,
          fontSize: 11,
          formatter: (value) => value.toFixed(4)
        },
        splitLine: {
          lineStyle: {
            color: t.gridLine,
            type: 'dashed'
          }
        },
        splitArea: {
          show: true,
          areaStyle: {
            color: [theme === 'dark' ? '#1a1a2e' : '#fafafa', theme === 'dark' ? '#252540' : '#f5f5f5']
          }
        }
      },
      // 主图右Y轴（价格）- 可选显示
      {
        type: 'value',
        gridIndex: 0,
        position: 'right',
        scale: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          show: false, // 默认隐藏，可通过配置开启
          color: t.textSecondary,
          fontSize: 11,
          formatter: (value) => value.toFixed(4)
        },
        splitLine: { show: false }
      },
      // 成交量Y轴
      {
        type: 'value',
        gridIndex: 1,
        position: 'left',
        scale: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: t.textSecondary,
          fontSize: 10,
          formatter: (value) => {
            if (value >= 10000) return (value / 10000).toFixed(1) + '万'
            return value.toFixed(0)
          }
        },
        splitLine: { show: false }
      },
      // MACD Y轴
      {
        type: 'value',
        gridIndex: 2,
        position: 'left',
        scale: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: t.textSecondary,
          fontSize: 10,
          formatter: (value) => value.toFixed(2)
        },
        splitLine: {
          lineStyle: {
            color: t.gridLine,
            type: 'dashed'
          }
        }
      }
    ],
    dataZoom: [
      // 内置缩放（鼠标滚轮）
      {
        type: 'inside',
        xAxisIndex: [0, 1, 2],
        yAxisIndex: [0, 1, 2],
        start: 60, // 默认显示最近40%数据
        end: 100,
        zoomOnMouseWheel: true,
        moveOnMouseMove: true,
        moveOnMouseWheel: true,
        // 缩放边界设置
        minValueSpan: 1,  // 最小显示1根K线
        maxValueSpan: 100, // 最大显示100根K线（或根据数据调整）
        // 锚定缩放（光标位置不变）
        rangeMode: ['percent', 'percent'],
        orient: 'horizontal'
      },
      // 滑块缩放
      {
        type: 'slider',
        xAxisIndex: [0, 1, 2],
        yAxisIndex: [0, 1, 2],
        start: 60,
        end: 100,
        height: 20,
        bottom: 10,
        borderColor: t.axisLine,
        backgroundColor: theme === 'dark' ? '#2d2d4a' : '#fafafa',
        fillerColor: theme === 'dark' ? 'rgba(45, 90, 247, 0.2)' : 'rgba(45, 90, 247, 0.15)',
        handleStyle: {
          color: '#3b82f6',
          borderColor: '#3b82f6'
        },
        textStyle: {
          color: t.textSecondary
        },
        // 缩放边界设置
        minValueSpan: 1,
        maxValueSpan: 100,
        rangeMode: ['percent', 'percent']
      }
    ],
    legend: {
      enabled: true,
      data: [],
      top: 5,
      left: 'center',
      textStyle: {
        color: t.textPrimary,
        fontSize: 12
      },
      itemWidth: 15,
      itemHeight: 10
    },
    series: []
  }
}

/**
 * 获取K线系列配置.
 *
 * @param theme - 主题名称
 * @returns K线系列配置
 */
export function getKLineSeriesOption(theme = 'light') {
  const t = chartThemes[theme]

  return {
    name: 'K线',
    type: 'candlestick',
    xAxisIndex: 0,
    yAxisIndex: 0,
    itemStyle: {
      color: t.upColor,
      color0: t.downColor,
      borderColor: t.upBorderColor,
      borderColor0: t.downBorderColor
    },
    barWidth: '60%', // K线宽度
    data: []
  }
}

/**
 * 获取均线系列配置.
 *
 * @param period - 均线周期
 * @param theme - 主题名称
 * @returns 均线系列配置
 */
export function getMASeriesOption(period, theme = 'light') {
  const t = chartThemes[theme]
  const colorMap = {
    5: t.ma5Color,
    10: t.ma10Color,
    20: t.ma20Color,
    60: t.ma60Color
  }

  return {
    name: `MA${period}`,
    type: 'line',
    xAxisIndex: 0,
    yAxisIndex: 0,
    smooth: false,
    symbol: 'none',
    lineStyle: {
      width: 1,
      color: colorMap[period] || '#999999'
    },
    data: []
  }
}

/**
 * 获取成交量系列配置.
 *
 * @param theme - 主题名称
 * @returns 成交量系列配置
 */
export function getVolumeSeriesOption(theme = 'light') {
  const t = chartThemes[theme]

  return {
    name: '成交量',
    type: 'bar',
    xAxisIndex: 1,
    yAxisIndex: 1,
    barWidth: '60%',
    itemStyle: {
      color: (params) => {
        // 根据涨跌设置颜色
        return params.dataIndex % 2 === 0 ? t.volumeUpColor : t.volumeDownColor
      }
    },
    data: []
  }
}

/**
 * 获取MACD系列配置.
 *
 * @param theme - 主题名称
 * @returns MACD系列配置数组[DIF, DEA, MACD柱]
 */
export function getMACDSeriesOptions(theme = 'light') {
  const t = chartThemes[theme]

  return [
    // DIF线
    {
      name: 'DIF',
      type: 'line',
      xAxisIndex: 2,
      yAxisIndex: 2,
      symbol: 'none',
      lineStyle: {
        width: 1,
        color: t.difColor
      },
      data: []
    },
    // DEA线
    {
      name: 'DEA',
      type: 'line',
      xAxisIndex: 2,
      yAxisIndex: 2,
      symbol: 'none',
      lineStyle: {
        width: 1,
        color: t.deaColor
      },
      data: []
    },
    // MACD柱
    {
      name: 'MACD',
      type: 'bar',
      xAxisIndex: 2,
      yAxisIndex: 2,
      barWidth: '40%',
      itemStyle: {
        color: (params) => {
          return params.value >= 0 ? t.macdUpColor : t.macdDownColor
        }
      },
      data: []
    }
  ]
}

/**
 * 格式化K线数据.
 *
 * @param rawData - 原始数据数组
 * @returns 格式化后的K线数据 [open, close, low, high]
 */
export function formatKLineData(rawData) {
  if (!rawData || !rawData.length) return []

  return rawData.map(item => [
    parseFloat(item.open) || 0,   // 开盘价
    parseFloat(item.close) || 0,  // 收盘价
    parseFloat(item.low) || 0,    // 最低价
    parseFloat(item.high) || 0    // 最高价
  ])
}

/**
 * 计算涨跌状态.
 *
 * @param rawData - 原始数据数组
 * @returns 涨跌状态数组 (true为涨，false为跌)
 */
export function calculateUpDown(rawData) {
  if (!rawData || !rawData.length) return []

  return rawData.map(item => {
    const open = parseFloat(item.open) || 0
    const close = parseFloat(item.close) || 0
    return close >= open
  })
}

/**
 * 格式化成交量数据（根据涨跌设置颜色）.
 *
 * @param rawData - 原始数据数组
 * @returns 成交量数据数组，包含颜色信息
 */
export function formatVolumeData(rawData) {
  if (!rawData || !rawData.length) return []

  return rawData.map(item => {
    const open = parseFloat(item.open) || 0
    const close = parseFloat(item.close) || 0
    const volume = parseFloat(item.volume) || 0
    return {
      value: volume,
      itemStyle: {
        color: close >= open ? '#ef4444' : '#22c55e'
      }
    }
  })
}