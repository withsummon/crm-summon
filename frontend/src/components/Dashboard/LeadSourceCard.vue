<template>
  <div
    class="crm-card crm-animate-in"
    :style="{ animationDelay: '150ms' }"
  >
    <!-- Header -->
    <div class="flex items-center justify-between mb-5">
      <h3 class="text-[16px] font-semibold text-crm-text">
        {{ __('Lead Source') }}
      </h3>
      <div class="flex items-center gap-3">
        <div
          v-for="source in sources"
          :key="source.label"
          class="flex items-center gap-1.5"
        >
          <span
            class="w-2.5 h-2.5 rounded-full"
            :style="{ backgroundColor: source.color }"
          />
          <span class="text-[12px] text-crm-muted font-medium">
            {{ __(source.label) }}
          </span>
        </div>
      </div>
    </div>

    <div class="flex items-start gap-6">
      <!-- Bubble Timeline (left) -->
      <div class="flex-1 overflow-hidden">
        <svg :viewBox="`0 0 ${bubbleWidth} ${bubbleHeight}`" class="w-full">
          <!-- Month labels -->
          <text
            v-for="(month, i) in months"
            :key="month"
            :x="bubblePadLeft + i * colSpacing"
            :y="bubbleHeight - 4"
            text-anchor="middle"
            class="fill-crm-muted"
            font-size="9"
            font-weight="500"
          >
            {{ month }}
          </text>

          <!-- Row labels -->
          <text
            v-for="(source, rowIdx) in sources"
            :key="'label-' + source.label"
            x="4"
            :y="bubblePadTop + rowIdx * rowSpacing + 4"
            class="fill-crm-muted"
            font-size="8"
            font-weight="500"
          >
            {{ source.short }}
          </text>

          <!-- Bubbles -->
          <circle
            v-for="(bubble, idx) in bubbleData"
            :key="idx"
            :cx="bubble.cx"
            :cy="bubble.cy"
            :r="bubble.r"
            :fill="bubble.color"
            :opacity="0.7"
            class="transition-all duration-300 hover:opacity-100"
          >
            <title>{{ bubble.tooltip }}</title>
          </circle>
        </svg>
      </div>

      <!-- Ring Chart (right) -->
      <div class="flex flex-col items-center gap-3 min-w-[140px]">
        <svg viewBox="0 0 120 120" class="w-[120px] h-[120px]">
          <circle
            v-for="(seg, idx) in ringSegments"
            :key="idx"
            cx="60"
            cy="60"
            :r="ringRadius"
            fill="none"
            :stroke="seg.color"
            :stroke-width="ringStroke"
            :stroke-dasharray="seg.dashArray"
            :stroke-dashoffset="seg.dashOffset"
            stroke-linecap="round"
            class="ring-segment"
            :style="{ animationDelay: `${idx * 200 + 400}ms` }"
          />
          <!-- Center total -->
          <text
            x="60"
            y="56"
            text-anchor="middle"
            class="fill-crm-text"
            font-size="14"
            font-weight="800"
          >
            {{ totalLeads.toLocaleString() }}
          </text>
          <text
            x="60"
            y="70"
            text-anchor="middle"
            class="fill-crm-muted"
            font-size="8"
            font-weight="500"
          >
            {{ __('Total') }}
          </text>
        </svg>

        <!-- Legend values -->
        <div class="flex flex-col gap-1.5 w-full">
          <div
            v-for="source in sources"
            :key="'legend-' + source.label"
            class="flex items-center justify-between text-[12px]"
          >
            <div class="flex items-center gap-1.5">
              <span
                class="w-2 h-2 rounded-full"
                :style="{ backgroundColor: source.color }"
              />
              <span class="text-crm-muted">{{ __(source.label) }}</span>
            </div>
            <span class="font-semibold text-crm-text">
              {{ source.value.toLocaleString() }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const sources = [
  { label: 'Email Pursing', short: 'Email', value: 7896, color: '#ff8a1f' },
  { label: 'API', short: 'API', value: 325, color: '#b77cff' },
  { label: 'Lead Scrap', short: 'Scrap', value: 24, color: '#6676ff' },
]

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const bubbleWidth = 420
const bubbleHeight = 130
const bubblePadLeft = 40
const bubblePadTop = 20
const colSpacing = (bubbleWidth - bubblePadLeft - 10) / 11
const rowSpacing = 32

// Generate pseudo-random bubble sizes based on source weights
const bubbleRawData = [
  // Email row (high volume)
  [8, 6, 9, 7, 10, 8, 7, 9, 6, 8, 10, 7],
  // API row (medium)
  [3, 4, 2, 5, 3, 4, 2, 3, 5, 4, 3, 2],
  // Lead Scrap row (low)
  [1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1],
]

const maxBubbleRadius = 10
const minBubbleRadius = 2

const bubbleData = computed(() => {
  const allValues = bubbleRawData.flat()
  const maxVal = Math.max(...allValues)
  const result = []

  bubbleRawData.forEach((row, rowIdx) => {
    row.forEach((val, colIdx) => {
      const normalizedR = minBubbleRadius + ((val / maxVal) * (maxBubbleRadius - minBubbleRadius))
      result.push({
        cx: bubblePadLeft + colIdx * colSpacing,
        cy: bubblePadTop + rowIdx * rowSpacing,
        r: normalizedR,
        color: sources[rowIdx].color,
        tooltip: `${sources[rowIdx].label} - ${months[colIdx]}: ${val}`,
      })
    })
  })

  return result
})

// Ring chart
const totalLeads = computed(() => sources.reduce((sum, s) => sum + s.value, 0))
const ringRadius = 44
const ringStroke = 10
const ringCircumference = 2 * Math.PI * ringRadius

const ringSegments = computed(() => {
  const total = totalLeads.value
  let currentOffset = 0
  const gap = 4 // small gap between segments

  return sources.map((source) => {
    const fraction = source.value / total
    const segmentLength = fraction * ringCircumference - gap
    const dashArray = `${Math.max(segmentLength, 0)} ${ringCircumference}`
    const dashOffset = -currentOffset
    currentOffset += fraction * ringCircumference

    return {
      color: source.color,
      dashArray,
      dashOffset,
    }
  })
})
</script>

<style scoped>
.ring-segment {
  transform-origin: center;
  transform: rotate(-90deg);
  animation: ring-draw 1s ease-out forwards;
}

@keyframes ring-draw {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
