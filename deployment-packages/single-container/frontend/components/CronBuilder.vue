<template>
  <div class="cron-builder">
    <!-- 执行周期类型选择 -->
    <div class="cron-type-section">
      <el-radio-group v-model="cronType" @change="updateCronExpression">
        <el-radio-button label="none">手动执行</el-radio-button>
        <el-radio-button label="daily">每天</el-radio-button>
        <el-radio-button label="weekly">每周</el-radio-button>
        <el-radio-button label="monthly">每月</el-radio-button>
        <el-radio-button label="custom">自定义</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 时间选择 -->
    <div class="time-section" v-if="cronType !== 'none' && cronType !== 'custom'">
      <span class="label">执行时间:</span>
      <el-time-select
        v-model="executeTime"
        start="00:00"
        end="23:59"
        step="00:30"
        placeholder="选择时间"
        @change="updateCronExpression"
      />
    </div>

    <!-- 星期选择（weekly模式） -->
    <div class="weekday-section" v-if="cronType === 'weekly'">
      <span class="label">执行星期:</span>
      <el-checkbox-group v-model="selectedDays" @change="updateCronExpression">
        <el-checkbox-button :label="0">周日</el-checkbox-button>
        <el-checkbox-button :label="1">周一</el-checkbox-button>
        <el-checkbox-button :label="2">周二</el-checkbox-button>
        <el-checkbox-button :label="3">周三</el-checkbox-button>
        <el-checkbox-button :label="4">周四</el-checkbox-button>
        <el-checkbox-button :label="5">周五</el-checkbox-button>
        <el-checkbox-button :label="6">周六</el-checkbox-button>
      </el-checkbox-group>
    </div>

    <!-- 日期选择（monthly模式） -->
    <div class="day-of-month-section" v-if="cronType === 'monthly'">
      <span class="label">执行日期:</span>
      <el-select v-model="dayOfMonth" placeholder="选择日期" @change="updateCronExpression">
        <el-option v-for="d in 31" :key="d" :label="`${d}日`" :value="d" />
      </el-select>
    </div>

    <!-- 自定义Cron表达式 -->
    <div class="custom-cron-section" v-if="cronType === 'custom'">
      <span class="label">Cron表达式:</span>
      <el-input
        v-model="customCron"
        placeholder="如: 0 18 * * * （每天18:00）"
        @change="updateCronExpression"
      />
    </div>

    <!-- 表达式描述 -->
    <div class="cron-desc" v-if="cronExpression">
      <el-icon><Clock /></el-icon>
      <span class="desc-text">{{ cronDescription }}</span>
    </div>

    <!-- 显示当前表达式 -->
    <div class="cron-expression" v-if="cronExpression">
      <span class="label">表达式:</span>
      <code class="expression-code">{{ cronExpression }}</code>
    </div>
  </div>
</template>

<script setup>
/**
 * Cron表达式可视化配置组件.
 *
 * 提供预设周期类型选择，自动生成Cron表达式.
 *
 * Author: FDAS Team
 * Created: 2026-04-11
 */
import { ref, computed, watch } from 'vue'
import { Clock } from '@element-plus/icons-vue'
import { describeCron } from '@/utils/validators'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

// Cron类型
const cronType = ref('none')

// 执行时间
const executeTime = ref('18:00')

// 选择的星期
const selectedDays = ref([1, 2, 3, 4, 5]) // 默认周一到周五

// 选择的日期
const dayOfMonth = ref(1)

// 自定义表达式
const customCron = ref('')

// 当前表达式
const cronExpression = computed({
  get: () => props.modelValue,
  set: (val) => {
    emit('update:modelValue', val)
    emit('change', val)
  }
})

// 表达式描述
const cronDescription = computed(() => {
  return describeCron(cronExpression.value)
})

// 更新Cron表达式
const updateCronExpression = () => {
  let expr = ''

  if (cronType.value === 'none') {
    expr = ''
  } else if (cronType.value === 'daily') {
    // 每天执行: 分 时 * * *
    const [hour, minute] = executeTime.value.split(':')
    expr = `${minute} ${hour} * * *`
  } else if (cronType.value === 'weekly') {
    // 每周执行: 分 时 * * 周
    const [hour, minute] = executeTime.value.split(':')
    const days = selectedDays.value.join(',')
    expr = `${minute} ${hour} * * ${days}`
  } else if (cronType.value === 'monthly') {
    // 每月执行: 分 时 日 * *
    const [hour, minute] = executeTime.value.split(':')
    expr = `${minute} ${hour} ${dayOfMonth.value} * *`
  } else if (cronType.value === 'custom') {
    expr = customCron.value
  }

  cronExpression.value = expr
}

// 监听外部值变化，同步内部状态
watch(() => props.modelValue, (val) => {
  if (!val) {
    cronType.value = 'none'
    return
  }

  const parts = val.split(/\s+/)
  if (parts.length !== 5) {
    cronType.value = 'custom'
    customCron.value = val
    return
  }

  const [minute, hour, dayOfMonthPart, monthPart, dayOfWeekPart] = parts

  // 判断类型
  if (dayOfMonthPart === '*' && monthPart === '*' && dayOfWeekPart === '*') {
    // 每天
    cronType.value = 'daily'
    executeTime.value = `${hour}:${minute.padStart(2, '0')}`
  } else if (dayOfMonthPart === '*' && monthPart === '*' && dayOfWeekPart !== '*') {
    // 每周
    cronType.value = 'weekly'
    executeTime.value = `${hour}:${minute.padStart(2, '0')}`
    selectedDays.value = dayOfWeekPart.split(',').map(Number)
  } else if (dayOfMonthPart !== '*' && monthPart === '*' && dayOfWeekPart === '*') {
    // 每月
    cronType.value = 'monthly'
    executeTime.value = `${hour}:${minute.padStart(2, '0')}`
    dayOfMonth.value = Number(dayOfMonthPart)
  } else {
    // 自定义
    cronType.value = 'custom'
    customCron.value = val
  }
}, { immediate: true })
</script>

<style scoped>
.cron-builder {
  display: flex;
  flex-direction: column;
  gap: var(--fdas-spacing-md);
}

.cron-type-section {
  margin-bottom: var(--fdas-spacing-sm);
}

.time-section,
.weekday-section,
.day-of-month-section,
.custom-cron-section {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
}

.label {
  font-size: 13px;
  color: var(--fdas-text-secondary);
  min-width: 70px;
}

.cron-desc {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
  padding: var(--fdas-spacing-sm) var(--fdas-spacing-md);
  background: var(--fdas-gray-50);
  border-radius: var(--fdas-radius-md);
}

.desc-text {
  font-size: 14px;
  color: var(--fdas-primary);
}

.cron-expression {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
}

.expression-code {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  padding: 4px 8px;
  background: var(--fdas-gray-100);
  border-radius: 4px;
  color: var(--fdas-text-primary);
}
</style>