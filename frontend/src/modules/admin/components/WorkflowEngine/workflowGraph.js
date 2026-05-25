export const DEFAULT_SOURCE_HANDLE = 'output'
export const DEFAULT_TARGET_HANDLE = 'input'

export function normalizeConnection(connection) {
  return {
    source: connection?.source || '',
    target: connection?.target || '',
    sourceHandle: connection?.sourceHandle || DEFAULT_SOURCE_HANDLE,
    targetHandle: connection?.targetHandle || DEFAULT_TARGET_HANDLE,
  }
}

export function getWorkflowEdgeId(connection) {
  const edge = normalizeConnection(connection)
  return `${edge.source}:${edge.sourceHandle}->${edge.target}:${edge.targetHandle}`
}

export function validateWorkflowConnection(connection, edges = []) {
  const edge = normalizeConnection(connection)

  if (!edge.source || !edge.target) {
    return { valid: false, reason: 'Connection is incomplete.' }
  }

  if (edge.source === edge.target) {
    return { valid: false, reason: 'A node cannot connect to itself.' }
  }

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

  if (createsWorkflowCycle(edge, edges)) {
    return { valid: false, reason: 'This connection would create a loop.' }
  }

  return { valid: true, reason: '' }
}

export function createsWorkflowCycle(connection, edges = []) {
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

