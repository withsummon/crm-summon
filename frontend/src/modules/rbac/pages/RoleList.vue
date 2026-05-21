<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #6366f1, #818cf8)"
          >
            <LucideShield class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">
            {{ __('Roles') }}
          </h1>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <div class="relative">
            <LucideSearch
              class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-crm-muted"
            />
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="__('Search roles...')"
              class="h-9 w-64 rounded-[10px] border border-crm-border bg-white pl-9 pr-4 text-sm outline-none transition-all focus:border-crm-orange focus:ring-2 focus:ring-crm-orange/20"
            />
          </div>
          <Button
            :label="__('New Role')"
            variant="solid"
            @click="showNewRoleDialog = true"
          >
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <!-- Tabs -->
      <div class="mb-6 flex items-center gap-3">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="rounded-full px-4 py-2 text-sm font-medium transition-all"
          :class="
            activeTab === tab.value
              ? 'bg-crm-purple text-white shadow-sm'
              : 'bg-white text-crm-muted hover:bg-purple-50 hover:text-crm-text'
          "
          @click="activeTab = tab.value"
        >
          {{ __(tab.label) }}
        </button>
      </div>

      <!-- Roles Grid -->
      <div v-if="loading" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="i in 6" :key="i" class="h-16 animate-pulse rounded-[14px] bg-white shadow-sm" />
      </div>

      <div v-else-if="filteredRoles.length" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="role in filteredRoles"
          :key="role.name"
          class="flex items-center justify-between rounded-[14px] bg-white p-4 shadow-sm border border-transparent transition-all hover:shadow-md hover:border-crm-purple/20 cursor-pointer"
          @click="viewRolePerms(role.name)"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-9 w-9 items-center justify-center rounded-[10px]"
              :class="role.is_custom ? 'bg-crm-peach' : 'bg-indigo-50'"
            >
              <LucideShieldCheck
                class="h-4 w-4"
                :class="role.is_custom ? 'text-crm-orange' : 'text-indigo-500'"
              />
            </div>
            <div>
              <div class="text-sm font-semibold text-crm-text">{{ role.name }}</div>
              <div class="text-xs text-crm-muted">
                {{ role.is_custom ? __('Custom') : __('Standard') }}
              </div>
            </div>
          </div>
          <Badge
            v-if="role.disabled"
            label="Disabled"
            variant="subtle"
            theme="red"
          />
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideShieldOff class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No roles found') }}</h3>
      </div>

      <!-- Role Permissions Panel -->
      <Dialog
        v-model="showRolePerms"
        :options="{ title: selectedRole ? `${__('Permissions')}: ${selectedRole}` : __('Permissions'), size: 'xl' }"
      >
        <template #body-content>
          <div v-if="rolePermsLoading" class="flex items-center justify-center py-8">
            <div class="h-6 w-6 animate-spin rounded-full border-2 border-crm-orange border-t-transparent" />
          </div>
          <div v-else-if="rolePerms.length" class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-crm-border">
                  <th class="py-2 pr-4 text-left font-medium text-crm-muted">{{ __('DocType') }}</th>
                  <th class="px-2 py-2 text-center font-medium text-crm-muted">{{ __('Read') }}</th>
                  <th class="px-2 py-2 text-center font-medium text-crm-muted">{{ __('Write') }}</th>
                  <th class="px-2 py-2 text-center font-medium text-crm-muted">{{ __('Create') }}</th>
                  <th class="px-2 py-2 text-center font-medium text-crm-muted">{{ __('Delete') }}</th>
                  <th class="px-2 py-2 text-center font-medium text-crm-muted">{{ __('Submit') }}</th>
                  <th class="px-2 py-2 text-center font-medium text-crm-muted">{{ __('Export') }}</th>
                  <th class="px-2 py-2 text-center font-medium text-crm-muted">{{ __('Report') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="perm in rolePerms"
                  :key="perm.name"
                  class="border-b border-crm-border/50 hover:bg-crm-peach-light transition-colors"
                >
                  <td class="py-2.5 pr-4 font-medium text-crm-text">{{ perm.parent }}</td>
                  <td class="px-2 py-2.5 text-center">
                    <span :class="perm.read ? 'text-crm-green' : 'text-gray-300'">{{ perm.read ? '✓' : '—' }}</span>
                  </td>
                  <td class="px-2 py-2.5 text-center">
                    <span :class="perm.write ? 'text-crm-green' : 'text-gray-300'">{{ perm.write ? '✓' : '—' }}</span>
                  </td>
                  <td class="px-2 py-2.5 text-center">
                    <span :class="perm.create ? 'text-crm-green' : 'text-gray-300'">{{ perm.create ? '✓' : '—' }}</span>
                  </td>
                  <td class="px-2 py-2.5 text-center">
                    <span :class="perm['delete'] ? 'text-crm-green' : 'text-gray-300'">{{ perm['delete'] ? '✓' : '—' }}</span>
                  </td>
                  <td class="px-2 py-2.5 text-center">
                    <span :class="perm.submit ? 'text-crm-green' : 'text-gray-300'">{{ perm.submit ? '✓' : '—' }}</span>
                  </td>
                  <td class="px-2 py-2.5 text-center">
                    <span :class="perm['export'] ? 'text-crm-green' : 'text-gray-300'">{{ perm['export'] ? '✓' : '—' }}</span>
                  </td>
                  <td class="px-2 py-2.5 text-center">
                    <span :class="perm.report ? 'text-crm-green' : 'text-gray-300'">{{ perm.report ? '✓' : '—' }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="py-8 text-center text-crm-muted">
            {{ __('No permissions configured for this role') }}
          </div>
        </template>
      </Dialog>
    </div>

    <!-- New Role Dialog -->
    <Dialog v-model="showNewRoleDialog" :options="{ title: __('Create New Role'), size: 'sm' }">
      <template #body-content>
        <FormControl
          :label="__('Role Name')"
          v-model="newRoleName"
          :placeholder="__('e.g. Sales Manager')"
        />
      </template>
      <template #actions>
        <Button
          variant="solid"
          :label="__('Create')"
          :loading="creatingRole"
          @click="createRole"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideShield from '~icons/lucide/shield'
import LucideShieldCheck from '~icons/lucide/shield-check'
import LucideShieldOff from '~icons/lucide/shield-off'
import LucideSearch from '~icons/lucide/search'
import LucidePlus from '~icons/lucide/plus'
import { Badge, Dialog, FormControl, call } from 'frappe-ui'
import { usePageMeta } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'

const searchQuery = ref('')
const activeTab = ref('all')
const selectedRole = ref(null)
const showNewRoleDialog = ref(false)
const newRoleName = ref('')
const creatingRole = ref(false)
const loading = ref(true)
const rolesList = ref([])
const rolePerms = ref([])
const rolePermsLoading = ref(false)

const tabs = [
  { label: 'All Roles', value: 'all' },
  { label: 'Standard', value: 'standard' },
  { label: 'Custom', value: 'custom' },
]

async function fetchRoles() {
  loading.value = true
  try {
    const data = await call('frappe.client.get_list', {
      doctype: 'Role',
      fields: ['name', 'is_custom', 'disabled'],
      filters: { name: ['not in', ['All', 'Guest', 'Administrator', 'Desk User']] },
      order_by: 'name asc',
      limit_page_length: 200,
    })
    rolesList.value = data
  } catch (err) {
    console.error('Error fetching roles:', err)
  } finally {
    loading.value = false
  }
}

const filteredRoles = computed(() => {
  let result = rolesList.value

  if (activeTab.value === 'standard') {
    result = result.filter((r) => !r.is_custom)
  } else if (activeTab.value === 'custom') {
    result = result.filter((r) => r.is_custom)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter((r) => r.name.toLowerCase().includes(q))
  }

  return result
})

const showRolePerms = computed({
  get: () => !!selectedRole.value,
  set: (val) => { if (!val) selectedRole.value = null },
})

async function viewRolePerms(roleName) {
  selectedRole.value = roleName
  rolePermsLoading.value = true
  try {
    // Use Frappe's built-in permission_manager API
    const data = await call(
      'frappe.core.page.permission_manager.permission_manager.get_permissions',
      { role: roleName },
    )
    rolePerms.value = data || []
  } catch (err) {
    console.error('Error loading permissions:', err)
    rolePerms.value = []
  } finally {
    rolePermsLoading.value = false
  }
}

async function createRole() {
  if (!newRoleName.value) return
  creatingRole.value = true
  try {
    await call('frappe.client.insert', {
      doc: { doctype: 'Role', role_name: newRoleName.value, is_custom: 1 },
    })
    showNewRoleDialog.value = false
    newRoleName.value = ''
    fetchRoles()
  } catch (err) {
    console.error('Error creating role:', err)
  } finally {
    creatingRole.value = false
  }
}

onMounted(fetchRoles)

usePageMeta(() => ({ title: __('Roles') }))
</script>
