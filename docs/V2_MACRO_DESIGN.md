# FDAS V2.0 宏观数据采集模块设计文档

> 金融数据分析系统 — 宏观数据采集模块详细设计

**版本**: 2.0
**创建日期**: 2026-07-29
**作者**: FDAS Team

---

## 一、模块概述

V2.0 宏观数据采集模块负责从 5 个美联储官方数据源自动采集自然利率(r-star)相关指标的时序数据。

### 1.1 设计原则

| 原则 | 说明 |
|------|------|
| **独立并行** | 不通过现有 market_registry/collection_service 驱动，独立模块运行 |
| **复用基础设施** | 复用 APScheduler 调度器、日志基础设施、数据库连接池 |
| **配置化管理** | 采集规则(URL/解析规则)全部配置化，支持前端编辑 |
| **增量采集** | 基于 publish_date 自动判断增量数据，避免重复 |

### 1.2 数据源概览

| 数据源 | 代码 | 类型 | 频率 | 来源机构 | 解析引擎 |
|--------|------|------|------|----------|----------|
| LW 模型 | r-star-LW | Excel | 季度 | New York Fed | openpyxl |
| HLW 模型 | r-star-HLW | Excel | 季度 | New York Fed | openpyxl |
| LM 模型 | r-star-LM | HTML | 季度 | Richmond Fed | beautifulsoup |
| SEP 预测 | r-sep | HTML | 按会议 | FOMC | beautifulsoup |
| 长期中性利率 | longer-run-neutral | JSON | 年度 | FEDS Notes | jsonpath |

---

## 二、数据库设计

### 2.1 表结构

```
macro_datasource_configs    宏观数据源配置表
macro_data_points           宏观数据点表 (按 publish_date 分区)
macro_collection_logs       宏观采集执行日志表
```

### 2.2 macro_datasource_configs

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 配置唯一标识 |
| name | VARCHAR(100) UNIQUE | 显示名称 |
| source_code | VARCHAR(50) UNIQUE | 数据源代码 |
| source_type | VARCHAR(30) | excel/html/json/csv |
| url | TEXT | 数据源 URL |
| parse_engine | VARCHAR(30) | openpyxl/beautifulsoup/jsonpath |
| parse_config | JSONB | 解析规则配置 |
| headers | JSONB | HTTP 请求头 |
| cron_expr | VARCHAR(100) | 定时采集表达式 |
| is_enabled | BOOLEAN | 是否启用 |
| last_collected_at | TIMESTAMPTZ | 上次采集时间 |
| last_status | VARCHAR(20) | 上次状态 |

### 2.3 macro_data_points

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 数据唯一标识 |
| config_id | UUID FK | 关联配置 |
| source_code | VARCHAR(50) | 数据源代码 |
| country | VARCHAR(30) | 国家/地区 |
| indicator_key | VARCHAR(100) | 指标键名 |
| value | NUMERIC(20,10) | 数值 |
| publish_date | DATE PK | 发布日期(分区键) |
| period_date | DATE | 数据所属期间 |
| frequency | VARCHAR(20) | quarterly/by_meeting/annual |
| raw_source_hash | VARCHAR(64) | SHA-256 行哈希 |

唯一约束: `(config_id, indicator_key, period_date, publish_date)`

### 2.4 分区策略

按 `publish_date` 年份 RANGE 分区，覆盖 2020-2028 + DEFAULT 分区。

---

## 三、采集器设计

### 3.1 类层次结构

```
MacroBaseCollector (ABC)
├── _fetch_raw()          异步 HTTP 请求 + tenacity 重试
├── parse_raw()           [abstract] 子类实现解析逻辑
├── _standardize()        转换为标准记录格式
├── _hash_row()           SHA-256 行哈希去重
└── collect()             完整流程: fetch→parse→standardize→增量过滤

具体实现:
├── MacroNYFedExcelCollector     openpyxl 解析 Excel
├── MacroRichmondHTMLCollector   beautifulsoup 解析 HTML 表格
├── MacroFOMCSEPCollector        SEP 表格特殊解析
└── MacroFEDSNotesCollector      catalog.data.gov API → CSV
```

### 3.2 parse_config 配置结构

```json
{
  "sheet_name": "data",
  "skiprows": 0,
  "table_index": 0,
  "columns": {"date": "Date", "r_star_lw": "r-star"},
  "indicator_key": "r_star_lw",
  "value_column": "median",
  "frequency": "quarterly",
  "country": "US",
  "multi_country": false
}
```

---

## 四、服务层设计

### 4.1 MacroConfigService

- 配置 CRUD (list/get/create/update/delete)
- 采集器工厂 (source_code → collector class 映射)
- 获取最大 publish_date (增量基线)
- parse_config 为每个采集器提供运行时配置

### 4.2 MacroCollectionService

- `load_enabled_configs()`: 启动时加载已启用配置到调度器
- `collect(config_id, full)`: 核心采集流程
  - full=True: 全量采集
  - full=False: 增量采集 (基于 MAX(publish_date))
- `enable_schedule()` / `disable_schedule()`: 调度管理
- `trigger_collect()`: 手动触发
- 采集日志全程记录 (running→success/failed)

### 4.3 与现有架构的关系

```
现有系统                           V2.0 宏观模块
┌──────────────┐                 ┌──────────────────────┐
│ collection_service│             │ macro_collection_service│
│ MARKET_SERVICE_MAP│            │ (独立编排)            │
└──────────────┘                 └──────┬───────────────┘
                                        │
┌──────────────┐                 ┌──────▼───────────────┐
│ scheduler_service│<------------│ macro_datasource_configs│
│ (复用)        │  job_id=       │ (独立配置表)          │
└──────────────┘  macro-{uuid}   └──────────────────────┘
```

---

## 五、API 设计

### 5.1 端点列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/macro/configs` | 配置列表 |
| GET | `/api/v1/macro/configs/{id}` | 配置详情 |
| POST | `/api/v1/macro/configs` | 创建配置 |
| PUT | `/api/v1/macro/configs/{id}` | 更新配置 |
| DELETE | `/api/v1/macro/configs/{id}` | 删除配置 |
| POST | `/api/v1/macro/configs/{id}/enable` | 启用调度 |
| POST | `/api/v1/macro/configs/{id}/disable` | 禁用调度 |
| POST | `/api/v1/macro/configs/{id}/collect` | 手动采集 |
| GET | `/api/v1/macro/data` | 分页查询数据 |
| GET | `/api/v1/macro/data/{source_code}/latest` | 最新数据 |
| GET | `/api/v1/macro/logs` | 采集日志查询 |

---

## 六、前端设计

### 6.1 导航

侧边栏新增独立一级菜单"宏观数据"，与"行情数据""数据采集""系统管理"并列。

### 6.2 页面

| 路由 | 组件 | 功能 |
|------|------|------|
| `/macro` | MacroDashboard.vue | 5个数据源状态卡片 + ECharts r-star 趋势图 |
| `/macro/configs` | MacroConfigs.vue | 配置列表 + 编辑(含 JSON 编辑器) + 采集/启停 |
| `/macro/data` | MacroData.vue | 筛选栏 + 分页表格 + ECharts 折线图 + CSV 导出 |

---

## 七、依赖新增

```txt
openpyxl>=3.1.0          # Excel 解析
beautifulsoup4>=4.12.0   # HTML 解析
lxml>=5.0.0              # bs4 快速解析器
jsonpath-ng>=1.6.0       # JSON 路径解析
pytest-mock>=3.12.0      # 测试 Mock
```

## 八、关键设计决策

1. **独立模块并行运行**: 不通过 market_registry 驱动，独立配置表和管理服务
2. **parse_config 配置化**: 全部解析规则存储在 JSONB 字段，支持前端动态修改
3. **SHA-256 行哈希去重**: 标准化的行内容哈希 + 唯一约束双重保障
4. **publish_date 增量**: 基于数据发布时间而非抓取时间判断增量
5. **按年分区**: 与现有 forex_daily/stock_daily 等表分区策略一致
