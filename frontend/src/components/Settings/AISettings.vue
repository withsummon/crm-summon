<template>
  <div class="flex h-full flex-col gap-6 py-8 px-6 text-ink-gray-8">
    <div class="flex flex-col gap-1 px-2">
      <h2 class="flex gap-2 text-xl font-semibold leading-none h-5">
        {{ __('AI Settings') }}
      </h2>
      <p class="text-p-base text-ink-gray-6">
        {{ __('Configure your AI API keys and models') }}
      </p>
    </div>

    <div class="flex-1 flex flex-col overflow-y-auto">
      <div class="flex flex-col gap-6 py-3 px-2">
        <div class="flex flex-col gap-2">
          <div class="text-p-base font-medium text-ink-gray-7">
            {{ __('AI Provider') }}
          </div>
          <div class="text-p-sm text-ink-gray-5 mb-2">
            {{ __('Choose which AI service to use for the AI Desk.') }}
          </div>
          <select
            v-model="settings.doc.ai_provider"
            class="w-full max-w-sm rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-summon-charcoal focus:outline-none focus:ring-1 focus:ring-summon-charcoal"
          >
            <option value="Gemini">Google Gemini</option>
            <option value="Kimi">Moonshot Kimi</option>
          </select>
        </div>

        <div v-if="settings.doc.ai_provider === 'Gemini' || !settings.doc.ai_provider" class="flex flex-col gap-2">
          <div class="text-p-base font-medium text-ink-gray-7">
            {{ __('Gemini API Key') }}
          </div>
          <div class="text-p-sm text-ink-gray-5 mb-2">
            {{ __('Enter your Google Gemini API Key to enable AI features.') }}
          </div>
          <div class="flex items-center gap-2">
            <Input
              v-model="settings.doc.gemini_api_key"
              type="password"
              placeholder="AIzaSy..."
              class="w-full max-w-sm"
            />
          </div>
        </div>

        <div v-if="settings.doc.ai_provider === 'Kimi'" class="flex flex-col gap-2">
          <div class="text-p-base font-medium text-ink-gray-7">
            {{ __('Kimi API Key') }}
          </div>
          <div class="text-p-sm text-ink-gray-5 mb-2">
            {{ __('Enter your Moonshot Kimi API Key to enable Kimi AI.') }}
          </div>
          <div class="flex items-center gap-2">
            <Input
              v-model="settings.doc.kimi_api_key"
              type="password"
              placeholder="sk-..."
              class="w-full max-w-sm"
            />
          </div>
        </div>

        <div class="pt-2">
          <Button @click="save" :loading="settings.save.loading">
            {{ __('Save Settings') }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getSettings } from '@/stores/settings'
import { Input, Button, toast } from 'frappe-ui'

const { _settings: settings } = getSettings()

function save() {
  settings.save.submit(null, {
    onSuccess: () => {
      toast.success(__('AI Settings saved successfully'))
    },
    onError: (e) => {
      toast.error(e.message || __('Failed to save settings'))
    }
  })
}
</script>
