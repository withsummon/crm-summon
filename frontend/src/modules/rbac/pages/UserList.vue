<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #7c3aed, #c084fc)"
          >
            <LucideUsers class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">
            {{ __('Users') }}
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
              :placeholder="__('Search users...')"
              class="h-9 w-64 rounded-[10px] border border-crm-border bg-white pl-9 pr-4 text-sm outline-none transition-all focus:border-crm-orange focus:ring-2 focus:ring-crm-orange/20"
            />
          </div>
          <Button
            :label="__('Add User')"
            variant="solid"
            @click="showNewUserDialog = true"
          >
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <!-- Filter Tabs -->
      <div class="mb-6 flex items-center gap-3">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          class="rounded-full px-4 py-2 text-sm font-medium transition-all"
          :class="
            activeTab === tab.value
              ? 'bg-crm-orange text-white shadow-sm'
              : 'bg-white text-crm-muted hover:bg-crm-peach hover:text-crm-text'
          "
          @click="activeTab = tab.value"
        >
          {{ __(tab.label) }}
          <span
            v-if="tab.count !== undefined"
            class="ml-1.5 rounded-full px-1.5 text-xs"
            :class="
              activeTab === tab.value
                ? 'bg-white/30'
                : 'bg-gray-100'
            "
          >
            {{ tab.count }}
          </span>
        </button>
      </div>

      <!-- User List -->
      <div
        v-if="loading"
        class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
      >
        <div
          v-for="i in 6"
          :key="i"
          class="h-20 animate-pulse rounded-[14px] bg-white shadow-sm"
        />
      </div>

      <div
        v-else-if="filteredUsers.length"
        class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
      >
        <router-link
          v-for="user in filteredUsers"
          :key="user.name"
          :to="{ name: 'User Detail', params: { userId: user.name } }"
          class="flex items-center gap-4 rounded-[14px] bg-white p-4 shadow-sm transition-all duration-200 hover:shadow-md hover:border-crm-soft-orange border border-transparent"
        >
          <Avatar
            :label="user.full_name || user.name"
            :image="user.user_image"
            size="lg"
            class="flex-shrink-0"
          />
          <div class="min-w-0 flex-1">
            <div class="truncate text-sm font-semibold text-crm-text">
              {{ user.full_name || user.name }}
            </div>
            <div class="truncate text-xs text-crm-muted">
              {{ user.name }}
            </div>
            <div class="mt-1.5 flex flex-wrap gap-1">
              <Badge
                v-if="user.user_type === 'System User'"
                label="System"
                variant="subtle"
                theme="blue"
              />
              <Badge
                v-else
                label="Website"
                variant="subtle"
                theme="gray"
              />
              <Badge
                v-if="!user.enabled"
                label="Disabled"
                variant="subtle"
                theme="red"
              />
            </div>
          </div>
          <FeatherIcon name="chevron-right" class="h-4 w-4 text-crm-muted flex-shrink-0" />
        </router-link>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideUserX class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">
          {{ __('No users found') }}
        </h3>
        <p class="mt-1 text-sm text-crm-muted">
          {{ __('Try adjusting your search or filter criteria') }}
        </p>
      </div>
    </div>

    <!-- New User Dialog -->
    <Dialog v-model="showNewUserDialog" :options="{ title: __('Add New User'), size: 'md' }">
      <template #body-content>
        <div class="flex flex-col gap-4">
          <FormControl
            :label="__('Email')"
            type="email"
            v-model="newUser.email"
            :placeholder="__('user@example.com')"
          />
          <FormControl
            :label="__('First Name')"
            v-model="newUser.first_name"
            :placeholder="__('First Name')"
          />
          <FormControl
            :label="__('Last Name')"
            v-model="newUser.last_name"
            :placeholder="__('Last Name')"
          />
        </div>
      </template>
      <template #actions>
        <Button
          variant="solid"
          :label="__('Create User')"
          :loading="creatingUser"
          @click="createUser"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideUsers from '~icons/lucide/users'
import LucideSearch from '~icons/lucide/search'
import LucidePlus from '~icons/lucide/plus'
import LucideUserX from '~icons/lucide/user-x'
import { Avatar, Badge, Dialog, FormControl, FeatherIcon, call } from 'frappe-ui'
import { usePageMeta } from 'frappe-ui'
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')
const activeTab = ref('all')
const showNewUserDialog = ref(false)
const creatingUser = ref(false)
const loading = ref(true)
const allUsers = ref([])
const newUser = reactive({ email: '', first_name: '', last_name: '' })

async function fetchUsers() {
  loading.value = true
  try {
    // Use the CRM session API which already handles permissions
    const [users, crmUsers] = await call('crm.api.session.get_users')
    allUsers.value = users || crmUsers || []
  } catch (err) {
    console.error('Error fetching users:', err)
    // Fallback: try standard API with safe fields
    try {
      const users = await call('frappe.client.get_list', {
        doctype: 'User',
        fields: ['name', 'full_name', 'user_image', 'user_type', 'enabled'],
        filters: { name: ['not in', ['Guest']] },
        order_by: 'full_name asc',
        limit_page_length: 100,
      })
      allUsers.value = users
    } catch (e2) {
      console.error('Fallback also failed:', e2)
    }
  } finally {
    loading.value = false
  }
}

const filterTabs = computed(() => {
  const data = allUsers.value || []
  return [
    { label: 'All', value: 'all', count: data.length },
    { label: 'System Users', value: 'system', count: data.filter((u) => u.user_type === 'System User').length },
    { label: 'Website Users', value: 'website', count: data.filter((u) => u.user_type === 'Website User').length },
    { label: 'Disabled', value: 'disabled', count: data.filter((u) => !u.enabled).length },
  ]
})

const filteredUsers = computed(() => {
  let result = allUsers.value || []

  if (activeTab.value === 'system') {
    result = result.filter((u) => u.user_type === 'System User')
  } else if (activeTab.value === 'website') {
    result = result.filter((u) => u.user_type === 'Website User')
  } else if (activeTab.value === 'disabled') {
    result = result.filter((u) => !u.enabled)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      (u) =>
        u.name.toLowerCase().includes(q) ||
        (u.full_name && u.full_name.toLowerCase().includes(q)),
    )
  }

  return result
})

async function createUser() {
  if (!newUser.email) return
  creatingUser.value = true
  try {
    const doc = await call('frappe.client.insert', {
      doc: {
        doctype: 'User',
        email: newUser.email,
        first_name: newUser.first_name,
        last_name: newUser.last_name,
        send_welcome_email: 1,
      },
    })
    showNewUserDialog.value = false
    newUser.email = ''
    newUser.first_name = ''
    newUser.last_name = ''
    fetchUsers()
    router.push({ name: 'User Detail', params: { userId: doc.name } })
  } catch (err) {
    console.error('Error creating user:', err)
  } finally {
    creatingUser.value = false
  }
}

onMounted(fetchUsers)

usePageMeta(() => ({ title: __('Users') }))
</script>
