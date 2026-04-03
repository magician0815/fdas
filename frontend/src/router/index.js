/**
 * 路由配置模块.
 *
 * 定义应用路由结构和导航守卫.
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/fx-data',
    name: 'FXData',
    component: () => import('@/views/FXData.vue'),
    meta: { requiresAuth: true, title: '数据分析' }
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

// 路由守卫：权限检查
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 检查是否需要登录
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
    return
  }

  // 检查是否需要admin权限
  if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    next('/')
    return
  }

  next()
})

export default router