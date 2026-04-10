<template>
  <div class="sidebar-container">
    <!-- Logo区域 -->
    <div class="logo-section" @click="$router.push('/fx-data')">
      <div class="logo-icon">
        <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="20" cy="20" r="18" stroke="#5a8bff" stroke-width="2" fill="none"/>
          <path d="M12 25 L20 15 L28 25" stroke="#2d5af7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="20" cy="20" r="3" fill="#2d5af7"/>
        </svg>
      </div>
      <transition name="fade">
        <span class="logo-text" v-if="!collapsed">FDAS</span>
      </transition>
    </div>

    <!-- 菜单区域 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      background-color="transparent"
      text-color="#e2e8f0"
      active-text-color="#ffffff"
      router
    >
      <el-menu-item index="/fx-data">
        <el-icon><TrendCharts /></el-icon>
        <template #title>数据分析</template>
      </el-menu-item>

      <el-menu-item index="/datasource" v-if="isAdmin">
        <el-icon><Connection /></el-icon>
        <template #title>数据源管理</template>
      </el-menu-item>

      <el-menu-item index="/collection" v-if="isAdmin">
        <el-icon><Timer /></el-icon>
        <template #title>采集任务</template>
      </el-menu-item>

      <el-menu-item index="/users" v-if="isAdmin">
        <el-icon><User /></el-icon>
        <template #title>用户管理</template>
      </el-menu-item>

      <el-menu-item index="/logs" v-if="isAdmin">
        <el-icon><Document /></el-icon>
        <template #title>系统日志</template>
      </el-menu-item>
    </el-menu>

    <!-- 底部折叠按钮 -->
    <div class="sidebar-footer">
      <button class="collapse-btn" @click="$emit('toggle')">
        <el-icon :size="18">
          <Expand v-if="collapsed" />
          <Fold v-else />
        </el-icon>
      </button>
    </div>
  </div>
</template>

<script setup>
/**
 * 侧边栏菜单组件.
 *
 * 根据用户角色动态显示菜单项.
 * 支持折叠/展开功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-10 - 优化侧边栏设计，添加Logo、折叠功能
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { TrendCharts, Connection, Timer, User, Document, Expand, Fold } from '@element-plus/icons-vue'

// Props
defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

// Emits
defineEmits(['toggle'])

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

/* Logo区域 */
.logo-section {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  cursor: pointer;
  transition: all var(--fdas-transition-normal);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-section:hover {
  background: rgba(255, 255, 255, 0.05);
}

.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon svg {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin-left: 12px;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #ffffff 0%, #5a8bff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 菜单样式 */
.el-menu {
  border: none;
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
}

.el-menu:not(.el-menu--collapse) {
  width: 220px;
}

.el-menu-item {
  margin: 4px 12px;
  border-radius: 8px;
  height: 44px;
  line-height: 44px;
  transition: all var(--fdas-transition-fast);
}

.el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.el-menu-item.is-active {
  background: linear-gradient(135deg, var(--fdas-primary) 0%, var(--fdas-primary-light) 100%);
  color: #ffffff;
  font-weight: 500;
}

.el-menu-item .el-icon {
  font-size: 18px;
  margin-right: 12px;
}

/* 折叠状态 */
.el-menu--collapse .el-menu-item {
  margin: 4px 6px;
  padding: 0 !important;
  justify-content: center;
}

/* 底部折叠按钮 */
.sidebar-footer {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px;
}

.collapse-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: #e2e8f0;
  cursor: pointer;
  transition: all var(--fdas-transition-fast);
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

/* 动画过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--fdas-transition-fast);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>