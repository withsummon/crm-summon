<template>
  <div class="flex h-full bg-slate-50 font-sans">
    <div v-if="!routeApplication" class="w-80 border-r border-slate-200 bg-white flex flex-col shrink-0">
      <div class="p-4 border-b border-slate-200">
        <h2 class="text-lg font-bold text-slate-800 mb-3">{{ __('Credit Analysis Queue') }}</h2>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search borrower or application')"
            class="w-full pl-9 pr-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-600 focus:bg-white transition-all"
          />
          <span class="absolute left-3 top-2.5 text-slate-400">
            <FeatherIcon name="search" class="h-4 w-4" />
          </span>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <button
          v-for="app in filteredApps"
          :key="app.name"
          class="w-full text-left flex flex-col gap-1 p-3 rounded-lg cursor-pointer transition-all hover:bg-slate-50 border"
          :class="selectedApp?.name === app.name ? 'bg-teal-50 border-teal-200' : 'border-transparent'"
          @click="selectApp(app)"
        >
          <div class="flex justify-between items-start gap-2">
            <div class="font-semibold text-sm text-slate-800 truncate">{{ app.borrower_name }}</div>
            <Badge :label="app.status" :theme="statusTheme(app.status)" size="sm" variant="subtle" />
          </div>
          <div class="text-xs text-slate-500 truncate flex items-center gap-2 mt-0.5">
            <span class="font-mono text-slate-600">{{ app.name }}</span>
            <span class="w-1 h-1 rounded-full bg-slate-300"></span>
            <span>{{ app.facility_type || __('Credit Facility') }}</span>
          </div>
          <div class="text-xs font-bold text-slate-700 mt-1">
            {{ formatCurrency(app.requested_amount) }}
          </div>
        </button>
        <div v-if="!queue.loading && filteredApps.length === 0" class="p-6 text-center text-sm text-slate-400">
          {{ __('No applications found') }}
        </div>
      </div>
    </div>

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <div v-if="!selectedApp" class="flex-1 flex flex-col items-center justify-center text-slate-400 p-8">
        <div class="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center mb-4">
          <FeatherIcon name="file-text" class="h-10 w-10 text-slate-300" />
        </div>
        <h3 class="text-lg font-semibold text-slate-700">{{ __('No Application Selected') }}</h3>
        <p class="text-sm text-slate-500 mt-1 max-w-sm text-center">
          {{ __('Select an application to run spreading, ratios, DSCR, scenarios, memo, and approval routing.') }}
        </p>
      </div>

      <div v-else class="flex-1 flex flex-col overflow-hidden">
        <div class="bg-white border-b border-slate-200 p-5 flex flex-col xl:flex-row xl:items-center justify-between gap-5 shrink-0 shadow-sm">
          <div class="flex items-center gap-4 min-w-0">
            <div class="w-14 h-14 rounded-xl bg-teal-600 text-white flex items-center justify-center font-black text-xl shadow-md shadow-teal-600/10 shrink-0">
              {{ initials(selectedApp.borrower_name) }}
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-3 flex-wrap">
                <h1 class="text-xl font-bold text-slate-800 truncate">{{ selectedApp.borrower_name }}</h1>
                <Badge :label="selectedApp.borrower_type || __('Credit')" theme="teal" variant="subtle" />
                <Badge :label="selectedApp.status" :theme="statusTheme(selectedApp.status)" variant="solid" />
                <Badge :label="riskGrade.grade ? `${riskGrade.grade} / ${riskGrade.score}` : (selectedApp.risk_grade ? selectedApp.risk_grade : __('Unscored'))" theme="blue" variant="subtle" />
              </div>
              <div class="text-sm text-slate-500 flex flex-wrap items-center gap-4 mt-1.5">
                <span class="flex items-center gap-1">
                  <FeatherIcon name="hash" class="h-3.5 w-3.5 text-slate-400" />
                  {{ selectedApp.name }}
                </span>
                <span class="flex items-center gap-1">
                  <FeatherIcon name="briefcase" class="h-3.5 w-3.5 text-slate-400" />
                  {{ selectedApp.industry || selectedApp.facility_type || __('Credit Facility') }}
                </span>
                <span class="flex items-center gap-1 font-bold text-slate-700">
                  <FeatherIcon name="dollar-sign" class="h-3.5 w-3.5 text-slate-500" />
                  {{ formatCurrency(selectedApp.requested_amount) }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2 flex-wrap">
            <Button v-if="routeApplication" variant="outline" :label="__('Back to List')" @click="goToCreditList">
              <template #prefix>
                <FeatherIcon name="arrow-left" class="h-4 w-4" />
              </template>
            </Button>
            <Button variant="outline" :loading="busy" :label="__('Save Draft')" @click="saveCurrentSpreading" />
            <Button variant="solid" :loading="busy" :label="__('Submit Memo')" @click="submitApproval">
              <template #prefix>
                <FeatherIcon name="check-circle" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>

        <div class="px-5 pt-3 shrink-0 bg-white border-b border-slate-200">
          <div class="flex gap-5 overflow-x-auto">
            <button
              v-for="t in tabs"
              :key="t.key"
              class="pb-3 text-sm font-semibold border-b-2 transition-all whitespace-nowrap"
              :class="activeTab === t.key ? 'border-teal-600 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'"
              @click="activeTab = t.key"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-5 min-h-0">
          <div v-if="analysis.loading" class="text-sm text-slate-500">{{ __('Loading credit analysis...') }}</div>

          <div v-else-if="activeTab === 'spreading'" class="space-y-5">
            <div class="grid grid-cols-1 xl:grid-cols-4 gap-4">
              <MetricCard :label="__('Years Covered')" :value="String(years.length)" icon="calendar" />
              <MetricCard :label="__('Spread Lines')" :value="String(spreadRows.length)" icon="table" />
              <MetricCard :label="__('Balance Status')" :value="balanceStatus" icon="check-square" />
              <MetricCard :label="__('Source')" :value="extraction.status || __('Manual')" icon="upload" />
            </div>

            <section class="bg-white border border-slate-200 rounded-lg shadow-sm">
              <div class="p-4 border-b border-slate-200 flex items-center justify-between gap-3">
                <div>
                  <h3 class="font-bold text-slate-800">{{ __('Financial Spreading - PSAK Template') }}</h3>
                  <p class="text-xs text-slate-500 mt-1">{{ __('Editable 3-5 year PL/BS/CF rows with original and adjusted amounts.') }}</p>
                </div>
                <FileUploader
                  :upload-args="{ doctype: 'CRM Credit Application', docname: selectedApp.name, private: true }"
                  :validate-file="validateStatementFile"
                  @success="onStatementUploaded"
                >
                  <template #default="{ openFileSelector, uploading }">
                    <Button variant="outline" size="sm" :loading="busy || uploading" :label="__('Import PDF / Excel')" @click="openFileSelector">
                      <template #prefix>
                        <FeatherIcon name="upload-cloud" class="h-4 w-4" />
                      </template>
                    </Button>
                  </template>
                </FileUploader>
              </div>
              <div v-if="importResult" class="mx-4 mt-4 rounded-lg border px-4 py-3 text-sm" :class="importResult.errors?.length ? 'border-red-200 bg-red-50 text-red-700' : 'border-teal-200 bg-teal-50 text-teal-700'">
                <div class="font-semibold">
                  {{ importResult.errors?.length ? __('Import failed') : __('Import completed') }}
                  <span v-if="!importResult.errors?.length">- {{ importResult.row_count }} {{ __('rows') }}</span>
                </div>
                <ul v-if="importResult.errors?.length" class="mt-2 list-disc pl-5">
                  <li v-for="error in importResult.errors" :key="error">{{ error }}</li>
                </ul>
              </div>
              <div v-if="!spreadRows.length" class="mx-4 my-4 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-8 text-center">
                <FeatherIcon name="file-plus" class="mx-auto h-8 w-8 text-slate-400" />
                <h3 class="mt-3 text-sm font-bold text-slate-800">{{ __('Belum ada financial statement') }}</h3>
                <p class="mt-1 text-sm text-slate-500">{{ __('Upload PDF, Excel, atau CSV untuk mengisi spreading, ratio, DSCR, dan memo dengan data real.') }}</p>
              </div>
              <div class="overflow-x-auto">
                <table v-if="spreadRows.length" class="w-full text-sm min-w-[980px]">
                  <thead>
                    <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                      <th class="py-3 px-4 text-left font-bold">{{ __('Statement') }}</th>
                      <th class="py-3 px-4 text-left font-bold">{{ __('Line Item') }}</th>
                      <th v-for="year in years" :key="year" class="py-3 px-4 text-right font-bold">{{ year }}</th>
                      <th class="py-3 px-4 text-left font-bold">{{ __('Source') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in spreadMatrix" :key="row.key" class="border-b border-slate-100">
                      <td class="py-3 px-4 text-xs font-semibold uppercase text-slate-400">{{ row.statement_type }}</td>
                      <td class="py-3 px-4 font-semibold text-slate-800">{{ row.metric_label }}</td>
                      <td v-for="year in years" :key="`${row.key}-${year}`" class="py-2 px-3 text-right">
                        <input
                          v-if="row.cells[year]"
                          v-model.number="row.cells[year].adjusted_amount"
                          type="number"
                          class="w-32 rounded border border-slate-200 bg-white px-2 py-1 text-right font-mono text-xs focus:border-teal-600 focus:outline-none"
                        />
                        <span v-else class="text-slate-300">-</span>
                      </td>
                      <td class="py-3 px-4 text-xs text-slate-500">{{ row.source || __('Manual') }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
              <h3 class="font-bold text-slate-800 mb-3">{{ __('Balance Validation') }}</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-3">
                <div v-for="check in balanceChecks" :key="check.year" class="rounded-lg border border-slate-100 bg-slate-50 p-3">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-bold text-slate-700">{{ check.year }}</span>
                    <Badge :label="check.status" :theme="check.status === 'Balanced' ? 'green' : 'orange'" variant="subtle" />
                  </div>
                  <div class="mt-2 text-xs text-slate-500">{{ __('Difference') }}</div>
                  <div class="font-mono text-sm text-slate-800">{{ formatCurrency(check.difference) }}</div>
                </div>
              </div>
            </section>
          </div>

          <div v-else-if="activeTab === 'extraction'" class="space-y-5">
            <section class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <h3 class="font-bold text-slate-800">{{ __('AI Extraction Review') }}</h3>
                  <p class="text-sm text-slate-500 mt-1">{{ __('RAGAnything parses document content and Kimi reviews extracted financial cells before save.') }}</p>
                </div>
                <Badge :label="extraction.status || __('Pending')" :theme="extraction.status === 'Extracted' ? 'green' : 'teal'" />
              </div>
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                <MetricCard :label="__('Parser')" :value="extraction.parser || __('Not imported')" icon="cpu" />
                <MetricCard :label="__('Cells')" :value="String(extraction.cell_count || spreadRows.length)" icon="grid" />
                <MetricCard :label="__('Low Confidence')" :value="String((extraction.low_confidence || []).length)" icon="alert-triangle" />
                <MetricCard :label="__('File')" :value="extraction.file_url || __('No file imported')" icon="paperclip" />
              </div>
            </section>

            <section class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
              <div class="p-4 border-b border-slate-200">
                <h3 class="font-bold text-slate-800">{{ __('Cells Needing Manual Review') }}</h3>
              </div>
              <table class="w-full text-sm">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left">{{ __('Metric') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Year') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Confidence') }}</th>
                    <th class="py-3 px-4 text-left">{{ __('Status') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="cell in extraction.low_confidence || []" :key="`${cell.metric_key}-${cell.year}`" class="border-b border-slate-100">
                    <td class="py-3 px-4 font-semibold text-slate-800">{{ cell.metric_label || cell.metric_key }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ cell.year }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ formatPercent(cell.confidence) }}</td>
                    <td class="py-3 px-4"><Badge :label="cell.status" theme="orange" variant="subtle" /></td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>

          <div v-else-if="activeTab === 'ratios'" class="space-y-5">
            <div class="grid grid-cols-1 xl:grid-cols-4 gap-4">
              <MetricCard :label="__('Current Ratio')" :value="ratioValue('current_ratio')" icon="droplet" />
              <MetricCard :label="__('Debt / Equity')" :value="ratioValue('debt_to_equity')" icon="bar-chart-2" />
              <MetricCard :label="__('Net Margin')" :value="ratioValue('net_margin', true)" icon="trending-up" />
              <MetricCard :label="__('CAGR Revenue')" :value="formatPercent(trend.cagr)" icon="activity" />
            </div>

            <section class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
              <div class="p-4 border-b border-slate-200 flex items-center justify-between">
                <h3 class="font-bold text-slate-800">{{ __('Ratios, YoY Flags, Common Size') }}</h3>
                <Button variant="outline" size="sm" :loading="busy" :label="__('Recalculate')" @click="recalculateRatios" />
              </div>
              <table class="w-full text-sm min-w-[920px]">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left">{{ __('Category') }}</th>
                    <th class="py-3 px-4 text-left">{{ __('Ratio') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Year') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Value') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Threshold') }}</th>
                    <th class="py-3 px-4 text-left">{{ __('Status') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Benchmark') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in ratios" :key="`${row.key}-${row.year}`" class="border-b border-slate-100">
                    <td class="py-3 px-4 text-xs font-semibold uppercase text-slate-400">{{ row.category }}</td>
                    <td class="py-3 px-4 font-semibold text-slate-800">{{ row.label }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ row.year }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ row.key.includes('margin') || row.key === 'roa' || row.key === 'roe' || row.key === 'debt_to_assets' ? formatPercent(row.value) : formatNumber(row.value) }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ row.threshold }}</td>
                    <td class="py-3 px-4"><Badge :label="row.status" :theme="row.status === 'Alert' ? 'orange' : 'green'" variant="subtle" /></td>
                    <td class="py-3 px-4 text-right font-mono">{{ row.benchmark_median ?? '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>

          <div v-else-if="activeTab === 'dscr'" class="space-y-5">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <MetricCard :label="__('Minimum DSCR')" :value="formatNumber(dscr.min_dscr)" icon="shield" />
              <MetricCard :label="__('DSCR Status')" :value="dscr.status || '-'" icon="check-circle" />
              <MetricCard :label="__('Cashflow Status')" :value="cashflow.status || '-'" icon="trending-up" />
            </div>
            <section class="grid grid-cols-1 xl:grid-cols-2 gap-5">
              <div class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
                <div class="p-4 border-b border-slate-200 flex items-center justify-between">
                  <h3 class="font-bold text-slate-800">{{ __('DSCR Sensitivity') }}</h3>
                  <Button variant="outline" size="sm" :loading="busy" :label="__('Run DSCR')" @click="runDscr" />
                </div>
                <table class="w-full text-sm">
                  <thead>
                    <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                      <th class="py-3 px-4 text-left">{{ __('Year') }}</th>
                      <th class="py-3 px-4 text-right">{{ __('-20%') }}</th>
                      <th class="py-3 px-4 text-right">{{ __('Base') }}</th>
                      <th class="py-3 px-4 text-right">{{ __('+20%') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in dscr.items || []" :key="row.year" class="border-b border-slate-100">
                      <td class="py-3 px-4 font-semibold text-slate-800">{{ row.year }}</td>
                      <td class="py-3 px-4 text-right font-mono">{{ formatNumber(row.downside_20) }}</td>
                      <td class="py-3 px-4 text-right font-mono" :class="row.alert ? 'text-orange-600 font-bold' : 'text-slate-800'">{{ formatNumber(row.base) }}</td>
                      <td class="py-3 px-4 text-right font-mono">{{ formatNumber(row.upside_20) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
                <div class="p-4 border-b border-slate-200 flex items-center justify-between">
                  <h3 class="font-bold text-slate-800">{{ __('Cashflow Projection') }}</h3>
                  <Button variant="outline" size="sm" :loading="busy" :label="__('Project')" @click="runCashflow" />
                </div>
                <table class="w-full text-sm">
                  <thead>
                    <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                      <th class="py-3 px-4 text-left">{{ __('Year') }}</th>
                      <th class="py-3 px-4 text-right">{{ __('Period CF') }}</th>
                      <th class="py-3 px-4 text-right">{{ __('Cumulative') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in cashflow.items || []" :key="row.year" class="border-b border-slate-100">
                      <td class="py-3 px-4 font-semibold text-slate-800">{{ row.year }}</td>
                      <td class="py-3 px-4 text-right font-mono">{{ formatCurrency(row.period_cf) }}</td>
                      <td class="py-3 px-4 text-right font-mono" :class="row.cash_gap_alert ? 'text-orange-600 font-bold' : 'text-slate-800'">{{ formatCurrency(row.cumulative_cf) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>
          </div>

          <div v-else-if="activeTab === 'benchmark'" class="space-y-5">
            <section class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <h3 class="font-bold text-slate-800">{{ __('Industry Benchmarking') }}</h3>
                  <p class="text-sm text-slate-500 mt-1">{{ benchmark.industry || __('General Commercial') }} - KBLI {{ selectedApp.kbli || __('default') }}</p>
                </div>
                <Badge label="Median / Q1 / Q3" theme="teal" variant="subtle" />
              </div>
              <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mt-4">
                <MetricCard v-for="(value, key) in benchmark.median || {}" :key="key" :label="labelize(key)" :value="formatNumber(value)" icon="bar-chart" />
              </div>
            </section>

            <section class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
              <div class="p-4 border-b border-slate-200">
                <h3 class="font-bold text-slate-800">{{ __('Peer Comparison') }}</h3>
              </div>
              <table class="w-full text-sm">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left">{{ __('Peer') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Current Ratio') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Debt / Equity') }}</th>
                    <th class="py-3 px-4 text-right">{{ __('Net Margin') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="peer in peers.peers || []" :key="peer.name" class="border-b border-slate-100">
                    <td class="py-3 px-4 font-semibold text-slate-800">{{ peer.name }} <Badge v-if="peer.type === 'Borrower'" label="Borrower" theme="teal" variant="subtle" /></td>
                    <td class="py-3 px-4 text-right font-mono">{{ formatNumber(peer.current_ratio) }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ formatNumber(peer.debt_to_equity) }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ formatPercent(peer.net_margin) }}</td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>

          <div v-else-if="activeTab === 'risk'" class="space-y-5">
            <div class="grid grid-cols-1 xl:grid-cols-5 gap-4">
              <MetricCard :label="__('Score')" :value="String(riskGrade.score || 0)" icon="activity" />
              <MetricCard :label="__('Grade')" :value="riskGrade.grade || '-'" icon="award" />
              <MetricCard :label="__('Bureau Score')" :value="String(bureau.score || '-')" icon="shield" />
              <MetricCard :label="__('KOL')" :value="bureau.kol_status || 'KOL-1'" icon="check-circle" />
              <MetricCard :label="__('Collateral Items')" :value="String(collaterals.length)" icon="home" />
            </div>

            <section class="grid grid-cols-1 xl:grid-cols-2 gap-5">
              <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
                <h3 class="font-bold text-slate-800 mb-3">{{ __('Risk Grade Breakdown') }}</h3>
                <div class="space-y-3">
                  <div v-for="(value, key) in riskGrade.breakdown || {}" :key="key">
                    <div class="flex justify-between text-sm mb-1">
                      <span class="font-semibold text-slate-700">{{ labelize(key) }}</span>
                      <span class="font-mono text-slate-600">{{ value }}</span>
                    </div>
                    <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div class="h-full bg-teal-600 rounded-full" :style="{ width: `${Math.min(100, value / 4)}%` }"></div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
                <div class="flex items-center justify-between">
                  <h3 class="font-bold text-slate-800">{{ __('Bureau Adapter') }}</h3>
                  <Button variant="outline" size="sm" :loading="busy" :label="__('Refresh')" @click="refreshBureau" />
                </div>
                <div class="mt-4 space-y-3 text-sm">
                  <InfoRow :label="__('Source')" :value="bureau.source || bureau.provider || __('Provider Not Configured')" />
                  <InfoRow :label="__('Score')" :value="String(bureau.score || '-')" />
                  <InfoRow :label="__('Exposure')" :value="formatCurrency(bureau.external_exposure || selectedApp.requested_amount * 0.18)" />
                  <InfoRow :label="__('Status')" :value="bureau.status || __('Manual Upload / Provider Not Configured')" />
                </div>
              </div>
            </section>
          </div>

          <div v-else-if="activeTab === 'scenarios'" class="space-y-5">
            <section class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
              <div class="flex items-center justify-between">
                <h3 class="font-bold text-slate-800">{{ __('Scenario Simulation') }}</h3>
                <Button variant="outline" size="sm" :loading="busy" :label="__('Run Scenario')" @click="runScenario" />
              </div>
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
                <div v-for="scenario in scenarios" :key="scenario.case" class="rounded-lg border border-slate-200 p-4" :class="scenario.case === 'Base' ? 'bg-teal-50 border-teal-200' : 'bg-white'">
                  <div class="flex items-center justify-between">
                    <h4 class="font-bold text-slate-800">{{ scenario.case }}</h4>
                    <Badge :label="scenario.decision" :theme="scenario.dscr >= 1.2 ? 'green' : 'orange'" variant="subtle" />
                  </div>
                  <div class="mt-3 grid grid-cols-2 gap-3 text-sm">
                    <InfoRow :label="__('Revenue')" :value="formatCurrency(scenario.revenue)" />
                    <InfoRow :label="__('EBITDA')" :value="formatCurrency(scenario.ebitda)" />
                    <InfoRow :label="__('DSCR')" :value="formatNumber(scenario.dscr)" />
                    <InfoRow :label="__('Growth')" :value="formatPercent(scenario.revenue_growth)" />
                  </div>
                </div>
              </div>
            </section>

            <section class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
              <div class="flex items-center justify-between">
                <h3 class="font-bold text-slate-800">{{ __('Sensitivity Heatmap') }}</h3>
                <Button variant="outline" size="sm" :loading="busy" :label="__('Run Sensitivity')" @click="runSensitivity" />
              </div>
              <div class="overflow-x-auto mt-4">
                <table class="text-xs min-w-[620px]">
                  <tbody>
                    <tr v-for="row in sensitivity.matrix || []" :key="row.revenue_delta">
                      <td class="w-28 p-2 text-right font-semibold text-slate-500">{{ formatPercent(row.revenue_delta) }}</td>
                      <td v-for="(cell, idx) in row.cells" :key="idx" class="p-1">
                        <div class="w-24 rounded px-2 py-2 text-center font-mono" :class="cell.status === 'Alert' ? 'bg-orange-100 text-orange-800' : 'bg-teal-50 text-teal-800'">
                          {{ formatNumber(cell.value) }}
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>
          </div>

          <div v-else-if="activeTab === 'collateral'" class="space-y-5">
            <section class="grid grid-cols-1 xl:grid-cols-2 gap-5">
              <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
                <h3 class="font-bold text-slate-800 mb-3">{{ __('Collateral Coverage') }}</h3>
                <div class="space-y-3">
                  <div v-for="col in collaterals" :key="col.name || col.asset" class="rounded-lg border border-slate-100 bg-slate-50 p-3">
                    <div class="flex items-center justify-between gap-3">
                      <div class="font-semibold text-slate-800">{{ col.asset || __('Collateral') }}</div>
                      <Badge :label="`${formatNumber(col.computed_ltv_percent || col.ltv_percent)}% LTV`" :theme="(col.computed_ltv_percent || col.ltv_percent) > 80 ? 'orange' : 'green'" variant="subtle" />
                    </div>
                    <div class="mt-2 text-xs text-slate-500">{{ col.collateral_type || __('Asset') }} - {{ formatCurrency(col.collateral_value) }} - {{ col.reappraisal_trigger ? __('Re-appraisal Triggered') : __('Re-appraisal Not Required') }}</div>
                  </div>
                  <div v-if="collaterals.length === 0" class="text-sm text-slate-400">{{ __('No collateral records yet.') }}</div>
                </div>
              </div>

              <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
                <div class="flex items-center justify-between">
                  <h3 class="font-bold text-slate-800">{{ __('News & Sentiment Scan') }}</h3>
                  <Button variant="outline" size="sm" :loading="busy" :label="__('Scan')" @click="scanNews" />
                </div>
                <div class="grid grid-cols-2 gap-3 mt-4">
                  <MetricCard :label="__('Sentiment')" :value="String(newsSentiment.sentiment_score || 0)" icon="activity" />
                  <MetricCard :label="__('Adverse Flags')" :value="String((newsSentiment.adverse_flags || []).length)" icon="alert-triangle" />
                </div>
                <div class="mt-4 space-y-2">
                  <div v-for="source in newsSentiment.sources || []" :key="source.url || source.title" class="rounded border border-slate-100 bg-slate-50 p-3 text-sm">
                    <div class="font-semibold text-slate-800">{{ source.title }}</div>
                    <a v-if="source.url" :href="source.url" target="_blank" rel="noreferrer" class="text-xs text-teal-700 hover:underline">{{ source.url }}</a>
                  </div>
                </div>
              </div>
            </section>
          </div>

          <div v-else-if="activeTab === 'memo'" class="space-y-5">
            <section class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <h3 class="font-bold text-slate-800">{{ __('AI Executive Summary, Memo, Recommendation') }}</h3>
                <div class="flex gap-2 flex-wrap">
                  <Button variant="outline" size="sm" :loading="busy" :label="__('Generate Summary')" @click="generateSummary" />
                  <Button variant="outline" size="sm" :loading="busy" :label="__('Generate Memo')" @click="generateMemo" />
                  <Button variant="outline" size="sm" :loading="busy" :label="__('Recommend')" @click="generateRecommendation" />
                  <Button variant="outline" size="sm" :loading="busy" :label="__('Export PDF')" @click="exportMemo" />
                </div>
              </div>
              <div class="grid grid-cols-1 xl:grid-cols-3 gap-4 mt-4">
                <MetricCard :label="__('Decision')" :value="recommendation.decision || '-'" icon="thumbs-up" />
                <MetricCard :label="__('Confidence')" :value="`${recommendation.confidence || 0}%`" icon="percent" />
                <MetricCard :label="__('Version')" :value="memo.version || '-'" icon="git-commit" />
              </div>
            </section>

            <section class="grid grid-cols-1 xl:grid-cols-3 gap-5">
              <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
                <h3 class="font-bold text-slate-800 mb-3">{{ __('Executive Summary') }}</h3>
                <ul class="space-y-2 text-sm text-slate-700">
                  <li v-for="item in memo.summary_bullets || []" :key="item" class="rounded border border-slate-100 bg-slate-50 p-2">{{ item }}</li>
                </ul>
              </div>
              <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4 xl:col-span-2">
                <h3 class="font-bold text-slate-800 mb-3">{{ __('Credit Memo Editor') }}</h3>
                <textarea
                  v-model="memoContent"
                  class="h-[360px] w-full rounded-lg border border-slate-200 p-4 text-sm leading-relaxed text-slate-700 focus:outline-none focus:border-teal-600"
                  :placeholder="__('Generate or write the memorandum...')"
                ></textarea>
              </div>
            </section>
          </div>

          <div v-else-if="activeTab === 'proof'" class="space-y-5">
            <section class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <h3 class="font-bold text-slate-800">{{ __('UAT Proof Pack') }}</h3>
                  <p class="text-sm text-slate-500 mt-1">{{ __('Evidence for 07_CreditAnalysis and AI Agent Center demo walkthrough.') }}</p>
                </div>
                <Badge :label="`${proofRows.length} Evidence Rows`" theme="teal" variant="subtle" />
              </div>
            </section>
            <section class="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
              <table class="w-full text-sm min-w-[900px]">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left">{{ __('Feature') }}</th>
                    <th class="py-3 px-4 text-left">{{ __('Status') }}</th>
                    <th class="py-3 px-4 text-left">{{ __('API') }}</th>
                    <th class="py-3 px-4 text-left">{{ __('Demo Step') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in proofRows" :key="row.feature_key" class="border-b border-slate-100">
                    <td class="py-3 px-4">
                      <div class="font-semibold text-slate-800">{{ row.feature }}</div>
                      <div class="text-xs text-slate-500 mt-1">{{ row.acceptance }}</div>
                    </td>
                    <td class="py-3 px-4"><Badge :label="row.status" theme="green" variant="subtle" /></td>
                    <td class="py-3 px-4 font-mono text-xs text-slate-600">{{ row.api }}</td>
                    <td class="py-3 px-4 text-xs text-slate-500">{{ (row.evidence || [])[0] || row.route }}</td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, FeatherIcon, Badge, FileUploader, usePageMeta, toast, createResource, call } from 'frappe-ui'
import { computed, h, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const MetricCard = {
  props: ['label', 'value', 'icon'],
  setup(props) {
    return () => h('div', { class: 'rounded-lg border border-slate-100 bg-white p-4 shadow-sm' }, [
      h('div', { class: 'flex items-center gap-2 text-xs font-semibold uppercase text-slate-400' }, [
        h(FeatherIcon, { name: props.icon, class: 'h-4 w-4 text-teal-600' }),
        props.label,
      ]),
      h('div', { class: 'mt-2 text-lg font-bold text-slate-800 truncate' }, props.value),
    ])
  },
}

const InfoRow = {
  props: ['label', 'value'],
  setup(props) {
    return () => h('div', { class: 'flex justify-between gap-4 border-b border-slate-100 pb-2' }, [
      h('span', { class: 'text-slate-500' }, props.label),
      h('span', { class: 'font-semibold text-slate-800 text-right' }, props.value),
    ])
  },
}

const searchQuery = ref('')
const selectedApp = ref(null)
const activeTab = ref('spreading')
const memoContent = ref('')
const spreadRows = ref([])
const importResult = ref(null)
const busy = ref(false)
const route = useRoute()
const router = useRouter()
const routeApplication = computed(() => String(route.params.applicationId || ''))

const tabs = [
  { key: 'spreading', label: 'Financial Spreading' },
  { key: 'extraction', label: 'AI Extraction' },
  { key: 'ratios', label: 'Ratios & Trends' },
  { key: 'dscr', label: 'DSCR & Cashflow' },
  { key: 'benchmark', label: 'Benchmark & Peers' },
  { key: 'risk', label: 'Risk Grade' },
  { key: 'scenarios', label: 'Scenarios & Sensitivity' },
  { key: 'collateral', label: 'Collateral & News' },
  { key: 'memo', label: 'Memo & Approval' },
]

const queue = createResource({
  url: 'crm.api.credit.get_credit_application_queue',
  auto: true,
  onSuccess(data) {
    if (routeApplication.value) loadRouteApplication()
    else if (!selectedApp.value && data?.length) selectApp(data[0])
  },
})

const analysis = createResource({
  url: 'crm.api.credit.get_credit_analysis',
  makeParams() {
    return { application_id: selectedApp.value?.name }
  },
  onSuccess(data) {
    spreadRows.value = (data?.spreading || []).map((row) => ({ ...row }))
    memoContent.value = data?.memo?.content || ''
  },
})

const applications = computed(() => queue.data || [])
const workspace = computed(() => analysis.data || {})
const filteredApps = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return applications.value
  return applications.value.filter((app) =>
    [app.borrower_name, app.name, app.facility_type, app.public_company_ticker, app.borrower_type, app.industry]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(q)),
  )
})

const years = computed(() => [...new Set(spreadRows.value.map((row) => Number(row.year)).filter(Boolean))].sort())
const balanceChecks = computed(() => workspace.value.balance_checks || [])
const balanceStatus = computed(() => (balanceChecks.value.every((row) => row.status === 'Balanced') ? __('Balanced') : __('Review')))
const ratios = computed(() => workspace.value.ratios || [])
const dscr = computed(() => workspace.value.dscr || {})
const trend = computed(() => workspace.value.trend || {})
const benchmark = computed(() => workspace.value.benchmark || {})
const peers = computed(() => workspace.value.peers || {})
const riskGrade = computed(() => workspace.value.risk_grade || {})
const scenarios = computed(() => workspace.value.scenarios || [])
const sensitivity = computed(() => workspace.value.sensitivity || {})
const cashflow = computed(() => workspace.value.cashflow || {})
const collaterals = computed(() => workspace.value.collaterals || [])
const bureau = computed(() => workspace.value.bureau || {})
const newsSentiment = computed(() => workspace.value.news_sentiment || {})
const extraction = computed(() => workspace.value.extraction || {})
const memo = computed(() => workspace.value.memo || {})
const recommendation = computed(() => workspace.value.recommendation || {})
const proofRows = computed(() => workspace.value.proof || [])

const spreadMatrix = computed(() => {
  const groups = new Map()
  for (const row of spreadRows.value) {
    const key = `${row.statement_type}-${row.metric_key}`
    if (!groups.has(key)) {
      groups.set(key, {
        key,
        statement_type: row.statement_type,
        metric_key: row.metric_key,
        metric_label: row.metric_label,
        source: row.source,
        cells: {},
      })
    }
    groups.get(key).cells[row.year] = row
  }
  return [...groups.values()]
})

function selectApp(app) {
  selectedApp.value = app
  activeTab.value = 'spreading'
  importResult.value = null
  analysis.fetch()
}

function loadRouteApplication() {
  if (!routeApplication.value) return
  const row = (queue.data || []).find((app) => app.name === routeApplication.value)
  selectApp(row || { name: routeApplication.value, borrower_name: routeApplication.value, status: 'Pending Review' })
}

function goToCreditList() {
  router.push({ name: 'Credit Analysis' })
}

function initials(value) {
  return (value || 'CA').slice(0, 2).toUpperCase()
}

function statusTheme(status) {
  if (status === 'Approved') return 'green'
  if (status === 'Rejected') return 'red'
  if (status === 'Pending Review') return 'orange'
  if (status === 'Submitted') return 'blue'
  return 'teal'
}

function formatCurrency(value) {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function formatNumber(value) {
  if (value === null || value === undefined || value === '') return '-'
  return new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 }).format(Number(value || 0))
}

function formatPercent(value) {
  return `${formatNumber(Number(value || 0) * 100)}%`
}

function labelize(value) {
  return String(value || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function latestRatio(key) {
  const rows = ratios.value.filter((row) => row.key === key).sort((a, b) => Number(b.year) - Number(a.year))
  return rows[0]?.value
}

function ratioValue(key, percent = false) {
  const value = latestRatio(key)
  return percent ? formatPercent(value) : formatNumber(value)
}

async function runAction(fn, successMessage) {
  if (!selectedApp.value?.name) return
  busy.value = true
  try {
    const result = await fn()
    if (result?.workspace) {
      analysis.data = result.workspace
      spreadRows.value = (result.workspace.spreading || []).map((row) => ({ ...row }))
    } else {
      await analysis.fetch()
    }
    toast.success(successMessage)
  } catch (error) {
    toast.error(error?.messages?.[0] || error.message || __('Credit Analysis action failed'))
  } finally {
    busy.value = false
  }
}

async function saveCurrentSpreading() {
  await runAction(
    () => call('crm.api.credit_analysis.save_spreading', {
      application_id: selectedApp.value.name,
      rows: spreadRows.value,
      status: 'Draft',
    }),
    __('Financial spreading draft saved'),
  )
}

function validateStatementFile(file) {
  const extn = String(file?.name || '').split('.').pop()?.toLowerCase()
  if (!['pdf', 'xlsx', 'xls', 'csv'].includes(extn)) {
    return __('Only PDF, Excel, and CSV files are allowed')
  }
}

async function onStatementUploaded(file) {
  if (!file?.file_url) return
  await runAction(
    async () => {
      const result = await call('crm.api.credit_analysis.import_statement_file', {
      application_id: selectedApp.value.name,
        file_url: file.file_url,
      })
      importResult.value = result
      if (result?.errors?.length) {
        throw new Error(result.errors.join('\n'))
      }
      return result
    },
    __('Financial statement imported'),
  )
}

async function recalculateRatios() {
  await runAction(() => call('crm.api.credit_analysis.calculate_ratios', { application_id: selectedApp.value.name }), __('Ratios recalculated'))
}

async function runDscr() {
  await runAction(() => call('crm.api.credit_analysis.calculate_dscr', { application_id: selectedApp.value.name }), __('DSCR calculated'))
}

async function runCashflow() {
  await runAction(() => call('crm.api.credit_analysis.run_cashflow_projection', { application_id: selectedApp.value.name }), __('Cashflow projection updated'))
}

async function refreshBureau() {
  await runAction(() => call('crm.api.credit_analysis.refresh_bureau_report', { application_id: selectedApp.value.name }), __('Bureau adapter refreshed'))
}

async function runScenario() {
  await runAction(() => call('crm.api.credit_analysis.run_scenario', { application_id: selectedApp.value.name }), __('Scenario simulation updated'))
}

async function runSensitivity() {
  await runAction(() => call('crm.api.credit_analysis.run_sensitivity', { application_id: selectedApp.value.name }), __('Sensitivity heatmap updated'))
}

async function scanNews() {
  await runAction(() => call('crm.api.credit_analysis.scan_news_sentiment', { application_id: selectedApp.value.name }), __('News sentiment scan updated'))
}

async function generateSummary() {
  await runAction(() => call('crm.api.credit_analysis.generate_credit_summary', { application_id: selectedApp.value.name }), __('AI executive summary generated'))
}

async function generateMemo() {
  await runAction(async () => {
    const result = await call('crm.api.credit_analysis.generate_credit_memo', { application_id: selectedApp.value.name })
    memoContent.value = result.content || memoContent.value
    return result
  }, __('AI credit memo generated'))
}

async function generateRecommendation() {
  await runAction(() => call('crm.api.credit_analysis.generate_credit_recommendation', { application_id: selectedApp.value.name }), __('AI recommendation generated'))
}

async function submitApproval() {
  await runAction(() => call('crm.api.credit_analysis.submit_memo_for_approval', { application_id: selectedApp.value.name }), __('Memo submitted to approval route'))
}

async function exportMemo() {
  await runAction(() => call('crm.api.credit_analysis.export_credit_memo_pdf', { application_id: selectedApp.value.name, watermark: 'Internal' }), __('Memo export queued'))
}

onMounted(() => {
  if (routeApplication.value) loadRouteApplication()
  else if (queue.data?.length && !selectedApp.value) selectApp(queue.data[0])
})

watch(routeApplication, () => {
  loadRouteApplication()
})

usePageMeta(() => ({ title: 'Credit Analysis' }))
</script>

<style scoped>
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
