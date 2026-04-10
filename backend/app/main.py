"""
FastAPI应用入口.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 注册新API路由，更新启动/关闭事件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.logging import setup_logging, get_logger
from app.core.exceptions import register_exception_handlers

# 初始化日志
setup_logging()
logger = get_logger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="FDAS - 金融数据抓取与分析系统",
    description="基于FastAPI构建的金融数据采集与可视化API服务",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 注册异常处理器
register_exception_handlers(app)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    应用启动事件处理.

    初始化数据库连接池、APScheduler调度器等.
    """
    from app.services.scheduler_service import scheduler_service
    from app.services.collection_service import collection_service

    # 启动调度器
    scheduler_service.start()

    # 加载已启用的采集任务
    await collection_service.load_enabled_tasks()

    logger.info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件处理.

    关闭数据库连接池、停止调度器等.
    """
    from app.services.scheduler_service import scheduler_service

    # 关闭调度器
    scheduler_service.shutdown(wait=True)

    logger.info("应用关闭完成")


@app.get("/api/health")
async def health_check():
    """
    健康检查接口.

    Returns:
        dict: 服务健康状态信息
    """
    return {"status": "healthy", "version": "1.0.0"}


# 注册API路由
from app.api.v1 import auth, users, fx_data, datasources, collection_tasks, markets, forex_symbols

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(markets.router, prefix="/api/v1/markets", tags=["市场类型"])
app.include_router(datasources.router, prefix="/api/v1/datasources", tags=["数据源管理"])
app.include_router(forex_symbols.router, prefix="/api/v1/forex-symbols", tags=["外汇标的"])
app.include_router(collection_tasks.router, prefix="/api/v1/collection-tasks", tags=["采集任务管理"])
app.include_router(fx_data.router, prefix="/api/v1/fx", tags=["外汇行情数据"])