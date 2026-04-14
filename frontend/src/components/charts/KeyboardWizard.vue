<template>
  <el-dialog
    v-model="visible"
    title="快速切换"
    width="400px"
    :modal="false"
    @keydown="handleKeydown"
  >
    <el-input
      ref="searchInputRef"
      v-model="searchQuery"
      placeholder="输入名称或代码搜索..."
      clearable
      @input="handleSearch"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>

    <div class="search-results">
      <div
        v-for="(item, index) in filteredItems"
        :key="item.id"
        class="result-item"
        :class="{ active: index === activeIndex }"
        @click="selectItem(item)"
        @mouseenter="activeIndex = index"
      >
        <span class="item-name">{{ item.name }}</span>
        <span class="item-code">{{ item.code }}</span>
      </div>
      <el-empty v-if="!filteredItems.length" description="无匹配结果" :image-size="60" />
    </div>

    <div class="search-hint">
      <span>↑↓ 选择</span>
      <span>Enter 确认</span>
      <span>Esc 关闭</span>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * 键盘精灵组件.
 *
 * 支持品种快速搜索和切换，键盘操作.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, computed, watch, nextTick } from 'vue'
import { Search } from '@element-plus/icons-vue'

// Props定义
interface Props {
  /** 是否显示 */
  modelValue: boolean
  /** 可搜索的项目列表 */
  items: Array<{
    id: string
    name: string
    code: string
  }>
  /** 搜索类型 */
  type?: 'symbol' | 'indicator'
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  items: () => [],
  type: 'symbol'
})

// Emits定义
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'select', item: { id: string; name: string; code: string }): void
}>()

// 搜索输入ref
const searchInputRef = ref<any>(null)

// 状态
const searchQuery = ref('')
const activeIndex = ref(0)

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const filteredItems = computed(() => {
  if (!searchQuery.value) return props.items.slice(0, 10) // 默认显示前10个

  const query = searchQuery.value.toLowerCase()
  return props.items.filter(item => {
    const nameMatch = item.name.toLowerCase().includes(query)
    const codeMatch = item.code.toLowerCase().includes(query)
    return nameMatch || codeMatch
  }).slice(0, 10)
})

// 监听显示状态，自动聚焦输入框
watch(visible, (val) => {
  if (val) {
    searchQuery.value = ''
    activeIndex.value = 0
    nextTick(() => {
      searchInputRef.value?.focus()
    })
  }
})

// 监听过滤结果变化，重置activeIndex
watch(filteredItems, () => {
  activeIndex.value = 0
})

/**
 * 处理搜索输入.
 */
const handleSearch = () => {
  // 搜索时重置选中索引
  activeIndex.value = 0
}

/**
 * 处理键盘事件.
 */
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, filteredItems.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (filteredItems.value.length > 0) {
      selectItem(filteredItems.value[activeIndex.value])
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    visible.value = false
  }
}

/**
 * 选择项目.
 */
const selectItem = (item: { id: string; name: string; code: string }) => {
  emit('select', item)
  visible.value = false
}
</script>

<style scoped>
.search-results {
  margin-top: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.result-item:hover,
.result-item.active {
  background-color: var(--fdas-primary-light);
}

.item-name {
  font-size: 14px;
  color: var(--fdas-text-primary);
}

.item-code {
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.search-hint {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--fdas-border-light);
  font-size: 12px;
  color: var(--fdas-text-muted);
}
</style>