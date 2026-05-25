/**
 * Composable for Node Type Definitions
 *
 * Provides convenient access to node type metadata for use
 * in canvas rendering, palette display, and property panel.
 */
import { computed } from 'vue'
import {
  NODE_TYPES,
  NODE_CATEGORIES,
  NODE_COLORS,
  AVAILABLE_ACTIONS,
  CONDITION_DATA_SOURCES,
  CONDITION_OPERATORS,
  getNodeType,
  getNodeColors,
  getNodeOutputHandles,
  getNodeInputHandles,
  getDefaultNodeConfig,
  getNodesByCategory,
} from '../data/creditFlowNodeTypes'

export function useNodeDefinitions() {
  // All node types as a flat array
  const allNodeTypes = computed(() => Object.values(NODE_TYPES))

  // Node categories with their nodes
  const categories = computed(() =>
    NODE_CATEGORIES.map((category) => ({
      ...category,
      nodeTypes: category.nodes.map((type) => NODE_TYPES[type]).filter(Boolean),
    }))
  )

  // Search/filter nodes by label or description
  function searchNodes(query) {
    if (!query) return allNodeTypes.value
    const lower = query.toLowerCase()
    return allNodeTypes.value.filter(
      (node) =>
        node.label.toLowerCase().includes(lower) ||
        node.description.toLowerCase().includes(lower)
    )
  }

  // Get icon component name from icon string (for lucide-vue-next)
  function getIconName(iconStr) {
    if (!iconStr) return 'settings'
    return iconStr
  }

  // Create a new node instance for the canvas
  function createNodeInstance(nodeType, position) {
    const def = NODE_TYPES[nodeType]
    if (!def) return null

    return {
      id: `node_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      type: 'creditNode',
      position: { x: position.x, y: position.y },
      data: {
        nodeType: def.type,
        label: def.label,
        description: def.description,
        config: getDefaultNodeConfig(def.type),
      },
    }
  }

  return {
    allNodeTypes,
    categories,
    NODE_TYPES,
    NODE_CATEGORIES,
    NODE_COLORS,
    AVAILABLE_ACTIONS,
    CONDITION_DATA_SOURCES,
    CONDITION_OPERATORS,

    // Functions
    getNodeType,
    getNodeColors,
    getNodeOutputHandles,
    getNodeInputHandles,
    getDefaultNodeConfig,
    getNodesByCategory,
    searchNodes,
    getIconName,
    createNodeInstance,
  }
}
