<template>
  <div class="h-full w-full relative bg-surface-gray-1" @drop="onDrop" @dragover.prevent @dragenter.prevent>
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      class="vue-flow-canvas"
      :default-viewport="{ zoom: 1 }"
      :min-zoom="0.2"
      :max-zoom="4"
    >
      <Background pattern-color="#cbd5e1" :gap="20" />
      <Controls />
      
      <!-- Custom Drop Target overlay -->
      <template #node-custom="props">
        <div class="custom-node p-3 rounded-[10px] bg-white border border-crm-border shadow-sm flex items-center gap-3 transition-shadow hover:shadow-md cursor-pointer" :class="{ 'ring-2 ring-purple-500 border-transparent': props.selected }">
          <div class="h-10 w-10 rounded-lg flex items-center justify-center" :class="getIconBgClass(props.data.type)">
            <LucideSettings v-if="!props.data.icon" class="w-5 h-5 text-gray-600" />
            <component :is="props.data.icon" v-else class="w-5 h-5" :class="getIconTextClass(props.data.type)" />
          </div>
          <div>
            <div class="font-semibold text-sm text-gray-800">{{ props.data.label }}</div>
            <div class="text-[11px] text-gray-500 uppercase tracking-wide font-medium mt-0.5">{{ props.data.subType }}</div>
          </div>
        </div>
      </template>

    </VueFlow>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import LucideSettings from '~icons/lucide/settings'
import LucideZap from '~icons/lucide/zap'
import LucideBot from '~icons/lucide/bot'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'

const { onConnect, addEdges, project } = useVueFlow()

const nodes = ref([
  {
    id: 'node-1',
    type: 'custom',
    position: { x: 250, y: 150 },
    data: { label: 'Lead Created', type: 'Trigger', subType: 'Lead Created', icon: LucideZap },
  },
  {
    id: 'node-2',
    type: 'custom',
    position: { x: 600, y: 150 },
    data: { label: 'AI Scraper', type: 'AIAgent', subType: 'AI Agent', icon: LucideBot },
  },
])

const edges = ref([
  { id: 'e1-2', source: 'node-1', target: 'node-2', animated: true, style: { stroke: '#94a3b8', strokeWidth: 2 } },
])

onConnect((connection) => {
  addEdges({ ...connection, animated: true, style: { stroke: '#94a3b8', strokeWidth: 2 } })
})

let id = 0
const getId = () => `dndnode_${id++}`

function onDrop(event) {
  const data = event.dataTransfer?.getData('application/vueflow')
  if (!data) return

  const nodeData = JSON.parse(data)
  
  // Project client coordinates to vue flow coordinates
  const position = project({ x: event.clientX - 260, y: event.clientY - 60 }) // offset for sidebar and header
  
  const newNode = {
    id: getId(),
    type: 'custom',
    position,
    data: { ...nodeData },
  }

  nodes.value.push(newNode)
}

function getIconBgClass(type) {
  if (type === 'Trigger') return 'bg-purple-100'
  if (type === 'Action' || type === 'AIAgent') return 'bg-green-100'
  if (type === 'Condition' || type === 'Approval') return 'bg-blue-100'
  return 'bg-gray-100'
}

function getIconTextClass(type) {
  if (type === 'Trigger') return 'text-purple-600'
  if (type === 'Action' || type === 'AIAgent') return 'text-green-600'
  if (type === 'Condition' || type === 'Approval') return 'text-blue-600'
  return 'text-gray-600'
}
</script>

<style>
.vue-flow-canvas {
  background-color: transparent;
}
.custom-node {
  min-width: 180px;
}
</style>
