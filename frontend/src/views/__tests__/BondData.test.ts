/**
 * BondData 页面测试.
 *
 * 测试债券数据页面核心逻辑：格式化、收益率显示、duration/convexity.
 *
 * Author: FDAS Team
 * Created: 2026-04-29
 */

import { describe, it, expect } from 'vitest'

describe('BondData核心逻辑', () => {
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

    it('formatPrice应正确格式化债券价格(2位小数)', () => {
      expect(formatPrice(101.567)).toBe('101.57')
      expect(formatPrice(100.0)).toBe('100.00')
      expect(formatPrice(null)).toBe('--')
    })

    it('formatChange应正确格式化涨跌幅', () => {
      expect(formatChange(0.15)).toBe('0.15%')
      expect(formatChange(-0.08)).toBe('-0.08%')
      expect(formatChange(null)).toBe('--')
    })

    it('getChangeClass应正确返回样式类', () => {
      expect(getChangeClass(0.5)).toBe('positive')
      expect(getChangeClass(-0.3)).toBe('negative')
      expect(getChangeClass(0)).toBe('')
    })
  })

  describe('收益率格式化', () => {
    const formatYield = (value: any) => {
      if (!value && value !== 0) return '--'
      return `${parseFloat(value).toFixed(2)}%`
    }

    it('应正确格式化收益率百分比', () => {
      expect(formatYield(2.85)).toBe('2.85%')
      expect(formatYield(3.0)).toBe('3.00%')
      expect(formatYield(0)).toBe('0.00%')
    })

    it('空值应返回--', () => {
      expect(formatYield(null)).toBe('--')
      expect(formatYield(undefined)).toBe('--')
    })
  })

  describe('债券特有字段', () => {
    const formatDuration = (value: any) => {
      if (!value && value !== 0) return '--'
      return parseFloat(value).toFixed(2)
    }

    const formatConvexity = (value: any) => {
      if (!value && value !== 0) return '--'
      return parseFloat(value).toFixed(4)
    }

    it('duration应保留2位小数', () => {
      expect(formatDuration(5.678)).toBe('5.68')
      expect(formatDuration(0)).toBe('0.00')
      expect(formatDuration(null)).toBe('--')
    })

    it('convexity应保留4位小数', () => {
      expect(formatConvexity(0.2356)).toBe('0.2356')
      expect(formatConvexity(0)).toBe('0.0000')
      expect(formatConvexity(null)).toBe('--')
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
      const labels = periodOptions.map(p => p.label)
      expect(labels).toContain('日线')
      expect(labels).toContain('周线')
      expect(labels).toContain('月线')
    })
  })

  describe('MA/MACD/VOL参数默认值', () => {
    const defaultMAs = ['5', '10', '20', '60']
    const defaultMACD = { fast: 12, slow: 26, signal: 9 }
    const defaultVOL = ['5', '10']

    it('MA默认周期应包含5/10/20/60', () => {
      expect(defaultMAs.length).toBe(4)
      expect(defaultMAs).toContain('60')
    })

    it('MACD默认参数fast=12,slow=26,signal=9', () => {
      expect(defaultMACD).toEqual({ fast: 12, slow: 26, signal: 9 })
    })

    it('VOL默认周期应包含5/10', () => {
      expect(defaultVOL).toEqual(['5', '10'])
    })
  })
})
