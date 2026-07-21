/**
 * KLineChart 自定义扩展统一入口.
 *
 * 在 main.ts 中调用 registerAllExtensions() 一次性注册所有扩展.
 * 所有扩展（指标、覆盖层、主题）注册后对所有 KLineChart 实例生效.
 * 借鉴 KLineChart 的全局 register 模式.
 */

import { registerChartThemes } from './themes'

// 副作用导入：各模块顶层调用 registerIndicator/registerOverlay 进行全局注册
// 失败时仅 warn 不阻断应用启动（各模块独立，互不影响）
import './limitUpDown'
import './openInterest'
import './yieldSpread'
import './gapMarker'
import './dividendMarker'

/**
 * 注册所有自定义扩展和主题.
 * 在应用启动时调用一次即可.
 * 副作用导入的扩展已在模块加载时自动注册.
 */
export function registerAllExtensions(): void {
  registerChartThemes()
}
