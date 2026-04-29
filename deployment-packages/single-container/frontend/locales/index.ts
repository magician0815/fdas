/**
 * 国际化语言配置.
 *
 * 支持中英文切换，使用vue-i18n.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import enUS from './locales/en-US'

// 获取保存的语言偏好或使用浏览器语言
const getSavedLocale = (): string => {
  // 优先从localStorage读取
  const saved = localStorage.getItem('fdas_locale')
  if (saved && (saved === 'zh-CN' || saved === 'en-US')) {
    return saved
  }

  // 检测浏览器语言
  const browserLang = navigator.language || navigator.userLanguage
  if (browserLang.startsWith('zh')) {
    return 'zh-CN'
  }

  // 默认中文
  return 'zh-CN'
}

// 创建i18n实例
const i18n = createI18n({
  legacy: false,
  locale: getSavedLocale(),
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  }
})

/**
 * 切换语言.
 */
export const switchLocale = (locale: string): void => {
  if (locale === 'zh-CN' || locale === 'en-US') {
    i18n.global.locale.value = locale as any
    localStorage.setItem('fdas_locale', locale)

    // 更新HTML lang属性
    document.documentElement.lang = locale === 'zh-CN' ? 'zh' : 'en'
  }
}

/**
 * 获取当前语言.
 */
export const getCurrentLocale = (): string => {
  return i18n.global.locale.value as string
}

/**
 * 获取支持的语言列表.
 */
export const getSupportedLocales = () => [
  { code: 'zh-CN', name: '简体中文', icon: '🇨🇳' },
  { code: 'en-US', name: 'English', icon: '🇺🇸' }
]

export default i18n