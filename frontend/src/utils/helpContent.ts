/**
 * 前端使用帮助内容数据.
 *
 * 定义各页面、各功能的操作说明和快捷键列表.
 * 内容为中文，国际化在组件层面通过vue-i18n处理.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

/**
 * 帮助内容章节结构.
 */
export interface HelpSection {
  /** 章节标题 */
  title: string
  /** 章节内容项列表 */
  items: HelpItem[]
}

/**
 * 帮助内容项结构.
 */
export interface HelpItem {
  /** 功能名称 */
  name: string
  /** 操作说明 */
  description: string
  /** 快捷键（可选） */
  shortcut?: string
  /** 图标提示（可选） */
  icon?: string
}

/**
 * 图表操作帮助内容.
 */
export const getChartHelpContent = (): HelpSection[] => {
  return [
    {
      title: 'K线图基础操作',
      items: [
        {
          name: '鼠标滚轮',
          description: '向前滚动放大图表，向后滚动缩小图表，以光标位置为中心缩放',
        },
        {
          name: '鼠标拖拽',
          description: '按住左键拖动可左右平移查看历史K线数据',
        },
        {
          name: '双击',
          description: '双击图表区域重置到默认视图位置',
          shortcut: '或按 ESC 键',
        },
        {
          name: '左侧价格轴',
          description: '显示当前屏幕范围内的价格刻度，随缩放自动调整',
        },
        {
          name: '右侧价格轴',
          description: '可选显示右侧价格轴，点击工具栏按钮切换',
        },
      ]
    },
    {
      title: '图表类型与样式',
      items: [
        {
          name: '蜡烛图/折线图切换',
          description: '工具栏中切换按钮可一键切换K线显示形式，切换时保持当前视图范围',
          icon: 'K线 / 折线',
        },
        {
          name: '白天/夜间主题',
          description: '点击主题按钮切换图表配色方案，设置会自动保存',
          icon: '☀ / 🌙',
        },
        {
          name: '价格坐标模式',
          description: '支持线性坐标和对数坐标切换，对数坐标适合观察大跨度价格变化',
        },
      ]
    },
    {
      title: '均线与技术指标',
      items: [
        {
          name: '均线显示控制',
          description: '工具栏下拉菜单可选择显示MA5、MA10、MA20、MA60均线',
        },
        {
          name: 'MACD指标',
          description: '副图显示MACD指标，包含DIF线、DEA线和MACD柱状图',
        },
        {
          name: '成交量副图',
          description: '主图下方显示成交量柱状图，颜色与K线涨跌同步',
        },
      ]
    },
    {
      title: '十字光标与数据查看',
      items: [
        {
          name: '十字光标',
          description: '鼠标移动时自动显示十字线，横线显示价格，竖线对齐K线',
        },
        {
          name: '数据详情',
          description: '光标位置显示当前K线的日期、开高低收、涨跌幅等详细数据',
        },
        {
          name: '光标锁定',
          description: '按空格键锁定当前位置的十字光标，锁定后可用方向键微调位置',
          shortcut: 'Space',
        },
        {
          name: '复制数据',
          description: '锁定光标后按 Ctrl+C 可复制当前K线数据到剪贴板',
          shortcut: 'Ctrl + C',
        },
      ]
    },
    {
      title: '画线工具',
      items: [
        {
          name: '画线工具栏',
          description: '点击编辑按钮打开画线工具面板，可选择不同画线类型',
        },
        {
          name: '基础画线',
          description: '支持趋势线、水平线、垂直线、矩形、文字标注、箭头标注',
        },
        {
          name: '专业画线',
          description: '支持黄金分割线、江恩角度线、安德鲁音叉线、斐波那契扇形线、平行通道线',
        },
        {
          name: '画线编辑',
          description: '点击已有画线可选中，按 Delete 键删除选中画线',
          shortcut: 'Delete',
        },
        {
          name: '磁吸功能',
          description: '开启磁吸后，画线端点会自动吸附到最近的K线高点或低点',
        },
      ]
    },
    {
      title: '区间统计',
      items: [
        {
          name: '区间选择',
          description: '点击区间统计按钮进入选择模式，拖动鼠标框选统计区间',
        },
        {
          name: '统计面板',
          description: '显示区间的起止价格、涨跌幅、振幅、最高最低价等统计数据',
        },
        {
          name: '取消统计',
          description: '点击面板关闭按钮或再次点击统计按钮取消区间选择',
        },
      ]
    },
    {
      title: '快速定位',
      items: [
        {
          name: '日期定位',
          description: '工具栏日期选择器可直接定位到指定日期的K线',
        },
        {
          name: '快速跳转',
          description: '按 Ctrl+左/右方向键可快速跳转100根K线',
          shortcut: 'Ctrl + ← / →',
        },
      ]
    },
  ]
}

/**
 * 数据管理帮助内容.
 */
export const getDataManagementHelpContent = (): HelpSection[] => {
  return [
    {
      title: '数据源管理',
      items: [
        {
          name: '数据源列表',
          description: '数据源管理页面显示所有已配置的外汇数据源，包括名称、接口类型、状态',
        },
        {
          name: '货币对同步',
          description: '点击"同步货币对"按钮可从数据源自动获取支持的货币对列表',
        },
        {
          name: '数据源状态',
          description: '激活状态的数据源可用于数据采集，未激活的数据源暂停使用',
        },
      ]
    },
    {
      title: '采集任务管理',
      items: [
        {
          name: '创建采集任务',
          description: '选择货币对、设置时间范围、配置定时表达式后创建采集任务',
        },
        {
          name: 'Cron表达式',
          description: '定时表达式使用Cron格式，如 "0 8 * * *" 表示每天8点执行',
        },
        {
          name: '立即执行',
          description: '点击"立即执行"按钮可手动触发一次数据采集',
        },
        {
          name: '任务状态',
          description: '查看任务的启用/禁用状态、上次执行时间、下次执行时间',
        },
        {
          name: '采集日志',
          description: '点击任务可查看采集执行日志，包括成功记录数、耗时、错误信息',
        },
      ]
    },
    {
      title: '数据查询',
      items: [
        {
          name: '货币对选择',
          description: '下拉菜单选择要查看的货币对，支持按代码或名称搜索',
        },
        {
          name: '时间范围',
          description: '选择开始日期和结束日期限定查询范围',
        },
        {
          name: '周期切换',
          description: '支持日线、周线、月线周期切换，后端自动聚合计算',
        },
        {
          name: '数据刷新',
          description: '点击刷新按钮重新获取最新数据',
        },
      ]
    },
    {
      title: '数据导出',
      items: [
        {
          name: '导出面板',
          description: '图表页面点击导出按钮打开导出选项面板',
        },
        {
          name: '导出格式',
          description: '支持CSV、Excel、JSON三种格式导出',
        },
        {
          name: '字段选择',
          description: '可选择导出的数据字段（日期、开盘价、收盘价等）',
        },
      ]
    },
  ]
}

/**
 * 快捷键帮助内容.
 */
export const getShortcutsHelpContent = (): HelpSection[] => {
  return [
    {
      title: '图表操作快捷键',
      items: [
        {
          name: '锁定/解锁光标',
          description: '锁定十字光标到当前K线位置，锁定后数据面板固定显示',
          shortcut: 'Space',
        },
        {
          name: '重置视图',
          description: '重置图表到默认显示位置，取消所有选择状态',
          shortcut: 'ESC',
        },
        {
          name: '光标左移',
          description: '锁定状态下，将光标向左移动一根K线',
          shortcut: '←',
        },
        {
          name: '光标右移',
          description: '锁定状态下，将光标向右移动一根K线',
          shortcut: '→',
        },
        {
          name: '快速左跳',
          description: '未锁定时，快速向左跳转100根K线',
          shortcut: 'Ctrl + ←',
        },
        {
          name: '快速右跳',
          description: '未锁定时，快速向右跳转100根K线',
          shortcut: 'Ctrl + →',
        },
        {
          name: '复制数据',
          description: '锁定状态下，复制当前K线数据到剪贴板',
          shortcut: 'Ctrl + C',
        },
        {
          name: '删除画线',
          description: '选中画线后删除该画线对象',
          shortcut: 'Delete',
        },
      ]
    },
    {
      title: '键盘精灵',
      items: [
        {
          name: '打开键盘精灵',
          description: '打开快速搜索面板，可搜索品种、指标或执行命令',
          shortcut: 'S',
        },
        {
          name: '切换标签页',
          description: '在键盘精灵中切换品种/指标/命令标签',
          shortcut: 'I / C',
        },
        {
          name: '选择项目',
          description: '在搜索结果中上下移动选择',
          shortcut: '↑ / ↓',
        },
        {
          name: '确认选择',
          description: '确认当前选择并关闭键盘精灵',
          shortcut: 'Enter',
        },
        {
          name: '关闭精灵',
          description: '关闭键盘精灵面板',
          shortcut: 'ESC',
        },
      ]
    },
    {
      title: '页面导航',
      items: [
        {
          name: '首页',
          description: '访问系统首页仪表盘',
          shortcut: 'Alt + 1',
        },
        {
          name: '外汇行情',
          description: '访问外汇行情分析页面',
          shortcut: 'Alt + 2',
        },
        {
          name: '数据源管理',
          description: '访问数据源管理页面',
          shortcut: 'Alt + 3',
        },
        {
          name: '采集任务',
          description: '访问采集任务管理页面',
          shortcut: 'Alt + 4',
        },
      ]
    },
  ]
}

/**
 * 获取全部帮助内容.
 */
export const getAllHelpContent = (): HelpSection[] => {
  return [
    ...getChartHelpContent(),
    ...getDataManagementHelpContent(),
    ...getShortcutsHelpContent(),
  ]
}