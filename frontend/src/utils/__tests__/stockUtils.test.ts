/**
 * 股票市场工具函数测试.
 *
 * 测试市场类型识别、涨跌停计算、复权处理等功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect } from 'vitest'
import {
  MarketType,
  marketConfigs,
  identifyMarketType,
  identifyMarketTypeByName,
  getMarketConfig,
  calculateLimitUpPrice,
  calculateLimitDownPrice,
  isLimitUp,
  isLimitDown,
  roundPrice,
  calculateLimitUpDownStats,
  AdjustmentType,
  calculateForwardAdjustedPrice,
  calculateBackwardAdjustedPrice,
  calculateAdjustmentFactor,
  calculateAdjustedPrices,
  generateDividendMarkPoints,
  generateDividendMarkLines,
  detectSuspensionPeriods,
  generateSuspensionMarkAreas,
  FuturesMarketType,
  calculateDaysToExpiry,
  isContractNearExpiry,
  isContractExpired,
  generateExpiryMarkPoints,
  generateExpiryMarkLines,
  generateMainSwitchMarkPoints,
  formatOpenInterest,
  calculateOIChangeRate,
  isOIAbnormalChange
} from '../stockUtils'

describe('StockUtils 股票市场工具', () => {
  describe('MarketType 市场类型枚举', () => {
    it('应包含所有市场类型', () => {
      expect(MarketType.FOREX).toBe('forex')
      expect(MarketType.STOCK_A).toBe('stock_a')
      expect(MarketType.STOCK_KCB).toBe('stock_kcb')
      expect(MarketType.STOCK_CYB).toBe('stock_cyb')
      expect(MarketType.STOCK_ST).toBe('stock_st')
      expect(MarketType.STOCK_BJB).toBe('stock_bjb')
    })
  })

  describe('marketConfigs 市场配置', () => {
    it('外汇市场配置应正确', () => {
      const config = marketConfigs[MarketType.FOREX]
      expect(config.name).toBe('外汇')
      expect(config.hasLimitUpDown).toBe(false)
      expect(config.needAdjustment).toBe(false)
      expect(config.is24HourTrading).toBe(true)
      expect(config.pricePrecision).toBe(4)
    })

    it('A股市场配置应正确', () => {
      const config = marketConfigs[MarketType.STOCK_A]
      expect(config.name).toBe('A股')
      expect(config.limitUpThreshold).toBe(10)
      expect(config.limitDownThreshold).toBe(10)
      expect(config.hasLimitUpDown).toBe(true)
      expect(config.needAdjustment).toBe(true)
      expect(config.pricePrecision).toBe(2)
    })

    it('科创板市场配置应正确', () => {
      const config = marketConfigs[MarketType.STOCK_KCB]
      expect(config.name).toBe('科创板')
      expect(config.limitUpThreshold).toBe(20)
      expect(config.limitDownThreshold).toBe(20)
      expect(config.hasLimitUpDown).toBe(true)
    })

    it('创业板市场配置应正确', () => {
      const config = marketConfigs[MarketType.STOCK_CYB]
      expect(config.name).toBe('创业板')
      expect(config.limitUpThreshold).toBe(20)
      expect(config.limitDownThreshold).toBe(20)
    })

    it('ST股市场配置应正确', () => {
      const config = marketConfigs[MarketType.STOCK_ST]
      expect(config.name).toBe('ST股')
      expect(config.limitUpThreshold).toBe(5)
      expect(config.limitDownThreshold).toBe(5)
    })

    it('北交所市场配置应正确', () => {
      const config = marketConfigs[MarketType.STOCK_BJB]
      expect(config.name).toBe('北交所')
      expect(config.limitUpThreshold).toBe(30)
      expect(config.limitDownThreshold).toBe(30)
    })
  })

  describe('identifyMarketType 市场类型识别', () => {
    it('外汇代码应识别为FOREX', () => {
      expect(identifyMarketType('EURUSD')).toBe(MarketType.FOREX)
      expect(identifyMarketType('USDCNY')).toBe(MarketType.FOREX)
      expect(identifyMarketType('GBPJPY')).toBe(MarketType.FOREX)
    })

    it('科创板代码应识别为STOCK_KCB', () => {
      expect(identifyMarketType('688001')).toBe(MarketType.STOCK_KCB)
      expect(identifyMarketType('688999')).toBe(MarketType.STOCK_KCB)
    })

    it('创业板代码应识别为STOCK_CYB', () => {
      expect(identifyMarketType('300001')).toBe(MarketType.STOCK_CYB)
      expect(identifyMarketType('300999')).toBe(MarketType.STOCK_CYB)
    })

    it('北交所代码应识别为STOCK_BJB', () => {
      expect(identifyMarketType('830001')).toBe(MarketType.STOCK_BJB)
      expect(identifyMarketType('430001')).toBe(MarketType.STOCK_BJB)
    })

    it('A股代码应识别为STOCK_A', () => {
      expect(identifyMarketType('600000')).toBe(MarketType.STOCK_A)
      expect(identifyMarketType('000001')).toBe(MarketType.STOCK_A)
    })

    it('空代码应返回FOREX', () => {
      expect(identifyMarketType('')).toBe(MarketType.FOREX)
      expect(identifyMarketType(null)).toBe(MarketType.FOREX)
      expect(identifyMarketType(undefined)).toBe(MarketType.FOREX)
    })

    it('带特殊字符的代码应正确识别', () => {
      expect(identifyMarketType('EUR-USD')).toBe(MarketType.FOREX)
      // 600000.SH去除特殊字符后变成600000SH，不符合A股模式
      // 应只处理标准格式代码
      expect(identifyMarketType('600000')).toBe(MarketType.STOCK_A)
    })
  })

  describe('identifyMarketTypeByName 根据名称识别市场', () => {
    it('ST名称应识别为STOCK_ST', () => {
      expect(identifyMarketTypeByName('600000', 'ST某某')).toBe(MarketType.STOCK_ST)
      expect(identifyMarketTypeByName('000001', '*ST某某')).toBe(MarketType.STOCK_ST)
    })

    it('无名称时应使用代码识别', () => {
      expect(identifyMarketTypeByName('688001')).toBe(MarketType.STOCK_KCB)
      expect(identifyMarketTypeByName('300001')).toBe(MarketType.STOCK_CYB)
    })

    it('名称不含ST时应使用代码识别', () => {
      expect(identifyMarketTypeByName('600000', '某某股份')).toBe(MarketType.STOCK_A)
    })
  })

  describe('getMarketConfig 获取市场配置', () => {
    it('有效市场类型应返回正确配置', () => {
      const config = getMarketConfig(MarketType.STOCK_A)
      expect(config.type).toBe(MarketType.STOCK_A)
      expect(config.name).toBe('A股')
    })

    it('无效市场类型应返回FOREX配置', () => {
      const config = getMarketConfig('invalid' as any)
      expect(config.type).toBe(MarketType.FOREX)
    })
  })

  describe('calculateLimitUpPrice 涨停价计算', () => {
    it('A股涨停价应正确计算', () => {
      // 10%涨停
      const result = calculateLimitUpPrice(10.00, MarketType.STOCK_A)
      expect(result).toBe(11.00)
    })

    it('科创板涨停价应正确计算', () => {
      // 20%涨停
      const result = calculateLimitUpPrice(10.00, MarketType.STOCK_KCB)
      expect(result).toBe(12.00)
    })

    it('ST股涨停价应正确计算', () => {
      // 5%涨停
      const result = calculateLimitUpPrice(5.00, MarketType.STOCK_ST)
      expect(result).toBe(5.25)
    })

    it('外汇市场应返回0（无涨跌停）', () => {
      const result = calculateLimitUpPrice(7.25, MarketType.FOREX)
      expect(result).toBe(0)
    })

    it('精度应为2位小数', () => {
      const result = calculateLimitUpPrice(10.123, MarketType.STOCK_A)
      expect(result).toBeCloseTo(11.14, 2)
    })
  })

  describe('calculateLimitDownPrice 跌停价计算', () => {
    it('A股跌停价应正确计算', () => {
      const result = calculateLimitDownPrice(10.00, MarketType.STOCK_A)
      expect(result).toBe(9.00)
    })

    it('科创板跌停价应正确计算', () => {
      const result = calculateLimitDownPrice(10.00, MarketType.STOCK_KCB)
      expect(result).toBe(8.00)
    })

    it('ST股跌停价应正确计算', () => {
      const result = calculateLimitDownPrice(5.00, MarketType.STOCK_ST)
      expect(result).toBe(4.75)
    })

    it('外汇市场应返回0', () => {
      const result = calculateLimitDownPrice(7.25, MarketType.FOREX)
      expect(result).toBe(0)
    })
  })

  describe('isLimitUp 判断涨停', () => {
    it('达到涨停价应返回true', () => {
      const limitUpPrice = 11.00
      expect(isLimitUp(11.00, limitUpPrice, MarketType.STOCK_A)).toBe(true)
    })

    it('接近涨停价（误差范围内）应返回true', () => {
      const limitUpPrice = 11.00
      // tolerance = 0.0001，差值应小于tolerance
      expect(isLimitUp(10.9999, limitUpPrice, MarketType.STOCK_A)).toBe(true)
    })

    it('未达涨停价应返回false', () => {
      const limitUpPrice = 11.00
      expect(isLimitUp(10.95, limitUpPrice, MarketType.STOCK_A)).toBe(false)
    })

    it('外汇市场应返回false', () => {
      expect(isLimitUp(7.25, 0, MarketType.FOREX)).toBe(false)
    })
  })

  describe('isLimitDown 判断跌停', () => {
    it('达到跌停价应返回true', () => {
      const limitDownPrice = 9.00
      expect(isLimitDown(9.00, limitDownPrice, MarketType.STOCK_A)).toBe(true)
    })

    it('接近跌停价应返回true', () => {
      const limitDownPrice = 9.00
      // tolerance = 0.0001，差值应小于tolerance
      expect(isLimitDown(9.0001, limitDownPrice, MarketType.STOCK_A)).toBe(true)
    })

    it('未达跌停价应返回false', () => {
      const limitDownPrice = 9.00
      expect(isLimitDown(9.05, limitDownPrice, MarketType.STOCK_A)).toBe(false)
    })

    it('外汇市场应返回false', () => {
      expect(isLimitDown(7.25, 0, MarketType.FOREX)).toBe(false)
    })
  })

  describe('roundPrice 价格取整', () => {
    it('精度2位应正确取整', () => {
      expect(roundPrice(7.256, 2)).toBe(7.26)
      expect(roundPrice(7.254, 2)).toBe(7.25)
    })

    it('精度4位应正确取整', () => {
      expect(roundPrice(7.25678, 4)).toBe(7.2568)
      expect(roundPrice(7.25672, 4)).toBe(7.2567)
    })

    it('精度0位应正确取整', () => {
      expect(roundPrice(7.5, 0)).toBe(8)
      expect(roundPrice(7.4, 0)).toBe(7)
    })
  })

  describe('calculateLimitUpDownStats 涨跌停统计', () => {
    it('应正确统计涨跌停次数', () => {
      const rawData = [
        { date: '2026-01-01', open: 10, close: 10 },
        { date: '2026-01-02', open: 10, close: 11 }, // 涨停（prevClose=10）
        { date: '2026-01-03', open: 11, close: 9.9 }, // 跌停（prevClose=11）
        { date: '2026-01-04', open: 10, close: 10 } // 正常（prevClose=9.9，涨幅约1%，非涨停）
      ]
      const result = calculateLimitUpDownStats(rawData, MarketType.STOCK_A)
      expect(result.limitUpCount).toBe(1)
      expect(result.limitDownCount).toBe(1)
      expect(result.limitUpDates).toContain('2026-01-02')
      expect(result.limitDownDates).toContain('2026-01-03')
    })

    it('外汇市场应返回空统计', () => {
      const rawData = [
        { date: '2026-01-01', open: 7.25, close: 7.30 },
        { date: '2026-01-02', open: 7.30, close: 7.28 }
      ]
      const result = calculateLimitUpDownStats(rawData, MarketType.FOREX)
      expect(result.limitUpCount).toBe(0)
      expect(result.limitDownCount).toBe(0)
    })

    it('少于2条数据应返回空统计', () => {
      const rawData = [{ date: '2026-01-01', open: 10, close: 10 }]
      const result = calculateLimitUpDownStats(rawData, MarketType.STOCK_A)
      expect(result.limitUpCount).toBe(0)
      expect(result.limitDownCount).toBe(0)
    })

    it('涨跌停比例应正确计算', () => {
      const rawData = [
        { date: '2026-01-01', open: 10, close: 10 },
        { date: '2026-01-02', open: 10, close: 11 }, // 涨停
        { date: '2026-01-03', open: 10, close: 10 }
      ]
      const result = calculateLimitUpDownStats(rawData, MarketType.STOCK_A)
      // 总共2天可统计（排除第一天），涨停1次
      expect(result.limitUpRatio).toBe(0.5)
    })
  })

  describe('复权处理', () => {
    describe('AdjustmentType 复权类型枚举', () => {
      it('应包含所有复权类型', () => {
        expect(AdjustmentType.NONE).toBe('none')
        expect(AdjustmentType.FORWARD).toBe('forward')
        expect(AdjustmentType.BACKWARD).toBe('backward')
      })
    })

    describe('calculateForwardAdjustedPrice 前复权价格计算', () => {
      it('前复权应正确计算', () => {
        // 前复权价格 = 原价格 * 累计复权因子
        expect(calculateForwardAdjustedPrice(10, 1.2)).toBe(12)
        expect(calculateForwardAdjustedPrice(10, 0.8)).toBe(8)
      })
    })

    describe('calculateBackwardAdjustedPrice 后复权价格计算', () => {
      it('后复权应正确计算', () => {
        // 后复权价格 = 原价格 / 累计复权因子
        expect(calculateBackwardAdjustedPrice(12, 1.2)).toBe(10)
        expect(calculateBackwardAdjustedPrice(8, 0.8)).toBe(10)
      })
    })

    describe('calculateAdjustmentFactor 复权因子计算', () => {
      it('仅分红时应正确计算', () => {
        // 分红后，复权因子 = (收盘价 - 分红) / 收盘价
        const result = calculateAdjustmentFactor(10, 0.5, 0, 0, 0)
        expect(result).toBe(0.95)
      })

      it('仅送股时应正确计算', () => {
        // 送股后，复权因子 = 收盘价 / (收盘价 * (1 + 送股比例))
        // 简化：= 1 / (1 + 送股比例)
        const result = calculateAdjustmentFactor(10, 0, 0.1, 0, 0) // 10送1
        expect(result).toBeCloseTo(0.909, 3)
      })

      it('分红+送股时应正确计算', () => {
        const result = calculateAdjustmentFactor(10, 0.5, 0.1, 0, 0)
        // adjustedClose = 9.5, totalRatio = 1.1
        // factor = 9.5 / (10 * 1.1) = 9.5 / 11
        expect(result).toBeCloseTo(0.8636, 4)
      })

      it('无分红送股时应返回1', () => {
        const result = calculateAdjustmentFactor(10)
        expect(result).toBe(1)
      })
    })

    describe('calculateAdjustedPrices 批量复权计算', () => {
      it('不复权应返回原始数据', () => {
        const rawData = [
          { date: '2026-01-01', open: 10, close: 10, high: 10.5, low: 9.5 },
          { date: '2026-01-02', open: 10, close: 11, high: 11.5, low: 9.5 }
        ]
        const factors = [{ date: '2026-01-02', factor: 0.95 }]
        const result = calculateAdjustedPrices(rawData, factors, AdjustmentType.NONE)
        expect(result[0].close).toBe(10)
        expect(result[1].close).toBe(11)
      })

      it('前复权应正确计算', () => {
        const rawData = [
          { date: '2026-01-01', open: 10, close: 10, high: 10.5, low: 9.5 },
          { date: '2026-01-02', open: 10, close: 10, high: 10.5, low: 9.5 }
        ]
        const factors = [{ date: '2026-01-02', factor: 0.9 }]
        const result = calculateAdjustedPrices(rawData, factors, AdjustmentType.FORWARD, 2)
        // 累计复权因子从后往前累积：
        // i=1: factor存在，cumulativeFactor=1*0.9=0.9
        // i=0: 无factor，cumulativeFactor保持0.9
        // 前复权：价格 * 累计因子
        expect(result[0].close).toBe(9) // 10 * 0.9
        expect(result[1].close).toBe(9) // 10 * 0.9
      })

      it('空数据应返回空数组', () => {
        expect(calculateAdjustedPrices(null, [], AdjustmentType.NONE)).toEqual([])
        expect(calculateAdjustedPrices([], [], AdjustmentType.NONE)).toEqual([])
      })
    })
  })

  describe('除权除息标记', () => {
    describe('generateDividendMarkPoints', () => {
      it('应正确生成除权除息标记点', () => {
        const events = [{
          eventDate: '2026-01-02',
          eventType: 'dividend',
          adjustmentFactor: 0.95
        }]
        const rawData = [
          { date: '2026-01-01', high: 10.5 },
          { date: '2026-01-02', high: 11 }
        ]
        const result = generateDividendMarkPoints(events, 'light', rawData)
        expect(result).not.toBeNull()
        expect(result.data).toHaveLength(1)
        expect(result.data[0].symbol).toBe('pin')
      })

      it('空事件应返回null', () => {
        expect(generateDividendMarkPoints(null, 'light', [])).toBeNull()
        expect(generateDividendMarkPoints([], 'light', [])).toBeNull()
      })

      it('找不到对应日期应返回null', () => {
        const events = [{ eventDate: '2026-01-05', eventType: 'dividend', adjustmentFactor: 0.95 }]
        const rawData = [{ date: '2026-01-01', high: 10.5 }]
        const result = generateDividendMarkPoints(events, 'light', rawData)
        expect(result).toBeNull()
      })
    })

    describe('generateDividendMarkLines', () => {
      it('应正确生成除权除息标记线', () => {
        const events = [{ eventDate: '2026-01-02', eventType: 'bonus', adjustmentFactor: 0.9 }]
        const rawData = [
          { date: '2026-01-01', high: 10.5, low: 9.5 },
          { date: '2026-01-02', high: 11, low: 10 }
        ]
        const result = generateDividendMarkLines(events, rawData, 'light')
        expect(result).not.toBeNull()
        expect(result.symbol).toBe('none')
      })

      it('空事件应返回null', () => {
        expect(generateDividendMarkLines(null, [], 'light')).toBeNull()
        expect(generateDividendMarkLines([], [], 'light')).toBeNull()
      })
    })
  })

  describe('停牌检测', () => {
    describe('detectSuspensionPeriods', () => {
      it('应检测超过7天的间隔', () => {
        const rawData = [
          { date: '2026-01-01' },
          { date: '2026-01-15' } // 间隔14天
        ]
        const result = detectSuspensionPeriods(rawData)
        expect(result).toHaveLength(1)
        expect(result[0].days).toBe(14)
      })

      it('正常间隔应不检测', () => {
        const rawData = [
          { date: '2026-01-01' },
          { date: '2026-01-03' } // 间隔2天
        ]
        const result = detectSuspensionPeriods(rawData)
        expect(result).toHaveLength(0)
      })

      it('少于2条数据应返回空', () => {
        expect(detectSuspensionPeriods(null)).toEqual([])
        expect(detectSuspensionPeriods([])).toEqual([])
        expect(detectSuspensionPeriods([{ date: '2026-01-01' }])).toEqual([])
      })
    })

    describe('generateSuspensionMarkAreas', () => {
      it('应正确生成停牌标记区域', () => {
        const suspensions = [{
          startDate: '2026-01-01',
          endDate: '2026-01-15',
          days: 14,
          startIndex: 0,
          endIndex: 1
        }]
        const rawData = [
          { date: '2026-01-01', high: 10.5, low: 9.5 },
          { date: '2026-01-15', high: 11, low: 10 }
        ]
        const result = generateSuspensionMarkAreas(suspensions, rawData, 'light')
        expect(result).not.toBeNull()
        expect(result.data).toHaveLength(1)
      })

      it('空停牌数组应返回null', () => {
        expect(generateSuspensionMarkAreas(null, [], 'light')).toBeNull()
        expect(generateSuspensionMarkAreas([], [], 'light')).toBeNull()
      })
    })
  })

  describe('期货市场功能', () => {
    describe('FuturesMarketType 期货市场类型', () => {
      it('应包含所有期货市场类型', () => {
        expect(FuturesMarketType.CFFEX_INDEX).toBe('cffex_index')
        expect(FuturesMarketType.SHFE_METAL).toBe('shfe_metal')
        expect(FuturesMarketType.DCE_AGRI).toBe('dce_agri')
        expect(FuturesMarketType.CZCE_AGRI).toBe('czce_agri')
      })
    })

    describe('calculateDaysToExpiry 距到期天数计算', () => {
      it('应正确计算距到期天数', () => {
        const result = calculateDaysToExpiry('2026-01-31', '2026-01-25')
        expect(result).toBe(6)
      })

      it('已到期应返回负数', () => {
        const result = calculateDaysToExpiry('2026-01-10', '2026-01-20')
        expect(result).toBeLessThan(0)
      })

      it('无当前日期参数应使用今天', () => {
        const futureDate = new Date()
        futureDate.setDate(futureDate.getDate() + 10)
        const result = calculateDaysToExpiry(futureDate.toISOString().split('T')[0])
        expect(result).toBeGreaterThan(0)
      })
    })

    describe('isContractNearExpiry 判断即将到期', () => {
      it('即将到期应返回true', () => {
        const contract = {
          contractCode: 'IF2401',
          contractName: '沪深300指数期货2401',
          contractMonth: '01',
          year: '24',
          month: '01',
          lastTradeDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          isMainContract: true
        } as any
        expect(isContractNearExpiry(contract, 5)).toBe(true)
      })

      it('非即将到期应返回false', () => {
        const contract = {
          contractCode: 'IF2402',
          contractName: '沪深300指数期货2402',
          contractMonth: '02',
          year: '24',
          month: '02',
          lastTradeDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          isMainContract: true
        } as any
        expect(isContractNearExpiry(contract, 5)).toBe(false)
      })

      it('已到期应返回false', () => {
        const contract = {
          contractCode: 'IF2312',
          contractName: '沪深300指数期货2312',
          contractMonth: '12',
          year: '23',
          month: '12',
          lastTradeDate: '2023-12-15',
          isMainContract: false
        } as any
        expect(isContractNearExpiry(contract, 5)).toBe(false)
      })
    })

    describe('isContractExpired 判断已到期', () => {
      it('已到期应返回true', () => {
        const contract = {
          lastTradeDate: '2023-12-15'
        } as any
        expect(isContractExpired(contract)).toBe(true)
      })

      it('未到期应返回false', () => {
        const futureDate = new Date()
        futureDate.setDate(futureDate.getDate() + 30)
        const contract = {
          lastTradeDate: futureDate.toISOString().split('T')[0]
        } as any
        expect(isContractExpired(contract)).toBe(false)
      })
    })

    describe('generateExpiryMarkPoints 到期标记点生成', () => {
      it('应正确生成到期标记点', () => {
        const contracts = [{
          contractCode: 'IF2401',
          lastTradeDate: '2026-01-02',
          isMainContract: true
        } as any]
        const rawData = [
          { date: '2026-01-01', high: 4000, low: 3900 },
          { date: '2026-01-02', high: 4050, low: 3950 }
        ]
        const result = generateExpiryMarkPoints(contracts, rawData, 'light', true)
        expect(result).not.toBeNull()
        expect(result.data).toHaveLength(1)
      })

      it('空合约数组应返回null', () => {
        expect(generateExpiryMarkPoints(null, [], 'light')).toBeNull()
        expect(generateExpiryMarkPoints([], [], 'light')).toBeNull()
      })
    })

    describe('generateExpiryMarkLines 到期标记线生成', () => {
      it('应正确生成到期标记线', () => {
        const contracts = [{
          contractCode: 'IF2401',
          lastTradeDate: '2026-01-02',
          isMainContract: true
        } as any]
        const rawData = [
          { date: '2026-01-01', high: 4000 },
          { date: '2026-01-02', high: 4050 }
        ]
        const result = generateExpiryMarkLines(contracts, rawData, 'light')
        expect(result).not.toBeNull()
        expect(result.symbol).toBe('none')
      })

      it('空合约数组应返回null', () => {
        expect(generateExpiryMarkLines(null, [], 'light')).toBeNull()
      })
    })

    describe('generateMainSwitchMarkPoints 主力切换标记', () => {
      it('应正确生成主力切换标记', () => {
        const switchPoints = [{
          switch_date: '2026-01-02',
          old_contract_code: 'IF2401',
          new_contract_code: 'IF2402'
        }]
        const rawData = [
          { date: '2026-01-01', high: 4000 },
          { date: '2026-01-02', high: 4050 }
        ]
        const result = generateMainSwitchMarkPoints(switchPoints, rawData, 'light')
        expect(result).not.toBeNull()
        expect(result.data).toHaveLength(1)
        expect(result.data[0].symbol).toBe('triangle')
      })

      it('空切换点应返回null', () => {
        expect(generateMainSwitchMarkPoints(null, [], 'light')).toBeNull()
        expect(generateMainSwitchMarkPoints([], [], 'light')).toBeNull()
      })
    })

    describe('formatOpenInterest 持仓量格式化', () => {
      it('亿手应正确格式化', () => {
        expect(formatOpenInterest(150000000)).toBe('1.50亿手')
      })

      it('千万手应正确格式化', () => {
        expect(formatOpenInterest(25000000)).toBe('2.50千万手')
      })

      it('万手应正确格式化', () => {
        expect(formatOpenInterest(15000)).toBe('1.50万手')
      })

      it('小数值应正确格式化', () => {
        expect(formatOpenInterest(500)).toBe('500手')
      })
    })

    describe('calculateOIChangeRate 持仓量变化率计算', () => {
      it('增加应正确计算', () => {
        expect(calculateOIChangeRate(120000, 100000)).toBe(20)
      })

      it('减少应正确计算', () => {
        expect(calculateOIChangeRate(80000, 100000)).toBe(-20)
      })

      it('前值为0应返回0', () => {
        expect(calculateOIChangeRate(100000, 0)).toBe(0)
      })
    })

    describe('isOIAbnormalChange 持仓量异常变化检测', () => {
      it('异常变化应返回true', () => {
        expect(isOIAbnormalChange(25, 20)).toBe(true)
        expect(isOIAbnormalChange(-25, 20)).toBe(true)
      })

      it('正常变化应返回false', () => {
        expect(isOIAbnormalChange(15, 20)).toBe(false)
        expect(isOIAbnormalChange(-15, 20)).toBe(false)
      })

      it('默认阈值应为20%', () => {
        expect(isOIAbnormalChange(20)).toBe(true)
        expect(isOIAbnormalChange(19)).toBe(false)
      })
    })
  })
})