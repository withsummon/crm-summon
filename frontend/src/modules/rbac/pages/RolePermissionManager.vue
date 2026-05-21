<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #f59e0b, #fbbf24)"
          >
            <LucideKey class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">
            {{ __('Role Permission Manager') }}
          </h1>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <!-- Role Selector -->
      <div class="mb-6 flex items-center gap-4">
        <FormControl
          :label="__('Select Role')"
          type="select"
          v-model="selectedRole"
          :options="roleOptions"
          class="w-72"
        />
        <FormControl
          :label="__('DocType Filter')"
          v-model="doctypeFilter"
          :placeholder="__('Filter by DocType...')"
          class="w-72"
        />
      </div>

      <!-- Permissions Table -->
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-crm-teal border-t-transparent" />
      </div>

      <div v-else-if="!selectedRole" class="flex flex-col items-center justify-center py-20">
        <LucideShieldQuestion class="h-16 w-16 text-crm-muted/30 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('Select a Role') }}</h3>
        <p class="mt-1 text-sm text-crm-muted">{{ __('Choose a role to view and manage its permissions') }}</p>
      </div>

      <div v-else-if="filteredPerms.length" class="rounded-[18px] bg-white shadow-sm border border-crm-border overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-crm-surface-light">
                <th class="px-4 py-3 text-left font-semibold text-crm-text sticky left-0 bg-crm-surface-light z-10">{{ __('DocType') }}</th>
                <th class="px-3 py-3 text-center font-medium text-crm-muted w-16">{{ __('Level') }}</th>
                <th v-for="perm in permColumns" :key="perm.field" class="px-3 py-3 text-center font-medium text-crm-muted w-16">
                  {{ __(perm.label) }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in filteredPerms"
                :key="row.name"
                class="border-t border-crm-border/50 hover:bg-crm-surface-light transition-colors"
              >
                <td class="px-4 py-3 font-medium text-crm-text sticky left-0 bg-white z-10">
                  {{ row.parent }}
                </td>
                <td class="px-3 py-3 text-center text-crm-muted">{{ row.permlevel }}</td>
                <td v-for="perm in permColumns" :key="perm.field" class="px-3 py-3 text-center">
                  <label class="flex items-center justify-center cursor-pointer">
                    <input
                      type="checkbox"
                      :checked="row[perm.field]"
                      @change="updatePerm(row, perm.field, $event)"
                      class="h-4 w-4 rounded border-gray-300 text-crm-teal focus:ring-crm-teal/30 cursor-pointer"
                    />
                  </label>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideShieldOff class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No permissions found') }}</h3>
        <p class="mt-1 text-sm text-crm-muted">{{ __('This role has no DocType permissions configured') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideKey from '~icons/lucide/key'
import LucideShieldQuestion from '~icons/lucide/shield-question'
import LucideShieldOff from '~icons/lucide/shield-off'
import { FormControl, createListResource, call } from 'frappe-ui'
import { usePageMeta } from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const selectedRole = ref('')
const doctypeFilter = ref('')
const loading = ref(false)
const permsData = ref([])

const permColumns = [
  { field: 'read', label: 'Read' },
  { field: 'write', label: 'Write' },
  { field: 'create', label: 'Create' },
  { field: 'delete', label: 'Delete' },
  { field: 'submit', label: 'Submit' },
  { field: 'cancel', label: 'Cancel' },
  { field: 'amend', label: 'Amend' },
  { field: 'report', label: 'Report' },
  { field: 'export', label: 'Export' },
  { field: 'import', label: 'Import' },
  { field: 'share', label: 'Share' },
  { field: 'print', label: 'Print' },
  { field: 'email', label: 'Email' },
]

const roles = createListResource({
  doctype: 'Role',
  fields: ['name'],
  filters: {
    disabled: 0,
    name: ['not in', ['All', 'Guest', 'Administrator']],
  },
  orderBy: 'name asc',
  pageLength: 200,
  auto: true,
})

const roleOptions = computed(() => {
  const opts = [{ label: __('Select Role...'), value: '' }]
  ;(roles.data || []).forEach((r) => {
    opts.push({ label: r.name, value: r.name })
  })
  return opts
})

const filteredPerms = computed(() => {
  if (!doctypeFilter.value) return permsData.value
  const q = doctypeFilter.value.toLowerCase()
  return permsData.value.filter((p) => p.parent.toLowerCase().includes(q))
})

watch(selectedRole, async (role) => {
  if (!role) {
    permsData.value = []
    return
  }
  loading.value = true
  try {
    const data = await call(
      'frappe.core.page.permission_manager.permission_manager.get_permissions',
      { role }
    )
    permsData.value = data || []
  } catch (err) {
    console.error('Error loading perms:', err)
  } finally {
    loading.value = false
  }
})

async function updatePerm(row, field, event) {
  const checked = event.target.checked ? 1 : 0
  try {
    await call('frappe.core.page.permission_manager.permission_manager.update', {
      doctype: row.parent,
      role: selectedRole.value,
      permlevel: row.permlevel,
      ptype: field,
      value: checked ? '1' : '0',
    })
    row[field] = checked
  } catch (err) {
    console.error('Error updating perm:', err)
    event.target.checked = !checked
  }
}

usePageMeta(() => ({ title: __('Role Permission Manager') }))
</script>
