<template>
  <div class="flex h-full flex-col gap-6 px-6 py-8 text-ink-gray-8">
    <div class="flex flex-col gap-1 px-2">
      <h2 class="text-xl font-semibold">{{ __('AI Settings') }}</h2>
      <p class="text-p-base text-ink-gray-6">{{ __('Configure OpenRouter for the AI Agent Center, RAG, and document analysis.') }}</p>
    </div>

    <div class="flex flex-col gap-6 px-2 py-3">
      <div class="flex flex-col gap-2">
        <label for="llm-model" class="text-p-base font-medium text-ink-gray-7">{{ __('OpenRouter Model') }}</label>
        <input
          id="llm-model"
          v-model="localModel"
          type="text"
          placeholder="openai/gpt-6-luna"
          class="w-full max-w-sm rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none"
        />
      </div>

      <div class="flex flex-col gap-2">
        <label for="openrouter-key" class="text-p-base font-medium text-ink-gray-7">{{ __('OpenRouter API Key') }}</label>
        <p class="text-p-sm text-ink-gray-5">{{ __('Leave blank to keep the existing key. OPENROUTER_API_KEY takes priority when set on the server.') }}</p>
        <input
          id="openrouter-key"
          v-model="localApiKey"
          type="password"
          placeholder="sk-or-..."
          autocomplete="new-password"
          class="w-full max-w-sm rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none"
        />
      </div>

      <p v-if="validationError" class="max-w-sm rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-xs text-red-700" role="alert">
        {{ validationError }}
      </p>
      <div>
        <Button @click="save" :loading="saving" :disabled="!!validationError">{{ __('Save Settings') }}</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getSettings } from '@/stores/settings'
import { Button, toast, call } from 'frappe-ui'
import { computed, ref, watch } from 'vue'

const { _settings: settings } = getSettings()
const saving = ref(false)
const localModel = ref('openai/gpt-6-luna')
const localApiKey = ref('')
const validationError = computed(() => {
  if (!localModel.value.trim()) return __('Model name cannot be empty.')
  if (localModel.value !== localModel.value.trim()) return __('Model name contains leading or trailing whitespace.')
  return ''
})

watch(() => settings.doc, (doc) => {
  if (doc) localModel.value = doc.llm_model || 'openai/gpt-6-luna'
}, { immediate: true })

async function save() {
  if (validationError.value) {
    toast.error(validationError.value)
    return
  }
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
