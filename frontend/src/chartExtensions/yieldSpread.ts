/**
 * 债券收益率/中美利差指标 — 在 KLineChart 中展示债券收益率曲线.
 *
 * YIELD: 单债券收益率曲线
 * YIELD_SPREAD: 中美利差曲线（美债特有）
 */

import { registerIndicator } from 'klinecharts'

// 债券收益率指标
registerIndicator({
  name: 'YIELD',
  shortName: '收益率',
  series: 'normal',
  precision: 4,
  figures: [
    {
      key: 'yield',
      title: '收益率: ',
      type: 'line',
    },
  ],
  calc: (dataList: any[]) => {
    return dataList.map((k) => {
      const y = k?.yield
      return y != null ? { yield: y } : {}
    })
  },
})

// 中美利差指标
registerIndicator({
  name: 'YIELD_SPREAD',
  shortName: '中美利差',
  series: 'normal',
  precision: 4,
  figures: [
    {
      key: 'spread',
      title: '利差: ',
      type: 'line',
    },
  ],
  calc: (dataList: any[]) => {
    return dataList.map((k) => {
      const s = k?.spread
      return s != null ? { spread: s } : {}
    })
  },
})
