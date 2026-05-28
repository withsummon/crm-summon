<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <h1 class="text-lg font-semibold text-crm-text">
        {{ __('Voice Commands') }}
      </h1>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Kontrol aplikasi dengan suara') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <button
          class="mx-auto flex size-20 items-center justify-center rounded-full transition-all duration-300"
          :class="isListening ? 'bg-red-50 scale-110 shadow-lg animate-pulse' : 'bg-crm-surface'"
          @click="toggleListening"
        >
          <div class="flex size-14 items-center justify-center rounded-full" :class="isListening ? 'bg-red-500' : 'bg-crm-teal'">
            <FeatherIcon name="mic" class="size-6 text-white" />
          </div>
        </button>
        <p class="text-sm font-medium text-crm-text mt-4">
          {{ statusText }}
        </p>
      </div>

      <div v-if="!isSupported" class="rounded-xl bg-amber-50 p-3 border border-amber-200 text-center">
        <p class="text-xs text-amber-700">{{ __('Peramban tidak mendukung pengenalan suara') }}</p>
      </div>

      <div v-if="history.length" class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <h2 class="text-sm font-semibold text-crm-text mb-3">{{ __('Riwayat Perintah') }}</h2>
        <div class="space-y-2">
          <div
            v-for="(item, i) in history"
            :key="i"
            class="flex items-start gap-3 rounded-lg bg-crm-surface p-3"
          >
            <FeatherIcon :name="item.recognized ? 'check-circle' : 'alert-circle'" class="size-4 mt-0.5 shrink-0" :class="item.recognized ? 'text-green-500' : 'text-red-500'" />
            <div class="min-w-0 flex-1">
              <p class="text-sm text-crm-text">"{{ item.transcript }}"</p>
              <p class="text-xs text-crm-muted mt-0.5">{{ item.action }} &middot; {{ item.time }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <FeatherIcon name="mic" class="size-10 text-crm-muted mx-auto mb-2" />
        <p class="text-sm text-crm-text-secondary">{{ __('Tekan tombol mic untuk mulai') }}</p>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <h2 class="text-sm font-semibold text-crm-text mb-3">{{ __('Contoh Perintah') }}</h2>
        <div class="grid grid-cols-1 gap-2">
          <button
            v-for="cmd in commandList"
            :key="cmd.phrase"
            class="flex items-center justify-between rounded-lg bg-crm-surface p-3 text-left hover:bg-crm-surface/80 transition-colors"
            @click="navigateCommand(cmd.route)"
          >
            <div class="flex items-center gap-3 min-w-0">
              <FeatherIcon :name="cmd.icon" class="size-4 text-crm-teal shrink-0" />
              <div>
                <code class="text-sm font-mono text-crm-text">{{ cmd.phrase }}</code>
                <p class="text-xs text-crm-text-secondary">{{ cmd.action }}</p>
              </div>
            </div>
            <FeatherIcon name="chevron-right" class="size-4 shrink-0 text-crm-muted" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { FeatherIcon, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()
const isListening = ref(false)
const isSupported = ref(false)
const history = ref([])
let recognition = null

const commandList = [
  { phrase: '"Buka dashboard"', action: __('Mobile Home Dashboard'), icon: 'grid', route: 'Mobile Home Dashboard' },
  { phrase: '"Buka lead baru"', action: __('Mobile Lead Capture'), icon: 'user-plus', route: 'Mobile Lead Capture' },
  { phrase: '"Buka nasabah"', action: __('My Customers Mobile'), icon: 'users', route: 'My Customers Mobile' },
  { phrase: '"Buka kunjungan"', action: __('Visit Planner & Route'), icon: 'map-pin', route: 'Visit Planner & Route' },
  { phrase: '"Buka approval"', action: __('Mobile Approval'), icon: 'check-circle', route: 'Mobile Approval' },
  { phrase: '"Buka notifikasi"', action: __('Mobile Push Notifications'), icon: 'bell', route: 'Mobile Push Notifications' },
  { phrase: '"Buka chat"', action: __('Mobile Omnichannel Chat'), icon: 'message-circle', route: 'Mobile Omnichannel Chat' },
  { phrase: '"Buka kalkulator"', action: __('Mobile Calculator Pricing'), icon: 'percent', route: 'Mobile Calculator Pricing' },
]

const phraseRouteMap = {
  'buka dashboard': 'Mobile Home Dashboard',
  'buka lead baru': 'Mobile Lead Capture',
  'buka nasabah': 'My Customers Mobile',
  'buka kunjungan': 'Visit Planner & Route',
  'buka approval': 'Mobile Approval',
  'buka notifikasi': 'Mobile Push Notifications',
  'buka chat': 'Mobile Omnichannel Chat',
  'buka kalkulator': 'Mobile Calculator Pricing',
}

const statusText = computed(() => {
  if (!isSupported.value) return __('Peramban tidak mendukung pengenalan suara')
  if (isListening.value) return __('Sedang mendengarkan...')
  if (history.value.length && !history.value[0].recognized) return __('Perintah tidak dikenali')
  if (history.value.length) return __('Katakan perintah...')
  return __('Tekan tombol mic untuk mulai')
})

function toggleListening() {
  if (isListening.value) {
    stopListening()
    return
  }
  startListening()
}

function startListening() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    isSupported.value = false
    return
  }
  isSupported.value = true
  recognition = new SpeechRecognition()
  recognition.lang = 'id-ID'
  recognition.continuous = false
  recognition.interimResults = false

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript.toLowerCase().trim()
    const matchedRoute = phraseRouteMap[transcript]
    if (matchedRoute) {
      history.value.unshift({
        transcript,
        action: __('Navigasi ke {0}', [matchedRoute]),
        time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
        recognized: true,
      })
      router.push({ name: matchedRoute })
    } else {
      history.value.unshift({
        transcript,
        action: __('Perintah tidak dikenali'),
        time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
        recognized: false,
      })
    }
    stopListening()
  }

  recognition.onerror = () => {
    toast.error(__('Gagal mengenali suara'))
    stopListening()
  }

  recognition.onend = () => {
    isListening.value = false
  }

  recognition.start()
  isListening.value = true
}

function stopListening() {
  if (recognition) {
    recognition.stop()
    recognition = null
  }
  isListening.value = false
}

function navigateCommand(routeName) {
  router.push({ name: routeName })
}

onUnmounted(() => {
  stopListening()
})
</script>
