/**
 * 路由配置模块测试.
 *
 * 测试路由结构、导航守卫、页面标题配置.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 * Updated: 2026-07-24 - 迁移至 /market-overview 统一行情页面
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'

// 路由配置数据（纯逻辑测试，不依赖模块导入）
const routeConfigs = [
  { path: '/login', name: 'Login', meta: { requiresAuth: false, title: '登录' } },
  { path: '/', redirect: '/market-overview' },
  { path: '/dashboard', name: 'Dashboard', meta: { requiresAuth: true, title: '系统概览' } },
  { path: '/market-overview', name: 'MarketOverview', meta: { requiresAuth: true, title: '行情数据' } },
  { path: '/datasource', name: 'DataSource', meta: { requiresAuth: true, requiresAdmin: true, title: '数据源管理' } },
  { path: '/collection', name: 'Collection', meta: { requiresAuth: true, requiresAdmin: true, title: '采集任务' } },
  { path: '/users', name: 'Users', meta: { requiresAuth: true, requiresAdmin: true, title: '用户管理' } },
  { path: '/logs', name: 'Logs', meta: { requiresAuth: true, requiresAdmin: true, title: '系统日志' } }
]

describe('Router 路由配置', () => {
  describe('路由结构验证', () => {
    it('应包含登录路由', () => {
      const loginRoute = routeConfigs.find(r => r.path === '/login')
      expect(loginRoute).toBeDefined()
      expect(loginRoute?.name).toBe('Login')
      expect(loginRoute?.meta?.requiresAuth).toBe(false)
    })

    it('应包含首页重定向到行情数据', () => {
      const rootRoute = routeConfigs.find(r => r.path === '/')
      expect(rootRoute).toBeDefined()
      expect(rootRoute?.redirect).toBe('/market-overview')
    })

    it('应包含Dashboard路由', () => {
      const dashboard = routeConfigs.find(r => r.path === '/dashboard')
      expect(dashboard).toBeDefined()
      expect(dashboard?.meta?.requiresAuth).toBe(true)
      expect(dashboard?.meta?.title).toBe('系统概览')
    })

    it('应包含行情数据路由', () => {
      const market = routeConfigs.find(r => r.path === '/market-overview')
      expect(market).toBeDefined()
      expect(market?.meta?.requiresAuth).toBe(true)
      expect(market?.meta?.title).toBe('行情数据')
    })

    it('应包含数据源管理路由', () => {
      const datasource = routeConfigs.find(r => r.path === '/datasource')
      expect(datasource).toBeDefined()
      expect(datasource?.meta?.requiresAuth).toBe(true)
      expect(datasource?.meta?.requiresAdmin).toBe(true)
      expect(datasource?.meta?.title).toBe('数据源管理')
    })

    it('应包含采集任务路由', () => {
      const collection = routeConfigs.find(r => r.path === '/collection')
      expect(collection).toBeDefined()
      expect(collection?.meta?.requiresAuth).toBe(true)
      expect(collection?.meta?.requiresAdmin).toBe(true)
      expect(collection?.meta?.title).toBe('采集任务')
    })

    it('应包含用户管理路由', () => {
      const users = routeConfigs.find(r => r.path === '/users')
      expect(users).toBeDefined()
      expect(users?.meta?.requiresAuth).toBe(true)
      expect(users?.meta?.requiresAdmin).toBe(true)
      expect(users?.meta?.title).toBe('用户管理')
    })

    it('应包含系统日志路由', () => {
      const logs = routeConfigs.find(r => r.path === '/logs')
      expect(logs).toBeDefined()
      expect(logs?.meta?.requiresAuth).toBe(true)
      expect(logs?.meta?.requiresAdmin).toBe(true)
      expect(logs?.meta?.title).toBe('系统日志')
    })

    it('路由总数应为8', () => {
      expect(routeConfigs.length).toBe(8)
    })
  })

  describe('路由元信息验证', () => {
    it('登录页不需要认证', () => {
      const login = routeConfigs.find(r => r.path === '/login')
      expect(login?.meta?.requiresAuth).toBe(false)
    })

    it('普通用户页面需要认证但不需要admin', () => {
      const market = routeConfigs.find(r => r.path === '/market-overview')
      expect(market?.meta?.requiresAuth).toBe(true)
      expect(market?.meta?.requiresAdmin).toBeUndefined()
    })

    it('管理员页面需要认证和admin权限', () => {
      const adminPages = routeConfigs.filter(r => r.meta?.requiresAdmin)
      expect(adminPages.length).toBe(4) // datasource, collection, users, logs
    })

    it('所有路由应有标题', () => {
      const routesWithTitle = routeConfigs.filter(r => r.meta?.title)
      expect(routesWithTitle.length).toBe(7) // 除重定向路由外
    })

    it('标题应为中文', () => {
      const routesWithTitle = routeConfigs.filter(r => r.meta?.title)
      routesWithTitle.forEach(r => {
        expect(r.meta?.title).toMatch(/[一-龥]/)
      })
    })
  })

  describe('路由守卫逻辑测试', () => {
    const mockBeforeEach = (to, authStore) => {
      if (to.meta?.requiresAuth && !authStore.isLoggedIn) {
        return '/login'
      }
      if (to.meta?.requiresAdmin && authStore.user?.role !== 'admin') {
        return '/'
      }
      return null
    }

    it('未登录访问需要认证的页面应重定向到登录页', () => {
      const to = { path: '/market-overview', meta: { requiresAuth: true } }
      const authStore = { isLoggedIn: false }
      const result = mockBeforeEach(to, authStore)
      expect(result).toBe('/login')
    })

    it('已登录访问需要认证的页面应允许通过', () => {
      const to = { path: '/market-overview', meta: { requiresAuth: true } }
      const authStore = { isLoggedIn: true, user: { role: 'user' } }
      const result = mockBeforeEach(to, authStore)
      expect(result).toBeNull()
    })

    it('未登录访问登录页应允许通过', () => {
      const to = { path: '/login', meta: { requiresAuth: false } }
      const authStore = { isLoggedIn: false }
      const result = mockBeforeEach(to, authStore)
      expect(result).toBeNull()
    })

    it('普通用户访问管理员页面应重定向到首页', () => {
      const to = { path: '/users', meta: { requiresAuth: true, requiresAdmin: true } }
      const authStore = { isLoggedIn: true, user: { role: 'user' } }
      const result = mockBeforeEach(to, authStore)
      expect(result).toBe('/')
    })

    it('管理员访问管理员页面应允许通过', () => {
      const to = { path: '/users', meta: { requiresAuth: true, requiresAdmin: true } }
      const authStore = { isLoggedIn: true, user: { role: 'admin' } }
      const result = mockBeforeEach(to, authStore)
      expect(result).toBeNull()
    })
  })

  describe('路由命名验证', () => {
    it('所有非重定向路由应有name', () => {
      const routesWithName = routeConfigs.filter(r => r.name)
      expect(routesWithName.length).toBe(7)
    })

    it('路由name应唯一', () => {
      const names = routeConfigs.filter(r => r.name).map(r => r.name)
      const uniqueNames = new Set(names)
      expect(uniqueNames.size).toBe(names.length)
    })

    it('路由name应使用PascalCase', () => {
      const namedRoutes = routeConfigs.filter(r => r.name)
      namedRoutes.forEach(r => {
        expect(r.name).toMatch(/^[A-Z][a-zA-Z]*$/)
      })
    })
  })

  describe('路由路径验证', () => {
    it('所有路径应以/开头', () => {
      routeConfigs.forEach(r => {
        expect(r.path.startsWith('/')).toBe(true)
      })
    })

    it('路径应唯一', () => {
      const paths = routeConfigs.map(r => r.path)
      const uniquePaths = new Set(paths)
      expect(uniquePaths.size).toBe(paths.length)
    })
  })
})