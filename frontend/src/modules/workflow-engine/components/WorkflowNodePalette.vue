<template>
  <div class="flex h-full w-64 flex-col border-r border-crm-border bg-white shadow-sm">
    <div class="p-4 border-b border-crm-border">
      <h2 class="text-sm font-semibold text-gray-800">{{ __('Node Palette') }}</h2>
      <p class="text-xs text-crm-muted mt-1">{{ __('Drag nodes to the canvas') }}</p>
      
      <!-- Search input -->
      <div class="mt-3 relative">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="__('Search nodes...')"
          class="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 bg-surface-gray-1"
        />
        <LucideSearch class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-crm-muted" />
      </div>
    </div>
    
    <div class="flex-1 overflow-y-auto p-3 space-y-4">
      <div
        v-for="category in filteredCategories"
        :key="category.name"
        class="space-y-2"
      >
        <h3 class="text-[10px] font-bold text-crm-muted uppercase tracking-wider px-1">
          {{ __(category.name) }}
        </h3>
        
        <div class="space-y-1.5">
          <div
            v-for="node in category.nodeTypes"
            :key="node.type"
            class="palette-node group cursor-grab rounded-lg border border-crm-border bg-surface-gray-1 p-2.5 transition-all hover:border-purple-200 hover:bg-purple-50/50 hover:shadow-sm"
            draggable="true"
            @dragstart="onDragStart($event, node)"
          >
            <div class="flex items-center gap-2.5">
              <div :class="['p-1.5 rounded-md', getNodeColorClasses(node.color).bg]">
                <component
                  :is="getIcon(node.type)"
                  :class="['w-4 h-4', getNodeColorClasses(node.color).text]"
                />
              </div>
              <div class="min-w-0">
                <span class="block text-xs font-semibold text-gray-700 truncate">{{ __(node.label) }}</span>
                <span class="block text-[10px] text-crm-muted truncate mt-0.5">{{ __(node.description) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="filteredCategories.length === 0" class="text-center py-8 text-xs text-crm-muted">
        {{ __('No matching nodes') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNodeDefinitions } from '../composables/useNodeDefinitions'
import { NODE_COLORS } from '../data/workflowNodeTypes'

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
import LucideSearch from '~icons/lucide/search'

const { categories } = useNodeDefinitions()
const searchQuery = ref('')

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

function getNodeColorClasses(colorName) {
  return NODE_COLORS[colorName] || NODE_COLORS.slate
}

const filteredCategories = computed(() => {
  if (!searchQuery.value) return categories.value

  const query = searchQuery.value.toLowerCase()
  return categories.value
    .map((category) => {
      const nodeTypes = category.nodeTypes.filter(
        (node) =>
          node.label.toLowerCase().includes(query) ||
          node.description.toLowerCase().includes(query)
      )
      return { ...category, nodeTypes }
    })
    .filter((category) => category.nodeTypes.length > 0)
})

function onDragStart(event, node) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/vueflow', JSON.stringify({ type: node.type }))
    event.dataTransfer.effectAllowed = 'move'
  }
}
</script>
