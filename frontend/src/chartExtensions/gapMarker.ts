/**
 * 跳空缺口覆盖层 — 标记 K 线图中的跳空高开/低开缺口.
 */

import { registerOverlay } from 'klinecharts'

registerOverlay({
  name: 'gapMarker',
  totalStep: 1,
  needDefaultPointFigure: false,
  needDefaultXAxisFigure: false,
  needDefaultYAxisFigure: false,
  createPointFigures: ({ overlay, bounding }) => {
    const { gaps } = (overlay.extendData || {}) as {
      gaps?: Array<{ x: number; y: number; type: 'up' | 'down'; label: string }>
    }

    if (!gaps || !bounding) return []

    return gaps.map((gap) => ({
      type: 'rect',
      attrs: {
        x: gap.x - 4,
        y: gap.type === 'up' ? gap.y - 20 : gap.y,
        width: 8,
        height: 20,
      },
      styles: {
        style: 'stroke',
        color: gap.type === 'up' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)',
        borderColor: gap.type === 'up' ? '#ef4444' : '#22c55e',
        borderSize: 1,
      },
    }))
  },
})
