/**
 * 前端校验函数库.
 *
 * 提供通用的数据校验函数.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 */

/**
 * 验证日期范围.
 *
 * @param {Date|string} startDate - 开始日期
 * @param {Date|string} endDate - 结束日期
 * @param {Date|string} minDate - 最小日期限制
 * @returns {Object} 校验结果 { valid: boolean, errors: string[] }
 */
export function validateDateRange(startDate, endDate, minDate = null) {
  const errors = []
  const today = new Date()

  // 转换为Date对象
  const start = startDate instanceof Date ? startDate : new Date(startDate)
  const end = endDate instanceof Date ? endDate : new Date(endDate)
  const min = minDate ? (minDate instanceof Date ? minDate : new Date(minDate)) : null

  if (startDate && endDate) {
    if (start > end) {
      errors.push('开始日期不能晚于结束日期')
    }

    if (end > today) {
      errors.push('结束日期不能超过今天')
    }

    if (min && start < min) {
      errors.push(`开始日期不能早于${formatDate(min)}`)
    }
  }

  return { valid: errors.length === 0, errors }
}

/**
 * 验证Cron表达式.
 *
 * @param {string} cronExpr - Cron表达式
 * @returns {Object} 校验结果 { valid: boolean, message: string }
 */
export function validateCronExpression(cronExpr) {
  if (!cronExpr) {
    return { valid: true, message: '未配置定时执行（手动执行模式）' }
  }

  const parts = cronExpr.trim().split(/\s+/)

  if (parts.length !== 5) {
    return { valid: false, message: 'Cron表达式格式错误，应为5部分（分 时 日 月 周）' }
  }

  // 简单验证各部分格式
  const [minute, hour, dayOfMonth, month, dayOfWeek] = parts

  // 验证分钟 (0-59)
  if (!isValidCronPart(minute, 0, 59)) {
    return { valid: false, message: '分钟部分格式错误（0-59）' }
  }

  // 验证小时 (0-23)
  if (!isValidCronPart(hour, 0, 23)) {
    return { valid: false, message: '小时部分格式错误（0-23）' }
  }

  // 验证日 (1-31)
  if (!isValidCronPart(dayOfMonth, 1, 31)) {
    return { valid: false, message: '日期部分格式错误（1-31）' }
  }

  // 验证月 (1-12)
  if (!isValidCronPart(month, 1, 12)) {
    return { valid: false, message: '月份部分格式错误（1-12）' }
  }

  // 验证周 (0-6)
  if (!isValidCronPart(dayOfWeek, 0, 6)) {
    return { valid: false, message: '星期部分格式错误（0-6）' }
  }

  return { valid: true, message: describeCron(cronExpr) }
}

/**
 * 验证Cron单个部分.
 *
 * @param {string} part - Cron部分值
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {boolean} 是否有效
 */
function isValidCronPart(part, min, max) {
  if (part === '*') return true

  // 处理范围 (如 1-5)
  if (part.includes('-')) {
    const [start, end] = part.split('-').map(Number)
    return start >= min && end <= max && start <= end
  }

  // 处理列表 (如 1,3,5)
  if (part.includes(',')) {
    const values = part.split(',').map(Number)
    return values.every(v => v >= min && v <= max)
  }

  // 处理步长 (如 */5 或 1-10/2)
  if (part.includes('/')) {
    const [base, step] = part.split('/')
    if (base === '*') {
      return Number(step) > 0
    }
    if (base.includes('-')) {
      const [start, end] = base.split('-').map(Number)
      return start >= min && end <= max && Number(step) > 0
    }
    return Number(base) >= min && Number(base) <= max && Number(step) > 0
  }

  // 单个数字
  const num = Number(part)
  return num >= min && num <= max
}

/**
 * 描述Cron表达式.
 *
 * @param {string} cronExpr - Cron表达式
 * @returns {string} 中文描述
 */
export function describeCron(cronExpr) {
  if (!cronExpr) return '手动执行'

  const parts = cronExpr.trim().split(/\s+/)
  const [minute, hour, dayOfMonth, month, dayOfWeek] = parts

  // 每天执行
  if (dayOfMonth === '*' && month === '*' && dayOfWeek === '*') {
    return `每天 ${hour}:${minute.padStart(2, '0')} 执行`
  }

  // 每周执行
  if (dayOfMonth === '*' && month === '*' && dayOfWeek !== '*') {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const dayNames = dayOfWeek.split(',').map(d => days[Number(d)] || days[d]).join('、')
    return `每${dayNames} ${hour}:${minute.padStart(2, '0')} 执行`
  }

  // 每月执行
  if (dayOfMonth !== '*' && month === '*' && dayOfWeek === '*') {
    return `每月${dayOfMonth}日 ${hour}:${minute.padStart(2, '0')} 执行`
  }

  return `定时执行: ${cronExpr}`
}

/**
 * 验证任务参数完整性.
 *
 * @param {Object} params - 任务参数
 * @returns {Object} 校验结果 { valid: boolean, errors: string[] }
 */
export function validateTaskParams(params) {
  const errors = []

  // 必填项检查
  if (!params.name?.trim()) {
    errors.push('任务名称不能为空')
  } else if (params.name.trim().length < 2) {
    errors.push('任务名称至少需要2个字符')
  }

  if (!params.datasource_id) {
    errors.push('必须选择数据源')
  }

  if (!params.market_id) {
    errors.push('必须选择市场')
  }

  if (!params.symbol_id) {
    errors.push('必须选择标的')
  }

  // 日期范围校验
  if (params.start_date && params.end_date) {
    const dateResult = validateDateRange(params.start_date, params.end_date, params.min_date)
    if (!dateResult.valid) {
      errors.push(...dateResult.errors)
    }
  }

  return { valid: errors.length === 0, errors }
}

/**
 * 格式化日期显示.
 *
 * @param {Date|string} date - 日期
 * @returns {string} 格式化后的日期字符串
 */
function formatDate(date) {
  if (!date) return ''
  const d = date instanceof Date ? date : new Date(date)
  return d.toLocaleDateString('zh-CN')
}