<template>
  <div class="h-full w-full relative bg-surface-gray-1" @drop="onDrop" @dragover.prevent @dragenter.prevent>
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      class="vue-flow-canvas"
      :default-viewport="{ zoom: 1 }"
      :min-zoom="0.2"
      :max-zoom="4"
      :nodes-connectable="true"
      :connection-mode="ConnectionMode.Strict"
      :snap-to-grid="true"
      :snap-grid="[20, 20]"
      :auto-pan-on-connect="true"
      :connect-on-click="true"
      :connection-line-options="connectionLineOptions"
      :default-edge-options="defaultEdgeOptions"
      @connect="handleConnect"
      @edge-context-menu="deleteEdge"
    >
      <Background pattern-color="#cbd5e1" :gap="20" />
      <Controls />

      <!-- Custom Drop Target overlay -->
      <template #node-custom="props">
        <div class="custom-node p-3 rounded-[10px] bg-white border border-crm-border shadow-sm flex items-center gap-3 transition-shadow hover:shadow-md cursor-pointer relative" :class="{ 'ring-2 ring-purple-500 border-transparent': props.selected }">
          <Handle id="input" type="target" :position="Position.Left" class="workflow-handle workflow-handle-input" />

          <div class="h-10 w-10 rounded-lg flex items-center justify-center" :class="getIconBgClass(props.data.type)">
            <LucideSettings v-if="!props.data.icon" class="w-5 h-5 text-gray-600" />
            <component :is="props.data.icon" v-else class="w-5 h-5" :class="getIconTextClass(props.data.type)" />
          </div>
          <div>
            <div class="font-semibold text-sm text-gray-800">{{ props.data.label }}</div>
            <div class="text-[11px] text-gray-500 uppercase tracking-wide font-medium mt-0.5">{{ props.data.subType }}</div>
          </div>

          <Handle
            v-for="handle in getOutputHandles(props.data.type)"
            :id="handle.id"
            :key="handle.id"
            type="source"
            :position="Position.Right"
            class="workflow-handle workflow-handle-output"
            :style="{ top: handle.top }"
          />
        </div>
      </template>

    </VueFlow>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import {
  ConnectionLineType,
  ConnectionMode,
  Handle,
  MarkerType,
  Position,
  VueFlow,
  useVueFlow,
} from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { toast } from 'frappe-ui'
import LucideSettings from '~icons/lucide/settings'
import LucideZap from '~icons/lucide/zap'
import LucideBot from '~icons/lucide/bot'
import {
  DEFAULT_SOURCE_HANDLE,
  DEFAULT_TARGET_HANDLE,
  getWorkflowEdgeId,
  normalizeConnection,
  validateWorkflowConnection,
} from './workflowGraph'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'

const emit = defineEmits(['update:nodes', 'update:edges', 'changed'])

const { screenToFlowCoordinate } = useVueFlow()

const edgeStyle = { stroke: '#64748b', strokeWidth: 2 }
const edgeMarker = { type: MarkerType.ArrowClosed, color: '#64748b' }

const connectionLineOptions = {
  type: ConnectionLineType.SmoothStep,
  style: edgeStyle,
  markerEnd: edgeMarker,
}

const defaultEdgeOptions = {
  type: 'smoothstep',
  animated: true,
  style: edgeStyle,
  markerEnd: edgeMarker,
}

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
  {
    id: 'node-1:output->node-2:input',
    source: 'node-1',
    target: 'node-2',
    sourceHandle: DEFAULT_SOURCE_HANDLE,
    targetHandle: DEFAULT_TARGET_HANDLE,
    data: { label: '' },
    ...defaultEdgeOptions,
  },
])

let id = nodes.value.length
const getId = () => `dndnode_${id++}`

function onDrop(event) {
  const data = event.dataTransfer?.getData('application/vueflow')
  if (!data) return

  const nodeData = JSON.parse(data)
  const position = screenToFlowCoordinate({ x: event.clientX, y: event.clientY })

  const newNode = {
    id: getId(),
    type: 'custom',
    position,
    data: { ...nodeData },
  }

  nodes.value.push(newNode)
}

function handleConnect(connection) {
  const normalizedConnection = normalizeConnection(connection)
  const validation = validateWorkflowConnection(normalizedConnection, edges.value)

  if (!validation.valid) {
    toast.warning(__(validation.reason))
    return
  }

  edges.value.push({
    id: getWorkflowEdgeId(normalizedConnection),
    ...normalizedConnection,
    data: { label: '' },
    ...defaultEdgeOptions,
  })
}

function deleteEdge({ event, edge }) {
  event.preventDefault()
  edges.value = edges.value.filter((item) => item.id !== edge.id)
}

function getOutputHandles(type) {
  if (type === 'Condition') {
    return [
      { id: 'true', top: '35%' },
      { id: 'false', top: '65%' },
    ]
  }

  if (type === 'Approval') {
    return [
      { id: 'approved', top: '30%' },
      { id: 'rejected', top: '50%' },
      { id: 'referred', top: '70%' },
    ]
  }

  return [{ id: DEFAULT_SOURCE_HANDLE, top: '50%' }]
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

watch(
  nodes,
  (value, oldValue) => {
    emit('update:nodes', value)
    if (oldValue) emit('changed', { nodes: value, edges: edges.value })
  },
  { deep: true, immediate: true },
)

watch(
  edges,
  (value, oldValue) => {
    emit('update:edges', value)
    if (oldValue) emit('changed', { nodes: nodes.value, edges: value })
  },
  { deep: true, immediate: true },
)
</script>

<style>
.vue-flow-canvas {
  background-color: transparent;
}
.custom-node {
  min-width: 180px;
}
.workflow-handle {
  width: 12px;
  height: 12px;
  border: 2px solid white;
  background: #7c3aed;
}
.workflow-handle-input {
  left: -6px;
}
.workflow-handle-output {
  right: -6px;
}
.vue-flow__edge-path {
  transition: stroke 0.15s ease, stroke-width 0.15s ease;
}
.vue-flow__edge:hover .vue-flow__edge-path,
.vue-flow__edge.selected .vue-flow__edge-path {
  stroke: #7c3aed;
  stroke-width: 3;
}
</style>
