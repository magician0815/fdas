<template>
  <teleport to="body">
    <transition name="keyboard-spirit-fade">
      <div v-if="visible" class="keyboard-spirit-overlay" @click.self="handleClose">
        <div class="keyboard-spirit-panel" :style="panelStyle">
          <!-- 搜索输入区 -->
          <div class="search-area">
            <el-input
              ref="searchInputRef"
              v-model="searchQuery"
              size="large"
              placeholder="输入代码/名称搜索，或输入命令..."
              clearable
              @input="handleSearch"
              @keydown="handleKeyDown"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <!-- 搜索结果区 -->
          <div class="results-area">
            <div v-if="activeTab === 'symbols'" class="symbols-tab">
              <!-- 常用品种 -->
              <div v-if="searchQuery === '' && recentSymbols.length > 0" class="result-section">
                <div class="section-title">最近使用</div>
                <div class="result-list">
                  <div
                    v-for="(symbol, index) in recentSymbols"
                    :key="`recent-${index}`"
                    class="result-item"
                    :class="{ selected: selectedIndex === index }"
                    @click="handleSelectSymbol(symbol)"
                    @mouseenter="selectedIndex = index"
                  >
                    <span class="item-code">{{ symbol.code }}</span>
                    <span class="item-name">{{ symbol.name }}</span>
                  </div>
                </div>
              </div>

              <!-- 搜索结果 -->
              <div v-if="searchQuery !== '' && filteredSymbols.length > 0" class="result-section">
                <div class="section-title">品种列表</div>
                <div class="result-list">
                  <div
                    v-for="(symbol, index) in filteredSymbols"
                    :key="`symbol-${index}`"
                    class="result-item"
                    :class="{ selected: selectedIndex === index }"
                    @click="handleSelectSymbol(symbol)"
                    @mouseenter="selectedIndex = index"
                  >
                    <span class="item-code">{{ symbol.code }}</span>
                    <span class="item-name">{{ symbol.name }}</span>
                    <span class="item-market">{{ symbol.market }}</span>
                  </div>
                </div>
              </div>

              <!-- 无结果提示 -->
              <div v-if="searchQuery !== '' && filteredSymbols.length === 0" class="no-result">
                <el-icon><Warning /></el-icon>
                <span>未找到匹配的品种</span>
              </div>
            </div>

            <div v-if="activeTab === 'indicators'" class="indicators-tab">
              <div class="result-list">
                <div
                  v-for="(indicator, index) in filteredIndicators"
                  :key="`indicator-${index}`"
                  class="result-item"
                  :class="{ selected: selectedIndex === index }"
                  @click="handleSelectIndicator(indicator)"
                  @mouseenter="selectedIndex = index"
                >
                  <span class="item-name">{{ indicator.name }}</span>
                  <span class="item-desc">{{ indicator.description }}</span>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'commands'" class="commands-tab">
              <div class="result-list">
                <div
                  v-for="(command, index) in filteredCommands"
                  :key="`command-${index}`"
                  class="result-item command-item"
                  :class="{ selected: selectedIndex === index }"
                  @click="handleSelectCommand(command)"
                  @mouseenter="selectedIndex = index"
                >
                  <span class="item-command">{{ command.key }}</span>
                  <span class="item-desc">{{ command.description }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab切换 -->
          <div class="tabs-area">
            <div
              class="tab-item"
              :class="{ active: activeTab === 'symbols' }"
              @click="switchTab('symbols')"
            >
              品种 (S)
            </div>
            <div
              class="tab-item"
              :class="{ active: activeTab === 'indicators' }"
              @click="switchTab('indicators')"
            >
              指标 (I)
            </div>
            <div
              class="tab-item"
              :class="{ active: activeTab === 'commands' }"
              @click="switchTab('commands')"
            >
              命令 (C)
            </div>
          </div>

          <!-- 提示区 -->
          <div class="hint-area">
            <span class="hint-item">
              <kbd>↑↓</kbd> 选择
            </span>
            <span class="hint-item">
              <kbd>Enter</kbd> 确认
            </span>
            <span class="hint-item">
              <kbd>Esc</kbd> 关闭
            </span>
            <span class="hint-item">
              <kbd>S/I/C</kbd> 切换标签
            </span>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
/**
 * 键盘精灵组件.
 *
 * 类似同花顺键盘精灵，快捷键呼出后可搜索品种、指标、执行命令.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */

import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Search, Warning } from '@element-plus/icons-vue'

// Props定义
interface Props {
  /** 是否显示 */
  visible?: boolean
  /** 品种列表 */
  symbols?: Array<{ code: string; name: string; market?: string }>
  /** 指标列表 */
  indicators?: Array<{ name: string; key: string; description?: string }>
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  symbols: () => [
    { code: 'USDCNY', name: '美元人民币', market: '外汇' },
    { code: 'EURCNY', name: '欧元人民币', market: '外汇' },
    { code: 'EURUSD', name: '欧元美元', market: '外汇' },
    { code: 'GBPUSD', name: '英镑美元', market: '外汇' },
    { code: 'USDJPY', name: '美元日元', market: '外汇' },
    { code: 'IF', name: '沪深300股指期货', market: '期货' },
    { code: 'IC', name: '中证500股指期货', market: '期货' },
    { code: 'IH', name: '上证50股指期货', market: '期货' },
    { code: 'AU', name: '黄金期货', market: '期货' },
    { code: 'CU', name: '铜期货', market: '期货' }
  ],
  indicators: () => [
    { name: 'MA均线', key: 'ma', description: '移动平均线' },
    { name: 'MACD', key: 'macd', description: '指数平滑异同移动平均线' },
    { name: 'KDJ', key: 'kdj', description: '随机指标' },
    { name: 'RSI', key: 'rsi', description: '相对强弱指数' },
    { name: 'BOLL', key: 'boll', description: '布林带' },
    { name: 'VOL', key: 'vol', description: '成交量' },
    { name: 'OI', key: 'oi', description: '持仓量（期货）' }
  ]
})

// Emits定义
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'selectSymbol', symbol: { code: string; name: string }): void
  (e: 'selectIndicator', indicator: { name: string; key: string }): void
  (e: 'executeCommand', command: { key: string }): void
}>()

// 状态
const searchQuery = ref<string>('')
const activeTab = ref<string>('symbols')
const selectedIndex = ref<number>(0)
const searchInputRef = ref<any>()
const recentSymbols = ref<Array<{ code: string; name: string }>>([])

// 面板样式
const panelStyle = computed(() => ({
  top: '30%',
  left: '50%',
  transform: 'translateX(-50%)',
  width: '400px',
  maxHeight: '400px'
}))

// 快捷命令列表
const commands = [
  { key: '/daily', description: '切换日线' },
  { key: '/weekly', description: '切换周线' },
  { key: '/monthly', description: '切换月线' },
  { key: '/dark', description: '切换夜间主题' },
  { key: '/light', description: '切换白天主题' },
  { key: '/reset', description: '重置图表' },
  { key: '/export', description: '导出数据' },
  { key: '/fullscreen', description: '全屏模式' },
  { key: '/help', description: '显示帮助' }
]

// 过滤后的品种列表
const filteredSymbols = computed(() => {
  if (!searchQuery.value) return props.symbols

  const query = searchQuery.value.toLowerCase()
  return props.symbols.filter(s =>
    s.code.toLowerCase().includes(query) ||
    s.name.toLowerCase().includes(query)
  )
})

// 过滤后的指标列表
const filteredIndicators = computed(() => {
  if (!searchQuery.value) return props.indicators

  const query = searchQuery.value.toLowerCase()
  return props.indicators.filter(i =>
    i.name.toLowerCase().includes(query) ||
    i.key.toLowerCase().includes(query)
  )
})

// 过滤后的命令列表
const filteredCommands = computed(() => {
  if (!searchQuery.value) return commands

  const query = searchQuery.value.toLowerCase()
  return commands.filter(c =>
    c.key.toLowerCase().includes(query) ||
    c.description.toLowerCase().includes(query)
  )
})

// 当前结果列表
const currentResults = computed(() => {
  if (activeTab.value === 'symbols') {
    return searchQuery.value === '' ? recentSymbols : filteredSymbols
  } else if (activeTab.value === 'indicators') {
    return filteredIndicators
  } else if (activeTab.value === 'commands') {
    return filteredCommands
  }
  return []
})

// 处理搜索
const handleSearch = () => {
  selectedIndex.value = 0
}

// 处理键盘事件
const handleKeyDown = (e: KeyboardEvent) => {
  const resultsLength = currentResults.value.length

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, resultsLength - 1)
      break
    case 'ArrowUp':
      e.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
      break
    case 'Enter':
      e.preventDefault()
      handleConfirmSelection()
      break
    case 'Escape':
      handleClose()
      break
    case 's':
      if (!e.ctrlKey && !e.metaKey && searchQuery.value === '') {
        e.preventDefault()
        switchTab('symbols')
      }
      break
    case 'i':
      if (!e.ctrlKey && !e.metaKey && searchQuery.value === '') {
        e.preventDefault()
        switchTab('indicators')
      }
      break
    case 'c':
      if (!e.ctrlKey && !e.metaKey && searchQuery.value === '') {
        e.preventDefault()
        switchTab('commands')
      }
      break
  }
}

// 切换Tab
const switchTab = (tab: string) => {
  activeTab.value = tab
  selectedIndex.value = 0
}

// 确认选择
const handleConfirmSelection = () => {
  if (currentResults.value.length === 0) return

  const selected = currentResults.value[selectedIndex.value]

  if (activeTab.value === 'symbols') {
    handleSelectSymbol(selected as any)
  } else if (activeTab.value === 'indicators') {
    handleSelectIndicator(selected as any)
  } else if (activeTab.value === 'commands') {
    handleSelectCommand(selected as any)
  }
}

// 选择品种
const handleSelectSymbol = (symbol: { code: string; name: string }) => {
  // 添加到最近使用
  const exists = recentSymbols.value.findIndex(s => s.code === symbol.code)
  if (exists !== -1) {
    recentSymbols.value.splice(exists, 1)
  }
  recentSymbols.value.unshift(symbol)
  recentSymbols.value = recentSymbols.value.slice(0, 10) // 最多保留10个

  // 保存到localStorage
  localStorage.setItem('fdas_recent_symbols', JSON.stringify(recentSymbols.value))

  emit('selectSymbol', symbol)
  handleClose()
}

// 选择指标
const handleSelectIndicator = (indicator: { name: string; key: string }) => {
  emit('selectIndicator', indicator)
  handleClose()
}

// 选择命令
const handleSelectCommand = (command: { key: string; description: string }) => {
  emit('executeCommand', command)
  handleClose()
}

// 关闭面板
const handleClose = () => {
  searchQuery.value = ''
  selectedIndex.value = 0
  emit('close')
}

// 监听显示状态，聚焦输入框
watch(() => props.visible, async (visible) => {
  if (visible) {
    await nextTick()
    searchInputRef.value?.focus()
  }
})

// 初始化最近使用的品种
onMounted(() => {
  const saved = localStorage.getItem('fdas_recent_symbols')
  if (saved) {
    try {
      recentSymbols.value = JSON.parse(saved)
    } catch {
      recentSymbols.value = []
    }
  }
})

// 全局键盘监听
const handleGlobalKeyDown = (e: KeyboardEvent) => {
  // 空格键呼出（非输入状态）
  if (e.key === ' ' && !props.visible && document.activeElement?.tagName !== 'INPUT') {
    e.preventDefault()
    // 这里需要父组件控制visible状态
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeyDown)
})
</script>

<style scoped>
.keyboard-spirit-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.keyboard-spirit-panel {
  background: var(--fdas-bg-card);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.search-area {
  padding: 12px;
  border-bottom: 1px solid var(--fdas-border-light);
}

.results-area {
  max-height: 250px;
  overflow-y: auto;
  padding: 8px;
}

.result-section {
  margin-bottom: 8px;
}

.section-title {
  font-size: 12px;
  color: var(--fdas-text-muted);
  margin-bottom: 4px;
  padding: 4px 8px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.result-item:hover,
.result-item.selected {
  background: var(--fdas-primary-light);
}

.item-code {
  font-weight: 600;
  color: var(--fdas-primary);
  min-width: 80px;
}

.item-name {
  color: var(--fdas-text-primary);
}

.item-market {
  font-size: 12px;
  color: var(--fdas-text-muted);
  margin-left: auto;
}

.item-desc {
  font-size: 12px;
  color: var(--fdas-text-muted);
  margin-left: auto;
}

.command-item .item-command {
  color: var(--fdas-primary);
  font-weight: 500;
  min-width: 100px;
}

.no-result {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: var(--fdas-text-muted);
}

.tabs-area {
  display: flex;
  border-top: 1px solid var(--fdas-border-light);
  border-bottom: 1px solid var(--fdas-border-light);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 8px;
  font-size: 12px;
  color: var(--fdas-text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item:hover {
  background: var(--fdas-bg-secondary);
}

.tab-item.active {
  color: var(--fdas-primary);
  background: var(--fdas-primary-light);
  font-weight: 500;
}

.hint-area {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 8px;
  font-size: 12px;
  color: var(--fdas-text-muted);
}

.hint-item kbd {
  background: var(--fdas-bg-secondary);
  border: 1px solid var(--fdas-border-light);
  border-radius: 3px;
  padding: 2px 6px;
  font-family: monospace;
}

/* 动画 */
.keyboard-spirit-fade-enter-active,
.keyboard-spirit-fade-leave-active {
  transition: opacity 0.2s ease;
}

.keyboard-spirit-fade-enter-from,
.keyboard-spirit-fade-leave-to {
  opacity: 0;
}
</style>