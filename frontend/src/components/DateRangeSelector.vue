<template>
  <div class="date-range-selector">
    <el-date-picker
      v-model="startDate"
      type="date"
      placeholder="开始日期"
      :disabled-date="disabledStartDate"
      format="YYYY-MM-DD"
      value-format="YYYY-MM-DD"
      class="date-picker"
    />
    <span class="separator">至</span>
    <el-date-picker
      v-model="endDate"
      type="date"
      placeholder="结束日期"
      :disabled-date="disabledEndDate"
      format="YYYY-MM-DD"
      value-format="YYYY-MM-DD"
      class="date-picker"
    />
    <span class="days-count" v-if="daysCount > 0">
      共 {{ daysCount }} 天
    </span>
  </div>
</template>

<script setup>
/**
 * 日期范围选择器组件.
 *
 * 提供两个日期选择器，自动计算日期范围天数.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 */
import { computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [null, null]
  },
  minDate: {
    type: [Date, String],
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

// 开始日期
const startDate = computed({
  get: () => props.modelValue?.[0] || null,
  set: (val) => {
    emit('update:modelValue', [val, endDate.value])
    emit('change', [val, endDate.value])
  }
})

// 结束日期
const endDate = computed({
  get: () => props.modelValue?.[1] || null,
  set: (val) => {
    emit('update:modelValue', [startDate.value, val])
    emit('change', [startDate.value, val])
  }
})

// 计算天数
const daysCount = computed(() => {
  if (startDate.value && endDate.value) {
    const start = new Date(startDate.value)
    const end = new Date(endDate.value)
    return Math.floor((end - start) / (1000 * 60 * 60 * 24)) + 1
  }
  return 0
})

// 禁用的开始日期
const disabledStartDate = (date) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // 不能超过今天
  if (date > today) return true

  // 不能早于最小日期
  if (props.minDate) {
    const min = props.minDate instanceof Date ? props.minDate : new Date(props.minDate)
    if (date < min) return true
  }

  // 不能晚于结束日期（如果有）
  if (endDate.value) {
    const end = new Date(endDate.value)
    if (date > end) return true
  }

  return false
}

// 禁用的结束日期
const disabledEndDate = (date) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // 不能超过今天
  if (date > today) return true

  // 不能早于开始日期（如果有）
  if (startDate.value) {
    const start = new Date(startDate.value)
    if (date < start) return true
  }

  return false
}
</script>

<style scoped>
.date-range-selector {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
}

.date-picker {
  width: 140px;
}

.separator {
  color: var(--fdas-text-muted);
}

.days-count {
  font-size: 12px;
  color: var(--fdas-primary);
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(45, 90, 247, 0.1);
}
</style>