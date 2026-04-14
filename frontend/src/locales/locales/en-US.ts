/**
 * English translation file.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

export default {
  // Common
  common: {
    confirm: 'Confirm',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    add: 'Add',
    search: 'Search',
    reset: 'Reset',
    refresh: 'Refresh',
    export: 'Export',
    import: 'Import',
    download: 'Download',
    upload: 'Upload',
    submit: 'Submit',
    back: 'Back',
    next: 'Next',
    previous: 'Previous',
    close: 'Close',
    open: 'Open',
    show: 'Show',
    hide: 'Hide',
    enable: 'Enable',
    disable: 'Disable',
    yes: 'Yes',
    no: 'No',
    all: 'All',
    none: 'None',
    loading: 'Loading...',
    noData: 'No Data',
    success: 'Success',
    failed: 'Failed',
    error: 'Error',
    warning: 'Warning',
    info: 'Info',
    tip: 'Tip',
    required: 'Required',
    optional: 'Optional'
  },

  // Navigation
  nav: {
    dashboard: 'Dashboard',
    forex: 'Forex Market',
    futures: 'Futures Market',
    stocks: 'Stock Market',
    dataSource: 'Data Sources',
    collection: 'Collection Tasks',
    users: 'Users',
    logs: 'System Logs',
    settings: 'Settings'
  },

  // Authentication
  auth: {
    login: 'Login',
    logout: 'Logout',
    username: 'Username',
    password: 'Password',
    rememberMe: 'Remember Me',
    forgotPassword: 'Forgot Password',
    loginSuccess: 'Login Successful',
    loginFailed: 'Login Failed',
    sessionExpired: 'Session Expired, Please Login Again',
    invalidCredentials: 'Invalid Username or Password'
  },

  // Chart
  chart: {
    candlestick: 'Candlestick',
    lineChart: 'Line Chart',
    areaChart: 'Area Chart',
    volumeChart: 'Volume Chart',
    oiChart: 'Open Interest Chart',
    macdChart: 'MACD Chart',

    period: 'Period',
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    minute1: '1 Min',
    minute5: '5 Min',
    minute15: '15 Min',
    minute30: '30 Min',
    minute60: '60 Min',

    open: 'Open',
    high: 'High',
    low: 'Low',
    close: 'Close',
    settle: 'Settlement',
    volume: 'Volume',
    openInterest: 'Open Interest',
    turnover: 'Turnover',
    change: 'Change',
    changePct: 'Change %',
    changeAmount: 'Change Amount',
    amplitude: 'Amplitude',

    ma: 'MA',
    ma5: 'MA5',
    ma10: 'MA10',
    ma20: 'MA20',
    ma60: 'MA60',
    macd: 'MACD',
    dif: 'DIF',
    dea: 'DEA',
    histogram: 'Histogram',
    kdj: 'KDJ',
    rsi: 'RSI',
    boll: 'BOLL',
    atr: 'ATR',

    zoomIn: 'Zoom In',
    zoomOut: 'Zoom Out',
    panLeft: 'Pan Left',
    panRight: 'Pan Right',
    resetView: 'Reset View',
    fullscreen: 'Fullscreen',
    exitFullscreen: 'Exit Fullscreen',
    crosshair: 'Crosshair',
    lockCursor: 'Lock Cursor',
    unlockCursor: 'Unlock Cursor',

    date: 'Date',
    time: 'Time',
    startDate: 'Start Date',
    endDate: 'End Date',
    dateRange: 'Date Range',
    selectDate: 'Select Date',

    theme: 'Theme',
    lightTheme: 'Light Mode',
    darkTheme: 'Dark Mode',
    currentTheme: 'Current Theme',

    rangeStats: 'Range Statistics',
    rangeHigh: 'Range High',
    rangeLow: 'Range Low',
    rangeStart: 'Start',
    rangeEnd: 'End',
    rangeDays: 'Range Days',
    rangeChange: 'Range Change',
    rangeChangePct: 'Range Change %',
    rangeMaxChange: 'Max Gain',
    rangeMinChange: 'Max Loss',

    multiPeriod: 'Multi Period',
    syncTime: 'Sync Time',
    independent: 'Independent',
    layoutMode: 'Layout Mode',
    periodCount: 'Period Count'
  },

  // Drawing Tools
  drawing: {
    tools: 'Drawing Tools',
    trendLine: 'Trend Line',
    horizontalLine: 'Horizontal Line',
    verticalLine: 'Vertical Line',
    rectangle: 'Rectangle',
    text: 'Text Annotation',
    arrowUp: 'Up Arrow',
    arrowDown: 'Down Arrow',

    proTools: 'Professional Tools',
    fibonacci: 'Fibonacci',
    gannLine: 'Gann Line',
    pitchfork: 'Andrews Pitchfork',
    fibonacciFan: 'Fibonacci Fan',
    parallelChannel: 'Parallel Channel',
    waveMark: 'Wave Mark',

    color: 'Color',
    lineWidth: 'Width',
    magnet: 'Magnet',
    magnetEnabled: 'Magnet Enabled',
    magnetDisabled: 'Magnet Disabled',

    selectTool: 'Select Tool',
    clearAll: 'Clear All',
    deleteSelected: 'Delete Selected',
    editSelected: 'Edit Selected',
    copySelected: 'Copy Selected'
  },

  // Stock Market
  stock: {
    marketType: 'Market Type',
    stockA: 'A-share',
    stockKcb: 'STAR Market',
    stockCyb: 'ChiNext',
    stockSt: 'ST Stock',
    stockBjb: 'BSE',

    limitUp: 'Limit Up',
    limitDown: 'Limit Down',
    limitUpThreshold: 'Limit Up Threshold',
    limitDownThreshold: 'Limit Down Threshold',
    hitLimitUp: 'Hit Limit Up',
    hitLimitDown: 'Hit Limit Down',

    adjustment: 'Adjustment',
    forwardAdjust: 'Forward Adjust',
    backwardAdjust: 'Backward Adjust',
    noAdjust: 'No Adjustment',
    adjustmentFactor: 'Adjustment Factor',

    dividend: 'Dividend',
    bonus: 'Bonus Share',
    split: 'Split',
    dividendDate: 'Ex-dividend Date',
    dividendAmount: 'Dividend Amount',
    dividendRatio: 'Dividend Ratio',

    suspension: 'Suspension',
    resume: 'Resume',
    suspensionDays: 'Suspension Days'
  },

  // Futures Market
  futures: {
    variety: 'Variety',
    contract: 'Contract',
    contractCode: 'Contract Code',
    contractMonth: 'Contract Month',
    expiryDate: 'Expiry Date',
    listingDate: 'Listing Date',
    deliveryDate: 'Delivery Date',
    deliveryMethod: 'Delivery Method',
    cashDelivery: 'Cash Delivery',
    physicalDelivery: 'Physical Delivery',

    mainContract: 'Main Contract',
    mainSwitch: 'Main Switch',
    mainSwitchDate: 'Switch Date',
    nextMain: 'Next Main',
    prevMain: 'Prev Main',

    oi: 'Open Interest',
    oiChange: 'OI Change',
    oiIncrease: 'OI Increase',
    oiDecrease: 'OI Decrease',

    rollOver: 'Roll Over',
    priceAdjust: 'Price Adjust',
    spreadAdjust: 'Spread Adjust',
    smoothAdjust: 'Smooth Adjust'
  },

  // Data Source
  dataSource: {
    name: 'Data Source Name',
    type: 'Data Source Type',
    interface: 'Interface Name',
    status: 'Status',
    active: 'Active',
    inactive: 'Inactive',
    lastSync: 'Last Sync',
    syncSymbols: 'Sync Symbols',
    syncSuccess: 'Sync Successful',
    syncFailed: 'Sync Failed'
  },

  // Collection Tasks
  collection: {
    taskName: 'Task Name',
    taskType: 'Task Type',
    symbol: 'Symbol',
    cronExpr: 'Cron Expression',
    lastRun: 'Last Run',
    nextRun: 'Next Run',
    status: 'Status',
    enabled: 'Enabled',
    disabled: 'Disabled',
    running: 'Running',
    completed: 'Completed',
    failed: 'Failed',
    records: 'Records',
    duration: 'Duration',
    message: 'Message',
    runNow: 'Run Now',
    enableTask: 'Enable Task',
    disableTask: 'Disable Task',
    createTask: 'Create Task',
    editTask: 'Edit Task',
    deleteTask: 'Delete Task'
  },

  // User Management
  user: {
    userId: 'User ID',
    userName: 'Username',
    role: 'Role',
    admin: 'Admin',
    user: 'User',
    createdAt: 'Created At',
    lastLogin: 'Last Login',
    createUser: 'Create User',
    editUser: 'Edit User',
    deleteUser: 'Delete User',
    changePassword: 'Change Password'
  },

  // System Logs
  log: {
    logId: 'Log ID',
    logType: 'Log Type',
    logLevel: 'Log Level',
    logTime: 'Log Time',
    logContent: 'Log Content',
    logSource: 'Log Source',
    viewLog: 'View Log',
    clearLog: 'Clear Log',
    exportLog: 'Export Log',
    info: 'Info',
    debug: 'Debug',
    warning: 'Warning',
    error: 'Error'
  },

  // Data Export
  export: {
    exportRange: 'Export Range',
    exportFields: 'Export Fields',
    exportFormat: 'Export Format',
    exportOptions: 'Export Options',
    includeHeader: 'Include Header',
    csvFormat: 'CSV Format',
    excelFormat: 'Excel Format',
    jsonFormat: 'JSON Format',
    exportSuccess: 'Export Successful',
    exportFailed: 'Export Failed',
    previewData: 'Preview Data',
    estimatedCount: 'Estimated Count'
  },

  // Template Management
  template: {
    templateName: 'Template Name',
    templateDesc: 'Template Description',
    saveTemplate: 'Save Template',
    loadTemplate: 'Load Template',
    deleteTemplate: 'Delete Template',
    shareTemplate: 'Share Template',
    publicTemplate: 'Public Template',
    privateTemplate: 'Private Template',
    myTemplates: 'My Templates',
    publicTemplates: 'Public Templates',
    applyTemplate: 'Apply Template',
    templateConfig: 'Template Configuration',
    shareLink: 'Share Link'
  },

  // Keyboard Spirit
  keyboardSpirit: {
    searchPlaceholder: 'Search by code/name',
    symbolsTab: 'Symbols',
    indicatorsTab: 'Indicators',
    commandsTab: 'Commands',
    recentUsed: 'Recent Used',
    noResult: 'No Results Found',
    selectHint: '↑↓ to select',
    confirmHint: 'Enter to confirm',
    closeHint: 'Esc to close'
  },

  // Help
  help: {
    title: 'Help Guide',
    chartTab: 'Chart Operations',
    dataTab: 'Data Management',
    shortcutsTab: 'Shortcuts',
    tip: 'Click section titles to expand or collapse details. For further assistance, contact administrator.',

    // Chart sections
    chartBasic: 'Basic Chart Operations',
    chartStyle: 'Chart Types & Styles',
    chartIndicators: 'Indicators & Moving Averages',
    chartCursor: 'Crosshair & Data Display',
    chartDrawing: 'Drawing Tools',
    chartRange: 'Range Statistics',
    chartNavigation: 'Quick Navigation',

    // Data sections
    dataSource: 'Data Source Management',
    collection: 'Collection Tasks',
    dataQuery: 'Data Query',
    dataExport: 'Data Export',

    // Shortcuts sections
    chartShortcuts: 'Chart Keyboard Shortcuts',
    keyboardSpirit: 'Keyboard Spirit',
    pageNav: 'Page Navigation'
  },

  // Errors
  errors: {
    networkError: 'Network Connection Error',
    serverError: 'Server Error',
    notFound: 'Resource Not Found',
    unauthorized: 'Unauthorized Access',
    forbidden: 'Access Forbidden',
    validationError: 'Data Validation Failed',
    unknownError: 'Unknown Error'
  }
}