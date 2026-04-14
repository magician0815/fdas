<template>
  <div class="custom-indicator-panel">
    <!-- 指标列表 -->
    <div class="indicator-list">
      <div class="list-header">
        <span class="header-title">自定义指标</span>
        <el-button size="small" type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建
        </el-button>
      </div>
      <div class="list-content">
        <div
          v-for="indicator in customIndicators"
          :key="indicator.id"
          class="indicator-item"
          :class="{ active: selectedIndicator?.id === indicator.id }"
          @click="selectIndicator(indicator)"
        >
          <div class="item-info">
            <span class="item-name">{{ indicator.name }}</span>
            <span class="item-formula">{{ indicator.formula.substring(0, 30) }}...</span>
          </div>
          <div class="item-actions">
            <el-button size="small" text @click.stop="editIndicator(indicator)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" text @click.stop="deleteIndicator(indicator)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
        <div v-if="customIndicators.length === 0" class="empty-list">
          <span>暂无自定义指标</span>
        </div>
      </div>
    </div>

    <!-- 创建/编辑指标对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingIndicator ? '编辑指标' : '创建指标'"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="indicator-form">
        <!-- 指标名称 -->
        <div class="form-item">
          <label class="form-label">指标名称</label>
          <el-input v-model="formData.name" placeholder="如：自定义均线" maxlength="50" />
        </div>

        <!-- 指标公式 -->
        <div class="form-item">
          <label class="form-label">计算公式</label>
          <el-input
            v-model="formData.formula"
            type="textarea"
            :rows="4"
            placeholder="如：MA(CLOSE, 10) 或 (HIGH + LOW) / 2"
          />
          <div class="formula-hints">
            <span class="hint-title">可用变量：</span>
            <span class="hint-item">OPEN, CLOSE, HIGH, LOW, VOLUME</span>
            <span class="hint-title">可用函数：</span>
            <span class="hint-item">MA(数组,周期), EMA(数组,周期), MAX(数组), MIN(数组), ABS(值), REF(数组,偏移)</span>
          </div>
        </div>

        <!-- 显示参数 -->
        <div class="form-item">
          <label class="form-label">显示颜色</label>
          <el-color-picker v-model="formData.color" show-alpha />
        </div>

        <div class="form-item">
          <label class="form-label">线条宽度</label>
          <el-slider v-model="formData.lineWidth" :min="1" :max="5" :step="1" show-stops />
        </div>

        <div class="form-item">
          <label class="form-label">显示类型</label>
          <el-radio-group v-model="formData.displayType">
            <el-radio label="line">线条</el-radio>
            <el-radio label="histogram">柱状图</el-radio>
            <el-radio label="dots">散点</el-radio>
          </el-radio-group>
        </div>

        <!-- 公式预览 -->
        <div class="form-item">
          <label class="form-label">公式预览</label>
          <div class="preview-result">
            <div v-if="formulaError" class="preview-error">
              <el-icon><Warning /></el-icon>
              {{ formulaError }}
            </div>
            <div v-else-if="previewData.length > 0" class="preview-chart">
              <span>计算成功，生成 {{ previewData.length }} 个数据点</span>
            </div>
            <div v-else class="preview-empty">
              输入公式后点击预览按钮
            </div>
          </div>
          <el-button size="small" @click="previewFormula">预览计算</el-button>
        </div>
      </div>

      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="saveIndicator" :disabled="!formData.formula || formulaError">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 函数参考文档 -->
    <el-collapse class="function-reference">
      <el-collapse-item title="函数参考" name="functions">
        <div class="reference-content">
          <div class="function-group">
            <h4>统计函数</h4>
            <table class="function-table">
              <tr><td><code>MA(arr, n)</code></td><td>简单移动平均，n周期</td></tr>
              <tr><td><code>EMA(arr, n)</code></td><td>指数移动平均，n周期</td></tr>
              <tr><td><code>SMA(arr, n, m)</code></td><td>平滑移动平均，权重m</td></tr>
              <tr><td><code>MAX(arr)</code></td><td>数组最大值</td></tr>
              <tr><td><code>MIN(arr)</code></td><td>数组最小值</td></tr>
              <tr><td><code>SUM(arr, n)</code></td><td>n周期求和</td></tr>
              <tr><td><code>AVG(arr, n)</code></td><td>n周期平均值</td></tr>
            </table>
          </div>
          <div class="function-group">
            <h4>数学函数</h4>
            <table class="function-table">
              <tr><td><code>ABS(x)</code></td><td>绝对值</td></tr>
              <tr><td><code>SQRT(x)</code></td><td>平方根</td></tr>
              <tr><td><code>POW(x, n)</code></td><td>x的n次方</td></tr>
              <tr><td><code>LOG(x)</code></td><td>自然对数</td></tr>
              <tr><td><code>ROUND(x, n)</code></td><td>四舍五入到n位小数</td></tr>
            </table>
          </div>
          <div class="function-group">
            <h4>引用函数</h4>
            <table class="function-table">
              <tr><td><code>REF(arr, n)</code></td><td>引用n周期前的值</td></tr>
              <tr><td><code>PREV(arr)</code></td><td>上一个周期的值</td></tr>
              <tr><td><code>FIRST(arr)</code></td><td>首个值</td></tr>
              <tr><td><code>LAST(arr)</code></td><td>最后值</td></tr>
            </table>
          </div>
          <div class="function-group">
            <h4>逻辑函数</h4>
            <table class="function-table">
              <tr><td><code>IF(cond, a, b)</code></td><td>条件判断</td></tr>
              <tr><td><code>CROSS(a, b)</code></td><td>a上穿b返回1，否则0</td></tr>
              <tr><td><code>CROSSDOWN(a, b)</code></td><td>a下穿b返回1，否则0</td></tr>
              <tr><td><code>BETWEEN(x, a, b)</code></td><td>x在a和b之间返回1</td></tr>
            </table>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
/**
 * 自定义指标计算器组件.
 *
 * 用户可以输入公式创建自定义指标，支持常用数学和统计函数.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, reactive, computed, watch } from 'vue'
import { Plus, Edit, Delete, Warning } from '@element-plus/icons-vue'

// Props定义
interface Props {
  /** K线数据（用于计算指标） */
  klineData?: Array<{
    date: string
    open: number | string
    high: number | string
    low: number | string
    close: number | string
    volume?: number | string
  }>
}

const props = withDefaults(defineProps<Props>(), {
  klineData: () => []
})

// Emits定义
const emit = defineEmits<{
  (e: 'indicatorCreated', indicator: CustomIndicator): void
  (e: 'indicatorUpdated', indicator: CustomIndicator): void
  (e: 'indicatorDeleted', indicatorId: string): void
  (e: 'indicatorSelected', indicator: CustomIndicator): void
}>()

// 自定义指标类型
interface CustomIndicator {
  id: string
  name: string
  formula: string
  color: string
  lineWidth: number
  displayType: 'line' | 'histogram' | 'dots'
  createdAt: number
}

// 状态
const showCreateDialog = ref<boolean>(false)
const selectedIndicator = ref<CustomIndicator | null>(null)
const editingIndicator = ref<CustomIndicator | null>(null)
const formulaError = ref<string>('')
const previewData = ref<number[]>([])

// 自定义指标列表（从localStorage加载）
const customIndicators = ref<CustomIndicator[]>([])

// 表单数据
const formData = reactive({
  name: '',
  formula: '',
  color: '#FF6B6B',
  lineWidth: 2,
  displayType: 'line' as 'line' | 'histogram' | 'dots'
})

// 初始化
const initCustomIndicators = () => {
  const saved = localStorage.getItem('fdas_custom_indicators')
  if (saved) {
    try {
      customIndicators.value = JSON.parse(saved)
    } catch {
      customIndicators.value = []
    }
  }
}

// 保存到localStorage
const saveToStorage = () => {
  localStorage.setItem('fdas_custom_indicators', JSON.stringify(customIndicators.value))
}

// 选择指标
const selectIndicator = (indicator: CustomIndicator) => {
  selectedIndicator.value = indicator
  emit('indicatorSelected', indicator)
}

// 编辑指标
const editIndicator = (indicator: CustomIndicator) => {
  editingIndicator.value = indicator
  formData.name = indicator.name
  formData.formula = indicator.formula
  formData.color = indicator.color
  formData.lineWidth = indicator.lineWidth
  formData.displayType = indicator.displayType
  showCreateDialog.value = true
}

// 删除指标
const deleteIndicator = (indicator: CustomIndicator) => {
  customIndicators.value = customIndicators.value.filter(i => i.id !== indicator.id)
  saveToStorage()
  emit('indicatorDeleted', indicator.id)

  if (selectedIndicator.value?.id === indicator.id) {
    selectedIndicator.value = null
  }
}

// 取消编辑
const cancelEdit = () => {
  showCreateDialog.value = false
  editingIndicator.value = null
  formData.name = ''
  formData.formula = ''
  formData.color = '#FF6B6B'
  formData.lineWidth = 2
  formData.displayType = 'line'
  formulaError.value = ''
  previewData.value = []
}

// 预览公式计算
const previewFormula = () => {
  if (!formData.formula || props.klineData.length < 20) {
    formulaError.value = '缺少公式或数据不足'
    return
  }

  try {
    const result = calculateIndicator(formData.formula, props.klineData)
    previewData.value = result.slice(-10) // 显示最近10个数据点
    formulaError.value = ''
  } catch (e: any) {
    formulaError.value = e.message || '公式计算错误'
    previewData.value = []
  }
}

// 计算指标
const calculateIndicator = (formula: string, data: any[]): number[] => {
  // 准备数据变量
  const OPEN = data.map(d => parseFloat(d.open) || 0)
  const CLOSE = data.map(d => parseFloat(d.close) || 0)
  const HIGH = data.map(d => parseFloat(d.high) || 0)
  const LOW = data.map(d => parseFloat(d.low) || 0)
  const VOLUME = data.map(d => parseFloat(d.volume) || 0)

  // 定义可用函数
  const functions = {
    // 统计函数
    MA: (arr: number[], period: number): number[] => {
      return arr.map((_, i) => {
        if (i < period - 1) return 0
        const slice = arr.slice(i - period + 1, i + 1)
        return slice.reduce((a, b) => a + b, 0) / period
      })
    },
    EMA: (arr: number[], period: number): number[] => {
      const k = 2 / (period + 1)
      const result: number[] = [arr[0]]
      for (let i = 1; i < arr.length; i++) {
        result.push(arr[i] * k + result[i - 1] * (1 - k))
      }
      return result
    },
    MAX: (arr: number[]): number => Math.max(...arr),
    MIN: (arr: number[]): number => Math.min(...arr),
    SUM: (arr: number[], period: number): number[] => {
      return arr.map((_, i) => {
        const slice = arr.slice(Math.max(0, i - period + 1), i + 1)
        return slice.reduce((a, b) => a + b, 0)
      })
    },
    AVG: (arr: number[], period: number): number[] => {
      return arr.map((_, i) => {
        const slice = arr.slice(Math.max(0, i - period + 1), i + 1)
        return slice.reduce((a, b) => a + b, 0) / slice.length
      })
    },

    // 数学函数
    ABS: (x: number): number => Math.abs(x),
    SQRT: (x: number): number => Math.sqrt(x),
    POW: (x: number, n: number): number => Math.pow(x, n),
    LOG: (x: number): number => Math.log(x),
    ROUND: (x: number, n: number): number => Math.round(x * Math.pow(10, n)) / Math.pow(10, n),

    // 引用函数
    REF: (arr: number[], offset: number): number[] => {
      return arr.map((_, i) => arr[Math.max(0, i - offset)] || 0)
    },
    PREV: (arr: number[]): number[] => {
      return arr.map((_, i) => arr[Math.max(0, i - 1)] || 0)
    },
    FIRST: (arr: number[]): number => arr[0] || 0,
    LAST: (arr: number[]): number => arr[arr.length - 1] || 0,

    // 逻辑函数
    IF: (cond: boolean, a: any, b: any): any => cond ? a : b,
    CROSS: (a: number[], b: number[]): number[] => {
      return a.map((v, i) => {
        if (i === 0) return 0
        return (a[i - 1] <= b[i - 1] && v > b[i]) ? 1 : 0
      })
    },
    CROSSDOWN: (a: number[], b: number[]): number[] => {
      return a.map((v, i) => {
        if (i === 0) return 0
        return (a[i - 1] >= b[i - 1] && v < b[i]) ? 1 : 0
      })
    },
    BETWEEN: (x: number, a: number, b: number): boolean => x >= a && x <= b
  }

  // 创建计算环境
  const env = { OPEN, CLOSE, HIGH, LOW, VOLUME, ...functions }

  // 解析并执行公式
  // 注意：这是一个简化实现，实际应该使用更安全的表达式解析器
  try {
    // 基本安全检查
    const forbiddenPatterns = /[;{}()]|eval|Function|constructor/
    if (forbiddenPatterns.test(formula)) {
      throw new Error('公式包含不安全字符')
    }

    // 计算公式（简化实现）
    // 实际应使用表达式解析器如mathjs
    const result = eval(formula.replace(/CLOSE/g, 'CLOSE').replace(/OPEN/g, 'OPEN').replace(/HIGH/g, 'HIGH').replace(/LOW/g, 'LOW').replace(/VOLUME/g, 'VOLUME'))

    return Array.isArray(result) ? result : [result]
  } catch (e: any) {
    throw new Error(`公式计算失败: ${e.message}`)
  }
}

// 保存指标
const saveIndicator = () => {
  if (!formData.formula || formulaError.value) return

  const indicator: CustomIndicator = {
    id: editingIndicator.value?.id || `indicator_${Date.now()}`,
    name: formData.name || '自定义指标',
    formula: formData.formula,
    color: formData.color,
    lineWidth: formData.lineWidth,
    displayType: formData.displayType,
    createdAt: editingIndicator.value?.createdAt || Date.now()
  }

  if (editingIndicator.value) {
    // 更新现有指标
    const index = customIndicators.value.findIndex(i => i.id === editingIndicator.value!.id)
    if (index !== -1) {
      customIndicators.value[index] = indicator
      emit('indicatorUpdated', indicator)
    }
  } else {
    // 创建新指标
    customIndicators.value.push(indicator)
    emit('indicatorCreated', indicator)
  }

  saveToStorage()
  cancelEdit()
}

// 初始化
initCustomIndicators()
</script>

<style scoped>
.custom-indicator-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 12px;
}

.indicator-list {
  background: var(--fdas-bg-card);
  border-radius: 8px;
  padding: 12px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.list-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.indicator-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.indicator-item:hover {
  background: var(--fdas-bg-secondary);
}

.indicator-item.active {
  background: var(--fdas-primary-light);
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.item-formula {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.item-actions {
  display: flex;
  gap: 4px;
}

.empty-list {
  padding: 20px;
  text-align: center;
  color: var(--fdas-text-muted);
}

.indicator-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.formula-hints {
  font-size: 12px;
  color: var(--fdas-text-muted);
  padding: 8px;
  background: var(--fdas-bg-secondary);
  border-radius: 4px;
}

.hint-title {
  font-weight: 500;
}

.hint-item {
  display: inline-block;
  margin-right: 8px;
}

.preview-result {
  padding: 12px;
  background: var(--fdas-bg-secondary);
  border-radius: 4px;
}

.preview-error {
  color: var(--fdas-color-down);
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-chart {
  color: var(--fdas-color-up);
}

.preview-empty {
  color: var(--fdas-text-muted);
}

.function-reference {
  background: var(--fdas-bg-card);
  border-radius: 8px;
}

.reference-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
}

.function-group h4 {
  font-size: 13px;
  font-weight: 500;
  color: var(--fdas-text-primary);
  margin-bottom: 8px;
}

.function-table {
  width: 100%;
  border-collapse: collapse;
}

.function-table td {
  padding: 4px 8px;
  font-size: 12px;
  border-bottom: 1px solid var(--fdas-border-light);
}

.function-table td:first-child {
  color: var(--fdas-primary);
}

.function-table td:last-child {
  color: var(--fdas-text-muted);
}
</style>