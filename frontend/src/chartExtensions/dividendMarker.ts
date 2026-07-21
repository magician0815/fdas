/**
 * 除权除息标记覆盖层 — 在 KLineChart 上标记除权除息事件.
 */

import { registerOverlay } from 'klinecharts'

registerOverlay({
  name: 'dividendMarker',
  totalStep: 1,
  needDefaultPointFigure: false,
  needDefaultXAxisFigure: false,
  needDefaultYAxisFigure: false,
  createPointFigures: ({ overlay, bounding }) => {
    const { dividends } = (overlay.extendData || {}) as {
      dividends?: Array<{
        x: number        // 像素X坐标
        y: number        // 像素Y坐标
        label: string    // 如 "DR", "D", "10送5"
        date: string
      }>
    }

    if (!dividends || !bounding) return []

    return dividends.map((d) => [
      // 标记三角形
      {
        type: 'polygon',
        attrs: {
          coordinates: [
            { x: d.x, y: d.y - 12 },
            { x: d.x - 6, y: d.y },
            { x: d.x + 6, y: d.y },
          ],
        },
        styles: {
          style: 'stroke_fill',
          color: 'rgba(245, 158, 11, 0.2)',
          borderColor: '#f59e0b',
          borderSize: 1,
        },
      },
      // 文字标签
      {
        type: 'text',
        attrs: {
          x: d.x - 15,
          y: d.y - 24,
          text: d.label,
        },
        styles: {
          size: 8,
          color: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.15)',
          paddingLeft: 2,
          paddingTop: 1,
          paddingRight: 2,
          paddingBottom: 1,
        },
      },
    ]).flat()
  },
})
