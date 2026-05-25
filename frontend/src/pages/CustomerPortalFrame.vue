<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3 pr-12">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #7c3aed, #c084fc)"
          >
            <FeatherIcon name="life-buoy" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Customer Portal') }}
            </h1>
          </div>
        </div>
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
import CustomerPortal from '@/pages/CustomerPortal.vue'
import { Button, FeatherIcon, usePageMeta } from 'frappe-ui'

function openExternalPortal() {
  window.open('/crm/customer-portal', '_blank', 'noopener,noreferrer')
}

usePageMeta(() => ({ title: __('Customer Portal') }))
</script>
