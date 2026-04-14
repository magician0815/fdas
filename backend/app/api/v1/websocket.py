"""
WebSocket API路由.

提供实时数据推送WebSocket接口.

Author: FDAS Team
Created: 2026-04-14
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.core.deps import get_current_user_ws
from app.services.websocket_service import ws_manager, websocket_handler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/realtime/{symbol_id}")
async def websocket_realtime(
    websocket: WebSocket,
    symbol_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    实时行情WebSocket连接.

    Args:
        websocket: WebSocket连接
        symbol_id: 标的ID
        db: 数据库会话
    """
    await websocket.accept()

    # 验证用户身份（从WebSocket header或query参数获取token）
    try:
        user_id = await get_current_user_ws(websocket, db)
        if not user_id:
            await websocket.close(code=4001, reason="Unauthorized")
            return

        # 注册连接
        await ws_manager.connect(websocket, user_id, symbol_id)

        # 处理消息
        await websocket_handler(websocket, user_id)

    except WebSocketDisconnect:
        logger.info(f"WebSocket断开: symbol={symbol_id}")

    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        await websocket.close(code=4000, reason=str(e))

    finally:
        # 清理连接
        await ws_manager.disconnect(websocket, user_id, symbol_id)


@router.websocket("/ws/chart")
async def websocket_chart(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """
    图表WebSocket连接（可动态订阅多个标的）.

    Args:
        websocket: WebSocket连接
        db: 数据库会话
    """
    await websocket.accept()

    try:
        user_id = await get_current_user_ws(websocket, db)
        if not user_id:
            await websocket.close(code=4001, reason="Unauthorized")
            return

        # 处理消息（包含订阅/取消订阅逻辑）
        await websocket_handler(websocket, user_id)

    except WebSocketDisconnect:
        logger.info(f"图表WebSocket断开")

    except Exception as e:
        logger.error(f"图表WebSocket错误: {e}")

    finally:
        await ws_manager.disconnect_all(websocket)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    获取WebSocket连接统计.
    """
    return {
        "total_connections": ws_manager.get_connection_count(),
        "active_users": len(ws_manager.active_connections)
    }