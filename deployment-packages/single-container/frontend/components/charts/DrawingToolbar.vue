<template>
  <div class="drawing-toolbar">
    <!-- 基础工具选择 -->
    <div class="tool-section">
      <div class="tool-grid">
        <el-tooltip content="直线（点击两点画线）" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'line' }"
            @click="selectTool('line')"
          >
            <svg viewBox="0 0 24 24" width="16" height="16">
              <line x1="4" y1="20" x2="20" y2="4" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="矩形" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'rectangle' }"
            @click="selectTool('rectangle')"
          >
            <svg viewBox="0 0 24 24" width="16" height="16">
              <rect x="4" y="4" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="黄金分割线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'fibonacci' }"
            @click="selectTool('fibonacci')"
          >
            <svg viewBox="0 0 24 24" width="16" height="16">
              <line x1="0" y1="4" x2="24" y2="4" stroke="currentColor" stroke-width="1"/>
              <line x1="0" y1="8" x2="24" y2="8" stroke="currentColor" stroke-width="1"/>
              <line x1="0" y1="12" x2="24" y2="12" stroke="currentColor" stroke-width="2"/>
              <line x1="0" y1="16" x2="24" y2="16" stroke="currentColor" stroke-width="1"/>
              <line x1="0" y1="20" x2="24" y2="20" stroke="currentColor" stroke-width="1"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="平行通道（点击三步）" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'parallelChannel' }"
            @click="selectTool('parallelChannel')"
          >
            <svg viewBox="0 0 24 24" width="16" height="16">
              <line x1="4" y1="8" x2="20" y2="4" stroke="currentColor" stroke-width="2"/>
              <line x1="4" y1="16" x2="20" y2="12" stroke="currentColor" stroke-width="1.5" opacity="0.7"/>
            </svg>
          </button>
        </el-tooltip>
      </div>
    </div>

    <!-- 颜色下拉选择 -->
    <div class="tool-section">
      <el-dropdown trigger="click" placement="bottom-start" @command="selectColor">
        <button class="tool-btn color-btn-dropdown" :style="{ backgroundColor: currentColor }">
          <svg viewBox="0 0 24 24" width="12" height="12">
            <circle cx="12" cy="12" r="6" fill="white"/>
          </svg>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="color in colorOptions"
              :key="color.value"
              :command="color.value"
              :class="{ 'is-active': currentColor === color.value }"
            >
              <span class="color-option">
                <span class="color-dot" :style="{ backgroundColor: color.value }"></span>
                <span>{{ color.name }}</span>
              </span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 粗细下拉选择 -->
    <div class="tool-section">
      <el-dropdown trigger="click" placement="bottom-start" @command="selectLineWidth">
        <button class="tool-btn">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" :stroke-width="Math.min(currentLineWidth, 4)"/>
          </svg>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :command="1" :class="{ 'is-active': currentLineWidth === 1 }">
              <span class="width-option">
                <span class="width-line thin"></span>
                <span>细 (1px)</span>
              </span>
            </el-dropdown-item>
            <el-dropdown-item :command="2" :class="{ 'is-active': currentLineWidth === 2 }">
              <span class="width-option">
                <span class="width-line medium"></span>
                <span>中 (2px)</span>
              </span>
            </el-dropdown-item>
            <el-dropdown-item :command="4" :class="{ 'is-active': currentLineWidth === 4 }">
              <span class="width-option">
                <span class="width-line thick"></span>
                <span>粗 (4px)</span>
              </span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 清除画线按钮 -->
    <div class="tool-section">
      <el-tooltip content="清除所有画线" placement="bottom">
        <el-button size="small" type="danger" @click="clearAllDrawings">
          <el-icon><Delete /></el-icon>
        </el-button>
      </el-tooltip>
    </div>

    <!-- 关闭画线模式 -->
    <div class="tool-section">
      <el-tooltip content="关闭画线工具" placement="bottom">
        <el-button size="small" type="info" @click="closeToolbar">
          关闭
        </el-button>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 画线工具栏组件.
 *
 * 提供画线工具选择、颜色下拉、粗细下拉和清除功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 * Updated: 2026-04-20 - 黄金分割线和平行通道改为独立按钮
 */
import { ref, watch } from 'vue'
import { Delete } from '@element-plus/icons-vue'

// Props定义
interface Props {
  /** 当前选中的工具 */
  tool?: string | null
  /** 当前颜色 */
  color?: string
  /** 当前粗细 */
  lineWidth?: number
}

const props = withDefaults(defineProps<Props>(), {
  tool: null,
  color: '#FF6B6B',
  lineWidth: 4
})

// Emits定义
const emit = defineEmits<{
  (e: 'toolChange', tool: string | null): void
  (e: 'colorChange', color: string): void
  (e: 'lineWidthChange', width: number): void
  (e: 'clearAll'): void
  (e: 'close'): void
}>()

// 状态
const currentTool = ref<string | null>(props.tool)
const currentColor = ref<string>(props.color)
const currentLineWidth = ref<number>(props.lineWidth)

// 颜色选项
const colorOptions = [
  { value: '#FF6B6B', name: '红色' },
  { value: '#4ECDC4', name: '青色' },
  { value: '#FFE66D', name: '黄色' },
  { value: '#95E1D3', name: '绿色' },
  { value: '#F38181', name: '粉色' },
  { value: '#3B82F6', name: '蓝色' },
  { value: '#F59E0B', name: '橙色' },
  { value: '#8B5CF6', name: '紫色' },
]

const selectTool = (tool: string | null) => {
  currentTool.value = tool
  emit('toolChange', tool)
}

const selectColor = (color: string) => {
  currentColor.value = color
  emit('colorChange', color)
}

const selectLineWidth = (width: number) => {
  currentLineWidth.value = width
  emit('lineWidthChange', width)
}

const clearAllDrawings = () => {
  emit('clearAll')
}

const closeToolbar = () => {
  emit('close')
}

watch(() => props.tool, (val) => { currentTool.value = val })
watch(() => props.color, (val) => { currentColor.value = val })
watch(() => props.lineWidth, (val) => { currentLineWidth.value = val })
</script>

<style scoped>
.drawing-toolbar {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-md);
  padding: 8px;
  box-shadow: var(--fdas-shadow-card);
  display: flex;
  gap: 8px;
  align-items: center;
  position: relative;
  z-index: 1000;
}

.tool-section {
  display: flex;
  align-items: center;
  gap: 4px;
  position: relative;
}

.tool-grid {
  display: flex;
  gap: 4px;
}

.tool-btn {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  background: var(--fdas-bg-secondary);
  border: 1px solid var(--fdas-border-light);
  color: var(--fdas-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: var(--fdas-primary-light);
  border-color: var(--fdas-primary);
}

.tool-btn.active {
  background: var(--fdas-primary);
  color: white;
  border-color: var(--fdas-primary);
}

.color-btn-dropdown svg { opacity: 0.8; }

.color-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid var(--fdas-border-light);
}

.width-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.width-line {
  width: 30px;
  height: 3px;
  background: currentColor;
  border-radius: 1px;
}

.width-line.thin { height: 1px; }
.width-line.medium { height: 2px; }
.width-line.thick { height: 4px; }
</style>