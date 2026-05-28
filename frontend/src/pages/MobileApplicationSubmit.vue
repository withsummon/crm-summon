<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <h1 class="text-lg font-semibold text-crm-text">
        {{ __('Ajukan Aplikasi') }}
      </h1>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Ajukan aplikasi kredit dari lapangan') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-4">
        <h2 class="text-sm font-semibold text-crm-text border-b border-crm-border pb-2">
          {{ __('Data Pemohon') }}
        </h2>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Nama Lengkap') }} <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.borrower_name"
            type="text"
            :placeholder="__('e.g. Budi Santoso / PT Maju Jaya')"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
          />
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Jenis Pemohon') }}
          </label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="t in borrowerTypes"
              :key="t.value"
              class="rounded-xl border py-2.5 text-sm font-medium transition-colors"
              :class="form.borrower_type === t.value
                ? 'border-crm-teal bg-crm-surface text-crm-teal'
                : 'border-crm-border text-crm-text-secondary hover:border-crm-teal/50'"
              @click="form.borrower_type = t.value"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('No. KTP') }}
            </label>
            <input
              v-model="form.nik"
              type="text"
              :placeholder="__('16 digit')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            />
          </div>
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('No. NPWP') }}
            </label>
            <input
              v-model="form.npwp"
              type="text"
              placeholder="XX.XXX.XXX.X-XXX.XXX"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text font-mono outline-none focus:border-crm-teal"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('Email') }}
            </label>
            <input
              v-model="form.email"
              type="email"
              :placeholder="__('email@example.com')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            />
          </div>
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('No. Telepon') }}
            </label>
            <input
              v-model="form.phone"
              type="tel"
              :placeholder="__('+62 xxx xxxx')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            />
          </div>
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-4">
        <h2 class="text-sm font-semibold text-crm-text border-b border-crm-border pb-2">
          {{ __('Detail Kredit') }}
        </h2>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Jenis Kredit') }}
          </label>
          <select
            v-model="form.loan_type"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
          >
            <option value="Kredit Modal Kerja">{{ __('Kredit Modal Kerja') }}</option>
            <option value="Kredit Investasi">{{ __('Kredit Investasi') }}</option>
            <option value="Kredit Konsumsi">{{ __('Kredit Konsumsi') }}</option>
            <option value="KPR">{{ __('KPR') }}</option>
            <option value="Kredit Multiguna">{{ __('Kredit Multiguna') }}</option>
            <option value="Lainnya">{{ __('Lainnya') }}</option>
          </select>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Jumlah Pengajuan') }} <span class="text-red-500">*</span>
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-crm-muted font-medium">
              Rp
            </span>
            <input
              v-model="form.amount"
              type="text"
              inputmode="numeric"
              :placeholder="__('0')"
              class="w-full rounded-xl border border-crm-border pl-10 pr-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
              @input="formatAmount"
            />
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Jangka Waktu') }}
          </label>
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="t in tenors"
              :key="t.value"
              class="rounded-xl border py-2 text-xs font-medium transition-colors"
              :class="form.tenor === t.value
                ? 'border-crm-teal bg-crm-surface text-crm-teal'
                : 'border-crm-border text-crm-text-secondary hover:border-crm-teal/50'"
              @click="form.tenor = t.value"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Tujuan Penggunaan') }}
          </label>
          <textarea
            v-model="form.purpose"
            rows="3"
            :placeholder="__('Deskripsikan tujuan penggunaan dana...')"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal resize-none"
          />
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-4">
        <h2 class="text-sm font-semibold text-crm-text border-b border-crm-border pb-2">
          {{ __('Dokumen Pendukung') }}
        </h2>

        <div
          v-for="doc in requiredDocs"
          :key="doc.key"
          class="flex items-center gap-3"
        >
          <div
            class="flex size-10 shrink-0 items-center justify-center rounded-xl"
            :class="doc.uploaded ? 'bg-green-50' : 'bg-crm-surface'"
          >
            <FeatherIcon
              :name="doc.uploaded ? 'check-circle' : 'upload'"
              class="size-5"
              :class="doc.uploaded ? 'text-green-600' : 'text-crm-muted'"
            />
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-crm-text">{{ doc.label }}</p>
            <p v-if="doc.uploaded" class="text-xs text-green-600">
              {{ __('Sudah diupload') }}
            </p>
          </div>
          <FileUploader @success="(file) => handleFileSuccess(doc, file)">
            <template #default="{ openFileSelector }">
              <Button variant="outline" size="sm" @click="openFileSelector">
                {{ doc.uploaded ? __('Ganti') : __('Upload') }}
              </Button>
            </template>
          </FileUploader>
        </div>
      </div>

      <ErrorMessage
        v-if="error"
        :message="error"
        class="rounded-xl"
      />

      <Button
        variant="solid"
        class="w-full"
        :loading="submitting"
        :disabled="!form.borrower_name || !form.amount"
        @click="submitApplication"
      >
        <template #prefix>
          <FeatherIcon name="send" class="size-4" />
        </template>
        {{ __('Ajukan Aplikasi') }}
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FeatherIcon, Button, FileUploader, ErrorMessage, call, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
  borrower_name: '',
  borrower_type: 'individual',
  nik: '',
  npwp: '',
  email: '',
  phone: '',
  loan_type: 'Kredit Modal Kerja',
  amount: '',
  tenor: '12',
  purpose: '',
})

const borrowerTypes = [
  { value: 'individual', label: __('Perorangan') },
  { value: 'company', label: __('Perusahaan') },
]

const tenors = [
  { value: '6', label: __('6 bln') },
  { value: '12', label: __('1 thn') },
  { value: '24', label: __('2 thn') },
  { value: '36', label: __('3 thn') },
  { value: '60', label: __('5 thn') },
  { value: '120', label: __('10 thn') },
  { value: '180', label: __('15 thn') },
  { value: '240', label: __('20 thn') },
]

const requiredDocs = ref([
  { key: 'ktp', label: __('KTP'), uploaded: false, file: null },
  { key: 'npwp_doc', label: __('NPWP'), uploaded: false, file: null },
  { key: 'bank_statement', label: __('Rekening Koran'), uploaded: false, file: null },
  { key: 'financial_report', label: __('Laporan Keuangan'), uploaded: false, file: null },
])

const error = ref('')
const submitting = ref(false)

function parseNumber(str) {
  return parseInt(String(str).replace(/[^0-9]/g, ''), 10) || 0
}

function formatAmount(e) {
  const value = e.target.value.replace(/[^0-9]/g, '')
  if (value) {
    form.value.amount = parseInt(value, 10).toLocaleString('id-ID')
  } else {
    form.value.amount = ''
  }
}

function handleFileSuccess(doc, file) {
  doc.uploaded = true
  doc.file = file
}

async function submitApplication() {
  error.value = ''
  if (!form.value.borrower_name) {
    error.value = __('Nama peminjam harus diisi')
    return
  }
  if (!form.value.amount || parseNumber(form.value.amount) <= 0) {
    error.value = __('Jumlah pinjaman harus diisi')
    return
  }

  submitting.value = true
  try {
    const result = await call('crm.api.credit.create_credit_application', {
      payload: {
        borrower_name: form.value.borrower_name,
        borrower_type: form.value.borrower_type,
        facility_type: form.value.loan_type,
        requested_amount: parseNumber(form.value.amount),
        tenor_months: parseInt(form.value.tenor, 10) || 0,
        purpose: form.value.purpose || '',
        submission_date: new Date().toISOString().split('T')[0],
      }
    })

    const uploadedDocs = requiredDocs.value.filter((d) => d.file)
    for (const doc of uploadedDocs) {
      try {
        await call('frappe.client.attach_file', {
          doctype: 'CRM Credit Application',
          docname: result.name,
          filedata: doc.file,
          filename: doc.file.name,
          is_private: 1,
        })
      } catch { /* silent */ }
    }

    toast.success(__('Aplikasi kredit berhasil diajukan'))
    router.push({ name: 'Mobile Home Dashboard' })
  } catch (err) {
    error.value = err.messages?.[0] || err.message || __('Gagal mengajukan aplikasi')
  } finally {
    submitting.value = false
  }
}
</script>
