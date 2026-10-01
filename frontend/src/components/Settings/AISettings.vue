<template>
  <div class="flex h-full flex-col gap-6 px-6 py-8 text-ink-gray-8">
    <div class="flex flex-col gap-1 px-2">
      <h2 class="text-xl font-semibold">{{ __('AI Settings') }}</h2>
      <p class="text-p-base text-ink-gray-6">{{ __('Configure AI assistance for analysis and documents.') }}</p>
    </div>

    <div class="flex flex-col gap-6 px-2 py-3">
      <div class="flex flex-col gap-2">
        <label for="openrouter-key" class="text-p-base font-medium text-ink-gray-7">{{ __('AI service key') }}</label>
        <p class="text-p-sm text-ink-gray-5">{{ __('Leave blank to keep the existing key. A server key takes priority when configured.') }}</p>
        <input
          id="openrouter-key"
          v-model="localApiKey"
          type="password"
          placeholder="Enter service key"
          autocomplete="new-password"
          class="w-full max-w-sm rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none"
        />
      </div>

      <div>
        <Button @click="save" :loading="saving">{{ __('Save Settings') }}</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getSettings } from '@/stores/settings'
import { Button, toast, call } from 'frappe-ui'
import { ref, watch } from 'vue'

const { _settings: settings } = getSettings()
const saving = ref(false)
const localModel = ref('openai/gpt-6-luna')
const localApiKey = ref('')

watch(() => settings.doc, (doc) => {
  if (doc) localModel.value = doc.llm_model || 'openai/gpt-6-luna'
}, { immediate: true })

async function save() {
  saving.value = true
  try {
    await call('crm.api.ai_agent_center.save_ai_settings', {
      model: localModel.value,
      api_key: localApiKey.value || null,
    })
    localApiKey.value = ''
    await settings.reload()
    toast.success(__('AI Settings saved successfully'))
  } catch (error) {
    toast.error(error?.message || __('Failed to save settings'))
  } finally {
    saving.value = false
  }
}
</script>
