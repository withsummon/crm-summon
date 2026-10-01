<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Call Logs" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="callLogsListView?.customListActions"
        :actions="callLogsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="createCallLog"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="callLogs"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Call Log"
  />
  <CallLogsListView
    v-if="callLogs.data && rows.length"
    ref="callLogsListView"
    v-model="callLogs.data.page_length_count"
    v-model:list="callLogs"
    :rows="rows"
    :columns="columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: callLogs.data.row_count,
      totalCount: callLogs.data.total_count,
    }"
    @showCallLog="showCallLog"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <div v-else-if="callLogs.data && !rows.length" class="mx-auto w-full max-w-2xl px-6 py-12">
    <div class="flex items-center gap-3 rounded-xl border border-outline-gray-2 bg-surface-white p-5">
      <PhoneIcon class="h-8 w-8 text-ink-gray-4" />
      <div>
        <h2 class="font-medium text-ink-gray-9">Belum ada panggilan tercatat</h2>
        <p class="text-sm text-ink-gray-5">Aktivitas suara akan muncul setelah panggilan benar-benar tercatat.</p>
      </div>
    </div>
    <div v-if="recentCommunications.data?.length" class="mt-6">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="font-medium text-ink-gray-9">Komunikasi pelanggan terbaru</h3>
        <RouterLink :to="{ name: 'Omnichannel Workspace' }" class="text-sm text-ink-red-3 hover:underline">Buka Omnichannel</RouterLink>
      </div>
      <div class="divide-y divide-outline-gray-2 rounded-xl border border-outline-gray-2 bg-surface-white">
        <div v-for="conversation in recentCommunications.data" :key="conversation.name" class="flex items-center justify-between gap-4 px-4 py-3">
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-ink-gray-9">{{ conversation.subject }}</p>
            <p class="truncate text-xs text-ink-gray-5">{{ conversation.last_message_preview || 'Tidak ada pratinjau pesan' }}</p>
          </div>
          <span class="shrink-0 text-xs text-ink-gray-5">{{ conversation.channel }}</span>
        </div>
      </div>
    </div>
  </div>
  <CallLogDetailModal
    v-model="showCallLogDetailModal"
    v-model:callLog="callLog"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import CallLogsListView from '@/components/ListViews/CallLogsListView.vue'
import CallLogDetailModal from '@/components/Modals/CallLogDetailModal.vue'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { getCallLogDetail } from '@/utils/callLog'
import { useTelemetry } from 'frappe-ui/frappe'
import { createResource } from 'frappe-ui'
import { computed, ref, onMounted } from 'vue'

const callLogsListView = ref(null)

const recentCommunications = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Omnichannel Conversation',
    fields: ['name', 'subject', 'channel', 'last_message_preview'],
    filters: [['status', '!=', 'Archived'], ['subject', 'not like', '%Demo%']],
    order_by: 'last_message_at desc',
    limit_page_length: 5,
  },
  auto: true,
})

// callLogs data is loaded in the ViewControls component
const callLogs = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const rows = computed(() => {
  if (
    !callLogs.value?.data?.data ||
    !['list', 'group_by'].includes(callLogs.value.data.view_type)
  )
    return []
  return callLogs.value?.data.data.map((callLog) => {
    let _rows = {}
    callLogs.value?.data.rows.forEach((row) => {
      _rows[row] = getCallLogDetail(row, callLog, callLogs.value?.data.columns)
    })
    return _rows
  })
})

const columns = computed(() => {
  let _columns = callLogs.value?.data?.columns || []

  // Set align right for last column
  if (_columns.length) {
    _columns = _columns.map((col, index) => {
      if (index === _columns.length - 1) {
        return { ...col, align: 'right' }
      }
      return col
    })
  }

  return _columns
})

const showCallLogDetailModal = ref(false)
const callLog = ref({})

function showCallLog(name) {
  showCallLogDetailModal.value = true
  callLog.value = createResource({
    url: 'crm.fcrm.doctype.crm_call_log.crm_call_log.get_call_log',
    params: { name },
    cache: ['call_log', name],
    auto: true,
  })
}

const { showModal } = useDoctypeModal()
const { capture } = useTelemetry()

function createCallLog() {
  showModal({
    doctype: 'CRM Call Log',
    title: 'Call Log',
    callbacks: {
      afterInsert: () => {
        capture('call_log_created')
        callLogs.value.reload()
      },
    },
  })
}

const openCallLogFromURL = () => {
  const searchParams = new URLSearchParams(window.location.search)
  const callLogName = searchParams.get('open')

  if (callLogName) {
    showCallLog(callLogName)
    searchParams.delete('open')
    window.history.replaceState(null, '', window.location.pathname)
  }
}

onMounted(() => {
  openCallLogFromURL()
})
</script>
