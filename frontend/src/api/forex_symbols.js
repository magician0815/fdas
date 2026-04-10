/**
 * 外汇标的API.
 *
 * 提供外汇标的的CRUD、列表查询等接口.
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

/**
 * 获取外汇标的详情.
 *
 * @param {string} symbolId - 标的ID
 * @returns {Promise} API响应
 */
export function getForexSymbol(symbolId) {
  return request.get(`/api/v1/forex-symbols/${symbolId}`)
}

/**
 * 根据代码获取外汇标的.
 *
 * @param {string} code - 标的代码
 * @returns {Promise} API响应
 */
export function getForexSymbolByCode(code) {
  return request.get(`/api/v1/forex-symbols/code/${code}`)
}

/**
 * 创建外汇标的.
 *
 * @param {Object} data - 标的数据
 * @returns {Promise} API响应
 */
export function createForexSymbol(data) {
  return request.post('/api/v1/forex-symbols', data)
}

/**
 * 更新外汇标的.
 *
 * @param {string} symbolId - 标的ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateForexSymbol(symbolId, data) {
  return request.put(`/api/v1/forex-symbols/${symbolId}`, data)
}

/**
 * 删除外汇标的.
 *
 * @param {string} symbolId - 标的ID
 * @returns {Promise} API响应
 */
export function deleteForexSymbol(symbolId) {
  return request.delete(`/api/v1/forex-symbols/${symbolId}`)
}