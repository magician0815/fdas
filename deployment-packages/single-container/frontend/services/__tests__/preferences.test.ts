/**
 * Preferences Service 测试.
 *
 * 测试用户偏好统一管理服务.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { preferencesService, PreferenceKeys } from '../preferences'

// Mock localStorage
const localStorageMock = {
  store: {} as Record<string, string>,
  getItem: vi.fn((key: string) => localStorageMock.store[key] || null),
  setItem: vi.fn((key: string, value: string) => {
    localStorageMock.store[key] = value
  }),
  removeItem: vi.fn((key: string) => {
    delete localStorageMock.store[key]
  }),
  clear: vi.fn(() => {
    localStorageMock.store = {}
  })
}

vi.stubGlobal('localStorage', localStorageMock)

describe('Preferences Service', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    localStorageMock.clear()
  })

  describe('get方法', () => {
    it('应该返回默认值当localStorage无数据', () => {
      const chartType = preferencesService.get(PreferenceKeys.CHART_TYPE)
      expect(chartType).toBe('candle')
    })

    it('应该返回存储的值当localStorage有数据', () => {
      localStorageMock.setItem('fdas_prefs_chartType', 'line')
      const chartType = preferencesService.get(PreferenceKeys.CHART_TYPE)
      expect(chartType).toBe('line')
    })

    it('应该正确解析数组类型偏好', () => {
      localStorageMock.setItem('fdas_prefs_visibleMA', JSON.stringify(['5', '10', '20']))
      const visibleMA = preferencesService.get(PreferenceKeys.VISIBLE_MA)
      expect(visibleMA).toEqual(['5', '10', '20'])
    })

    it('应该正确解析布尔类型偏好', () => {
      localStorageMock.setItem('fdas_prefs_showRightAxis', 'true')
      const showRightAxis = preferencesService.get(PreferenceKeys.SHOW_RIGHT_AXIS)
      expect(showRightAxis).toBe(true)
    })

    it('应该正确解析数字类型偏好', () => {
      localStorageMock.setItem('fdas_prefs_drawingWidth', JSON.stringify(3))
      const drawingWidth = preferencesService.get(PreferenceKeys.DRAWING_WIDTH)
      expect(drawingWidth).toBe(3)
    })
  })

  describe('set方法', () => {
    it('应该正确存储字符串值', () => {
      preferencesService.set(PreferenceKeys.CHART_TYPE, 'line')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('fdas_prefs_chartType', 'line')
    })

    it('应该正确存储数组值（JSON序列化）', () => {
      preferencesService.set(PreferenceKeys.VISIBLE_MA, ['5', '10', '30'])
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'fdas_prefs_visibleMA',
        JSON.stringify(['5', '10', '30'])
      )
    })

    it('应该正确存储布尔值', () => {
      preferencesService.set(PreferenceKeys.SHOW_RIGHT_AXIS, true)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('fdas_prefs_showRightAxis', 'true')
    })

    it('应该正确存储数字值', () => {
      preferencesService.set(PreferenceKeys.DRAWING_WIDTH, 4)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('fdas_prefs_drawingWidth', '4')
    })
  })

  describe('remove方法', () => {
    it('应该正确删除偏好', () => {
      localStorageMock.setItem('fdas_prefs_chartType', 'line')
      preferencesService.remove(PreferenceKeys.CHART_TYPE)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('fdas_prefs_chartType')
    })
  })

  describe('getAll方法', () => {
    it('应该返回所有偏好', () => {
      localStorageMock.setItem('fdas_prefs_chartType', 'line')
      localStorageMock.setItem('fdas_prefs_theme', 'dark')
      const allPrefs = preferencesService.getAll()
      expect(allPrefs.chartType).toBe('line')
      expect(allPrefs.theme).toBe('dark')
    })

    it('应该返回默认值当无存储数据', () => {
      const allPrefs = preferencesService.getAll()
      expect(allPrefs.chartType).toBe('candle')
      expect(allPrefs.theme).toBe('light')
    })
  })

  describe('clearAll方法', () => {
    it('应该清除所有FDAS偏好', () => {
      localStorageMock.setItem('fdas_prefs_chartType', 'line')
      localStorageMock.setItem('fdas_prefs_theme', 'dark')
      localStorageMock.setItem('other_key', 'other_value')

      preferencesService.clearAll()

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('fdas_prefs_chartType')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('fdas_prefs_theme')
      expect(localStorageMock.removeItem).not.toHaveBeenCalledWith('other_key')
    })
  })

  describe('setBatch方法', () => {
    it('应该批量设置多个偏好', () => {
      preferencesService.setBatch({
        chartType: 'line',
        theme: 'dark',
        showRightAxis: true
      })

      expect(localStorageMock.setItem).toHaveBeenCalledWith('fdas_prefs_chartType', 'line')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('fdas_prefs_theme', 'dark')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('fdas_prefs_showRightAxis', 'true')
    })

    it('应该跳过undefined值', () => {
      preferencesService.setBatch({
        chartType: 'line',
        theme: undefined
      })

      expect(localStorageMock.setItem).toHaveBeenCalledWith('fdas_prefs_chartType', 'line')
      expect(localStorageMock.setItem).not.toHaveBeenCalledWith('fdas_prefs_theme')
    })
  })

  describe('reset方法', () => {
    it('应该重置为默认偏好', () => {
      localStorageMock.setItem('fdas_prefs_chartType', 'line')
      localStorageMock.setItem('fdas_prefs_theme', 'dark')

      preferencesService.reset()

      const chartType = preferencesService.get(PreferenceKeys.CHART_TYPE)
      const theme = preferencesService.get(PreferenceKeys.THEME)
      expect(chartType).toBe('candle')  // 默认值
      expect(theme).toBe('light')       // 默认值
    })
  })

  describe('PreferenceKeys常量', () => {
    it('应该包含所有预期键名', () => {
      expect(PreferenceKeys.CHART_TYPE).toBe('chartType')
      expect(PreferenceKeys.VISIBLE_MA).toBe('visibleMA')
      expect(PreferenceKeys.THEME).toBe('theme')
      expect(PreferenceKeys.DRAWING_COLOR).toBe('drawingColor')
    })
  })

  describe('边界情况', () => {
    it('应该处理无效JSON数据', () => {
      localStorageMock.setItem('fdas_prefs_visibleMA', 'invalid-json')
      const visibleMA = preferencesService.get(PreferenceKeys.VISIBLE_MA)
      // 应该返回默认值
      expect(visibleMA).toEqual(['5', '10', '20', '60'])
    })

    it('应该处理空字符串值', () => {
      localStorageMock.setItem('fdas_prefs_lastSymbolId', '')
      const lastSymbolId = preferencesService.get(PreferenceKeys.LAST_SYMBOL_ID)
      expect(lastSymbolId).toBe('')
    })
  })
})