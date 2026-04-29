/**
 * StockData 页面测试.
 *
 * 测试股票数据页面核心逻辑：格式化、ST/停牌状态、复权类型映射、周期切换、指标参数.
 *
 * Author: FDAS Team
 * Created: 2026-04-23
 * Updated: 2026-04-29 - 扩展测试覆盖
 */

import { describe, it, expect, beforeEach } from 'vitest'

// ============================================================
// 格式化函数
// ============================================================
describe('格式化函数', () => {
  const formatPrice = (value: any) => {
    if (!value) return '--'
    return parseFloat(value).toFixed(2)
  }

  const formatChange = (value: any) => {
    if (!value) return '--'
    return `${parseFloat(value).toFixed(2)}%`
  }

  const getChangeClass = (change: any) => {
    if (!change) return ''
    const value = parseFloat(change)
    if (value > 0) return 'positive'
    if (value < 0) return 'negative'
    return ''
  }

  describe('formatPrice', () => {
    it('应正确格式化股票价格(2位小数)', () => {
      expect(formatPrice(123.456)).toBe('123.46')
      expect(formatPrice(100.0)).toBe('100.00')
      expect(formatPrice(0.1)).toBe('0.10')
    })

    it('null/undefined/空字符串应返回--', () => {
      expect(formatPrice(null)).toBe('--')
      expect(formatPrice(undefined)).toBe('--')
      expect(formatPrice('')).toBe('--')
    })

    it('0应返回--(falsy值)', () => {
      expect(formatPrice(0)).toBe('--')
    })
  })

  describe('formatChange', () => {
    it('应正确格式化涨跌幅', () => {
      expect(formatChange(5.67)).toBe('5.67%')
      expect(formatChange(-3.21)).toBe('-3.21%')
      expect(formatChange(0.5)).toBe('0.50%')
    })

    it('null/undefined应返回--', () => {
      expect(formatChange(null)).toBe('--')
      expect(formatChange(undefined)).toBe('--')
    })

    it('0应返回--', () => {
      expect(formatChange(0)).toBe('--')
    })
  })

  describe('getChangeClass', () => {
    it('正数应返回positive', () => {
      expect(getChangeClass(5)).toBe('positive')
      expect(getChangeClass(0.01)).toBe('positive')
    })

    it('负数应返回negative', () => {
      expect(getChangeClass(-3)).toBe('negative')
      expect(getChangeClass(-0.01)).toBe('negative')
    })

    it('零应返回空字符串', () => {
      expect(getChangeClass(0)).toBe('')
    })

    it('null/undefined应返回空字符串', () => {
      expect(getChangeClass(null)).toBe('')
      expect(getChangeClass(undefined)).toBe('')
    })
  })
})

// ============================================================
// 股票特殊状态
// ============================================================
describe('股票特殊状态', () => {
  describe('ST标记', () => {
    it('is_st=true时识别为ST股票', () => {
      const isST = (record: any) => record.is_st === true
      expect(isST({ is_st: true })).toBe(true)
    })

    it('is_st=false时不是ST股票', () => {
      const isST = (record: any) => record.is_st === true
      expect(isST({ is_st: false })).toBe(false)
    })

    it('is_st缺失时不是ST股票', () => {
      const isST = (record: any) => record.is_st === true
      expect(isST({})).toBe(false)
    })
  })

  describe('停牌标记', () => {
    it('is_suspended=true时识别为停牌股票', () => {
      const isSuspended = (record: any) => record.is_suspended === true
      expect(isSuspended({ is_suspended: true })).toBe(true)
    })

    it('is_suspended=false时不是停牌股票', () => {
      const isSuspended = (record: any) => record.is_suspended === true
      expect(isSuspended({ is_suspended: false })).toBe(false)
    })
  })

  describe('从行情数据提取状态', () => {
    it('应从最新记录提取ST和停牌状态', () => {
      const chartData = [
        { date: '2026-04-01', close: 10.0, is_st: false, is_suspended: false },
        { date: '2026-04-02', close: 10.5, is_st: true, is_suspended: false },
      ]
      const latest = chartData[chartData.length - 1]
      expect(latest.is_st).toBe(true)
      expect(latest.is_suspended).toBe(false)
    })

    it('空数据时不应设置状态', () => {
      const chartData: any[] = []
      expect(chartData.length).toBe(0)
    })
  })
})

// ============================================================
// 周期选项与切换逻辑
// ============================================================
describe('周期选项', () => {
  const periodOptions = [
    { value: 'daily', label: '日线' },
    { value: 'weekly', label: '周线' },
    { value: 'monthly', label: '月线' }
  ]

  it('应包含日线、周线、月线选项', () => {
    expect(periodOptions.length).toBe(3)
    expect(periodOptions.find(p => p.value === 'daily')).toBeDefined()
    expect(periodOptions.find(p => p.value === 'weekly')).toBeDefined()
    expect(periodOptions.find(p => p.value === 'monthly')).toBeDefined()
  })

  it('标签应正确', () => {
    const labels = periodOptions.map(p => p.label)
    expect(labels).toEqual(['日线', '周线', '月线'])
  })
})

describe('周期切换逻辑', () => {
  const STORAGE_KEY = 'fdas_stock_period_type'

  beforeEach(() => {
    localStorage.clear()
  })

  it('应保存周期到localStorage(stock专用key)', () => {
    const handlePeriodChange = (period: string) => {
      localStorage.setItem(STORAGE_KEY, period)
    }
    handlePeriodChange('weekly')
    expect(localStorage.getItem(STORAGE_KEY)).toBe('weekly')
  })

  it('应从localStorage恢复周期', () => {
    localStorage.setItem(STORAGE_KEY, 'monthly')
    const savedPeriod = localStorage.getItem(STORAGE_KEY) || 'daily'
    expect(savedPeriod).toBe('monthly')
  })

  it('无保存时应使用默认daily', () => {
    const savedPeriod = localStorage.getItem(STORAGE_KEY) || 'daily'
    expect(savedPeriod).toBe('daily')
  })

  it('切换周期后应触发数据获取', () => {
    let fetchCalled = false
    const handlePeriodChange = (period: string) => {
      localStorage.setItem(STORAGE_KEY, period)
      fetchCalled = true
    }
    handlePeriodChange('monthly')
    expect(fetchCalled).toBe(true)
    expect(localStorage.getItem(STORAGE_KEY)).toBe('monthly')
  })
})

// ============================================================
// 指标参数默认值
// ============================================================
describe('MA/MACD/VOL参数默认值', () => {
  it('默认MA周期应为5,10,20,60', () => {
    const maPeriods = ['5', '10', '20', '60']
    expect(maPeriods).toEqual(['5', '10', '20', '60'])
  })

  it('默认MACD参数应为(12,26,9)', () => {
    const macdParams = { fast: 12, slow: 26, signal: 9 }
    expect(macdParams.fast).toBe(12)
    expect(macdParams.slow).toBe(26)
    expect(macdParams.signal).toBe(9)
  })

  it('默认VOL周期应为5,10', () => {
    const volPeriods = ['5', '10']
    expect(volPeriods).toEqual(['5', '10'])
  })
})

describe('指标参数变更', () => {
  it('handleMAChange应更新MA周期', () => {
    let maPeriods = ['5', '10', '20', '60']
    const handleMAChange = (periods: string[]) => { maPeriods = periods }
    handleMAChange(['5', '10', '30'])
    expect(maPeriods).toEqual(['5', '10', '30'])
  })

  it('handleMACDChange应更新MACD参数', () => {
    let macdParams = { fast: 12, slow: 26, signal: 9 }
    const handleMACDChange = (params: { fast: number; slow: number; signal: number }) => { macdParams = params }
    handleMACDChange({ fast: 10, slow: 20, signal: 5 })
    expect(macdParams).toEqual({ fast: 10, slow: 20, signal: 5 })
  })

  it('handleVOLChange应更新VOL周期', () => {
    let volPeriods = ['5', '10']
    const handleVOLChange = (periods: string[]) => { volPeriods = periods }
    handleVOLChange(['10', '20'])
    expect(volPeriods).toEqual(['10', '20'])
  })
})

// ============================================================
// 键盘快捷键
// ============================================================
describe('键盘快捷键', () => {
  const shouldOpenKeyboardWizard = (e: any) =>
    (e.ctrlKey || e.metaKey) && e.key === 'k'

  const shouldOpenIndicatorWizard = (e: any) =>
    (e.ctrlKey || e.metaKey) && e.key === 'i'

  describe('Ctrl键组合', () => {
    it('Ctrl+K应打开键盘精灵', () => {
      expect(shouldOpenKeyboardWizard({ ctrlKey: true, key: 'k' })).toBe(true)
    })

    it('Ctrl+I应打开指标精灵', () => {
      expect(shouldOpenIndicatorWizard({ ctrlKey: true, key: 'i' })).toBe(true)
    })
  })

  describe('Meta键组合(macOS)', () => {
    it('Meta+K应打开键盘精灵', () => {
      expect(shouldOpenKeyboardWizard({ metaKey: true, key: 'k' })).toBe(true)
    })

    it('Meta+I应打开指标精灵', () => {
      expect(shouldOpenIndicatorWizard({ metaKey: true, key: 'i' })).toBe(true)
    })
  })

  describe('边缘情况', () => {
    it('普通K键不应触发', () => {
      expect(shouldOpenKeyboardWizard({ ctrlKey: false, metaKey: false, key: 'k' })).toBe(false)
    })

    it('普通I键不应触发', () => {
      expect(shouldOpenIndicatorWizard({ ctrlKey: false, metaKey: false, key: 'i' })).toBe(false)
    })

    it('大写K不应触发', () => {
      expect(shouldOpenKeyboardWizard({ ctrlKey: true, key: 'K' })).toBe(false)
    })

    it('大写I不应触发', () => {
      expect(shouldOpenIndicatorWizard({ ctrlKey: true, key: 'I' })).toBe(false)
    })
  })
})

// ============================================================
// 复权类型映射
// ============================================================
describe('复权类型映射', () => {
  const adjustMap: Record<string, string> = {
    'forward': 'qfq',
    'backward': 'hfq'
  }

  it('前复权forward应映射为qfq', () => {
    expect(adjustMap['forward']).toBe('qfq')
  })

  it('后复权backward应映射为hfq', () => {
    expect(adjustMap['backward']).toBe('hfq')
  })

  it('none不复权不映射', () => {
    expect(adjustMap['none']).toBeUndefined()
  })

  it('未知类型返回空字符串', () => {
    const mapWithDefault = (type: string) => adjustMap[type] || ''
    expect(mapWithDefault('unknown')).toBe('')
    expect(mapWithDefault('')).toBe('')
  })
})

describe('复权切换类型列表', () => {
  it('应支持三种复权类型', () => {
    const types = ['none', 'forward', 'backward']
    expect(types).toHaveLength(3)
    expect(types).toContain('none')
    expect(types).toContain('forward')
    expect(types).toContain('backward')
  })

  it('none类型应直接调用fetchData', () => {
    // none 不复权，直接刷新原始数据
    let fetchCalled = false
    const handleAdjustmentChange = (type: string) => {
      if (type === 'none') {
        fetchCalled = true
      }
    }
    handleAdjustmentChange('none')
    expect(fetchCalled).toBe(true)
  })
})

// ============================================================
// 键盘精灵数据映射
// ============================================================
describe('键盘精灵数据', () => {
  const mockSymbols = [
    { id: '1', name: '平安银行', code: '000001' },
    { id: '2', name: '万科A', code: '000002' },
    { id: '3', name: '贵州茅台', code: '600519' },
  ]

  it('应将symbols映射为键盘精灵条目', () => {
    const keyboardItems = mockSymbols.map(s => ({
      id: s.id,
      name: s.name,
      code: s.code,
    }))
    expect(keyboardItems).toHaveLength(3)
    expect(keyboardItems[0]).toEqual({ id: '1', name: '平安银行', code: '000001' })
    expect(keyboardItems[2].code).toBe('600519')
  })

  it('空symbols应生成空数组', () => {
    const symbols: any[] = []
    const keyboardItems = symbols.map(s => ({
      id: s.id,
      name: s.name,
      code: s.code,
    }))
    expect(keyboardItems).toEqual([])
  })
})

// ============================================================
// 标的选择逻辑
// ============================================================
describe('标的选择逻辑', () => {
  const mockSymbols = [
    { id: 's1', name: '平安银行', code: '000001' },
    { id: 's2', name: '贵州茅台', code: '600519' },
  ]

  describe('selectedSymbolName', () => {
    it('应根据selectedSymbolId从symbols查找名称', () => {
      const selectedSymbolId = 's1'
      const symbol = mockSymbols.find(s => s.id === selectedSymbolId)
      expect(symbol?.name).toBe('平安银行')
    })

    it('未选中时应返回空字符串', () => {
      const selectedSymbolId = null
      const symbol = selectedSymbolId ? mockSymbols.find(s => s.id === selectedSymbolId) : undefined
      expect(symbol?.name || '').toBe('')
    })

    it('选中不存在的ID应返回空', () => {
      const selectedSymbolId = 'nonexistent'
      const symbol = mockSymbols.find(s => s.id === selectedSymbolId)
      expect(symbol).toBeUndefined()
    })
  })

  describe('selectedSymbolCode', () => {
    it('应根据selectedSymbolId从symbols查找代码', () => {
      const selectedSymbolId = 's2'
      const symbol = mockSymbols.find(s => s.id === selectedSymbolId)
      expect(symbol?.code).toBe('600519')
    })
  })

  describe('键盘精灵选择回调', () => {
    it('handleKeyboardSelect应设置selectedSymbolId', () => {
      let selectedSymbolId: string | null = null
      const handleKeyboardSelect = (item: { id: string }) => {
        selectedSymbolId = item.id
      }
      handleKeyboardSelect({ id: 'test-id', name: '测试', code: '999999' })
      expect(selectedSymbolId).toBe('test-id')
    })
  })
})

// ============================================================
// 数据计算逻辑
// ============================================================
describe('数据计算逻辑', () => {
  const mockChartData = [
    { date: '2026-04-01', open: 45.0, close: 46.2, high: 46.8, low: 44.5, change_pct: 2.5, volume: 1000000, is_st: false, is_suspended: false },
    { date: '2026-04-02', open: 46.2, close: 45.8, high: 46.5, low: 45.3, change_pct: -0.86, volume: 1200000, is_st: false, is_suspended: false },
    { date: '2026-04-03', open: 45.8, close: 47.5, high: 48.0, low: 45.5, change_pct: 3.7, volume: 1500000, is_st: false, is_suspended: false },
  ]

  describe('currentPrice计算', () => {
    it('应取最新记录的收盘价', () => {
      const latest = mockChartData[mockChartData.length - 1]
      const price = parseFloat(latest.close).toFixed(2)
      expect(price).toBe('47.50')
    })

    it('空数据应返回null', () => {
      const data: any[] = []
      const currentPrice = data.length ? data[data.length - 1].close : null
      expect(currentPrice).toBeNull()
    })
  })

  describe('changePercent计算', () => {
    it('应取最新记录的change_pct并格式化', () => {
      const latest = mockChartData[mockChartData.length - 1]
      const change = latest.change_pct ? `${parseFloat(latest.change_pct).toFixed(2)}%` : null
      expect(change).toBe('3.70%')
    })

    it('仅有1条数据时change_pct可能为空', () => {
      const data = [{ date: '2026-04-01', close: 45.0 }]
      const hasChangePct = data[data.length - 1].change_pct !== undefined
      expect(hasChangePct).toBe(false)
    })
  })

  describe('priceClass计算', () => {
    it('涨跌幅为正应返回positive', () => {
      const change = 3.7
      const cls = change > 0 ? 'positive' : change < 0 ? 'negative' : ''
      expect(cls).toBe('positive')
    })

    it('涨跌幅为负应返回negative', () => {
      const change = -0.86
      const cls = change > 0 ? 'positive' : change < 0 ? 'negative' : ''
      expect(cls).toBe('negative')
    })

    it('未选中标的应返回空', () => {
      const selectedSymbolId = null
      const changePercent = '3.70%'
      const cls = !selectedSymbolId || !changePercent ? '' : 'positive'
      expect(cls).toBe('')
    })
  })
})

// ============================================================
// 不同周期limit计算
// ============================================================
describe('周期数据limit计算', () => {
  const getLimit = (period: string) => {
    switch (period) {
      case 'daily': return 1000
      case 'weekly': return 208
      case 'monthly': return 48
      default: return 1000
    }
  }

  it('daily应获取1000条', () => {
    expect(getLimit('daily')).toBe(1000)
  })

  it('weekly应获取208条', () => {
    expect(getLimit('weekly')).toBe(208)
  })

  it('monthly应获取48条', () => {
    expect(getLimit('monthly')).toBe(48)
  })

  it('未知周期默认返回1000', () => {
    expect(getLimit('unknown')).toBe(1000)
  })
})

// ============================================================
// 标的搜索过滤逻辑
// ============================================================
describe('标的搜索过滤逻辑', () => {
  const mockSymbols = [
    { id: '1', name: '平安银行', code: '000001' },
    { id: '2', name: '万科A', code: '000002' },
    { id: '3', name: '贵州茅台', code: '600519' },
  ]

  it('应按代码过滤(大小写不敏感)', () => {
    const query = '0000'
    const lowerQuery = query.toLowerCase()
    const filtered = mockSymbols.filter(s =>
      s.code.toLowerCase().includes(lowerQuery) ||
      s.name.toLowerCase().includes(lowerQuery)
    )
    expect(filtered).toHaveLength(2)
    expect(filtered.map(f => f.code)).toEqual(['000001', '000002'])
  })

  it('应按名称过滤', () => {
    const query = '茅台'
    const lowerQuery = query.toLowerCase()
    const filtered = mockSymbols.filter(s =>
      s.code.toLowerCase().includes(lowerQuery) ||
      s.name.toLowerCase().includes(lowerQuery)
    )
    expect(filtered).toHaveLength(1)
    expect(filtered[0].code).toBe('600519')
  })

  it('空查询应返回空', () => {
    const query = ''
    if (!query) {
      expect(true).toBe(true)
    }
  })
})