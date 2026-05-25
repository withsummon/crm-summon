<template>
  <div class="flex h-full flex-col bg-white overflow-hidden">
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
            :label="__('Save Workflow')"
            variant="solid"
            @click="saveWorkflow"
          >
            <template #prefix>
              <LucideSave class="h-4 w-4" />
            </template>
          </Button>
          <Button
            :label="__('Publish')"
            variant="outline"
          >
            <template #prefix>
              <LucideRocket class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex min-h-0 flex-1 bg-white relative">
      <WorkflowNodePalette />
      
      <div class="flex-1 relative">
        <WorkflowCanvas />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideGitBranch from '~icons/lucide/git-branch'
import LucideSave from '~icons/lucide/save'
import LucideRocket from '~icons/lucide/rocket'
import { Button, usePageMeta } from 'frappe-ui'
import WorkflowNodePalette from '../components/WorkflowEngine/WorkflowNodePalette.vue'
import WorkflowCanvas from '../components/WorkflowEngine/WorkflowCanvas.vue'

function saveWorkflow() {
  console.log('Save workflow')
}

usePageMeta(() => ({ title: __('Workflow Engine') }))
</script>
