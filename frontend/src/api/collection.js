/**
 * 采集任务API.
 *
 * 提供采集任务的CRUD、启停、执行、校验等接口.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 */

import request from './index'

/**
 * 获取采集任务列表.
 *
 * @param {string} marketId - 可选，按市场过滤
 * @returns {Promise} API响应
 */
export function getCollectionTasks(marketId = null) {
  const params = marketId ? { market_id: marketId } : {}
  return request.get('/api/v1/collection-tasks', { params })
}

/**
 * 获取采集任务详情.
 *
 * @param {string} taskId - 任务ID
 * @returns {Promise} API响应
 */
export function getCollectionTask(taskId) {
  return request.get(`/api/v1/collection-tasks/${taskId}`)
}

/**
 * 创建采集任务.
 *
 * @param {Object} data - 任务数据
 * @returns {Promise} API响应
 */
export function createCollectionTask(data) {
  return request.post('/api/v1/collection-tasks', data)
}

/**
 * 更新采集任务.
 *
 * @param {string} taskId - 任务ID
 * @param {Object} data - 更新数据
 * @returns {Promise} API响应
 */
export function updateCollectionTask(taskId, data) {
  return request.put(`/api/v1/collection-tasks/${taskId}`, data)
}

/**
 * 删除采集任务.
 *
 * @param {string} taskId - 任务ID
 * @returns {Promise} API响应
 */
export function deleteCollectionTask(taskId) {
  return request.delete(`/api/v1/collection-tasks/${taskId}`)
}

/**
 * 启用采集任务.
 *
 * @param {string} taskId - 任务ID
 * @returns {Promise} API响应
 */
export function enableTask(taskId) {
  return request.put(`/api/v1/collection-tasks/${taskId}/enable`)
}

/**
 * 禁用采集任务.
 *
 * @param {string} taskId - 任务ID
 * @returns {Promise} API响应
 */
export function disableTask(taskId) {
  return request.put(`/api/v1/collection-tasks/${taskId}/disable`)
}

/**
 * 手动执行采集任务.
 *
 * @param {string} taskId - 任务ID
 * @param {boolean} force - 是否强制执行（忽略日期限制）
 * @returns {Promise} API响应
 */
export function executeTask(taskId, force = false) {
  return request.post(`/api/v1/collection-tasks/${taskId}/execute`, { force })
}

/**
 * 获取任务执行日志.
 *
 * @param {string} taskId - 任务ID
 * @param {number} limit - 日志数量限制
 * @returns {Promise} API响应
 */
export function getTaskLogs(taskId, limit = 50) {
  return request.get(`/api/v1/collection-tasks/${taskId}/logs`, { params: { limit } })
}

/**
 * 参数预校验.
 *
 * @param {Object} data - 校验参数
 * @returns {Promise} API响应
 */
export function validateTaskParams(data) {
  return request.post('/api/v1/collection-tasks/validate', data)
}