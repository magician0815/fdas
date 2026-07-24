/**
 * 数据管道 — 将 FastAPI 数据转换为 KLineChart KLineData 格式.
 *
 * 从 PostgreSQL 后端获取数据，转换为 KLineChart 所需的时间戳-价格格式.
 * 支持复权预处理和扩展字段注入（持仓量/收益率/利差）.
 */

import type { KLineData } from 'klinecharts'
import type { MarketProfile } from './useMarketProfile'

// ---- API 响应类型 ----

interface RawDataItem {
  date: string
  open: number | string
  high: number | string
  low: number | string
  close: number | string
  volume?: number | string
  turnover?: number | string
  open_interest?: number
  yield?: number
  yield_rate?: number
  spread?: number
  change_pct?: number
}

// ---- 复权类型 ----

export type AdjustmentType = 'none' | 'forward' | 'backward'

export interface AdjustmentFactor {
  date: string
  factor: number
}

// ---- 核心转换函数 ----

/** 将后端原始数据转换为 KLineChart KLineData 格式 */
export function convertToKLineData(
  rawData: RawDataItem[],
  profile: MarketProfile,
  options?: {
    adjustmentType?: AdjustmentType
    factors?: AdjustmentFactor[]
  }
): KLineData[] {
  let result = rawData.map((item) => ({
    timestamp: new Date(item.date).getTime(),
    open: Number(item.open),
    high: Number(item.high),
    low: Number(item.low),
    close: Number(item.close),
    volume: Number(item.volume ?? 0),
    turnover: Number(item.turnover || 0),
    open_interest: item.open_interest,
    yield: item.yield ?? item.yield_rate,
    spread: item.spread,
    change_pct: Number(item.change_pct || 0),
  }))

  // 复权处理
  if (options?.adjustmentType && options.adjustmentType !== 'none' && options.factors?.length) {
    result = applyAdjustment(result, options.factors, options.adjustmentType, profile.pricePrecision)
  }

  return result
}

/** 复权预处理 — 在数据进入 KLineChart 之前对价格进行调整 */
export function applyAdjustment(
  data: KLineData[],
  factors: AdjustmentFactor[],
  type: AdjustmentType,
  precision: number
): KLineData[] {
  if (type === 'none' || factors.length === 0) return data

  // 构建日期→累积因子的映射
  const factorMap = new Map<number, number>()
  const factorTimestamps = factors
    .map((f) => ({ ts: new Date(f.date).getTime(), factor: f.factor }))
    .sort((a, b) => a.ts - b.ts)

  // 计算每个时间点的累积因子（定期 snap 到 8 位精度防止浮点累积误差）
  let cumulative = 1
  for (const f of factorTimestamps) {
    cumulative = Number((cumulative * f.factor).toFixed(8))
    factorMap.set(f.ts, cumulative)
  }

  const round = (v: number) => Number(v.toFixed(precision))
  const isForward = type === 'forward'

  return data.map((k) => {
    // 找到该数据点之前的累积因子
    let factor = 1
    for (const [ts, f] of factorMap) {
      if (k.timestamp >= ts) factor = f
    }

    if (factor === 1) return k

    const adjFactor = isForward ? factor : (1 / factor)
    return {
      ...k,
      open: round(k.open * adjFactor),
      high: round(k.high * adjFactor),
      low: round(k.low * adjFactor),
      close: round(k.close * adjFactor),
    }
  })
}

/** 构建 KLineChart DataLoader 的 getBars 函数（离线模式） */
export function createDataLoader(data: KLineData[]) {
  // 按时间戳排序
  const sorted = [...data].sort((a, b) => a.timestamp - b.timestamp)

  return {
    getBars: ({ type, timestamp, callback }: {
      type: 'init' | 'forward' | 'backward'
      timestamp?: number
      callback: (data: KLineData[], more?: { forward?: boolean }) => void
    }) => {
      if (sorted.length === 0) {
        callback([])
        return
      }

      if (type === 'init') {
        // 初次加载：返回全部数据
        callback(sorted, { forward: false })
      } else if (type === 'forward' && timestamp) {
        // 向前加载更早数据（这里本地数据只有这么多，返回空）
        callback([])
      } else if (type === 'backward' && timestamp) {
        // 向后加载更新数据
        callback([])
      } else {
        callback(sorted, { forward: false })
      }
    },
  }
}
