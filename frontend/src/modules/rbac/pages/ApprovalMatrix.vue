<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-gray-100 transition-colors hover:bg-gray-200" @click="$router.push({ name: 'RBAC Admin' })">
            <LucideArrowLeft class="h-4 w-4 text-crm-text" />
          </button>
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px]" style="background: linear-gradient(135deg, #f59e0b, #fbbf24)">
            <LucideFileSignature class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">{{ __('Approval Authority Matrix') }}</h1>
        </div>
      </template>
      <template #right-header>
        <Button :label="__('New Rule')" variant="solid" @click="showNewDialog = true">
          <template #prefix><LucidePlus class="h-4 w-4" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-crm-teal border-t-transparent" />
      </div>

      <div v-else-if="rules.length" class="rounded-[18px] bg-white shadow-sm border border-crm-border overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-crm-surface-light">
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('Type') }}</th>
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('DocType') }}</th>
              <th class="px-4 py-3 text-right font-medium text-crm-muted">{{ __('Min Amount') }}</th>
              <th class="px-4 py-3 text-right font-medium text-crm-muted">{{ __('Max Amount') }}</th>
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('Approver Role') }}</th>
              <th class="px-4 py-3 text-center font-medium text-crm-muted">{{ __('Seq') }}</th>
              <th class="px-4 py-3 text-center font-medium text-crm-muted">{{ __('Flow') }}</th>
              <th class="px-4 py-3 text-center font-medium text-crm-muted">{{ __('Status') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rule in rules" :key="rule.name" class="border-t border-crm-border/50 hover:bg-crm-surface-light transition-colors">
              <td class="px-4 py-3 font-medium text-crm-text">{{ rule.approval_type }}</td>
              <td class="px-4 py-3 text-crm-muted">{{ rule.document_type }}</td>
              <td class="px-4 py-3 text-right">{{ formatCurrency(rule.min_amount) }}</td>
              <td class="px-4 py-3 text-right">{{ formatCurrency(rule.max_amount) }}</td>
              <td class="px-4 py-3">
                <Badge :label="rule.approver_role" variant="subtle" theme="purple" />
              </td>
              <td class="px-4 py-3 text-center">{{ rule.approval_sequence }}</td>
              <td class="px-4 py-3 text-center">
                <Badge :label="rule.approval_type" variant="subtle" :theme="rule.approval_type === 'Parallel' ? 'orange' : 'blue'" />
              </td>
              <td class="px-4 py-3 text-center">
                <span :class="rule.enabled ? 'text-crm-green' : 'text-gray-300'">{{ rule.enabled ? '✓' : '—' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideFileSignature class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No approval rules configured') }}</h3>
      </div>
    </div>

    <Dialog v-model="showNewDialog" :options="{ title: __('New Approval Rule'), size: 'lg' }">
      <template #body-content>
        <div class="grid grid-cols-2 gap-4">
          <FormControl :label="__('Approval Type')" type="select" v-model="form.approval_type" :options="approvalTypes" />
          <FormControl :label="__('Document Type')" type="select" v-model="form.document_type" :options="docTypes" />
          <FormControl :label="__('Min Amount (IDR)')" type="number" v-model="form.min_amount" />
          <FormControl :label="__('Max Amount (IDR)')" type="number" v-model="form.max_amount" />
          <FormControl :label="__('Approver Role')" v-model="form.approver_role" />
          <FormControl :label="__('Approval Sequence')" type="number" v-model="form.approval_sequence" />
          <FormControl :label="__('Approval Flow')" type="select" v-model="form.approval_flow" :options="flowTypes" />
        </div>
      </template>
      <template #actions>
        <Button variant="solid" :label="__('Save')" :loading="saving" @click="createRule" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideFileSignature from '~icons/lucide/file-signature'
import LucidePlus from '~icons/lucide/plus'
import { Badge, Button, Dialog, FormControl, call } from 'frappe-ui'
import { ref, reactive, onMounted } from 'vue'

const loading = ref(true)
const saving = ref(false)
const showNewDialog = ref(false)
const rules = ref([])
const form = reactive({ approval_type: 'Credit', document_type: 'CRM Credit Application', min_amount: 0, max_amount: 1000000000, approver_role: '', approval_sequence: 1, approval_flow: 'Sequential' })

const approvalTypes = [
  { label: 'Credit', value: 'Credit' }, { label: 'Disbursement', value: 'Disbursement' },
  { label: 'Waiver', value: 'Waiver' }, { label: 'Override', value: 'Override' },
  { label: 'Exception', value: 'Exception' },
]
const docTypes = [
  { label: 'Credit Application', value: 'CRM Credit Application' },
  { label: 'Credit Facility', value: 'CRM Credit Facility' },
  { label: 'Deal', value: 'CRM Deal' },
]
const flowTypes = [
  { label: 'Sequential', value: 'Sequential' },
  { label: 'Parallel', value: 'Parallel' },
]

function formatCurrency(val) {
  if (!val) return '-'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val)
}

async function fetchRules() {
  loading.value = true
  try { rules.value = await call('crm.api.rbac.get_approval_matrices') }
  catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function createRule() {
  if (!form.approver_role) return
  saving.value = true
  try {
    await call('frappe.client.insert', {
      doc: { doctype: 'FCRM Approval Matrix', ...form, enabled: 1 }
    })
    showNewDialog.value = false
    fetchRules()
  } catch (err) { console.error(err) }
  finally { saving.value = false }
}

onMounted(fetchRules)
</script>
