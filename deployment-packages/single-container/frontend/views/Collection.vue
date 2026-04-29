<template>
  <div class="collection-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">采集任务</h1>
        <p class="page-subtitle">配置数据采集任务和调度</p>
      </div>
      <div class="header-right">
        <el-button @click="fetchTasks" :loading="loading">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
        </el-button>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          <span>创建任务</span>
        </el-button>
      </div>
    </div>

    <!-- 任务统计 -->
    <div class="stats-row">
      <div class="stat-card mini">
        <span class="stat-label">总任务数</span>
        <span class="stat-value">{{ stats.total }}</span>
      </div>
      <div class="stat-card mini">
        <span class="stat-label">运行中</span>
        <span class="stat-value primary">{{ stats.running }}</span>
      </div>
      <div class="stat-card mini">
        <span class="stat-label">已启用</span>
        <span class="stat-value success">{{ stats.enabled }}</span>
      </div>
      <div class="stat-card mini">
        <span class="stat-label">已停用</span>
        <span class="stat-value muted">{{ stats.disabled }}</span>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="table-panel">
      <el-table :data="tasks" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="任务名称" width="200">
          <template #default="{ row }">
            <div class="task-name">
              <el-icon class="task-icon"><Timer /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="标的" width="150">
          <template #default="{ row }">
            <span class="symbol-badge">{{ getSymbolCode(row.symbol_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="数据源" width="150">
          <template #default="{ row }">
            {{ getDatasourceName(row.datasource_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="cron_expr" label="执行周期" width="150">
          <template #default="{ row }">
            <span class="cron-text">{{ row.cron_expr || '手动执行' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled ? 'success' : 'info'" size="small">
              {{ row.is_enabled ? '已启用' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_status" label="上次执行" width="120">
          <template #default="{ row }">
            <span class="status-badge" :class="row.last_status">
              {{ getStatusText(row.last_status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="next_run_at" label="下次执行" width="180">
          <template #default="{ row }">
            {{ row.next_run_at ? formatDate(row.next_run_at) : '--' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="executeTask(row)" :loading="row.executing">
              <el-icon><VideoPlay /></el-icon>
            </el-button>
            <el-button size="small" text :type="row.is_enabled ? 'warning' : 'success'" @click="toggleTask(row)">
              {{ row.is_enabled ? '停用' : '启用' }}
            </el-button>
            <el-button size="small" text type="primary" @click="editTask(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" text type="primary" @click="viewLogs(row)">
              <el-icon><Document /></el-icon>
            </el-button>
            <el-button size="small" text type="danger" @click="deleteTask(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!tasks.length && !loading" description="暂无采集任务">
        <el-button type="primary" @click="showCreateDialog">创建第一个任务</el-button>
      </el-empty>
    </div>

    <!-- 创建/编辑任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑采集任务' : '创建采集任务'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="formData.name" placeholder="如: USDCNY日线采集" />
        </el-form-item>

        <el-form-item label="数据源" prop="datasource_id">
          <el-select v-model="formData.datasource_id" placeholder="选择数据源" @change="onDatasourceChange">
            <el-option
              v-for="ds in datasources"
              :key="ds.id"
              :label="ds.name"
              :value="ds.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="市场" prop="market_id">
          <el-select v-model="formData.market_id" placeholder="选择市场" @change="onMarketChange">
            <el-option
              v-for="m in markets"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="标的" prop="symbol_id">
          <el-select v-model="formData.symbol_id" placeholder="选择标的" filterable>
            <el-option
              v-for="s in symbols"
              :key="s.id"
              :label="`${s.name} (${s.code})`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="日期范围">
          <DateRangeSelector
            v-model="dateRange"
            :min-date="minDate"
          />
        </el-form-item>

        <el-form-item label="定时配置">
          <CronBuilder v-model="formData.cron_expr" />
        </el-form-item>

        <!-- 参数校验结果 -->
        <el-form-item label="校验结果" v-if="validationResult">
          <ParamValidator :result="validationResult" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button @click="validateForm" :loading="validating">校验参数</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行日志对话框 -->
    <el-dialog
      v-model="logsDialogVisible"
      :title="`${currentTask?.name || '任务'} - 执行日志`"
      width="800px"
    >
      <el-table :data="taskLogs" stripe max-height="400">
        <el-table-column prop="run_at" label="执行时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.run_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getLogStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="records_count" label="记录数" width="100" />
        <el-table-column prop="duration_ms" label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration_ms ? `${row.duration_ms}ms` : '--' }}
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 采集任务管理页面.
 *
 * 提供采集任务的CRUD、启停、执行、日志查看等完整功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-11 - 完整功能实现
 */
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus, Timer, VideoPlay, Edit, Document, Delete, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import DateRangeSelector from '@/components/DateRangeSelector.vue'
import CronBuilder from '@/components/CronBuilder.vue'
import ParamValidator from '@/components/ParamValidator.vue'
import {
  getCollectionTasks, createCollectionTask, updateCollectionTask,
  deleteCollectionTask as deleteTaskApi, enableTask, disableTask,
  executeTask as executeTaskApi, getTaskLogs, validateTaskParams
} from '@/api/collection'
import { getForexSymbols } from '@/api/forex_symbols'
import { getStockSymbols } from '@/api/stock_symbols'
import { getFuturesVarieties } from '@/api/futures_varieties'
import { getBondSymbols } from '@/api/bond_symbols'
import { getDatasources } from '@/api/datasources'
import { getMarkets } from '@/api/markets'

// 数据状态
const loading = ref(false)
const tasks = ref([])
const symbols = ref([])
const datasources = ref([])
const markets = ref([])
const taskLogs = ref([])
const currentTask = ref(null)

// 对话框状态
const dialogVisible = ref(false)
const logsDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const validating = ref(false)
const formRef = ref()
const validationResult = ref(null)

// 日期范围
const dateRange = ref([null, null])

// 最小日期
const minDate = computed(() => {
  const ds = datasources.value.find(d => d.id === formData.datasource_id)
  return ds?.min_date || null
})

// 表单数据
const formData = reactive({
  name: '',
  datasource_id: '',
  market_id: '',
  symbol_id: '',
  start_date: null,
  end_date: null,
  cron_expr: '',
})

// 日期范围变化时同步表单
watch(dateRange, (val) => {
  formData.start_date = val[0]
  formData.end_date = val[1]
})

// 表单校验规则
const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  datasource_id: [{ required: true, message: '请选择数据源', trigger: 'change' }],
  market_id: [{ required: true, message: '请选择市场', trigger: 'change' }],
  symbol_id: [{ required: true, message: '请选择标的', trigger: 'change' }],
}

// 统计数据
const stats = computed(() => {
  const total = tasks.value.length
  const enabled = tasks.value.filter(t => t.is_enabled).length
  const disabled = total - enabled
  const running = tasks.value.filter(t => t.last_status === 'running').length
  return { total, enabled, disabled, running }
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    'success': '成功',
    'failed': '失败',
    'running': '运行中',
    'pending': '待执行'
  }
  return texts[status] || '--'
}

// 获取日志状态类型
const getLogStatusType = (status) => {
  const types = {
    'success': 'success',
    'failed': 'danger',
    'running': 'primary'
  }
  return types[status] || 'info'
}

// 根据ID获取标的代码
const getSymbolCode = (symbolId) => {
  const s = symbols.value.find(s => s.id === symbolId)
  return s?.code || '--'
}

// 根据ID获取数据源名称
const getDatasourceName = (datasourceId) => {
  const ds = datasources.value.find(d => d.id === datasourceId)
  return ds?.name || '--'
}

// 数据源变化时自动设置市场
const onDatasourceChange = (dsId) => {
  const ds = datasources.value.find(d => d.id === dsId)
  if (ds?.market_id) {
    formData.market_id = ds.market_id
    // 根据数据源自动加载对应市场的标的
    loadSymbolsByMarket(ds.market_id)
  }
}

// 市场变化时加载对应标的
const onMarketChange = (marketId) => {
  loadSymbolsByMarket(marketId)
}

// 根据市场ID加载对应标的
const loadSymbolsByMarket = async (marketId) => {
  if (!marketId) {
    symbols.value = []
    return
  }

  const market = markets.value.find(m => m.id === marketId)
  if (!market) return

  try {
    let res
    // 股票类市场统一处理（包括stock_cn, stock_us, stock_hk等）
    if (market.code && market.code.startsWith('stock')) {
      res = await getStockSymbols({ marketId, activeOnly: true })
    } else if (market.code === 'forex') {
      res = await getForexSymbols({ activeOnly: true })
    } else if (market.code === 'futures' || market.code === 'futures_cn') {
      res = await getFuturesVarieties({ activeOnly: true })
    } else if (market.code === 'bond' || market.code.startsWith('bond')) {
      res = await getBondSymbols({ marketId, activeOnly: true })
    } else {
      // 默认外汇
      res = await getForexSymbols({ activeOnly: true })
    }
    if (res.success) symbols.value = res.data
  } catch (e) {
    console.error('加载标的失败:', e)
  }
}

// 获取任务列表
const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await getCollectionTasks()
    if (res.success) {
      tasks.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

// 获取基础数据
const fetchBaseData = async () => {
  try {
    const [datasourcesRes, marketsRes] = await Promise.all([
      getDatasources(),
      getMarkets()
    ])
    if (datasourcesRes.success) datasources.value = datasourcesRes.data
    if (marketsRes.success) markets.value = marketsRes.data

    // 不再默认加载外汇标的，让用户选择数据源后再加载对应标的
    symbols.value = []
  } catch (e) {
    ElMessage.error('获取基础数据失败')
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑任务
const editTask = (task) => {
  isEdit.value = true
  resetForm()
  formData.name = task.name
  formData.datasource_id = task.datasource_id
  formData.market_id = task.market_id
  formData.symbol_id = task.symbol_id
  formData.start_date = task.start_date
  formData.end_date = task.end_date
  formData.cron_expr = task.cron_expr || ''
  dateRange.value = [task.start_date, task.end_date]
  formData.id = task.id
  // 编辑时根据数据源加载对应市场的标的
  loadSymbolsByMarket(task.market_id)
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  formData.name = ''
  formData.datasource_id = ''
  formData.market_id = ''
  formData.symbol_id = ''
  formData.start_date = null
  formData.end_date = null
  formData.cron_expr = ''
  formData.id = undefined
  dateRange.value = [null, null]
  validationResult.value = null
  if (formRef.value) formRef.value.resetFields()
}

// 校验参数
const validateForm = async () => {
  try {
    await formRef.value.validate()
    validating.value = true
    const res = await validateTaskParams(formData)
    if (res.success) {
      validationResult.value = res.data
    }
  } catch (e) {
    ElMessage.warning('请先填写必填项')
  } finally {
    validating.value = false
  }
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    if (isEdit.value) {
      const res = await updateCollectionTask(formData.id, formData)
      if (res.success) {
        ElMessage.success('任务更新成功')
        dialogVisible.value = false
        fetchTasks()
      } else {
        ElMessage.error(res.message || '更新失败')
      }
    } else {
      const res = await createCollectionTask(formData)
      if (res.success) {
        ElMessage.success('任务创建成功')
        dialogVisible.value = false
        fetchTasks()
      } else {
        ElMessage.error(res.message || '创建失败')
      }
    }
  } catch (e) {
    ElMessage.warning('请先填写必填项')
  } finally {
    submitting.value = false
  }
}

// 执行任务
const executeTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确定要立即执行任务 "${task.name}" 吗？`,
      '执行确认',
      { type: 'info' }
    )
    task.executing = true
    const res = await executeTaskApi(task.id)
    if (res.success) {
      ElMessage.success(`执行成功，采集 ${res.data.records_count} 条数据`)
      fetchTasks()
    } else {
      ElMessage.error(res.message || '执行失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('执行失败')
    }
  } finally {
    task.executing = false
  }
}

// 启用/停用任务
const toggleTask = async (task) => {
  const action = task.is_enabled ? '停用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}任务 "${task.name}" 吗？`,
      '确认',
      { type: 'warning' }
    )
    let res
    if (task.is_enabled) {
      res = await disableTask(task.id)
    } else {
      res = await enableTask(task.id)
    }
    console.log('toggleTask response:', res)
    if (res && res.success) {
      ElMessage.success(`任务已${action}`)
      fetchTasks()
    } else {
      ElMessage.error(res?.message || res?.error || `${action}失败，请检查控制台`)
    }
  } catch (e) {
    console.error('toggleTask error:', e)
    if (e !== 'cancel') {
      ElMessage.error(`${action}失败: ${e.message || e}`)
    }
  }
}

// 删除任务
const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.name}" 吗？此操作不可恢复。`,
      '删除确认',
      { type: 'error' }
    )
    const res = await deleteTaskApi(task.id)
    if (res.success) {
      ElMessage.success('任务已删除')
      fetchTasks()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 查看日志
const viewLogs = async (task) => {
  currentTask.value = task
  logsDialogVisible.value = true
  try {
    const res = await getTaskLogs(task.id)
    if (res.success) {
      taskLogs.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取日志失败')
  }
}

onMounted(() => {
  fetchBaseData()
  fetchTasks()
})
</script>

<style scoped>
.collection-page {
  max-width: 1400px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--fdas-spacing-lg);
}

.header-left {
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--fdas-text-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 13px;
  color: var(--fdas-text-muted);
  margin-top: 4px;
}

.header-right {
  display: flex;
  gap: var(--fdas-spacing-sm);
}

/* 统计卡片 */
.stats-row {
  display: flex;
  gap: var(--fdas-spacing-md);
  margin-bottom: var(--fdas-spacing-lg);
}

.stat-card.mini {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-md);
  padding: var(--fdas-spacing-md) var(--fdas-spacing-lg);
  display: flex;
  flex-direction: column;
  min-width: 100px;
  box-shadow: var(--fdas-shadow-card);
}

.stat-label {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--fdas-text-primary);
  margin-top: 4px;
}

.stat-value.primary { color: var(--fdas-primary); }
.stat-value.success { color: var(--fdas-success); }
.stat-value.muted { color: var(--fdas-text-muted); }

/* 任务名称 */
.task-name {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
}

.task-icon { color: var(--fdas-primary); }

/* 标的徽章 */
.symbol-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(45, 90, 247, 0.1);
  color: var(--fdas-primary);
}

/* Cron表达式 */
.cron-text {
  font-size: 12px;
  color: var(--fdas-text-secondary);
}

/* 状态徽章 */
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-badge.success { background: rgba(34, 197, 94, 0.1); color: var(--fdas-success); }
.status-badge.failed { background: rgba(239, 68, 68, 0.1); color: var(--fdas-danger); }
.status-badge.running { background: rgba(45, 90, 247, 0.1); color: var(--fdas-primary); }

/* 表格面板 */
.table-panel {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-lg);
  box-shadow: var(--fdas-shadow-card);
}
</style>