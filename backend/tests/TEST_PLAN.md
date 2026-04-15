# 测试覆盖率提升计划

> 当前覆盖率：70%，目标：80%

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
| chart_template_service.py | 83% | ✅ 达标 |
| main_contract_service.py | 97% | ✅ 达标 |
| websocket_service.py | 60% | ⚠️ 需提升 |
| stock_utils.py | 97% | ✅ 达标 |
| config/settings.py | 100% | ✅ 达标 |
| config/logging.py | 100% | ✅ 达标 |
| models/* | 95-100% | ✅ 达标 |

### 需提升的API模块

| 模块 | 当前覆盖率 | 目标覆盖率 |
|------|------------|------------|
| auth.py | 95% | ✅ 达标 |
| users.py | 49% | 80%+ |
| fx_data.py | 28% | 80%+ |
| collection_tasks.py | 19% | 80%+ |
| datasources.py | 27% | 80%+ |
| forex_symbols.py | 32% | 80%+ |

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

### Phase 3：集成测试修复（已完成）

| 任务 | 目标 | 状态 |
|------|------|------|
| T3.1 | 修复test_akshare_collector.py方法名错误 | ✅ 完成 |
| T3.2 | 修复test_integration.py数据库依赖 | ✅ 完成 |
| T3.3 | 标记需要完整数据库的测试为skip | ✅ 完成 |

### Phase 4：未覆盖服务层测试（已完成）

| 任务 | 目标模块 | 测试数 | 状态 |
|------|----------|--------|------|
| T4.1 | stock_utils.py 测试 | 28 | ✅ 完成 |
| T4.2 | main_contract_service.py 测试 | 18 | ✅ 完成 |
| T4.3 | websocket_service.py 测试 | 24 | ✅ 完成 |
| T4.4 | chart_template_service.py 测试 | 16 | ✅ 完成 |

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
├── test_auth_api_full.py     ✅ 完成 (6 tests)
├── test_users_api.py         ✅ 完成 (6 tests)
├── test_fx_data_api.py       ✅ 完成 (8 tests)
├── test_collection_tasks_api.py ✅ 完成 (13 tests)
├── test_datasources_api.py   ✅ 完成 (12 tests)
├── test_integration.py       ✅ 修复 (4 skipped)
├── test_akshare_collector.py ✅ 修复 (5 tests)
├── test_stock_utils.py       ✅ 新增 (28 tests)
├── test_main_contract_service.py ✅ 新增 (18 tests)
├── test_websocket_service.py ✅ 新增 (24 tests)
├── test_chart_template_service.py ✅ 新增 (16 tests)
```

---

## 四、下一步行动

### Phase 5 - API层深度测试

为低覆盖率API模块添加授权测试：
- collection_tasks.py (19% -> 80%+)
- datasources.py (27% -> 80%+)
- fx_data.py (28% -> 80%+)
- forex_symbols.py (32% -> 80%+)

---

**当前统计**
- 总测试数：530 passing + 4 skipped
- 覆盖率：70%（目标80%）
- Phase 1：100%完成（核心服务层）
- Phase 2：100%完成（API层）
- Phase 3：100%完成（集成测试修复）
- Phase 4：100%完成（未覆盖服务层）

---

**文档结束**