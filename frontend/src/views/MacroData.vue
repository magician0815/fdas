<template>
  <div class="macro-data">
    <h2 class="page-title">宏观数据查询</h2>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select v-model="filters.indicator_key" placeholder="选择指标" clearable style="width: 220px">
        <el-option label="r-star (LW 模型)" value="r_star_lw" />
        <el-option label="r-star (HLW 模型)" value="r_star_hlw" />
        <el-option label="r-star (LM 模型)" value="r_star_lm" />
        <el-option label="SEP 长期联邦基金利率中位值" value="sep_median" />
        <el-option label="长期中性利率 (美国)" value="longer_run_neutral" />
      </el-select>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="width: 280px"
      />

      <el-button type="primary" @click="search">查询</el-button>
      <el-button @click="exportCSV">导出 CSV</el-button>
    </div>

    <!-- 图表 -->
    <div class="chart-section" v-if="tableData.length > 0">
      <div ref="chartRef" class="chart-container"></div>
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" v-loading="loading" stripe class="data-table">
      <el-table-column prop="source_code" label="数据源" width="180" />
      <el-table-column prop="indicator_key" label="指标" width="160" />
      <el-table-column prop="country" label="国家" width="80" />
      <el-table-column prop="value" label="数值" width="120" align="right">
        <template #default="{ row }">
          {{ row.value != null ? Number(row.value).toFixed(4) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="发布日期" width="130">
        <template #default="{ row }">
          {{ row.publish_date || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="期间" width="130">
        <template #default="{ row }">
          {{ row.period_date || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="frequency" label="频率" width="120" />
      <el-table-column prop="series_name" label="系列名称" min-width="200" />
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > 0">
      <el-pagination
        v-model:current-page="filters.page"
        :page-size="filters.page_size"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="search"
      />
    </div>
  </div>
</template>

<script setup>
/**
 * 宏观数据查询页面.
 *
 * 支持按数据源/指标/国家/日期范围筛选，分页表格 + ECharts 折线图联动，CSV 导出.
 *
 * Author: FDAS Team
 * Created: 2026-07-29
 */
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { queryData } from '@/api/macro'

const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const chartRef = ref(null)
// 默认显示最近2年
const today = new Date()
const dateRange = ref([new Date(today.getFullYear() - 2, 0, 1), today])
let chartInstance = null

const filters = reactive({
  indicator_key: '',
  page: 1,
  page_size: 50,
})

const search = async () => {
  loading.value = true
  try {
    const params = { ...filters }
    if (dateRange.value) {
      params.period_start = dateRange.value[0]?.toISOString().split('T')[0]
      params.period_end = dateRange.value[1]?.toISOString().split('T')[0]
    }

    // 表格数据(分页)
    const res = await queryData({ ...params, page: filters.page, page_size: filters.page_size })
    tableData.value = res.data || []
    total.value = res.meta?.total || 0

    // 图表数据(全量, 不设pagination限制)
    let chartItems = []
    let cp = 1
    while (true) {
      const cr = await queryData({ ...params, page: cp, page_size: 200 })
      const items = cr.data || []
      chartItems = chartItems.concat(items)
      if (items.length < 200) break
      cp++
    }
    nextTick(() => renderChart(chartItems))
  } catch (e) {
    ElMessage.error('查询失败: ' + (e.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const renderChart = (chartItems) => {
  const data = chartItems || tableData.value
  if (!chartRef.value || data.length === 0) return

  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)

  const groups = {}
  data.forEach(d => {
    const key = (d.indicator_key || d.source_code) + (d.country ? `_${d.country}` : '')
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

const exportCSV = () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('无数据可导出')
    return
  }
  const headers = ['数据源', '指标', '国家', '数值', '发布日期', '期间', '频率', '系列名称']
  const rows = tableData.value.map(r => [
    r.source_code, r.indicator_key, r.country, r.value,
    r.publish_date, r.period_date, r.frequency, r.series_name
  ])
  const csv = [headers.join(','), ...rows.map(r => r.map(v => `"${v ?? ''}"`).join(','))].join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `macro_data_${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(search)

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.macro-data {
  padding: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 24px 0;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  align-items: center;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-container {
  height: 360px;
  background: var(--fdas-card-bg);
  border-radius: 12px;
  border: 1px solid var(--fdas-border);
}

.data-table {
  background: var(--fdas-card-bg);
  border-radius: 12px;
  overflow: hidden;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
