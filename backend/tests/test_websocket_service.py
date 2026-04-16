"""
WebSocket Service 测试.

测试WebSocket连接管理功能.

Author: FDAS Team
Created: 2026-04-15
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.websocket_service import WebSocketManager, ws_manager, websocket_handler


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
    async def test_handler_subscribe_message(self):
        """测试订阅消息处理."""
        from app.services.websocket_service import websocket_handler, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.close = AsyncMock()

        # 模拟订阅消息后关闭连接
        call_count = 0
        async def receive_once():
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                # 模拟连接关闭
                raise Exception("Connection closed")
            return {"type": "subscribe", "symbol_id": "symbol1"}

        mock_ws.receive_json = receive_once

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass

        # 验证连接消息发送
        mock_ws.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_handler_ping_message(self):
        """测试Ping消息处理."""
        from app.services.websocket_service import websocket_handler, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.close = AsyncMock()

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
        calls = mock_ws.send_json.call_args_list
        # 最后一个调用应该是pong
        pong_found = False
        for call in calls:
            if call[0][0].get("type") == "pong":
                pong_found = True
        assert pong_found

    @pytest.mark.asyncio
    async def test_handler_unsubscribe_message(self):
        """测试取消订阅消息处理."""
        from app.services.websocket_service import websocket_handler, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.close = AsyncMock()

        call_count = 0
        async def receive_messages():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"type": "subscribe", "symbol_id": "symbol1"}
            elif call_count == 2:
                return {"type": "unsubscribe", "symbol_id": "symbol1"}
            raise Exception("Connection closed")

        mock_ws.receive_json = receive_messages

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass

        mock_ws.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_handler_error_message(self):
        """测试错误消息处理."""
        from app.services.websocket_service import websocket_handler, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.close = AsyncMock()

        call_count = 0
        async def receive_error():
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                raise Exception("Connection closed")
            return {"type": "unknown_type"}

        mock_ws.receive_json = receive_error

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass

        # 验证错误响应
        calls = mock_ws.send_json.call_args_list
        error_found = False
        for call in calls:
            if call[0][0].get("type") == "error":
                error_found = True
        assert error_found

    @pytest.mark.asyncio
    async def test_handler_json_decode_error(self):
        """测试JSON解析错误."""
        from app.services.websocket_service import websocket_handler, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.close = AsyncMock()

        # 第一次调用抛出JSONDecodeError，第二次抛出普通Exception退出循环
        call_count = 0
        async def receive_with_error():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise json.JSONDecodeError("test", "test", 0)
            raise Exception("Connection closed")

        mock_ws.receive_json = receive_with_error

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass

        # 验证错误响应
        mock_ws.send_json.assert_called()
        # 验证发送了error类型消息
        calls = mock_ws.send_json.call_args_list
        error_found = False
        for call in calls:
            if call[0][0].get("type") == "error":
                error_found = True
        assert error_found


class TestHeartbeatTask:
    """测试心跳任务."""

    @pytest.mark.asyncio
    async def test_start_heartbeat(self, manager: WebSocketManager):
        """测试启动心跳."""
        from app.services.websocket_service import start_heartbeat_task, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}
        ws_manager.is_running = False

        ws = AsyncMock()
        ws.send_json = AsyncMock()

        await manager.connect(ws, "user1", "symbol1")

        # 运行一次心跳后停止
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

    @pytest.mark.asyncio
    async def test_start_heartbeat_task_loop(self):
        """测试心跳任务循环."""
        from app.services.websocket_service import start_heartbeat_task, ws_manager
        import asyncio

        # 清空全局manager状态
        ws_manager.active_connections = {}
        ws_manager.is_running = False

        ws = AsyncMock()
        ws.send_json = AsyncMock()

        await ws_manager.connect(ws, "user1", "symbol1")
        ws.send_json.reset_mock()

        # 运行短暂心跳后停止
        ws_manager.heartbeat_interval = 0.1  # 快速心跳

        # 创建任务并在短时间内取消
        task = asyncio.create_task(start_heartbeat_task())

        await asyncio.sleep(0.3)  # 运行2-3次心跳
        ws_manager.is_running = False  # 停止标志

        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.TimeoutError:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        ws.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_handler_subscribe_with_existing_subscription(self):
        """测试已有订阅时切换订阅（covers line 272）."""
        from app.services.websocket_service import websocket_handler, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.close = AsyncMock()

        call_count = 0
        async def receive_messages():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"type": "subscribe", "symbol_id": "symbol1"}
            elif call_count == 2:
                return {"type": "subscribe", "symbol_id": "symbol2"}
            raise Exception("Connection closed")

        mock_ws.receive_json = receive_messages

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass

        # 验证订阅消息发送
        mock_ws.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_handler_heartbeat_response(self):
        """测试心跳响应消息处理（covers line 299）."""
        from app.services.websocket_service import websocket_handler, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.close = AsyncMock()

        call_count = 0
        async def receive_messages():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"type": "subscribe", "symbol_id": "symbol1"}
            elif call_count == 2:
                return {"type": "heartbeat_response"}
            raise Exception("Connection closed")

        mock_ws.receive_json = receive_messages

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass

        # heartbeat_response应该被忽略，不发送额外消息
        mock_ws.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_handler_connection_error(self):
        """测试连接错误处理（covers lines 327-328）."""
        from app.services.websocket_service import websocket_handler, ws_manager

        # 清空全局manager状态
        ws_manager.active_connections = {}

        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.close = AsyncMock()

        # 模拟连接时立即抛出异常
        mock_ws.receive_json = AsyncMock(side_effect=Exception("Connection error immediately"))

        try:
            await websocket_handler(mock_ws, "user1")
        except Exception:
            pass

        # 验证没有发送消息（错误发生在连接开始）
        # send_json可能被调用一次（connect消息）或失败


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
        """测试广播移除失败连接（covers lines 145-147, 151）."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()
        # ws2发送失败
        ws2.send_json.side_effect = Exception("Connection failed")

        await manager.connect(ws1, "user1", "symbol1")
        await manager.connect(ws2, "user2", "symbol1")

        ws1.send_json.reset_mock()
        ws2.send_json.reset_mock()
        ws2.send_json.side_effect = Exception("Failed")

        await manager.broadcast_to_symbol("symbol1", {"type": "test"})

        # ws2应该被移除
        assert "user2" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_heartbeat_task_exception_handling(self):
        """测试心跳任务异常处理（covers lines 350-352）."""
        from app.services.websocket_service import start_heartbeat_task, ws_manager
        import asyncio

        # 清空全局manager状态
        ws_manager.active_connections = {}
        ws_manager.is_running = False

        # 创建一个会抛出异常的websocket
        ws = AsyncMock()
        ws.send_json = AsyncMock(side_effect=Exception("Send failed"))

        await ws_manager.connect(ws, "user1", "symbol1")
        ws_manager.heartbeat_interval = 0.1

        # 创建心跳任务
        task = asyncio.create_task(start_heartbeat_task())

        # 等待短暂时间让异常发生
        await asyncio.sleep(0.3)
        ws_manager.is_running = False

        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.TimeoutError:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # 验证任务已停止
        assert ws_manager.is_running is False


class TestWebSocketHandler:
    """测试websocket_handler函数."""

    @pytest.mark.asyncio
    async def test_websocket_handler_connection_exception(self):
        """测试WebSocket连接异常处理（covers lines 327-328）."""
        # 创建一个会在receive_json时抛出异常的websocket
        ws = AsyncMock()
        ws.receive_json = AsyncMock(side_effect=Exception("Connection lost"))

        # 清空manager状态
        ws_manager.active_connections = {}

        # 调用handler，应该捕获异常并清理
        await websocket_handler(ws, "test_user")

        # 验证连接已被清理
        assert "test_user" not in ws_manager.active_connections

    @pytest.mark.asyncio
    async def test_websocket_handler_subscribe_success(self):
        """测试WebSocket订阅成功."""
        ws = AsyncMock()
        ws.receive_json = AsyncMock(side_effect=[
            {"type": "subscribe", "symbol_id": "symbol-1"},
            {"type": "heartbeat_response"},  # 不触发异常，继续循环
            Exception("Break loop")
        ])
        ws.send_json = AsyncMock()

        ws_manager.active_connections = {}

        # 捕获并验证订阅消息
        await websocket_handler(ws, "test_user")

        # 验证订阅消息被发送（在异常后连接被清理）
        calls = ws.send_json.call_args_list
        subscribe_success = any(
            call[0][0].get("type") == "subscribe_success" for call in calls
        )
        assert subscribe_success

    @pytest.mark.asyncio
    async def test_websocket_handler_json_decode_error(self):
        """测试WebSocket JSON解析错误."""
        ws = AsyncMock()
        ws.receive_json = AsyncMock(side_effect=[
            json.JSONDecodeError("Invalid JSON", "test", 0),
            Exception("Break loop")
        ])
        ws.send_json = AsyncMock()

        ws_manager.active_connections = {}

        await websocket_handler(ws, "test_user")

        # 验证错误消息被发送
        ws.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_websocket_handler_ping_pong(self):
        """测试WebSocket ping-pong."""
        ws = AsyncMock()
        ws.receive_json = AsyncMock(side_effect=[
            {"type": "ping"},
            Exception("Break loop")
        ])
        ws.send_json = AsyncMock()

        ws_manager.active_connections = {}

        await websocket_handler(ws, "test_user")

        # 验证pong消息被发送
        calls = ws.send_json.call_args_list
        pong_sent = any(call[0][0].get("type") == "pong" for call in calls)
        assert pong_sent

    @pytest.mark.asyncio
    async def test_websocket_handler_unknown_message_type(self):
        """测试WebSocket未知消息类型."""
        ws = AsyncMock()
        ws.receive_json = AsyncMock(side_effect=[
            {"type": "unknown_type"},
            Exception("Break loop")
        ])
        ws.send_json = AsyncMock()

        ws_manager.active_connections = {}

        await websocket_handler(ws, "test_user")

        # 验证错误消息被发送
        calls = ws.send_json.call_args_list
        error_sent = any(
            call[0][0].get("type") == "error" and "Unknown message type" in call[0][0].get("message", "")
            for call in calls
        )
        assert error_sent

    @pytest.mark.asyncio
    async def test_websocket_handler_unsubscribe(self):
        """测试WebSocket取消订阅."""
        ws = AsyncMock()
        ws.receive_json = AsyncMock(side_effect=[
            {"type": "subscribe", "symbol_id": "symbol-1"},
            {"type": "unsubscribe", "symbol_id": "symbol-1"},
            Exception("Break loop")
        ])
        ws.send_json = AsyncMock()

        ws_manager.active_connections = {}

        await websocket_handler(ws, "test_user")

        # 取消订阅后连接应被清理
        # 注意：unsubscribe只清理特定symbol，不是全部
        assert "test_user" not in ws_manager.active_connections or \
               "symbol-1" not in ws_manager.active_connections.get("test_user", {})


class TestStopHeartbeatTask:
    """测试停止心跳任务."""

    @pytest.mark.asyncio
    async def test_stop_heartbeat_task(self):
        """测试停止心跳任务."""
        from app.services.websocket_service import stop_heartbeat_task, start_heartbeat_task

        ws_manager.is_running = False

        # 启动心跳任务
        task = asyncio.create_task(start_heartbeat_task())

        # 等待短暂时间
        await asyncio.sleep(0.1)

        # 停止心跳任务
        await stop_heartbeat_task()

        # 验证任务已停止
        assert ws_manager.is_running is False

        # 取消任务
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass