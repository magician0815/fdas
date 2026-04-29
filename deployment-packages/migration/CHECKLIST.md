# FDAS迁移方案 - 验证检查清单

## 前置检查（迁移前）

### 单容器状态检查
- [ ] 单容器服务正常运行
- [ ] 数据库连接正常
- [ ] 前端页面可访问
- [ ] API健康检查通过
- [ ] 环境变量已备份

### 备份验证
- [ ] 数据库备份文件非空
- [ ] 备份文件大小正常（>1KB）
- [ ] 数据卷备份完整
- [ ] 配置文件已复制

---

## 数据迁移验证

### 备份完整性
```bash
# 检查备份文件
ls -lh /tmp/fdas_migration/

# 验证数据库备份
pg_restore -l /tmp/fdas_migration/fdas_db_source_*.dump | head -20
```

### 备份内容检查
- [ ] 用户数据存在
- [ ] 市场数据存在
- [ ] 外汇货币对数据存在
- [ ] 采集任务配置存在

---

## 多容器部署验证

### 容器状态
```bash
# 检查容器运行状态
docker ps

# 检查容器健康
docker inspect fdas-db --format='{{.State.Health.Status}}'
docker inspect fdas-app --format='{{.State.Health.Status}}'
```

### 容器检查项
- [ ] fdas-db容器运行正常
- [ ] fdas-db健康检查通过
- [ ] fdas-app容器运行正常
- [ ] fdas-app健康检查通过
- [ ] 网络通信正常

---

## 数据恢复验证

### 数据库完整性验证
```bash
# 检查表数量
docker exec fdas-db psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

# 检查用户数据
docker exec fdas-db psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM users;"

# 检查外汇货币对
docker exec fdas-db psql -U fdas -d fdas -t -c "SELECT COUNT(*) FROM forex_symbols;"
```

### 数据检查项
- [ ] 表数量一致（>10）
- [ ] 用户数据完整（>0）
- [ ] 市场数据完整（6种）
- [ ] 外汇货币对完整（20个）
- [ ] 采集任务配置完整

---

## 服务功能验证

### 基础功能
```bash
# 健康检查
curl http://localhost:8000/api/health

# API文档
curl http://localhost:8000/api/docs
```

### 功能检查项
- [ ] 健康检查返回200
- [ ] API文档可访问
- [ ] 前端页面加载正常
- [ ] 登录功能正常
- [ ] 数据查询API正常
- [ ] 图表渲染正常

### 性能验证
- [ ] API响应时间 < 500ms
- [ ] 数据库查询时间 < 100ms
- [ ] 前端加载时间 < 3s

---

## 安全验证

### 配置检查
```bash
# 检查环境变量
docker exec fdas-app env | grep SESSION_SECRET

# 检查CORS配置
docker exec fdas-app env | grep ALLOWED_ORIGINS
```

### 安全检查项
- [ ] SESSION_SECRET已配置（非默认值）
- [ ] SESSION_SECRET长度>=32字符
- [ ] CORS配置正确
- [ ] 无硬编码密码
- [ ] 无敏感信息泄露

---

## 迁移后清理（24小时后）

### 清理操作
- [ ] 观察期结束，服务稳定
- [ ] 原单容器镜像清理
- [ ] 临时备份文件归档
- [ ] 监控日志检查
- [ ] 用户通知（如有）

### 归档命令
```bash
# 归档备份文件
mv /tmp/fdas_migration /var/backups/fdas/migration_$(date +%Y%m%d)

# 清理原容器（可选）
docker rm fdas-single
docker rmi fdas-single-image
```

---

## 回滚预案

如果迁移失败，执行回滚：
```bash
cd deployment-packages/migration
./rollback.sh
```

回滚条件：
- 数据恢复失败
- 服务无法启动
- 功能异常无法修复
- 性能严重下降