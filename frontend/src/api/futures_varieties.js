/**
 * 期货品种API.
 *
 * 提供期货品种的列表查询、CRUD等功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-23
 */

import request from './index'

/**
 * 获取期货品种列表.
 *
 * @param {object} params - 查询参数
 * @param {boolean} params.activeOnly - 是否只返回启用的品种（默认true）
 * @param {string} params.search - 搜索代码或名称（可选）
 * @returns {Promise} API响应
 */
export function getFuturesVarieties(params = {}) {
  return request.get('/api/v1/futures-varieties/', { params })
}

/**
 * 获取期货品种详情.
 *
 * @param {string} varietyId - 品种ID
 * @returns {Promise} API响应
 */
export function getFuturesVariety(varietyId) {
  return request.get(`/api/v1/futures-varieties/${varietyId}`)
}

/**
 * 创建期货品种.
 *
 * @param {object} data - 品种数据
 * @returns {Promise} API响应
 */
export function createFuturesVariety(data) {
  return request.post('/api/v1/futures-varieties/', data)
}

/**
 * 更新期货品种.
 *
 * @param {string} varietyId - 品种ID
 * @param {object} data - 更新的数据
 * @returns {Promise} API响应
 */
export function updateFuturesVariety(varietyId, data) {
  return request.put(`/api/v1/futures-varieties/${varietyId}`, data)
}

/**
 * 删除期货品种.
 *
 * @param {string} varietyId - 品种ID
 * @returns {Promise} API响应
 */
export function deleteFuturesVariety(varietyId) {
  return request.delete(`/api/v1/futures-varieties/${varietyId}`)
}