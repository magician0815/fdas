/**
 * 图表设置API.
 *
 * 提供用户图表个性化配置的存取功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import request from './index'

/**
 * 获取图表设置列表.
 *
 * @param {string} settingType - 设置类型（可选）
 * @returns {Promise} API响应
 */
export function getChartSettings(settingType) {
  return request.get('/api/v1/chart/settings', {
    params: { setting_type: settingType }
  })
}

/**
 * 获取单个图表设置.
 *
 * @param {string} settingType - 设置类型
 * @param {string} settingKey - 设置键名
 * @returns {Promise} API响应
 */
export function getChartSetting(settingType, settingKey) {
  return request.get(`/api/v1/chart/settings/${settingType}/${settingKey}`)
}

/**
 * 保存图表设置.
 *
 * @param {string} settingType - 设置类型
 * @param {string} settingKey - 设置键名
 * @param {Object} settingValue - 设置值
 * @returns {Promise} API响应
 */
export function saveChartSetting(settingType, settingKey, settingValue) {
  return request.post('/api/v1/chart/settings', null, {
    params: {
      setting_type: settingType,
      setting_key: settingKey
    },
    data: settingValue
  })
}

/**
 * 删除图表设置.
 *
 * @param {string} settingId - 设置ID
 * @returns {Promise} API响应
 */
export function deleteChartSetting(settingId) {
  return request.delete(`/api/v1/chart/settings/${settingId}`)
}

/**
 * 删除指定类型的所有设置.
 *
 * @param {string} settingType - 设置类型
 * @returns {Promise} API响应
 */
export function deleteChartSettingsByType(settingType) {
  return request.delete(`/api/v1/chart/settings/type/${settingType}`)
}