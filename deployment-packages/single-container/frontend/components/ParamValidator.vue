<template>
  <div class="param-validator">
    <!-- 校验状态指示器 -->
    <div class="validator-header" :class="statusClass">
      <el-icon class="status-icon">
        <CircleCheck v-if="isValid" />
        <Warning v-else-if="hasWarnings" />
        <CircleClose v-else />
      </el-icon>
      <span class="status-text">{{ statusText }}</span>
    </div>

    <!-- 错误列表 -->
    <div class="errors-list" v-if="errors.length > 0">
      <div class="error-item" v-for="(error, index) in errors" :key="index">
        <el-icon class="error-icon"><CircleClose /></el-icon>
        <span class="error-text">{{ error }}</span>
      </div>
    </div>

    <!-- 警告列表 -->
    <div class="warnings-list" v-if="warnings.length > 0">
      <div class="warning-item" v-for="(warning, index) in warnings" :key="index">
        <el-icon class="warning-icon"><Warning /></el-icon>
        <span class="warning-text">{{ warning }}</span>
      </div>
    </div>

    <!-- 信息展示 -->
    <div class="info-list" v-if="infoItems.length > 0">
      <div class="info-item" v-for="(item, index) in infoItems" :key="index">
        <el-icon class="info-icon"><InfoFilled /></el-icon>
        <span class="info-text">{{ item }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 参数校验显示组件.
 *
 * 显示校验结果、错误、警告和信息.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 */
import { computed } from 'vue'
import { CircleCheck, CircleClose, Warning, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  result: {
    type: Object,
    default: () => ({
      valid: true,
      errors: [],
      warnings: [],
      info: {}
    })
  }
})

// 是否有效
const isValid = computed(() => props.result?.valid ?? true)

// 是否有警告
const hasWarnings = computed(() => (props.result?.warnings?.length ?? 0) > 0)

// 错误列表
const errors = computed(() => props.result?.errors ?? [])

// 警告列表
const warnings = computed(() => props.result?.warnings ?? [])

// 信息项列表
const infoItems = computed(() => {
  const info = props.result?.info ?? {}
  return Object.entries(info).map(([key, value]) => {
    // 格式化显示
    if (key === 'estimated_records' || key === 'estimated_days') {
      return value
    }
    if (key === 'symbol_name') {
      return `标的名称: ${value}`
    }
    if (key === 'symbol_code') {
      return `标的代码: ${value}`
    }
    if (key === 'cron_desc') {
      return value
    }
    return `${key}: ${value}`
  })
})

// 状态样式类
const statusClass = computed(() => {
  if (errors.value.length > 0) return 'error'
  if (warnings.value.length > 0) return 'warning'
  return 'success'
})

// 状态文本
const statusText = computed(() => {
  if (errors.value.length > 0) return `校验失败: ${errors.value.length} 个错误`
  if (warnings.value.length > 0) return `校验通过（有${warnings.value.length}个警告）`
  return '校验通过'
})
</script>

<style scoped>
.param-validator {
  padding: var(--fdas-spacing-md);
  border-radius: var(--fdas-radius-md);
  background: var(--fdas-gray-50);
}

.validator-header {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
  margin-bottom: var(--fdas-spacing-sm);
}

.validator-header.success {
  color: var(--fdas-success);
}

.validator-header.warning {
  color: var(--fdas-warning);
}

.validator-header.error {
  color: var(--fdas-danger);
}

.status-icon {
  font-size: 20px;
}

.status-text {
  font-size: 14px;
  font-weight: 500;
}

.errors-list,
.warnings-list,
.info-list {
  display: flex;
  flex-direction: column;
  gap: var(--fdas-spacing-xs);
  margin-top: var(--fdas-spacing-sm);
}

.error-item,
.warning-item,
.info-item {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-xs);
  padding: var(--fdas-spacing-xs) var(--fdas-spacing-sm);
  border-radius: 4px;
}

.error-item {
  background: rgba(239, 68, 68, 0.1);
  color: var(--fdas-danger);
}

.warning-item {
  background: rgba(245, 158, 11, 0.1);
  color: var(--fdas-warning);
}

.info-item {
  background: rgba(45, 90, 247, 0.1);
  color: var(--fdas-primary);
}

.error-icon,
.warning-icon,
.info-icon {
  font-size: 16px;
}

.error-text,
.warning-text,
.info-text {
  font-size: 13px;
}
</style>