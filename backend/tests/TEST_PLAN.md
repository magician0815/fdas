# 测试覆盖率提升计划

> 当前覆盖率：44%，目标：80%

**创建日期**: 2026-04-15
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
| config/settings.py | 100% | ✅ 达标 |
| config/logging.py | 100% | ✅ 达标 |
| models/* | 95-100% | ✅ 达标 |

### 需提升的核心服务模块

| 模块 | 当前覆盖率 | 目标覆盖率 | 优先级 |
|------|------------|------------|--------|
| scheduler_service.py | 42% | 80% | P1 |
| collection_service.py | 21% | 80% | P1 |
| forex_daily_service.py | 23% | 80% | P1 |
| adjustment_service.py | 22% | 80% | P2 |
| period_aggregation_service.py | 16% | 80% | P2 |

### 需提升的API模块

| 模块 | 当前覆盖率 | 目标覆盖率 |
|------|------------|------------|
| auth.py | 74% | 80%+ |
| users.py | 49% | 80%+ |
| fx_data.py | 28% | 80%+ |
| collection_tasks.py | 19% | 80%+ |

---

## 二、测试开发计划

### Phase 1：核心服务层测试（优先）

**目标**: 将核心服务覆盖率提升到80%+

| 任务 | 目标模块 | 预估工作量 |
|------|----------|------------|
| T1.1 | scheduler_service.py 测试 | 2天 |
| T1.2 | collection_service.py 测试 | 2天 |
| T1.3 | forex_daily_service.py 测试 | 2天 |
| T1.4 | adjustment_service.py 测试 | 1天 |
| T1.5 | period_aggregation_service.py 测试 | 1天 |

### Phase 2：API层测试

**目标**: 将API覆盖率提升到80%+

| 任务 | 目标模块 | 预估工作量 |
|------|----------|------------|
| T2.1 | auth.py API测试补充 | 0.5天 |
| T2.2 | users.py API测试 | 1天 |
| T2.3 | fx_data.py API测试 | 1天 |
| T2.4 | collection_tasks.py API测试 | 1天 |
| T2.5 | datasources.py API测试 | 1天 |

### Phase 3：集成测试修复

**目标**: 修复集成测试，确保端到端功能可用

| 任务 | 目标 | 预估工作量 |
|------|------|------------|
| T3.1 | 修复test_integration.py导入错误 | 0.5天 |
| T3.2 | 修复test_akshare_collector.py错误 | 0.5天 |
| T3.3 | 添加数据库Mock配置 | 0.5天 |

---

## 三、下一步行动

### 立即执行

1. **T1.1** - scheduler_service.py 测试开发
   - 创建 `test_scheduler_service.py`
   - 测试任务调度、启停、状态管理

2. 提交当前修复的代码变更
   - `app/core/deps.py` - Python兼容性修复
   - `app/schemas/datasource.py` - 语法错误修复

---

## 四、测试文件结构规划

```
backend/tests/
├── test_auth_service.py      ✅ 完成 (100%)
├── test_user_service.py      ✅ 完成 (100%)
├── test_session_service.py   ✅ 完成 (84%)
├── test_technical_service.py ✅ 完成 (99%)
├── test_scheduler_service.py 📝 待开发
├── test_collection_service.py 📝 待开发
├── test_forex_daily_service.py 📝 待开发
├── test_auth_api.py          ⚠️ 部分完成 (74%)
├── test_integration.py       ❌ 需修复
└── test_akshare_collector.py ❌ 需修复
```

---

**文档结束**