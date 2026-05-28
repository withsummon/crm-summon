<template>
  <div class="flex flex-1 flex-col min-h-0 bg-gray-50 font-sans select-none">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-9 w-9 items-center justify-center rounded-[12px] bg-gradient-to-br from-[#FF6600] to-[#CC5200]"
          >
            <FeatherIcon name="shield" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-ink-gray-9">
              {{ __("Covenant Monitoring") }}
            </h1>
          </div>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex flex-1 min-h-0 overflow-hidden">
      <!-- ── Left Sidebar ── -->
      <div class="w-52 bg-white border-r border-gray-200 flex flex-col shrink-0">
        <div class="p-3 space-y-0.5">
          <button
            v-for="nav in navItems"
            :key="nav.id"
            @click="activeNav = nav.id"
            class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-all text-left"
            :class="
              activeNav === nav.id
                ? 'bg-[#FFF8F2] text-[#CC5200] font-semibold'
                : 'text-gray-600 hover:bg-gray-50'
            "
          >
            <FeatherIcon :name="nav.icon" class="h-3.5 w-3.5 shrink-0" />
            <span class="truncate">{{ nav.label }}</span>
            <span
              v-if="nav.badge"
              class="ml-auto text-[9px] rounded-full px-1.5 font-bold"
              :class="nav.badgeColor || 'bg-[#FFF0E6] text-[#CC5200]'"
              >{{ nav.badge }}</span
            >
          </button>
        </div>

        <!-- Quick Stats -->
        <div class="mt-2 border-t border-gray-100 p-3 space-y-2">
          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">
            {{ __("Portfolio Health") }}
          </p>
          <div
            v-for="s in quickStats"
            :key="s.label"
            class="flex items-center justify-between"
          >
            <div class="flex items-center gap-1.5">
              <div class="w-2 h-2 rounded-full" :class="s.dot" />
              <span class="text-[11px] text-gray-600">{{ s.label }}</span>
            </div>
            <span class="text-[11px] font-bold" :class="s.textColor">{{ s.value }}</span>
          </div>
          <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden flex mt-1">
            <div class="h-full bg-green-500 transition-all" :style="{ width: '62%' }" />
            <div class="h-full bg-amber-400 transition-all" :style="{ width: '24%' }" />
            <div class="h-full bg-red-500 transition-all" :style="{ width: '14%' }" />
          </div>
        </div>

        <div class="mt-auto p-3 border-t border-gray-100">
          <p class="text-[10px] text-gray-400">
            {{ __("Last tested") }}:
            <span class="font-semibold text-gray-600">24 May 08:00</span>
          </p>
        </div>
      </div>

      <!-- ── Main Content ── -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        <!-- DASHBOARD -->
        <div
          v-if="activeNav === 'dashboard'"
          class="flex-1 overflow-y-auto p-5 space-y-5"
        >
          <!-- Stat cards -->
          <div class="grid grid-cols-4 gap-4">
            <div
              v-for="stat in dashStats"
              :key="stat.label"
              class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm cursor-pointer hover:shadow-md transition-all"
              @click="activeNav = stat.nav"
            >
              <div class="flex items-start justify-between mb-3">
                <div
                  class="w-9 h-9 rounded-xl flex items-center justify-center"
                  :class="stat.iconBg"
                >
                  <FeatherIcon
                    :name="stat.icon"
                    class="h-4 w-4"
                    :class="stat.iconColor"
                  />
                </div>
                <span
                  class="text-[10px] font-bold rounded-full px-2 py-0.5"
                  :class="stat.badgeClass"
                  >{{ stat.badge }}</span
                >
              </div>
              <p class="text-2xl font-black text-gray-900 mb-0.5">{{ stat.value }}</p>
              <p class="text-[10px] font-semibold text-gray-500 uppercase tracking-wide">
                {{ stat.label }}
              </p>
            </div>
          </div>

          <!-- Charts row -->
          <div class="grid grid-cols-3 gap-4">
            <!-- Breach Trend -->
            <div
              class="col-span-2 bg-white rounded-xl border border-gray-200 p-4 shadow-sm"
            >
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="text-sm font-bold text-gray-800">
                    {{ __("Breach Trend") }}
                  </h3>
                  <p class="text-[10px] text-gray-400">
                    {{ __("Active breaches by month") }}
                  </p>
                </div>
                <div class="flex items-center gap-3 text-[10px]">
                  <span class="flex items-center gap-1"
                    ><span
                      class="w-2 h-2 rounded-full bg-red-500 inline-block"
                    />Breach</span
                  >
                  <span class="flex items-center gap-1"
                    ><span
                      class="w-2 h-2 rounded-full bg-amber-400 inline-block"
                    />Watch</span
                  >
                </div>
              </div>
              <svg class="w-full" viewBox="0 0 400 100" preserveAspectRatio="none">
                <line
                  v-for="i in 4"
                  :key="i"
                  x1="0"
                  :y1="(100 / 4) * i"
                  x2="400"
                  :y2="(100 / 4) * i"
                  stroke="#f3f4f6"
                  stroke-width="1"
                />
                <!-- Watch bars -->
                <rect
                  v-for="(v, i) in watchTrend"
                  :key="'w' + i"
                  :x="(400 / watchTrend.length) * i + 4"
                  :y="100 - (v / 16) * 100"
                  :width="400 / watchTrend.length - 10"
                  :height="(v / 16) * 100"
                  fill="#fbbf24"
                  rx="2"
                />
                <!-- Breach bars -->
                <rect
                  v-for="(v, i) in breachTrend"
                  :key="'b' + i"
                  :x="(400 / breachTrend.length) * i + 4"
                  :y="100 - (v / 16) * 100"
                  :width="400 / breachTrend.length - 10"
                  :height="(v / 16) * 100"
                  fill="#ef4444"
                  rx="2"
                  opacity="0.8"
                />
              </svg>
              <div class="flex justify-around mt-1">
                <span
                  v-for="m in trendMonths"
                  :key="m"
                  class="text-[9px] text-gray-400 flex-1 text-center"
                  >{{ m }}</span
                >
              </div>
            </div>

            <!-- Status Donut -->
            <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <h3 class="text-sm font-bold text-gray-800 mb-0.5">
                {{ __("Covenant Status") }}
              </h3>
              <p class="text-[10px] text-gray-400 mb-3">
                {{ __("All active covenants") }}
              </p>
              <div class="flex flex-col items-center">
                <svg viewBox="0 0 120 120" class="w-28 h-28">
                  <circle
                    cx="60"
                    cy="60"
                    r="42"
                    fill="none"
                    stroke="#f3f4f6"
                    stroke-width="18"
                  />
                  <circle
                    v-for="seg in statusDonut"
                    :key="seg.label"
                    cx="60"
                    cy="60"
                    r="42"
                    fill="none"
                    :stroke="seg.color"
                    stroke-width="18"
                    :stroke-dasharray="`${seg.dash} ${donutC}`"
                    :stroke-dashoffset="seg.offset"
                  />
                  <text
                    x="60"
                    y="56"
                    text-anchor="middle"
                    fill="#1f2937"
                    font-size="11"
                    font-weight="700"
                  >
                    {{ totalCovenants }}
                  </text>
                  <text x="60" y="68" text-anchor="middle" fill="#9ca3af" font-size="7">
                    Covenants
                  </text>
                </svg>
                <div class="w-full space-y-1 mt-1">
                  <div
                    v-for="s in statusBreakdown"
                    :key="s.label"
                    class="flex items-center justify-between"
                  >
                    <div class="flex items-center gap-1.5">
                      <div
                        class="w-2 h-2 rounded-full"
                        :style="{ background: s.color }"
                      />
                      <span class="text-[10px] text-gray-600">{{ s.label }}</span>
                    </div>
                    <span class="text-[10px] font-bold" :class="s.textClass">{{
                      s.count
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom row -->
          <div class="grid grid-cols-2 gap-4">
            <!-- Active Breaches -->
            <div
              class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
            >
              <div
                class="px-4 py-3 border-b border-gray-100 flex items-center justify-between"
              >
                <h3 class="text-sm font-bold text-gray-800">
                  {{ __("Active Breaches") }}
                </h3>
                <button
                  @click="activeNav = 'breach'"
                  class="text-[10px] text-[#FF6600] hover:underline"
                >
                  {{ __("View all") }}
                </button>
              </div>
              <div class="divide-y divide-gray-50">
                <div
                  v-for="b in activeBreaches.slice(0, 4)"
                  :key="b.id"
                  class="px-4 py-3 hover:bg-gray-50 transition-colors cursor-pointer"
                  @click="activeNav = 'breach'"
                >
                  <div class="flex items-start justify-between gap-2">
                    <div class="min-w-0">
                      <p class="text-xs font-semibold text-gray-800 truncate">
                        {{ b.covenant }}
                      </p>
                      <p class="text-[10px] text-gray-400 truncate">{{ b.facility }}</p>
                    </div>
                    <span
                      class="shrink-0 rounded-full px-2 py-0.5 text-[9px] font-bold"
                      :class="
                        b.severity === 'Critical'
                          ? 'bg-red-100 text-red-700'
                          : b.severity === 'High'
                          ? 'bg-orange-100 text-orange-700'
                          : 'bg-amber-100 text-amber-700'
                      "
                    >
                      {{ b.severity }}
                    </span>
                  </div>
                  <div class="flex items-center gap-3 mt-1.5 text-[10px] text-gray-500">
                    <span
                      >Actual:
                      <span class="font-semibold text-red-600">{{ b.actual }}</span></span
                    >
                    <span
                      >Threshold:
                      <span class="font-semibold">{{ b.threshold }}</span></span
                    >
                    <span class="ml-auto text-[9px] text-gray-400">{{ b.since }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Upcoming Tests -->
            <div
              class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
            >
              <div
                class="px-4 py-3 border-b border-gray-100 flex items-center justify-between"
              >
                <h3 class="text-sm font-bold text-gray-800">
                  {{ __("Upcoming Tests") }}
                </h3>
                <button
                  @click="activeNav = 'calendar'"
                  class="text-[10px] text-[#FF6600] hover:underline"
                >
                  {{ __("Calendar") }}
                </button>
              </div>
              <div class="divide-y divide-gray-50">
                <div
                  v-for="t in upcomingTests.slice(0, 5)"
                  :key="t.id"
                  class="px-4 py-2.5 flex items-center gap-3"
                >
                  <div
                    class="w-9 h-9 rounded-lg flex flex-col items-center justify-center shrink-0"
                    :class="
                      t.urgent
                        ? 'bg-red-50 border border-red-200'
                        : 'bg-gray-50 border border-gray-200'
                    "
                  >
                    <p
                      class="text-[9px] font-semibold"
                      :class="t.urgent ? 'text-red-500' : 'text-gray-500'"
                    >
                      {{ t.month }}
                    </p>
                    <p
                      class="text-sm font-black"
                      :class="t.urgent ? 'text-red-600' : 'text-gray-700'"
                    >
                      {{ t.day }}
                    </p>
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="text-[11px] font-semibold text-gray-800 truncate">
                      {{ t.covenant }}
                    </p>
                    <p class="text-[10px] text-gray-400 truncate">{{ t.facility }}</p>
                  </div>
                  <span
                    class="text-[10px] rounded-full px-2 py-0.5 font-semibold shrink-0"
                    :class="
                      t.freq === 'Monthly'
                        ? 'bg-[#FFF0E6] text-[#CC5200]'
                        : t.freq === 'Quarterly'
                        ? 'bg-[#E6F4FA] text-[#004D73]'
                        : 'bg-gray-100 text-gray-600'
                    "
                  >
                    {{ t.freq }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Risk Predictor -->
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div class="flex items-center gap-2 mb-3">
              <div
                class="w-7 h-7 rounded-lg bg-purple-100 flex items-center justify-center"
              >
                <FeatherIcon name="zap" class="h-3.5 w-3.5 text-purple-600" />
              </div>
              <h3 class="text-sm font-bold text-gray-800">
                {{ __("AI Covenant Risk Predictor") }}
              </h3>
              <span
                class="text-[9px] bg-purple-100 text-purple-700 rounded-full px-2 py-0.5 font-bold"
                >BETA</span
              >
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div
                v-for="pred in aiPredictions"
                :key="pred.id"
                class="rounded-xl border p-3 cursor-pointer hover:shadow-sm transition-all"
                :class="
                  pred.risk === 'High'
                    ? 'border-red-200 bg-red-50'
                    : pred.risk === 'Medium'
                    ? 'border-amber-200 bg-amber-50'
                    : 'border-green-200 bg-green-50'
                "
              >
                <div class="flex items-start justify-between mb-2">
                  <p class="text-[11px] font-semibold text-gray-800">
                    {{ pred.facility }}
                  </p>
                  <span
                    class="text-[9px] font-bold rounded-full px-1.5 py-0.5"
                    :class="
                      pred.risk === 'High'
                        ? 'bg-red-100 text-red-700'
                        : pred.risk === 'Medium'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-green-100 text-green-700'
                    "
                  >
                    {{ pred.risk }}
                  </span>
                </div>
                <p class="text-[10px] text-gray-600 mb-2">
                  {{ pred.covenant }} — {{ pred.msg }}
                </p>
                <div class="flex items-center gap-1.5">
                  <div class="flex-1 h-1.5 bg-white rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full"
                      :class="
                        pred.risk === 'High'
                          ? 'bg-red-400'
                          : pred.risk === 'Medium'
                          ? 'bg-amber-400'
                          : 'bg-green-400'
                      "
                      :style="{ width: pred.confidence + '%' }"
                    />
                  </div>
                  <span class="text-[9px] font-bold text-gray-500"
                    >{{ pred.confidence }}%</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- COVENANT LIBRARY -->
        <div
          v-else-if="activeNav === 'library'"
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div
            class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3"
          >
            <div class="relative flex-1 max-w-sm">
              <FeatherIcon
                name="search"
                class="absolute left-3 top-2.5 h-3.5 w-3.5 text-gray-400"
              />
              <input
                v-model="libSearch"
                type="text"
                :placeholder="__('Search covenants...')"
                class="w-full pl-9 pr-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#FF6600]"
              />
            </div>
            <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
              <button
                v-for="t in ['All', 'Financial', 'Non-Financial', 'Reporting']"
                :key="t"
                @click="libFilter = t"
                class="px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all"
                :class="
                  libFilter === t ? 'bg-white text-[#CC5200] shadow-sm' : 'text-gray-500'
                "
              >
                {{ t }}
              </button>
            </div>
            <button
              @click="openAddCovenant"
              class="ml-auto flex items-center gap-1.5 rounded-lg bg-[#FF6600] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#CC5200] transition-colors"
            >
              <FeatherIcon name="plus" class="h-3.5 w-3.5" />{{ __("Add Covenant") }}
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <div
              class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
            >
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-gray-100 bg-gray-50">
                    <th class="px-5 py-3 text-left font-semibold text-gray-500">
                      {{ __("Covenant Name") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Type") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Metric") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Frequency") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Facilities") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Tags") }}
                    </th>
                    <th class="px-4 py-3 text-right font-semibold text-gray-500">
                      {{ __("Actions") }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="cov in filteredLibrary"
                    :key="cov.id"
                    class="border-b border-gray-50 hover:bg-gray-50 transition-colors cursor-pointer"
                    @click="selectedCovenant = cov"
                  >
                    <td class="px-5 py-3">
                      <div class="flex items-center gap-2.5">
                        <div
                          class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                          :class="
                            cov.type === 'Financial'
                              ? 'bg-[#FFF0E6]'
                              : cov.type === 'Non-Financial'
                              ? 'bg-purple-100'
                              : 'bg-[#E6F4FA]'
                          "
                        >
                          <FeatherIcon
                            :name="cov.icon"
                            class="h-3.5 w-3.5"
                            :class="
                              cov.type === 'Financial'
                                ? 'text-[#FF6600]'
                                : cov.type === 'Non-Financial'
                                ? 'text-purple-600'
                                : 'text-[#006699]'
                            "
                          />
                        </div>
                        <div>
                          <p class="font-semibold text-gray-800">{{ cov.name }}</p>
                          <p class="text-[10px] text-gray-400">
                            {{ cov.template ? "Standard" : "Custom" }}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <span
                        class="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                        :class="
                          cov.type === 'Financial'
                            ? 'bg-[#FFF0E6] text-[#CC5200]'
                            : cov.type === 'Non-Financial'
                            ? 'bg-purple-100 text-purple-700'
                            : 'bg-[#E6F4FA] text-[#004D73]'
                        "
                      >
                        {{ cov.type }}
                      </span>
                    </td>
                    <td class="px-4 py-3 font-mono text-gray-700 text-[11px]">
                      {{ cov.metric }}
                    </td>
                    <td class="px-4 py-3 text-gray-500">{{ cov.frequency }}</td>
                    <td class="px-4 py-3 font-semibold text-gray-700">
                      {{ cov.facilities }}
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex flex-wrap gap-1">
                        <span
                          v-for="tag in cov.tags"
                          :key="tag"
                          class="text-[9px] bg-gray-100 text-gray-600 rounded px-1.5 py-0.5"
                          >{{ tag }}</span
                        >
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex items-center justify-end gap-1">
                        <button
                          @click.stop="openEditCovenant(cov)"
                          class="p-1.5 rounded hover:bg-[#FFF8F2] text-gray-400 hover:text-[#FF6600]"
                        >
                          <FeatherIcon name="edit-2" class="h-3 w-3" />
                        </button>
                        <button @click.stop="duplicateCovenant(cov)" class="p-1.5 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600">
                          <FeatherIcon name="copy" class="h-3 w-3" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- TEST ENGINE -->
        <div
          v-else-if="activeNav === 'tests'"
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div
            class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3"
          >
            <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
              <button
                v-for="p in ['Latest', 'This Month', 'Last Quarter']"
                :key="p"
                @click="testPeriod = p"
                class="px-3 py-1.5 rounded-md text-xs font-semibold transition-all"
                :class="
                  testPeriod === p ? 'bg-white text-[#CC5200] shadow-sm' : 'text-gray-500'
                "
              >
                {{ p }}
              </button>
            </div>
            <span class="text-xs text-gray-400">{{ testResults.length }} tests</span>
            <button
              @click="runAllTests"
              class="ml-auto flex items-center gap-1.5 rounded-lg bg-[#FF6600] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#CC5200] transition-colors"
            >
              <FeatherIcon
                :name="testing ? 'loader' : 'play'"
                class="h-3.5 w-3.5"
                :class="testing && 'animate-spin'"
              />
              {{ testing ? __("Running...") : __("Run All Tests") }}
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <div
              class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
            >
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-gray-100 bg-gray-50">
                    <th class="px-5 py-3 text-left font-semibold text-gray-500">
                      {{ __("Covenant") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Facility") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Test Date") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Actual") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Threshold") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Headroom") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Status") }}
                    </th>
                    <th class="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="r in testResults"
                    :key="r.id"
                    class="border-b border-gray-50 hover:bg-gray-50 transition-colors"
                  >
                    <td class="px-5 py-3 font-semibold text-gray-800">
                      {{ r.covenant }}
                    </td>
                    <td class="px-4 py-3 text-gray-500">{{ r.facility }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ r.testDate }}</td>
                    <td
                      class="px-4 py-3 font-black"
                      :class="
                        r.status === 'Breach'
                          ? 'text-red-600'
                          : r.status === 'Watch'
                          ? 'text-amber-600'
                          : 'text-gray-900'
                      "
                    >
                      {{ r.actual }}
                    </td>
                    <td class="px-4 py-3 text-gray-600">{{ r.threshold }}</td>
                    <td class="px-4 py-3">
                      <div class="flex items-center gap-2">
                        <div class="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            class="h-full rounded-full"
                            :class="
                              r.headroomPct < 10
                                ? 'bg-red-400'
                                : r.headroomPct < 25
                                ? 'bg-amber-400'
                                : 'bg-green-500'
                            "
                            :style="{ width: Math.min(r.headroomPct, 100) + '%' }"
                          />
                        </div>
                        <span
                          class="text-[10px] font-semibold"
                          :class="
                            r.headroomPct < 10
                              ? 'text-red-500'
                              : r.headroomPct < 25
                              ? 'text-amber-600'
                              : 'text-green-600'
                          "
                          >{{ r.headroom }}</span
                        >
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <span
                        class="rounded-full px-2 py-0.5 text-[9px] font-bold"
                        :class="
                          r.status === 'Pass'
                            ? 'bg-green-100 text-green-700'
                            : r.status === 'Watch'
                            ? 'bg-amber-100 text-amber-700'
                            : r.status === 'Breach'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-600'
                        "
                      >
                        {{ r.status }}
                      </span>
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex items-center gap-1.5">
                        <button
                          v-if="r.status === 'Breach'"
                          @click="activeNav = 'cure'; showToast('Cure task created for ' + r.covenant)"
                          class="text-[10px] bg-red-600 text-white rounded-lg px-2.5 py-1 font-semibold hover:bg-red-700 transition-colors"
                        >{{ __("Cure") }}</button>
                        <button
                          @click.stop="openAttachDoc({ context: 'test', ref: r.covenant + ' — ' + r.facility })"
                          class="flex items-center gap-1 text-[10px] border border-[#006699] text-[#006699] rounded-lg px-2 py-1 hover:bg-[#E6F4FA] transition-colors font-semibold"
                          :title="__('Attach document')"
                        ><FeatherIcon name="paperclip" class="h-3 w-3" />{{ r.attachCount || 0 }}</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- COVENANT CALENDAR -->
        <div v-else-if="activeNav === 'calendar'" class="flex-1 overflow-y-auto p-5">
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-bold text-gray-800">{{ __("June 2026") }}</h3>
              <div class="flex items-center gap-2">
                <button class="p-1.5 rounded hover:bg-gray-100 text-gray-500">
                  <FeatherIcon name="chevron-left" class="h-4 w-4" />
                </button>
                <button class="p-1.5 rounded hover:bg-gray-100 text-gray-500">
                  <FeatherIcon name="chevron-right" class="h-4 w-4" />
                </button>
              </div>
            </div>
            <!-- Calendar grid -->
            <div class="grid grid-cols-7 gap-1 mb-2">
              <div
                v-for="d in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']"
                :key="d"
                class="text-center text-[10px] font-semibold text-gray-400 py-1"
              >
                {{ d }}
              </div>
            </div>
            <div class="grid grid-cols-7 gap-1">
              <div
                v-for="cell in calendarCells"
                :key="cell.key"
                class="min-h-[72px] rounded-lg border p-1.5 transition-colors"
                :class="
                  cell.day
                    ? cell.today
                      ? 'border-[#FF8533] bg-[#FFF8F2]'
                      : 'border-gray-100 hover:bg-gray-50'
                    : 'border-transparent'
                "
              >
                <p
                  v-if="cell.day"
                  class="text-[11px] font-semibold mb-1"
                  :class="cell.today ? 'text-[#CC5200]' : 'text-gray-700'"
                >
                  {{ cell.day }}
                </p>
                <div class="space-y-0.5">
                  <div
                    v-for="ev in cell.events"
                    :key="ev.id"
                    class="text-[9px] rounded px-1 py-0.5 truncate font-semibold cursor-pointer"
                    :class="
                      ev.status === 'Breach'
                        ? 'bg-red-100 text-red-700'
                        : ev.status === 'Watch'
                        ? 'bg-amber-100 text-amber-700'
                        : ev.status === 'Due'
                        ? 'bg-[#E6F4FA] text-[#004D73]'
                        : 'bg-green-100 text-green-700'
                    "
                    @click="showToast(ev.name + ' — ' + ev.status)"
                  >
                    {{ ev.name }}
                  </div>
                </div>
              </div>
            </div>
            <!-- Legend -->
            <div class="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100">
              <div
                v-for="l in calLegend"
                :key="l.label"
                class="flex items-center gap-1.5"
              >
                <div class="w-3 h-3 rounded" :class="l.color" />
                <span class="text-[10px] text-gray-500">{{ l.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- BREACH & ALERTS -->
        <div
          v-else-if="activeNav === 'breach'"
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div
            class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3"
          >
            <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
              <button
                v-for="s in ['All', 'Critical', 'High', 'Medium']"
                :key="s"
                @click="breachFilter = s"
                class="px-3 py-1.5 rounded-md text-xs font-semibold transition-all"
                :class="
                  breachFilter === s
                    ? 'bg-white text-[#CC5200] shadow-sm'
                    : 'text-gray-500'
                "
              >
                {{ s }}
              </button>
            </div>
            <span class="text-xs text-red-500 font-semibold"
              >{{ activeBreaches.length }} active breaches</span
            >
          </div>
          <div class="flex-1 overflow-y-auto p-5 space-y-3">
            <div
              v-for="b in filteredBreaches"
              :key="b.id"
              class="bg-white rounded-xl border shadow-sm p-4 hover:shadow-md transition-all"
              :class="
                b.severity === 'Critical'
                  ? 'border-red-300'
                  : b.severity === 'High'
                  ? 'border-orange-200'
                  : 'border-amber-200'
              "
            >
              <div class="flex items-start justify-between gap-3 mb-3">
                <div>
                  <div class="flex items-center gap-2 mb-1">
                    <span
                      class="rounded-full px-2 py-0.5 text-[9px] font-bold"
                      :class="
                        b.severity === 'Critical'
                          ? 'bg-red-100 text-red-700'
                          : b.severity === 'High'
                          ? 'bg-orange-100 text-orange-700'
                          : 'bg-amber-100 text-amber-700'
                      "
                    >
                      {{ b.severity }}
                    </span>
                    <span class="text-[10px] text-gray-400">Since {{ b.since }}</span>
                  </div>
                  <h4 class="text-sm font-bold text-gray-800">{{ b.covenant }}</h4>
                  <p class="text-xs text-gray-500">{{ b.facility }}</p>
                </div>
                <div class="text-right shrink-0">
                  <p class="text-[10px] text-gray-400">Actual vs Threshold</p>
                  <p class="text-sm font-black text-red-600">
                    {{ b.actual }} <span class="text-gray-300 font-normal">/</span>
                    <span class="text-gray-700 font-semibold">{{ b.threshold }}</span>
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click="activeNav = 'cure'; showToast('Cure task created')"
                  class="flex items-center gap-1.5 rounded-lg bg-[#FF6600] text-white px-3 py-1.5 text-xs font-semibold hover:bg-[#CC5200] transition-colors"
                >
                  <FeatherIcon name="check-square" class="h-3 w-3" />{{ __("Create Cure Task") }}
                </button>
                <button
                  @click="activeNav = 'waiver'; showToast('Waiver request initiated')"
                  class="flex items-center gap-1.5 rounded-lg border border-[#006699] text-[#006699] px-3 py-1.5 text-xs font-semibold hover:bg-[#E6F4FA] transition-colors"
                >
                  <FeatherIcon name="file-minus" class="h-3 w-3" />{{ __("Request Waiver") }}
                </button>
                <button
                  @click="openAttachDoc({ context: 'breach', ref: b.covenant + ' — ' + b.facility })"
                  class="flex items-center gap-1.5 rounded-lg border border-[#006699] text-[#006699] px-3 py-1.5 text-xs font-semibold hover:bg-[#E6F4FA] transition-colors"
                >
                  <FeatherIcon name="paperclip" class="h-3 w-3" />{{ __("Attach Doc") }}
                </button>
                <button class="flex items-center gap-1.5 rounded-lg border border-gray-200 text-gray-500 px-3 py-1.5 text-xs font-semibold hover:bg-gray-50 transition-colors" @click="showToast('Notification sent')">
                  <FeatherIcon name="bell" class="h-3 w-3" />{{ __("Notify") }}
                </button>
                <span class="ml-auto text-[10px] text-gray-400">RM: {{ b.rm }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- CURE WORKFLOW -->
        <div
          v-else-if="activeNav === 'cure'"
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div
            class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3"
          >
            <h3 class="text-sm font-semibold text-gray-800">{{ __("Cure Workflow") }}</h3>
            <span class="text-[11px] text-gray-400"
              >{{ cureTasks.length }} {{ __("active tasks") }}</span
            >
            <button
              @click="openAddTask"
              class="ml-auto flex items-center gap-1.5 rounded-lg bg-[#FF6600] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#CC5200] transition-colors"
            >
              <FeatherIcon name="plus" class="h-3.5 w-3.5" />{{ __("Add Task") }}
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <div class="grid grid-cols-3 gap-4">
              <div v-for="col in cureColumns" :key="col.id" class="space-y-3">
                <div class="flex items-center gap-2 px-1">
                  <div class="w-2 h-2 rounded-full" :class="col.dot" />
                  <p class="text-xs font-bold text-gray-700">{{ col.label }}</p>
                  <span class="ml-auto text-[10px] text-gray-400">{{
                    cureTasks.filter((t) => t.status === col.id).length
                  }}</span>
                </div>
                <div class="space-y-2">
                  <div
                    v-for="task in cureTasks.filter((t) => t.status === col.id)"
                    :key="task.id"
                    class="bg-white rounded-xl border border-gray-200 p-3 shadow-sm hover:shadow-md transition-all cursor-pointer"
                  >
                    <div class="flex items-start justify-between gap-2 mb-2">
                      <p class="text-xs font-semibold text-gray-800 leading-tight">
                        {{ task.title }}
                      </p>
                      <span
                        class="shrink-0 text-[9px] rounded-full px-1.5 py-0.5 font-bold"
                        :class="
                          task.priority === 'Critical'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-amber-100 text-amber-700'
                        "
                      >
                        {{ task.priority }}
                      </span>
                    </div>
                    <p class="text-[10px] text-gray-400 mb-2">{{ task.facility }}</p>
                    <div class="flex items-center gap-2 text-[10px] text-gray-400">
                      <FeatherIcon name="calendar" class="h-3 w-3" />
                      <span :class="task.overdue ? 'text-red-500 font-semibold' : ''">{{
                        task.deadline
                      }}</span>
                      <span class="ml-auto">{{ task.owner }}</span>
                    </div>
                    <div v-if="task.progress !== undefined" class="mt-2">
                      <div class="h-1 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          class="h-full bg-[#FF6600] rounded-full"
                          :style="{ width: task.progress + '%' }"
                        />
                      </div>
                    </div>
                    <div class="flex items-center gap-1 mt-2">
                      <button
                        v-if="task.status !== 'Done'"
                        @click="advanceCure(task)"
                        class="text-[10px] text-[#FF6600] hover:underline font-semibold"
                      >
                        {{ task.status === "Open" ? "Start →" : "Mark Done →" }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- WAIVER MANAGEMENT -->
        <div
          v-else-if="activeNav === 'waiver'"
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div
            class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3"
          >
            <h3 class="text-sm font-semibold text-gray-800">
              {{ __("Waiver Management") }}
            </h3>
            <span class="text-[11px] text-gray-400"
              >{{ waivers.length }} {{ __("waivers") }}</span
            >
            <button
              @click="openAddWaiver"
              class="ml-auto flex items-center gap-1.5 rounded-lg bg-[#FF6600] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#CC5200] transition-colors"
            >
              <FeatherIcon name="plus" class="h-3.5 w-3.5" />{{ __("New Waiver") }}
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <div
              class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
            >
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-gray-100 bg-gray-50">
                    <th class="px-5 py-3 text-left font-semibold text-gray-500">
                      {{ __("Waiver") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Facility") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Requested") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Expiry") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Approver") }}
                    </th>
                    <th class="px-4 py-3 text-left font-semibold text-gray-500">
                      {{ __("Status") }}
                    </th>
                    <th class="px-4 py-3 text-right font-semibold text-gray-500">
                      {{ __("Actions") }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="w in waivers"
                    :key="w.id"
                    class="border-b border-gray-50 hover:bg-gray-50 transition-colors"
                  >
                    <td class="px-5 py-3">
                      <p class="font-semibold text-gray-800">{{ w.covenant }}</p>
                      <p class="text-[10px] text-gray-400">{{ w.reason }}</p>
                    </td>
                    <td class="px-4 py-3 text-gray-500">{{ w.facility }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ w.requested }}</td>
                    <td
                      class="px-4 py-3"
                      :class="
                        w.expiring ? 'text-amber-600 font-semibold' : 'text-gray-500'
                      "
                    >
                      {{ w.expiry }}
                    </td>
                    <td class="px-4 py-3 text-gray-500">{{ w.approver }}</td>
                    <td class="px-4 py-3">
                      <span
                        class="rounded-full px-2 py-0.5 text-[9px] font-bold"
                        :class="
                          w.status === 'Approved'
                            ? 'bg-green-100 text-green-700'
                            : w.status === 'Pending'
                            ? 'bg-amber-100 text-amber-700'
                            : w.status === 'Expired'
                            ? 'bg-gray-100 text-gray-500'
                            : 'bg-red-100 text-red-700'
                        "
                      >
                        {{ w.status }}
                      </span>
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex items-center justify-end gap-1.5">
                        <button
                          class="p-1.5 rounded hover:bg-[#FFF8F2] text-gray-400 hover:text-[#FF6600]"
                        >
                          <FeatherIcon name="file-text" class="h-3 w-3" />
                        </button>
                        <button
                          v-if="w.status === 'Pending'"
                          @click="approveWaiver(w)"
                          class="px-2.5 py-1 bg-[#FF6600] text-white rounded-lg text-[10px] font-semibold hover:bg-[#CC5200] transition-colors"
                        >
                          Approve
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- COVENANT REPORTS -->
        <div v-else-if="activeNav === 'reports'" class="flex-1 overflow-y-auto p-5">
          <div class="grid grid-cols-2 gap-4">
            <div
              v-for="rep in covReports"
              :key="rep.id"
              class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-all cursor-pointer group"
              @click="showToast('Opening ' + rep.name)"
            >
              <div class="flex items-start justify-between mb-3">
                <div
                  class="w-9 h-9 rounded-xl flex items-center justify-center"
                  :class="rep.colorBg"
                >
                  <FeatherIcon :name="rep.icon" class="h-4 w-4" :class="rep.colorText" />
                </div>
                <span
                  class="text-[9px] rounded-full px-2 py-0.5 font-bold"
                  :class="rep.statusClass"
                  >{{ rep.status }}</span
                >
              </div>
              <h3 class="text-sm font-bold text-gray-800 mb-1">{{ rep.name }}</h3>
              <p class="text-xs text-gray-400 mb-3">{{ rep.desc }}</p>
              <div
                class="flex items-center justify-between pt-2 border-t border-gray-100"
              >
                <span class="text-[10px] text-gray-400">{{ rep.period }}</span>
                <div
                  class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <button
                    @click.stop="showToast('Downloading ' + rep.name)"
                    class="text-[10px] text-[#FF6600] font-semibold hover:underline"
                  >
                    PDF
                  </button>
                  <button
                    @click.stop="showToast('Exporting ' + rep.name)"
                    class="text-[10px] text-[#006699] font-semibold hover:underline"
                  >
                    Excel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- SENSITIVITY ANALYSIS -->
        <div
          v-else-if="activeNav === 'sensitivity'"
          class="flex-1 overflow-y-auto p-5 space-y-4"
        >
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <h3 class="text-sm font-bold text-gray-800 mb-1">
              {{ __("Breach Headroom Heatmap") }}
            </h3>
            <p class="text-[10px] text-gray-400 mb-4">
              {{
                __(
                  "Headroom to threshold breach (%) — Red = at risk, Green = comfortable"
                )
              }}
            </p>
            <div class="overflow-x-auto">
              <table class="text-xs w-full">
                <thead>
                  <tr class="border-b border-gray-100">
                    <th
                      class="px-3 py-2 text-left font-semibold text-gray-500 min-w-[160px]"
                    >
                      {{ __("Facility") }}
                    </th>
                    <th
                      v-for="cov in heatmapCovs"
                      :key="cov"
                      class="px-3 py-2 text-center font-semibold text-gray-500 min-w-[90px]"
                    >
                      {{ cov }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in heatmapData"
                    :key="row.facility"
                    class="border-b border-gray-50"
                  >
                    <td class="px-3 py-2.5 font-semibold text-gray-800">
                      {{ row.facility }}
                    </td>
                    <td
                      v-for="cov in heatmapCovs"
                      :key="cov"
                      class="px-3 py-2.5 text-center"
                    >
                      <div
                        class="inline-flex items-center justify-center w-14 h-8 rounded-lg text-[10px] font-bold"
                        :class="heatmapColor(row[cov])"
                      >
                        {{ row[cov] !== null ? row[cov] + "%" : "-" }}
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100">
              <span class="text-[10px] font-semibold text-gray-500">{{
                __("Legend:")
              }}</span>
              <div
                v-for="l in heatLegend"
                :key="l.label"
                class="flex items-center gap-1.5"
              >
                <div class="w-8 h-4 rounded" :class="l.color" />
                <span class="text-[10px] text-gray-500">{{ l.label }}</span>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
            <h3 class="text-sm font-bold text-gray-800 mb-3">
              {{ __("Scenario Simulation") }}
            </h3>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="text-[10px] font-semibold text-gray-500 mb-1.5 block">{{
                  __("Simulate Revenue Drop")
                }}</label>
                <input
                  type="range"
                  v-model="simRevDrop"
                  min="0"
                  max="50"
                  class="w-full accent-[#FF6600]"
                />
                <p class="text-[10px] text-gray-500 mt-1">-{{ simRevDrop }}% revenue</p>
              </div>
              <div>
                <label class="text-[10px] font-semibold text-gray-500 mb-1.5 block">{{
                  __("Debt Service Increase")
                }}</label>
                <input
                  type="range"
                  v-model="simDebtInc"
                  min="0"
                  max="50"
                  class="w-full accent-[#FF6600]"
                />
                <p class="text-[10px] text-gray-500 mt-1">
                  +{{ simDebtInc }}% debt service
                </p>
              </div>
              <div class="flex items-end">
                <button
                  @click="runSim"
                  class="w-full flex items-center justify-center gap-1.5 rounded-lg bg-[#FF6600] px-3 py-2 text-xs font-semibold text-white hover:bg-[#CC5200] transition-colors"
                >
                  <FeatherIcon name="play" class="h-3.5 w-3.5" />{{ __("Simulate") }}
                </button>
              </div>
            </div>
            <div
              v-if="simResult"
              class="mt-3 p-3 rounded-lg"
              :class="
                simResult.breaches > 0
                  ? 'bg-red-50 border border-red-200'
                  : 'bg-green-50 border border-green-200'
              "
            >
              <p
                class="text-xs font-semibold"
                :class="simResult.breaches > 0 ? 'text-red-700' : 'text-green-700'"
              >
                {{
                  simResult.breaches > 0
                    ? `⚠ ${simResult.breaches} covenants would breach under this scenario`
                    : "✓ No additional breaches under this scenario"
                }}
              </p>
              <p class="text-[10px] text-gray-500 mt-0.5">{{ simResult.detail }}</p>
            </div>
          </div>
        </div>

        <!-- BORROWER SUBMISSION -->
        <div v-else-if="activeNav === 'borrower'" class="flex-1 flex flex-col overflow-hidden">
          <div class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3">
            <h3 class="text-sm font-semibold text-gray-800">{{ __("Borrower Covenant Submission") }}</h3>
            <span class="text-[11px] text-gray-400">{{ borrowerSubmissions.length }} submissions</span>
          </div>
          <div class="flex-1 overflow-y-auto p-5 space-y-5">
            <!-- Submission Form -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-8 h-8 rounded-lg bg-[#FFF0E6] flex items-center justify-center">
                  <FeatherIcon name="upload-cloud" class="h-4 w-4 text-[#FF6600]" />
                </div>
                <h4 class="text-sm font-bold text-gray-800">{{ __("Submit Financial Ratios") }}</h4>
              </div>
              <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1">Borrower / Facility <span class="text-red-400">*</span></label>
                  <select v-model="submissionForm.facility" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]">
                    <option value="">Select facility…</option>
                    <option>PT Maju Bersama — Working Capital Rp 5B</option>
                    <option>CV Teknik Jaya — Investment Loan Rp 2.5B</option>
                    <option>Budi Santoso — KPR Rp 800M</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1">Covenant <span class="text-red-400">*</span></label>
                  <select v-model="submissionForm.covenant" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]">
                    <option value="">Select covenant…</option>
                    <option v-for="c in covenantLibrary" :key="c.id" :value="c.name">{{ c.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1">Reporting Period <span class="text-red-400">*</span></label>
                  <input v-model="submissionForm.period" type="text" placeholder="e.g. Q1 2026 / May 2026" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1">Actual Value <span class="text-red-400">*</span></label>
                  <input v-model="submissionForm.value" type="text" placeholder="e.g. 1.35x / 2.8x / Rp 2.5B" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
                </div>
              </div>
              <div class="mb-4">
                <label class="block text-xs font-semibold text-gray-600 mb-1">Supporting Notes</label>
                <input v-model="submissionForm.notes" type="text" placeholder="e.g. Based on audited financial statements Q1 2026" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
              </div>
              <div class="mb-5">
                <label class="block text-xs font-semibold text-gray-600 mb-2">Upload Evidence</label>
                <div class="border-2 border-dashed border-gray-300 rounded-xl p-5 flex flex-col items-center justify-center text-center hover:border-[#FF8533] transition-colors cursor-pointer" @click="showToast('File picker opened')">
                  <FeatherIcon name="upload" class="h-6 w-6 text-gray-300 mb-2" />
                  <p class="text-xs text-gray-500 font-medium">Drop files here or <span class="text-[#FF6600]">browse</span></p>
                  <p class="text-[10px] text-gray-400 mt-0.5">Financial statements, audit reports, insurance certificates</p>
                </div>
              </div>
              <button @click="submitBorrowerForm" :disabled="!submissionForm.facility || !submissionForm.covenant || !submissionForm.value"
                class="flex items-center gap-1.5 rounded-lg bg-[#FF6600] px-4 py-2 text-sm font-semibold text-white hover:bg-[#CC5200] disabled:opacity-40 transition-colors">
                <FeatherIcon name="send" class="h-3.5 w-3.5" />{{ __("Submit for Review") }}
              </button>
            </div>

            <!-- Submission History -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
                <h4 class="text-xs font-bold text-gray-700">{{ __("Submission History") }}</h4>
                <span class="text-[11px] text-gray-400">{{ borrowerSubmissions.length }} records</span>
              </div>
              <table class="w-full text-xs">
                <thead><tr class="border-b border-gray-100 bg-gray-50">
                  <th class="px-5 py-2.5 text-left font-semibold text-gray-500">Submitted</th>
                  <th class="px-4 py-2.5 text-left font-semibold text-gray-500">Facility</th>
                  <th class="px-4 py-2.5 text-left font-semibold text-gray-500">Covenant</th>
                  <th class="px-4 py-2.5 text-left font-semibold text-gray-500">Period</th>
                  <th class="px-4 py-2.5 text-left font-semibold text-gray-500">Value</th>
                  <th class="px-4 py-2.5 text-left font-semibold text-gray-500">Status</th>
                </tr></thead>
                <tbody>
                  <tr v-for="s in borrowerSubmissions" :key="s.id" class="border-b border-gray-50 hover:bg-gray-50">
                    <td class="px-5 py-3 text-gray-500 font-mono text-[11px]">{{ s.submitted }}</td>
                    <td class="px-4 py-3 text-gray-700 font-medium">{{ s.facility }}</td>
                    <td class="px-4 py-3 text-gray-700">{{ s.covenant }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ s.period }}</td>
                    <td class="px-4 py-3 font-semibold text-gray-900">{{ s.value }}</td>
                    <td class="px-4 py-3">
                      <span class="rounded-full px-2 py-0.5 text-[9px] font-bold" :class="s.status==='Reviewed' ? 'bg-green-100 text-green-700' : s.status==='Rejected' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'">{{ s.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- CHANGE LOG -->
        <div v-else-if="activeNav === 'changelog'" class="flex-1 flex flex-col overflow-hidden">
          <div class="bg-white border-b border-gray-200 px-5 py-3 shrink-0 flex items-center gap-3">
            <h3 class="text-sm font-semibold text-gray-800">{{ __("Covenant Change Log") }}</h3>
            <span class="text-[11px] text-gray-400">{{ covenantChangelog.length }} events</span>
            <button @click="showToast('Exported')" class="ml-auto flex items-center gap-1.5 text-xs text-[#006699] hover:text-[#004D73] border border-[#006699] rounded-lg px-3 py-1.5 transition-colors">
              <FeatherIcon name="download" class="h-3.5 w-3.5" />Export CSV
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-5">
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <table class="w-full text-xs">
                <thead><tr class="border-b border-gray-100 bg-gray-50">
                  <th class="px-5 py-3 text-left font-semibold text-gray-500">Timestamp</th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-500">User</th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-500">Action</th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-500">Covenant</th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-500">Detail</th>
                </tr></thead>
                <tbody>
                  <tr v-for="log in covenantChangelog" :key="log.id" class="border-b border-gray-50 hover:bg-gray-50">
                    <td class="px-5 py-3 text-gray-500 font-mono text-[11px]">{{ log.ts }}</td>
                    <td class="px-4 py-3">
                      <div class="flex items-center gap-2">
                        <div class="w-6 h-6 rounded-full bg-[#FFF0E6] text-[#CC5200] flex items-center justify-center text-[9px] font-bold">{{ log.user[0] }}</div>
                        <span class="text-gray-700 font-medium">{{ log.user }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-3">
                      <span class="rounded-full px-2 py-0.5 text-[9px] font-bold" :class="log.action==='Added' ? 'bg-green-100 text-green-700' : log.action==='Edited' ? 'bg-[#FFF0E6] text-[#CC5200]' : log.action==='Duplicated' ? 'bg-[#E6F4FA] text-[#006699]' : 'bg-red-100 text-red-700'">{{ log.action }}</span>
                    </td>
                    <td class="px-4 py-3 font-semibold text-gray-800">{{ log.covenant }}</td>
                    <td class="px-4 py-3 text-gray-500">{{ log.detail }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Add Covenant Modal -->
    <div
      v-if="showAddCovForm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      @click.self="showAddCovForm = false"
    >
      <div class="w-full max-w-md bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-[#FFF0E6] flex items-center justify-center shrink-0">
            <FeatherIcon :name="editingCov ? 'edit-2' : 'shield'" class="h-5 w-5 text-[#FF6600]" />
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-800">{{ editingCov ? 'Edit Covenant' : 'Add Covenant' }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ editingCov ? editingCov.name : 'Add a new covenant to the library' }}</p>
          </div>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Covenant Name <span class="text-red-400">*</span></label>
            <input v-model="covForm.name" type="text" placeholder="e.g. DSCR Minimum 1.25x" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Type</label>
              <select v-model="covForm.type" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]">
                <option>Financial</option>
                <option>Non-Financial</option>
                <option>Operational</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Frequency</label>
              <select v-model="covForm.frequency" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]">
                <option>Monthly</option>
                <option>Quarterly</option>
                <option>Semi-Annual</option>
                <option>Annual</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Metric / Threshold</label>
            <input v-model="covForm.metric" type="text" placeholder="e.g. DSCR ≥ 1.25" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Tags (comma-separated)</label>
            <input v-model="covForm.tags" type="text" placeholder="e.g. Cash Flow, Core" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
          </div>
        </div>
        <div class="flex gap-2 mt-6">
          <button @click="showAddCovForm = false" class="flex-1 rounded-lg border border-[#006699] py-2 text-sm font-semibold text-[#006699] hover:bg-[#E6F4FA] transition-colors">Cancel</button>
          <button @click="submitAddCovenant" class="flex-1 rounded-lg bg-[#FF6600] py-2 text-sm font-semibold text-white hover:bg-[#CC5200] transition-colors">{{ editingCov ? 'Save Changes' : 'Add Covenant' }}</button>
        </div>
      </div>
    </div>

    <!-- Add Task Modal -->
    <div
      v-if="showAddTaskForm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      @click.self="showAddTaskForm = false"
    >
      <div class="w-full max-w-md bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-[#FFF0E6] flex items-center justify-center shrink-0">
            <FeatherIcon name="check-square" class="h-5 w-5 text-[#FF6600]" />
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-800">Add Cure Task</h3>
            <p class="text-xs text-gray-400 mt-0.5">Create a new cure workflow task</p>
          </div>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Task Title <span class="text-red-400">*</span></label>
            <input v-model="taskForm.title" type="text" placeholder="e.g. DSCR Improvement Plan" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Facility / Borrower <span class="text-red-400">*</span></label>
            <input v-model="taskForm.facility" type="text" placeholder="e.g. PT Maju Bersama" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Priority</label>
              <select v-model="taskForm.priority" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]">
                <option>Critical</option>
                <option>High</option>
                <option>Medium</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Deadline</label>
              <input v-model="taskForm.deadline" type="date" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Assigned To</label>
            <input v-model="taskForm.owner" type="text" placeholder="e.g. Reza M." class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
          </div>
        </div>
        <div class="flex gap-2 mt-6">
          <button @click="showAddTaskForm = false" class="flex-1 rounded-lg border border-[#006699] py-2 text-sm font-semibold text-[#006699] hover:bg-[#E6F4FA] transition-colors">Cancel</button>
          <button @click="submitAddTask" class="flex-1 rounded-lg bg-[#FF6600] py-2 text-sm font-semibold text-white hover:bg-[#CC5200] transition-colors">Add Task</button>
        </div>
      </div>
    </div>

    <!-- New Waiver Modal -->
    <div
      v-if="showAddWaiverForm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      @click.self="showAddWaiverForm = false"
    >
      <div class="w-full max-w-md bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-[#FFF0E6] flex items-center justify-center shrink-0">
            <FeatherIcon name="file-text" class="h-5 w-5 text-[#FF6600]" />
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-800">New Waiver Request</h3>
            <p class="text-xs text-gray-400 mt-0.5">Submit a covenant waiver for approval</p>
          </div>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Covenant <span class="text-red-400">*</span></label>
            <select v-model="waiverForm.covenant" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]">
              <option value="">Select covenant…</option>
              <option v-for="c in covenantLibrary" :key="c.id" :value="c.name">{{ c.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Facility / Borrower <span class="text-red-400">*</span></label>
            <input v-model="waiverForm.facility" type="text" placeholder="e.g. PT Maju Bersama" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">Reason <span class="text-red-400">*</span></label>
            <input v-model="waiverForm.reason" type="text" placeholder="e.g. Post-pandemic recovery" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Waiver Expiry</label>
              <input v-model="waiverForm.expiry" type="date" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">Approver</label>
              <select v-model="waiverForm.approver" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]">
                <option>Risk Committee</option>
                <option>Credit Head</option>
                <option>Division Director</option>
                <option>Risk Officer</option>
              </select>
            </div>
          </div>
        </div>
        <div class="flex gap-2 mt-6">
          <button @click="showAddWaiverForm = false" class="flex-1 rounded-lg border border-[#006699] py-2 text-sm font-semibold text-[#006699] hover:bg-[#E6F4FA] transition-colors">Cancel</button>
          <button @click="submitAddWaiver" class="flex-1 rounded-lg bg-[#FF6600] py-2 text-sm font-semibold text-white hover:bg-[#CC5200] transition-colors">Submit Waiver</button>
        </div>
      </div>
    </div>

    <!-- Attach Document Modal -->
    <div v-if="showAttachModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showAttachModal = false">
      <div class="w-full max-w-sm bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-[#E6F4FA] flex items-center justify-center shrink-0">
            <FeatherIcon name="paperclip" class="h-5 w-5 text-[#006699]" />
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-800">Attach Document</h3>
            <p class="text-xs text-gray-400 mt-0.5 truncate max-w-[200px]">{{ attachContext?.ref }}</p>
          </div>
        </div>
        <div class="border-2 border-dashed border-gray-300 rounded-xl p-6 flex flex-col items-center justify-center text-center hover:border-[#FF8533] transition-colors cursor-pointer mb-4" @click="showToast('File picker opened')">
          <FeatherIcon name="upload-cloud" class="h-7 w-7 text-gray-300 mb-2" />
          <p class="text-xs text-gray-500 font-medium">Drop file here or <span class="text-[#FF6600]">browse</span></p>
          <p class="text-[10px] text-gray-400 mt-0.5">PDF, Excel, JPG — max 20MB</p>
        </div>
        <div v-if="attachContext?.context === 'test'" class="mb-4">
          <label class="block text-xs font-semibold text-gray-600 mb-1">Document Type</label>
          <select class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#FF8533]">
            <option>Financial Statement</option><option>Audit Report</option><option>Management Account</option><option>Supporting Data</option>
          </select>
        </div>
        <div class="flex gap-2">
          <button @click="showAttachModal = false" class="flex-1 rounded-lg border border-[#006699] py-2 text-sm font-semibold text-[#006699] hover:bg-[#E6F4FA]">Cancel</button>
          <button @click="confirmAttach" class="flex-1 rounded-lg bg-[#FF6600] py-2 text-sm font-semibold text-white hover:bg-[#CC5200] transition-colors">Attach</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div
        v-if="toast"
        class="fixed bottom-5 right-5 z-50 bg-gray-800 text-white text-sm font-medium px-4 py-2.5 rounded-xl shadow-xl flex items-center gap-2"
      >
        <FeatherIcon name="check-circle" class="h-4 w-4 text-[#FF8533]" />{{ toast }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { FeatherIcon } from "frappe-ui";
import LayoutHeader from "@/components/LayoutHeader.vue";

// ── Nav ──
const activeNav = ref("dashboard");
const navItems = [
  { id: "dashboard", label: "Dashboard", icon: "bar-chart-2" },
  { id: "library", label: "Covenant Library", icon: "book-open" },
  { id: "tests", label: "Test Engine", icon: "cpu" },
  { id: "calendar", label: "Covenant Calendar", icon: "calendar" },
  {
    id: "breach",
    label: "Breach & Alerts",
    icon: "alert-triangle",
    badge: "3",
    badgeColor: "bg-red-100 text-red-700",
  },
  {
    id: "cure",
    label: "Cure Workflow",
    icon: "check-square",
    badge: "5",
    badgeColor: "bg-amber-100 text-amber-700",
  },
  { id: "waiver", label: "Waiver Management", icon: "file-minus" },
  { id: "borrower", label: "Borrower Submission", icon: "upload-cloud" },
  { id: "changelog", label: "Change Log", icon: "clock" },
  { id: "sensitivity", label: "Sensitivity Analysis", icon: "activity" },
  { id: "reports", label: "Reports", icon: "bar-chart" },
];

const quickStats = [
  { label: "Pass", value: "26", dot: "bg-green-500", textColor: "text-green-600" },
  { label: "Watch", value: "10", dot: "bg-amber-400", textColor: "text-amber-600" },
  { label: "Breach", value: "6", dot: "bg-red-500", textColor: "text-red-600" },
];

// ── Dashboard ──
const dashStats = [
  {
    label: "Total Covenants",
    value: "42",
    icon: "shield",
    iconBg: "bg-[#FFF0E6]",
    iconColor: "text-[#FF6600]",
    badge: "Active",
    badgeClass: "bg-[#FFF0E6] text-[#CC5200]",
    nav: "library",
  },
  {
    label: "Pass",
    value: "26",
    icon: "check-circle",
    iconBg: "bg-green-100",
    iconColor: "text-green-600",
    badge: "62%",
    badgeClass: "bg-green-100 text-green-700",
    nav: "tests",
  },
  {
    label: "Watch",
    value: "10",
    icon: "eye",
    iconBg: "bg-amber-100",
    iconColor: "text-amber-600",
    badge: "24%",
    badgeClass: "bg-amber-100 text-amber-700",
    nav: "tests",
  },
  {
    label: "Breach",
    value: "6",
    icon: "alert-octagon",
    iconBg: "bg-red-100",
    iconColor: "text-red-600",
    badge: "Critical",
    badgeClass: "bg-red-100 text-red-700",
    nav: "breach",
  },
];

const trendMonths = ["Dec", "Jan", "Feb", "Mar", "Apr", "May"];
const watchTrend = [9, 11, 8, 12, 10, 10];
const breachTrend = [4, 5, 3, 7, 5, 6];

// ── Donut ──
const totalCovenants = 42;
const donutC = 2 * Math.PI * 42;
const statusBreakdown = [
  { label: "Pass", count: 26, color: "#10b981", textClass: "text-green-600" },
  { label: "Watch", count: 10, color: "#fbbf24", textClass: "text-amber-600" },
  { label: "Breach", count: 6, color: "#ef4444", textClass: "text-red-600" },
];
const statusDonut = computed(() => {
  let accum = donutC / 4;
  return statusBreakdown.map((s) => {
    const dash = (s.count / totalCovenants) * donutC;
    const result = { ...s, dash, offset: accum };
    accum -= dash;
    return result;
  });
});

// ── Active Breaches ──
const activeBreaches = ref([
  {
    id: 1,
    covenant: "DSCR Minimum 1.25x",
    facility: "PT Maju Bersama — Working Capital Rp 5B",
    actual: "1.08x",
    threshold: "≥ 1.25x",
    severity: "Critical",
    since: "30 Apr 2026",
    rm: "Reza M.",
  },
  {
    id: 2,
    covenant: "DER Maximum 3.0x",
    facility: "CV Teknik Jaya — Investment Loan Rp 2.5B",
    actual: "3.42x",
    threshold: "≤ 3.0x",
    severity: "High",
    since: "31 Mar 2026",
    rm: "Sari D.",
  },
  {
    id: 3,
    covenant: "Current Ratio 1.0x",
    facility: "PT Maju Bersama — Working Capital Rp 5B",
    actual: "0.87x",
    threshold: "≥ 1.0x",
    severity: "High",
    since: "30 Apr 2026",
    rm: "Reza M.",
  },
  {
    id: 4,
    covenant: "Insurance Renewal",
    facility: "Budi Santoso — KPR Rp 800M",
    actual: "Expired",
    threshold: "Valid",
    severity: "Medium",
    since: "15 May 2026",
    rm: "Ahmad F.",
  },
  {
    id: 5,
    covenant: "EBITDA Minimum Rp 2B",
    facility: "CV Teknik Jaya — Investment Loan Rp 2.5B",
    actual: "Rp 1.4B",
    threshold: "≥ Rp 2B",
    severity: "Critical",
    since: "31 Mar 2026",
    rm: "Sari D.",
  },
  {
    id: 6,
    covenant: "Financial Statement Submission",
    facility: "PT Maju Bersama — Working Capital Rp 5B",
    actual: "Overdue 15d",
    threshold: "Quarterly",
    severity: "Medium",
    since: "15 May 2026",
    rm: "Reza M.",
  },
]);

const breachFilter = ref("All");
const filteredBreaches = computed(() => {
  if (breachFilter.value === "All") return activeBreaches.value;
  return activeBreaches.value.filter((b) => b.severity === breachFilter.value);
});

// ── Upcoming Tests ──
const upcomingTests = [
  {
    id: 1,
    covenant: "DSCR Monthly Test",
    facility: "PT Maju Bersama",
    month: "JUN",
    day: 1,
    freq: "Monthly",
    urgent: true,
  },
  {
    id: 2,
    covenant: "Financial Statement Q2",
    facility: "CV Teknik Jaya",
    month: "JUN",
    day: 15,
    freq: "Quarterly",
    urgent: false,
  },
  {
    id: 3,
    covenant: "DER Quarterly Test",
    facility: "All Facilities",
    month: "JUN",
    day: 30,
    freq: "Quarterly",
    urgent: false,
  },
  {
    id: 4,
    covenant: "Insurance Validity",
    facility: "Budi Santoso",
    month: "JUL",
    day: 1,
    freq: "Monthly",
    urgent: false,
  },
  {
    id: 5,
    covenant: "EBITDA Review",
    facility: "CV Teknik Jaya",
    month: "JUL",
    day: 15,
    freq: "Monthly",
    urgent: false,
  },
];

// ── AI Predictions ──
const aiPredictions = [
  {
    id: 1,
    facility: "PT Maju Bersama",
    covenant: "DSCR",
    msg: "Likely to remain in breach — revenue recovery slow",
    risk: "High",
    confidence: 82,
  },
  {
    id: 2,
    facility: "CV Teknik Jaya",
    covenant: "DER",
    msg: "Improvement trend — potential cure by Aug 2026",
    risk: "Medium",
    confidence: 67,
  },
  {
    id: 3,
    facility: "Budi Santoso",
    covenant: "LTV",
    msg: "Property value stable — no breach risk",
    risk: "Low",
    confidence: 91,
  },
];

// ── Covenant Library ──
const libSearch = ref("");
const libFilter = ref("All");

const covenantLibrary = ref([
  {
    id: 1,
    name: "DSCR Minimum 1.25x",
    type: "Financial",
    metric: "DSCR ≥ 1.25",
    frequency: "Monthly",
    facilities: 8,
    tags: ["Cash Flow", "Core"],
    icon: "trending-up",
    template: true,
  },
  {
    id: 2,
    name: "DER Maximum 3.0x",
    type: "Financial",
    metric: "DER ≤ 3.0",
    frequency: "Quarterly",
    facilities: 12,
    tags: ["Leverage", "Core"],
    icon: "bar-chart",
    template: true,
  },
  {
    id: 3,
    name: "EBITDA Minimum",
    type: "Financial",
    metric: "EBITDA ≥ Target",
    frequency: "Quarterly",
    facilities: 6,
    tags: ["Profitability"],
    icon: "dollar-sign",
    template: true,
  },
  {
    id: 4,
    name: "Current Ratio 1.0x",
    type: "Financial",
    metric: "CR ≥ 1.0",
    frequency: "Monthly",
    facilities: 9,
    tags: ["Liquidity"],
    icon: "activity",
    template: true,
  },
  {
    id: 5,
    name: "Insurance Renewal",
    type: "Non-Financial",
    metric: "Valid Policy",
    frequency: "Annual",
    facilities: 15,
    tags: ["Insurance", "Affirmative"],
    icon: "shield",
    template: true,
  },
  {
    id: 6,
    name: "Financial Statement",
    type: "Reporting",
    metric: "On-time Submission",
    frequency: "Quarterly",
    facilities: 20,
    tags: ["Reporting"],
    icon: "file-text",
    template: true,
  },
  {
    id: 7,
    name: "No Additional Debt",
    type: "Non-Financial",
    metric: "Negative Covenant",
    frequency: "Continuous",
    facilities: 7,
    tags: ["Restriction", "Negative"],
    icon: "minus-circle",
    template: false,
  },
  {
    id: 8,
    name: "Asset Disposal Restriction",
    type: "Non-Financial",
    metric: "Prior Consent",
    frequency: "Continuous",
    facilities: 5,
    tags: ["Asset", "Negative"],
    icon: "lock",
    template: false,
  },
]);

const filteredLibrary = computed(() => {
  let list = covenantLibrary.value;
  if (libFilter.value !== "All") list = list.filter((c) => c.type === libFilter.value);
  if (libSearch.value) {
    const q = libSearch.value.toLowerCase();
    list = list.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.tags.some((t) => t.toLowerCase().includes(q))
    );
  }
  return list;
});

const selectedCovenant = ref(null);

// ── Test Engine ──
const testPeriod = ref("Latest");
const testing = ref(false);

const testResults = ref([
  {
    id: 1,
    covenant: "DSCR Minimum 1.25x",
    facility: "PT Maju Bersama",
    testDate: "31 May 2026",
    actual: "1.08x",
    threshold: "≥ 1.25x",
    headroom: "-14%",
    headroomPct: 0,
    status: "Breach",
  },
  {
    id: 2,
    covenant: "DSCR Minimum 1.25x",
    facility: "CV Teknik Jaya",
    testDate: "31 May 2026",
    actual: "1.48x",
    threshold: "≥ 1.25x",
    headroom: "+18%",
    headroomPct: 18,
    status: "Pass",
  },
  {
    id: 3,
    covenant: "DER Maximum 3.0x",
    facility: "PT Maju Bersama",
    testDate: "31 May 2026",
    actual: "2.6x",
    threshold: "≤ 3.0x",
    headroom: "+13%",
    headroomPct: 13,
    status: "Watch",
  },
  {
    id: 4,
    covenant: "DER Maximum 3.0x",
    facility: "CV Teknik Jaya",
    testDate: "31 May 2026",
    actual: "3.42x",
    threshold: "≤ 3.0x",
    headroom: "-14%",
    headroomPct: 0,
    status: "Breach",
  },
  {
    id: 5,
    covenant: "EBITDA Minimum Rp 2B",
    facility: "CV Teknik Jaya",
    testDate: "31 Mar 2026",
    actual: "Rp 1.4B",
    threshold: "≥ Rp 2B",
    headroom: "-30%",
    headroomPct: 0,
    status: "Breach",
  },
  {
    id: 6,
    covenant: "Current Ratio 1.0x",
    facility: "PT Maju Bersama",
    testDate: "31 May 2026",
    actual: "0.87x",
    threshold: "≥ 1.0x",
    headroom: "-13%",
    headroomPct: 0,
    status: "Breach",
  },
  {
    id: 7,
    covenant: "Current Ratio 1.0x",
    facility: "CV Teknik Jaya",
    testDate: "31 May 2026",
    actual: "1.32x",
    threshold: "≥ 1.0x",
    headroom: "+32%",
    headroomPct: 32,
    status: "Pass",
  },
  {
    id: 8,
    covenant: "Insurance Validity",
    facility: "Budi Santoso",
    testDate: "24 May 2026",
    actual: "Expired",
    threshold: "Valid",
    headroom: "-",
    headroomPct: 0,
    status: "Breach",
  },
  {
    id: 9,
    covenant: "Financial Statement",
    facility: "PT Maju Bersama",
    testDate: "15 May 2026",
    actual: "Overdue 15d",
    threshold: "On-time",
    headroom: "-",
    headroomPct: 0,
    status: "Breach",
  },
  {
    id: 10,
    covenant: "LTV Maximum 80%",
    facility: "Budi Santoso",
    testDate: "31 May 2026",
    actual: "68%",
    threshold: "≤ 80%",
    headroom: "+15%",
    headroomPct: 15,
    status: "Pass",
  },
]);

function runAllTests() {
  testing.value = true;
  setTimeout(() => {
    testing.value = false;
    showToast("All covenant tests completed — 3 breaches detected");
  }, 2000);
}

// ── Calendar ──
const calLegend = [
  { label: "Due Today", color: "bg-[#B3DDEF]" },
  { label: "Breach", color: "bg-red-200" },
  { label: "Watch", color: "bg-amber-200" },
  { label: "Pass", color: "bg-green-200" },
];

const calendarCells = computed(() => {
  const cells = [];
  // June 2026 starts on Monday
  for (let i = 0; i < 5; i++) cells.push({ key: `empty-${i}`, day: null, events: [] });
  const events = {
    1: [
      { id: 1, name: "DSCR Test", status: "Due" },
      { id: 2, name: "Current Ratio", status: "Breach" },
    ],
    5: [{ id: 3, name: "Fin. Statement", status: "Due" }],
    10: [{ id: 4, name: "DER Review", status: "Watch" }],
    15: [
      { id: 5, name: "Q2 Reporting", status: "Due" },
      { id: 6, name: "Insurance", status: "Watch" },
    ],
    20: [{ id: 7, name: "EBITDA Test", status: "Pass" }],
    25: [{ id: 8, name: "NPL Covenant", status: "Pass" }],
    30: [
      { id: 9, name: "DER Quarterly", status: "Due" },
      { id: 10, name: "DSCR Review", status: "Watch" },
    ],
  };
  for (let d = 1; d <= 30; d++) {
    cells.push({ key: `day-${d}`, day: d, today: d === 24, events: events[d] || [] });
  }
  return cells;
});

// ── Cure Workflow ──
const cureTasks = ref([
  {
    id: 1,
    title: "DSCR Improvement Plan — PT Maju Bersama",
    facility: "PT Maju Bersama",
    status: "Open",
    priority: "Critical",
    deadline: "30 Jun 2026",
    owner: "Reza M.",
    progress: 0,
    overdue: false,
  },
  {
    id: 2,
    title: "DER Reduction Strategy — CV Teknik Jaya",
    facility: "CV Teknik Jaya",
    status: "Open",
    priority: "Critical",
    deadline: "30 Jun 2026",
    owner: "Sari D.",
    progress: 0,
    overdue: false,
  },
  {
    id: 3,
    title: "Insurance Renewal Follow-up",
    facility: "Budi Santoso",
    status: "In Progress",
    priority: "High",
    deadline: "01 Jun 2026",
    owner: "Ahmad F.",
    progress: 60,
    overdue: false,
  },
  {
    id: 4,
    title: "Financial Statement Collection",
    facility: "PT Maju Bersama",
    status: "In Progress",
    priority: "High",
    deadline: "25 May 2026",
    owner: "Reza M.",
    progress: 40,
    overdue: true,
  },
  {
    id: 5,
    title: "EBITDA Turnaround Meeting",
    facility: "CV Teknik Jaya",
    status: "Done",
    priority: "Critical",
    deadline: "20 May 2026",
    owner: "Sari D.",
    progress: 100,
    overdue: false,
  },
]);

const cureColumns = [
  { id: "Open", label: "Open", dot: "bg-gray-400" },
  { id: "In Progress", label: "In Progress", dot: "bg-amber-400" },
  { id: "Done", label: "Done", dot: "bg-green-500" },
];

function advanceCure(task) {
  if (task.status === "Open") {
    task.status = "In Progress";
    task.progress = 30;
  } else if (task.status === "In Progress") {
    task.status = "Done";
    task.progress = 100;
  }
  showToast(`Task "${task.title.substring(0, 30)}..." updated`);
}

// ── Waivers ──
const waivers = ref([
  {
    id: 1,
    covenant: "DSCR Minimum 1.25x",
    reason: "Post-pandemic recovery",
    facility: "PT Maju Bersama",
    requested: "01 May 2026",
    expiry: "31 Jul 2026",
    approver: "Risk Committee",
    status: "Approved",
    expiring: false,
  },
  {
    id: 2,
    covenant: "DER Maximum 3.0x",
    reason: "Refinancing in progress",
    facility: "CV Teknik Jaya",
    requested: "10 May 2026",
    expiry: "30 Jun 2026",
    approver: "Credit Head",
    status: "Pending",
    expiring: false,
  },
  {
    id: 3,
    covenant: "Financial Statement Q1",
    reason: "Auditor delay",
    facility: "PT Maju Bersama",
    requested: "01 Apr 2026",
    expiry: "30 Apr 2026",
    approver: "Branch Head",
    status: "Expired",
    expiring: false,
  },
  {
    id: 4,
    covenant: "EBITDA Minimum",
    reason: "Seasonal business impact",
    facility: "CV Teknik Jaya",
    requested: "15 May 2026",
    expiry: "30 Jun 2026",
    approver: "Risk Committee",
    status: "Pending",
    expiring: true,
  },
]);

function approveWaiver(w) {
  w.status = "Approved";
  showToast(`Waiver approved for ${w.covenant}`);
}

// ── Reports ──
const covReports = [
  {
    id: 1,
    name: "Monthly Compliance Report",
    desc: "Pass/Watch/Breach summary with trend analysis",
    icon: "bar-chart-2",
    colorBg: "bg-[#FFF0E6]",
    colorText: "text-[#FF6600]",
    period: "May 2026",
    status: "Ready",
    statusClass: "bg-green-100 text-green-700",
  },
  {
    id: 2,
    name: "Breach & Cure Analytics",
    desc: "Breach aging, cure progress, and resolution rates",
    icon: "alert-triangle",
    colorBg: "bg-red-100",
    colorText: "text-red-600",
    period: "May 2026",
    status: "Ready",
    statusClass: "bg-green-100 text-green-700",
  },
  {
    id: 3,
    name: "Portfolio Covenant Health",
    desc: "Facility-level covenant health and portfolio segmentation",
    icon: "activity",
    colorBg: "bg-purple-100",
    colorText: "text-purple-600",
    period: "Q1 2026",
    status: "Ready",
    statusClass: "bg-green-100 text-green-700",
  },
  {
    id: 4,
    name: "Waiver Summary Report",
    desc: "Active waivers, approvals, and expiry tracking",
    icon: "file-minus",
    colorBg: "bg-amber-100",
    colorText: "text-amber-600",
    period: "May 2026",
    status: "Draft",
    statusClass: "bg-gray-100 text-gray-600",
  },
  {
    id: 5,
    name: "AI Risk Prediction Report",
    desc: "AI-generated breach probability and recommendations",
    icon: "zap",
    colorBg: "bg-indigo-100",
    colorText: "text-indigo-600",
    period: "May 2026",
    status: "Ready",
    statusClass: "bg-green-100 text-green-700",
  },
  {
    id: 6,
    name: "Regulatory Covenant Report",
    desc: "OJK/BI required covenant monitoring disclosure",
    icon: "shield",
    colorBg: "bg-[#E6F4FA]",
    colorText: "text-[#006699]",
    period: "Q1 2026",
    status: "Generating...",
    statusClass: "bg-[#E6F4FA] text-[#004D73]",
  },
];

// ── Sensitivity / Heatmap ──
const heatmapCovs = ["DSCR", "DER", "EBITDA", "Curr. Ratio", "LTV"];
const heatmapData = [
  {
    facility: "PT Maju Bersama",
    DSCR: -14,
    DER: 13,
    EBITDA: null,
    "Curr. Ratio": -13,
    LTV: null,
  },
  {
    facility: "CV Teknik Jaya",
    DSCR: 18,
    DER: -14,
    EBITDA: -30,
    "Curr. Ratio": 32,
    LTV: null,
  },
  {
    facility: "Budi Santoso",
    DSCR: null,
    DER: null,
    EBITDA: null,
    "Curr. Ratio": null,
    LTV: 15,
  },
  {
    facility: "PT Karya Utama",
    DSCR: 35,
    DER: 28,
    EBITDA: 22,
    "Curr. Ratio": 18,
    LTV: null,
  },
  {
    facility: "CV Mitra Sejati",
    DSCR: 8,
    DER: 45,
    EBITDA: 12,
    "Curr. Ratio": 6,
    LTV: null,
  },
];

function heatmapColor(val) {
  if (val === null) return "bg-gray-100 text-gray-400";
  if (val < 0) return "bg-red-100 text-red-700";
  if (val < 10) return "bg-amber-100 text-amber-700";
  if (val < 25) return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
}

const heatLegend = [
  { label: "Breach (<0%)", color: "bg-red-200" },
  { label: "Danger (<10%)", color: "bg-amber-200" },
  { label: "Watch (<25%)", color: "bg-yellow-200" },
  { label: "Safe (≥25%)", color: "bg-green-200" },
];

const simRevDrop = ref(10);
const simDebtInc = ref(10);
const simResult = ref(null);

function runSim() {
  const breaches =
    simRevDrop.value > 20 || simDebtInc.value > 30 ? 2 : simRevDrop.value > 10 ? 1 : 0;
  simResult.value = {
    breaches,
    detail:
      breaches > 0
        ? `Under -${simRevDrop.value}% revenue / +${
            simDebtInc.value
          }% debt service: DSCR would drop to ${(1.08 - simRevDrop.value * 0.01).toFixed(
            2
          )}x, DER would rise to ${(3.42 + simDebtInc.value * 0.02).toFixed(2)}x`
        : `Under -${simRevDrop.value}% revenue / +${simDebtInc.value}% debt service: all covenants remain within threshold`,
  };
  showToast("Simulation complete");
}

// ── Toast ──
const toast = ref("");
let toastTimer = null;
function showToast(msg) {
  toast.value = msg;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.value = "";
  }, 2500);
}

// ── Covenant Change Log ──
const covenantChangelog = ref([
  { id: 1, ts: '2026-05-24 09:00', user: 'Dewi Kusuma', action: 'Added', covenant: 'DSCR Minimum 1.25x', detail: 'New covenant added to library' },
  { id: 2, ts: '2026-05-23 14:30', user: 'Ahmad Fauzi', action: 'Edited', covenant: 'DER Maximum 3.0x', detail: 'Threshold changed from 3.5x to 3.0x' },
  { id: 3, ts: '2026-05-22 11:00', user: 'Sari Indrawati', action: 'Duplicated', covenant: 'Current Ratio 1.0x', detail: 'Duplicated as "Current Ratio 1.2x"' },
  { id: 4, ts: '2026-05-20 09:45', user: 'Dewi Kusuma', action: 'Edited', covenant: 'Insurance Renewal', detail: 'Frequency changed to Semi-Annual' },
  { id: 5, ts: '2026-05-18 16:00', user: 'Bimo Prakoso', action: 'Added', covenant: 'Financial Statement', detail: 'New reporting covenant added' },
])
let changelogIdSeq = 6

function addChangelogEntry(action, covenantName, detail) {
  const now = new Date()
  const ts = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
  covenantChangelog.value.unshift({ id: changelogIdSeq++, ts, user: 'Current User', action, covenant: covenantName, detail })
}

// ── Attach Document ──
const showAttachModal = ref(false)
const attachContext = ref(null)

function openAttachDoc(ctx) {
  attachContext.value = ctx
  showAttachModal.value = true
}

function confirmAttach() {
  // increment attach count on test results
  if (attachContext.value?.context === 'test') {
    const row = testResults.value.find(r => (r.covenant + ' — ' + r.facility) === attachContext.value.ref)
    if (row) row.attachCount = (row.attachCount || 0) + 1
  }
  showAttachModal.value = false
  showToast('Document attached successfully')
}

// ── Borrower Submission ──
const submissionForm = ref({ facility: '', covenant: '', period: '', value: '', notes: '' })
const borrowerSubmissions = ref([
  { id: 1, submitted: '2026-05-20 10:00', facility: 'PT Maju Bersama', covenant: 'DSCR Minimum 1.25x', period: 'Q1 2026', value: '1.08x', status: 'Reviewed' },
  { id: 2, submitted: '2026-05-18 14:30', facility: 'CV Teknik Jaya', covenant: 'DER Maximum 3.0x', period: 'Q1 2026', value: '3.42x', status: 'Reviewed' },
  { id: 3, submitted: '2026-05-15 09:00', facility: 'PT Maju Bersama', covenant: 'Financial Statement', period: 'Q1 2026', value: 'Submitted', status: 'Pending' },
  { id: 4, submitted: '2026-05-10 11:00', facility: 'Budi Santoso', covenant: 'Insurance Renewal', period: 'May 2026', value: 'Valid', status: 'Reviewed' },
])
let submissionIdSeq = 5

function submitBorrowerForm() {
  if (!submissionForm.value.facility || !submissionForm.value.covenant || !submissionForm.value.value) return
  const now = new Date()
  const ts = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
  borrowerSubmissions.value.unshift({
    id: submissionIdSeq++,
    submitted: ts,
    facility: submissionForm.value.facility.split('—')[0].trim(),
    covenant: submissionForm.value.covenant,
    period: submissionForm.value.period || '—',
    value: submissionForm.value.value,
    status: 'Pending',
  })
  submissionForm.value = { facility: '', covenant: '', period: '', value: '', notes: '' }
  showToast('Submission received — under review')
}

// ── Add / Edit Covenant ──
const showAddCovForm = ref(false);
const editingCov = ref(null);
const covForm = ref({ name: '', type: 'Financial', frequency: 'Quarterly', metric: '', tags: '' });

function openAddCovenant() {
  editingCov.value = null;
  covForm.value = { name: '', type: 'Financial', frequency: 'Quarterly', metric: '', tags: '' };
  showAddCovForm.value = true;
}

function openEditCovenant(cov) {
  editingCov.value = cov;
  covForm.value = {
    name: cov.name,
    type: cov.type,
    frequency: cov.frequency,
    metric: cov.metric === '—' ? '' : cov.metric,
    tags: cov.tags.join(', '),
  };
  showAddCovForm.value = true;
}

function submitAddCovenant() {
  if (!covForm.value.name.trim()) return;
  const tags = covForm.value.tags
    ? covForm.value.tags.split(',').map(t => t.trim()).filter(Boolean)
    : [];
  const icon = covForm.value.type === 'Financial' ? 'trending-up'
    : covForm.value.type === 'Non-Financial' ? 'check-circle'
    : 'file-text';

  if (editingCov.value) {
    const idx = covenantLibrary.value.findIndex(c => c.id === editingCov.value.id);
    if (idx !== -1) {
      covenantLibrary.value[idx] = {
        ...covenantLibrary.value[idx],
        name: covForm.value.name,
        type: covForm.value.type,
        frequency: covForm.value.frequency,
        metric: covForm.value.metric || '—',
        tags,
        icon,
      };
    }
    addChangelogEntry('Edited', covForm.value.name, `Type: ${covForm.value.type}, Metric: ${covForm.value.metric || '—'}`)
    showToast('Covenant updated');
  } else {
    covenantLibrary.value.unshift({
      id: Date.now(),
      name: covForm.value.name,
      type: covForm.value.type,
      metric: covForm.value.metric || '—',
      frequency: covForm.value.frequency,
      facilities: 0,
      tags,
      icon,
      template: false,
    });
    addChangelogEntry('Added', covForm.value.name, `Type: ${covForm.value.type}, Frequency: ${covForm.value.frequency}`)
    showToast('Covenant added to library');
  }
  showAddCovForm.value = false;
}

function duplicateCovenant(cov) {
  covenantLibrary.value.unshift({
    ...cov,
    id: Date.now(),
    name: cov.name + ' (Copy)',
    template: false,
  });
  addChangelogEntry('Duplicated', cov.name, `Created copy: "${cov.name} (Copy)"`)
  showToast('Covenant duplicated');
}

// ── Add Cure Task ──
const showAddTaskForm = ref(false);
const taskForm = ref({ title: '', facility: '', priority: 'High', deadline: '', owner: '' });

function openAddTask() {
  taskForm.value = { title: '', facility: '', priority: 'High', deadline: '', owner: '' };
  showAddTaskForm.value = true;
}

function submitAddTask() {
  if (!taskForm.value.title.trim() || !taskForm.value.facility.trim()) return;
  const dl = taskForm.value.deadline
    ? new Date(taskForm.value.deadline).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
    : '—';
  cureTasks.value.unshift({
    id: Date.now(),
    title: taskForm.value.title,
    facility: taskForm.value.facility,
    status: 'Open',
    priority: taskForm.value.priority,
    deadline: dl,
    owner: taskForm.value.owner || 'Unassigned',
    progress: 0,
    overdue: false,
  });
  showAddTaskForm.value = false;
  showToast('Cure task created');
}

// ── Add Waiver ──
const showAddWaiverForm = ref(false);
const waiverForm = ref({ covenant: '', facility: '', reason: '', expiry: '', approver: 'Risk Committee' });

function openAddWaiver() {
  waiverForm.value = { covenant: '', facility: '', reason: '', expiry: '', approver: 'Risk Committee' };
  showAddWaiverForm.value = true;
}

function submitAddWaiver() {
  if (!waiverForm.value.covenant || !waiverForm.value.facility.trim() || !waiverForm.value.reason.trim()) return;
  const today = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  const exp = waiverForm.value.expiry
    ? new Date(waiverForm.value.expiry).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
    : '—';
  waivers.value.unshift({
    id: Date.now(),
    covenant: waiverForm.value.covenant,
    reason: waiverForm.value.reason,
    facility: waiverForm.value.facility,
    requested: today,
    expiry: exp,
    approver: waiverForm.value.approver,
    status: 'Pending',
    expiring: false,
  });
  showAddWaiverForm.value = false;
  showToast('Waiver request submitted');
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
