/**
 * 涨跌停线覆盖层 — 在 KLineChart 上绘制涨跌停水平标记线.
 *
 * 通过 registerOverlay 注册，程序化添加 extendData 中的涨跌停价格线.
 * 借鉴 KLineChart 内置 priceLine 覆盖层的实现模式.
 */

import { registerOverlay } from 'klinecharts'

registerOverlay({
  name: 'limitUpDown',
  totalStep: 1,
  needDefaultPointFigure: false,
  needDefaultXAxisFigure: false,
  needDefaultYAxisFigure: true,
  mode: 'normal',
  createPointFigures: ({ coordinates, overlay, bounding }) => {
    const { limitUpPrice, limitDownPrice, prevClose } = (overlay.extendData || {}) as {
      limitUpPrice?: number
      limitDownPrice?: number
      prevClose?: number
    }

    const figures: any[] = []

    if (limitUpPrice && bounding) {
      // 涨停虚线
      figures.push({
        type: 'line',
        attrs: {
          coordinates: [
            { x: 0, y: limitUpPrice },
            { x: bounding.width, y: limitUpPrice },
          ],
        },
        styles: {
          style: 'dashed',
          color: '#ff6b6b',
          size: 1,
          dashedValue: [6, 3],
        },
      })
      // 涨停标签
      figures.push({
        type: 'text',
        attrs: {
          x: bounding.width - 100,
          y: limitUpPrice - 16,
          text: `涨停 ${limitUpPrice}`,
        },
        styles: {
          size: 10,
          color: '#ff6b6b',
          backgroundColor: 'rgba(255, 107, 107, 0.1)',
          paddingLeft: 4,
          paddingTop: 2,
          paddingRight: 4,
          paddingBottom: 2,
        },
      })
    }

    if (limitDownPrice && bounding) {
      // 跌停虚线
      figures.push({
        type: 'line',
        attrs: {
          coordinates: [
            { x: 0, y: limitDownPrice },
            { x: bounding.width, y: limitDownPrice },
          ],
        },
        styles: {
          style: 'dashed',
          color: '#4ade80',
          size: 1,
          dashedValue: [6, 3],
        },
      })
      // 跌停标签
      figures.push({
        type: 'text',
        attrs: {
          x: bounding.width - 100,
          y: limitDownPrice + 4,
          text: `跌停 ${limitDownPrice}`,
        },
        styles: {
          size: 10,
          color: '#4ade80',
          backgroundColor: 'rgba(74, 222, 128, 0.1)',
          paddingLeft: 4,
          paddingTop: 2,
          paddingRight: 4,
          paddingBottom: 2,
        },
      })
    }

    if (prevClose && bounding) {
      // 昨收价参考线
      figures.push({
        type: 'line',
        attrs: {
          coordinates: [
            { x: 0, y: prevClose },
            { x: bounding.width, y: prevClose },
          ],
        },
        styles: {
          style: 'dashed',
          color: '#999999',
          size: 1,
          dashedValue: [3, 3],
        },
      })
    }

    return figures
  },
  createYAxisFigures: ({ overlay }) => {
    const { limitUpPrice, limitDownPrice } = (overlay.extendData || {}) as {
      limitUpPrice?: number
      limitDownPrice?: number
    }
    const figures: any[] = []

    if (limitUpPrice) {
      figures.push({
        type: 'text',
        attrs: { x: 0, y: limitUpPrice, text: `${limitUpPrice}` },
        styles: { size: 10, color: '#ff6b6b' },
      })
    }

    if (limitDownPrice) {
      figures.push({
        type: 'text',
        attrs: { x: 0, y: limitDownPrice, text: `${limitDownPrice}` },
        styles: { size: 10, color: '#4ade80' },
      })
    }

    return figures
  },
})
