<template>
  <div class="datasource-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据源管理</h1>
        <p class="page-subtitle">管理数据采集来源和金融标的同步</p>
      </div>
      <div class="header-right">
        <el-button @click="fetchDatasources" :loading="loading">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
        </el-button>
        <el-button type="success" @click="showImportDialog">
          <el-icon><Upload /></el-icon>
          <span>导入配置</span>
        </el-button>
      </div>
    </div>

    <!-- 数据源列表 -->
    <div class="datasource-grid">
      <div class="datasource-card" v-for="ds in datasources" :key="ds.id">
        <div class="card-header">
          <div class="ds-icon" :class="ds.type">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="ds-info">
            <h3 class="ds-name">{{ ds.name }}</h3>
            <span class="ds-interface">{{ ds.interface }}</span>
          </div>
          <el-tag :type="ds.is_active ? 'success' : 'info'" size="small">
            {{ ds.is_active ? '活跃' : '停用' }}
          </el-tag>
        </div>

        <div class="card-body">
          <div class="info-row">
            <span class="info-label">市场类型</span>
            <span class="info-value">{{ getMarketName(ds.market_id) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">数据类型</span>
            <span class="info-value">{{ ds.type }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">最早日期</span>
            <span class="info-value">{{ ds.min_date || '不限' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">支持标的</span>
            <span class="info-value">{{ ds.supported_symbols?.length || 0 }} 个</span>
          </div>
          <div class="info-row">
            <span class="info-label">配置版本</span>
            <span class="info-value">{{ ds.config_version || '默认' }}</span>
          </div>
        </div>

        <div class="card-footer">
          <el-button size="small" type="primary" @click="syncSymbolsToDb(ds)" :loading="ds.syncing">
            <el-icon><Refresh /></el-icon>
            同步金融标的
          </el-button>
          <el-button size="small" @click="showConfigDialog(ds)" :loading="ds.loadingConfig">
            <el-icon><Setting /></el-icon>
            配置
          </el-button>
          <el-button size="small" @click="exportConfig(ds)" :loading="ds.exporting">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-card" v-if="!datasources.length && !loading">
        <el-empty description="暂无数据源">
          <el-button type="primary" @click="showImportDialog">添加数据源</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 同步结果对话框 -->
    <el-dialog
      v-model="syncResultDialogVisible"
      title="金融标的同步结果"
      width="500px"
    >
      <div class="sync-result">
        <div class="result-item success">
          <el-icon><CircleCheck /></el-icon>
          <span>新增: {{ syncResult.added }} 个</span>
        </div>
        <div class="result-item warning">
          <el-icon><Edit /></el-icon>
          <span>更新: {{ syncResult.updated }} 个</span>
        </div>
        <div class="result-item info">
          <el-icon><CircleCheck /></el-icon>
          <span>跳过（已存在）: {{ syncResult.skipped }} 个</span>
        </div>
        <div class="result-item total">
          <span>总计处理: {{ syncResult.total }} 个金融标的</span>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="syncResultDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>

    <!-- 配置编辑对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      :title="`配置编辑 - ${currentDatasource?.name}`"
      width="800px"
      destroy-on-close
    >
      <div class="config-editor">
        <el-alert
          title="配置说明"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          <template #default>
            修改配置后，采集任务将使用新配置执行。JSON格式必须正确。
          </template>
        </el-alert>
        <el-input
          v-model="configContent"
          type="textarea"
          :rows="20"
          placeholder="请输入JSON配置..."
          :style="{ fontFamily: 'monospace', fontSize: '12px' }"
        />
      </div>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="resetConfig">重置为默认</el-button>
        <el-button type="primary" @click="saveConfig" :loading="savingConfig">保存</el-button>
      </template>
    </el-dialog>

    <!-- 导入配置对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入数据源配置"
      width="600px"
      destroy-on-close
    >
      <div class="import-form">
        <el-form :model="importForm" label-width="100px">
          <el-form-item label="数据源名称" required>
            <el-input v-model="importForm.name" placeholder="请输入数据源名称" />
          </el-form-item>
          <el-form-item label="市场" required>
            <el-select v-model="importForm.market_id" placeholder="请选择市场">
              <el-option
                v-for="m in markets"
                :key="m.id"
                :label="m.name"
                :value="m.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="配置文件" required>
            <el-input
              v-model="importForm.config_file"
              type="textarea"
              :rows="15"
              placeholder="请粘贴JSON配置..."
              :style="{ fontFamily: 'monospace', fontSize: '12px' }"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 数据源管理页面.
 *
 * 提供数据源查看、金融标的同步、配置管理功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-21 - 添加配置编辑、导入导出功能
 */
import { ref, reactive, onMounted } from 'vue'
import { Connection, Refresh, CircleCheck, Edit, Setting, Download, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getDatasources,
  syncSymbolsToDatabase,
  getDatasourceConfig,
  updateDatasourceConfig,
  exportDatasourceConfig,
  importDatasourceConfig,
  getDefaultConfig
} from '@/api/datasources'
import { getMarkets } from '@/api/markets'
import logger from '@/services/logger'

// 数据状态
const loading = ref(false)
const datasources = ref([])
const markets = ref([])

// 配置编辑相关
const configDialogVisible = ref(false)
const currentDatasource = ref(null)
const configContent = ref('')
const savingConfig = ref(false)

// 导入相关
const importDialogVisible = ref(false)
const importing = ref(false)
const importForm = reactive({
  name: '',
  market_id: '',
  config_file: ''
})

// 同步结果对话框
const syncResultDialogVisible = ref(false)
const syncResult = reactive({
  added: 0,
  updated: 0,
  skipped: 0,
  total: 0
})

// 根据ID获取市场名称
const getMarketName = (marketId) => {
  const m = markets.value.find(m => m.id === marketId)
  return m?.name || '--'
}

// 获取数据源列表
const fetchDatasources = async () => {
  loading.value = true
  try {
    const res = await getDatasources()
    if (res.success) {
      datasources.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取数据源列表失败')
  } finally {
    loading.value = false
  }
}

// 获取市场列表
const fetchMarkets = async () => {
  try {
    const res = await getMarkets()
    if (res.success) {
      markets.value = res.data
    }
  } catch (e) {
    logger.error('获取市场列表失败', e)
  }
}

// 同步金融标的到数据库
const syncSymbolsToDb = async (ds) => {
  try {
    ds.syncing = true
    const res = await syncSymbolsToDatabase(ds.id)
    if (res.success) {
      syncResult.added = res.data.added
      syncResult.updated = res.data.updated
      syncResult.skipped = res.data.skipped
      syncResult.total = res.data.total
      syncResultDialogVisible.value = true
      ElMessage.success(res.message)
      fetchDatasources()
    } else {
      ElMessage.error(res.message || '同步失败')
    }
  } catch (e) {
    ElMessage.error('同步金融标的失败')
  } finally {
    ds.syncing = false
  }
}

// 显示配置对话框
const showConfigDialog = async (ds) => {
  try {
    ds.loadingConfig = true
    currentDatasource.value = ds
    const res = await getDatasourceConfig(ds.id)
    if (res.success) {
      configContent.value = res.data.config_file || ''
      if (!configContent.value) {
        // 获取默认配置
        configContent.value = getDefaultConfig()
      }
    } else {
      ElMessage.error(res.message || '获取配置失败')
      return
    }
    configDialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取配置失败')
  } finally {
    ds.loadingConfig = false
  }
}

// 保存配置
const saveConfig = async () => {
  if (!currentDatasource.value) return

  // 验证JSON格式
  try {
    JSON.parse(configContent.value)
  } catch (e) {
    ElMessage.error('JSON格式不正确')
    return
  }

  try {
    savingConfig.value = true
    const res = await updateDatasourceConfig(
      currentDatasource.value.id,
      configContent.value
    )
    if (res.success) {
      ElMessage.success('配置保存成功')
      configDialogVisible.value = false
      fetchDatasources()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存配置失败')
  } finally {
    savingConfig.value = false
  }
}

// 重置为默认配置
const resetConfig = () => {
  configContent.value = getDefaultConfig()
  ElMessage.info('已重置为默认配置')
}

// 导出配置
const exportConfig = async (ds) => {
  try {
    ds.exporting = true
    const res = await exportDatasourceConfig(ds.id)
    if (res.success && res.data.config_file) {
      // 创建下载
      const blob = new Blob([res.data.config_file], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${ds.name}_config.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      ElMessage.success('配置导出成功')
    } else {
      ElMessage.warning('该数据源暂无配置')
    }
  } catch (e) {
    ElMessage.error('导出配置失败')
  } finally {
    ds.exporting = false
  }
}

// 显示导入对话框
const showImportDialog = () => {
  importForm.name = ''
  importForm.market_id = ''
  importForm.config_file = getDefaultConfig()
  importDialogVisible.value = true
}

// 处理导入
const handleImport = async () => {
  if (!importForm.name) {
    ElMessage.error('请输入数据源名称')
    return
  }
  if (!importForm.market_id) {
    ElMessage.error('请选择市场')
    return
  }
  if (!importForm.config_file) {
    ElMessage.error('请输入配置文件')
    return
  }

  // 验证JSON格式
  try {
    JSON.parse(importForm.config_file)
  } catch (e) {
    ElMessage.error('JSON格式不正确')
    return
  }

  try {
    importing.value = true
    const res = await importDatasourceConfig(
      importForm.config_file,
      importForm.name,
      importForm.market_id
    )
    if (res.success) {
      ElMessage.success('配置导入成功')
      importDialogVisible.value = false
      fetchDatasources()
    } else {
      ElMessage.error(res.message || '导入失败')
    }
  } catch (e) {
    ElMessage.error('导入配置失败')
  } finally {
    importing.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  ElMessage.info('请使用"导入配置"功能创建数据源')
}

onMounted(() => {
  fetchMarkets()
  fetchDatasources()
})
</script>

<style scoped>
.datasource-page {
  max-width: 1200px;
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

/* 数据源网格 */
.datasource-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--fdas-spacing-lg);
}

.datasource-card {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  box-shadow: var(--fdas-shadow-card);
  transition: all var(--fdas-transition-normal);
}

.datasource-card:hover {
  box-shadow: var(--fdas-shadow-md);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-md);
  padding: var(--fdas-spacing-lg);
  border-bottom: 1px solid var(--fdas-border-light);
}

.ds-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--fdas-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.ds-icon.akshare {
  background: rgba(45, 90, 247, 0.1);
  color: var(--fdas-primary);
}

.ds-info { flex: 1; }

.ds-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--fdas-text-primary);
  margin: 0;
}

.ds-interface {
  font-size: 13px;
  color: var(--fdas-text-muted);
}

.card-body {
  padding: var(--fdas-spacing-md) var(--fdas-spacing-lg);
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: var(--fdas-spacing-xs) 0;
}

.info-label {
  color: var(--fdas-text-muted);
  font-size: 13px;
}

.info-value {
  color: var(--fdas-text-primary);
  font-size: 13px;
  font-weight: 500;
}

.card-footer {
  display: flex;
  gap: var(--fdas-spacing-sm);
  padding: var(--fdas-spacing-md) var(--fdas-spacing-lg);
  border-top: 1px solid var(--fdas-border-light);
}

.empty-card {
  grid-column: 1 / -1;
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-xl);
  box-shadow: var(--fdas-shadow-card);
}

/* 同步结果 */
.sync-result {
  display: flex;
  flex-direction: column;
  gap: var(--fdas-spacing-md);
}

.result-item {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
  padding: var(--fdas-spacing-sm) var(--fdas-spacing-md);
  border-radius: var(--fdas-radius-md);
}

.result-item.success {
  background: rgba(34, 197, 94, 0.1);
  color: var(--fdas-success);
}

.result-item.warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--fdas-warning);
}

.result-item.info {
  background: rgba(45, 90, 247, 0.1);
  color: var(--fdas-primary);
}

.result-item.total {
  background: var(--fdas-gray-100);
  color: var(--fdas-text-primary);
  font-weight: 500;
}

/* 配置编辑器 */
.config-editor {
  display: flex;
  flex-direction: column;
}

.config-editor .el-textarea {
  font-family: monospace;
}

/* 导入表单 */
.import-form {
  padding: var(--fdas-spacing-md) 0;
}

.import-form .el-textarea {
  font-family: monospace;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .datasource-grid {
    grid-template-columns: 1fr;
  }
}
</style>