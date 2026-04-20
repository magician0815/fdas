---
name: 开发进度
description: 项目当前开发状态、已完成工作、下一步任务
type: project
---

# FDAS 项目开发进度

> 最后更新: 2026-04-21

## 当前版本: 2.1.0

### 2026-04-21 更新: 可配置数据源系统

**版本**: 2.0.1 → 2.1.0

**新功能**:
- 可配置数据源系统（配置文件模式）
- 每个数据源拥有独立配置文件（JSON格式）
- 前端支持配置查看、编辑、导入、导出
- 采集器支持从数据库加载配置参数

**实现内容**:
1. **Phase 1** - 数据库模型扩展
   - datasources 表新增 config_file, config_version, config_updated_at 字段
   - 创建 DatasourceConfigSchema 配置验证类

2. **Phase 2** - 后端 API 扩展
   - GET /{id}/config - 获取配置
   - PUT /{id}/config - 更新配置
   - GET /{id}/export - 导出配置
   - POST /import - 导入配置

3. **Phase 3** - 采集器重构
   - 创建 BaseCollector 基类
   - 重构 AKShareCollector 支持外部配置
   - 修改 CollectionService 传递配置给采集器

4. **Phase 4** - 前端配置页面
   - DataSource.vue 添加配置编辑、导入导出功能
   - 新增 datasources.js API 函数

5. **Phase 5** - 数据库初始化
   - 更新 init-db.sql 添加配置字段
   - 添加默认配置文件

**代码审查修复**:
- DataSourceResponse 添加配置字段
- API 使用 Pydantic 模型替代 dict

**测试状态**:
- 所有原有接口正常工作
- 新增配置接口正常工作
- Pydantic 验证生效