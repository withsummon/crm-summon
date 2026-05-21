<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #7c3aed, #c084fc)"
          >
            <LucideGitBranch class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Workflow Engine') }}
            </h1>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            :label="__('Refresh')"
            variant="subtle"
            @click="refreshFrame"
          >
            <template #prefix>
              <LucideRefreshCw class="h-4 w-4" />
            </template>
          </Button>
          <Button
            :label="__('Open Desk View')"
            variant="outline"
            @click="openDeskView"
          >
            <template #prefix>
              <LucideExternalLink class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex min-h-0 flex-1 flex-col bg-surface-gray-1 p-4">

      <div class="min-h-0 flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <iframe
          ref="workflowFrame"
          title="Workflow Engine"
          src="/app/workflow"
          class="h-full w-full border-0"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideExternalLink from '~icons/lucide/external-link'
import LucideGitBranch from '~icons/lucide/git-branch'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import { Button, usePageMeta } from 'frappe-ui'
import { ref } from 'vue'

const workflowFrame = ref(null)

function refreshFrame() {
  if (workflowFrame.value) {
    workflowFrame.value.src = '/app/workflow'
  }
}

function openDeskView() {
  window.location.href = '/app/workflow'
}

usePageMeta(() => ({ title: __('Workflow Engine') }))
</script>
