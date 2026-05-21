<template>
  <div
    class="crm-card crm-animate-in"
    :style="{ animationDelay: '100ms' }"
  >
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-[16px] font-semibold text-crm-text">{{ __(title) }}</h3>
      <div class="flex items-center gap-1">
        <span class="w-2 h-2 rounded-full bg-crm-orange" />
        <span class="text-[12px] text-crm-muted">{{ __('Active') }}</span>
        <span class="w-2 h-2 rounded-full bg-[#edf0f4] ml-2" />
        <span class="text-[12px] text-crm-muted">{{ __('Remaining') }}</span>
      </div>
    </div>

    <!-- SVG Gauge -->
    <div class="flex items-center justify-center">
      <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`" class="w-full max-w-[280px]">
        <!-- Scale marks -->
        <text
          v-for="mark in scaleMarks"
          :key="mark.label"
          :x="mark.x"
          :y="mark.y"
          text-anchor="middle"
          class="fill-crm-muted"
          font-size="11"
          font-weight="500"
        >
          {{ mark.label }}
        </text>

        <!-- Inactive arc (background) -->
        <path
          :d="inactiveArcPath"
          fill="none"
          stroke="#edf0f4"
          :stroke-width="strokeWidth"
          stroke-linecap="round"
        />

        <!-- Active arc (progress) -->
        <path
          :d="activeArcPath"
          fill="none"
          stroke="#ff8a1f"
          :stroke-width="strokeWidth"
          stroke-linecap="round"
          class="gauge-progress"
          :style="{
            strokeDasharray: activeArcLength,
            strokeDashoffset: activeArcOffset,
          }"
        />

        <!-- Center value -->
        <text
          :x="centerX"
          :y="centerY - 8"
          text-anchor="middle"
          class="fill-crm-text"
          font-size="26"
          font-weight="800"
        >
          ${{ formattedValue }}
        </text>

        <!-- Subtitle -->
        <text
          :x="centerX"
          :y="centerY + 16"
          text-anchor="middle"
          class="fill-crm-muted"
          font-size="12"
          font-weight="500"
        >
          {{ __('Out Of') }} {{ formattedTarget }}
        </text>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: {
    type: Number,
    default: 7580,
  },
  target: {
    type: Number,
    default: 7000,
  },
  title: {
    type: String,
    default: 'Goals',
  },
})

const svgWidth = 280
const svgHeight = 180
const centerX = svgWidth / 2
const centerY = 150
const radius = 110
const strokeWidth = 14

const percentage = computed(() => {
  if (props.target <= 0) return 0
  return Math.min((props.value / props.target) * 100, 100)
})

const formattedValue = computed(() => {
  return props.value.toLocaleString()
})

const formattedTarget = computed(() => {
  return props.target.toLocaleString()
})

// Helper to convert polar to cartesian
function polarToCartesian(cx, cy, r, angleDeg) {
  const angleRad = ((angleDeg - 180) * Math.PI) / 180
  return {
    x: cx + r * Math.cos(angleRad),
    y: cy + r * Math.sin(angleRad),
  }
}

// Generate arc path
function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle)
  const end = polarToCartesian(cx, cy, r, startAngle)
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1'
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`
}

const inactiveArcPath = computed(() => {
  return describeArc(centerX, centerY, radius, 0, 180)
})

const activeArcPath = computed(() => {
  return describeArc(centerX, centerY, radius, 0, 180)
})

// Calculate arc length for stroke-dasharray animation
const totalArcLength = computed(() => {
  return Math.PI * radius // semi-circle
})

const activeArcLength = computed(() => {
  return `${totalArcLength.value}`
})

const activeArcOffset = computed(() => {
  const progress = percentage.value / 100
  return `${totalArcLength.value * (1 - progress)}`
})

// Scale marks at 0, 25, 50, 75, 100
const scaleMarks = computed(() => {
  const marks = [0, 25, 50, 75, 100]
  const labelRadius = radius + 22
  return marks.map((val) => {
    const angle = (val / 100) * 180
    const pos = polarToCartesian(centerX, centerY, labelRadius, angle)
    return {
      label: val,
      x: pos.x,
      y: pos.y + 4,
    }
  })
})
</script>

<style scoped>
.gauge-progress {
  transition: stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
