<template>
  <div
    class="credit-flow-canvas h-full w-full relative bg-gray-50"
    @drop="onDrop"
    @dragover.prevent
    @dragenter.prevent
  >
    <VueFlow
      v-model:nodes="localNodes"
      v-model:edges="localEdges"
      class="vue-flow-credit"
      :default-viewport="{ zoom: 1 }"
      :min-zoom="0.15"
      :max-zoom="4"
      :nodes-connectable="true"
      :connection-mode="ConnectionMode.Strict"
      :snap-to-grid="true"
      :snap-grid="[20, 20]"
      :auto-pan-on-connect="true"
      :connect-on-click="true"
      :connection-line-options="connectionLineOptions"
      :default-edge-options="defaultEdgeOptions"
      :node-types="nodeTypes"
      @connect="handleConnect"
      @edge-context-menu="onEdgeContextMenu"
      @node-click="onNodeClick"
      @pane-click="onPaneClick"
    >
      <Background pattern-color="#cbd5e1" :gap="20" />
      <Controls position="bottom-right" />
    </VueFlow>
  </div>
</template>

<script setup>
import { ref, watch, markRaw, computed } from 'vue'
import {
  ConnectionLineType,
  ConnectionMode,
  MarkerType,
  Position,
  VueFlow,
  useVueFlow,
} from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { toast } from 'frappe-ui'

import CreditNodeRenderer from './CreditNodeRenderer.vue'
import { useNodeDefinitions } from '../../composables/useNodeDefinitions'
import {
  normalizeConnection,
  getCreditFlowEdgeId,
  validateConnection,
} from './creditFlowGraph'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'

// ─── Props & Emits ──────────────────────────────────────────
const props = defineProps({
  nodes: { type: Array, default: () => [] },
  edges: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'update:nodes',
  'update:edges',
  'changed',
  'node-selected',
  'node-deselected',
])

// ─── Vue Flow Setup ─────────────────────────────────────────
const { screenToFlowCoordinate } = useVueFlow()
const { createNodeInstance } = useNodeDefinitions()

// Register custom node types
const nodeTypes = {
  creditNode: markRaw(CreditNodeRenderer),
}

// ─── Edge Styling ───────────────────────────────────────────
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

// ─── Reactive State ─────────────────────────────────────────
const localNodes = ref([...props.nodes])
const localEdges = ref([...props.edges])

// Sync props → local state when parent changes
watch(
  () => props.nodes,
  (newVal) => {
    localNodes.value = [...newVal]
  },
  { deep: true }
)

watch(
  () => props.edges,
  (newVal) => {
    localEdges.value = [...newVal]
  },
  { deep: true }
)

// Emit changes back to parent
watch(
  localNodes,
  (value, oldValue) => {
    emit('update:nodes', value)
    if (oldValue) emit('changed', { nodes: value, edges: localEdges.value })
  },
  { deep: true }
)

watch(
  localEdges,
  (value, oldValue) => {
    emit('update:edges', value)
    if (oldValue) emit('changed', { nodes: localNodes.value, edges: value })
  },
  { deep: true }
)

// ─── Drag & Drop from Palette ───────────────────────────────
function onDrop(event) {
  const data = event.dataTransfer?.getData('application/creditflow')
  if (!data) return

  const payload = JSON.parse(data)
  const position = screenToFlowCoordinate({
    x: event.clientX,
    y: event.clientY,
  })

  const newNode = createNodeInstance(payload.nodeType, position)
  if (!newNode) {
    toast({ title: __('Unknown node type'), variant: 'subtle' })
    return
  }

  // Check maxInstances constraint
  const nodeDef = newNode.data?.nodeType
  if (nodeDef) {
    const { NODE_TYPES } = useNodeDefinitions()
    const def = NODE_TYPES[nodeDef]
    if (def?.maxInstances) {
      const existingCount = localNodes.value.filter(
        (n) => n.data?.nodeType === nodeDef
      ).length
      if (existingCount >= def.maxInstances) {
        toast({
          title: __(`Only ${def.maxInstances} ${def.label} node(s) allowed`),
          variant: 'subtle',
        })
        return
      }
    }
  }

  localNodes.value.push(newNode)
}

// ─── Connection Handling ────────────────────────────────────
function handleConnect(connection) {
  const normalized = normalizeConnection(connection)
  const validation = validateConnection(normalized, localEdges.value)

  if (!validation.valid) {
    toast({ title: __(validation.reason), variant: 'subtle' })
    return
  }

  localEdges.value.push({
    id: getCreditFlowEdgeId(normalized),
    ...normalized,
    data: { label: '' },
    ...defaultEdgeOptions,
  })
}

// ─── Edge Context Menu (Delete) ─────────────────────────────
function onEdgeContextMenu({ event, edge }) {
  event.preventDefault()
  localEdges.value = localEdges.value.filter((e) => e.id !== edge.id)
}

// ─── Node Selection ─────────────────────────────────────────
function onNodeClick({ node }) {
  if (node?.data) {
    emit('node-selected', { id: node.id, ...node.data })
  }
}

function onPaneClick() {
  emit('node-deselected')
}
</script>

<style>
.vue-flow-credit {
  background-color: transparent;
}

/* Edge transitions */
.vue-flow-credit .vue-flow__edge-path {
  transition: stroke 0.15s ease, stroke-width 0.15s ease;
}

.vue-flow-credit .vue-flow__edge:hover .vue-flow__edge-path,
.vue-flow-credit .vue-flow__edge.selected .vue-flow__edge-path {
  stroke: #006699;
  stroke-width: 3;
}

/* Connection line animation */
.vue-flow-credit .vue-flow__connection-path {
  stroke: #006699;
  stroke-dasharray: 5;
  animation: dashdraw 0.5s linear infinite;
}

@keyframes dashdraw {
  to {
    stroke-dashoffset: -10;
  }
}

/* Controls panel styling */
.vue-flow-credit .vue-flow__controls {
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.vue-flow-credit .vue-flow__controls-button {
  border-color: #e2e8f0;
}

.vue-flow-credit .vue-flow__controls-button:hover {
  background: #f1f5f9;
}
</style>
