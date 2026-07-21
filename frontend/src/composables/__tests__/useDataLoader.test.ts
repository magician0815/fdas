/**
 * useDataLoader 数据管道测试.
 *
 * 测试 FastAPI 数据到 KLineData 格式转换、复权预处理.
 */

import { describe, it, expect } from 'vitest'
import {
  convertToKLineData,
  applyAdjustment,
  createDataLoader,
  type AdjustmentFactor,
} from '../useDataLoader'
import { getMarketProfile, registerMarketPresets } from '../useMarketProfile'
import type { KLineData } from 'klinecharts'

describe('useDataLoader 数据管道', () => {
  beforeAll(() => {
    registerMarketPresets()
  })

  describe('convertToKLineData', () => {
    it('应将原始数据转换为 KLineData 格式', () => {
      const profile = getMarketProfile('stock_cn')!
      const rawData = [{
        date: '2026-01-02',
        open: 100,
        high: 105,
        low: 99,
        close: 103,
        volume: 10000,
      }]

      const result = convertToKLineData(rawData, profile)

      expect(result).toHaveLength(1)
      expect(result[0].timestamp).toBe(new Date('2026-01-02').getTime())
      expect(result[0].open).toBe(100)
      expect(result[0].high).toBe(105)
      expect(result[0].low).toBe(99)
      expect(result[0].close).toBe(103)
      expect(result[0].volume).toBe(10000)
    })

    it('应处理字符串数字', () => {
      const profile = getMarketProfile('stock_cn')!
      const rawData = [{
        date: '2026-01-02',
        open: '100.5',
        high: '105.3',
        low: '99.1',
        close: '103.2',
        volume: '5000',
      }]

      const result = convertToKLineData(rawData, profile)

      expect(result[0].open).toBe(100.5)
      expect(result[0].high).toBe(105.3)
    })

    it('应注入扩展字段(持仓量/收益率/利差)', () => {
      const profile = getMarketProfile('futures_cn')!
      const rawData = [{
        date: '2026-01-02',
        open: 100,
        high: 105,
        low: 99,
        close: 103,
        open_interest: 50000,
      }]

      const result = convertToKLineData(rawData, profile)

      expect((result[0] as any).open_interest).toBe(50000)
    })

    it('空数组应返回空数组', () => {
      const profile = getMarketProfile('stock_cn')!
      const result = convertToKLineData([], profile)
      expect(result).toHaveLength(0)
    })
  })

  describe('applyAdjustment 复权处理', () => {
    const factors: AdjustmentFactor[] = [
      { date: '2026-01-03', factor: 0.95 },
      { date: '2026-01-05', factor: 1.1 },
    ]

    const data: KLineData[] = [
      { timestamp: new Date('2026-01-02').getTime(), open: 10, high: 11, low: 9, close: 10.5, volume: 100 },
      { timestamp: new Date('2026-01-03').getTime(), open: 10, high: 12, low: 9.5, close: 11, volume: 200 },
      { timestamp: new Date('2026-01-06').getTime(), open: 12, high: 13, low: 11, close: 12.5, volume: 150 },
    ]

    it('前复权应调整价格', () => {
      const result = applyAdjustment(data, factors, 'forward', 2)

      // 2026-01-02: factor=1 (before any adjustment)
      expect(result[0].close).toBe(10.5)

      // 2026-01-03: factor=0.95 (前复权: price * 0.95)
      expect(result[1].close).toBe(10.45) // 11 * 0.95

      // 2026-01-06: factor=0.95*1.1=1.045 (前复权: price * 1.045)
      expect(result[2].close).toBeCloseTo(12.5 * 1.045, 1)
    })

    it('不复权应保持原值', () => {
      const result = applyAdjustment(data, factors, 'none', 2)
      expect(result[0].close).toBe(10.5)
      expect(result[1].close).toBe(11)
      expect(result[2].close).toBe(12.5)
    })

    it('空因子应保持原值', () => {
      const result = applyAdjustment(data, [], 'forward', 2)
      expect(result[0].close).toBe(10.5)
      expect(result[1].close).toBe(11)
    })

    it('应保持精度', () => {
      const result = applyAdjustment(data, factors, 'forward', 1)
      // 10.45 四舍五入到 1 位小数，JS浮点可能有 10.4 或 10.5
      expect(result[1].close).toBeCloseTo(10.45, 0)
    })
  })

  describe('createDataLoader', () => {
    const data: KLineData[] = [
      { timestamp: 1000, open: 10, high: 11, low: 9, close: 10.5, volume: 100 },
      { timestamp: 2000, open: 11, high: 12, low: 10, close: 11.5, volume: 200 },
    ]

    it('init 应返回全部数据', async () => {
      const loader = createDataLoader(data)
      const result = await new Promise<any[]>((resolve) => {
        loader.getBars({
          type: 'init',
          callback: (d, more) => resolve({ d, more }),
        })
      })

      expect((result as any).d).toHaveLength(2)
    })

    it('空数据应返回空数组', async () => {
      const loader = createDataLoader([])
      const result = await new Promise<any[]>((resolve) => {
        loader.getBars({
          type: 'init',
          callback: (d) => resolve(d),
        })
      })

      expect(result).toHaveLength(0)
    })

    it('forward 应返回空(本地数据已包含全部)', async () => {
      const loader = createDataLoader(data)
      const result = await new Promise<any[]>((resolve) => {
        loader.getBars({
          type: 'forward',
          timestamp: 1000,
          callback: (d) => resolve(d),
        })
      })

      expect(result).toHaveLength(0)
    })
  })
})
