<template>
  <div class="help-button-wrapper">
    <!-- 悬浮帮助按钮 -->
    <el-tooltip content="使用帮助" placement="left">
      <el-button
        class="help-float-btn"
        type="primary"
        circle
        size="large"
        @click="openHelpDrawer"
      >
        <el-icon :size="20"><QuestionFilled /></el-icon>
      </el-button>
    </el-tooltip>

    <!-- 帮助内容抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="使用帮助"
      direction="rtl"
      size="40%"
      :append-to-body="true"
    >
      <div class="help-content">
        <!-- 标签页切换 -->
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 图表操作 -->
          <el-tab-pane label="图表操作" name="chart">
            <HelpSection :sections="chartSections" />
          </el-tab-pane>

          <!-- 数据管理 -->
          <el-tab-pane label="数据管理" name="data">
            <HelpSection :sections="dataSections" />
          </el-tab-pane>

          <!-- 快捷键 -->
          <el-tab-pane label="快捷键" name="shortcuts">
            <HelpSection :sections="shortcutSections" />
          </el-tab-pane>
        </el-tabs>

        <!-- 底部提示 -->
        <div class="help-footer">
          <el-alert
            title="提示"
            description="点击各章节标题可展开或收起详细说明。如有疑问，请联系管理员获取更多帮助。"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
/**
 * 使用帮助按钮组件.
 *
 * 在页面右下角显示悬浮帮助按钮，点击打开帮助内容抽屉.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, computed } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import HelpSection from './HelpSection.vue'
import {
  getChartHelpContent,
  getDataManagementHelpContent,
  getShortcutsHelpContent,
  HelpSection as HelpSectionType
} from '@/utils/helpContent'

// 抽屉显示状态
const drawerVisible = ref(false)

// 当前激活的标签页
const activeTab = ref('chart')

// 帮助内容数据
const chartSections = computed(() => getChartHelpContent())
const dataSections = computed(() => getDataManagementHelpContent())
const shortcutSections = computed(() => getShortcutsHelpContent())

/**
 * 打开帮助抽屉.
 */
const openHelpDrawer = () => {
  drawerVisible.value = true
}
</script>

<style scoped>
.help-button-wrapper {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 1000;
}

.help-float-btn {
  width: 48px;
  height: 48px;
  box-shadow: 0 4px 12px rgba(45, 90, 247, 0.4);
  transition: all 0.3s ease;
}

.help-float-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(45, 90, 247, 0.5);
}

.help-content {
  padding: 16px;
  height: calc(100% - 40px);
  overflow-y: auto;
}

.help-footer {
  margin-top: 16px;
}

/* 移动端适配 */
@media (max-width: 576px) {
  .help-button-wrapper {
    right: 10px;
    bottom: 70px;  /* 避开底部导航栏 */
  }

  .help-float-btn {
    width: 40px;
    height: 40px;
  }
}
</style>