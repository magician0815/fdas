/**
 * 市场画像系统 — 声明式定义每个金融市场的特征配置.
 *
 * 借鉴 KLineChart 的扩展注册模式，将市场特性作为配置中心，
 * 驱动 KLineChart 的功能开关和参数设置.
 */

import type { Styles } from 'klinecharts'

// ---- 类型定义 ----

/** 市场唯一标识 */
export type MarketId =
  | 'stock_cn'
  | 'stock_hk'
  | 'stock_us'
  | 'forex'
  | 'futures_cn'
  | 'bond_cn'
  | 'bond_us'

/** 涨跌颜色方向 */
export type ColorDirection = 'red-up-green-down' | 'green-up-red-down'

/** 副图面板槽位 */
export interface SubChartSlot {
  id: 'volume' | 'macd' | 'open_interest' | 'yield' | 'yield_spread'
  indicatorName: string
  defaultVisible: boolean
}

/** 周期选项 */
export interface PeriodOption {
  value: string
  label: string
}

/** 涨跌停子类型 */
export interface LimitUpDownSubType {
  id: string
  name: string
  thresholdPercent: number
  matcher: (code: string, name?: string) => boolean
}

/** 市场画像 */
export interface MarketProfile {
  id: MarketId
  displayName: string
  colorDirection: ColorDirection
  pricePrecision: number
  volumeUnit: string

  features: {
    limitUpDown: boolean
    adjustment: boolean
    openInterest: boolean
    yieldDisplay: boolean
    yieldSpread: boolean
    continuousTrading: boolean
    dividendMarkers: boolean
    suspensionDetection: boolean
    logScale: boolean
    gapDetection: boolean
  }

  limitUpDownSubTypes?: LimitUpDownSubType[]
  subChartSlots: SubChartSlot[]
  defaultIndicators: string[]
  indicatorStrategy: 'client' | 'server'
  periodOptions: PeriodOption[]
  apiNamespace: string
  supportedPeriods: string[]
  defaultBars: number

  identification: {
    priority: number
    matcher: (code: string, name?: string) => boolean
  }

  /** KLineChart 样式覆盖（由 themes.ts 提供运行时映射） */
  getStyles?: (themeId: string) => Styles
}

// ---- 市场预设 ----

const stockCN: MarketProfile = {
  id: 'stock_cn',
  displayName: 'A股',
  colorDirection: 'red-up-green-down',
  pricePrecision: 2,
  volumeUnit: 'shares',
  features: {
    limitUpDown: true,
    adjustment: true,
    openInterest: false,
    yieldDisplay: false,
    yieldSpread: false,
    continuousTrading: false,
    dividendMarkers: true,
    suspensionDetection: true,
    logScale: true,
    gapDetection: true,
  },
  limitUpDownSubTypes: [
    { id: 'stock_a', name: 'A股主板', thresholdPercent: 10, matcher: (c, n) => /^(60[0-9]{4}|00[0-9]{5})$/.test(c) && !/[sS][tT]/.test(n || '') },
    { id: 'stock_cyb', name: '创业板', thresholdPercent: 20, matcher: (c) => /^30[0-9]{4}$/.test(c) },
    { id: 'stock_kcb', name: '科创板', thresholdPercent: 20, matcher: (c) => /^688[0-9]{3}$/.test(c) },
    { id: 'stock_st', name: 'ST股', thresholdPercent: 5, matcher: (_c, n) => /[sS][tT]/.test(n || '') },
    { id: 'stock_bjb', name: '北交所', thresholdPercent: 30, matcher: (c) => /^[84][0-9]{5}$/.test(c) },
  ],
  subChartSlots: [
    { id: 'volume', indicatorName: 'VOL', defaultVisible: true },
    { id: 'macd', indicatorName: 'MACD', defaultVisible: true },
  ],
  defaultIndicators: ['MA', 'VOL', 'MACD'],
  indicatorStrategy: 'client',
  periodOptions: [
    { value: 'daily', label: '日K' },
    { value: 'weekly', label: '周K' },
    { value: 'monthly', label: '月K' },
    { value: '5min', label: '5分钟' },
    { value: '15min', label: '15分钟' },
    { value: '30min', label: '30分钟' },
    { value: '60min', label: '60分钟' },
  ],
  apiNamespace: 'stock_data',
  supportedPeriods: ['daily', 'weekly', 'monthly', '5min', '15min', '30min', '60min'],
  defaultBars: 60,
  identification: {
    priority: 0,
    matcher: (c) => /^(60[0-9]{4}|00[0-9]{5}|30[0-9]{4}|688[0-9]{3}|[84][0-9]{5})$/.test(c),
  },
}

const stockHK: MarketProfile = {
  id: 'stock_hk',
  displayName: '港股',
  colorDirection: 'red-up-green-down',
  pricePrecision: 3,
  volumeUnit: 'shares',
  features: {
    limitUpDown: false,
    adjustment: false,
    openInterest: false,
    yieldDisplay: false,
    yieldSpread: false,
    continuousTrading: false,
    dividendMarkers: true,
    suspensionDetection: true,
    logScale: true,
    gapDetection: true,
  },
  subChartSlots: [
    { id: 'volume', indicatorName: 'VOL', defaultVisible: true },
    { id: 'macd', indicatorName: 'MACD', defaultVisible: true },
  ],
  defaultIndicators: ['MA', 'VOL', 'MACD'],
  indicatorStrategy: 'client',
  periodOptions: [
    { value: 'daily', label: '日K' },
    { value: 'weekly', label: '周K' },
    { value: 'monthly', label: '月K' },
  ],
  apiNamespace: 'stock_data',
  supportedPeriods: ['daily', 'weekly', 'monthly'],
  defaultBars: 60,
  identification: {
    priority: 3,
    matcher: (c) => /^\d{5}\.HK$/.test(c),
  },
}

const stockUS: MarketProfile = {
  id: 'stock_us',
  displayName: '美股',
  colorDirection: 'green-up-red-down',
  pricePrecision: 2,
  volumeUnit: 'shares',
  features: {
    limitUpDown: false,
    adjustment: true,
    openInterest: false,
    yieldDisplay: false,
    yieldSpread: false,
    continuousTrading: false,
    dividendMarkers: true,
    suspensionDetection: false,
    logScale: true,
    gapDetection: true,
  },
  subChartSlots: [
    { id: 'volume', indicatorName: 'VOL', defaultVisible: true },
    { id: 'macd', indicatorName: 'MACD', defaultVisible: true },
  ],
  defaultIndicators: ['MA', 'VOL', 'MACD'],
  indicatorStrategy: 'client',
  periodOptions: [
    { value: 'daily', label: '日K' },
    { value: 'weekly', label: '周K' },
    { value: 'monthly', label: '月K' },
  ],
  apiNamespace: 'stock_data',
  supportedPeriods: ['daily', 'weekly', 'monthly'],
  defaultBars: 60,
  identification: {
    priority: 1,
    matcher: (c) => /^[A-Z]{1,5}$/.test(c) && !c.includes('.'),
  },
}

const forex: MarketProfile = {
  id: 'forex',
  displayName: '外汇',
  colorDirection: 'red-up-green-down',
  pricePrecision: 4,
  volumeUnit: 'none',
  features: {
    limitUpDown: false,
    adjustment: false,
    openInterest: false,
    yieldDisplay: false,
    yieldSpread: false,
    continuousTrading: true,
    dividendMarkers: false,
    suspensionDetection: false,
    logScale: true,
    gapDetection: false,
  },
  subChartSlots: [
    { id: 'macd', indicatorName: 'MACD', defaultVisible: true },
  ],
  defaultIndicators: ['MA', 'MACD'],
  indicatorStrategy: 'server',
  periodOptions: [
    { value: 'daily', label: '日K' },
    { value: 'weekly', label: '周K' },
    { value: 'monthly', label: '月K' },
    { value: '1min', label: '1分钟' },
    { value: '5min', label: '5分钟' },
    { value: '15min', label: '15分钟' },
    { value: '30min', label: '30分钟' },
    { value: '60min', label: '60分钟' },
  ],
  apiNamespace: 'fx_data',
  supportedPeriods: ['daily', 'weekly', 'monthly', '1min', '5min', '15min', '30min', '60min'],
  defaultBars: 100,
  identification: {
    priority: 99,
    matcher: () => true,
  },
}

const futuresCN: MarketProfile = {
  id: 'futures_cn',
  displayName: '国内期货',
  colorDirection: 'red-up-green-down',
  pricePrecision: 0,
  volumeUnit: 'contracts',
  features: {
    limitUpDown: true,
    adjustment: false,
    openInterest: true,
    yieldDisplay: false,
    yieldSpread: false,
    continuousTrading: false,
    dividendMarkers: false,
    suspensionDetection: false,
    logScale: false,
    gapDetection: true,
  },
  limitUpDownSubTypes: [
    { id: 'futures_default', name: '期货默认', thresholdPercent: 10, matcher: () => true },
  ],
  subChartSlots: [
    { id: 'volume', indicatorName: 'VOL', defaultVisible: true },
    { id: 'open_interest', indicatorName: 'OI', defaultVisible: true },
    { id: 'macd', indicatorName: 'MACD', defaultVisible: true },
  ],
  defaultIndicators: ['MA', 'VOL', 'OI', 'MACD'],
  indicatorStrategy: 'client',
  periodOptions: [
    { value: 'daily', label: '日K' },
    { value: 'weekly', label: '周K' },
    { value: 'monthly', label: '月K' },
    { value: '5min', label: '5分钟' },
    { value: '15min', label: '15分钟' },
    { value: '30min', label: '30分钟' },
    { value: '60min', label: '60分钟' },
  ],
  apiNamespace: 'futures_data',
  supportedPeriods: ['daily', 'weekly', 'monthly', '5min', '15min', '30min', '60min'],
  defaultBars: 60,
  identification: {
    priority: 2,
    matcher: (c) => /^[A-Z]{1,2}\d{3,4}$/.test(c),
  },
}

const bondCN: MarketProfile = {
  id: 'bond_cn',
  displayName: '国内债券',
  colorDirection: 'red-up-green-down',
  pricePrecision: 4,
  volumeUnit: 'none',
  features: {
    limitUpDown: false,
    adjustment: false,
    openInterest: false,
    yieldDisplay: true,
    yieldSpread: false,
    continuousTrading: false,
    dividendMarkers: false,
    suspensionDetection: false,
    logScale: false,
    gapDetection: false,
  },
  subChartSlots: [
    { id: 'yield', indicatorName: 'YIELD', defaultVisible: true },
  ],
  defaultIndicators: ['MA', 'YIELD'],
  indicatorStrategy: 'client',
  periodOptions: [
    { value: 'daily', label: '日K' },
    { value: 'weekly', label: '周K' },
    { value: 'monthly', label: '月K' },
  ],
  apiNamespace: 'bond_data',
  supportedPeriods: ['daily', 'weekly', 'monthly'],
  defaultBars: 60,
  identification: {
    priority: 5,
    matcher: (c) => /^\d{6}$/.test(c) && !c.startsWith('6') && !c.startsWith('0') && !c.startsWith('3'),
  },
}

const bondUS: MarketProfile = {
  id: 'bond_us',
  displayName: '美债',
  colorDirection: 'green-up-red-down',
  pricePrecision: 4,
  volumeUnit: 'none',
  features: {
    limitUpDown: false,
    adjustment: false,
    openInterest: false,
    yieldDisplay: true,
    yieldSpread: true,
    continuousTrading: false,
    dividendMarkers: false,
    suspensionDetection: false,
    logScale: false,
    gapDetection: false,
  },
  subChartSlots: [
    { id: 'yield', indicatorName: 'YIELD', defaultVisible: true },
    { id: 'yield_spread', indicatorName: 'YIELD_SPREAD', defaultVisible: true },
  ],
  defaultIndicators: ['MA', 'YIELD', 'YIELD_SPREAD'],
  indicatorStrategy: 'client',
  periodOptions: [
    { value: 'daily', label: '日K' },
    { value: 'weekly', label: '周K' },
    { value: 'monthly', label: '月K' },
  ],
  apiNamespace: 'bond_data',
  supportedPeriods: ['daily', 'weekly', 'monthly'],
  defaultBars: 60,
  identification: {
    priority: 6,
    matcher: (c) => /^US\d{2}Y/i.test(c),
  },
}

// ---- 注册中心 ----

const profiles = new Map<MarketId, MarketProfile>()

/** 注册市场配置 */
export function registerMarketProfile(profile: MarketProfile): void {
  profiles.set(profile.id, profile)
}

/** 按 ID 获取市场配置 */
export function getMarketProfile(id: string): MarketProfile | undefined {
  return profiles.get(id as MarketId)
}

/** 自动识别市场（按优先级匹配） */
export function identifyMarket(code: string, name?: string): MarketProfile {
  const sorted = Array.from(profiles.values())
    .sort((a, b) => a.identification.priority - b.identification.priority)
  for (const profile of sorted) {
    if (profile.identification.matcher(code, name)) {
      return profile
    }
  }
  return profiles.get('forex')!
}

/** 获取所有已注册市场 */
export function getAllMarkets(): MarketProfile[] {
  return Array.from(profiles.values())
}

/** 获取某股票的涨跌停阈值百分比 */
export function getLimitThreshold(
  profile: MarketProfile,
  code: string,
  name?: string
): number {
  if (!profile.features.limitUpDown || !profile.limitUpDownSubTypes) return 0
  for (const subType of profile.limitUpDownSubTypes) {
    if (subType.matcher(code, name)) return subType.thresholdPercent
  }
  return 10
}

// 应用启动时注册所有预设
export function registerMarketPresets(): void {
  registerMarketProfile(stockCN)
  registerMarketProfile(stockHK)
  registerMarketProfile(stockUS)
  registerMarketProfile(forex)
  registerMarketProfile(futuresCN)
  registerMarketProfile(bondCN)
  registerMarketProfile(bondUS)
}
