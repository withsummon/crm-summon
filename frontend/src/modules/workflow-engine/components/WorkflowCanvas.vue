<template>
  <div
    class="h-full w-full relative overflow-hidden"
    @drop="onDrop"
    @dragover.prevent
    @dragenter.prevent
  >
    <!-- bpmn-js Container -->
    <div ref="canvasRef" class="bpmn-canvas-container h-full w-full"></div>
    
    <!-- Quick tooltip or help banner -->
    <div class="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm border border-crm-border px-3 py-2 rounded-lg shadow-sm text-[10px] text-crm-muted pointer-events-none z-10 flex flex-col gap-1">
      <div class="flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 bg-teal-600 rounded-full animate-pulse" />
        <span class="font-bold text-gray-700">{{ __('Canvas Quick Actions') }}</span>
      </div>
      <div>• {{ __('Drag nodes from palette to add') }}</div>
      <div>• {{ __('Click node to configure properties') }}</div>
      <div>• {{ __('Use connection tool to link nodes') }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import BpmnModeler from 'bpmn-js/lib/Modeler'
import { toast } from 'frappe-ui'

import { INITIAL_XML, parseBPMN } from './FlowCanvas/bpmnParser'
import './FlowCanvas/bpmnCustomTheme.css'

// bpmn-js library default styles
import 'bpmn-js/dist/assets/diagram-js.css'
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css'
import 'bpmn-js/dist/assets/bpmn-js.css'

const props = defineProps({
  flowXml: { type: String, default: '' },
  elementConfigs: { type: Object, default: () => ({}) },
})

const emit = defineEmits([
  'changed',
  'node-selected',
  'pane-clicked',
  'config-created',
  'config-deleted'
])

const canvasRef = ref(null)
let modeler = null
let isImporting = false

// Set up bpmn-js modeler on mount
onMounted(() => {
  if (!canvasRef.value) return

  modeler = new BpmnModeler({
    container: canvasRef.value,
    keyboard: {
      bindTo: window
    }
  })

  // Import XML and draw
  const xmlToLoad = props.flowXml || INITIAL_XML
  importXML(xmlToLoad)

  // Listen for selection changes to trigger property panel details
  modeler.on('selection.changed', (e) => {
    const selection = e.newSelection
    if (selection && selection.length > 0) {
      const element = selection[0]
      const elementId = element.id
      
      // Avoid emitting if clicking on process canvas background or connection
      if (element.type === 'bpmn:Process' || element.type === 'bpmn:SequenceFlow') {
        emit('pane-clicked')
        return
      }

      const savedConfig = props.elementConfigs[elementId] || {}
      emit('node-selected', {
        id: elementId,
        type: 'creditNode',
        data: {
          nodeType: savedConfig.nodeType || mapBPMNTypeToNodeType(element.type),
          label: element.businessObject.name || savedConfig.label || elementId,
          description: savedConfig.description || '',
          config: savedConfig.config || {},
          actions: savedConfig.actions || []
        }
      })
    } else {
      emit('pane-clicked')
    }
  })

  // Track edits to canvas (e.g. connections, deletions, movements) to trigger updates
  modeler.on('commandStack.changed', () => {
    if (!isImporting) {
      triggerChange()
    }
  })

  // Track deletion of elements to delete associated logical configs
  modeler.on('elements.changed', (e) => {
    if (isImporting) return
    const elements = e.elements
    
    // Check if any registered element was deleted from registry
    const elementRegistry = modeler.get('elementRegistry')
    for (const key in props.elementConfigs) {
      if (!elementRegistry.get(key)) {
        emit('config-deleted', key)
      }
    }
  })
})

onBeforeUnmount(() => {
  if (modeler) {
    modeler.destroy()
  }
})

// React to flowXml changes (e.g. version rollback)
watch(
  () => props.flowXml,
  (newXml) => {
    if (newXml && modeler) {
      // Get current XML to avoid infinite cycles
      modeler.saveXML().then(({ xml }) => {
        if (xml !== newXml) {
          importXML(newXml)
        }
      }).catch(() => {
        importXML(newXml)
      })
    }
  }
)

// Watch configurations to update element labels reactively on the canvas
watch(
  () => props.elementConfigs,
  (newConfigs) => {
    if (!modeler || isImporting) return
    const modeling = modeler.get('modeling')
    const elementRegistry = modeler.get('elementRegistry')
    
    for (const id in newConfigs) {
      const element = elementRegistry.get(id)
      if (element && element.businessObject.name !== newConfigs[id].label) {
        modeling.updateLabel(element, newConfigs[id].label || '')
      }
    }
  },
  { deep: true }
)

// Helper to load BPMN XML safely
async function importXML(xmlString) {
  if (!modeler) return
  isImporting = true
  try {
    await modeler.importXML(xmlString)
    
    // Zoom canvas to fit viewport perfectly
    const canvas = modeler.get('canvas')
    canvas.zoom('fit-viewport')
  } catch (err) {
    console.error('Failed to import BPMN XML', err)
    toast.error(__('Failed to load BPMN diagram'))
  } finally {
    isImporting = false
  }
}

// Convert standard BPMN elements to FCRM execution node categories
function mapBPMNTypeToNodeType(bpmnType) {
  switch (bpmnType) {
    case 'bpmn:StartEvent': return 'StartNode'
    case 'bpmn:EndEvent': return 'EndNode'
    case 'bpmn:ExclusiveGateway': return 'DecisionNode'
    case 'bpmn:SendTask': return 'NotificationNode'
    case 'bpmn:ServiceTask': return 'IntegrationNode'
    case 'bpmn:BoundaryEvent': return 'SLANode'
    default: return 'FormNode'
  }
}

// Drag & drop element drop placement
function onDrop(event) {
  if (!modeler) return

  // Retrieve dropped node type (passed from WorkflowNodePalette)
  const data = event.dataTransfer?.getData('application/vueflow')
  if (!data) return

  try {
    const { type } = JSON.parse(data)

    // Compute cursor offset relative to modeler canvas bounds
    const rect = canvasRef.value.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    // Map drag type to standard BPMN shape element
    let bpmnType = 'bpmn:UserTask'
    if (type === 'StartNode') bpmnType = 'bpmn:StartEvent'
    else if (type === 'EndNode') bpmnType = 'bpmn:EndEvent'
    else if (type === 'DecisionNode' || type === 'SkipNode') bpmnType = 'bpmn:ExclusiveGateway'
    else if (type === 'NotificationNode') bpmnType = 'bpmn:SendTask'
    else if (type === 'IntegrationNode') bpmnType = 'bpmn:ServiceTask'
    else if (type === 'SLANode') bpmnType = 'bpmn:BoundaryEvent'

    const elementFactory = modeler.get('elementFactory')
    const modeling = modeler.get('modeling')
    const canvas = modeler.get('canvas')

    const parent = canvas.getRootElement()
    const shape = elementFactory.createShape({
      type: bpmnType
    })

    // Set readable default visual name on element
    const cleanLabel = type.replace('Node', '')
    shape.businessObject.name = cleanLabel

    // Place shape onto BPMN canvas
    modeling.createShape(shape, { x, y }, parent)

    // Seed configuration properties map
    const elementId = shape.id
    const initialConfig = {
      nodeType: type,
      label: cleanLabel,
      description: '',
      config: getInitialNodeConfig(type),
      actions: []
    }

    emit('config-created', { id: elementId, config: initialConfig })
    triggerChange()
    toast.success(__('{0} placed on canvas', [cleanLabel]))
  } catch (err) {
    console.error('Failed placing BPMN element', err)
  }
}

// Default settings schemas matched with workflowNodeTypes.js defaults
function getInitialNodeConfig(type) {
  switch (type) {
    case 'StartNode':
      return { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] }
    case 'EndNode':
      return { outcome: 'approved', finalActions: [], notifications: [] }
    case 'DecisionNode':
      return { conditions: [], defaultPath: '' }
    case 'SkipNode':
      return { conditions: [], skipTargetNode: '' }
    case 'FormNode':
      return { formTemplate: '', sections: [], fields: [] }
    case 'ApprovalNode':
      return { approvalType: 'single', approvers: [], requireAll: false }
    case 'CommitteeNode':
      return { committee: '', quorum: 3, majority: 'majority' }
    case 'DelegationNode':
      return { checkAvailability: true, maxDepth: 3, fallbackTarget: '' }
    case 'IntegrationNode':
      return { endpointUrl: '', httpMethod: 'POST', requestMapping: {}, responseMapping: {} }
    case 'NotificationNode':
      return { channels: ['in_app'], template: '', subject: '', body: '' }
    case 'SLANode':
      return { durationHours: 24, alertPercentage: 80, escalationTarget: '' }
    default:
      return {}
  }
}

// Save XML, parse back to nodes/edges list arrays, and emit updates
async function triggerChange() {
  if (!modeler) return
  try {
    const { xml } = await modeler.saveXML({ format: true })
    const { nodes: parsedNodes, edges: parsedEdges } = parseBPMN(xml, props.elementConfigs)
    
    emit('changed', {
      xml,
      nodes: parsedNodes,
      edges: parsedEdges
    })
  } catch (err) {
    console.error('Failed saving BPMN modeler XML', err)
  }
}
</script>
