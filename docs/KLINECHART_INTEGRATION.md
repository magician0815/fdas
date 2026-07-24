# FDAS KLineChart 集成设计文档

> 金融数据抓取与分析系统 — KLineChart 图表引擎集成方案

**版本**: 1.0
**创建日期**: 2026-07-21
**作者**: FDAS Team

---

## 一、方案概述

FDAS V1.0.0 起，金融K线图表由自研 ECharts 方案迁移至 [KLineChart](https://github.com/klinecharts/KLineChart) (MIT License) 开源图表库。

### 迁移原因

| 维度 | 自研 ECharts | KLineChart |
|------|-------------|-----------|
| 代码量 | ~7,000 行自研代码 | ~1,800 行包装代码 |
| 内置功能 | 仅 K线/成交量/MACD | 27 个指标 + 15 种画线工具 |
| 维护成本 | 高（每功能需自研） | 低（上游持续更新） |
| 性能 | ECharts 渲染 | Canvas 直接绘制（40KB gzipped） |
| 多副图 | 手动 ECharts grid 布局 | 自动 Pane 布局 |

### 核心技术栈

- **KLineChart v10** — Canvas 渲染引擎，零依赖，完全离线
- **Vue 3 Composition API** — UI 壳层和组件封装
- **TypeScript** — 完整类型支持
- **Pinia** — 图表状态管理
- **FastAPI + PostgreSQL** — 后端数据源（离线运行）

---

## 二、架构关系

```
Vue 3 Application Layer (UI Shell)
  ├── MarketOverview.vue      ← 统一行情页面
  ├── ChartDashboard.vue      ← KLineChart 包装器
  ├── ChartToolbar.vue        ← 市场自适应工具栏
  └── RangeStatsPanel.vue     ← 区间统计 Vue 浮层

        ↓ (调用)

KLineChart Engine (Rendering Engine)
  ├── init() / dispose()      ← Canvas 实例管理
  ├── setDataLoader()         ← 离线数据管道
  ├── createIndicator()       ← 技术指标
  ├── createOverlay()         ← 画线工具
  └── registerStyles()        ← 主题系统

        ↑ (扩展)

FDAS Custom Extensions
  ├── OI (持仓量指标)         ← registerIndicator
  ├── YIELD / YIELD_SPREAD    ← registerIndicator (债券)
  ├── limitUpDown             ← registerOverlay (涨跌停线)
  ├── gapMarker               ← registerOverlay (跳空)
  └── dividendMarker          ← registerOverlay (除权)
```

---

## 三、数据流设计

```
PostgreSQL (fdas-db)
    ↓ SQLAlchemy async
FastAPI Backend
    ↓ JSON (RESTful API)
useDataLoader composable
    ↓ convertToKLineData()
KLineData[] 数组 (完全在浏览器内存)
    ↓ setDataLoader({ getBars })
KLineChart Canvas 渲染

全程离线，无需任何在线 API
```

---

## 四、市场配置系统

通过 MarketProfile 声明式定义 7 个市场：

| 市场 | 精度 | 涨跌停 | 复权 | 副图 | 特殊功能 |
|------|------|--------|------|------|---------|
| A股 | 2位 | 10%/20%/5%/30% | 前/后复权 | VOL+MACD | ST检测/停牌/除权 |
| 港股 | 3位 | 无 | 无 | VOL+MACD | 除权 |
| 美股 | 2位 | 无 | 前/后复权 | VOL+MACD | 绿涨红跌 |
| 外汇 | 4位 | 无 | 无 | MACD | 24H/服务端指标 |
| 期货 | 品种可变 | 10% | 无 | OI+MACD | 主力合约 |
| 国内债券 | 4位 | 无 | 无 | 收益率 | — |
| 美债 | 4位 | 无 | 无 | 收益率+利差 | 中美利差 |

---

## 五、自定义扩展清单

### 指标 (registerIndicator)

| 名称 | 文件 | 用途 |
|------|------|------|
| OI | `chartExtensions/openInterest.ts` | 期货持仓量柱状图 |
| YIELD | `chartExtensions/yieldSpread.ts` | 债券收益率曲线 |
| YIELD_SPREAD | `chartExtensions/yieldSpread.ts` | 中美利差曲线 |

### 覆盖层 (registerOverlay)

| 名称 | 文件 | 用途 |
|------|------|------|
| limitUpDown | `chartExtensions/limitUpDown.ts` | 涨跌停价格虚线和昨收参考线 |
| gapMarker | `chartExtensions/gapMarker.ts` | 跳空缺口高亮 |
| dividendMarker | `chartExtensions/dividendMarker.ts` | 除权除息事件标记 |

---

## 六、离线数据接入

KLineChart 通过 `setDataLoader` 机制完全离线运行：

```typescript
chart.setDataLoader({
  getBars: ({ type, timestamp, callback }) => {
    // 从本地 Pinia Store 或 API 响应数组切片数据
    const sorted = [...allData].sort((a, b) => a.timestamp - b.timestamp)
    if (type === 'init') callback(sorted, { forward: false })
    else callback([])
  }
})
```

数据格式仅需 6 个字段：
```typescript
{ timestamp, open, high, low, close, volume }
```

---

## 七、与 ECharts/TradingView 方案对比

| 维度 | KLineChart | ECharts | TradingView |
|------|-----------|---------|-------------|
| 许可证 | MIT (免费) | Apache 2.0 (免费) | 商业授权 |
| 包体积 | ~40KB gzipped | ~200KB gzipped | ~500KB+ |
| 离线支持 | 完全离线 | 完全离线 | 有限制 |
| 内置K线 | 完整金融图表 | 仅基础 candlestick 系列 | 完整 |
| 自定义指标 | registerIndicator | 手动 series | Pine Script |
| Vue 3 集成 | 简单 (init/dispose) | echarts 包 + vue-echarts | 有限 |
| 中文本地化 | registerLocale | 手动配置 | 部分 |

---

## 八、核心设计原则

### 8.1 统一渲染引擎

**原则**: 所有市场的 K 线图表必须通过同一个 `ChartDashboard` 组件渲染，底层使用 KLineChart v10 Canvas 引擎。禁止各市场独立实现图表逻辑。

**路由**: `/market-overview` → `MarketOverview` → `ChartDashboard`

**架构保证**:
- 新增市场只需注册 `MarketProfile`，不需要修改任何图表组件代码
- 所有市场共享同一套 KLineChart v10 初始化流程（`setSymbol` → `setPeriod` → `setDataLoader`）
- Bug 修复一次即可覆盖所有市场

### 8.2 声明式市场差异化

**原则**: 市场间差异通过 `MarketProfile.features` 声明式开关控制，不在组件中硬编码 `if (market === 'xxx')`。

| 差异化维度 | 实现方式 | 示例 |
|-----------|---------|------|
| 涨跌停 | `features.limitUpDown` + `limitUpDownSubTypes` | A股主板10%, 科创板20%, ST股5% |
| 复权 | `features.adjustment` | A股前/后复权, 外汇无复权 |
| 副图指标 | `defaultIndicators` + `subChartSlots` | 期货多OI, 债券多YIELD |
| 颜色方向 | `colorDirection` | A股红涨绿跌, 美股绿涨红跌 |
| 精度 | `pricePrecision` | 外汇4位, A股2位 |
| 交易时间 | `features.continuousTrading` | 外汇24H, A股固定时段 |
| 对数坐标 | `features.logScale` | A股支持, 债券不支持 |
| 指标策略 | `indicatorStrategy` | 外汇服务端, 其他客户端 |

### 8.3 扩展即注册

**原则**: 所有自定义指标和覆盖层通过 KLineChart 全局注册机制（`registerIndicator` / `registerOverlay`）添加，注册后所有图表实例自动可用。

当前扩展清单:
| 扩展名 | 类型 | 适用市场 | 用途 |
|--------|------|---------|------|
| OI | registerIndicator | futures_cn | 持仓量柱状图 |
| YIELD | registerIndicator | bond_cn, bond_us | 收益率曲线 |
| YIELD_SPREAD | registerIndicator | bond_us | 中美利差 |
| limitUpDown | registerOverlay | stock_cn, futures_cn | 涨跌停线 |
| gapMarker | registerOverlay | stock_cn, stock_hk | 跳空缺口 |
| dividendMarker | registerOverlay | stock_cn, stock_hk, stock_us | 除权标记 |

### 8.4 新增市场流程

**只需 4 步，不修改任何组件代码**:

1. 在 `useMarketProfile.ts` 定义新的 `MarketProfile` 对象
2. 如有特有指标，在 `chartExtensions/` 添加 `registerIndicator` 或 `registerOverlay`
3. 在 `router/index.js` 添加 `/market/{new-market}` 路由
4. 在 `Sidebar.vue` "多市场数据"子菜单中添加菜单项

```typescript
// 示例: 新增加密货币市场
const crypto: MarketProfile = {
  id: 'crypto',
  displayName: '加密货币',
  colorDirection: 'green-up-red-down',
  pricePrecision: 2,
  features: { limitUpDown: false, adjustment: false, ... },
  defaultIndicators: ['MA', 'VOL', 'MACD'],
  subChartSlots: [
    { id: 'volume', indicatorName: 'VOL', defaultVisible: true },
    { id: 'macd', indicatorName: 'MACD', defaultVisible: true },
  ],
  // ...其余配置
}
registerMarketProfile(crypto)
```
