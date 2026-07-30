<template>
  <div class="macro-calc">
    <h2 class="page-title">指标测算</h2>

    <!-- 规则选择 -->
    <div class="rule-selector">
      <span class="selector-label">测算规则：</span>
      <el-select v-model="selectedRule" placeholder="选择规则" @change="loadRule" style="width: 320px">
        <el-option v-for="r in rules" :key="r.rule_code" :label="r.rule_name" :value="r.rule_code" />
      </el-select>
      <el-button type="primary" @click="execute" :loading="calculating" style="margin-left: 12px">
        执行测算
      </el-button>
    </div>

    <!-- 规则信息 -->
    <div class="rule-info" v-if="rule">
      <h3>{{ rule.rule_name }}</h3>
      <p class="desc">{{ rule.description }}</p>
      <div class="formula-box">
        <span class="formula-label">公式：</span>
        <span ref="formulaEl" class="formula"></span>
      </div>
    </div>

    <!-- 计算结果 -->
    <div class="result-section" v-if="result">
      <div class="result-header">
        <span class="result-label">计算结果：</span>
        <span class="result-value">FFR_BA = {{ result.result_value }}%</span>
        <span class="result-period">（期间：{{ formatPeriod(result.result_period) }}）</span>
      </div>

      <!-- 变量取值明细 -->
      <h4>变量取值明细</h4>
      <el-table :data="variableTable" stripe size="small" class="detail-table" style="width: 100%">
        <el-table-column prop="var" label="变量" width="100" />
        <el-table-column prop="label" label="名称" width="160" />
        <el-table-column prop="source" label="数据源" width="170" />
        <el-table-column prop="period" label="期间" width="130" />
        <el-table-column prop="value" label="取值" />
      </el-table>

      <!-- 计算过程 -->
      <h4>计算过程</h4>
      <div class="steps" v-if="result.calculation_process">
        <div v-for="s in result.calculation_process.steps" :key="s.step" class="step-row">
          <span class="step-num">{{ s.step }}.</span>
          <span class="step-desc">{{ s.description }}</span>
          <span class="step-eq">{{ s.formula }} = {{ s.result }}</span>
        </div>
      </div>
    </div>

    <!-- 历史记录 -->
    <div class="history-section" v-if="history.length > 0">
      <h4>历史记录</h4>
      <el-table :data="history" stripe size="small" style="width: 100%">
        <el-table-column prop="result_value" label="结果" width="100">
          <template #default="{row}">{{ row.result_value }}%</template>
        </el-table-column>
        <el-table-column label="期间" width="130">
          <template #default="{row}">{{ row.result_period }}</template>
        </el-table-column>
        <el-table-column label="计算时间" width="180">
          <template #default="{row}">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="变量快照" min-width="300">
          <template #default="{row}">
            <span v-for="(v,k) in row.variable_snapshot" :key="k" class="snapshot-tag">
              {{ k }}={{ v.value }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import { listCalcRules, getCalcRule, executeCalc, queryCalcResults } from '@/api/macro'

const rules = ref([])
const selectedRule = ref('BALANCED_APPROACH')
const rule = ref(null)
const result = ref(null)
const calculating = ref(false)
const history = ref([])
const formulaEl = ref(null)

const loadRule = async () => {
  try {
    const res = await getCalcRule(selectedRule.value)
    rule.value = res.data
    nextTick(() => renderFormula())
  } catch (e) {
    ElMessage.error('加载规则失败')
  }
}

const renderFormula = () => {
  if (!formulaEl.value || !rule.value) return
  try {
    katex.render(rule.value.formula_latex, formulaEl.value, { throwOnError: false, displayMode: true })
  } catch {}
}

const execute = async () => {
  calculating.value = true
  try {
    const res = await executeCalc(selectedRule.value)
    result.value = res
    ElMessage.success(`计算完成: FFR_BA = ${res.result_value}%`)
    loadHistory()
  } catch (e) {
    ElMessage.error('计算失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    calculating.value = false
  }
}

const loadHistory = async () => {
  try {
    const res = await queryCalcResults({ rule_code: selectedRule.value, limit: 10 })
    history.value = res.data || []
  } catch {}
}

const variableTable = computed(() => {
  if (!result.value) return []
  const labels = {
    R_LR_t: '长期自然利率', PI_t: '核心PCE通胀率', PI_STAR: '目标通胀率',
    Y_t: '实际GDP', Y_P_t: '潜在GDP'
  }
  return Object.entries(result.value.variable_snapshot).map(([k,v]) => ({
    var: k, label: labels[k] || k, source: v.source || '-',
    period: v.period || '-', value: typeof v.value === 'number' ? v.value.toFixed(4) : v.value
  }))
})

const formatPeriod = (p) => {
  if (!p) return '-'
  const d = new Date(p)
  const y = d.getFullYear()
  const m = d.getMonth() + 1
  const q = Math.ceil(m / 3)
  return `${y}年Q${q}`
}

const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : '-'

onMounted(async () => {
  try {
    const res = await listCalcRules()
    rules.value = res.data || []
    if (rules.value.length > 0) {
      selectedRule.value = rules.value[0].rule_code
      await loadRule()
      await loadHistory()
    }
  } catch {}
})
</script>

<style scoped>
.macro-calc { padding: 24px; }
.page-title { font-size: 22px; font-weight: 600; color: #e2e8f0; margin: 0 0 24px 0; }
.rule-selector { display: flex; align-items: center; margin-bottom: 20px; }
.selector-label { color: #a0aec0; margin-right: 8px; font-size: 14px; }
.rule-info { background: var(--fdas-card-bg); border: 1px solid var(--fdas-border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.rule-info h3 { color: #e2e8f0; margin: 0 0 8px; font-size: 18px; }
.desc { color: #a0aec0; font-size: 13px; margin-bottom: 12px; }
.formula-box { background: #1a202c; border-radius: 8px; padding: 16px; overflow-x: auto; }
.formula-label { color: #718096; font-size: 12px; margin-right: 8px; }
.formula { color: #e2e8f0; }
.result-section { background: var(--fdas-card-bg); border: 1px solid var(--fdas-border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.result-header { margin-bottom: 16px; }
.result-label { color: #a0aec0; font-size: 14px; }
.result-value { color: #48bb78; font-size: 24px; font-weight: 700; margin: 0 8px; }
.result-period { color: #718096; font-size: 13px; }
h4 { color: #e2e8f0; font-size: 15px; margin: 16px 0 10px; }
.detail-table { margin-bottom: 8px; }
.steps { background: #1a202c; border-radius: 8px; padding: 16px; }
.step-row { padding: 4px 0; color: #e2e8f0; font-size: 14px; line-height: 1.8; }
.step-num { color: #718096; margin-right: 8px; }
.step-desc { color: #a0aec0; margin-right: 8px; }
.step-eq { color: #e2e8f0; font-family: monospace; }
.history-section { margin-top: 24px; }
.snapshot-tag { display: inline-block; background: #2d3748; color: #a0aec0; padding: 1px 6px; border-radius: 4px; margin: 2px; font-size: 12px; }
</style>
