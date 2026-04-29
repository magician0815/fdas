<template>
  <div class="logs-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统日志</h1>
        <p class="page-subtitle">查看系统运行日志和任务执行记录</p>
      </div>
      <div class="header-right">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          class="date-picker"
          @change="fetchLogs"
        />
        <el-button @click="fetchLogs" :loading="loading">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
        </el-button>
      </div>
    </div>

    <!-- 日志筛选 -->
    <div class="filter-bar">
      <el-radio-group v-model="logType" @change="fetchLogs">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="collection">采集日志</el-radio-button>
        <el-radio-button label="system">系统日志</el-radio-button>
        <el-radio-button label="error">错误日志</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 日志列表 -->
    <div class="logs-container">
      <div class="log-item" v-for="log in logs" :key="log.id" :class="log.level">
        <div class="log-header">
          <el-icon class="log-icon" :class="log.level">
            <component :is="getLogIcon(log.level)" />
          </el-icon>
          <span class="log-type">{{ log.type }}</span>
          <span class="log-time">{{ formatDate(log.created_at) }}</span>
        </div>
        <div class="log-body">
          <p class="log-message">{{ log.message }}</p>
          <div class="log-details" v-if="log.details">
            <span class="detail-item" v-for="(value, key) in log.details" :key="key">
              <span class="detail-key">{{ key }}:</span>
              <span class="detail-value">{{ value }}</span>
            </span>
          </div>
        </div>
      </div>

      <el-empty v-if="!logs.length && !loading" description="暂无日志记录" />
    </div>
  </div>
</template>

<script setup>
/**
 * 系统日志页面.
 *
 * 查看系统运行日志（仅管理员）.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-10 - 优化页面设计
 */
import { ref, onMounted } from 'vue'
import { Refresh, CircleCheck, CircleClose, Warning, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const logs = ref([])
const logType = ref('all')
const dateRange = ref([])

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取日志图标
const getLogIcon = (level) => {
  const icons = {
    'success': CircleCheck,
    'error': CircleClose,
    'warning': Warning,
    'info': InfoFilled
  }
  return icons[level] || InfoFilled
}

// 获取日志
const fetchLogs = () => {
  ElMessage.info('获取日志功能开发中')
}

onMounted(() => {
  // 模拟数据
  logs.value = [
    {
      id: '1',
      type: '采集任务',
      level: 'success',
      message: 'USDCNY日线数据采集完成',
      created_at: '2026-04-10T18:05:32',
      details: { 记录数: 156, 耗时: '1.2s' }
    },
    {
      id: '2',
      type: '系统',
      level: 'info',
      message: '调度器启动成功',
      created_at: '2026-04-10T08:00:00',
      details: null
    },
    {
      id: '3',
      type: '采集任务',
      level: 'error',
      message: 'EURUSD数据采集失败：网络超时',
      created_at: '2026-04-10T17:30:15',
      details: { 错误码: 'TIMEOUT', 重试次数: 3 }
    },
    {
      id: '4',
      type: '系统',
      level: 'warning',
      message: '数据库连接池接近上限',
      created_at: '2026-04-10T12:45:00',
      details: { 当前连接: 8, 最大连接: 10 }
    }
  ]
})
</script>

<style scoped>
.logs-page {
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
  align-items: center;
  gap: var(--fdas-spacing-md);
}

.date-picker {
  width: 240px;
}

/* 筛选栏 */
.filter-bar {
  margin-bottom: var(--fdas-spacing-lg);
}

/* 日志容器 */
.logs-container {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-lg);
  box-shadow: var(--fdas-shadow-card);
}

.log-item {
  padding: var(--fdas-spacing-md);
  border-radius: var(--fdas-radius-md);
  margin-bottom: var(--fdas-spacing-md);
  background: var(--fdas-gray-50);
  transition: all var(--fdas-transition-fast);
}

.log-item:hover {
  background: var(--fdas-gray-100);
}

.log-item.success {
  border-left: 3px solid var(--fdas-success);
}

.log-item.error {
  border-left: 3px solid var(--fdas-danger);
}

.log-item.warning {
  border-left: 3px solid var(--fdas-warning);
}

.log-item.info {
  border-left: 3px solid var(--fdas-info);
}

.log-header {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
  margin-bottom: var(--fdas-spacing-sm);
}

.log-icon {
  font-size: 16px;
}

.log-icon.success {
  color: var(--fdas-success);
}

.log-icon.error {
  color: var(--fdas-danger);
}

.log-icon.warning {
  color: var(--fdas-warning);
}

.log-icon.info {
  color: var(--fdas-info);
}

.log-type {
  font-size: 13px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.log-time {
  font-size: 12px;
  color: var(--fdas-text-muted);
  margin-left: auto;
}

.log-body {
  margin-top: var(--fdas-spacing-sm);
}

.log-message {
  font-size: 14px;
  color: var(--fdas-text-secondary);
  margin: 0;
}

.log-details {
  display: flex;
  flex-wrap: wrap;
  gap: var(--fdas-spacing-md);
  margin-top: var(--fdas-spacing-sm);
}

.detail-item {
  font-size: 12px;
}

.detail-key {
  color: var(--fdas-text-muted);
}

.detail-value {
  color: var(--fdas-text-primary);
  font-weight: 500;
}
</style>