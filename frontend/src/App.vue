<template>
  <div id="app">
    <!-- 登录页不使用Layout -->
    <transition name="fade" mode="out-in">
      <router-view v-if="isLoginPage" />
      <!-- 其他页面使用Layout -->
      <Layout v-else />
    </transition>
  </div>
</template>

<script setup>
/**
 * 应用根组件.
 *
 * 根据路由判断是否显示Layout.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-10 - 添加路由过渡动画
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'

const route = useRoute()

// 是否为登录页
const isLoginPage = computed(() => route.path === '/login')
</script>

<style>
/* 全局样式已移至 styles/index.css */
</style>