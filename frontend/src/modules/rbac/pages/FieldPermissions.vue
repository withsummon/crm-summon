<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-gray-100 transition-colors hover:bg-gray-200" @click="$router.push({ name: 'RBAC Admin' })">
            <LucideArrowLeft class="h-4 w-4 text-crm-text" />
          </button>
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px]" style="background: linear-gradient(135deg, #06b6d4, #22d3ee)">
            <LucideUserCog class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">{{ __('Field Permissions') }}</h1>
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

      <div v-else-if="fieldPerms.length" class="rounded-[18px] bg-white shadow-sm border border-crm-border overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-crm-surface-light">
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('DocType') }}</th>
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('Field') }}</th>
              <th class="px-4 py-3 text-left font-medium text-crm-muted">{{ __('Role') }}</th>
              <th class="px-4 py-3 text-center font-medium text-crm-muted">{{ __('Access') }}</th>
              <th class="px-4 py-3 text-center font-medium text-crm-muted">{{ __('Mask') }}</th>
              <th class="px-4 py-3 text-center font-medium text-crm-muted">{{ __('Status') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="fp in fieldPerms" :key="fp.name" class="border-t border-crm-border/50 hover:bg-crm-surface-light transition-colors">
              <td class="px-4 py-3 font-medium text-crm-text">{{ fp.target_doctype }}</td>
              <td class="px-4 py-3">
                <code class="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-mono">{{ fp.fieldname }}</code>
              </td>
              <td class="px-4 py-3">
                <Badge :label="fp.role" variant="subtle" theme="blue" />
              </td>
              <td class="px-4 py-3 text-center">
                <Badge :label="fp.permission_type" variant="subtle" :theme="permTheme(fp.permission_type)" />
              </td>
              <td class="px-4 py-3 text-center text-crm-muted">{{ fp.mask_type || '-' }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="fp.enabled ? 'text-crm-green' : 'text-gray-300'">{{ fp.enabled ? '✓' : '—' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20">
        <LucideUserCog class="h-12 w-12 text-crm-muted/40 mb-4" />
        <h3 class="text-base font-semibold text-crm-text">{{ __('No field permissions configured') }}</h3>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideUserCog from '~icons/lucide/user-cog'
import LucidePlus from '~icons/lucide/plus'
import { Badge, Button, call } from 'frappe-ui'
import { ref, onMounted } from 'vue'

const loading = ref(true)
const fieldPerms = ref([])

function permTheme(type) {
  return { Hidden: 'red', 'Read Only': 'orange', 'Read/Write': 'green', Masked: 'purple' }[type] || 'gray'
}

async function fetchFieldPerms() {
  loading.value = true
  try { fieldPerms.value = await call('crm.api.rbac.get_field_permissions_list') }
  catch (err) { console.error(err) }
  finally { loading.value = false }
}

onMounted(fetchFieldPerms)
</script>
