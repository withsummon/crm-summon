<template>
  <Dialog
    v-model="showDialog"
    :options="{
      title: __('Import Leads from Excel'),
      size: 'xl',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <!-- Step 1: Upload -->
        <div v-if="step === 'upload'" class="flex flex-col items-center gap-4 py-8">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-100">
            <FeatherIcon name="upload-cloud" class="h-8 w-8 text-gray-600" />
          </div>
          <div class="text-center">
            <h3 class="text-lg font-semibold text-ink-gray-9">
              {{ __('Upload Excel File') }}
            </h3>
            <p class="mt-1 text-sm text-ink-gray-5">
              {{ __('Upload a .xlsx file with lead data. Expected columns: Company, Name, Email, Phone, Position, Industry, Status') }}
            </p>
          </div>
          <FileUploader
            :upload-args="{ private: true }"
            @success="onFileUploaded"
          >
            <template #default="{ openFileSelector }">
              <Button
                variant="solid"
                size="md"
                :label="__('Select Excel File')"
                @click="openFileSelector"
              >
                <template #prefix>
                  <FeatherIcon name="file-plus" class="h-4 w-4" />
                </template>
              </Button>
            </template>
          </FileUploader>
        </div>

        <!-- Step 2: Preview -->
        <div v-else-if="step === 'preview'" class="flex flex-col gap-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-base font-semibold text-ink-gray-9">
                {{ __('Preview Import Data') }}
              </h3>
              <p class="text-sm text-ink-gray-5">
                {{ __('Found {0} rows in the file. Showing first 10 rows.', [previewData.total_rows]) }}
              </p>
            </div>
            <Badge :label="fileName" variant="subtle" theme="gray" />
          </div>

          <!-- Preview Table -->
          <div class="max-h-[400px] overflow-auto rounded-lg border">
            <table class="w-full text-sm">
              <thead class="sticky top-0 bg-surface-gray-2">
                <tr>
                  <th
                    v-for="(header, idx) in previewData.headers"
                    :key="idx"
                    class="whitespace-nowrap px-3 py-2 text-left text-xs font-medium text-ink-gray-5"
                  >
                    {{ header }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, rowIdx) in previewData.rows"
                  :key="rowIdx"
                  class="border-t"
                >
                  <td
                    v-for="(cell, cellIdx) in row"
                    :key="cellIdx"
                    class="whitespace-nowrap px-3 py-2 text-ink-gray-8"
                  >
                    {{ cell || '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Step 3: Importing -->
        <div v-else-if="step === 'importing'" class="flex flex-col items-center gap-4 py-8">
          <LoadingIndicator class="h-8 w-8 text-gray-600" />
          <div class="text-center">
            <h3 class="text-lg font-semibold text-ink-gray-9">
              {{ __('Importing Leads...') }}
            </h3>
            <p class="mt-1 text-sm text-ink-gray-5">
              {{ __('Please wait while we process your data.') }}
            </p>
          </div>
        </div>

        <!-- Step 4: Results -->
        <div v-else-if="step === 'results'" class="flex flex-col gap-4 py-4">
          <div class="flex items-center gap-3">
            <div
              class="flex h-12 w-12 items-center justify-center rounded-xl"
              :class="importResult.errors.length ? 'bg-amber-100' : 'bg-green-100'"
            >
              <FeatherIcon
                :name="importResult.errors.length ? 'alert-triangle' : 'check-circle'"
                class="h-6 w-6"
                :class="importResult.errors.length ? 'text-amber-600' : 'text-green-600'"
              />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-ink-gray-9">
                {{ __('Import Complete') }}
              </h3>
              <p class="text-sm text-ink-gray-5">
                {{ __('Processed {0} rows', [importResult.total]) }}
              </p>
            </div>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-3 gap-3">
            <div class="rounded-lg border bg-green-50 p-3 text-center">
              <div class="text-2xl font-bold text-green-700">{{ importResult.created }}</div>
              <div class="text-xs text-green-600">{{ __('Created') }}</div>
            </div>
            <div class="rounded-lg border bg-surface-gray-2 p-3 text-center">
              <div class="text-2xl font-bold text-ink-gray-7">{{ importResult.skipped }}</div>
              <div class="text-xs text-ink-gray-5">{{ __('Skipped (duplicates)') }}</div>
            </div>
            <div class="rounded-lg border bg-red-50 p-3 text-center">
              <div class="text-2xl font-bold text-red-700">{{ importResult.errors.length }}</div>
              <div class="text-xs text-red-600">{{ __('Errors') }}</div>
            </div>
          </div>

          <!-- Error details -->
          <div
            v-if="importResult.errors.length"
            class="max-h-[200px] overflow-auto rounded-lg border bg-red-50 p-3"
          >
            <p class="mb-2 text-xs font-medium text-red-700">{{ __('Errors:') }}</p>
            <div
              v-for="(err, idx) in importResult.errors"
              :key="idx"
              class="text-xs text-red-600"
            >
              Row {{ err.row }}: {{ err.error }}
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex items-center justify-end gap-2">
        <Button
          v-if="step === 'preview'"
          variant="subtle"
          :label="__('Back')"
          @click="step = 'upload'"
        />
        <Button
          v-if="step === 'preview'"
          variant="solid"
          :label="__('Import {0} Leads', [previewData.total_rows])"
          @click="doImport"
        >
          <template #prefix>
            <FeatherIcon name="download" class="h-4 w-4" />
          </template>
        </Button>
        <Button
          v-if="step === 'results'"
          variant="solid"
          :label="__('Done')"
          @click="onDone"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import {
  Dialog,
  Button,
  Badge,
  LoadingIndicator,
  FileUploader,
  FeatherIcon,
  call,
  toast,
} from 'frappe-ui'

const showDialog = defineModel()
const emit = defineEmits(['imported'])

const step = ref('upload') // upload, preview, importing, results
const fileUrl = ref('')
const fileName = ref('')
const previewData = ref({ headers: [], rows: [], total_rows: 0 })
const importResult = ref({ created: 0, skipped: 0, errors: [], total: 0 })

async function onFileUploaded(file) {
  if (!file || !file.file_url) {
    toast.error(__('File upload failed. Please try again.'))
    return
  }
  fileUrl.value = file.file_url
  fileName.value = file.file_name

  // Get preview
  try {
    const result = await call('crm.api.lead_gen.get_excel_preview', {
      file_url: file.file_url,
    })
    previewData.value = result
    step.value = 'preview'
  } catch (e) {
    console.error('Preview error:', e)
    toast.error(__('Failed to preview file: {0}', [e.message || 'Unknown error']))
  }
}

async function doImport() {
  step.value = 'importing'
  try {
    const result = await call('crm.api.lead_gen.import_leads_from_excel', {
      file_url: fileUrl.value,
    })
    importResult.value = result
    step.value = 'results'
  } catch (e) {
    console.error('Import error:', e)
    importResult.value = {
      created: 0,
      skipped: 0,
      errors: [{ row: 0, error: e.message || 'Unknown error' }],
      total: 0,
    }
    step.value = 'results'
  }
}

function onDone() {
  showDialog.value = false
  step.value = 'upload'
  if (importResult.value.created > 0) {
    emit('imported')
  }
}
</script>
