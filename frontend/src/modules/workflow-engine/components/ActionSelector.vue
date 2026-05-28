<template>
  <div class="space-y-4 p-3 bg-surface-gray-1/40 rounded-xl border border-crm-border">
    <div class="flex items-center justify-between">
      <span class="text-[10px] font-bold text-crm-muted uppercase tracking-wider">{{ label || __('Configure Available Actions') }}</span>
      <span class="text-[9px] bg-purple-100 text-purple-700 px-2 py-0.5 rounded font-bold font-mono">
        {{ selectedActions.length }} {{ __('selected') }}
      </span>
    </div>

    <!-- Grouped Actions Layout -->
    <div class="space-y-3.5">
      <div
        v-for="group in actionGroups"
        :key="group.id"
        class="space-y-1.5"
      >
        <h4 class="text-[9px] font-bold text-crm-muted uppercase tracking-wider px-1">
          {{ __(group.name) }}
        </h4>

        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="action in group.items"
            :key="action.id"
            type="button"
            class="flex items-center gap-2 p-2 rounded-lg border text-left text-xs font-medium transition-all"
            :class="[
              isSelected(action.id)
                ? 'bg-purple-50 border-purple-300 text-purple-700 shadow-sm ring-1 ring-purple-300'
                : 'bg-white border-crm-border text-crm-text hover:border-gray-300 hover:bg-surface-gray-1'
            ]"
            @click="toggleAction(action.id)"
          >
            <div
              class="p-1 rounded shrink-0"
              :class="isSelected(action.id) ? 'bg-purple-100' : 'bg-gray-100'"
            >
              <component
                :is="getIcon(action.icon)"
                class="w-3.5 h-3.5"
                :class="isSelected(action.id) ? 'text-purple-700' : 'text-crm-muted'"
              />
            </div>
            <span class="truncate">{{ __(action.label) }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { AVAILABLE_ACTIONS } from '../data/workflowNodeTypes'

// Lucide Icons
import LucideSave from '~icons/lucide/save'
import LucideSend from '~icons/lucide/send'
import LucideArrowRight from '~icons/lucide/arrow-right'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideXCircle from '~icons/lucide/x-circle'
import LucideCornerUpLeft from '~icons/lucide/corner-up-left'
import LucideCornerDownLeft from '~icons/lucide/corner-down-left'
import LucideFilePlus from '~icons/lucide/file-plus'
import LucideUserPlus from '~icons/lucide/user-plus'
import LucideUserCheck from '~icons/lucide/user-check'
import LucideFileOutput from '~icons/lucide/file-output'
import LucideUpload from '~icons/lucide/upload'
import LucideCheckSquare from '~icons/lucide/check-square'
import LucideXSquare from '~icons/lucide/x-square'
import LucideLogOut from '~icons/lucide/log-out'
import LucideTrendingUp from '~icons/lucide/trending-up'
import LucideShare2 from '~icons/lucide/share-2'
import LucideShuffle from '~icons/lucide/shuffle'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  label: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'changed'])

const selectedActions = ref([])

watch(
  () => props.modelValue,
  (newVal) => {
    if (JSON.stringify(newVal) !== JSON.stringify(selectedActions.value)) {
      selectedActions.value = newVal ? [...newVal] : []
    }
  },
  { immediate: true, deep: true }
)

const iconMap = {
  save: LucideSave,
  send: LucideSend,
  'arrow-right': LucideArrowRight,
  'check-circle': LucideCheckCircle,
  'x-circle': LucideXCircle,
  'corner-up-left': LucideCornerUpLeft,
  'corner-down-left': LucideCornerDownLeft,
  'file-plus': LucideFilePlus,
  'user-plus': LucideUserPlus,
  'user-check': LucideUserCheck,
  'file-output': LucideFileOutput,
  upload: LucideUpload,
  'check-square': LucideCheckSquare,
  'x-square': LucideXSquare,
  'log-out': LucideLogOut,
  'trending-up': LucideTrendingUp,
  'share-2': LucideShare2,
  shuffle: LucideShuffle,
}

function getIcon(iconName) {
  return iconMap[iconName] || LucideCheckCircle
}

const actionGroups = computed(() => {
  const groups = [
    { id: 'general', name: 'General Actions', items: [] },
    { id: 'approval', name: 'Approvals & Returns', items: [] },
    { id: 'document', name: 'Documents & Records', items: [] },
    { id: 'assignment', name: 'Assignments & Escalations', items: [] },
    { id: 'terminal', name: 'Terminal States', items: [] },
  ]
  
  for (const action of AVAILABLE_ACTIONS) {
    const found = groups.find((g) => g.id === (action.group || 'general'))
    if (found) {
      found.items.push(action)
    }
  }
  
  return groups.filter((g) => g.items.length > 0)
})

function isSelected(actionId) {
  return selectedActions.value.includes(actionId)
}

function toggleAction(actionId) {
  const idx = selectedActions.value.indexOf(actionId)
  if (idx > -1) {
    selectedActions.value.splice(idx, 1)
  } else {
    selectedActions.value.push(actionId)
  }
  emit('update:modelValue', selectedActions.value)
  emit('changed', selectedActions.value)
}
</script>
