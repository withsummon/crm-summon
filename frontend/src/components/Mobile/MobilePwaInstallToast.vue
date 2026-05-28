<template>
  <TransitionRoot
    :show="visible"
    enter="transition-all duration-300 ease-out"
    enter-from="translate-y-full opacity-0"
    enter-to="translate-y-0 opacity-100"
    leave="transition-all duration-200 ease-in"
    leave-from="translate-y-0 opacity-100"
    leave-to="translate-y-full opacity-0"
  >
    <div
      class="fixed bottom-0 left-0 right-0 z-50 border-t bg-white px-4 pb-6 pt-3 shadow-lg"
    >
      <div class="flex items-start gap-3">
        <div
          class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-crm-surface"
        >
          <FeatherIcon name="smartphone" class="size-5 text-crm-teal" />
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-semibold text-ink-gray-9">
            {{ __('Install BNI CRM') }}
          </p>
          <p class="text-xs text-ink-gray-6 mt-0.5">
            {{ __('Install for quick access & offline support') }}
          </p>
        </div>
        <button
          class="flex size-7 items-center justify-center rounded-lg hover:bg-surface-gray-2"
          @click="dismiss"
        >
          <FeatherIcon name="x" class="size-4 text-ink-gray-5" />
        </button>
      </div>
      <div class="mt-3 flex gap-2">
        <Button variant="solid" class="flex-1" @click="install">
          <template #prefix>
            <FeatherIcon name="download" class="size-4" />
          </template>
          {{ __('Install') }}
        </Button>
        <Button variant="ghost" class="flex-1" @click="dismiss">
          {{ __('Not Now') }}
        </Button>
      </div>
    </div>
  </TransitionRoot>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import { TransitionRoot } from '@headlessui/vue'

const visible = ref(false)
const deferredPrompt = ref(null)
const dismissed = ref(false)

const DISMISS_DURATION = 7 * 24 * 60 * 60 * 1000

onMounted(() => {
  if (window.matchMedia('(display-mode: standalone)').matches) return

  const dismissedUntil = localStorage.getItem('pwaToastDismissed')
  if (dismissedUntil && Date.now() < parseInt(dismissedUntil, 10)) return

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt.value = e
    visible.value = true
  })

  window.addEventListener('appinstalled', () => {
    visible.value = false
  })
})

async function install() {
  if (!deferredPrompt.value) return
  deferredPrompt.value.prompt()
  const result = await deferredPrompt.value.userChoice
  if (result.outcome === 'accepted') {
    visible.value = false
  }
  deferredPrompt.value = null
}

function dismiss() {
  visible.value = false
  dismissed.value = true
  localStorage.setItem('pwaToastDismissed', String(Date.now() + DISMISS_DURATION))
}
</script>
