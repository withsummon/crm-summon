<template>
  <div class="space-y-4">
    <div>
      <label class="config-label">{{ __('Document Action') }}</label>
      <select :value="config.documentAction || 'upload'" class="config-select" @change="update('documentAction', $event.target.value)">
        <option value="upload">{{ __('Upload Documents') }}</option>
        <option value="generate">{{ __('Generate Document') }}</option>
        <option value="review">{{ __('Review Documents') }}</option>
        <option value="validate">{{ __('Validate Documents') }}</option>
      </select>
    </div>

    <!-- Required Documents -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label class="config-label mb-0">{{ __('Required Documents') }}</label>
        <button class="text-xs brand-link font-medium" @click="addDocument">+ {{ __('Add') }}</button>
      </div>
      <div class="space-y-1.5">
        <div v-for="(doc, idx) in requiredDocs" :key="idx" class="flex items-center gap-2">
          <input :value="doc.name" type="text" class="config-input-sm flex-1" :placeholder="__('Document name')" @input="updateDoc(idx, 'name', $event.target.value)" />
          <label class="flex items-center gap-1 flex-shrink-0">
            <input type="checkbox" :checked="doc.mandatory !== false" class="h-3.5 w-3.5 rounded border-gray-300 text-secondary-600" @change="updateDoc(idx, 'mandatory', $event.target.checked)" />
            <span class="text-[11px] text-gray-500">{{ __('Req') }}</span>
          </label>
          <button class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500" @click="removeDoc(idx)">×</button>
        </div>
      </div>
    </div>

    <!-- Templates (for generate action) -->
    <div v-if="config.documentAction === 'generate'">
      <div class="flex items-center justify-between mb-2">
        <label class="config-label mb-0">{{ __('Templates') }}</label>
        <button class="text-xs brand-link font-medium" @click="addTemplate">+ {{ __('Add') }}</button>
      </div>
      <div class="space-y-1.5">
        <div v-for="(tpl, idx) in templates" :key="idx" class="flex items-center gap-2">
          <input :value="tpl" type="text" class="config-input-sm flex-1" :placeholder="__('Template name')" @input="updateTemplate(idx, $event.target.value)" />
          <button class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500" @click="removeTemplate(idx)">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:config'])
const requiredDocs = computed(() => props.config.requiredDocuments || [])
const templates = computed(() => props.config.templates || [])
function update(key, value) { emit('update:config', { ...props.config, [key]: value }) }
function addDocument() { emit('update:config', { ...props.config, requiredDocuments: [...requiredDocs.value, { name: '', mandatory: true }] }) }
function updateDoc(idx, key, value) { const arr = [...requiredDocs.value]; arr[idx] = { ...arr[idx], [key]: value }; emit('update:config', { ...props.config, requiredDocuments: arr }) }
function removeDoc(idx) { emit('update:config', { ...props.config, requiredDocuments: requiredDocs.value.filter((_, i) => i !== idx) }) }
function addTemplate() { emit('update:config', { ...props.config, templates: [...templates.value, ''] }) }
function updateTemplate(idx, value) { const arr = [...templates.value]; arr[idx] = value; emit('update:config', { ...props.config, templates: arr }) }
function removeTemplate(idx) { emit('update:config', { ...props.config, templates: templates.value.filter((_, i) => i !== idx) }) }
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
</style>
