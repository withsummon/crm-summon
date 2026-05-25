/**
 * Composable for Credit Flow CRUD operations
 *
 * Provides reactive resources for listing, creating, saving, publishing,
 * cloning, and managing credit flow definitions.
 */
import { ref, computed } from 'vue'
import { createResource, createListResource } from 'frappe-ui'

export function useCreditFlow(flowId = null) {
  // ─── Flow List ──────────────────────────────────────────
  const flowList = createListResource({
    doctype: 'CRM Credit Flow',
    fields: [
      'name',
      'title',
      'description',
      'status',
      'product_type',
      'applicant_persona',
      'is_pre_approved',
      'current_version',
      'created_by',
      'published_by',
      'published_at',
      'creation',
      'modified',
    ],
    orderBy: 'modified desc',
    pageLength: 50,
    auto: !flowId,
  })

  // ─── Single Flow ────────────────────────────────────────
  const flow = flowId
    ? createResource({
        url: 'crm.api.credit_flow.get_flow',
        params: { flow_id: flowId },
        auto: true,
      })
    : null

  // ─── Save Draft ─────────────────────────────────────────
  const saveDraft = createResource({
    url: 'crm.api.credit_flow.save_flow_draft',
    onSuccess() {
      if (flow) flow.reload()
    },
  })

  function saveFlowDraft(flowId, flowData) {
    return saveDraft.submit({
      flow_id: flowId,
      title: flowData.title,
      description: flowData.description,
      product_type: flowData.productType,
      applicant_persona: flowData.applicantPersona,
      is_pre_approved: flowData.isPreApproved,
      flow_json: JSON.stringify(flowData.flowJson),
    })
  }

  // ─── Publish ────────────────────────────────────────────
  const publishResource = createResource({
    url: 'crm.api.credit_flow.publish_flow',
    onSuccess() {
      if (flow) flow.reload()
      if (flowList) flowList.reload()
    },
  })

  function publishFlow(flowId, changeNote = '') {
    return publishResource.submit({
      flow_id: flowId,
      change_note: changeNote,
    })
  }

  // ─── Clone ──────────────────────────────────────────────
  const cloneResource = createResource({
    url: 'crm.api.credit_flow.clone_flow',
    onSuccess() {
      if (flowList) flowList.reload()
    },
  })

  function cloneFlow(flowId) {
    return cloneResource.submit({ flow_id: flowId })
  }

  // ─── Deactivate ─────────────────────────────────────────
  const deactivateResource = createResource({
    url: 'crm.api.credit_flow.deactivate_flow',
    onSuccess() {
      if (flowList) flowList.reload()
    },
  })

  function deactivateFlow(flowId) {
    return deactivateResource.submit({ flow_id: flowId })
  }

  // ─── Validate ───────────────────────────────────────────
  const validateResource = createResource({
    url: 'crm.api.credit_flow.validate_flow',
  })

  function validateFlowServer(flowId) {
    return validateResource.submit({ flow_id: flowId })
  }

  // ─── Version History ────────────────────────────────────
  const versions = flowId
    ? createResource({
        url: 'crm.api.credit_flow.get_flow_versions',
        params: { flow_id: flowId },
      })
    : null

  function loadVersions() {
    if (versions) versions.submit()
  }

  // ─── Rollback ───────────────────────────────────────────
  const rollbackResource = createResource({
    url: 'crm.api.credit_flow.rollback_flow',
    onSuccess() {
      if (flow) flow.reload()
      if (versions) versions.reload()
    },
  })

  function rollbackFlow(flowId, version) {
    return rollbackResource.submit({ flow_id: flowId, version })
  }

  // ─── Loading States ─────────────────────────────────────
  const isLoading = computed(() => {
    return (
      flowList?.loading ||
      flow?.loading ||
      saveDraft.loading ||
      publishResource.loading
    )
  })

  const isSaving = computed(() => saveDraft.loading)
  const isPublishing = computed(() => publishResource.loading)

  return {
    // Resources
    flowList,
    flow,
    versions,

    // Actions
    saveFlowDraft,
    publishFlow,
    cloneFlow,
    deactivateFlow,
    validateFlowServer,
    loadVersions,
    rollbackFlow,

    // State
    isLoading,
    isSaving,
    isPublishing,
  }
}
