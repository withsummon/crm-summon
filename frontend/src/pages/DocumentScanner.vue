<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Scan Dokumen') }}
        </h1>
      </div>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Ambil foto dokumen nasabah') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div v-if="!cameraActive && !capturedImage" class="space-y-4">
        <div class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
          <div class="flex justify-center mb-4">
            <div class="flex size-16 items-center justify-center rounded-2xl bg-crm-surface">
              <FeatherIcon name="camera" class="size-8 text-crm-teal" />
            </div>
          </div>
          <p class="text-sm font-medium text-crm-text mb-1">
            {{ __('Ambil Dokumen') }}
          </p>
          <p class="text-xs text-crm-text-secondary mb-5">
            {{ __('Posisikan dokumen dalam bingkai') }}
          </p>
          <div class="space-y-2">
            <Button variant="solid" class="w-full" @click="startCamera">
              <template #prefix>
                <FeatherIcon name="camera" class="size-4" />
              </template>
              {{ __('Buka Kamera') }}
            </Button>
            <Button variant="outline" class="w-full" @click="openGallery">
              <template #prefix>
                <FeatherIcon name="upload" class="size-4" />
              </template>
              {{ __('Pilih dari Galeri') }}
            </Button>
          </div>
        </div>

        <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('Jenis Dokumen') }}
            </label>
            <select
              v-model="docType"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            >
              <option value="">{{ __('Pilih jenis dokumen') }}</option>
              <option v-for="t in docTypes" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <div class="flex justify-center mb-3">
          <FeatherIcon name="loader" class="size-8 animate-spin text-crm-teal" />
        </div>
        <p class="text-sm text-crm-text-secondary">{{ __('Memproses dokumen...') }}</p>
      </div>

      <div v-if="cameraPermissionDenied && !cameraActive && !capturedImage" class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <div class="flex justify-center mb-3">
          <div class="flex size-14 items-center justify-center rounded-2xl bg-red-50">
            <FeatherIcon name="alert-triangle" class="size-6 text-red-500" />
          </div>
        </div>
        <p class="text-sm font-medium text-crm-text mb-1">{{ __('Kamera Tidak Tersedia') }}</p>
        <p class="text-xs text-crm-text-secondary mb-4">{{ __('Izinkan akses kamera di pengaturan perangkat') }}</p>
        <Button variant="outline" class="w-full" @click="cameraPermissionDenied = false; startCamera()">
          {{ __('Coba Lagi') }}
        </Button>
      </div>

      <div v-if="cameraActive" class="relative overflow-hidden rounded-xl bg-black">
        <video ref="videoRef" autoplay playsinline class="w-full h-80 object-cover" />
        <div class="absolute inset-4 border-2 border-dashed border-white/30 rounded-xl" />
        <div class="absolute bottom-4 left-0 right-0 flex justify-center">
          <button
            class="size-14 rounded-full bg-white/90 flex items-center justify-center shadow-lg active:scale-95 transition-transform"
            @click="captureImage"
          >
            <div class="size-11 rounded-full border-2 border-crm-text" />
          </button>
        </div>
        <button
          class="absolute top-4 right-4 flex size-8 items-center justify-center rounded-full bg-black/50 text-white"
          @click="stopCamera"
        >
          <FeatherIcon name="x" class="size-5" />
        </button>
      </div>

      <div v-if="capturedImage && !loading && !ocrResult" class="space-y-4">
        <div class="rounded-xl overflow-hidden bg-black">
          <img :src="capturedImage" class="w-full object-contain max-h-64" />
        </div>

        <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('Jenis Dokumen') }}
            </label>
            <select
              v-model="docType"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            >
              <option value="">{{ __('Pilih jenis dokumen') }}</option>
              <option v-for="t in docTypes" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
        </div>

        <div class="flex gap-2">
          <Button variant="ghost" class="flex-1" @click="retake">
            <template #prefix>
              <FeatherIcon name="rotate-ccw" class="size-4" />
            </template>
            {{ __('Ambil Ulang') }}
          </Button>
          <Button variant="solid" class="flex-1" :loading="loading" :disabled="!docType" @click="runOCR">
            <template #prefix>
              <FeatherIcon name="search" class="size-4" />
            </template>
            {{ __('OCR & Ekstrak') }}
          </Button>
        </div>
      </div>

      <div v-if="ocrResult" class="space-y-4">
        <div class="rounded-xl overflow-hidden bg-black">
          <img :src="capturedImage" class="w-full object-contain max-h-48" />
        </div>

        <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
          <h3 class="text-sm font-semibold text-crm-text mb-3">
            {{ __('Hasil Ekstraksi') }}
            <span class="text-xs font-normal text-crm-text-secondary ml-2">
              ({{ ocrResult.model }})
            </span>
          </h3>
          <pre class="text-xs text-crm-text bg-crm-surface rounded-lg p-3 overflow-x-auto whitespace-pre-wrap">{{ extractedText }}</pre>
        </div>

        <div class="flex gap-2">
          <Button variant="ghost" class="flex-1" @click="retake">
            {{ __('Baru') }}
          </Button>
          <Button variant="solid" class="flex-1" :loading="uploading" @click="uploadDocument">
            <template #prefix>
              <FeatherIcon name="upload-cloud" class="size-4" />
            </template>
            {{ __('Unggah ke Lead') }}
          </Button>
        </div>
      </div>
    </div>

    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      class="hidden"
      @change="onFileSelected"
    />
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'

const videoRef = ref(null)
const fileInputRef = ref(null)
const cameraActive = ref(false)
const capturedImage = ref(null)
const docType = ref('')
const loading = ref(false)
const uploading = ref(false)
const ocrResult = ref(null)
const extractedText = ref('')
const cameraPermissionDenied = ref(false)
let stream = null

const docTypes = ['KTP', 'NPWP', 'KK', 'Akta', 'SHM', 'Sertifikat', 'Lainnya']

async function startCamera() {
  try {
    cameraPermissionDenied.value = false
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
      audio: false,
    })
    if (videoRef.value) videoRef.value.srcObject = stream
    cameraActive.value = true
  } catch {
    cameraPermissionDenied.value = true
  }
}

function stopCamera() {
  if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null }
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
  ocrResult.value = null
  extractedText.value = ''
}

function openGallery() {
  fileInputRef.value?.click()
}

function onFileSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  loading.value = true
  const reader = new FileReader()
  reader.onload = (ev) => {
    capturedImage.value = ev.target.result
    loading.value = false
    ocrResult.value = null
    extractedText.value = ''
  }
  reader.onerror = () => {
    toast.error(__('Gagal membaca file'))
    loading.value = false
  }
  reader.readAsDataURL(file)
}

function retake() {
  capturedImage.value = null
  docType.value = ''
  ocrResult.value = null
  extractedText.value = ''
}

async function runOCR() {
  if (!capturedImage.value || !docType.value) return
  loading.value = true
  ocrResult.value = null
  extractedText.value = ''
  try {
    const result = await call('crm.api.ocr.scan_document', {
      image_data: capturedImage.value,
      document_type: docType.value,
    })
    ocrResult.value = result
    extractedText.value = JSON.stringify(result.extracted, null, 2)
    toast.success(__('Dokumen berhasil diproses'))
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || __('Gagal memproses dokumen'))
  } finally {
    loading.value = false
  }
}

async function uploadDocument() {
  if (!capturedImage.value || !docType.value) return
  uploading.value = true
  try {
    const blob = await (await fetch(capturedImage.value)).blob()
    const file = new File([blob], `dokumen_${Date.now()}.jpg`, { type: 'image/jpeg' })
    await call('frappe.client.attach_file', {
      doctype: 'CRM Lead',
      docname: null,
      file: file,
      filename: file.name,
      is_private: true,
    })
    toast.success(__('Dokumen berhasil diunggah'))
    capturedImage.value = null
    docType.value = ''
    ocrResult.value = null
    extractedText.value = ''
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || __('Gagal mengunggah dokumen'))
  } finally {
    uploading.value = false
  }
}

onUnmounted(() => { stopCamera() })
</script>
