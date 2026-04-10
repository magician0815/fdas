/**
 * 数据源API.
 *
 * 提供数据源的CRUD、货币对同步等接口.
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
 * 获取数据源详情.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function getDatasource(datasourceId) {
  return request.get(`/api/v1/datasources/${datasourceId}`)
}

/**
 * 创建数据源.
 *
 * @param {Object} data - 数据源数据
 * @returns {Promise} API响应
 */
export function createDatasource(data) {
  return request.post('/api/v1/datasources', data)
}

/**
 * 更新数据源.
 *
 * @param {string} datasourceId - 数据源ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateDatasource(datasourceId, data) {
  return request.put(`/api/v1/datasources/${datasourceId}`, data)
}

/**
 * 删除数据源.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function deleteDatasource(datasourceId) {
  return request.delete(`/api/v1/datasources/${datasourceId}`)
}

/**
 * 获取数据源支持的货币对列表.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function getDatasourceSymbols(datasourceId) {
  return request.get(`/api/v1/datasources/${datasourceId}/symbols`)
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