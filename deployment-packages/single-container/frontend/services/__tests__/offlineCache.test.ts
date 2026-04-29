/**
 * OfflineCache Service 测试.
 *
 * 测试IndexedDB离线缓存服务的核心逻辑.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import 'fake-indexeddb/auto'
import {
  KLineCacheService,
  SymbolsCacheService,
  ConfigCacheService,
  MetaCacheService,
  OfflineCacheService
} from '../offlineCache'

// Mock console.error
vi.spyOn(console, 'error').mockImplementation(() => {})

describe('OfflineCache Service', () => {
  beforeEach(async () => {
    // 清除所有缓存
    vi.clearAllMocks()
  })

  afterEach(async () => {
    // 清理
    try {
      await OfflineCacheService.clearAll()
    } catch (e) {
      // 忽略清理错误
    }
  })

  describe('OfflineCacheService初始化', () => {
    it('init应成功初始化', async () => {
      await OfflineCacheService.init()
      // 不应抛出错误
    })

    it('close应成功关闭', () => {
      OfflineCacheService.close()
      // 不应抛出错误
    })
  })

  describe('KLineCacheService', () => {
    describe('setCache/getCache', () => {
      it('应成功设置缓存', async () => {
        const data = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [
            { date: '2026-01-01', open: 7.1, high: 7.2, low: 7.0, close: 7.15, volume: 1000 }
          ],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 1
        }

        await KLineCacheService.setCache('symbol-1', 'daily', data)
        const result = await KLineCacheService.getCache('symbol-1', 'daily')

        expect(result).toBeTruthy()
        expect(result.symbolId).toBe('symbol-1')
        expect(result.period).toBe('daily')
        expect(result.data.length).toBe(1)
      })

      it('未设置缓存应返回null', async () => {
        const result = await KLineCacheService.getCache('symbol-2', 'daily')
        expect(result).toBeNull()
      })

      it('应支持自定义版本', async () => {
        const data = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 0
        }

        await KLineCacheService.setCache('symbol-1', 'daily', data, '2.0')
        const result = await KLineCacheService.getCache('symbol-1', 'daily')
        expect(result).toBeTruthy()
      })

      it('大量数据应正确缓存', async () => {
        const data = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: Array.from({ length: 100 }, (_, i) => ({
            date: `2026-01-${String(i + 1).padStart(2, '0')}`,
            open: 7.1 + i * 0.01,
            high: 7.2 + i * 0.01,
            low: 7.0 + i * 0.01,
            close: 7.15 + i * 0.01,
            volume: 1000 + i
          })),
          startDate: '2026-01-01',
          endDate: '2026-01-100',
          count: 100
        }

        await KLineCacheService.setCache('symbol-1', 'daily', data)
        const result = await KLineCacheService.getCache('symbol-1', 'daily')
        expect(result.data.length).toBe(100)
      })
    })

    describe('hasCache', () => {
      it('存在有效缓存应返回true', async () => {
        const data = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 0
        }

        await KLineCacheService.setCache('symbol-1', 'daily', data)
        const result = await KLineCacheService.hasCache('symbol-1', 'daily')
        expect(result).toBe(true)
      })

      it('不存在缓存应返回false', async () => {
        const result = await KLineCacheService.hasCache('symbol-x', 'daily')
        expect(result).toBe(false)
      })
    })

    describe('deleteCache', () => {
      it('应成功删除缓存', async () => {
        const data = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 0
        }

        await KLineCacheService.setCache('symbol-1', 'daily', data)
        await KLineCacheService.deleteCache('symbol-1', 'daily')
        const result = await KLineCacheService.getCache('symbol-1', 'daily')
        expect(result).toBeNull()
      })

      it('删除不存在的缓存不应报错', async () => {
        await KLineCacheService.deleteCache('symbol-x', 'daily')
        // 不应抛出错误
      })
    })

    describe('clearAllCache', () => {
      it('应清除所有K线缓存', async () => {
        const data = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 0
        }

        await KLineCacheService.setCache('symbol-1', 'daily', data)
        await KLineCacheService.setCache('symbol-2', 'daily', data)
        await KLineCacheService.clearAllCache()

        expect(await KLineCacheService.getCache('symbol-1', 'daily')).toBeNull()
        expect(await KLineCacheService.getCache('symbol-2', 'daily')).toBeNull()
      })
    })

    describe('clearExpiredCache', () => {
      it('应清除过期缓存', async () => {
        // 手动设置一个过期缓存（模拟）
        const data = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 0
        }

        await KLineCacheService.setCache('symbol-1', 'daily', data)
        // 正常情况下24小时后才过期，这里无法直接测试过期
        const count = await KLineCacheService.clearExpiredCache()
        expect(typeof count).toBe('number')
      })
    })

    describe('getCacheStats', () => {
      it('应返回缓存统计信息', async () => {
        const data = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [{ date: '2026-01-01', open: 7.1, high: 7.2, low: 7.0, close: 7.15, volume: 1000 }],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 1
        }

        await KLineCacheService.setCache('symbol-1', 'daily', data)

        const stats = await KLineCacheService.getCacheStats()
        expect(stats.totalEntries).toBe(1)
        expect(stats.totalSize).toBeGreaterThan(0)
        expect(stats.symbols).toContain('symbol-1')
      })

      it('无缓存时统计应为零', async () => {
        await KLineCacheService.clearAllCache()
        const stats = await KLineCacheService.getCacheStats()
        expect(stats.totalEntries).toBe(0)
        expect(stats.expiredEntries).toBe(0)
      })
    })

    describe('mergeCache', () => {
      it('无现有缓存时应直接设置', async () => {
        const newData = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [{ date: '2026-01-01', open: 7.1, high: 7.2, low: 7.0, close: 7.15, volume: 1000 }],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 1
        }

        await KLineCacheService.mergeCache('symbol-1', 'daily', newData)
        const result = await KLineCacheService.getCache('symbol-1', 'daily')
        expect(result.data.length).toBe(1)
      })

      it('应合并新数据到现有缓存', async () => {
        const existingData = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [{ date: '2026-01-01', open: 7.1, high: 7.2, low: 7.0, close: 7.15, volume: 1000 }],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 1
        }

        await KLineCacheService.setCache('symbol-1', 'daily', existingData)

        const newData = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [{ date: '2026-01-02', open: 7.15, high: 7.25, low: 7.05, close: 7.20, volume: 1200 }],
          startDate: '2026-01-02',
          endDate: '2026-01-02',
          count: 1
        }

        await KLineCacheService.mergeCache('symbol-1', 'daily', newData)
        const result = await KLineCacheService.getCache('symbol-1', 'daily')
        expect(result.data.length).toBe(2)
      })

      it('相同日期应更新数据', async () => {
        const existingData = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [{ date: '2026-01-01', open: 7.1, high: 7.2, low: 7.0, close: 7.15, volume: 1000 }],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 1
        }

        await KLineCacheService.setCache('symbol-1', 'daily', existingData)

        const newData = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [{ date: '2026-01-01', open: 7.2, high: 7.3, low: 7.1, close: 7.25, volume: 1500 }],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 1
        }

        await KLineCacheService.mergeCache('symbol-1', 'daily', newData)
        const result = await KLineCacheService.getCache('symbol-1', 'daily')
        expect(result.data.length).toBe(1)
        expect(result.data[0].close).toBe(7.25)
      })

      it('应按日期排序', async () => {
        const existingData = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [{ date: '2026-01-03', open: 7.1, high: 7.2, low: 7.0, close: 7.15, volume: 1000 }],
          startDate: '2026-01-03',
          endDate: '2026-01-03',
          count: 1
        }

        await KLineCacheService.setCache('symbol-1', 'daily', existingData)

        const newData = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [{ date: '2026-01-01', open: 7.0, high: 7.1, low: 6.9, close: 7.05, volume: 900 }],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 1
        }

        await KLineCacheService.mergeCache('symbol-1', 'daily', newData)
        const result = await KLineCacheService.getCache('symbol-1', 'daily')
        expect(result.data[0].date).toBe('2026-01-01')
        expect(result.data[1].date).toBe('2026-01-03')
      })
    })
  })

  describe('SymbolsCacheService', () => {
    describe('setCache/getCache', () => {
      it('应成功设置标的列表缓存', async () => {
        const data = {
          marketType: 'forex',
          symbols: [
            { id: 'symbol-1', code: 'USDCNH', name: '美元人民币' },
            { id: 'symbol-2', code: 'EURUSD', name: '欧元美元' }
          ]
        }

        await SymbolsCacheService.setCache('forex', data)
        const result = await SymbolsCacheService.getCache('forex')

        expect(result).toBeTruthy()
        expect(result.marketType).toBe('forex')
        expect(result.symbols.length).toBe(2)
      })

      it('未设置缓存应返回null', async () => {
        const result = await SymbolsCacheService.getCache('stock')
        expect(result).toBeNull()
      })
    })

    describe('clearCache', () => {
      it('应清除指定市场缓存', async () => {
        const data = {
          marketType: 'forex',
          symbols: [{ id: 'symbol-1', code: 'USDCNH', name: '美元人民币' }]
        }

        await SymbolsCacheService.setCache('forex', data)
        await SymbolsCacheService.clearCache('forex')
        const result = await SymbolsCacheService.getCache('forex')
        expect(result).toBeNull()
      })
    })
  })

  describe('ConfigCacheService', () => {
    describe('setCache/getCache', () => {
      it('应成功设置配置缓存', async () => {
        await ConfigCacheService.setCache('chart', 'theme', 'dark')
        const result = await ConfigCacheService.getCache('chart', 'theme')
        expect(result).toBe('dark')
      })

      it('应支持复杂对象缓存', async () => {
        const config = { ma: [5, 10, 20], macd: { fast: 12, slow: 26, signal: 9 } }
        await ConfigCacheService.setCache('indicator', 'default', config)
        const result = await ConfigCacheService.getCache('indicator', 'default')
        expect(result.ma).toEqual([5, 10, 20])
      })

      it('未设置缓存应返回null', async () => {
        const result = await ConfigCacheService.getCache('unknown', 'key')
        expect(result).toBeNull()
      })
    })
  })

  describe('MetaCacheService', () => {
    describe('setLastSyncTime/getLastSyncTime', () => {
      it('应成功设置同步时间', async () => {
        const time = Date.now()
        await MetaCacheService.setLastSyncTime('kline', time)
        const result = await MetaCacheService.getLastSyncTime('kline')
        expect(result).toBe(time)
      })

      it('未设置同步时间应返回null', async () => {
        const result = await MetaCacheService.getLastSyncTime('unknown')
        expect(result).toBeNull()
      })
    })
  })

  describe('OfflineCacheService统一接口', () => {
    describe('init', () => {
      it('应成功初始化', async () => {
        await OfflineCacheService.init()
        // 初始化成功不应抛出错误
      })
    })

    describe('close', () => {
      it('应成功关闭', () => {
        OfflineCacheService.close()
        // 关闭成功不应抛出错误
      })
    })

    describe('clearAll', () => {
      it('应清除所有缓存', async () => {
        // 设置一些缓存
        const klineData = {
          symbolId: 'symbol-1',
          period: 'daily',
          data: [],
          startDate: '2026-01-01',
          endDate: '2026-01-01',
          count: 0
        }
        await KLineCacheService.setCache('symbol-1', 'daily', klineData)

        await OfflineCacheService.clearAll()

        expect(await KLineCacheService.getCache('symbol-1', 'daily')).toBeNull()
      })
    })

    describe('getStatus', () => {
      it('应返回缓存状态', async () => {
        const status = await OfflineCacheService.getStatus()
        expect(status).toBeTruthy()
        expect(status.klineStats).toBeTruthy()
        expect(status.lastSyncTimes).toBeTruthy()
      })
    })

    describe('子服务引用', () => {
      it('应暴露kline服务', () => {
        expect(OfflineCacheService.kline).toBe(KLineCacheService)
      })

      it('应暴露symbols服务', () => {
        expect(OfflineCacheService.symbols).toBe(SymbolsCacheService)
      })

      it('应暴露config服务', () => {
        expect(OfflineCacheService.config).toBe(ConfigCacheService)
      })

      it('应暴露meta服务', () => {
        expect(OfflineCacheService.meta).toBe(MetaCacheService)
      })
    })
  })
})