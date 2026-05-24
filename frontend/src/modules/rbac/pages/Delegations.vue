<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-gray-100 transition-colors hover:bg-gray-200" @click="$router.push({ name: 'RBAC Admin' })">
            <LucideArrowLeft class="h-4 w-4 text-crm-text" />
          </button>
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px]" style="background: linear-gradient(135deg, #14b8a6, #2dd4bf)">
            <LucideUserPlus class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">{{ __('Delegations') }}</h1>
        </div>
      </template>
      <template #right-header>
        <Button :label="__('New Delegation')" variant="solid" @click="showNewDialog = true">
          <template #prefix><LucidePlus class="h-4 w-4" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-crm-teal border-t-transparent" />
      </div>

      <div v-else-if="delegations.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="d in delegations" :key="d.name" class="rounded-[14px] bg-white p-5 shadow-sm border border-crm-border">
          <div class="flex items-center justify-between mb-2">
            <Badge :label="d.status" variant="subtle" :theme="d.status === 'Active' ? 'green' : 'gray'" />
            <span class="text-xs text-crm-muted">{{ d.role }}</span>
          </div>
          <div class="text-sm">
            <span class="font-medium text-crm-text">{{ d.delegator }}</span>
            <span class="text-crm-muted"> → </span>
            <span class="font-medium text-crm-text">{{ d.delegate }}</span>
          </div>
          <div class="mt-2 text-xs text-crm-muted">
            {{ formatDate(d.from_date) }} → {{ formatDate(d.to_date) }}
          </div>
          <div v-if="d.reason" class="mt-1 text-xs text-crm-muted truncate">{{ d.reason }}</div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideUserPlus class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No active delegations') }}</h3>
      </div>
    </div>

    <Dialog v-model="showNewDialog" :options="{ title: 'New Delegation', size: 'md' }">
      <template #body>
        <div class="space-y-4">
          <FormControl label="Delegator" type="autocomplete" :fetchOptions="() => userOptions" v-model="form.delegator" :placeholder="'Select delegator'" />
          <FormControl label="Delegate" type="autocomplete" :fetchOptions="() => userOptions" v-model="form.delegate" :placeholder="'Select delegate'" />
          <FormControl label="Role" type="autocomplete" :fetchOptions="() => roleOptions" v-model="form.role" :placeholder="'Select role'" />
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="From Date" type="date" v-model="form.from_date" />
            <FormControl label="To Date" type="date" v-model="form.to_date" />
          </div>
          <FormControl label="Reason" type="textarea" v-model="form.reason" :placeholder="'Reason for delegation'" />
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Max Amount (IDR)" type="number" v-model="form.max_amount" :placeholder="'0'" />
            <FormControl label="Branch Only" type="checkbox" v-model="form.branch_only" />
          </div>
        </div>
      </template>
      <template #actions>
        <Button label="Cancel" variant="outline" @click="showNewDialog = false" />
        <Button label="Create" variant="solid" :loading="saving" @click="createDelegation" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideUserPlus from '~icons/lucide/user-plus'
import LucidePlus from '~icons/lucide/plus'
import { Badge, Button, Dialog, FormControl, call } from 'frappe-ui'
import { ref, onMounted } from 'vue'

const loading = ref(true)
const saving = ref(false)
const delegations = ref([])
const showNewDialog = ref(false)
const form = ref({ from_date: '', to_date: '', reason: '', max_amount: 0, branch_only: 0 })
const userOptions = ref([])
const roleOptions = ref([])

function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '-' }

async function fetchDelegations() {
  loading.value = true
  try { delegations.value = await call('crm.api.rbac.get_delegations') }
  catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function createDelegation() {
  if (!form.value.delegator || !form.value.delegate || !form.value.role) return
  saving.value = true
  try {
    await call('frappe.client.insert', {
      doc: { doctype: 'FCRM Delegation', ...form.value, enabled: 1 }
    })
    showNewDialog.value = false
    form.value = { from_date: '', to_date: '', reason: '', max_amount: 0, branch_only: 0 }
    fetchDelegations()
  } catch (err) { console.error(err) }
  finally { saving.value = false }
}

onMounted(async () => {
  userOptions.value = (await call('frappe.client.get_list', { doctype: 'User', fields: ['name'], limit_page_length: 500 })).map(u => ({ label: u.name, value: u.name }))
  roleOptions.value = (await call('crm.api.rbac.get_roles')).filter(r => r.name.startsWith('FCRM')).map(r => ({ label: r.name, value: r.name }))
  fetchDelegations()
})
</script>
