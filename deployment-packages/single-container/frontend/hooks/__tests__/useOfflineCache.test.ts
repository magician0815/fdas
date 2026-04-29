/**
 * useOfflineCache Hook测试.
 *
 * 测试离线数据缓存功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock offlineCache服务
vi.mock('@/services/offlineCache', () => ({
  OfflineCacheService: {
    init: vi.fn().mockResolvedValue(undefined),
    getStatus: vi.fn().mockResolvedValue({
      klineStats: {
        totalEntries: 100,
        totalSize: 50000,
        expiredEntries: 5,
        symbols: ['USDCNY', 'EURUSD']
      },
      lastSyncTimes: { kline: 1234567890 }
    }),
    clearAll: vi.fn().mockResolvedValue(undefined),
    close: vi.fn(),
    meta: {
      setLastSyncTime: vi.fn().mockResolvedValue(undefined)
    }
  },
  KLineCacheService: {
    hasCache: vi.fn().mockResolvedValue(true),
    getCache: vi.fn().mockResolvedValue({
      symbolId: 'test-symbol',
      period: 'daily',
      data: [{ date: '2026-04-01', open: 7.1, high: 7.2, low: 7.05, close: 7.15 }],
      startDate: '2026-04-01',
      endDate: '2026-04-01',
      count: 1,
      timestamp: Date.now()
    }),
    setCache: vi.fn().mockResolvedValue(undefined),
    mergeCache: vi.fn().mockResolvedValue(undefined),
    deleteCache: vi.fn().mockResolvedValue(undefined),
    clearExpiredCache: vi.fn().mockResolvedValue(5),
    getCacheStats: vi.fn().mockResolvedValue({
      totalEntries: 95,
      totalSize: 45000,
      expiredEntries: 0,
      symbols: ['USDCNY']
    })
  },
  SymbolsCacheService: {
    getCache: vi.fn().mockResolvedValue({
      marketType: 'forex',
      symbols: [{ id: '1', code: 'USDCNY', name: '美元人民币' }]
    }),
    setCache: vi.fn().mockResolvedValue(undefined),
    clearCache: vi.fn().mockResolvedValue(undefined)
  }
}))

// Mock navigator.onLine
vi.stubGlobal('navigator', {
  onLine: true
})

// Mock window事件监听
vi.stubGlobal('window', {
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
})

describe('useOfflineCache', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetModules()
  })

  describe('初始化', () => {
    it('应该返回初始状态', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')

      // 简化测试，不触发onMounted
      const result = useOfflineCache()

      expect(result.isInitialized).toBeDefined()
      expect(result.cacheReady).toBeDefined()
      expect(result.cacheStats).toBeDefined()
      expect(result.networkStatus).toBeDefined()
    })

    it('应该提供initCache方法', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')

      const result = useOfflineCache()

      expect(result.initCache).toBeDefined()
      expect(typeof result.initCache).toBe('function')
    })

    it('应该提供clearAllCache方法', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')

      const result = useOfflineCache()

      expect(result.clearAllCache).toBeDefined()
      expect(typeof result.clearAllCache).toBe('function')
    })

    it('应该提供clearExpiredCache方法', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')

      const result = useOfflineCache()

      expect(result.clearExpiredCache).toBeDefined()
      expect(typeof result.clearExpiredCache).toBe('function')
    })

    it('应该提供refreshCacheStats方法', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')

      const result = useOfflineCache()

      expect(result.refreshCacheStats).toBeDefined()
      expect(typeof result.refreshCacheStats).toBe('function')
    })
  })

  describe('缓存操作', () => {
    it('initCache应该初始化缓存服务', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')
      const { OfflineCacheService } = await import('@/services/offlineCache')

      const result = useOfflineCache()
      await result.initCache()

      expect(OfflineCacheService.init).toHaveBeenCalled()
    })

    it('clearAllCache应该清除所有缓存', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')
      const { OfflineCacheService } = await import('@/services/offlineCache')

      const result = useOfflineCache()
      await result.clearAllCache()

      expect(OfflineCacheService.clearAll).toHaveBeenCalled()
    })

    it('clearExpiredCache应该清除过期缓存', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')
      const { KLineCacheService } = await import('@/services/offlineCache')

      const result = useOfflineCache()
      const deletedCount = await result.clearExpiredCache()

      expect(KLineCacheService.clearExpiredCache).toHaveBeenCalled()
      expect(deletedCount).toBe(5)
    })

    it('refreshCacheStats应该刷新缓存状态', async () => {
      const { useOfflineCache } = await import('../useOfflineCache')
      const { OfflineCacheService } = await import('@/services/offlineCache')

      const result = useOfflineCache()
      await result.refreshCacheStats()

      expect(OfflineCacheService.getStatus).toHaveBeenCalled()
    })
  })
})

describe('useKLineCache', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('初始化', () => {
    it('应该返回初始状态', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')

      // 设置cacheReady
      cacheReady.value = true

      const result = useKLineCache('test-symbol', 'daily')

      expect(result.cacheData).toBeDefined()
      expect(result.hasCache).toBeDefined()
      expect(result.isLoading).toBeDefined()
      expect(result.error).toBeDefined()
    })

    it('应该提供loadCache方法', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useKLineCache('test-symbol', 'daily')

      expect(result.loadCache).toBeDefined()
    })

    it('应该提供saveCache方法', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useKLineCache('test-symbol', 'daily')

      expect(result.saveCache).toBeDefined()
    })

    it('应该提供mergeCache方法', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useKLineCache('test-symbol', 'daily')

      expect(result.mergeCache).toBeDefined()
    })

    it('应该提供deleteCache方法', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useKLineCache('test-symbol', 'daily')

      expect(result.deleteCache).toBeDefined()
    })

    it('应该提供needsUpdate方法', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useKLineCache('test-symbol', 'daily')

      expect(result.needsUpdate).toBeDefined()
    })
  })

  describe('缓存操作', () => {
    it('loadCache应该加载缓存数据', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')
      const { KLineCacheService } = await import('@/services/offlineCache')

      cacheReady.value = true
      const result = useKLineCache('test-symbol', 'daily')
      await result.loadCache()

      expect(KLineCacheService.hasCache).toHaveBeenCalled()
      expect(KLineCacheService.getCache).toHaveBeenCalled()
    })

    it('saveCache应该保存数据', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')
      const { KLineCacheService } = await import('@/services/offlineCache')

      cacheReady.value = true
      const result = useKLineCache('test-symbol', 'daily')

      const testData = [{
        date: '2026-04-01',
        open: 7.1,
        high: 7.2,
        low: 7.05,
        close: 7.15,
        volume: 0
      }]

      await result.saveCache(testData)

      expect(KLineCacheService.setCache).toHaveBeenCalled()
    })

    it('deleteCache应该删除缓存', async () => {
      const { useKLineCache, cacheReady } = await import('../useOfflineCache')
      const { KLineCacheService } = await import('@/services/offlineCache')

      cacheReady.value = true
      const result = useKLineCache('test-symbol', 'daily')
      await result.deleteCache()

      expect(KLineCacheService.deleteCache).toHaveBeenCalledWith('test-symbol', 'daily')
    })
  })
})

describe('useSymbolsCache', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('初始化', () => {
    it('应该返回初始状态', async () => {
      const { useSymbolsCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useSymbolsCache('forex')

      expect(result.cacheData).toBeDefined()
      expect(result.isLoading).toBeDefined()
      expect(result.error).toBeDefined()
    })

    it('应该提供loadCache方法', async () => {
      const { useSymbolsCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useSymbolsCache('forex')

      expect(result.loadCache).toBeDefined()
    })

    it('应该提供saveCache方法', async () => {
      const { useSymbolsCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useSymbolsCache('forex')

      expect(result.saveCache).toBeDefined()
    })

    it('应该提供clearCache方法', async () => {
      const { useSymbolsCache, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const result = useSymbolsCache('forex')

      expect(result.clearCache).toBeDefined()
    })
  })

  describe('缓存操作', () => {
    it('loadCache应该加载标的列表', async () => {
      const { useSymbolsCache, cacheReady } = await import('../useOfflineCache')
      const { SymbolsCacheService } = await import('@/services/offlineCache')

      cacheReady.value = true
      const result = useSymbolsCache('forex')
      await result.loadCache()

      expect(SymbolsCacheService.getCache).toHaveBeenCalledWith('forex')
    })

    it('saveCache应该保存标的列表', async () => {
      const { useSymbolsCache, cacheReady } = await import('../useOfflineCache')
      const { SymbolsCacheService } = await import('@/services/offlineCache')

      cacheReady.value = true
      const result = useSymbolsCache('forex')

      const testSymbols = [{ id: '1', code: 'USDCNY', name: '美元人民币' }]
      await result.saveCache(testSymbols)

      expect(SymbolsCacheService.setCache).toHaveBeenCalled()
    })

    it('clearCache应该清除缓存', async () => {
      const { useSymbolsCache, cacheReady } = await import('../useOfflineCache')
      const { SymbolsCacheService } = await import('@/services/offlineCache')

      cacheReady.value = true
      const result = useSymbolsCache('forex')
      await result.clearCache()

      expect(SymbolsCacheService.clearCache).toHaveBeenCalledWith('forex')
    })
  })
})

describe('useNetworkStatus', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('网络状态检测', () => {
    it('应该返回网络状态', async () => {
      const { useNetworkStatus } = await import('../useOfflineCache')

      const result = useNetworkStatus()

      expect(result.networkStatus).toBeDefined()
      expect(result.isOnline).toBeDefined()
      expect(result.isOffline).toBeDefined()
    })

    it('isOnline应该是computed属性', async () => {
      const { useNetworkStatus, networkStatus } = await import('../useOfflineCache')

      networkStatus.value = 'online'
      const result = useNetworkStatus()

      expect(result.isOnline.value).toBe(true)
      expect(result.isOffline.value).toBe(false)
    })

    it('isOffline应该是computed属性', async () => {
      const { useNetworkStatus, networkStatus } = await import('../useOfflineCache')

      networkStatus.value = 'offline'
      const result = useNetworkStatus()

      expect(result.isOnline.value).toBe(false)
      expect(result.isOffline.value).toBe(true)
    })
  })
})

describe('useSmartDataLoader', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('智能数据加载', () => {
    it('应该返回数据加载状态', async () => {
      const { useSmartDataLoader, cacheReady, networkStatus } = await import('../useOfflineCache')

      cacheReady.value = true
      networkStatus.value = 'online'

      const fetchFn = vi.fn().mockResolvedValue([{ date: '2026-04-01', close: 7.15 }])
      const result = useSmartDataLoader('test-symbol', 'daily', fetchFn)

      expect(result.data).toBeDefined()
      expect(result.isLoading).toBeDefined()
      expect(result.error).toBeDefined()
      expect(result.dataSource).toBeDefined()
    })

    it('应该提供loadData方法', async () => {
      const { useSmartDataLoader, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const fetchFn = vi.fn().mockResolvedValue([])
      const result = useSmartDataLoader('test-symbol', 'daily', fetchFn)

      expect(result.loadData).toBeDefined()
    })

    it('应该提供forceRefresh方法', async () => {
      const { useSmartDataLoader, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const fetchFn = vi.fn().mockResolvedValue([])
      const result = useSmartDataLoader('test-symbol', 'daily', fetchFn)

      expect(result.forceRefresh).toBeDefined()
    })
  })

  describe('边界值测试', () => {
    it('空symbolId不应该触发加载', async () => {
      const { useSmartDataLoader, cacheReady } = await import('../useOfflineCache')

      cacheReady.value = true
      const fetchFn = vi.fn()
      const result = useSmartDataLoader('', 'daily', fetchFn)

      expect(fetchFn).not.toHaveBeenCalled()
    })

    it('网络错误应该设置error状态', async () => {
      const { useSmartDataLoader, cacheReady, networkStatus } = await import('../useOfflineCache')

      cacheReady.value = true
      networkStatus.value = 'online'

      const fetchFn = vi.fn().mockRejectedValue(new Error('Network error'))
      const result = useSmartDataLoader('test-symbol', 'daily', fetchFn)

      await result.loadData(true)

      expect(result.error.value).toBeDefined()
    })
  })
})