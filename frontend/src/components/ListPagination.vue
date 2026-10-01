<template>
  <div v-if="total > pageSize" class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
    <span>{{ __('Showing {0}-{1} of {2}', [(page - 1) * pageSize + 1, Math.min(page * pageSize, total), total]) }}</span>
    <div class="flex items-center gap-2">
      <Button variant="outline" :label="__('Previous')" :disabled="page <= 1" @click="emit('update:page', page - 1)" />
      <span class="min-w-16 text-center">{{ page }} / {{ pageCount }}</span>
      <Button variant="outline" :label="__('Next')" :disabled="page >= pageCount" @click="emit('update:page', page + 1)" />
    </div>
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui'
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  total: { type: Number, required: true },
})
const emit = defineEmits(['update:page'])
const pageCount = computed(() => Math.ceil(props.total / props.pageSize))
</script>
