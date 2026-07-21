/**
 * 债券行情数据API.
 *
 * 提供债券日线行情数据的查询功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-23
 */

import request from './index'

/**
 * 获取债券日线行情数据.
 *
 * @param {object} params - 查询参数
 * @param {string} params.symbolId - 债券ID（可选）
 * @param {string} params.marketId - 市场ID（可选）
 * @param {string} params.startDate - 开始日期（可选）
 * @param {string} params.endDate - 结束日期（可选）
 * @param {number} params.limit - 数据条数限制（默认1000）
 * @returns {Promise} API响应
 */
export function getBondDailyData(params = {}) {
  return request.get('/api/v1/bond/data/', { params })
}

/**
 * 获取指定债券的最新数据.
 *
 * @param {string} symbolId - 债券ID
 * @returns {Promise} API响应
 */
export function getBondLatestData(symbolId) {
  return request.get(`/api/v1/bond/data/${symbolId}/latest`)
}

/**
 * 获取指定债券的最新数据日期.
 *
 * @param {string} symbolId - 债券ID
 * @returns {Promise} API响应
 */
export function getBondLatestDate(symbolId) {
  return request.get(`/api/v1/bond/data/${symbolId}/latest-date`)
}

/** 搜索债券标的 */
export function searchSymbols(query) {
  return request.get('/api/v1/bond-symbols/', { params: { search: query, limit: 20 } })
}

/** 获取债券K线图表数据 */
export function getChartData(symbolId, period = 'daily') {
  return request.get('/api/v1/bond/data/', { params: { symbol_id: symbolId, period } })
}

export default { searchSymbols, getChartData, getBondDailyData, getBondLatestData, getBondLatestDate }