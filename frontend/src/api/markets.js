/**
 * 市场类型API.
 *
 * 提供市场类型的查询接口.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 */

import request from './index'

/**
 * 获取市场类型列表.
 *
 * @returns {Promise} API响应
 */
export function getMarkets() {
  return request.get('/api/v1/markets')
}