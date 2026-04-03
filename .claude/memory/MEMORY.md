# FDAS项目记忆索引

> 此文件由Claude Code自动加载，保持在200行以内。

## 项目概述
- 名称: FDAS（金融数据抓取与分析系统）
- 目标: USDCNH汇率数据采集与可视化
- 技术栈: FastAPI + Vue3 + PostgreSQL + AKShare + TA-Lib
- 目录: `/Users/chao/.local/bin/Projects/fdas`

## 当前状态
- 阶段: 第一阶段（技术框架搭建）
- 模块: SQLAlchemy模型定义
- 进度: 20% (7/35)
- 详情: [progress.md](progress.md)

## 开发策略
- **最小功能增量**：每次只完成1个模块
- **独立可测试**：每个模块有明确验收标准
- **中断恢复**：通过progress.md快速定位进度

## 已完成模块（数据库层 11/35）
1. 项目目录结构
2. Claude记忆框架
3. PRD需求设计文档
4. ARCHITECTURE技术架构文档
5. CODE_STANDARDS代码规范文档
6. PERMISSION_DESIGN权限设计文档
7. PHASE1_DESIGN第一阶段详细设计
8. SQLAlchemy模型定义
9. Alembic配置
10. 迁移脚本创建
11. 迁移执行验证

## 下一步任务
**当前**: 数据库连接池（后端基础层第1项）
**后续**: 配置验证 → 日志配置验证 → 全局异常处理

## 技术决策速查
| 决策 | 选择 |
|------|------|
| 认证 | Session+Cookie(PostgreSQL) |
| 缓存 | Python内存(cachetools) |
| 技术指标 | TA-Lib |
| 日志 | 标准logging |
| 权限控制 | 前后端双重 |
| 数据量 | 1000条 |

## 开发策略（自动选择）
- **直接开发**：模型、配置、基础设施、前端组件 → 完成后 `/code-review`
- **TDD开发**：业务API、认证、采集服务、技术指标 → 使用 `/tdd` 命令
- **详情**：见 [progress.md](progress.md) 开发策略部分

## MCP配置（已就绪）
- context7: 库文档查询 ✅
- postgres: 数据库操作 ✅ (新添加)
- github: 代码搜索 ✅
- memory: 记忆持久化 ✅

## Skill配置（已就绪）
- python-patterns ✅
- python-testing ✅
- postgres-patterns ✅
- docker-patterns ✅

## 关键文件路径
```
docs/PRD.md                  # 需求设计
docs/ARCHITECTURE.md         # 技术架构
docs/CODE_STANDARDS.md       # 代码规范
docs/PERMISSION_DESIGN.md    # 权限设计
docs/PHASE1_DESIGN.md        # 第一阶段设计
.claude/memory/progress.md   # 开发进度
backend/app/models/          # 待开发
```