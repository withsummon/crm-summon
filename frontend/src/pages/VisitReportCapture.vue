<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Laporan Kunjungan') }}
        </h1>
      </div>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Catat hasil kunjungan lapangan') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-4">
        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Kunjungan') }}
          </label>
          <select
            v-model="selectedVisit"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
          >
            <option :value="null">{{ __('Pilih kunjungan') }}</option>
            <option
              v-for="v in visits"
              :key="v.name"
              :value="v"
            >
              {{ v.customer_name || v.customer }} — {{ v.visit_date }}
            </option>
          </select>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Tujuan') }}
          </label>
          <select
            v-model="report.purpose"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
          >
            <option value="">{{ __('Pilih tujuan kunjungan') }}</option>
            <option v-for="p in purposes" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Hasil') }} <span class="text-red-500">*</span>
          </label>
          <select
            v-model="report.result"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
          >
            <option value="">{{ __('Pilih hasil kunjungan') }}</option>
            <option v-for="r in results" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Catatan') }}
          </label>
          <textarea
            v-model="report.notes"
            rows="4"
            :placeholder="__('Catatan hasil kunjungan...')"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted resize-none"
          />
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <h2 class="text-sm font-semibold text-crm-text mb-3">{{ __('Foto Kunjungan') }}</h2>
        <div class="grid grid-cols-3 gap-2">
          <div
            v-for="(slot, idx) in photoSlots"
            :key="idx"
            class="relative aspect-square rounded-xl border-2 border-dashed border-crm-border flex items-center justify-center overflow-hidden cursor-pointer transition-colors hover:border-crm-teal"
            :class="{ 'border-solid border-crm-teal': slot }"
            @click="triggerPhotoSlot(idx)"
          >
            <img v-if="slot" :src="slot.url" class="absolute inset-0 w-full h-full object-cover" />
            <div v-if="!slot" class="flex flex-col items-center gap-1">
              <FeatherIcon name="camera" class="size-6 text-crm-muted" />
            </div>
            <button
              v-if="slot"
              class="absolute top-1 right-1 flex size-5 items-center justify-center rounded-full bg-black/50 text-white"
              @click.stop="removePhoto(idx)"
            >
              <FeatherIcon name="x" class="size-3" />
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="fullscreenPhoto !== null"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/90 p-4"
        @click="fullscreenPhoto = null"
      >
        <img :src="photoSlots[fullscreenPhoto]?.url" class="max-w-full max-h-full object-contain" />
        <button class="absolute top-6 right-6 flex size-8 items-center justify-center rounded-full bg-black/50 text-white" @click="fullscreenPhoto = null">
          <FeatherIcon name="x" class="size-5" />
        </button>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-crm-text">{{ __('Action Items') }}</h2>
          <button
            class="flex items-center gap-1 text-xs font-medium text-crm-teal"
            @click="addActionItem"
          >
            <FeatherIcon name="plus" class="size-3.5" />
            {{ __('Tambah') }}
          </button>
        </div>

        <div v-if="actionItems.length === 0" class="py-4 text-center">
          <FeatherIcon name="check-square" class="size-6 text-crm-muted mx-auto mb-1" />
          <p class="text-xs text-crm-text-secondary">{{ __('Belum ada action items') }}</p>
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="(item, idx) in actionItems"
            :key="idx"
            class="rounded-xl border border-crm-border p-3"
          >
            <div class="flex items-start justify-between mb-2">
              <input
                v-model="item.description"
                type="text"
                :placeholder="__('Deskripsi action item')"
                class="flex-1 text-sm text-crm-text outline-none placeholder:text-crm-muted bg-transparent"
              />
              <button class="ml-2 shrink-0" @click="removeActionItem(idx)">
                <FeatherIcon name="trash-2" class="size-4 text-red-400" />
              </button>
            </div>
            <div class="flex gap-2">
              <select
                v-model="item.dueDate"
                class="flex-1 rounded-xl border border-crm-border px-2.5 py-1.5 text-xs text-crm-text outline-none focus:border-crm-teal"
              >
                <option value="H+1">H+1</option>
                <option value="H+3">H+3</option>
                <option value="H+7">H+7</option>
                <option value="H+14">H+14</option>
                <option value="H+30">H+30</option>
              </select>
              <input
                v-model="item.assignee"
                type="text"
                :placeholder="__('Penanggung jawab')"
                class="flex-1 rounded-xl border border-crm-border px-2.5 py-1.5 text-xs text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-if="error" class="rounded-xl bg-red-50 border border-red-200 p-3">
        <p class="text-xs text-red-600">{{ error }}</p>
      </div>

      <Button
        variant="solid"
        class="w-full"
        :loading="saving"
        :disabled="!selectedVisit || !report.result"
        @click="saveReport"
      >
        <template #prefix>
          <FeatherIcon name="save" class="size-4" />
        </template>
        {{ __('Simpan Laporan') }}
      </Button>
    </div>

    <input
      ref="photoInputRef"
      type="file"
      accept="image/*"
      capture="environment"
      class="hidden"
      @change="onPhotoCaptured"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

const purposes = ['Survey', 'Collection', 'Promotion', 'Follow-up', 'Evaluation', 'Lainnya']
const results = ['Succeeded', 'Follow-up Needed', 'Customer Not Available', 'Rejected', 'Lainnya']

const visits = ref([])
const selectedVisit = ref(null)

const report = ref({
  purpose: '',
  result: '',
  notes: '',
})

const photoSlots = ref([null, null, null])
const fullscreenPhoto = ref(null)
const photoInputRef = ref(null)
let activeSlotIndex = 0
const saving = ref(false)
const error = ref('')

const actionItems = ref([])

async function loadVisits() {
  try {
    visits.value = await call('crm.api.visit.list_visits')
  } catch (err) {
    error.value = err.messages?.[0] || err.message || __('Gagal memuat daftar kunjungan')
  }
}

onMounted(loadVisits)

function triggerPhotoSlot(idx) {
  if (photoSlots.value[idx]) {
    fullscreenPhoto.value = idx
    return
  }
  activeSlotIndex = idx
  photoInputRef.value?.click()
}

function onPhotoCaptured(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    photoSlots.value[activeSlotIndex] = { url: ev.target.result, file }
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

function removePhoto(idx) {
  photoSlots.value[idx] = null
}

function addActionItem() {
  actionItems.value.push({
    description: '',
    dueDate: 'H+3',
    assignee: '',
  })
}

function removeActionItem(idx) {
  actionItems.value.splice(idx, 1)
}

function fileToBase64(file) {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result.split(',')[1])
    reader.readAsDataURL(file)
  })
}

async function saveReport() {
  error.value = ''
  if (!selectedVisit.value) {
    error.value = __('Pilih kunjungan terlebih dahulu')
    return
  }
  if (!report.value.result) {
    error.value = __('Hasil kunjungan harus diisi')
    return
  }

  saving.value = true
  try {
    const uploadedPhotos = []
    for (const slot of photoSlots.value) {
      if (slot && slot.file) {
        const base64 = await fileToBase64(slot.file)
        const result = await call('frappe.client.attach_file', {
          doctype: 'CRM Visit Log',
          docname: selectedVisit.value.name,
          filedata: base64,
          filename: `visit_${Date.now()}.jpg`,
          is_private: 1,
        })
        uploadedPhotos.push({ file_url: result.file_url, caption: '' })
      }
    }

    await call('crm.api.visit.submit_report', {
      visit_id: selectedVisit.value.name,
      result: report.value.result,
      report_notes: report.value.notes,
      photos: uploadedPhotos.length ? JSON.stringify(uploadedPhotos) : null,
      action_items: actionItems.value.length
        ? JSON.stringify(
            actionItems.value.map((a) => ({
              description: a.description,
              due_date: a.dueDate,
              assignee: a.assignee,
            }))
          )
        : null,
    })

    toast.success(__('Laporan kunjungan berhasil disimpan'))
    router.push({ name: 'Visit Planner & Route' })
  } catch (err) {
    error.value = err.messages?.[0] || err.message || __('Gagal menyimpan laporan')
  } finally {
    saving.value = false
  }
}
</script>
