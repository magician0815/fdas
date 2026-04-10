# 专业行情走势功能实现计划

> 本文档定义专业行情走势功能的分阶段实现计划，按最小功能点逐个开发

**创建日期**: 2026-04-11
**预估总工作量**: 14-17周（70-82天）

---

## 一、需求确认摘要

| 确认项 | 决策 |
|--------|------|
| 市场范围 | 三大市场全覆盖（股票、期货、外汇） |
| 开发方式 | 按最小功能点逐个开发 |
| 渲染引擎 | 继续使用ECharts |
| 实时数据 | 暂不考虑，页面刷新获取最新数据 |
| 画线存储 | 画线内容不保存（刷新消失），工具设置保存在服务端 |
| 历史数据 | 根据后台存储时间长度确定范围 |
| 周期范围 | 全周期覆盖（1分钟~年K） |

---

## 二、功能点分级清单

### 功能分级原则

| 级别 | 定义 | 预估时间 | 优先级 |
|------|------|----------|--------|
| P0 | 核心渲染功能，无此功能系统不可用 | 2周 | 最高 |
| P1 | 基础交互功能，提升用户体验 | 1周 | 高 |
| P2 | 进阶功能，专业用户需求 | 2周 | 中 |
| P3 | 专业功能，高度专业用户需求 | 3-4周 | 低 |

---

## 三、P0级功能详细描述（15项）

### F001 - K线基础渲染（蜡烛图）

**功能描述**: 实现标准蜡烛图渲染，红涨绿跌配色，支持OHLC四个价格点渲染

**验收标准**:
- [ ] 蜡烛图正确渲染OHLC数据
- [ ] 红色表示上涨，绿色表示下跌
- [ ] 开盘价、收盘价、最高价、最低价正确显示
- [ ] 价格精度根据品种自动适配（外汇4位小数，股票2位）

**预估工作量**: 1天

**依赖关系**: 无依赖，可独立开发

**实现方案**:
```javascript
// ECharts candlestick配置
series: [{
  type: 'candlestick',
  data: ohlcData,
  itemStyle: {
    color: '#ef5350',   // 上涨红色
    color0: '#26a69a',  // 下跌绿色
    borderColor: '#ef5350',
    borderColor0: '#26a69a'
  }
}]
```

---

### F002 - K线形态切换（蜡烛图/折线图）

**功能描述**: 支持蜡烛图与收盘价折线图一键切换，切换时无闪屏

**验收标准**:
- [ ] 一键切换按钮，切换动画平滑
- [ ] 切换后数据范围保持一致
- [ ] 记住用户上次选择的形态

**预估工作量**: 0.5天

**依赖关系**: 依赖F001

**实现方案**:
```javascript
// 切换逻辑
const chartType = ref('candlestick')
const toggleChartType = () => {
  chartType.value = chartType.value === 'candlestick' ? 'line' : 'candlestick'
  updateSeries()
}
```

---

### F003 - 价格坐标轴系统

**功能描述**: 实现左右双价格轴，支持固定坐标、动态坐标模式

**验收标准**:
- [ ] 左侧价格轴显示当前屏最高最低价范围
- [ ] 右侧价格轴可选显示
- [ ] 缩放时价格轴自动适配
- [ ] 价格精度根据品种自动适配

**预估工作量**: 0.5天

**依赖关系**: 依赖F001

---

### F004 - 基准线标注

**功能描述**: 标注昨收价/前结算价基准线，开盘价、收盘价基准线

**验收标准**:
- [ ] 昨收价虚线贯穿全图
- [ ] 开盘价、收盘价可选标注
- [ ] 基准线颜色可配置
- [ ] 鼠标悬浮显示基准线数值

**预估工作量**: 0.5天

**依赖关系**: 依赖F001、F003

**实现方案**:
```javascript
// markLine配置
markLine: {
  data: [
    { yAxis: lastClosePrice, name: '昨收', lineStyle: { color: '#999', type: 'dashed' } }
  ]
}
```

---

### F005 - 市场识别系统

**功能描述**: 自动识别品种类型（股票/期货/外汇），匹配对应渲染规则

**验收标准**:
- [ ] 根据品种代码自动识别市场类型
- [ ] 外汇：无涨跌停，4位小数，24小时交易
- [ ] 股票：涨跌停标注（10%/20%/5%），2位小数，固定交易时段
- [ ] 期货：涨跌停标注，主力合约标识，日夜盘

**预估工作量**: 1天

**依赖关系**: 无依赖，可独立开发

**实现方案**:
```javascript
// 市场类型识别
const getMarketType = (symbol) => {
  if (symbol.includes('USD') || symbol.includes('EUR')) return 'forex'
  if (symbol.match(/\d{4}$/)) return 'futures'
  return 'stock'
}

// 市场配置映射
const marketConfig = {
  forex: { decimal: 4, hasLimit: false, tradingHours: '24h' },
  stock: { decimal: 2, hasLimit: true, limitPercent: 10 },
  futures: { decimal: 2, hasLimit: true, limitPercent: null }
}
```

---

### F006 - 数据库扩展（分钟数据表）

**功能描述**: 创建分钟级K线数据表，支持多周期数据存储

**验收标准**:
- [ ] forex_intraday表创建（包含所有字段中文注释）
- [ ] 支持1分钟/3分钟/5分钟/15分钟等周期
- [ ] 按时间范围分区优化查询性能

**预估工作量**: 1天

**依赖关系**: 无依赖，可独立开发

**实现方案**:
```sql
-- 分钟数据表（按周期分区）
CREATE TABLE forex_intraday (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol_id UUID NOT NULL REFERENCES forex_symbols(id),
    period VARCHAR(10) NOT NULL,  -- 周期类型：1min/5min/15min等
    datetime TIMESTAMP NOT NULL,  -- 时间戳
    open NUMERIC(10, 4),          -- 开盘价
    high NUMERIC(10, 4),          -- 最高价
    low NUMERIC(10, 4),           -- 最低价
    close NUMERIC(10, 4),         -- 收盘价
    volume BIGINT,                -- 成交量
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN forex_intraday.id IS '数据唯一标识ID';
COMMENT ON COLUMN forex_intraday.symbol_id IS '关联货币对ID';
COMMENT ON COLUMN forex_intraday.period IS '周期类型（1min/5min/15min/30min/60min）';
COMMENT ON COLUMN forex_intraday.datetime IS '时间戳';
COMMENT ON COLUMN forex_intraday.open IS '开盘价';
COMMENT ON COLUMN forex_intraday.high IS '最高价';
COMMENT ON COLUMN forex_intraday.low IS '最低价';
COMMENT ON COLUMN forex_intraday.close IS '收盘价';
COMMENT ON COLUMN forex_intraday.volume IS '成交量';

CREATE INDEX idx_forex_intraday_symbol_period_time ON forex_intraday(symbol_id, period, datetime);
```

---

### F007 - 周期切换系统

**功能描述**: 实现全周期切换（1分钟~年K），切换时数据无缝加载

**验收标准**:
- [ ] 周期选择器：1min/3min/5min/15min/30min/60min/120min/日K/周K/月K/季K/年K
- [ ] 切换周期后数据自动加载
- [ ] 切换后视图范围保持一致（时间范围）
- [ ] 加载状态显示（loading indicator）

**预估工作量**: 1天

**依赖关系**: 依赖F006（分钟数据表）

---

### F008 - 成交量副图渲染

**功能描述**: 在K线图下方渲染成交量柱状图，颜色与K线涨跌同步

**验收标准**:
- [ ] 成交量柱状图正确渲染
- [ ] 红色柱表示上涨日成交量，绿色柱表示下跌日
- [ ] 成交量数值显示在Y轴
- [ ] 成交量柱与K线时间轴对齐

**预估工作量**: 0.5天

**依赖关系**: 依赖F001

**实现方案**:
```javascript
// 成交量series配置
series: [{
  type: 'bar',
  xAxisIndex: 0,
  yAxisIndex: 1,
  data: volumeData,
  itemStyle: {
    color: function(params) {
      return params.dataIndex % 2 === 0 ? '#ef5350' : '#26a69a'
    }
  }
}]
```

---

### F009 - 基础均线系统（MA）

**功能描述**: 实现MA均线叠加，支持自定义周期和颜色

**验收标准**:
- [ ] 默认显示MA5、MA10、MA20、MA60
- [ ] 支持添加/删除均线
- [ ] 每条均线颜色可配置
- [ ] 鼠标悬浮显示均线数值

**预估工作量**: 0.5天

**依赖关系**: 依赖F001

**实现方案**:
```javascript
// MA均线计算
const calculateMA = (data, period) => {
  const result = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push('-')
    } else {
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += data[i - j][1] // 收盘价
      }
      result.push(sum / period)
    }
  }
  return result
}

// ECharts series配置
series: [
  { type: 'line', name: 'MA5', data: calculateMA(ohlcData, 5), lineStyle: { color: '#1E90FF' } },
  { type: 'line', name: 'MA10', data: calculateMA(ohlcData, 10), lineStyle: { color: '#FF6347' } }
]
```

---

### F010 - MACD副图指标

**功能描述**: 实现MACD指标副图渲染（DIF、DEA、MACD柱）

**验收标准**:
- [ ] MACD（12,26,9）默认参数正确计算
- [ ] DIF线、DEA线、MACD柱正确渲染
- [ ] MACD柱颜色：正值红色，负值绿色
- [ ] 参数可自定义

**预估工作量**: 1天

**依赖关系**: 依赖F001

**实现方案**:
```javascript
// MACD计算
const calculateMACD = (data, shortPeriod = 12, longPeriod = 26, signalPeriod = 9) => {
  const closes = data.map(d => d.close)
  const emaShort = calculateEMA(closes, shortPeriod)
  const emaLong = calculateEMA(closes, longPeriod)
  const dif = emaShort.map((v, i) => v - emaLong[i])
  const dea = calculateEMA(dif, signalPeriod)
  const macd = dif.map((v, i) => (v - dea[i]) * 2)
  return { dif, dea, macd }
}
```

---

### F011 - 十字光标系统

**功能描述**: 实现十字光标，水平价格线+垂直时间线，主副图同步

**验收标准**:
- [ ] 鼠标移入自动显示十字光标
- [ ] 垂直线精准对齐K线中心
- [ ] 主副图垂直线100%同步
- [ ] 显示当前K线的OHLC数据
- [ ] 数据框固定位置不随光标移动

**预估工作量**: 1天

**依赖关系**: 依赖F001、F008、F010

**实现方案**:
```javascript
// ECharts axisPointer配置
axisPointer: {
  link: [{ xAxisIndex: 'all' }],
  label: {
    backgroundColor: '#777'
  },
  crossStyle: {
    color: '#999',
    width: 1,
    type: 'dashed'
  }
}

// tooltip固定位置
tooltip: {
  position: function(point, params, dom, rect, size) {
    return [10, 10] // 固定左上角
  }
}
```

---

### F012 - 缩放交互

**功能描述**: 实现鼠标滚轮缩放，Ctrl+框选缩放，保持光标位置不变

**验收标准**:
- [ ] 滚轮向前放大，向后缩小
- [ ] 缩放时光标位置不变（锚定缩放）
- [ ] Ctrl+鼠标框选放大选中区域
- [ ] 设置缩放边界（最小单根K线，最大全量历史）

**预估工作量**: 1天

**依赖关系**: 依赖F001

**实现方案**:
```javascript
// ECharts dataZoom配置
dataZoom: [
  {
    type: 'inside',
    xAxisIndex: [0, 1],
    start: 50,
    end: 100,
    minValueSpan: 1,  // 最小显示1根K线
    maxValueSpan: 1000  // 最大显示1000根K线
  },
  {
    type: 'slider',
    xAxisIndex: [0, 1],
    start: 50,
    end: 100
  }
]
```

---

### F013 - 平移交互

**功能描述**: 实现鼠标拖拽平移，Shift锁定方向，视图重置

**验收标准**:
- [ ] 左键拖拽左右平移历史K线
- [ ] Shift+拖拽锁定水平方向
- [ ] 双击/ESC重置到默认视图
- [ ] 平移边界控制

**预估工作量**: 0.5天

**依赖关系**: 依赖F012

---

### F014 - 外观系统（白天/夜间主题）

**功能描述**: 实现白天/夜间主题一键切换

**验收标准**:
- [ ] 白天主题：浅色背景，深色K线
- [ ] 夜间主题：深色背景，亮色K线
- [ ] 一键切换按钮
- [ ] 切换后所有组件颜色同步变化

**预估工作量**: 0.5天

**依赖关系**: 无依赖，可独立开发

**实现方案**:
```javascript
// 主题配置
const themes = {
  light: {
    background: '#ffffff',
    text: '#333333',
    upColor: '#ef5350',
    downColor: '#26a69a'
  },
  dark: {
    background: '#1a1a2e',
    text: '#e0e0e0',
    upColor: '#ef5350',
    downColor: '#26a69a'
  }
}

// 主题切换
const currentTheme = ref('light')
const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
  applyTheme(currentTheme.value)
}
```

---

### F015 - 数据校验机制

**功能描述**: 建立OHLC数据合法性校验，自动过滤脏数据

**验收标准**:
- [ ] 校验OHLC数据合法性（High >= Low，High >= Open/Close等）
- [ ] 校验时间序列连续性
- [ ] 异常数据标注提示，不渲染
- [ ] 缺失数据自动请求补全

**预估工作量**: 0.5天

**依赖关系**: 无依赖，可独立开发

**实现方案**:
```javascript
// 数据校验函数
const validateOHLC = (data) => {
  const errors = []
  data.forEach((d, i) => {
    if (d.high < d.low) errors.push(`第${i}条数据：最高价小于最低价`)
    if (d.high < Math.max(d.open, d.close)) errors.push(`第${i}条数据：最高价小于开盘/收盘价`)
    if (d.low > Math.min(d.open, d.close)) errors.push(`第${i}条数据：最低价大于开盘/收盘价`)
  })
  return { valid: errors.length === 0, errors }
}
```

---

## 四、P1级功能清单（20项）

| 编号 | 功能名称 | 预估工作量 | 依赖 |
|------|----------|------------|------|
| F016 | 分时价格线渲染 | 1天 | F006 |
| F017 | 分时均价线渲染 | 0.5天 | F016 |
| F018 | 涨跌幅基准轴（0轴） | 0.5天 | F016 |
| F019 | 分时成交量渲染 | 0.5天 | F016 |
| F020 | 分时图涨跌区间填充 | 0.5天 | F016 |
| F021 | 交易时段标注（休市留白） | 1天 | F005 |
| F022 | 区间统计功能 | 1天 | F011 |
| F023 | 区间统计面板（股票） | 0.5天 | F022 |
| F024 | 区间统计面板（期货） | 0.5天 | F022 |
| F025 | 区间统计面板（外汇） | 0.5天 | F022 |
| F026 | 键盘精灵（品种切换） | 1天 | 无 |
| F027 | 键盘精灵（指标切换） | 0.5天 | F026 |
| F028 | 光标锁定功能（空格键） | 0.5天 | F011 |
| F029 | 光标键盘微调（方向键） | 0.5天 | F028 |
| F030 | 光标数据一键复制 | 0.5天 | F011 |
| F031 | 成交量均线（VOL5/VOL10） | 0.5天 | F008 |
| F032 | 视图记忆功能 | 0.5天 | F012, F013 |
| F033 | 默认视图重置 | 0.5天 | F013 |
| F034 | 品种切换无缝加载 | 0.5天 | F007 |
| F035 | 加载状态优化 | 0.5天 | 无 |

---

## 五、P2级功能清单（30项）

### 画线工具（10项）

| 编号 | 功能名称 | 预估工作量 |
|------|----------|------------|
| F036 | 趋势线绘制 | 1天 |
| F037 | 水平线绘制 | 0.5天 |
| F038 | 垂直线绘制 | 0.5天 |
| F039 | 矩形绘制 | 0.5天 |
| F040 | 文字标注 | 0.5天 |
| F041 | 箭头标注 | 0.5天 |
| F042 | 画线工具栏 | 0.5天 |
| F043 | 画线选择/修改/删除 | 0.5天 |
| F044 | 画线端点磁吸 | 0.5天 |
| F045 | 画线工具设置保存（服务端） | 1天 |

### 进阶渲染（10项）

| 编号 | 功能名称 | 预估工作量 |
|------|----------|------------|
| F046 | K线特殊形态高亮（一字板） | 0.5天 |
| F047 | K线特殊形态高亮（跳空缺口） | 0.5天 |
| F048 | K线特殊形态高亮（长影线） | 0.5天 |
| F049 | 涨跌停K线标注（股票） | 0.5天 |
| F050 | 主力合约标识（期货） | 0.5天 |
| F051 | 涨跌停价标注线（股票/期货） | 0.5天 |
| F052 | 价格坐标对数模式 | 0.5天 |
| F053 | 副图高度拖拽调整 | 0.5天 |
| F054 | 副图最大化/最小化 | 0.5天 |
| F055 | 多日连续分时（1/2/3/5日） | 1天 |

### 进阶交互（10项）

| 编号 | 功能名称 | 预估工作量 |
|------|----------|------------|
| F056 | Alt+滚轮纵向缩放 | 0.5天 |
| F057 | Ctrl+方向键快速跳转 | 0.5天 |
| F058 | 快速定位到指定日期 | 0.5天 |
| F059 | 均线参数预设方案 | 0.5天 |
| F060 | 均线自定义保存 | 0.5天 |
| F061 | MACD参数自定义 | 0.5天 |
| F062 | 分时指标叠加（量比） | 0.5天 |
| F063 | 分时异动标记 | 1天 |
| F064 | 品种停牌/退市标识 | 0.5天 |
| F065 | 合约到期日标注（期货） | 0.5天 |

---

## 六、P3级功能清单（85项简要）

### 专业画线工具（20项）

黄金分割线、扩展线、时间周期线、江恩角度线、江恩方格、安德鲁音叉线、通道线、圆形、斐波那契弧线、速度阻力线、等距通道、平行通道等

### 股票复权系统（8项）

前复权、后复权、不复权切换，除权除息DR/DXR标注，复权因子计算，复权价格重算

### 期货连续合约（8项）

主力连续合约拼接，换月平滑处理，合约换月事件标注，保证金调整标注，持仓量异动标注

### 外汇专属功能（8项）

点值坐标轴，pip值换算，隔夜利息标注，交割日标注，货币对分类标识，点差指标

### 多周期联动（10项）

多周期同屏布局，长周期区间跳转短周期，周期同步画线，周期同步光标

### 专业指标体系（20项）

BOLL、KDJ、RSI、OBV、ATR、CCI、WR、DMI、SAR、BBI等全套指标

### 高级分时功能（11项）

Level2分时，逐笔成交分时，集合竞价虚拟量，多日分时叠加，分时买卖力道

---

## 七、开发顺序建议

### 阶段一：P0核心渲染（第1-2周）

**并行开发组A（无依赖）**:
- F005 市场识别系统
- F006 数据库扩展
- F014 外观系统
- F015 数据校验机制

**顺序开发组B**:
```
F001 K线基础渲染
  ↓
F002 K线形态切换
  ↓
F003 价格坐标轴系统
  ↓
F004 基准线标注
  ↓
F007 周期切换系统
  ↓
F008 成交量副图渲染
  ↓
F009 基础均线系统
  ↓
F010 MACD副图指标
  ↓
F011 十字光标系统
  ↓
F012 缩放交互
  ↓
F013 平移交互
```

---

### 阶段二：P1基础交互（第3周）

所有P1功能可并行开发，建议按功能组分组：

**分时图组**: F016-F021（可并行）
**交互组**: F022-F030（可并行）
**辅助组**: F031-F035（可并行）

---

### 阶段三：P2进阶功能（第4-5周）

**画线工具组**: F036-F045（顺序开发）
**进阶渲染组**: F046-F055（可并行）
**进阶交互组**: F056-F065（可并行）

---

### 阶段四：P3专业功能（第6-8周起）

按市场需求逐步实施：
- 外汇市场P3功能优先
- 股票市场复权系统次之
- 期货连续合约系统最后

---

## 八、里程碑定义

| 里程碑 | 时间点 | 验收标准 |
|--------|--------|----------|
| M1 | 第2周末 | P0全部完成，K线图可正常浏览、缩放、平移 |
| M2 | 第3周末 | P1全部完成，分时图可用，区间统计可用 |
| M3 | 第5周末 | P2全部完成，基础画线可用，进阶交互可用 |
| M4 | 第8周末 | P3外汇专属功能完成 |
| M5 | 第10周末 | 外汇市场全部功能完成 |
| M6 | 第13周末 | 股票市场全部功能完成 |
| M7 | 第17周末 | 三大市场全覆盖完成 |

---

## 九、风险与应对策略

| 风险 | 等级 | 应对策略 |
|------|------|----------|
| ECharts性能瓶颈 | 高 | 降采样+离屏缓存，必要时考虑lightweight-charts |
| 分钟数据采集频率 | 中 | 分批采集，优先采集常用周期 |
| 股票复权算法复杂 | 高 | 先实现不复权，逐步完善复权算法 |
| 期货换月拼接算法 | 高 | 参考成熟方案，分阶段实现 |
| 画线跨交易日对齐 | 中 | 基于时间戳而非索引对齐 |
| 多周期同步性能 | 中 | 按需加载，懒渲染 |
| 三大市场适配工作量 | 高 | 优先外汇，逐步扩展 |
| 浏览器兼容性 | 低 | 主流浏览器测试，降级兼容方案 |
| 移动端适配 | 低 | 响应式设计，触屏交互优化 |

---

## 十、验收标准

### 全局验收标准

1. **性能标准**
   - 首屏加载 < 2秒
   - 缩放/平移响应 < 100ms
   - 周期切换 < 500ms
   - 无明显卡顿、闪屏

2. **渲染标准**
   - OHLC数据精度正确
   - 时间轴对齐准确
   - 主副图同步无错位
   - 抗锯齿渲染清晰

3. **交互标准**
   - 鼠标/键盘操作响应准确
   - 光标定位精度 < 1像素偏差
   - 画线端点磁吸准确

4. **兼容标准**
   - Chrome/Firefox/Safari最新版兼容
   - 不同分辨率自适应
   - 高刷新率显示器流畅

---

## 十一、下一步行动

**建议从F001开始**：K线基础渲染是整个系统的核心，后续所有功能都依赖此基础。

开发流程遵循项目规范：
1. 使用 `/frontend-patterns` 指令进行前端设计
2. 数据库字段必须有中文注释
3. 每个功能点完成后进行代码审查
4. 逐步测试验收

---

**文档结束**