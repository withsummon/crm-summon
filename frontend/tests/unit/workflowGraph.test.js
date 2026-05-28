import { describe, expect, it } from 'vitest'
import {
  DEFAULT_SOURCE_HANDLE,
  DEFAULT_TARGET_HANDLE,
  validateConnection as validateWorkflowConnection,
} from '@/modules/workflow-engine/components/FlowCanvas/workflowGraph'

describe('workflow graph validation', () => {
  it('accepts a valid connection between two nodes', () => {
    const result = validateWorkflowConnection(
      {
        source: 'node-a',
        target: 'node-b',
        sourceHandle: DEFAULT_SOURCE_HANDLE,
        targetHandle: DEFAULT_TARGET_HANDLE,
      },
      [],
    )

    expect(result.valid).toBe(true)
  })

  it('rejects self-loop connections', () => {
    const result = validateWorkflowConnection(
      {
        source: 'node-a',
        target: 'node-a',
        sourceHandle: DEFAULT_SOURCE_HANDLE,
        targetHandle: DEFAULT_TARGET_HANDLE,
      },
      [],
    )

    expect(result.valid).toBe(false)
    expect(result.reason).toContain('itself')
  })

  it('rejects duplicate connections with the same handles', () => {
    const existingEdges = [
      {
        id: 'edge-1',
        source: 'node-a',
        target: 'node-b',
        sourceHandle: DEFAULT_SOURCE_HANDLE,
        targetHandle: DEFAULT_TARGET_HANDLE,
      },
    ]

    const result = validateWorkflowConnection(
      {
        source: 'node-a',
        target: 'node-b',
        sourceHandle: DEFAULT_SOURCE_HANDLE,
        targetHandle: DEFAULT_TARGET_HANDLE,
      },
      existingEdges,
    )

    expect(result.valid).toBe(false)
    expect(result.reason).toContain('already exists')
  })

  it('rejects connections that create a cycle', () => {
    const existingEdges = [
      { id: 'edge-1', source: 'node-a', target: 'node-b' },
      { id: 'edge-2', source: 'node-b', target: 'node-c' },
    ]

    const result = validateWorkflowConnection(
      {
        source: 'node-c',
        target: 'node-a',
        sourceHandle: DEFAULT_SOURCE_HANDLE,
        targetHandle: DEFAULT_TARGET_HANDLE,
      },
      existingEdges,
    )

    expect(result.valid).toBe(false)
    expect(result.reason).toContain('loop')
  })
})

