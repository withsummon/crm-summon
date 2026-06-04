<template>
  <div class="space-y-4">
    <div>
      <label class="config-label">{{ __('Channels') }}</label>
      <div class="space-y-1.5 mt-1">
        <label v-for="ch in allChannels" :key="ch.id" class="flex items-center gap-2 cursor-pointer rounded-lg px-3 py-2 hover:bg-gray-50">
          <input type="checkbox" :checked="selectedChannels.includes(ch.id)" class="h-4 w-4 rounded border-gray-300 text-secondary-600" @change="toggleChannel(ch.id)" />
          <span class="text-sm text-gray-700">{{ __(ch.label) }}</span>
        </label>
      </div>
    </div>
    <div>
      <label class="config-label">{{ __('Recipient Type') }}</label>
      <select :value="config.recipientType || 'role'" class="config-select" @change="update('recipientType', $event.target.value)">
        <option value="user">{{ __('Specific User') }}</option>
        <option value="role">{{ __('By Role') }}</option>
        <option value="team">{{ __('Team') }}</option>
        <option value="applicant">{{ __('Applicant') }}</option>
        <option value="assignee">{{ __('Current Assignee') }}</option>
      </select>
    </div>
    <div>
      <label class="config-label">{{ __('Template') }}</label>
      <input :value="config.template || ''" type="text" class="config-input" :placeholder="__('Notification template name')" @input="update('template', $event.target.value)" />
    </div>
    <div>
      <label class="config-label">{{ __('Subject') }}</label>
      <input :value="config.subject || ''" type="text" class="config-input" :placeholder="__('Notification subject')" @input="update('subject', $event.target.value)" />
    </div>
    <div>
      <label class="config-label">{{ __('Message') }}</label>
      <textarea :value="config.message || ''" rows="3" class="config-textarea" :placeholder="__('Notification message body...')" @input="update('message', $event.target.value)" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:config'])
const allChannels = [
  { id: 'in_app', label: 'In-App' },
  { id: 'email', label: 'Email' },
  { id: 'sms', label: 'SMS' },
  { id: 'whatsapp', label: 'WhatsApp' },
  { id: 'push', label: 'Push Notification' },
]
const selectedChannels = computed(() => props.config.channels || ['in_app'])
function update(key, value) { emit('update:config', { ...props.config, [key]: value }) }
function toggleChannel(id) {
  const current = [...selectedChannels.value]
  const idx = current.indexOf(id)
  if (idx >= 0) current.splice(idx, 1)
  else current.push(id)
  update('channels', current)
}
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-textarea { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500 resize-none; }
</style>
