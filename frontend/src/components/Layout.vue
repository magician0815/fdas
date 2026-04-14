<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <Sidebar :collapsed="isCollapsed" @toggle="toggleSidebar" />
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <Navbar />
      </el-header>

      <!-- 页面内容 -->
      <el-main class="main">
        <transition name="slide" mode="out-in">
          <router-view />
        </transition>
      </el-main>
    </el-container>

    <!-- 使用帮助按钮 -->
    <HelpButton />
  </div>
</template>

<script setup>
/**
 * 主布局组件.
 *
 * 包含侧边栏、顶部导航栏和主内容区.
 * 支持侧边栏折叠功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-14 - 新增使用帮助按钮组件
 */
import { ref, computed } from 'vue'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import HelpButton from './HelpButton.vue'

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 侧边栏宽度
const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '220px')

// 切换侧边栏
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.sidebar {
  background: linear-gradient(180deg, #1e3a5f 0%, #0f2744 100%);
  height: 100vh;
  transition: width var(--fdas-transition-normal);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--fdas-bg-body);
}

.header {
  background-color: var(--fdas-bg-header);
  border-bottom: 1px solid var(--fdas-border-color);
  display: flex;
  align-items: center;
  padding: 0 var(--fdas-spacing-lg);
  height: 60px;
  box-shadow: var(--fdas-shadow-sm);
  z-index: 10;
}

.main {
  background-color: var(--fdas-bg-body);
  overflow: auto;
  padding: var(--fdas-spacing-lg);
}
</style>