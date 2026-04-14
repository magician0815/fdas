"""
WebSocket实时数据推送服务.

提供实时行情数据推送功能，支持断线重连、心跳检测.

Author: FDAS Team
Created: 2026-04-14
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Any, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器."""

    def __init__(self):
        # 活跃连接字典 {user_id: {symbol_id: [websocket_connections]}}
        self.active_connections: Dict[str, Dict[str, Set[Any]]] = {}
        # 心跳间隔（秒）
        self.heartbeat_interval = 30
        # 数据推送间隔（秒）
        self.push_interval = 5
        # 是否运行中
        self.is_running = False

    async def connect(self, websocket: Any, user_id: str, symbol_id: str):
        """
        注册WebSocket连接.

        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID
            symbol_id: 标的ID
        """
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}

        if symbol_id not in self.active_connections[user_id]:
            self.active_connections[user_id][symbol_id] = set()

        self.active_connections[user_id][symbol_id].add(websocket)
        logger.info(f"WebSocket连接注册: user={user_id}, symbol={symbol_id}")

        # 发送连接成功消息
        await self.send_message(websocket, {
            "type": "connected",
            "symbol_id": symbol_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def disconnect(self, websocket: Any, user_id: str, symbol_id: str):
        """
        移除WebSocket连接.

        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID
            symbol_id: 标的ID
        """
        if user_id in self.active_connections:
            if symbol_id in self.active_connections[user_id]:
                self.active_connections[user_id][symbol_id].discard(websocket)

                # 如果该标的没有连接了，移除标的键
                if not self.active_connections[user_id][symbol_id]:
                    del self.active_connections[user_id][symbol_id]

                # 如果用户没有连接了，移除用户键
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]

        logger.info(f"WebSocket连接断开: user={user_id}, symbol={symbol_id}")

    async def disconnect_all(self, websocket: Any):
        """
        断开指定WebSocket的所有订阅.

        Args:
            websocket: WebSocket连接对象
        """
        for user_id in list(self.active_connections.keys()):
            for symbol_id in list(self.active_connections[user_id].keys()):
                self.active_connections[user_id][symbol_id].discard(websocket)

    async def send_message(self, websocket: Any, message: Dict[str, Any]):
        """
        发送消息到单个连接.

        Args:
            websocket: WebSocket连接对象
            message: 消息内容
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")

    async def broadcast_to_symbol(self, symbol_id: str, message: Dict[str, Any]):
        """
        广播消息到订阅指定标的的所有连接.

        Args:
            symbol_id: 标的ID
            message: 消息内容
        """
        disconnected = []

        for user_id in self.active_connections:
            if symbol_id in self.active_connections[user_id]:
                for websocket in self.active_connections[user_id][symbol_id]:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"广播消息失败: {e}")
                        disconnected.append((websocket, user_id, symbol_id))

        # 移除断开的连接
        for ws, uid, sid in disconnected:
            await self.disconnect(ws, uid, sid)

    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """
        广播消息到指定用户的所有连接.

        Args:
            user_id: 用户ID
            message: 消息内容
        """
        if user_id not in self.active_connections:
            return

        disconnected = []

        for symbol_id in self.active_connections[user_id]:
            for websocket in self.active_connections[user_id][symbol_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"广播消息失败: {e}")
                    disconnected.append((websocket, user_id, symbol_id))

        # 移除断开的连接
        for ws, uid, sid in disconnected:
            await self.disconnect(ws, uid, sid)

    async def send_heartbeat(self):
        """
        发送心跳消息到所有连接.
        """
        heartbeat_msg = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        }

        for user_id in list(self.active_connections.keys()):
            await self.broadcast_to_user(user_id, heartbeat_msg)

    async def push_realtime_data(self, symbol_id: str, data: Dict[str, Any]):
        """
        推送实时行情数据.

        Args:
            symbol_id: 标的ID
            data: 行情数据
        """
        message = {
            "type": "realtime_data",
            "symbol_id": symbol_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_symbol(symbol_id, message)

    async def push_kline_update(self, symbol_id: str, kline_data: Dict[str, Any]):
        """
        推送K线更新数据.

        Args:
            symbol_id: 标的ID
            kline_data: K线数据
        """
        message = {
            "type": "kline_update",
            "symbol_id": symbol_id,
            "data": kline_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_symbol(symbol_id, message)

    async def push_indicator_update(self, symbol_id: str, indicator_data: Dict[str, Any]):
        """
        推送指标更新数据.

        Args:
            symbol_id: 标的ID
            indicator_data: 指标数据
        """
        message = {
            "type": "indicator_update",
            "symbol_id": symbol_id,
            "data": indicator_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_symbol(symbol_id, message)

    def get_connection_count(self) -> int:
        """
        获取当前连接总数.
        """
        count = 0
        for user_id in self.active_connections:
            for symbol_id in self.active_connections[user_id]:
                count += len(self.active_connections[user_id][symbol_id])
        return count

    def get_user_symbols(self, user_id: str) -> list:
        """
        获取用户订阅的标的列表.

        Args:
            user_id: 用户ID

        Returns:
            标的ID列表
        """
        if user_id not in self.active_connections:
            return []
        return list(self.active_connections[user_id].keys())


# 全局WebSocket管理器实例
ws_manager = WebSocketManager()


async def websocket_handler(websocket: Any, user_id: str):
    """
    WebSocket消息处理函数.

    Args:
        websocket: WebSocket连接对象
        user_id: 用户ID
    """
    current_symbol_id = None

    try:
        # 连接建立
        logger.info(f"WebSocket连接建立: user={user_id}")

        # 接收消息循环
        while True:
            try:
                # 接收消息
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "subscribe":
                    # 订阅标的
                    symbol_id = data.get("symbol_id")
                    if symbol_id:
                        # 如果之前订阅了其他标的，先取消
                        if current_symbol_id:
                            await ws_manager.disconnect(websocket, user_id, current_symbol_id)

                        # 注册新订阅
                        await ws_manager.connect(websocket, user_id, symbol_id)
                        current_symbol_id = symbol_id

                        # 发送订阅成功消息
                        await ws_manager.send_message(websocket, {
                            "type": "subscribe_success",
                            "symbol_id": symbol_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })

                elif message_type == "unsubscribe":
                    # 取消订阅
                    symbol_id = data.get("symbol_id") or current_symbol_id
                    if symbol_id:
                        await ws_manager.disconnect(websocket, user_id, symbol_id)
                        current_symbol_id = None

                        await ws_manager.send_message(websocket, {
                            "type": "unsubscribe_success",
                            "timestamp": datetime.utcnow().isoformat()
                        })

                elif message_type == "heartbeat_response":
                    # 心跳响应，忽略
                    pass

                elif message_type == "ping":
                    # Ping消息，返回Pong
                    await ws_manager.send_message(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })

                else:
                    # 未知消息类型
                    logger.warning(f"未知WebSocket消息类型: {message_type}")
                    await ws_manager.send_message(websocket, {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })

            except json.JSONDecodeError:
                logger.error("WebSocket消息JSON解析失败")
                await ws_manager.send_message(websocket, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })

            except Exception as e:
                logger.error(f"WebSocket消息处理错误: {e}")
                break

    except Exception as e:
        logger.error(f"WebSocket连接错误: {e}")

    finally:
        # 清理连接
        if current_symbol_id:
            await ws_manager.disconnect(websocket, user_id, current_symbol_id)
        else:
            await ws_manager.disconnect_all(websocket)

        logger.info(f"WebSocket连接关闭: user={user_id}")


async def start_heartbeat_task():
    """
    启动心跳任务.
    """
    ws_manager.is_running = True

    while ws_manager.is_running:
        try:
            await ws_manager.send_heartbeat()
            await asyncio.sleep(ws_manager.heartbeat_interval)
        except Exception as e:
            logger.error(f"心跳任务错误: {e}")
            await asyncio.sleep(5)


async def stop_heartbeat_task():
    """
    停止心跳任务.
    """
    ws_manager.is_running = False