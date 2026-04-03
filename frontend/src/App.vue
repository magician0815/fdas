<template>
  <div id="app">
    <!-- 登录页不使用Layout -->
    <router-view v-if="isLoginPage" />
    <!-- 其他页面使用Layout -->
    <Layout v-else />
  </div>
</template>

<script setup>
/**
 * 应用根组件.
 *
 * 根据路由判断是否显示Layout.
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'

const route = useRoute()

// 是否为登录页
const isLoginPage = computed(() => route.path === '/login')
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  width: 100%;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}
</style>