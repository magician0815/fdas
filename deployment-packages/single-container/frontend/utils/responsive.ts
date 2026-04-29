/**
 * 移动端响应式工具函数.
 *
 * 提供设备检测、响应式布局、触摸交互等功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'

// 设备类型枚举
export enum DeviceType {
  MOBILE = 'mobile',      // 手机（宽度 < 768px）
  TABLET = 'tablet',      // 平板（768px - 1024px）
  DESKTOP = 'desktop'     // 桌面（宽度 >= 1024px）
}

// 触摸类型枚举
export enum TouchAction {
  TAP = 'tap',            // 单击
  DOUBLE_TAP = 'double_tap', // 双击
  LONG_PRESS = 'long_press', // 长按
  SWIPE_LEFT = 'swipe_left',
  SWIPE_RIGHT = 'swipe_right',
  SWIPE_UP = 'swipe_up',
  SWIPE_DOWN = 'swipe_down',
  PINCH_IN = 'pinch_in',  // 缩小
  PINCH_OUT = 'pinch_out' // 放大
}

/**
 * 设备检测Hook.
 */
export function useDeviceDetection() {
  const screenWidth = ref<number>(window.innerWidth)
  const screenHeight = ref<number>(window.innerHeight)
  const isTouchDevice = ref<boolean>(false)

  // 设备类型
  const deviceType = computed<DeviceType>(() => {
    const width = screenWidth.value
    if (width < 768) {
      return DeviceType.MOBILE
    } else if (width < 1024) {
      return DeviceType.TABLET
    } else {
      return DeviceType.DESKTOP
    }
  })

  // 是否移动端
  const isMobile = computed<boolean>(() => {
    return deviceType.value === DeviceType.MOBILE
  })

  // 是否平板
  const isTablet = computed<boolean>(() => {
    return deviceType.value === DeviceType.TABLET
  })

  // 是否桌面端
  const isDesktop = computed<boolean>(() => {
    return deviceType.value === DeviceType.DESKTOP
  })

  // 屏幕方向
  const orientation = computed<'portrait' | 'landscape'>(() => {
    return screenWidth.value < screenHeight.value ? 'portrait' : 'landscape'
  })

  // 检测触摸设备
  const checkTouchDevice = () => {
    isTouchDevice.value = 'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      // @ts-ignore
      navigator.msMaxTouchPoints > 0
  }

  // 更新屏幕尺寸
  const updateScreenSize = () => {
    screenWidth.value = window.innerWidth
    screenHeight.value = window.innerHeight
  }

  // 监听窗口变化
  const handleResize = () => {
    updateScreenSize()
  }

  onMounted(() => {
    checkTouchDevice()
    updateScreenSize()
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })

  return {
    screenWidth,
    screenHeight,
    deviceType,
    isMobile,
    isTablet,
    isDesktop,
    isTouchDevice,
    orientation
  }
}

/**
 * 触摸交互Hook.
 */
export function useTouchInteraction(elementRef: any) {
  const touchStartPos = ref<{ x: number; y: number } | null>(null)
  const touchEndPos = ref<{ x: number; y: number } | null>(null)
  const touchStartTime = ref<number>(0)
  const touchEndTime = ref<number>(0)
  const lastTapTime = ref<number>(0)
  const isLongPress = ref<boolean>(false)

  // 触摸事件处理器
  const touchHandlers = new Map<TouchAction, (data: any) => void>()

  // 注册触摸处理器
  const registerTouchHandler = (action: TouchAction, handler: (data: any) => void) => {
    touchHandlers.set(action, handler)
  }

  // 移除触摸处理器
  const removeTouchHandler = (action: TouchAction) => {
    touchHandlers.delete(action)
  }

  // 触摸开始
  const handleTouchStart = (e: TouchEvent) => {
    if (e.touches.length === 1) {
      touchStartPos.value = {
        x: e.touches[0].clientX,
        y: e.touches[0].clientY
      }
      touchStartTime.value = Date.now()

      // 检测长按（500ms）
      setTimeout(() => {
        if (touchStartPos.value && !touchEndPos.value) {
          isLongPress.value = true
          if (touchHandlers.has(TouchAction.LONG_PRESS)) {
            touchHandlers.get(TouchAction.LONG_PRESS)?.({
              position: touchStartPos.value,
              duration: 500
            })
          }
        }
      }, 500)
    }
  }

  // 触摸结束
  const handleTouchEnd = (e: TouchEvent) => {
    if (e.changedTouches.length === 1) {
      touchEndPos.value = {
        x: e.changedTouches[0].clientX,
        y: e.changedTouches[0].clientY
      }
      touchEndTime.value = Date.now()

      if (touchStartPos.value && !isLongPress.value) {
        const deltaX = touchEndPos.value.x - touchStartPos.value.x
        const deltaY = touchEndPos.value.y - touchStartPos.value.y
        const duration = touchEndTime.value - touchStartTime.value
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)

        // 判断触摸类型
        if (distance < 10 && duration < 300) {
          // 点击
          const now = Date.now()
          if (now - lastTapTime.value < 300) {
            // 双击
            if (touchHandlers.has(TouchAction.DOUBLE_TAP)) {
              touchHandlers.get(TouchAction.DOUBLE_TAP)?.({
                position: touchEndPos.value
              })
            }
          } else {
            // 单击
            if (touchHandlers.has(TouchAction.TAP)) {
              touchHandlers.get(TouchAction.TAP)?.({
                position: touchEndPos.value
              })
            }
          }
          lastTapTime.value = now
        } else if (distance > 50) {
          // 滑动
          if (Math.abs(deltaX) > Math.abs(deltaY)) {
            // 水平滑动
            if (deltaX > 0) {
              if (touchHandlers.has(TouchAction.SWIPE_RIGHT)) {
                touchHandlers.get(TouchAction.SWIPE_RIGHT)?.({ deltaX, deltaY })
              }
            } else {
              if (touchHandlers.has(TouchAction.SWIPE_LEFT)) {
                touchHandlers.get(TouchAction.SWIPE_LEFT)?.({ deltaX, deltaY })
              }
            }
          } else {
            // 垂直滑动
            if (deltaY > 0) {
              if (touchHandlers.has(TouchAction.SWIPE_DOWN)) {
                touchHandlers.get(TouchAction.SWIPE_DOWN)?.({ deltaX, deltaY })
              }
            } else {
              if (touchHandlers.has(TouchAction.SWIPE_UP)) {
                touchHandlers.get(TouchAction.SWIPE_UP)?.({ deltaX, deltaY })
              }
            }
          }
        }
      }

      // 重置状态
      touchStartPos.value = null
      touchEndPos.value = null
      isLongPress.value = false
    }
  }

  // 双指缩放
  let pinchStartDistance = 0

  const handleTouchMove = (e: TouchEvent) => {
    if (e.touches.length === 2) {
      const touch1 = e.touches[0]
      const touch2 = e.touches[1]
      const distance = Math.sqrt(
        Math.pow(touch1.clientX - touch2.clientX, 2) +
        Math.pow(touch1.clientY - touch2.clientY, 2)
      )

      if (pinchStartDistance === 0) {
        pinchStartDistance = distance
      } else {
        const scale = distance / pinchStartDistance
        if (scale < 0.9) {
          if (touchHandlers.has(TouchAction.PINCH_IN)) {
            touchHandlers.get(TouchAction.PINCH_IN)?.({ scale })
          }
        } else if (scale > 1.1) {
          if (touchHandlers.has(TouchAction.PINCH_OUT)) {
            touchHandlers.get(TouchAction.PINCH_OUT)?.({ scale })
          }
        }
      }
    }
  }

  // 绑定事件
  const bindEvents = () => {
    const element = elementRef.value
    if (element) {
      element.addEventListener('touchstart', handleTouchStart, { passive: true })
      element.addEventListener('touchend', handleTouchEnd, { passive: true })
      element.addEventListener('touchmove', handleTouchMove, { passive: true })
    }
  }

  // 解绑事件
  const unbindEvents = () => {
    const element = elementRef.value
    if (element) {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchend', handleTouchEnd)
      element.removeEventListener('touchmove', handleTouchMove)
    }
  }

  onMounted(() => {
    bindEvents()
  })

  onUnmounted(() => {
    unbindEvents()
  })

  return {
    registerTouchHandler,
    removeTouchHandler,
    bindEvents,
    unbindEvents
  }
}

/**
 * 响应式尺寸计算Hook.
 */
export function useResponsiveSize() {
  const { deviceType, screenWidth, screenHeight } = useDeviceDetection()

  // 计算图表高度
  const chartHeight = computed<number>(() => {
    switch (deviceType.value) {
      case DeviceType.MOBILE:
        return Math.min(screenHeight.value * 0.4, 300)
      case DeviceType.TABLET:
        return Math.min(screenHeight.value * 0.5, 400)
      default:
        return 500
    }
  })

  // 计算工具栏方向
  const toolbarDirection = computed<'horizontal' | 'vertical'>(() => {
    return deviceType.value === DeviceType.MOBILE ? 'horizontal' : 'vertical'
  })

  // 计算按钮大小
  const buttonSize = computed<'small' | 'default' | 'large'>(() => {
    switch (deviceType.value) {
      case DeviceType.MOBILE:
        return 'small'
      case DeviceType.TABLET:
        return 'default'
      default:
        return 'default'
    }
  })

  // 计算字体大小
  const fontSize = computed<number>(() => {
    switch (deviceType.value) {
      case DeviceType.MOBILE:
        return 12
      case DeviceType.TABLET:
        return 14
      default:
        return 14
    }
  })

  // 计算K线宽度
  const candleWidth = computed<number>(() => {
    switch (deviceType.value) {
      case DeviceType.MOBILE:
        return 4
      case DeviceType.TABLET:
        return 6
      default:
        return 8
    }
  })

  // 计算可见K线数量
  const visibleCandleCount = computed<number>(() => {
    const width = screenWidth.value
    const candleWidthValue = candleWidth.value
    const gap = 2
    return Math.floor(width / (candleWidthValue + gap))
  })

  // 是否显示简化工具栏
  const showSimplifiedToolbar = computed<boolean>(() => {
    return deviceType.value === DeviceType.MOBILE
  })

  // 是否隐藏次要信息
  const hideSecondaryInfo = computed<boolean>(() => {
    return screenWidth.value < 480
  })

  return {
    chartHeight,
    toolbarDirection,
    buttonSize,
    fontSize,
    candleWidth,
    visibleCandleCount,
    showSimplifiedToolbar,
    hideSecondaryInfo
  }
}

/**
 * 移动端手势缩放Hook.
 *
 * 用于图表的触摸缩放操作.
 */
export function useMobileZoom(chartRef: any) {
  const scale = ref<number>(1)
  const minScale = 0.5
  const maxScale = 3

  const { registerTouchHandler } = useTouchInteraction(chartRef)

  // 放大
  const zoomIn = () => {
    scale.value = Math.min(scale.value * 1.2, maxScale)
    applyZoom()
  }

  // 缩小
  const zoomOut = () => {
    scale.value = Math.max(scale.value / 1.2, minScale)
    applyZoom()
  }

  // 应用缩放
  const applyZoom = () => {
    if (chartRef.value) {
      // 触发图表缩放
      chartRef.value?.zoom?.(scale.value)
    }
  }

  // 注册双指缩放处理器
  registerTouchHandler(TouchAction.PINCH_OUT, () => zoomIn())
  registerTouchHandler(TouchAction.PINCH_IN, () => zoomOut())

  // 双击重置
  registerTouchHandler(TouchAction.DOUBLE_TAP, () => {
    scale.value = 1
    applyZoom()
  })

  return {
    scale,
    zoomIn,
    zoomOut,
    applyZoom
  }
}

/**
 * 移动端滑动导航Hook.
 *
 * 用于图表的水平滑动切换时间范围.
 */
export function useMobileSwipe(chartRef: any, updateRange: (direction: 'left' | 'right') => void) {
  const { registerTouchHandler } = useTouchInteraction(chartRef)

  // 注册滑动处理器
  registerTouchHandler(TouchAction.SWIPE_LEFT, () => {
    updateRange('left')
  })

  registerTouchHandler(TouchAction.SWIPE_RIGHT, () => {
    updateRange('right')
  })

  return {}
}

/**
 * 检测是否为iOS设备.
 */
export function isIOS(): boolean {
  return /iPad|iPhone|iPod/.test(navigator.userAgent)
}

/**
 * 检测是否为Android设备.
 */
export function isAndroid(): boolean {
  return /Android/.test(navigator.userAgent)
}

/**
 * 获取安全区域Insets（iOS刘海屏等）.
 */
export function getSafeAreaInsets(): {
  top: number
  bottom: number
  left: number
  right: number
} {
  const style = getComputedStyle(document.documentElement)

  return {
    top: parseInt(style.getPropertyValue('--sat') || '0'),
    bottom: parseInt(style.getPropertyValue('--sab') || '0'),
    left: parseInt(style.getPropertyValue('--sal') || '0'),
    right: parseInt(style.getPropertyValue('--sar') || '0')
  }
}

/**
 * 设置CSS安全区域变量.
 */
export function setupSafeAreaCSS(): void {
  // 设置CSS变量以支持iOS安全区域
  const css = `
    :root {
      --sat: env(safe-area-inset-top);
      --sab: env(safe-area-inset-bottom);
      --sal: env(safe-area-inset-left);
      --sar: env(safe-area-inset-right);
    }
  `

  const style = document.createElement('style')
  style.textContent = css
  document.head.appendChild(style)
}