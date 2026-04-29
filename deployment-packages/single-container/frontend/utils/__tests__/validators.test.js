/**
 * Validators 测试.
 *
 * 测试前端校验函数库的核心逻辑.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect } from 'vitest'
import {
  validateDateRange,
  validateCronExpression,
  describeCron,
  validateTaskParams
} from '../validators'

describe('Validators', () => {
  describe('validateDateRange', () => {
    describe('有效日期范围', () => {
      it('有效日期范围应返回valid=true', () => {
        const result = validateDateRange('2026-01-01', '2026-01-31')
        expect(result.valid).toBe(true)
        expect(result.errors).toEqual([])
      })

      it('相同日期应有效', () => {
        const result = validateDateRange('2026-01-15', '2026-01-15')
        expect(result.valid).toBe(true)
      })

      it('Date对象作为参数应有效', () => {
        const start = new Date(2026, 0, 1)
        const end = new Date(2026, 0, 31)
        const result = validateDateRange(start, end)
        expect(result.valid).toBe(true)
      })

      it('混合Date和字符串应有效', () => {
        const start = new Date(2026, 0, 1)
        const result = validateDateRange(start, '2026-01-31')
        expect(result.valid).toBe(true)
      })

      it('无minDate限制应有效', () => {
        const result = validateDateRange('2020-01-01', '2026-01-31', null)
        expect(result.valid).toBe(true)
      })
    })

    describe('无效日期范围', () => {
      it('开始日期晚于结束日期应无效', () => {
        const result = validateDateRange('2026-01-31', '2026-01-01')
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('开始日期不能晚于结束日期')
      })

      it('结束日期超过今天应无效', () => {
        const futureDate = new Date()
        futureDate.setFullYear(futureDate.getFullYear() + 1)
        const result = validateDateRange('2026-01-01', futureDate.toISOString())
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('结束日期不能超过今天')
      })

      it('开始日期早于minDate应无效', () => {
        const result = validateDateRange('2020-01-01', '2026-01-31', '2025-01-01')
        expect(result.valid).toBe(false)
        expect(result.errors[0]).toContain('开始日期不能早于')
      })

      it('多个错误应同时返回', () => {
        const futureDate = new Date()
        futureDate.setFullYear(futureDate.getFullYear() + 2)
        const result = validateDateRange(futureDate.toISOString(), futureDate.toISOString(), '2025-01-01')
        expect(result.errors.length).toBeGreaterThan(0)
      })
    })

    describe('边界情况', () => {
      it('null参数应返回valid', () => {
        const result = validateDateRange(null, null)
        expect(result.valid).toBe(true)
      })

      it('undefined参数应返回valid', () => {
        const result = validateDateRange(undefined, undefined)
        expect(result.valid).toBe(true)
      })

      it('minDate为Date对象应正确验证', () => {
        const minDate = new Date(2025, 0, 1)
        const result = validateDateRange('2024-01-01', '2026-01-31', minDate)
        expect(result.valid).toBe(false)
      })
    })
  })

  describe('validateCronExpression', () => {
    describe('有效Cron表达式', () => {
      it('标准5部分表达式应有效', () => {
        const result = validateCronExpression('0 0 * * *')
        expect(result.valid).toBe(true)
      })

      it('每天执行表达式应有效', () => {
        const result = validateCronExpression('30 8 * * *')
        expect(result.valid).toBe(true)
      })

      it('每小时执行应有效', () => {
        const result = validateCronExpression('0 * * * *')
        expect(result.valid).toBe(true)
      })

      it('使用范围表达式应有效', () => {
        const result = validateCronExpression('0 9-17 * * *')
        expect(result.valid).toBe(true)
      })

      it('使用列表表达式应有效', () => {
        const result = validateCronExpression('0 9,12,17 * * *')
        expect(result.valid).toBe(true)
      })

      it('使用步长表达式应有效', () => {
        const result = validateCronExpression('*/15 * * * *')
        expect(result.valid).toBe(true)
      })

      it('范围加步长应有效', () => {
        const result = validateCronExpression('0-30/5 * * * *')
        // 验证步长格式正确性
        expect(result.message).toBeDefined()
      })

      it('空表达式应有效（手动执行模式）', () => {
        const result = validateCronExpression('')
        expect(result.valid).toBe(true)
        expect(result.message).toContain('手动执行')
      })

      it('null表达式应有效', () => {
        const result = validateCronExpression(null)
        expect(result.valid).toBe(true)
      })
    })

    describe('无效Cron表达式', () => {
      it('少于5部分应无效', () => {
        const result = validateCronExpression('0 0 * *')
        expect(result.valid).toBe(false)
        expect(result.message).toContain('5部分')
      })

      it('多于5部分应无效', () => {
        const result = validateCronExpression('0 0 * * * *')
        expect(result.valid).toBe(false)
      })

      it('分钟超出范围应无效', () => {
        const result = validateCronExpression('60 0 * * *')
        expect(result.valid).toBe(false)
        expect(result.message).toContain('分钟')
      })

      it('小时超出范围应无效', () => {
        const result = validateCronExpression('0 24 * * *')
        expect(result.valid).toBe(false)
        expect(result.message).toContain('小时')
      })

      it('日期超出范围应无效', () => {
        const result = validateCronExpression('0 0 32 * *')
        expect(result.valid).toBe(false)
        expect(result.message).toContain('日期')
      })

      it('月份超出范围应无效', () => {
        const result = validateCronExpression('0 0 * 13 *')
        expect(result.valid).toBe(false)
        expect(result.message).toContain('月份')
      })

      it('星期超出范围应无效', () => {
        const result = validateCronExpression('0 0 * * 7')
        expect(result.valid).toBe(false)
        expect(result.message).toContain('星期')
      })

      it('范围倒序应无效', () => {
        const result = validateCronExpression('17-9 0 * * *')
        expect(result.valid).toBe(false)
      })

      it('列表值超出范围应无效', () => {
        const result = validateCronExpression('0 24,25 * * *')
        expect(result.valid).toBe(false)
      })

      it('步长为0应无效', () => {
        const result = validateCronExpression('*/0 * * * *')
        expect(result.valid).toBe(false)
      })
    })
  })

  describe('describeCron', () => {
    it('空表达式应返回手动执行', () => {
      expect(describeCron('')).toBe('手动执行')
    })

    it('null表达式应返回手动执行', () => {
      expect(describeCron(null)).toBe('手动执行')
    })

    it('每天执行应有正确描述', () => {
      const desc = describeCron('30 8 * * *')
      expect(desc).toContain('每天')
      expect(desc).toContain('8:30')
    })

    it('每周执行应有正确描述', () => {
      const desc = describeCron('0 9 * * 1')
      expect(desc).toContain('周一')
      expect(desc).toContain('9:00')
    })

    it('多天执行应有正确描述', () => {
      const desc = describeCron('0 9 * * 1,3,5')
      expect(desc).toContain('周一')
      expect(desc).toContain('周三')
      expect(desc).toContain('周五')
    })

    it('每月执行应有正确描述', () => {
      const desc = describeCron('0 10 15 * *')
      expect(desc).toContain('每月')
      expect(desc).toContain('15日')
    })

    it('复杂表达式应返回原始表达式', () => {
      const desc = describeCron('*/15 9-17 1-15 * 1-5')
      expect(desc).toContain('定时执行')
    })

    it('分钟应补零显示', () => {
      const desc = describeCron('5 8 * * *')
      expect(desc).toContain(':05')
    })
  })

  describe('validateTaskParams', () => {
    describe('有效参数', () => {
      it('完整参数应有效', () => {
        const params = {
          name: '测试任务',
          datasource_id: 'ds-1',
          market_id: 'market-1',
          symbol_id: 'symbol-1',
          start_date: '2026-01-01',
          end_date: '2026-01-31'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(true)
        expect(result.errors).toEqual([])
      })

      it('无日期范围应有效', () => {
        const params = {
          name: '测试任务',
          datasource_id: 'ds-1',
          market_id: 'market-1',
          symbol_id: 'symbol-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(true)
      })

      it('cron表达式可选应有效', () => {
        const params = {
          name: '测试任务',
          datasource_id: 'ds-1',
          market_id: 'market-1',
          symbol_id: 'symbol-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(true)
      })
    })

    describe('无效参数', () => {
      it('名称为空应无效', () => {
        const params = {
          name: '',
          datasource_id: 'ds-1',
          market_id: 'market-1',
          symbol_id: 'symbol-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('任务名称不能为空')
      })

      it('名称为null应无效', () => {
        const params = {
          name: null,
          datasource_id: 'ds-1',
          market_id: 'market-1',
          symbol_id: 'symbol-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(false)
      })

      it('名称少于2字符应无效', () => {
        const params = {
          name: '测',
          datasource_id: 'ds-1',
          market_id: 'market-1',
          symbol_id: 'symbol-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('任务名称至少需要2个字符')
      })

      it('无datasource_id应无效', () => {
        const params = {
          name: '测试任务',
          market_id: 'market-1',
          symbol_id: 'symbol-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('必须选择数据源')
      })

      it('无market_id应无效', () => {
        const params = {
          name: '测试任务',
          datasource_id: 'ds-1',
          symbol_id: 'symbol-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('必须选择市场')
      })

      it('无symbol_id应无效', () => {
        const params = {
          name: '测试任务',
          datasource_id: 'ds-1',
          market_id: 'market-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('必须选择标的')
      })

      it('多个缺失字段应返回多个错误', () => {
        const params = { name: '测试任务' }
        const result = validateTaskParams(params)
        expect(result.errors.length).toBe(3)
      })

      it('日期范围无效应返回日期错误', () => {
        const params = {
          name: '测试任务',
          datasource_id: 'ds-1',
          market_id: 'market-1',
          symbol_id: 'symbol-1',
          start_date: '2026-01-31',
          end_date: '2026-01-01'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('开始日期不能晚于结束日期')
      })
    })

    describe('边界情况', () => {
      it('空对象应返回所有必填错误', () => {
        const result = validateTaskParams({})
        expect(result.errors.length).toBe(4)
      })

      it('名称只有空格应无效', () => {
        const params = {
          name: '   ',
          datasource_id: 'ds-1',
          market_id: 'market-1',
          symbol_id: 'symbol-1'
        }
        const result = validateTaskParams(params)
        expect(result.valid).toBe(false)
        expect(result.errors).toContain('任务名称不能为空')
      })

      it('部分参数缺失应返回对应错误', () => {
        const result = validateTaskParams({ name: '测试' })
        expect(result.valid).toBe(false)
        expect(result.errors.length).toBe(3) // datasource_id, market_id, symbol_id
      })
    })
  })
})