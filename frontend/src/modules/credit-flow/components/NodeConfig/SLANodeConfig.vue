<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="config-label">{{ __('Deadline (hours)') }}</label>
        <input :value="config.deadlineHours || 24" type="number" min="1" class="config-input" @input="update('deadlineHours', parseInt($event.target.value))" />
      </div>
      <div>
        <label class="config-label">{{ __('Warning (hours before)') }}</label>
        <input :value="config.warningHours || 4" type="number" min="0" class="config-input" @input="update('warningHours', parseInt($event.target.value))" />
      </div>
    </div>
    <div>
      <label class="config-label">{{ __('Reminder Interval (hours)') }}</label>
      <input :value="config.reminderIntervalHours || 2" type="number" min="0" class="config-input" @input="update('reminderIntervalHours', parseInt($event.target.value))" />
    </div>
    <div>
      <label class="config-label">{{ __('Escalation Target') }}</label>
      <input :value="config.escalationTarget || ''" type="text" class="config-input" :placeholder="__('Role or user to escalate to')" @input="update('escalationTarget', $event.target.value)" />
    </div>
    <div>
      <label class="config-label">{{ __('Escalation Action') }}</label>
      <select :value="config.escalationAction || 'notify'" class="config-select" @change="update('escalationAction', $event.target.value)">
        <option value="notify">{{ __('Send Notification') }}</option>
        <option value="reassign">{{ __('Reassign Task') }}</option>
        <option value="escalate">{{ __('Escalate to Supervisor') }}</option>
      </select>
    </div>
    <label class="flex items-center gap-2 cursor-pointer">
      <input type="checkbox" :checked="config.businessHoursOnly !== false" class="h-4 w-4 rounded border-gray-300 text-secondary-600" @change="update('businessHoursOnly', $event.target.checked)" />
      <span class="text-sm text-gray-700">{{ __('Business hours only') }}</span>
    </label>
    <div class="rounded-lg bg-rose-50 border border-rose-100 p-3">
      <div class="text-[11px] font-medium text-rose-600 mb-1">{{ __('SLA Summary') }}</div>
      <p class="text-xs text-rose-500">
        {{ __('Deadline:') }} {{ config.deadlineHours || 24 }}h •
        {{ __('Warning at:') }} {{ (config.deadlineHours || 24) - (config.warningHours || 4) }}h •
        {{ __('Remind every:') }} {{ config.reminderIntervalHours || 2 }}h
      </p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:config'])
function update(key, value) { emit('update:config', { ...props.config, [key]: value }) }
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
</style>
