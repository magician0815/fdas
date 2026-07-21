/**
 * KLineChart 键盘快捷键管理.
 *
 * 封装所有键盘操作，映射到 KLineChart API 调用.
 *
 * **重要**: 必须在 Vue 组件的 `setup()` 或 `<script setup>` 中调用，
 * 不能在普通 TS 模块或 Pinia store 中使用（依赖 onMounted/onUnmounted 生命周期）.
 */

import type { Chart } from 'klinecharts'
import { onMounted, onUnmounted } from 'vue'

// 快捷键常量
const ZOOM_STEP = 0.9
const ZOOM_STEP_REVERSE = 1.1
const FAST_JUMP_STEP = 10
const OFFSET_RIGHT_CONTINUOUS = 80
const OFFSET_RIGHT_DEFAULT = 50

export interface KeyboardNavOptions {
  enableReset?: boolean
  enableLockCursor?: boolean
  enableCursorMove?: boolean
  enableCopyImage?: boolean
  enableVerticalZoom?: boolean
}

/**
 * 绑定键盘快捷键到 KLineChart 实例.
 * 必须在 setup() 中调用.
 *
 * 注意: cursorLocked 状态在 composable 内部维护，
 * 如果用户通过鼠标操作解除 KLineChart 锁定，此状态不会同步。
 * KLineChart v10 当前未提供锁定状态查询 API。
 */
export function useKeyboardNav(
  chart: () => Chart | null,
  options: KeyboardNavOptions = {}
): void {
  const {
    enableReset = true,
    enableLockCursor = true,
    enableCursorMove = true,
    enableCopyImage = true,
  } = options

  let cursorLocked = false
  let cursorIndex = 0

  function handleKeyDown(e: KeyboardEvent): void {
    const c = chart()
    if (!c) return

    const tag = (e.target as HTMLElement)?.tagName
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return

    switch (e.key) {
      case 'Escape':
        if (enableReset) {
          e.preventDefault()
          c.scrollToRealTime()
          cursorLocked = false
        }
        break

      case ' ':
        if (enableLockCursor) {
          e.preventDefault()
          cursorLocked = !cursorLocked
        }
        break

      case 'ArrowLeft':
        if (enableCursorMove && cursorLocked) {
          e.preventDefault()
          const step = e.ctrlKey ? FAST_JUMP_STEP : 1
          cursorIndex = Math.max(0, cursorIndex - step)
          c.scrollByDistance(-step)
        }
        break

      case 'ArrowRight':
        if (enableCursorMove && cursorLocked) {
          e.preventDefault()
          const step = e.ctrlKey ? FAST_JUMP_STEP : 1
          cursorIndex += step
          c.scrollByDistance(step)
        }
        break

      case 'ArrowUp':
        if (enableCursorMove) {
          e.preventDefault()
          c.zoomAtCoordinate(ZOOM_STEP, { x: window.innerWidth / 2, y: 0 })
        }
        break

      case 'ArrowDown':
        if (enableCursorMove) {
          e.preventDefault()
          c.zoomAtCoordinate(ZOOM_STEP_REVERSE, { x: window.innerWidth / 2, y: 0 })
        }
        break

      case 'c':
      case 'C':
        if (enableCopyImage && (e.ctrlKey || e.metaKey)) {
          e.preventDefault()
          const canvas = (c as any).getCanvas?.()
          if (canvas) {
            canvas.toBlob?.((blob: Blob | null) => {
              if (blob) {
                navigator.clipboard?.write?.([
                  new ClipboardItem({ 'image/png': blob }),
                ])
              }
            })
          }
        }
        break

      case 'Delete':
      case 'Backspace':
        break
    }
  }

  onMounted(() => window.addEventListener('keydown', handleKeyDown))
  onUnmounted(() => window.removeEventListener('keydown', handleKeyDown))
}

export { ZOOM_STEP, OFFSET_RIGHT_CONTINUOUS, OFFSET_RIGHT_DEFAULT }
