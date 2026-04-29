/**
 * 日志服务.
 *
 * 提供统一的日志接口，生产环境可禁用详细日志.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

const isDevelopment = import.meta.env.DEV

const logger = {
  /**
   * 信息日志.
   *
   * @param {string} message - 日志消息
   * @param {...any} args - 附加参数
   */
  info: (message, ...args) => {
    if (isDevelopment) {
      console.log(`[INFO] ${message}`, ...args)
    }
  },

  /**
   * 警告日志.
   *
   * @param {string} message - 日志消息
   * @param {...any} args - 附加参数
   */
  warn: (message, ...args) => {
    if (isDevelopment) {
      console.warn(`[WARN] ${message}`, ...args)
    }
  },

  /**
   * 错误日志.
   *
   * 生产环境仅记录错误类型，不记录敏感信息.
   *
   * @param {string} message - 日志消息
   * @param {Error|any} error - 错误对象
   */
  error: (message, error) => {
    if (isDevelopment) {
      console.error(`[ERROR] ${message}`, error)
    } else {
      // 生产环境只记录错误类型
      console.error(`[ERROR] ${message}: ${error?.constructor?.name || 'Unknown'}`)
    }
  },

  /**
   * 调试日志（仅开发环境）.
   *
   * @param {string} message - 日志消息
   * @param {...any} args - 附加参数
   */
  debug: (message, ...args) => {
    if (isDevelopment) {
      console.debug(`[DEBUG] ${message}`, ...args)
    }
  }
}

export default logger