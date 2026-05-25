<template>
  <EditValueModal
    v-if="showEditModal"
    v-model="showEditModal"
    :doctype="doctype"
    :selectedValues="selectedValues"
    @reload="reload"
  />
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="bulkAssignees"
    :docs="selectedValues"
    :doctype="doctype"
    @reload="reload"
  />
  <DeleteLinkedDocModal
    v-if="showDeleteDocModal.showLinkedDocsModal"
    v-model="showDeleteDocModal.showLinkedDocsModal"
    :doctype="props.doctype"
    :docname="showDeleteDocModal.docname"
    :reload="reload"
  />
  <BulkDeleteLinkedDocModal
    v-if="showDeleteDocModal.showDeleteModal"
    v-model="showDeleteDocModal.showDeleteModal"
    :doctype="props.doctype"
    :items="showDeleteDocModal.items"
    :reload="reload"
  />
  <Dialog
    v-model="showReassignDialog"
    :options="{ title: __('Reassign Leads'), size: 'sm' }"
  >
    <template #body-content>
      <div class="flex flex-col gap-3 py-2">
        <FormControl
          v-model="reassignTo"
          type="text"
          :label="__('Assign To')"
          :placeholder="__('user@example.com')"
        />
        <FormControl
          v-model="reassignReason"
          type="textarea"
          :label="__('Reason')"
          :placeholder="__('Reason is mandatory for audit trail')"
        />
      </div>
    </template>
    <template #actions>
      <Button
        variant="solid"
        :label="__('Reassign')"
        :loading="bulkActionLoading"
        @click="submitReassign"
      />
    </template>
  </Dialog>
  <Dialog
    v-model="showTagDialog"
    :options="{ title: __('Tag Leads'), size: 'sm' }"
  >
    <template #body-content>
      <div class="flex flex-col gap-3 py-2">
        <FormControl
          v-model="tagName"
          type="text"
          :label="__('Tag')"
          :placeholder="__('Priority, Win-back, SME')"
        />
        <FormControl
          v-model="tagColor"
          type="text"
          :label="__('Color')"
          placeholder="#0f766e"
        />
      </div>
    </template>
    <template #actions>
      <Button
        variant="solid"
        :label="__('Apply Tag')"
        :loading="bulkActionLoading"
        @click="submitTag"
      />
    </template>
  </Dialog>
</template>

<script setup>
import EditValueModal from '@/components/Modals/EditValueModal.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import { setupListCustomizations } from '@/utils'
import { globalStore } from '@/stores/global'
import { useTelemetry } from 'frappe-ui/frappe'
import { Button, Dialog, FormControl, call, toast } from 'frappe-ui'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  doctype: { type: String, default: '' },
  options: {
    type: Object,
    default: () => ({
      hideEdit: false,
      hideDelete: false,
      hideAssign: false,
    }),
  },
})

const list = defineModel({ type: Object })

const router = useRouter()

const { $dialog, $socket } = globalStore()
const { capture } = useTelemetry()

const showEditModal = ref(false)
const selectedValues = ref([])
const unselectAllAction = ref(() => {})
const showDeleteDocModal = ref({
  showLinkedDocsModal: false,
  showDeleteModal: false,
  docname: null,
})
function editValues(selections, unselectAll) {
  selectedValues.value = selections
  showEditModal.value = true
  unselectAllAction.value = unselectAll
}

function convertToDeal(selections, unselectAll) {
  $dialog({
    title: __('Convert to Deal'),
    message: __('Are you sure you want to convert {0} lead(s) to deal(s)?', [
      selections.size,
    ]),
    variant: 'solid',
    theme: 'blue',
    actions: [
      {
        label: __('Convert'),
        variant: 'solid',
        onClick: (close) => {
          capture('bulk_convert_to_deal')
          Array.from(selections).forEach((name) => {
            call('crm.fcrm.doctype.crm_lead.crm_lead.convert_to_deal', {
              lead: name,
            }).then(() => {
              toast.success(__('Converted Successfully'))
              list.value.reload()
              unselectAll()
              close()
            })
          })
        },
      },
    ],
  })
}

function deleteValues(selections, unselectAll) {
  unselectAllAction.value = unselectAll

  const selectedDocs = Array.from(selections)
  if (selectedDocs.length == 1) {
    showDeleteDocModal.value = {
      showLinkedDocsModal: true,
      docname: selectedDocs[0],
    }
  } else {
    showDeleteDocModal.value = {
      showDeleteModal: true,
      items: selectedDocs,
    }
  }
}

const showAssignmentModal = ref(false)
const bulkAssignees = ref([])
const showReassignDialog = ref(false)
const showTagDialog = ref(false)
const bulkActionLoading = ref(false)
const pendingSelections = ref([])
const reassignTo = ref('')
const reassignReason = ref('')
const tagName = ref('')
const tagColor = ref('#0f766e')

function assignValues(selections, unselectAll) {
  showAssignmentModal.value = true
  selectedValues.value = selections
  unselectAllAction.value = unselectAll
}

function openReassignDialog(selections, unselectAll) {
  pendingSelections.value = Array.from(selections)
  unselectAllAction.value = unselectAll
  reassignTo.value = ''
  reassignReason.value = ''
  showReassignDialog.value = true
}

async function submitReassign() {
  if (!reassignTo.value || !reassignReason.value) {
    toast.error(__('Assign To and Reason are required'))
    return
  }
  bulkActionLoading.value = true
  try {
    await call('crm.api.lead_management.reassign_leads', {
      leads: pendingSelections.value,
      to_user: reassignTo.value,
      reason: reassignReason.value,
    })
    toast.success(__('Leads reassigned'))
    showReassignDialog.value = false
    reload()
  } finally {
    bulkActionLoading.value = false
  }
}

function openTagDialog(selections, unselectAll) {
  pendingSelections.value = Array.from(selections)
  unselectAllAction.value = unselectAll
  tagName.value = ''
  tagColor.value = '#0f766e'
  showTagDialog.value = true
}

async function submitTag() {
  if (!tagName.value) {
    toast.error(__('Tag is required'))
    return
  }
  bulkActionLoading.value = true
  try {
    await call('crm.api.lead_management.bulk_tag_leads', {
      leads: pendingSelections.value,
      tag: tagName.value,
      color: tagColor.value || '#0f766e',
    })
    toast.success(__('Tags applied'))
    showTagDialog.value = false
    reload()
  } finally {
    bulkActionLoading.value = false
  }
}

async function exportSelectedLeads(selections) {
  const names = Array.from(selections)
  const result = await call('crm.api.lead_management.export_leads', {
    filters: { name: ['in', names] },
    format: 'CSV',
  })
  if (result.file_url) {
    window.location.href = result.file_url
  }
  toast.success(__('Lead export prepared'))
}

async function refreshDuplicateCandidates(selections) {
  for (const name of Array.from(selections)) {
    await call('crm.api.lead_management.preview_duplicates', { lead: name })
  }
  toast.success(__('Duplicate candidates refreshed'))
  reload()
}

function clearAssignments(selections, unselectAll) {
  $dialog({
    title: __('Clear Assignment'),
    message: __('Are you sure you want to clear assignment for {0} item(s)?', [
      selections.size,
    ]),
    variant: 'solid',
    theme: 'red',
    actions: [
      {
        label: __('Clear Assignment'),
        variant: 'solid',
        theme: 'red',
        onClick: (close) => {
          capture('bulk_clear_assignment')
          call('frappe.desk.form.assign_to.remove_multiple', {
            doctype: props.doctype,
            names: JSON.stringify(Array.from(selections)),
            ignore_permissions: true,
          }).then(() => {
            toast.success(__('Assignment Cleared Successfully'))
            reload(unselectAll)
            close()
          })
        },
      },
    ],
  })
}

const customBulkActions = ref([])
const customListActions = ref([])

function bulkActions(selections, unselectAll) {
  let actions = []

  if (!props.options.hideEdit) {
    actions.push({
      label: __('Edit'),
      onClick: () => editValues(selections, unselectAll),
    })
  }

  if (!props.options.hideDelete) {
    actions.push({
      label: __('Delete'),
      onClick: () => deleteValues(selections, unselectAll),
    })
  }

  if (!props.options.hideAssign) {
    actions.push({
      label: __('Assign To'),
      onClick: () => assignValues(selections, unselectAll),
    })
    actions.push({
      label: __('Clear Assignment'),
      onClick: () => clearAssignments(selections, unselectAll),
    })
  }

  if (props.doctype === 'CRM Lead') {
    actions.push({
      label: __('Convert to Deal'),
      onClick: () => convertToDeal(selections, unselectAll),
    })
    actions.push({
      label: __('Reassign with Reason'),
      onClick: () => openReassignDialog(selections, unselectAll),
    })
    actions.push({
      label: __('Apply Tag'),
      onClick: () => openTagDialog(selections, unselectAll),
    })
    actions.push({
      label: __('Review Duplicates'),
      onClick: () => refreshDuplicateCandidates(selections),
    })
    actions.push({
      label: __('Export Selected'),
      onClick: () => exportSelectedLeads(selections),
    })
  }

  customBulkActions.value.forEach((action) => {
    actions.push({
      label: __(action.label),
      onClick: () =>
        action.onClick({
          list: list.value,
          selections,
          unselectAll,
          call,
          createToast: toast.create,
          toast,
          $dialog,
          router,
        }),
    })
  })
  return actions
}

function reload(unselectAll) {
  showDeleteDocModal.value = {
    showLinkedDocsModal: false,
    showDeleteModal: false,
    docname: null,
  }

  unselectAllAction.value?.()
  unselectAll?.()
  list.value?.reload()
}

onMounted(async () => {
  if (!list.value?.data) return
  let customization = await setupListCustomizations(list.value.data, {
    list: list.value,
    call,
    createToast: toast.create,
    toast,
    $dialog,
    $socket,
    router,
  })
  customBulkActions.value =
    customization?.bulkActions || list.value?.data?.bulkActions || []
  customListActions.value =
    customization?.actions || list.value?.data?.listActions || []
})

defineExpose({
  bulkActions,
  customListActions,
})
</script>
