<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #10b981, #34d399)"
          >
            <LucideLock class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">
            {{ __('User Permissions') }}
          </h1>
        </div>
      </template>
      <template #right-header>
        <Button
          :label="__('Add Permission')"
          variant="solid"
          @click="showAddDialog = true"
        >
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-end gap-4">
        <FormControl
          :label="__('User')"
          v-model="filters.user"
          :placeholder="__('Filter by user...')"
          class="w-60"
        />
        <FormControl
          :label="__('Allow DocType')"
          type="select"
          v-model="filters.allow"
          :options="allowOptions"
          class="w-60"
        />
        <Button
          :label="__('Apply')"
          variant="subtle"
          @click="fetchPermissions"
        />
        <Button
          :label="__('Clear')"
          variant="ghost"
          @click="clearFilters"
        />
      </div>

      <!-- Permissions Table -->
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-crm-green border-t-transparent" />
      </div>

      <div v-else-if="permissions.length" class="rounded-[18px] bg-white shadow-sm border border-crm-border overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-[#fffaf6]">
              <th class="px-4 py-3 text-left font-semibold text-crm-text">{{ __('User') }}</th>
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('Allow') }}</th>
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('For Value') }}</th>
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('Applicable For') }}</th>
              <th class="px-4 py-3 text-center font-medium text-crm-muted">{{ __('Is Default') }}</th>
              <th class="px-4 py-3 text-center font-medium text-crm-muted w-16"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="perm in permissions"
              :key="perm.name"
              class="border-t border-crm-border/50 hover:bg-crm-peach-light transition-colors"
            >
              <td class="px-4 py-3 font-medium text-crm-text">{{ perm.user }}</td>
              <td class="px-4 py-3 text-crm-text">
                <Badge :label="perm.allow" variant="subtle" theme="blue" />
              </td>
              <td class="px-4 py-3 text-crm-text">{{ perm.for_value || '-' }}</td>
              <td class="px-4 py-3 text-crm-muted">{{ perm.applicable_for || __('All') }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="perm.is_default ? 'text-crm-green' : 'text-gray-300'">
                  {{ perm.is_default ? '✓' : '—' }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <button
                  class="rounded-md p-1.5 text-red-400 hover:bg-red-50 transition-colors"
                  @click="deletePermission(perm.name)"
                >
                  <LucideTrash class="h-4 w-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideLockOpen class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No user permissions found') }}</h3>
        <p class="mt-1 text-sm text-crm-muted">{{ __('Add user permissions to restrict document access') }}</p>
      </div>
    </div>

    <!-- Add Permission Dialog -->
    <Dialog v-model="showAddDialog" :options="{ title: __('Add User Permission'), size: 'md' }">
      <template #body-content>
        <div class="flex flex-col gap-4">
          <FormControl
            :label="__('User')"
            v-model="newPerm.user"
            :placeholder="__('user@example.com')"
          />
          <FormControl
            :label="__('Allow (DocType)')"
            v-model="newPerm.allow"
            :placeholder="__('e.g. Company, Branch')"
          />
          <FormControl
            :label="__('For Value')"
            v-model="newPerm.for_value"
            :placeholder="__('Document name to restrict to')"
          />
          <FormControl
            :label="__('Applicable For (optional)')"
            v-model="newPerm.applicable_for"
            :placeholder="__('Apply restriction only for this DocType')"
          />
        </div>
      </template>
      <template #actions>
        <Button
          variant="solid"
          :label="__('Add')"
          :loading="adding"
          @click="addPermission"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideLock from '~icons/lucide/lock'
import LucideLockOpen from '~icons/lucide/lock-open'
import LucidePlus from '~icons/lucide/plus'
import LucideTrash from '~icons/lucide/trash-2'
import { Badge, Dialog, FormControl, call } from 'frappe-ui'
import { usePageMeta } from 'frappe-ui'
import { ref, reactive, onMounted } from 'vue'

const loading = ref(false)
const adding = ref(false)
const showAddDialog = ref(false)
const permissions = ref([])

const filters = reactive({ user: '', allow: '' })
const newPerm = reactive({ user: '', allow: '', for_value: '', applicable_for: '' })

const allowOptions = [
  { label: __('All DocTypes'), value: '' },
  { label: 'Company', value: 'Company' },
  { label: 'Territory', value: 'Territory' },
  { label: 'Branch', value: 'Branch' },
  { label: 'Department', value: 'Department' },
  { label: 'Cost Center', value: 'Cost Center' },
]

async function fetchPermissions() {
  loading.value = true
  try {
    const f = {}
    if (filters.user) f.user = ['like', `%${filters.user}%`]
    if (filters.allow) f.allow = filters.allow

    const data = await call('frappe.client.get_list', {
      doctype: 'User Permission',
      filters: f,
      fields: ['name', 'user', 'allow', 'for_value', 'applicable_for', 'is_default'],
      order_by: 'user asc',
      limit_page_length: 200,
    })
    permissions.value = data
  } catch (err) {
    console.error('Error fetching user permissions:', err)
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  filters.user = ''
  filters.allow = ''
  fetchPermissions()
}

async function addPermission() {
  if (!newPerm.user || !newPerm.allow || !newPerm.for_value) return
  adding.value = true
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'User Permission',
        user: newPerm.user,
        allow: newPerm.allow,
        for_value: newPerm.for_value,
        applicable_for: newPerm.applicable_for || undefined,
      },
    })
    showAddDialog.value = false
    newPerm.user = ''
    newPerm.allow = ''
    newPerm.for_value = ''
    newPerm.applicable_for = ''
    fetchPermissions()
  } catch (err) {
    console.error('Error adding permission:', err)
  } finally {
    adding.value = false
  }
}

async function deletePermission(name) {
  try {
    await call('frappe.client.delete', { doctype: 'User Permission', name })
    permissions.value = permissions.value.filter((p) => p.name !== name)
  } catch (err) {
    console.error('Error deleting permission:', err)
  }
}

onMounted(fetchPermissions)

usePageMeta(() => ({ title: __('User Permissions') }))
</script>
