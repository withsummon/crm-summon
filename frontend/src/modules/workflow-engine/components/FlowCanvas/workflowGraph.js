/**
 * Workflow Graph Validation Utilities
 *
 * Extends the pattern from workflowGraph.js with workflow-engine-specific rules:
 * - Exactly one StartNode required
 * - At least one EndNode required
 * - All nodes must be connected
 * - Decision/Skip nodes must have all output handles connected
 * - No orphan nodes (unreachable from Start)
 */

export const DEFAULT_SOURCE_HANDLE = 'default'
export const DEFAULT_TARGET_HANDLE = 'default'

/**
 * Normalize a connection to ensure all fields have values
 */
export function normalizeConnection(connection) {
  return {
    source: connection?.source || '',
    target: connection?.target || '',
    sourceHandle: connection?.sourceHandle || DEFAULT_SOURCE_HANDLE,
    targetHandle: connection?.targetHandle || DEFAULT_TARGET_HANDLE,
  }
}

/**
 * Generate a deterministic edge ID from a connection
 */
export function getWorkflowEdgeId(connection) {
  const edge = normalizeConnection(connection)
  return `${edge.source}:${edge.sourceHandle}->${edge.target}:${edge.targetHandle}`
}

/**
 * Validate a single connection attempt
 */
export function validateConnection(connection, edges = []) {
  const edge = normalizeConnection(connection)

  if (!edge.source || !edge.target) {
    return { valid: false, reason: 'Connection is incomplete.' }
  }

  if (edge.source === edge.target) {
    return { valid: false, reason: 'A node cannot connect to itself.' }
  }

  // Check for duplicates
  const duplicate = edges.some((existingEdge) => {
    const existing = normalizeConnection(existingEdge)
    return (
      existing.source === edge.source &&
      existing.target === edge.target &&
      existing.sourceHandle === edge.sourceHandle &&
      existing.targetHandle === edge.targetHandle
    )
  })

  if (duplicate) {
    return { valid: false, reason: 'This connection already exists.' }
  }

  // Cycle detection
  if (createsCycle(edge, edges)) {
    return { valid: false, reason: 'This connection would create a loop.' }
  }

  return { valid: true, reason: '' }
}

/**
 * BFS-based cycle detection
 */
export function createsCycle(connection, edges = []) {
  const edge = normalizeConnection(connection)
  if (!edge.source || !edge.target) return false

  const adjacency = new Map()
  for (const existingEdge of edges) {
    if (!existingEdge?.source || !existingEdge?.target) continue
    const targets = adjacency.get(existingEdge.source) || []
    targets.push(existingEdge.target)
    adjacency.set(existingEdge.source, targets)
  }

  const visited = new Set()
  const stack = [edge.target]

  while (stack.length) {
    const nodeId = stack.pop()
    if (nodeId === edge.source) return true
    if (visited.has(nodeId)) continue

    visited.add(nodeId)
    stack.push(...(adjacency.get(nodeId) || []))
  }

  return false
}

/**
 * Validate the entire flow for completeness before publishing
 * Returns an array of validation errors/warnings
 */
export function validateFlow(nodes, edges) {
  const errors = []
  const warnings = []

  if (!nodes || nodes.length === 0) {
    errors.push({
      type: 'error',
      code: 'NO_NODES',
      message: 'Flow has no nodes. Add at least a Start and End node.',
    })
    return { valid: false, errors, warnings }
  }

  // Check for exactly one StartNode
  const startNodes = nodes.filter((n) => n.data?.nodeType === 'StartNode')
  if (startNodes.length === 0) {
    errors.push({
      type: 'error',
      code: 'NO_START',
      message: 'Flow must have exactly one Start node.',
    })
  } else if (startNodes.length > 1) {
    errors.push({
      type: 'error',
      code: 'MULTIPLE_STARTS',
      message: 'Flow must have exactly one Start node. Found ' + startNodes.length + '.',
      nodeIds: startNodes.map((n) => n.id),
    })
  }

  // Check for at least one EndNode
  const endNodes = nodes.filter((n) => n.data?.nodeType === 'EndNode')
  if (endNodes.length === 0) {
    errors.push({
      type: 'error',
      code: 'NO_END',
      message: 'Flow must have at least one End node.',
    })
  }

  // Check for disconnected nodes
  const connectedNodeIds = new Set()
  for (const edge of edges) {
    connectedNodeIds.add(edge.source)
    connectedNodeIds.add(edge.target)
  }

  const disconnected = nodes.filter(
    (n) => !connectedNodeIds.has(n.id) && nodes.length > 1
  )
  for (const node of disconnected) {
    errors.push({
      type: 'error',
      code: 'DISCONNECTED',
      message: `Node "${node.data?.label || node.id}" is not connected to any other node.`,
      nodeIds: [node.id],
    })
  }

  // Check that multi-output nodes have all handles connected
  const multiOutputTypes = ['DecisionNode', 'SkipNode', 'ApprovalNode', 'CommitteeNode', 'DelegationNode', 'IntegrationNode', 'SLANode']
  for (const node of nodes) {
    if (multiOutputTypes.includes(node.data?.nodeType)) {
      const nodeEdges = edges.filter((e) => e.source === node.id)
      const connectedHandles = new Set(nodeEdges.map((e) => e.sourceHandle))

      // Get expected handles from node definition
      const expectedHandles = getExpectedOutputHandles(node.data.nodeType)
      const missingHandles = expectedHandles.filter((h) => !connectedHandles.has(h))

      if (missingHandles.length > 0) {
        warnings.push({
          type: 'warning',
          code: 'UNCONNECTED_HANDLE',
          message: `Node "${node.data?.label || node.id}" has unconnected output(s): ${missingHandles.join(', ')}`,
          nodeIds: [node.id],
        })
      }
    }
  }

  // Check reachability from Start
  if (startNodes.length === 1) {
    const reachable = getReachableNodes(startNodes[0].id, edges)
    const unreachable = nodes.filter(
      (n) => !reachable.has(n.id) && n.data?.nodeType !== 'StartNode'
    )
    for (const node of unreachable) {
      warnings.push({
        type: 'warning',
        code: 'UNREACHABLE',
        message: `Node "${node.data?.label || node.id}" is not reachable from the Start node.`,
        nodeIds: [node.id],
      })
    }
  }

  // Check for nodes without config
  for (const node of nodes) {
    if (node.data?.nodeType === 'FormNode' && (!node.data?.config?.sections || node.data.config.sections.length === 0)) {
      warnings.push({
        type: 'warning',
        code: 'UNCONFIGURED',
        message: `Form node "${node.data?.label || node.id}" has no sections configured.`,
        nodeIds: [node.id],
      })
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  }
}

/**
 * Get expected output handle IDs for a node type
 */
function getExpectedOutputHandles(nodeType) {
  const handleMap = {
    DecisionNode: ['true', 'false'],
    SkipNode: ['continue', 'skip'],
    ApprovalNode: ['approved', 'rejected', 'returned'],
    CommitteeNode: ['approved', 'rejected', 'deferred'],
    DelegationNode: ['delegated', 'escalated', 'fallback'],
    IntegrationNode: ['success', 'failure'],
    SLANode: ['on-time', 'warning', 'breached'],
  }
  return handleMap[nodeType] || ['default']
}

/**
 * Get all nodes reachable from a given start node via BFS
 */
function getReachableNodes(startId, edges) {
  const reachable = new Set([startId])
  const queue = [startId]

  while (queue.length) {
    const nodeId = queue.shift()
    const outgoing = edges.filter((e) => e.source === nodeId)

    for (const edge of outgoing) {
      if (!reachable.has(edge.target)) {
        reachable.add(edge.target)
        queue.push(edge.target)
      }
    }
  }

  return reachable
}

/**
 * Serialize flow data for saving (strip non-serializable fields like icons)
 */
export function serializeFlow(nodes, edges) {
  return {
    nodes: nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: { ...node.position },
      data: {
        nodeType: node.data?.nodeType,
        label: node.data?.label,
        description: node.data?.description,
        config: node.data?.config ? JSON.parse(JSON.stringify(node.data.config)) : {},
      },
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      sourceHandle: edge.sourceHandle,
      targetHandle: edge.targetHandle,
      label: edge.label || edge.data?.label || '',
      data: edge.data ? { label: edge.data.label || '' } : {},
    })),
  }
}
