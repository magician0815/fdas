/**
 * 用户偏好状态管理 (Pinia Store).
 *
 * 替代当前分散在各处的 localStorage 直接调用.
 * 支持按 symbolId 记忆图表视图状态.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChartType, PriceAxisType } from './chart'

const STORAGE_KEY = 'fdas_chart_preferences'

interface ViewState {
  chartType: ChartType
  priceAxisType: PriceAxisType
  visibleMA: string[]
  yAxisMode: 'auto' | 'manual'
  manualYRange: { min: number; max: number } | null
}

interface StoredData {
  theme?: string
  viewStates?: Record<string, ViewState>
}

function load(): StoredData {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function save(data: StoredData): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

export const usePreferenceStore = defineStore('preferences', () => {
  const stored = load()

  const theme = ref<string>(stored.theme || 'light')

  /** 按 symbolId 保存视图状态 */
  function saveViewState(symbolId: string, state: ViewState): void {
    const current = load()
    if (!current.viewStates) current.viewStates = {}
    current.viewStates[symbolId] = state
    save(current)
  }

  /** 按 symbolId 恢复视图状态 */
  function restoreViewState(symbolId: string): ViewState | null {
    const current = load()
    return current.viewStates?.[symbolId] || null
  }

  /** 清除指定 symbol 的视图记忆 */
  function clearViewState(symbolId: string): void {
    const current = load()
    if (current.viewStates) {
      delete current.viewStates[symbolId]
      save(current)
    }
  }

  function saveTheme(t: string): void {
    theme.value = t
    const current = load()
    current.theme = t
    save(current)
  }

  return { theme, saveViewState, restoreViewState, clearViewState, saveTheme }
})
