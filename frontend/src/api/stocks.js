/**
 * 股票数据API.
 *
 * 提供复权数据、除权除息事件等接口.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import request from './index'

/**
 * 获取复权后的K线数据.
 *
 * @param {string} symbolId - 股票ID
 * @param {string} adjustmentType - 复权类型 (none/forward/backward)
 * @param {string} startDate - 开始日期（可选）
 * @param {string} endDate - 结束日期（可选）
 * @returns {Promise} API响应
 */
export function getAdjustmentData(symbolId, adjustmentType, startDate, endDate) {
  return request.get('/api/v1/stocks/adjustment', {
    params: {
      symbol_id: symbolId,
      adjustment_type: adjustmentType,
      start_date: startDate,
      end_date: endDate
    }
  })
}

/**
 * 获取除权除息事件列表.
 *
 * @param {string} symbolId - 股票ID
 * @param {string} startDate - 开始日期（可选）
 * @param {string} endDate - 结束日期（可选）
 * @returns {Promise} API响应
 */
export function getDividendEvents(symbolId, startDate, endDate) {
  return request.get('/api/v1/stocks/dividend-events', {
    params: {
      symbol_id: symbolId,
      start_date: startDate,
      end_date: endDate
    }
  })
}

/**
 * 识别股票市场类型.
 *
 * @param {string} symbolCode - 股票代码
 * @param {string} symbolName - 股票名称（可选）
 * @returns {Promise} API响应
 */
export function getMarketType(symbolCode, symbolName) {
  return request.get('/api/v1/stocks/market-type', {
    params: {
      symbol_code: symbolCode,
      symbol_name: symbolName
    }
  })
}