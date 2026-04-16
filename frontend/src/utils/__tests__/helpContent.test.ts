/**
 * 前端使用帮助内容数据测试.
 *
 * 测试帮助内容章节结构和内容完整性.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect } from 'vitest'
import {
  getChartHelpContent,
  getDataManagementHelpContent,
  getShortcutsHelpContent,
  getAllHelpContent
} from '../helpContent'

describe('HelpContent 帮助内容', () => {
  describe('getChartHelpContent 图表操作帮助', () => {
    it('应返回帮助章节数组', () => {
      const result = getChartHelpContent()
      expect(Array.isArray(result)).toBe(true)
      expect(result.length).toBeGreaterThan(0)
    })

    it('每个章节应有title和items', () => {
      const result = getChartHelpContent()
      result.forEach(section => {
        expect(section).toHaveProperty('title')
        expect(section).toHaveProperty('items')
        expect(Array.isArray(section.items)).toBe(true)
        expect(typeof section.title).toBe('string')
      })
    })

    it('每个帮助项应有name和description', () => {
      const result = getChartHelpContent()
      result.forEach(section => {
        section.items.forEach(item => {
          expect(item).toHaveProperty('name')
          expect(item).toHaveProperty('description')
          expect(typeof item.name).toBe('string')
          expect(typeof item.description).toBe('string')
        })
      })
    })

    it('应包含K线图基础操作章节', () => {
      const result = getChartHelpContent()
      const basicOps = result.find(s => s.title === 'K线图基础操作')
      expect(basicOps).toBeDefined()
      expect(basicOps?.items.length).toBeGreaterThan(0)
    })

    it('应包含均线与技术指标章节', () => {
      const result = getChartHelpContent()
      const indicators = result.find(s => s.title.includes('均线') || s.title.includes('指标'))
      expect(indicators).toBeDefined()
    })

    it('应包含画线工具章节', () => {
      const result = getChartHelpContent()
      const drawing = result.find(s => s.title.includes('画线'))
      expect(drawing).toBeDefined()
    })

    it('鼠标滚轮操作应有说明', () => {
      const result = getChartHelpContent()
      const basicOps = result.find(s => s.title === 'K线图基础操作')
      const scrollItem = basicOps?.items.find(i => i.name === '鼠标滚轮')
      expect(scrollItem).toBeDefined()
      expect(scrollItem?.description).toContain('放大')
    })

    it('十字光标操作应有说明', () => {
      const result = getChartHelpContent()
      const crosshairSection = result.find(s => s.title.includes('十字光标'))
      expect(crosshairSection).toBeDefined()
    })

    it('快捷键应可选提供', () => {
      const result = getChartHelpContent()
      const itemsWithShortcut = result.flatMap(s => s.items.filter(i => i.shortcut))
      expect(itemsWithShortcut.length).toBeGreaterThan(0)
    })
  })

  describe('getDataManagementHelpContent 数据管理帮助', () => {
    it('应返回帮助章节数组', () => {
      const result = getDataManagementHelpContent()
      expect(Array.isArray(result)).toBe(true)
      expect(result.length).toBeGreaterThan(0)
    })

    it('应包含数据源管理章节', () => {
      const result = getDataManagementHelpContent()
      const datasource = result.find(s => s.title.includes('数据源'))
      expect(datasource).toBeDefined()
    })

    it('应包含采集任务管理章节', () => {
      const result = getDataManagementHelpContent()
      const tasks = result.find(s => s.title.includes('采集任务'))
      expect(tasks).toBeDefined()
    })

    it('应包含数据查询章节', () => {
      const result = getDataManagementHelpContent()
      const query = result.find(s => s.title.includes('数据查询'))
      expect(query).toBeDefined()
    })

    it('应包含数据导出章节', () => {
      const result = getDataManagementHelpContent()
      const exportSection = result.find(s => s.title.includes('数据导出'))
      expect(exportSection).toBeDefined()
    })

    it('Cron表达式应有说明', () => {
      const result = getDataManagementHelpContent()
      const tasks = result.find(s => s.title.includes('采集任务'))
      const cronItem = tasks?.items.find(i => i.name.includes('Cron'))
      expect(cronItem).toBeDefined()
      expect(cronItem?.description).toContain('定时')
    })

    it('导出格式应有说明', () => {
      const result = getDataManagementHelpContent()
      const exportSection = result.find(s => s.title.includes('数据导出'))
      const formatItem = exportSection?.items.find(i => i.name.includes('导出格式'))
      expect(formatItem).toBeDefined()
      expect(formatItem?.description).toContain('CSV')
    })
  })

  describe('getShortcutsHelpContent 快捷键帮助', () => {
    it('应返回帮助章节数组', () => {
      const result = getShortcutsHelpContent()
      expect(Array.isArray(result)).toBe(true)
      expect(result.length).toBeGreaterThan(0)
    })

    it('应包含图表操作快捷键章节', () => {
      const result = getShortcutsHelpContent()
      const chartShortcuts = result.find(s => s.title.includes('图表操作'))
      expect(chartShortcuts).toBeDefined()
    })

    it('应包含键盘精灵章节', () => {
      const result = getShortcutsHelpContent()
      const keyboardWizard = result.find(s => s.title.includes('键盘精灵'))
      expect(keyboardWizard).toBeDefined()
    })

    it('应包含页面导航章节', () => {
      const result = getShortcutsHelpContent()
      const navigation = result.find(s => s.title.includes('页面导航'))
      expect(navigation).toBeDefined()
    })

    it('所有快捷键项应有shortcut字段', () => {
      const result = getShortcutsHelpContent()
      result.forEach(section => {
        section.items.forEach(item => {
          expect(item.shortcut).toBeDefined()
          expect(typeof item.shortcut).toBe('string')
        })
      })
    })

    it('锁定光标快捷键应为Space', () => {
      const result = getShortcutsHelpContent()
      const chartShortcuts = result.find(s => s.title.includes('图表操作'))
      const lockItem = chartShortcuts?.items.find(i => i.name.includes('锁定'))
      expect(lockItem?.shortcut).toBe('Space')
    })

    it('重置视图快捷键应为ESC', () => {
      const result = getShortcutsHelpContent()
      const chartShortcuts = result.find(s => s.title.includes('图表操作'))
      const resetItem = chartShortcuts?.items.find(i => i.name.includes('重置'))
      expect(resetItem?.shortcut).toBe('ESC')
    })

    it('删除画线快捷键应为Delete', () => {
      const result = getShortcutsHelpContent()
      const chartShortcuts = result.find(s => s.title.includes('图表操作'))
      const deleteItem = chartShortcuts?.items.find(i => i.name.includes('删除'))
      expect(deleteItem?.shortcut).toBe('Delete')
    })

    it('复制数据快捷键应为Ctrl+C', () => {
      const result = getShortcutsHelpContent()
      const chartShortcuts = result.find(s => s.title.includes('图表操作'))
      const copyItem = chartShortcuts?.items.find(i => i.name.includes('复制'))
      expect(copyItem?.shortcut).toBe('Ctrl + C')
    })

    it('页面导航快捷键应使用Alt组合', () => {
      const result = getShortcutsHelpContent()
      const navigation = result.find(s => s.title.includes('页面导航'))
      navigation?.items.forEach(item => {
        expect(item.shortcut).toContain('Alt')
      })
    })
  })

  describe('getAllHelpContent 全部帮助内容', () => {
    it('应合并所有帮助内容', () => {
      const result = getAllHelpContent()
      const chart = getChartHelpContent()
      const data = getDataManagementHelpContent()
      const shortcuts = getShortcutsHelpContent()

      expect(result.length).toBe(chart.length + data.length + shortcuts.length)
    })

    it('应包含图表帮助内容', () => {
      const result = getAllHelpContent()
      const chartOps = result.find(s => s.title === 'K线图基础操作')
      expect(chartOps).toBeDefined()
    })

    it('应包含数据管理帮助内容', () => {
      const result = getAllHelpContent()
      const datasource = result.find(s => s.title.includes('数据源'))
      expect(datasource).toBeDefined()
    })

    it('应包含快捷键帮助内容', () => {
      const result = getAllHelpContent()
      const chartShortcuts = result.find(s => s.title.includes('图表操作快捷键'))
      expect(chartShortcuts).toBeDefined()
    })

    it('应返回非空数组', () => {
      const result = getAllHelpContent()
      expect(result.length).toBeGreaterThan(10)
    })
  })

  describe('HelpContent 内容完整性检查', () => {
    it('所有章节标题应为中文', () => {
      const allContent = getAllHelpContent()
      allContent.forEach(section => {
        // 检查是否包含中文字符
        expect(section.title).toMatch(/[\u4e00-\u9fa5]/)
      })
    })

    it('所有帮助项名称应为中文', () => {
      const allContent = getAllHelpContent()
      allContent.forEach(section => {
        section.items.forEach(item => {
          expect(item.name).toMatch(/[\u4e00-\u9fa5]/)
        })
      })
    })

    it('所有帮助项描述应为中文', () => {
      const allContent = getAllHelpContent()
      allContent.forEach(section => {
        section.items.forEach(item => {
          expect(item.description).toMatch(/[\u4e00-\u9fa5]/)
        })
      })
    })

    it('描述内容应详细（至少5字符）', () => {
      const allContent = getAllHelpContent()
      allContent.forEach(section => {
        section.items.forEach(item => {
          expect(item.description.length).toBeGreaterThan(5)
        })
      })
    })
  })
})