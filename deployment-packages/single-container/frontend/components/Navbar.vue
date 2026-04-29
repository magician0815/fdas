<template>
  <div class="navbar">
    <!-- 左侧标题和面包屑 -->
    <div class="navbar-left">
      <div class="page-info">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <span class="page-subtitle">{{ pageSubtitle }}</span>
      </div>
    </div>

    <!-- 右侧用户信息 -->
    <div class="navbar-right">
      <!-- 主题切换按钮 -->
      <div class="theme-switch" @click="toggleTheme" :title="themeStore.isDark ? '切换白天模式' : '切换夜间模式'">
        <el-icon :size="18">
          <Sunny v-if="themeStore.isDark" />
          <Moon v-else />
        </el-icon>
      </div>

      <!-- 用户信息 -->
      <el-dropdown @command="handleCommand" trigger="click">
        <div class="user-dropdown-trigger">
          <div class="user-avatar">
            <el-icon :size="12"><UserFilled /></el-icon>
          </div>
          <div class="user-info">
            <span class="username">{{ authStore.user?.username || '未登录' }}</span>
            <span class="role-badge" :class="roleClass">{{ roleText }}</span>
          </div>
          <el-icon class="dropdown-arrow" :size="10"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
/**
 * 顶部导航栏组件.
 *
 * 显示页面标题、主题切换按钮和用户信息.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-17 - 新增全局主题切换按钮
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { UserFilled, ArrowDown, SwitchButton, User, Sunny, Moon } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// 页面标题
const pageTitle = computed(() => route.meta?.title || '首页')

// 页面副标题 - 简化版
const pageSubtitle = computed(() => {
  const subtitles = {
    '/fx-data': '',
    '/datasource': '管理数据采集来源',
    '/collection': '配置数据采集任务',
    '/users': '管理系统用户账户',
    '/logs': '查看系统运行日志'
  }
  return subtitles[route.path] || ''
})

// 用户角色文本
const roleText = computed(() => {
  const roles = {
    'admin': '管理员',
    'user': '普通用户'
  }
  return roles[authStore.user?.role] || '未知'
})

// 角色样式类
const roleClass = computed(() => {
  return authStore.user?.role === 'admin' ? 'admin' : 'user'
})

// 切换主题
const toggleTheme = () => {
  themeStore.toggleTheme()
}

// 处理下拉菜单命令
const handleCommand = async (command) => {
  if (command === 'logout') {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } else if (command === 'profile') {
    // TODO: 实现个人信息页面
    ElMessage.info('个人信息功能开发中')
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
}

/* 左侧区域 */
.navbar-left {
  display: flex;
  align-items: center;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--fdas-text-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 11px;
  color: var(--fdas-text-muted);
  border-left: 1px solid var(--fdas-border-color);
  padding-left: 8px;
}

/* 右侧区域 */
.navbar-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 主题切换按钮 */
.theme-switch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background-color: var(--fdas-gray-50);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--fdas-transition-fast);
  color: var(--fdas-text-muted);
}

.theme-switch:hover {
  background-color: var(--fdas-gray-100);
  color: var(--fdas-primary);
}

.theme-switch .el-icon {
  font-size: 12px;
}

/* 夜间模式主题按钮 */
[data-theme="dark"] .theme-switch {
  background-color: var(--fdas-gray-700);
  color: var(--fdas-text-secondary);
}

[data-theme="dark"] .theme-switch:hover {
  background-color: var(--fdas-gray-600);
  color: var(--fdas-primary);
}

/* 用户下拉触发器 */
.user-dropdown-trigger {
  display: flex;
  align-items: center;
  padding: 2px 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--fdas-transition-fast);
  background-color: var(--fdas-gray-50);
}

.user-dropdown-trigger:hover {
  background-color: var(--fdas-gray-100);
}

/* 夜间模式用户触发器 */
[data-theme="dark"] .user-dropdown-trigger {
  background-color: var(--fdas-gray-700);
}

[data-theme="dark"] .user-dropdown-trigger:hover {
  background-color: var(--fdas-gray-600);
}

/* 用户头像 */
.user-avatar {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(135deg, var(--fdas-primary) 0%, var(--fdas-primary-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.user-avatar .el-icon {
  font-size: 12px;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 4px;
}

.username {
  font-size: 10px;
  font-weight: 500;
  color: var(--fdas-text-primary);
}

.role-badge {
  font-size: 9px;
  padding: 0 2px;
  border-radius: 2px;
}

.role-badge.admin {
  background-color: rgba(45, 90, 247, 0.15);
  color: var(--fdas-primary);
}

.role-badge.user {
  background-color: rgba(100, 116, 139, 0.15);
  color: var(--fdas-text-muted);
}

/* 夜间模式角色徽章 */
[data-theme="dark"] .role-badge.admin {
  background-color: rgba(45, 90, 247, 0.25);
  color: var(--fdas-primary-light);
}

/* 下拉箭头 */
.dropdown-arrow {
  color: var(--fdas-text-muted);
  font-size: 10px;
}

/* 下拉菜单项 */
.el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.el-dropdown-menu__item .el-icon {
  font-size: 14px;
}
</style>