<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div class="min-w-0">
            <div class="flex items-center gap-2 text-base">
              <button class="text-ink-gray-5 hover:text-ink-gray-9" @click="navigate('catalog')">
                {{ __('Product Configuration') }}
              </button>
              <template v-if="activeView === 'detail' && draft">
                <span class="text-ink-gray-3">/</span>
                <span class="font-medium text-ink-gray-9 truncate">
                  {{ draft.product_code || __('New Product') }}
                </span>
              </template>
            </div>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-1.5 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-2.5 py-1.5">
          <FeatherIcon name="user" class="h-3.5 w-3.5 text-ink-gray-5" />
          <span class="text-sm font-medium text-ink-gray-8">{{ currentUser }}</span>
        </div>
      </template>
    </LayoutHeader>

    <!-- Tab strip -->
    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-5">
      <div class="flex items-center justify-between gap-4">
        <div class="flex gap-5 overflow-x-auto">
          <button
            v-for="tab in TABS"
            :key="tab.view"
            class="border-b-2 py-2.5 text-base transition-colors whitespace-nowrap"
            :class="isActiveTab(tab.view)
              ? 'border-ink-gray-8 font-medium text-ink-gray-9'
              : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
            @click="navigate(tab.view)"
          >
            {{ tab.label }}
          </button>
        </div>
        <div class="flex shrink-0 items-center gap-2 py-1.5">
          <Button
            v-if="activeView === 'catalog'"
            variant="outline"
            size="sm"
            label="Export CSV"
            @click="exportCsv"
          >
            <template #prefix><FeatherIcon name="download" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'catalog'"
            variant="solid"
            size="sm"
            label="New Product"
            @click="openWizard(null)"
          >
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'detail' && draft"
            variant="outline"
            size="sm"
            label="Back"
            @click="navigate('catalog')"
          >
            <template #prefix><FeatherIcon name="arrow-left" class="h-4 w-4" /></template>
          </Button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto bg-surface-gray-1">
      <div class="max-w-6xl px-5 py-5">

        <!-- ── CATALOG ──────────────────────────────────────── -->
        <template v-if="activeView === 'catalog'">
          <!-- KPI strip -->
          <div class="mb-4 grid gap-3 md:grid-cols-5">
            <KpiCard :label="__('All Products')" :value="catalog?.counts?.total ?? 0" icon="package" />
            <KpiCard :label="__('Active')" :value="catalog?.counts?.active ?? 0" icon="check-circle" theme="teal" />
            <KpiCard :label="__('Draft')" :value="catalog?.counts?.draft ?? 0" icon="edit-3" />
            <KpiCard :label="__('Pending')" :value="catalog?.counts?.pending ?? 0" icon="clock" theme="orange" />
            <KpiCard :label="__('Retired')" :value="catalog?.counts?.retired ?? 0" icon="archive" />
          </div>

          <!-- Filter strip -->
          <div class="mb-3 flex flex-wrap items-center gap-2">
            <div class="flex flex-1 min-w-[200px] items-center gap-2 rounded-md border border-outline-gray-2 bg-white px-3 py-1.5">
              <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-4" />
              <input
                v-model="filters.search"
                type="text"
                :placeholder="__('Search code, name, tagline…')"
                class="flex-1 bg-transparent text-sm outline-none"
                @input="debouncedLoad"
              />
            </div>
            <select v-model="filters.status" class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8" @change="loadCatalog">
              <option value="">{{ __('All statuses') }}</option>
              <option value="Draft">Draft</option>
              <option value="Pending Approval">Pending Approval</option>
              <option value="Active">Active</option>
              <option value="Retired">Retired</option>
            </select>
            <select v-model="filters.product_type" class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8" @change="loadCatalog">
              <option value="">{{ __('All types') }}</option>
              <option v-for="t in TYPES" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>

          <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm">
            <div v-if="catalogLoading" class="flex h-40 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else-if="!catalog?.rows?.length" class="flex flex-col items-center justify-center px-6 py-16 text-center">
              <FeatherIcon name="package" class="mb-3 h-8 w-8 text-ink-gray-3" />
              <p class="text-base font-medium text-ink-gray-8">{{ __('No products yet') }}</p>
              <p class="mt-1 text-sm text-ink-gray-5">{{ __('Create your first loan product to start.') }}</p>
              <Button class="mt-4" variant="solid" size="sm" label="New Product" @click="openWizard(null)">
                <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
              </Button>
            </div>
            <table v-else class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-4 py-2.5">{{ __('Code') }}</th>
                  <th class="px-4 py-2.5">{{ __('Name') }}</th>
                  <th class="px-4 py-2.5">{{ __('Type') }}</th>
                  <th class="px-4 py-2.5">{{ __('Status') }}</th>
                  <th class="px-4 py-2.5">{{ __('Amount Range') }}</th>
                  <th class="px-4 py-2.5">{{ __('Tenor') }}</th>
                  <th class="px-4 py-2.5">{{ __('Updated') }}</th>
                  <th class="px-4 py-2.5"></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in catalog.rows"
                  :key="p.name"
                  class="border-b border-outline-gray-1 last:border-b-0 hover:bg-surface-gray-1 cursor-pointer"
                  @click="openWizard(p.product_code)"
                >
                  <td class="px-4 py-2.5 font-medium text-ink-gray-9">{{ p.product_code }}</td>
                  <td class="px-4 py-2.5 text-ink-gray-8">{{ p.product_name }}</td>
                  <td class="px-4 py-2.5 text-ink-gray-7">{{ p.product_type || '—' }}</td>
                  <td class="px-4 py-2.5">
                    <StatusPill :status="p.status" />
                  </td>
                  <td class="px-4 py-2.5 text-ink-gray-7">{{ fmtRange(p.min_amount, p.max_amount, p.currency) }}</td>
                  <td class="px-4 py-2.5 text-ink-gray-7">{{ fmtTenor(p.min_tenor_months, p.max_tenor_months) }}</td>
                  <td class="px-4 py-2.5 text-xs text-ink-gray-5">{{ fmtDate(p.modified) }}</td>
                  <td class="px-4 py-2.5 text-right">
                    <div class="flex justify-end gap-1">
                      <Button size="sm" variant="ghost" @click.stop="cloneProductPrompt(p)">
                        <FeatherIcon name="copy" class="h-4 w-4 text-ink-gray-5" />
                      </Button>
                      <Button v-if="p.status !== 'Retired'" size="sm" variant="ghost" @click.stop="retirePrompt(p)">
                        <FeatherIcon name="archive" class="h-4 w-4 text-ink-gray-5" />
                      </Button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- ── DETAIL / WIZARD ─────────────────────────────── -->
        <template v-else-if="activeView === 'detail' && draft">
          <div class="grid gap-4 md:grid-cols-[220px_1fr]">
            <!-- Step nav -->
            <aside class="rounded-[14px] border border-outline-gray-2 bg-white p-3 shadow-sm h-fit">
              <button
                v-for="(s, i) in STEPS"
                :key="s.key"
                class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm transition-colors"
                :class="step === i ? 'bg-surface-gray-2 font-medium text-ink-gray-9' : 'text-ink-gray-6 hover:bg-surface-gray-1'"
                @click="step = i"
              >
                <span
                  class="flex h-5 w-5 items-center justify-center rounded-full text-[11px] font-semibold"
                  :class="step >= i ? 'text-white' : 'bg-surface-gray-2 text-ink-gray-5'"
                  :style="step >= i ? 'background:#008C95' : ''"
                >{{ i + 1 }}</span>
                {{ s.label }}
              </button>
              <div class="mt-3 border-t border-outline-gray-1 pt-3 flex flex-col gap-2">
                <Button size="sm" variant="outline" label="Save Draft" :loading="saving" @click="saveDraft" />
                <Button
                  v-if="draft.status === 'Draft'"
                  size="sm"
                  variant="solid"
                  label="Submit for Approval"
                  @click="submitForReview"
                />
                <Button
                  v-else-if="draft.status === 'Pending Approval'"
                  size="sm"
                  variant="solid"
                  label="Approve & Publish"
                  @click="approveProduct"
                />
                <span v-else class="text-center text-xs text-ink-gray-5">
                  {{ __('Status: ') }}<StatusPill :status="draft.status" />
                </span>
              </div>
            </aside>

            <!-- Step content -->
            <section class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
              <div class="mb-4 flex items-center justify-between">
                <div>
                  <h2 class="text-base font-semibold text-ink-gray-9">{{ STEPS[step].label }}</h2>
                  <p class="mt-0.5 text-xs text-ink-gray-5">{{ STEPS[step].hint }}</p>
                </div>
                <div class="flex gap-2">
                  <Button v-if="step > 0" size="sm" variant="outline" label="Back" @click="step--" />
                  <Button v-if="step < STEPS.length - 1" size="sm" variant="solid" label="Next" @click="step++" />
                </div>
              </div>

              <!-- Step 1: Basics -->
              <div v-if="step === 0" class="grid gap-4 md:grid-cols-2">
                <Field label="Product Code" required>
                  <input v-model="draft.product_code" class="field-input" :disabled="!!draft._existing" />
                </Field>
                <Field label="Product Name">
                  <input v-model="draft.product_name" class="field-input" />
                </Field>
                <Field label="Product Type">
                  <select v-model="draft.product_type" class="field-input">
                    <option v-for="t in TYPES" :key="t" :value="t">{{ t }}</option>
                  </select>
                </Field>
                <Field label="Currency">
                  <input v-model="draft.currency" class="field-input" placeholder="IDR" />
                </Field>
                <Field label="Marketing Tagline" class="md:col-span-2">
                  <input v-model="draft.marketing_tagline" class="field-input" />
                </Field>
                <Field label="Description" class="md:col-span-2">
                  <textarea v-model="draft.description" rows="3" class="field-input" />
                </Field>
              </div>

              <!-- Step 2: Pricing -->
              <div v-else-if="step === 1" class="space-y-4">
                <div class="grid gap-4 md:grid-cols-3">
                  <Field label="Min Amount">
                    <input v-model.number="draft.min_amount" type="number" class="field-input" />
                  </Field>
                  <Field label="Max Amount">
                    <input v-model.number="draft.max_amount" type="number" class="field-input" />
                  </Field>
                  <Field label="Standard Rate %">
                    <input v-model.number="draft.standard_rate" type="number" step="0.01" class="field-input" />
                  </Field>
                  <Field label="Min Tenor (months)">
                    <input v-model.number="draft.min_tenor_months" type="number" class="field-input" />
                  </Field>
                  <Field label="Max Tenor (months)">
                    <input v-model.number="draft.max_tenor_months" type="number" class="field-input" />
                  </Field>
                  <Field label="Tenor Increment">
                    <input v-model.number="draft.tenor_increment_months" type="number" class="field-input" />
                  </Field>
                  <Field label="Repayment Frequency">
                    <select v-model="draft.repayment_frequency" class="field-input">
                      <option>Monthly</option><option>Bi-weekly</option><option>Quarterly</option><option>Custom</option>
                    </select>
                  </Field>
                  <Field label="Grace Period (days)">
                    <input v-model.number="draft.grace_period_days" type="number" class="field-input" />
                  </Field>
                </div>

                <ChildTable
                  title="Interest Tiers"
                  :rows="draft.interest_tiers"
                  :columns="[
                    { key: 'tenor_from', label: 'Tenor From', type: 'number' },
                    { key: 'tenor_to', label: 'Tenor To', type: 'number' },
                    { key: 'segment', label: 'Segment', type: 'text' },
                    { key: 'rate_type', label: 'Type', type: 'select', options: ['Flat', 'Effective', 'Annuity', 'Reducing'] },
                    { key: 'rate_pct', label: 'Rate %', type: 'number' },
                    { key: 'risk_premium_pct', label: 'Risk +%', type: 'number' },
                  ]"
                  @add="draft.interest_tiers.push({ rate_type: 'Effective' })"
                  @remove="(i) => draft.interest_tiers.splice(i, 1)"
                />

                <ChildTable
                  title="Fees"
                  :rows="draft.fees"
                  :columns="[
                    { key: 'fee_type', label: 'Type', type: 'select', options: ['Admin', 'Provision', 'Late', 'Prepay', 'Other'] },
                    { key: 'calc_mode', label: 'Mode', type: 'select', options: ['Fixed', 'Percent'] },
                    { key: 'value', label: 'Value', type: 'number' },
                    { key: 'min_cap', label: 'Min Cap', type: 'number' },
                    { key: 'max_cap', label: 'Max Cap', type: 'number' },
                    { key: 'trigger_event', label: 'Trigger', type: 'select', options: ['Origination', 'Disbursement', 'Repayment', 'Prepayment', 'Default'] },
                  ]"
                  @add="draft.fees.push({ fee_type: 'Admin', calc_mode: 'Fixed', trigger_event: 'Origination' })"
                  @remove="(i) => draft.fees.splice(i, 1)"
                />
              </div>

              <!-- Step 3: Eligibility -->
              <div v-else-if="step === 2" class="space-y-4">
                <ChildTable
                  title="Eligibility Rules"
                  :rows="draft.eligibility_rules"
                  :columns="[
                    { key: 'criterion', label: 'Criterion', type: 'select', options: ['Min Age','Min Income','Min Vintage Years','Min Credit Score','Industry Whitelist','Industry Blacklist','Geography Whitelist','Geography Blacklist'] },
                    { key: 'operator', label: 'Op', type: 'select', options: ['>=', '<=', '=', 'in', 'not in'] },
                    { key: 'value', label: 'Value', type: 'text' },
                    { key: 'notes', label: 'Notes', type: 'text' },
                  ]"
                  @add="draft.eligibility_rules.push({ criterion: 'Min Age', operator: '>=' })"
                  @remove="(i) => draft.eligibility_rules.splice(i, 1)"
                />
              </div>

              <!-- Step 4: Workflow -->
              <div v-else-if="step === 3" class="space-y-4">
                <div class="grid gap-4 md:grid-cols-2">
                  <Field label="Workflow">
                    <input v-model="draft.workflow" class="field-input" placeholder="e.g. LOS Standard" />
                  </Field>
                  <Field label="Form Template">
                    <input v-model="draft.form_template" class="field-input" placeholder="e.g. KMK Application v3" />
                  </Field>
                </div>
                <ChildTable
                  title="Approval Matrix"
                  :rows="draft.approval_tiers"
                  :columns="[
                    { key: 'amount_from', label: 'Amount From', type: 'number' },
                    { key: 'amount_to', label: 'Amount To', type: 'number' },
                    { key: 'approver_role', label: 'Approver Role', type: 'text' },
                    { key: 'sequence', label: 'Seq', type: 'number' },
                    { key: 'parallel', label: 'Parallel', type: 'checkbox' },
                  ]"
                  @add="draft.approval_tiers.push({ sequence: (draft.approval_tiers.length + 1) })"
                  @remove="(i) => draft.approval_tiers.splice(i, 1)"
                />
              </div>

              <!-- Step 5: Documents -->
              <div v-else-if="step === 4" class="space-y-4">
                <ChildTable
                  title="Required Documents"
                  :rows="draft.document_requirements"
                  :columns="[
                    { key: 'document_type', label: 'Document', type: 'text' },
                    { key: 'mandatory', label: 'Mandatory', type: 'checkbox' },
                    { key: 'segment', label: 'Segment', type: 'text' },
                    { key: 'expiry_months', label: 'Expiry (m)', type: 'number' },
                  ]"
                  @add="draft.document_requirements.push({ mandatory: 1 })"
                  @remove="(i) => draft.document_requirements.splice(i, 1)"
                />
                <div class="rounded-md border border-outline-gray-2 bg-surface-gray-1 p-4">
                  <h3 class="text-sm font-semibold text-ink-gray-9 mb-2">{{ __('Preview') }}</h3>
                  <div class="grid gap-2 text-xs text-ink-gray-7 md:grid-cols-2">
                    <div><span class="text-ink-gray-5">{{ __('Code') }}:</span> {{ draft.product_code || '—' }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Name') }}:</span> {{ draft.product_name || '—' }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Type') }}:</span> {{ draft.product_type || '—' }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Status') }}:</span> {{ draft.status || 'Draft' }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Amount') }}:</span> {{ fmtRange(draft.min_amount, draft.max_amount, draft.currency) }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Tenor') }}:</span> {{ fmtTenor(draft.min_tenor_months, draft.max_tenor_months) }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Tiers') }}:</span> {{ (draft.interest_tiers || []).length }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Fees') }}:</span> {{ (draft.fees || []).length }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Eligibility Rules') }}:</span> {{ (draft.eligibility_rules || []).length }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Required Docs') }}:</span> {{ (draft.document_requirements || []).length }}</div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </template>

        <!-- ── CALCULATOR ──────────────────────────────────── -->
        <template v-else-if="activeView === 'calculator'">
          <div class="grid gap-4 md:grid-cols-[1fr_1fr]">
            <section class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
              <h2 class="text-base font-semibold text-ink-gray-9 mb-3">{{ __('Quote Inputs') }}</h2>
              <div class="grid gap-3">
                <Field label="Product">
                  <select v-model="quote.product_code" class="field-input" @change="quoteResult = null">
                    <option value="">{{ __('Select a product…') }}</option>
                    <option v-for="p in catalog?.rows || []" :key="p.name" :value="p.product_code">
                      {{ p.product_code }} — {{ p.product_name }}
                    </option>
                  </select>
                </Field>
                <Field label="Amount">
                  <input v-model.number="quote.amount" type="number" class="field-input" />
                </Field>
                <Field label="Tenor (months)">
                  <input v-model.number="quote.tenor" type="number" class="field-input" />
                </Field>
                <Field label="Segment (optional)">
                  <input v-model="quote.segment" class="field-input" placeholder="e.g. SME, Corporate" />
                </Field>
                <Button variant="solid" size="sm" label="Calculate" :loading="quoteLoading" @click="runQuote" />
              </div>
            </section>
            <section class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
              <h2 class="text-base font-semibold text-ink-gray-9 mb-3">{{ __('Result') }}</h2>
              <div v-if="!quoteResult" class="flex h-40 items-center justify-center text-sm text-ink-gray-5">
                {{ __('Enter inputs and click Calculate.') }}
              </div>
              <div v-else class="space-y-3">
                <div class="grid grid-cols-2 gap-3">
                  <Metric :label="__('Rate')" :value="`${quoteResult.rate_pct.toFixed(2)}%`" :sub="quoteResult.rate_type" />
                  <Metric :label="__('APR')" :value="`${quoteResult.apr.toFixed(2)}%`" />
                  <Metric :label="__('EMI')" :value="fmtMoney(quoteResult.emi, quoteResult.currency)" />
                  <Metric :label="__('Total Payable')" :value="fmtMoney(quoteResult.total_payable, quoteResult.currency)" />
                  <Metric :label="__('Total Interest')" :value="fmtMoney(quoteResult.total_interest, quoteResult.currency)" />
                  <Metric :label="__('Total Fees')" :value="fmtMoney(quoteResult.total_fees, quoteResult.currency)" />
                </div>
                <div v-if="quoteResult.fees?.length" class="rounded-md border border-outline-gray-2 bg-surface-gray-1 p-3">
                  <h3 class="text-xs font-semibold uppercase tracking-wide text-ink-gray-5 mb-2">{{ __('Fee Breakdown') }}</h3>
                  <table class="w-full text-xs">
                    <tbody>
                      <tr v-for="(f, i) in quoteResult.fees" :key="i" class="border-t border-outline-gray-1 first:border-t-0">
                        <td class="py-1.5 text-ink-gray-7">{{ f.fee_type }}</td>
                        <td class="py-1.5 text-ink-gray-5">{{ f.trigger_event }}</td>
                        <td class="py-1.5 text-right text-ink-gray-8">{{ fmtMoney(f.charge, quoteResult.currency) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </section>
          </div>
        </template>

        <!-- ── ANALYTICS ────────────────────────────────────── -->
        <template v-else-if="activeView === 'analytics'">
          <div v-if="analyticsLoading" class="flex h-40 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>
          <div v-else-if="analytics" class="space-y-4">
            <div class="grid gap-3 md:grid-cols-5">
              <KpiCard :label="__('Total Products')" :value="analytics.totals.products" icon="package" />
              <KpiCard :label="__('Active')" :value="analytics.totals.active" icon="check-circle" theme="teal" />
              <KpiCard :label="__('Pending')" :value="analytics.totals.pending" icon="clock" theme="orange" />
              <KpiCard :label="__('Retired')" :value="analytics.totals.retired" icon="archive" />
              <KpiCard :label="__('Applications')" :value="analytics.totals.applications" icon="file-text" theme="blue" />
            </div>
            <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm overflow-hidden">
              <table class="w-full text-sm">
                <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                  <tr>
                    <th class="px-4 py-2.5">{{ __('Product') }}</th>
                    <th class="px-4 py-2.5">{{ __('Status') }}</th>
                    <th class="px-4 py-2.5 text-right">{{ __('Applications') }}</th>
                    <th class="px-4 py-2.5 text-right">{{ __('Approvals') }}</th>
                    <th class="px-4 py-2.5 text-right">{{ __('Disbursed') }}</th>
                    <th class="px-4 py-2.5 text-right">{{ __('Avg Ticket') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in analytics.per_product" :key="p.name" class="border-b border-outline-gray-1 last:border-b-0">
                    <td class="px-4 py-2.5">
                      <div class="font-medium text-ink-gray-9">{{ p.product_code }}</div>
                      <div class="text-xs text-ink-gray-5">{{ p.product_name }}</div>
                    </td>
                    <td class="px-4 py-2.5"><StatusPill :status="p.status" /></td>
                    <td class="px-4 py-2.5 text-right text-ink-gray-8">{{ p.applications }}</td>
                    <td class="px-4 py-2.5 text-right text-ink-gray-8">{{ p.approvals }}</td>
                    <td class="px-4 py-2.5 text-right text-ink-gray-8">{{ p.disbursements }}</td>
                    <td class="px-4 py-2.5 text-right text-ink-gray-7">{{ fmtMoney(p.avg_ticket, 'IDR') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>

        <!-- ── APPROVALS ────────────────────────────────────── -->
        <template v-else-if="activeView === 'approvals'">
          <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm">
            <div v-if="approvalsLoading" class="flex h-40 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else-if="!pendingApprovals.length" class="flex flex-col items-center justify-center px-6 py-16 text-center">
              <FeatherIcon name="check-circle" class="mb-3 h-8 w-8 text-ink-gray-3" />
              <p class="text-base font-medium text-ink-gray-8">{{ __('No pending approvals') }}</p>
              <p class="mt-1 text-sm text-ink-gray-5">{{ __('Product change requests will appear here.') }}</p>
            </div>
            <table v-else class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-4 py-2.5">{{ __('Product') }}</th>
                  <th class="px-4 py-2.5">{{ __('Type') }}</th>
                  <th class="px-4 py-2.5">{{ __('Submitted By') }}</th>
                  <th class="px-4 py-2.5">{{ __('Submitted') }}</th>
                  <th class="px-4 py-2.5"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in pendingApprovals" :key="p.name" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-4 py-2.5">
                    <div class="font-medium text-ink-gray-9">{{ p.product_code }}</div>
                    <div class="text-xs text-ink-gray-5">{{ p.product_name }}</div>
                  </td>
                  <td class="px-4 py-2.5 text-ink-gray-7">{{ p.product_type }}</td>
                  <td class="px-4 py-2.5 text-ink-gray-7">{{ p.owner }}</td>
                  <td class="px-4 py-2.5 text-xs text-ink-gray-5">{{ fmtDate(p.modified) }}</td>
                  <td class="px-4 py-2.5 text-right">
                    <div class="flex justify-end gap-2">
                      <Button size="sm" variant="outline" label="Open" @click="openWizard(p.product_code)" />
                      <Button size="sm" variant="solid" label="Approve" @click="approveByCode(p.product_code)" />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, h, onMounted, ref, defineComponent } from 'vue'
import { Button, FeatherIcon, LoadingIndicator, call as _frappeCall, toast } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

const call = (method, args = {}) => _frappeCall(method, args)

const notify = {
  ok: (msg) => (toast.success ? toast.success(msg) : toast(msg)),
  err: (msg) => (toast.error ? toast.error(msg) : toast(msg)),
  warn: (msg) => (toast.warning ? toast.warning(msg) : (toast.info ? toast.info(msg) : toast(msg))),
}

const TABS = [
  { view: 'catalog', label: 'Catalog' },
  { view: 'calculator', label: 'Pricing Calculator' },
  { view: 'analytics', label: 'Analytics' },
  { view: 'approvals', label: 'Approvals' },
]

const TYPES = ['Working Capital', 'Investment', 'Consumer', 'Mortgage', 'Other']

const STEPS = [
  { key: 'basics', label: 'Basics', hint: 'Code, name, type, and description.' },
  { key: 'pricing', label: 'Pricing', hint: 'Amount/tenor limits, interest tiers, fees.' },
  { key: 'eligibility', label: 'Eligibility', hint: 'Who can apply for this product.' },
  { key: 'workflow', label: 'Workflow', hint: 'Workflow, form template, approval matrix.' },
  { key: 'documents', label: 'Documents', hint: 'Required documents and preview.' },
]

const activeView = ref('catalog')
const step = ref(0)
const draft = ref(null)
const saving = ref(false)

const catalog = ref(null)
const catalogLoading = ref(false)
const filters = ref({ search: '', status: '', product_type: '' })

const quote = ref({ product_code: '', amount: 1000000000, tenor: 12, segment: '' })
const quoteResult = ref(null)
const quoteLoading = ref(false)

const analytics = ref(null)
const analyticsLoading = ref(false)

const pendingApprovals = ref([])
const approvalsLoading = ref(false)

const currentUser = computed(() => window.frappe?.session?.user_fullname || window.frappe?.session?.user || 'You')

function __(s) { return s }
function isActiveTab(v) { return activeView.value === v || (activeView.value === 'detail' && v === 'catalog') }

function navigate(view) {
  activeView.value = view
  if (view === 'analytics') loadAnalytics()
  if (view === 'approvals') loadApprovals()
  if (view === 'calculator' && !catalog.value) loadCatalog()
}

let searchTimer = null
function debouncedLoad() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadCatalog, 250)
}

async function loadCatalog() {
  catalogLoading.value = true
  try {
    catalog.value = await call('crm.api.products.get_product_catalog', { filters: { ...filters.value } })
  } catch (e) {
    notify.err(`Failed to load catalog: ` + (e?.message || String(e)))
  } finally {
    catalogLoading.value = false
  }
}

function emptyDraft() {
  return {
    product_code: '', product_name: '', product_type: 'Working Capital', currency: 'IDR',
    status: 'Draft', marketing_tagline: '', description: '',
    min_amount: 0, max_amount: 0,
    min_tenor_months: 0, max_tenor_months: 0, tenor_increment_months: 1,
    repayment_frequency: 'Monthly', grace_period_days: 0,
    allow_balloon: 0, allow_step_schedule: 0,
    workflow: '', form_template: '',
    interest_tiers: [], fees: [], eligibility_rules: [], document_requirements: [], approval_tiers: [],
    _existing: false,
  }
}

async function openWizard(code) {
  step.value = 0
  if (!code) {
    draft.value = emptyDraft()
    activeView.value = 'detail'
    return
  }
  try {
    const data = await call('crm.api.products.get_product', { code })
    draft.value = {
      ...emptyDraft(),
      ...data,
      interest_tiers: data.interest_tiers || [],
      fees: data.fees || [],
      eligibility_rules: data.eligibility_rules || [],
      document_requirements: data.document_requirements || [],
      approval_tiers: data.approval_tiers || [],
      _existing: true,
    }
    activeView.value = 'detail'
  } catch (e) {
    notify.err(`Failed to load product: ` + (e?.message || String(e)))
  }
}

async function saveDraft() {
  if (!draft.value?.product_code) {
    notify.err('Product code is required before saving.')
    step.value = 0
    return false
  }
  saving.value = true
  try {
    const payload = { ...draft.value }
    delete payload._existing
    const saved = await call('crm.api.products.save_product', { payload })
    draft.value = { ...draft.value, ...saved, _existing: true }
    notify.ok('Draft saved')
    return true
  } catch (e) {
    console.error('save_product failed', e)
    notify.err(`Save failed: ` + (e?.message || e?._server_messages || String(e)))
    return false
  } finally {
    saving.value = false
  }
}

async function submitForReview() {
  console.log('[ProductConfig] submitForReview clicked', { code: draft.value?.product_code, status: draft.value?.status })
  const ok = await saveDraft()
  if (!ok) return
  try {
    const result = await call('crm.api.products.submit_for_review', { code: draft.value.product_code })
    if (result?.status) draft.value.status = result.status
    notify.ok('Submitted for approval')
  } catch (e) {
    console.error('submit_for_review failed', e)
    notify.err(`Submit failed: ` + (e?.message || e?._server_messages || String(e)))
  }
}

async function approveProduct() {
  try {
    const result = await call('crm.api.products.approve_product', { code: draft.value.product_code })
    draft.value.status = result.status
    draft.value.version = result.version
    notify.ok('Product approved & activated')
  } catch (e) {
    notify.err(`Approval failed: ` + (e?.message || String(e)))
  }
}

async function approveByCode(code) {
  try {
    await call('crm.api.products.approve_product', { code })
    notify.ok('Approved')
    await loadApprovals()
    await loadCatalog()
  } catch (e) {
    notify.err(`Approval failed: ` + (e?.message || String(e)))
  }
}

async function cloneProductPrompt(p) {
  const newCode = window.prompt('New product code:', `${p.product_code}-COPY`)
  if (!newCode) return
  try {
    const cloned = await call('crm.api.products.clone_product', { code: p.product_code, new_code: newCode })
    notify.ok('Cloned')
    await loadCatalog()
    openWizard(cloned.product_code)
  } catch (e) {
    notify.err(`Clone failed: ` + (e?.message || String(e)))
  }
}

async function retirePrompt(p) {
  if (!window.confirm(`Retire ${p.product_code}? New applications will be blocked.`)) return
  try {
    await call('crm.api.products.retire_product', { code: p.product_code })
    notify.err('Product retired')
    await loadCatalog()
  } catch (e) {
    notify.err(`Retire failed: ` + (e?.message || String(e)))
  }
}

async function runQuote() {
  if (!quote.value.product_code) {
    notify.warn('Select a product first')
    return
  }
  quoteLoading.value = true
  try {
    quoteResult.value = await call('crm.api.products.calculate_quote', { payload: { ...quote.value } })
  } catch (e) {
    notify.err(`Calculation failed: ` + (e?.message || String(e)))
  } finally {
    quoteLoading.value = false
  }
}

async function loadAnalytics() {
  analyticsLoading.value = true
  try {
    analytics.value = await call('crm.api.products.get_product_analytics')
  } catch (e) {
    notify.err(`Failed to load analytics: ` + (e?.message || String(e)))
  } finally {
    analyticsLoading.value = false
  }
}

async function loadApprovals() {
  approvalsLoading.value = true
  try {
    pendingApprovals.value = await call('crm.api.products.get_pending_approvals')
  } catch (e) {
    notify.err(`Failed to load approvals: ` + (e?.message || String(e)))
  } finally {
    approvalsLoading.value = false
  }
}

async function exportCsv() {
  try {
    const r = await call('crm.api.products.export_catalog_csv', { filters: { ...filters.value } })
    const blob = new Blob([r.content], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = r.filename
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    notify.err(`Export failed: ` + (e?.message || String(e)))
  }
}

// ── Formatters ──────────────────────────────────────────────────
function fmtMoney(v, ccy = 'IDR') {
  const n = Number(v || 0)
  try {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: ccy || 'IDR', maximumFractionDigits: 0 }).format(n)
  } catch {
    return `${ccy} ${n.toLocaleString()}`
  }
}
function fmtRange(min, max, ccy) {
  if (!min && !max) return '—'
  return `${fmtMoney(min || 0, ccy)} – ${fmtMoney(max || 0, ccy)}`
}
function fmtTenor(min, max) {
  if (!min && !max) return '—'
  return `${min || 0}–${max || 0} mo`
}
function fmtDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return isNaN(dt) ? '' : dt.toLocaleDateString()
}

// ── Inline components ──────────────────────────────────────────
const KpiCard = defineComponent({
  name: 'KpiCard',
  props: ['label', 'value', 'icon', 'theme'],
  setup(props) {
    return () => h('div', { class: 'rounded-[12px] border border-outline-gray-2 bg-white px-3.5 py-3 shadow-sm' }, [
      h('div', { class: 'flex items-center justify-between' }, [
        h('span', { class: 'text-[11px] font-medium uppercase tracking-wide text-ink-gray-5' }, props.label),
        h(FeatherIcon, { name: props.icon || 'circle', class: 'h-3.5 w-3.5 text-ink-gray-4' }),
      ]),
      h('div', {
        class: 'mt-1.5 text-xl font-semibold leading-tight',
        style: props.theme === 'red' ? 'color:#dc2626'
          : props.theme === 'orange' ? 'color:#d97706'
          : props.theme === 'blue' ? 'color:#1d4ed8'
          : props.theme === 'teal' ? 'color:#008C95'
          : 'color:#111827',
      }, String(props.value ?? 0)),
    ])
  },
})

const StatusPill = defineComponent({
  name: 'StatusPill',
  props: ['status'],
  setup(props) {
    return () => {
      const map = {
        'Active': 'bg-surface-green-2 text-ink-green-9',
        'Draft': 'bg-surface-gray-2 text-ink-gray-7',
        'Pending Approval': 'bg-surface-amber-2 text-ink-amber-9',
        'Retired': 'bg-surface-gray-2 text-ink-gray-5',
      }
      const cls = map[props.status] || 'bg-surface-gray-2 text-ink-gray-6'
      return h('span', { class: `inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${cls}` }, props.status || '—')
    }
  },
})

const Field = defineComponent({
  name: 'Field',
  props: ['label', 'required'],
  setup(props, { slots }) {
    return () => h('label', { class: 'flex flex-col gap-1' }, [
      h('span', { class: 'text-xs font-medium text-ink-gray-6' }, [
        props.label,
        props.required ? h('span', { class: 'text-red-500 ml-0.5' }, '*') : null,
      ]),
      slots.default?.(),
    ])
  },
})

const Metric = defineComponent({
  name: 'Metric',
  props: ['label', 'value', 'sub'],
  setup(props) {
    return () => h('div', { class: 'rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5' }, [
      h('div', { class: 'text-[11px] font-medium uppercase tracking-wide text-ink-gray-5' }, props.label),
      h('div', { class: 'text-base font-semibold text-ink-gray-9' }, props.value),
      props.sub ? h('div', { class: 'text-[11px] text-ink-gray-5' }, props.sub) : null,
    ])
  },
})

const ChildTable = defineComponent({
  name: 'ChildTable',
  props: ['title', 'rows', 'columns'],
  emits: ['add', 'remove'],
  setup(props, { emit }) {
    return () => h('div', { class: 'rounded-md border border-outline-gray-2 overflow-hidden' }, [
      h('div', { class: 'flex items-center justify-between border-b border-outline-gray-2 bg-surface-gray-1 px-3 py-2' }, [
        h('h3', { class: 'text-sm font-semibold text-ink-gray-9' }, props.title),
        h('button', {
          class: 'inline-flex items-center gap-1 text-xs font-medium text-ink-gray-7 hover:text-ink-gray-9',
          onClick: () => emit('add'),
        }, [h(FeatherIcon, { name: 'plus', class: 'h-3.5 w-3.5' }), '+ Add Row']),
      ]),
      h('div', { class: 'overflow-x-auto' }, [
        h('table', { class: 'w-full text-sm' }, [
          h('thead', { class: 'bg-white text-left text-[11px] font-medium uppercase tracking-wide text-ink-gray-5' }, [
            h('tr', {}, [
              ...props.columns.map((c) => h('th', { class: 'px-3 py-2 border-b border-outline-gray-1' }, c.label)),
              h('th', { class: 'px-3 py-2 border-b border-outline-gray-1 w-8' }),
            ]),
          ]),
          h('tbody', {}, (props.rows || []).map((row, idx) => h('tr', { key: idx, class: 'border-b border-outline-gray-1 last:border-b-0' }, [
            ...props.columns.map((c) => h('td', { class: 'px-2 py-1.5' }, [renderInput(row, c)])),
            h('td', { class: 'px-2 py-1.5 text-right' }, [
              h('button', {
                class: 'text-ink-gray-4 hover:text-red-500',
                onClick: () => emit('remove', idx),
              }, [h(FeatherIcon, { name: 'trash-2', class: 'h-3.5 w-3.5' })]),
            ]),
          ]))),
        ]),
      ]),
      (!props.rows || !props.rows.length) ? h('div', { class: 'px-3 py-4 text-center text-xs text-ink-gray-4' }, 'No rows yet. Click + Add Row.') : null,
    ])

    function renderInput(row, c) {
      const baseClass = 'w-full rounded border border-outline-gray-2 bg-white px-2 py-1 text-sm text-ink-gray-8 outline-none focus:border-outline-gray-4'
      if (c.type === 'select') {
        return h('select', {
          class: baseClass,
          value: row[c.key] ?? '',
          onChange: (e) => { row[c.key] = e.target.value },
        }, (c.options || []).map((o) => h('option', { value: o }, o)))
      }
      if (c.type === 'checkbox') {
        return h('input', {
          type: 'checkbox',
          checked: !!row[c.key],
          class: 'h-4 w-4 rounded border-outline-gray-3',
          onChange: (e) => { row[c.key] = e.target.checked ? 1 : 0 },
        })
      }
      return h('input', {
        type: c.type === 'number' ? 'number' : 'text',
        value: row[c.key] ?? '',
        class: baseClass,
        onInput: (e) => {
          const v = e.target.value
          row[c.key] = c.type === 'number' ? (v === '' ? null : Number(v)) : v
        },
      })
    }
  },
})

onMounted(() => {
  loadCatalog()
})
</script>

<style scoped>
.field-input {
  @apply w-full rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8 outline-none focus:border-outline-gray-4;
}
.field-input:disabled {
  @apply bg-surface-gray-1 text-ink-gray-5;
}
</style>
