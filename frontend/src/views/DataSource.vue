<template>
  <div class="datasource-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据源管理</h1>
        <p class="page-subtitle">管理数据采集来源和货币对同步</p>
      </div>
      <div class="header-right">
        <el-button @click="fetchDatasources" :loading="loading">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
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
        </div>

        <div class="card-footer">
          <el-button size="small" type="primary" @click="syncSymbolsToDb(ds)" :loading="ds.syncing">
            <el-icon><Refresh /></el-icon>
            同步货币对到数据库
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-card" v-if="!datasources.length && !loading">
        <el-empty description="暂无数据源">
          <el-button type="primary" @click="showCreateDialog">添加数据源</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 同步结果对话框 -->
    <el-dialog
      v-model="syncResultDialogVisible"
      title="货币对同步结果"
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
          <span>总计处理: {{ syncResult.total }} 个货币对</span>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="syncResultDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 数据源管理页面.
 *
 * 提供数据源查看和货币对同步功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-11 - 完整功能实现，添加货币对同步
 */
import { ref, reactive, onMounted } from 'vue'
import { Connection, Refresh, CircleCheck, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getDatasources, syncSymbolsToDatabase } from '@/api/datasources'
import { getMarkets } from '@/api/markets'

// 数据状态
const loading = ref(false)
const datasources = ref([])
const markets = ref([])

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
    console.error('获取市场列表失败')
  }
}

// 同步货币对到数据库
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
    ElMessage.error('同步货币对失败')
  } finally {
    ds.syncing = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  ElMessage.info('创建数据源功能开发中')
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

/* 响应式设计 */
@media (max-width: 768px) {
  .datasource-grid {
    grid-template-columns: 1fr;
  }
}
</style>