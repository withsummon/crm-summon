<template>
  <div
    class="crm-metric-card crm-animate-in"
    :style="{ animationDelay: `${animationDelay}ms` }"
  >
    <div class="flex flex-col justify-between h-full gap-2">
      <div
        class="text-[28px] font-[800] leading-tight tracking-tight"
        :class="valueColorClass"
      >
        {{ displayValue }}
      </div>
      <div class="flex items-center gap-1.5">
        <component
          :is="iconComponent"
          v-if="iconComponent"
          class="w-3.5 h-3.5 text-crm-muted"
        />
        <span class="text-[14px] text-crm-muted font-medium leading-snug">
          {{ __(label) }}
        </span>
      </div>
    </div>
    <!-- Accent strip at bottom -->
    <div
      class="absolute bottom-0 left-0 right-0 h-[3px] rounded-b-[18px]"
      :class="accentStripClass"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LucideUserPlus from '~icons/lucide/user-plus'
import LucideUsers from '~icons/lucide/users'
import LucideFileText from '~icons/lucide/file-text'
import LucideCheckSquare from '~icons/lucide/check-square'
import LucideClipboardList from '~icons/lucide/clipboard-list'
import LucideAlertCircle from '~icons/lucide/alert-circle'

const props = defineProps({
  value: {
    type: [String, Number],
    default: 0,
  },
  label: {
    type: String,
    default: '',
  },
  icon: {
    type: String,
    default: '',
  },
  accentColor: {
    type: String,
    default: 'crm-teal',
  },
  animationDelay: {
    type: Number,
    default: 0,
  },
})

const iconMap = {
  'user-plus': LucideUserPlus,
  'users': LucideUsers,
  'file-text': LucideFileText,
  'check-square': LucideCheckSquare,
  'clipboard-list': LucideClipboardList,
  'alert-circle': LucideAlertCircle,
}

const iconComponent = computed(() => {
  return iconMap[props.icon] || null
})

const displayValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})

const accentColorMap = {
  'crm-teal': 'bg-crm-teal',
  'crm-purple': 'bg-crm-purple',
  'crm-blue': 'bg-crm-blue',
  'crm-green': 'bg-crm-green',
  'crm-pink': 'bg-crm-pink',
}

const valueColorMap = {
  'crm-teal': 'text-crm-text',
  'crm-purple': 'text-crm-text',
  'crm-blue': 'text-crm-text',
  'crm-green': 'text-crm-text',
  'crm-pink': 'text-crm-text',
}

const accentStripClass = computed(() => {
  return accentColorMap[props.accentColor] || 'bg-crm-teal'
})

const valueColorClass = computed(() => {
  return valueColorMap[props.accentColor] || 'text-crm-text'
})
</script>
