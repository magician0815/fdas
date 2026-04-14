<template>
  <div class="drawing-toolbar">
    <!-- 工具选择 -->
    <div class="tool-section">
      <div class="section-title">画线工具</div>
      <div class="tool-grid">
        <el-tooltip content="趋势线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'trendLine' }"
            @click="selectTool('trendLine')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <line x1="4" y1="20" x2="20" y2="4" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="水平线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'horizontalLine' }"
            @click="selectTool('horizontalLine')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="垂直线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'verticalLine' }"
            @click="selectTool('verticalLine')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <line x1="12" y1="4" x2="12" y2="20" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="矩形" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'rectangle' }"
            @click="selectTool('rectangle')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <rect x="4" y="4" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="文字标注" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'text' }"
            @click="selectTool('text')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <text x="6" y="18" font-size="14" fill="currentColor">T</text>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="上涨箭头" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'arrowUp' }"
            @click="selectTool('arrowUp')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path d="M12 4 L12 20 M8 8 L12 4 L16 8" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="下跌箭头" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'arrowDown' }"
            @click="selectTool('arrowDown')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path d="M12 4 L12 20 M8 16 L12 20 L16 16" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="取消选择" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === null }"
            @click="selectTool(null)"
          >
            <el-icon><Close /></el-icon>
          </button>
        </el-tooltip>
      </div>
    </div>

    <!-- 颜色选择 -->
    <div class="tool-section">
      <div class="section-title">颜色</div>
      <div class="color-grid">
        <button
          v-for="color in colorOptions"
          :key="color"
          class="color-btn"
          :class="{ active: currentColor === color }"
          :style="{ backgroundColor: color }"
          @click="selectColor(color)"
        />
      </div>
      <div class="custom-color">
        <el-color-picker
          v-model="currentColor"
          size="small"
          show-alpha
        />
      </div>
    </div>

    <!-- 粗细选择 -->
    <div class="tool-section">
      <div class="section-title">粗细</div>
      <div class="line-width-grid">
        <button
          v-for="width in lineWidthOptions"
          :key="width"
          class="width-btn"
          :class="{ active: currentLineWidth === width }"
          @click="selectLineWidth(width)"
        >
          <span class="width-line" :style="{ height: `${width}px`, backgroundColor: currentColor }"></span>
        </button>
      </div>
    </div>

    <!-- 专业画线工具 -->
    <div class="tool-section">
      <div class="section-title">专业工具</div>
      <div class="tool-grid">
        <el-tooltip content="黄金分割线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'fibonacci' }"
            @click="selectTool('fibonacci')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <line x1="4" y1="20" x2="20" y2="4" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2,1"/>
              <line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" stroke-width="1" opacity="0.5"/>
              <line x1="4" y1="16" x2="20" y2="8" stroke="currentColor" stroke-width="1" opacity="0.5"/>
              <line x1="4" y1="8" x2="20" y2="16" stroke="currentColor" stroke-width="1" opacity="0.5"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="江恩角度线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'gannLine' }"
            @click="selectTool('gannLine')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <circle cx="4" cy="20" r="2" fill="currentColor"/>
              <line x1="4" y1="20" x2="20" y2="4" stroke="currentColor" stroke-width="1.5"/>
              <line x1="4" y1="20" x2="20" y2="10" stroke="currentColor" stroke-width="1" opacity="0.6"/>
              <line x1="4" y1="20" x2="20" y2="16" stroke="currentColor" stroke-width="1" opacity="0.6"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="安德鲁音叉线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'pitchfork' }"
            @click="selectTool('pitchfork')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <line x1="4" y1="20" x2="12" y2="8" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="14" x2="20" y2="4" stroke="currentColor" stroke-width="1" opacity="0.7"/>
              <line x1="8" y1="14" x2="20" y2="14" stroke="currentColor" stroke-width="1" opacity="0.7"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="斐波那契扇形线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'fibonacciFan' }"
            @click="selectTool('fibonacciFan')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <circle cx="4" cy="20" r="2" fill="currentColor"/>
              <line x1="4" y1="20" x2="20" y2="4" stroke="currentColor" stroke-width="1.5"/>
              <line x1="4" y1="20" x2="20" y2="8" stroke="currentColor" stroke-width="1" opacity="0.6"/>
              <line x1="4" y1="20" x2="20" y2="12" stroke="currentColor" stroke-width="1" opacity="0.6"/>
              <line x1="4" y1="20" x2="20" y2="16" stroke="currentColor" stroke-width="1" opacity="0.6"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="平行通道线" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'parallelChannel' }"
            @click="selectTool('parallelChannel')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <line x1="4" y1="16" x2="20" y2="8" stroke="currentColor" stroke-width="1.5"/>
              <line x1="4" y1="20" x2="20" y2="12" stroke="currentColor" stroke-width="1.5"/>
              <rect x="4" y="16" width="16" height="4" fill="currentColor" opacity="0.1"/>
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip content="波浪线标注" placement="bottom">
          <button
            class="tool-btn"
            :class="{ active: currentTool === 'waveMark' }"
            @click="selectTool('waveMark')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path d="M2 12 Q6 6, 10 12 T18 12" fill="none" stroke="currentColor" stroke-width="1.5"/>
              <text x="4" y="10" font-size="6" fill="currentColor">1</text>
              <text x="10" y="8" font-size="6" fill="currentColor">2</text>
              <text x="16" y="10" font-size="6" fill="currentColor">3</text>
            </svg>
          </button>
        </el-tooltip>
      </div>
    </div>

    <!-- 工具参数配置 -->
    <div v-if="showToolConfig" class="tool-section tool-config">
      <div class="section-title">参数配置</div>

      <!-- 黄金分割线配置 -->
      <div v-if="currentTool === 'fibonacci'" class="config-item">
        <div class="config-label">分割比例</div>
        <div class="config-ratios">
          <el-checkbox-group v-model="fibonacciRatios" size="small">
            <el-checkbox-button label="0.236">0.236</el-checkbox-button>
            <el-checkbox-button label="0.382">0.382</el-checkbox-button>
            <el-checkbox-button label="0.5">0.5</el-checkbox-button>
            <el-checkbox-button label="0.618">0.618</el-checkbox-button>
            <el-checkbox-button label="0.786">0.786</el-checkbox-button>
          </el-checkbox-group>
        </div>
      </div>

      <!-- 江恩角度线配置 -->
      <div v-if="currentTool === 'gannLine'" class="config-item">
        <div class="config-label">角度模式</div>
        <el-select v-model="gannAngleMode" size="small" @change="emitGannConfig">
          <el-option label="标准角度 (1x1, 1x2, 1x4...)" value="standard" />
          <el-option label="时间角度 (15°, 30°, 45°...)" value="time" />
          <el-option label="自定义角度" value="custom" />
        </el-select>
        <div v-if="gannAngleMode === 'custom'" class="config-input">
          <el-input
            v-model="gannCustomAngles"
            size="small"
            placeholder="输入角度，如: 15,30,45,60"
            @change="emitGannConfig"
          />
        </div>
      </div>

      <!-- 安德鲁音叉线配置 -->
      <div v-if="currentTool === 'pitchfork'" class="config-item">
        <div class="config-label">支点模式</div>
        <el-radio-group v-model="pitchforkMode" size="small">
          <el-radio-button label="threePoint">三点式</el-radio-button>
          <el-radio-button label="twoPoint">两点式</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 斐波那契扇形线配置 -->
      <div v-if="currentTool === 'fibonacciFan'" class="config-item">
        <div class="config-label">扇形角度</div>
        <div class="config-ratios">
          <el-checkbox-group v-model="fanAngles" size="small">
            <el-checkbox-button label="38.2">38.2°</el-checkbox-button>
            <el-checkbox-button label="50">50°</el-checkbox-button>
            <el-checkbox-button label="61.8">61.8°</el-checkbox-button>
          </el-checkbox-group>
        </div>
      </div>

      <!-- 平行通道线配置 -->
      <div v-if="currentTool === 'parallelChannel'" class="config-item">
        <div class="config-label">通道宽度</div>
        <el-slider
          v-model="channelWidth"
          :min="5"
          :max="50"
          :step="5"
          size="small"
          show-input
          @change="emitChannelConfig"
        />
      </div>

      <!-- 波浪线标注配置 -->
      <div v-if="currentTool === 'waveMark'" class="config-item">
        <div class="config-label">波浪类型</div>
        <el-radio-group v-model="waveType" size="small">
          <el-radio-button label="elliott">艾略特波浪</el-radio-button>
          <el-radio-button label="simple">简单标注</el-radio-button>
        </el-radio-group>
        <div class="config-label" style="margin-top: 8px;">起点波浪号</div>
        <el-select v-model="waveStartNumber" size="small">
          <el-option label="Ⅰ" value="1" />
          <el-option label="A" value="A" />
          <el-option label="1" value="1n" />
        </el-select>
      </div>
    </div>

    <!-- 磁吸开关 -->
    <div class="tool-section">
      <div class="section-title">磁吸</div>
      <el-switch
        v-model="magnetEnabled"
        size="small"
        active-text="开启"
        inactive-text="关闭"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 画线工具栏组件.
 *
 * 提供画线工具选择、颜色设置、粗细设置等功能.
 *
 * Author: FDAS Team
 * Created: 2026-04-14
 */
import { ref, watch, computed } from 'vue'
import { Close } from '@element-plus/icons-vue'

// Props定义
interface Props {
  /** 当前选中的工具 */
  tool?: string | null
  /** 当前颜色 */
  color?: string
  /** 当前粗细 */
  lineWidth?: number
  /** 磁吸开关 */
  magnet?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  tool: null,
  color: '#FF6B6B',
  lineWidth: 2,
  magnet: true
})

// Emits定义
const emit = defineEmits<{
  (e: 'toolChange', tool: string | null): void
  (e: 'colorChange', color: string): void
  (e: 'lineWidthChange', width: number): void
  (e: 'magnetChange', enabled: boolean): void
  (e: 'toolConfigChange', config: ToolConfig): void
}>()

// 工具配置类型
interface ToolConfig {
  tool: string
  params: Record<string, any>
}

// 状态
const currentTool = ref<string | null>(props.tool)
const currentColor = ref<string>(props.color)
const currentLineWidth = ref<number>(props.lineWidth)
const magnetEnabled = ref<boolean>(props.magnet)

// 专业工具参数配置
const fibonacciRatios = ref<string[]>(['0.236', '0.382', '0.5', '0.618', '0.786'])
const gannAngleMode = ref<string>('standard')
const gannCustomAngles = ref<string>('15,30,45,60,75')
const pitchforkMode = ref<string>('threePoint')
const fanAngles = ref<string[]>(['38.2', '50', '61.8'])
const channelWidth = ref<number>(20)
const waveType = ref<string>('elliott')
const waveStartNumber = ref<string>('1')

// 计算是否显示工具配置面板
const showToolConfig = computed(() => {
  return ['fibonacci', 'gannLine', 'pitchfork', 'fibonacciFan', 'parallelChannel', 'waveMark'].includes(currentTool.value || '')
})

// 预设颜色选项
const colorOptions = [
  '#FF6B6B', // 红
  '#4ECDC4', // 青
  '#FFE66D', // 黄
  '#95E1D3', // 绿
  '#F38181', // 粉红
  '#AA96DA', // 紫
  '#FCBAD3', // 浅粉
  '#FFFFFF', // 白
  '#A8D8EA', // 浅蓝
  '#1A1A2E', // 黑
]

// 粗细选项
const lineWidthOptions = [1, 2, 3, 4, 5]

/**
 * 选择工具.
 */
const selectTool = (tool: string | null) => {
  currentTool.value = tool
  emit('toolChange', tool)

  // 立即发射工具默认配置
  if (tool === 'fibonacci') {
    emitFibonacciConfig()
  } else if (tool === 'gannLine') {
    emitGannConfig()
  } else if (tool === 'pitchfork') {
    emit('toolConfigChange', {
      tool: 'pitchfork',
      params: { mode: pitchforkMode.value }
    })
  } else if (tool === 'fibonacciFan') {
    emit('toolConfigChange', {
      tool: 'fibonacciFan',
      params: { angles: fanAngles.value.map(Number) }
    })
  } else if (tool === 'parallelChannel') {
    emitChannelConfig()
  } else if (tool === 'waveMark') {
    emitWaveConfig()
  }
}

/**
 * 选择颜色.
 */
const selectColor = (color: string) => {
  currentColor.value = color
  emit('colorChange', color)
}

/**
 * 选择粗细.
 */
const selectLineWidth = (width: number) => {
  currentLineWidth.value = width
  emit('lineWidthChange', width)
}

/**
 * 发射黄金分割线配置.
 */
const emitFibonacciConfig = () => {
  emit('toolConfigChange', {
    tool: 'fibonacci',
    params: {
      ratios: fibonacciRatios.value.map(Number)
    }
  })
}

/**
 * 发射江恩角度线配置.
 */
const emitGannConfig = () => {
  let angles: number[] = []
  if (gannAngleMode.value === 'standard') {
    angles = [15, 26.25, 30, 33.75, 45, 56.25, 60, 63.75, 75]
  } else if (gannAngleMode.value === 'time') {
    angles = [15, 30, 45, 60, 75]
  } else if (gannAngleMode.value === 'custom') {
    angles = gannCustomAngles.value.split(',').map(Number).filter(n => !isNaN(n))
  }
  emit('toolConfigChange', {
    tool: 'gannLine',
    params: { angles, mode: gannAngleMode.value }
  })
}

/**
 * 发射平行通道配置.
 */
const emitChannelConfig = () => {
  emit('toolConfigChange', {
    tool: 'parallelChannel',
    params: { width: channelWidth.value }
  })
}

/**
 * 发射波浪线配置.
 */
const emitWaveConfig = () => {
  emit('toolConfigChange', {
    tool: 'waveMark',
    params: {
      type: waveType.value,
      startNumber: waveStartNumber.value
    }
  })
}

/**
 * 监听专业工具参数变化.
 */
watch(fibonacciRatios, () => {
  if (currentTool.value === 'fibonacci') emitFibonacciConfig()
}, { deep: true })

watch(fanAngles, () => {
  if (currentTool.value === 'fibonacciFan') {
    emit('toolConfigChange', {
      tool: 'fibonacciFan',
      params: { angles: fanAngles.value.map(Number) }
    })
  }
}, { deep: true })

watch(pitchforkMode, () => {
  if (currentTool.value === 'pitchfork') {
    emit('toolConfigChange', {
      tool: 'pitchfork',
      params: { mode: pitchforkMode.value }
    })
  }
})

watch(waveType, emitWaveConfig)
watch(waveStartNumber, emitWaveConfig)

// 监听磁吸开关变化
watch(magnetEnabled, (val) => {
  emit('magnetChange', val)
})

// 监听props变化
watch(() => props.tool, (val) => {
  currentTool.value = val
})
watch(() => props.color, (val) => {
  currentColor.value = val
})
watch(() => props.lineWidth, (val) => {
  currentLineWidth.value = val
})
watch(() => props.magnet, (val) => {
  magnetEnabled.value = val
})
</script>

<style scoped>
.drawing-toolbar {
  background: var(--fdas-bg-card);
  border-radius: var(--fdas-radius-md);
  padding: 8px;
  box-shadow: var(--fdas-shadow-card);
  min-width: 160px;
}

/* 工具区域 */
.tool-section {
  margin-bottom: 12px;
}

.section-title {
  font-size: 12px;
  color: var(--fdas-text-muted);
  margin-bottom: 6px;
}

/* 工具网格 */
.tool-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
}

.tool-btn {
  width: 32px;
  height: 32px;
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

/* 颜色网格 */
.color-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
}

.color-btn {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.color-btn:hover {
  transform: scale(1.1);
}

.color-btn.active {
  border-color: var(--fdas-primary);
  box-shadow: 0 0 0 2px rgba(var(--fdas-primary-rgb), 0.3);
}

.custom-color {
  margin-top: 6px;
}

/* 粗细网格 */
.line-width-grid {
  display: flex;
  gap: 6px;
}

.width-btn {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  background: var(--fdas-bg-secondary);
  border: 1px solid var(--fdas-border-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.width-btn:hover {
  background: var(--fdas-primary-light);
  border-color: var(--fdas-primary);
}

.width-btn.active {
  background: var(--fdas-primary-light);
  border-color: var(--fdas-primary);
}

.width-line {
  width: 20px;
  border-radius: 2px;
}

/* 工具配置面板 */
.tool-config {
  border-top: 1px solid var(--fdas-border-light);
  padding-top: 8px;
}

.config-item {
  margin-bottom: 8px;
}

.config-label {
  font-size: 12px;
  color: var(--fdas-text-muted);
  margin-bottom: 4px;
}

.config-ratios {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.config-input {
  margin-top: 6px;
}

/* 调整checkbox按钮样式 */
.el-checkbox-button {
  margin-right: 4px;
}

.el-checkbox-button__inner {
  padding: 4px 8px;
  font-size: 12px;
}
</style>