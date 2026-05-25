<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-gray-100 transition-colors hover:bg-gray-200" @click="$router.push({ name: 'RBAC Admin' })">
            <LucideArrowLeft class="h-4 w-4 text-crm-text" />
          </button>
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px]" style="background: linear-gradient(135deg, #10b981, #34d399)">
            <LucideGitBranch class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">{{ __('Branch Management') }}</h1>
        </div>
      </template>
      <template #right-header>
        <Button :label="__('New Branch')" variant="solid" @click="showNewDialog = true">
          <template #prefix><LucidePlus class="h-4 w-4" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-crm-teal border-t-transparent" />
      </div>

      <div v-else-if="branches.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="branch in branches" :key="branch.name" class="rounded-[14px] bg-white p-5 shadow-sm border border-crm-border">
          <div class="flex items-center justify-between mb-3">
            <Badge :label="branch.branch_type" variant="subtle" theme="blue" />
            <span class="text-xs text-crm-muted">{{ branch.branch_code }}</span>
          </div>
          <h3 class="text-sm font-semibold text-crm-text">{{ branch.branch_name }}</h3>
          <p v-if="branch.city" class="mt-1 text-xs text-crm-muted">{{ branch.city }}{{ branch.region ? ` · ${branch.region}` : '' }}</p>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideGitBranch class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No branches configured') }}</h3>
      </div>
    </div>

    <Dialog v-model="showNewDialog" :options="{ title: __('Create Branch'), size: 'md' }">
      <template #body-content>
        <div class="flex flex-col gap-4">
          <FormControl :label="__('Branch Code')" v-model="form.branch_code" :placeholder="__('e.g. BDG001')" />
          <FormControl :label="__('Branch Name')" v-model="form.branch_name" :placeholder="__('e.g. Bandung Main Branch')" />
          <FormControl :label="__('Branch Type')" type="select" v-model="form.branch_type" :options="branchTypes" />
          <FormControl :label="__('Region')" v-model="form.region" />
          <FormControl :label="__('City')" v-model="form.city" />
        </div>
      </template>
      <template #actions>
        <Button variant="solid" :label="__('Save')" :loading="saving" @click="createBranch" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideGitBranch from '~icons/lucide/git-branch'
import LucidePlus from '~icons/lucide/plus'
import { Badge, Button, Dialog, FormControl, call } from 'frappe-ui'
import { ref, reactive, onMounted } from 'vue'

const loading = ref(true)
const saving = ref(false)
const showNewDialog = ref(false)
const branches = ref([])
const form = reactive({ branch_code: '', branch_name: '', branch_type: 'Sub Branch', region: '', city: '' })

const branchTypes = [
  { label: 'Main Branch', value: 'Main Branch' },
  { label: 'Sub Branch', value: 'Sub Branch' },
  { label: 'Micro Branch', value: 'Micro Branch' },
  { label: 'Digital Branch', value: 'Digital Branch' },
  { label: 'Kantor Kas', value: 'Kantor Kas' },
]

async function fetchBranches() {
  loading.value = true
  try {
    branches.value = await call('crm.api.rbac.get_branches')
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function createBranch() {
  if (!form.branch_code || !form.branch_name) return
  saving.value = true
  try {
    await call('frappe.client.insert', {
      doc: { doctype: 'FCRM Branch', ...form, is_active: 1 }
    })
    showNewDialog.value = false
    form.branch_code = ''; form.branch_name = ''; form.branch_type = 'Sub Branch'; form.region = ''; form.city = ''
    fetchBranches()
  } catch (err) { console.error(err) }
  finally { saving.value = false }
}

onMounted(fetchBranches)
</script>
