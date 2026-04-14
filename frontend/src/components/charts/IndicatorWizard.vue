<template>
  <el-dialog
    v-model="visible"
    title="指标设置"
    width="400px"
    :modal="false"
    @keydown="handleKeydown"
  >
    <div class="indicator-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- MA设置 -->
    <div v-if="activeTab === 'ma'" class="indicator-section">
      <div class="section-title">均线周期</div>
      <div class="period-grid">
        <button
          v-for="period in maPeriods"
          :key="period"
          class="period-btn"
          :class="{ active: selectedMA.includes(period) }"
          @click="toggleMA(period)"
        >
          MA{{ period }}
        </button>
      </div>
    </div>

    <!-- MACD设置 -->
    <div v-if="activeTab === 'macd'" class="indicator-section">
      <div class="section-title">MACD参数</div>
      <div class="param-inputs">
        <div class="param-item">
          <label>快线周期</label>
          <el-input-number
            v-model="macdParams.fast"
            :min="1"
            :max="50"
            size="small"
          />
        </div>
        <div class="param-item">
          <label>慢线周期</label>
          <el-input-number
            v-model="macdParams.slow"
            :min="1"
            :max="100"
            size="small"
          />
        </div>
        <div class="param-item">
          <label>信号线周期</label>
          <el-input-number
            v-model="macdParams.signal"
            :min="1"
            :max="50"
            size="small"
          />
        </div>
      </div>
    </div>

    <!-- VOL设置 -->
    <div v-if="activeTab === 'vol'" class="indicator-section">
      <div class="section-title">成交量均线</div>
      <div class="period-grid">
        <button
          v-for="period in volPeriods"
          :key="period"
          class="period-btn"
          :class="{ active: selectedVOL.includes(period) }"
          @click="toggleVOL(period)"
        >
          VOL{{ period }}
        </button>
      </div>
    </div>

    <div class="wizard-hint">
      <span>Tab 切换类型</span>
      <span>↑↓ 选择周期</span>
      <span>Enter 确认</span>
      <span>Esc 关闭</span>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 指标键盘精灵组件.
 *
 * 支持技术指标参数快速调整.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, computed, watch } from 'vue'

// Props定义
interface Props {
  /** 是否显示 */
  modelValue: boolean
  /** 当前MA周期 */
  maPeriods?: string[]
  /** 当前MACD参数 */
  macdParams?: { fast: number; slow: number; signal: number }
  /** 当前VOL周期 */
  volPeriods?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  maPeriods: () => ['5', '10', '20', '60'],
  macdParams: () => ({ fast: 12, slow: 26, signal: 9 }),
  volPeriods: () => ['5', '10']
})

// Emits定义
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'maChange', periods: string[]): void
  (e: 'macdChange', params: { fast: number; slow: number; signal: number }): void
  (e: 'volChange', periods: string[]): void
}>()

// Tab定义
const tabs = [
  { key: 'ma', label: 'MA' },
  { key: 'macd', label: 'MACD' },
  { key: 'vol', label: 'VOL' }
]

// 状态
const activeTab = ref<'ma' | 'macd' | 'vol'>('ma')
const selectedMA = ref<string[]>([])
const macdParams = ref({ fast: 12, slow: 26, signal: 9 })
const selectedVOL = ref<string[]>([])
const activePeriodIndex = ref(0)

// 可选周期
const maPeriods = ['5', '10', '20', '30', '60', '120']
const volPeriods = ['5', '10', '20']

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 监听显示状态，同步数据
watch(visible, (val) => {
  if (val) {
    selectedMA.value = [...props.maPeriods]
    macdParams.value = { ...props.macdParams }
    selectedVOL.value = [...props.volPeriods]
    activeTab.value = 'ma'
    activePeriodIndex.value = 0
  }
})

/**
 * 切换MA周期.
 */
const toggleMA = (period: string) => {
  const index = selectedMA.value.indexOf(period)
  if (index > -1) {
    selectedMA.value.splice(index, 1)
  } else {
    selectedMA.value.push(period)
    selectedMA.value.sort((a, b) => parseInt(a) - parseInt(b))
  }
}

/**
 * 切换VOL周期.
 */
const toggleVOL = (period: string) => {
  const index = selectedVOL.value.indexOf(period)
  if (index > -1) {
    selectedVOL.value.splice(index, 1)
  } else {
    selectedVOL.value.push(period)
    selectedVOL.value.sort((a, b) => parseInt(a) - parseInt(b))
  }
}

/**
 * 处理键盘事件.
 */
const handleKeydown = (e: KeyboardEvent) => {
  const currentPeriods = activeTab.value === 'ma' ? maPeriods : volPeriods

  if (e.key === 'Tab') {
    e.preventDefault()
    const tabIndex = tabs.findIndex(t => t.key === activeTab.value)
    const nextIndex = (tabIndex + 1) % tabs.length
    activeTab.value = tabs[nextIndex].key as 'ma' | 'macd' | 'vol'
    activePeriodIndex.value = 0
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (activeTab.value !== 'macd') {
      activePeriodIndex.value = Math.min(activePeriodIndex.value + 1, currentPeriods.length - 1)
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (activeTab.value !== 'macd') {
      activePeriodIndex.value = Math.max(activePeriodIndex.value - 1, 0)
    }
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (activeTab.value === 'ma') {
      toggleMA(maPeriods[activePeriodIndex.value])
    } else if (activeTab.value === 'vol') {
      toggleVOL(volPeriods[activePeriodIndex.value])
    } else {
      // MACD - 确认并关闭
      emit('macdChange', { ...macdParams.value })
      visible.value = false
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    visible.value = false
  }
}

/**
 * 确认并关闭.
 */
const confirmAndClose = () => {
  emit('maChange', [...selectedMA.value])
  emit('macdChange', { ...macdParams.value })
  emit('volChange', [...selectedVOL.value])
  visible.value = false
}
</script>

<style scoped>
.indicator-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab-btn {
  padding: 8px 16px;
  border-radius: 4px;
  background: var(--fdas-bg-secondary);
  border: 1px solid var(--fdas-border-light);
  color: var(--fdas-text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: var(--fdas-primary);
  color: white;
  border-color: var(--fdas-primary);
}

.indicator-section {
  padding: 12px 0;
}

.section-title {
  font-size: 13px;
  color: var(--fdas-text-muted);
  margin-bottom: 12px;
}

.period-grid {
  display: flex;
  gap: 8px;
}

.period-btn {
  padding: 8px 12px;
  border-radius: 4px;
  background: var(--fdas-bg-secondary);
  border: 1px solid var(--fdas-border-light);
  color: var(--fdas-text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.period-btn.active {
  background: var(--fdas-primary-light);
  border-color: var(--fdas-primary);
  color: var(--fdas-primary);
}

.param-inputs {
  display: flex;
  gap: 16px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.param-item label {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.wizard-hint {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--fdas-border-light);
  font-size: 12px;
  color: var(--fdas-text-muted);
}
</style>