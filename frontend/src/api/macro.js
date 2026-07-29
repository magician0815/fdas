/**
 * 宏观数据 API 服务.
 *
 * 封装宏观数据模块的所有 API 调用.
 *
 * Author: FDAS Team
 * Created: 2026-07-29
 */

import request from './index'

// ========== 数据源配置 ==========

/** 获取配置列表 */
export function listConfigs() {
  return request.get('/api/v1/macro/configs')
}

/** 获取单个配置 */
export function getConfig(id) {
  return request.get(`/api/v1/macro/configs/${id}`)
}

/** 创建配置 */
export function createConfig(data) {
  return request.post('/api/v1/macro/configs', data)
}

/** 更新配置 */
export function updateConfig(id, data) {
  return request.put(`/api/v1/macro/configs/${id}`, data)
}

/** 删除配置 */
export function deleteConfig(id) {
  return request.delete(`/api/v1/macro/configs/${id}`)
}

/** 启用定时调度 */
export function enableConfig(id) {
  return request.post(`/api/v1/macro/configs/${id}/enable`)
}

/** 禁用定时调度 */
export function disableConfig(id) {
  return request.post(`/api/v1/macro/configs/${id}/disable`)
}

/** 手动触发采集 */
export function triggerCollect(id, full = false) {
  return request.post(`/api/v1/macro/configs/${id}/collect`, null, {
    params: { full }
  })
}

// ========== 数据查询 ==========

/** 分页查询宏观数据 */
export function queryData(params = {}) {
  return request.get('/api/v1/macro/data', { params })
}

/** 获取最新数据 */
export function getLatest(sourceCode) {
  return request.get(`/api/v1/macro/data/${sourceCode}/latest`)
}

// ========== 采集日志 ==========

/** 查询采集日志 */
export function queryLogs(params = {}) {
  return request.get('/api/v1/macro/logs', { params })
}
