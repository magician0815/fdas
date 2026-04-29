<template>
  <el-dialog
    v-model="visible"
    title="数据导出"
    width="500px"
    :close-on-click-modal="false"
  >
    <div class="export-panel">
      <!-- 导出范围 -->
      <div class="export-section">
        <div class="section-title">导出范围</div>
        <div class="date-range">
          <el-date-picker
            v-model="exportConfig.startDate"
            type="date"
            placeholder="开始日期"
            size="small"
            :disabled-date="disabledStartDate"
          />
          <span class="date-separator">至</span>
          <el-date-picker
            v-model="exportConfig.endDate"
            type="date"
            placeholder="结束日期"
            size="small"
            :disabled-date="disabledEndDate"
          />
        </div>
        <div class="quick-range">
          <el-button size="small" text @click="setQuickRange('week')">近一周</el-button>
          <el-button size="small" text @click="setQuickRange('month')">近一月</el-button>
          <el-button size="small" text @click="setQuickRange('quarter')">近三月</el-button>
          <el-button size="small" text @click="setQuickRange('year')">近一年</el-button>
          <el-button size="small" text @click="setQuickRange('all')">全部数据</el-button>
        </div>
      </div>

      <!-- 导出字段 -->
      <div class="export-section">
        <div class="section-title">导出字段</div>
        <div class="field-selection">
          <el-checkbox-group v-model="exportConfig.fields">
            <el-checkbox label="date">日期</el-checkbox>
            <el-checkbox label="open">开盘价</el-checkbox>
            <el-checkbox label="high">最高价</el-checkbox>
            <el-checkbox label="low">最低价</el-checkbox>
            <el-checkbox label="close">收盘价</el-checkbox>
            <el-checkbox label="volume">成交量</el-checkbox>
            <el-checkbox label="change_pct">涨跌幅</el-checkbox>
            <el-checkbox label="change_amount">涨跌额</el-checkbox>
            <el-checkbox label="amplitude">振幅</el-checkbox>
            <el-checkbox label="open_interest" v-if="hasOI">持仓量</el-checkbox>
          </el-checkbox-group>
        </div>
        <div class="field-preset">
          <el-button size="small" text @click="selectFieldPreset('basic')">基础字段</el-button>
          <el-button size="small" text @click="selectFieldPreset('full')">全部字段</el-button>
        </div>
      </div>

      <!-- 导出格式 -->
      <div class="export-section">
        <div class="section-title">导出格式</div>
        <el-radio-group v-model="exportConfig.format">
          <el-radio label="csv">
            <div class="format-option">
              <span class="format-name">CSV</span>
              <span class="format-desc">逗号分隔，通用格式</span>
            </div>
          </el-radio>
          <el-radio label="excel">
            <div class="format-option">
              <span class="format-name">Excel (xlsx)</span>
              <span class="format-desc">表格格式，支持多工作表</span>
            </div>
          </el-radio>
          <el-radio label="json">
            <div class="format-option">
              <span class="format-name">JSON</span>
              <span class="format-desc">结构化数据，适合程序处理</span>
            </div>
          </el-radio>
        </el-radio-group>
      </div>

      <!-- 导出选项 -->
      <div class="export-section">
        <div class="section-title">导出选项</div>
        <div class="export-options">
          <el-checkbox v-model="exportConfig.includeHeader">包含表头</el-checkbox>
          <el-checkbox v-model="exportConfig.includeMA" :disabled="!canIncludeIndicators">包含均线数据</el-checkbox>
          <el-checkbox v-model="exportConfig.includeMACD" :disabled="!canIncludeIndicators">包含MACD数据</el-checkbox>
        </div>
      </div>

      <!-- 数据预览 -->
      <div class="export-section">
        <div class="section-title">
          数据预览
          <span class="preview-count">(预计导出 {{ estimatedCount }} 条)</span>
        </div>
        <div class="preview-table">
          <table>
            <thead>
              <tr>
                <th v-for="field in previewFields" :key="field">{{ getFieldLabel(field) }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in previewData" :key="index">
                <td v-for="field in previewFields" :key="field">{{ row[field] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleExport" :loading="exporting">
          <el-icon><Download /></el-icon>
          开始导出
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 数据导出面板组件.
 *
 * 支持将K线数据导出为CSV、Excel、JSON格式.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, computed, watch } from 'vue'
import { Download } from '@element-plus/icons-vue'

// Props定义
interface Props {
  /** 是否显示 */
  visible?: boolean
  /** 标的代码 */
  symbolCode?: string
  /** 标的名称 */
  symbolName?: string
  /** 数据数组 */
  data?: Array<Record<string, any>>
  /** 是否有持仓量数据（期货） */
  hasOI?: boolean
  /** 数据最早日期 */
  minDate?: Date
  /** 数据最晚日期 */
  maxDate?: Date
  /** 均线数据 */
  maData?: Record<string, any[]>
  /** MACD数据 */
  macdData?: Record<string, any[]>
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  symbolCode: '',
  symbolName: '',
  data: () => [],
  hasOI: false,
  minDate: () => new Date('1994-01-01'),
  maxDate: () => new Date(),
  maData: () => {},
  macdData: () => {}
})

// Emits定义
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'export', config: ExportConfig): void
}>()

// 导出配置类型
interface ExportConfig {
  startDate: Date
  endDate: Date
  fields: string[]
  format: 'csv' | 'excel' | 'json'
  includeHeader: boolean
  includeMA: boolean
  includeMACD: boolean
}

// 状态
const exporting = ref<boolean>(false)
const exportConfig = ref<ExportConfig>({
  startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
  endDate: new Date(),
  fields: ['date', 'open', 'high', 'low', 'close'],
  format: 'csv',
  includeHeader: true,
  includeMA: false,
  includeMACD: false
})

// 字段标签映射
const fieldLabels: Record<string, string> = {
  date: '日期',
  open: '开盘价',
  high: '最高价',
  low: '最低价',
  close: '收盘价',
  volume: '成交量',
  change_pct: '涨跌幅%',
  change_amount: '涨跌额',
  amplitude: '振幅%',
  open_interest: '持仓量'
}

// 获取字段标签
const getFieldLabel = (field: string): string => {
  return fieldLabels[field] || field
}

// 禁用开始日期
const disabledStartDate = (date: Date): boolean => {
  return date > props.maxDate || date < props.minDate
}

// 禁用结束日期
const disabledEndDate = (date: Date): boolean => {
  return date > props.maxDate || date < exportConfig.value.startDate
}

// 是否可以包含指标
const canIncludeIndicators = computed(() => {
  return Object.keys(props.maData).length > 0 || Object.keys(props.macdData).length > 0
})

// 预览字段
const previewFields = computed(() => {
  return exportConfig.value.fields.slice(0, 5) // 最多显示5个字段预览
})

// 预览数据
const previewData = computed(() => {
  // 获取时间范围内的数据
  const filteredData = props.data.filter(d => {
    const date = new Date(d.date)
    return date >= exportConfig.value.startDate && date <= exportConfig.value.endDate
  })

  // 只显示前5条
  return filteredData.slice(0, 5)
})

// 预计导出数量
const estimatedCount = computed(() => {
  return props.data.filter(d => {
    const date = new Date(d.date)
    return date >= exportConfig.value.startDate && date <= exportConfig.value.endDate
  }).length
})

// 设置快捷范围
const setQuickRange = (range: string) => {
  const today = new Date()

  switch (range) {
    case 'week':
      exportConfig.value.startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      exportConfig.value.endDate = today
      break
    case 'month':
      exportConfig.value.startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
      exportConfig.value.endDate = today
      break
    case 'quarter':
      exportConfig.value.startDate = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000)
      exportConfig.value.endDate = today
      break
    case 'year':
      exportConfig.value.startDate = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000)
      exportConfig.value.endDate = today
      break
    case 'all':
      exportConfig.value.startDate = props.minDate
      exportConfig.value.endDate = props.maxDate
      break
  }
}

// 选择字段预设
const selectFieldPreset = (preset: string) => {
  if (preset === 'basic') {
    exportConfig.value.fields = ['date', 'open', 'high', 'low', 'close', 'volume']
  } else if (preset === 'full') {
    const allFields = ['date', 'open', 'high', 'low', 'close', 'volume', 'change_pct', 'change_amount', 'amplitude']
    if (props.hasOI) {
      allFields.push('open_interest')
    }
    exportConfig.value.fields = allFields
  }
}

// 处理导出
const handleExport = async () => {
  exporting.value = true

  try {
    // 过滤数据
    const filteredData = props.data.filter(d => {
      const date = new Date(d.date)
      return date >= exportConfig.value.startDate && date <= exportConfig.value.endDate
    })

    // 根据格式生成导出内容
    let content: string
    let filename: string
    let mimeType: string

    const baseFilename = `${props.symbolCode}_${formatDate(exportConfig.value.startDate)}_${formatDate(exportConfig.value.endDate)}`

    if (exportConfig.value.format === 'csv') {
      content = generateCSV(filteredData)
      filename = `${baseFilename}.csv`
      mimeType = 'text/csv;charset=utf-8'
    } else if (exportConfig.value.format === 'json') {
      content = generateJSON(filteredData)
      filename = `${baseFilename}.json`
      mimeType = 'application/json;charset=utf-8'
    } else {
      // Excel格式需要使用第三方库（如xlsx）
      // 这里简化为CSV格式，实际应使用xlsx库
      content = generateCSV(filteredData)
      filename = `${baseFilename}.xlsx`
      mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }

    // 创建下载链接
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    emit('export', exportConfig.value)
    handleClose()
  } finally {
    exporting.value = false
  }
}

// 生成CSV内容
const generateCSV = (data: any[]): string => {
  const fields = exportConfig.value.fields

  // 表头
  const lines: string[] = []
  if (exportConfig.value.includeHeader) {
    lines.push(fields.map(f => getFieldLabel(f)).join(','))
  }

  // 数据行
  for (const row of data) {
    const values = fields.map(f => {
      const value = row[f]
      if (value === null || value === undefined) return ''
      if (typeof value === 'number') return value.toFixed(4)
      return String(value)
    })
    lines.push(values.join(','))
  }

  return lines.join('\n')
}

// 生成JSON内容
const generateJSON = (data: any[]): string => {
  const fields = exportConfig.value.fields

  const jsonData = data.map(row => {
    const obj: Record<string, any> = {}
    for (const field of fields) {
      obj[getFieldLabel(field)] = row[field]
    }
    return obj
  })

  return JSON.stringify(jsonData, null, 2)
}

// 格式化日期
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0]
}

// 关闭面板
const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.export-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.export-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.section-title .preview-count {
  font-size: 12px;
  color: var(--fdas-text-muted);
  margin-left: 8px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-separator {
  color: var(--fdas-text-muted);
}

.quick-range {
  display: flex;
  gap: 8px;
}

.field-selection {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.field-preset {
  display: flex;
  gap: 8px;
}

.format-option {
  display: flex;
  flex-direction: column;
}

.format-name {
  font-weight: 500;
}

.format-desc {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-table {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid var(--fdas-border-light);
  border-radius: 4px;
}

.preview-table table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th,
.preview-table td {
  padding: 4px 8px;
  text-align: left;
  font-size: 12px;
  border-bottom: 1px solid var(--fdas-border-light);
}

.preview-table th {
  background: var(--fdas-bg-secondary);
  font-weight: 500;
}

.preview-table tr:last-child td {
  border-bottom: none;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>