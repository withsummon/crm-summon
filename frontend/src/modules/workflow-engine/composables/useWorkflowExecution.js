/**
 * Composable for Workflow Execution Monitoring
 *
 * Provides reactive resources for tracking flow execution status,
 * audit logs, and monitoring statistics.
 */
import { computed } from 'vue'
import { createResource, createListResource } from 'frappe-ui'

export function useWorkflowExecution(flowId = null) {
  // ─── Active Executions ──────────────────────────────────
  const executions = createListResource({
    doctype: 'CRM Workflow Execution',
    fields: [
      'name',
      'flow',
      'flow_version',
      'application',
      'current_node',
      'current_node_type',
      'current_node_label',
      'status',
      'started_at',
      'completed_at',
      'completed_nodes',
      'skipped_nodes',
      'flow_version_json',
      'execution_data',
    ],
    filters: flowId ? { flow: flowId } : {},
    orderBy: 'started_at desc',
    pageLength: 50,
    auto: true,
  })

  // ─── Execution Detail ──────────────────────────────────
  function getExecutionDetail(executionId) {
    return createResource({
      url: 'crm.api.workflow_execution.get_execution_history',
      params: { execution_id: executionId },
      auto: true,
    })
  }

  // ─── Execution Stats ───────────────────────────────────
  const stats = flowId
    ? createResource({
        url: 'crm.api.workflow_execution.get_execution_stats',
        params: { flow_id: flowId },
        auto: true,
      })
    : null

  // ─── Audit Log ──────────────────────────────────────────
  function getAuditLog(executionId) {
    return createListResource({
      doctype: 'CRM Workflow Audit Log',
      fields: [
        'name',
        'node_id',
        'event_type',
        'timestamp',
        'user',
        'original_assignee',
        'delegated_to',
        'decision',
        'reason',
      ],
      filters: { execution: executionId },
      orderBy: 'timestamp asc',
      pageLength: 200,
      auto: true,
    })
  }

  // ─── Computed Stats ─────────────────────────────────────
  const activeCount = computed(() => {
    return (
      executions.data?.filter((e) => e.status === 'Running').length || 0
    )
  })

  const completedCount = computed(() => {
    return (
      executions.data?.filter((e) => e.status === 'Completed').length || 0
    )
  })

  const failedCount = computed(() => {
    return (
      executions.data?.filter((e) => e.status === 'Failed').length || 0
    )
  })

  return {
    executions,
    stats,
    getExecutionDetail,
    getAuditLog,
    activeCount,
    completedCount,
    failedCount,
  }
}
