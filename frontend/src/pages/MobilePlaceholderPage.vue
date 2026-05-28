<template>
  <div class="flex flex-1 flex-col items-center justify-center px-6 py-20 text-center">
    <div
      class="flex size-16 items-center justify-center rounded-2xl bg-crm-surface mb-5"
    >
      <FeatherIcon :name="icon" class="size-8 text-crm-teal" />
    </div>
    <h1 class="text-xl font-semibold text-ink-gray-9 mb-2">
      {{ __(title) }}
    </h1>
    <p class="text-sm text-ink-gray-6 max-w-xs mb-6">
      {{ __(description) }}
    </p>
    <div class="rounded-xl bg-surface-amber-1 border border-outline-amber-2 px-4 py-3">
      <div class="flex items-center gap-2">
        <FeatherIcon name="clock" class="size-4 text-amber-600 shrink-0" />
        <p class="text-xs font-medium text-amber-700">
          {{ __('Fitur ini akan segera tersedia') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = route.meta?.featureTitle || 'Mobile Feature'
const icon = route.meta?.featureIcon || 'smartphone'
const description = route.meta?.featureDescription || ''
</script>
