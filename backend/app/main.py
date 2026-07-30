"""
FastAPI应用入口.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-16 - 添加slowapi速率限制中间件，支持测试环境禁用
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config.settings import settings
from app.config.logging import setup_logging, get_logger
from app.core.exceptions import register_exception_handlers

# 初始化日志
setup_logging()
logger = get_logger(__name__)

# 检测是否在测试环境中
TESTING = os.environ.get("TESTING", "").lower() in ("true", "1", "yes")

# 初始化速率限制器（测试环境禁用）
limiter = Limiter(key_func=get_remote_address, enabled=not TESTING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理.

    使用lifespan handler代替deprecated on_event.
    """
    from app.services.scheduler_service import scheduler_service
    from app.services.collection_service import collection_service
    from app.services.macro_collection_service import macro_collection_service

    # Startup
    # 安全检查：验证SESSION_SECRET已配置
    if not settings.SESSION_SECRET:
        logger.error("SESSION_SECRET未配置，请在环境变量中设置")
        raise ValueError("SESSION_SECRET must be set in environment variables")

    scheduler_service.start()
    await collection_service.load_enabled_tasks()
    await macro_collection_service.load_enabled_configs()
    logger.info("应用启动完成")

    yield

    # Shutdown
    scheduler_service.shutdown(wait=True)
    logger.info("应用关闭完成")


# 创建FastAPI应用实例
app = FastAPI(
    title="FDAS - 金融数据抓取与分析系统",
    description="基于FastAPI构建的金融数据采集与可视化API服务",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# 添加速率限制器状态
app.state.limiter = limiter
# 注册速率限制异常处理器
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 注册异常处理器
register_exception_handlers(app)

# CORS中间件配置 - 收紧安全策略
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 仅允许必要方法
    allow_headers=["Content-Type", "X-Session-ID", "Authorization"],  # 仅允许必要headers
)


@app.get("/api/health")
async def health_check():
    """
    健康检查接口.

    Returns:
        dict: 服务健康状态信息
    """
    return {"status": "healthy", "version": "2.0.0"}


# 注册API路由
from app.api.v1 import auth, users, fx_data, datasources, datasource_wizard, collection_tasks, markets, forex_symbols, chart_settings, stocks
from app.api.v1 import stock_symbols, stock_data, futures_varieties, futures_data, bond_symbols, bond_data
from app.api.v1 import macro_configs, macro_data, macro_collection, macro_calcs

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(markets.router, prefix="/api/v1/markets", tags=["市场类型"])
app.include_router(datasources.router, prefix="/api/v1/datasources", tags=["数据源管理"])
app.include_router(datasource_wizard.router, prefix="/api/v1/datasources", tags=["数据源向导"])
app.include_router(forex_symbols.router, prefix="/api/v1/forex-symbols", tags=["外汇标的"])
app.include_router(collection_tasks.router, prefix="/api/v1/collection-tasks", tags=["采集任务管理"])
app.include_router(fx_data.router, prefix="/api/v1/fx", tags=["外汇行情数据"])
app.include_router(chart_settings.router, prefix="/api/v1/chart", tags=["图表设置"])
# stocks.router 已经包含 prefix="/stocks"
app.include_router(stocks.router, prefix="/api/v1", tags=["股票数据"])
# stock_symbols 无 prefix
app.include_router(stock_symbols.router, prefix="/api/v1", tags=["股票标的"])
# stock_data.router 已包含 prefix="/stock/data"
app.include_router(stock_data.router, prefix="/api/v1", tags=["股票行情数据"])
# futures_varieties 无 prefix
app.include_router(futures_varieties.router, prefix="/api/v1", tags=["期货品种"])
# futures_data.router 已包含 prefix="/futures/data"
app.include_router(futures_data.router, prefix="/api/v1", tags=["期货行情数据"])
# bond_symbols 无 prefix
app.include_router(bond_symbols.router, prefix="/api/v1", tags=["债券标的"])
# bond_data.router 已包含 prefix="/bond/data"
app.include_router(bond_data.router, prefix="/api/v1", tags=["债券行情数据"])
# 宏观数据采集模块 (V2.0)
app.include_router(macro_configs.router, prefix="/api/v1", tags=["宏观数据源配置"])
app.include_router(macro_data.router, prefix="/api/v1", tags=["宏观数据"])
app.include_router(macro_collection.router, prefix="/api/v1", tags=["宏观采集"])
app.include_router(macro_calcs.router, prefix="/api/v1", tags=["指标测算"])

# 诊断工具（后端自带，不受卷挂载影响）
DIAG_DIR = Path("/app/static_diag")
if DIAG_DIR.exists() and DIAG_DIR.is_dir():
    app.mount("/diag", StaticFiles(directory=DIAG_DIR, html=True), name="diag")

# 静态文件服务（前端）
STATIC_DIR = Path("/app/static")
if STATIC_DIR.exists() and STATIC_DIR.is_dir():
    # 挂载静态资源目录（CSS、JS、图片等）
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
    # 首页处理 - 返回index.html
    from fastapi.responses import FileResponse

    @app.get("/")
    async def serve_index():
        """返回前端首页."""
        return FileResponse(STATIC_DIR / "index.html")

    # 捕获所有未匹配的路径
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA路由支持. API路径404, 静态文件直接返回, 其余返回index.html."""
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        # 如果路径对应实际文件, 直接返回
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # SPA fallback
        return FileResponse(STATIC_DIR / "index.html")