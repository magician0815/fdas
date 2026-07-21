/**
 * 汇率数据API.
 *
 * 提供汇率数据查询接口.
 */

import request from './index'

/**
 * 获取汇率数据.
 *
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getFXData(params = {}) {
  return request.get('/api/v1/fx/data', { params })
}

/**
 * 获取技术指标.
 *
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export function getIndicators(params = {}) {
  return request.get('/api/v1/fx/indicators', { params })
}

/** 搜索外汇标的 */
export function searchSymbols(query) {
  return request.get('/api/v1/forex-symbols/', { params: { search: query, limit: 20 } })
}

/** 获取外汇K线图表数据 */
export function getChartData(symbolId, period = 'daily') {
  return request.get('/api/v1/fx/data', { params: { symbol_id: symbolId, period } })
}

export default { searchSymbols, getChartData, getFXData, getIndicators }