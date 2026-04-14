<template>
  <div class="period-jumper">
    <!-- 跳转按钮 -->
    <el-tooltip content="跳转到短周期查看详情" placement="top">
      <el-button
        v-if="canJump"
        size="small"
        type="primary"
        @click="handleJump"
        :disabled="!selectedRange"
      >
        <el-icon><Bottom /></el-icon>
        跳转详情
      </el-button>
    </el-tooltip>

    <!-- 跳转目标周期选择 -->
    <el-select
      v-if="canJump"
      v-model="targetPeriod"
      size="small"
      style="width: 100px; margin-left: 8px;"
    >
      <el-option
        v-for="option in jumpOptions"
        :key="option.value"
        :label="option.label"
        :value="option.value"
        :disabled="!option.available"
      />
    </el-select>

    <!-- 跳转信息提示 -->
    <div v-if="selectedRange && showJumpInfo" class="jump-info">
      <div class="jump-info-row">
        <span class="label">选中区间:</span>
        <span class="value">{{ selectedRange.startDate }} ~ {{ selectedRange.endDate }}</span>
      </div>
      <div class="jump-info-row">
        <span class="label">包含天数:</span>
        <span class="value">{{ estimatedDays }}天</span>
      </div>
      <div class="jump-info-row">
        <span class="label">跳转周期:</span>
        <span class="value">{{ getPeriodTitle(targetPeriod) }}</span>
      </div>
    </div>

    <!-- 返回按钮（在短周期图表中显示） -->
    <el-tooltip content="返回上一级周期" placement="top">
      <el-button
        v-if="isJumpedView"
        size="small"
        type="default"
        @click="handleReturn"
      >
        <el-icon><Top /></el-icon>
        返回
      </el-button>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
/**
 * 周期跳转功能组件.
 *
 * 支持从长周期选中区间跳转到短周期查看详细走势.
 * 如周线选中一周跳转到日线查看该周的日K详情.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, computed, watch } from 'vue'
import { Bottom, Top } from '@element-plus/icons-vue'

// Props定义
interface Props {
  /** 当前周期 */
  currentPeriod: string
  /** 选中的时间范围 */
  selectedRange?: {
    startDate: string
    endDate: string
    startIndex: number
    endIndex: number
  }
  /** 是否已跳转视图 */
  isJumpedView?: boolean
  /** 可跳转的周期列表 */
  availablePeriods?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  currentPeriod: 'daily',
  selectedRange: undefined,
  isJumpedView: false,
  availablePeriods: () => ['daily', 'weekly', 'monthly', '60', '30', '15', '5', '1']
})

// Emits定义
const emit = defineEmits<{
  (e: 'jump', data: {
    targetPeriod: string
    startDate: string
    endDate: string
    sourcePeriod: string
  }): void
  (e: 'return'): void
}>()

// 状态
const targetPeriod = ref<string>('')
const showJumpInfo = ref<boolean>(false)

// 周期等级映射（用于判断跳转方向）
const periodLevel: Record<string, number> = {
  'monthly': 3,
  'weekly': 2,
  'daily': 1,
  '60': 0.6,
  '30': 0.5,
  '15': 0.4,
  '5': 0.2,
  '1': 0.1
}

// 周期标题映射
const periodTitles: Record<string, string> = {
  'monthly': '月K',
  'weekly': '周K',
  'daily': '日K',
  '60': '60分钟',
  '30': '30分钟',
  '15': '15分钟',
  '5': '5分钟',
  '1': '1分钟'
}

// 获取周期标题
const getPeriodTitle = (period: string): string => {
  return periodTitles[period] || period
}

// 是否可以跳转（当前周期级别大于目标周期）
const canJump = computed(() => {
  const currentLevel = periodLevel[props.currentPeriod] || 1
  // 只有日线及以上周期可以跳转
  return currentLevel >= 1 && !props.isJumpedView
})

// 可跳转的目标周期选项
const jumpOptions = computed(() => {
  const currentLevel = periodLevel[props.currentPeriod] || 1

  const options: Array<{ value: string; label: string; available: boolean }> = []

  // 根据当前周期决定可跳转的目标周期
  if (props.currentPeriod === 'monthly') {
    // 月线可跳转到周线或日线
    options.push({ value: 'weekly', label: '周K', available: true })
    options.push({ value: 'daily', label: '日K', available: true })
  } else if (props.currentPeriod === 'weekly') {
    // 周线可跳转到日线
    options.push({ value: 'daily', label: '日K', available: true })
  } else if (props.currentPeriod === 'daily') {
    // 日线可跳转到60分钟、30分钟等
    options.push({ value: '60', label: '60分钟', available: true })
    options.push({ value: '30', label: '30分钟', available: true })
    options.push({ value: '15', label: '15分钟', available: true })
  }

  return options
})

// 估算包含天数
const estimatedDays = computed(() => {
  if (!props.selectedRange) return 0

  const start = new Date(props.selectedRange.startDate)
  const end = new Date(props.selectedRange.endDate)

  const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))

  // 根据周期类型调整估算
  if (props.currentPeriod === 'monthly') {
    return diffDays + 1 // 月份包含的天数
  } else if (props.currentPeriod === 'weekly') {
    return Math.min(diffDays + 1, 7) // 一周最多7天
  } else if (props.currentPeriod === 'daily') {
    return 1 // 日线跳转到分钟线，一天
  }

  return diffDays + 1
})

// 初始化默认目标周期
watch(() => jumpOptions.value, (options) => {
  if (options.length > 0 && !targetPeriod.value) {
    targetPeriod.value = options[0].value
  }
}, { immediate: true })

// 显示跳转信息
watch(() => props.selectedRange, (range) => {
  if (range && canJump.value) {
    showJumpInfo.value = true
  } else {
    showJumpInfo.value = false
  }
})

// 处理跳转
const handleJump = () => {
  if (!props.selectedRange || !targetPeriod.value) return

  emit('jump', {
    targetPeriod: targetPeriod.value,
    startDate: props.selectedRange.startDate,
    endDate: props.selectedRange.endDate,
    sourcePeriod: props.currentPeriod
  })
}

// 处理返回
const handleReturn = () => {
  emit('return')
}
</script>

<style scoped>
.period-jumper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.jump-info {
  background: var(--fdas-bg-card);
  border: 1px solid var(--fdas-border-light);
  border-radius: 4px;
  padding: 8px 12px;
  margin-left: 8px;
  font-size: 12px;
}

.jump-info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.jump-info-row:last-child {
  margin-bottom: 0;
}

.label {
  color: var(--fdas-text-muted);
  margin-right: 8px;
}

.value {
  color: var(--fdas-text-primary);
  font-weight: 500;
}
</style>