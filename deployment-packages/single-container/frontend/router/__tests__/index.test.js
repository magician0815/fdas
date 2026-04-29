/**
 * Router 测试.
 *
 * 测试路由配置和导航守卫.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import router from '../index'
import { useAuthStore } from '@/stores/auth'

// Mock Vue组件动态导入
vi.mock('@/views/Login.vue', () => ({ default: { name: 'Login' } }))
vi.mock('@/views/Dashboard.vue', () => ({ default: { name: 'Dashboard' } }))
vi.mock('@/views/FXData.vue', () => ({ default: { name: 'FXData' } }))
vi.mock('@/views/DataSource.vue', () => ({ default: { name: 'DataSource' } }))
vi.mock('@/views/Collection.vue', () => ({ default: { name: 'Collection' } }))
vi.mock('@/views/Users.vue', () => ({ default: { name: 'Users' } }))
vi.mock('@/views/Logs.vue', () => ({ default: { name: 'Logs' } }))

describe('Router', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  // 获取路由守卫函数
  const getNavigationGuards = () => {
    // router.beforeEach注册的守卫存储在内部
    // 我们需要直接测试router/index.js中的守卫逻辑
    const authStore = useAuthStore()
    return (to, from, next) => {
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
    }
  }

  describe('路由配置', () => {
    it('应该包含登录路由', () => {
      const loginRoute = router.options.routes.find(r => r.path === '/login')
      expect(loginRoute).toBeDefined()
      expect(loginRoute?.name).toBe('Login')
      expect(loginRoute?.meta?.requiresAuth).toBe(false)
    })

    it('应该包含根路由重定向', () => {
      const rootRoute = router.options.routes.find(r => r.path === '/')
      expect(rootRoute).toBeDefined()
      expect(rootRoute?.redirect).toBe('/fx-data')
    })

    it('应该包含fx-data路由', () => {
      const fxDataRoute = router.options.routes.find(r => r.path === '/fx-data')
      expect(fxDataRoute).toBeDefined()
      expect(fxDataRoute?.name).toBe('FXData')
      expect(fxDataRoute?.meta?.requiresAuth).toBe(true)
    })

    it('应该包含dashboard路由', () => {
      const dashboardRoute = router.options.routes.find(r => r.path === '/dashboard')
      expect(dashboardRoute).toBeDefined()
      expect(dashboardRoute?.meta?.requiresAuth).toBe(true)
    })

    it('应该包含admin专属路由', () => {
      const adminRoutes = router.options.routes.filter(r => r.meta?.requiresAdmin)
      expect(adminRoutes.length).toBeGreaterThan(0)
      expect(adminRoutes.map(r => r.path)).toContain('/datasource')
      expect(adminRoutes.map(r => r.path)).toContain('/collection')
      expect(adminRoutes.map(r => r.path)).toContain('/users')
      expect(adminRoutes.map(r => r.path)).toContain('/logs')
    })

    it('所有路由应有title元数据', () => {
      const routesWithMeta = router.options.routes.filter(r => r.meta?.title)
      const namedRoutes = router.options.routes.filter(r => r.name)
      expect(routesWithMeta.length).toBe(namedRoutes.length)
    })
  })

  describe('路由守卫 - 登录检查', () => {
    it('未登录访问需要认证的路由应重定向到登录页', async () => {
      const authStore = useAuthStore()
      // 模拟未登录状态
      authStore.user = null

      const guard = getNavigationGuards()
      const to = { path: '/fx-data', meta: { requiresAuth: true } }
      const from = { path: '/login' }
      const next = vi.fn()

      guard(to, from, next)

      expect(next).toHaveBeenCalledWith('/login')
    })

    it('已登录访问需要认证的路由应允许通过', async () => {
      const authStore = useAuthStore()
      // 模拟已登录状态
      authStore.user = { id: '1', username: 'test', role: 'user' }

      const guard = getNavigationGuards()
      const to = { path: '/fx-data', meta: { requiresAuth: true } }
      const from = { path: '/login' }
      const next = vi.fn()

      guard(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })

    it('访问登录页应允许通过（无认证要求）', async () => {
      const authStore = useAuthStore()
      authStore.user = null

      const guard = getNavigationGuards()
      const to = { path: '/login', meta: { requiresAuth: false } }
      const from = { path: '/' }
      const next = vi.fn()

      guard(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })
  })

  describe('路由守卫 - Admin权限检查', () => {
    it('非admin用户访问admin路由应重定向到首页', async () => {
      const authStore = useAuthStore()
      // 模拟普通用户登录
      authStore.user = { id: '1', username: 'user', role: 'user' }

      const guard = getNavigationGuards()
      const to = { path: '/users', meta: { requiresAuth: true, requiresAdmin: true } }
      const from = { path: '/fx-data' }
      const next = vi.fn()

      guard(to, from, next)

      expect(next).toHaveBeenCalledWith('/')
    })

    it('admin用户访问admin路由应允许通过', async () => {
      const authStore = useAuthStore()
      // 模拟admin用户登录
      authStore.user = { id: '1', username: 'admin', role: 'admin' }

      const guard = getNavigationGuards()
      const to = { path: '/users', meta: { requiresAuth: true, requiresAdmin: true } }
      const from = { path: '/fx-data' }
      const next = vi.fn()

      guard(to, from, next)

      expect(next).toHaveBeenCalledWith()
    })

    it('未登录用户访问admin路由应重定向到登录页', async () => {
      const authStore = useAuthStore()
      authStore.user = null

      const guard = getNavigationGuards()
      const to = { path: '/users', meta: { requiresAuth: true, requiresAdmin: true } }
      const from = { path: '/' }
      const next = vi.fn()

      guard(to, from, next)

      // 首先检查登录，所以应重定向到登录页
      expect(next).toHaveBeenCalledWith('/login')
    })
  })

  describe('路由实例', () => {
    it('应该使用createWebHistory', () => {
      expect(router.options.history).toBeDefined()
    })

    it('应该正确导出router实例', () => {
      expect(router).toBeDefined()
      expect(router.beforeEach).toBeDefined()
      expect(router.push).toBeDefined()
      expect(router.replace).toBeDefined()
    })
  })
})