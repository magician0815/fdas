# FDAS版本变更日志模板

## 版本 X.X.X (示例)

**发布日期**: YYYY-MM-DD

---

### 新增功能

- 功能1: 简要描述
- 功能2: 简要描述

### 功能改进

- 改进1: 简要描述
- 改进2: 简要描述

### Bug修复

- Bug1: 描述 + Issue编号
- Bug2: 描述 + Issue编号

---

### 数据库变更

| 类型 | 说明 |
|------|------|
| 新增表 | `table_name` - 表用途说明 |
| 新增字段 | `table.field` - 字段用途说明 |
| 新增索引 | `idx_name` - 索引用途说明 |
| 数据迁移 | 数据迁移说明 |

**迁移脚本**: `versions/X.X.X/migrations.sql`

---

### API变更

| 类型 | 接口 | 说明 |
|------|------|------|
| 新增 | `/api/v1/xxx` | 接口说明 |
| 修改 | `/api/v1/xxx` | 参数变更说明 |
| 删除 | `/api/v1/xxx` | 删除原因说明 |

---

### 前端变更

| 类型 | 组件/文件 | 说明 |
|------|---------|------|
| 新增 | `Component.vue` | 组件说明 |
| 修改 | `Component.vue` | 修改说明 |

---

### 配置变更

| 配置项 | 变更类型 | 说明 |
|--------|---------|------|
| `NEW_CONFIG` | 新增 | 配置说明 |
| `OLD_CONFIG` | 修改默认值 | 新默认值说明 |

---

### 部署注意事项

1. 执行数据库迁移:
   ```bash
   cd deployment-packages/update
   ./upgrade.sh --version X.X.X
   ```

2. 更新环境变量:
   - 添加新配置项
   - 修改默认值

3. 重启服务:
   ```bash
   docker-compose restart fdas-app
   ```

---

### 升级步骤

**多容器方案**:
```bash
# 检查当前版本
curl http://localhost:8000/api/health

# 升级
cd deployment-packages/update
./upgrade.sh --version X.X.X

# 验证
curl http://localhost:8000/api/health
```

**单容器方案**:
```bash
# 停止服务
supervisorctl stop fdas_backend

# 执行数据库迁移
psql -U fdas -d fdas -f versions/X.X.X/migrations.sql

# 更新代码
git pull origin main

# 重启服务
supervisorctl start fdas_backend
```

---

### 回滚步骤

如升级后发现问题，执行回滚:
```bash
cd deployment-packages/update
./rollback.sh --version X.X.X
```

---

### 兼容性说明

- Python版本要求: 3.13+
- PostgreSQL版本要求: 16+
- Node.js版本要求: 18+

---

### 安全更新

| 项目 | 说明 |
|------|------|
| SESSION_SECRET | 无变更 |
| CORS | 新增允许域名配置 |
| 密码策略 | 无变更 |