/**
 * 股票标的API.
 *
 * 提供股票标的的列表查询、CRUD等功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-23
 */

import request from './index'

/**
 * 获取股票标的列表.
 *
 * @param {object} params - 查询参数
 * @param {string} params.marketId - 市场ID（可选）
 * @param {boolean} params.activeOnly - 是否只返回启用的标的（默认true）
 * @param {string} params.search - 搜索代码或名称（可选）
 * @returns {Promise} API响应
 */
export function getStockSymbols(params = {}) {
  return request.get('/api/v1/stock-symbols/', { params })
}

/**
 * 获取股票标的详情.
 *
 * @param {string} symbolId - 标的ID
 * @returns {Promise} API响应
 */
export function getStockSymbol(symbolId) {
  return request.get(`/api/v1/stock-symbols/${symbolId}`)
}

/**
 * 根据代码获取股票标的.
 *
 * @param {string} code - 股票代码
 * @param {string} marketId - 市场ID（可选）
 * @returns {Promise} API响应
 */
export function getStockSymbolByCode(code, marketId = null) {
  return request.get(`/api/v1/stock-symbols/code/${code}`, { params: { market_id: marketId } })
}

/**
 * 创建股票标的.
 *
 * @param {object} data - 标的数据
 * @returns {Promise} API响应
 */
export function createStockSymbol(data) {
  return request.post('/api/v1/stock-symbols/', data)
}

/**
 * 更新股票标的.
 *
 * @param {string} symbolId - 标的ID
 * @param {object} data - 更新的数据
 * @returns {Promise} API响应
 */
export function updateStockSymbol(symbolId, data) {
  return request.put(`/api/v1/stock-symbols/${symbolId}`, data)
}

/**
 * 删除股票标的.
 *
 * @param {string} symbolId - 标的ID
 * @returns {Promise} API响应
 */
export function deleteStockSymbol(symbolId) {
  return request.delete(`/api/v1/stock-symbols/${symbolId}`)
}