<template>
  <div class="flex flex-1 flex-col bg-white">
    <div class="px-4 pb-4 pt-2">
      <h1 class="text-lg font-semibold text-crm-text">
        {{ __('Keamanan Aplikasi') }}
      </h1>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Atur keamanan dan metode login mobile') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-crm-surface">
              <FeatherIcon name="fingerprint" class="size-5 text-crm-teal" />
            </div>
            <div>
              <p class="text-sm font-medium text-crm-text">
                {{ __('Biometric Unlock') }}
              </p>
              <p class="text-xs text-crm-text-secondary mt-0.5">
                {{ biometricSupported ? __('Gunakan sidik jari atau Face ID') : __('Tidak didukung perangkat ini') }}
              </p>
            </div>
          </div>
          <button
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
            :class="biometricEnabled ? 'bg-crm-teal' : 'bg-gray-200'"
            :disabled="!biometricSupported || enrolling"
            @click="toggleBiometric"
          >
            <span
              class="inline-block size-5 transform rounded-full bg-white shadow-sm transition-transform"
              :class="biometricEnabled ? 'translate-x-[22px]' : 'translate-x-[2px]'"
            />
          </button>
        </div>
        <div
          v-if="!biometricSupported"
          class="mt-3 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2"
        >
          <p class="text-xs text-amber-700">
            {{ __('Perangkat ini tidak mendukung biometric. Gunakan PIN sebagai alternatif.') }}
          </p>
        </div>
        <div v-if="enrolling" class="mt-3 flex items-center gap-2 text-sm text-crm-text-secondary">
          <FeatherIcon name="loader" class="size-4 animate-spin" />
          {{ __('Memindai sidik jari...') }}
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-crm-surface">
              <FeatherIcon name="lock" class="size-5 text-crm-teal" />
            </div>
            <div>
              <p class="text-sm font-medium text-crm-text">
                {{ __('PIN Security') }}
              </p>
              <p class="text-xs text-crm-text-secondary mt-0.5">
                {{ pinSet ? __('PIN sudah diatur') : __('Atur PIN 6 digit sebagai cadangan') }}
              </p>
            </div>
          </div>
          <button
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
            :class="pinEnabled ? 'bg-crm-teal' : 'bg-gray-200'"
            @click="togglePin"
          >
            <span
              class="inline-block size-5 transform rounded-full bg-white shadow-sm transition-transform"
              :class="pinEnabled ? 'translate-x-[22px]' : 'translate-x-[2px]'"
            />
          </button>
        </div>

        <div v-if="showPinInput" class="mt-4 space-y-3">
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1 block">
              {{ pinSet ? __('Masukkan PIN baru') : __('Buat PIN 6 digit') }}
            </label>
            <div class="flex gap-2 justify-center">
              <input
                v-for="i in 6"
                :key="i"
                :ref="el => pinRefs[i - 1] = el"
                v-model="pinDigits[i - 1]"
                type="tel"
                maxlength="1"
                class="size-11 rounded-xl border text-center text-lg font-semibold text-crm-text outline-none transition-colors"
                :class="pinError ? 'border-red-400 bg-red-50' : 'border-crm-border focus:border-crm-teal'"
                @input="onPinInput(i - 1)"
                @keydown="onPinKeydown($event, i - 1)"
              />
            </div>
            <p v-if="pinError" class="text-xs text-red-500 mt-1.5 text-center">
              {{ pinError }}
            </p>
          </div>
          <Button
            variant="solid"
            class="w-full"
            :disabled="pinDigits.filter(Boolean).length !== 6 || savingPin"
            @click="savePin"
          >
            {{ pinSet ? __('Update PIN') : __('Simpan PIN') }}
          </Button>
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex size-10 items-center justify-center rounded-xl bg-crm-surface">
              <FeatherIcon name="clock" class="size-5 text-crm-teal" />
            </div>
            <div>
              <p class="text-sm font-medium text-crm-text">
                {{ __('Auto Lock') }}
              </p>
              <p class="text-xs text-crm-text-secondary mt-0.5">
                {{ autoLockLabel }}
              </p>
            </div>
          </div>
        </div>
        <div class="mt-3">
          <select
            v-model="autoLockMinutes"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            @change="saveAutoLock"
          >
            <option :value="0">{{ __('Jangan kunci otomatis') }}</option>
            <option :value="1">{{ __('1 menit') }}</option>
            <option :value="5">{{ __('5 menit') }}</option>
            <option :value="15">{{ __('15 menit') }}</option>
            <option :value="30">{{ __('30 menit') }}</option>
            <option :value="60">{{ __('1 jam') }}</option>
          </select>
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex size-10 items-center justify-center rounded-xl bg-crm-surface">
            <FeatherIcon name="log-out" class="size-5 text-red-500" />
          </div>
          <div>
            <p class="text-sm font-medium text-crm-text">
              {{ __('Sesi Aktif') }}
            </p>
            <p class="text-xs text-crm-text-secondary mt-0.5">
              {{ session.user.value }}
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          class="w-full text-red-500 border-red-200 hover:bg-red-50"
          @click="confirmLogout"
        >
          <template #prefix>
            <FeatherIcon name="log-out" class="size-4" />
          </template>
          {{ __('Logout') }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon, Button, toast } from 'frappe-ui'
import { sessionStore } from '@/stores/session'

const session = sessionStore()

const BIOMETRIC_KEY = 'crm_biometric_credential'
const PIN_KEY = 'crm_pin_hash'
const PIN_ENABLED_KEY = 'crm_pin_enabled'
const AUTO_LOCK_KEY = 'crm_auto_lock_minutes'
const BIOMETRIC_ENABLED_KEY = 'crm_biometric_enabled'

const biometricSupported = ref(false)
const biometricEnabled = ref(false)
const enrolling = ref(false)
const pinSet = ref(false)
const pinEnabled = ref(false)
const showPinInput = ref(false)
const pinDigits = ref(Array(6).fill(''))
const pinError = ref('')
const savingPin = ref(false)
const autoLockMinutes = ref(0)
const pinRefs = ref([])

onMounted(() => {
  biometricSupported.value = !!(window.PublicKeyCredential && navigator.credentials)
  biometricEnabled.value = localStorage.getItem(BIOMETRIC_ENABLED_KEY) === 'true'
  pinSet.value = !!localStorage.getItem(PIN_KEY)
  pinEnabled.value = localStorage.getItem(PIN_ENABLED_KEY) === 'true'
  autoLockMinutes.value = parseInt(localStorage.getItem(AUTO_LOCK_KEY) || '0', 10)
})

function generateChallenge() {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return array
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}

async function toggleBiometric() {
  if (biometricEnabled.value) {
    biometricEnabled.value = false
    localStorage.removeItem(BIOMETRIC_KEY)
    localStorage.removeItem(BIOMETRIC_ENABLED_KEY)
    toast.success(__('Biometric disabled'))
    return
  }

  if (!biometricSupported.value) {
    toast.error(__('Biometric tidak didukung perangkat ini'))
    return
  }

  enrolling.value = true
  try {
    const credential = await navigator.credentials.create({
      publicKey: {
        challenge: generateChallenge(),
        rp: { name: 'BNI CRM' },
        user: {
          id: generateChallenge(),
          name: session.user.value || 'user',
          displayName: session.user.value || 'User',
        },
        pubKeyCredParams: [{ alg: -7, type: 'public-key' }],
        authenticatorSelection: {
          authenticatorAttachment: 'platform',
          userVerification: 'required',
        },
        timeout: 60000,
      },
    })

    if (credential) {
      const credId = arrayBufferToBase64(credential.rawId)
      localStorage.setItem(BIOMETRIC_KEY, credId)
      localStorage.setItem(BIOMETRIC_ENABLED_KEY, 'true')
      biometricEnabled.value = true
      toast.success(__('Biometric berhasil diaktifkan'))
    }
  } catch (err) {
    if (err.name === 'NotAllowedError') {
      toast.error(__('Biometric dibatalkan'))
    } else {
      toast.error(__('Gagal mendaftarkan biometric'))
    }
  } finally {
    enrolling.value = false
  }
}

function togglePin() {
  if (pinEnabled.value) {
    pinEnabled.value = false
    localStorage.setItem(PIN_ENABLED_KEY, 'false')
    showPinInput.value = false
    toast.success(__('PIN login dinonaktifkan'))
  } else {
    showPinInput.value = true
    pinDigits.value = Array(6).fill('')
    pinError.value = ''
    setTimeout(() => pinRefs.value[0]?.focus(), 100)
  }
}

function onPinInput(index) {
  const val = pinDigits.value[index]
  if (val && !/^\d$/.test(val)) {
    pinDigits.value[index] = ''
    return
  }
  if (val && index < 5) {
    pinRefs.value[index + 1]?.focus()
  }
  pinError.value = ''
}

function onPinKeydown(event, index) {
  if (event.key === 'Backspace') {
    pinDigits.value[index] = ''
    if (index > 0) {
      pinRefs.value[index - 1]?.focus()
    }
  }
}

function savePin() {
  const pin = pinDigits.value.join('')
  if (pin.length !== 6) {
    pinError.value = __('PIN harus 6 digit')
    return
  }
  savingPin.value = true
  try {
    const hash = btoa(pin)
    localStorage.setItem(PIN_KEY, hash)
    localStorage.setItem(PIN_ENABLED_KEY, 'true')
    pinSet.value = true
    pinEnabled.value = true
    showPinInput.value = false
    pinDigits.value = Array(6).fill('')
    toast.success(__('PIN berhasil disimpan'))
  } catch {
    pinError.value = __('Gagal menyimpan PIN')
  } finally {
    savingPin.value = false
  }
}

const autoLockLabel = computed(() => {
  if (autoLockMinutes.value === 0) return __('Tidak ada auto lock')
  if (autoLockMinutes.value === 1) return __('1 menit tidak aktif')
  return `${autoLockMinutes.value} ${__('menit tidak aktif')}`
})

function saveAutoLock() {
  localStorage.setItem(AUTO_LOCK_KEY, String(autoLockMinutes.value))
  toast.success(__('Auto lock diperbarui'))
}

function confirmLogout() {
  session.logout.submit()
}
</script>
