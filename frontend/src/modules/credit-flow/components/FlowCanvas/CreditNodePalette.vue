<template>
  <aside class="credit-node-palette w-72 h-full flex flex-col bg-white border-r border-gray-200">
    <!-- Header -->
    <div class="px-4 pt-4 pb-2">
      <h3 class="text-sm font-semibold text-gray-800 mb-3">{{ __('Node Palette') }}</h3>
      <div class="relative">
        <LucideSearch class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="__('Search nodes...')"
          class="w-full pl-8 pr-3 py-2 text-sm border border-gray-200 rounded-lg bg-gray-50 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-300 transition-all duration-200"
        />
      </div>
    </div>

    <!-- Category List -->
    <div class="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
      <!-- Search Results Mode -->
      <template v-if="searchQuery">
        <div v-if="filteredNodes.length === 0" class="px-2 py-8 text-center">
          <LucideSearch class="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p class="text-sm text-gray-400">{{ __('No nodes found') }}</p>
        </div>
        <PaletteItem
          v-for="node in filteredNodes"
          :key="node.type"
          :node="node"
          @dragstart="onDragStart($event, node)"
        />
      </template>

      <!-- Categories Mode -->
      <template v-else>
        <div v-for="category in categoriesWithNodes" :key="category.name" class="mb-1">
          <!-- Category Header -->
          <button
            class="w-full flex items-center gap-2 px-2 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider hover:text-gray-700 transition-colors duration-150 rounded-md hover:bg-gray-50"
            @click="toggleCategory(category.name)"
          >
            <LucideChevronRight
              class="w-3.5 h-3.5 text-gray-400 transition-transform duration-200"
              :class="{ 'rotate-90': expandedCategories.has(category.name) }"
            />
            <span>{{ __(category.name) }}</span>
            <span class="ml-auto text-[10px] font-medium text-gray-400 bg-gray-100 rounded-full px-1.5 py-0.5">
              {{ category.nodeTypes.length }}
            </span>
          </button>

          <!-- Category Nodes -->
          <Transition name="collapse">
            <div v-show="expandedCategories.has(category.name)" class="space-y-1 mt-1 ml-1">
              <PaletteItem
                v-for="node in category.nodeTypes"
                :key="node.type"
                :node="node"
                @dragstart="onDragStart($event, node)"
              />
            </div>
          </Transition>
        </div>
      </template>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { NODE_TYPES, NODE_CATEGORIES, NODE_COLORS } from '../../data/creditFlowNodeTypes'
import { useNodeDefinitions } from '../../composables/useNodeDefinitions'

// Icons
import LucideSearch from '~icons/lucide/search'
import LucideChevronRight from '~icons/lucide/chevron-right'
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

const { searchNodes } = useNodeDefinitions()

const searchQuery = ref('')

const expandedCategories = ref(new Set(NODE_CATEGORIES.map((c) => c.name)))

const categoriesWithNodes = computed(() =>
  NODE_CATEGORIES.map((category) => ({
    ...category,
    nodeTypes: category.nodes.map((type) => NODE_TYPES[type]).filter(Boolean),
  }))
)

const filteredNodes = computed(() => searchNodes(searchQuery.value))

function toggleCategory(name) {
  const expanded = expandedCategories.value
  if (expanded.has(name)) {
    expanded.delete(name)
  } else {
    expanded.add(name)
  }
}

function onDragStart(event, node) {
  const payload = {
    nodeType: node.type,
    label: node.label,
    description: node.description,
  }
  event.dataTransfer.setData('application/creditflow', JSON.stringify(payload))
  event.dataTransfer.effectAllowed = 'move'
}

// ─── Palette Item Sub-component ──────────────────────────────
// Defined inline for co-location; renders a single draggable node card
const PaletteItem = {
  props: {
    node: { type: Object, required: true },
  },
  emits: ['dragstart'],
  setup(props, { emit }) {
    const colors = computed(() => NODE_COLORS[props.node.color] || NODE_COLORS.slate)
    const iconComponent = computed(() => ICON_MAP[props.node.icon] || null)

    return { colors, iconComponent }
  },
  template: `
    <div
      draggable="true"
      class="palette-item group flex items-start gap-3 px-3 py-2.5 rounded-lg border border-transparent cursor-grab transition-all duration-200 hover:bg-gray-50 hover:border-gray-200 hover:shadow-sm active:cursor-grabbing active:shadow-md active:scale-[0.98]"
      @dragstart="$emit('dragstart', $event)"
    >
      <div
        class="flex-shrink-0 h-9 w-9 rounded-lg flex items-center justify-center transition-colors duration-200"
        :class="colors.bg"
      >
        <component
          :is="iconComponent"
          v-if="iconComponent"
          class="w-[18px] h-[18px]"
          :class="colors.text"
        />
      </div>
      <div class="min-w-0 flex-1 pt-0.5">
        <div class="text-sm font-medium text-gray-800 leading-tight truncate">{{ node.label }}</div>
        <div class="text-[11px] text-gray-400 leading-snug mt-0.5 line-clamp-2">{{ node.description }}</div>
      </div>
    </div>
  `,
}
</script>

<style scoped>
.credit-node-palette {
  @apply select-none;
}

/* Collapse transition */
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}
.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-4px);
}
.collapse-enter-to,
.collapse-leave-from {
  opacity: 1;
  max-height: 600px;
}

/* Scrollbar */
.credit-node-palette ::-webkit-scrollbar {
  width: 4px;
}
.credit-node-palette ::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}
.credit-node-palette ::-webkit-scrollbar-track {
  background: transparent;
}
</style>
