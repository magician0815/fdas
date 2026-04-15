# 测试覆盖率提升计划

> 当前覆盖率：58%，目标：80%

**创建日期**: 2026-04-15
**更新日期**: 2026-04-15
**策略**: 核心服务层优先

---

## 一、当前覆盖率分析

### 已达标模块（≥80%）

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| auth_service.py | 100% | ✅ 达标 |
| user_service.py | 100% | ✅ 达标 |
| technical_service.py | 99% | ✅ 达标 |
| session_service.py | 84% | ✅ 达标 |
| scheduler_service.py | 100% | ✅ 达标 |
| collection_service.py | 100% | ✅ 达标 |
| forex_daily_service.py | 97% | ✅ 达标 |
| adjustment_service.py | 98% | ✅ 达标 |
| period_aggregation_service.py | 98% | ✅ 达标 |
| config/settings.py | 100% | ✅ 达标 |
| config/logging.py | 100% | ✅ 达标 |
| models/* | 95-100% | ✅ 达标 |

### 需提升的API模块

| 模块 | 当前覆盖率 | 目标覆盖率 |
|------|------------|------------|
| auth.py | 74% | 80%+ |
| users.py | 49% | 80%+ |
| fx_data.py | 28% | 80%+ |
| collection_tasks.py | 19% | 80%+ |

### 未覆盖的服务模块

| 模块 | 当前覆盖率 | 状态 |
|------|------------|------|
| chart_template_service.py | 0% | 待开发 |
| main_contract_service.py | 0% | 待开发 |
| websocket_service.py | 0% | 待开发 |
| stock_utils.py | 0% | 待开发 |

---

## 二、测试开发计划

### Phase 1：核心服务层测试（已完成）

| 任务 | 目标模块 | 覆盖率 | 状态 |
|------|----------|--------|------|
| T1.1 | scheduler_service.py 测试 | 100% | ✅ 完成 |
| T1.2 | collection_service.py 测试 | 100% | ✅ 完成 |
| T1.3 | forex_daily_service.py 测试 | 97% | ✅ 完成 |
| T1.4 | adjustment_service.py 测试 | 98% | ✅ 完成 |
| T1.5 | period_aggregation_service.py 测试 | 98% | ✅ 完成 |

### Phase 2：API层测试（已完成）

| 任务 | 目标模块 | 测试数 | 状态 |
|------|----------|--------|------|
| T2.1 | auth.py API测试补充 | 6 | ✅ 完成 |
| T2.2 | users.py API测试 | 6 | ✅ 完成 |
| T2.3 | fx_data.py API测试 | 8 | ✅ 完成 |
| T2.4 | collection_tasks.py API测试 | 13 | ✅ 完成 |
| T2.5 | datasources.py API测试 | 12 | ✅ 完成 |

### Phase 3：集成测试修复

| 任务 | 目标 | 预估工作量 |
|------|------|------------|
| T3.1 | 修复test_integration.py导入错误 | 0.5天 |
| T3.2 | 修复test_akshare_collector.py错误 | 0.5天 |
| T3.3 | 添加数据库Mock配置 | 0.5天 |

---

## 三、测试文件结构

```
backend/tests/
├── test_auth_service.py      ✅ 完成 (100%)
├── test_user_service.py      ✅ 完成 (100%)
├── test_session_service.py   ✅ 完成 (84%)
├── test_technical_service.py ✅ 完成 (99%)
├── test_scheduler_service.py ✅ 完成 (100%)
├── test_collection_service.py ✅ 完成 (100%)
├── test_forex_daily_service.py ✅ 完成 (97%)
├── test_adjustment_service.py ✅ 完成 (98%)
├── test_period_aggregation_service.py ✅ 完成 (98%, 60 tests)
├── test_auth_api.py          ⚠️ 部分完成
├── test_auth_api_full.py     ✅ 新增 (6 tests)
├── test_users_api.py         ✅ 新增 (6 tests)
├── test_fx_data_api.py       ✅ 新增 (8 tests)
├── test_collection_tasks_api.py ✅ 新增 (13 tests)
├── test_datasources_api.py   ✅ 新增 (12 tests)
├── test_integration.py       ❌ 需修复
└── test_akshare_collector.py ❌ 需修复
```

---

## 四、下一步行动

### Phase 3 - 集成测试修复

修复失败的集成测试：
- test_integration.py (4个错误)
- test_akshare_collector.py (1个失败)

---

**当前统计**
- 总测试数：445 passing
- 覆盖率：58%（目标80%）
- Phase 1：100%完成（核心服务层）
- Phase 2：100%完成（API层）
- Phase 3：待开始

---

**文档结束**