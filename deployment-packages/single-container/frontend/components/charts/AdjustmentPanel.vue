<template>
  <div class="adjustment-panel" v-if="hasAdjustment">
    <div class="panel-header">
      <span class="panel-title">复权设置</span>
      <el-button size="small" text @click="$emit('close')">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>
    <div class="panel-body">
      <div class="adjustment-options">
        <el-radio-group v-model="adjustmentType" @change="handleChange">
          <el-radio value="none">
            <span class="option-label">不复权</span>
            <span class="option-desc">显示原始价格</span>
          </el-radio>
          <el-radio value="forward">
            <span class="option-label">前复权</span>
            <span class="option-desc">当前价不变，历史价调整</span>
          </el-radio>
          <el-radio value="backward">
            <span class="option-label">后复权</span>
            <span class="option-desc">历史价不变，当前价调整</span>
          </el-radio>
        </el-radio-group>
      </div>
      <div class="adjustment-info">
        <div class="info-row">
          <span class="info-label">复权说明</span>
          <span class="info-value">
            复权可消除除权除息对K线形态的影响，使技术分析更准确
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 复权参数选择面板组件.
 *
 * 提供前复权、后复权、不复权三种模式的选择.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, watch, computed } from 'vue'
import { Close } from '@element-plus/icons-vue'
import { AdjustmentType } from '@/utils/stockUtils'

// Props定义
interface Props {
  /** 当前复权类型 */
  modelValue?: AdjustmentType
  /** 是否有复权需求（仅股票市场） */
  hasAdjustment?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: AdjustmentType.NONE,
  hasAdjustment: false
})

// Emits定义
const emit = defineEmits<{
  (e: 'update:modelValue', value: AdjustmentType): void
  (e: 'close'): void
}>()

// 本地复权类型状态
const adjustmentType = ref<AdjustmentType>(props.modelValue)

// 监听props变化
watch(() => props.modelValue, (newVal) => {
  adjustmentType.value = newVal
})

// 处理复权类型变更
const handleChange = (value: AdjustmentType) => {
  // 保存到localStorage
  localStorage.setItem('fdas_adjustment_type', value)
  emit('update:modelValue', value)
}
</script>

<style scoped>
.adjustment-panel {
  position: absolute;
  top: 50px;
  right: 80px;
  width: 220px;
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-md);
  box-shadow: var(--fdas-shadow-card);
  z-index: 20;
  border: 1px solid var(--fdas-border-light);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--fdas-border-light);
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--fdas-text-primary);
}

.panel-body {
  padding: 12px;
}

.adjustment-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.el-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.el-radio {
  display: flex;
  align-items: flex-start;
  margin-right: 0;
  padding: 8px;
  border-radius: 4px;
  background: var(--fdas-bg-hover);
  transition: background 0.2s;
}

.el-radio.is-checked {
  background: rgba(59, 130, 246, 0.1);
}

.el-radio__label {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.option-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.option-desc {
  font-size: 11px;
  color: var(--fdas-text-muted);
}

.adjustment-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--fdas-border-light);
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 11px;
  color: var(--fdas-text-muted);
}

.info-value {
  font-size: 12px;
  color: var(--fdas-text-secondary);
  line-height: 1.4;
}
</style>