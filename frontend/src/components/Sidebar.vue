<template>
  <div class="sidebar-container">
    <!-- Logo -->
    <div class="logo">
      <h1>FDAS</h1>
    </div>

    <!-- 菜单 -->
    <el-menu
      :default-active="activeMenu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/fx-data">
        <el-icon><TrendCharts /></el-icon>
        <span>数据分析</span>
      </el-menu-item>

      <el-menu-item index="/datasource" v-if="isAdmin">
        <el-icon><Connection /></el-icon>
        <span>数据源管理</span>
      </el-menu-item>

      <el-menu-item index="/collection" v-if="isAdmin">
        <el-icon><Timer /></el-icon>
        <span>采集任务</span>
      </el-menu-item>

      <el-menu-item index="/users" v-if="isAdmin">
        <el-icon><User /></el-icon>
        <span>用户管理</span>
      </el-menu-item>

      <el-menu-item index="/logs" v-if="isAdmin">
        <el-icon><Document /></el-icon>
        <span>系统日志</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
/**
 * 侧边栏菜单组件.
 *
 * 根据用户角色动态显示菜单项.
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { TrendCharts, Connection, Timer, User, Document } from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

// 当前激活菜单
const activeMenu = computed(() => route.path)

// 是否为管理员
const isAdmin = computed(() => authStore.user?.role === 'admin')
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
}

.logo h1 {
  color: #fff;
  font-size: 18px;
  margin: 0;
}

.el-menu {
  border-right: none;
  flex: 1;
}
</style>