<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Customer Portal" />
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            :label="__('Open Customer Portal')"
            variant="outline"
            @click="openExternalPortal"
          >
            <template #prefix>
              <FeatherIcon name="external-link" class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex min-h-0 flex-1 flex-col bg-surface-gray-1 p-4">
      <div class="min-h-0 flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <CustomerPortal embedded />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomerPortal from '@/pages/CustomerPortal.vue'
import { Button, FeatherIcon, usePageMeta } from 'frappe-ui'
import { ref } from 'vue'

const viewControls = ref(null)

function openExternalPortal() {
  window.open('/crm/customer-portal', '_blank', 'noopener,noreferrer')
}

usePageMeta(() => ({ title: __('Customer Portal') }))
</script>
