<template>
  <div class="help-sections">
    <el-collapse v-model="activeNames" accordion>
      <el-collapse-item
        v-for="(section, index) in sections"
        :key="index"
        :title="section.title"
        :name="index"
      >
        <div class="section-content">
          <div
            v-for="(item, itemIndex) in section.items"
            :key="itemIndex"
            class="help-item"
          >
            <div class="item-header">
              <span class="item-name">{{ item.name }}</span>
              <span v-if="item.shortcut" class="item-shortcut">{{ item.shortcut }}</span>
              <span v-if="item.icon" class="item-icon">{{ item.icon }}</span>
            </div>
            <div class="item-description">{{ item.description }}</div>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
/**
 * 帮助内容章节渲染组件.
 *
 * 使用折叠面板展示各章节的帮助内容.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref } from 'vue'
import type { HelpSection as HelpSectionType } from '@/utils/helpContent'

interface Props {
  /** 帮助内容章节列表 */
  sections: HelpSectionType[]
}

const props = defineProps<Props>()

// 默认展开第一个章节
const activeNames = ref([0])
</script>

<style scoped>
.help-sections {
  margin-bottom: 16px;
}

.el-collapse {
  border: none;
}

.el-collapse-item__header {
  font-weight: 600;
  color: var(--fdas-text-primary);
  background-color: var(--fdas-gray-50);
  border-radius: 8px;
  margin-bottom: 4px;
}

.el-collapse-item__content {
  padding: 12px 16px;
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.help-item {
  padding: 12px;
  background-color: var(--fdas-bg-card);
  border-radius: 8px;
  border: 1px solid var(--fdas-border-light);
  transition: all 0.2s ease;
}

.help-item:hover {
  border-color: var(--fdas-primary-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.item-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--fdas-primary);
}

.item-shortcut {
  font-size: 12px;
  padding: 2px 8px;
  background-color: var(--fdas-gray-100);
  border-radius: 4px;
  color: var(--fdas-text-secondary);
  font-family: monospace;
}

.item-icon {
  font-size: 14px;
  padding: 2px 8px;
  background-color: var(--fdas-gray-100);
  border-radius: 4px;
  color: var(--fdas-text-secondary);
}

.item-description {
  font-size: 13px;
  color: var(--fdas-text-secondary);
  line-height: 1.6;
}

/* 移动端适配 */
@media (max-width: 576px) {
  .help-item {
    padding: 10px;
  }

  .item-name {
    font-size: 13px;
  }

  .item-description {
    font-size: 12px;
  }
}
</style>