/**
 * Vitest全局测试配置.
 *
 * 配置全局Mock、Pinia等测试依赖.
 *
 * Author: FDAS Team
 * Created: 2026-04-24
 */

import { createPinia, setActivePinia } from 'pinia'
import { vi } from 'vitest'

// 创建Pinia实例并在测试中激活
const pinia = createPinia()
setActivePinia(pinia)

// 模拟localStorage存储
const localStorageStore: Record<string, string> = {}

// 全局Mock - localStorage (带实际存储功能)
const localStorageMock = {
  getItem: vi.fn((key: string) => localStorageStore[key] || null),
  setItem: vi.fn((key: string, value: string) => { localStorageStore[key] = value }),
  removeItem: vi.fn((key: string) => { delete localStorageStore[key] }),
  clear: vi.fn(() => { Object.keys(localStorageStore).forEach(k => delete localStorageStore[k]) }),
  get length() { return Object.keys(localStorageStore).length },
  key: vi.fn((index: number) => Object.keys(localStorageStore)[index] || null)
}
global.localStorage = localStorageMock as any

// 模拟sessionStorage存储
const sessionStorageStore: Record<string, string> = {}

// 全局Mock - sessionStorage (带实际存储功能)
const sessionStorageMock = {
  getItem: vi.fn((key: string) => sessionStorageStore[key] || null),
  setItem: vi.fn((key: string, value: string) => { sessionStorageStore[key] = value }),
  removeItem: vi.fn((key: string) => { delete sessionStorageStore[key] }),
  clear: vi.fn(() => { Object.keys(sessionStorageStore).forEach(k => delete sessionStorageStore[k]) }),
  get length() { return Object.keys(sessionStorageStore).length },
  key: vi.fn((index: number) => Object.keys(sessionStorageStore)[index] || null)
}
global.sessionStorage = sessionStorageMock as any

// 全局Mock - IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// 全局Mock - ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})