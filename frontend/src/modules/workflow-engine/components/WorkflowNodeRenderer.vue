<template>
  <div
    class="workflow-engine-node p-3 rounded-[12px] bg-white border border-crm-border shadow-sm flex flex-col min-w-[200px] max-w-[260px] transition-all hover:shadow-md cursor-pointer relative"
    :class="[
      selected ? 'ring-2 ring-purple-600 border-transparent shadow-md scale-[1.02]' : '',
      `node-accent-${nodeColorName}`
    ]"
  >
    <!-- Left colored accent bar -->
    <div :class="['absolute left-0 top-3 bottom-3 w-1 rounded-r-md', colorClasses.bg]" />

    <!-- Input Handle -->
    <Handle
      v-for="input in inputHandles"
      :id="input.id"
      :key="input.id"
      type="target"
      :position="Position.Left"
      class="workflow-handle workflow-handle-input"
      :style="{ top: input.position || '50%' }"
    />

    <!-- Header section -->
    <div class="flex items-center gap-3">
      <!-- Icon badge -->
      <div :class="['h-9 w-9 rounded-lg flex items-center justify-center shrink-0 shadow-inner', colorClasses.bg]">
        <component
          :is="getIcon(data.nodeType)"
          :class="['w-4.5 h-4.5', colorClasses.text]"
        />
      </div>

      <!-- Node labels -->
      <div class="min-w-0 flex-1">
        <div class="font-bold text-xs text-gray-800 truncate pr-4">
          {{ __(data.label || defaultLabel) }}
        </div>
        <div class="text-[9px] text-crm-muted uppercase tracking-wider font-semibold mt-0.5">
          {{ __(nodeDef?.category || 'Flow') }}
        </div>
      </div>
      
      <!-- Node Type abbreviation badge -->
      <span class="absolute top-2.5 right-2.5 text-[8px] bg-gray-100 px-1.5 py-0.5 rounded-full font-mono text-crm-muted">
        {{ data.nodeType }}
      </span>
    </div>

    <!-- Configuration Summary Body -->
    <div class="mt-2.5 pt-2.5 border-t border-gray-50 flex flex-col text-[10px] text-gray-500">
      <div v-if="data.description" class="line-clamp-2 text-[10px] text-crm-muted italic mb-1.5 leading-normal">
        {{ __(data.description) }}
      </div>

      <!-- Type-specific information -->
      <div class="flex flex-col gap-1 text-[10px] text-gray-600 bg-surface-gray-1/40 p-1.5 rounded-md">
        <!-- Form Node -->
        <template v-if="data.nodeType === 'FormNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Template:') }}</span>
            <span class="font-bold text-crm-text truncate max-w-[120px]">{{ data.config?.formTemplate || '—' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Sections:') }}</span>
            <span class="font-bold text-crm-text">{{ data.config?.sections?.length || 0 }}</span>
          </div>
        </template>

        <!-- Start Node -->
        <template v-else-if="data.nodeType === 'StartNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Trigger:') }}</span>
            <span class="font-bold text-crm-text capitalize">{{ data.config?.triggerType || 'manual' }}</span>
          </div>
        </template>

        <!-- End Node -->
        <template v-else-if="data.nodeType === 'EndNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Outcome:') }}</span>
            <span class="font-bold text-red-600 capitalize font-mono text-[9px]">{{ data.config?.outcome || 'approved' }}</span>
          </div>
        </template>

        <!-- Decision Node -->
        <template v-else-if="data.nodeType === 'DecisionNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Data Source:') }}</span>
            <span class="font-bold text-crm-text capitalize">{{ data.config?.dataSource || 'application' }}</span>
          </div>
        </template>

        <!-- Skip Node -->
        <template v-else-if="data.nodeType === 'SkipNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Reason:') }}</span>
            <span class="font-bold text-crm-text truncate max-w-[120px]">{{ data.config?.skipReason || '—' }}</span>
          </div>
        </template>

        <!-- Approval Node -->
        <template v-else-if="data.nodeType === 'ApprovalNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Type:') }}</span>
            <span class="font-bold text-crm-text capitalize">{{ data.config?.approvalType || 'single' }}</span>
          </div>
        </template>

        <!-- Committee Node -->
        <template v-else-if="data.nodeType === 'CommitteeNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Voting:') }}</span>
            <span class="font-bold text-crm-text capitalize">{{ data.config?.votingMethod || 'majority' }}</span>
          </div>
        </template>

        <!-- Delegation Node -->
        <template v-else-if="data.nodeType === 'DelegationNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Fallback:') }}</span>
            <span class="font-bold text-crm-text capitalize">{{ data.config?.fallbackType || 'role' }}</span>
          </div>
        </template>

        <!-- SLA Node -->
        <template v-else-if="data.nodeType === 'SLANode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Deadline:') }}</span>
            <span class="font-bold text-crm-text">{{ data.config?.deadlineHours || 24 }}h</span>
          </div>
        </template>

        <!-- Notification Node -->
        <template v-else-if="data.nodeType === 'NotificationNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Channels:') }}</span>
            <span class="font-bold text-crm-text capitalize">{{ data.config?.channels?.join(', ') || 'in_app' }}</span>
          </div>
        </template>

        <!-- Integration Node -->
        <template v-else-if="data.nodeType === 'IntegrationNode'">
          <div class="flex justify-between">
            <span class="font-medium text-crm-muted">{{ __('Endpoint:') }}</span>
            <span class="font-bold text-crm-text truncate max-w-[120px]">{{ data.config?.endpoint || '—' }}</span>
          </div>
        </template>

        <!-- Generic placeholder for other nodes -->
        <template v-else>
          <span class="text-crm-muted italic text-[9px]">{{ __('Double-click to configure properties') }}</span>
        </template>
      </div>
    </div>

    <!-- Output Handles -->
    <template v-for="output in outputHandles" :key="output.id">
      <Handle
        :id="output.id"
        type="source"
        :position="Position.Right"
        class="workflow-handle workflow-handle-output"
        :style="{ top: output.position || '50%' }"
      />
      <!-- Output Handle label -->
      <span
        v-if="output.label && output.label !== 'Next' && output.label !== 'Input'"
        class="absolute right-[-32px] text-[8px] font-bold text-crm-muted bg-white border border-crm-border px-1.5 py-0.5 rounded shadow-sm z-10 pointer-events-none select-none"
        :style="{ top: `calc(${output.position || '50%'} - 8px)` }"
      >
        {{ __(output.label) }}
      </span>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { useNodeDefinitions } from '../composables/useNodeDefinitions'

// Lucide Icons
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

const props = defineProps({
  id: { type: String, required: true },
  selected: { type: Boolean, default: false },
  data: { type: Object, required: true },
})

const { NODE_TYPES, NODE_COLORS, getNodeColors } = useNodeDefinitions()

const nodeDef = computed(() => NODE_TYPES[props.data.nodeType])
const defaultLabel = computed(() => nodeDef.value?.label || 'Node')

const nodeColorName = computed(() => nodeDef.value?.color || 'slate')
const colorClasses = computed(() => {
  return NODE_COLORS[nodeColorName.value] || NODE_COLORS.slate
})

const iconMap = {
  StartNode: LucidePlayCircle,
  EndNode: LucideStopCircle,
  DecisionNode: LucideGitBranch,
  SkipNode: LucideSkipForward,
  FormNode: LucideFileText,
  DocumentNode: LucideFolderOpen,
  AssignmentNode: LucideUserPlus,
  ApprovalNode: LucideShieldCheck,
  CommitteeNode: LucideUsers,
  DelegationNode: LucideUserCheck,
  IntegrationNode: LucidePlug,
  NotificationNode: LucideBell,
  SLANode: LucideClock,
}

function getIcon(type) {
  return iconMap[type] || LucidePlayCircle
}

const inputHandles = computed(() => {
  return nodeDef.value?.handles?.inputs || []
})

const outputHandles = computed(() => {
  return nodeDef.value?.handles?.outputs || []
})
</script>

<style scoped>
.workflow-engine-node {
  border-left-width: 0 !important;
}
.workflow-handle {
  width: 10px;
  height: 10px;
  border: 2px solid white;
  background: #7c3aed;
  transition: transform 0.15s ease, background 0.15s ease;
  z-index: 20;
}
.workflow-handle:hover {
  transform: scale(1.3);
  background: #6d28d9;
}
.workflow-handle-input {
  left: -5px;
}
.workflow-handle-output {
  right: -5px;
}
</style>
