<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #7c3aed, #c084fc)"
          >
            <FeatherIcon :name="icon" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __(title) }}
            </h1>
            <p class="truncate text-xs text-crm-muted">
              {{ __(subtitle) }}
            </p>
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
          <Button
            :label="__('Open Original View')"
            variant="outline"
            @click="openSource"
          >
            <template #prefix>
              <FeatherIcon name="external-link" class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex min-h-0 flex-1 flex-col bg-surface-gray-1 p-4">
      <div
        v-if="note"
        class="mb-3 rounded-[12px] border border-crm-border bg-white px-4 py-3 text-sm text-crm-muted shadow-sm"
      >
        {{ __(note) }}
      </div>

      <div
        class="min-h-0 flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm"
      >
        <iframe
          ref="frame"
          :title="title"
          :src="sourcePath"
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

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: 'grid' },
  sourcePath: { type: String, required: true },
  note: { type: String, default: '' },
})

const frame = ref(null)

function refreshFrame() {
  if (frame.value) {
    frame.value.src = props.sourcePath
  }
}

function openSource() {
  window.location.href = props.sourcePath
}

usePageMeta(() => ({ title: __(props.title) }))
</script>
