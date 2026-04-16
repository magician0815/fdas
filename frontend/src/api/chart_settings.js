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