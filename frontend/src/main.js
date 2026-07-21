/**
 * Vue应用入口文件.
 *
 * 初始化Vue实例、路由、状态管理、Element Plus等.
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import './styles/index.css'
import { useAuthStore } from './stores/auth'
import { registerAllExtensions } from './chartExtensions/index'

// 注册 KLineChart 自定义扩展（指标、覆盖层、主题）
// 在应用挂载前全局注册，所有 KLineChart 实例共享
registerAllExtensions()

// 创建Vue应用实例
const app = createApp(App)

// 注册Pinia状态管理
const pinia = createPinia()
app.use(pinia)

// 注册Vue Router
app.use(router)

// 注册Element Plus组件库
app.use(ElementPlus)

// 应用初始化：恢复用户登录状态（异步等待完成后再挂载）
async function initializeApp() {
  const authStore = useAuthStore(pinia)
  const sessionId = sessionStorage.getItem('session_id')

  if (sessionId) {
    // 有session_id，尝试恢复用户信息
    try {
      await authStore.fetchUser()
    } catch (error) {
      // 恢复失败，清除session_id
      sessionStorage.removeItem('session_id')
    }
  }

  // 挂载应用
  app.mount('#app')
}

// 启动应用初始化
initializeApp()