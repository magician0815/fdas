/**
 * 股票行情数据API.
 *
 * 提供股票日线行情数据的查询功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-23
 */

import request from './index'

/**
 * 获取股票日线行情数据.
 *
 * @param {object} params - 查询参数
 * @param {string} params.symbolId - 股票ID（可选）
 * @param {string} params.marketId - 市场ID（可选）
 * @param {string} params.startDate - 开始日期（可选）
 * @param {string} params.endDate - 结束日期（可选）
 * @param {number} params.limit - 数据条数限制（默认1000）
 * @returns {Promise} API响应
 */
export function getStockDailyData(params = {}) {
  return request.get('/api/v1/stock/data/', { params })
}

/**
 * 获取指定股票的最新数据.
 *
 * @param {string} symbolId - 股票ID
 * @returns {Promise} API响应
 */
export function getStockLatestData(symbolId) {
  return request.get(`/api/v1/stock/data/${symbolId}/latest`)
}

/**
 * 获取指定股票的最新数据日期.
 *
 * @param {string} symbolId - 股票ID
 * @returns {Promise} API响应
 */
export function getStockLatestDate(symbolId) {
  return request.get(`/api/v1/stock/data/${symbolId}/latest-date`)
}

/**
 * 获取股票复权日线数据（实时从AKShare获取）.
 *
 * @param {object} params - 查询参数
 * @param {string} params.symbolCode - 股票代码（如 sh600519）
 * @param {string} params.adjust - 复权类型: ''=不复权, 'qfq'=前复权, 'hfq'=后复权
 * @param {string} params.startDate - 开始日期（可选）
 * @param {string} params.endDate - 结束日期（可选）
 * @param {number} params.limit - 数据条数限制（默认1000）
 * @returns {Promise} API响应
 */
export function getStockAdjustedData(params = {}) {
  return request.get('/api/v1/stock/data/adjusted', { params })
}