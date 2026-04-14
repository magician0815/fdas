/**
 * 中文翻译文件.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

export default {
  // 通用
  common: {
    confirm: '确认',
    cancel: '取消',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    add: '添加',
    search: '搜索',
    reset: '重置',
    refresh: '刷新',
    export: '导出',
    import: '导入',
    download: '下载',
    upload: '上传',
    submit: '提交',
    back: '返回',
    next: '下一步',
    previous: '上一步',
    close: '关闭',
    open: '打开',
    show: '显示',
    hide: '隐藏',
    enable: '启用',
    disable: '禁用',
    yes: '是',
    no: '否',
    all: '全部',
    none: '无',
    loading: '加载中...',
    noData: '暂无数据',
    success: '操作成功',
    failed: '操作失败',
    error: '错误',
    warning: '警告',
    info: '提示',
    tip: '提示',
    required: '必填',
    optional: '可选'
  },

  // 导航菜单
  nav: {
    dashboard: '首页',
    forex: '外汇行情',
    futures: '期货行情',
    stocks: '股票行情',
    dataSource: '数据源管理',
    collection: '采集任务',
    users: '用户管理',
    logs: '系统日志',
    settings: '系统设置'
  },

  // 用户认证
  auth: {
    login: '登录',
    logout: '退出登录',
    username: '用户名',
    password: '密码',
    rememberMe: '记住我',
    forgotPassword: '忘记密码',
    loginSuccess: '登录成功',
    loginFailed: '登录失败',
    sessionExpired: '会话已过期，请重新登录',
    invalidCredentials: '用户名或密码错误'
  },

  // 图表相关
  chart: {
    // 图表类型
    candlestick: '蜡烛图',
    lineChart: '折线图',
    areaChart: '面积图',
    volumeChart: '成交量图',
    oiChart: '持仓量图',
    macdChart: 'MACD图',

    // 周期
    period: '周期',
    daily: '日线',
    weekly: '周线',
    monthly: '月线',
    minute1: '1分钟',
    minute5: '5分钟',
    minute15: '15分钟',
    minute30: '30分钟',
    minute60: '60分钟',

    // 价格
    open: '开盘价',
    high: '最高价',
    low: '最低价',
    close: '收盘价',
    settle: '结算价',
    volume: '成交量',
    openInterest: '持仓量',
    turnover: '成交额',
    change: '涨跌',
    changePct: '涨跌幅',
    changeAmount: '涨跌额',
    amplitude: '振幅',

    // 指标
    ma: '均线',
    ma5: 'MA5',
    ma10: 'MA10',
    ma20: 'MA20',
    ma60: 'MA60',
    macd: 'MACD',
    dif: 'DIF',
    dea: 'DEA',
    histogram: '柱状图',
    kdj: 'KDJ',
    rsi: 'RSI',
    boll: '布林带',
    atr: 'ATR',

    // 图表操作
    zoomIn: '放大',
    zoomOut: '缩小',
    panLeft: '左移',
    panRight: '右移',
    resetView: '重置视图',
    fullscreen: '全屏',
    exitFullscreen: '退出全屏',
    crosshair: '十字光标',
    lockCursor: '锁定光标',
    unlockCursor: '解锁光标',

    // 日期时间
    date: '日期',
    time: '时间',
    startDate: '开始日期',
    endDate: '结束日期',
    dateRange: '日期范围',
    selectDate: '选择日期',

    // 主题
    theme: '主题',
    lightTheme: '白天模式',
    darkTheme: '夜间模式',
    currentTheme: '当前主题',

    // 区间统计
    rangeStats: '区间统计',
    rangeHigh: '区间最高',
    rangeLow: '区间最低',
    rangeStart: '起点',
    rangeEnd: '终点',
    rangeDays: '区间天数',
    rangeChange: '区间涨跌',
    rangeChangePct: '区间涨跌幅',
    rangeMaxChange: '最大涨幅',
    rangeMinChange: '最大跌幅',

    // 多周期
    multiPeriod: '多周期',
    syncTime: '时间同步',
    independent: '独立显示',
    layoutMode: '布局模式',
    periodCount: '周期数量'
  },

  // 画线工具
  drawing: {
    tools: '画线工具',
    trendLine: '趋势线',
    horizontalLine: '水平线',
    verticalLine: '垂直线',
    rectangle: '矩形',
    text: '文字标注',
    arrowUp: '上涨箭头',
    arrowDown: '下跌箭头',

    // 专业工具
    proTools: '专业画线',
    fibonacci: '黄金分割线',
    gannLine: '江恩角度线',
    pitchfork: '安德鲁音叉线',
    fibonacciFan: '斐波那契扇形线',
    parallelChannel: '平行通道线',
    waveMark: '波浪线标注',

    // 工具设置
    color: '颜色',
    lineWidth: '粗细',
    magnet: '磁吸',
    magnetEnabled: '磁吸开启',
    magnetDisabled: '磁吸关闭',

    // 操作
    selectTool: '选择工具',
    clearAll: '清除全部',
    deleteSelected: '删除选中',
    editSelected: '编辑选中',
    copySelected: '复制选中'
  },

  // 股票市场
  stock: {
    marketType: '市场类型',
    stockA: 'A股',
    stockKcb: '科创板',
    stockCyb: '创业板',
    stockSt: 'ST股票',
    stockBjb: '北交所',

    // 涨跌停
    limitUp: '涨停',
    limitDown: '跌停',
    limitUpThreshold: '涨停阈值',
    limitDownThreshold: '跌停阈值',
    hitLimitUp: '触及涨停',
    hitLimitDown: '触及跌停',

    // 复权
    adjustment: '复权',
    forwardAdjust: '前复权',
    backwardAdjust: '后复权',
    noAdjust: '不复权',
    adjustmentFactor: '复权因子',

    // 除权除息
    dividend: '分红',
    bonus: '送股',
    split: '拆股',
    dividendDate: '除权除息日',
    dividendAmount: '分红金额',
    dividendRatio: '分红比例',

    // 停牌
    suspension: '停牌',
    resume: '复牌',
    suspensionDays: '停牌天数'
  },

  // 期货市场
  futures: {
    variety: '品种',
    contract: '合约',
    contractCode: '合约代码',
    contractMonth: '合约月份',
    expiryDate: '到期日',
    listingDate: '上市日',
    deliveryDate: '交割日',
    deliveryMethod: '交割方式',
    cashDelivery: '现金交割',
    physicalDelivery: '实物交割',

    // 主力合约
    mainContract: '主力合约',
    mainSwitch: '主力切换',
    mainSwitchDate: '切换日期',
    nextMain: '下月主力',
    prevMain: '上月主力',

    // 持仓量
    oi: '持仓量',
    oiChange: '持仓量变化',
    oiIncrease: '持仓增加',
    oiDecrease: '持仓减少',

    // 挢月
    rollOver: '挢月',
    priceAdjust: '价格调整',
    spreadAdjust: '价差调整',
    smoothAdjust: '平滑调整'
  },

  // 数据源管理
  dataSource: {
    name: '数据源名称',
    type: '数据源类型',
    interface: '接口名称',
    status: '状态',
    active: '激活',
    inactive: '未激活',
    lastSync: '最后同步',
    syncSymbols: '同步货币对',
    syncSuccess: '同步成功',
    syncFailed: '同步失败'
  },

  // 采集任务
  collection: {
    taskName: '任务名称',
    taskType: '任务类型',
    symbol: '标的',
    cronExpr: '定时表达式',
    lastRun: '上次执行',
    nextRun: '下次执行',
    status: '状态',
    enabled: '已启用',
    disabled: '已禁用',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    records: '记录数',
    duration: '耗时',
    message: '消息',
    runNow: '立即执行',
    enableTask: '启用任务',
    disableTask: '禁用任务',
    createTask: '创建任务',
    editTask: '编辑任务',
    deleteTask: '删除任务'
  },

  // 用户管理
  user: {
    userId: '用户ID',
    userName: '用户名',
    role: '角色',
    admin: '管理员',
    user: '普通用户',
    createdAt: '创建时间',
    lastLogin: '最后登录',
    createUser: '创建用户',
    editUser: '编辑用户',
    deleteUser: '删除用户',
    changePassword: '修改密码'
  },

  // 系统日志
  log: {
    logId: '日志ID',
    logType: '日志类型',
    logLevel: '日志级别',
    logTime: '日志时间',
    logContent: '日志内容',
    logSource: '日志来源',
    viewLog: '查看日志',
    clearLog: '清除日志',
    exportLog: '导出日志',
    info: '信息',
    debug: '调试',
    warning: '警告',
    error: '错误'
  },

  // 数据导出
  export: {
    exportRange: '导出范围',
    exportFields: '导出字段',
    exportFormat: '导出格式',
    exportOptions: '导出选项',
    includeHeader: '包含表头',
    csvFormat: 'CSV格式',
    excelFormat: 'Excel格式',
    jsonFormat: 'JSON格式',
    exportSuccess: '导出成功',
    exportFailed: '导出失败',
    previewData: '数据预览',
    estimatedCount: '预计导出条数'
  },

  // 模板管理
  template: {
    templateName: '模板名称',
    templateDesc: '模板描述',
    saveTemplate: '保存模板',
    loadTemplate: '加载模板',
    deleteTemplate: '删除模板',
    shareTemplate: '分享模板',
    publicTemplate: '公开模板',
    privateTemplate: '私有模板',
    myTemplates: '我的模板',
    publicTemplates: '公开模板',
    applyTemplate: '应用模板',
    templateConfig: '模板配置',
    shareLink: '分享链接'
  },

  // 键盘精灵
  keyboardSpirit: {
    searchPlaceholder: '输入代码/名称搜索',
    symbolsTab: '品种',
    indicatorsTab: '指标',
    commandsTab: '命令',
    recentUsed: '最近使用',
    noResult: '未找到匹配结果',
    selectHint: '↑↓选择',
    confirmHint: 'Enter确认',
    closeHint: 'Esc关闭'
  },

  // 使用帮助
  help: {
    title: '使用帮助',
    chartTab: '图表操作',
    dataTab: '数据管理',
    shortcutsTab: '快捷键',
    tip: '点击各章节标题可展开或收起详细说明。如有疑问，请联系管理员获取更多帮助。',

    // 图表操作章节
    chartBasic: 'K线图基础操作',
    chartStyle: '图表类型与样式',
    chartIndicators: '均线与技术指标',
    chartCursor: '十字光标与数据查看',
    chartDrawing: '画线工具',
    chartRange: '区间统计',
    chartNavigation: '快速定位',

    // 数据管理章节
    dataSource: '数据源管理',
    collection: '采集任务管理',
    dataQuery: '数据查询',
    dataExport: '数据导出',

    // 快捷键章节
    chartShortcuts: '图表操作快捷键',
    keyboardSpirit: '键盘精灵',
    pageNav: '页面导航'
  },

  // 错误提示
  errors: {
    networkError: '网络连接错误',
    serverError: '服务器错误',
    notFound: '资源不存在',
    unauthorized: '未授权访问',
    forbidden: '禁止访问',
    validationError: '数据验证失败',
    unknownError: '未知错误'
  }
}