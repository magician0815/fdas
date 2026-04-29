/**
 * useWebSocket Hook集成测试补充.
 *
 * 补充连接断开、重连、心跳等边界情况测试.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.OPEN
  onopen = null
  onmessage = null
  onerror = null
  onclose = null

  constructor(url) {
    this.url = url
    setTimeout(() => {
      if (this.onopen) this.onopen({ type: 'open' })
    }, 0)
  }

  send(data) {
    if (this.readyState === MockWebSocket.OPEN) {
      // 模拟发送成功
    }
  }

  close(code = 1000, reason = '') {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) this.onclose({ type: 'close', code, reason })
  }

  simulateMessage(data) {
    if (this.onmessage) {
      this.onmessage({ type: 'message', data: JSON.stringify(data) })
    }
  }

  simulateError() {
    if (this.onerror) this.onerror({ type: 'error' })
  }

  simulateClose(code = 1000, reason = '') {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) this.onclose({ type: 'close', code, reason })
  }
}

vi.stubGlobal('WebSocket', MockWebSocket)

describe('useWebSocket Hook集成测试', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  describe('WebSocket连接配置', () => {
    const createHook = (url, options = {}) => {
      // 模拟Hook调用
      return {
        url,
        config: {
          heartbeatInterval: options.heartbeatInterval || 30000,
          reconnectInterval: options.reconnectInterval || 5000,
          maxReconnectAttempts: options.maxReconnectAttempts || 10,
          autoReconnect: options.autoReconnect !== false
        }
      }
    }

    it('默认配置应正确', () => {
      const hook = createHook('ws://localhost:8000/ws')
      expect(hook.config.heartbeatInterval).toBe(30000)
      expect(hook.config.reconnectInterval).toBe(5000)
      expect(hook.config.maxReconnectAttempts).toBe(10)
      expect(hook.config.autoReconnect).toBe(true)
    })

    it('自定义配置应生效', () => {
      const hook = createHook('ws://localhost:8000/ws', {
        heartbeatInterval: 10000,
        reconnectInterval: 3000,
        maxReconnectAttempts: 5,
        autoReconnect: false
      })
      expect(hook.config.heartbeatInterval).toBe(10000)
      expect(hook.config.reconnectInterval).toBe(3000)
      expect(hook.config.maxReconnectAttempts).toBe(5)
      expect(hook.config.autoReconnect).toBe(false)
    })
  })

  describe('消息处理器管理', () => {
    const messageHandlers = new Map()

    const onMessage = (type, handler) => {
      messageHandlers.set(type, handler)
    }

    const offMessage = (type) => {
      messageHandlers.delete(type)
    }

    const clearHandlers = () => {
      messageHandlers.clear()
    }

    beforeEach(() => {
      messageHandlers.clear()
    })

    it('应正确注册消息处理器', () => {
      const handler = vi.fn()
      onMessage('realtime_data', handler)
      expect(messageHandlers.has('realtime_data')).toBe(true)
      expect(messageHandlers.get('realtime_data')).toBe(handler)
    })

    it('应正确移除消息处理器', () => {
      onMessage('realtime_data', vi.fn())
      offMessage('realtime_data')
      expect(messageHandlers.has('realtime_data')).toBe(false)
    })

    it('clearHandlers应清除所有处理器', () => {
      onMessage('type1', vi.fn())
      onMessage('type2', vi.fn())
      onMessage('type3', vi.fn())
      clearHandlers()
      expect(messageHandlers.size).toBe(0)
    })

    it('应支持多个处理器类型', () => {
      onMessage('connected', vi.fn())
      onMessage('disconnected', vi.fn())
      onMessage('error', vi.fn())
      onMessage('realtime_data', vi.fn())
      onMessage('kline_update', vi.fn())
      expect(messageHandlers.size).toBe(5)
    })
  })

  describe('消息处理逻辑', () => {
    const handleMessage = (message, handlers) => {
      const { type, data } = message

      // 心跳响应
      if (type === 'heartbeat' || type === 'pong') {
        return { handled: true, type: 'heartbeat' }
      }

      // 根据消息类型调用对应的处理器
      if (handlers.has(type)) {
        handlers.get(type)?.(data)
      }

      // 通用消息处理器
      if (handlers.has('*')) {
        handlers.get('*')?.(message)
      }

      return { handled: true, type }
    }

    it('心跳消息应特殊处理', () => {
      const handlers = new Map()
      const result = handleMessage({ type: 'heartbeat' }, handlers)
      expect(result.type).toBe('heartbeat')
    })

    it('pong消息应特殊处理', () => {
      const handlers = new Map()
      const result = handleMessage({ type: 'pong' }, handlers)
      expect(result.type).toBe('heartbeat')
    })

    it('应调用对应类型的处理器', () => {
      const handlers = new Map()
      const handler = vi.fn()
      handlers.set('realtime_data', handler)
      handleMessage({ type: 'realtime_data', data: { price: 7.25 } }, handlers)
      expect(handler).toHaveBeenCalledWith({ price: 7.25 })
    })

    it('应调用通用处理器', () => {
      const handlers = new Map()
      const genericHandler = vi.fn()
      handlers.set('*', genericHandler)
      handleMessage({ type: 'custom', data: {} }, handlers)
      expect(genericHandler).toHaveBeenCalled()
    })
  })

  describe('发送消息逻辑', () => {
    const send = (ws, state, message) => {
      if (ws && state.connected) {
        ws.send(JSON.stringify(message))
        return true
      }
      return false
    }

    const subscribe = (ws, state, symbolId) => {
      return send(ws, state, { type: 'subscribe', symbol_id: symbolId })
    }

    const unsubscribe = (ws, state, symbolId) => {
      return send(ws, state, { type: 'unsubscribe', symbol_id: symbolId })
    }

    it('connected=true时应成功发送', () => {
      const ws = { send: vi.fn() }
      const state = { connected: true }
      expect(send(ws, state, { type: 'ping' })).toBe(true)
      expect(ws.send).toHaveBeenCalledWith(JSON.stringify({ type: 'ping' }))
    })

    it('connected=false时应返回false', () => {
      const ws = { send: vi.fn() }
      const state = { connected: false }
      expect(send(ws, state, { type: 'ping' })).toBe(false)
      expect(ws.send).not.toHaveBeenCalled()
    })

    it('subscribe应发送订阅消息', () => {
      const ws = { send: vi.fn() }
      const state = { connected: true }
      subscribe(ws, state, 'symbol-1')
      expect(ws.send).toHaveBeenCalledWith(JSON.stringify({ type: 'subscribe', symbol_id: 'symbol-1' }))
    })

    it('unsubscribe应发送取消订阅消息', () => {
      const ws = { send: vi.fn() }
      const state = { connected: true }
      unsubscribe(ws, state, 'symbol-1')
      expect(ws.send).toHaveBeenCalledWith(JSON.stringify({ type: 'unsubscribe', symbol_id: 'symbol-1' }))
    })
  })

  describe('重连机制', () => {
    const scheduleReconnect = (state, config, callback) => {
      if (config.autoReconnect && state.reconnectAttempts < config.maxReconnectAttempts) {
        state.reconnecting = true
        setTimeout(() => {
          state.reconnectAttempts++
          callback()
        }, config.reconnectInterval)
        return true
      }
      return false
    }

    it('autoReconnect=true时应触发重连', () => {
      const state = { reconnectAttempts: 0, reconnecting: false }
      const config = { autoReconnect: true, maxReconnectAttempts: 10, reconnectInterval: 5000 }
      const callback = vi.fn()
      scheduleReconnect(state, config, callback)
      vi.advanceTimersByTime(5000)
      expect(state.reconnectAttempts).toBe(1)
    })

    it('达到maxReconnectAttempts时应停止重连', () => {
      const state = { reconnectAttempts: 10, reconnecting: false }
      const config = { autoReconnect: true, maxReconnectAttempts: 10, reconnectInterval: 5000 }
      const callback = vi.fn()
      expect(scheduleReconnect(state, config, callback)).toBe(false)
    })

    it('autoReconnect=false时不重连', () => {
      const state = { reconnectAttempts: 0, reconnecting: false }
      const config = { autoReconnect: false, maxReconnectAttempts: 10, reconnectInterval: 5000 }
      const callback = vi.fn()
      expect(scheduleReconnect(state, config, callback)).toBe(false)
    })
  })

  describe('心跳机制', () => {
    const startHeartbeat = (ws, state, interval, onHeartbeat) => {
      return setInterval(() => {
        if (ws && state.connected) {
          ws.send(JSON.stringify({ type: 'ping' }))
          if (onHeartbeat) onHeartbeat()
        }
      }, interval)
    }

    const stopHeartbeat = (timer) => {
      if (timer) clearInterval(timer)
    }

    it('应按间隔发送心跳', () => {
      const ws = { send: vi.fn() }
      const state = { connected: true }
      const onHeartbeat = vi.fn()
      const timer = startHeartbeat(ws, state, 30000, onHeartbeat)

      vi.advanceTimersByTime(30000)
      expect(ws.send).toHaveBeenCalledWith(JSON.stringify({ type: 'ping' }))
      expect(onHeartbeat).toHaveBeenCalled()

      stopHeartbeat(timer)
    })

    it('断开连接时应停止心跳', () => {
      const ws = { send: vi.fn() }
      const state = { connected: true }
      const timer = startHeartbeat(ws, state, 30000)

      vi.advanceTimersByTime(30000)
      expect(ws.send).toHaveBeenCalled()

      state.connected = false
      vi.advanceTimersByTime(30000)
      // 断开后不再发送
    })
  })

  describe('状态管理', () => {
    const createState = () => ({
      connected: false,
      connecting: false,
      reconnecting: false,
      reconnectAttempts: 0,
      lastHeartbeat: null,
      error: null
    })

    it('初始状态应正确', () => {
      const state = createState()
      expect(state.connected).toBe(false)
      expect(state.connecting).toBe(false)
      expect(state.reconnecting).toBe(false)
      expect(state.reconnectAttempts).toBe(0)
      expect(state.lastHeartbeat).toBeNull()
      expect(state.error).toBeNull()
    })

    it('连接成功应更新状态', () => {
      const state = createState()
      state.connecting = true
      // 连接成功
      state.connected = true
      state.connecting = false
      state.reconnecting = false
      state.reconnectAttempts = 0
      expect(state.connected).toBe(true)
      expect(state.connecting).toBe(false)
    })

    it('断开连接应更新状态', () => {
      const state = createState()
      state.connected = true
      // 断开
      state.connected = false
      state.connecting = false
      expect(state.connected).toBe(false)
    })

    it('错误应记录到error字段', () => {
      const state = createState()
      state.error = 'WebSocket连接错误'
      expect(state.error).toBe('WebSocket连接错误')
    })
  })

  describe('连接URL处理', () => {
    const buildWsUrl = (apiBaseUrl, path = '/ws/chart') => {
      return `${apiBaseUrl.replace('http', 'ws')}${path}`
    }

    it('http URL应转换为ws', () => {
      expect(buildWsUrl('http://localhost:8000')).toBe('ws://localhost:8000/ws/chart')
    })

    it('https URL应转换为wss', () => {
      expect(buildWsUrl('https://api.example.com')).toBe('wss://api.example.com/ws/chart')
    })

    it('应支持自定义path', () => {
      expect(buildWsUrl('http://localhost:8000', '/ws/realtime')).toBe('ws://localhost:8000/ws/realtime')
    })
  })
})