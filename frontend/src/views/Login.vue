<template>
  <div class="login-container">
    <!-- 左侧装饰区域 -->
    <div class="login-decoration">
      <div class="decoration-content">
        <!-- Logo -->
        <div class="logo-large">
          <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="40" r="36" stroke="#5a8bff" stroke-width="3" fill="none"/>
            <path d="M24 50 L40 30 L56 50" stroke="#2d5af7" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="40" cy="40" r="5" fill="#2d5af7"/>
          </svg>
        </div>
        <h1 class="decoration-title">FDAS</h1>
        <p class="decoration-subtitle">金融数据抓取与分析系统</p>

        <!-- 功能亮点 -->
        <div class="features-list">
          <div class="feature-item">
            <el-icon><TrendCharts /></el-icon>
            <span>实时行情数据采集</span>
          </div>
          <div class="feature-item">
            <el-icon><Connection /></el-icon>
            <span>多数据源支持</span>
          </div>
          <div class="feature-item">
            <el-icon><Timer /></el-icon>
            <span>智能定时任务</span>
          </div>
          <div class="feature-item">
            <el-icon><DataAnalysis /></el-icon>
            <span>技术指标分析</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-form-section">
      <div class="login-form-container">
        <div class="form-header">
          <h2 class="form-title">登录系统</h2>
          <p class="form-subtitle">请输入您的账户信息</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" class="login-form">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名"
              size="large"
              class="login-input"
            >
              <template #prefix>
                <el-icon class="input-icon"><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              class="login-input"
              show-password
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <el-icon class="input-icon"><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              @click="handleLogin"
              :loading="loading"
              class="login-button"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 底部信息 -->
        <div class="form-footer">
          <p class="footer-text">
            <el-icon><InfoFilled /></el-icon>
            需要帮助请联系管理员
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 登录页面.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-10 - 优化登录页设计，添加装饰区域
 */
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { User, Lock, TrendCharts, Connection, Timer, DataAnalysis, InfoFilled } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const result = await authStore.login(form.username, form.password)
    if (result.success) {
      ElMessage.success('登录成功')
      const redirect = route.query.redirect || '/fx-data'
      router.push(redirect)
    } else {
      ElMessage.error(result.message || '用户名或密码错误')
    }
  } catch (error) {
    ElMessage.error('登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
  background-color: var(--fdas-bg-body);
}

/* 左侧装饰区域 */
.login-decoration {
  flex: 1;
  background: linear-gradient(135deg, #1e3a5f 0%, #0f2744 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--fdas-spacing-2xl);
  position: relative;
  overflow: hidden;
}

.login-decoration::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
}

.decoration-content {
  text-align: center;
  color: #ffffff;
  position: relative;
  z-index: 1;
}

.logo-large {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--fdas-spacing-lg);
}

.logo-large svg {
  width: 100%;
  height: 100%;
}

.decoration-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 2px;
}

.decoration-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin-top: var(--fdas-spacing-sm);
}

/* 功能亮点 */
.features-list {
  display: flex;
  flex-direction: column;
  gap: var(--fdas-spacing-md);
  margin-top: var(--fdas-spacing-xl);
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
  font-size: 14px;
  opacity: 0.9;
}

.feature-item .el-icon {
  font-size: 20px;
  color: #5a8bff;
}

/* 右侧登录表单区域 */
.login-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--fdas-spacing-2xl);
  background-color: var(--fdas-bg-body);
}

.login-form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: var(--fdas-spacing-xl);
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--fdas-text-primary);
  margin: 0;
}

.form-subtitle {
  font-size: 14px;
  color: var(--fdas-text-muted);
  margin-top: var(--fdas-spacing-sm);
}

/* 登录表单 */
.login-form {
  margin-top: var(--fdas-spacing-lg);
}

.login-input {
  height: 48px;
}

.input-icon {
  color: var(--fdas-text-muted);
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--fdas-radius-md);
}

/* 底部信息 */
.form-footer {
  margin-top: var(--fdas-spacing-lg);
  text-align: center;
}

.footer-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--fdas-spacing-xs);
  font-size: 13px;
  color: var(--fdas-text-muted);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-decoration {
    display: none;
  }

  .login-form-section {
    padding: var(--fdas-spacing-lg);
  }

  .login-form-container {
    max-width: 100%;
  }
}
</style>