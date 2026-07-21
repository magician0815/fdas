/**
 * 期货行情数据API.
 *
 * 提供期货日线行情数据的查询功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-23
 */

import request from './index'

/**
 * 获取期货日线行情数据.
 *
 * @param {object} params - 查询参数
 * @param {string} params.contractId - 合约ID（可选）
 * @param {string} params.varietyId - 品种ID（可选）
 * @param {string} params.startDate - 开始日期（可选）
 * @param {string} params.endDate - 结束日期（可选）
 * @param {boolean} params.isMainData - 是否仅查询主力合约数据（可选）
 * @param {number} params.limit - 数据条数限制（默认1000）
 * @returns {Promise} API响应
 */
export function getFuturesDailyData(params = {}) {
  return request.get('/api/v1/futures/data/', { params })
}

/**
 * 获取指定合约的最新数据.
 *
 * @param {string} contractId - 合约ID
 * @returns {Promise} API响应
 */
export function getFuturesLatestData(contractId) {
  return request.get(`/api/v1/futures/data/${contractId}/latest`)
}

/**
 * 获取指定合约的最新数据日期.
 *
 * @param {string} contractId - 合约ID
 * @returns {Promise} API响应
 */
export function getFuturesLatestDate(contractId) {
  return request.get(`/api/v1/futures/data/${contractId}/latest-date`)
}

/** 搜索期货品种 */
export function searchSymbols(query) {
  return request.get('/api/v1/futures-varieties/', { params: { search: query, limit: 20 } })
}

/** 获取期货K线图表数据 */
export function getChartData(symbolId, period = 'daily') {
  return request.get('/api/v1/futures/data/', { params: { symbol_id: symbolId, period } })
}

export default { searchSymbols, getChartData, getFuturesDailyData, getFuturesLatestData, getFuturesLatestDate }