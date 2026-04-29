/**
 * 股票市场工具函数.
 *
 * 提供股票市场识别、涨跌停计算、复权处理等功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

/**
 * 市场类型枚举.
 */
export enum MarketType {
  /** 外汇市场 */
  FOREX = 'forex',
  /** A股普通股票 */
  STOCK_A = 'stock_a',
  /** 科创板 */
  STOCK_KCB = 'stock_kcb',
  /** 创业板 */
  STOCK_CYB = 'stock_cyb',
  /** ST股票 */
  STOCK_ST = 'stock_st',
  /** 北交所 */
  STOCK_BJB = 'stock_bjb'
}

/**
 * 市场配置信息.
 */
export interface MarketConfig {
  /** 市场类型 */
  type: MarketType
  /** 市场名称 */
  name: string
  /** 涨停阈值（百分比） */
  limitUpThreshold: number
  /** 跌停阈值（百分比） */
  limitDownThreshold: number
  /** 价格精度（小数位数） */
  pricePrecision: number
  /** 是否有涨跌停限制 */
  hasLimitUpDown: boolean
  /** 是否需要复权处理 */
  needAdjustment: boolean
  /** 是否24小时交易 */
  is24HourTrading: boolean
}

/**
 * 各市场配置.
 */
export const marketConfigs: Record<MarketType, MarketConfig> = {
  [MarketType.FOREX]: {
    type: MarketType.FOREX,
    name: '外汇',
    limitUpThreshold: 0,
    limitDownThreshold: 0,
    pricePrecision: 4,
    hasLimitUpDown: false,
    needAdjustment: false,
    is24HourTrading: true
  },
  [MarketType.STOCK_A]: {
    type: MarketType.STOCK_A,
    name: 'A股',
    limitUpThreshold: 10,   // 10%
    limitDownThreshold: 10, // 10%
    pricePrecision: 2,
    hasLimitUpDown: true,
    needAdjustment: true,
    is24HourTrading: false
  },
  [MarketType.STOCK_KCB]: {
    type: MarketType.STOCK_KCB,
    name: '科创板',
    limitUpThreshold: 20,   // 20%
    limitDownThreshold: 20, // 20%
    pricePrecision: 2,
    hasLimitUpDown: true,
    needAdjustment: true,
    is24HourTrading: false
  },
  [MarketType.STOCK_CYB]: {
    type: MarketType.STOCK_CYB,
    name: '创业板',
    limitUpThreshold: 20,   // 20%
    limitDownThreshold: 20, // 20%
    pricePrecision: 2,
    hasLimitUpDown: true,
    needAdjustment: true,
    is24HourTrading: false
  },
  [MarketType.STOCK_ST]: {
    type: MarketType.STOCK_ST,
    name: 'ST股',
    limitUpThreshold: 5,    // 5%
    limitDownThreshold: 5,  // 5%
    pricePrecision: 2,
    hasLimitUpDown: true,
    needAdjustment: true,
    is24HourTrading: false
  },
  [MarketType.STOCK_BJB]: {
    type: MarketType.STOCK_BJB,
    name: '北交所',
    limitUpThreshold: 30,   // 30%
    limitDownThreshold: 30, // 30%
    pricePrecision: 2,
    hasLimitUpDown: true,
    needAdjustment: true,
    is24HourTrading: false
  }
}

/**
 * 根据品种代码识别市场类型.
 *
 * @param symbol - 品种代码（如 'EURUSD', '600000', '300001', '688001'）
 * @returns 市场类型
 */
export function identifyMarketType(symbol: string): MarketType {
  if (!symbol) return MarketType.FOREX

  // 清理代码（去除前后缀）
  const cleanSymbol = symbol.toUpperCase().replace(/[^A-Z0-9]/g, '')

  // 外汇判断：通常为6位字母组合如 EURUSD, USDCNY
  if (/^[A-Z]{6}$/.test(cleanSymbol)) {
    return MarketType.FOREX
  }

  // 科创板：688开头
  if (/^688\d{3}$/.test(cleanSymbol)) {
    return MarketType.STOCK_KCB
  }

  // 创业板：300开头
  if (/^300\d{3}$/.test(cleanSymbol)) {
    return MarketType.STOCK_CYB
  }

  // 北交所：8开头或4开头（老三板转板）
  if (/^(8|4)\d{5}$/.test(cleanSymbol)) {
    return MarketType.STOCK_BJB
  }

  // ST股票判断：名称包含ST
  // 注意：这里需要名称来判断，代码无法直接判断ST
  // 默认返回A股，ST判断需要额外逻辑
  if (/^6\d{5}$/.test(cleanSymbol) || /^0\d{5}$/.test(cleanSymbol)) {
    return MarketType.STOCK_A
  }

  // 默认返回外汇
  return MarketType.FOREX
}

/**
 * 根据品种代码和名称识别市场类型.
 *
 * @param symbol - 品种代码
 * @param name - 品种名称（可选）
 * @returns 市场类型
 */
export function identifyMarketTypeByName(symbol: string, name?: string): MarketType {
  // 先根据代码识别基础类型
  let marketType = identifyMarketType(symbol)

  // ST股票特殊判断：名称包含ST
  if (name && /ST/i.test(name)) {
    return MarketType.STOCK_ST
  }

  return marketType
}

/**
 * 获取市场配置.
 *
 * @param marketType - 市场类型
 * @returns 市场配置
 */
export function getMarketConfig(marketType: MarketType): MarketConfig {
  return marketConfigs[marketType] || marketConfigs[MarketType.FOREX]
}

/**
 * 计算涨停价.
 *
 * @param prevClose - 昨日收盘价
 * @param marketType - 市场类型
 * @returns 涨停价
 */
export function calculateLimitUpPrice(prevClose: number, marketType: MarketType): number {
  const config = getMarketConfig(marketType)
  if (!config.hasLimitUpDown) return 0

  const limitUp = prevClose * (1 + config.limitUpThreshold / 100)
  return roundPrice(limitUp, config.pricePrecision)
}

/**
 * 计算跌停价.
 *
 * @param prevClose - 昨日收盘价
 * @param marketType - 市场类型
 * @returns 跌停价
 */
export function calculateLimitDownPrice(prevClose: number, marketType: MarketType): number {
  const config = getMarketConfig(marketType)
  if (!config.hasLimitUpDown) return 0

  const limitDown = prevClose * (1 - config.limitDownThreshold / 100)
  return roundPrice(limitDown, config.pricePrecision)
}

/**
 * 判断是否涨停.
 *
 * @param close - 当前收盘价
 * @param limitUpPrice - 涨停价
 * @param marketType - 市场类型
 * @returns 是否涨停
 */
export function isLimitUp(close: number, limitUpPrice: number, marketType: MarketType): boolean {
  const config = getMarketConfig(marketType)
  if (!config.hasLimitUpDown) return false

  // 允许0.01%的误差（由于价格精度限制）
  const tolerance = 0.0001
  return close >= limitUpPrice - tolerance
}

/**
 * 判断是否跌停.
 *
 * @param close - 当前收盘价
 * @param limitDownPrice - 跌停价
 * @param marketType - 市场类型
 * @returns 是否跌停
 */
export function isLimitDown(close: number, limitDownPrice: number, marketType: MarketType): boolean {
  const config = getMarketConfig(marketType)
  if (!config.hasLimitUpDown) return false

  // 允许0.01%的误差（由于价格精度限制）
  const tolerance = 0.0001
  return close <= limitDownPrice + tolerance
}

/**
 * 价格取整（按精度）.
 *
 * @param price - 价格
 * @param precision - 精度（小数位数）
 * @returns 取整后的价格
 */
export function roundPrice(price: number, precision: number): number {
  const multiplier = Math.pow(10, precision)
  return Math.round(price * multiplier) / multiplier
}

/**
 * 计算涨跌停统计.
 *
 * @param rawData - K线数据数组
 * @param marketType - 市场类型
 * @returns 涨跌停统计信息
 */
export interface LimitUpDownStats {
  /** 涨停次数 */
  limitUpCount: number
  /** 跌停次数 */
  limitDownCount: number
  /** 涨停日期列表 */
  limitUpDates: string[]
  /** 跌停日期列表 */
  limitDownDates: string[]
  /** 涨停占比 */
  limitUpRatio: number
  /** 跌停占比 */
  limitDownRatio: number
}

export function calculateLimitUpDownStats(
  rawData: Array<{ date: string; open: number | string; close: number | string }>,
  marketType: MarketType
): LimitUpDownStats {
  const config = getMarketConfig(marketType)
  if (!config.hasLimitUpDown || !rawData || rawData.length < 2) {
    return {
      limitUpCount: 0,
      limitDownCount: 0,
      limitUpDates: [],
      limitDownDates: [],
      limitUpRatio: 0,
      limitDownRatio: 0
    }
  }

  const limitUpDates: string[] = []
  const limitDownDates: string[] = []

  for (let i = 1; i < rawData.length; i++) {
    const prevClose = parseFloat(rawData[i - 1].close) || 0
    const currClose = parseFloat(rawData[i].close) || 0

    const limitUpPrice = calculateLimitUpPrice(prevClose, marketType)
    const limitDownPrice = calculateLimitDownPrice(prevClose, marketType)

    if (isLimitUp(currClose, limitUpPrice, marketType)) {
      limitUpDates.push(rawData[i].date)
    }

    if (isLimitDown(currClose, limitDownPrice, marketType)) {
      limitDownDates.push(rawData[i].date)
    }
  }

  const total = rawData.length - 1 // 排除第一天

  return {
    limitUpCount: limitUpDates.length,
    limitDownCount: limitDownDates.length,
    limitUpDates,
    limitDownDates,
    limitUpRatio: limitUpDates.length / total,
    limitDownRatio: limitDownDates.length / total
  }
}

/**
 * 复权类型枚举.
 */
export enum AdjustmentType {
  /** 不复权 */
  NONE = 'none',
  /** 前复权 */
  FORWARD = 'forward',
  /** 后复权 */
  BACKWARD = 'backward'
}

/**
 * 复权因子数据结构.
 */
export interface AdjustmentFactor {
  /** 日期 */
  date: string
  /** 复权因子 */
  factor: number
  /** 分红金额 */
  dividend?: number
  /** 送股比例 */
  bonusRatio?: number
  /** 配股比例 */
  splitRatio?: number
}

/**
 * 计算前复权价格.
 *
 * 前复权：当前价格不变，历史价格按复权因子调整
 * 公式：前复权价格 = 原价格 * 累计复权因子
 *
 * @param originalPrice - 原始价格
 * @param cumulativeFactor - 累计复权因子（从当前日期往历史累积）
 * @returns 前复权价格
 */
export function calculateForwardAdjustedPrice(
  originalPrice: number,
  cumulativeFactor: number
): number {
  return originalPrice * cumulativeFactor
}

/**
 * 计算后复权价格.
 *
 * 后复权：历史价格不变，当前价格按复权因子调整
 * 公式：后复权价格 = 原价格 / 累计复权因子
 *
 * @param originalPrice - 原始价格
 * @param cumulativeFactor - 累计复权因子（从历史往当前累积）
 * @returns 后复权价格
 */
export function calculateBackwardAdjustedPrice(
  originalPrice: number,
  cumulativeFactor: number
): number {
  return originalPrice / cumulativeFactor
}

/**
 * 计算单次复权因子.
 *
 * 公式：复权因子 = (原价格 - 分红 + 配股价*配股比例) / 原价格 * (1 + 送股比例 + 配股比例)
 * 简化版：复权因子 = (收盘价 - 分红) / 收盘价 * (1 + 送股比例)
 *
 * @param prevClose - 除权前收盘价
 * @param dividend - 每股分红金额
 * @param bonusRatio - 每股送股比例（如0.1表示10送1）
 * @param splitRatio - 每股配股比例
 * @param splitPrice - 配股价格
 * @returns 复权因子
 */
export function calculateAdjustmentFactor(
  prevClose: number,
  dividend: number = 0,
  bonusRatio: number = 0,
  splitRatio: number = 0,
  splitPrice: number = 0
): number {
  // 简化计算：只考虑分红和送股
  // 复权因子 = (收盘价 - 分红) / (收盘价 * (1 + 送股比例))
  const adjustedClose = prevClose - dividend
  const totalRatio = 1 + bonusRatio

  return adjustedClose / (prevClose * totalRatio)
}

/**
 * 批量计算复权价格.
 *
 * @param rawData - 原始K线数据
 * @param adjustmentFactors - 复权因子列表
 * @param adjustmentType - 复权类型
 * @param precision - 价格精度
 * @returns 复权后的K线数据
 */
export function calculateAdjustedPrices(
  rawData: Array<{
    date: string
    open: number | string
    close: number | string
    high: number | string
    low: number | string
  }>,
  adjustmentFactors: AdjustmentFactor[],
  adjustmentType: AdjustmentType,
  precision: number = 2
): Array<{
  date: string
  open: number
  close: number
  high: number
  low: number
}> {
  if (!rawData || rawData.length === 0) return []
  if (adjustmentType === AdjustmentType.NONE) {
    return rawData.map(item => ({
      date: item.date,
      open: parseFloat(item.open) || 0,
      close: parseFloat(item.close) || 0,
      high: parseFloat(item.high) || 0,
      low: parseFloat(item.low) || 0
    }))
  }

  // 构建日期到复权因子的映射
  const factorMap: Record<string, number> = {}
  for (const af of adjustmentFactors) {
    factorMap[af.date] = af.factor
  }

  // 计算累计复权因子
  const cumulativeFactors: number[] = []
  let cumulativeFactor = 1

  for (let i = rawData.length - 1; i >= 0; i--) {
    const date = rawData[i].date
    if (factorMap[date]) {
      cumulativeFactor *= factorMap[date]
    }
    cumulativeFactors[i] = cumulativeFactor
  }

  // 根据复权类型计算价格
  return rawData.map((item, index) => {
    const factor = cumulativeFactors[index]
    const originalOpen = parseFloat(item.open) || 0
    const originalClose = parseFloat(item.close) || 0
    const originalHigh = parseFloat(item.high) || 0
    const originalLow = parseFloat(item.low) || 0

    if (adjustmentType === AdjustmentType.FORWARD) {
      return {
        date: item.date,
        open: roundPrice(calculateForwardAdjustedPrice(originalOpen, factor), precision),
        close: roundPrice(calculateForwardAdjustedPrice(originalClose, factor), precision),
        high: roundPrice(calculateForwardAdjustedPrice(originalHigh, factor), precision),
        low: roundPrice(calculateForwardAdjustedPrice(originalLow, factor), precision)
      }
    } else {
      return {
        date: item.date,
        open: roundPrice(calculateBackwardAdjustedPrice(originalOpen, factor), precision),
        close: roundPrice(calculateBackwardAdjustedPrice(originalClose, factor), precision),
        high: roundPrice(calculateBackwardAdjustedPrice(originalHigh, factor), precision),
        low: roundPrice(calculateBackwardAdjustedPrice(originalLow, factor), precision)
      }
    }
  })
}

/**
 * 除权除息事件数据结构.
 */
export interface DividendEvent {
  /** 事件日期 */
  eventDate: string
  /** 事件类型（dividend/split/bonus） */
  eventType: 'dividend' | 'split' | 'bonus' | 'dr' | 'dxr'
  /** 每股分红金额 */
  dividendPerShare?: number
  /** 送股比例 */
  bonusPerShare?: number
  /** 配股比例 */
  splitRatio?: number
  /** 复权因子 */
  adjustmentFactor: number
}

/**
 * 生成除权除息标记配置.
 *
 * @param events - 除权除息事件数组
 * @param theme - 主题名称
 * @param rawData - K线数据数组
 * @returns ECharts markPoint配置
 */
export function generateDividendMarkPoints(
  events: DividendEvent[],
  theme: string,
  rawData: Array<{ date: string; high: number | string }>
): any {
  if (!events || events.length === 0) return null

  const dividendColor = theme === 'dark' ? '#faad14' : '#f59e0b'
  const dividendBgColor = theme === 'dark' ? 'rgba(250, 173, 20, 0.15)' : 'rgba(245, 158, 11, 0.1)'

  const data = events.map(event => {
    // 找到对应日期的K线索引
    const index = rawData.findIndex(d => d.date === event.eventDate)
    if (index === -1) return null

    const high = parseFloat(rawData[index]?.high) || 0

    return {
      coord: [index, high],
      symbol: 'pin',
      symbolSize: 30,
      itemStyle: {
        color: dividendColor
      },
      label: {
        show: true,
        formatter: event.eventType === 'dividend' ? 'DR' : event.eventType === 'bonus' ? '送股' : 'DXR',
        color: '#ffffff',
        fontSize: 10,
        fontWeight: 'bold'
      }
    }
  }).filter(Boolean)

  if (data.length === 0) return null

  return {
    data,
    animation: false
  }
}

/**
 * 生成除权除息缺口标记线配置.
 *
 * @param events - 除权除息事件数组
 * @param rawData - K线数据数组
 * @param theme - 主题名称
 * @returns ECharts markLine配置
 */
export function generateDividendMarkLines(
  events: DividendEvent[],
  rawData: Array<{ date: string; high: number | string; low: number | string }>,
  theme: string
): any {
  if (!events || events.length === 0) return null

  const dividendColor = theme === 'dark' ? '#faad14' : '#f59e0b'

  const data = events.map(event => {
    // 找到对应日期的K线索引
    const index = rawData.findIndex(d => d.date === event.eventDate)
    if (index === -1) return null

    // 获取当日最高价和最低价
    const high = parseFloat(rawData[index]?.high) || 0
    const low = parseFloat(rawData[index]?.low) || 0

    return {
      name: `${event.eventDate} ${event.eventType === 'dividend' ? '除息' : '除权'}`,
      xAxis: index,
      yAxis: high,
      lineStyle: {
        type: 'solid',
        width: 2,
        color: dividendColor,
        opacity: 0.6
      },
      label: {
        show: true,
        formatter: event.eventType === 'dividend' ? '除息' : '除权',
        position: 'insideEndTop',
        fontSize: 10,
        color: dividendColor
      }
    }
  }).filter(Boolean)

  if (data.length === 0) return null

  return {
    data,
    animation: false,
    symbol: 'none'
  }
}

/**
 * 检测停牌期间数据缺失.
 *
 * @param rawData - K线数据数组
 * @param tradingDays - 交易日列表（可选）
 * @returns 停牌区间数组
 */
export interface SuspensionPeriod {
  startDate: string
  endDate: string
  days: number
  startIndex: number
  endIndex: number
}

export function detectSuspensionPeriods(
  rawData: Array<{ date: string }>,
  tradingDays?: string[]
): SuspensionPeriod[] {
  if (!rawData || rawData.length < 2) return []

  // 如果没有交易日列表，无法准确检测停牌
  // 简化实现：检测日期间隔超过7天的区域
  const suspensions: SuspensionPeriod[] = []

  // 按日期排序
  const sortedData = [...rawData].sort((a, b) => a.date.localeCompare(b.date))

  for (let i = 1; i < sortedData.length; i++) {
    const prevDate = new Date(sortedData[i - 1].date)
    const currDate = new Date(sortedData[i].date)
    const dayDiff = Math.floor((currDate.getTime() - prevDate.getTime()) / (1000 * 60 * 60 * 24))

    // 如果间隔超过7天，可能为停牌期间
    if (dayDiff > 7) {
      suspensions.push({
        startDate: sortedData[i - 1].date,
        endDate: sortedData[i].date,
        days: dayDiff,
        startIndex: rawData.findIndex(d => d.date === sortedData[i - 1].date),
        endIndex: rawData.findIndex(d => d.date === sortedData[i].date)
      })
    }
  }

  return suspensions
}

/**
 * 生成停牌期间标记配置.
 *
 * @param suspensions - 停牌区间数组
 * @param rawData - K线数据数组
 * @param theme - 主题名称
 * @returns ECharts markArea配置
 */
export function generateSuspensionMarkAreas(
  suspensions: SuspensionPeriod[],
  rawData: Array<{ date: string; high: number | string; low: number | string }>,
  theme: string
): any {
  if (!suspensions || suspensions.length === 0) return null

  const bgColor = theme === 'dark' ? 'rgba(100, 100, 100, 0.2)' : 'rgba(200, 200, 200, 0.2)'
  const borderColor = theme === 'dark' ? '#666666' : '#cccccc'

  const data = suspensions.map(s => {
    // 获取区间内的最高价和最低价
    const rangeData = rawData.slice(s.startIndex, s.endIndex + 1)
    const highs = rangeData.map(d => parseFloat(d.high) || 0)
    const lows = rangeData.map(d => parseFloat(d.low) || 0)
    const maxHeight = Math.max(...highs)
    const minHeight = Math.min(...lows)

    return [
      {
        xAxis: s.startIndex,
        yAxis: maxHeight,
        name: `停牌开始 ${s.startDate}`,
        itemStyle: {
          color: bgColor,
          borderColor: borderColor,
          borderWidth: 1
        }
      },
      {
        xAxis: s.endIndex,
        yAxis: minHeight,
        name: `停牌结束 ${s.endDate}`,
        label: {
          show: true,
          formatter: `停牌${s.days}天`,
          position: 'inside'
        }
      }
    ]
  })

  if (data.length === 0) return null

  return {
    data,
    animation: false
  }
}

// ============================================
// 期货市场专属功能
// ============================================

/**
 * 期货市场类型枚举.
 */
export enum FuturesMarketType {
  /** 中金所股指期货 */
  CFFEX_INDEX = 'cffex_index',
  /** 上期所金属期货 */
  SHFE_METAL = 'shfe_metal',
  /** 大商所农产品期货 */
  DCE_AGRI = 'dce_agri',
  /** 郑商所农产品期货 */
  CZCE_AGRI = 'czce_agri'
}

/**
 * 期货合约信息.
 */
export interface FuturesContract {
  /** 合约代码（如IF2401） */
  contractCode: string
  /** 合约名称 */
  contractName: string
  /** 合约月份标识 */
  contractMonth: string
  /** 合约年份 */
  year: string
  /** 合约月份 */
  month: string
  /** 上市日期 */
  listingDate?: string
  /** 最后交易日/到期日 */
  lastTradeDate: string
  /** 交割日 */
  deliveryDate?: string
  /** 是否为当前主力合约 */
  isMainContract: boolean
  /** 成为主力合约的开始日期 */
  mainStartDate?: string
  /** 作为主力合约的结束日期 */
  mainEndDate?: string
  /** 当前持仓量 */
  openInterest?: number
}

/**
 * 期货品种信息.
 */
export interface FuturesVariety {
  /** 品种代码（如IF、IC） */
  code: string
  /** 品种名称 */
  name: string
  /** 交易所 */
  exchange: string
  /** 合约单位 */
  contractUnit: number
  /** 最小变动价位 */
  minPriceTick: number
  /** 交割方式 */
  deliveryMethod: string
}

/**
 * 期货持仓量数据.
 */
export interface OIData {
  date: string
  open_interest: number
  oi_change?: number
}

/**
 * 计算合约距到期天数.
 *
 * @param lastTradeDate - 最后交易日字符串（YYYY-MM-DD格式）
 * @param currentDate - 当前日期字符串（可选，默认为今天）
 * @returns 距离到期天数（负数表示已到期）
 */
export function calculateDaysToExpiry(
  lastTradeDate: string,
  currentDate?: string
): number {
  const today = currentDate ? new Date(currentDate) : new Date()
  const expiry = new Date(lastTradeDate)

  const diffMs = expiry.getTime() - today.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))

  return diffDays
}

/**
 * 判断合约是否即将到期.
 *
 * @param contract - 合约信息
 * @param warningDays - 提前预警天数
 * @returns 是否即将到期
 */
export function isContractNearExpiry(
  contract: FuturesContract,
  warningDays: number = 5
): boolean {
  const daysToExpiry = calculateDaysToExpiry(contract.lastTradeDate)
  return daysToExpiry > 0 && daysToExpiry <= warningDays
}

/**
 * 判断合约是否已到期.
 *
 * @param contract - 合约信息
 * @returns 是否已到期
 */
export function isContractExpired(contract: FuturesContract): boolean {
  const daysToExpiry = calculateDaysToExpiry(contract.lastTradeDate)
  return daysToExpiry < 0
}

/**
 * 生成合约到期日标记点配置.
 *
 * @param contracts - 合约列表
 * @param rawData - K线数据数组
 * @param theme - 主题名称
 * @param showWarning - 是否显示即将到期警告
 * @returns ECharts markPoint配置
 */
export function generateExpiryMarkPoints(
  contracts: FuturesContract[],
  rawData: Array<{ date: string; high: number | string; low: number | string }>,
  theme: string,
  showWarning: boolean = true
): any {
  if (!contracts || contracts.length === 0) return null

  const expiredColor = theme === 'dark' ? '#ef4444' : '#dc3545'
  const warningColor = theme === 'dark' ? '#f59e0b' : '#ffc107'
  const normalColor = theme === 'dark' ? '#6b7280' : '#9ca3af'

  const data: any[] = []

  for (const contract of contracts) {
    // 找到到期日在K线数据中的位置
    const expiryIndex = rawData.findIndex(d => d.date === contract.lastTradeDate)

    if (expiryIndex === -1) continue

    const high = parseFloat(rawData[expiryIndex]?.high) || 0
    const isExpired = isContractExpired(contract)
    const isNearExpiry = isContractNearExpiry(contract, 5)
    const isMain = contract.isMainContract

    // 只标记主力合约的到期日，或即将到期的合约
    if (!isMain && !isNearExpiry && !isExpired) continue

    let color = normalColor
    let symbolSize = 30
    let label = '到期'

    if (isExpired) {
      color = expiredColor
      label = '已到期'
      symbolSize = 35
    } else if (isNearExpiry && showWarning) {
      color = warningColor
      const daysToExpiry = calculateDaysToExpiry(contract.lastTradeDate)
      label = `${daysToExpiry}天后到期`
      symbolSize = 32
    } else if (isMain) {
      color = theme === 'dark' ? '#3b82f6' : '#2196f3'
      label = '主力到期'
      symbolSize = 28
    }

    data.push({
      coord: [expiryIndex, high],
      symbol: 'pin',
      symbolSize,
      itemStyle: { color },
      label: {
        show: true,
        formatter: label,
        color: '#ffffff',
        fontSize: 10,
        fontWeight: 'bold'
      }
    })
  }

  if (data.length === 0) return null

  return {
    data,
    animation: false
  }
}

/**
 * 生成合约到期日标记线配置.
 *
 * @param contracts - 合约列表
 * @param rawData - K线数据数组
 * @param theme - 主题名称
 * @returns ECharts markLine配置
 */
export function generateExpiryMarkLines(
  contracts: FuturesContract[],
  rawData: Array<{ date: string; high: number | string }>,
  theme: string
): any {
  if (!contracts || contracts.length === 0) return null

  const expiredColor = theme === 'dark' ? '#ef4444' : '#dc3545'
  const mainColor = theme === 'dark' ? '#3b82f6' : '#2196f3'

  const data: any[] = []

  for (const contract of contracts) {
    const expiryIndex = rawData.findIndex(d => d.date === contract.lastTradeDate)

    if (expiryIndex === -1) continue

    const high = parseFloat(rawData[expiryIndex]?.high) || 0
    const isExpired = isContractExpired(contract)
    const isMain = contract.isMainContract

    // 只标记主力合约和已到期合约
    if (!isMain && !isExpired) continue

    const color = isExpired ? expiredColor : mainColor

    data.push({
      name: `${contract.contractCode} 到期日`,
      xAxis: expiryIndex,
      yAxis: high,
      lineStyle: {
        type: 'dashed',
        width: 2,
        color,
        opacity: 0.6
      },
      label: {
        show: true,
        formatter: `${contract.contractCode}到期`,
        position: 'insideEndTop',
        fontSize: 10,
        color
      }
    })
  }

  if (data.length === 0) return null

  return {
    data,
    animation: false,
    symbol: 'none'
  }
}

/**
 * 生成主力合约切换点标记.
 *
 * @param switchPoints - 主力合约切换点列表
 * @param rawData - K线数据数组
 * @param theme - 主题名称
 * @returns ECharts markPoint配置
 */
export interface ContractSwitchPoint {
  switch_date: string
  old_contract_code: string
  new_contract_code: string
  price_diff?: number
}

export function generateMainSwitchMarkPoints(
  switchPoints: ContractSwitchPoint[],
  rawData: Array<{ date: string; high: number | string }>,
  theme: string
): any {
  if (!switchPoints || switchPoints.length === 0) return null

  const switchColor = theme === 'dark' ? '#8b5cf6' : '#9c27b0'

  const data = switchPoints.map(point => {
    const switchIndex = rawData.findIndex(d => d.date === point.switch_date)
    if (switchIndex === -1) return null

    const high = parseFloat(rawData[switchIndex]?.high) || 0

    return {
      coord: [switchIndex, high],
      symbol: 'triangle',
      symbolSize: 20,
      itemStyle: { color: switchColor },
      label: {
        show: true,
        formatter: '主力切换',
        color: '#ffffff',
        fontSize: 9,
        fontWeight: 'bold'
      }
    }
  }).filter(Boolean)

  if (data.length === 0) return null

  return {
    data,
    animation: false
  }
}

/**
 * 格式化持仓量数值显示.
 *
 * @param oi - 持仓量数值
 * @returns 格式化后的字符串
 */
export function formatOpenInterest(oi: number): string {
  if (oi >= 100000000) {
    return `${(oi / 100000000).toFixed(2)}亿手`
  }
  if (oi >= 10000000) {
    return `${(oi / 10000000).toFixed(2)}千万手`
  }
  if (oi >= 10000) {
    return `${(oi / 10000).toFixed(2)}万手`
  }
  return `${oi.toFixed(0)}手`
}

/**
 * 计算持仓量变化率.
 *
 * @param currentOI - 当前持仓量
 * @param previousOI - 上一期持仓量
 * @returns 持仓量变化率（百分比）
 */
export function calculateOIChangeRate(
  currentOI: number,
  previousOI: number
): number {
  if (previousOI === 0) return 0

  return ((currentOI - previousOI) / previousOI) * 100
}

/**
 * 检测持仓量异常变化（超过阈值）.
 *
 * @param oiChangeRate - 持仓量变化率
 * @param threshold - 异常阈值（百分比）
 * @returns 是否异常变化
 */
export function isOIAbnormalChange(
  oiChangeRate: number,
  threshold: number = 20
): boolean {
  return Math.abs(oiChangeRate) >= threshold
}