<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <h1 class="text-lg font-semibold text-crm-text">
        {{ __('Scan Kartu Nama') }}
      </h1>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Scan kartu nama langsung jadi lead') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div v-if="!capturedImage && !cameraActive && !processing" class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <FeatherIcon name="camera" class="size-12 text-crm-muted mx-auto mb-3" />
        <p class="text-sm font-medium text-crm-text mb-4">
          {{ __('Arahkan kamera ke kartu nama') }}
        </p>
        <div class="space-y-2">
          <Button variant="solid" class="w-full" @click="startCamera">
            <template #prefix>
              <FeatherIcon name="camera" class="size-4" />
            </template>
            {{ __('Buka Kamera') }}
          </Button>
          <label class="block">
            <Button variant="outline" class="w-full cursor-pointer">
              <template #prefix>
                <FeatherIcon name="upload" class="size-4" />
              </template>
              {{ __('Pilih dari Gallery') }}
            </Button>
            <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileSelected" />
          </label>
        </div>
      </div>

      <div v-if="cameraActive" class="relative overflow-hidden rounded-xl bg-black">
        <video ref="videoRef" autoplay playsinline class="w-full h-80 object-cover" />
        <div class="absolute inset-4 border-2 border-dashed border-white/30 rounded-xl" />
        <div class="absolute bottom-4 left-0 right-0 flex justify-center">
          <button
            class="flex size-16 items-center justify-center rounded-full bg-white/80 shadow-lg"
            @click="captureImage"
          >
            <div class="size-12 rounded-full border-2 border-crm-teal" />
          </button>
        </div>
        <button class="absolute top-4 right-4 flex size-8 items-center justify-center rounded-full bg-black/50 text-white" @click="stopCamera">
          <FeatherIcon name="x" class="size-5" />
        </button>
      </div>

      <div v-if="processing" class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <FeatherIcon name="loader" class="size-10 text-crm-teal mx-auto mb-3 animate-spin" />
        <p class="text-sm font-medium text-crm-text">{{ __('Memproses kartu nama...') }}</p>
      </div>

      <div v-if="capturedImage && !processing" class="space-y-4">
        <div class="rounded-xl overflow-hidden bg-black">
          <img :src="capturedImage" class="w-full object-contain max-h-56" />
        </div>

        <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-3">
          <h2 class="text-sm font-semibold text-crm-text border-b border-crm-border pb-2">
            {{ __('Data Ekstraksi') }}
          </h2>
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('Nama') }}</label>
            <input v-model="extracted.name" type="text" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal" />
          </div>
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('No. Telepon') }}</label>
            <input v-model="extracted.phone" type="tel" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal" />
          </div>
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('Email') }}</label>
            <input v-model="extracted.email" type="email" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal" />
          </div>
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('Perusahaan') }}</label>
            <input v-model="extracted.company" type="text" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal" />
          </div>
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('Jabatan') }}</label>
            <input v-model="extracted.position" type="text" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal" />
          </div>
        </div>

        <div class="flex gap-2">
          <Button variant="ghost" class="flex-1" @click="retake">
            {{ __('Ambil Ulang') }}
          </Button>
          <Button variant="solid" class="flex-1" :disabled="!extracted.name" :loading="saving" @click="saveAsLead">
            <template #prefix>
              <FeatherIcon name="user-plus" class="size-4" />
            </template>
            {{ __('Simpan sebagai Lead') }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { usersStore } from '@/stores/users'

const router = useRouter()
const { getUser } = usersStore()

const videoRef = ref(null)
const fileInput = ref(null)
const cameraActive = ref(false)
const capturedImage = ref(null)
const processing = ref(false)
const saving = ref(false)
let stream = null

const extracted = ref({
  name: '',
  phone: '',
  email: '',
  company: '',
  position: '',
})

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
      audio: false,
    })
    if (videoRef.value) videoRef.value.srcObject = stream
    cameraActive.value = true
  } catch {
    toast.error(__('Izin kamera ditolak. Periksa pengaturan peramban Anda.'))
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(t => t.stop())
    stream = null
  }
  cameraActive.value = false
}

function captureImage() {
  if (!videoRef.value) return
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  canvas.getContext('2d').drawImage(videoRef.value, 0, 0)
  capturedImage.value = canvas.toDataURL('image/jpeg', 0.9)
  stopCamera()
  runOCRExtraction()
}

function onFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    capturedImage.value = ev.target.result
    runOCRExtraction()
  }
  reader.readAsDataURL(file)
}

async function runOCRExtraction() {
  if (!capturedImage.value) return
  processing.value = true
  try {
    const result = await call('crm.api.ocr.scan_business_card', {
      image_data: capturedImage.value,
    })
    extracted.value = {
      name: result.name || '',
      phone: result.phone || '',
      email: result.email || '',
      company: result.company || '',
      position: result.position || '',
    }
    if (result.name) {
      toast.success(__('Kartu nama berhasil diproses'))
    } else {
      toast.warning(__('Hasil ekstraksi kosong, coba foto dengan pencahayaan lebih baik'))
    }
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || __('Gagal memproses kartu nama'))
  } finally {
    processing.value = false
  }
}

function retake() {
  capturedImage.value = null
  extracted.value = { name: '', phone: '', email: '', company: '', position: '' }
  processing.value = false
}

async function saveAsLead() {
  if (!extracted.value.name) {
    toast.error(__('Nama harus diisi'))
    return
  }
  saving.value = true
  try {
    const nameParts = extracted.value.name.split(' ')
    const doc = {
      doctype: 'CRM Lead',
      first_name: nameParts[0],
      last_name: nameParts.slice(1).join(' ') || '',
      mobile_no: extracted.value.phone,
      email_id: extracted.value.email,
      company_name: extracted.value.company,
      custom_position: extracted.value.position,
      source: 'Business Card Scan',
      lead_owner: getUser().name,
    }
    const result = await call('frappe.client.insert', { doc })
    toast.success(__('Lead berhasil dibuat dari kartu nama'))
    router.push({ name: 'Lead', params: { leadId: result.name } })
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || __('Gagal membuat lead'))
  } finally {
    saving.value = false
  }
}

onUnmounted(() => { stopCamera() })
</script>
