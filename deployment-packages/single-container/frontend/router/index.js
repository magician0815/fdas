/**
 * 路由配置模块.
 *
 * 定义应用路由结构和导航守卫.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-17 - 改进路由守卫，等待用户状态恢复
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/',
    redirect: '/fx-data'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true, title: '系统概览' }
  },
  {
    path: '/fx-data',
    name: 'FXData',
    component: () => import('@/views/FXData.vue'),
    meta: { requiresAuth: true, title: '数据分析' }
  },
  {
    path: '/stock-data',
    name: 'StockData',
    component: () => import('@/views/StockData.vue'),
    meta: { requiresAuth: true, title: '股票数据' }
  },
  {
    path: '/futures-data',
    name: 'FuturesData',
    component: () => import('@/views/FuturesData.vue'),
    meta: { requiresAuth: true, title: '期货数据' }
  },
  {
    path: '/bond-data',
    name: 'BondData',
    component: () => import('@/views/BondData.vue'),
    meta: { requiresAuth: true, title: '债券数据' }
  },
  {
    path: '/datasource',
    name: 'DataSource',
    component: () => import('@/views/DataSource.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, title: '数据源管理' }
  },
  {
    path: '/collection',
    name: 'Collection',
    component: () => import('@/views/Collection.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, title: '采集任务' }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, title: '用户管理' }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/Logs.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, title: '系统日志' }
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 用户状态恢复标记
let authInitialized = false
let authInitializing = false

// 路由守卫：权限检查
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const sessionId = sessionStorage.getItem('session_id')

  // 如果有session_id但用户状态未恢复，尝试恢复
  if (sessionId && !authStore.user && !authInitialized && !authInitializing) {
    authInitializing = true
    try {
      await authStore.fetchUser()
      authInitialized = true
    } catch (error) {
      // 恢复失败，清除session_id
      sessionStorage.removeItem('session_id')
    }
    authInitializing = false
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    if (authStore.isLoggedIn) {
      // 已登录，检查admin权限
      if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
        next('/')
        return
      }
      next()
    } else if (sessionId && authInitializing) {
      // 正在初始化，等待
      // 简单处理：允许继续，后续检查
      next()
    } else {
      // 未登录，跳转登录页
      next('/login')
    }
    return
  }

  next()
})

export default router