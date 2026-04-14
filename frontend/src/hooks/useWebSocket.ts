/**
 * WebSocket实时数据连接Hook.
 *
 * 管理WebSocket连接、断线重连、心跳检测、消息处理.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'

// WebSocket配置
interface WebSocketConfig {
  /** WebSocket服务器URL */
  url: string
  /** 心跳间隔（毫秒） */
  heartbeatInterval?: number
  /** 重连间隔（毫秒） */
  reconnectInterval?: number
  /** 最大重连次数 */
  maxReconnectAttempts?: number
  /** 自动重连 */
  autoReconnect?: boolean
}

// WebSocket状态
interface WebSocketState {
  /** 是否已连接 */
  connected: boolean
  /** 是否正在连接 */
  connecting: boolean
  /** 是否正在重连 */
  reconnecting: boolean
  /** 重连次数 */
  reconnectAttempts: number
  /** 最后心跳时间 */
  lastHeartbeat: Date | null
  /** 连接错误 */
  error: string | null
}

// 消息类型定义
interface WSMessage {
  type: string
  symbol_id?: string
  data?: any
  timestamp?: string
  message?: string
}

/**
 * WebSocket连接Hook.
 */
export function useWebSocket(config: WebSocketConfig) {
  // 默认配置
  const defaultConfig = {
    heartbeatInterval: 30000,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    autoReconnect: true
  }

  const finalConfig = { ...defaultConfig, ...config }

  // WebSocket实例
  let ws: WebSocket | null = null

  // 状态
  const state = ref<WebSocketState>({
    connected: false,
    connecting: false,
    reconnecting: false,
    reconnectAttempts: 0,
    lastHeartbeat: null,
    error: null
  })

  // 消息处理器映射
  const messageHandlers = new Map<string, (data: any) => void>()

  // 心跳定时器
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null

  // 重连定时器
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  /**
   * 连接WebSocket.
   */
  const connect = (): void => {
    if (ws && state.value.connected) {
      return
    }

    state.value.connecting = true
    state.value.error = null

    try {
      ws = new WebSocket(finalConfig.url)

      ws.onopen = () => {
        state.value.connected = true
        state.value.connecting = false
        state.value.reconnecting = false
        state.value.reconnectAttempts = 0

        // 启动心跳
        startHeartbeat()

        // 调用连接成功回调
        if (messageHandlers.has('connected')) {
          messageHandlers.get('connected')?.({ connected: true })
        }
      }

      ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data)
          handleMessage(message)
        } catch (e) {
          console.error('WebSocket消息解析失败:', e)
        }
      }

      ws.onerror = (error) => {
        state.value.error = 'WebSocket连接错误'
        console.error('WebSocket错误:', error)

        if (messageHandlers.has('error')) {
          messageHandlers.get('error')?.({ error: '连接错误' })
        }
      }

      ws.onclose = (event) => {
        state.value.connected = false
        state.value.connecting = false

        // 停止心跳
        stopHeartbeat()

        // 调用断开连接回调
        if (messageHandlers.has('disconnected')) {
          messageHandlers.get('disconnected')?.({ code: event.code, reason: event.reason })
        }

        // 自动重连
        if (finalConfig.autoReconnect && state.value.reconnectAttempts < finalConfig.maxReconnectAttempts) {
          scheduleReconnect()
        }
      }

    } catch (error: any) {
      state.value.error = error.message
      state.value.connecting = false

      if (finalConfig.autoReconnect) {
        scheduleReconnect()
      }
    }
  }

  /**
   * 断开WebSocket连接.
   */
  const disconnect = (): void => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    stopHeartbeat()

    if (ws) {
      ws.close()
      ws = null
    }

    state.value.connected = false
    state.value.connecting = false
    state.value.reconnecting = false
  }

  /**
   * 重连WebSocket.
   */
  const reconnect = (): void => {
    state.value.reconnecting = true
    state.value.reconnectAttempts++

    connect()
  }

  /**
   * 安排重连.
   */
  const scheduleReconnect = (): void => {
    state.value.reconnecting = true

    reconnectTimer = setTimeout(() => {
      reconnect()
    }, finalConfig.reconnectInterval)
  }

  /**
   * 启动心跳.
   */
  const startHeartbeat = (): void => {
    heartbeatTimer = setInterval(() => {
      if (ws && state.value.connected) {
        ws.send(JSON.stringify({ type: 'ping' }))
        state.value.lastHeartbeat = new Date()
      }
    }, finalConfig.heartbeatInterval)
  }

  /**
   * 停止心跳.
   */
  const stopHeartbeat = (): void => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  /**
   * 处理消息.
   */
  const handleMessage = (message: WSMessage): void => {
    const { type, data, symbol_id, timestamp } = message

    // 心跳响应
    if (type === 'heartbeat' || type === 'pong') {
      state.value.lastHeartbeat = new Date()
      return
    }

    // 根据消息类型调用对应的处理器
    if (messageHandlers.has(type)) {
      messageHandlers.get(type)?.(data)
    }

    // 通用消息处理器
    if (messageHandlers.has('*')) {
      messageHandlers.get('*')?.(message)
    }
  }

  /**
   * 发送消息.
   */
  const send = (message: any): boolean => {
    if (ws && state.value.connected) {
      ws.send(JSON.stringify(message))
      return true
    }
    return false
  }

  /**
   * 订阅标的.
   */
  const subscribe = (symbolId: string): boolean => {
    return send({
      type: 'subscribe',
      symbol_id: symbolId
    })
  }

  /**
   * 取消订阅.
   */
  const unsubscribe = (symbolId?: string): boolean => {
    return send({
      type: 'unsubscribe',
      symbol_id: symbolId
    })
  }

  /**
   * 注册消息处理器.
   */
  const onMessage = (type: string, handler: (data: any) => void): void => {
    messageHandlers.set(type, handler)
  }

  /**
   * 移除消息处理器.
   */
  const offMessage = (type: string): void => {
    messageHandlers.delete(type)
  }

  /**
   * 清除所有消息处理器.
   */
  const clearHandlers = (): void => {
    messageHandlers.clear()
  }

  // 组件挂载时自动连接
  onMounted(() => {
    connect()
  })

  // 组件卸载时自动断开
  onUnmounted(() => {
    disconnect()
    clearHandlers()
  })

  return {
    // 状态
    state,

    // 方法
    connect,
    disconnect,
    reconnect,
    send,
    subscribe,
    unsubscribe,
    onMessage,
    offMessage,
    clearHandlers
  }
}

/**
 * 实时行情数据Hook.
 *
 * 使用WebSocket订阅实时行情数据并更新图表.
 */
export function useRealtimeData(symbolId: string, apiBaseUrl: string) {
  const wsUrl = `${apiBaseUrl.replace('http', 'ws')}/ws/chart`

  const { state, subscribe, unsubscribe, onMessage, offMessage } = useWebSocket({
    url: wsUrl,
    heartbeatInterval: 30000,
    autoReconnect: true
  })

  // 实时数据
  const realtimeData = ref<any>(null)

  // K线更新数据
  const klineUpdate = ref<any>(null)

  // 指标更新数据
  const indicatorUpdate = ref<any>(null)

  // 订阅标的
  watch(() => symbolId, (newId) => {
    if (state.value.connected && newId) {
      subscribe(newId)
    }
  }, { immediate: true })

  // 处理实时数据消息
  onMessage('realtime_data', (data: any) => {
    realtimeData.value = data
  })

  // 处理K线更新消息
  onMessage('kline_update', (data: any) => {
    klineUpdate.value = data
  })

  // 处理指标更新消息
  onMessage('indicator_update', (data: any) => {
    indicatorUpdate.value = data
  })

  return {
    // WebSocket状态
    wsState: state,

    // 实时数据
    realtimeData,
    klineUpdate,
    indicatorUpdate,

    // 方法
    subscribe: () => subscribe(symbolId),
    unsubscribe: () => unsubscribe(symbolId)
  }
}