# FDAS 部署操作文档

> 金融数据抓取与分析系统 - 多容器部署方案操作指南
> Version: 2.0.1
> Updated: 2026-04-17

---

## 目录

1. [关键依赖说明](#1-关键依赖说明)
2. [环境变量配置](#2-环境变量配置)
3. [部署步骤](#3-部署步骤)
4. [常见问题与解决方案](#4-常见问题与解决方案)
5. [数据迁移注意事项](#5-数据迁移注意事项)
6. [安全配置检查清单](#6-安全配置检查清单)

---

## 1. 关键依赖说明

### 1.1 Python依赖用途

| 依赖包 | 版本要求 | 用途 | 缺失影响 |
|--------|---------|------|---------|
| `bcrypt` | >=4.0.0 | 密码哈希算法 | 登录时 `ModuleNotFoundError: No module named 'bcrypt'` |
| `psycopg2-binary` | >=2.9.0 | APScheduler PostgreSQL同步驱动 | 调度器启动失败 `ModuleNotFoundError: No module named 'psycopg2'` |
| `slowapi` | >=0.1.9 | API速率限制 | login接口返回 `INTERNAL_ERROR` |

### 1.2 APScheduler特殊依赖说明

**重要**: APScheduler使用PostgreSQL作为JobStore时，需要**同步驱动**，而非异步驱动。

```
# 错误配置
DATABASE_URL: postgresql+asyncpg://...  # APScheduler无法使用

# 正确配置
SQLALCHEMY_JOBSTORE_URL: postgresql+psycopg2://...  # APScheduler专用
```

### 1.3 slowapi参数命名要求

使用slowapi速率限制时，Request参数必须命名为 `request`：

```python
# 错误写法
async def login(request: LoginRequest, http_request: Request):
    # slowapi无法识别Request参数，导致INTERNAL_ERROR
    pass

# 正确写法
async def login(request_body: LoginRequest, request: Request):
    # slowapi正确识别Request参数
    pass
```

---

## 2. 环境变量配置

### 2.1 SESSION_SECRET配置

**安全要求**: SESSION_SECRET必须至少32字符，生产环境禁止使用默认值。

**自动生成方法**:

```bash
# Python方式
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL方式
openssl rand -base64 32

# Shell方式
echo "fdas-$(date +%s)-$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' ' | head -c 16)"
```

### 2.2 环境变量验证

deploy.sh脚本会自动验证SESSION_SECRET：

- 长度检查：必须 >= 32字符
- 默认值检测：检测包含 `change-this` 或 `dev-secret` 的值并发出警告

### 2.3 生产环境配置示例

```bash
# .env 文件配置示例
DB_PASSWORD=your-secure-password-with-special-chars-!@#
SESSION_SECRET=xK9mP2vL8nQ4wR7jT3yH5cF1bN6gA0sE  # 32字符随机值
DEBUG=false
ALLOWED_ORIGINS=["https://your-domain.com"]
ENABLE_IP_VALIDATION=true
```

---

## 3. 部署步骤

### 3.1 快速部署

```bash
cd deployment-packages/multi-container
./deploy.sh --action deploy
```

### 3.2 部署脚本执行步骤

| Step | 操作 | 检查内容 |
|------|------|---------|
| 1 | 检查Docker环境 | docker/docker-compose版本 |
| 2 | 检查环境变量 | SESSION_SECRET长度和默认值检测 |
| 3 | 拉取基础镜像 | postgres:16-alpine |
| 4 | 构建应用镜像 | 包含pip check依赖验证 |
| 5 | 启动服务 | docker-compose up -d |
| 6 | 等待数据库就绪 | 动态等待pg_isready（最多60秒） |
| 7 | 健康检查 | API健康检查 + 前端首页检查 |
| 8 | 显示服务状态 | docker-compose ps |

### 3.3 其他操作命令

```bash
# 停止服务
./deploy.sh --action stop

# 重启服务
./deploy.sh --action restart

# 查看日志
./deploy.sh --action logs

# 查看状态
./deploy.sh --action status

# 备份数据
./deploy.sh --action backup

# 清理（删除容器和卷）
./deploy.sh --action clean
```

---

## 4. 常见问题与解决方案

### 4.1 ModuleNotFoundError: bcrypt

**症状**: 登录API返回500错误，日志显示 `No module named 'bcrypt'`

**原因**: bcrypt依赖未安装或安装失败

**解决方案**:
1. 检查requirements.txt包含 `bcrypt>=4.0.0`
2. Dockerfile.app中deps-builder阶段执行 `pip check` 验证
3. 重新构建镜像: `docker-compose build --no-cache fdas-app`

### 4.2 ModuleNotFoundError: psycopg2

**症状**: APScheduler启动失败，日志显示 `No module named 'psycopg2'`

**原因**: APScheduler需要同步驱动psycopg2，asyncpg不满足需求

**解决方案**:
1. 检查requirements.txt包含 `psycopg2-binary>=2.9.0`
2. Dockerfile.app中deps-builder阶段执行 `pip check` 验证
3. 重新构建镜像

### 4.3 APScheduler类型错误

**症状**: 日志显示 `operator does not exist: timestamp with time zone <= numeric`

**原因**: init-db.sql中apscheduler_jobs.next_run_time使用了错误的TIMESTAMP类型

**解决方案**:
init-db.sql已修复为正确类型：
```sql
-- 正确类型定义
CREATE TABLE IF NOT EXISTS apscheduler_jobs (
    next_run_time NUMERIC(24, 6),  -- Unix timestamp
    ...
);
```

### 4.4 slowapi INTERNAL_ERROR

**症状**: 登录API返回 `{"success":false, "error":"INTERNAL_ERROR"}`

**原因**: Request参数命名不符合slowapi要求

**解决方案**:
修改auth.py中的参数命名：
```python
# request参数必须是Request类型
@rate_limit("5/minute")
async def login(request_body: LoginRequest, request: Request):
    # slowapi正确识别
```

### 4.5 前端404错误

**症状**: 访问首页返回404

**原因**: main.py未配置StaticFiles挂载

**解决方案**:
main.py已配置：
```python
# 静态文件服务配置
STATIC_DIR = Path("/app/static")
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"))
    # SPA路由支持
```

### 4.6 SESSION_SECRET验证失败

**症状**: deploy.sh报错 `SESSION_SECRET 长度不足32字符`

**原因**: SESSION_SECRET配置不符合要求

**解决方案**:
1. 使用自动生成: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
2. 或手动创建至少32字符的安全随机值
3. 更新.env文件中的SESSION_SECRET

---

## 5. 数据迁移注意事项

### 5.1 Schema兼容性检查

迁移数据前，必须检查以下schema兼容性：

| 表/字段 | 原schema | 目标schema | 兼容性 |
|---------|---------|-----------|--------|
| `apscheduler_jobs.next_run_time` | TIMESTAMP | NUMERIC(24,6) | 不兼容，需转换 |
| `collection_tasks` 字段 | 可能不同 | 参考init-db.sql | 需对比 |

### 5.2 APScheduler数据转换

如果备份中包含旧的TIMESTAMP类型数据，需要转换：

```sql
-- TIMESTAMP转Unix timestamp
UPDATE apscheduler_jobs
SET next_run_time = EXTRACT(EPOCH FROM next_run_time_old);
```

### 5.3 迁移失败回滚

如果数据恢复失败，执行回滚：

```bash
# 重新初始化数据库
docker-compose down -v
docker-compose up -d

# 或使用备份恢复
./scripts/restore.sh /path/to/backup.dump
```

---

## 6. 安全配置检查清单

部署完成后，执行以下安全检查：

### 6.1 必查项目

| 检查项 | 要求 | 检查方法 |
|--------|------|---------|
| SESSION_SECRET | >=32字符，非默认值 | `grep SESSION_SECRET .env` |
| DB_PASSWORD | 强密码（16+字符，含特殊字符） | `grep DB_PASSWORD .env` |
| DEBUG模式 | 生产环境必须false | `grep DEBUG .env` |
| ALLOWED_ORIGINS | 非localhost | `grep ALLOWED_ORIGINS .env` |
| 默认密码 | 登录后立即修改admin密码 | 前端用户管理界面 |

### 6.2 建议配置

| 配置项 | 生产环境建议 |
|--------|-------------|
| `ENABLE_IP_VALIDATION` | true（防止Session被盗用） |
| SSL/TLS | 配置HTTPS证书 |
| 防火墙 | 仅开放必要端口（8000, 5432） |
| 日志级别 | INFO或WARNING |

---

## 附录

### A. 命令速查表

```bash
# 部署
./deploy.sh --action deploy

# 健康检查
curl http://localhost:8000/api/health

# 登录测试
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 查看容器状态
docker ps --filter "name=fdas"

# 查看应用日志
docker logs fdas-app --tail 50

# 进入容器调试
docker exec -it fdas-app bash
docker exec -it fdas-db psql -U fdas -d fdas
```

### B. 文件路径参考

| 文件 | 路径 |
|------|------|
| 部署脚本 | `deployment-packages/multi-container/deploy.sh` |
| Docker Compose | `deployment-packages/multi-container/docker-compose.yml` |
| Dockerfile | `deployment-packages/multi-container/Dockerfile.app` |
| 环境变量模板 | `deployment-packages/multi-container/config/.env.template` |
| 数据库初始化 | `docker/init-db.sql` |
| Python依赖 | `backend/requirements.txt` |