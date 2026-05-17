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
      <div class="flex flex-col gap-2 py-3 px-2">
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
          <Button @click="save" :loading="settings.save.loading">
            {{ __('Save') }}
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
