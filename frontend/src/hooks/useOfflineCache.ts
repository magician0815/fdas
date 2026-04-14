/**
 * 离线数据缓存 Vue Hook.
 *
 * 功能：
 * - 自动缓存K线数据
 * - 缓存状态管理
 * - 网络状态检测
 * - 缓存数据加载
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import {
  OfflineCacheService,
  KLineCacheService,
  SymbolsCacheService,
  KLineCacheData
} from '@/services/offlineCache'

// 网络状态
const networkStatus = ref<'online' | 'offline' | 'unknown'>('unknown')

// 缓存服务状态
const cacheReady = ref(false)

/**
 * 初始化离线缓存Hook.
 */
export function useOfflineCache() {
  const isInitialized = ref(false)
  const cacheStats = ref<{
    totalEntries: number
    totalSize: number
    expiredEntries: number
    symbols: string[]
  } | null>(null)
  const lastSyncTimes = ref<Record<string, number>>({})

  /**
   * 初始化缓存服务.
   */
  const initCache = async () => {
    try {
      await OfflineCacheService.init()
      isInitialized.value = true
      cacheReady.value = true
      // 获取缓存状态
      const status = await OfflineCacheService.getStatus()
      cacheStats.value = status.klineStats
      lastSyncTimes.value = status.lastSyncTimes
    } catch (error) {
      console.error('Failed to initialize offline cache:', error)
      isInitialized.value = false
      cacheReady.value = false
    }
  }

  /**
   * 监听网络状态变化.
   */
  const handleNetworkChange = () => {
    networkStatus.value = navigator.onLine ? 'online' : 'offline'
  }

  /**
   * 清除所有缓存.
   */
  const clearAllCache = async () => {
    try {
      await OfflineCacheService.clearAll()
      // 重新获取状态
      const status = await OfflineCacheService.getStatus()
      cacheStats.value = status.klineStats
      lastSyncTimes.value = status.lastSyncTimes
    } catch (error) {
      console.error('Failed to clear cache:', error)
    }
  }

  /**
   * 清除过期缓存.
   */
  const clearExpiredCache = async () => {
    try {
      const deletedCount = await KLineCacheService.clearExpiredCache()
      // 重新获取状态
      const stats = await KLineCacheService.getCacheStats()
      cacheStats.value = stats
      return deletedCount
    } catch (error) {
      console.error('Failed to clear expired cache:', error)
      return 0
    }
  }

  /**
   * 刷新缓存状态.
   */
  const refreshCacheStats = async () => {
    try {
      const status = await OfflineCacheService.getStatus()
      cacheStats.value = status.klineStats
      lastSyncTimes.value = status.lastSyncTimes
    } catch (error) {
      console.error('Failed to refresh cache stats:', error)
    }
  }

  onMounted(() => {
    initCache()
    // 监听网络状态变化
    window.addEventListener('online', handleNetworkChange)
    window.addEventListener('offline', handleNetworkChange)
    handleNetworkChange()
  })

  onUnmounted(() => {
    window.removeEventListener('online', handleNetworkChange)
    window.removeEventListener('offline', handleNetworkChange)
    OfflineCacheService.close()
  })

  return {
    isInitialized,
    cacheReady,
    cacheStats,
    lastSyncTimes,
    networkStatus,
    initCache,
    clearAllCache,
    clearExpiredCache,
    refreshCacheStats
  }
}

/**
 * K线数据缓存Hook.
 */
export function useKLineCache(symbolId: string, period: string = 'daily') {
  const cacheData = ref<KLineCacheData | null>(null)
  const hasCache = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 加载缓存数据.
   */
  const loadCache = async () => {
    if (!symbolId || !cacheReady.value) return

    isLoading.value = true
    error.value = null

    try {
      // 检查缓存是否存在
      hasCache.value = await KLineCacheService.hasCache(symbolId, period)

      if (hasCache.value) {
        cacheData.value = await KLineCacheService.getCache(symbolId, period)
      } else {
        cacheData.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载缓存失败'
      console.error('Failed to load cache:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 保存数据到缓存.
   */
  const saveCache = async (data: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>) => {
    if (!symbolId || !cacheReady.value || !data.length) return

    isLoading.value = true
    error.value = null

    try {
      const cacheDataToSave: KLineCacheData = {
        symbolId,
        period,
        data,
        startDate: data[0].date,
        endDate: data[data.length - 1].date,
        count: data.length
      }

      await KLineCacheService.setCache(symbolId, period, cacheDataToSave)
      cacheData.value = cacheDataToSave
      hasCache.value = true

      // 更新同步时间
      await OfflineCacheService.meta.setLastSyncTime('kline', Date.now())
    } catch (err) {
      error.value = err instanceof Error ? err.message : '保存缓存失败'
      console.error('Failed to save cache:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 合并新数据到缓存（增量更新）.
   */
  const mergeCache = async (newData: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>) => {
    if (!symbolId || !cacheReady.value || !newData.length) return

    isLoading.value = true
    error.value = null

    try {
      const cacheDataToMerge: KLineCacheData = {
        symbolId,
        period,
        data: newData,
        startDate: newData[0].date,
        endDate: newData[newData.length - 1].date,
        count: newData.length
      }

      await KLineCacheService.mergeCache(symbolId, period, cacheDataToMerge)

      // 重新加载缓存数据
      cacheData.value = await KLineCacheService.getCache(symbolId, period)
      hasCache.value = true

      // 更新同步时间
      await OfflineCacheService.meta.setLastSyncTime('kline', Date.now())
    } catch (err) {
      error.value = err instanceof Error ? err.message : '合并缓存失败'
      console.error('Failed to merge cache:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 删除缓存.
   */
  const deleteCache = async () => {
    if (!symbolId || !cacheReady.value) return

    try {
      await KLineCacheService.deleteCache(symbolId, period)
      cacheData.value = null
      hasCache.value = false
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除缓存失败'
      console.error('Failed to delete cache:', err)
    }
  }

  /**
   * 检查缓存是否需要更新（根据过期时间）.
   */
  const needsUpdate = async (): Promise<boolean> => {
    if (!hasCache.value) return true

    // 检查缓存是否过期
    const exists = await KLineCacheService.hasCache(symbolId, period)
    return !exists
  }

  // 监听symbolId和period变化，自动加载缓存
  watch([symbolId, period], () => {
    if (symbolId && cacheReady.value) {
      loadCache()
    }
  })

  return {
    cacheData,
    hasCache,
    isLoading,
    error,
    loadCache,
    saveCache,
    mergeCache,
    deleteCache,
    needsUpdate
  }
}

/**
 * 标的列表缓存Hook.
 */
export function useSymbolsCache(marketType: string) {
  const cacheData = ref<{
    marketType: string
    symbols: Array<{ id: string; code: string; name: string }>
  } | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 加载标的列表缓存.
   */
  const loadCache = async () => {
    if (!marketType || !cacheReady.value) return

    isLoading.value = true
    error.value = null

    try {
      cacheData.value = await SymbolsCacheService.getCache(marketType)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载缓存失败'
      console.error('Failed to load symbols cache:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 保存标的列表缓存.
   */
  const saveCache = async (symbols: Array<{ id: string; code: string; name: string }>) => {
    if (!marketType || !cacheReady.value || !symbols.length) return

    isLoading.value = true
    error.value = null

    try {
      const data = { marketType, symbols }
      await SymbolsCacheService.setCache(marketType, data)
      cacheData.value = data

      // 更新同步时间
      await OfflineCacheService.meta.setLastSyncTime('symbols', Date.now())
    } catch (err) {
      error.value = err instanceof Error ? err.message : '保存缓存失败'
      console.error('Failed to save symbols cache:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 清除标的列表缓存.
   */
  const clearCache = async () => {
    if (!marketType || !cacheReady.value) return

    try {
      await SymbolsCacheService.clearCache(marketType)
      cacheData.value = null
    } catch (err) {
      error.value = err instanceof Error ? err.message : '清除缓存失败'
      console.error('Failed to clear symbols cache:', err)
    }
  }

  // 监听marketType变化，自动加载缓存
  watch(marketType, () => {
    if (marketType && cacheReady.value) {
      loadCache()
    }
  })

  return {
    cacheData,
    isLoading,
    error,
    loadCache,
    saveCache,
    clearCache
  }
}

/**
 * 网络状态检测Hook.
 */
export function useNetworkStatus() {
  const isOnline = computed(() => networkStatus.value === 'online')
  const isOffline = computed(() => networkStatus.value === 'offline')

  /**
   * 监听网络状态变化.
   */
  const handleNetworkChange = () => {
    networkStatus.value = navigator.onLine ? 'online' : 'offline'
  }

  onMounted(() => {
    window.addEventListener('online', handleNetworkChange)
    window.addEventListener('offline', handleNetworkChange)
    handleNetworkChange()
  })

  onUnmounted(() => {
    window.removeEventListener('online', handleNetworkChange)
    window.removeEventListener('offline', handleNetworkChange)
  })

  return {
    networkStatus,
    isOnline,
    isOffline
  }
}

/**
 * 智能数据加载Hook（结合缓存和网络）.
 */
export function useSmartDataLoader<T>(
  symbolId: string,
  period: string,
  fetchFn: () => Promise<T>,
  options?: {
    preferCache?: boolean
    cacheExpireTime?: number
  }
) {
  const {
    preferCache = true,
    cacheExpireTime
  } = options || {}

  const data = ref<T | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const dataSource = ref<'cache' | 'network' | 'unknown'>('unknown')
  const lastUpdateTime = ref<number | null>(null)

  const { cacheData, hasCache, saveCache, needsUpdate } = useKLineCache(symbolId, period)
  const { isOnline, isOffline } = useNetworkStatus()

  /**
   * 加载数据.
   */
  const loadData = async (forceRefresh = false) => {
    if (!symbolId) return

    isLoading.value = true
    error.value = null

    try {
      // 策略1: 优先使用缓存（离线或偏好缓存）
      if (!forceRefresh && (isOffline.value || preferCache)) {
        await needsUpdate()

        if (hasCache.value) {
          data.value = cacheData.value?.data as T
          dataSource.value = 'cache'
          lastUpdateTime.value = cacheData.value?.timestamp || null
          isLoading.value = false
          return
        }
      }

      // 策略2: 从网络获取数据
      if (isOnline.value) {
        const networkData = await fetchFn()
        data.value = networkData
        dataSource.value = 'network'
        lastUpdateTime.value = Date.now()

        // 保存到缓存
        if (networkData && Array.isArray(networkData)) {
          await saveCache(networkData as any)
        }

        isLoading.value = false
        return
      }

      // 策略3: 离线时尝试使用旧缓存
      if (isOffline.value && hasCache.value) {
        data.value = cacheData.value?.data as T
        dataSource.value = 'cache'
        lastUpdateTime.value = cacheData.value?.timestamp || null
        isLoading.value = false
        return
      }

      // 无法获取数据
      error.value = '无法获取数据：离线状态且无缓存数据'
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载数据失败'
      console.error('Failed to load data:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 强制刷新数据.
   */
  const forceRefresh = async () => {
    await loadData(true)
  }

  // 自动加载
  watch([symbolId, period], () => {
    if (symbolId) {
      loadData()
    }
  })

  return {
    data,
    isLoading,
    error,
    dataSource,
    lastUpdateTime,
    loadData,
    forceRefresh,
    isOnline,
    isOffline
  }
}

/**
 * 导出所有Hook.
 */
export {
  networkStatus,
  cacheReady
}