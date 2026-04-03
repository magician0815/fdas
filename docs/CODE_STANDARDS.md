# FDAS 代码规范文档

> 金融数据抓取与分析系统 - 代码编写规范说明书

**版本**: 1.0
**创建日期**: 2026-04-03
**作者**: FDAS Team

---

## 一、代码注释规范

### 1.1 统一注释格式

**采用Google风格注释**，格式统一，便于阅读与AI理解。

### 1.2 Python注释规范

#### 1.2.1 模块级注释

文件顶部，说明模块功能、作者、创建日期。

```python
"""
数据采集服务模块.

提供AKShare数据采集、APScheduler任务调度、重试机制等功能.

Author: FDAS Team
Created: 2026-04-03
"""
```

#### 1.2.2 类级注释

类定义下方，说明类的职责、主要方法、属性。

```python
class FXDataService:
    """
    汇率数据服务.

    负责汇率数据的查询、缓存、技术指标计算等业务逻辑.

    Attributes:
        db: 数据库会话
        cache: 内存缓存实例

    主要方法:
        get_fx_data: 查询汇率数据
        calculate_indicators: 计算技术指标
    """
```

#### 1.2.3 函数级注释

函数定义下方，说明函数功能、参数、返回值、异常。

```python
async def get_fx_data(
    symbol: str,
    start_date: date,
    end_date: date,
    limit: int = 1000,
) -> list[dict]:
    """
    查询汇率数据.

    根据时间范围查询指定汇率的历史数据，支持缓存优化.

    Args:
        symbol: 汇率符号，如 'USDCNH'
        start_date: 开始日期
        end_date: 结束日期
        limit: 返回数据条数限制，默认1000

    Returns:
        list[dict]: 汇率数据列表，每条包含:
            - date: 日期
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价

    Raises:
        ValueError: symbol参数为空或limit超出范围
        DatabaseError: 数据库查询失败

    Example:
        >>> data = await service.get_fx_data('USDCNH', date(2024,1,1), date(2024,1,31))
        >>> print(len(data))  # 31条数据
    """
```

#### 1.2.4 关键逻辑注释

复杂业务逻辑、算法、容易混淆的代码必须有行内注释。

```python
# 使用TA-Lib计算MACD指标
# 参数：快线周期12，慢线周期26，信号线周期9
macd, signal, hist = talib.MACD(
    close_prices,
    fastperiod=12,
    slowperiod=26,
    signalperiod=9
)

# 缓存命中检查：30天数据缓存24小时
cache_key = f"{symbol}_30d"
if cache_key in self.cache:
    return self.cache[cache_key]  # 缓存命中，直接返回

# APScheduler任务添加：解析cron表达式为调度参数
# cron格式：分钟 小时 日 月 星期
cron_parts = cron_expression.split()
scheduler.add_job(
    func=collect_task,
    trigger='cron',
    minute=cron_parts[0],
    hour=cron_parts[1],
    day=cron_parts[2],
    month=cron_parts[3],
    day_of_week=cron_parts[4],
)
```

### 1.3 Vue/JavaScript注释规范

#### 1.3.1 Vue组件注释

`<script setup>`顶部添加组件功能说明。

```vue
<script setup>
/**
 * 汇率数据可视化组件.
 *
 * 使用ECharts渲染K线图、均线图、MACD图，支持时间范围切换.
 *
 * 功能：
 * - K线图展示（开盘/最高/最低/收盘）
 * - MA均线叠加（MA5/MA10/MA20）
 * - MACD指标图（MACD线/信号线/柱状图）
 * - 时间范围选择（默认30天，可切换）
 */
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
// ...
</script>
```

#### 1.3.2 JavaScript函数注释

复杂方法添加JSDoc风格注释，说明功能、参数、返回值。

```javascript
/**
 * 解析cron表达式为可视化参数.
 *
 * @param {string} cronExpr - cron表达式，如 "0 18 * * *"
 * @returns {Object} 解析结果对象
 * @returns {string} returns.periodType - 周期类型：daily/weekly/monthly/custom
 * @returns {string} returns.executeTime - 执行时间，如 "18:00"
 * @returns {string} returns.description - cron描述，如 "每天18:00执行"
 *
 * @example
 * const result = parseCron('0 18 * * *')
 * console.log(result.periodType) // 'daily'
 */
function parseCron(cronExpr) {
  // 实现逻辑...
}
```

#### 1.3.3 关键逻辑注释

```javascript
// ECharts图表配置：K线图占50%高度，MACD图占20%高度
const grid = [
  { left: '10%', right: '8%', height: '50%' },  // K线图区域
  { left: '10%', right: '8%', top: '65%', height: '20%' },  // MACD图区域
]

// 权限检查：路由守卫拦截未授权访问
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 需要登录的页面，检查Session状态
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')  // 重定向到登录页
    return
  }

  // 需要admin权限的页面，检查用户角色
  if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    next('/')  // 重定向到首页
    return
  }

  next()
})
```

---

## 二、日志规范

### 2.1 统一日志格式

```
[时间] [级别] [模块名] [请求ID] - 日志内容
```

**示例**：
```
2026-04-03 14:30:00,123 [INFO] [services.fx_service] [req-abc123] - 开始抓取USDCNH汇率数据
2026-04-03 14:30:05,456 [INFO] [services.fx_service] [req-abc123] - 成功抓取31条数据，已入库
2026-04-03 14:30:10,789 [WARNING] [services.scheduler_service] [req-def456] - 任务usdcnh_daily重试第2次
2026-04-03 14:30:15,012 [ERROR] [collectors.akshare_collector] [req-abc123] - AKShare接口调用失败：连接超时
```

### 2.2 日志级别划分

| 级别 | 使用场景 | 示例 |
|------|---------|------|
| **DEBUG** | 开发调试信息，生产环境关闭 | - SQL查询语句<br>- 函数入参/出参<br>- 变量值跟踪 |
| **INFO** | 关键业务流程信息 | - 用户登录成功<br>- 采集任务执行成功<br>- 数据保存成功<br>- 服务启动/停止 |
| **WARNING** | 警告信息，不影响系统运行 | - 采集任务重试<br>- 数据量超过阈值<br>- 配置项缺失使用默认值<br>- 缓存过期清理 |
| **ERROR** | 错误信息，影响单个功能 | - 采集任务失败<br>- 飞书告警发送失败<br>- 数据库查询失败<br>- API调用超时 |
| **CRITICAL** | 严重错误，系统无法运行 | - 数据库连接失败<br>- 后端服务启动失败<br>- 配置文件加载失败 |

### 2.3 日志输出方式

#### 2.3.1 控制台输出（开发环境）

```python
# 开发环境使用，便于调试
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
```

#### 2.3.2 文件输出（生产环境）

```python
# 生产环境使用，文件按大小轮转
file_handler = RotatingFileHandler(
    filename='logs/app.log',
    maxBytes=100 * 1024 * 1024,  # 100MB
    backupCount=30,  # 保留30个文件
    encoding='utf-8',
)
file_handler.setLevel(logging.INFO)
```

**文件命名规则**：
- 主日志文件：`app.log`
- 轮转文件：`app.log.1`, `app.log.2`, ... `app.log.30`

### 2.4 关键操作必须记录日志

| 操作类型 | 日志级别 | 日志内容 |
|---------|---------|---------|
| **用户登录** | INFO | 用户{username}登录成功 |
| **用户登出** | INFO | 用户{username}登出 |
| **采集任务触发** | INFO | 任务{task_id}开始执行 |
| **采集任务完成** | INFO | 任务{task_id}完成，采集{count}条数据 |
| **采集任务失败** | ERROR | 任务{task_id}失败：{error_message} |
| **数据修改** | INFO | 用户{user_id}修改{table}表{id}记录 |
| **数据删除** | WARNING | 用户{user_id}删除{table}表{id}记录 |
| **告警推送** | WARNING | 告警推送失败：{error_message} |
| **系统启动** | INFO | FDAS服务启动成功，监听端口{port} |
| **系统关闭** | INFO | FDAS服务关闭 |

### 2.5 请求ID追踪

**中间件注入请求ID**：

```python
# backend/app/core/middleware.py
import uuid
from fastapi import Request

async def request_id_middleware(request: Request, call_next):
    """
    请求ID中间件.

    为每个请求生成唯一ID，便于日志追踪.
    """
    request_id = str(uuid.uuid4())[:8]  # 8位短ID
    request.state.request_id = request_id

    # 在日志上下文中注入请求ID
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### 2.6 日志使用示例

```python
from app.config.logging import get_logger

logger = get_logger(__name__)

# INFO级别：关键业务流程
logger.info(f"开始抓取{symbol}汇率数据")

# WARNING级别：警告信息
logger.warning(f"缓存{cache_key}已过期，重新查询数据库")

# ERROR级别：错误信息
logger.error(f"AKShare接口调用失败：{str(e)}")

# CRITICAL级别：严重错误
logger.critical(f"数据库连接失败，服务无法启动")

# DEBUG级别：调试信息（仅开发环境）
logger.debug(f"SQL查询：{query}，参数：{params}")
```

---

## 三、配置规范

### 3.1 配置分层结构

```
┌─────────────────────────────────────────────────┐
│              配置分层架构                         │
├─────────────────────────────────────────────────┤
│  第一层：基础配置（与环境无关）                    │
│  - LOG_FORMAT: 日志格式                          │
│  - LOG_LEVEL: 日志级别                           │
│  - DEFAULT_MA_PERIOD: 默认MA周期                 │
│  - DEFAULT_MACD_PARAMS: MACD参数                │
├─────────────────────────────────────────────────┤
│  第二层：环境配置（与环境相关）                    │
│  - DATABASE_URL: 数据库连接                      │
│  - SESSION_SECRET: Session密钥                  │
│  - DEBUG: 调试模式                               │
│  - ALLOWED_ORIGINS: CORS白名单                   │
│  - APP_PORT: 应用端口                            │
├─────────────────────────────────────────────────┤
│  第三层：业务配置（业务相关）                      │
│  - DEFAULT_COLLECTION_TIME: 默认采集时间         │
│  - FX_DATA_LIMIT: 数据查询限制                   │
│  - CACHE_TTL_SECONDS: 缓存过期时间               │
└─────────────────────────────────────────────────┘
```

### 3.2 Pydantic Settings实现

```python
# backend/app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class BaseConfig(BaseSettings):
    """
    基础配置（与环境无关）.

    这些配置在所有环境中保持一致.
    """
    # 日志配置
    LOG_FORMAT: str = "%(asctime)s %(levelname)s %(name)s %(message)s"
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_SIZE: int = 100 * 1024 * 1024  # 100MB
    LOG_FILE_BACKUP_COUNT: int = 30

    # 技术指标默认参数
    DEFAULT_MA_PERIOD: int = 20
    DEFAULT_MACD_FAST: int = 12
    DEFAULT_MACD_SLOW: int = 26
    DEFAULT_MACD_SIGNAL: int = 9


class EnvConfig(BaseSettings):
    """
    环境配置（与环境相关）.

    通过.env文件或环境变量加载.
    """
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://fdas:fdas@localhost:5432/fdas"

    # 安全配置
    SESSION_SECRET: str = "change-this-in-production"

    # 运行配置
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    APP_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


class BusinessConfig(BaseSettings):
    """
    业务配置（业务相关）.

    可根据业务需求调整.
    """
    # 采集配置
    DEFAULT_COLLECTION_TIME: str = "18:00"

    # 数据查询配置
    FX_DATA_LIMIT: int = 1000

    # 缓存配置
    CACHE_TTL_SECONDS: int = 86400  # 24小时


class Settings(BaseConfig, EnvConfig, BusinessConfig):
    """
    综合配置类.

    继承三层配置，提供统一的配置访问接口.

    使用方式：
        from app.config.settings import settings
        db_url = settings.DATABASE_URL
    """
    pass


# 全局配置实例
settings = Settings()
```

### 3.3 .env文件示例

```bash
# FDAS环境变量配置
# 复制此文件为 .env 并根据环境修改

# === 环境配置 ===
DATABASE_URL=postgresql+asyncpg://fdas:fdas@fdas-db:5432/fdas
SESSION_SECRET=your-secret-key-change-in-production
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]
APP_PORT=8000

# === 业务配置（可选覆盖） ===
DEFAULT_COLLECTION_TIME=18:00
FX_DATA_LIMIT=1000
CACHE_TTL_SECONDS=86400
```

### 3.4 配置加载顺序

```
优先级（从高到低）：
1. 环境变量（最高优先级）
2. .env文件
3. 配置类默认值（最低优先级）
```

**示例**：

```python
# 默认值
LOG_LEVEL: str = "INFO"

# .env文件覆盖
LOG_LEVEL=DEBUG

# 环境变量覆盖（最高优先级）
export LOG_LEVEL=WARNING

# 最终生效值：WARNING
```

---

## 四、性能优化规范

### 4.1 数据库层面

| 优化项 | 规范要求 | 实现方式 |
|--------|---------|---------|
| **索引优化** | 为所有查询字段、关联字段、时间字段建立索引 | PostgreSQL B-tree索引 |
| **连接池配置** | 限制数据库连接数，避免连接泄漏 | asyncpg pool (10+20) |
| **查询优化** | 避免全表扫描，限制单次查询数据量 | LIMIT 1000，WHERE条件 |
| **批量写入** | 使用批量insert提升写入性能 | SQLAlchemy bulk_insert |
| **事务控制** | 合理使用事务，避免长事务 | 短事务，及时提交 |

**索引设计规范**：

```sql
-- 单字段索引（查询频繁的字段）
CREATE INDEX idx_fx_data_symbol ON fx_data(symbol);
CREATE INDEX idx_fx_data_date ON fx_data(date);

-- 复合索引（多字段联合查询）
CREATE INDEX idx_fx_data_symbol_date ON fx_data(symbol, date);

-- 外键索引（关联查询）
CREATE INDEX idx_collection_tasks_datasource_id ON collection_tasks(datasource_id);
```

**查询优化示例**：

```python
# GOOD：使用索引查询，限制数据量
async def get_fx_data_optimized(symbol: str, days: int = 30) -> list:
    query = select(FXData).where(
        FXData.symbol == symbol,  # 索引字段
        FXData.date >= date.today() - timedelta(days=days)  # 索引字段
    ).limit(1000)  # 限制数据量
    return await db.execute(query)

# BAD：全表扫描，无限制
async def get_fx_data_bad(symbol: str) -> list:
    query = select(FXData)  # 全表扫描
    return await db.execute(query)
```

### 4.2 后端层面

| 优化项 | 规范要求 | 实现方式 |
|--------|---------|---------|
| **全异步处理** | 所有API使用async/await | FastAPI async + SQLAlchemy async |
| **内存缓存** | 缓存热点数据，减少数据库查询 | cachetools TTL缓存 |
| **全局异常捕获** | 统一异常处理，避免服务崩溃 | FastAPI exception_handler |
| **请求超时控制** | 所有外部API调用设置超时 | httpx timeout=10s |
| **批量操作** | 批量处理减少请求次数 | 批量insert/update |

**异步处理规范**：

```python
# GOOD：全异步处理
async def get_fx_data(symbol: str) -> list:
    async with db.begin():  # 异步事务
        result = await db.execute(query)  # 异步查询
        return result.scalars().all()

# BAD：同步阻塞
def get_fx_data_bad(symbol: str) -> list:
    result = db.execute(query)  # 同步阻塞
    return result.scalars().all()
```

**缓存使用规范**：

```python
from cachetools import TTLCache

# 缓存实例：100个key，24小时过期
fx_cache = TTLCache(maxsize=100, ttl=86400)

async def get_fx_data_with_cache(symbol: str) -> list:
    """
    缓存优化的数据查询.

    先检查缓存，未命中则查询数据库并缓存结果.
    """
    cache_key = f"{symbol}_30d"

    # 缓存命中检查
    if cache_key in fx_cache:
        return fx_cache[cache_key]

    # 查询数据库
    data = await query_fx_data(symbol)

    # 写入缓存
    fx_cache[cache_key] = data
    return data
```

### 4.3 前端层面

| 优化项 | 规范要求 | 实现方式 |
|--------|---------|---------|
| **路由懒加载** | 页面组件按需加载 | Vue defineAsyncComponent |
| **数据分页** | 列表数据分页加载，避免大量数据 | 默认1000条，分页展示 |
| **图表优化** | 默认显示30天，用户可切换时间范围 | ECharts dataZoom |
| **防抖节流** | 搜索、筛选等操作防抖 | lodash.debounce 300ms |
| **组件复用** | 公共组件封装复用 | DataTable、FXChart等 |

**路由懒加载规范**：

```javascript
// GOOD：路由懒加载
const routes = [
  {
    path: '/fx-data',
    component: () => import('@/views/FXData.vue'),  // 懒加载
  },
]

// BAD：直接导入（增加首屏加载）
import FXData from '@/views/FXData.vue'
const routes = [
  { path: '/fx-data', component: FXData },
]
```

**防抖节流规范**：

```javascript
import { debounce } from 'lodash-es'

// GOOD：搜索防抖300ms
const handleSearch = debounce((keyword) => {
  fetchFXData({ keyword })
}, 300)

// BAD：每次输入都请求
const handleSearchBad = (keyword) => {
  fetchFXData({ keyword })  // 频繁请求
}
```

---

## 五、代码质量规范

### 5.1 文件大小限制

| 类型 | 最大行数 | 建议 |
|------|---------|------|
| **Python文件** | 800行 | 超过后拆分模块 |
| **Vue文件** | 500行 | 超过后拆分组件 |
| **函数/方法** | 50行 | 超过后拆分函数 |

### 5.2 嵌套深度限制

| 类型 | 最大深度 | 建议 |
|------|---------|------|
| **Python代码** | 4层 | 使用early return减少嵌套 |
| **Vue模板** | 3层 | 拆分子组件 |

**嵌套优化示例**：

```python
# BAD：深层嵌套（5层）
async def process_data_bad(data):
    if data:
        if data.valid:
            if data.type == 'fx':
                if data.symbol:
                    if data.date:
                        return process(data)

# GOOD：early return减少嵌套（1层）
async def process_data_good(data):
    if not data:
        return None
    if not data.valid:
        return None
    if data.type != 'fx':
        return None
    if not data.symbol:
        return None
    if not data.date:
        return None
    return process(data)
```

### 5.3 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| **Python变量** | snake_case | `fx_data`, `collection_task` |
| **Python函数** | snake_case | `get_fx_data()`, `calculate_macd()` |
| **Python类** | PascalCase | `FXDataService`, `AKShareCollector` |
| **Python常量** | UPPER_SNAKE_CASE | `MAX_DATA_LIMIT`, `CACHE_TTL` |
| **Vue组件** | PascalCase | `FXChart.vue`, `CronBuilder.vue` |
| **Vue变量** | camelCase | `fxData`, `chartOption` |
| **Vue函数** | camelCase | `fetchData()`, `renderChart()` |
| **数据库表** | snake_case | `fx_data`, `collection_tasks` |
| **API路由** | snake_case | `/api/v1/fx-data` |

### 5.4 类型注解规范

**Python类型注解**：

```python
from typing import List, Dict, Optional
from datetime import date

# GOOD：完整类型注解
async def get_fx_data(
    symbol: str,
    start_date: date,
    end_date: date,
    limit: int = 1000,
) -> List[Dict[str, any]]:
    """查询汇率数据."""
    pass

# BAD：无类型注解
async def get_fx_data_bad(symbol, start_date, end_date, limit=1000):
    pass
```

**Vue TypeScript注解**（可选）：

```typescript
// GOOD：TypeScript类型定义
interface FXDataItem {
  date: string
  open: number
  high: number
  low: number
  close: number
}

const fxData: Ref<FXDataItem[]> = ref([])
```

---

## 六、Git提交规范

### 6.1 Commit消息格式

```
<类型>: <描述>

<可选正文>
```

**类型列表**：

| 类型 | 说明 | 示例 |
|------|------|------|
| **feat** | 新功能 | feat: 添加用户登录API |
| **fix** | Bug修复 | fix: 修复Session过期检查 |
| **refactor** | 重构 | refactor: 重构数据采集模块 |
| **docs** | 文档 | docs: 更新API文档 |
| **test** | 测试 | test: 添加FXDataService测试 |
| **chore** | 构建/配置 | chore: 更新依赖版本 |
| **perf** | 性能优化 | perf: 优化数据库查询 |

### 6.2 分支规范

| 分支 | 说明 | 示例 |
|------|------|------|
| **main** | 主分支，稳定版本 | - |
| **develop** | 开发分支 | - |
| **feature/*** | 功能分支 | feature/user-auth |
| **fix/*** | 修复分支 | fix/session-expire |
| **release/*** | 发布分支 | release/v1.0 |

---

## 七、代码审查清单

### 7.1 提交前自查清单

**功能检查**：

- [ ] 功能是否按需求实现
- [ ] 边界条件是否处理
- [ ] 错误处理是否完整

**代码质量检查**：

- [ ] 代码是否可读、命名良好
- [ ] 函数是否小于50行
- [ ] 文件是否小于800行
- [ ] 嵌套是否小于4层
- [ ] 是否有类型注解

**注释检查**：

- [ ] 模块注释是否完整
- [ ] 函数注释是否完整（Args/Returns/Raises）
- [ ] 关键逻辑是否有行内注释

**日志检查**：

- [ ] 关键操作是否记录日志
- [ ] 日志级别是否正确
- [ ] 日志内容是否清晰

**安全检查**：

- [ ] 是否有权限检查
- [ ] 密码是否使用bcrypt
- [ ] 是否有SQL注入风险
- [ ] 是否有硬编码密钥

**性能检查**：

- [ ] 是否使用异步处理
- [ ] 是否有缓存优化
- [ ] 数据库查询是否使用索引
- [ ] 是否有数据量限制

---

## 八、附录

### 8.1 参考文档

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Vue 3 Style Guide](https://vuejs.org/style-guide/)
- [JSDoc Documentation](https://jsdoc.app/)

### 8.2 工具推荐

| 工具 | 用途 | 配置 |
|------|------|------|
| **black** | Python代码格式化 | `black app/` |
| **isort** | Python导入排序 | `isort app/` |
| **flake8** | Python代码检查 | `flake8 app/` |
| **mypy** | Python类型检查 | `mypy app/` |
| **ESLint** | JavaScript代码检查 | `eslint src/` |
| **Prettier** | JavaScript代码格式化 | `prettier src/` |

### 8.3 相关文档

- [PRD.md](PRD.md) - 需求设计文档
- [ARCHITECTURE.md](ARCHITECTURE.md) - 技术架构文档
- [PERMISSION_DESIGN.md](PERMISSION_DESIGN.md) - 权限设计文档
- [PHASE1_DESIGN.md](PHASE1_DESIGN.md) - 第一阶段设计文档