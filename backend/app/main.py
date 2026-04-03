"""
FastAPI应用入口.

Author: FDAS Team
Created: 2026-04-03
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.logging import setup_logging
from app.core.exceptions import register_exception_handlers

# 初始化日志
setup_logging()

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
    # TODO: 实现数据库连接池初始化
    # TODO: 实现APScheduler调度器初始化
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件处理.

    关闭数据库连接池、停止调度器等.
    """
    # TODO: 实现资源清理
    pass


@app.get("/api/health")
async def health_check():
    """
    健康检查接口.

    Returns:
        dict: 服务健康状态信息
    """
    return {"status": "healthy", "version": "1.0.0"}


# TODO: 注册API路由
# from app.api.v1 import auth, users, fx_data, datasource, collection, system
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
# app.include_router(fx_data.router, prefix="/api/v1/fx", tags=["汇率数据"])
# app.include_router(datasource.router, prefix="/api/v1/datasource", tags=["数据源管理"])
# app.include_router(collection.router, prefix="/api/v1/collection", tags=["采集任务管理"])
# app.include_router(system.router, prefix="/api/v1/system", tags=["系统管理"])