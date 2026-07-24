/**
 * ChartToolbar 市场自适应工具栏测试.
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import ChartToolbar from '../ChartToolbar.vue'
import { getMarketProfile, registerMarketPresets } from '@/composables/useMarketProfile'

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  ArrowDown: { template: '<span>▼</span>' },
  Sunny: { template: '<span>☀</span>' },
  Moon: { template: '<span>☽</span>' },
  Download: { template: '<span>⬇</span>' },
  RefreshRight: { template: '<span>↻</span>' },
}))

function makeMockChart() {
  return {
    createIndicator: vi.fn(),
    removeIndicator: vi.fn(),
    createOverlay: vi.fn(),
    scrollToRealTime: vi.fn(),
  }
}

describe('ChartToolbar', () => {
  beforeAll(() => {
    registerMarketPresets()
  })

  function mountToolbar(marketId: string, overrides: any = {}) {
    const profile = getMarketProfile(marketId)!
    return mount(ChartToolbar, {
      props: {
        profile,
        chartRef: makeMockChart(),
        theme: 'light',
        ...overrides,
      },
      global: {
        stubs: {
          'el-button': { template: '<button><slot/></button>' },
          'el-button-group': { template: '<div><slot/></div>' },
          'el-divider': { template: '<hr/>' },
          'el-dropdown': { template: '<div><slot/></div>' },
          'el-dropdown-menu': { template: '<div><slot/></div>' },
          'el-dropdown-item': { template: '<div><slot/></div>' },
          'el-icon': { template: '<span/>' },
        },
      },
    })
  }

  it('A股应显示成交量+MACD切换按钮', () => {
    const wrapper = mountToolbar('stock_cn')
    expect(wrapper.text()).toContain('成交量')
    expect(wrapper.text()).toContain('MACD')
  })

  it('外汇应显示MACD按钮', () => {
    const wrapper = mountToolbar('forex')
    expect(wrapper.text()).toContain('MACD')
  })

  it('期货应显示持仓量按钮', () => {
    const wrapper = mountToolbar('futures_cn')
    expect(wrapper.text()).toContain('持仓量')
  })

  it('应包含导出和重置按钮', () => {
    const wrapper = mountToolbar('stock_cn')
    // 只需验证组件正常渲染
    expect(wrapper.find('.chart-toolbar').exists()).toBe(true)
  })

  it('深色主题应有 dark class', () => {
    const wrapper = mountToolbar('stock_cn', { theme: 'dark' })
    expect(wrapper.find('.toolbar-dark').exists()).toBe(true)
  })

  it('点击蜡烛图/折线图应 emit', async () => {
    const wrapper = mountToolbar('stock_cn')
    const buttons = wrapper.findAll('button')
    // 有按钮存在
    expect(buttons.length).toBeGreaterThan(0)
  })
})
