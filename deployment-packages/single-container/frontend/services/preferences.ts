/**
 * 用户偏好设置服务.
 *
 * 统一管理用户偏好存储，替代分散的localStorage调用.
 * 使用localStorage存储非敏感的用户偏好数据.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

// 前缀用于区分FDAS偏好与其他localStorage数据
const PREFIX = 'fdas_prefs_'

// 偏好类型定义
interface UserPreferences {
  // 图表偏好
  chartType: 'candle' | 'line'
  visibleMA: string[]
  showRightAxis: boolean
  showGapMarks: boolean
  showLongShadowMarks: boolean
  priceAxisType: 'value' | 'log'

  // 画线工具偏好
  drawingColor: string
  drawingWidth: number
  drawingMagnet: boolean

  // 主题偏好
  theme: 'light' | 'dark'

  // 其他偏好
  lastSymbolId: string
  lastPeriod: string
}

// 默认偏好值
const DEFAULT_PREFERENCES: UserPreferences = {
  chartType: 'candle',
  visibleMA: ['5', '10', '20', '60'],
  showRightAxis: false,
  showGapMarks: true,
  showLongShadowMarks: true,
  priceAxisType: 'value',
  drawingColor: '#FF6B6B',
  drawingWidth: 2,
  drawingMagnet: true,
  theme: 'light',
  lastSymbolId: '',
  lastPeriod: 'daily'
}

/**
 * 用户偏好服务.
 */
export const preferencesService = {
  /**
   * 获取偏好值.
   *
   * @param key - 偏好键名
   * @param defaultValue - 默认值（可选）
   * @returns 偏好值
   */
  get<K extends keyof UserPreferences>(key: K): UserPreferences[K] {
    const storageKey = PREFIX + key
    const storedValue = localStorage.getItem(storageKey)

    if (storedValue === null) {
      return DEFAULT_PREFERENCES[key]
    }

    try {
      // 尝试JSON解析（数组或对象）
      const parsed = JSON.parse(storedValue) as UserPreferences[K]
      return parsed
    } catch {
      // JSON解析失败时：
      // 如果期望值是数组或对象，返回默认值
      const defaultValue = DEFAULT_PREFERENCES[key]
      if (Array.isArray(defaultValue) || typeof defaultValue === 'object') {
        return defaultValue
      }
      // 否则返回字符串值（适用于字符串、布尔、数字等）
      return storedValue as UserPreferences[K]
    }
  },

  /**
   * 设置偏好值.
   *
   * @param key - 偏好键名
   * @param value - 偏好值
   */
  set<K extends keyof UserPreferences>(key: K, value: UserPreferences[K]): void {
    const storageKey = PREFIX + key
    const stringValue = typeof value === 'string' ? value : JSON.stringify(value)
    localStorage.setItem(storageKey, stringValue)
  },

  /**
   * 删除偏好值.
   *
   * @param key - 偏好键名
   */
  remove<K extends keyof UserPreferences>(key: K): void {
    const storageKey = PREFIX + key
    localStorage.removeItem(storageKey)
  },

  /**
   * 获取所有偏好.
   *
   * @returns 所有偏好对象
   */
  getAll(): UserPreferences {
    const prefs: Partial<UserPreferences> = {}

    for (const key of Object.keys(DEFAULT_PREFERENCES) as (keyof UserPreferences)[]) {
      prefs[key] = this.get(key)
    }

    return prefs as UserPreferences
  },

  /**
   * 清除所有偏好.
   */
  clearAll(): void {
    for (const key of Object.keys(DEFAULT_PREFERENCES)) {
      const storageKey = PREFIX + key
      localStorage.removeItem(storageKey)
    }
  },

  /**
   * 批量设置偏好.
   *
   * @param prefs - 偏好对象
   */
  setBatch(prefs: Partial<UserPreferences>): void {
    for (const [key, value] of Object.entries(prefs)) {
      if (value !== undefined) {
        this.set(key as keyof UserPreferences, value as any)
      }
    }
  },

  /**
   * 重置为默认偏好.
   */
  reset(): void {
    this.clearAll()
    this.setBatch(DEFAULT_PREFERENCES)
  }
}

// 导出偏好键名常量（便于其他模块使用）
export const PreferenceKeys = {
  CHART_TYPE: 'chartType',
  VISIBLE_MA: 'visibleMA',
  SHOW_RIGHT_AXIS: 'showRightAxis',
  SHOW_GAP_MARKS: 'showGapMarks',
  SHOW_LONG_SHADOW_MARKS: 'showLongShadowMarks',
  PRICE_AXIS_TYPE: 'priceAxisType',
  DRAWING_COLOR: 'drawingColor',
  DRAWING_WIDTH: 'drawingWidth',
  DRAWING_MAGNET: 'drawingMagnet',
  THEME: 'theme',
  LAST_SYMBOL_ID: 'lastSymbolId',
  LAST_PERIOD: 'lastPeriod'
} as const

// 导出类型
export type { UserPreferences }