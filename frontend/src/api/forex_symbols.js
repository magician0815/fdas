/**
 * 外汇标的API.
 *
 * 提供外汇标的的列表查询接口.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 */

import request from './index'

/**
 * 获取外汇标的列表.
 *
 * @param {boolean} activeOnly - 是否只返回启用的标的
 * @returns {Promise} API响应
 */
export function getForexSymbols(activeOnly = true) {
  return request.get('/api/v1/forex-symbols', { params: { active_only: activeOnly } })
}