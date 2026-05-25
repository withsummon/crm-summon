<template>
  <div
    v-if="visible"
    class="absolute z-50 w-[360px] rounded-[14px] border border-outline-gray-2 bg-white p-4 shadow-lg"
    :style="positionStyle"
    @mouseenter="clearHide"
    @mouseleave="startHide"
  >
    <div v-if="loading" class="flex h-20 items-center justify-center">
      <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
    </div>
    <template v-else-if="lead">
      <div class="flex items-start gap-3">
        <Avatar
          size="xl"
          class="size-10"
          :label="lead.lead_name || lead.name"
          :image="lead.image"
        />
        <div class="min-w-0 flex-1">
          <div class="truncate text-sm font-semibold text-ink-gray-9">
            {{ lead.lead_name || lead.name }}
          </div>
          <div class="truncate text-xs text-ink-gray-5">
            {{ lead.organization || '-' }}
          </div>
        </div>
      </div>

      <div class="mt-3 flex flex-wrap gap-2">
        <Badge
          v-if="lead.lead_score_band"
          :label="`${lead.lead_score_band} ${lead.lead_score || 0}`"
          variant="subtle"
          theme="blue"
        />
        <Badge
          v-if="lead.capture_channel"
          :label="lead.capture_channel"
          variant="subtle"
          theme="teal"
        />
        <Badge
          v-if="lead.sla_status"
          :label="lead.sla_status"
          variant="subtle"
          :theme="slaTheme(lead.sla_status)"
        />
        <Badge
          v-if="agingLabel"
          :label="agingLabel"
          variant="subtle"
          theme="gray"
        />
      </div>

      <div class="mt-3 grid grid-cols-2 gap-2 text-xs text-ink-gray-6">
        <div>{{ __('Owner') }}: {{ lead.lead_owner_name || lead.lead_owner || '-' }}</div>
        <div>{{ __('Source') }}: {{ lead.source || '-' }}</div>
        <div>{{ __('Campaign') }}: {{ lead.campaign || '-' }}</div>
        <div>{{ __('Last activity') }}: {{ formatDate(lead.last_activity_on || lead.modified) }}</div>
      </div>

      <div class="mt-3 flex gap-2">
        <Button size="sm" variant="outline" @click="makeCall">
          <template #prefix><FeatherIcon name="phone" class="h-3.5 w-3.5" /></template>
          {{ __('Call') }}
        </Button>
        <Button size="sm" variant="outline" @click="sendEmail">
          <template #prefix><FeatherIcon name="mail" class="h-3.5 w-3.5" /></template>
          {{ __('Email') }}
        </Button>
        <Button size="sm" variant="solid" class="ml-auto" @click="openLead">
          {{ __('Open') }}
        </Button>
      </div>

      <div v-if="summary?.duplicates?.length" class="mt-3 rounded border border-outline-gray-1 bg-surface-gray-1 p-2">
        <div class="text-[11px] font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Duplicate Candidates') }}</div>
        <div class="mt-1 space-y-1">
          <div v-for="d in summary.duplicates.slice(0, 2)" :key="d.name" class="flex items-center justify-between text-xs">
            <span class="truncate">{{ d.lead_name || d.name }}</span>
            <Badge :label="`${d.score}%`" theme="orange" variant="subtle" size="sm" />
          </div>
        </div>
      </div>

      <div v-if="summary?.tags?.length" class="mt-2 flex flex-wrap gap-1">
        <Badge
          v-for="tag in summary.tags.slice(0, 5)"
          :key="tag.tag"
          :label="tag.tag"
          theme="teal"
          variant="subtle"
          size="sm"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { Avatar, Badge, Button, FeatherIcon, LoadingIndicator, createResource, call, toast } from 'frappe-ui'
import { computed, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import { globalStore } from '@/stores/global'

const props = defineProps({
  visible: { type: Boolean, default: false },
  leadName: { type: String, default: '' },
  positionStyle: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['close'])

const router = useRouter()
const { makeCall: doMakeCall } = globalStore()

const hideTimer = ref(null)
const loading = ref(false)
const lead = ref(null)

const summary = createResource({
  url: 'crm.api.lead_management.get_lead_uat_summary',
  makeParams: () => ({ lead: props.leadName }),
})

watch(() => props.visible, async (val) => {
  if (!val) {
    lead.value = null
    return
  }
  if (!props.leadName) return
  loading.value = true
  try {
    const fields = ['lead_name', 'organization', 'mobile_no', 'email', 'lead_owner', 'capture_channel', 'lead_score_band', 'lead_score', 'sla_status', 'last_activity_on', 'modified', 'source', 'campaign', 'image']
    const row = await call('frappe.client.get_value', {
      doctype: 'CRM Lead',
      filters: { name: props.leadName },
      fieldname: fields,
    })
    if (row) {
      const ownerName = row.lead_owner ? await call('frappe.client.get_value', { doctype: 'User', filters: { name: row.lead_owner }, fieldname: 'full_name' }) : null
      lead.value = { ...row, lead_owner_name: ownerName?.full_name || row.lead_owner }
    }
    summary.fetch()
  } catch (e) {
    toast.error(__('Failed to load lead preview'))
  } finally {
    loading.value = false
  }
})

function slaTheme(status) {
  if (status === 'Failed' || status === 'Breached') return 'red'
  if (status === 'At Risk') return 'orange'
  if (status === 'Fulfilled') return 'green'
  return 'gray'
}

const agingLabel = computed(() => {
  if (!lead.value?.last_activity_on) return null
  const days = Math.floor((Date.now() - new Date(lead.value.last_activity_on).getTime()) / (1000 * 60 * 60 * 24))
  if (days > 60) return `Frozen (${days}d)`
  if (days > 30) return `Stale (${days}d)`
  if (days > 14) return `Warm (${days}d)`
  return `Fresh (${days}d)`
})

function formatDate(value) {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function openLead() {
  emit('close')
  router.push({ name: 'Lead', params: { leadId: props.leadName } })
}

function makeCall() {
  if (lead.value?.mobile_no) {
    doMakeCall(lead.value.mobile_no)
  } else {
    toast.error(__('No mobile number'))
  }
}

function sendEmail() {
  if (lead.value?.email) {
    window.location.href = `mailto:${lead.value.email}`
  } else {
    toast.error(__('No email address'))
  }
}

function clearHide() {
  if (hideTimer.value) {
    clearTimeout(hideTimer.value)
    hideTimer.value = null
  }
}

function startHide() {
  hideTimer.value = setTimeout(() => emit('close'), 400)
}
</script>
