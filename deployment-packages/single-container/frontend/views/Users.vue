<template>
  <div class="users-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">管理系统用户账户和权限</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          <span>创建用户</span>
        </el-button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="table-panel">
      <el-table :data="users" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="username" label="用户名" width="200">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="user-avatar">
                <el-icon><UserFilled /></el-icon>
              </div>
              <span class="username">{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <span class="role-badge" :class="row.role">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="180">
          <template #default="{ row }">
            {{ row.last_login ? formatDate(row.last_login) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="editUser(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" text type="danger" @click="deleteUser(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!users.length && !loading" description="暂无用户数据">
        <el-button type="primary" @click="showCreateDialog">创建第一个用户</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
/**
 * 用户管理页面.
 *
 * 管理系统用户（仅管理员）.
 *
 * Author: FDAS Team
 * Created: 2026-04-03
 * Updated: 2026-04-10 - 优化页面设计
 */
import { ref, onMounted } from 'vue'
import { Plus, UserFilled, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const users = ref([])

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 显示创建对话框
const showCreateDialog = () => {
  ElMessage.info('创建用户功能开发中')
}

// 编辑用户
const editUser = (user) => {
  ElMessage.info('编辑用户功能开发中')
}

// 删除用户
const deleteUser = (user) => {
  ElMessage.info('删除用户功能开发中')
}

onMounted(() => {
  // 模拟数据
  users.value = [
    { username: 'admin', role: 'admin', created_at: '2026-04-01T10:00:00', last_login: '2026-04-10T08:30:00' },
    { username: 'user1', role: 'user', created_at: '2026-04-03T14:00:00', last_login: '2026-04-09T16:00:00' },
  ]
})
</script>

<style scoped>
.users-page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--fdas-spacing-lg);
}

.header-left {
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--fdas-text-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 13px;
  color: var(--fdas-text-muted);
  margin-top: 4px;
}

/* 用户单元格 */
.user-cell {
  display: flex;
  align-items: center;
  gap: var(--fdas-spacing-sm);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--fdas-primary) 0%, var(--fdas-primary-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 16px;
}

.username {
  font-weight: 500;
}

/* 角色徽章 */
.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background: rgba(45, 90, 247, 0.1);
  color: var(--fdas-primary);
}

.role-badge.user {
  background: rgba(100, 116, 139, 0.1);
  color: var(--fdas-text-muted);
}

/* 表格面板 */
.table-panel {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-lg);
  padding: var(--fdas-spacing-lg);
  box-shadow: var(--fdas-shadow-card);
}
</style>