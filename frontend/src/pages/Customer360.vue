<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-summon-blue">
            <FeatherIcon name="user" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Customer 360') }}
            </h1>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button :label="__('Refresh')" variant="subtle" @click="refreshFrame">
            <template #prefix>
              <FeatherIcon name="refresh-cw" class="h-4 w-4" />
            </template>
          </Button>
          <Button :label="__('Customer List')" variant="outline" @click="openCustomerList">
            <template #prefix>
              <FeatherIcon name="list" class="h-4 w-4" />
            </template>
          </Button>
          <Button :label="__('Add Customer')" variant="solid" @click="openAddCustomer">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex min-h-0 flex-1 flex-col bg-surface-gray-1 p-4">

      <div class="min-h-0 flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <iframe
          ref="frame"
          title="Customer 360"
          :src="frameSource"
          class="h-full w-full border-0"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Button, FeatherIcon, usePageMeta } from 'frappe-ui'
import { ref } from 'vue'

const frame = ref(null)
const frameSource = ref('/app/customer')

function refreshFrame() {
  if (frame.value) {
    frame.value.src = frameSource.value
  }
}

function openCustomerList() {
  frameSource.value = '/app/customer'
  refreshFrame()
}

function openAddCustomer() {
  frameSource.value = '/app/customer/new-customer'
  refreshFrame()
}

usePageMeta(() => ({ title: __('Customer 360') }))
</script>
