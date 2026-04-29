/**
 * 全局主题状态管理.
 *
 * 管理系统白天/夜间主题切换.
 *
 * Author: FDAS Team
 * Created: 2026-04-17
 */

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 主题状态：light（白天）或 dark（夜间）
  const theme = ref(localStorage.getItem('fdas_theme') || 'light')

  // 是否为夜间模式
  const isDark = ref(theme.value === 'dark')

  // 切换主题
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    isDark.value = theme.value === 'dark'
    applyTheme()
  }

  // 应用主题
  function applyTheme() {
    // 保存到localStorage
    localStorage.setItem('fdas_theme', theme.value)
    // 更新CSS变量
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // 监听主题变化
  watch(theme, () => {
    applyTheme()
  })

  // 初始化时应用主题
  applyTheme()

  return {
    theme,
    isDark,
    toggleTheme
  }
})