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
 * 删除数据源.
 *
 * @param {string} datasourceId - 数据源ID
 * @returns {Promise} API响应
 */
export function deleteDatasource(datasourceId) {
  return request.delete(`/api/v1/datasources/${datasourceId}`)
}

/**
 * 更新数据源基本信息.
 *
 * @param {string} datasourceId - 数据源ID
 * @param {string} name - 数据源名称
 * @returns {Promise} API响应
 */
export function updateDatasourceName(datasourceId, name) {
  return request.put(`/api/v1/datasources/${datasourceId}`, {
    name: name
  })
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
 * 获取默认数据源配置.
 *
 * @param {string} marketCode - 市场代码（forex/stock_cn/stock_us/stock_hk/futures_cn/bond_cn/bond_us）
 * @returns {string} 默认配置JSON字符串
 */
export function getDefaultConfig(marketCode = 'forex') {
  const configs = {
    forex: {
      version: "1.0",
      name: "东方财富外汇数据源",
      type: "akshare",
      market: "forex",
      collector_type: "http_api",
      api: {
        base_url: "https://push2his.eastmoney.com/api/qt/stock/kline/get",
        method: "GET",
        timeout: 30,
        retry: { max_attempt: 3, backoff_factor: 2 }
      },
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
        "Accept": "application/json, text/plain, */*"
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
        "AUDJPY": "133.AUDJPY"
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
    },
    stock_cn: {
      version: "1.0",
      name: "AKShare A股历史数据",
      type: "akshare",
      market: "stock_cn",
      collector_type: "akshare_native",
      akshare_interface: "stock_zh_a_hist",
      akshare_params: {
        symbol: "000001",
        period: "daily",
        adjust: ""
      }
    },
    stock_us: {
      version: "1.0",
      name: "AKShare 美股历史数据",
      type: "akshare",
      market: "stock_us",
      collector_type: "akshare_native",
      akshare_interface: "stock_us_daily",
      akshare_params: {
        symbol: "AAPL",
        period: "daily"
      }
    },
    stock_hk: {
      version: "1.0",
      name: "AKShare 港股历史数据",
      type: "akshare",
      market: "stock_hk",
      collector_type: "akshare_native",
      akshare_interface: "stock_hk_daily",
      akshare_params: {
        symbol: "00700"
      }
    },
    futures_cn: {
      version: "1.0",
      name: "AKShare 国内期货历史数据",
      type: "akshare",
      market: "futures_cn",
      collector_type: "akshare_native",
      akshare_interface: "futures_zh_daily_sina",
      akshare_params: {
        symbol: "IF9999"
      }
    },
    bond_cn: {
      version: "1.0",
      name: "AKShare 国内债券历史数据",
      type: "akshare",
      market: "bond_cn",
      collector_type: "akshare_native",
      akshare_interface: "bond_cn_daily",
      akshare_params: {
        symbol: "113052"
      }
    },
    bond_us: {
      version: "1.0",
      name: "AKShare 美国债券历史数据",
      type: "akshare",
      market: "bond_us",
      collector_type: "akshare_native",
      akshare_interface: "bond_us_daily",
      akshare_params: {
        symbol: "US10Y"
      }
    }
  }

  const config = configs[marketCode] || configs.forex
  return JSON.stringify(config, null, 2)
}

// ==================== 向导API ====================

/**
 * 步骤1：验证基础信息并创建会话.
 *
 * @param {string} datasourceName - 数据源名称
 * @param {string} marketId - 市场ID
 * @returns {Promise} API响应
 */
export function wizardStep1Validate(datasourceName, marketId) {
  return request.post('/api/v1/datasources/wizard/step1', {
    datasource_name: datasourceName,
    market_id: marketId
  })
}

/**
 * 步骤2：测试API连接。
 *
 * @param {string} sessionId - 会话ID
 * @param {string} apiBaseUrl - API基础URL
 * @param {string} apiMethod - 请求方法
 * @param {number} apiTimeout - 超时时间
 * @param {object} apiHeaders - 请求头
 * @returns {Promise} API响应
 */
export function wizardStep2TestConnection(sessionId, apiBaseUrl, apiMethod = 'GET', apiTimeout = 30, apiHeaders = null) {
  return request.post('/api/v1/datasources/wizard/step2-test', {
    session_id: sessionId,
    api_base_url: apiBaseUrl,
    api_method: apiMethod,
    api_timeout: apiTimeout,
    api_headers: apiHeaders
  })
}

/**
 * 步骤3：探测可用端点。
 *
 * @param {string} sessionId - 会话ID
 * @param {string} apiBaseUrl - API基础URL
 * @param {string} apiMethod - 请求方法
 * @param {number} apiTimeout - 超时时间
 * @param {object} apiHeaders - 请求头
 * @param {object} testParams - 测试参数
 * @returns {Promise} API响应
 */
export function wizardStep3ProbeEndpoints(sessionId, apiBaseUrl, apiMethod = 'GET', apiTimeout = 30, apiHeaders = null, testParams = null) {
  return request.post('/api/v1/datasources/wizard/step3-probe', {
    session_id: sessionId,
    api_base_url: apiBaseUrl,
    api_method: apiMethod,
    api_timeout: apiTimeout,
    api_headers: apiHeaders,
    test_params: testParams
  })
}

/**
 * 步骤4：获取数据预览。
 *
 * @param {string} sessionId - 会话ID
 * @param {string} endpointUrl - 端点URL
 * @param {string} apiMethod - 请求方法
 * @param {number} apiTimeout - 超时时间
 * @param {object} apiHeaders - 请求头
 * @param {object} params - 请求参数
 * @returns {Promise} API响应
 */
export function wizardStep4PreviewData(sessionId, endpointUrl, apiMethod = 'GET', apiTimeout = 30, apiHeaders = null, params = null) {
  return request.post('/api/v1/datasources/wizard/step4-preview', {
    session_id: sessionId,
    endpoint_url: endpointUrl,
    api_method: apiMethod,
    api_timeout: apiTimeout,
    api_headers: apiHeaders,
    params: params
  })
}

/**
 * 步骤5：自动识别字段映射。
 *
 * @param {string} sessionId - 会话ID
 * @param {Array} sampleData - 样本数据列表
 * @returns {Promise} API响应
 */
export function wizardStep5DetectFieldsMapping(sessionId, sampleData) {
  return request.post('/api/v1/datasources/wizard/step5-detect', {
    session_id: sessionId,
    sample_data: sampleData
  })
}

/**
 * 步骤6：测试采集。
 *
 * @param {string} sessionId - 会话ID
 * @param {object} config - 完整配置
 * @param {string} symbolCode - 测试用货币对
 * @returns {Promise} API响应
 */
export function wizardStep6TestCollection(sessionId, config, symbolCode = 'TEST') {
  return request.post('/api/v1/datasources/wizard/step6-test-collect', {
    session_id: sessionId,
    config: config,
    symbol_code: symbolCode
  })
}

/**
 * 步骤7：确认保存。
 *
 * @param {string} sessionId - 会话ID
 * @returns {Promise} API响应
 */
export function wizardStep7SaveDatasource(sessionId) {
  return request.post('/api/v1/datasources/wizard/step7-save', {
    session_id: sessionId
  })
}

/**
 * 获取向导会话状态。
 *
 * @param {string} sessionId - 会话ID
 * @returns {Promise} API响应
 */
export function wizardGetSession(sessionId) {
  return request.get(`/api/v1/datasources/wizard/${sessionId}`)
}