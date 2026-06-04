<template>
  <div
    class="flex h-full w-[420px] flex-col border-l border-gray-200 bg-white shadow-lg"
  >
    <!-- Header -->
    <div class="flex items-center gap-3 border-b border-gray-200 px-4 py-3">
      <div
        class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg"
        :class="nodeColors.bg"
      >
        <component
          :is="iconMap[nodeDef?.icon]"
          v-if="iconMap[nodeDef?.icon]"
          class="h-4 w-4"
          :class="nodeColors.text"
        />
      </div>
      <div class="min-w-0 flex-1">
        <input
          :value="nodeLabel"
          type="text"
          class="w-full border-none bg-transparent text-sm font-semibold text-gray-800 outline-none focus:ring-0"
          @input="updateLabel($event.target.value)"
        />
        <div class="text-[11px] text-gray-400 uppercase tracking-wide">
          {{ nodeDef?.category || 'Node' }}
        </div>
      </div>
      <button
        class="flex h-7 w-7 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
        @click="$emit('close')"
      >
        <LucideX class="h-4 w-4" />
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200">
      <button
        v-for="tab in availableTabs"
        :key="tab.id"
        class="flex-1 border-b-2 px-3 py-2.5 text-xs font-medium transition-colors"
        :class="
          activeTab === tab.id
            ? 'brand-tab-active'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        "
        @click="activeTab = tab.id"
      >
        {{ __(tab.label) }}
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-4">
      <!-- General Tab -->
      <div v-if="activeTab === 'general'" class="space-y-4">
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-600">
            {{ __('Node Label') }}
          </label>
          <input
            :value="nodeLabel"
            type="text"
            class="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none transition-colors brand-focus focus:bg-white"
            @input="updateLabel($event.target.value)"
          />
        </div>
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-600">
            {{ __('Description') }}
          </label>
          <textarea
            :value="nodeDescription"
            rows="3"
            class="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none transition-colors brand-focus focus:bg-white resize-none"
            :placeholder="nodeDef?.description || ''"
            @input="updateDescription($event.target.value)"
          />
        </div>

        <!-- End Node: outcome selector -->
        <div v-if="nodeType === 'EndNode'">
          <label class="mb-1 block text-xs font-medium text-gray-600">
            {{ __('Outcome') }}
          </label>
          <select
            :value="config.outcome || 'approved'"
            class="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500"
            @change="updateConfig('outcome', $event.target.value)"
          >
            <option value="approved">{{ __('Approved') }}</option>
            <option value="rejected">{{ __('Rejected') }}</option>
            <option value="cancelled">{{ __('Cancelled') }}</option>
            <option value="withdrawn">{{ __('Withdrawn') }}</option>
          </select>
        </div>

        <!-- Start Node: trigger type -->
        <div v-if="nodeType === 'StartNode'">
          <label class="mb-1 block text-xs font-medium text-gray-600">
            {{ __('Trigger Type') }}
          </label>
          <select
            :value="config.triggerType || 'manual'"
            class="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500"
            @change="updateConfig('triggerType', $event.target.value)"
          >
            <option value="manual">{{ __('Manual') }}</option>
            <option value="auto">{{ __('Automatic') }}</option>
            <option value="api">{{ __('API Trigger') }}</option>
          </select>
        </div>

        <!-- Node info -->
        <div class="rounded-lg bg-gray-50 p-3">
          <div class="text-xs font-medium text-gray-500 mb-1">{{ __('Node Type') }}</div>
          <div class="text-sm text-gray-700">{{ nodeDef?.label }}</div>
          <div class="mt-1 text-xs text-gray-400">{{ nodeDef?.description }}</div>
        </div>
      </div>

      <!-- Configuration Tab -->
      <div v-if="activeTab === 'config'">
        <component
          :is="configComponent"
          v-if="configComponent"
          :config="config"
          @update:config="onConfigUpdate"
        />
        <div v-else class="py-8 text-center text-sm text-gray-400">
          {{ __('No additional configuration for this node type.') }}
        </div>
      </div>

      <!-- Actions Tab -->
      <div v-if="activeTab === 'actions'" class="space-y-3">
        <p class="text-xs text-gray-500 mb-3">
          {{ __('Select which actions are available to users at this stage.') }}
        </p>
        <div
          v-for="group in actionGroups"
          :key="group.name"
          class="mb-4"
        >
          <h4 class="mb-2 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
            {{ __(group.name) }}
          </h4>
          <div class="space-y-1.5">
            <label
              v-for="action in group.actions"
              :key="action.id"
              class="flex cursor-pointer items-center gap-2.5 rounded-lg px-3 py-2 transition-colors hover:bg-gray-50"
            >
              <input
                type="checkbox"
                :checked="selectedActions.includes(action.id)"
                class="h-4 w-4 rounded border-gray-300 text-secondary-600 focus:ring-primary-500"
                @change="toggleAction(action.id)"
              />
              <span class="text-sm text-gray-700">{{ __(action.label) }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineAsyncComponent } from 'vue'
import {
  NODE_TYPES,
  NODE_COLORS,
  AVAILABLE_ACTIONS,
  getNodeColors,
} from '../../data/creditFlowNodeTypes'

import LucideX from '~icons/lucide/x'
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

const iconMap = {
  'play-circle': LucidePlayCircle,
  'stop-circle': LucideStopCircle,
  'git-branch': LucideGitBranch,
  'skip-forward': LucideSkipForward,
  'file-text': LucideFileText,
  'folder-open': LucideFolderOpen,
  'user-plus': LucideUserPlus,
  'shield-check': LucideShieldCheck,
  users: LucideUsers,
  'user-check': LucideUserCheck,
  plug: LucidePlug,
  bell: LucideBell,
  clock: LucideClock,
}

// Lazy-load node config components
const configComponentMap = {
  FormNode: defineAsyncComponent(() => import('./FormNodeConfig.vue')),
  DecisionNode: defineAsyncComponent(() => import('./DecisionNodeConfig.vue')),
  ApprovalNode: defineAsyncComponent(() => import('./ApprovalNodeConfig.vue')),
  CommitteeNode: defineAsyncComponent(() => import('./CommitteeNodeConfig.vue')),
  DelegationNode: defineAsyncComponent(() => import('./DelegationNodeConfig.vue')),
  AssignmentNode: defineAsyncComponent(() => import('./AssignmentNodeConfig.vue')),
  SLANode: defineAsyncComponent(() => import('./SLANodeConfig.vue')),
  NotificationNode: defineAsyncComponent(() => import('./NotificationNodeConfig.vue')),
  IntegrationNode: defineAsyncComponent(() => import('./IntegrationNodeConfig.vue')),
  DocumentNode: defineAsyncComponent(() => import('./DocumentNodeConfig.vue')),
  SkipNode: defineAsyncComponent(() => import('./SkipNodeConfig.vue')),
}

const props = defineProps({
  node: { type: Object, required: true },
})

const emit = defineEmits(['update:node', 'close'])

const activeTab = ref('general')

const nodeType = computed(() => props.node?.data?.nodeType || '')
const nodeDef = computed(() => NODE_TYPES[nodeType.value] || null)
const nodeColors = computed(() => {
  const c = getNodeColors(nodeType.value)
  return c || { bg: 'bg-gray-100', text: 'text-gray-600' }
})

const nodeLabel = computed(() => props.node?.data?.label || '')
const nodeDescription = computed(() => props.node?.data?.description || '')
const config = computed(() => props.node?.data?.config || {})
const configComponent = computed(() => configComponentMap[nodeType.value] || null)

const selectedActions = computed(() => config.value.availableActions || [])

const availableTabs = computed(() => {
  const tabs = [{ id: 'general', label: 'General' }]
  if (configComponent.value) tabs.push({ id: 'config', label: 'Configuration' })
  if (nodeType.value !== 'StartNode' && nodeType.value !== 'EndNode') {
    tabs.push({ id: 'actions', label: 'Actions' })
  }
  return tabs
})

const actionGroups = computed(() => {
  const groups = {}
  for (const action of AVAILABLE_ACTIONS) {
    const g = action.group || 'general'
    if (!groups[g]) groups[g] = { name: g, actions: [] }
    groups[g].actions.push(action)
  }
  return Object.values(groups)
})

function updateLabel(value) {
  emit('update:node', { ...props.node.data, label: value })
}

function updateDescription(value) {
  emit('update:node', { ...props.node.data, description: value })
}

function updateConfig(key, value) {
  const newConfig = { ...config.value, [key]: value }
  emit('update:node', { ...props.node.data, config: newConfig })
}

function onConfigUpdate(newConfig) {
  emit('update:node', { ...props.node.data, config: newConfig })
}

function toggleAction(actionId) {
  const current = [...(config.value.availableActions || [])]
  const idx = current.indexOf(actionId)
  if (idx >= 0) current.splice(idx, 1)
  else current.push(actionId)
  updateConfig('availableActions', current)
}

watch(
  () => props.node?.id,
  () => {
    activeTab.value = 'general'
  }
)
</script>
