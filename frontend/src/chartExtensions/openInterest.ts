/**
 * 期货持仓量指标 — 在 KLineChart 中展示期货 OI 数据.
 *
 * 作为 KLineChart 自定义指标注册，在独立 IndicatorPane 中渲染持仓量柱状图.
 */

import { registerIndicator } from 'klinecharts'

registerIndicator({
  name: 'OI',
  shortName: '持仓量',
  series: 'volume',
  shouldFormatBigNumber: true,
  figures: [
    {
      key: 'oi',
      title: '持仓量: ',
      type: 'bar',
      baseValue: 0,
      styles: (dataList: any[], indicator: any) => {
        // 持仓量变化：上升用红色，下降用绿色
        const result: Record<number, any> = {}
        for (let i = 1; i < dataList.length; i++) {
          const prev = dataList[i - 1]?.open_interest ?? 0
          const curr = dataList[i]?.open_interest ?? 0
          result[i] = {
            color: curr >= prev ? '#ef4444' : '#22c55e',
          }
        }
        return result
      },
    },
  ],
  calc: (dataList: any[]) => {
    return dataList.map((k) => {
      const oi = k?.open_interest
      return oi != null && oi > 0 ? { oi } : {}
    })
  },
})
