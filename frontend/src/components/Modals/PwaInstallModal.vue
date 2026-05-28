<template>
  <Dialog v-model="show" :options="{ size: 'sm' }">
    <template #body>
      <div class="p-5">
        <div class="flex flex-col items-center text-center mb-5">
          <div class="flex size-14 items-center justify-center rounded-2xl bg-crm-surface mb-4">
            <FeatherIcon name="smartphone" class="size-7 text-crm-teal" />
          </div>
          <h3 class="text-lg font-semibold text-ink-gray-9 mb-1">{{ __('Mobile RM Workspace') }}</h3>
          <p class="text-sm text-ink-gray-6 max-w-xs">
            {{ __('Akses workspace RM melalui PWA untuk pengalaman terbaik, atau langsung di browser.') }}
          </p>
        </div>

        <div class="space-y-3">
          <Button
            variant="solid"
            class="w-full !justify-start !h-auto py-3 px-4"
            @click="installOrShowGuide"
          >
            <div class="flex items-start gap-3">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-white/20">
                <FeatherIcon name="download" class="size-5" />
              </div>
              <div class="text-left">
                <p class="text-sm font-semibold">{{ __('Download PWA') }}</p>
                <p class="text-xs opacity-80">{{ __('Install di home screen untuk akses cepat & offline') }}</p>
              </div>
            </div>
          </Button>

          <Button
            variant="outline"
            class="w-full !justify-start !h-auto py-3 px-4"
            @click="navigateWeb"
          >
            <div class="flex items-start gap-3">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-crm-surface">
                <FeatherIcon name="globe" class="size-5 text-crm-teal" />
              </div>
              <div class="text-left">
                <p class="text-sm font-semibold text-crm-text">{{ __('Akses via Web') }}</p>
                <p class="text-xs text-crm-text-secondary">{{ __('Tetap di browser tanpa instalasi') }}</p>
              </div>
            </div>
          </Button>
        </div>

        <div v-if="showInstallGuide" class="mt-4 rounded-xl bg-surface-gray-1 border p-3 space-y-3">
          <p class="text-sm font-medium text-ink-gray-8">{{ __('Panduan Install') }}</p>
          <div v-if="installable" class="space-y-2">
            <Button variant="solid" class="w-full" @click="install">
              {{ __('Install Sekarang') }}
            </Button>
          </div>
          <div v-else class="space-y-2 text-xs text-ink-gray-6">
            <div class="flex items-start gap-2">
              <span class="flex size-5 shrink-0 items-center justify-center rounded-full bg-crm-surface text-xs font-bold text-crm-teal mt-0.5">1</span>
              <span>{{ __('Buka halaman ini di Chrome, Edge, atau Samsung Internet') }}</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="flex size-5 shrink-0 items-center justify-center rounded-full bg-crm-surface text-xs font-bold text-crm-teal mt-0.5">2</span>
              <span>{{ __('Tap menu browser (⋮) dan pilih "Add to Home Screen" atau "Install App"') }}</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="flex size-5 shrink-0 items-center justify-center rounded-full bg-crm-surface text-xs font-bold text-crm-teal mt-0.5">3</span>
              <span>{{ __('Ikuti langkah di layar untuk menyelesaikan instalasi') }}</span>
            </div>
          </div>
        </div>

        <div v-if="isInstalled" class="mt-4 rounded-xl bg-surface-green-2 border border-outline-green-2 p-3">
          <div class="flex items-center gap-2">
            <FeatherIcon name="check" class="size-5 text-green-600 shrink-0" />
            <p class="text-sm font-medium text-green-700">{{ __('App sudah terinstall') }}</p>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Dialog, Button, FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()
let show = defineModel({ type: Boolean })

const deferredPrompt = ref(null)
const installable = ref(false)
const isInstalled = ref(false)
const showInstallGuide = ref(false)

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

function installOrShowGuide() {
  if (installable.value) {
    install()
  } else {
    showInstallGuide.value = !showInstallGuide.value
  }
}

function navigateWeb() {
  show.value = false
  router.push('/mobile')
}

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
