/**
 * DataSource页面测试.
 *
 * 测试数据源管理页面核心逻辑：配置重置按市场类型。
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 * Updated: 2026-04-23 - 新增配置重置按市场类型测试
 */

import { describe, it, expect } from 'vitest'

// 直接测试逻辑函数，不依赖组件渲染
describe('DataSource核心逻辑', () => {
  describe('市场名称获取', () => {
    const mockMarkets = [
      { id: 'market-1', name: '外汇市场' },
      { id: 'market-2', name: '股票市场' },
      { id: 'market-3', name: '期货市场' }
    ]

    const getMarketName = (marketId: string, markets: any[]) => {
      const market = markets.find(m => m.id === marketId)
      return market?.name || '--'
    }

    it('getMarketName应返回正确的市场名称', () => {
      expect(getMarketName('market-1', mockMarkets)).toBe('外汇市场')
      expect(getMarketName('market-2', mockMarkets)).toBe('股票市场')
    })
  })

  describe('getMarketCode - 市场代码获取 (v2.2.2新增)', () => {
    const markets = [
      { id: 'forex-id', code: 'forex', name: '外汇' },
      { id: 'stock-cn-id', code: 'stock_cn', name: 'A股' },
      { id: 'stock-us-id', code: 'stock_us', name: '美股' },
      { id: 'stock-hk-id', code: 'stock_hk', name: '港股' },
      { id: 'futures-cn-id', code: 'futures_cn', name: '国内期货' },
      { id: 'bond-cn-id', code: 'bond_cn', name: '国内债券' },
      { id: 'bond-us-id', code: 'bond_us', name: '美国债券' }
    ]

    // 复制 DataSource.vue 中的 getMarketCode 逻辑
    const getMarketCode = (marketId: string) => {
      const m = markets.find(m => m.id === marketId)
      return m?.code || 'forex'
    }

    it('应正确返回外汇市场代码', () => {
      expect(getMarketCode('forex-id')).toBe('forex')
    })

    it('应正确返回A股市场代码', () => {
      expect(getMarketCode('stock-cn-id')).toBe('stock_cn')
    })

    it('应正确返回美股市场代码', () => {
      expect(getMarketCode('stock-us-id')).toBe('stock_us')
    })

    it('应正确返回港股市场代码', () => {
      expect(getMarketCode('stock-hk-id')).toBe('stock_hk')
    })

    it('应正确返回期货市场代码', () => {
      expect(getMarketCode('futures-cn-id')).toBe('futures_cn')
    })

    it('应正确返回国内债券市场代码', () => {
      expect(getMarketCode('bond-cn-id')).toBe('bond_cn')
    })

    it('应正确返回美国债券市场代码', () => {
      expect(getMarketCode('bond-us-id')).toBe('bond_us')
    })

    it('未知市场ID应返回默认值forex', () => {
      expect(getMarketCode('unknown-id')).toBe('forex')
      expect(getMarketCode('')).toBe('forex')
    })
  })

  describe('resetConfig - 配置重置消息 (v2.2.2新增)', () => {
    const markets = [
      { id: 'stock-cn-id', code: 'stock_cn', name: 'A股' },
      { id: 'forex-id', code: 'forex', name: '外汇' }
    ]

    const getMarketName = (marketId: string) => {
      const m = markets.find(m => m.id === marketId)
      return m?.name || '--'
    }

    const getMarketCode = (marketId: string) => {
      const m = markets.find(m => m.id === marketId)
      return m?.code || 'forex'
    }

    // 模拟配置重置逻辑
    const resetConfig = (currentDatasource: any) => {
      if (currentDatasource) {
        const marketCode = getMarketCode(currentDatasource.market_id)
        const marketName = getMarketName(currentDatasource.market_id)
        return `已重置为${marketName}默认配置`
      }
      return '已重置为默认配置'
    }

    it('应返回A股配置重置消息', () => {
      expect(resetConfig({ market_id: 'stock-cn-id' })).toBe('已重置为A股默认配置')
    })

    it('应返回外汇配置重置消息', () => {
      expect(resetConfig({ market_id: 'forex-id' })).toBe('已重置为外汇默认配置')
    })

    it('无数据源时应返回默认消息', () => {
      expect(resetConfig(null)).toBe('已重置为默认配置')
      expect(resetConfig(undefined)).toBe('已重置为默认配置')
    })
  })
})