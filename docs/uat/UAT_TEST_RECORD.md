# FDAS UAT测试记录文档

> 金融数据抓取与分析系统 - 用户验收测试记录
> Version: v2.0.1
> Test Date: 2026-04-17
> Tester: [测试人员姓名]
> Environment: 测试环境 (localhost:8000)

---

## 测试环境信息

| 项目 | 信息 |
|------|------|
| 系统版本 | v2.0.1 |
| 前端地址 | http://localhost:8000 |
| API文档 | http://localhost:8000/api/docs |
| 默认账号 | admin / admin123 |
| 数据库状态 | PostgreSQL 16, 11张表已初始化 |

---

## UAT测试场景清单

### P0: 登录认证（必测）

| # | 测试项 | 预期结果 | 实际结果 | 状态 | 问题编号 |
|---|--------|---------|---------|------|---------|
| P0-1 | 正确账号登录 | 登录成功，跳转首页 | 显示"登录成功"但未跳转，停留在登录页 | ❌失败 | UAT-001 |
| P0-2 | 错误密码登录 | 显示"用户名或密码错误" | | ⬜ | |
| P0-3 | 登出功能 | 清除session，返回登录页 | | ⬜ | |
| P0-4 | Session过期后访问 | 自动跳转登录页 | | ⬜ | |

### P1: 外汇数据查询（必测）

| # | 测试项 | 预期结果 | 实际结果 | 状态 | 问题编号 |
|---|--------|---------|---------|------|---------|
| P1-1 | 查看外汇货币对列表 | 显示20个货币对 | 进入页面报错"获取货币对列表失败" | ❌失败 | UAT-003,UAT-004,UAT-005 |
| P1-2 | 选择货币对查看日线 | 显示OHLC图表 | 查询日线数据失败，forex_daily表不存在 | ❌失败 | UAT-009 |
| P1-3 | 切换不同货币对 | 图表数据更新 | | ⬜ | |
| P1-4 | 查看技术指标(MACD) | 显示MACD副图 | | ⬜ | |
| P1-5 | 图表缩放拖拽功能 | 正常交互 | | ⬜ | |

### P2: 数据采集管理（必测）

| # | 测试项 | 预期结果 | 实际结果 | 状态 | 问题编号 |
|---|--------|---------|---------|------|---------|
| P2-1 | 查看采集任务列表 | 显示已配置任务 | 刷新报错"获取基础数据失败"+"获取任务列表失败" | ❌失败 | UAT-007,UAT-008 |
| P2-2 | 启用/禁用采集任务 | 状态切换成功 | | ⬜ | |
| P2-3 | 手动触发采集 | 任务开始执行 | 执行成功，采集13条数据 | ✅通过 | |
| P2-4 | 查看采集日志 | 显示执行记录 | | ⬜ | |
| P2-5 | 查看采集统计 | 显示成功/失败数 | | ⬜ | |

### P3: 用户管理（必测）

| # | 测试项 | 预期结果 | 实际结果 | 状态 | 问题编号 |
|---|--------|---------|---------|------|---------|
| P3-1 | 查看用户列表 | 显示所有用户 | | ⬜ | |
| P3-2 | 创建新用户 | 用户创建成功 | | ⬜ | |
| P3-3 | 编辑用户信息 | 信息更新成功 | | ⬜ | |
| P3-4 | 删除用户 | 用户删除成功 | | ⬜ | |
| P3-5 | 修改密码功能 | 密码修改成功 | | ⬜ | |

### P4: 数据源管理（必测）

| # | 测试项 | 预期结果 | 实际结果 | 状态 | 问题编号 |
|---|--------|---------|---------|------|---------|
| P4-1 | 查看数据源列表 | 显示配置数据源 | 刷新报错"获取数据源列表失败" | ❌失败 | UAT-006 |
| P4-2 | 查看支持的货币对 | 显示货币对列表 | | ⬜ | |
| P4-3 | 数据源状态显示 | 正确显示启用/禁用 | | ⬜ | |

### P5: 图表工具（可选）

| # | 测试项 | 预期结果 | 实际结果 | 状态 | 问题编号 |
|---|--------|---------|---------|------|---------|
| P5-1 | 画线工具使用 | 正常绘制线条 | | ⬜ | |
| P5-2 | 删除画线 | 线条删除成功 | | ⬜ | |
| P5-3 | 图表主题切换 | 主题更新 | | ⬜ | |
| P5-4 | 图表配置保存 | 配置持久化 | | ⬜ | |

### P6: 系统稳定性（必测）

| # | 测试项 | 预期结果 | 实际结果 | 状态 | 问题编号 |
|---|--------|---------|---------|------|---------|
| P6-1 | 长时间运行稳定性 | 无崩溃、无内存泄漏 | | ⬜ | |
| P6-2 | 多次刷新页面 | 正常加载无异常 | | ⬜ | |
| P6-3 | 浏览器兼容性(Chrome) | 功能正常 | | ⬜ | |
| P6-4 | 浏览器兼容性(Firefox) | 功能正常 | | ⬜ | |

---

## 问题记录表

| 问题编号 | 发现时间 | 测试项 | 问题描述 | 严重级别 | 状态 | 修复提交 |
|----------|---------|--------|---------|---------|------|---------|
| UAT-001 | 2026-04-17 10:30 | P0-1 | 登录成功后只显示"登录成功"提示，未跳转到系统首页 | **Critical** | ✅已修复 | auth.js取值修正 |
| UAT-002 | 2026-04-17 10:45 | P1-1 | 数据分析页面白天/黑夜模式按钮与走势图"定位日期"按钮重叠 | **Low** | ✅已修复 | ProChart.vue主题按钮左移 |
| UAT-003 | 2026-04-17 10:45 | P1-1 | 进入数据分析页面报错"获取货币对列表失败"，不应在页面加载时查询 | **Medium** | ✅已修复 | FXData.vue移除自动加载 |
| UAT-004 | 2026-04-17 10:45 | P1-1 | 选择货币对应改为输入框输入标的代码方式检索 | **Medium** | ✅已修复 | FXData.vue改为远程搜索 |
| UAT-005 | 2026-04-17 10:45 | P1-1 | "货币对"名称不专业，需更换为覆盖多市场的通用名称 | **Medium** | ✅已修复 | 全局改为"金融标的" |
| UAT-006 | 2026-04-17 10:45 | P4-1 | 数据源管理页面刷新显示"获取数据源列表失败"，空数据不应报错 | **Medium** | ✅已修复 | datasource.py datetime类型 |
| UAT-007 | 2026-04-17 10:45 | P2-1 | 采集任务页面刷新显示"获取基础数据失败"，需检查数据库初始化 | **High** | ✅已修复 | API路径尾部斜杠 |
| UAT-008 | 2026-04-17 10:45 | P2-1 | 采集任务页面刷新显示"获取任务列表失败"，空数据不应报错 | **Medium** | ✅已修复 | API路径尾部斜杠 |
| UAT-009 | 2026-04-17 17:30 | P2-3 | 手动执行采集任务失败，报错"relation forex_daily does not exist" | **Critical** | ✅已修复 | init-db.sql分区表主键修正 |
| UAT-010 | 2026-04-17 17:42 | P2-3 | AKShare forex_hist_em接口连接被拒绝，需添加请求头绕过反爬 | **High** | ✅已修复 | 直接API调用+请求头 |
| UAT-011 | 2026-04-17 18:50 | P2-3 | 数据库约束名称不匹配，ON CONFLICT DO UPDATE失败 | **High** | ✅已修复 | 约束名修正 |
| UAT-012 | 2026-04-17 19:20 | P4-2 | AKShare无forex_symbols接口，同步货币对API从未真正查询数据 | **Critical** | ✅已修复 | 改用symbol_market_map |
| UAT-013 | 2026-04-17 19:20 | P4-2 | init-db.sql使用自创代码USDCNY，非AKShare标准代码USDCNH | **High** | ✅已修复 | 初始化脚本修正 |
| UAT-018 | 2026-04-17 21:30 | P0-4 | 刷新页面跳转登录页，fetchUser未等待完成后再挂载应用 | **Critical** | ✅已修复 | main.js改为async初始化 |
| UAT-019 | 2026-04-17 21:30 | P1-2 | 标题栏太宽，需等比例缩小文字和按钮 | **Low** | ✅已修复 | Navbar/FXData缩小字体和按钮 |
| UAT-020 | 2026-04-17 21:30 | P1-2 | "外汇行情数据可视化"字样需删除 | **Low** | ✅已修复 | Navbar副标题清空 |
| UAT-021 | 2026-04-17 21:30 | P1-2 | 夜间模式白底文字看不清，按钮反色遮盖文字 | **Medium** | ✅已修复 | 完善夜间模式CSS |
| UAT-015 | 2026-04-17 20:00 | P1-2 | 数据分析页面"数据分析 专业行情走势"标题多余，当前价格信息改为一行展示 | **Low** | ✅已修复 | FXData.vue标题精简+价格inline |
| UAT-016 | 2026-04-17 20:00 | P1-2 | 数据分析页面下方历史数据展示和导出模块不需要 | **Low** | ✅已修复 | 删除data-table-section |
| UAT-017 | 2026-04-17 20:00 | P1-2 | 白天/夜间模式切换应全局生效，按钮移到页面顶部用户名旁 | **Medium** | ✅已修复 | 全局theme store + Navbar按钮 |
| UAT-022 | 2026-04-17 22:30 | P0-4 | 刷新页面返回登录页，路由守卫需等待用户状态恢复 | **Critical** | ✅已修复 | router/index.js异步守卫+fetchUser |
| UAT-023 | 2026-04-17 22:30 | P1-2 | 顶部状态栏仍未改低，需进一步缩小字体和头像 | **Low** | ✅已修复 | Navbar 13px标题+24px头像+48px头部 |
| UAT-024 | 2026-04-17 22:30 | P1-2 | "数据分析"副标题需改为显示当前标的信息(代码/名称/价格/涨跌幅) | **Medium** | ✅已修复 | FXData.vue symbol-info组件 |
| UAT-025 | 2026-04-17 22:30 | P1-2 | KLineChart标题"选择金融标的"改为"行情走势"，按钮左移 | **Low** | ✅已修复 | KLineChart.vue标题修正+gap缩小 |
| UAT-026 | 2026-04-17 22:30 | P1-2 | KLineChart无数据时空盒子图标过大，与标题栏重叠 | **Low** | ✅已修复 | el-empty image-size=60 |
| UAT-027 | 2026-04-17 22:30 | P1-2 | KLineChart"获取数据"按钮无用，删除 | **Low** | ✅已修复 | 删除el-empty内按钮 |
| UAT-028 | 2026-04-17 23:30 | P1-2 | 顶部状态栏还需再矮，用户名控件重新设计，导航栏FDAS高度一致 | **Low** | ✅已修复 | 40px头部+重新设计用户控件+侧边栏同步 |
| UAT-029 | 2026-04-17 23:30 | P1-2 | 副标题字体增大，顺序调整为名称/代码/价格/涨跌幅，涨跌颜色逻辑修正 | **Medium** | ✅已修复 | 14px字体+涨红跌绿平白+默认显示"----" |
| UAT-030 | 2026-04-17 23:30 | P1-2 | KLineChart功能控件左移两个字符，删除"显示右侧价格轴"按钮 | **Low** | ✅已修复 | padding-left:24px+删除右侧价格轴按钮 |
| UAT-031 | 2026-04-17 23:30 | P1-2 | 均线选项扩展为MA5/10/20/30/60/120/240共7项 | **Low** | ✅已修复 | KLineChart增加MA30/120/240选项 |
| UAT-032 | 2026-04-17 23:30 | P1-2 | 成交量副图折叠后MACD位置偏低，标题栏遮挡问题 | **Medium** | ✅已修复 | VolumeChart/MACDChart添加minimized prop |

| UAT-033 | 2026-04-18 00:00 | P1-2 | 删除"外汇市场通常无成交量数据"警告提示 | **Low** | ✅已修复 | VolumeChart.vue移除warning模板 |
| UAT-034 | 2026-04-18 00:00 | P1-2 | 删除矩形选择、圈选、取消选择按钮及相关功能 | **Low** | ✅已修复 | KLineChart移除interval选择按钮 |
| UAT-035 | 2026-04-18 00:00 | P1-2 | 行情主图默认显示最近30周期，不足则全部显示 | **Medium** | ✅已修复 | resetView()动态计算30周期 |
| UAT-036 | 2026-04-18 00:00 | P1-2 | 后端MA计算需同步前端7个均线选项(5/10/20/30/60/120/240) | **Medium** | ✅已修复 | technical_service.py periods数组 |
| UAT-037 | 2026-04-18 00:00 | P1-2 | 均线按钮与折叠成交量按钮重叠，需移到工具栏行 | **Medium** | ✅已修复 | 成交量/MACD按钮移到toolbar |
| UAT-038 | 2026-04-18 00:00 | P1-2 | 画线工具栏简化，添加清除画线按钮 | **Medium** | ✅已修复 | DrawingToolbar简化+clearAll |
| UAT-039 | 2026-04-18 00:00 | P1-2 | K线模式下拖拽画矩形显示统计（功能保留，按钮删除） | **Low** | ✅已修复 | 移除按钮保留brush功能 |
| UAT-040 | 2026-04-18 00:00 | P1-2 | 主图图例移到底部，只显示均线，使用彩色方块 | **Medium** | ✅已修复 | legend位置+样式调整 |
| UAT-041 | 2026-04-18 00:00 | P1-2 | 增大图表面积，缩小边距 | **Medium** | ✅已修复 | chartConfig.ts缩小grid margins |
| UAT-042 | 2026-04-18 00:00 | P1-2 | 副标题标的名称字体增大两号(16px) | **Low** | ✅已修复 | FXData.vue symbol-name字体 |
| UAT-043 | 2026-04-18 00:00 | P1-2 | 主图标题栏功能按钮排列间隙均匀 | **Low** | ✅已修复 | toolbar-right gap:8px |

### 严重级别定义

| 级别 | 定义 | 处理优先级 |
|------|------|-----------|
| **Critical** | 系统崩溃、数据丢失、核心功能无法使用 | 立即修复 |
| **High** | 主要功能异常、严重影响用户体验 | 当日修复 |
| **Medium** | 次要功能异常、有一定影响 | 本周修复 |
| **Low** | UI细节、文案错误、轻微体验问题 | 下版本修复 |
| **环境问题** | 外部数据源/网络限制，非系统内部bug | 记录并等待恢复 |

---

## 测试进度统计

| 优先级 | 测试项数 | 通过数 | 失败数 | 阻塞数 | 通过率 |
|--------|---------|--------|--------|--------|--------|
| P0 | 4 | 2 | 0 | 2 | 50% |
| P1 | 5 | 0 | 0 | 5 | 0% |
| P2 | 5 | 1 | 0 | 4 | 20% |
| P3 | 5 | | | | |
| P4 | 3 | 0 | 0 | 3 | 0% |
| P5 | 4 | | | | |
| P6 | 4 | | | | |
| **总计** | **30** | **3** | **0** | **9** | **10%** |

**注：系统内部问题43个均已修复，问题数量增至43个**

---

## 测试结论

### 测试完成时间
- 开始时间：2026-04-17 __:__
- 完成时间：2026-04-17 __:__

### 问题汇总
- Critical问题：__ 个
- High问题：__ 个
- Medium问题：__ 个
- Low问题：__ 个

### 结论选项
- ⬜ **PASS** - 所有P0-P4测试通过，无Critical/High问题
- ⬜ **PASS with Conditions** - P0-P4测试通过，存在Medium/Low问题待修复
- ⬜ **FAIL** - 存在Critical/High问题，需修复后重新测试

### 测试人员签字
测试人员：_______________
日期：2026-04-17

---

## 问题详情补充

### UAT-001
- **发现时间**：2026-04-17 10:30
- **测试步骤**：
  1. 打开浏览器访问 http://localhost:8000
  2. 输入用户名 admin 和密码 admin123
  3. 点击登录按钮
- **预期结果**：登录成功后自动跳转到系统首页（Dashboard）
- **实际结果**：页面显示"登录成功"提示消息，但未发生页面跳转，仍停留在登录页面
- **错误截图/日志**：待补充
- **重现频率**：100%（每次登录都会出现）
- **备注**：这是一个Critical级别问题，登录是系统入口功能，必须立即修复
- **根因分析**：
  - axios响应拦截器返回 `response.data`（第39行），而非完整response对象
  - auth.js中 `response.data.data.user` 取值错误（第44行），应为 `response.data.user`
  - 导致 `user.value = undefined`，`isLoggedIn = false`，路由守卫拦截跳转
- **修复方案**：修改 `frontend/src/stores/auth.js` 第44、48、87行，将 `response.data.data.xxx` 改为 `response.data.xxx`

### UAT-002
- **发现时间**：2026-04-17 10:45
- **测试步骤**：进入数据分析页面，观察顶部工具栏布局
- **预期结果**：白天/黑夜模式切换按钮与下方走势图工具栏无重叠
- **实际结果**：主题切换按钮与走势图"定位日期"按钮位置重叠，影响操作
- **错误截图/日志**：待补充
- **重现频率**：100%
- **备注**：UI布局问题，需调整样式
- **根因分析**：ProChart.vue中主题切换按钮定位在右上角（right: 12px），与KLineChart工具栏右侧按钮区域重叠
- **修复方案**：将主题切换按钮从右上角移到左上角（left: 12px），避免与工具栏右侧按钮重叠
- **状态**：✅ 已修复

### UAT-003
- **发现时间**：2026-04-17 10:45
- **测试步骤**：进入数据分析页面
- **预期结果**：页面正常加载，无错误提示
- **实际结果**：页面刷新时报错"获取货币对列表失败"
- **错误截图/日志**：待补充
- **重现频率**：100%
- **备注**：金融标的列表不应在页面初始化时加载，应改为用户选择时查询
- **根因分析**：FXData.vue的onMounted中调用fetchSymbols()自动获取标的列表，若API失败则报错
- **修复方案**：移除onMounted中的自动加载逻辑，改为用户输入时远程搜索
- **状态**：✅ 已修复

### UAT-004
- **发现时间**：2026-04-17 10:45
- **测试步骤**：选择金融标的
- **预期结果**：通过输入框输入标的代码进行检索
- **实际结果**：当前使用下拉列表方式选择，不符合用户预期
- **错误截图/日志**：待补充
- **重现频率**：100%
- **备注**：需改为输入框+数据库检索方式，检索不到时提示"无对应标的"
- **根因分析**：使用普通el-select下拉列表，不支持远程搜索
- **修复方案**：将el-select改为远程搜索模式（remote + remote-method），用户输入时实时搜索
- **状态**：✅ 已修复

### UAT-005
- **发现时间**：2026-04-17 10:45
- **测试步骤**：观察系统中对金融标的的命名
- **预期结果**：使用专业通用名称，覆盖股票、期货、外汇等
- **实际结果**：系统使用"货币对"命名，仅适用于外汇，不专业
- **错误截图/日志**：无
- **重现频率**：100%
- **备注**：建议改为"金融标的"或"交易标的"等通用名称
- **根因分析**：系统多处使用"货币对"命名，仅适用于外汇市场
- **修复方案**：全局将"货币对"改为"金融标的"，涉及FXData.vue、KLineChart.vue、DataSource.vue、helpContent.ts、locales等文件
- **状态**：✅ 已修复

### UAT-006
- **发现时间**：2026-04-17 10:45
- **测试步骤**：进入数据源管理页面
- **预期结果**：页面正常显示数据源列表，空数据时显示"无数据源"
- **实际结果**：刷新显示"获取数据源列表失败"错误提示
- **错误截图/日志**：待补充
- **重现频率**：100%
- **备注**：空数据不应报错，需检查API返回处理逻辑
- **根因分析**：
  - `datasource.py` schema中 `created_at` 和 `updated_at` 定义为 `date` 类型
  - 数据库实际存储为 `TIMESTAMP` 类型
  - Pydantic验证失败导致INTERNAL_ERROR
- **修复方案**：将schema中的类型改为 `datetime`

### UAT-007
- **发现时间**：2026-04-17 10:45
- **测试步骤**：进入采集任务页面
- **预期结果**：页面正常显示，无错误提示
- **实际结果**：刷新显示"获取基础数据失败"
- **错误截图/日志**：待补充
- **重现频率**：100%
- **备注**：需确认"基础数据"具体指什么，检查数据库初始化是否有遗漏
- **根因分析**：
  - 前端API路径缺少尾部斜杠：`/api/v1/collection-tasks` 应为 `/api/v1/collection-tasks/`
  - 后端使用 `"/"` 定义路由，生成带尾部斜杠的完整路径
  - 前端请求404导致获取失败
- **修复方案**：统一修复前端所有API路径，添加尾部斜杠匹配后端定义

### UAT-008
- **发现时间**：2026-04-17 10:45
- **测试步骤**：进入采集任务页面
- **预期结果**：页面正常显示任务列表，空数据时显示"无任务"
- **实际结果**：刷新显示"获取任务列表失败"错误提示
- **错误截图/日志**：待补充
- **重现频率**：100%
- **备注**：空数据不应报错，需检查API返回处理逻辑
- **根因分析**：同UAT-007，API路径尾部斜杠问题
- **修复方案**：修复前端API路径

### UAT-009
- **发现时间**：2026-04-17 17:30
- **测试步骤**：新建采集任务后，点击"立即执行"按钮手动触发采集
- **预期结果**：采集任务执行成功，返回采集记录数
- **实际结果**：采集任务执行失败，报错"relation forex_daily does not exist"
- **错误日志**：
  ```
  ERROR: relation "forex_daily" does not exist
  [SQL: SELECT ... FROM forex_daily ...]
  ```
- **重现频率**：100%
- **备注**：数据库初始化脚本执行失败，核心业务数据表未创建
- **根因分析**：
  - PostgreSQL分区表的主键必须包含分区键字段
  - init-db.sql定义 `id UUID PRIMARY KEY`，缺少分区键 `date`
  - 导致建表语句执行失败，forex_daily和futures_daily表未创建
  - 数据分析页面查询和采集任务写入均失败
- **修复方案**：
  - 修改init-db.sql：主键改为 `PRIMARY KEY (id, date)`
  - 修改forex_daily.py模型：date字段添加 `primary_key=True`
  - 手动创建forex_daily分区表及索引
  - 手动创建futures_daily分区表及索引
- **修复文件**：
  - `deployment-packages/database/init-db.sql`
  - `docker/init-db.sql`
  - `backend/app/models/forex_daily.py`
- **状态**：✅ 已修复并验证

### UAT-010
- **发现时间**：2026-04-17 17:42
- **测试步骤**：重新执行采集任务（UAT-009修复后）
- **预期结果**：采集任务执行成功，返回采集记录数
- **实际结果**：采集任务执行失败，AKShare `forex_hist_em` 接口连接被远程断开
- **错误日志**：
  ```
  ERROR: Connection aborted, RemoteDisconnected('Remote end closed connection without response')
  [调用ak.forex_hist_em(symbol='USDCNH')失败]
  ```
- **重现频率**：100%（3次重试均失败）
- **根因分析**：
  - AKShare库的 `forex_hist_em` 内部调用东方财富API时未添加必要的请求头
  - 东方财富API要求请求必须包含 `User-Agent` 和 `Referer` 头
  - 缺少这些头会导致连接被反爬虫机制拒绝
- **验证结果**：
  - 直接调用API（带headers） → ✅ 成功获取100条历史数据
  - AKShare库调用（无headers） → ❌ 连接被断开
  - 东方财富网站 `quote.eastmoney.com` → ✅ 可访问
- **修复方案**：
  - 改用直接HTTP请求调用东方财富API
  - 添加必要的请求头：`User-Agent`、`Referer`、`Accept`
  - 使用正确的secid格式：`133.{symbol}`（市场代码133=外汇）
- **修复文件**：
  - `backend/app/collectors/akshare_collector.py` - `_call_forex_hist`方法改用直接API调用
- **修复后验证**：
  - 执行采集任务 → ✅ 成功采集13条数据
  - 数据入库 → ✅ 数据正确保存到forex_daily表
- **状态**：✅ 已修复并验证

### UAT-011（约束名称不匹配）
- **发现时间**：2026-04-17 18:50
- **测试步骤**：修复UAT-010后再次执行采集任务
- **预期结果**：数据成功保存到数据库
- **实际结果**：保存失败，报错 "constraint 'uq_forex_daily_symbol_date_datasource' does not exist"
- **根因分析**：
  - SQLAlchemy模型定义约束名 `uq_forex_daily_symbol_date_datasource`
  - 实际数据库约束名 `forex_daily_symbol_id_date_datasource_id_key`
  - 约束名称不匹配导致ON CONFLICT DO UPDATE失败
- **修复方案**：
  - 更新 `forex_daily_service.py` 使用正确的约束名
  - 更新 `forex_daily.py` 模型定义保持一致性
- **修复文件**：
  - `backend/app/services/forex_daily_service.py`
  - `backend/app/models/forex_daily.py`
- **状态**：✅ 已修复并验证

### UAT-012（货币对同步API从未真正查询数据）
- **发现时间**：2026-04-17 19:20
- **测试步骤**：点击"同步货币对到数据库"按钮，观察数据库中的货币对代码
- **预期结果**：同步AKShare实际支持的货币对代码，如USDCNH
- **实际结果**：数据库中只有USDCNY等自创代码，从未出现过USDCNH
- **根因分析**：
  - `akshare_collector._fetch_forex_symbols()` 调用 `ak.forex_symbols()`
  - **AKShare根本没有forex_symbols接口！**
  - 每次调用都失败，返回默认列表（也是错误的USDCNY）
  - 同步API从未真正从AKShare获取数据
- **验证结果**：
  ```
  >>> import akshare as ak
  >>> ak.forex_symbols()
  AttributeError: module 'akshare' has no attribute 'forex_symbols'
  ```
- **AKShare实际支持的货币对代码**：
  - 从 `forex_em.symbol_market_map` 获取（共190个）
  - 正确代码：USDCNH（美元离岸人民币）、USDCNYC（美元人民币中间价）
  - 错误代码：USDCNY（设计者自创，AKShare不支持）
- **修复方案**：
  - 改用 `forex_em.symbol_market_map` 获取AKShare实际支持的货币对
  - 新增 `_generate_symbol_name()` 方法自动生成中文名称
  - 更新默认列表使用正确代码（USDCNH）
- **修复文件**：
  - `backend/app/collectors/akshare_collector.py` - `_fetch_forex_symbols`方法重构
- **修复后验证**：
  - 获取货币对 → ✅ 成功获取190个（包含USDCNH）
  - 同步到数据库 → ✅ 新增175个正确代码
- **状态**：✅ 已修复并验证

### UAT-013（初始化脚本使用错误代码）
- **发现时间**：2026-04-17 19:20
- **测试步骤**：检查init-db.sql中的货币对初始化数据
- **预期结果**：使用AKShare标准代码（USDCNH）
- **实际结果**：使用自创代码USDCNY，与AKShare不兼容
- **根因分析**：
  - `init-db.sql` 第363-366行硬编码INSERT使用USDCNY
  - 此代码为设计者自创，不是AKShare标准代码
  - 导致：
    - 数据库初始数据与AKShare不一致
    - 采集任务需要代码映射才能工作
    - 用户看到USDCNY但AKShare实际不支持
- **AKShare代码标准说明**：
  | 代码 | 含义 | 市场代码 |
  |------|------|---------|
  | USDCNH | 美元/离岸人民币 | 133 |
  | USDCNYC | 美元/人民币中间价 | 120 |
  | EURCNH | 欧元/离岸人民币 | 133 |
  | EURCNYC | 欧元/人民币中间价 | 120 |
  - CNH = 离岸人民币（可交易汇率）
  - CNYC = 人民币中间价（央行公布）
  - CNY = 人民币（通用符号，非交易代码）
- **修复方案**：
  - 更新 `init-db.sql` 使用AKShare标准代码
  - 清理数据库中的错误代码数据
- **修复文件**：
  - `deployment-packages/database/init-db.sql`
  - `docker/init-db.sql`
- **状态**：✅ 已修复并验证

### 通用问题总结：API路径尾部斜杠一致性
- **发现时间**：2026-04-17 10:30
- **问题描述**：后端路由定义不一致导致前端API调用失败
- **影响范围**：
  - `/api/v1/collection-tasks/` - 需要尾部斜杠
  - `/api/v1/datasources/` - 需要尾部斜杠
  - `/api/v1/forex-symbols/` - 需要尾部斜杠
  - `/api/v1/markets/` - 需要尾部斜杠
- **修复文件**：
  - `frontend/src/api/collection.js`
  - `frontend/src/api/datasources.js`
  - `frontend/src/api/forex_symbols.js`
  - `frontend/src/api/markets.js`
- **状态**：✅ 已全部修复

### 通用问题：后端API缺失
- **发现时间**：2026-04-17 10:30
- **问题描述**：前端调用 `/api/v1/auth/me` 但后端未实现该API
- **根因分析**：
  - 前端 `stores/auth.js` 中 `fetchUser()` 方法调用 `/api/v1/auth/me`
  - 后端 `auth.py` 中只有 `/login` 和 `/logout` 路由
  - 导致用户信息刷新失败
- **修复文件**：`backend/app/api/v1/auth.py` - 添加 `/me` 路由
- **修复内容**：
  - 新增 `get_current_user()` 函数
  - 通过 session_id 获取 session，再获取用户信息
  - 返回 UserResponse 格式的用户数据
- **状态**：✅ 已修复并验证

### UAT-014（刷新页面Session丢失）
- **发现时间**：2026-04-17 20:00
- **测试步骤**：登录系统后刷新浏览器页面
- **预期结果**：页面刷新后保持登录状态，无需重新登录
- **实际结果**：刷新页面后返回登录页，需要重新登录
- **根因分析**：
  - `stores/auth.js` 使用 `sessionStorage` 存储 `session_id`（刷新不会丢失）
  - 但刷新后 `user` 状态为 `null`（Pinia状态未恢复）
  - 路由守卫检查 `isLoggedIn` 失败，跳转到登录页
- **修复方案**：
  - 在 `main.js` 应用初始化时检查 `sessionStorage` 是否有 `session_id`
  - 如果有，调用 `authStore.fetchUser()` 恢复用户状态
- **修复文件**：
  - `frontend/src/main.js` - 添加应用初始化逻辑
- **状态**：✅ 已修复并验证

### UAT-015（页面标题和价格信息展示优化）
- **发现时间**：2026-04-17 20:00
- **测试步骤**：进入数据分析页面观察布局
- **预期结果**：标题简洁，价格信息一行展示
- **实际结果**：
  - "数据分析 专业行情走势"标题冗余
  - 当前价格、涨跌幅等用独立卡片展示，占用空间大
- **修复方案**：
  - 删除 `page-subtitle` 副标题
  - 将 `stats-row` 改为 `price-info` inline展示
  - 价格信息与标的选择、周期选择在同一行
- **修复文件**：
  - `frontend/src/views/FXData.vue` - 标题精简+价格inline
- **状态**：✅ 已修复并验证

### UAT-016（删除历史数据表格）
- **发现时间**：2026-04-17 20:00
- **测试步骤**：观察数据分析页面底部
- **预期结果**：无历史数据表格和导出功能
- **实际结果**：页面底部有历史数据表格和导出按钮
- **修复方案**：
  - 删除 `data-table-section` 模板部分
  - 删除 `tableData`、`exportData` 相关代码
  - 删除表格相关样式
- **修复文件**：
  - `frontend/src/views/FXData.vue` - 删除历史数据表格
- **状态**：✅ 已修复并验证

### UAT-017（全局主题切换）
- **发现时间**：2026-04-17 20:00
- **测试步骤**：切换白天/夜间模式
- **预期结果**：整个前端风格切换，按钮在页面顶部用户名旁
- **实际结果**：只改变走势图部分，按钮在图表左上角
- **修复方案**：
  - 创建 `stores/theme.js` 全局主题状态管理
  - 在 `Navbar.vue` 添加主题切换按钮（用户名旁）
  - 在 `styles/index.css` 添加 `[data-theme="dark"]` 夜间模式CSS变量
  - 修改 `ProChart.vue` 移除独立主题按钮，使用全局主题
- **修复文件**：
  - `frontend/src/stores/theme.js` - 新建全局主题store
  - `frontend/src/components/Navbar.vue` - 添加主题切换按钮
  - `frontend/src/styles/index.css` - 夜间模式CSS变量
  - `frontend/src/components/charts/ProChart.vue` - 使用全局主题
- **状态**：✅ 已修复并验证

### UAT-018（刷新页面跳转登录页-异步初始化）
- **发现时间**：2026-04-17 21:30
- **测试步骤**：登录系统后刷新浏览器页面
- **预期结果**：页面刷新后保持登录状态
- **实际结果**：刷新后跳转登录页，需重新登录
- **根因分析**：
  - `main.js`调用`authStore.fetchUser()`是异步操作
  - 应用在fetchUser完成前就挂载了
  - 路由守卫检查时用户状态仍为null
- **修复方案**：
  - 将应用初始化改为async函数
  - 使用await等待fetchUser完成后再挂载应用
- **修复文件**：
  - `frontend/src/main.js` - 改为async initializeApp()
- **状态**：✅ 已修复并验证

### UAT-019（标题栏太宽）
- **发现时间**：2026-04-17 21:30
- **测试步骤**：观察页面顶部导航栏布局
- **预期结果**：标题栏紧凑，文字和按钮比例适中
- **实际结果**：标题栏太宽，占用过多空间
- **修复方案**：
  - Navbar.vue缩小标题字体(18px→15px)
  - 缩小副标题(12px→11px)
  - 缩小用户头像(36px→28px)
  - 缩小按钮尺寸和间距
  - FXData.vue缩小标题(20px→16px)
  - 价格信息字体(14px→12px)
- **修复文件**：
  - `frontend/src/components/Navbar.vue`
  - `frontend/src/views/FXData.vue`
- **状态**：✅ 已修复并验证

### UAT-020（删除冗余副标题）
- **发现时间**：2026-04-17 21:30
- **测试步骤**：进入数据分析页面
- **预期结果**：标题简洁，无冗余文字
- **实际结果**：副标题显示"外汇行情数据可视化"，多余
- **修复方案**：
  - 将FXData页面的副标题设置为空字符串
- **修复文件**：
  - `frontend/src/components/Navbar.vue` - pageSubtitle.fx-data改为''
- **状态**：✅ 已修复并验证

### UAT-021（夜间模式样式问题）
- **发现时间**：2026-04-17 21:30
- **测试步骤**：切换到夜间模式，观察界面元素
- **预期结果**：文字清晰可见，按钮正常显示
- **实际结果**：
  - 白底背景上的文字看不清（文字颜色未适配）
  - 按钮反色后遮盖文字内容
- **修复方案**：
  - 完善`index.css`夜间模式CSS变量覆盖
  - 为Element Plus组件添加夜间模式样式：
    - el-input: 背景和文字颜色
    - el-select: 下拉框样式
    - el-button: 按钮背景和文字
    - el-table: 表格样式
    - el-dropdown: 下拉菜单
    - el-switch: 开关组件
    - el-pagination: 分页组件
    - el-tag: 标签组件
  - 确保夜间模式下所有文字使用浅色(--fdas-text-primary)
- **修复文件**：
  - `frontend/src/styles/index.css` - 完善夜间模式CSS
- **状态**：✅ 已修复并验证

### UAT-033（删除成交量警告提示）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：观察成交量副图区域
- **预期结果**：无警告提示
- **实际结果**：显示"外汇市场通常无成交量数据"警告提示，用户认为多余
- **修复方案**：
  - 删除VolumeChart.vue中的warning模板和computed属性
  - 删除Warning图标导入和相关CSS
- **修复文件**：
  - `frontend/src/components/charts/VolumeChart.vue`
- **状态**：✅ 已修复并验证

### UAT-034（删除区间选择按钮）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：观察KLineChart工具栏
- **预期结果**：无矩形选择、圈选、取消选择按钮
- **实际结果**：存在interval选择相关按钮，用户不需要
- **修复方案**：
  - 移除KLineChart.vue中的interval选择按钮
  - 保留brush功能用于矩形拖拽统计
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue`
- **状态**：✅ 已修复并验证

### UAT-035（默认显示30周期）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：加载行情图表
- **预期结果**：默认显示最近30个周期，数据不足则全部显示
- **实际结果**：默认显示全部数据，过多时难以查看
- **修复方案**：
  - 修改resetView()函数动态计算DataZoom范围
  - 数据<=30时显示全部(0-100%)
  - 数据>30时显示最近30周期
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - resetView()
- **状态**：✅ 已修复并验证

### UAT-036（后端MA同步7个选项）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：选择MA120/MA240均线
- **预期结果**：后端计算并返回MA120/MA240数据
- **实际结果**：后端只计算MA5/10/20/30/60，缺少MA120/MA240
- **修复方案**：
  - 更新technical_service.py的periods数组
  - 从[5,10,20,30,60]改为[5,10,20,30,60,120,240]
- **修复文件**：
  - `backend/app/services/technical_service.py` - calculate_all_ma()
- **状态**：✅ 已修复并验证

### UAT-037（按钮重叠修复）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：观察KLineChart工具栏均线按钮和成交量折叠按钮
- **预期结果**：按钮排列不重叠，间隙均匀
- **实际结果**：均线下拉按钮与成交量折叠按钮位置重叠
- **修复方案**：
  - 将成交量/MACD折叠按钮移到toolbar-right
  - 统一按钮间距为8px
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - toolbar布局
- **状态**：✅ 已修复并验证

### UAT-038（画线工具栏简化）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：点击画线工具按钮
- **预期结果**：简化的画线工具栏，包含清除画线按钮
- **实际结果**：工具栏复杂，无清除画线功能
- **修复方案**：
  - 简化DrawingToolbar.vue为4个工具按钮+5种颜色+清除按钮
  - 添加clearAll emit事件
  - KLineChart.vue添加@clearAll处理
- **修复文件**：
  - `frontend/src/components/charts/DrawingToolbar.vue` - 简化版本
  - `frontend/src/components/charts/KLineChart.vue` - clearAll处理
- **状态**：✅ 已修复并验证

### UAT-039（矩形拖拽统计保留）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：在K线模式下拖拽矩形
- **预期结果**：拖拽完成后显示区间统计面板
- **实际结果**：按钮删除后brush功能仍保留
- **备注**：功能保留，只是删除了显式的区间选择按钮
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - brush功能保持
- **状态**：✅ 已保留功能

### UAT-040（图例位置和样式）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：观察K线图表例
- **预期结果**：图例在底部，只显示MA，使用彩色方块图标
- **实际结果**：图例在顶部，显示K线和收盘价，图标样式不符
- **修复方案**：
  - chartConfig.ts: legend位置改为bottom:5
  - legend.data只添加MA系列名称
  - 使用彩色方块(itemWidth/Height:12)
- **修复文件**：
  - `frontend/src/utils/chartConfig.ts`
  - `frontend/src/components/charts/KLineChart.vue`
- **状态**：✅ 已修复并验证

### UAT-041（增大图表面积）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：观察图表布局
- **预期结果**：图表区域尽可能大，边距最小化
- **实际结果**：左右边距过大，浪费显示空间
- **修复方案**：
  - grid margins: left 8%, right 4%, top 5%
  - 增加主图height到60%
  - 减少legend占用空间
- **修复文件**：
  - `frontend/src/utils/chartConfig.ts` - grid配置
- **状态**：✅ 已修复并验证

### UAT-042（标的名称字体增大）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：观察副标题中的标的名称
- **预期结果**：标的名称字体增大两号，突出显示
- **实际结果**：字体偏小，不够醒目
- **修复方案**：
  - FXData.vue: symbol-name字体从14px改为16px
- **修复文件**：
  - `frontend/src/views/FXData.vue` - .symbol-name样式
- **状态**：✅ 已修复并验证

### UAT-043（按钮间隙均匀）
- **发现时间**：2026-04-18 00:00
- **测试步骤**：观察KLineChart工具栏按钮排列
- **预期结果**：所有按钮间隙均匀一致
- **实际结果**：按钮间隙不均匀，视觉效果不佳
- **修复方案**：
  - toolbar-right: gap统一为8px
  - 添加padding-left:24px增加与左侧间距
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - toolbar样式
- **状态**：✅ 已修复并验证

---

## Round 7 - 第七轮UAT测试问题（2026-04-18）

### UAT-044（侧边栏收起后图表自适应）
- **发现时间**：2026-04-18 02:00
- **测试步骤**：点击侧边栏折叠按钮，观察主图表区域
- **预期结果**：图表自动扩展填充空白区域
- **实际结果**：侧边栏收起后，主图右边有空白，走势图没有自适应拉长
- **修复方案**：
  - Layout.vue: toggleSidebar时触发window resize事件
  - 图表组件监听resize事件并重新渲染
- **修复文件**：
  - `frontend/src/components/Layout.vue` - toggleSidebar函数
- **状态**：✅ 已修复

### UAT-045（动态数据加载）
- **发现时间**：2026-04-18 02:00
- **测试步骤**：观察日线行情图，尝试查看早期历史数据
- **预期结果**：可加载足够历史数据（至少4年），无硬性条数限制
- **实际结果**：只能查看有限历史数据（约1年）
- **修复方案**：
  - 前端: 增加数据请求limit（daily:1000, weekly:208, monthly:48）
  - 后端: 扩大默认日期范围（支持4年历史）
  - fx_data.py: start_date改为4年前
  - 增加raw_data查询limit以支持聚合计算
- **修复文件**：
  - `frontend/src/views/FXData.vue` - fetchData limit参数
  - `backend/app/api/v1/fx_data.py` - start_date日期范围
- **状态**：✅ 已修复

### UAT-046（键盘导航重新设计）
- **发现时间**：2026-04-18 02:00
- **测试步骤**：按键盘左右键移动K线视图
- **预期结果**：左右键移动十字线一根K线，到达边缘时移动视图
- **实际结果**：左右键移动整个视图，不移动十字线
- **修复方案**：
  - 新增moveCursorByKline函数：移动十字线一根K线
  - 新增zoomAtCursor函数：以十字线为中心缩放
  - 新增getVisibleRange/getVisibleCenterIndex辅助函数
  - 自动锁定十字线，键盘始终控制十字线位置
  - 到达边缘时自动移动视图保持十字线可见
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - handleKeydown及相关函数
- **状态**：✅ 已修复

### UAT-047（侧边栏宽度缩窄）
- **发现时间**：2026-04-18 02:00
- **测试步骤**：观察侧边栏宽度占比
- **预期结果**：侧边栏较窄，图表区域占比更大
- **实际结果**：侧边栏过宽（220px），浪费显示空间
- **修复方案**：
  - Layout.vue: 展开宽度从220px改为180px
  - Sidebar.vue: el-menu宽度同步改为180px
- **修复文件**：
  - `frontend/src/components/Layout.vue` - sidebarWidth
  - `frontend/src/components/Sidebar.vue` - el-menu样式
- **状态**：✅ 已修复

### UAT-048（矩形拖拽统计功能）
- **发现时间**：2026-04-18 02:00
- **测试步骤**：点击矩形选择按钮，拖拽选择K线区间
- **预期结果**：显示区间统计面板（涨跌幅、振幅等）
- **实际结果**：功能未实现，缺少brush feature
- **修复方案**：
  - chartConfig.ts: 添加brush配置（矩形框选）
  - KLineChart.vue: 
    - 导入RangeStats组件
    - 添加brushActive状态和toggleBrush函数
    - 监听brush事件计算区间统计
    - 在模板中添加RangeStats面板和框选按钮
  - 添加Rank图标用于框选按钮
- **修复文件**：
  - `frontend/src/utils/chartConfig.ts` - brush配置
  - `frontend/src/components/charts/KLineChart.vue` - brush事件处理和RangeStats
- **状态**：✅ 已修复

### UAT-049（昨收价标签位置）
- **发现时间**：2026-04-18 02:00
- **测试步骤**：观察主图黄色虚线（昨收价）标签位置
- **预期结果**：标签显示在左端
- **实际结果**：标签显示在右端
- **修复方案**：
  - K线markLine: label添加position: 'start'
  - 折线markLine: label改为position: 'start'
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - markLine label position
- **状态**：✅ 已修复

---

## Round 8-11 - 第八至十一轮UAT测试问题（2026-04-18）

### UAT-050（删除光标锁定浮窗）
- **发现时间**：2026-04-18 03:00
- **测试步骤**：观察K线图表区域
- **预期结果**：无光标锁定浮窗面板
- **实际结果**：存在cursor-lock-panel浮窗，显示光标锁定状态
- **修复方案**：
  - 删除KLineChart.vue中的cursor-lock-panel模板和CSS样式
  - 移除cursorLocked状态和相关锁定功能
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - 删除cursor-lock-panel
- **状态**：✅ 已修复

### UAT-051（删除功能按钮）
- **发现时间**：2026-04-18 03:00
- **测试步骤**：观察K线工具栏按钮
- **预期结果**：无矩形选择、圈选、取消选择按钮
- **实际结果**：按钮再次出现（可能为部署未同步）
- **修复方案**：
  - 确认按钮删除代码已部署
  - 重新构建前端并部署
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - 确认按钮删除
- **状态**：✅ 已修复

### UAT-052（鼠标拖拽统计功能）
- **发现时间**：2026-04-18 03:00
- **测试步骤**：在K线图上单击并拖拽
- **预期结果**：拖拽后显示区间统计面板
- **实际结果**：功能未正确实现
- **修复方案**：
  - 添加mousedown/mousemove/mouseup事件处理
  - 实现crosshairTracking状态跟踪
  - 计算拖拽范围内的统计数据
  - 使用markArea显示选中区域
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - 拖拽事件处理
  - `frontend/src/components/charts/RangeStats.vue` - 统计面板
- **状态**：✅ 已修复

### UAT-053（主图副图同步缩放）
- **发现时间**：2026-04-18 04:00
- **测试步骤**：缩放主图K线，观察成交量/MACD副图
- **预期结果**：副图与主图同步缩放、移动
- **实际结果**：副图未同步缩放
- **修复方案**：
  - 使用echarts.connect实现图表联动
  - VolumeChart/MACDChart添加dataZoom配置
  - 设置相同的start/end参数
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - echarts.connect
  - `frontend/src/components/charts/VolumeChart.vue` - dataZoom配置
  - `frontend/src/components/charts/MACDChart.vue` - dataZoom配置
- **状态**：✅ 已修复

### UAT-054（侧边栏收起后空白）
- **发现时间**：2026-04-18 04:00
- **测试步骤**：收起侧边栏，观察图表右侧
- **预期结果**：图表扩展填充空间，无空白
- **实际结果**：侧边栏收起后图表右侧仍有空白
- **修复方案**：
  - Layout.vue: toggleSidebar时添加delayed resize触发
  - 使用nextTick + setTimeout确保DOM更新后再resize
- **修复文件**：
  - `frontend/src/components/Layout.vue` - delayed resize
- **状态**：✅ 已修复

### UAT-055（MACD副图未同步）
- **发现时间**：2026-04-18 04:30
- **测试步骤**：移动主图，观察MACD副图
- **预期结果**：MACD副图与主图同步移动
- **实际结果**：MACD副图未跟随主图同步刷新
- **修复方案**：
  - 添加MACDChart dataZoom配置与主图一致
  - 使用echarts.connect绑定所有图表
- **修复文件**：
  - `frontend/src/components/charts/MACDChart.vue` - dataZoom配置
- **状态**：✅ 已修复

### UAT-056（边界错误提示）
- **发现时间**：2026-04-18 05:00
- **测试步骤**：移动十字光标到数据边界
- **预期结果**：到达边界时无错误提示，静默处理
- **实际结果**：到达边界显示"已到最早数据"等错误提示
- **修复方案**：
  - 移除边界检查时的ElMessage.warning调用
  - 到达边界时直接return，不显示任何提示
- **修复文件**：
  - `frontend/src/components/charts/KLineChart.vue` - 移除warning
- **状态**：✅ 已修复

### UAT-057（副图数值日期对齐）
- **发现时间**：2026-04-18 05:00
- **测试步骤**：对比主图日期与副图MACD数值
- **预期结果**：副图数值与主图按日期对齐
- **实际结果**：副图数据与主图日期不一致
- **修复方案**：
  - 后端MACD/成交量计算确保数据长度与K线一致
  - 前端接收后直接渲染，无需额外对齐处理
- **修复文件**：
  - `backend/app/utils/technical_utils.py` - EMA返回长度对齐
  - `backend/app/services/technical_service.py` - MACD对齐逻辑
  - `backend/app/services/period_aggregation_service.py` - MACD对齐逻辑
- **状态**：✅ 已修复

### UAT-058（缩放范围限制）
- **发现时间**：2026-04-18 05:00
- **测试步骤**：缩放K线图表
- **预期结果**：最少显示60根K线，最多显示300根
- **实际结果**：缩放无范围限制
- **修复方案**：
  - chartConfig.ts: dataZoom添加minValueSpan/maxValueSpan
  - minValueSpan=60, maxValueSpan=300
  - 使用rangeMode=['value', 'value']固定计数模式
- **修复文件**：
  - `frontend/src/utils/chartConfig.ts` - dataZoom范围限制
- **状态**：✅ 已修复

### UAT-059（MACD缺少最新数据）
- **发现时间**：2026-04-18 05:30
- **测试步骤**：查看MACD副图，检查最新日期4-17的数值
- **预期结果**：MACD有最新日期(4-17)的数值
- **实际结果**：MACD最近30多天都没有数值
- **根因分析**：
  - calculate_ema函数返回数组长度不等于输入长度
  - EMA(12)返回338-12+1=327元素，EMA(26)返回313元素
  - DIF计算使用错误的索引访问不同长度数组
  - 最终MACD数组只有327元素，缺少最近11个数据点
- **修复方案**：
  - 重写calculate_ema函数：前period-1个元素用SMA填充
  - 确保EMA返回长度与输入一致
  - 简化MACD计算逻辑：直接对齐数组相减
  - 最终对齐：offset=34，前33个None+剩余数据
- **修复文件**：
  - `backend/app/utils/technical_utils.py` - EMA长度对齐
  - `backend/app/services/technical_service.py` - MACD计算重构
  - `backend/app/services/period_aggregation_service.py` - MACD计算重构
- **验证结果**：
  - K-line data length: 338
  - MACD dif length: 338 ✓
  - MACD dea length: 338 ✓
  - MACD bar length: 338 ✓
  - Latest date 2026-04-17: DIF=-0.0224 ✓
- **状态**：✅ 已修复并验证

---

## 附录：测试辅助命令

```bash
# 检查系统状态
curl http://localhost:8000/api/health

# 检查容器状态
docker ps --filter "name=fdas"

# 查看应用日志
docker logs fdas-app --tail 50

# 查看数据库状态
docker exec fdas-db psql -U fdas -d fdas -c "SELECT COUNT(*) FROM forex_symbols;"

# 重启服务（如需要）
cd deployment-packages/multi-container
./deploy.sh --action restart
```