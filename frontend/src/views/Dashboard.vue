<template>
  <div class="dashboard-page">
    <h2>欢迎回来，{{ authStore.user?.username }}</h2>
    <p>这是FDAS金融数据抓取与分析系统的首页。</p>
  </div>
</template>

<script setup>
/**
 * 首页.
 */
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
}
</style>