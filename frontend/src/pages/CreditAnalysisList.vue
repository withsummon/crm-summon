<template>
  <div class="h-full overflow-y-auto bg-slate-50 font-sans">
    <div class="mx-auto max-w-7xl px-6 py-6">
      <div class="mb-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">{{ __('Credit Analysis') }}</h1>
          <p class="mt-1 text-sm text-slate-500">
            {{ __('Credit application register. Click a row to open the analysis workspace.') }}
          </p>
        </div>
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
          <div class="relative w-full sm:w-96">
            <input
              v-model="query"
              type="text"
              :placeholder="__('Search borrower, app ID, facility, ticker')"
              class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm text-slate-700 shadow-sm outline-none transition focus:border-teal-500"
            />
            <FeatherIcon name="search" class="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          </div>
          <Button variant="solid" :label="__('New Credit Application')" @click="openCreateDialog">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
          </Button>
          <Button variant="outline" :loading="applications.loading" :label="__('Refresh')" @click="applications.fetch()" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <SummaryCard :label="__('Applications')" :value="String(rows.length)" icon="file-text" />
        <SummaryCard :label="__('Requested')" :value="formatCurrency(totalRequested)" icon="dollar-sign" />
        <SummaryCard :label="__('In Analysis')" :value="String(statusCount(['Credit Analysis', 'In Progress']))" icon="clock" />
        <SummaryCard :label="__('With PT Tbk')" :value="String(withTicker)" icon="briefcase" />
      </div>

      <div class="mt-5 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <div class="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
          {{ __('Credit Application Register') }}
        </div>
        
        <!-- Desktop Table view -->
        <div class="hidden md:block overflow-x-auto">
          <table class="w-full min-w-[980px] text-sm">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <th class="px-4 py-3 font-bold">{{ __('Application') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Borrower') }}</th>
                <th class="px-4 py-3 text-right font-bold">{{ __('Amount') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Facility') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Status') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Employer / Ticker') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Risk Grade') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in rows"
                :key="row.name"
                class="cursor-pointer border-b border-slate-100 transition hover:bg-teal-50/60"
                @click="openApplication(row)"
              >
                <td class="px-4 py-4">
                  <div class="font-mono font-bold text-slate-800">{{ row.name }}</div>
                  <div class="mt-0.5 text-xs text-slate-500">{{ formatDate(row.modified || row.creation) }}</div>
                </td>
                <td class="px-4 py-4">
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-teal-100 text-sm font-black text-teal-700">
                      {{ initials(row.borrower_name) }}
                    </div>
                    <div class="min-w-0">
                      <div class="truncate font-bold text-slate-800">{{ row.borrower_name || row.borrower || row.name }}</div>
                      <div class="text-xs text-slate-500">{{ row.borrower_type || __('Borrower') }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-4 text-right font-mono text-slate-700">{{ formatCurrency(row.requested_amount) }}</td>
                <td class="px-4 py-4 text-slate-700">{{ row.facility_type || __('Credit Facility') }}</td>
                <td class="px-4 py-4">
                  <Badge :label="row.status || 'Pending Review'" :theme="statusTheme(row.status)" variant="subtle" />
                </td>
                <td class="px-4 py-4">
                  <div class="font-semibold text-slate-700">{{ row.employer_name || '-' }}</div>
                  <Badge v-if="row.public_company_ticker" :label="row.public_company_ticker" theme="teal" variant="subtle" />
                </td>
                <td class="px-4 py-4 font-bold text-slate-800">{{ row.risk_grade || __('Unrated') }}</td>
              </tr>
              <tr v-if="!applications.loading && rows.length === 0">
                <td colspan="7" class="px-4 py-12 text-center text-sm text-slate-400">{{ __('No credit applications found') }}</td>
              </tr>
              <tr v-if="applications.loading">
                <td colspan="7" class="px-4 py-12 text-center text-sm text-slate-400">{{ __('Loading application table...') }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Card List view -->
        <div class="block md:hidden divide-y divide-slate-100">
          <div
            v-for="row in rows"
            :key="row.name"
            class="p-4 active:bg-slate-50 transition cursor-pointer"
            @click="openApplication(row)"
          >
            <div class="flex justify-between items-start mb-2.5">
              <div class="font-mono text-xs font-bold text-slate-500">{{ row.name }}</div>
              <Badge :label="row.status || 'Pending Review'" :theme="statusTheme(row.status)" variant="subtle" size="sm" />
            </div>
            <div class="flex items-center gap-3 mb-2">
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-teal-100 text-xs font-black text-teal-700">
                {{ initials(row.borrower_name) }}
              </div>
              <div class="min-w-0">
                <div class="font-bold text-sm text-slate-800 truncate">{{ row.borrower_name || row.borrower || row.name }}</div>
                <div class="text-xs text-slate-500">{{ row.borrower_type || __('Borrower') }} • {{ row.facility_type || __('Credit Facility') }}</div>
              </div>
            </div>
            <div class="flex justify-between items-center text-xs pt-2 mt-2 border-t border-slate-100">
              <div class="font-mono font-bold text-teal-700 text-sm">{{ formatCurrency(row.requested_amount) }}</div>
              <div class="text-slate-400 font-semibold">{{ row.risk_grade || __('Unrated') }}</div>
            </div>
          </div>
          <div v-if="!applications.loading && rows.length === 0" class="p-8 text-center text-sm text-slate-400">
            {{ __('No credit applications found') }}
          </div>
          <div v-if="applications.loading" class="p-8 text-center text-sm text-slate-400">
            {{ __('Loading application list...') }}
          </div>
        </div>
      </div>
    </div>

    <!-- Create Credit Application Dialog - comprehensive form aligned with 07_CreditAnalysis -->
    <Dialog v-model="showCreateDialog" :options="{ title: __('New Credit Analysis Application'), size: '4xl' }">
      <template #body-content>
        <div class="pt-2">
          <!-- Tab Navigation -->
          <div class="flex gap-1 border-b border-slate-200 mb-5 overflow-x-auto">
            <button
              v-for="tab in createTabs"
              :key="tab.key"
              class="shrink-0 px-4 pb-2 text-sm font-semibold border-b-2 transition-all"
              :class="activeCreateTab === tab.key ? 'border-teal-600 text-teal-700' : 'border-transparent text-slate-500 hover:text-slate-700'"
              @click="activeCreateTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Tab: Borrower Information -->
          <div v-if="activeCreateTab === 'borrower'" class="space-y-4">
            <div class="rounded-lg bg-teal-50 border border-teal-100 px-4 py-3 text-xs text-teal-700">
              {{ __('Basic borrower identification. Required fields: Borrower Name, Borrower Type, Facility Type, Requested Amount.') }}
            </div>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <FieldGroup :label="__('Existing Customer ID')" hint="Optional — link to an existing Customer record">
                <Link v-model="newApp.borrower" doctype="Customer" :placeholder="__('Search customer')" />
              </FieldGroup>
              <FieldGroup :label="__('Borrower Name')" required>
                <input v-model="newApp.borrower_name" class="form-input" :placeholder="__('Full legal name')" />
              </FieldGroup>
              <FieldGroup :label="__('Borrower Type')" required>
                <select v-model="newApp.borrower_type" class="form-input">
                  <option value="Company">{{ __('Company / Badan Usaha') }}</option>
                  <option value="Individual">{{ __('Individual / Perorangan') }}</option>
                </select>
              </FieldGroup>
              <FieldGroup :label="__('Industry / Sektor Usaha')">
                <input v-model="newApp.industry" class="form-input" :placeholder="__('e.g. Financial Services')" />
              </FieldGroup>
              <FieldGroup :label="__('KBLI Code')">
                <input v-model="newApp.kbli" class="form-input" :placeholder="__('e.g. 6419')" />
              </FieldGroup>
              <FieldGroup :label="__('Employer / Affiliation')">
                <input v-model="newApp.employer_name" class="form-input" :placeholder="__('PT ... Tbk')" />
              </FieldGroup>
              <FieldGroup :label="__('PT Tbk Ticker')">
                <input v-model="newApp.public_company_ticker" class="form-input uppercase" :placeholder="__('e.g. BBNI')" />
              </FieldGroup>
              <FieldGroup :label="__('NPWP')">
                <input v-model="newApp.npwp" class="form-input" placeholder="XX.XXX.XXX.X-XXX.XXX" />
              </FieldGroup>
            </div>
            <!-- File Upload for Financial Spread -->
            <div class="mt-6 rounded-lg border border-dashed border-teal-200 bg-teal-50/40 p-4">
              <div class="flex items-center justify-between gap-4">
                <div>
                  <h4 class="font-semibold text-sm text-teal-800">{{ __('Upload Financial Statements (Optional)') }}</h4>
                  <p class="mt-1 text-xs text-teal-600">{{ __('Upload PDF / Excel to auto-fill the financial spread. Data will be imported when the application is created.') }}</p>
                  <div v-if="newApp.spread_file_url" class="mt-2 flex items-center gap-2 text-xs text-teal-700">
                    <FeatherIcon name="check-circle" class="h-4 w-4" />
                    <span>{{ __('File uploaded:') }} {{ newApp.spread_file_name || newApp.spread_file_url }}</span>
                  </div>
                </div>
                <FileUploader
                  :upload-args="{ private: true }"
                  @success="onSpreadFileUploaded"
                >
                  <template #default="{ openFileSelector, uploading }">
                    <Button variant="outline" size="sm" :loading="uploading" :label="newApp.spread_file_url ? __('Replace File') : __('Choose File')" @click="openFileSelector">
                      <template #prefix>
                        <FeatherIcon :name="newApp.spread_file_url ? 'refresh-cw' : 'upload-cloud'" class="h-4 w-4" />
                      </template>
                    </Button>
                  </template>
                </FileUploader>
              </div>
            </div>
          </div>

          <!-- Tab: Facility & Limit -->
          <div v-else-if="activeCreateTab === 'facility'" class="space-y-4">
            <div class="rounded-lg bg-teal-50 border border-teal-100 px-4 py-3 text-xs text-teal-700">
              {{ __('Credit facility structure, limit, tenor, and pricing. This data will be pre-filled in the Financial Spreading worksheet.') }}
            </div>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <FieldGroup :label="__('Facility Type / Jenis Kredit')" required>
                <select v-model="newApp.facility_type" class="form-input">
                  <option value="">{{ __('-- Select --') }}</option>
                  <option value="Working Capital">Working Capital (Modal Kerja)</option>
                  <option value="Working Capital — Revolving">Working Capital — Revolving</option>
                  <option value="Working Capital — Non-Revolving">Working Capital — Non-Revolving</option>
                  <option value="Investment Loan">Investment Loan (Kredit Investasi)</option>
                  <option value="Consumer Loan">Consumer Loan (KPR/KKB)</option>
                  <option value="Trade Finance">Trade Finance (L/C, SKBDN)</option>
                  <option value="Multipurpose">Multipurpose (Multiguna)</option>
                  <option value="Syndicated">Syndicated Loan</option>
                  <option value="Other">Other</option>
                </select>
              </FieldGroup>
              <FieldGroup :label="__('Requested Amount (IDR)')" required>
                <RupiahInput v-model="newApp.requested_amount" :placeholder="__('e.g. 5.000.000.000')" />
                <div v-if="newApp.requested_amount" class="mt-1 text-xs text-teal-700 font-semibold">{{ formatCurrency(newApp.requested_amount) }}</div>
              </FieldGroup>
              <FieldGroup :label="__('Credit Limit (IDR)')">
                <RupiahInput v-model="newApp.credit_limit" />
              </FieldGroup>
              <FieldGroup :label="__('Plafond (IDR)')">
                <RupiahInput v-model="newApp.plafond" />
              </FieldGroup>
              <FieldGroup :label="__('Tenor (months) / Jangka Waktu')">
                <input v-model.number="newApp.tenor_months" type="number" class="form-input" placeholder="12" />
              </FieldGroup>
              <FieldGroup :label="__('Interest Rate (% p.a.)')">
                <input v-model.number="newApp.interest_rate" type="number" step="0.01" class="form-input" placeholder="11.00" />
              </FieldGroup>
              <FieldGroup :label="__('Repayment Scheme')">
                <select v-model="newApp.repayment_scheme" class="form-input">
                  <option value="">{{ __('-- Select --') }}</option>
                  <option value="Annuity">Annuity</option>
                  <option value="Flat">Flat</option>
                  <option value="Bullet">Bullet</option>
                  <option value="Revolving">Revolving Draw-down</option>
                </select>
              </FieldGroup>
              <FieldGroup :label="__('Application Status')">
                <select v-model="newApp.status" class="form-input">
                  <option value="Draft">Draft</option>
                  <option value="Application Received">Application Received</option>
                  <option value="Document Review">Document Review</option>
                  <option value="Credit Analysis">Credit Analysis</option>
                  <option value="Committee Approval">Committee Approval</option>
                </select>
              </FieldGroup>
              <FieldGroup :label="__('Risk Grade (if known)')">
                <input v-model="newApp.risk_grade" class="form-input" placeholder="A / B+ / B / C" />
              </FieldGroup>
              <FieldGroup :label="__('Submission Date')">
                <input v-model="newApp.submission_date" type="date" class="form-input" />
              </FieldGroup>
            </div>
          </div>

          <!-- Tab: Collateral -->
          <div v-else-if="activeCreateTab === 'collateral'" class="space-y-4">
            <div class="rounded-lg bg-amber-50 border border-amber-100 px-4 py-3 text-xs text-amber-700">
              {{ __('Collateral details will be editable after creation in the Collateral tab. Provide a summary here for the initial application.') }}
            </div>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <FieldGroup :label="__('Primary Collateral Type')">
                <select v-model="newApp.collateral_type" class="form-input">
                  <option value="">{{ __('-- Select --') }}</option>
                  <option value="Property">Property / Real Estate</option>
                  <option value="Vehicle">Vehicle / Kendaraan</option>
                  <option value="Inventory">Inventory / Persediaan</option>
                  <option value="Receivables">Receivables / Piutang</option>
                  <option value="Equipment">Equipment / Mesin</option>
                  <option value="Cash Deposit">Cash Deposit / Deposito</option>
                  <option value="Guarantee">Bank Guarantee / Aval</option>
                  <option value="Other">Other</option>
                </select>
              </FieldGroup>
              <FieldGroup :label="__('Collateral Value (IDR)')">
                <RupiahInput v-model="newApp.collateral_value" />
              </FieldGroup>
              <FieldGroup :label="__('LTV % (Loan to Value)')">
                <input v-model.number="newApp.ltv_percent" type="number" step="0.1" class="form-input" placeholder="80" />
              </FieldGroup>
              <FieldGroup :label="__('Coverage Ratio (Collateral/Loan)')">
                <input v-model.number="newApp.coverage_ratio" type="number" step="0.01" class="form-input" placeholder="1.25" />
              </FieldGroup>
            </div>
            <FieldGroup :label="__('Collateral Description')">
              <textarea v-model="newApp.collateral_description" rows="3" class="form-input" :placeholder="__('Describe collateral assets...')" />
            </FieldGroup>
          </div>

          <!-- Tab: Financial Summary -->
          <div v-else-if="activeCreateTab === 'financials'" class="space-y-4">
            <div class="rounded-lg bg-slate-50 border border-slate-200 px-4 py-3 text-xs text-slate-600">
              {{ __('Key financial indicators for initial application. Detailed financial spreading will be input in the analysis workspace after creation.') }}
            </div>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
              <FieldGroup :label="__('Revenue / Penjualan (Latest Year IDR)')">
                <RupiahInput v-model="newApp.revenue" />
              </FieldGroup>
              <FieldGroup :label="__('EBITDA (IDR)')">
                <RupiahInput v-model="newApp.ebitda" />
              </FieldGroup>
              <FieldGroup :label="__('Net Profit / Laba Bersih (IDR)')">
                <RupiahInput v-model="newApp.net_profit" />
              </FieldGroup>
              <FieldGroup :label="__('Total Assets (IDR)')">
                <RupiahInput v-model="newApp.total_assets" />
              </FieldGroup>
              <FieldGroup :label="__('Total Liabilities (IDR)')">
                <RupiahInput v-model="newApp.total_liabilities" />
              </FieldGroup>
              <FieldGroup :label="__('Equity / Modal (IDR)')">
                <RupiahInput v-model="newApp.equity" />
              </FieldGroup>
              <FieldGroup :label="__('Financial Year')">
                <input v-model.number="newApp.financial_year" type="number" class="form-input" :placeholder="String(new Date().getFullYear() - 1)" />
              </FieldGroup>
              <FieldGroup :label="__('Current Ratio')">
                <input v-model.number="newApp.current_ratio" type="number" step="0.01" class="form-input" placeholder="1.50" />
              </FieldGroup>
              <FieldGroup :label="__('Debt to Equity (DER)')">
                <input v-model.number="newApp.der" type="number" step="0.01" class="form-input" placeholder="1.80" />
              </FieldGroup>
            </div>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <FieldGroup :label="__('Auditor')">
                <input v-model="newApp.auditor" class="form-input" :placeholder="__('e.g. KAP Deloitte Indonesia')" />
              </FieldGroup>
              <FieldGroup :label="__('Audit Status')">
                <select v-model="newApp.audit_status" class="form-input">
                  <option value="">{{ __('-- Select --') }}</option>
                  <option value="Audited">Audited</option>
                  <option value="Reviewed">Reviewed (Limited)</option>
                  <option value="Compiled">Compiled (Unaudited)</option>
                  <option value="Management">Management Accounts</option>
                </select>
              </FieldGroup>
            </div>
          </div>

          <!-- Tab: Analyst & Approval -->
          <div v-else-if="activeCreateTab === 'analyst'" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <FieldGroup :label="__('Relationship Manager (RM)')">
                <input v-model="newApp.relationship_manager" class="form-input" :placeholder="__('RM name or user ID')" />
              </FieldGroup>
              <FieldGroup :label="__('Analyst / Credit Officer')">
                <input v-model="newApp.analyst" class="form-input" :placeholder="__('Analyst name or user ID')" />
              </FieldGroup>
              <FieldGroup :label="__('Branch / Unit Kerja')">
                <input v-model="newApp.branch" class="form-input" :placeholder="__('e.g. Jakarta Pusat')" />
              </FieldGroup>
              <FieldGroup :label="__('Segment / Portfolio')">
                <select v-model="newApp.segment" class="form-input">
                  <option value="">{{ __('-- Select --') }}</option>
                  <option value="Corporate">Corporate</option>
                  <option value="Commercial">Commercial (Menengah)</option>
                  <option value="SME">SME (Usaha Kecil)</option>
                  <option value="Micro">Micro</option>
                  <option value="Consumer">Consumer / Retail</option>
                </select>
              </FieldGroup>
              <FieldGroup :label="__('Priority / SLA Level')">
                <select v-model="newApp.priority" class="form-input">
                  <option value="Normal">Normal</option>
                  <option value="High">High</option>
                  <option value="Urgent">Urgent</option>
                </select>
              </FieldGroup>
              <FieldGroup :label="__('Target Decision Date')">
                <input v-model="newApp.target_date" type="date" class="form-input" />
              </FieldGroup>
            </div>
            <FieldGroup :label="__('Internal Notes / Catatan Analisa')">
              <textarea v-model="newApp.internal_notes" rows="4" class="form-input" :placeholder="__('Internal analyst notes, risk observations, conditions...')" />
            </FieldGroup>
          </div>

          <!-- Summary row at bottom -->
          <div class="mt-5 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600">
            <div class="font-semibold mb-2 text-slate-700">{{ __('Application Summary') }}</div>
            <div class="grid grid-cols-2 gap-2 md:grid-cols-4">
              <div>
                <span class="text-slate-500">{{ __('Borrower') }}: </span>
                <span class="font-semibold">{{ newApp.borrower_name || '—' }}</span>
              </div>
              <div>
                <span class="text-slate-500">{{ __('Facility') }}: </span>
                <span class="font-semibold">{{ newApp.facility_type || '—' }}</span>
              </div>
              <div>
                <span class="text-slate-500">{{ __('Amount') }}: </span>
                <span class="font-semibold">{{ newApp.requested_amount ? formatCurrency(newApp.requested_amount) : '—' }}</span>
              </div>
              <div>
                <span class="text-slate-500">{{ __('Status') }}: </span>
                <span class="font-semibold">{{ newApp.status }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-between gap-2 w-full">
          <div class="flex gap-1">
            <button
              v-for="tab in createTabs"
              :key="tab.key"
              class="h-2 w-2 rounded-full transition-all"
              :class="activeCreateTab === tab.key ? 'bg-teal-600 w-4' : 'bg-slate-300'"
              @click="activeCreateTab = tab.key"
            />
          </div>
          <div class="flex gap-2">
            <Button variant="outline" :label="__('Cancel')" @click="showCreateDialog = false" />
            <Button variant="outline" :label="__('← Back')" :disabled="activeCreateTab === createTabs[0].key" @click="prevTab" />
            <Button v-if="activeCreateTab !== createTabs[createTabs.length - 1].key" variant="outline" :label="__('Next →')" @click="nextTab" />
            <Button variant="solid" :label="__('Create & Open Analysis')" :loading="creatingApplication" @click="createApplication">
              <template #prefix><FeatherIcon name="check-circle" class="h-4 w-4" /></template>
            </Button>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Badge, Button, Dialog, FeatherIcon, FileUploader, call, createResource, toast, usePageMeta } from 'frappe-ui'
import { computed, h, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Link from '@/components/Controls/Link.vue'
import RupiahInput from '@/components/Controls/RupiahInput.vue'

const router = useRouter()
const query = ref('')
const showCreateDialog = ref(false)
const creatingApplication = ref(false)
const activeCreateTab = ref('borrower')
let searchTimer = null

const createTabs = [
  { key: 'borrower', label: '① Borrower' },
  { key: 'facility', label: '② Facility & Limit' },
  { key: 'collateral', label: '③ Collateral' },
  { key: 'financials', label: '④ Financial Summary' },
  { key: 'analyst', label: '⑤ Analyst & Approval' },
]

function nextTab() {
  const idx = createTabs.findIndex((t) => t.key === activeCreateTab.value)
  if (idx < createTabs.length - 1) activeCreateTab.value = createTabs[idx + 1].key
}

function prevTab() {
  const idx = createTabs.findIndex((t) => t.key === activeCreateTab.value)
  if (idx > 0) activeCreateTab.value = createTabs[idx - 1].key
}

function openCreateDialog() {
  Object.assign(newApp, defaultApplication())
  activeCreateTab.value = 'borrower'
  showCreateDialog.value = true
}

const applications = createResource({
  url: 'crm.api.credit.get_credit_analysis_table',
  auto: true,
  makeParams() {
    return { query: query.value, limit: 200 }
  },
})

const rows = computed(() => applications.data || [])
const totalRequested = computed(() => rows.value.reduce((sum, row) => sum + Number(row.requested_amount || 0), 0))
const withTicker = computed(() => rows.value.filter((row) => row.public_company_ticker).length)

function openApplication(row) {
  router.push({ name: 'Credit Analysis Detail', params: { applicationId: row.name } })
}

function defaultApplication() {
  return {
    // Borrower tab
    borrower: '',
    borrower_name: '',
    borrower_type: 'Company',
    industry: '',
    kbli: '',
    employer_name: '',
    public_company_ticker: '',
    npwp: '',
    purpose: '',
    // Facility tab
    facility_type: '',
    requested_amount: null,
    credit_limit: null,
    plafond: null,
    tenor_months: null,
    interest_rate: null,
    repayment_scheme: '',
    status: 'Draft',
    risk_grade: '',
    submission_date: '',
    // Collateral tab
    collateral_type: '',
    collateral_value: null,
    ltv_percent: null,
    coverage_ratio: null,
    collateral_description: '',
    // Financial summary tab
    revenue: null,
    ebitda: null,
    net_profit: null,
    total_assets: null,
    total_liabilities: null,
    equity: null,
    financial_year: new Date().getFullYear() - 1,
    current_ratio: null,
    der: null,
    auditor: '',
    audit_status: '',
    spread_file_url: '',
    spread_file_name: '',
    // Analyst tab
    relationship_manager: '',
    analyst: '',
    branch: '',
    segment: '',
    priority: 'Normal',
    target_date: '',
    internal_notes: '',
  }
}

const newApp = reactive(defaultApplication())

function onSpreadFileUploaded(file) {
  if (file?.file_url) {
    newApp.spread_file_url = file.file_url
    newApp.spread_file_name = file.filename || file.file_url.split('/').pop()
  }
}

async function createApplication() {
  if (!newApp.borrower_name && !newApp.borrower) {
    toast.error(__('Borrower name is required'))
    activeCreateTab.value = 'borrower'
    return
  }
  if (!newApp.facility_type) {
    toast.error(__('Facility type is required'))
    activeCreateTab.value = 'facility'
    return
  }
  if (!newApp.requested_amount || newApp.requested_amount <= 0) {
    toast.error(__('Requested amount must be greater than zero'))
    activeCreateTab.value = 'facility'
    return
  }

  creatingApplication.value = true
  try {
    const payload = {
      ...newApp,
      public_company_ticker: (newApp.public_company_ticker || '').toUpperCase()
    }

    const row = await call('crm.api.credit.create_credit_application', { payload })
    toast.success(__('Credit application created'))

    // If a spread file was uploaded, import it immediately
    if (newApp.spread_file_url) {
      try {
        const importResult = await call('crm.api.credit_analysis.import_statement_file', {
          application_id: row.name,
          file_url: newApp.spread_file_url,
        })
        toast.success(__('Financial spread imported: {0} rows', [importResult.row_count || 0]))
      } catch (importError) {
        toast.error(importError?.messages?.[0] || importError.message || __('Credit application was created, but the spread file import failed'))
      }
    }

    showCreateDialog.value = false
    await applications.fetch()
    router.push({ name: 'Credit Analysis Detail', params: { applicationId: row.name } })
  } catch (error) {
    toast.error(error?.messages?.[0] || error.message || __('Could not create credit application'))
  } finally {
    creatingApplication.value = false
  }
}

function statusCount(status) {
  const statuses = Array.isArray(status) ? status : [status]
  return rows.value.filter((row) => statuses.includes(row.status)).length
}

function statusTheme(status) {
  if (status === 'Approved') return 'green'
  if (status === 'Rejected') return 'red'
  if (status === 'Pending Review') return 'orange'
  return 'teal'
}

function initials(value) {
  return String(value || 'CA').slice(0, 2).toUpperCase()
}

function formatCurrency(value) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(Number(value || 0))
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('id-ID', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value))
}

watch(query, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => applications.fetch(), 250)
})

usePageMeta(() => ({ title: 'Credit Analysis' }))

const SummaryCard = {
  props: ['label', 'value', 'icon'],
  setup(props) {
    return () => h('div', { class: 'rounded-lg border border-slate-200 bg-white p-4 shadow-sm' }, [
      h('div', { class: 'flex items-center justify-between gap-3' }, [
        h('div', { class: 'text-xs font-bold uppercase tracking-wide text-slate-500' }, props.label),
        h('div', { class: 'flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50 text-teal-600' }, [
          h(FeatherIcon, { name: props.icon, class: 'h-4 w-4' }),
        ]),
      ]),
      h('div', { class: 'mt-3 text-2xl font-black text-slate-900' }, props.value),
    ])
  },
}

// Form helper components (inline)
const FieldGroup = {
  props: ['label', 'hint', 'required'],
  setup(props, { slots }) {
    return () => h('label', { class: 'flex flex-col gap-1' }, [
      h('span', { class: 'text-xs font-semibold text-slate-600' }, [
        props.label,
        props.required ? h('span', { class: 'ml-0.5 text-red-500' }, '*') : null,
      ]),
      slots.default?.(),
      props.hint ? h('span', { class: 'text-[11px] text-slate-400' }, props.hint) : null,
    ])
  },
}
</script>

<style scoped>
.form-input {
  height: 2.5rem;
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  padding-left: 0.75rem;
  padding-right: 0.75rem;
  font-size: 0.875rem;
  outline: none;
  background-color: white;
  transition: border-color 0.15s ease-in-out;
}
.form-input:focus {
  border-color: #0d9488;
}
select.form-input {
  cursor: pointer;
}
textarea.form-input {
  height: auto;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  resize: vertical;
}
</style>
