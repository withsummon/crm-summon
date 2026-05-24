<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-gray-100 transition-colors hover:bg-gray-200" @click="$router.push({ name: 'RBAC Admin' })">
            <LucideArrowLeft class="h-4 w-4 text-crm-text" />
          </button>
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px]" style="background: linear-gradient(135deg, #eab308, #facc15)">
            <LucideClock class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">{{ __('Just-in-Time Access') }}</h1>
        </div>
      </template>
      <template #right-header>
        <Button :label="__('Request Access')" variant="solid" @click="showNewDialog = true">
          <template #prefix><LucidePlus class="h-4 w-4" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <div class="mb-6 flex gap-3">
        <button v-for="tab in tabs" :key="tab.value"
          class="rounded-full px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === tab.value ? 'bg-crm-teal text-white shadow-sm' : 'bg-white text-crm-muted hover:bg-teal-50 hover:text-crm-text'"
          @click="activeTab = tab.value">{{ __(tab.label) }}</button>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-crm-teal border-t-transparent" />
      </div>

      <div v-else-if="filteredRequests.length" class="grid gap-4 sm:grid-cols-2">
        <div v-for="req in filteredRequests" :key="req.name" class="rounded-[14px] bg-white p-5 shadow-sm border border-crm-border">
          <div class="flex items-center justify-between mb-2">
            <Badge :label="req.status" variant="subtle" :theme="statusTheme(req.status)" />
            <span class="text-xs text-crm-muted">{{ req.duration_hours }}h</span>
          </div>
          <div class="text-sm">
            <span class="font-medium text-crm-text">{{ req.requester }}</span>
            <span class="text-crm-muted"> → </span>
            <Badge :label="req.requested_role" variant="subtle" theme="purple" />
          </div>
          <p class="mt-1 text-xs text-crm-muted">{{ req.reason }}</p>
          <div v-if="req.status === 'Pending'" class="mt-3 flex gap-2">
            <Button :label="__('Approve')" variant="solid" theme="green" size="sm" :loading="approving === req.name" @click="approve(req.name)" />
            <Button :label="__('Reject')" variant="outline" theme="red" size="sm" :loading="rejecting === req.name" @click="reject(req.name)" />
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideClock class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No JIT requests') }}</h3>
      </div>
    </div>

    <Dialog v-model="showNewDialog" :options="{ title: 'Request Access', size: 'md' }">
      <template #body>
        <div class="space-y-4">
          <FormControl label="Requested Role" type="autocomplete" :fetchOptions="() => roleOptions" v-model="form.requested_role" :placeholder="'Select role'" />
          <FormControl label="Reason" type="textarea" v-model="form.reason" :placeholder="'Why do you need this access?'" />
          <FormControl label="Duration (hours)" type="number" v-model="form.duration_hours" :placeholder="'4'" />
        </div>
      </template>
      <template #actions>
        <Button label="Cancel" variant="outline" @click="showNewDialog = false" />
        <Button label="Submit Request" variant="solid" :loading="saving" @click="createRequest" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideClock from '~icons/lucide/clock'
import LucidePlus from '~icons/lucide/plus'
import { Badge, Button, Dialog, FormControl, call } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'

const loading = ref(true)
const saving = ref(false)
const approving = ref('')
const rejecting = ref('')
const activeTab = ref('all')
const requests = ref([])
const showNewDialog = ref(false)
const form = ref({ requested_role: '', reason: '', duration_hours: 4 })
const roleOptions = ref([])

const tabs = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'Pending' },
  { label: 'Approved', value: 'Approved' },
  { label: 'Expired', value: 'Expired' },
]

const filteredRequests = computed(() => {
  if (activeTab.value === 'all') return requests.value
  return requests.value.filter(r => r.status === activeTab.value)
})

function statusTheme(s) {
  return { Pending: 'orange', Approved: 'green', Rejected: 'red', Expired: 'gray', Revoked: 'gray' }[s] || 'gray'
}

async function fetchRequests() {
  loading.value = true
  try { requests.value = await call('crm.api.rbac.get_jit_requests') }
  catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function createRequest() {
  if (!form.value.requested_role || !form.value.reason) return
  saving.value = true
  try {
    await call('crm.api.rbac.create_jit_request', {
      role: form.value.requested_role,
      reason: form.value.reason,
      duration_hours: form.value.duration_hours || 4,
    })
    showNewDialog.value = false
    form.value = { requested_role: '', reason: '', duration_hours: 4 }
    fetchRequests()
  } catch (err) { console.error(err) }
  finally { saving.value = false }
}

async function approve(name) {
  approving.value = name
  try { await call('crm.api.rbac.approve_jit_request', { name }); fetchRequests() }
  catch (err) { console.error(err) }
  finally { approving.value = '' }
}

async function reject(name) {
  rejecting.value = name
  try { await call('crm.api.rbac.reject_jit_request', { name }); fetchRequests() }
  catch (err) { console.error(err) }
  finally { rejecting.value = '' }
}

onMounted(async () => {
  roleOptions.value = (await call('crm.api.rbac.get_roles')).filter(r => r.name.startsWith('FCRM')).map(r => ({ label: r.name, value: r.name }))
  fetchRequests()
})
</script>
