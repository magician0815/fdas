/**
 * IndexedDB 离线数据缓存服务.
 *
 * 功能：
 * - K线数据本地缓存
 * - 缓存数据版本管理
 * - 缓存过期策略
 * - 数据压缩存储
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

// IndexedDB 配置
const DB_NAME = 'FDAS_Cache'
const DB_VERSION = 1

// 存储对象名称
const STORE_NAMES = {
  KLINE: 'kline_cache',       // K线数据缓存
  SYMBOLS: 'symbols_cache',   // 标的列表缓存
  CONFIG: 'config_cache',     // 配置数据缓存
  META: 'meta_cache'          // 元数据缓存
}

// 缓存配置
const CACHE_CONFIG = {
  // K线数据缓存过期时间（毫秒）
  KLINE_EXPIRE: 24 * 60 * 60 * 1000,  // 24小时
  // 标的列表缓存过期时间
  SYMBOLS_EXPIRE: 7 * 24 * 60 * 60 * 1000,  // 7天
  // 配置数据缓存过期时间
  CONFIG_EXPIRE: 30 * 24 * 60 * 60 * 1000,  // 30天
  // 最大缓存条数
  MAX_KLINE_ENTRIES: 100,  // 最多缓存100个标的的K线数据
  // 单条数据最大条数
  MAX_DATA_POINTS: 5000    // 单条缓存最多5000条K线数据
}

// 缓存数据结构接口
interface CacheEntry<T> {
  key: string
  data: T
  timestamp: number
  expireTime: number
  version: string
  metadata?: Record<string, any>
}

// K线数据缓存结构
interface KLineCacheData {
  symbolId: string
  period: string
  data: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>
  startDate: string
  endDate: string
  count: number
}

// 标的列表缓存结构
interface SymbolsCacheData {
  marketType: string
  symbols: Array<{
    id: string
    code: string
    name: string
  }>
}

// 配置数据缓存结构
interface ConfigCacheData {
  type: string
  key: string
  value: any
}

// 元数据缓存结构
interface MetaCacheData {
  type: string
  lastSyncTime: number
  version: string
}

/**
 * IndexedDB 数据库管理类.
 */
class IndexedDBManager {
  private db: IDBDatabase | null = null
  private initPromise: Promise<IDBDatabase> | null = null

  /**
   * 初始化数据库.
   */
  async init(): Promise<IDBDatabase> {
    // 如果已经初始化，直接返回
    if (this.db) {
      return this.db
    }

    // 如果正在初始化，等待完成
    if (this.initPromise) {
      return this.initPromise
    }

    // 开始初始化
    this.initPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      // 数据库升级（创建存储对象）
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result

        // 创建K线数据存储
        if (!db.objectStoreNames.contains(STORE_NAMES.KLINE)) {
          const klineStore = db.createObjectStore(STORE_NAMES.KLINE, { keyPath: 'key' })
          klineStore.createIndex('symbolId', 'data.symbolId', { unique: false })
          klineStore.createIndex('period', 'data.period', { unique: false })
          klineStore.createIndex('timestamp', 'timestamp', { unique: false })
        }

        // 创建标的列表存储
        if (!db.objectStoreNames.contains(STORE_NAMES.SYMBOLS)) {
          const symbolsStore = db.createObjectStore(STORE_NAMES.SYMBOLS, { keyPath: 'key' })
          symbolsStore.createIndex('marketType', 'data.marketType', { unique: false })
          symbolsStore.createIndex('timestamp', 'timestamp', { unique: false })
        }

        // 创建配置数据存储
        if (!db.objectStoreNames.contains(STORE_NAMES.CONFIG)) {
          const configStore = db.createObjectStore(STORE_NAMES.CONFIG, { keyPath: 'key' })
          configStore.createIndex('type', 'data.type', { unique: false })
        }

        // 创建元数据存储
        if (!db.objectStoreNames.contains(STORE_NAMES.META)) {
          const metaStore = db.createObjectStore(STORE_NAMES.META, { keyPath: 'key' })
          metaStore.createIndex('type', 'data.type', { unique: false })
        }
      }

      // 数据库打开成功
      request.onsuccess = (event) => {
        this.db = (event.target as IDBOpenDBRequest).result
        resolve(this.db)
      }

      // 数据库打开失败
      request.onerror = (event) => {
        reject((event.target as IDBOpenDBRequest).error)
      }
    })

    return this.initPromise
  }

  /**
   * 获取存储对象.
   */
  async getStore(storeName: string, mode: IDBTransactionMode = 'readonly'): Promise<IDBObjectStore> {
    const db = await this.init()
    const transaction = db.transaction(storeName, mode)
    return transaction.objectStore(storeName)
  }

  /**
   * 关闭数据库连接.
   */
  close(): void {
    if (this.db) {
      this.db.close()
      this.db = null
      this.initPromise = null
    }
  }

  /**
   * 删除数据库.
   */
  async deleteDatabase(): Promise<void> {
    this.close()
    return new Promise((resolve, reject) => {
      const request = indexedDB.deleteDatabase(DB_NAME)
      request.onsuccess = () => resolve()
      request.onerror = (event) => reject((event.target as IDBRequest).error)
    })
  }
}

// 全局数据库管理实例
const dbManager = new IndexedDBManager()

/**
 * K线数据缓存服务.
 */
export class KLineCacheService {
  /**
   * 生成缓存键.
   */
  private static generateKey(symbolId: string, period: string): string {
    return `kline_${symbolId}_${period}`
  }

  /**
   * 检查缓存是否存在.
   */
  static async hasCache(symbolId: string, period: string): Promise<boolean> {
    try {
      const key = this.generateKey(symbolId, period)
      const store = await dbManager.getStore(STORE_NAMES.KLINE, 'readonly')

      return new Promise((resolve, reject) => {
        const request = store.get(key)
        request.onsuccess = () => {
          const entry = request.result as CacheEntry<KLineCacheData> | undefined
          if (entry && entry.expireTime > Date.now()) {
            resolve(true)
          } else {
            resolve(false)
          }
        }
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to check cache:', error)
      return false
    }
  }

  /**
   * 获取K线缓存数据.
   */
  static async getCache(symbolId: string, period: string): Promise<KLineCacheData | null> {
    try {
      const key = this.generateKey(symbolId, period)
      const store = await dbManager.getStore(STORE_NAMES.KLINE, 'readonly')

      return new Promise((resolve, reject) => {
        const request = store.get(key)
        request.onsuccess = () => {
          const entry = request.result as CacheEntry<KLineCacheData> | undefined
          if (entry && entry.expireTime > Date.now()) {
            // 检查数据是否过期
            resolve(entry.data)
          } else {
            // 缓存不存在或已过期
            resolve(null)
          }
        }
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to get cache:', error)
      return null
    }
  }

  /**
   * 设置K线缓存数据.
   */
  static async setCache(
    symbolId: string,
    period: string,
    data: KLineCacheData,
    version: string = '1.0'
  ): Promise<void> {
    try {
      const key = this.generateKey(symbolId, period)
      const now = Date.now()
      const expireTime = now + CACHE_CONFIG.KLINE_EXPIRE

      const entry: CacheEntry<KLineCacheData> = {
        key,
        data,
        timestamp: now,
        expireTime,
        version,
        metadata: {
          symbolId,
          period,
          dataCount: data.count,
          startDate: data.startDate,
          endDate: data.endDate
        }
      }

      const store = await dbManager.getStore(STORE_NAMES.KLINE, 'readwrite')

      return new Promise((resolve, reject) => {
        const request = store.put(entry)
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to set cache:', error)
      throw error
    }
  }

  /**
   * 删除K线缓存数据.
   */
  static async deleteCache(symbolId: string, period: string): Promise<void> {
    try {
      const key = this.generateKey(symbolId, period)
      const store = await dbManager.getStore(STORE_NAMES.KLINE, 'readwrite')

      return new Promise((resolve, reject) => {
        const request = store.delete(key)
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to delete cache:', error)
      throw error
    }
  }

  /**
   * 清除所有K线缓存.
   */
  static async clearAllCache(): Promise<void> {
    try {
      const store = await dbManager.getStore(STORE_NAMES.KLINE, 'readwrite')

      return new Promise((resolve, reject) => {
        const request = store.clear()
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to clear all cache:', error)
      throw error
    }
  }

  /**
   * 清除过期缓存.
   */
  static async clearExpiredCache(): Promise<number> {
    try {
      const store = await dbManager.getStore(STORE_NAMES.KLINE, 'readwrite')
      const now = Date.now()
      const index = store.index('timestamp')

      // 使用范围查询获取所有缓存条目
      const allEntries: CacheEntry<KLineCacheData>[] = []

      return new Promise((resolve, reject) => {
        const request = index.openCursor()
        let deletedCount = 0

        request.onsuccess = (event) => {
          const cursor = (event.target as IDBRequest).result
          if (cursor) {
            const entry = cursor.value as CacheEntry<KLineCacheData>
            if (entry.expireTime <= now) {
              // 删除过期缓存
              cursor.delete()
              deletedCount++
            }
            cursor.continue()
          } else {
            // 遍历完成
            resolve(deletedCount)
          }
        }

        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to clear expired cache:', error)
      return 0
    }
  }

  /**
   * 获取缓存统计信息.
   */
  static async getCacheStats(): Promise<{
    totalEntries: number
    totalSize: number
    expiredEntries: number
    symbols: string[]
  }> {
    try {
      const store = await dbManager.getStore(STORE_NAMES.KLINE, 'readonly')
      const now = Date.now()

      return new Promise((resolve, reject) => {
        const request = store.getAll()
        request.onsuccess = () => {
          const entries = request.result as CacheEntry<KLineCacheData>[]
          const expiredEntries = entries.filter(e => e.expireTime <= now)
          const symbols = entries.map(e => e.data.symbolId)

          // 估算缓存大小（近似）
          const totalSize = entries.reduce((size, entry) => {
            return size + JSON.stringify(entry).length * 2  // 每个字符约2字节
          }, 0)

          resolve({
            totalEntries: entries.length,
            totalSize,
            expiredEntries: expiredEntries.length,
            symbols
          })
        }
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to get cache stats:', error)
      return {
        totalEntries: 0,
        totalSize: 0,
        expiredEntries: 0,
        symbols: []
      }
    }
  }

  /**
   * 合并新数据到缓存（增量更新）.
   */
  static async mergeCache(
    symbolId: string,
    period: string,
    newData: KLineCacheData
  ): Promise<void> {
    try {
      const existingCache = await this.getCache(symbolId, period)

      if (!existingCache) {
        // 无缓存，直接设置
        await this.setCache(symbolId, period, newData)
        return
      }

      // 合并数据（去重）
      const existingDates = new Set(existingCache.data.map(d => d.date))
      const mergedData = [...existingCache.data]

      for (const item of newData.data) {
        if (!existingDates.has(item.date)) {
          mergedData.push(item)
        } else {
          // 更新已存在的数据
          const index = mergedData.findIndex(d => d.date === item.date)
          if (index !== -1) {
            mergedData[index] = item
          }
        }
      }

      // 按日期排序
      mergedData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

      // 限制数据条数
      const limitedData = mergedData.slice(-CACHE_CONFIG.MAX_DATA_POINTS)

      // 更新缓存
      const updatedCache: KLineCacheData = {
        symbolId,
        period,
        data: limitedData,
        startDate: limitedData[0]?.date || newData.startDate,
        endDate: limitedData[limitedData.length - 1]?.date || newData.endDate,
        count: limitedData.length
      }

      await this.setCache(symbolId, period, updatedCache)
    } catch (error) {
      console.error('Failed to merge cache:', error)
      throw error
    }
  }
}

/**
 * 标的列表缓存服务.
 */
export class SymbolsCacheService {
  /**
   * 生成缓存键.
   */
  private static generateKey(marketType: string): string {
    return `symbols_${marketType}`
  }

  /**
   * 获取标的列表缓存.
   */
  static async getCache(marketType: string): Promise<SymbolsCacheData | null> {
    try {
      const key = this.generateKey(marketType)
      const store = await dbManager.getStore(STORE_NAMES.SYMBOLS, 'readonly')

      return new Promise((resolve, reject) => {
        const request = store.get(key)
        request.onsuccess = () => {
          const entry = request.result as CacheEntry<SymbolsCacheData> | undefined
          if (entry && entry.expireTime > Date.now()) {
            resolve(entry.data)
          } else {
            resolve(null)
          }
        }
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to get symbols cache:', error)
      return null
    }
  }

  /**
   * 设置标的列表缓存.
   */
  static async setCache(
    marketType: string,
    data: SymbolsCacheData,
    version: string = '1.0'
  ): Promise<void> {
    try {
      const key = this.generateKey(marketType)
      const now = Date.now()
      const expireTime = now + CACHE_CONFIG.SYMBOLS_EXPIRE

      const entry: CacheEntry<SymbolsCacheData> = {
        key,
        data,
        timestamp: now,
        expireTime,
        version
      }

      const store = await dbManager.getStore(STORE_NAMES.SYMBOLS, 'readwrite')

      return new Promise((resolve, reject) => {
        const request = store.put(entry)
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to set symbols cache:', error)
      throw error
    }
  }

  /**
   * 清除标的列表缓存.
   */
  static async clearCache(marketType: string): Promise<void> {
    try {
      const key = this.generateKey(marketType)
      const store = await dbManager.getStore(STORE_NAMES.SYMBOLS, 'readwrite')

      return new Promise((resolve, reject) => {
        const request = store.delete(key)
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to clear symbols cache:', error)
      throw error
    }
  }
}

/**
 * 配置数据缓存服务.
 */
export class ConfigCacheService {
  /**
   * 生成缓存键.
   */
  private static generateKey(type: string, key: string): string {
    return `config_${type}_${key}`
  }

  /**
   * 获取配置缓存.
   */
  static async getCache<T>(type: string, key: string): Promise<T | null> {
    try {
      const cacheKey = this.generateKey(type, key)
      const store = await dbManager.getStore(STORE_NAMES.CONFIG, 'readonly')

      return new Promise((resolve, reject) => {
        const request = store.get(cacheKey)
        request.onsuccess = () => {
          const entry = request.result as CacheEntry<ConfigCacheData> | undefined
          if (entry && entry.expireTime > Date.now()) {
            resolve(entry.data.value as T)
          } else {
            resolve(null)
          }
        }
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to get config cache:', error)
      return null
    }
  }

  /**
   * 设置配置缓存.
   */
  static async setCache<T>(
    type: string,
    key: string,
    value: T,
    version: string = '1.0'
  ): Promise<void> {
    try {
      const cacheKey = this.generateKey(type, key)
      const now = Date.now()
      const expireTime = now + CACHE_CONFIG.CONFIG_EXPIRE

      const entry: CacheEntry<ConfigCacheData> = {
        key: cacheKey,
        data: { type, key, value },
        timestamp: now,
        expireTime,
        version
      }

      const store = await dbManager.getStore(STORE_NAMES.CONFIG, 'readwrite')

      return new Promise((resolve, reject) => {
        const request = store.put(entry)
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to set config cache:', error)
      throw error
    }
  }
}

/**
 * 元数据缓存服务（用于追踪缓存状态）.
 */
export class MetaCacheService {
  /**
   * 获取上次同步时间.
   */
  static async getLastSyncTime(type: string): Promise<number | null> {
    try {
      const key = `meta_${type}`
      const store = await dbManager.getStore(STORE_NAMES.META, 'readonly')

      return new Promise((resolve, reject) => {
        const request = store.get(key)
        request.onsuccess = () => {
          const entry = request.result as CacheEntry<MetaCacheData> | undefined
          if (entry) {
            resolve(entry.data.lastSyncTime)
          } else {
            resolve(null)
          }
        }
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to get last sync time:', error)
      return null
    }
  }

  /**
   * 设置上次同步时间.
   */
  static async setLastSyncTime(type: string, time: number, version: string = '1.0'): Promise<void> {
    try {
      const key = `meta_${type}`
      const now = Date.now()

      const entry: CacheEntry<MetaCacheData> = {
        key,
        data: { type, lastSyncTime: time, version },
        timestamp: now,
        expireTime: now + CACHE_CONFIG.CONFIG_EXPIRE
      }

      const store = await dbManager.getStore(STORE_NAMES.META, 'readwrite')

      return new Promise((resolve, reject) => {
        const request = store.put(entry)
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    } catch (error) {
      console.error('Failed to set last sync time:', error)
      throw error
    }
  }
}

/**
 * 导出统一的缓存管理接口.
 */
export const OfflineCacheService = {
  kline: KLineCacheService,
  symbols: SymbolsCacheService,
  config: ConfigCacheService,
  meta: MetaCacheService,

  /**
   * 初始化缓存服务.
   */
  async init(): Promise<void> {
    await dbManager.init()
    // 清理过期缓存
    await KLineCacheService.clearExpiredCache()
  },

  /**
   * 关闭缓存服务.
   */
  close(): void {
    dbManager.close()
  },

  /**
   * 清除所有缓存.
   */
  async clearAll(): Promise<void> {
    await KLineCacheService.clearAllCache()
    const symbolsStore = await dbManager.getStore(STORE_NAMES.SYMBOLS, 'readwrite')
    const configStore = await dbManager.getStore(STORE_NAMES.CONFIG, 'readwrite')
    const metaStore = await dbManager.getStore(STORE_NAMES.META, 'readwrite')

    await Promise.all([
      new Promise<void>((resolve, reject) => {
        const request = symbolsStore.clear()
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      }),
      new Promise<void>((resolve, reject) => {
        const request = configStore.clear()
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      }),
      new Promise<void>((resolve, reject) => {
        const request = metaStore.clear()
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    ])
  },

  /**
   * 获取缓存状态.
   */
  async getStatus(): Promise<{
    isReady: boolean
    klineStats: any
    lastSyncTimes: Record<string, number>
  }> {
    const klineStats = await KLineCacheService.getCacheStats()

    const lastSyncTimes: Record<string, number> = {}
    const types = ['kline', 'symbols', 'forex']

    for (const type of types) {
      const time = await MetaCacheService.getLastSyncTime(type)
      if (time) {
        lastSyncTimes[type] = time
      }
    }

    return {
      isReady: this.db !== null,
      klineStats,
      lastSyncTimes
    }
  }
}