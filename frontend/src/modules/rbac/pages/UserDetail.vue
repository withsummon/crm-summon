<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button
            class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-gray-100 transition-colors hover:bg-gray-200"
            @click="$router.push({ name: 'User List' })"
          >
            <LucideArrowLeft class="h-4 w-4 text-crm-text" />
          </button>
          <Avatar
            :label="userData?.full_name || userId"
            :image="userData?.user_image"
            size="lg"
          />
          <div>
            <h1 class="text-lg font-semibold text-crm-text">
              {{ userData?.full_name || userId }}
            </h1>
            <span class="text-sm text-crm-muted">{{ userId }}</span>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Badge
            v-if="userData?.enabled"
            label="Active"
            variant="subtle"
            theme="green"
          />
          <Badge
            v-else
            label="Disabled"
            variant="subtle"
            theme="red"
          />
          <Badge
            v-if="userData?.user_type"
            :label="userData.user_type"
            variant="subtle"
            theme="blue"
          />
          <Button
            :label="userData?.enabled ? __('Disable') : __('Enable')"
            :variant="userData?.enabled ? 'outline' : 'solid'"
            @click="toggleUserEnabled"
            :loading="saving"
          />
        </div>
      </template>
    </LayoutHeader>

    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="h-8 w-8 animate-spin rounded-full border-4 border-crm-orange border-t-transparent" />
    </div>

    <div v-else-if="userData" class="flex-1 overflow-y-auto">
      <div class="mx-auto max-w-4xl p-6 space-y-6">
        <!-- Basic Info Card -->
        <div class="rounded-[18px] bg-white p-6 shadow-sm border border-crm-border">
          <h2 class="mb-4 text-base font-semibold text-crm-text flex items-center gap-2">
            <LucideUser class="h-4 w-4 text-crm-orange" />
            {{ __('Basic Information') }}
          </h2>
          <div class="grid gap-4 sm:grid-cols-2">
            <FormControl
              :label="__('First Name')"
              v-model="editData.first_name"
              @change="markDirty"
            />
            <FormControl
              :label="__('Last Name')"
              v-model="editData.last_name"
              @change="markDirty"
            />
            <FormControl
              :label="__('Email')"
              :modelValue="userId"
              disabled
            />
            <FormControl
              :label="__('Gender')"
              type="select"
              v-model="editData.gender"
              :options="[
                { label: '', value: '' },
                { label: __('Male'), value: 'Male' },
                { label: __('Female'), value: 'Female' },
                { label: __('Other'), value: 'Other' },
                { label: __('Prefer not to say'), value: 'Prefer not to say' },
              ]"
              @change="markDirty"
            />
            <FormControl
              :label="__('Birth Date')"
              type="date"
              v-model="editData.birth_date"
              @change="markDirty"
            />
            <FormControl
              :label="__('Phone')"
              v-model="editData.phone"
              @change="markDirty"
            />
            <FormControl
              :label="__('Location')"
              v-model="editData.location"
              @change="markDirty"
              class="sm:col-span-2"
            />
          </div>
          <div v-if="isDirty" class="mt-4 flex justify-end gap-2">
            <Button
              :label="__('Discard')"
              variant="outline"
              @click="resetEdits"
            />
            <Button
              :label="__('Save')"
              variant="solid"
              :loading="saving"
              @click="saveUserInfo"
            />
          </div>
        </div>

        <!-- Roles Card -->
        <div class="rounded-[18px] bg-white p-6 shadow-sm border border-crm-border">
          <h2 class="mb-4 text-base font-semibold text-crm-text flex items-center gap-2">
            <LucideShield class="h-4 w-4 text-crm-purple" />
            {{ __('Roles') }}
          </h2>

          <div class="mb-4 relative">
            <LucideSearch
              class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-crm-muted"
            />
            <input
              v-model="roleSearch"
              type="text"
              :placeholder="__('Search roles...')"
              class="h-9 w-full rounded-[10px] border border-crm-border bg-[#fffaf6] pl-9 pr-4 text-sm outline-none focus:border-crm-orange focus:ring-2 focus:ring-crm-orange/20"
            />
          </div>

          <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            <label
              v-for="role in filteredRoles"
              :key="role.name"
              class="flex cursor-pointer items-center gap-3 rounded-[10px] border p-3 transition-all"
              :class="
                userRoleNames.includes(role.name)
                  ? 'border-crm-orange/40 bg-crm-peach'
                  : 'border-crm-border hover:border-crm-soft-orange hover:bg-crm-peach-light'
              "
            >
              <input
                type="checkbox"
                :checked="userRoleNames.includes(role.name)"
                @change="toggleRole(role.name, $event)"
                class="h-4 w-4 rounded border-gray-300 text-crm-orange focus:ring-crm-orange/30"
              />
              <span class="text-sm font-medium text-crm-text">{{ role.name }}</span>
            </label>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="rounded-[18px] bg-white p-6 shadow-sm border border-crm-border">
          <h2 class="mb-4 text-base font-semibold text-crm-text flex items-center gap-2">
            <LucideClock class="h-4 w-4 text-crm-green" />
            {{ __('Activity') }}
          </h2>
          <div class="grid gap-3 sm:grid-cols-3">
            <div class="rounded-[10px] bg-[#fffaf6] p-4">
              <div class="text-xs text-crm-muted">{{ __('Last Active') }}</div>
              <div class="mt-1 text-sm font-semibold text-crm-text">
                {{ userData.last_active ? timeAgo(userData.last_active) : __('Never') }}
              </div>
            </div>
            <div class="rounded-[10px] bg-[#fffaf6] p-4">
              <div class="text-xs text-crm-muted">{{ __('Last Login') }}</div>
              <div class="mt-1 text-sm font-semibold text-crm-text">
                {{ userData.last_login ? timeAgo(userData.last_login) : __('Never') }}
              </div>
            </div>
            <div class="rounded-[10px] bg-[#fffaf6] p-4">
              <div class="text-xs text-crm-muted">{{ __('Created On') }}</div>
              <div class="mt-1 text-sm font-semibold text-crm-text">
                {{ userData.creation ? formatDate(userData.creation) : '-' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideUser from '~icons/lucide/user'
import LucideShield from '~icons/lucide/shield'
import LucideClock from '~icons/lucide/clock'
import LucideSearch from '~icons/lucide/search'
import {
  Avatar,
  Badge,
  FormControl,
  call,
} from 'frappe-ui'
import { usePageMeta } from 'frappe-ui'
import { ref, computed, reactive, watch, onMounted } from 'vue'

const props = defineProps({
  userId: { type: String, required: true },
})

const saving = ref(false)
const loading = ref(true)
const isDirty = ref(false)
const roleSearch = ref('')
const userData = ref(null)
const allRoles = ref([])
const userRoleNames = ref([])

const editData = reactive({
  first_name: '',
  last_name: '',
  gender: '',
  birth_date: '',
  phone: '',
  location: '',
})

// Fetch user document (includes roles as child table)
async function fetchUser() {
  loading.value = true
  try {
    const doc = await call('frappe.client.get', {
      doctype: 'User',
      name: props.userId,
    })
    userData.value = doc
    // Roles come from the user doc's 'roles' child table
    userRoleNames.value = (doc.roles || []).map((r) => r.role)
    // Populate edit fields
    editData.first_name = doc.first_name || ''
    editData.last_name = doc.last_name || ''
    editData.gender = doc.gender || ''
    editData.birth_date = doc.birth_date || ''
    editData.phone = doc.phone || ''
    editData.location = doc.location || ''
  } catch (err) {
    console.error('Error fetching user:', err)
  } finally {
    loading.value = false
  }
}

// Fetch all available roles
async function fetchRoles() {
  try {
    const roles = await call('frappe.client.get_list', {
      doctype: 'Role',
      fields: ['name'],
      filters: {
        disabled: 0,
        name: ['not in', ['All', 'Guest', 'Administrator', 'Desk User']],
      },
      order_by: 'name asc',
      limit_page_length: 200,
    })
    allRoles.value = roles
  } catch (err) {
    console.error('Error fetching roles:', err)
  }
}

const filteredRoles = computed(() => {
  if (!roleSearch.value) return allRoles.value
  const q = roleSearch.value.toLowerCase()
  return allRoles.value.filter((r) => r.name.toLowerCase().includes(q))
})

async function toggleRole(roleName, event) {
  const checked = event.target.checked
  saving.value = true
  try {
    // Get current roles from the user doc, modify, and save back
    let currentRoles = [...userRoleNames.value]
    if (checked && !currentRoles.includes(roleName)) {
      currentRoles.push(roleName)
    } else if (!checked) {
      currentRoles = currentRoles.filter((r) => r !== roleName)
    }
    // Use frappe.client.set_value won't work for child tables,
    // so we use run_doc_method or save the full doc
    const rolesTable = currentRoles.map((r) => ({ role: r }))
    
    // We pass the full existing user document along with the modified roles table 
    // to preserve all metadata including the latest 'modified' timestamp.
    const savedDoc = await call('frappe.client.save', {
      doc: {
        ...userData.value,
        roles: rolesTable,
      },
    })
    
    if (savedDoc) {
      userData.value = savedDoc
      userRoleNames.value = (savedDoc.roles || []).map((r) => r.role)
    } else {
      userRoleNames.value = currentRoles
      await fetchUser()
    }
  } catch (err) {
    console.error('Error toggling role:', err)
    event.target.checked = !checked
    // Refresh to get correct state
    await fetchUser()
  } finally {
    saving.value = false
  }
}


function markDirty() { isDirty.value = true }

function resetEdits() {
  const doc = userData.value
  if (doc) {
    editData.first_name = doc.first_name || ''
    editData.last_name = doc.last_name || ''
    editData.gender = doc.gender || ''
    editData.birth_date = doc.birth_date || ''
    editData.phone = doc.phone || ''
    editData.location = doc.location || ''
  }
  isDirty.value = false
}

async function saveUserInfo() {
  saving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'User',
      name: props.userId,
      fieldname: editData,
    })
    isDirty.value = false
    fetchUser()
  } catch (err) {
    console.error('Error saving user:', err)
  } finally {
    saving.value = false
  }
}

async function toggleUserEnabled() {
  saving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'User',
      name: props.userId,
      fieldname: 'enabled',
      value: userData.value?.enabled ? 0 : 1,
    })
    fetchUser()
  } catch (err) {
    console.error('Error toggling user:', err)
  } finally {
    saving.value = false
  }
}

function timeAgo(dateStr) {
  if (!dateStr) return '-'
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return __('Just now')
  if (mins < 60) return `${mins}m ${__('ago')}`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ${__('ago')}`
  const days = Math.floor(hours / 24)
  return `${days}d ${__('ago')}`
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

onMounted(() => {
  fetchUser()
  fetchRoles()
})

usePageMeta(() => ({
  title: userData.value?.full_name || props.userId,
}))
</script>
