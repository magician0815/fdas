/**
 * KLineChart 自定义扩展注册测试.
 *
 * 测试自定义指标和覆盖层的注册是否成功执行.
 */

import { describe, it, expect, beforeAll } from 'vitest'
import { registerAllExtensions } from '../index'
import { registerMarketPresets, getAllMarkets, getMarketProfile } from '@/composables/useMarketProfile'

describe('KLineChart 自定义扩展', () => {
  beforeAll(() => {
    registerMarketPresets()
    registerAllExtensions()
  })

  describe('扩展注册无异常', () => {
    it('registerAllExtensions 应不抛错', () => {
      expect(() => registerAllExtensions()).not.toThrow()
    })
  })

  describe('MarketProfile 数据完整性', () => {
    it('所有7个市场应有完整配置', () => {
      const markets = getAllMarkets()
      expect(markets).toHaveLength(7)

      for (const m of markets) {
        expect(m.id).toBeTruthy()
        expect(m.displayName).toBeTruthy()
        expect(m.pricePrecision).toBeGreaterThanOrEqual(0)
        expect(m.defaultIndicators.length).toBeGreaterThan(0)
        expect(m.subChartSlots).toBeDefined()
        expect(m.periodOptions.length).toBeGreaterThan(0)
      }
    })

    it('各市场特征应互不相同', () => {
      const stock = getMarketProfile('stock_cn')
      const forex = getMarketProfile('forex')
      const futures = getMarketProfile('futures_cn')
      const bond = getMarketProfile('bond_cn')

      expect(stock!.features.limitUpDown).toBe(true)
      expect(forex!.features.limitUpDown).toBe(false)
      expect(futures!.features.openInterest).toBe(true)
      expect(stock!.features.openInterest).toBe(false)
      expect(bond!.features.yieldDisplay).toBe(true)
      expect(stock!.features.yieldDisplay).toBe(false)
    })
  })
})
