# FDAS 项目配置

## 版本
- **当前版本**: V2.0.0 (宏观数据采集模块)
- V1.0.0: KLineChart v10 图表引擎重构 + 多市场支持

## 技术栈
- 后端: FastAPI + SQLAlchemy + PostgreSQL + AKShare + httpx + BeautifulSoup + openpyxl
- 前端: Vue 3 + Vite + KLineChart v10(Canvas) + ECharts(Dashboard) + TypeScript
- Python 版本: 3.13+ (使用 venv-fdas-313 虚拟环境)
- 数据库: PostgreSQL (fdas@localhost:5432/fdas)

## 构建/运行命令
- 后端启动: `cd backend && SESSION_SECRET=xxx PYTHONPATH=. ./venv-fdas-313/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- 前端启动: `cd frontend && npm run dev`
- 前端构建: `cd frontend && npm run build`
- 运行测试: `cd backend && PYTHONPATH=. ./venv-fdas-313/bin/python -m pytest tests/ -q --tb=short`
- 数据库连接: `docker exec -it fdas-db psql -U fdas -d fdas`
- Docker 重建: `cd docker && docker compose build fdas-app && docker rm -f fdas-app && docker run -d --name fdas-app --network fdas-network -p 8000:8000 -e DATABASE_URL=postgresql+asyncpg://fdas:fdas@fdas-db:5432/fdas -e SESSION_SECRET=xxx -v $(pwd)/../frontend/dist:/app/static:ro docker-fdas-app`

## 架构约束
- API 路由: app/api/v1/ 下按资源分文件
- 服务层: app/services/ 下，业务逻辑不入路由
- 采集器: app/collectors/ 下，MacroBaseCollector 为宏观采集基类
- 数据库变更: 直接修改 docker/init-db.sql，不使用 Alembic 迁移
- 所有表字段必须有中文 comment

## V2.0 宏观数据采集模块
- 5 个美联储数据源: r-star-LW / r-star-HLW / r-star-LM / r-sep / longer-run-neutral
- 全部美国数据 (~900 条), 时间跨度 1960-2026
- 独立配置表 macro_datasource_configs + 分区表 macro_data_points + 日志表 macro_collection_logs
- 采集器: MacroBaseCollector 基类 + 4 个具体实现 (Excel/HTML/CSV/SEP表格)
- API: /api/v1/macro/configs /data /logs
- 前端: MacroDashboard / MacroConfigs / MacroData (独立一级菜单)

## 关键约定
- 前端设计使用 /frontend-patterns 指令
- 优先使用 memory 系统记录长期信息
- 多步骤任务完成后主动 /compact

## 已知问题/陷阱
- AKShare 部分接口返回中文货币对名，解析时注意编码
- datetime.utcnow 已弃用，使用 datetime.now(timezone.utc)
- SQLAlchemy 分区表 Identity Map 缺陷：需用原始 SQL 查询避免重复返回同一对象
- KLineChart 自定义扩展通过 registerIndicator/registerOverlay 全局注册
- Docker Desktop macOS 卷挂载有缓存问题，更新前端后需 restart 容器

---

# 上下文管理规则

## 本项目特殊要求

- 优先使用 memory 系统记录长期信息
- 大型工具输出（如完整文件内容）仅保留关键摘要
- 多步骤任务完成后主动使用 /compact
- 使用 /context-budget 定期检查上下文消耗
- 优先使用 context7 (/docs) 获取文档而非预加载

## 压缩策略

根据任务类型选择压缩级别：

- `/compact` 或 `/compact full` - 完整压缩（默认）
- `/compact debug` - 保留调试信息（排查问题时使用）
- `/compact minimal` - 最小化压缩

## 注意事项

- 不主动过滤错误详情（traceback）- 可能影响问题排查
- Debug/排查问题时保留完整输出
- 正常开发时可精简工具输出

## Compact 保留指令
执行 /compact 时始终保留：
- 修改的文件列表及修改内容摘要
- 测试结果（通过/失败/错误信息）
- 当前任务的 TODO 状态
- 架构决策及其理由
- 当前调试假设