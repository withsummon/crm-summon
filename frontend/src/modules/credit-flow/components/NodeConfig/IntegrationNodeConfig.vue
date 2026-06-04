<template>
  <div class="space-y-4">
    <div>
      <label class="config-label">{{ __('Integration Type') }}</label>
      <select :value="config.integrationType || 'internal'" class="config-select" @change="update('integrationType', $event.target.value)">
        <option value="internal">{{ __('Internal API') }}</option>
        <option value="external">{{ __('External API') }}</option>
        <option value="webhook">{{ __('Webhook') }}</option>
      </select>
    </div>
    <div>
      <label class="config-label">{{ __('Endpoint URL') }}</label>
      <input :value="config.endpoint || ''" type="text" class="config-input" :placeholder="__('/api/method/...')" @input="update('endpoint', $event.target.value)" />
    </div>
    <div>
      <label class="config-label">{{ __('HTTP Method') }}</label>
      <select :value="config.method || 'GET'" class="config-select" @change="update('method', $event.target.value)">
        <option value="GET">GET</option>
        <option value="POST">POST</option>
        <option value="PUT">PUT</option>
        <option value="DELETE">DELETE</option>
      </select>
    </div>
    <div>
      <label class="config-label">{{ __('Request Headers (JSON)') }}</label>
      <textarea :value="headersText" rows="3" class="config-textarea font-mono text-xs" :placeholder="__('{ \"Content-Type\": \"application/json\" }')" @input="updateHeaders($event.target.value)" />
    </div>
    <div>
      <label class="config-label">{{ __('Request Payload (JSON)') }}</label>
      <textarea :value="payloadText" rows="4" class="config-textarea font-mono text-xs" :placeholder="__('{ \"key\": \"value\" }')" @input="updatePayload($event.target.value)" />
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="config-label">{{ __('Retry Count') }}</label>
        <input :value="config.retryCount || 3" type="number" min="0" max="10" class="config-input" @input="update('retryCount', parseInt($event.target.value))" />
      </div>
      <div>
        <label class="config-label">{{ __('Timeout (seconds)') }}</label>
        <input :value="config.timeoutSeconds || 30" type="number" min="1" class="config-input" @input="update('timeoutSeconds', parseInt($event.target.value))" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:config'])
const headersText = computed(() => {
  try { return JSON.stringify(props.config.headers || {}, null, 2) } catch { return '{}' }
})
const payloadText = computed(() => {
  try { return JSON.stringify(props.config.payload || {}, null, 2) } catch { return '{}' }
})
function update(key, value) { emit('update:config', { ...props.config, [key]: value }) }
function updateHeaders(text) { try { update('headers', JSON.parse(text)) } catch {} }
function updatePayload(text) { try { update('payload', JSON.parse(text)) } catch {} }
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-textarea { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500 resize-none; }
</style>
