# FDAS项目记忆索引

> 此文件由Claude Code自动加载，保持在200行以内。

## 项目概述
- 名称: FDAS（金融数据抓取与分析系统）
- 目标: 外汇汇率数据采集与可视化
- 技术栈: FastAPI + Vue3 + PostgreSQL + AKShare(forex_hist) + ECharts
- 目录: `/Users/chao/.local/bin/Projects/fdas`
- 当前版本: **2.1.0**

## 当前状态
- 阶段: 第一阶段（核心功能实现）
- 状态: 可配置数据源系统已完成

## 2026-04-21 更新: 版本 2.1.0

### 新功能: 可配置数据源系统
- 每个数据源拥有独立配置文件（JSON格式）
- 前端支持配置查看、编辑、导入、导出
- 采集器支持从数据库加载配置参数

### 数据库更新
- datasources表新增: config_file, config_version, config_updated_at

### API端点
- GET /{id}/config - 获取配置
- PUT /{id}/config - 更新配置
- GET /{id}/export - 导出配置
- POST /import - 导入配置

### 核心验收项状态

| 功能 | 状态 |
|------|------|
| 数据实际采集 | ✅ 完成 |
| 数据入库 | ✅ 完成 |
| 定时调度 | ✅ 完成 |
| K线/MA/MACD图表 | ✅ 完成 |
| 数据源配置功能 | ✅ 完成 |
| 采集任务配置功能 | ✅ 完成 |

## 技术决策
| 决策 | 选择 |
|------|------|
| 认证 | Session+Cookie(PostgreSQL) |
| 数据采集 | AKShare forex_hist接口 |
| 货币对格式 | 中文名称 + 英文代码 |
| 调度 | APScheduler |
| 前端图表 | ECharts |