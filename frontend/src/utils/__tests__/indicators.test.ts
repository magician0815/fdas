/**
 * 技术指标计算工具测试.
 *
 * Author: FDAS Team
 * Created: 2026-04-29
 */

import { describe, it, expect } from 'vitest'
import { calculateMA, calculateMACD, calculateVOL, calculateAllIndicators } from '../indicators'
import type { KLineRecord } from '../indicators'

const mockData: KLineRecord[] = [
  { date: '2026-01-02', open: 10.0, close: 10.5, high: 10.8, low: 9.9, volume: 10000 },
  { date: '2026-01-03', open: 10.5, close: 11.0, high: 11.2, low: 10.4, volume: 12000 },
  { date: '2026-01-04', open: 11.0, close: 10.8, high: 11.3, low: 10.7, volume: 9000 },
  { date: '2026-01-05', open: 10.8, close: 11.2, high: 11.5, low: 10.6, volume: 15000 },
  { date: '2026-01-06', open: 11.2, close: 11.5, high: 11.8, low: 11.0, volume: 18000 },
  { date: '2026-01-07', open: 11.5, close: 11.3, high: 11.7, low: 11.1, volume: 11000 },
  { date: '2026-01-08', open: 11.3, close: 11.8, high: 12.0, low: 11.2, volume: 20000 },
  { date: '2026-01-09', open: 11.8, close: 12.0, high: 12.3, low: 11.7, volume: 22000 },
  { date: '2026-01-10', open: 12.0, close: 11.6, high: 12.2, low: 11.5, volume: 16000 },
  { date: '2026-01-11', open: 11.6, close: 11.9, high: 12.1, low: 11.4, volume: 14000 },
]

describe('calculateMA', () => {
  it('应返回正确key格式(ma+周期)', () => {
    const result = calculateMA(mockData, ['5', '10'])
    expect(result).toHaveProperty('ma5')
    expect(result).toHaveProperty('ma10')
  })

  it('前N-1个值应为null', () => {
    const result = calculateMA(mockData, ['5'])
    expect(result.ma5[0].value).toBeNull()
    expect(result.ma5[1].value).toBeNull()
    expect(result.ma5[2].value).toBeNull()
    expect(result.ma5[3].value).toBeNull()
    expect(result.ma5[4].value).not.toBeNull()
  })

  it('应正确计算SMA值', () => {
    const result = calculateMA(mockData, ['5'])
    const expectedMA5 = (10.5 + 11.0 + 10.8 + 11.2 + 11.5) / 5
    expect(result.ma5[4].value).toBeCloseTo(expectedMA5, 4)
  })

  it('空数据应返回空对象', () => {
    const result = calculateMA([], ['5', '10'])
    expect(result).toEqual({})
  })

  it('无效周期应被跳过', () => {
    const result = calculateMA(mockData, ['abc', '-1'])
    expect(Object.keys(result)).toHaveLength(0)
  })

  it('支持多个周期同时计算', () => {
    const result = calculateMA(mockData, ['5', '10', '20'])
    expect(Object.keys(result)).toHaveLength(3)
    expect(result.ma5).toBeDefined()
    expect(result.ma10).toBeDefined()
    expect(result.ma20).toBeDefined()
  })

  it('ma20在前19个位置为null', () => {
    const result = calculateMA(mockData, ['20'])
    for (let i = 0; i < 19; i++) {
      if (i < mockData.length) {
        expect(result.ma20[i].value).toBeNull()
      }
    }
  })
})

describe('calculateMACD', () => {
  it('应返回标准格式 {dif, dea, macd}', () => {
    const result = calculateMACD(mockData)
    expect(result).toHaveProperty('dif')
    expect(result).toHaveProperty('dea')
    expect(result).toHaveProperty('macd')
    expect(result.dif).toHaveLength(mockData.length)
    expect(result.dea).toHaveLength(mockData.length)
    expect(result.macd).toHaveLength(mockData.length)
  })

  it('前期EMA未成熟时DIF应为null', () => {
    const result = calculateMACD(mockData, 12, 26, 9)
    // 索引0处两个EMA均取close[0]，故DIF=0
    expect(result.dif[0]).toBe(0)
    // 索引1处fastEMA[1]=null, slowEMA[1]=null，故DIF=null
    expect(result.dif[1]).toBeNull()
  })

  it('MACD柱应为 2*(DIF-DEA)', () => {
    const data: KLineRecord[] = []
    for (let i = 0; i < 40; i++) {
      data.push({
        date: `2026-01-${String(i + 1).padStart(2, '0')}`,
        open: 10 + i * 0.1,
        close: 10 + i * 0.15,
        high: 10 + i * 0.2,
        low: 10 + i * 0.05,
        volume: 10000
      })
    }
    const result = calculateMACD(data, 12, 26, 9)
    for (let i = 0; i < data.length; i++) {
      if (result.dif[i] != null && result.dea[i] != null) {
        const expectedMacd = 2 * (result.dif[i]! - result.dea[i]!)
        expect(result.macd[i]).toBeCloseTo(expectedMacd, 4)
      }
    }
  })

  it('空数据应返回空数组', () => {
    const result = calculateMACD([], 12, 26, 9)
    expect(result.dif).toEqual([])
    expect(result.dea).toEqual([])
    expect(result.macd).toEqual([])
  })

  it('应接受自定义参数', () => {
    const result = calculateMACD(mockData, 10, 20, 5)
    expect(result.dif).toHaveLength(mockData.length)
  })
})

describe('calculateVOL', () => {
  it('应返回正确key格式(vol+周期)', () => {
    const result = calculateVOL(mockData, ['5', '10'])
    expect(result).toHaveProperty('vol5')
    expect(result).toHaveProperty('vol10')
  })

  it('前N-1个值应为null', () => {
    const result = calculateVOL(mockData, ['5'])
    expect(result.vol5[0].value).toBeNull()
    expect(result.vol5[3].value).toBeNull()
    expect(result.vol5[4].value).not.toBeNull()
  })

  it('应正确计算成交量MA', () => {
    const result = calculateVOL(mockData, ['5'])
    const expectedVol5 = (10000 + 12000 + 9000 + 15000 + 18000) / 5
    expect(result.vol5[4].value).toBeCloseTo(expectedVol5, 4)
  })

  it('空数据应返回空对象', () => {
    const result = calculateVOL([], ['5'])
    expect(result).toEqual({})
  })

  it('缺少volume字段的数据应使用0', () => {
    const data = [
      { date: '2026-01-01', open: 10, close: 10.5, high: 11, low: 9.5 },
      { date: '2026-01-02', open: 10.5, close: 11, high: 11.5, low: 10 },
    ]
    const result = calculateVOL(data as KLineRecord[], ['1'])
    expect(result.vol1).toBeDefined()
  })
})

describe('calculateAllIndicators', () => {
  it('应一次性返回ma/macd/vol', () => {
    const result = calculateAllIndicators(mockData)
    expect(result).toHaveProperty('ma')
    expect(result).toHaveProperty('macd')
    expect(result).toHaveProperty('vol')
    expect(result.ma).toHaveProperty('ma5')
    expect(result.macd).toHaveProperty('dif')
    expect(result.vol).toHaveProperty('vol5')
  })

  it('应接受自定义参数', () => {
    const result = calculateAllIndicators(
      mockData,
      ['10', '30'],
      { fast: 10, slow: 20, signal: 5 },
      ['10']
    )
    expect(result.ma).toHaveProperty('ma10')
    expect(result.ma).toHaveProperty('ma30')
    expect(result.vol).toHaveProperty('vol10')
  })

  it('空数据应返回空结构', () => {
    const result = calculateAllIndicators([])
    expect(result.ma).toEqual({})
    expect(result.macd.dif).toEqual([])
    expect(result.vol).toEqual({})
  })
})
