/**
 * MarketProfile 系统测试.
 *
 * 测试市场配置注册、识别、涨跌停阈值计算.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import {
  registerMarketProfile,
  getMarketProfile,
  identifyMarket,
  getAllMarkets,
  getLimitThreshold,
  registerMarketPresets,
  type MarketProfile,
  type MarketId,
} from '../useMarketProfile'

// 最小测试用的 MarketProfile
function makeProfile(overrides: Partial<MarketProfile> & { id: MarketId }): MarketProfile {
  return {
    displayName: overrides.id,
    colorDirection: 'red-up-green-down',
    pricePrecision: 2,
    volumeUnit: 'shares',
    features: {
      limitUpDown: false, adjustment: false, openInterest: false,
      yieldDisplay: false, yieldSpread: false, continuousTrading: false,
      dividendMarkers: false,
      suspensionDetection: false, logScale: false, gapDetection: false,
    },
    subChartSlots: [],
    defaultIndicators: ['MA'],
    indicatorStrategy: 'client',
    periodOptions: [{ value: 'daily', label: '日K' }],
    apiNamespace: '',
    supportedPeriods: ['daily'],
    defaultBars: 60,
    identification: { priority: 0, matcher: () => false },
    ...overrides,
  }
}

describe('MarketProfile 市场配置系统', () => {
  beforeEach(() => {
    registerMarketPresets()
  })

  describe('registerMarketProfile', () => {
    it('应正确注册市场配置', () => {
      const profile = makeProfile({
        id: 'stock_cn',
        displayName: 'A股',
      })
      registerMarketProfile(profile)
      expect(getMarketProfile('stock_cn')).toBeDefined()
      expect(getMarketProfile('stock_cn')!.displayName).toBe('A股')
    })

    it('get 不存在市场应返回 undefined', () => {
      expect(getMarketProfile('nonexistent')).toBeUndefined()
    })
  })

  describe('identifyMarket', () => {
    it('应识别A股主板代码(6开头)', () => {
      const profile = identifyMarket('600519', '贵州茅台')
      expect(profile.id).toBe('stock_cn')
    })

    it('应识别创业板代码(30开头)', () => {
      const profile = identifyMarket('300750')
      expect(profile.id).toBe('stock_cn')
    })

    it('应识别科创板代码(688开头)', () => {
      const profile = identifyMarket('688981')
      expect(profile.id).toBe('stock_cn')
    })

    it('应识别美股代码(纯字母)', () => {
      const profile = identifyMarket('AAPL')
      expect(profile.id).toBe('stock_us')
    })

    it('应识别期货代码(字母+数字)', () => {
      const profile = identifyMarket('IF2401')
      expect(profile.id).toBe('futures_cn')
    })

    it('未知代码应兜底返回外汇市场', () => {
      const profile = identifyMarket('XYZ_UNKNOWN_CODE')
      expect(profile.id).toBe('forex')
    })
  })

  describe('getAllMarkets', () => {
    it('应返回所有7个市场', () => {
      const all = getAllMarkets()
      expect(all.length).toBe(7)
      const ids = all.map(p => p.id).sort()
      expect(ids).toEqual([
        'bond_cn', 'bond_us', 'forex', 'futures_cn',
        'stock_cn', 'stock_hk', 'stock_us',
      ])
    })
  })

  describe('市场特征差异', () => {
    it('A股应有涨跌停和复权', () => {
      const p = getMarketProfile('stock_cn')!
      expect(p.features.limitUpDown).toBe(true)
      expect(p.features.adjustment).toBe(true)
      expect(p.features.limitUpDown).toBe(true)
      expect(p.pricePrecision).toBe(2)
    })

    it('美股应红涨绿跌且无涨跌停', () => {
      const p = getMarketProfile('stock_us')!
      expect(p.colorDirection).toBe('red-up-green-down')
      expect(p.features.limitUpDown).toBe(false)
    })

    it('外汇应为4位精度且无成交量副图', () => {
      const p = getMarketProfile('forex')!
      expect(p.pricePrecision).toBe(4)
      expect(p.pricePrecision).toBe(4)
      expect(p.indicatorStrategy).toBe('server')
    })

    it('期货应有持仓量副图', () => {
      const p = getMarketProfile('futures_cn')!
      expect(p.features.openInterest).toBe(true)
      expect(p.subChartSlots.find(s => s.id === 'open_interest')).toBeDefined()
    })

    it('债券应有收益率展示', () => {
      const p = getMarketProfile('bond_cn')!
      expect(p.features.yieldDisplay).toBe(true)
      expect(p.subChartSlots.find(s => s.id === 'yield')).toBeDefined()
    })

    it('美债应有中美利差', () => {
      const p = getMarketProfile('bond_us')!
      expect(p.features.yieldSpread).toBe(true)
      expect(p.subChartSlots.find(s => s.id === 'yield_spread')).toBeDefined()
    })
  })

  describe('getLimitThreshold', () => {
    it('A股主板应为10%', () => {
      const p = getMarketProfile('stock_cn')!
      expect(getLimitThreshold(p, '600519')).toBe(10)
    })

    it('科创板应为20%', () => {
      const p = getMarketProfile('stock_cn')!
      expect(getLimitThreshold(p, '688981')).toBe(20)
    })

    it('ST股票应为5%', () => {
      const p = getMarketProfile('stock_cn')!
      expect(getLimitThreshold(p, '600000', 'ST股')).toBe(5)
    })

    it('无涨跌停市场应返回0', () => {
      const p = getMarketProfile('stock_us')!
      expect(getLimitThreshold(p, 'AAPL')).toBe(0)
    })
  })
})
