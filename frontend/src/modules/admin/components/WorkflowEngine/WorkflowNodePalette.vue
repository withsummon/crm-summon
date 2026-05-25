<template>
  <div class="flex h-full w-64 flex-col border-r border-crm-border bg-white">
    <div class="p-4 border-b border-crm-border">
      <h2 class="text-sm font-semibold text-gray-800">{{ __('Node Palette') }}</h2>
      <p class="text-xs text-gray-500 mt-1">{{ __('Drag nodes to the canvas') }}</p>
    </div>
    
    <div class="flex-1 overflow-y-auto p-3 space-y-4">
      <!-- Triggers -->
      <div>
        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{{ __('Triggers') }}</h3>
        <div class="space-y-2">
          <div
            v-for="node in triggerNodes"
            :key="node.type"
            class="palette-node group"
            draggable="true"
            @dragstart="onDragStart($event, node)"
          >
            <div class="flex items-center gap-2">
              <component :is="node.icon" class="w-4 h-4 text-purple-500" />
              <span class="text-sm font-medium text-gray-700">{{ node.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Logic -->
      <div>
        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{{ __('Logic') }}</h3>
        <div class="space-y-2">
          <div
            v-for="node in logicNodes"
            :key="node.type"
            class="palette-node group"
            draggable="true"
            @dragstart="onDragStart($event, node)"
          >
            <div class="flex items-center gap-2">
              <component :is="node.icon" class="w-4 h-4 text-blue-500" />
              <span class="text-sm font-medium text-gray-700">{{ node.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div>
        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{{ __('Actions') }}</h3>
        <div class="space-y-2">
          <div
            v-for="node in actionNodes"
            :key="node.type"
            class="palette-node group"
            draggable="true"
            @dragstart="onDragStart($event, node)"
          >
            <div class="flex items-center gap-2">
              <component :is="node.icon" class="w-4 h-4 text-green-500" />
              <span class="text-sm font-medium text-gray-700">{{ node.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LucideZap from '~icons/lucide/zap'
import LucideGitCommit from '~icons/lucide/git-commit'
import LucideGitMerge from '~icons/lucide/git-merge'
import LucideUserCheck from '~icons/lucide/user-check'
import LucideWebhook from '~icons/lucide/webhook'
import LucideBot from '~icons/lucide/bot'
import LucideMail from '~icons/lucide/mail'
import LucideClock from '~icons/lucide/clock'

const triggerNodes = [
  { type: 'Trigger', subType: 'Lead Created', label: 'Lead Created', icon: LucideZap },
  { type: 'Trigger', subType: 'App Submitted', label: 'App Submitted', icon: LucideZap },
  { type: 'Trigger', subType: 'Schedule', label: 'Schedule (Cron)', icon: LucideClock },
]

const logicNodes = [
  { type: 'Condition', subType: 'IF/ELSE', label: 'IF/ELSE Branch', icon: LucideGitMerge },
  { type: 'Approval', subType: 'Approval Gate', label: 'Approval Gate', icon: LucideUserCheck },
  { type: 'Action', subType: 'Sub Workflow', label: 'Sub Workflow', icon: LucideGitCommit },
]

const actionNodes = [
  { type: 'AIAgent', subType: 'AI Agent', label: 'AI Agent', icon: LucideBot },
  { type: 'Action', subType: 'Webhook', label: 'Webhook', icon: LucideWebhook },
  { type: 'Action', subType: 'Send Email', label: 'Send Email', icon: LucideMail },
]

function onDragStart(event, nodeData) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/vueflow', JSON.stringify(nodeData))
    event.dataTransfer.effectAllowed = 'move'
  }
}
</script>

<style scoped>
.palette-node {
  @apply cursor-grab rounded-lg border border-transparent bg-gray-50 p-3 transition-colors hover:border-purple-200 hover:bg-purple-50;
}
</style>
