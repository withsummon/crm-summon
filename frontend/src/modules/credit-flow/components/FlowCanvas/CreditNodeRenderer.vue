<template>
  <div
    class="credit-node group relative bg-white rounded-xl border border-gray-200 shadow-sm transition-all duration-200 cursor-pointer"
    :class="[
      selected ? 'ring-2 shadow-lg scale-[1.02]' : 'hover:shadow-md hover:-translate-y-px',
      borderColorClass,
    ]"
    :style="selectedRingStyle"
  >
    <!-- Colored Left Border Accent -->
    <div
      class="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
      :style="{ backgroundColor: nodeColors.accent }"
    />

    <!-- Node Content -->
    <div class="flex items-center gap-3 pl-4 pr-4 py-3 min-w-[220px]">
      <!-- Icon Circle -->
      <div
        class="flex-shrink-0 h-10 w-10 rounded-lg flex items-center justify-center transition-colors duration-200"
        :class="nodeColors.bg"
      >
        <component
          :is="iconComponent"
          v-if="iconComponent"
          class="w-5 h-5"
          :class="nodeColors.text"
        />
      </div>

      <!-- Label & Subtitle -->
      <div class="min-w-0 flex-1">
        <div class="text-sm font-semibold text-gray-800 leading-tight truncate">
          {{ data.label || 'Untitled' }}
        </div>
        <div class="text-[11px] text-gray-400 uppercase tracking-wide font-medium mt-0.5 truncate">
          {{ nodeTypeDef?.label || data.nodeType }}
        </div>
      </div>

      <!-- Status Indicator Dot (optional) -->
      <div
        v-if="data.status"
        class="flex-shrink-0 w-2.5 h-2.5 rounded-full ring-2 ring-white"
        :class="statusDotClass"
        :title="data.status"
      />
    </div>

    <!-- Description (if provided and not too long) -->
    <div
      v-if="data.description && data.description !== nodeTypeDef?.description"
      class="px-4 pb-2.5 -mt-1"
    >
      <p class="text-[11px] text-gray-400 leading-snug line-clamp-2">{{ data.description }}</p>
    </div>

    <!-- Input Handles -->
    <Handle
      v-for="handle in inputHandles"
      :id="handle.id"
      :key="'input-' + handle.id"
      type="target"
      :position="Position.Left"
      class="credit-handle credit-handle-input"
      :style="{ top: handle.position }"
      :title="handle.label"
    />

    <!-- Output Handles -->
    <Handle
      v-for="handle in outputHandles"
      :id="handle.id"
      :key="'output-' + handle.id"
      type="source"
      :position="Position.Right"
      class="credit-handle credit-handle-output"
      :style="{ top: handle.position }"
      :title="handle.label"
    >
      <!-- Handle label badge (shown for multi-output nodes) -->
      <span
        v-if="outputHandles.length > 1"
        class="absolute left-full ml-1.5 whitespace-nowrap text-[9px] font-medium text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"
      >
        {{ handle.label }}
      </span>
    </Handle>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import {
  NODE_TYPES,
  getNodeColors,
  getNodeOutputHandles,
  getNodeInputHandles,
} from '../../data/creditFlowNodeTypes'

// Icons
import LucidePlayCircle from '~icons/lucide/play-circle'
import LucideStopCircle from '~icons/lucide/stop-circle'
import LucideGitBranch from '~icons/lucide/git-branch'
import LucideSkipForward from '~icons/lucide/skip-forward'
import LucideFileText from '~icons/lucide/file-text'
import LucideFolderOpen from '~icons/lucide/folder-open'
import LucideUserPlus from '~icons/lucide/user-plus'
import LucideShieldCheck from '~icons/lucide/shield-check'
import LucideUsers from '~icons/lucide/users'
import LucideUserCheck from '~icons/lucide/user-check'
import LucidePlug from '~icons/lucide/plug'
import LucideBell from '~icons/lucide/bell'
import LucideClock from '~icons/lucide/clock'
import LucideSettings from '~icons/lucide/settings'

const ICON_MAP = {
  'play-circle': LucidePlayCircle,
  'stop-circle': LucideStopCircle,
  'git-branch': LucideGitBranch,
  'skip-forward': LucideSkipForward,
  'file-text': LucideFileText,
  'folder-open': LucideFolderOpen,
  'user-plus': LucideUserPlus,
  'shield-check': LucideShieldCheck,
  'users': LucideUsers,
  'user-check': LucideUserCheck,
  'plug': LucidePlug,
  'bell': LucideBell,
  'clock': LucideClock,
}

const props = defineProps({
  id: { type: String, required: true },
  data: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  dragging: { type: Boolean, default: false },
})

const nodeTypeDef = computed(() => NODE_TYPES[props.data.nodeType] || null)

const nodeColors = computed(() => getNodeColors(props.data.nodeType))

const iconComponent = computed(() => {
  const iconName = nodeTypeDef.value?.icon
  return ICON_MAP[iconName] || LucideSettings
})

const inputHandles = computed(() => getNodeInputHandles(props.data.nodeType))
const outputHandles = computed(() => getNodeOutputHandles(props.data.nodeType))

const borderColorClass = computed(() => {
  if (props.selected) return 'border-transparent'
  return ''
})

const selectedRingStyle = computed(() => {
  if (!props.selected) return {}
  return { '--tw-ring-color': nodeColors.value.accent }
})

const statusDotClass = computed(() => {
  switch (props.data.status) {
    case 'running':
      return 'bg-blue-500 animate-pulse'
    case 'completed':
      return 'bg-primary-500'
    case 'error':
      return 'bg-red-500'
    case 'waiting':
      return 'bg-amber-400'
    case 'skipped':
      return 'bg-gray-400'
    default:
      return 'bg-gray-300'
  }
})
</script>

<style>
.credit-node {
  min-width: 220px;
  max-width: 300px;
}

.credit-handle {
  width: 12px;
  height: 12px;
  border: 2px solid white;
  background: #006699;
  transition: transform 0.15s ease, background-color 0.15s ease;
}

.credit-handle:hover {
  transform: scale(1.3);
  background: #005b8a;
}

.credit-handle-input {
  left: -6px;
}

.credit-handle-output {
  right: -6px;
}

/* Override Vue Flow handle defaults for better visuals */
.credit-node .vue-flow__handle {
  border-radius: 50%;
}
</style>
