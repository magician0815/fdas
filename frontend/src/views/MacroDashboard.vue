<template>
  <div class="macro-dashboard">
    <h2 class="page-title">宏观数据总览</h2>

    <!-- 数据源状态卡片 -->
    <div class="source-cards" v-loading="loading">
      <div
        v-for="config in configs"
        :key="config.id"
        class="source-card"
        :class="statusClass(config.last_status)"
      >
        <div class="card-header">
          <span class="source-code">{{ config.source_code }}</span>
          <el-tag :type="statusTagType(config.last_status)" size="small">
            {{ config.last_status || '未采集' }}
          </el-tag>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <span class="label">描述</span>
            <span class="value">{{ config.description || '-' }}</span>
          </div>
          <div class="stat-row">
            <span class="label">最新数据</span>
            <span class="value">{{ latestDates[config.source_code] || '-' }}</span>
          </div>
          <div class="stat-row">
            <span class="label">记录数</span>
            <span class="value">{{ config.last_records_count }}</span>
          </div>
          <div class="stat-row">
            <span class="label">上次采集</span>
            <span class="value">{{ formatTime(config.last_collected_at) }}</span>
          </div>
        </div>
        <div class="card-actions">
          <el-button size="small" type="primary" @click="triggerCollect(config.id)" :loading="collecting === config.id">
            手动采集
          </el-button>
          <el-button size="small" @click="$router.push(`/macro/data?source=${config.source_code}`)">
            查看数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 趋势图 -->
    <div class="chart-section" v-if="chartData.length > 0">
      <h3>r-star 趋势对比</h3>
      <div ref="chartRef" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup>
/**
 * 宏观数据总览页面.
 *
 * 展示5个数据源的采集状态和 r-star 趋势对比图.
 *
 * Author: FDAS Team
 * Created: 2026-07-29
 */
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { listConfigs, triggerCollect, queryData, getLatest } from '@/api/macro'

const router = useRouter()
const configs = ref([])
const loading = ref(false)
const collecting = ref(null)
const chartData = ref([])
const chartRef = ref(null)
const latestDates = ref({})
let chartInstance = null

const statusClass = (status) => ({
  'status-success': status === 'success',
  'status-failed': status === 'failed',
  'status-partial': status === 'partial',
  'status-idle': !status,
})

const statusTagType = (status) => {
  if (status === 'success') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'partial') return 'warning'
  return 'info'
}

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const res = await listConfigs()
    configs.value = res.data || []
    // 获取各数据源最新数据时间
    const dates = {}
    for (const c of configs.value) {
      try {
        const lr = await getLatest(c.source_code)
        if (lr.success && lr.data) {
          dates[c.source_code] = lr.data.period_date || lr.data.publish_date
        }
      } catch {}
    }
    latestDates.value = dates
  } catch (e) {
    ElMessage.error('加载配置失败: ' + (e.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleCollect = async (id) => {
  collecting.value = id
  try {
    await triggerCollect(id)
    ElMessage.success('采集任务已触发')
    setTimeout(loadConfigs, 2000)
  } catch (e) {
    ElMessage.error('触发采集失败: ' + (e.message || '未知错误'))
  } finally {
    collecting.value = null
  }
}

const loadChartData = async () => {
  try {
    // 分页获取全量数据用于图表渲染(每页最大200)
    let allData = []
    let page = 1
    while (true) {
      const res = await queryData({ page, page_size: 200 })
      const items = res.data || []
      allData = allData.concat(items)
      if (items.length < 200) break
      page++
    }
    chartData.value = allData
  } catch (e) {
    // 图表数据加载失败不影响主界面
  }
}

const renderChart = () => {
  if (!chartRef.value || chartData.value.length === 0) return

  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)

  // 按 source_code 分组
  const groups = {}
  chartData.value.forEach(d => {
    const key = d.indicator_key || d.source_code
    if (!groups[key]) groups[key] = []
    groups[key].push({ date: d.period_date || d.publish_date, value: d.value })
  })

  const series = Object.entries(groups).map(([key, data]) => ({
    name: key,
    type: 'line',
    data: data
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .map(d => [d.date, d.value]),
    smooth: true,
  }))

  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 10, textStyle: { color: '#a0aec0' } },
    grid: { left: 60, right: 30, top: 50, bottom: 40 },
    xAxis: { type: 'time', axisLine: { lineStyle: { color: '#4a5568' } } },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#4a5568' } },
      axisLabel: { formatter: '{value}%' },
    },
    series,
    backgroundColor: 'transparent',
  })
}

onMounted(() => {
  loadConfigs()
  loadChartData().then(() => nextTick(renderChart))
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

watch(chartData, () => nextTick(renderChart))
</script>

<style scoped>
.macro-dashboard {
  padding: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 24px 0;
}

.source-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.source-card {
  background: var(--fdas-card-bg);
  border: 1px solid var(--fdas-border);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s;
}

.source-card:hover {
  border-color: var(--fdas-primary);
}

.source-card.status-success { border-left: 4px solid #48bb78; }
.source-card.status-failed { border-left: 4px solid #fc8181; }
.source-card.status-partial { border-left: 4px solid #ecc94b; }
.source-card.status-idle { border-left: 4px solid #718096; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.source-code {
  font-weight: 600;
  font-size: 15px;
  color: #e2e8f0;
}

.card-body {
  margin-bottom: 12px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 13px;
}

.stat-row .label {
  color: #a0aec0;
}

.stat-row .value {
  color: #e2e8f0;
  max-width: 60%;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.chart-section {
  margin-top: 24px;
}

.chart-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 16px;
}

.chart-container {
  height: 400px;
  background: var(--fdas-card-bg);
  border-radius: 12px;
  border: 1px solid var(--fdas-border);
}
</style>
