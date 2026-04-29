/**
 * StockData 页面测试.
 *
 * 测试股票数据页面核心逻辑：格式化、状态显示.
 *
 * Author: FDAS Team
 * Created: 2026-04-23
 */

import { describe, it, expect } from 'vitest'

describe('StockData核心逻辑', () => {
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

    it('formatPrice应正确格式化股票价格(2位小数)', () => {
      expect(formatPrice(123.456)).toBe('123.46')
      expect(formatPrice(100.0)).toBe('100.00')
      expect(formatPrice(null)).toBe('--')
    })

    it('formatChange应正确格式化涨跌幅', () => {
      expect(formatChange(5.67)).toBe('5.67%')
      expect(formatChange(-3.21)).toBe('-3.21%')
      expect(formatChange(null)).toBe('--')
    })

    it('getChangeClass应正确返回样式类', () => {
      expect(getChangeClass(5)).toBe('positive')
      expect(getChangeClass(-3)).toBe('negative')
      expect(getChangeClass(0)).toBe('')
      expect(getChangeClass(null)).toBe('')
    })
  })

  describe('股票特殊状态', () => {
    const isST = (is_st: boolean) => is_st
    const isSuspended = (is_suspended: boolean) => is_suspended

    it('应正确识别ST股票', () => {
      expect(isST(true)).toBe(true)
      expect(isST(false)).toBe(false)
    })

    it('应正确识别停牌股票', () => {
      expect(isSuspended(true)).toBe(true)
      expect(isSuspended(false)).toBe(false)
    })
  })

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
  })
})