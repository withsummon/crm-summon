<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-gray-100 transition-colors hover:bg-gray-200" @click="$router.push({ name: 'RBAC Admin' })">
            <LucideArrowLeft class="h-4 w-4 text-crm-text" />
          </button>
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px]" style="background: linear-gradient(135deg, #f97316, #fb923c)">
            <LucideScale class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">{{ __('Segregation of Duties') }}</h1>
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

      <div v-else-if="sodRules.length" class="grid gap-4 sm:grid-cols-2">
        <div v-for="rule in sodRules" :key="rule.name" class="rounded-[14px] bg-white p-5 shadow-sm border border-crm-border">
          <div class="flex items-center gap-3">
            <Badge :label="rule.role_a" variant="subtle" theme="red" />
            <LucideX class="h-4 w-4 text-red-400" />
            <Badge :label="rule.role_b" variant="subtle" theme="red" />
          </div>
          <div class="mt-2">
            <Badge :label="rule.conflict_type" variant="subtle" theme="orange" />
          </div>
          <p v-if="rule.description" class="mt-2 text-xs text-crm-muted">{{ rule.description }}</p>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideScale class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No SoD rules configured') }}</h3>
      </div>
    </div>

    <Dialog v-model="showNewDialog" :options="{ title: 'New SoD Rule', size: 'md' }">
      <template #body>
        <div class="space-y-4">
          <FormControl label="Role A" type="autocomplete" :fetchOptions="() => roleOptions" v-model="form.role_a" :placeholder="'Select first role'" />
          <FormControl label="Role B" type="autocomplete" :fetchOptions="() => roleOptions" v-model="form.role_b" :placeholder="'Select second role'" />
          <FormControl label="Conflict Type" type="select" v-model="form.conflict_type" :options="conflictTypes" />
          <FormControl label="Description" type="textarea" v-model="form.description" :placeholder="'Describe the conflict...'" />
          <FormControl label="Allow Override with Approval" type="checkbox" v-model="form.allow_override" />
        </div>
      </template>
      <template #actions>
        <Button label="Cancel" variant="outline" @click="showNewDialog = false" />
        <Button label="Create" variant="solid" :loading="saving" @click="createRule" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideScale from '~icons/lucide/scale'
import LucideX from '~icons/lucide/x'
import LucidePlus from '~icons/lucide/plus'
import { Badge, Button, Dialog, FormControl, call } from 'frappe-ui'
import { ref, onMounted } from 'vue'

const loading = ref(true)
const saving = ref(false)
const sodRules = ref([])
const showNewDialog = ref(false)
const form = ref({ conflict_type: 'Hard', description: '', allow_override: 0 })
const roleOptions = ref([])
const conflictTypes = ['Hard', 'Soft', 'Maker-Checker', 'Approval-Check', 'Data Access-Approval', 'Custom']

async function fetchRules() {
  loading.value = true
  try { sodRules.value = await call('crm.api.rbac.get_sod_rules') }
  catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function createRule() {
  if (!form.value.role_a || !form.value.role_b) return
  saving.value = true
  try {
    await call('frappe.client.insert', {
      doc: { doctype: 'FCRM SOD Rule', ...form.value, enabled: 1 }
    })
    showNewDialog.value = false
    form.value = { conflict_type: 'Hard', description: '', allow_override: 0 }
    fetchRules()
  } catch (err) { console.error(err) }
  finally { saving.value = false }
}

onMounted(async () => {
  roleOptions.value = (await call('crm.api.rbac.get_roles')).filter(r => r.name.startsWith('FCRM')).map(r => ({ label: r.name, value: r.name }))
  fetchRules()
})
</script>
