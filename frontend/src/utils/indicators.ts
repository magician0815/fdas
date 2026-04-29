/**
 * 客户端技术指标计算工具.
 *
 * 从原始K线数据计算 MA/MACD/VOL 指标.
 * 数据格式与ProChart组件期望的props格式一致.
 */

export interface KLineRecord {
  date: string
  open: number | string
  close: number | string
  high: number | string
  low: number | string
  volume?: number | string
  change_pct?: number | string
  amplitude?: number | string
}

export interface MAResult {
  [key: string]: Array<{ value: number | null }>
}

export interface MACDResult {
  dif: (number | null)[]
  dea: (number | null)[]
  macd: (number | null)[]
}

export interface VOLResult {
  [key: string]: Array<{ value: number | null }>
}

/**
 * 计算简单移动平均线(SMA).
 * 前N-1个数据点填充null.
 */
function sma(values: number[], period: number): (number | null)[] {
  const result: (number | null)[] = []
  let sum = 0
  for (let i = 0; i < values.length; i++) {
    sum += values[i]
    if (i < period - 1) {
      result.push(null)
    } else {
      if (i >= period) {
        sum -= values[i - period]
      }
      result.push(sum / period)
    }
  }
  return result
}

/**
 * 计算指数移动平均线(EMA).
 */
function ema(values: number[], period: number): (number | null)[] {
  const result: (number | null)[] = []
  const multiplier = 2 / (period + 1)
  for (let i = 0; i < values.length; i++) {
    if (i === 0) {
      result.push(values[0])
    } else if (i < period - 1) {
      result.push(null)
    } else if (i === period - 1) {
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += values[j]
      }
      result.push(sum / period)
    } else {
      const prev = result[i - 1]!
      result.push((values[i] - prev) * multiplier + prev)
    }
  }
  return result
}

/**
 * 从K线数据提取数值数组.
 */
function extractValues(data: KLineRecord[], field: keyof KLineRecord): number[] {
  return data.map(d => {
    const v = d[field]
    if (typeof v === 'number') return v
    if (typeof v === 'string') return parseFloat(v)
    return 0
  })
}

/**
 * 计算多周期MA指标.
 *
 * @param data - 原始K线数据
 * @param periods - MA周期数组，如 ['5', '10', '20', '60']
 * @returns 格式: { ma5: [{value: ...}], ma10: [{value: ...}], ... }
 */
export function calculateMA(data: KLineRecord[], periods: string[]): MAResult {
  const result: MAResult = {}
  if (!data.length) return result

  const closes = extractValues(data, 'close')

  for (const period of periods) {
    const p = parseInt(period)
    if (isNaN(p) || p <= 0) continue

    const values = sma(closes, p)
    result[`ma${period}`] = values.map(v => ({ value: v }))
  }

  return result
}

/**
 * 计算MACD指标.
 *
 * @param data - 原始K线数据
 * @param fast - 快线周期，默认12
 * @param slow - 慢线周期，默认26
 * @param signal - 信号线周期，默认9
 * @returns { dif, dea, macd } 数组，前N-1个位置为null
 */
export function calculateMACD(
  data: KLineRecord[],
  fast: number = 12,
  slow: number = 26,
  signal: number = 9
): MACDResult {
  if (!data.length) {
    return { dif: [], dea: [], macd: [] }
  }

  const closes = extractValues(data, 'close')
  const fastEMA = ema(closes, fast)
  const slowEMA = ema(closes, slow)

  const dif: (number | null)[] = []
  for (let i = 0; i < closes.length; i++) {
    if (fastEMA[i] == null || slowEMA[i] == null) {
      dif.push(null)
    } else {
      dif.push(fastEMA[i]! - slowEMA[i]!)
    }
  }

  const validDif = dif.filter(v => v != null) as number[]
  const deaRaw = ema(validDif, signal)
  const dea: (number | null)[] = []
  let deaI = 0
  for (let i = 0; i < dif.length; i++) {
    if (dif[i] == null) {
      dea.push(null)
    } else {
      dea.push(deaRaw[deaI++])
    }
  }

  const macd: (number | null)[] = []
  for (let i = 0; i < dif.length; i++) {
    if (dif[i] == null || dea[i] == null) {
      macd.push(null)
    } else {
      macd.push(2 * (dif[i]! - dea[i]!))
    }
  }

  return { dif, dea, macd }
}

/**
 * 计算成交量均线.
 *
 * @param data - 原始K线数据（需包含volume字段）
 * @param periods - VOL周期数组，如 ['5', '10']
 * @returns 格式: { vol5: [{value: ...}], vol10: [{value: ...}], ... }
 */
export function calculateVOL(data: KLineRecord[], periods: string[]): VOLResult {
  const result: VOLResult = {}
  if (!data.length) return result

  const volumes = extractValues(data, 'volume')

  for (const period of periods) {
    const p = parseInt(period)
    if (isNaN(p) || p <= 0) continue

    const values = sma(volumes, p)
    result[`vol${period}`] = values.map(v => ({ value: v }))
  }

  return result
}

/**
 * 一次性计算所有指标.
 */
export function calculateAllIndicators(
  data: KLineRecord[],
  maPeriods: string[] = ['5', '10', '20', '60'],
  macdParams: { fast: number; slow: number; signal: number } = { fast: 12, slow: 26, signal: 9 },
  volPeriods: string[] = ['5', '10']
): {
  ma: MAResult
  macd: MACDResult
  vol: VOLResult
} {
  return {
    ma: calculateMA(data, maPeriods),
    macd: calculateMACD(data, macdParams.fast, macdParams.slow, macdParams.signal),
    vol: calculateVOL(data, volPeriods)
  }
}
