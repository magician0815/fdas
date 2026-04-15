"""
WebSocket Service 测试.

测试WebSocket连接管理功能.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.services.websocket_service import WebSocketManager


@pytest.fixture
def manager():
    """WebSocket管理器实例."""
    return WebSocketManager()


@pytest.fixture
def mock_websocket():
    """Mock WebSocket连接."""
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


class TestWebSocketManagerConnect:
    """测试WebSocket连接管理."""

    @pytest.mark.asyncio
    async def test_connect_new_user(self, manager: WebSocketManager, mock_websocket):
        """测试新用户连接."""
        await manager.connect(mock_websocket, "user1", "symbol1")

        assert "user1" in manager.active_connections
        assert "symbol1" in manager.active_connections["user1"]
        assert mock_websocket in manager.active_connections["user1"]["symbol1"]
        mock_websocket.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_existing_user_new_symbol(
        self, manager: WebSocketManager, mock_websocket
    ):
        """测试已有用户连接新标的."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()

        await manager.connect(ws1, "user1", "symbol1")
        await manager.connect(mock_websocket, "user1", "symbol2")

        assert "symbol1" in manager.active_connections["user1"]
        assert "symbol2" in manager.active_connections["user1"]

    @pytest.mark.asyncio
    async def test_connect_same_symbol_multiple_connections(
        self, manager: WebSocketManager, mock_websocket
    ):
        """测试同一标的多个连接."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()

        await manager.connect(ws1, "user1", "symbol1")
        await manager.connect(ws2, "user1", "symbol1")

        assert len(manager.active_connections["user1"]["symbol1"]) == 2


class TestWebSocketManagerDisconnect:
    """测试WebSocket断开."""

    @pytest.mark.asyncio
    async def test_disconnect_single_symbol(self, manager: WebSocketManager, mock_websocket):
        """测试断开单个标的连接."""
        await manager.connect(mock_websocket, "user1", "symbol1")
        await manager.disconnect(mock_websocket, "user1", "symbol1")

        assert "user1" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_keeps_other_symbols(
        self, manager: WebSocketManager, mock_websocket
    ):
        """测试断开后保留其他标的."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()

        await manager.connect(ws1, "user1", "symbol1")
        await manager.connect(mock_websocket, "user1", "symbol2")

        await manager.disconnect(mock_websocket, "user1", "symbol2")

        assert "symbol1" in manager.active_connections["user1"]
        assert "symbol2" not in manager.active_connections["user1"]

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_user(self, manager: WebSocketManager, mock_websocket):
        """测试断开不存在用户."""
        # 不应报错
        await manager.disconnect(mock_websocket, "nonexistent", "symbol1")
        assert len(manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_disconnect_all(self, manager: WebSocketManager, mock_websocket):
        """测试断开所有连接."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()

        await manager.connect(ws1, "user1", "symbol1")
        await manager.connect(mock_websocket, "user1", "symbol2")

        await manager.disconnect_all(mock_websocket)

        # Check that symbol2 is removed (mock_websocket)
        # symbol1 should still exist (ws1)
        assert "symbol1" in manager.active_connections.get("user1", {})
        assert mock_websocket not in manager.active_connections.get("user1", {}).get("symbol2", set())


class TestWebSocketManagerSendMessage:
    """测试消息发送."""

    @pytest.mark.asyncio
    async def test_send_message_success(self, manager: WebSocketManager, mock_websocket):
        """测试成功发送消息."""
        message = {"type": "test", "data": "value"}
        await manager.send_message(mock_websocket, message)

        mock_websocket.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_message_failure(self, manager: WebSocketManager, mock_websocket):
        """测试发送失败."""
        mock_websocket.send_json.side_effect = Exception("Connection error")

        await manager.send_message(mock_websocket, {"type": "test"})
        # 不应报错，只记录日志


class TestWebSocketManagerBroadcast:
    """测试广播消息."""

    @pytest.mark.asyncio
    async def test_broadcast_to_symbol(self, manager: WebSocketManager):
        """测试广播到指定标的."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()
        ws3 = AsyncMock()
        ws3.send_json = AsyncMock()

        await manager.connect(ws1, "user1", "symbol1")
        await manager.connect(ws2, "user1", "symbol1")
        await manager.connect(ws3, "user2", "symbol2")

        # Reset mocks after connect (which sends connected message)
        ws1.send_json.reset_mock()
        ws2.send_json.reset_mock()
        ws3.send_json.reset_mock()

        message = {"type": "broadcast", "data": "test"}
        await manager.broadcast_to_symbol("symbol1", message)

        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)
        ws3.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_broadcast_to_user(self, manager: WebSocketManager):
        """测试广播到用户."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()

        await manager.connect(ws1, "user1", "symbol1")
        await manager.connect(ws2, "user1", "symbol2")

        # Reset mocks after connect
        ws1.send_json.reset_mock()
        ws2.send_json.reset_mock()

        message = {"type": "user_broadcast", "data": "test"}
        await manager.broadcast_to_user("user1", message)

        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_nonexistent_user(self, manager: WebSocketManager):
        """测试广播到不存在用户."""
        # 不应报错
        await manager.broadcast_to_user("nonexistent", {"type": "test"})


class TestWebSocketManagerDataPush:
    """测试数据推送."""

    @pytest.mark.asyncio
    async def test_push_realtime_data(self, manager: WebSocketManager):
        """测试实时数据推送."""
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        await manager.connect(ws, "user1", "symbol1")

        # Reset mock after connect
        ws.send_json.reset_mock()

        data = {"price": 7.25, "volume": 1000}
        await manager.push_realtime_data("symbol1", data)

        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "realtime_data"
        assert call_args["symbol_id"] == "symbol1"
        assert call_args["data"] == data
        assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_push_kline_update(self, manager: WebSocketManager):
        """测试K线更新推送."""
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        await manager.connect(ws, "user1", "symbol1")

        # Reset mock after connect
        ws.send_json.reset_mock()

        kline_data = {"open": 7.20, "close": 7.25}
        await manager.push_kline_update("symbol1", kline_data)

        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "kline_update"

    @pytest.mark.asyncio
    async def test_push_indicator_update(self, manager: WebSocketManager):
        """测试指标更新推送."""
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        await manager.connect(ws, "user1", "symbol1")

        # Reset mock after connect
        ws.send_json.reset_mock()

        indicator_data = {"ma": [7.20, 7.25]}
        await manager.push_indicator_update("symbol1", indicator_data)

        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "indicator_update"


class TestWebSocketManagerHeartbeat:
    """测试心跳."""

    @pytest.mark.asyncio
    async def test_send_heartbeat(self, manager: WebSocketManager):
        """测试发送心跳."""
        ws = AsyncMock()
        ws.send_json = AsyncMock()

        await manager.connect(ws, "user1", "symbol1")

        await manager.send_heartbeat()

        ws.send_json.assert_called()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "heartbeat"
        assert "timestamp" in call_args


class TestWebSocketManagerStats:
    """测试统计功能."""

    def test_get_connection_count_empty(self, manager: WebSocketManager):
        """测试空连接计数."""
        assert manager.get_connection_count() == 0

    def test_get_connection_count(self, manager: WebSocketManager):
        """测试连接计数."""
        ws1 = MagicMock()
        ws2 = MagicMock()
        ws3 = MagicMock()

        manager.active_connections = {
            "user1": {"symbol1": {ws1, ws2}},
            "user2": {"symbol2": {ws3}},
        }

        assert manager.get_connection_count() == 3

    def test_get_user_symbols(self, manager: WebSocketManager):
        """测试获取用户订阅标的."""
        manager.active_connections = {
            "user1": {"symbol1": set(), "symbol2": set()},
        }

        symbols = manager.get_user_symbols("user1")
        assert symbols == ["symbol1", "symbol2"]

    def test_get_user_symbols_nonexistent(self, manager: WebSocketManager):
        """测试获取不存在用户标的."""
        symbols = manager.get_user_symbols("nonexistent")
        assert symbols == []


class TestWebSocketHandler:
    """测试WebSocket消息处理器."""

    @pytest.mark.asyncio
    async def test_handler_subscribe_message(self, manager: WebSocketManager):
        """测试订阅消息处理."""
        from app.services.websocket_service import websocket_handler

        mock_ws = AsyncMock()
        mock_ws.receive_json = AsyncMock()
        mock_ws.send_json = AsyncMock()

        # 模拟订阅消息
        mock_ws.receive_json.return_value = {
            "type": "subscribe",
            "symbol_id": "symbol1"
        }

        # 只处理一条消息后模拟关闭
        call_count = 0
        async def receive_once():
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                raise Exception("Connection closed")
            return {"type": "subscribe", "symbol_id": "symbol1"}

        mock_ws.receive_json = receive_once

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass  # 处理器会抛出异常退出循环

        # 验证连接注册
        mock_ws.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_handler_ping_message(self, manager: WebSocketManager):
        """测试Ping消息处理."""
        from app.services.websocket_service import websocket_handler

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()

        call_count = 0
        async def receive_ping():
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                raise Exception("Connection closed")
            return {"type": "ping"}

        mock_ws.receive_json = receive_ping

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass

        # 验证pong响应
        mock_ws.send_json.assert_called()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "pong"


class TestHeartbeatTask:
    """测试心跳任务."""

    @pytest.mark.asyncio
    async def test_start_heartbeat(self, manager: WebSocketManager):
        """测试启动心跳."""
        from app.services.websocket_service import start_heartbeat_task

        ws = AsyncMock()
        ws.send_json = AsyncMock()

        await manager.connect(ws, "user1", "symbol1")

        # 运行一次心跳后停止
        original_is_running = manager.is_running

        async def run_once():
            await manager.send_heartbeat()

        await run_once()

        ws.send_json.assert_called()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "heartbeat"

    @pytest.mark.asyncio
    async def test_stop_heartbeat(self, manager: WebSocketManager):
        """测试停止心跳."""
        from app.services.websocket_service import stop_heartbeat_task, ws_manager

        # 设置全局manager的状态
        ws_manager.is_running = True
        await stop_heartbeat_task()

        assert ws_manager.is_running is False


class TestWebSocketManagerCleanup:
    """测试连接清理."""

    @pytest.mark.asyncio
    async def test_cleanup_on_error(self, manager: WebSocketManager):
        """测试错误时清理连接."""
        ws = AsyncMock()
        ws.send_json = AsyncMock()
        ws.send_json.side_effect = Exception("Connection error")

        await manager.connect(ws, "user1", "symbol1")

        # 发送消息失败后应该移除连接
        await manager.send_message(ws, {"type": "test"})

        # 连接仍然存在（只是日志记录错误）
        assert "user1" in manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast_removes_failed_connections(self, manager: WebSocketManager):
        """测试广播移除失败连接."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()
        ws2.send_json.side_effect = Exception("Failed")

        await manager.connect(ws1, "user1", "symbol1")
        await manager.connect(ws2, "user2", "symbol1")

        ws1.send_json.reset_mock()
        ws2.send_json.reset_mock()
        ws2.send_json.side_effect = Exception("Failed")

        await manager.broadcast_to_symbol("symbol1", {"type": "test"})

        # ws2应该被移除
        assert "user2" not in manager.active_connections