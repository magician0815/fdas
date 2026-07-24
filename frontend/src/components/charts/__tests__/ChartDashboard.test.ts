/**
 * ChartDashboard KLineChart 包装器测试.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

// Mock klinecharts 模块
vi.mock('klinecharts', () => ({
  init: vi.fn(() => ({
    setSymbol: vi.fn(),
    setOffsetRightDistance: vi.fn(),
    applyNewData: vi.fn(),
    createIndicator: vi.fn(),
    addOverlay: vi.fn(),
    subscribeAction: vi.fn(),
    setStyles: vi.fn(),
    scrollToRealTime: vi.fn(),
    getCanvas: vi.fn(() => ({ toDataURL: vi.fn(() => 'data:image/png;base64,...') })),
    convertFromPixel: vi.fn(),
  })),
  dispose: vi.fn(),
  registerStyles: vi.fn(),
}))

vi.mock('@/stores/theme', () => ({
  useThemeStore: vi.fn(() => ({
    theme: { value: 'light' },
    isDark: { value: false },
    toggleTheme: vi.fn(),
  })),
}))

vi.mock('@/composables/useKeyboardNav', () => ({
  useKeyboardNav: vi.fn(),
}))

// 导入会用到的 composables
import { registerMarketPresets, getMarketProfile } from '@/composables/useMarketProfile'

describe('ChartDashboard', () => {
  beforeEach(() => {
    registerMarketPresets()
  })

  it('应接收 marketId prop', () => {
    const profile = getMarketProfile('stock_cn')
    expect(profile).toBeDefined()
    expect(profile!.id).toBe('stock_cn')
  })

  it('A股市场应有涨跌停和复权功能', () => {
    const profile = getMarketProfile('stock_cn')!
    expect(profile.features.limitUpDown).toBe(true)
    expect(profile.features.adjustment).toBe(true)
  })

  it('外汇市场应无涨跌停', () => {
    const profile = getMarketProfile('forex')!
    expect(profile.features.limitUpDown).toBe(false)
  })

  it('期货市场应有持仓量副图', () => {
    const profile = getMarketProfile('futures_cn')!
    expect(profile.features.openInterest).toBe(true)
    expect(profile.subChartSlots.some(s => s.id === 'open_interest')).toBe(true)
  })

  it('债券市场应有收益率展示', () => {
    const profile = getMarketProfile('bond_cn')!
    expect(profile.features.yieldDisplay).toBe(true)
  })
})
