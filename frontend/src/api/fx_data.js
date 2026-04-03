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