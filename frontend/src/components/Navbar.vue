<template>
  <div class="navbar">
    <!-- 左侧标题 -->
    <div class="left">
      <span class="title">{{ pageTitle }}</span>
    </div>

    <!-- 右侧用户信息 -->
    <div class="right">
      <el-dropdown @command="handleCommand">
        <span class="user-info">
          <el-icon><UserFilled /></el-icon>
          <span class="username">{{ authStore.user?.username || '未登录' }}</span>
          <el-icon class="arrow"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
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
 * 显示页面标题和用户信息.
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserFilled, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 页面标题
const pageTitle = computed(() => route.meta?.title || '首页')

// 处理下拉菜单命令
const handleCommand = async (command) => {
  if (command === 'logout') {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.left {
  display: flex;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.username {
  margin: 0 5px;
}

.arrow {
  font-size: 12px;
}
</style>