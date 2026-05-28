<template>
  <div class="flex h-full flex-col gap-6 py-8 px-6 text-ink-gray-8">
    <div class="flex flex-col gap-1 px-2">
      <h2 class="flex gap-2 text-xl font-semibold leading-none h-5">
        {{ __('AI Settings') }}
      </h2>
      <p class="text-p-base text-ink-gray-6">
        {{ __('Configure your AI provider, model, and API key') }}
      </p>
    </div>

    <div class="flex-1 flex flex-col overflow-y-auto">
      <div class="flex flex-col gap-6 py-3 px-2">
        <!-- AI Provider -->
        <div class="flex flex-col gap-2">
          <div class="text-p-base font-medium text-ink-gray-7">
            {{ __('AI Provider') }}
          </div>
          <div class="text-p-sm text-ink-gray-5 mb-2">
            {{ __('Choose which AI service to use for the AI Agent Center.') }}
          </div>
          <select
            v-model="localProvider"
            class="w-full max-w-sm rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none"
          >
            <option value="Kimi">Moonshot Kimi</option>
            <option value="OpenAI">OpenAI (GPT)</option>
            <option value="Anthropic">Anthropic (Claude)</option>
            <option value="Gemini">Google Gemini</option>
            <option value="Custom">Custom / OpenAI-Compatible</option>
          </select>
        </div>

        <!-- Model Selection -->
        <div class="flex flex-col gap-2">
          <div class="text-p-base font-medium text-ink-gray-7">
            {{ __('Model') }}
          </div>
          <div class="text-p-sm text-ink-gray-5 mb-2">
            {{ __('Select the specific model to use, or enter a custom model name.') }}
          </div>
          <div class="flex gap-2 max-w-sm">
            <select
              v-if="providerModels.length > 0"
              v-model="localModel"
              class="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none"
            >
              <option v-for="m in providerModels" :key="m.value" :value="m.value">{{ m.label }}</option>
              <option value="__custom__">Custom model...</option>
            </select>
          </div>
          <input
            v-if="localModel === '__custom__' || providerModels.length === 0"
            v-model="localCustomModel"
            type="text"
            placeholder="e.g. gpt-4o, claude-3-5-sonnet, moonshot-v1-8k"
            class="w-full max-w-sm rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none"
          />
        </div>

        <!-- API Key -->
        <div class="flex flex-col gap-2">
          <div class="text-p-base font-medium text-ink-gray-7">
            {{ __('API Key') }}
          </div>
          <div class="text-p-sm text-ink-gray-5 mb-2">
            {{ __('Your API key for the selected provider. Stored securely in FCRM Settings.') }}
          </div>
          <input
            v-model="localApiKey"
            type="password"
            :placeholder="apiKeyPlaceholder"
            autocomplete="new-password"
            class="w-full max-w-sm rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none"
          />
        </div>

        <!-- API Base URL -->
        <div v-if="localProvider === 'Kimi' || localProvider === 'Custom'" class="flex flex-col gap-2">
          <div class="text-p-base font-medium text-ink-gray-7">
            {{ __('API Base URL') }}
          </div>
          <div class="text-p-sm text-ink-gray-5 mb-2">
            {{ localProvider === 'Kimi' ? __('Moonshot/Kimi OpenAI-compatible API endpoint.') : __('Base URL for your OpenAI-compatible endpoint (e.g. https://api.openrouter.ai/v1).') }}
          </div>
          <input
            v-model="localApiBase"
            type="text"
            :placeholder="localProvider === 'Kimi' ? 'https://api.moonshot.ai/v1' : 'https://api.openrouter.ai/v1'"
            class="w-full max-w-sm rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none"
          />
        </div>

        <!-- Model info card -->
        <div class="rounded-lg border border-teal-100 bg-teal-50 px-4 py-3 text-xs text-teal-800 max-w-sm">
          <div class="font-semibold mb-1">{{ __('Currently active') }}</div>
          <div>{{ __('Provider') }}: <span class="font-mono">{{ localProvider }}</span></div>
          <div>{{ __('Model') }}: <span class="font-mono">{{ effectiveModel }}</span></div>
          <div v-if="modelInfo" class="mt-1.5 border-t border-teal-200 pt-1.5">
            <div class="flex gap-2">{{ __('Context') }}: <span class="font-mono">{{ modelInfo.context }}</span></div>
          </div>
        </div>

        <!-- Validation errors -->
        <div v-if="validationError" class="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-xs text-red-700 max-w-sm">
          {{ validationError }}
        </div>

        <div class="pt-2">
          <Button @click="save" :loading="saving" :disabled="!!validationError">
            {{ __('Save Settings') }}
          </Button>
        </div>
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

const PROVIDER_MODELS = {
  Kimi: [
    { value: 'kimi-k2.6', label: 'Kimi K2.6 (Moonshot latest)' },
    { value: 'moonshot-v1-8k', label: 'Kimi moonshot-v1-8k' },
    { value: 'moonshot-v1-32k', label: 'Kimi moonshot-v1-32k' },
    { value: 'moonshot-v1-128k', label: 'Kimi moonshot-v1-128k' },
  ],
  OpenAI: [
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    { value: 'o1-mini', label: 'o1-mini' },
  ],
  Anthropic: [
    { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
    { value: 'claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku' },
    { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
  ],
  Gemini: [
    { value: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash' },
    { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
    { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash' },
  ],
  Custom: [],
}

const localProvider = ref(settings.doc?.ai_provider || 'Kimi')
const localModel = ref(settings.doc?.kimi_model || '')
const localCustomModel = ref('')
const localApiKey = ref('')
const localApiBase = ref(settings.doc?.kimi_base_url || 'https://api.moonshot.ai/v1')

function normalizeKimiModel(model) {
  const value = String(model || '').trim()
  if (value === 'kimi-k2' || value === 'kimi-k2-latest') return 'kimi-k2.6'
  return value
}

function applyModel(provider, model) {
  const models = PROVIDER_MODELS[provider] || []
  const normalized = provider === 'Kimi' ? normalizeKimiModel(model) : String(model || '').trim()
  if (!normalized) {
    localModel.value = models[0]?.value || ''
    localCustomModel.value = ''
    return
  }
  if (models.some((row) => row.value === normalized)) {
    localModel.value = normalized
    localCustomModel.value = ''
    return
  }
  localModel.value = '__custom__'
  localCustomModel.value = normalized
}

// watch for settings doc to be loaded
watch(() => settings.doc, (doc) => {
  if (doc) {
    localProvider.value = doc.ai_provider || 'Kimi'
    applyModel(localProvider.value, doc.kimi_model)
    localApiBase.value = doc.kimi_base_url || (localProvider.value === 'Kimi' ? 'https://api.moonshot.ai/v1' : '')
  }
}, { immediate: true })

const MODEL_INFO = {
  'kimi-k2.6': { context: '128K' },
  'moonshot-v1-8k': { context: '8K' },
  'moonshot-v1-32k': { context: '32K' },
  'moonshot-v1-128k': { context: '128K' },
  'gpt-4o': { context: '128K' },
  'gpt-4o-mini': { context: '128K' },
  'gpt-4-turbo': { context: '128K' },
  'o1-mini': { context: '128K' },
  'claude-3-5-sonnet-20241022': { context: '200K' },
  'claude-3-5-haiku-20241022': { context: '200K' },
  'claude-3-opus-20240229': { context: '200K' },
  'gemini-2.0-flash': { context: '1M' },
  'gemini-1.5-pro': { context: '2M' },
  'gemini-1.5-flash': { context: '1M' },
}

const validationError = ref('')

const providerModels = computed(() => PROVIDER_MODELS[localProvider.value] || [])

const effectiveModel = computed(() => {
  if (localModel.value === '__custom__') return localCustomModel.value || '(not set)'
  return localModel.value || providerModels.value[0]?.value || '(not set)'
})

const modelInfo = computed(() => MODEL_INFO[effectiveModel.value] || null)

function validateModel() {
  const model = localModel.value === '__custom__' ? localCustomModel.value : localModel.value
  if (!model || !model.trim()) {
    validationError.value = __('Model name cannot be empty.')
    return false
  }
  if (model !== model.trim()) {
    validationError.value = __('Model name contains leading or trailing whitespace.')
    return false
  }
  validationError.value = ''
  return true
}

watch(effectiveModel, () => validateModel())

const apiKeyPlaceholder = computed(() => {
  switch (localProvider.value) {
    case 'Kimi': return 'sk-... (Moonshot API Key)'
    case 'OpenAI': return 'sk-... (OpenAI API Key)'
    case 'Anthropic': return 'sk-ant-... (Anthropic API Key)'
    case 'Gemini': return 'AIzaSy... (Google AI API Key)'
    default: return 'Enter your API key'
  }
})

watch(localProvider, (newProvider) => {
  // Reset model to first available when provider changes
  const models = PROVIDER_MODELS[newProvider] || []
  localModel.value = models[0]?.value || ''
  localCustomModel.value = ''
  if (newProvider === 'Kimi' && !localApiBase.value) {
    localApiBase.value = 'https://api.moonshot.ai/v1'
  }
})

async function save() {
  if (!validateModel()) {
    toast.error(validationError.value)
    return
  }
  const effectiveModelVal = localModel.value === '__custom__' ? localCustomModel.value : localModel.value

  saving.value = true
  try {
    await call('crm.api.ai_agent_center.save_ai_settings', {
      provider: localProvider.value,
      model: effectiveModelVal,
      base_url: localApiBase.value,
      api_key: localApiKey.value || null
    })
    toast.success(__('AI Settings saved successfully'))
    localApiKey.value = '' // Clear for security
    await settings.reload() // Reload the settings store
  } catch (e) {
    toast.error(e?.message || __('Failed to save settings'))
  } finally {
    saving.value = false
  }
}
</script>
