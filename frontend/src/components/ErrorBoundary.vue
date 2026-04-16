<template>
  <div class="error-boundary">
    <slot v-if="!hasError" />
    <div v-else class="error-fallback">
      <el-icon class="error-icon"><WarningFilled /></el-icon>
      <h3>组件加载失败</h3>
      <p class="error-message">{{ errorMessage }}</p>
      <el-button type="primary" @click="resetError">
        重试
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Vue ErrorBoundary组件.
 *
 * 捕获子组件的错误，防止整个应用崩溃.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { ref, onErrorCaptured } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'
import logger from '@/services/logger'

// Props定义
interface Props {
  /** 自定义错误消息 */
  fallbackMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  fallbackMessage: '组件发生错误，请尝试刷新'
})

// Emits定义
const emit = defineEmits<{
  (e: 'error', error: Error): void
  (e: 'reset'): void
}>>()

// 状态
const hasError = ref(false)
const errorMessage = ref(props.fallbackMessage)

// 捕获错误
onErrorCaptured((error: Error, instance, info) => {
  logger.error('组件错误捕获', error)

  hasError.value = true
  errorMessage.value = error.message || props.fallbackMessage

  // 通知父组件
  emit('error', error)

  // 阻止错误继续传播
  return false
})

// 重置错误状态
const resetError = () => {
  hasError.value = false
  errorMessage.value = props.fallbackMessage
  emit('reset')
}
</script>

<style scoped>
.error-boundary {
  width: 100%;
  min-height: 200px;
}

.error-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background-color: var(--el-bg-color);
  border-radius: 8px;
}

.error-icon {
  font-size: 48px;
  color: var(--el-color-danger);
  margin-bottom: 16px;
}

.error-message {
  color: var(--el-text-color-secondary);
  margin-bottom: 24px;
  text-align: center;
}
</style>