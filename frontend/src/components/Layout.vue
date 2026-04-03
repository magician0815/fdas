<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <Sidebar />
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <Navbar />
      </el-header>

      <!-- 页面内容 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
/**
 * 主布局组件.
 *
 * 包含侧边栏、顶部导航栏和主内容区.
 */
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  width: 100%;
}

.sidebar {
  background-color: #304156;
  height: 100vh;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 50px;
}

.main {
  background-color: #f0f2f5;
  overflow: auto;
}
</style>