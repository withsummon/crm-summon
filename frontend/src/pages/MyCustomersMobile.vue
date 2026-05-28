<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <h1 class="text-lg font-semibold text-crm-text mb-2">
        {{ __('My Customers') }}
      </h1>
      <div class="relative">
        <FeatherIcon
          name="search"
          class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-crm-muted"
        />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="__('Cari nasabah...')"
          class="w-full rounded-xl border border-crm-border bg-crm-surface py-2.5 pl-9 pr-3 text-sm text-crm-text outline-none transition-colors placeholder:text-crm-muted focus:border-crm-teal"
        />
        <button
          v-if="searchQuery"
          class="absolute right-3 top-1/2 -translate-y-1/2"
          @click="searchQuery = ''"
        >
          <FeatherIcon name="x" class="size-4 text-crm-muted" />
        </button>
      </div>
    </div>

    <div v-if="error" class="rounded-xl bg-red-50 border border-red-200 p-4 mx-4 mb-4">
      <div class="flex items-center gap-2">
        <FeatherIcon name="alert-triangle" class="size-4 text-red-500 shrink-0" />
        <p class="text-xs text-red-600 flex-1">{{ error }}</p>
        <button class="text-xs font-medium text-red-700" @click="loadCustomers">{{ __('Coba Lagi') }}</button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 pt-2">
      <div v-if="organizations.loading" class="space-y-3">
        <div
          v-for="i in 5"
          :key="i"
          class="animate-pulse rounded-xl bg-white p-4 shadow-sm border border-crm-border"
        >
          <div class="flex items-center gap-3">
            <div class="size-10 rounded-full bg-crm-surface" />
            <div class="flex-1 space-y-2">
              <div class="h-4 w-3/4 rounded bg-crm-surface" />
              <div class="h-3 w-1/2 rounded bg-crm-surface" />
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="filteredCustomers.length" class="space-y-2.5">
        <div
          v-for="customer in filteredCustomers"
          :key="customer.name"
          class="rounded-xl bg-white p-4 shadow-sm border border-crm-border active:scale-[0.98] transition-transform cursor-pointer"
          @click="viewCustomer(customer)"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex size-11 shrink-0 items-center justify-center rounded-full text-sm font-semibold"
              :class="getOrgColor(customer)"
            >
              {{ getInitials(customer.organization_name || customer.name) }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-crm-text truncate">
                {{ customer.organization_name || customer.name }}
              </p>
              <div class="flex items-center gap-2 mt-1">
                <span
                  v-if="customer.city"
                  class="flex items-center gap-1 text-xs text-crm-text-secondary"
                >
                  <FeatherIcon name="map-pin" class="size-3" />
                  {{ customer.city }}
                </span>
                <span
                  v-if="customer.industry"
                  class="text-xs text-crm-text-secondary"
                >
                  {{ customer.industry }}
                </span>
              </div>
            </div>
            <FeatherIcon
              name="chevron-right"
              class="size-4 shrink-0 text-crm-muted"
            />
          </div>
        </div>
      </div>

      <div
        v-else
        class="flex flex-col items-center justify-center py-16 text-center"
      >
        <FeatherIcon
          name="users"
          class="size-12 text-crm-muted mb-3"
        />
        <p class="text-sm font-medium text-crm-text">
          {{ searchQuery ? __('Nasabah tidak ditemukan') : __('Belum ada nasabah') }}
        </p>
        <p class="text-xs text-crm-text-secondary mt-1">
          {{ searchQuery ? __('Coba kata kunci lain') : __('Nasabah akan muncul di sini') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { organizationsStore } from '@/stores/organizations'

const router = useRouter()
const { organizations } = organizationsStore()

const searchQuery = ref('')
const error = ref('')

const orgColors = [
  'bg-crm-surface text-crm-teal',
  'bg-blue-50 text-blue-600',
  'bg-green-50 text-green-600',
  'bg-amber-50 text-amber-600',
  'bg-purple-50 text-purple-600',
  'bg-rose-50 text-rose-600',
  'bg-cyan-50 text-cyan-600',
  'bg-orange-50 text-orange-600',
]

function getOrgColor(org) {
  if (!org?.name) return orgColors[0]
  const index = org.name.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  return orgColors[index % orgColors.length]
}

function getInitials(name) {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

const filteredCustomers = computed(() => {
  const data = organizations.data || []
  if (!searchQuery.value) return data

  const q = searchQuery.value.toLowerCase()
  return data.filter(
    (c) =>
      (c.organization_name || '').toLowerCase().includes(q) ||
      (c.name || '').toLowerCase().includes(q) ||
      (c.city || '').toLowerCase().includes(q) ||
      (c.industry || '').toLowerCase().includes(q) ||
      (c.email || '').toLowerCase().includes(q),
  )
})

function viewCustomer(customer) {
  router.push({
    name: 'Customer 360 Mobile',
    params: { customer: customer.name },
  })
}

async function loadCustomers() {
  error.value = ''
  try {
    await organizations.reload()
  } catch (err) {
    if (!(err && err.exc_type === 'AuthenticationError')) {
      error.value = __('Gagal memuat data nasabah')
    }
  }
}

if (organizations.promise) {
  organizations.promise.catch((err) => {
    if (!(err && err.exc_type === 'AuthenticationError')) {
      error.value = __('Gagal memuat data nasabah')
    }
  })
}
</script>
