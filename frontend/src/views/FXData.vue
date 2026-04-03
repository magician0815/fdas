<template>
  <div class="fx-data-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>USDCNH 汇率走势</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="fetchData"
          />
        </div>
      </template>

      <!-- 数据图表占位 -->
      <div class="chart-placeholder">
        <el-empty description="暂无数据，请先采集数据">
          <el-button type="primary" @click="fetchData">刷新数据</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 数据分析页面.
 *
 * 展示K线图、均线图、MACD图.
 */
import { ref, onMounted } from 'vue'
import { getFXData, getIndicators } from '@/api/fx_data'

const dateRange = ref([])
const chartData = ref([])

const fetchData = async () => {
  try {
    const response = await getFXData()
    if (response.success) {
      chartData.value = response.data
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.fx-data-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>