<template>
  <div class="macro-configs">
    <h2 class="page-title">宏观数据源配置</h2>

    <el-table :data="configs" v-loading="loading" stripe class="config-table">
      <el-table-column prop="source_code" label="数据源代码" width="200" />
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column prop="source_type" label="类型" width="100" />
      <el-table-column prop="parse_engine" label="解析引擎" width="120" />
      <el-table-column label="URL" min-width="200">
        <template #default="{ row }">
          <a :href="row.url" target="_blank" class="url-link">{{ truncate(row.url, 50) }}</a>
        </template>
      </el-table-column>
      <el-table-column label="调度" width="140">
        <template #default="{ row }">
          <span v-if="row.cron_expr">{{ row.cron_expr }}</span>
          <span v-else class="text-muted">未设置</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.last_status)" size="small">
            {{ row.last_status || '未采集' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="启用" width="70">
        <template #default="{ row }">
          <el-switch
            :model-value="row.is_enabled"
            @change="(val) => toggleEnable(row, val)"
            size="small"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editConfig(row)">编辑</el-button>
          <el-button size="small" type="primary" @click="handleCollect(row)" :loading="collecting === row.id">
            采集
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑配置' : '新建配置'" width="700px">
      <el-form :model="form" label-width="120px" v-if="dialogVisible">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="数据源代码">
          <el-input v-model="form.source_code" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="数据源类型">
          <el-select v-model="form.source_type">
            <el-option label="Excel" value="excel" />
            <el-option label="HTML" value="html" />
            <el-option label="JSON" value="json" />
            <el-option label="CSV" value="csv" />
          </el-select>
        </el-form-item>
        <el-form-item label="解析引擎">
          <el-select v-model="form.parse_engine">
            <el-option label="openpyxl" value="openpyxl" />
            <el-option label="beautifulsoup" value="beautifulsoup" />
            <el-option label="jsonpath" value="jsonpath" />
            <el-option label="pandas" value="pandas" />
          </el-select>
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="form.url" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="Cron 表达式">
          <el-input v-model="form.cron_expr" placeholder="如: 0 9 * * 5" />
        </el-form-item>
        <el-form-item label="请求超时(秒)">
          <el-input-number v-model="form.timeout_seconds" :min="10" :max="300" />
        </el-form-item>
        <el-form-item label="最大重试">
          <el-input-number v-model="form.retry_max_attempts" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="解析规则 (JSON)">
          <el-input
            v-model="parseConfigStr"
            type="textarea"
            :rows="8"
            placeholder='{"columns": {"date": "Date"}, "indicator_key": "example"}'
            :class="{ 'json-error': jsonError }"
          />
          <span v-if="jsonError" class="error-hint">{{ jsonError }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 宏观数据源配置管理页面.
 *
 * 提供配置列表展示、新建/编辑/删除配置、手动采集、启用/禁用调度.
 *
 * Author: FDAS Team
 * Created: 2026-07-29
 */
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listConfigs, createConfig, updateConfig, deleteConfig,
  triggerCollect, enableConfig, disableConfig
} from '@/api/macro'

const configs = ref([])
const loading = ref(false)
const collecting = ref(null)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const parseConfigStr = ref('{}')
const jsonError = ref('')

const form = reactive({
  name: '', source_code: '', source_type: 'html', parse_engine: 'beautifulsoup',
  url: '', cron_expr: '', timeout_seconds: 60, retry_max_attempts: 3,
  description: ''
})

const statusType = (s) => {
  if (s === 'success') return 'success'
  if (s === 'failed') return 'danger'
  if (s === 'partial') return 'warning'
  return 'info'
}

const truncate = (str, len) => {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '...' : str
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const res = await listConfigs()
    configs.value = res.data || []
  } finally {
    loading.value = false
  }
}

const editConfig = (row) => {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name, source_code: row.source_code, source_type: row.source_type,
    parse_engine: row.parse_engine, url: row.url, cron_expr: row.cron_expr,
    timeout_seconds: row.timeout_seconds, retry_max_attempts: row.retry_max_attempts,
    description: row.description || ''
  })
  parseConfigStr.value = JSON.stringify(row.parse_config || {}, null, 2)
  jsonError.value = ''
  dialogVisible.value = true
}

const saveConfig = async () => {
  // 验证 JSON
  try {
    JSON.parse(parseConfigStr.value)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'JSON 格式错误: ' + e.message
    return
  }

  saving.value = true
  try {
    const data = {
      ...form,
      parse_config: JSON.parse(parseConfigStr.value)
    }
    if (editingId.value) {
      await updateConfig(editingId.value, data)
      ElMessage.success('配置已更新')
    } else {
      await createConfig(data)
      ElMessage.success('配置已创建')
    }
    dialogVisible.value = false
    await loadConfigs()
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

const handleCollect = async (row) => {
  collecting.value = row.id
  try {
    await triggerCollect(row.id)
    ElMessage.success(`已触发 ${row.source_code} 采集`)
    setTimeout(loadConfigs, 3000)
  } catch (e) {
    ElMessage.error('采集触发失败')
  } finally {
    collecting.value = null
  }
}

const toggleEnable = async (row, val) => {
  try {
    if (val) {
      await enableConfig(row.id)
    } else {
      await disableConfig(row.id)
    }
    row.is_enabled = val
    ElMessage.success(val ? '已启用' : '已禁用')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除 ${row.source_code} 配置及关联数据?`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteConfig(row.id)
    ElMessage.success('已删除')
    await loadConfigs()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(loadConfigs)
</script>

<style scoped>
.macro-configs {
  padding: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 24px 0;
}

.config-table {
  background: var(--fdas-card-bg);
  border-radius: 12px;
  overflow: hidden;
}

.url-link {
  color: var(--fdas-primary);
  text-decoration: none;
}

.url-link:hover {
  text-decoration: underline;
}

.text-muted {
  color: #718096;
}

.json-error {
  border-color: #fc8181 !important;
}

.error-hint {
  color: #fc8181;
  font-size: 12px;
}
</style>
