<template>
  <div class="flex h-full bg-slate-50 font-sans">
    <!-- Sidebar: Application Queue -->
    <div class="w-80 border-r border-slate-200 bg-white flex flex-col shrink-0">
      <div class="p-4 border-b border-slate-200">
        <h2 class="text-lg font-bold text-slate-800 mb-3">{{ __('Credit App Queue') }}</h2>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search Borrower or App ID')"
            class="w-full pl-9 pr-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-600 focus:bg-white transition-all"
          />
          <span class="absolute left-3 top-2.5 text-slate-400">
            <FeatherIcon name="search" class="h-4 w-4" />
          </span>
        </div>
      </div>

      <!-- Queue List -->
      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div
          v-for="app in filteredApps"
          :key="app.id"
          @click="selectApp(app)"
          class="flex flex-col gap-1 p-3 rounded-lg cursor-pointer transition-all hover:bg-slate-50 border"
          :class="selectedApp?.id === app.id ? 'bg-teal-50 border-teal-200' : 'border-transparent'"
        >
          <div class="flex justify-between items-start">
            <div class="font-semibold text-sm text-slate-800 truncate">{{ app.borrower }}</div>
            <Badge :label="app.status" :theme="app.status === 'In Progress' ? 'orange' : 'teal'" size="sm" variant="subtle" />
          </div>
          <div class="text-xs text-slate-500 truncate flex items-center gap-2 mt-0.5">
            <span class="font-mono text-slate-600">{{ app.id }}</span>
            <span class="w-1 h-1 rounded-full bg-slate-300"></span>
            <span>{{ app.facility }}</span>
          </div>
          <div class="text-xs font-bold text-slate-700 mt-1">
            Rp {{ app.amount }}B
          </div>
        </div>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <div v-if="!selectedApp" class="flex-1 flex flex-col items-center justify-center text-slate-400 p-8">
        <div class="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center mb-4">
          <FeatherIcon name="file-text" class="h-10 w-10 text-slate-300" />
        </div>
        <h3 class="text-lg font-semibold text-slate-700">{{ __('No Application Selected') }}</h3>
        <p class="text-sm text-slate-500 mt-1 max-w-sm text-center">
          {{ __('Select an application from the queue to perform credit analysis and generate CAM.') }}
        </p>
      </div>

      <div v-else class="flex-1 flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="bg-white border-b border-slate-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shrink-0 shadow-sm">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-xl bg-teal-600 text-white flex items-center justify-center font-black text-2xl shadow-md shadow-teal-600/10 shrink-0">
              {{ selectedApp.borrower.slice(0, 2).toUpperCase() }}
            </div>
            <div>
              <div class="flex items-center gap-3">
                <h1 class="text-2xl font-bold text-slate-800">{{ selectedApp.borrower }}</h1>
                <Badge :label="selectedApp.status" :theme="selectedApp.status === 'In Progress' ? 'orange' : 'teal'" variant="solid" />
              </div>
              <div class="text-sm text-slate-500 flex flex-wrap items-center gap-4 mt-1.5">
                <span class="flex items-center gap-1">
                  <FeatherIcon name="hash" class="h-3.5 w-3.5 text-slate-400" />
                  App: {{ selectedApp.id }}
                </span>
                <span class="flex items-center gap-1">
                  <FeatherIcon name="briefcase" class="h-3.5 w-3.5 text-slate-400" />
                  {{ selectedApp.industry }} (KBLI: {{ selectedApp.kbli }})
                </span>
                <span class="flex items-center gap-1 font-bold text-slate-700">
                  <FeatherIcon name="dollar-sign" class="h-3.5 w-3.5 text-slate-500" />
                  Req: Rp {{ selectedApp.amount }}B
                </span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <Button variant="outline" :label="__('Save Draft')" @click="triggerSave" />
            <Button variant="solid" :label="__('Submit to Committee')" @click="triggerSubmit">
              <template #prefix>
                <FeatherIcon name="check-circle" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>

        <!-- Custom Tabs Component -->
        <div class="px-6 pt-4 shrink-0 bg-white border-b border-slate-200">
          <div class="flex gap-6">
            <button
              v-for="t in tabs"
              :key="t.key"
              @click="activeTab = t.key"
              class="pb-3 text-sm font-semibold border-b-2 transition-all"
              :class="activeTab === t.key ? 'border-teal-600 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <!-- Scrollable Tab Content Panels -->
        <div class="flex-1 overflow-y-auto p-6 min-h-0">
          <!-- 1. Spreading & Financials -->
          <div v-if="activeTab === 'financials'" class="space-y-6">
            <div class="flex justify-between items-center">
              <h3 class="font-bold text-slate-800 text-lg">{{ __('Automated Financial Spreading') }}</h3>
              <Button variant="outline" size="sm" :label="__('AI OCR Extract from PDF')" @click="triggerOCR" iconLeft="zap" />
            </div>

            <!-- Financial Grid -->
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm overflow-x-auto">
              <table class="w-full text-sm min-w-[700px]">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left font-bold w-1/4">{{ __('P&L Items (Rp Bn)') }}</th>
                    <th class="py-3 px-4 text-right font-bold w-1/6">{{ __('2023 (Audited)') }}</th>
                    <th class="py-3 px-4 text-right font-bold w-1/6">{{ __('2024 (Audited)') }}</th>
                    <th class="py-3 px-4 text-right font-bold w-1/6">{{ __('YoY %') }}</th>
                    <th class="py-3 px-4 text-right font-bold w-1/6">{{ __('2025 (Proj)') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ __('Revenue') }}</td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.rev23" class="w-full text-right p-1 border rounded focus:border-teal-500 focus:outline-none" /></td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.rev24" class="w-full text-right p-1 border rounded focus:border-teal-500 focus:outline-none" /></td>
                    <td class="py-3 px-4 text-right">
                      <Badge :label="calcYoY(finData.rev23, finData.rev24)" :theme="getYoYTheme(finData.rev23, finData.rev24)" />
                    </td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.rev25" class="w-full text-right p-1 border rounded bg-slate-50 focus:border-teal-500 focus:outline-none" /></td>
                  </tr>
                  <tr class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ __('EBITDA') }}</td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.ebitda23" class="w-full text-right p-1 border rounded focus:border-teal-500 focus:outline-none" /></td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.ebitda24" class="w-full text-right p-1 border rounded focus:border-teal-500 focus:outline-none" /></td>
                    <td class="py-3 px-4 text-right">
                      <Badge :label="calcYoY(finData.ebitda23, finData.ebitda24)" :theme="getYoYTheme(finData.ebitda23, finData.ebitda24)" />
                    </td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.ebitda25" class="w-full text-right p-1 border rounded bg-slate-50 focus:border-teal-500 focus:outline-none" /></td>
                  </tr>
                  <tr class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ __('Interest Exp') }}</td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.int23" class="w-full text-right p-1 border rounded focus:border-teal-500 focus:outline-none" /></td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.int24" class="w-full text-right p-1 border rounded focus:border-teal-500 focus:outline-none" /></td>
                    <td class="py-3 px-4 text-right">
                      <Badge :label="calcYoY(finData.int23, finData.int24)" :theme="getYoYTheme(finData.int24, finData.int23)" /> <!-- lower is better -->
                    </td>
                    <td class="py-3 px-4"><input type="number" v-model.number="finData.int25" class="w-full text-right p-1 border rounded bg-slate-50 focus:border-teal-500 focus:outline-none" /></td>
                  </tr>
                  <tr class="border-b border-slate-100 bg-slate-50">
                    <td class="py-3 px-4 text-slate-800 font-bold">{{ __('Auto DSCR') }}</td>
                    <td class="py-3 px-4 text-right font-mono font-bold">{{ (finData.ebitda23 / (finData.int23 + 2)).toFixed(2) }}x</td>
                    <td class="py-3 px-4 text-right font-mono font-bold">{{ (finData.ebitda24 / (finData.int24 + 2)).toFixed(2) }}x</td>
                    <td class="py-3 px-4 text-right"></td>
                    <td class="py-3 px-4 text-right font-mono font-bold text-teal-700">{{ (finData.ebitda25 / (finData.int25 + 2)).toFixed(2) }}x</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Key Ratios -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h4 class="font-bold text-slate-700 mb-4">{{ __('Liquidity (Current Ratio)') }}</h4>
                <div class="flex items-end gap-3 h-24 pb-2 border-b border-slate-100">
                  <div class="w-1/3 bg-teal-100 rounded-t flex items-end justify-center" style="height: 50%"><span class="text-xs mb-1 font-bold">1.2</span></div>
                  <div class="w-1/3 bg-teal-300 rounded-t flex items-end justify-center" style="height: 60%"><span class="text-xs mb-1 font-bold">1.4</span></div>
                  <div class="w-1/3 bg-teal-600 rounded-t flex items-end justify-center" style="height: 80%"><span class="text-xs text-white mb-1 font-bold">1.8</span></div>
                </div>
                <div class="text-xs text-slate-500 mt-2 text-center">Industry Avg: 1.5</div>
              </div>
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h4 class="font-bold text-slate-700 mb-4">{{ __('Leverage (DER)') }}</h4>
                <div class="flex items-end gap-3 h-24 pb-2 border-b border-slate-100">
                  <div class="w-1/3 bg-orange-600 rounded-t flex items-end justify-center" style="height: 90%"><span class="text-xs text-white mb-1 font-bold">2.1</span></div>
                  <div class="w-1/3 bg-orange-400 rounded-t flex items-end justify-center" style="height: 70%"><span class="text-xs mb-1 font-bold">1.8</span></div>
                  <div class="w-1/3 bg-teal-500 rounded-t flex items-end justify-center" style="height: 50%"><span class="text-xs text-white mb-1 font-bold">1.4</span></div>
                </div>
                <div class="text-xs text-slate-500 mt-2 text-center">Threshold: < 2.0</div>
              </div>
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h4 class="font-bold text-slate-700 mb-4">{{ __('Profitability (EBITDA Margin)') }}</h4>
                <div class="flex items-end gap-3 h-24 pb-2 border-b border-slate-100">
                  <div class="w-1/3 bg-teal-200 rounded-t flex items-end justify-center" :style="{ height: (finData.ebitda23/finData.rev23*100*3) + '%' }"></div>
                  <div class="w-1/3 bg-teal-400 rounded-t flex items-end justify-center" :style="{ height: (finData.ebitda24/finData.rev24*100*3) + '%' }"></div>
                  <div class="w-1/3 bg-teal-600 rounded-t flex items-end justify-center" :style="{ height: (finData.ebitda25/finData.rev25*100*3) + '%' }"></div>
                </div>
                <div class="text-xs text-slate-500 mt-2 text-center">Auto-calculated from Spreading</div>
              </div>
            </div>
          </div>

          <!-- 2. Risk & Scoring -->
          <div v-if="activeTab === 'risk'" class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Internal Risk Engine -->
              <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <div class="flex justify-between items-center mb-6">
                  <h3 class="font-bold text-slate-800 text-lg">{{ __('Internal Risk Engine') }}</h3>
                  <Badge label="Grade: 2A" theme="emerald" size="lg" />
                </div>
                <div class="space-y-4">
                  <div>
                    <div class="flex justify-between text-sm mb-1">
                      <span class="text-slate-600 font-semibold">Financial Score</span>
                      <span class="text-slate-800 font-bold">340 / 400</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2"><div class="bg-teal-500 h-2 rounded-full" style="width: 85%"></div></div>
                  </div>
                  <div>
                    <div class="flex justify-between text-sm mb-1">
                      <span class="text-slate-600 font-semibold">Management Quality</span>
                      <span class="text-slate-800 font-bold">280 / 300</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2"><div class="bg-teal-500 h-2 rounded-full" style="width: 93%"></div></div>
                  </div>
                  <div>
                    <div class="flex justify-between text-sm mb-1">
                      <span class="text-slate-600 font-semibold">Industry Outlook</span>
                      <span class="text-slate-800 font-bold">150 / 300</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2"><div class="bg-orange-500 h-2 rounded-full" style="width: 50%"></div></div>
                  </div>
                </div>
                <div class="mt-6 pt-6 border-t border-slate-100">
                  <div class="flex justify-between items-center text-lg">
                    <span class="font-bold text-slate-800">Total Obligor Score</span>
                    <span class="font-black text-teal-600">770 / 1000</span>
                  </div>
                </div>
              </div>

              <!-- SLIK / Bureau Integration -->
              <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <div class="flex justify-between items-center mb-6">
                  <h3 class="font-bold text-slate-800 text-lg">{{ __('External Bureau (SLIK)') }}</h3>
                  <Button variant="outline" size="sm" :label="__('Pull Latest Report')" @click="triggerOCR" iconLeft="refresh-cw" />
                </div>
                <div class="space-y-4">
                  <div class="flex items-center gap-4 p-4 border border-slate-100 rounded-lg bg-slate-50">
                    <div class="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-xl">1</div>
                    <div>
                      <div class="font-bold text-slate-800">KOL Status (Current)</div>
                      <div class="text-sm text-slate-500">Lancar / Performing Loan</div>
                    </div>
                  </div>
                  <div class="flex justify-between items-center p-3 border-b border-slate-100">
                    <span class="text-sm text-slate-600">Total External Exposure</span>
                    <span class="text-sm font-bold text-slate-800">Rp 12.4B</span>
                  </div>
                  <div class="flex justify-between items-center p-3 border-b border-slate-100">
                    <span class="text-sm text-slate-600">Worst Historical KOL (24m)</span>
                    <span class="text-sm font-bold text-slate-800">2 (Dalam Perhatian Khusus)</span>
                  </div>
                </div>
              </div>

              <!-- Collateral Coverage (LTV) -->
              <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm lg:col-span-2">
                <h3 class="font-bold text-slate-800 text-lg mb-4">{{ __('Collateral Coverage (LTV)') }}</h3>
                <div class="flex items-center gap-6 p-4 bg-teal-50 rounded-xl border border-teal-100">
                  <div class="flex-1">
                    <div class="text-xs font-bold text-teal-800 uppercase">Proposed Loan Limit</div>
                    <div class="text-2xl font-black text-teal-900 mt-1">Rp 20.0B</div>
                  </div>
                  <div class="h-12 w-px bg-teal-200"></div>
                  <div class="flex-1">
                    <div class="text-xs font-bold text-teal-800 uppercase">Total Collateral Value</div>
                    <div class="text-2xl font-black text-teal-900 mt-1">Rp 32.5B</div>
                  </div>
                  <div class="h-12 w-px bg-teal-200"></div>
                  <div class="flex-1">
                    <div class="text-xs font-bold text-teal-800 uppercase">LTV (Loan to Value)</div>
                    <div class="text-2xl font-black mt-1" :class="20.0/32.5 > 0.8 ? 'text-red-600' : 'text-teal-900'">
                      {{ ((20.0 / 32.5) * 100).toFixed(1) }}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. Sensitivity & Scenarios -->
          <div v-if="activeTab === 'scenarios'" class="space-y-6">
            <h3 class="font-bold text-slate-800 text-lg">{{ __('Scenario Simulation & Stress Testing') }}</h3>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col items-center justify-center text-center hover:bg-slate-50 cursor-pointer transition-colors border-l-4 border-l-emerald-500">
                <h4 class="font-bold text-slate-800 mb-2">Best Case</h4>
                <p class="text-xs text-slate-500 mb-4">+10% Rev, -2% Interest</p>
                <Badge label="Proj DSCR: 1.8x" theme="emerald" />
              </div>
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col items-center justify-center text-center border-2 border-teal-500 shadow-teal-500/20">
                <h4 class="font-bold text-slate-800 mb-2">Base Case</h4>
                <p class="text-xs text-slate-500 mb-4">Baseline Projections</p>
                <Badge label="Proj DSCR: 1.4x" theme="teal" />
              </div>
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col items-center justify-center text-center hover:bg-slate-50 cursor-pointer transition-colors border-l-4 border-l-red-500">
                <h4 class="font-bold text-slate-800 mb-2">Worst Case</h4>
                <p class="text-xs text-slate-500 mb-4">-15% Rev, +3% Interest</p>
                <Badge label="Proj DSCR: 0.9x" theme="red" />
              </div>
            </div>

            <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mt-6">
              <h3 class="font-bold text-slate-800 text-md mb-4">{{ __('Sensitivity Heatmap (DSCR)') }}</h3>
              <div class="overflow-x-auto">
                <table class="w-full text-sm text-center">
                  <thead>
                    <tr>
                      <th class="p-2 border border-slate-200 bg-slate-50">Rev / Rate</th>
                      <th class="p-2 border border-slate-200 bg-slate-50">-2% (Rate)</th>
                      <th class="p-2 border border-slate-200 bg-slate-50">Base Rate</th>
                      <th class="p-2 border border-slate-200 bg-slate-50">+2% (Rate)</th>
                      <th class="p-2 border border-slate-200 bg-slate-50">+5% (Rate)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="p-2 border border-slate-200 bg-slate-50 font-bold">+10% Rev</td>
                      <td class="p-2 border border-slate-200 bg-emerald-200 text-emerald-900 font-bold">1.82</td>
                      <td class="p-2 border border-slate-200 bg-emerald-100 text-emerald-900 font-bold">1.65</td>
                      <td class="p-2 border border-slate-200 bg-yellow-100 text-yellow-900 font-bold">1.40</td>
                      <td class="p-2 border border-slate-200 bg-orange-200 text-orange-900 font-bold">1.15</td>
                    </tr>
                    <tr>
                      <td class="p-2 border border-slate-200 bg-slate-50 font-bold">Base Rev</td>
                      <td class="p-2 border border-slate-200 bg-emerald-100 text-emerald-900 font-bold">1.60</td>
                      <td class="p-2 border border-slate-200 bg-white font-bold">1.42</td>
                      <td class="p-2 border border-slate-200 bg-orange-100 text-orange-900 font-bold">1.18</td>
                      <td class="p-2 border border-slate-200 bg-red-200 text-red-900 font-bold">0.95</td>
                    </tr>
                    <tr>
                      <td class="p-2 border border-slate-200 bg-slate-50 font-bold">-10% Rev</td>
                      <td class="p-2 border border-slate-200 bg-yellow-100 text-yellow-900 font-bold">1.35</td>
                      <td class="p-2 border border-slate-200 bg-orange-200 text-orange-900 font-bold">1.10</td>
                      <td class="p-2 border border-slate-200 bg-red-200 text-red-900 font-bold">0.85</td>
                      <td class="p-2 border border-slate-200 bg-red-400 text-white font-bold">0.65</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 4. AI Memorandum -->
          <div v-if="activeTab === 'memo'" class="space-y-6">
            <div class="flex justify-between items-center">
              <h3 class="font-bold text-slate-800 text-lg">{{ __('Credit Analysis Memorandum (CAM)') }}</h3>
              <Button variant="solid" size="sm" :label="__('Generate AI Draft')" @click="generateMemo" iconLeft="cpu" />
            </div>

            <!-- Editor area -->
            <div class="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-[500px]">
              <div class="bg-slate-50 border-b border-slate-200 p-2 flex gap-2">
                <Button variant="subtle" size="sm" icon="bold" />
                <Button variant="subtle" size="sm" icon="italic" />
                <Button variant="subtle" size="sm" icon="list" />
                <div class="w-px h-6 bg-slate-300 mx-2"></div>
                <Button variant="subtle" size="sm" :label="__('Insert Ratios Table')" />
                <Button variant="subtle" size="sm" :label="__('Insert Heatmap')" />
              </div>
              <textarea
                v-model="memoContent"
                class="flex-1 w-full p-6 focus:outline-none resize-none text-sm text-slate-700 leading-relaxed font-serif"
                placeholder="Click 'Generate AI Draft' to auto-populate the memorandum..."
              ></textarea>
            </div>

            <div class="flex justify-between items-center bg-teal-50 border border-teal-100 rounded-xl p-5">
              <div>
                <h4 class="font-bold text-teal-900">{{ __('AI Recommendation') }}</h4>
                <p class="text-sm text-teal-800 mt-1 max-w-2xl">
                  Based on DSCR > 1.2, positive YoY EBITDA growth, and LTV < 70%, the AI recommends <b>APPROVAL</b> with standard conditions.
                </p>
              </div>
              <div class="flex flex-col items-end gap-2">
                <span class="text-xs font-bold text-teal-700 uppercase">Confidence</span>
                <div class="text-2xl font-black text-teal-900">89%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button, FeatherIcon, Badge, usePageMeta, toast } from 'frappe-ui'

// Mock Data
const searchQuery = ref('')
const selectedApp = ref(null)
const activeTab = ref('financials')

const applications = ref([
  { id: 'APP-2026-001', borrower: 'PT Investama Sejahtera', amount: 20.0, facility: 'Working Capital', status: 'In Progress', industry: 'Manufacturing', kbli: '1032' },
  { id: 'APP-2026-002', borrower: 'CV Makmur Sentosa', amount: 5.5, facility: 'Investment Loan', status: 'Pending Review', industry: 'Retail', kbli: '4711' },
  { id: 'APP-2026-003', borrower: 'PT Teknologi Bangsa', amount: 15.0, facility: 'Revolving Credit', status: 'Approved', industry: 'IT Services', kbli: '6201' }
])

const filteredApps = computed(() => {
  if (!searchQuery.value) return applications.value
  const q = searchQuery.value.toLowerCase()
  return applications.value.filter(a => a.borrower.toLowerCase().includes(q) || a.id.toLowerCase().includes(q))
})

function selectApp(app) {
  selectedApp.value = app
  activeTab.value = 'financials'
}

// Spreading Data Mock
const finData = ref({
  rev23: 110.5,
  rev24: 125.0,
  rev25: 140.0,
  ebitda23: 15.2,
  ebitda24: 18.5,
  ebitda25: 22.0,
  int23: 5.1,
  int24: 5.5,
  int25: 6.0,
})

function calcYoY(oldVal, newVal) {
  if (!oldVal) return '0%'
  const pct = ((newVal - oldVal) / oldVal) * 100
  return (pct > 0 ? '+' : '') + pct.toFixed(1) + '%'
}

function getYoYTheme(oldVal, newVal) {
  if (!oldVal) return 'gray'
  const pct = ((newVal - oldVal) / oldVal) * 100
  if (pct >= 10) return 'emerald'
  if (pct <= -10) return 'red'
  return 'gray'
}

const memoContent = ref('')

function generateMemo() {
  toast.success('AI generating Credit Analysis Memorandum...')
  setTimeout(() => {
    memoContent.value = `EXECUTIVE SUMMARY
PT Investama Sejahtera ("Borrower") is requesting a Working Capital facility of Rp 20.0B. The Borrower operates in the Manufacturing sector with a solid track record spanning over 10 years.

1. FINANCIAL PERFORMANCE
Revenue grew by 13.1% YoY from 2023 to 2024, accompanied by an EBITDA margin improvement. The projected DSCR for 2025 is a healthy 1.4x under base case scenarios.

2. RISK & MITIGANTS
- Risk: Industry cyclicality affecting material costs.
- Mitigant: Long-term supplier contracts lock in prices for the next 24 months.

3. RECOMMENDATION
Based on the strong LTV of 61.5% and performing SLIK history (KOL-1), we recommend APPROVAL of the Rp 20.0B facility subject to the following Covenants:
- Maintain DSCR > 1.20x
- Submit quarterly financial statements.`
  }, 800)
}

function triggerSave() {
  toast.success('Analysis drafted saved successfully.')
}

function triggerSubmit() {
  toast.success('CAM submitted to Credit Committee routing.')
}

function triggerOCR() {
  toast.success('AI OCR processing uploaded PDF. Fields auto-populated.')
}

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
