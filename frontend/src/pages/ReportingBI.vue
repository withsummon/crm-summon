<template>
   <div class="flex h-full flex-col bg-gray-50 font-sans select-none">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-[12px] bg-gradient-to-br from-teal-500 to-teal-700">
            <FeatherIcon name="bar-chart-2" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-ink-gray-9">{{ __('Reporting & Business Intelligence') }}</h1>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <button @click="doRefresh" class="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-50 transition-colors bg-white">
            <FeatherIcon :name="refreshing ? 'loader' : 'refresh-cw'" class="h-3.5 w-3.5" :class="refreshing && 'animate-spin'" />
            {{ __('Refresh') }}
          </button>
          <button @click="doExport" class="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 transition-colors">
            <FeatherIcon name="download" class="h-3.5 w-3.5" />
            {{ __('Export') }}
          </button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex flex-1 min-h-0 overflow-hidden">
      <!-- ── Left Sidebar ── -->
      <div class="w-52 bg-white border-r border-gray-200 flex flex-col shrink-0">
        <div class="p-3 space-y-0.5">
          <button
            v-for="nav in navItems" :key="nav.id"
            @click="activeNav = nav.id"
            class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-all text-left"
            :class="activeNav === nav.id ? 'bg-teal-50 text-teal-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'"
          >
            <FeatherIcon :name="nav.icon" class="h-3.5 w-3.5 shrink-0" />
            <span class="truncate">{{ nav.label }}</span>
            <span v-if="nav.badge" class="ml-auto text-[9px] bg-teal-100 text-teal-700 rounded-full px-1.5 font-bold">{{ nav.badge }}</span>
          </button>
        </div>

        <div class="mt-2 border-t border-gray-100 p-3">
          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-2">{{ __('Recent') }}</p>
          <div class="space-y-1">
            <button v-for="r in recentReports.slice(0,4)" :key="r.id" @click="openReport(r)"
              class="w-full text-left px-2 py-1.5 rounded-lg hover:bg-gray-50 transition-colors">
              <p class="text-[11px] text-gray-700 truncate font-medium">{{ r.name }}</p>
              <p class="text-[10px] text-gray-400">{{ r.lastRun }}</p>
            </button>
          </div>
        </div>

        <div class="mt-auto p-3 border-t border-gray-100">
          <p class="text-[10px] text-gray-400">{{ __('Last updated') }}: <span class="font-semibold text-gray-600">{{ lastUpdated }}</span></p>
        </div>
      </div>

      <!-- ── Main Content ── -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

        <!-- DASHBOARD -->
        <div v-if="activeNav === 'dashboard'" class="flex-1 overflow-y-auto p-5 space-y-5">
          <!-- KPI Cards -->
          <div class="grid grid-cols-3 gap-4">
            <div v-for="kpi in kpis" :key="kpi.id" class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <div class="flex items-start justify-between mb-2">
                <div>
                  <p class="text-[10px] font-semibold text-gray-500 uppercase tracking-wide">{{ kpi.label }}</p>
                  <p class="text-xl font-black text-gray-900 mt-0.5">{{ kpi.value }}</p>
                </div>
                <span class="flex items-center gap-0.5 text-[10px] font-bold rounded-full px-2 py-0.5"
                  :class="kpi.up ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'">
                  <FeatherIcon :name="kpi.up ? 'trending-up' : 'trending-down'" class="h-3 w-3" />
                  {{ kpi.trend }}
                </span>
              </div>
              <div class="flex items-center justify-between text-[10px] text-gray-400 mb-1">
                <span>{{ __('Target') }}: {{ kpi.target }}</span>
                <span class="font-semibold" :class="kpi.pct >= 100 ? 'text-green-600' : 'text-amber-600'">{{ kpi.pct }}%</span>
              </div>
              <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all"
                  :class="kpi.pct >= 100 ? 'bg-green-500' : kpi.pct >= 80 ? 'bg-teal-500' : 'bg-amber-400'"
                  :style="{ width: Math.min(kpi.pct, 100) + '%' }" />
              </div>
            </div>
          </div>

          <!-- Charts Row -->
          <div class="grid grid-cols-3 gap-4">
            <!-- Disbursement Trend -->
            <div class="col-span-2 bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="text-sm font-bold text-gray-800">{{ __('Disbursement Trend') }}</h3>
                  <p class="text-[10px] text-gray-400">{{ __('Monthly (Rp Billion)') }}</p>
                </div>
                <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
                  <button v-for="ct in ['Bar','Line']" :key="ct" @click="chartType = ct"
                    class="px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all"
                    :class="chartType===ct ? 'bg-white text-teal-700 shadow-sm' : 'text-gray-400'">
                    {{ ct }}
                  </button>
                </div>
              </div>
              <svg class="w-full" :viewBox="`0 0 400 110`" preserveAspectRatio="none">
                <line v-for="i in 4" :key="i" x1="0" :y1="(110/4)*i" x2="400" :y2="(110/4)*i" stroke="#f3f4f6" stroke-width="1" />
                <template v-if="chartType==='Bar'">
                  <rect v-for="(v,i) in disbursement" :key="i"
                    :x="(400/disbursement.length)*i+3" :y="110-(v/maxDisb)*110"
                    :width="(400/disbursement.length)-6" :height="(v/maxDisb)*110"
                    :fill="i===disbursement.length-1?'#0d9488':'#99f6e4'" rx="2" />
                </template>
                <template v-else>
                  <polyline :points="linePoints" fill="none" stroke="#0d9488" stroke-width="2" stroke-linejoin="round" />
                  <circle v-for="(v,i) in disbursement" :key="i"
                    :cx="(400/disbursement.length)*i+(400/disbursement.length/2)"
                    :cy="110-(v/maxDisb)*110" r="3" fill="#0d9488" />
                </template>
              </svg>
              <div class="flex justify-around mt-1">
                <span v-for="(m,i) in months" :key="i" class="text-[9px] text-gray-400 flex-1 text-center">{{ m }}</span>
              </div>
            </div>

            <!-- Portfolio Donut -->
            <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <h3 class="text-sm font-bold text-gray-800 mb-0.5">{{ __('Portfolio Mix') }}</h3>
              <p class="text-[10px] text-gray-400 mb-3">{{ __('By product type') }}</p>
              <div class="flex flex-col items-center">
                <svg viewBox="0 0 120 120" class="w-28 h-28">
                  <circle cx="60" cy="60" r="42" fill="none" stroke="#f3f4f6" stroke-width="18" />
                  <circle v-for="seg in donutSegments" :key="seg.label"
                    cx="60" cy="60" r="42" fill="none"
                    :stroke="seg.color" stroke-width="18"
                    :stroke-dasharray="`${seg.dash} ${circumference}`"
                    :stroke-dashoffset="seg.dashoffset" />
                  <text x="60" y="56" text-anchor="middle" fill="#1f2937" font-size="10" font-weight="700">Rp 2.4T</text>
                  <text x="60" y="68" text-anchor="middle" fill="#9ca3af" font-size="7">Portfolio</text>
                </svg>
                <div class="w-full space-y-1 mt-1">
                  <div v-for="seg in portfolioBreakdown" :key="seg.label" class="flex items-center justify-between">
                    <div class="flex items-center gap-1.5">
                      <div class="w-2 h-2 rounded-full shrink-0" :style="{background:seg.color}" />
                      <span class="text-[10px] text-gray-600">{{ seg.label }}</span>
                    </div>
                    <span class="text-[10px] font-semibold text-gray-800">{{ seg.pct }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Row -->
          <div class="grid grid-cols-3 gap-4">
            <!-- NPL Trend -->
            <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <h3 class="text-sm font-bold text-gray-800 mb-0.5">{{ __('NPL Trend') }}</h3>
              <p class="text-[10px] text-gray-400 mb-2">{{ __('NPL ratio (%)') }}</p>
              <svg class="w-full" height="72" viewBox="0 0 200 72" preserveAspectRatio="none">
                <polygon :points="nplArea" fill="#fff7ed" />
                <polyline :points="nplPoints" fill="none" stroke="#f97316" stroke-width="1.5" stroke-linejoin="round" />
              </svg>
              <div class="flex justify-between text-[10px] text-gray-400 mt-1">
                <span>Jun</span><span>May</span>
              </div>
            </div>

            <!-- KPI Alerts -->
            <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <h3 class="text-sm font-bold text-gray-800 mb-3">{{ __('KPI Alerts') }}</h3>
              <div class="space-y-2">
                <div v-for="alert in kpiAlerts" :key="alert.id"
                  class="flex items-start gap-2 p-2 rounded-lg"
                  :class="alert.level==='warn' ? 'bg-amber-50' : 'bg-green-50'">
                  <FeatherIcon :name="alert.level==='warn' ? 'alert-triangle' : 'check-circle'"
                    class="h-3.5 w-3.5 shrink-0 mt-0.5"
                    :class="alert.level==='warn' ? 'text-amber-500' : 'text-green-500'" />
                  <div>
                    <p class="text-[11px] font-semibold text-gray-800">{{ alert.kpi }}</p>
                    <p class="text-[10px] text-gray-500">{{ alert.msg }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Recent Reports -->
            <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-bold text-gray-800">{{ __('Recent Reports') }}</h3>
                <button @click="activeNav='hub'" class="text-[10px] text-teal-600 hover:underline">{{ __('View all') }}</button>
              </div>
              <div class="space-y-1.5">
                <div v-for="r in recentReports.slice(0,5)" :key="r.id"
                  @click="openReport(r)"
                  class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                  <div class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0" :class="r.colorBg">
                    <FeatherIcon :name="r.icon" class="h-3.5 w-3.5" :class="r.colorText" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="text-[11px] font-semibold text-gray-800 truncate">{{ r.name }}</p>
                    <p class="text-[10px] text-gray-400">{{ r.lastRun }}</p>
                  </div>
                  <button @click.stop="downloadReport(r)" class="shrink-0">
                    <FeatherIcon name="download" class="h-3 w-3 text-gray-300 hover:text-teal-500" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- REPORT HUB -->
        <div v-else-if="activeNav==='hub'" class="flex-1 flex flex-col overflow-hidden">
          <div class="bg-white border-b border-gray-200 px-5 py-3 shrink-0">
            <div class="flex items-center gap-3">
              <div class="relative flex-1 max-w-md">
                <FeatherIcon name="search" class="absolute left-3 top-2.5 h-3.5 w-3.5 text-gray-400" />
                <input v-model="reportSearch" type="text" :placeholder="__('Search reports...')"
                  class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-teal-500" />
              </div>
              <select v-model="reportCategory" class="text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none bg-white text-gray-600">
                <option value="">{{ __('All Categories') }}</option>
                <option>Regulatory</option><option>Executive</option><option>Portfolio</option><option>Operations</option><option>Sales</option>
              </select>
              <button @click="showCreateReport = true" class="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-2 text-xs font-semibold text-white hover:bg-teal-700 transition-colors">
                <FeatherIcon name="plus" class="h-3.5 w-3.5" />{{ __('New Report') }}
              </button>
            </div>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <!-- Favorites -->
            <div class="mb-5">
              <h3 class="text-xs font-bold text-gray-700 uppercase tracking-wide mb-3">{{ __('Favorites') }}</h3>
              <div class="grid grid-cols-4 gap-3">
                <div v-for="r in favoriteReports" :key="r.id"
                  @click="openReport(r)"
                  class="bg-white rounded-xl border border-gray-200 p-4 cursor-pointer hover:border-teal-300 hover:shadow-md transition-all group">
                  <div class="w-9 h-9 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform" :class="r.colorBg">
                    <FeatherIcon :name="r.icon" class="h-4 w-4" :class="r.colorText" />
                  </div>
                  <p class="text-xs font-semibold text-gray-800 mb-0.5">{{ r.name }}</p>
                  <p class="text-[10px] text-gray-400">{{ r.category }}</p>
                  <div class="flex items-center justify-between mt-3">
                    <span class="text-[9px] text-gray-400">{{ r.lastRun }}</span>
                    <FeatherIcon name="star" class="h-3 w-3 text-amber-400 fill-amber-400" />
                  </div>
                </div>
                <div @click="showCreateReport = true"
                  class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-xl p-4 cursor-pointer hover:border-teal-300 transition-all flex flex-col items-center justify-center gap-2">
                  <FeatherIcon name="plus-circle" class="h-6 w-6 text-gray-300" />
                  <p class="text-[11px] text-gray-400 font-medium text-center">{{ __('New Report') }}</p>
                </div>
              </div>
            </div>

            <!-- All Reports Table -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
                <h3 class="text-xs font-bold text-gray-700">
                  {{ __('All Reports') }} <span class="text-gray-400 font-normal">({{ filteredReportsList.length }})</span>
                </h3>
              </div>
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-gray-100 bg-gray-50">
                    <th class="px-5 py-2.5 text-left font-semibold text-gray-500">{{ __('Report Name') }}</th>
                    <th class="px-4 py-2.5 text-left font-semibold text-gray-500">{{ __('Category') }}</th>
                    <th class="px-4 py-2.5 text-left font-semibold text-gray-500">{{ __('Schedule') }}</th>
                    <th class="px-4 py-2.5 text-left font-semibold text-gray-500">{{ __('Last Run') }}</th>
                    <th class="px-4 py-2.5 text-left font-semibold text-gray-500">{{ __('Format') }}</th>
                    <th class="px-4 py-2.5 text-right font-semibold text-gray-500">{{ __('Actions') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in filteredReportsList" :key="r.id"
                    class="border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition-colors"
                    @click="openReport(r)">
                    <td class="px-5 py-3">
                      <div class="flex items-center gap-2.5">
                        <div class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0" :class="r.colorBg">
                          <FeatherIcon :name="r.icon" class="h-3.5 w-3.5" :class="r.colorText" />
                        </div>
                        <div>
                          <p class="font-semibold text-gray-800">{{ r.name }}</p>
                          <p class="text-[10px] text-gray-400">{{ r.desc }}</p>
                        </div>
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <span class="rounded-full px-2 py-0.5 text-[10px] font-semibold" :class="categoryBadge(r.category)">{{ r.category }}</span>
                    </td>
                    <td class="px-4 py-3 text-gray-500">{{ r.schedule || '-' }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ r.lastRun }}</td>
                    <td class="px-4 py-3">
                      <div class="flex gap-1">
                        <span v-for="fmt in r.formats" :key="fmt" class="text-[9px] border border-gray-200 rounded px-1.5 py-0.5 text-gray-500 font-semibold">{{ fmt }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex items-center justify-end gap-1.5">
                        <button @click.stop="downloadReport(r)" class="p-1.5 rounded-lg hover:bg-teal-50 text-gray-400 hover:text-teal-600 transition-colors"><FeatherIcon name="download" class="h-3.5 w-3.5" /></button>
                        <button @click.stop="shareReport(r)" class="p-1.5 rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-500 transition-colors"><FeatherIcon name="share-2" class="h-3.5 w-3.5" /></button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- KPI MONITORING -->
        <div v-else-if="activeNav==='kpi'" class="flex-1 flex flex-col overflow-hidden">
          <div class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3">
            <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
              <button v-for="p in ['Daily','Weekly','Monthly','YTD']" :key="p" @click="kpiPeriod = p"
                class="px-3 py-1.5 rounded-md text-xs font-semibold transition-all"
                :class="kpiPeriod===p ? 'bg-white text-teal-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
                {{ p }}
              </button>
            </div>
            <span class="text-xs text-gray-400">{{ activePeriod }}</span>
            <button @click="showToast('KPI added')" class="ml-auto flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-50 transition-colors">
              <FeatherIcon name="plus" class="h-3.5 w-3.5" />{{ __('Add KPI') }}
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-gray-100 bg-gray-50">
                    <th class="px-5 py-3 text-left font-semibold text-gray-500">{{ __('KPI') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Actual') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Target') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Achievement') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('MoM') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Alert') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Trend') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="k in kpiTable" :key="k.id" class="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                    <td class="px-5 py-3">
                      <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full shrink-0" :class="k.alert==='OK' ? 'bg-green-400' : 'bg-amber-400'" />
                        <span class="font-semibold text-gray-800">{{ k.label }}</span>
                        <span class="text-[9px] text-gray-400 bg-gray-100 rounded px-1.5 py-0.5">{{ k.category }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-3 font-black text-gray-900">{{ k.value }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ k.target }}</td>
                    <td class="px-4 py-3">
                      <div class="flex items-center gap-2">
                        <div class="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div class="h-full rounded-full" :class="k.pct>=100?'bg-green-500':k.pct>=80?'bg-teal-500':'bg-amber-400'" :style="{width:Math.min(k.pct,100)+'%'}" />
                        </div>
                        <span class="font-semibold" :class="k.pct>=100?'text-green-600':'text-amber-600'">{{ k.pct }}%</span>
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <span class="flex items-center gap-0.5 text-[10px] font-bold" :class="k.up?'text-green-600':'text-red-500'">
                        <FeatherIcon :name="k.up?'arrow-up-right':'arrow-down-right'" class="h-3 w-3" />
                        {{ k.trend }}
                      </span>
                    </td>
                    <td class="px-4 py-3">
                      <span class="rounded-full px-2 py-0.5 text-[9px] font-bold"
                        :class="k.alert==='OK'?'bg-green-100 text-green-700':k.alert==='WARN'?'bg-amber-100 text-amber-700':'bg-red-100 text-red-700'">
                        {{ k.alert }}
                      </span>
                    </td>
                    <td class="px-4 py-3">
                      <svg :viewBox="`0 0 60 24`" class="w-16 h-6">
                        <polyline :points="sparkline(k.spark)" fill="none" :stroke="k.up?'#0d9488':'#f97316'" stroke-width="1.5" stroke-linejoin="round" />
                      </svg>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- PIVOT TABLE -->
        <div v-else-if="activeNav==='pivot'" class="flex-1 overflow-y-auto p-5">
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h3 class="text-sm font-bold text-gray-800">{{ __('Portfolio Pivot Analysis') }}</h3>
                <p class="text-[10px] text-gray-400">{{ __('Outstanding balance by product × branch (Rp Billion)') }}</p>
              </div>
              <button @click="doExport" class="flex items-center gap-1.5 text-xs text-gray-500 hover:text-teal-600 transition-colors border border-gray-200 rounded-lg px-3 py-1.5">
                <FeatherIcon name="download" class="h-3.5 w-3.5" />{{ __('Export Excel') }}
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-xs">
                <thead>
                  <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="px-5 py-3 text-left font-semibold text-gray-600 border-r border-gray-200">{{ __('Product / Branch') }}</th>
                    <th v-for="branch in pivotBranches" :key="branch" class="px-4 py-3 text-right font-semibold text-gray-600 min-w-[100px]">{{ branch }}</th>
                    <th class="px-4 py-3 text-right font-semibold text-teal-700 border-l border-gray-200">{{ __('Total') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in pivotData" :key="row.product" class="border-b border-gray-100 hover:bg-teal-50/30 transition-colors">
                    <td class="px-5 py-3 font-semibold text-gray-800 border-r border-gray-100">{{ row.product }}</td>
                    <td v-for="branch in pivotBranches" :key="branch" class="px-4 py-3 text-right text-gray-700">{{ row[branch] || '-' }}</td>
                    <td class="px-4 py-3 text-right font-black text-teal-700 border-l border-gray-200">{{ row.total }}</td>
                  </tr>
                  <tr class="bg-teal-50 border-t-2 border-teal-200 font-bold">
                    <td class="px-5 py-3 text-teal-700 font-black border-r border-gray-200">{{ __('Grand Total') }}</td>
                    <td v-for="branch in pivotBranches" :key="branch" class="px-4 py-3 text-right text-teal-800">{{ pivotTotals[branch] }}</td>
                    <td class="px-4 py-3 text-right text-teal-900 font-black text-sm border-l border-gray-200">Rp 2.4T</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- SCHEDULED REPORTS -->
        <div v-else-if="activeNav==='scheduled'" class="flex-1 flex flex-col overflow-hidden">
          <div class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3">
            <h3 class="text-sm font-semibold text-gray-800">{{ __('Scheduled Reports') }}</h3>
            <span class="text-[11px] text-gray-400">{{ schedules.length }} {{ __('schedules') }}</span>
            <button @click="showToast('Schedule created')" class="ml-auto flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 transition-colors">
              <FeatherIcon name="plus" class="h-3.5 w-3.5" />{{ __('Add Schedule') }}
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-gray-100 bg-gray-50">
                    <th class="px-5 py-3 text-left font-semibold text-gray-500">{{ __('Report') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Frequency') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Next Run') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Last Run') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Recipients') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Format') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Status') }}</th>
                    <th class="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in schedules" :key="s.id" class="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                    <td class="px-5 py-3 font-semibold text-gray-800">{{ s.report }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ s.frequency }}</td>
                    <td class="px-4 py-3 text-gray-700 font-medium">{{ s.nextRun }}</td>
                    <td class="px-4 py-3 text-gray-400">{{ s.lastRun }}</td>
                    <td class="px-4 py-3">
                      <div class="flex items-center gap-0.5">
                        <span v-for="(rec,i) in s.recipients.slice(0,2)" :key="i"
                          class="w-6 h-6 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center text-[9px] font-bold border border-white -ml-1 first:ml-0">
                          {{ rec[0] }}
                        </span>
                        <span v-if="s.recipients.length>2" class="text-[10px] text-gray-400 ml-1">+{{ s.recipients.length-2 }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex gap-1">
                        <span v-for="fmt in s.formats" :key="fmt" class="text-[9px] border border-gray-200 rounded px-1.5 py-0.5 text-gray-500 font-semibold">{{ fmt }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <span class="rounded-full px-2 py-0.5 text-[9px] font-bold"
                        :class="s.status==='Active'?'bg-green-100 text-green-700':s.status==='Failed'?'bg-red-100 text-red-700':'bg-gray-100 text-gray-500'">
                        {{ s.status }}
                      </span>
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex items-center gap-1">
                        <button class="p-1.5 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600"><FeatherIcon name="edit-2" class="h-3 w-3" /></button>
                        <button @click="deleteSchedule(s)" class="p-1.5 rounded hover:bg-red-50 text-gray-400 hover:text-red-500"><FeatherIcon name="trash-2" class="h-3 w-3" /></button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- REGULATORY REPORTS -->
        <div v-else-if="activeNav==='regulatory'" class="flex-1 flex flex-col overflow-hidden">
          <div class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3">
            <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
              <button v-for="t in ['OJK','Bank Indonesia','Tax']" :key="t" @click="regTab=t"
                class="px-3 py-1.5 rounded-md text-xs font-semibold transition-all"
                :class="regTab===t?'bg-white text-teal-700 shadow-sm':'text-gray-500 hover:text-gray-700'">
                {{ t }}
              </button>
            </div>
            <span class="text-xs text-gray-400">{{ activePeriod }}</span>
            <button @click="generateReg" class="ml-auto flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 transition-colors">
              <FeatherIcon name="file-text" class="h-3.5 w-3.5" />{{ __('Generate') }}
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-gray-100 bg-gray-50">
                    <th class="px-5 py-3 text-left font-semibold text-gray-500">{{ __('Report Name') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Type') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Period') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Due Date') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Validation') }}</th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">{{ __('Status') }}</th>
                    <th class="px-4 py-3 text-right font-semibold text-gray-500">{{ __('Actions') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in currentRegReports" :key="r.id" class="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                    <td class="px-5 py-3 font-semibold text-gray-800">{{ r.name }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ r.type }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ r.period }}</td>
                    <td class="px-4 py-3" :class="r.overdue?'text-red-500 font-semibold':'text-gray-700'">{{ r.dueDate }}</td>
                    <td class="px-4 py-3">
                      <span class="rounded-full px-2 py-0.5 text-[9px] font-bold" :class="r.valid?'bg-green-100 text-green-700':'bg-amber-100 text-amber-700'">{{ r.valid ? 'Valid' : 'Pending' }}</span>
                    </td>
                    <td class="px-4 py-3">
                      <span class="rounded-full px-2 py-0.5 text-[9px] font-bold"
                        :class="r.status==='Submitted'?'bg-teal-100 text-teal-700':r.status==='Ready'?'bg-blue-100 text-blue-700':'bg-gray-100 text-gray-600'">
                        {{ r.status }}
                      </span>
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex items-center justify-end gap-1.5">
                        <button class="p-1.5 rounded-lg hover:bg-teal-50 text-gray-400 hover:text-teal-600 transition-colors" @click="downloadReport(r)">
                          <FeatherIcon name="download" class="h-3.5 w-3.5" />
                        </button>
                        <button v-if="r.status!=='Submitted'" @click="submitReg(r)"
                          class="px-2.5 py-1 rounded-lg bg-teal-600 text-white text-[10px] font-semibold hover:bg-teal-700 transition-colors">
                          {{ __('Submit') }}
                        </button>
                        <span v-else class="text-[10px] text-teal-600 font-semibold">✓ {{ __('Submitted') }}</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- EXECUTIVE REPORTS -->
        <div v-else-if="activeNav==='executive'" class="flex-1 overflow-y-auto p-5">
          <div class="grid grid-cols-2 gap-4">
            <div v-for="rep in executiveReports" :key="rep.id"
              @click="openReport(rep)"
              class="bg-white rounded-xl border border-gray-200 shadow-sm p-5 hover:shadow-md transition-all cursor-pointer group">
              <div class="flex items-start justify-between mb-4">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center" :class="rep.colorBg">
                  <FeatherIcon :name="rep.icon" class="h-5 w-5" :class="rep.colorText" />
                </div>
                <span class="text-[10px] rounded-full px-2 py-0.5 font-semibold" :class="rep.statusClass">{{ rep.status }}</span>
              </div>
              <h3 class="text-sm font-bold text-gray-800 mb-1">{{ rep.name }}</h3>
              <p class="text-xs text-gray-400 mb-4">{{ rep.desc }}</p>
              <div class="flex items-center justify-between pt-3 border-t border-gray-100">
                <span class="text-[10px] text-gray-400">{{ rep.period }} · {{ rep.pages }} pages</span>
                <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click.stop="downloadReport(rep)" class="text-[10px] text-teal-600 font-semibold flex items-center gap-1 hover:underline">
                    <FeatherIcon name="download" class="h-3 w-3" />PDF
                  </button>
                  <button @click.stop="downloadReport(rep)" class="text-[10px] text-blue-600 font-semibold flex items-center gap-1 hover:underline">
                    <FeatherIcon name="file" class="h-3 w-3" />Excel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AD-HOC QUERY -->
        <div v-else-if="activeNav==='adhoc'" class="flex-1 flex min-h-0 overflow-hidden">
          <!-- Left: Tables -->
          <div class="w-64 border-r border-gray-200 bg-white flex flex-col shrink-0">
            <div class="p-4 border-b border-gray-100">
              <h3 class="text-sm font-bold text-gray-800">{{ __('Visual Query Builder') }}</h3>
              <p class="text-[10px] text-gray-400 mt-0.5">{{ __('Select table and columns') }}</p>
            </div>
            <div class="flex-1 overflow-y-auto p-3 space-y-2">
              <div v-for="tbl in queryTables" :key="tbl.name"
                class="p-3 rounded-lg border border-gray-200 cursor-pointer hover:border-teal-300 transition-all"
                :class="selectedTable===tbl.name?'bg-teal-50 border-teal-300':''"
                @click="selectedTable=tbl.name; buildQuery()">
                <div class="flex items-center gap-2 mb-1">
                  <FeatherIcon name="database" class="h-3.5 w-3.5 text-teal-600" />
                  <span class="text-xs font-semibold text-gray-800">{{ tbl.name }}</span>
                </div>
                <div v-if="selectedTable===tbl.name" class="space-y-1 mt-2">
                  <label v-for="col in tbl.columns" :key="col" class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="selectedColumns" :value="col" class="rounded text-teal-600" />
                    <span class="text-[11px] text-gray-600">{{ col }}</span>
                  </label>
                </div>
                <p v-else class="text-[10px] text-gray-400">{{ tbl.columns.length }} columns</p>
              </div>
            </div>
          </div>

          <!-- Right: SQL + Results -->
          <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
            <div class="border-b border-gray-200 p-4 bg-white shrink-0">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-gray-700">{{ __('SQL Preview') }}</span>
                <button @click="runQuery" class="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 transition-colors">
                  <FeatherIcon :name="queryRunning?'loader':'play'" class="h-3.5 w-3.5" :class="queryRunning&&'animate-spin'" />
                  {{ queryRunning ? __('Running...') : __('Run Query') }}
                </button>
              </div>
              <div class="bg-gray-900 rounded-lg p-3 font-mono text-[11px] text-green-400">
                <span class="text-blue-400">SELECT </span>{{ selectedColumns.join(', ') || '*' }}<br />
                <span class="text-blue-400">FROM </span><span class="text-yellow-400">{{ selectedTable || 'crm_lead' }}</span><br />
                <span class="text-blue-400">WHERE </span>status <span class="text-red-400">!=</span> <span class="text-green-300">'Closed'</span><br />
                <span class="text-blue-400">LIMIT </span>100
              </div>
            </div>
            <div class="flex-1 overflow-auto p-4">
              <div v-if="queryRunning" class="flex items-center justify-center h-32">
                <div class="flex items-center gap-2 text-sm text-gray-500">
                  <FeatherIcon name="loader" class="h-4 w-4 animate-spin text-teal-500" />{{ __('Running query...') }}
                </div>
              </div>
              <template v-else-if="queryResults.length > 0">
                <div class="flex items-center justify-between mb-3">
                  <span class="text-xs text-gray-500">{{ queryResults.length }} {{ __('rows') }} · {{ queryTime }}ms</span>
                  <button @click="doExport" class="text-xs text-teal-600 font-semibold hover:underline flex items-center gap-1">
                    <FeatherIcon name="download" class="h-3 w-3" />{{ __('Export CSV') }}
                  </button>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <table class="w-full text-xs">
                    <thead>
                      <tr class="bg-gray-50 border-b border-gray-100">
                        <th v-for="col in queryResultCols" :key="col" class="px-4 py-2.5 text-left font-semibold text-gray-500">{{ col }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row,i) in queryResults" :key="i" class="border-b border-gray-50 hover:bg-gray-50">
                        <td v-for="col in queryResultCols" :key="col" class="px-4 py-2.5 text-gray-700">{{ row[col] }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </template>
              <div v-else class="flex flex-col items-center justify-center h-40 text-gray-400">
                <FeatherIcon name="terminal" class="h-8 w-8 mb-2 text-gray-300" />
                <p class="text-sm font-medium">{{ __('Run a query to see results') }}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast" class="fixed bottom-5 right-5 z-50 bg-gray-800 text-white text-sm font-medium px-4 py-2.5 rounded-xl shadow-xl flex items-center gap-2">
        <FeatherIcon name="check-circle" class="h-4 w-4 text-teal-400" />{{ toast }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

// ── Nav ──
const activeNav = ref('dashboard')
const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'bar-chart-2' },
  { id: 'hub', label: 'Report Hub', icon: 'folder', badge: '24' },
  { id: 'kpi', label: 'KPI Monitoring', icon: 'target' },
  { id: 'pivot', label: 'Pivot Table', icon: 'grid' },
  { id: 'scheduled', label: 'Scheduled Reports', icon: 'clock' },
  { id: 'regulatory', label: 'Regulatory Reports', icon: 'shield', badge: '3' },
  { id: 'executive', label: 'Executive Reports', icon: 'briefcase' },
  { id: 'adhoc', label: 'Ad-Hoc Query', icon: 'terminal' },
]

// ── Period / Refresh ──
const activePeriod = ref('May 2026')
const refreshing = ref(false)
const lastUpdated = ref('24 May 2026 09:15')

function doRefresh() {
  refreshing.value = true
  setTimeout(() => { refreshing.value = false; showToast('Data refreshed successfully') }, 1200)
}

// ── Dashboard KPIs ──
const kpis = [
  { id: 'portfolio', label: 'Total Portfolio', value: 'Rp 2.4T', target: 'Rp 2.5T', pct: 96, trend: '+8.2%', up: true },
  { id: 'npl', label: 'NPL Ratio', value: '2.14%', target: '< 3%', pct: 71, trend: '-0.3%', up: true },
  { id: 'disbursement', label: 'Disbursement MTD', value: 'Rp 186B', target: 'Rp 200B', pct: 93, trend: '+12.4%', up: true },
  { id: 'collection', label: 'Collection Rate', value: '97.8%', target: '> 95%', pct: 103, trend: '+0.5%', up: true },
  { id: 'car', label: 'CAR', value: '18.4%', target: '> 14%', pct: 131, trend: '+0.8%', up: true },
  { id: 'roa', label: 'ROA', value: '1.92%', target: '> 1.5%', pct: 128, trend: '+0.12%', up: true },
]

// ── Disbursement Chart ──
const chartType = ref('Bar')
const disbursement = [145, 162, 138, 175, 190, 168, 195, 182, 210, 198, 186, 220]
const months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May']
const maxDisb = computed(() => Math.max(...disbursement) * 1.1)

const linePoints = computed(() => {
  const W = 400, H = 110
  return disbursement.map((v, i) => {
    const x = (W / disbursement.length) * i + (W / disbursement.length / 2)
    const y = H - (v / maxDisb.value) * H
    return `${x},${y}`
  }).join(' ')
})

// ── Portfolio Donut ──
const portfolioBreakdown = [
  { label: 'Working Capital', pct: 38, color: '#0d9488' },
  { label: 'Investment Loan', pct: 24, color: '#06b6d4' },
  { label: 'KPR', pct: 18, color: '#8b5cf6' },
  { label: 'KKB', pct: 11, color: '#f59e0b' },
  { label: 'Others', pct: 9, color: '#10b981' },
]
const circumference = 2 * Math.PI * 42

const donutSegments = computed(() => {
  let accum = circumference / 4
  return portfolioBreakdown.map(seg => {
    const dash = (seg.pct / 100) * circumference
    const result = { ...seg, dash, dashoffset: accum }
    accum -= dash
    return result
  })
})

// ── NPL Trend SVG ──
const nplData = [2.8, 2.6, 2.7, 2.5, 2.4, 2.5, 2.3, 2.4, 2.2, 2.3, 2.14, 2.1]
const nplPoints = computed(() => {
  const W = 200, H = 72, max = 3.2, min = 1.8
  return nplData.map((v, i) => {
    const x = (W / (nplData.length - 1)) * i
    const y = H - ((v - min) / (max - min)) * H
    return `${x},${y}`
  }).join(' ')
})
const nplArea = computed(() => {
  const W = 200, H = 72, max = 3.2, min = 1.8
  const pts = nplData.map((v, i) => {
    const x = (W / (nplData.length - 1)) * i
    const y = H - ((v - min) / (max - min)) * H
    return `${x},${y}`
  })
  return `0,${H} ` + pts.join(' ') + ` ${W},${H}`
})

// ── KPI Alerts ──
const kpiAlerts = [
  { id: 1, level: 'ok', kpi: 'Collection Rate', msg: '97.8% — above threshold (95%)' },
  { id: 2, level: 'warn', kpi: 'BOPO Ratio', msg: '82.4% — approaching limit (85%)' },
  { id: 3, level: 'warn', kpi: 'LDR', msg: '89.2% — near ceiling (90%)' },
  { id: 4, level: 'ok', kpi: 'CAR', msg: '18.4% — comfortably above 14%' },
]

// ── Recent Reports ──
const recentReports = ref([
  { id: 1, name: 'OJK LPBB Monthly', category: 'Regulatory', lastRun: '24 May 09:00', icon: 'shield', colorBg: 'bg-blue-100', colorText: 'text-blue-600' },
  { id: 2, name: 'Board Pack May 2026', category: 'Executive', lastRun: '24 May 08:30', icon: 'briefcase', colorBg: 'bg-purple-100', colorText: 'text-purple-600' },
  { id: 3, name: 'NPL Report MTD', category: 'Portfolio', lastRun: '23 May 18:00', icon: 'trending-down', colorBg: 'bg-amber-100', colorText: 'text-amber-600' },
  { id: 4, name: 'Disbursement Summary', category: 'Operations', lastRun: '23 May 17:30', icon: 'credit-card', colorBg: 'bg-teal-100', colorText: 'text-teal-600' },
  { id: 5, name: 'Sales Pipeline Report', category: 'Sales', lastRun: '23 May 16:00', icon: 'trending-up', colorBg: 'bg-green-100', colorText: 'text-green-600' },
])

// ── Report Hub ──
const reportSearch = ref('')
const reportCategory = ref('')
const showCreateReport = ref(false)

const favoriteReports = [
  { id: 1, name: 'Board Pack', category: 'Executive', icon: 'briefcase', colorBg: 'bg-purple-100', colorText: 'text-purple-600', lastRun: '24 May' },
  { id: 2, name: 'OJK LPBB Report', category: 'Regulatory', icon: 'shield', colorBg: 'bg-blue-100', colorText: 'text-blue-600', lastRun: '24 May' },
  { id: 3, name: 'NPL Monitoring', category: 'Portfolio', icon: 'activity', colorBg: 'bg-amber-100', colorText: 'text-amber-600', lastRun: '23 May' },
]

const allReports = ref([
  { id: 1, name: 'OJK LPBB Monthly Report', desc: 'Laporan Bulanan Bank Umum', category: 'Regulatory', schedule: 'Monthly', lastRun: '24 May 09:00', formats: ['PDF', 'XML'], icon: 'shield', colorBg: 'bg-blue-100', colorText: 'text-blue-600' },
  { id: 2, name: 'Board Pack Dashboard', desc: 'Executive summary for board', category: 'Executive', schedule: 'Monthly', lastRun: '24 May 08:30', formats: ['PDF', 'PPT'], icon: 'briefcase', colorBg: 'bg-purple-100', colorText: 'text-purple-600' },
  { id: 3, name: 'NPL Report MTD', desc: 'Non-performing loan monitoring', category: 'Portfolio', schedule: 'Daily', lastRun: '23 May 18:00', formats: ['Excel', 'PDF'], icon: 'trending-down', colorBg: 'bg-amber-100', colorText: 'text-amber-600' },
  { id: 4, name: 'Disbursement Summary', desc: 'Daily disbursement tracker', category: 'Operations', schedule: 'Daily', lastRun: '23 May 17:30', formats: ['Excel', 'CSV'], icon: 'credit-card', colorBg: 'bg-teal-100', colorText: 'text-teal-600' },
  { id: 5, name: 'Sales Pipeline Report', desc: 'Pipeline and conversion analytics', category: 'Sales', schedule: 'Weekly', lastRun: '23 May 16:00', formats: ['PDF', 'Excel'], icon: 'trending-up', colorBg: 'bg-green-100', colorText: 'text-green-600' },
  { id: 6, name: 'BI LKPBU Report', desc: 'Laporan Keuangan Publikasi BU', category: 'Regulatory', schedule: 'Quarterly', lastRun: '30 Mar 2026', formats: ['XML', 'PDF'], icon: 'file-text', colorBg: 'bg-indigo-100', colorText: 'text-indigo-600' },
  { id: 7, name: 'Credit Approval Analytics', desc: 'Approval rate & SLA tracking', category: 'Portfolio', schedule: 'Weekly', lastRun: '22 May 09:00', formats: ['Excel', 'PDF'], icon: 'check-circle', colorBg: 'bg-emerald-100', colorText: 'text-emerald-600' },
  { id: 8, name: 'Collection Officer Report', desc: 'Collection productivity & recovery', category: 'Operations', schedule: 'Daily', lastRun: '23 May 18:00', formats: ['Excel'], icon: 'users', colorBg: 'bg-rose-100', colorText: 'text-rose-600' },
  { id: 9, name: 'PPN & PPh Monthly', desc: 'Tax reconciliation report', category: 'Regulatory', schedule: 'Monthly', lastRun: '30 Apr 2026', formats: ['Excel', 'CSV'], icon: 'percent', colorBg: 'bg-gray-100', colorText: 'text-gray-600' },
  { id: 10, name: 'Vintage Analysis', desc: 'Portfolio vintage cohort analysis', category: 'Portfolio', schedule: 'Monthly', lastRun: '30 Apr 2026', formats: ['Excel', 'PDF'], icon: 'layers', colorBg: 'bg-sky-100', colorText: 'text-sky-600' },
])

const filteredReportsList = computed(() => {
  let list = allReports.value
  if (reportSearch.value) {
    const q = reportSearch.value.toLowerCase()
    list = list.filter(r => r.name.toLowerCase().includes(q) || r.category.toLowerCase().includes(q))
  }
  if (reportCategory.value) list = list.filter(r => r.category === reportCategory.value)
  return list
})

function categoryBadge(cat) {
  const map = { Regulatory: 'bg-blue-100 text-blue-700', Executive: 'bg-purple-100 text-purple-700', Portfolio: 'bg-amber-100 text-amber-700', Operations: 'bg-teal-100 text-teal-700', Sales: 'bg-green-100 text-green-700' }
  return map[cat] || 'bg-gray-100 text-gray-600'
}

// ── KPI Table ──
const kpiPeriod = ref('Monthly')
const kpiTable = [
  { id: 1, label: 'Total Portfolio', category: 'Balance Sheet', value: 'Rp 2.4T', target: 'Rp 2.5T', pct: 96, trend: '+8.2%', up: true, alert: 'OK', spark: [180, 185, 192, 188, 195, 200, 210, 205, 215, 220, 230, 240] },
  { id: 2, label: 'NPL Ratio', category: 'Asset Quality', value: '2.14%', target: '< 3.0%', pct: 71, trend: '-0.30%', up: true, alert: 'OK', spark: [2.8, 2.6, 2.7, 2.5, 2.4, 2.5, 2.3, 2.4, 2.2, 2.3, 2.14, 2.1] },
  { id: 3, label: 'CAR', category: 'Capital', value: '18.4%', target: '> 14.0%', pct: 131, trend: '+0.8%', up: true, alert: 'OK', spark: [16, 16.5, 17, 17.2, 17.8, 17.5, 18, 17.9, 18.2, 18.1, 18.4, 18.6] },
  { id: 4, label: 'LDR', category: 'Liquidity', value: '89.2%', target: '< 90%', pct: 99, trend: '+1.2%', up: false, alert: 'WARN', spark: [84, 85, 86, 87, 86, 87, 88, 87.5, 88, 88.5, 89, 89.2] },
  { id: 5, label: 'BOPO', category: 'Efficiency', value: '82.4%', target: '< 85%', pct: 97, trend: '+0.6%', up: false, alert: 'WARN', spark: [78, 79, 80, 80.5, 81, 80.5, 82, 81.5, 82, 82.5, 82.4, 82.8] },
  { id: 6, label: 'ROA', category: 'Profitability', value: '1.92%', target: '> 1.5%', pct: 128, trend: '+0.12%', up: true, alert: 'OK', spark: [1.5, 1.6, 1.65, 1.7, 1.75, 1.72, 1.78, 1.80, 1.85, 1.88, 1.92, 1.95] },
  { id: 7, label: 'NIM', category: 'Profitability', value: '4.82%', target: '> 4.0%', pct: 120, trend: '+0.08%', up: true, alert: 'OK', spark: [4.2, 4.3, 4.4, 4.5, 4.55, 4.6, 4.65, 4.7, 4.72, 4.75, 4.8, 4.82] },
  { id: 8, label: 'Collection Rate', category: 'Collection', value: '97.8%', target: '> 95%', pct: 103, trend: '+0.5%', up: true, alert: 'OK', spark: [95, 96, 96.5, 97, 96.8, 97.2, 97, 97.3, 97.5, 97.6, 97.8, 97.9] },
]

function sparkline(data) {
  const W = 60, H = 24
  const max = Math.max(...data) * 1.05
  const min = Math.min(...data) * 0.95
  return data.map((v, i) => {
    const x = (W / (data.length - 1)) * i
    const y = H - ((v - min) / (max - min)) * H
    return `${x},${y}`
  }).join(' ')
}

// ── Scheduled Reports ──
const schedules = ref([
  { id: 1, report: 'OJK LPBB Monthly Report', frequency: 'Monthly', nextRun: '01 Jun 2026 06:00', lastRun: '24 May 09:00', recipients: ['Direktur', 'Risk', 'Finance'], formats: ['PDF', 'XML'], status: 'Active' },
  { id: 2, report: 'Daily Disbursement Summary', frequency: 'Daily', nextRun: '25 May 18:00', lastRun: '24 May 18:00', recipients: ['Ops Head', 'Branch'], formats: ['Excel'], status: 'Active' },
  { id: 3, report: 'NPL Weekly Report', frequency: 'Weekly', nextRun: '28 May 08:00', lastRun: '21 May 09:00', recipients: ['Risk', 'Finance'], formats: ['PDF', 'Excel'], status: 'Active' },
  { id: 4, report: 'Board Pack Dashboard', frequency: 'Monthly', nextRun: '01 Jun 2026 07:00', lastRun: '24 May 08:30', recipients: ['Board', 'CEO', 'CFO'], formats: ['PDF', 'PPT'], status: 'Active' },
  { id: 5, report: 'Tax PPN Monthly', frequency: 'Monthly', nextRun: '01 Jun 2026 06:00', lastRun: '01 May 2026', recipients: ['Finance', 'Tax'], formats: ['Excel', 'CSV'], status: 'Failed' },
  { id: 6, report: 'Vintage Analysis', frequency: 'Monthly', nextRun: '01 Jun 2026', lastRun: '01 May 2026', recipients: ['Risk'], formats: ['Excel'], status: 'Active' },
])

function deleteSchedule(s) {
  schedules.value = schedules.value.filter(x => x.id !== s.id)
  showToast('Schedule deleted')
}

// ── Regulatory Reports ──
const regTab = ref('OJK')

const ojkReports = ref([
  { id: 1, name: 'LPBB — Laporan Bulanan Bank Umum', type: 'Monthly', period: 'Apr 2026', dueDate: '15 May 2026', valid: true, status: 'Submitted', overdue: false },
  { id: 2, name: 'LKPBU — Laporan Keuangan Publikasi', type: 'Quarterly', period: 'Q1 2026', dueDate: '30 Apr 2026', valid: true, status: 'Submitted', overdue: false },
  { id: 3, name: 'LBU — Laporan Batas Usia', type: 'Monthly', period: 'May 2026', dueDate: '15 Jun 2026', valid: false, status: 'Draft', overdue: false },
  { id: 4, name: 'LHBU — Laporan Harian BU', type: 'Daily', period: '24 May 2026', dueDate: '25 May 2026', valid: true, status: 'Ready', overdue: false },
  { id: 5, name: 'LDP — Laporan Debitur Perorangan', type: 'Monthly', period: 'Apr 2026', dueDate: '10 May 2026', valid: true, status: 'Submitted', overdue: false },
])

const biReports = ref([
  { id: 1, name: 'LKPBU — BI Quarterly Report', type: 'Quarterly', period: 'Q1 2026', dueDate: '30 Apr 2026', valid: true, status: 'Submitted', overdue: false },
  { id: 2, name: 'Sistem Informasi Debitur (SID)', type: 'Monthly', period: 'Apr 2026', dueDate: '10 May 2026', valid: true, status: 'Submitted', overdue: false },
  { id: 3, name: 'SLIK — Sistem Layanan Informasi Keuangan', type: 'Monthly', period: 'May 2026', dueDate: '10 Jun 2026', valid: false, status: 'Draft', overdue: false },
])

const taxReports = ref([
  { id: 1, name: 'SPT PPN Masa April 2026', type: 'Monthly', period: 'Apr 2026', dueDate: '31 May 2026', valid: true, status: 'Ready', overdue: false },
  { id: 2, name: 'SPT PPh 21 Masa April 2026', type: 'Monthly', period: 'Apr 2026', dueDate: '20 May 2026', valid: true, status: 'Submitted', overdue: false },
  { id: 3, name: 'e-Faktur Pajak April 2026', type: 'Monthly', period: 'Apr 2026', dueDate: '15 May 2026', valid: true, status: 'Submitted', overdue: false },
])

const currentRegReports = computed(() => {
  if (regTab.value === 'OJK') return ojkReports.value
  if (regTab.value === 'Bank Indonesia') return biReports.value
  return taxReports.value
})

function generateReg() { showToast(`${regTab.value} report generated`) }
function submitReg(r) { r.status = 'Submitted'; showToast(`${r.name} submitted`) }

// ── Executive Reports ──
const executiveReports = [
  { id: 1, name: 'Board Pack — May 2026', desc: 'Executive summary with KPI, financial highlights, and portfolio overview', icon: 'briefcase', colorBg: 'bg-purple-100', colorText: 'text-purple-600', period: 'May 2026', pages: 24, status: 'Ready', statusClass: 'bg-green-100 text-green-700' },
  { id: 2, name: 'Risk Dashboard Report', desc: 'Comprehensive risk metrics, NPL analysis, and concentration report', icon: 'shield', colorBg: 'bg-amber-100', colorText: 'text-amber-600', period: 'May 2026', pages: 18, status: 'Ready', statusClass: 'bg-green-100 text-green-700' },
  { id: 3, name: 'Financial Performance Summary', desc: 'P&L, balance sheet highlights, and ROA/ROE analysis', icon: 'trending-up', colorBg: 'bg-teal-100', colorText: 'text-teal-600', period: 'May 2026', pages: 12, status: 'Draft', statusClass: 'bg-gray-100 text-gray-600' },
  { id: 4, name: 'Loan Portfolio Analytics', desc: 'Disbursement trend, vintage analysis, and segment breakdown', icon: 'pie-chart', colorBg: 'bg-sky-100', colorText: 'text-sky-600', period: 'May 2026', pages: 16, status: 'Ready', statusClass: 'bg-green-100 text-green-700' },
  { id: 5, name: 'Collection & Recovery Report', desc: 'Collection rate, officer productivity, and delinquency buckets', icon: 'users', colorBg: 'bg-rose-100', colorText: 'text-rose-600', period: 'May 2026', pages: 10, status: 'Generating...', statusClass: 'bg-blue-100 text-blue-700' },
  { id: 6, name: 'Operational Excellence Report', desc: 'SLA tracking, branch performance, and approval analytics', icon: 'activity', colorBg: 'bg-emerald-100', colorText: 'text-emerald-600', period: 'May 2026', pages: 14, status: 'Ready', statusClass: 'bg-green-100 text-green-700' },
]

// ── Pivot Table ──
const pivotBranches = ['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Bali']
const pivotData = [
  { product: 'Working Capital', Jakarta: 'Rp 412B', Surabaya: 'Rp 198B', Bandung: 'Rp 142B', Medan: 'Rp 89B', Bali: 'Rp 67B', total: 'Rp 908B' },
  { product: 'Investment Loan', Jakarta: 'Rp 285B', Surabaya: 'Rp 156B', Bandung: 'Rp 98B', Medan: 'Rp 54B', Bali: 'Rp 43B', total: 'Rp 636B' },
  { product: 'KPR', Jakarta: 'Rp 198B', Surabaya: 'Rp 87B', Bandung: 'Rp 76B', Medan: 'Rp 45B', Bali: 'Rp 62B', total: 'Rp 468B' },
  { product: 'KKB', Jakarta: 'Rp 124B', Surabaya: 'Rp 56B', Bandung: 'Rp 42B', Medan: 'Rp 28B', Bali: 'Rp 14B', total: 'Rp 264B' },
  { product: 'Multifinance', Jakarta: 'Rp 87B', Surabaya: 'Rp 44B', Bandung: 'Rp 32B', Medan: 'Rp 18B', Bali: 'Rp 11B', total: 'Rp 192B' },
]
const pivotTotals = { Jakarta: 'Rp 1.1T', Surabaya: 'Rp 541B', Bandung: 'Rp 390B', Medan: 'Rp 234B', Bali: 'Rp 197B' }

// ── Ad-Hoc Query ──
const selectedTable = ref('crm_lead')
const selectedColumns = ref(['name', 'lead_name', 'status', 'lead_owner'])
const queryRunning = ref(false)
const queryResults = ref([])
const queryResultCols = ref([])
const queryTime = ref(0)

const queryTables = [
  { name: 'crm_lead', columns: ['name', 'lead_name', 'status', 'lead_owner', 'source', 'industry', 'annual_revenue', 'creation'] },
  { name: 'crm_deal', columns: ['name', 'deal_name', 'status', 'owner', 'expected_amount', 'close_date', 'lead_source', 'stage'] },
  { name: 'credit_application', columns: ['name', 'borrower_name', 'facility_type', 'requested_amount', 'status', 'creation', 'tenor_months'] },
  { name: 'customer_360', columns: ['name', 'customer_name', 'segment', 'risk_grade', 'total_exposure', 'npl_flag', 'relationship_manager'] },
]

function buildQuery() {
  selectedColumns.value = queryTables.find(t => t.name === selectedTable.value)?.columns.slice(0, 4) || []
}

function runQuery() {
  queryRunning.value = true
  queryResults.value = []
  setTimeout(() => {
    queryRunning.value = false
    queryTime.value = Math.floor(Math.random() * 200) + 50
    queryResultCols.value = selectedColumns.value.length > 0 ? selectedColumns.value : ['name', 'status', 'owner', 'creation']
    queryResults.value = Array.from({ length: 12 }, (_, i) => {
      const row = {}
      queryResultCols.value.forEach(col => {
        if (col === 'name') row[col] = `CRM-${1000 + i}`
        else if (col.includes('name')) row[col] = ['PT Maju Jaya', 'Budi Santoso', 'CV Teknik', 'Ahmad Fuad', 'Sari Dewi'][i % 5]
        else if (col === 'status') row[col] = ['Active', 'Draft', 'Pending', 'Closed'][i % 4]
        else if (col.includes('amount') || col.includes('revenue') || col.includes('exposure')) row[col] = `Rp ${(Math.random() * 900 + 100).toFixed(0)}M`
        else if (col.includes('date') || col === 'creation') row[col] = `2026-0${(i % 5) + 1}-${String((i % 28) + 1).padStart(2, '0')}`
        else row[col] = `Value ${i + 1}`
      })
      return row
    })
    showToast(`Query returned ${queryResults.value.length} rows`)
  }, 800)
}

// ── Actions ──
function openReport(r) { showToast(`Opening ${r.name}...`) }
function downloadReport(r) { showToast(`Downloading ${r.name}...`) }
function shareReport(r) { showToast(`Share link copied for ${r.name}`) }
function doExport() { showToast('Export started — check your email when ready') }

// ── Toast ──
const toast = ref('')
let toastTimer = null
function showToast(msg) {
  toast.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = '' }, 2500)
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(8px); }
</style>
