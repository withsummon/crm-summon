<template>
  <div class="portfolio-monitoring min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
    <!-- Header -->
    <header class="border-b border-slate-200 bg-white px-6 py-4 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center">
          <FeatherIcon name="pie-chart" class="w-5 h-5 text-teal-400" />
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-xl font-bold text-slate-900 tracking-tight">Portfolio Monitoring</h1>
          </div>
          <p class="text-xs text-slate-500">Concentration Risk, Early Warning System & Stress Testing Engine</p>
        </div>
      </div>

      <!-- Global Filter Bar -->
      <div class="flex items-center space-x-4">
        <div class="flex bg-slate-100 rounded-lg p-0.5 border border-slate-200">
          <button 
            v-for="p in ['MTD', 'YTD', '12M', 'Custom']" 
            :key="p"
            @click="activePeriod = p"
            :class="[
              'px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200',
              activePeriod === p 
                ? 'bg-teal-500 text-slate-900 font-bold shadow-lg shadow-teal-500/10' 
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            ]"
          >
            {{ p }}
          </button>
        </div>
        <div class="bg-slate-100 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-600 flex items-center space-x-2">
          <FeatherIcon name="calendar" class="w-4 h-4 text-teal-400" />
          <span>May 24, 2026</span>
        </div>
        <button 
          @click="showReportBuilder = true"
          class="bg-slate-100 border border-slate-200 hover:bg-slate-200 text-slate-700 px-4 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-2 transition-all"
        >
          <FeatherIcon name="download" class="w-4 h-4 text-teal-400" />
          <span>Export Report</span>
        </button>
      </div>
    </header>

    <transition name="fade">
      <div v-if="toast.show" class="fixed right-6 top-[92px] z-40 w-[min(360px,calc(100vw-2rem))] rounded-3xl border border-slate-200 bg-white/95 p-4 shadow-2xl backdrop-blur-sm">
        <div class="flex items-start gap-3">
          <span :class="toast.type === 'danger' ? 'text-red-500' : toast.type === 'warning' ? 'text-amber-500' : 'text-teal-500'" class="mt-1">
            <FeatherIcon :name="toast.type === 'danger' ? 'alert-octagon' : toast.type === 'warning' ? 'alert-triangle' : 'check-circle'" class="w-5 h-5" />
          </span>
          <div>
            <p class="text-sm font-semibold text-slate-900">{{ toast.message }}</p>
            <p class="text-[11px] text-slate-500 mt-1">EWS notification and portfolio workflow update.</p>
          </div>
        </div>
      </div>
    </transition>

    <nav class="sticky top-[73px] z-20 bg-white border-b border-slate-200 px-6 py-4">
      <div class="grid gap-3 xl:grid-cols-2">
        <template v-for="(group, gIdx) in navigationGroups" :key="group.title">
          <div class="rounded-3xl border border-slate-200 bg-slate-50/80 p-3">
            <div class="flex items-center justify-between gap-4 mb-3">
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">{{ group.title }}</p>
                <p class="text-[10px] text-slate-400 mt-1">{{ group.items.length }} views</p>
              </div>
              <span class="hidden xl:inline-flex rounded-full bg-slate-100 px-3 py-1 text-[10px] font-semibold text-slate-600">Tap to explore</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="item in group.items"
                :key="item.id"
                @click="activeTab = item.id"
                :class="[
                  'inline-flex items-center gap-2 px-3 py-2 rounded-full text-sm font-semibold transition-all duration-200 whitespace-nowrap',
                  activeTab === item.id
                    ? 'bg-teal-500/10 text-teal-700 border border-teal-200 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200'
                ]"
              >
                <FeatherIcon :name="item.icon" class="w-4 h-4" />
                <span>{{ item.label }}</span>
                <span v-if="item.badge" :class="['rounded-full px-2 py-0.5 text-[10px] font-semibold', item.badgeType === 'warning' ? 'bg-amber-100 text-amber-700 border border-amber-200' : item.badgeType === 'danger' ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-slate-100 text-slate-700 border border-slate-200']">
                  {{ item.badge }}
                </span>
              </button>
            </div>
          </div>
        </template>
      </div>
    </nav>

    <!-- Main Container -->
    <main class="flex-1 overflow-y-auto bg-slate-50 p-6">
        <!-- 1.0 PORTFOLIO OVERVIEW -->
        <section v-if="activeTab === 'overview'" class="space-y-6">
          <div class="bg-white rounded-3xl border border-slate-200 p-5 shadow-sm">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <p class="text-[10px] uppercase tracking-widest text-slate-500">AI Portfolio Advisor</p>
                <h2 class="mt-2 text-xl font-semibold text-slate-900">Strategic guidance for Indonesian regional portfolio hubs</h2>
                <p class="mt-2 text-sm text-slate-600 max-w-2xl">Interest rate shock simulation indicates capital buffer headroom remains stable, with priority monitoring recommended for Sumatera and Papua exposure pockets.</p>
              </div>
              <div class="rounded-3xl bg-teal-50 border border-teal-200 px-5 py-4 text-teal-700 shadow-sm">
                <div class="text-sm font-semibold">Scenario Insight</div>
                <div class="mt-2 text-3xl font-bold">-120bps</div>
                <div class="text-xs uppercase tracking-[0.2em]">Projected Portfolio Impact</div>
              </div>
            </div>
          </div>

          <!-- KPI Cards -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
            <div 
              v-for="kpi in overviewKPIs" 
              :key="kpi.title"
              class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm relative overflow-hidden group hover:border-teal-500/30 transition-all duration-300 hover:shadow-lg"
            >
              <div class="absolute -right-6 -bottom-6 opacity-5 group-hover:scale-125 transition-transform duration-300">
                <FeatherIcon :name="kpi.icon" class="w-24 h-24 text-slate-900" />
              </div>
              <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ kpi.title }}</span>
                <div class="w-7 h-7 rounded-lg bg-teal-500/10 flex items-center justify-center">
                  <FeatherIcon :name="kpi.icon" class="w-4 h-4 text-teal-400" />
                </div>
              </div>
              <div class="text-2xl font-extrabold text-slate-900 tracking-tight mb-1">{{ kpi.value }}</div>
              <div class="flex items-center text-[10px] font-semibold space-x-1">
                <span :class="kpi.trendUp ? 'text-emerald-400' : 'text-rose-400'">
                  <FeatherIcon :name="kpi.trendUp ? 'arrow-up-right' : 'arrow-down-right'" class="w-3.5 h-3.5 inline mr-0.5" />
                  {{ kpi.change }}
                </span>
                <span class="text-slate-500">since last quarter</span>
              </div>
            </div>
          </div>

          <!-- Trend Chart & Watchlist Summary -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- 12-Month Trend (SVG Chart) -->
            <div class="bg-white rounded-xl p-5 border border-slate-200 lg:col-span-2 space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-bold text-slate-900">12M Trend Analysis</h3>
                  <p class="text-[11px] text-slate-500">Total Outstanding Portfolio & NPL Ratio progression</p>
                </div>
                <div class="flex items-center space-x-4 text-xs font-semibold">
                  <div class="flex items-center space-x-1.5">
                    <span class="w-3 h-1.5 rounded-full bg-teal-400"></span>
                    <span class="text-slate-600">OS (in Trillion IDR)</span>
                  </div>
                  <div class="flex items-center space-x-1.5">
                    <span class="w-3 h-1.5 rounded-full bg-rose-400"></span>
                    <span class="text-slate-600">NPL Ratio (%)</span>
                  </div>
                </div>
              </div>

              <!-- Interactive SVG Trend Chart -->
              <div class="relative h-64 w-full bg-slate-50/60 rounded-lg border border-slate-200 p-4 flex items-end">
                <svg class="w-full h-full" viewBox="0 0 600 200" preserveAspectRatio="none">
                  <!-- Gridlines -->
                  <line x1="0" y1="50" x2="600" y2="50" stroke="#1b2530" stroke-dasharray="4" />
                  <line x1="0" y1="100" x2="600" y2="100" stroke="#1b2530" stroke-dasharray="4" />
                  <line x1="0" y1="150" x2="600" y2="150" stroke="#1b2530" stroke-dasharray="4" />

                  <!-- OS Trend Line (Teal) -->
                  <path 
                    d="M 20 120 L 70 115 L 120 125 L 170 110 L 220 100 L 270 95 L 320 85 L 370 70 L 420 65 L 470 58 L 520 52 L 570 45" 
                    fill="none" 
                    stroke="#14b8a6" 
                    stroke-width="3" 
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <!-- NPL Trend Line (Rose) -->
                  <path 
                    d="M 20 140 L 70 145 L 120 148 L 170 135 L 220 130 L 270 125 L 320 132 L 370 128 L 420 120 L 470 118 L 520 112 L 570 108" 
                    fill="none" 
                    stroke="#f43f5e" 
                    stroke-width="2" 
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-dasharray="2 1"
                  />

                  <!-- Dots for interactive feel -->
                  <circle cx="570" cy="45" r="5" fill="#14b8a6" stroke="#0d121a" stroke-width="2" />
                  <circle cx="570" cy="108" r="4.5" fill="#f43f5e" stroke="#0d121a" stroke-width="1.5" />
                </svg>
                
                <!-- Bottom Axis Labels -->
                <div class="absolute bottom-1 left-4 right-4 flex justify-between text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                  <span>Jun 25</span>
                  <span>Aug 25</span>
                  <span>Oct 25</span>
                  <span>Dec 25</span>
                  <span>Feb 26</span>
                  <span>May 26</span>
                </div>
              </div>
            </div>

            <!-- Top Watchlist Highlight -->
            <div class="bg-white rounded-xl p-5 border border-slate-200 space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-bold text-slate-900">Critical Watchlist</h3>
                <span class="text-[10px] font-bold text-teal-400 cursor-pointer hover:underline" @click="activeTab = 'watchlist'">View All</span>
              </div>
              
              <div class="space-y-3 overflow-y-auto max-h-64 pr-1">
                <div 
                  v-for="w in watchlistData.slice(0, 4)" 
                  :key="w.account"
                  class="bg-slate-50 rounded-lg p-3 border border-slate-200 hover:border-red-500/30 transition-all flex justify-between items-start"
                >
                  <div class="space-y-1">
                    <h4 class="text-xs font-bold text-slate-900">{{ w.account }}</h4>
                    <div class="flex space-x-2 text-[9px] text-slate-500 font-semibold">
                      <span>OS: {{ w.os }}</span>
                      <span class="text-red-400 font-extrabold uppercase">DPD: {{ w.dpd }}</span>
                    </div>
                  </div>
                  <span class="px-2 py-0.5 rounded text-[8px] font-bold bg-red-500/10 text-red-400 border border-red-500/30">{{ w.trigger }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 2.0 INDUSTRY EXPOSURE -->
        <section v-if="activeTab === 'industry'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-bold text-slate-900">Industry Exposure & Limit Control</h3>
                <p class="text-xs text-slate-500">Tracking concentration against regulatory SBL & KBLI sector boundaries.</p>
              </div>
              <div class="px-3 py-1 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-bold flex items-center space-x-2">
                <FeatherIcon name="alert-triangle" class="w-4 h-4 text-red-400 animate-bounce" />
                <span>1 Sector Exceeding Limit Threshold!</span>
              </div>
            </div>

            <!-- Industry Exposure Table with Progress Bars -->
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs text-slate-600">
                <thead>
                  <tr class="border-b border-slate-200 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    <th class="pb-3">Sector / KBLI</th>
                    <th class="pb-3">Outstanding Exposure</th>
                    <th class="pb-3">% of Portfolio</th>
                    <th class="pb-3">Concentration Limit</th>
                    <th class="pb-3">Actual vs Limit</th>
                    <th class="pb-3">Status</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#1b2530]">
                  <tr v-for="ind in industryData" :key="ind.kbli" class="hover:bg-slate-50 transition-all">
                    <td class="py-4 font-bold text-slate-900">
                      {{ ind.name }}
                      <span class="block text-[10px] text-slate-500 font-light">KBLI Code: {{ ind.kbli }}</span>
                    </td>
                    <td class="py-4">{{ ind.os }}</td>
                    <td class="py-4 font-semibold text-teal-400">{{ ind.pct }}</td>
                    <td class="py-4 text-slate-500">{{ ind.limit }}</td>
                    <td class="py-4 w-1/4">
                      <div class="space-y-1">
                        <div class="flex justify-between text-[10px] font-semibold text-slate-500">
                          <span>Usage: {{ ind.usage }}%</span>
                        </div>
                        <div class="w-full h-2 rounded bg-slate-800 overflow-hidden relative border border-slate-200">
                          <div 
                            :class="[
                              'h-full rounded transition-all duration-500', 
                              ind.usage > 100 ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : ind.usage > 80 ? 'bg-amber-500' : 'bg-teal-400'
                            ]"
                            :style="{ width: Math.min(ind.usage, 100) + '%' }"
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td class="py-4">
                      <span 
                        :class="[
                          'px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border',
                          ind.usage > 100 ? 'bg-red-500/10 text-red-400 border-red-500/30' : ind.usage > 80 ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : 'bg-teal-500/10 text-teal-400 border-teal-500/30'
                        ]"
                      >
                        {{ ind.usage > 100 ? 'Breach' : ind.usage > 80 ? 'Warning' : 'Normal' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- 3.0 GEOGRAPHIC EXPOSURE -->
        <section v-if="activeTab === 'geographic'" class="space-y-6">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Heatmap & Stats -->
            <div class="bg-white rounded-xl p-5 border border-slate-200 space-y-5 lg:col-span-1">
              <div>
                <h3 class="text-sm font-bold text-slate-900">Regional Exposure breakdown</h3>
                <p class="text-xs text-slate-500">NPL and outstanding tracking per Indonesian provinces.</p>
              </div>
              <div class="space-y-3">
                <div 
                  v-for="geo in geographicData" 
                  :key="geo.province"
                  @click="selectedProvince = geo.province"
                  :class="[
                    'p-3 rounded-lg border cursor-pointer transition-all duration-150 flex justify-between items-center',
                    selectedProvince === geo.province 
                      ? 'bg-teal-500/10 border-teal-500 shadow-md text-teal-300' 
                      : 'bg-slate-50 border-slate-200 hover:border-slate-300 text-slate-600'
                  ]"
                >
                  <div class="space-y-0.5">
                    <span class="text-xs font-bold">{{ geo.province }}</span>
                    <span class="block text-[10px] text-slate-500 font-semibold">OS: {{ geo.os }}</span>
                  </div>
                  <div class="text-right">
                    <span class="text-xs font-bold text-teal-400">{{ geo.pct }}</span>
                    <span class="block text-[10px] text-rose-400 font-extrabold">NPL: {{ geo.npl }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Geographic Exposure Map -->
            <div class="bg-white rounded-xl p-5 border border-slate-200 lg:col-span-2">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-4">
                <div>
                  <h3 class="text-sm font-bold text-slate-900">Interactive Geographic Map</h3>
                  <p class="text-xs text-slate-500">Click a region marker to sync exposure metrics and view the latest portfolio focus.</p>
                </div>
                <div class="rounded-full bg-slate-50 border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-700">
                  Active Focus: <strong class="text-slate-900">{{ selectedProvince }}</strong>
                </div>
              </div>

              <div id="portfolio-map" class="h-96 w-full rounded-xl border border-slate-200 shadow-inner overflow-hidden"></div>

              <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="rounded-3xl bg-slate-50 border border-slate-100 p-4">
                  <p class="text-[10px] uppercase tracking-widest text-slate-500">Selected Region</p>
                  <h4 class="mt-2 text-lg font-semibold text-slate-900">{{ selectedProvince }}</h4>
                  <p class="mt-2 text-sm text-slate-600">Regional markers are linked to the geographic metrics sidebar and update on every map interaction.</p>
                </div>
                <div class="rounded-3xl bg-slate-50 border border-slate-100 p-4">
                  <p class="text-[10px] uppercase tracking-widest text-slate-500">Interaction Guide</p>
                  <p class="mt-2 text-sm text-slate-600">Use the map or regional list to fly directly to hubs in Jawa, Sumatera, Kalimantan, Sulawesi, and Papua.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 4.0 SINGLE BORROWER LIMIT (SBL / BMPK) -->
        <section v-if="activeTab === 'sbl'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div>
              <h3 class="text-sm font-bold text-slate-900">BMPK Regulatory SBL Monitor</h3>
              <p class="text-xs text-slate-500">Monitoring single borrowers and corporate group exposure limits against BNI's Core Capital base.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div 
                v-for="group in sblData" 
                :key="group.name"
                class="bg-slate-50 rounded-xl p-5 border border-slate-200 hover:border-teal-500/30 transition-all flex flex-col justify-between"
              >
                <div class="space-y-2">
                  <div class="flex justify-between items-start">
                    <div>
                      <h4 class="text-sm font-bold text-slate-900">{{ group.name }}</h4>
                      <span class="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">{{ group.type }} LIMIT MONITORING</span>
                    </div>
                    <span 
                      :class="[
                        'px-2 py-0.5 rounded text-[10px] font-semibold border uppercase tracking-wider',
                        group.usage >= 100 ? 'bg-red-500/10 text-red-400 border-red-500/30 animate-pulse' : group.usage >= 80 ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : 'bg-teal-500/10 text-teal-400 border-teal-500/30'
                      ]"
                    >
                      {{ group.usage >= 100 ? 'Breach' : group.usage >= 80 ? 'Near Breach' : 'Compliant' }}
                    </span>
                  </div>

                  <div class="border-t border-slate-200 pt-3 grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span class="block text-[10px] text-slate-500 font-semibold uppercase">Total OS</span>
                      <strong class="text-slate-700">{{ group.os }}</strong>
                    </div>
                    <div>
                      <span class="block text-[10px] text-slate-500 font-semibold uppercase">Max Allowed</span>
                      <strong class="text-slate-500">{{ group.limit }}</strong>
                    </div>
                    <div>
                      <span class="block text-[10px] text-slate-500 font-semibold uppercase">% of Capital</span>
                      <strong class="text-teal-400">{{ group.pctCapital }}%</strong>
                    </div>
                  </div>
                </div>

                <div class="space-y-1.5 mt-5">
                  <div class="flex justify-between text-[10px] font-semibold text-slate-500">
                    <span>Limit Utilization</span>
                    <span>{{ group.usage }}%</span>
                  </div>
                  <div class="w-full h-2.5 rounded bg-slate-800 overflow-hidden relative border border-slate-200">
                    <div 
                      :class="[
                        'h-full rounded transition-all duration-500', 
                        group.usage >= 100 ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : group.usage >= 80 ? 'bg-amber-500' : 'bg-teal-400'
                      ]"
                      :style="{ width: Math.min(group.usage, 100) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 5.0 TOP 20 EXPOSURES -->
        <section v-if="activeTab === 'top-exposures'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div>
              <h3 class="text-sm font-bold text-slate-900">Top 20 Corporate Exposure List</h3>
              <p class="text-xs text-slate-500">Sorted by outstanding balances with active risk grade and Days Past Due tracking.</p>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs text-slate-600">
                <thead>
                  <tr class="border-b border-slate-200 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    <th class="pb-3">Borrower / Group</th>
                    <th class="pb-3">Outstanding Balance</th>
                    <th class="pb-3">Risk Grade</th>
                    <th class="pb-3">DPD</th>
                    <th class="pb-3">Trend</th>
                    <th class="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#1b2530]">
                  <tr v-for="exp in topExposures" :key="exp.name" class="hover:bg-slate-50 transition-all">
                    <td class="py-4 font-bold text-slate-900 flex items-center space-x-2">
                      <div class="w-2.5 h-2.5 rounded-full" :class="exp.dpd > 0 ? 'bg-rose-400' : 'bg-teal-400'"></div>
                      <span>{{ exp.name }}</span>
                    </td>
                    <td class="py-4 font-semibold text-slate-700">{{ exp.os }}</td>
                    <td class="py-4">
                      <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 border border-slate-200 text-teal-400">
                        {{ exp.grade }}
                      </span>
                    </td>
                    <td class="py-4" :class="exp.dpd > 0 ? 'text-rose-400 font-extrabold' : 'text-slate-500'">
                      {{ exp.dpd }} Days
                    </td>
                    <td class="py-4 font-semibold">
                      <span :class="exp.trend === 'Growing' ? 'text-teal-400' : exp.trend === 'Decreasing' ? 'text-slate-500' : 'text-slate-500'">
                        {{ exp.trend }}
                      </span>
                    </td>
                    <td class="py-4 text-right">
                      <a 
                        :href="`/crm/crm-core/customer-360/${encodeURIComponent(exp.name)}`"
                        class="px-3 py-1 rounded bg-teal-500/10 hover:bg-teal-500 text-teal-300 hover:text-slate-900 border border-teal-500/20 text-[10px] font-bold transition-all"
                      >
                        Open Customer 360
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- 6.0 CONCENTRATION RISK MATRIX -->
        <section v-if="activeTab === 'concentration-matrix'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-bold text-slate-900">Concentration Risk Matrix (Industry x Region)</h3>
                <p class="text-xs text-slate-500">A 2D double-exposure heatmap showing intersection hotspots.</p>
              </div>
              <button 
                class="bg-slate-100 border border-slate-200 text-slate-700 hover:bg-slate-100 px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all"
                @click="exportMatrix"
              >
                <FeatherIcon name="file" class="w-4 h-4 text-teal-400" />
                <span>Export PDF Matrix</span>
              </button>
            </div>

            <!-- Heatmap Grid -->
            <div class="grid grid-cols-5 gap-3">
              <!-- Matrix Header Cells -->
              <div class="col-span-1"></div>
              <div v-for="prov in ['Jawa', 'Sumatera', 'Kalimantan', 'Sulawesi']" :key="prov" class="text-center text-[10px] font-bold text-slate-500 uppercase tracking-widest py-2">
                {{ prov }}
              </div>

              <!-- Matrix Rows -->
              <template v-for="row in matrixRows" :key="row.industry">
                <div class="col-span-1 font-bold text-xs text-slate-600 flex items-center pr-3 border-r border-slate-200">
                  {{ row.industry }}
                </div>
                <div 
                  v-for="cell in row.cells" 
                  :key="cell.region"
                  @click="selectedMatrixCell = { industry: row.industry, region: cell.region, details: cell.details }"
                  :class="[
                    'rounded-lg p-4 cursor-pointer text-center transition-all hover:scale-105',
                    cell.intensity === 'high' ? 'bg-red-500/20 text-red-400 border border-red-500/40 hover:bg-red-500/30' : cell.intensity === 'medium' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40 hover:bg-amber-500/30' : 'bg-teal-500/10 text-teal-400 border border-teal-500/20 hover:bg-teal-500/20'
                  ]"
                >
                  <strong class="text-sm block">{{ cell.os }}</strong>
                  <span class="text-[9px] font-semibold uppercase tracking-wider block opacity-70">{{ cell.accounts }} Accs</span>
                </div>
              </template>
            </div>

            <!-- Cell Drill Down Modal Segment -->
            <div v-if="selectedMatrixCell" class="bg-slate-50 rounded-xl p-5 border border-teal-500/30 mt-6 space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="text-xs font-bold text-teal-400 uppercase tracking-widest">Selected Cell Drilldown</h4>
                  <strong class="text-sm text-slate-900">{{ selectedMatrixCell.industry }} x {{ selectedMatrixCell.region }}</strong>
                </div>
                <button @click="selectedMatrixCell = null" class="text-xs text-slate-500 hover:text-slate-700">Close</button>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-600">
                <div 
                  v-for="acc in selectedMatrixCell.details" 
                  :key="acc.name"
                  class="bg-slate-50 p-3 rounded-lg border border-slate-200 flex justify-between"
                >
                  <div>
                    <span class="font-bold block text-slate-700">{{ acc.name }}</span>
                    <span class="text-[10px] text-slate-500">Grade: {{ acc.grade }}</span>
                  </div>
                  <strong class="text-teal-400">{{ acc.os }}</strong>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 7.0 EARLY WARNING SYSTEM (EWS) -->
        <section v-if="activeTab === 'ews'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-bold text-slate-900">Early Warning System (EWS) Alerts</h3>
                <p class="text-xs text-slate-500">Real-time indicators showing transactional or operational credit deterioration.</p>
              </div>
              <span class="text-xs font-bold text-slate-500">Total Alerts: {{ ewsAlerts.length }}</span>
            </div>

            <div class="space-y-4">
              <div 
                v-for="alert in ewsAlerts" 
                :key="alert.id"
                class="bg-slate-50 rounded-xl p-5 border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div class="space-y-2 flex-1">
                  <div class="flex items-center space-x-3">
                    <span 
                      :class="[
                        'px-2 py-0.5 rounded text-[9px] font-extrabold uppercase border',
                        alert.severity === 'Red' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      ]"
                    >
                      {{ alert.severity }} Alert
                    </span>
                    <strong class="text-sm text-slate-900">{{ alert.borrower }}</strong>
                  </div>
                  <p class="text-xs text-slate-600 leading-relaxed font-light">{{ alert.signal }}</p>
                  <span class="block text-[10px] text-slate-500 font-semibold uppercase">Trigger Date: {{ alert.date }}</span>
                </div>

                <div class="flex items-center space-x-3 shrink-0">
                  <button 
                    v-if="!alert.acknowledged"
                    @click="acknowledgeAlert(alert)"
                    class="bg-teal-500 hover:bg-teal-600 text-slate-900 px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
                  >
                    Acknowledge Signal
                  </button>
                  <span 
                    v-else 
                    class="px-3 py-1 rounded bg-slate-50 border border-slate-200 text-teal-400 text-xs font-bold"
                  >
                    Acknowledged & Remedied
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 8.0 COVENANT BREACH DETECTION -->
        <section v-if="activeTab === 'covenants'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div>
              <h3 class="text-sm font-bold text-slate-900">Covenant Breach Detection</h3>
              <p class="text-xs text-slate-500">Auto-flagging credit covenant parameters based on current balance sheets and financial statements.</p>
            </div>

            <div class="space-y-4">
              <div 
                v-for="cov in covenants" 
                :key="cov.id"
                class="bg-slate-50 rounded-xl p-5 border border-slate-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
              >
                <div class="space-y-1.5 flex-1">
                  <div class="flex items-center space-x-3">
                    <strong class="text-sm text-slate-900">{{ cov.borrower }}</strong>
                    <span 
                      :class="[
                        'px-2 py-0.5 rounded text-[9px] font-bold uppercase border',
                        cov.status === 'Breach' ? 'bg-red-500/10 text-red-400 border-red-500/30 animate-pulse' : 'bg-teal-500/10 text-teal-400 border-teal-500/30'
                      ]"
                    >
                      {{ cov.status }}
                    </span>
                  </div>
                  <div class="text-xs text-slate-600">
                    Covenant rule: <strong class="text-slate-900">{{ cov.rule }}</strong>
                    <span class="block mt-0.5 text-[10px] text-slate-500 font-semibold uppercase">
                      Current Value: <strong class="text-rose-400">{{ cov.actual }}</strong> (Limit threshold: {{ cov.threshold }})
                    </span>
                  </div>
                </div>

                <div class="flex items-center space-x-3">
                  <button 
                    v-if="cov.status === 'Breach'"
                    @click="cureCovenant(cov)"
                    class="bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 hover:border-slate-300 px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
                  >
                    Resolve / Trigger Remedy Workflow
                  </button>
                  <span 
                    v-else 
                    class="text-xs text-teal-400 font-extrabold flex items-center space-x-1.5"
                  >
                    <FeatherIcon name="check-circle" class="w-4 h-4" />
                    <span>Active Audit Passed</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 16.0 STRESS TESTING ENGINE -->
        <section v-if="activeTab === 'stress-testing'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div>
              <h3 class="text-sm font-bold text-slate-900">Stress Testing Scenario Engine</h3>
              <p class="text-xs text-slate-500">Simulate interest rate or loan default shocks to see the instant impact on profit and capital adequacy buffer.</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <!-- Sliders & Preset Scenarios -->
              <div class="space-y-5 lg:col-span-1">
                <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-4">
                  <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Scenario Selector</h4>
                  <div class="space-y-2">
                    <button 
                      v-for="sc in scenarios" 
                      :key="sc.name"
                      @click="applyScenarioPreset(sc)"
                      class="w-full text-left px-3 py-2 rounded-lg text-xs font-semibold bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 flex justify-between items-center transition-all"
                    >
                      <span>{{ sc.name }}</span>
                      <span class="text-[10px] text-teal-400 font-bold">Apply</span>
                    </button>
                  </div>
                </div>

                <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-5">
                  <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Custom Sliders</h4>
                  
                  <div class="space-y-2">
                    <div class="flex justify-between text-xs text-slate-600 font-semibold">
                      <span>Interest Rate Shock</span>
                      <span class="text-teal-400">+{{ stressRates }} bps</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="500" 
                      step="50" 
                      v-model.number="stressRates"
                      class="w-full h-3 bg-slate-200 rounded-full appearance-none cursor-pointer accent-teal-500"
                    />
                  </div>

                  <div class="space-y-2">
                    <div class="flex justify-between text-xs text-slate-600 font-semibold">
                      <span>NPL Shock Rate</span>
                      <span class="text-teal-400">+{{ stressNPL }} %</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="10" 
                      step="0.5" 
                      v-model.number="stressNPL"
                      class="w-full h-3 bg-slate-200 rounded-full appearance-none cursor-pointer accent-teal-500"
                    />
                  </div>
                </div>
              </div>

              <!-- Stress Test Simulation Impact View -->
              <div class="bg-slate-50 p-5 rounded-xl border border-slate-200 lg:col-span-2 space-y-6">
                <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Instant Portfolio Capital Impact</h4>
                
                <div class="grid grid-cols-2 gap-5">
                  <!-- Capital Adequacy Card -->
                  <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
                    <span class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider">CAR Buffer Level</span>
                    <div class="text-2xl font-extrabold text-slate-900">
                      {{ (18.5 - (stressRates * 0.002 + stressNPL * 0.4)).toFixed(2) }}%
                    </div>
                    <span 
                      :class="[
                        'text-[10px] font-semibold',
                        (stressRates > 150 || stressNPL > 3) ? 'text-red-400' : 'text-teal-400'
                      ]"
                    >
                      Impact: -{{ (stressRates * 0.002 + stressNPL * 0.4).toFixed(2) }}%
                    </span>
                  </div>

                  <!-- Provisioning Impact Card -->
                  <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
                    <span class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider">Additional ECL Provisions</span>
                    <div class="text-2xl font-extrabold text-slate-900">
                      IDR {{ ((stressNPL * 0.08) + (stressRates * 0.001)).toFixed(2) }} Trillion
                    </div>
                    <span class="text-[10px] font-semibold text-rose-400">Reduction in Net PnL Profit</span>
                  </div>
                </div>

                <!-- Scenario Warning Banners -->
                <div 
                  v-if="(stressRates * 0.002 + stressNPL * 0.4) > 2.0"
                  class="bg-red-500/10 border border-red-500/20 text-red-400 text-xs p-4 rounded-lg flex items-center space-x-3 leading-relaxed"
                >
                  <FeatherIcon name="alert-octagon" class="w-6 h-6 text-red-400 shrink-0" />
                  <p>
                    <strong>ALERT: CAP BUFFERS EXCEEDED!</strong> The simulated parameters reduce BNI's local Capital Adequacy ratio (CAR) close to the regulatory minimum of 14%. Risk mitigation action plan is highly recommended.
                  </p>
                </div>
                <div 
                  v-else
                  class="bg-teal-500/10 border border-teal-500/20 text-teal-400 text-xs p-4 rounded-lg flex items-center space-x-3"
                >
                  <FeatherIcon name="info" class="w-5 h-5 text-teal-400" />
                  <span>The simulated stress impact remains within the bank's internal approved risk limit profiles.</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 17.0 EXPECTED CREDIT LOSS (ECL / PSAK 71) -->
        <section v-if="activeTab === 'ecl'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div>
              <h3 class="text-sm font-bold text-slate-900">Expected Credit Loss (ECL / PSAK 71) Segment</h3>
              <p class="text-xs text-slate-500">Classifying outstanding portfolios into standard credit provisioning stages (PD/LGD/EAD and macro-adjustments).</p>
            </div>

            <!-- ECL provisioning progress breakdown -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div 
                v-for="stg in eclStages" 
                :key="stg.stage"
                class="bg-slate-50 p-5 rounded-xl border border-slate-200 space-y-3"
              >
                <div class="flex justify-between items-center">
                  <strong class="text-sm text-slate-900">{{ stg.stage }}</strong>
                  <span class="px-2 py-0.5 rounded text-[8px] font-extrabold bg-slate-50 text-slate-500 border border-slate-200">
                    {{ stg.pdRange }} PD
                  </span>
                </div>
                <div class="text-2xl font-extrabold text-teal-400 tracking-tight">{{ stg.os }}</div>
                <p class="text-[10px] text-slate-500 leading-normal">{{ stg.desc }}</p>
                
                <div class="border-t border-slate-200 pt-2 text-[10px] flex justify-between font-semibold text-slate-600">
                  <span>ECL Provisions</span>
                  <strong class="text-rose-400">{{ stg.ecl }}</strong>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 14.0 WATCHLIST MANAGEMENT -->
        <section v-if="activeTab === 'watchlist'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-bold text-slate-900">Watchlist Management</h3>
                <p class="text-xs text-slate-500">Add, track, or request removal of corporate accounts under special monitoring.</p>
              </div>
              <button 
                @click="showAddWatchlist = true"
                class="bg-teal-500 hover:bg-teal-600 text-slate-900 px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5"
              >
                <FeatherIcon name="plus" class="w-4 h-4" />
                <span>Add Borrower</span>
              </button>
            </div>

            <!-- Watchlist Table -->
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs text-slate-600">
                <thead>
                  <tr class="border-b border-slate-200 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    <th class="pb-3">Account Name</th>
                    <th class="pb-3">Outstanding Exposure</th>
                    <th class="pb-3">Days Past Due</th>
                    <th class="pb-3">Trigger Reason</th>
                    <th class="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#1b2530]">
                  <tr v-for="w in watchlistData" :key="w.account" class="hover:bg-slate-50 transition-all">
                    <td class="py-4 font-bold text-slate-900">{{ w.account }}</td>
                    <td class="py-4 font-semibold text-slate-700">{{ w.os }}</td>
                    <td class="py-4 text-rose-400 font-bold">{{ w.dpd }} Days</td>
                    <td class="py-4">
                      <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                        {{ w.trigger }}
                      </span>
                    </td>
                    <td class="py-4 text-right">
                      <button 
                        @click="requestRemoveWatchlist(w)"
                        class="px-2.5 py-1 rounded bg-red-500/10 hover:bg-red-500 text-red-400 hover:text-slate-900 border border-red-500/20 text-[10px] font-bold transition-all"
                      >
                        Request Removal
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- 20.0 PORTFOLIO SIMULATION (WHAT-IF) -->
        <section v-if="activeTab === 'simulation'" class="space-y-6">
          <div class="bg-white rounded-xl p-6 border border-slate-200 space-y-6">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-bold text-slate-900">What-if Portfolio Simulator</h3>
                <p class="text-xs text-slate-500">Add or remove hypothetical large borrower profiles to view instant shifts in concentration limits and overall NPL.</p>
              </div>
              <button 
                @click="resetSimulation"
                class="px-3 py-1 rounded bg-slate-100 border border-slate-200 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition-all"
              >
                Reset Simulation
              </button>
            </div>

            <!-- Simulation Dashboard -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <!-- Left: Controls -->
              <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-4">
                <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Simulator Controls</h4>
                
                <div class="space-y-3">
                  <div v-for="sim in simAccounts" :key="sim.name" class="p-3 rounded-lg bg-slate-50 border border-slate-200 flex justify-between items-center">
                    <div class="space-y-0.5">
                      <span class="text-xs font-bold text-slate-700 block">{{ sim.name }}</span>
                      <span class="text-[9px] text-slate-500 uppercase font-semibold">{{ sim.sector }} | {{ sim.os }}</span>
                    </div>
                    <button 
                      @click="toggleSimAccount(sim)"
                      :class="[
                        'px-2.5 py-1 rounded text-[10px] font-bold transition-all',
                        sim.active 
                          ? 'bg-red-500/10 hover:bg-red-500 text-red-400 hover:text-slate-900 border border-red-500/20' 
                          : 'bg-teal-500 hover:bg-teal-600 text-slate-900'
                      ]"
                    >
                      {{ sim.active ? 'Exclude' : 'Include' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Right: Impact Charts & Values -->
              <div class="bg-slate-50 p-5 rounded-xl border border-slate-200 lg:col-span-2 space-y-6">
                <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Simulated Limit Impact</h4>
                
                <div class="grid grid-cols-3 gap-4">
                  <div class="bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
                    <span class="block text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-1">Total Outstanding</span>
                    <strong class="text-lg text-slate-900 font-extrabold">IDR {{ currentSimOS.toFixed(2) }} T</strong>
                  </div>
                  <div class="bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
                    <span class="block text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-1">Portfolio NPL</span>
                    <strong class="text-lg font-extrabold" :class="currentSimNPL > 2.5 ? 'text-rose-400' : 'text-teal-400'">
                      {{ currentSimNPL.toFixed(2) }}%
                    </strong>
                  </div>
                  <div class="bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
                    <span class="block text-[9px] text-slate-500 font-bold uppercase tracking-wider mb-1">Top Sector Ratio</span>
                    <strong class="text-lg text-slate-900 font-extrabold">{{ currentSimConcentration.toFixed(1) }}%</strong>
                  </div>
                </div>

                <!-- Concentration limits progress in simulator -->
                <div class="space-y-4 pt-3 border-t border-slate-200">
                  <h5 class="text-xs font-bold text-slate-500">Simulation Limit Warnings</h5>
                  
                  <div class="space-y-3">
                    <div class="space-y-1">
                      <div class="flex justify-between text-xs text-slate-600">
                        <span>Property / Real Estate Sector Limits</span>
                        <span class="font-bold" :class="currentSimConcentration > 25.0 ? 'text-red-400' : 'text-teal-400'">
                          {{ currentSimConcentration.toFixed(1) }}% / 25.0%
                        </span>
                      </div>
                      <div class="w-full h-2 rounded bg-slate-800 overflow-hidden relative border border-slate-200">
                        <div 
                          :class="[
                            'h-full rounded transition-all duration-300',
                            currentSimConcentration > 25.0 ? 'bg-red-500' : 'bg-teal-400'
                          ]"
                          :style="{ width: Math.min((currentSimConcentration / 25.0) * 100, 100) + '%' }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

    <!-- Export Report/PDF Modal segment -->
    <Dialog 
      v-model="showReportBuilder"
      :options="{
        title: 'Auto-Generate Portfolio Report',
        size: 'sm'
      }"
    >
      <template #body>
        <div class="space-y-4 py-2 text-xs">
          <p class="text-slate-600 font-light">Select the parameters and template files to render and download. Reports will automatically be saved into operational history.</p>
          
          <div class="space-y-3">
            <div class="space-y-1">
              <label class="block font-bold text-slate-500 uppercase text-[10px]">Report Template</label>
              <select class="w-full bg-slate-50 border border-slate-200 rounded p-2 text-slate-700 focus:outline-none focus:border-teal-500">
                <option>Committee Meeting Summary Package (PDF)</option>
                <option>Risk Management SBL/BMPK Limit Audit (Excel)</option>
                <option>Monthly EWS Trigger & Covenant Report (PDF)</option>
              </select>
            </div>

            <div class="flex items-center space-x-2">
              <input type="checkbox" id="sendEmail" class="rounded bg-slate-50 border-slate-200 accent-teal-400 cursor-pointer" />
              <label for="sendEmail" class="text-slate-600 cursor-pointer">Auto-email to Risk Management Committee</label>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end space-x-2">
          <Button variant="outline" label="Cancel" @click="showReportBuilder = false" />
          <Button variant="solid" label="Generate & Download" @click="generateReport" />
        </div>
      </template>
    </Dialog>

    <!-- Add Watchlist Dialog -->
    <Dialog 
      v-model="showAddWatchlist"
      :options="{
        title: 'Add Account to Watchlist',
        size: 'sm'
      }"
    >
      <template #body>
        <div class="space-y-4 py-2 text-xs">
          <div class="rounded-3xl bg-slate-50 border border-slate-200 p-4 space-y-2">
            <p class="text-sm font-semibold text-slate-900">Add a borrower to the watchlist for closer monitoring and committee review.</p>
            <p class="text-[11px] text-slate-500">Only add counterparties with significant payment or covenant deterioration.</p>
          </div>
          <div class="space-y-1">
            <label class="block font-bold text-slate-500 uppercase text-[10px]">Account Name</label>
            <input v-model="newWatchlistName" type="text" placeholder="e.g. Graha Sentosa Tbk" class="w-full bg-white border border-slate-200 rounded-xl p-3 text-slate-700 focus:outline-none focus:border-teal-500" />
          </div>
          <div class="space-y-1">
            <label class="block font-bold text-slate-500 uppercase text-[10px]">Outstanding Balance (OS)</label>
            <input v-model="newWatchlistOS" type="text" placeholder="e.g. IDR 150 Billion" class="w-full bg-slate-50 border border-slate-200 rounded p-2 text-slate-700 focus:outline-none focus:border-teal-500" />
          </div>
          <div class="space-y-1">
            <label class="block font-bold text-slate-500 uppercase text-[10px]">Days Past Due (DPD)</label>
            <input v-model.number="newWatchlistDPD" type="number" class="w-full bg-slate-50 border border-slate-200 rounded p-2 text-slate-700 focus:outline-none focus:border-teal-500" />
          </div>
          <div class="space-y-1">
            <label class="block font-bold text-slate-500 uppercase text-[10px]">Trigger Reason</label>
            <select v-model="newWatchlistTrigger" class="w-full bg-slate-50 border border-slate-200 rounded p-2 text-slate-700 focus:outline-none focus:border-teal-500">
              <option>Payment Delay</option>
              <option>Ratio Drop</option>
              <option>Negative News</option>
              <option>DPD > 30</option>
              <option>Covenant Breach</option>
            </select>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end space-x-2">
          <Button variant="outline" label="Cancel" @click="showAddWatchlist = false" />
          <Button variant="solid" label="Add to Watchlist" @click="submitAddWatchlist" />
        </div>
      </template>
    </Dialog>

    <!-- Remove Watchlist Dialog -->
    <Dialog 
      v-model="showRemoveWatchlist"
      :options="{
        title: 'Request Watchlist Removal',
        size: 'sm'
      }"
    >
      <template #body>
        <div class="space-y-4 py-2 text-xs">
          <div class="rounded-3xl bg-slate-50 border border-slate-200 p-4 space-y-2">
            <p class="text-sm font-semibold text-slate-900">Submit a removal request for the selected watchlist borrower.</p>
            <p class="text-[11px] text-slate-500">Provide an explanation so the risk committee can review the request promptly.</p>
          </div>
          <div class="space-y-3">
            <p class="text-slate-600">Request removal of <strong class="text-slate-900">{{ selectedWatchlistToRemove?.account }}</strong>. Removal requires committee approval and a documented rationale.</p>
            <div class="space-y-1">
              <label class="block font-bold text-slate-500 uppercase text-[10px]">Justification Reason</label>
              <textarea v-model="removeReason" placeholder="Describe remediation actions (e.g. loan restructured, covenant amended)" class="w-full h-24 bg-white border border-slate-200 rounded-xl p-3 text-slate-700 focus:outline-none focus:border-teal-500"></textarea>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end space-x-2">
          <Button variant="outline" label="Cancel" @click="showRemoveWatchlist = false" />
          <Button variant="solid" label="Submit Request" @click="submitRemoveWatchlist" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { FeatherIcon, Dialog, Button } from 'frappe-ui'

// Active periods & Navigation tabs
const activePeriod = ref('12M')
const activeTab = ref('overview')
const selectedProvince = ref('Jawa')
const selectedMatrixCell = ref(null)
const showReportBuilder = ref(false)
const map = ref(null)
const mapInitialized = ref(false)
const toast = ref({ show: false, message: '', type: 'success' })
const markerRefs = ref({})
const regionalCenters = [
  { province: 'Jawa', coords: [-7.250445, 112.768845], label: 'Greater Java Hub' },
  { province: 'Sumatera', coords: [0.789275, 113.921327], label: 'Sumatera Banking Cluster' },
  { province: 'Kalimantan', coords: [-1.493850, 113.144722], label: 'Kalimantan Regional Center' },
  { province: 'Sulawesi', coords: [-0.789275, 120.741444], label: 'Sulawesi Growth Corridor' },
  { province: 'Papua', coords: [-4.931132, 140.970716], label: 'Papua Emerging Hub' }
]

const showAddWatchlist = ref(false)
const newWatchlistName = ref('')
const newWatchlistOS = ref('')
const newWatchlistDPD = ref(0)
const newWatchlistTrigger = ref('Payment Delay')
const showRemoveWatchlist = ref(false)
const selectedWatchlistToRemove = ref(null)
const removeReason = ref('')

const watchlistData = ref([
  { account: 'Bhakti Nusantara Corp', os: 'IDR 850 Billion', dpd: 15, trigger: 'Payment Delay' },
  { account: 'Citra Baru Property', os: 'IDR 420 Billion', dpd: 0, trigger: 'Ratio Drop' },
  { account: 'Pioneer Logistik Tbk', os: 'IDR 310 Billion', dpd: 0, trigger: 'Negative News' },
  { account: 'Graha Sentosa Tbk', os: 'IDR 150 Billion', dpd: 32, trigger: 'DPD > 30' },
  { account: 'Pratama Steel', os: 'IDR 95 Billion', dpd: 8, trigger: 'Covenant Breach' },
])

function showToastMessage(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3200)
}

function submitAddWatchlist() {
  if (!newWatchlistName.value || !newWatchlistOS.value) return
  watchlistData.value.push({
    account: newWatchlistName.value,
    os: newWatchlistOS.value,
    dpd: newWatchlistDPD.value || 0,
    trigger: newWatchlistTrigger.value
  })
  newWatchlistName.value = ''
  newWatchlistOS.value = ''
  newWatchlistDPD.value = 0
  newWatchlistTrigger.value = 'Payment Delay'
  showAddWatchlist.value = false
  showToastMessage('Borrower added to watchlist and queued for risk review.')
}

function requestRemoveWatchlist(w) {
  selectedWatchlistToRemove.value = w
  removeReason.value = ''
  showRemoveWatchlist.value = true
}

function submitRemoveWatchlist() {
  if (!removeReason.value) return
  watchlistData.value = watchlistData.value.filter(x => x.account !== selectedWatchlistToRemove.value.account)
  showRemoveWatchlist.value = false
  selectedWatchlistToRemove.value = null
  removeReason.value = ''
  showToastMessage('Watchlist removal request submitted for committee approval.', 'warning')
}

// Custom stress values
const stressRates = ref(0)
const stressNPL = ref(0)

const navigationGroups = [
  {
    title: 'Overview & Exposure',
    items: [
      { id: 'overview', label: 'Portfolio Overview', icon: 'pie-chart' },
      { id: 'industry', label: 'Industry Exposure', icon: 'server' },
      { id: 'geographic', label: 'Geographic Exposure', icon: 'map' },
      { id: 'sbl', label: 'Single Borrower Limit (SBL)', icon: 'shield' },
      { id: 'top-exposures', label: 'Top 20 Exposures', icon: 'list' },
      { id: 'concentration-matrix', label: 'Concentration Matrix', icon: 'grid' },
    ]
  },
  {
    title: 'Risk Deterioration & EWS',
    items: [
      { id: 'ews', label: 'Early Warning System (EWS)', icon: 'alert-triangle', badge: '3 Alerts', badgeType: 'warning' },
      { id: 'covenants', label: 'Covenant Breach', icon: 'activity', badge: '1 Breach', badgeType: 'danger' },
      { id: 'watchlist', label: 'Watchlist Management', icon: 'eye' },
      { id: 'stress-testing', label: 'Stress Testing Scenario', icon: 'sliders' },
      { id: 'ecl', label: 'ECL Stage (PSAK 71)', icon: 'percent' },
      { id: 'simulation', label: 'What-if Simulator', icon: 'terminal' },
    ]
  }
]

// Mock databases
const overviewKPIs = computed(() => [
  { title: 'Total Portfolio OS', value: 'IDR 12.42 T', change: '+4.2%', trendUp: true, icon: 'dollar-sign' },
  { title: 'Active Loan Accounts', value: '14,230', change: '+1.5%', trendUp: true, icon: 'users' },
  { title: 'Portfolio NPL Ratio', value: '2.14%', change: '-0.3%', trendUp: false, icon: 'trending-down' },
  { title: 'Watchlist Borrowers', value: '142 Accs', change: '+2.8%', trendUp: true, icon: 'eye' }
])

const industryData = [
  { name: 'KBLI 10 - Food & Beverage Processing', kbli: '10XXX', os: 'IDR 2.45 Trillion', pct: '19.7%', limit: 'IDR 3.00 T', usage: 81.6 },
  { name: 'KBLI 41 - Real Estate Development', kbli: '41XXX', os: 'IDR 2.89 Trillion', pct: '23.2%', limit: 'IDR 2.50 T', usage: 115.6 },
  { name: 'KBLI 46 - Wholesale Trade Exporters', kbli: '46XXX', os: 'IDR 1.84 Trillion', pct: '14.8%', limit: 'IDR 2.50 T', usage: 73.6 },
  { name: 'KBLI 01 - Agriculture & Palm Oil Plantation', kbli: '01XXX', os: 'IDR 1.22 Trillion', pct: '9.8%', limit: 'IDR 2.00 T', usage: 61.0 },
]

const geographicData = [
  { province: 'Jawa', os: 'IDR 7.82 Trillion', pct: '62.9%', npl: 1.8 },
  { province: 'Sumatera', os: 'IDR 2.45 Trillion', pct: '19.7%', npl: 2.5 },
  { province: 'Kalimantan', os: 'IDR 1.15 Trillion', pct: '9.2%', npl: 3.1 },
  { province: 'Sulawesi', os: 'IDR 0.64 Trillion', pct: '5.1%', npl: 1.4 },
  { province: 'Papua', os: 'IDR 0.36 Trillion', pct: '2.9%', npl: 4.2 },
]

function initializeMap() {
  if (mapInitialized.value) return
  const mapElement = document.getElementById('portfolio-map')
  if (!mapElement) return

  map.value = L.map(mapElement, {
    center: [-2.5489, 118.0149],
    zoom: 5,
    zoomControl: true,
    attributionControl: false,
  })

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">Carto</a>',
    maxZoom: 18,
  }).addTo(map.value)

  regionalCenters.forEach(center => {
    const marker = L.circleMarker(center.coords, {
      radius: 10,
      color: '#0f766e',
      fillColor: '#14b8a6',
      fillOpacity: 0.85,
      weight: 2,
      opacity: 0.95,
    })
      .addTo(map.value)
      .bindPopup(`<strong>${center.province}</strong><br>${center.label}`)
      .on('click', () => {
        selectedProvince.value = center.province
      })

    markerRefs.value[center.province] = marker
  })

  if (markerRefs.value[selectedProvince.value]) {
    markerRefs.value[selectedProvince.value].openPopup()
  }

  mapInitialized.value = true
}

onMounted(() => {
  if (typeof window === 'undefined') return
  if (activeTab.value === 'geographic') {
    nextTick().then(initializeMap)
  }
})

watch(activeTab, async (tab) => {
  if (tab === 'geographic') {
    await nextTick()
    initializeMap()
  }

  if (tab === 'ews') {
    showToastMessage('EWS panel loaded with active alerts.', 'warning')
  }
})

watch(selectedProvince, (province) => {
  if (!mapInitialized.value || !map.value || !province) return
  const center = regionalCenters.find(item => item.province === province)
  if (!center) return

  map.value.flyTo(center.coords, 6, { duration: 1.2 })
  if (markerRefs.value[province]) {
    markerRefs.value[province].openPopup()
  }
})

const sblData = [
  { name: 'Astra Group Conglomerate', type: 'GROUP', os: 'IDR 1.85 Trillion', limit: 'IDR 2.50 T', pctCapital: 14.8, usage: 74.0 },
  { name: 'Sinarmas Group Corporate', type: 'GROUP', os: 'IDR 2.41 Trillion', limit: 'IDR 2.50 T', pctCapital: 19.2, usage: 96.4 },
  { name: 'Indofood Sukses Makmur Tbk', type: 'SINGLE', os: 'IDR 1.25 Trillion', limit: 'IDR 1.50 T', pctCapital: 10.0, usage: 83.3 },
  { name: 'Djarum Group Conglomerate', type: 'GROUP', os: 'IDR 2.80 Trillion', limit: 'IDR 2.50 T', pctCapital: 22.4, usage: 112.0 },
]

const topExposures = [
  { name: 'Sinarmas Group Corporate', os: 'IDR 2.41 Trillion', grade: 'AAA', dpd: 0, trend: 'Stable' },
  { name: 'Djarum Group Conglomerate', os: 'IDR 1.95 Trillion', grade: 'AA', dpd: 0, trend: 'Growing' },
  { name: 'Indofood Sukses Makmur Tbk', os: 'IDR 1.25 Trillion', grade: 'AAA', dpd: 0, trend: 'Stable' },
  { name: 'Astra Group Conglomerate', os: 'IDR 1.12 Trillion', grade: 'AAA', dpd: 0, trend: 'Stable' },
  { name: 'Bhakti Nusantara Corp', os: 'IDR 0.85 Trillion', grade: 'BB', dpd: 15, trend: 'Decreasing' },
]

const matrixRows = [
  {
    industry: 'Food & Beverage Processing',
    cells: [
      { region: 'Jawa', os: '1.20 T', accounts: 242, intensity: 'normal', details: [{ name: 'Indofood', os: '1.25 T', grade: 'AAA' }] },
      { region: 'Sumatera', os: '0.45 T', accounts: 110, intensity: 'normal', details: [{ name: 'Sumatra Agri', os: '0.45 T', grade: 'AA' }] },
      { region: 'Kalimantan', os: '0.22 T', accounts: 85, intensity: 'normal', details: [{ name: 'Borneo Food', os: '0.22 T', grade: 'A' }] },
      { region: 'Sulawesi', os: '0.12 T', accounts: 40, intensity: 'normal', details: [{ name: 'Celebes Ocean', os: '0.12 T', grade: 'A' }] }
    ]
  },
  {
    industry: 'Real Estate & Property',
    cells: [
      { region: 'Jawa', os: '2.10 T', accounts: 88, intensity: 'high', details: [{ name: 'Sinarmas Land', os: '2.10 T', grade: 'AA' }] },
      { region: 'Sumatera', os: '0.85 T', accounts: 54, intensity: 'medium', details: [{ name: 'Andalas Realty', os: '0.85 T', grade: 'BB' }] },
      { region: 'Kalimantan', os: '0.45 T', accounts: 30, intensity: 'normal', details: [{ name: 'Equator Dev', os: '0.45 T', grade: 'BBB' }] },
      { region: 'Sulawesi', os: '0.22 T', accounts: 15, intensity: 'normal', details: [{ name: 'Manado Indah', os: '0.22 T', grade: 'BBB' }] }
    ]
  }
]

const ewsAlerts = ref([
  { id: 1, severity: 'Red', borrower: 'Bhakti Nusantara Corp', signal: 'Debt Service Coverage Ratio (DSCR) dropped below 1.05x. Debt payment anomaly detected.', date: 'May 20, 2026', acknowledged: false },
  { id: 2, severity: 'Amber', borrower: 'Citra Baru Property', signal: 'Covenant Debt-to-Equity is nearing critical limit. Actual values: 2.85x vs limit threshold: 3.0x.', date: 'May 22, 2026', acknowledged: false },
  { id: 3, severity: 'Amber', borrower: 'Pioneer Logistik Tbk', signal: 'Adverse local media sentiment detected. Class Action lawsuit filed by logistics partners.', date: 'May 23, 2026', acknowledged: false },
])

const covenants = ref([
  { id: 1, borrower: 'Bhakti Nusantara Corp', rule: 'Debt-to-Equity ratio must not exceed 2.50x', status: 'Breach', actual: '2.95x', threshold: '2.50x' },
  { id: 2, borrower: 'Citra Baru Property', rule: 'Current ratio must remain above 1.20x', status: 'Compliant', actual: '1.42x', threshold: '1.20x' },
])

const scenarios = [
  { name: 'Mild Market Softening', rates: 150, npl: 1.5 },
  { name: 'Severe Economic Crisis', rates: 350, npl: 4.5 },
  { name: 'Custom Rate Shock Only', rates: 250, npl: 0.0 }
]

const eclStages = [
  { stage: 'Stage 1 (Normal)', pdRange: '0.1% - 1.5%', os: 'IDR 10.25 Trillion', desc: 'No significant increase in credit risk since origination. Provisioned on 12-month ECL calculation model.', ecl: 'IDR 51 Billion' },
  { stage: 'Stage 2 (Watchlist)', pdRange: '1.5% - 8.0%', os: 'IDR 1.82 Trillion', desc: 'Significant increase in credit risk. Provisioned on lifetime expected credit losses calculation methodology.', ecl: 'IDR 182 Billion' },
  { stage: 'Stage 3 (Default)', pdRange: '100% (Default)', os: 'IDR 0.35 Trillion', desc: 'Objective evidence of impairment or default (e.g. Days Past Due > 90 days). Provisioned at 100% lifetime default value.', ecl: 'IDR 245 Billion' }
]

// Simulator accounts data
const simAccounts = ref([
  { name: 'Purnama Property Group', sector: 'Real Estate', os: 'IDR 0.85 T', active: false },
  { name: 'Kalpataru Food Processor', sector: 'Food Processing', os: 'IDR 0.42 T', active: false }
])

// Simulator Computeds
const currentSimOS = computed(() => {
  let base = 12.42
  simAccounts.value.forEach(acc => {
    if (acc.active) {
      base += parseFloat(acc.os.replace('IDR ', '').replace(' T', ''))
    }
  })
  return base
})

const currentSimNPL = computed(() => {
  let base = 2.14
  simAccounts.value.forEach(acc => {
    if (acc.active) {
      base += acc.sector === 'Real Estate' ? 0.35 : 0.08
    }
  })
  return base
})

const currentSimConcentration = computed(() => {
  let base = 23.2
  simAccounts.value.forEach(acc => {
    if (acc.active && acc.sector === 'Real Estate') {
      base += 3.8
    }
  })
  return base
})

// Actions
function acknowledgeAlert(alert) {
  alert.acknowledged = true
  showToastMessage('EWS alert acknowledged and activity logged.', 'success')
}

function cureCovenant(cov) {
  cov.status = 'Compliant'
  cov.actual = '2.40x'
}

function applyScenarioPreset(sc) {
  stressRates.value = sc.rates
  stressNPL.value = sc.npl
}

function toggleSimAccount(sim) {
  sim.active = !sim.active
}

function resetSimulation() {
  simAccounts.value.forEach(sim => sim.active = false)
}

function exportMatrix() {
  showToastMessage('Concentration matrix export queued for download.', 'success')
}

function generateReport() {
  showReportBuilder.value = false
  showToastMessage('Portfolio report generated successfully.', 'success')
}
</script>

<style scoped>
.portfolio-monitoring {
  scrollbar-color: #1b2530 #0a0f14;
}
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  outline: none;
}
input[type="range"]::-webkit-slider-runnable-track {
  height: 10px;
  border-radius: 999px;
  background: #e2e8f0;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: #14b8a6;
  border: 3px solid white;
  box-shadow: 0 0 8px rgba(20, 184, 166, 0.35);
  margin-top: -4px;
}
input[type="range"]::-moz-range-track {
  height: 10px;
  border-radius: 999px;
  background: #e2e8f0;
}
input[type="range"]::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: #14b8a6;
  border: 3px solid white;
  box-shadow: 0 0 8px rgba(20, 184, 166, 0.35);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.18s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-enter-to, .fade-leave-from {
  opacity: 1;
}
</style>
