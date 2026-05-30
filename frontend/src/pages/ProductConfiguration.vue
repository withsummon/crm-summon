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
    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-4">
      <div class="flex items-center justify-between gap-3">
        <div class="flex gap-3 overflow-x-auto">
          <button
            v-for="tab in TABS"
            :key="tab.view"
            class="border-b-2 py-2 text-base transition-colors whitespace-nowrap"
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
      <div class="w-full px-3 py-2">

        <!-- ── CATALOG ──────────────────────────────────────── -->
        <template v-if="activeView === 'catalog'">
          <!-- KPI strip -->
          <div class="mb-3 grid gap-3 md:grid-cols-6">
            <KpiCard :label="__('All Products')" :value="catalog?.counts?.total ?? 0" icon="package" />
            <KpiCard :label="__('Active')" :value="catalog?.counts?.active ?? 0" icon="check-circle" theme="teal" />
            <KpiCard :label="__('Draft')" :value="catalog?.counts?.draft ?? 0" icon="edit-3" />
            <KpiCard :label="__('Pending')" :value="catalog?.counts?.pending ?? 0" icon="clock" theme="orange" />
            <KpiCard :label="__('Retired')" :value="catalog?.counts?.retired ?? 0" icon="archive" />
            <KpiCard :label="__('Retiring Soon')" :value="retiringSoonCount" icon="alert-triangle" theme="orange" />
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
              <option value="Scheduled">Scheduled</option>
            </select>
            <select v-model="filters.product_type" class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8" @change="loadCatalog">
              <option value="">{{ __('All types') }}</option>
              <option v-for="t in TYPES" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>

          <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
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
                  <th class="px-3 py-1.5">{{ __('Code') }}</th>
                  <th class="px-3 py-1.5">{{ __('Name') }}</th>
                  <th class="px-3 py-1.5">{{ __('Type') }}</th>
                  <th class="px-3 py-1.5">{{ __('Status') }}</th>
                  <th class="px-3 py-1.5">{{ __('Amount Range') }}</th>
                  <th class="px-3 py-1.5">{{ __('Tenor') }}</th>
                  <th class="px-3 py-1.5">{{ __('Updated') }}</th>
                  <th class="px-3 py-1.5"></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in catalog.rows"
                  :key="p.name"
                  class="border-b border-outline-gray-1 last:border-b-0 hover:bg-surface-gray-1 cursor-pointer"
                  @click="openWizard(p.product_code)"
                >
                  <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ p.product_code }}</td>
                  <td class="px-3 py-1.5 text-ink-gray-8">{{ p.product_name }}</td>
                  <td class="px-3 py-1.5 text-ink-gray-7">{{ p.product_type || '—' }}</td>
                  <td class="px-3 py-1.5">
                    <div class="flex flex-wrap gap-1">
                      <StatusPill :status="p.status" />
                      <span v-if="p.retirement_status === 'Scheduled'" class="inline-flex items-center rounded-full bg-surface-amber-2 px-2 py-0.5 text-[11px] font-medium text-ink-amber-9">Retires {{ fmtDate(p.retirement_date) }}</span>
                    </div>
                  </td>
                  <td class="px-3 py-1.5 text-ink-gray-7">{{ fmtRange(p.min_amount, p.max_amount, p.currency) }}</td>
                  <td class="px-3 py-1.5 text-ink-gray-7">{{ fmtTenor(p.min_tenor_months, p.max_tenor_months) }}</td>
                  <td class="px-3 py-1.5 text-xs text-ink-gray-5">{{ fmtDate(p.modified) }}</td>
                  <td class="px-3 py-1.5 text-right">
                    <div class="flex justify-end gap-1">
                      <Button size="sm" variant="ghost" @click.stop="cloneProductPrompt(p)">
                        <FeatherIcon name="copy" class="h-4 w-4 text-ink-gray-5" />
                      </Button>
                      <Button size="sm" variant="ghost" @click.stop="openRetireDialog(p)">
                        <FeatherIcon name="more-vertical" class="h-4 w-4 text-ink-gray-5" />
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
          <div class="grid gap-3 md:grid-cols-[220px_1fr]">
            <!-- Step nav -->
            <aside class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm h-fit">
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
                  :style="step >= i ? 'background:#FF6600' : ''"
                >{{ i + 1 }}</span>
                {{ s.label }}
              </button>
              <div v-if="draft._existing && draft.versions && draft.versions.length" class="mt-3 border-t border-outline-gray-1 pt-3">
                <label class="text-xs uppercase tracking-wide text-ink-gray-5">{{ __('Version') }}</label>
                <select v-model="selectedVersion" class="mt-1 w-full rounded-md border border-outline-gray-2 px-2 py-1 text-sm" @change="onVersionChange">
                  <option v-for="v in draft.versions" :key="v.version" :value="v.version">v{{ v.version }} · {{ v.status }}</option>
                </select>
                <Button v-if="draft.status === 'Active'" class="mt-2 w-full" size="sm" variant="outline" label="Bump Version" @click="bumpVersion" />
              </div>
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
            <section class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
              <div class="mb-3 flex items-center justify-between">
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
              <div v-if="step === 0" class="grid gap-3 md:grid-cols-2">
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
              <div v-else-if="step === 1" class="space-y-3">
                <div class="grid gap-3 md:grid-cols-3">
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
              <div v-else-if="step === 2" class="space-y-3">
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

              <!-- Step 4: Collateral -->
              <div v-else-if="step === 3" class="space-y-3">
                <div v-if="(draft.collateral_rules || []).length" class="flex flex-wrap gap-2">
                  <span class="rounded-full bg-surface-gray-2 px-2 py-0.5 text-[11px] text-ink-gray-7">{{ draft.collateral_rules.length }} types</span>
                  <span class="rounded-full bg-surface-gray-2 px-2 py-0.5 text-[11px] text-ink-gray-7">Insurance on {{ draft.collateral_rules.filter(r => r.insurance_required).length }}</span>
                </div>
                <ChildTable
                  title="Collateral Rules"
                  :rows="draft.collateral_rules"
                  :columns="[
                    { key: 'collateral_type', label: 'Type', type: 'text' },
                    { key: 'mandatory', label: 'Mandatory', type: 'checkbox' },
                    { key: 'min_ltv_pct', label: 'Min LTV %', type: 'number' },
                    { key: 'min_coverage_pct', label: 'Min Coverage %', type: 'number' },
                    { key: 'insurance_required', label: 'Insurance', type: 'checkbox' },
                    { key: 'insurance_min_coverage_pct', label: 'Ins. Coverage %', type: 'number' },
                    { key: 'reappraisal_months', label: 'Reappraisal (mo)', type: 'number' },
                  ]"
                  @add="draft.collateral_rules.push({ mandatory: 1 })"
                  @remove="(i) => draft.collateral_rules.splice(i, 1)"
                />
              </div>

              <!-- Step 5: Workflow -->
              <div v-else-if="step === 4" class="space-y-3">
                <div class="grid gap-3 md:grid-cols-2">
                  <Field label="Workflow">
                    <input v-model="draft.workflow" class="field-input" placeholder="e.g. LOS Standard" />
                  </Field>
                  <Field label="Form Template">
                    <select v-model="draft.form_template" class="field-input">
                      <option value="">—</option>
                      <option v-for="t in formTemplates" :key="t.name" :value="t.name">{{ t.template_name }}</option>
                    </select>
                  </Field>
                </div>
                <div v-if="draft.form_template" class="flex gap-2">
                  <Button size="sm" variant="outline" label="Preview" @click="previewTemplate" />
                  <Button size="sm" variant="ghost" @click="activeView = 'form_templates'">Manage templates</Button>
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

              <!-- Step 6: Documents -->
              <div v-else-if="step === 5" class="space-y-3">
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
                <div class="rounded-md border border-outline-gray-2 bg-surface-gray-1 p-3">
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
                    <div><span class="text-ink-gray-5">{{ __('Collateral Rules') }}:</span> {{ (draft.collateral_rules || []).length }}</div>
                    <div><span class="text-ink-gray-5">{{ __('Required Docs') }}:</span> {{ (draft.document_requirements || []).length }}</div>
                  </div>
                </div>
              </div>

              <!-- Step 7: Cross-Sell -->
              <div v-else-if="step === 6" class="space-y-3">
                <p class="text-sm text-ink-gray-6">{{ __('Define which products should be suggested to customers of this product.') }}</p>
                <ChildTable
                  title="Cross-Sell Targets"
                  :rows="draft.cross_sell_targets || (draft.cross_sell_targets = [])"
                  :columns="[
                    { key: 'target', label: 'Target Product', type: 'text' },
                    { key: 'segment', label: 'Segment', type: 'text' },
                    { key: 'min_exposure', label: 'Min Exposure', type: 'number' },
                    { key: 'reason', label: 'Reason', type: 'text' },
                  ]"
                  @add="draft.cross_sell_targets.push({})"
                  @remove="(i) => draft.cross_sell_targets.splice(i, 1)"
                />
              </div>
            </section>
          </div>
        </template>

        <!-- ── CALCULATOR ──────────────────────────────────── -->
        <template v-else-if="activeView === 'calculator'">
          <div class="grid gap-3 md:grid-cols-[1fr_1fr]">
            <section class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
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
            <section class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
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
          <div v-else-if="analytics" class="space-y-3">
            <div class="grid gap-3 md:grid-cols-5">
              <KpiCard :label="__('Total Products')" :value="analytics.totals.products" icon="package" />
              <KpiCard :label="__('Active')" :value="analytics.totals.active" icon="check-circle" theme="teal" />
              <KpiCard :label="__('Pending')" :value="analytics.totals.pending" icon="clock" theme="orange" />
              <KpiCard :label="__('Retired')" :value="analytics.totals.retired" icon="archive" />
              <KpiCard :label="__('Applications')" :value="analytics.totals.applications" icon="file-text" theme="blue" />
            </div>
            <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm overflow-hidden">
              <table class="w-full text-sm">
                <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                  <tr>
                    <th class="px-3 py-1.5">{{ __('Product') }}</th>
                    <th class="px-3 py-1.5">{{ __('Status') }}</th>
                    <th class="px-3 py-1.5 text-right">{{ __('Applications') }}</th>
                    <th class="px-3 py-1.5 text-right">{{ __('Approvals') }}</th>
                    <th class="px-3 py-1.5 text-right">{{ __('Disbursed') }}</th>
                    <th class="px-3 py-1.5 text-right">{{ __('Avg Ticket') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in analytics.per_product" :key="p.name" class="border-b border-outline-gray-1 last:border-b-0">
                    <td class="px-3 py-1.5">
                      <div class="font-medium text-ink-gray-9">{{ p.product_code }}</div>
                      <div class="text-xs text-ink-gray-5">{{ p.product_name }}</div>
                    </td>
                    <td class="px-3 py-1.5"><StatusPill :status="p.status" /></td>
                    <td class="px-3 py-1.5 text-right text-ink-gray-8">{{ p.applications }}</td>
                    <td class="px-3 py-1.5 text-right text-ink-gray-8">{{ p.approvals }}</td>
                    <td class="px-3 py-1.5 text-right text-ink-gray-8">{{ p.disbursements }}</td>
                    <td class="px-3 py-1.5 text-right text-ink-gray-7">{{ fmtMoney(p.avg_ticket, 'IDR') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>

        <!-- ── CROSS-SELL ────────────────────────────────────── -->
        <template v-else-if="activeView === 'crosssell'">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <div class="mb-3 flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold text-ink-gray-9">{{ __('Cross-Sell Mappings') }}</h2>
                <p class="text-xs text-ink-gray-5">{{ __('Suggest target products to customers based on their source product.') }}</p>
              </div>
              <Button variant="solid" size="sm" label="+ New Mapping" @click="addCrossSell" />
            </div>
            <table class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-3 py-2">Source Product</th>
                  <th class="px-3 py-2">Target Product</th>
                  <th class="px-3 py-2">Segment</th>
                  <th class="px-3 py-2 text-right">Min Exposure</th>
                  <th class="px-3 py-2">Reason</th>
                  <th class="px-3 py-2 text-right"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(m, i) in crossSell" :key="m.id" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-3 py-2">
                    <select v-model="m.source" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm w-full">
                      <option v-for="p in (catalog?.rows || [])" :key="p.product_code" :value="p.product_code">{{ p.product_code }}</option>
                    </select>
                  </td>
                  <td class="px-3 py-2">
                    <select v-model="m.target" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm w-full">
                      <option v-for="p in (catalog?.rows || [])" :key="p.product_code" :value="p.product_code">{{ p.product_code }}</option>
                    </select>
                  </td>
                  <td class="px-3 py-2"><input v-model="m.segment" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm w-full" placeholder="SME, Corporate…" /></td>
                  <td class="px-3 py-2 text-right"><input type="number" v-model.number="m.min_exposure" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm w-32 text-right" /></td>
                  <td class="px-3 py-2"><input v-model="m.reason" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm w-full" placeholder="Eligibility reason" /></td>
                  <td class="px-3 py-2 text-right"><button @click="removeCrossSell(i)" class="text-red-500 hover:text-red-700 text-sm">✕</button></td>
                </tr>
                <tr v-if="!crossSell.length">
                  <td colspan="6" class="px-3 py-8 text-center text-ink-gray-5">No cross-sell mappings yet.</td>
                </tr>
              </tbody>
            </table>
            <div class="mt-3 flex justify-end">
              <Button variant="solid" size="sm" :loading="crossSellSaving" label="Save Mappings" @click="saveCrossSell" />
            </div>
          </div>
        </template>

        <!-- ── APPROVALS ────────────────────────────────────── -->
        <template v-else-if="activeView === 'approvals'">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
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
                  <th class="px-3 py-1.5">{{ __('Product') }}</th>
                  <th class="px-3 py-1.5">{{ __('Type') }}</th>
                  <th class="px-3 py-1.5">{{ __('Submitted By') }}</th>
                  <th class="px-3 py-1.5">{{ __('Submitted') }}</th>
                  <th class="px-3 py-1.5"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in pendingApprovals" :key="p.name" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-3 py-1.5">
                    <div class="font-medium text-ink-gray-9">{{ p.product_code }}</div>
                    <div class="text-xs text-ink-gray-5">{{ p.product_name }}</div>
                  </td>
                  <td class="px-3 py-1.5 text-ink-gray-7">{{ p.product_type }}</td>
                  <td class="px-3 py-1.5 text-ink-gray-7">{{ p.owner }}</td>
                  <td class="px-3 py-1.5 text-xs text-ink-gray-5">{{ fmtDate(p.modified) }}</td>
                  <td class="px-3 py-1.5 text-right">
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

        <!-- ── FORM TEMPLATES ─────────────────────────────────── -->
        <template v-else-if="activeView === 'form_templates'">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <div class="mb-3 flex items-center justify-between">
              <h2 class="text-base font-semibold text-ink-gray-9">{{ __('Form Templates') }}</h2>
            </div>
            <div v-if="formTemplatesLoading" class="flex h-40 items-center justify-center"><LoadingIndicator class="h-5 w-5 text-ink-gray-4" /></div>
            <table v-else class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
                <tr><th class="px-3 py-2">Template</th><th class="px-3 py-2">Applies To</th><th class="px-3 py-2">Status</th><th class="px-3 py-2 text-right">Fields</th><th class="px-3 py-2 text-right">Used By</th></tr>
              </thead>
              <tbody>
                <tr v-for="t in formTemplates" :key="t.name" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ t.template_name }}</td>
                  <td class="px-3 py-1.5 text-ink-gray-7">{{ t.applies_to_product_type }}</td>
                  <td class="px-3 py-1.5"><StatusPill :status="t.status" /></td>
                  <td class="px-3 py-1.5 text-right">{{ t.field_count }}</td>
                  <td class="px-3 py-1.5 text-right">{{ t.product_usage }}</td>
                </tr>
                <tr v-if="!formTemplates.length"><td colspan="5" class="px-3 py-8 text-center text-ink-gray-5">No templates yet.</td></tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- ── RETIREMENTS ────────────────────────────────────── -->
        <template v-else-if="activeView === 'retirements'">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <h2 class="text-base font-semibold text-ink-gray-9 mb-3">{{ __('Retirements') }}</h2>
            <div v-if="retirementsLoading" class="flex h-40 items-center justify-center"><LoadingIndicator class="h-5 w-5 text-ink-gray-4" /></div>
            <div v-else class="space-y-4">
              <div>
                <h3 class="text-xs font-semibold uppercase tracking-wide text-ink-gray-5 mb-2">{{ __('Upcoming') }}</h3>
                <table class="w-full text-sm">
                  <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5"><tr><th class="px-3 py-2">Product</th><th class="px-3 py-2">Date</th><th class="px-3 py-2">Reason</th><th class="px-3 py-2">Replacement</th><th class="px-3 py-2 text-right"></th></tr></thead>
                  <tbody>
                    <tr v-for="p in retirements.upcoming" :key="p.name" class="border-b border-outline-gray-1 last:border-b-0">
                      <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ p.product_code }}</td>
                      <td class="px-3 py-1.5 text-ink-gray-7">{{ fmtDate(p.retirement_date) }}</td>
                      <td class="px-3 py-1.5 text-ink-gray-7">{{ p.retirement_reason || '—' }}</td>
                      <td class="px-3 py-1.5 text-ink-gray-7">{{ p.replacement_product || '—' }}</td>
                      <td class="px-3 py-1.5 text-right"><Button size="sm" variant="outline" label="Cancel" @click="cancelRetirement(p)" /></td>
                    </tr>
                    <tr v-if="!retirements.upcoming.length"><td colspan="5" class="px-3 py-8 text-center text-ink-gray-5">No upcoming retirements.</td></tr>
                  </tbody>
                </table>
              </div>
              <div>
                <h3 class="text-xs font-semibold uppercase tracking-wide text-ink-gray-5 mb-2">{{ __('Past Log') }}</h3>
                <table class="w-full text-sm">
                  <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5"><tr><th class="px-3 py-2">Product</th><th class="px-3 py-2">Action</th><th class="px-3 py-2">Actor</th><th class="px-3 py-2">When</th></tr></thead>
                  <tbody>
                    <tr v-for="l in retirements.past" :key="l.name" class="border-b border-outline-gray-1 last:border-b-0">
                      <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ l.product }}</td>
                      <td class="px-3 py-1.5 text-ink-gray-7">{{ l.action }}</td>
                      <td class="px-3 py-1.5 text-ink-gray-7">{{ l.actor }}</td>
                      <td class="px-3 py-1.5 text-xs text-ink-gray-5">{{ fmtDate(l.creation) }}</td>
                    </tr>
                    <tr v-if="!retirements.past.length"><td colspan="4" class="px-3 py-8 text-center text-ink-gray-5">No retirement history.</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </template>

      </div>
    </div>

    <Dialog
      v-model="retireDialog.open"
      :options="{
        title: retireDialog.product ? ('Retire ' + retireDialog.product.product_code) : 'Retire Product',
        size: 'md',
        actions: [
          { label: 'Cancel', onClick: () => (retireDialog.open = false) },
          { label: 'Confirm', variant: 'solid', onClick: confirmRetire },
        ],
      }"
    >
      <template #body-content>
        <div class="space-y-3">
          <div class="flex gap-2">
            <label class="flex items-center gap-2 text-sm text-ink-gray-7"><input v-model="retireDialog.mode" type="radio" value="schedule" class="size-4 accent-[#FF6600]" /> Schedule</label>
            <label class="flex items-center gap-2 text-sm text-ink-gray-7"><input v-model="retireDialog.mode" type="radio" value="immediate" class="size-4 accent-[#FF6600]" /> Retire now</label>
          </div>
          <div v-if="retireDialog.mode === 'schedule'">
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Retirement Date</label>
            <input v-model="retireDialog.date" type="date" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Reason</label>
            <select v-model="retireDialog.reason" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm">
              <option value="">—</option>
              <option>Replaced</option>
              <option>Compliance</option>
              <option>Low Volume</option>
              <option>Strategic</option>
              <option>Other</option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Replacement Product</label>
            <input v-model="retireDialog.replacement_product" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm" placeholder="Product code" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Migration Plan</label>
            <textarea v-model="retireDialog.migration_plan" rows="3" class="w-full rounded-md border border-outline-gray-2 bg-white px-2 py-1.5 text-sm" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Notes</label>
            <textarea v-model="retireDialog.notes" rows="2" class="w-full rounded-md border border-outline-gray-2 bg-white px-2 py-1.5 text-sm" />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, h, onMounted, ref, defineComponent } from 'vue'
import { Button, Dialog, FeatherIcon, LoadingIndicator, call as _frappeCall, toast } from 'frappe-ui'
import { loadPersisted, persistRef } from '@/utils/persist'
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
  { view: 'crosssell', label: 'Cross-Sell' },
  { view: 'form_templates', label: 'Form Templates' },
  { view: 'analytics', label: 'Analytics' },
  { view: 'approvals', label: 'Approvals' },
  { view: 'retirements', label: 'Retirements' },
]

const TYPES = ['Working Capital', 'Investment', 'Consumer', 'Mortgage', 'Other']

const STEPS = [
  { key: 'basics', label: 'Basics', hint: 'Code, name, type, and description.' },
  { key: 'pricing', label: 'Pricing', hint: 'Amount/tenor limits, interest tiers, fees.' },
  { key: 'eligibility', label: 'Eligibility', hint: 'Who can apply for this product.' },
  { key: 'collateral', label: 'Collateral', hint: 'Required collateral types, LTV, insurance, re-appraisal cadence.' },
  { key: 'workflow', label: 'Workflow', hint: 'Workflow, form template, approval matrix.' },
  { key: 'documents', label: 'Documents', hint: 'Required documents and preview.' },
  { key: 'crosssell', label: 'Cross-Sell', hint: 'Suggested products and eligibility criteria.' },
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

const selectedVersion = ref(null)
const crossSell = ref(loadPersisted('crm:product:crossSell', []))
persistRef('crm:product:crossSell', crossSell)
const crossSellSaving = ref(false)

const formTemplates = ref([])
const formTemplatesLoading = ref(false)
const retirements = ref({ upcoming: [], past: [] })
const retirementsLoading = ref(false)
const retireDialog = ref({ open: false, product: null, mode: 'schedule', date: '', reason: '', replacement_product: '', migration_plan: '', notes: '' })
const retiringSoonCount = computed(() => (catalog.value?.rows || []).filter(p => p.retirement_status === 'Scheduled' && p.retirement_date && (new Date(p.retirement_date) - new Date()) / (1000 * 60 * 60 * 24) <= 30).length)

function addCrossSell() {
  crossSell.value.push({ id: Date.now(), source: '', target: '', segment: '', min_exposure: 0, reason: '' })
}
function removeCrossSell(idx) {
  crossSell.value.splice(idx, 1)
}
async function saveCrossSell() {
  crossSellSaving.value = true
  try {
    await call('crm.api.products.save_cross_sell_mappings', { mappings: crossSell.value }).catch(() => null)
    notify.ok('Cross-sell mappings saved')
  } finally {
    crossSellSaving.value = false
  }
}
async function loadCrossSell() {
  try {
    const data = await call('crm.api.products.get_cross_sell_mappings').catch(() => null)
    if (data?.mappings?.length) crossSell.value = data.mappings
  } catch (_) {}
}

async function loadFormTemplates() {
  formTemplatesLoading.value = true
  try {
    const res = await call('crm.api.products.list_form_templates')
    formTemplates.value = res.templates || []
  } catch (e) {}
  finally { formTemplatesLoading.value = false }
}

async function loadRetirements() {
  retirementsLoading.value = true
  try {
    const res = await call('crm.api.products.list_retirements', { range: 'all' })
    retirements.value = res
  } catch (e) {}
  finally { retirementsLoading.value = false }
}

function openRetireDialog(p) {
  retireDialog.value = { open: true, product: p, mode: 'schedule', date: '', reason: '', replacement_product: '', migration_plan: '', notes: '' }
}

async function confirmRetire() {
  const d = retireDialog.value
  if (!d.product) return
  try {
    await call('crm.api.products.retire_product', { code: d.product.product_code, retirement_date: d.date, reason: d.reason, replacement_product: d.replacement_product, migration_plan: d.migration_plan, mode: d.mode, notes: d.notes })
    notify.ok(d.mode === 'schedule' ? 'Scheduled' : 'Retired')
    retireDialog.value.open = false
    await loadCatalog()
  } catch (e) {
    notify.err(e?.message || 'Failed')
  }
}

async function cancelRetirement(p) {
  if (!confirm('Cancel retirement for ' + p.product_code + '?')) return
  try {
    await call('crm.api.products.cancel_retirement', { code: p.product_code })
    notify.ok('Cancelled')
    await loadCatalog()
  } catch (e) {
    notify.err(e?.message || 'Failed')
  }
}

async function reactivateProduct(p) {
  if (!confirm('Reactivate ' + p.product_code + '?')) return
  try {
    await call('crm.api.products.reactivate_product', { code: p.product_code })
    notify.ok('Reactivated')
    await loadCatalog()
  } catch (e) {
    notify.err(e?.message || 'Failed')
  }
}

function previewTemplate() {
  if (!draft.value?.form_template) return
  window.open('/crm/lending-risk/product-configuration?preview_template=' + draft.value.form_template, '_blank')
}

function onVersionChange() {
  if (!draft.value || !selectedVersion.value) return
  const v = (draft.value.versions || []).find((x) => x.version === selectedVersion.value)
  if (v) Object.assign(draft.value, v.snapshot || {})
}

async function bumpVersion() {
  if (!draft.value || !draft.value.product_code) return
  try {
    const res = await call('crm.api.products.bump_version', { code: draft.value.product_code }).catch(() => null)
    if (res?.version) {
      draft.value.version = res.version
      draft.value.versions = res.versions || draft.value.versions || []
      selectedVersion.value = res.version
      notify.ok(`Bumped to v${res.version}`)
    } else {
      const current = parseFloat(draft.value.version || '1.0')
      const next = (current + 1).toFixed(1)
      draft.value.versions = [
        ...(draft.value.versions || []),
        { version: draft.value.version || '1.0', status: 'Archived', snapshot: { ...draft.value } },
      ]
      draft.value.version = next
      draft.value.status = 'Draft'
      selectedVersion.value = next
      notify.ok(`Bumped to v${next}`)
    }
  } catch (e) {
    notify.err('Failed to bump version')
  }
}

const currentUser = computed(() => window.frappe?.session?.user_fullname || window.frappe?.session?.user || 'You')

function __(s) { return s }
function isActiveTab(v) { return activeView.value === v || (activeView.value === 'detail' && v === 'catalog') }

function navigate(view) {
  activeView.value = view
  if (view === 'analytics') loadAnalytics()
  if (view === 'approvals') loadApprovals()
  if (view === 'form_templates') loadFormTemplates()
  if (view === 'retirements') loadRetirements()
  if (view === 'calculator' && !catalog.value) loadCatalog()
  if (view === 'crosssell') {
    if (!catalog.value) loadCatalog()
    loadCrossSell()
  }
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
    workflow: '', form_template: '', form_template_version: '',
    interest_tiers: [], fees: [], eligibility_rules: [], collateral_rules: [], document_requirements: [], approval_tiers: [],
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
      collateral_rules: data.collateral_rules || [],
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
  openRetireDialog(p)
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
          : props.theme === 'teal' ? 'color:#FF6600'
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
    return () => h('div', { class: 'rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2' }, [
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
