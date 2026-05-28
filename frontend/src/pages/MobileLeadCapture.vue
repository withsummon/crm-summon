<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Capture Lead') }}
        </h1>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-4">
        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Nama Lengkap') }} <span class="text-red-500">*</span>
          </label>
          <div class="grid grid-cols-2 gap-2">
            <input
              v-model="form.first_name"
              type="text"
              :placeholder="__('Nama Depan')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
            />
            <input
              v-model="form.last_name"
              type="text"
              :placeholder="__('Nama Belakang')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
            />
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('No. Telepon') }}
          </label>
          <input
            v-model="form.mobile_no"
            type="tel"
            :placeholder="__('+62 xxx xxxx xxxx')"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
          />
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Email') }}
          </label>
          <input
            v-model="form.email"
            type="email"
            :placeholder="__('email@example.com')"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
          />
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Perusahaan') }}
          </label>
          <input
            v-model="form.company"
            type="text"
            :placeholder="__('Nama perusahaan')"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
          />
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Source') }}
          </label>
          <select
            v-model="form.source"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
          >
            <option value="">{{ __('Pilih source') }}</option>
            <option v-for="s in leadSources" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Catatan') }}
          </label>
          <textarea
            v-model="form.notes"
            rows="3"
            :placeholder="__('Catatan tambahan...')"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted resize-none"
          />
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
        :disabled="!form.first_name"
        @click="submitLead"
      >
        <template #prefix>
          <FeatherIcon name="user-plus" class="size-4" />
        </template>
        {{ __('Simpan Lead') }}
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FeatherIcon, Button, ErrorMessage, call, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { usersStore } from '@/stores/users'

const router = useRouter()
const { getUser } = usersStore()

const form = ref({
  first_name: '',
  last_name: '',
  mobile_no: '',
  email: '',
  company: '',
  source: '',
  notes: '',
})

const error = ref('')
const submitting = ref(false)

const leadSources = [
  'Walk In', 'Phone Call', 'WhatsApp', 'Email', 'Website',
  'Referral', 'Event', 'Social Media', 'Cold Call', 'Other',
]

async function submitLead() {
  error.value = ''
  if (!form.value.first_name) {
    error.value = __('Nama depan harus diisi')
    return
  }

  submitting.value = true
  try {
    const doc = {
      doctype: 'CRM Lead',
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      mobile_no: form.value.mobile_no,
      email_id: form.value.email,
      company_name: form.value.company,
      source: form.value.source || 'Mobile App',
      lead_owner: getUser().name,
      notes: form.value.notes,
    }

    const result = await call('frappe.client.insert', { doc })
    toast.success(__('Lead berhasil dibuat'))
    router.push({ name: 'Lead', params: { leadId: result.name } })
  } catch (err) {
    error.value = err.messages?.[0] || err.message || __('Gagal membuat lead')
  } finally {
    submitting.value = false
  }
}
</script>
