<template>
  <Dialog v-model="show" :options="{ size: 'sm' }">
    <template #body>
      <div class="p-5">
        <div class="flex flex-col items-center text-center">
          <div class="flex size-14 items-center justify-center rounded-2xl bg-crm-surface mb-4">
            <FeatherIcon name="smartphone" class="size-7 text-crm-teal" />
          </div>
          <h3 class="text-lg font-semibold text-ink-gray-9 mb-1">{{ __('Install BNI CRM') }}</h3>
          <p class="text-sm text-ink-gray-6 mb-5 max-w-xs">
            {{ __('Install this app on your device for quick access, offline support, and a native experience.') }}
          </p>
        </div>

        <div v-if="isInstalled" class="rounded-xl bg-surface-green-2 border border-outline-green-2 p-3 mb-4">
          <div class="flex items-center gap-2">
            <FeatherIcon name="check" class="size-5 text-green-600 shrink-0" />
            <p class="text-sm font-medium text-green-700">{{ __('App is installed') }}</p>
          </div>
        </div>

        <div v-else-if="installable" class="space-y-2 mb-4">
          <Button
            variant="solid"
            class="w-full"
            @click="install"
          >
            <template #prefix>
              <FeatherIcon name="download" class="size-4" />
            </template>
            {{ __('Install App') }}
          </Button>
          <p class="text-xs text-ink-gray-5 text-center">{{ __('Opens browser install dialog') }}</p>
        </div>

        <div v-if="!installable && !isInstalled" class="rounded-xl bg-surface-gray-1 border p-3 mb-4 space-y-3">
          <p class="text-sm font-medium text-ink-gray-8">{{ __('Manual Install') }}</p>
          <div class="space-y-2 text-xs text-ink-gray-6">
            <div class="flex items-start gap-2">
              <span class="flex size-5 shrink-0 items-center justify-center rounded-full bg-crm-surface text-xs font-bold text-crm-teal mt-0.5">1</span>
              <span>{{ __('Open this page in Chrome, Edge, or Samsung Internet browser') }}</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="flex size-5 shrink-0 items-center justify-center rounded-full bg-crm-surface text-xs font-bold text-crm-teal mt-0.5">2</span>
              <span>{{ __('Tap the browser menu (⋮) and select "Add to Home Screen" or "Install App"') }}</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="flex size-5 shrink-0 items-center justify-center rounded-full bg-crm-surface text-xs font-bold text-crm-teal mt-0.5">3</span>
              <span>{{ __('Follow the on-screen steps to complete installation') }}</span>
            </div>
          </div>
        </div>

        <Button
          variant="ghost"
          class="w-full"
          @click="show = false"
        >
          {{ __('Close') }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Dialog, Button, FeatherIcon } from 'frappe-ui'

let show = defineModel({ type: Boolean })

const deferredPrompt = ref(null)
const installable = ref(false)
const isInstalled = ref(false)

onMounted(() => {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt.value = e
    installable.value = true
  })

  window.addEventListener('appinstalled', () => {
    isInstalled.value = true
    installable.value = false
  })

  if (window.matchMedia('(display-mode: standalone)').matches) {
    isInstalled.value = true
  }
})

async function install() {
  if (!deferredPrompt.value) {
    installable.value = false
    return
  }
  deferredPrompt.value.prompt()
  const result = await deferredPrompt.value.userChoice
  if (result.outcome === 'accepted') {
    isInstalled.value = true
    installable.value = false
  }
  deferredPrompt.value = null
}
</script>
