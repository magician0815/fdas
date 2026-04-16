/**
 * 数据源API.
 *
 * 提供数据源的列表查询、货币对同步等接口.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 */

import request from './index'

/**
 * 获取数据源列表.
 *
 * @returns {Promise} API响应
 */
export function getDatasources() {
  return request.get('/api/v1/datasources')
}

/**
 * 实时获取货币对并比较变更.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function fetchAndCompareSymbols(datasourceId) {
  return request.post(`/api/v1/datasources/${datasourceId}/symbols/fetch`)
}

/**
 * 更新数据源支持的货币对列表（存储到supported_symbols字段）.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function updateSupportedSymbols(datasourceId) {
  return request.put(`/api/v1/datasources/${datasourceId}/symbols`)
}

/**
 * 从数据源同步货币对到数据库（创建ForexSymbol记录）.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function syncSymbolsToDatabase(datasourceId) {
  return request.post(`/api/v1/datasources/${datasourceId}/sync-to-database`)
}