<template>
  <div class="dashboard-page">
    <!-- 顶部欢迎信息 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎回来，{{ authStore.user?.username }}</h1>
        <p class="welcome-subtitle">FDAS 金融数据抓取与分析系统为您服务</p>
      </div>
      <div class="current-time">
        <el-icon><Clock /></el-icon>
        <span>{{ currentTime }}</span>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-title">数据记录</span>
          <span class="stat-value">{{ stats.dataRecords }}</span>
          <span class="stat-change positive">
            <el-icon><Top /></el-icon>
            较昨日增加 {{ stats.dataRecordsChange }}
          </span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-title">数据源</span>
          <span class="stat-value">{{ stats.datasources }}</span>
          <span class="stat-change">已配置 {{ stats.activeDatasources }} 个活跃</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-title">采集任务</span>
          <span class="stat-value">{{ stats.tasks }}</span>
          <span class="stat-change">运行中 {{ stats.runningTasks }} 个</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-title">执行日志</span>
          <span class="stat-value">{{ stats.logs }}</span>
          <span class="stat-change positive">
            <el-icon><CircleCheck /></el-icon>
            成功率 {{ stats.successRate }}%
          </span>
        </div>
      </div>
    </div>

    <!-- 快速操作区域 -->
    <div class="quick-actions-section">
      <h2 class="section-title">快速操作</h2>
      <div class="actions-grid">
        <button class="action-card" @click="$router.push('/fx-data')">
          <el-icon class="action-icon"><TrendCharts /></el-icon>
          <span class="action-text">查看数据</span>
        </button>
        <button class="action-card" @click="$router.push('/collection')" v-if="isAdmin">
          <el-icon class="action-icon"><Timer /></el-icon>
          <span class="action-text">创建任务</span>
        </button>
        <button class="action-card" @click="$router.push('/datasource')" v-if="isAdmin">
          <el-icon class="action-icon"><Connection /></el-icon>
          <span class="action-text">管理数据源</span>
        </button>
        <button class="action-card" @click="$router.push('/logs')" v-if="isAdmin">
          <el-icon class="action-icon"><Document /></el-icon>
          <span class="action-text">查看日志</span>
        </button>
      </div>
    </div>

    <!-- 系统信息区域 -->
    <div class="system-info-section">
      <div class="info-panel">
        <h2 class="section-title">系统状态</h2>
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">系统版本</span>
            <span class="info-value">v1.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">后端服务</span>
            <span class="info-value status-ok">正常运行</span>
          </div>
          <div class="info-item">
            <span class="info-label">数据库</span>
            <span class="info-value status-ok">已连接</span>
          </div>
          <div class="info-item">
            <span class="info-label">调度器</span>
            <span class="info-value status-ok">运行中</span>
          </div>
        </div>
      </div>

      <div class="info-panel">
        <h2 class="section-title">最近动态</h2>
        <div class="activity-list">
          <div class="activity-item" v-for="(activity, index) in recentActivities" :key="index">
            <el-icon class="activity-icon" :class="activity.type"><component :is="activity.icon" /></el-icon>
            <span class="activity-text">{{ activity.text }}</span>
            <span class="activity-time">{{ activity.time }}</span>
          </div>
          <el-empty v-if="recentActivities.length === 0" description="暂无最近动态" :image-size="60" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 首页Dashboard.
 *
 * 展示系统概览、统计数据、快速操作等.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-10 - 优化Dashboard设计，添加统计卡片和快速操作
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  TrendCharts, Connection, Timer, Document, Clock, Top,
  CircleCheck, CircleClose, Loading
} from '@element-plus/icons-vue'

const authStore = useAuthStore()

// 是否为管理员
const isAdmin = computed(() => authStore.user?.role === 'admin')

// 当前时间
const currentTime = ref('')
let timeInterval = null

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

// 统计数据（模拟数据，后续从API获取）
const stats = ref({
  dataRecords: '12,856',
  dataRecordsChange: '156',
  datasources: '5',
  activeDatasources: '3',
  tasks: '8',
  runningTasks: '2',
  logs: '1,245',
  successRate: '98.5'
})

// 最近动态（模拟数据）
const recentActivities = ref([
  { type: 'success', icon: CircleCheck, text: 'USDCNY 数据采集完成', time: '2分钟前' },
  { type: 'info', icon: Timer, text: 'EURUSD 定时任务已启动', time: '15分钟前' },
  { type: 'success', icon: CircleCheck, text: 'GBPUSD 数据采集完成', time: '1小时前' },
])
</script>

<style scoped>
.dashboard-page {
  max-width: 1200px;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fdas-spacing-lg);
  background: linear-gradient(135deg, var(--fdas-primary) 0%, var(--fdas-primary-light) 100%);
  border-radius: var(--fdas-radius-lg);
  margin-bottom: var(--fdas-spacing-lg);
  color: #ffffff;
}

.welcome-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.welcome-subtitle {
  font-size: 14px;
  margin-top: 8px;
  opacity: 0.9;
}

.current-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.9;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--fdas-spacing-lg);
  margin-bottom: var(--fdas-spacing-lg);
}

.stat-card {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-md);
  box-shadow: var(--fdas-shadow-card);
  transition: all var(--fdas-transition-normal);
}

.stat-card:hover {
  box-shadow: var(--fdas-shadow-md);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--fdas-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue {
  background: rgba(45, 90, 247, 0.1);
  color: var(--fdas-primary);
}

.stat-icon.green {
  background: rgba(34, 197, 94, 0.1);
  color: var(--fdas-success);
}

.stat-icon.orange {
  background: rgba(245, 158, 11, 0.1);
  color: var(--fdas-warning);
}

.stat-icon.purple {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-title {
  font-size: 13px;
  color: var(--fdas-text-muted);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--fdas-text-primary);
  line-height: 1.2;
}

.stat-change {
  font-size: 12px;
  color: var(--fdas-text-muted);
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.stat-change.positive {
  color: var(--fdas-success);
}

.stat-change.negative {
  color: var(--fdas-danger);
}

/* 快速操作区域 */
.quick-actions-section {
  margin-bottom: var(--fdas-spacing-lg);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--fdas-text-primary);
  margin-bottom: var(--fdas-spacing-md);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--fdas-spacing-md);
}

.action-card {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--fdas-spacing-sm);
  cursor: pointer;
  border: 2px solid transparent;
  transition: all var(--fdas-transition-fast);
  box-shadow: var(--fdas-shadow-card);
}

.action-card:hover {
  border-color: var(--fdas-primary);
  background: rgba(45, 90, 247, 0.05);
}

.action-icon {
  font-size: 28px;
  color: var(--fdas-primary);
}

.action-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

/* 系统信息区域 */
.system-info-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--fdas-spacing-lg);
}

.info-panel {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-lg);
  box-shadow: var(--fdas-shadow-card);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: var(--fdas-spacing-sm);
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: var(--fdas-spacing-sm) 0;
  border-bottom: 1px solid var(--fdas-border-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: var(--fdas-text-muted);
}

.info-value {
  color: var(--fdas-text-primary);
  font-weight: 500;
}

.info-value.status-ok {
  color: var(--fdas-success);
}

/* 最近动态列表 */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--fdas-spacing-sm);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
  padding: var(--fdas-spacing-sm);
  border-radius: var(--fdas-radius-md);
  background: var(--fdas-gray-50);
}

.activity-icon {
  font-size: 16px;
}

.activity-icon.success {
  color: var(--fdas-success);
}

.activity-icon.info {
  color: var(--fdas-primary);
}

.activity-text {
  flex: 1;
  color: var(--fdas-text-secondary);
  font-size: 13px;
}

.activity-time {
  color: var(--fdas-text-muted);
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--fdas-spacing-md);
  }

  .stats-grid,
  .actions-grid {
    grid-template-columns: 1fr;
  }

  .system-info-section {
    grid-template-columns: 1fr;
  }
}
</style>