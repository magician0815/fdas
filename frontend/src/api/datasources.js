/**
 * 数据源API.
 *
 * 提供数据源的列表查询、货币对同步等接口.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 * Updated: 2026-04-17 - 修复API路径添加尾部斜杠
 */

import request from './index'

/**
 * 获取数据源列表.
 *
 * @returns {Promise} API响应
 */
export function getDatasources() {
  return request.get('/api/v1/datasources/')
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

/**
 * 获取数据源配置.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function getDatasourceConfig(datasourceId) {
  return request.get(`/api/v1/datasources/${datasourceId}/config`)
}

/**
 * 更新数据源配置.
 *
 * @param {string} datasourceId - 数据源ID
 * @param {string} configFile - 配置JSON字符串
 * @returns {Promise} API响应
 */
export function updateDatasourceConfig(datasourceId, configFile) {
  return request.put(`/api/v1/datasources/${datasourceId}/config`, { config_file: configFile })
}

/**
 * 导出数据源配置.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function exportDatasourceConfig(datasourceId) {
  return request.get(`/api/v1/datasources/${datasourceId}/export`)
}

/**
 * 导入数据源配置.
 *
 * @param {string} configFile - 配置JSON字符串
 * @param {string} name - 数据源名称
 * @param {string} marketId - 市场ID
 * @returns {Promise} API响应
 */
export function importDatasourceConfig(configFile, name, marketId) {
  return request.post('/api/v1/datasources/import', {
    config_file: configFile,
    name: name,
    market_id: marketId
  })
}

/**
 * 获取默认外汇数据源配置.
 *
 * @returns {string} 默认配置JSON字符串
 */
export function getDefaultConfig() {
  return JSON.stringify({
    version: "1.0",
    name: "东方财富外汇数据源",
    type: "akshare",
    market: "forex",
    api: {
      base_url: "https://push2his.eastmoney.com/api/qt/stock/kline/get",
      method: "GET",
      timeout: 30,
      retry: { max_attempt: 3, backoff_factor: 2 }
    },
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Referer": "https://quote.eastmoney.com/",
      "Accept": "application/json, text/plain, */*",
      "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    },
    symbol_mapping: {
      "USDCNY": "133.USDCNH",
      "EURCNY": "133.EURCNH",
      "GBPCNY": "133.GBPCNH",
      "JPYCNY": "133.CNHJPY",
      "HKDCNY": "133.CNHHKD",
      "AUDCNY": "133.AUDCNH",
      "CADCNY": "133.CADCNH",
      "CHFCNY": "133.CHFCNH",
      "NZDCNY": "133.NZDCNH",
      "EURUSD": "133.EURUSD",
      "GBPUSD": "133.GBPUSD",
      "USDJPY": "133.USDJPY",
      "AUDUSD": "133.AUDUSD",
      "USDCAD": "133.USDCAD",
      "USDCHF": "133.USDCHF",
      "NZDUSD": "133.NZDUSD",
      "EURGBP": "133.EURGBP",
      "EURJPY": "133.EURJPY",
      "GBPJPY": "133.GBPJPY",
      "AUDJPY": "133.AUDJPY",
      "USDSGD": "133.USDSGD",
      "USDHKD": "133.USDHKD"
    },
    data_parser: {
      response_root: "data.klines",
      date_field: 0,
      open_field: 1,
      high_field: 2,
      low_field: 3,
      close_field: 4,
      volume_field: 5
    }
  }, null, 2)
}