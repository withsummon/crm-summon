<template>
  <div class="covenant-monitoring flex flex-col h-full bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-orange-600 flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">Covenant Monitoring</h1>
            <p class="text-sm text-gray-500">Financial &amp; non-financial covenant tracking, breach detection, and cure workflows</p>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            @click="showCovenantModal = true"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
            Add Covenant
          </button>
          <button
            @click="runMonitoring"
            :disabled="isRunning"
            class="px-4 py-2 bg-orange-600 text-white rounded-lg text-sm font-medium hover:bg-orange-700 disabled:opacity-60 flex items-center gap-2"
          >
            <svg v-if="isRunning" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3l14 9-14 9V3z" /></svg>
            {{ isRunning ? 'Running...' : 'Run Monitoring' }}
          </button>
        </div>
      </div>

      <!-- Page Tabs -->
      <div class="flex gap-1 mt-4">
        <button
          v-for="tab in pageTabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
            activeTab === tab.id
              ? 'bg-orange-50 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300'
              : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400'
          ]"
        >
          {{ tab.label }}
          <span v-if="tab.badge" :class="['px-1.5 py-0.5 text-xs rounded-full font-semibold', tab.badgeColor || 'bg-orange-600 text-white']">{{ tab.badge }}</span>
        </button>
      </div>
    </div>

    <!-- Body -->
    <div class="flex-1 overflow-auto p-6">

      <!-- ───── TAB: Dashboard ───── -->
      <div v-if="activeTab === 'dashboard'">
        <!-- KPI Strip -->
        <div class="grid grid-cols-5 gap-4 mb-6">
          <div v-for="kpi in dashKPIs" :key="kpi.label" :class="['rounded-xl p-4 border', kpi.highlight ? 'bg-red-50 border-red-200' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700']">
            <div class="flex justify-between items-start">
              <p class="text-xs text-gray-500 mb-1">{{ kpi.label }}</p>
              <span v-if="kpi.alert" class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            </div>
            <p class="text-2xl font-bold" :class="kpi.color">{{ kpi.value }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ kpi.sub }}</p>
          </div>
        </div>

        <!-- Health Matrix + Alert Feed -->
        <div class="grid grid-cols-3 gap-6 mb-6">
          <!-- Covenant Health by Type -->
          <div class="col-span-2 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Covenant Health Overview</h3>
            <div class="space-y-3">
              <div v-for="type in covenantTypes" :key="type.name">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-gray-700 dark:text-gray-300 font-medium">{{ type.name }}</span>
                  <div class="flex gap-3 text-xs">
                    <span class="text-green-600">✓ {{ type.compliant }}</span>
                    <span class="text-amber-600">⚠ {{ type.warning }}</span>
                    <span class="text-red-600">✗ {{ type.breached }}</span>
                  </div>
                </div>
                <div class="flex h-3 rounded-full overflow-hidden gap-0.5">
                  <div class="bg-green-500 rounded-full" :style="{ width: (type.compliant / type.total * 100) + '%' }"></div>
                  <div class="bg-amber-400" :style="{ width: (type.warning / type.total * 100) + '%' }"></div>
                  <div class="bg-red-500" :style="{ width: (type.breached / type.total * 100) + '%' }"></div>
                </div>
                <p class="text-xs text-gray-400 mt-0.5">{{ type.total }} total covenants</p>
              </div>
            </div>
            <div class="flex gap-4 mt-4 text-xs text-gray-500">
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-green-500 inline-block"></span>Compliant</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-400 inline-block"></span>Warning Zone</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-500 inline-block"></span>Breached</span>
            </div>
          </div>

          <!-- Live Alert Feed -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 overflow-hidden">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">Recent Alerts</h3>
              <span class="flex h-2 w-2 relative">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
              </span>
            </div>
            <div class="space-y-3 overflow-y-auto max-h-64">
              <div v-for="alert in recentAlerts" :key="alert.id" :class="['p-3 rounded-lg border text-xs', alert.severity === 'breach' ? 'bg-red-50 border-red-200' : 'bg-amber-50 border-amber-200']">
                <div class="flex justify-between items-start mb-1">
                  <span :class="['font-semibold', alert.severity === 'breach' ? 'text-red-700' : 'text-amber-700']">
                    {{ alert.severity === 'breach' ? '🔴 BREACH' : '🟡 WARNING' }}
                  </span>
                  <span class="text-gray-400">{{ alert.time }}</span>
                </div>
                <p class="font-medium text-gray-800">{{ alert.borrower }}</p>
                <p class="text-gray-600 mt-0.5">{{ alert.message }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Facilities at Risk -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Facilities Under Close Watch</h3>
          <table class="w-full text-sm">
            <thead class="border-b border-gray-100 dark:border-gray-700">
              <tr>
                <th class="text-left pb-2 text-xs text-gray-500">Borrower</th>
                <th class="text-left pb-2 text-xs text-gray-500">Facility</th>
                <th class="text-right pb-2 text-xs text-gray-500">Outstanding</th>
                <th class="text-left pb-2 text-xs text-gray-500">Covenants</th>
                <th class="text-left pb-2 text-xs text-gray-500">Risk Level</th>
                <th class="text-left pb-2 text-xs text-gray-500">Next Review</th>
                <th class="pb-2"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50 dark:divide-gray-700">
              <tr v-for="f in watchlist" :key="f.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td class="py-3">
                  <div class="font-medium text-gray-900 dark:text-white">{{ f.borrower }}</div>
                  <div class="text-xs text-gray-500">RM: {{ f.rm }}</div>
                </td>
                <td class="py-3 text-gray-700 dark:text-gray-300">{{ f.facility }}</td>
                <td class="py-3 text-right font-semibold text-gray-900 dark:text-white">{{ f.outstanding }}</td>
                <td class="py-3">
                  <div class="flex gap-1">
                    <span v-if="f.breached > 0" class="px-1.5 py-0.5 bg-red-100 text-red-700 rounded text-xs">{{ f.breached }} breach</span>
                    <span v-if="f.warning > 0" class="px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded text-xs">{{ f.warning }} warn</span>
                    <span v-if="f.compliant > 0" class="px-1.5 py-0.5 bg-green-100 text-green-700 rounded text-xs">{{ f.compliant }} ok</span>
                  </div>
                </td>
                <td class="py-3"><span :class="riskBadge(f.risk)">{{ f.risk }}</span></td>
                <td class="py-3 text-gray-500 text-xs">{{ f.nextReview }}</td>
                <td class="py-3">
                  <button @click="openFacility(f)" class="px-3 py-1 border border-orange-300 text-orange-600 rounded text-xs hover:bg-orange-50">Review</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ───── TAB: Covenant Library ───── -->
      <div v-if="activeTab === 'library'">
        <div class="flex gap-3 mb-5 flex-wrap items-center">
          <input v-model="librarySearch" type="text" placeholder="Search covenants..." class="flex-1 min-w-52 px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          <select v-model="libraryFilter" class="px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            <option value="">All Types</option>
            <option value="financial">Financial</option>
            <option value="non_financial">Non-Financial</option>
            <option value="reporting">Reporting</option>
            <option value="operational">Operational</option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="cov in filteredLibrary"
            :key="cov.id"
            class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5"
          >
            <div class="flex justify-between items-start mb-2">
              <div>
                <span :class="['px-2 py-0.5 rounded text-xs font-semibold mr-2', typeBadge(cov.type)]">{{ cov.typeLabel }}</span>
                <h3 class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ cov.name }}</h3>
              </div>
              <span class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">Active</span>
            </div>
            <p class="text-xs text-gray-500 mb-3">{{ cov.description }}</p>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="bg-gray-50 dark:bg-gray-700 rounded p-2">
                <p class="text-gray-400">Threshold</p>
                <p class="font-semibold text-gray-800 dark:text-white">{{ cov.threshold }}</p>
              </div>
              <div class="bg-gray-50 dark:bg-gray-700 rounded p-2">
                <p class="text-gray-400">Frequency</p>
                <p class="font-semibold text-gray-800 dark:text-white">{{ cov.frequency }}</p>
              </div>
              <div class="bg-gray-50 dark:bg-gray-700 rounded p-2">
                <p class="text-gray-400">Cure Period</p>
                <p class="font-semibold text-gray-800 dark:text-white">{{ cov.curePeriod }}</p>
              </div>
              <div class="bg-gray-50 dark:bg-gray-700 rounded p-2">
                <p class="text-gray-400">Facilities Using</p>
                <p class="font-semibold text-orange-600">{{ cov.facilityCount }}</p>
              </div>
            </div>
            <div class="flex gap-2 mt-3">
              <button class="flex-1 py-1.5 border border-gray-300 text-gray-600 rounded text-xs hover:bg-gray-50">Edit</button>
              <button @click="showCovenantModal = true" class="flex-1 py-1.5 border border-orange-300 text-orange-600 rounded text-xs hover:bg-orange-50">Assign to Facility</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Monitoring ───── -->
      <div v-if="activeTab === 'monitoring'">
        <div class="flex gap-3 mb-5 items-center flex-wrap">
          <input v-model="monitorSearch" type="text" placeholder="Search borrower or facility..." class="flex-1 min-w-52 px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          <select v-model="monitorFilterStatus" class="px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            <option value="">All Status</option>
            <option value="compliant">Compliant</option>
            <option value="warning">Warning Zone</option>
            <option value="breached">Breached</option>
          </select>
          <select v-model="monitorFilterType" class="px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            <option value="">All Types</option>
            <option value="financial">Financial</option>
            <option value="non_financial">Non-Financial</option>
            <option value="reporting">Reporting</option>
          </select>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Borrower / Facility</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Covenant</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Type</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Threshold</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Actual</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Headroom</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Next Check</th>
                <th class="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr
                v-for="item in filteredMonitoring"
                :key="item.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/50"
              >
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900 dark:text-white">{{ item.borrower }}</div>
                  <div class="text-xs text-gray-500">{{ item.facilityId }}</div>
                </td>
                <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ item.covenant }}</td>
                <td class="px-4 py-3"><span :class="typeBadge(item.type)">{{ item.typeLabel }}</span></td>
                <td class="px-4 py-3 text-right text-gray-700 dark:text-gray-300">{{ item.threshold }}</td>
                <td class="px-4 py-3 text-right font-semibold" :class="item.status === 'breached' ? 'text-red-600' : item.status === 'warning' ? 'text-amber-600' : 'text-gray-900 dark:text-white'">{{ item.actual }}</td>
                <td class="px-4 py-3 text-right text-xs" :class="item.headroom < 0 ? 'text-red-600 font-semibold' : item.headroom < 10 ? 'text-amber-600' : 'text-green-600'">{{ item.headroom >= 0 ? '+' : '' }}{{ item.headroom }}%</td>
                <td class="px-4 py-3"><span :class="monitorStatusBadge(item.status)">{{ monitorStatusLabel(item.status) }}</span></td>
                <td class="px-4 py-3 text-xs text-gray-500">{{ item.nextCheck }}</td>
                <td class="px-4 py-3">
                  <button
                    v-if="item.status === 'breached'"
                    @click="openBreachDetail(item)"
                    class="px-3 py-1 bg-red-600 text-white rounded text-xs font-medium hover:bg-red-700"
                  >Cure</button>
                  <button
                    v-else
                    @click="openBreachDetail(item)"
                    class="px-3 py-1 border border-gray-300 text-gray-600 rounded text-xs hover:bg-gray-50"
                  >Detail</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ───── TAB: Breaches ───── -->
      <div v-if="activeTab === 'breaches'" class="space-y-4">
        <!-- Breach Summary -->
        <div class="grid grid-cols-4 gap-4">
          <div v-for="s in breachSummary" :key="s.label" :class="['rounded-xl p-4 border', s.red ? 'bg-red-50 border-red-200' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700']">
            <p class="text-xs text-gray-500 mb-1">{{ s.label }}</p>
            <p class="text-2xl font-bold" :class="s.color">{{ s.value }}</p>
          </div>
        </div>

        <!-- Active Breaches -->
        <div
          v-for="breach in activeBreaches"
          :key="breach.id"
          class="bg-white dark:bg-gray-800 rounded-xl border-l-4 border-red-500 border border-gray-200 dark:border-gray-700 p-5"
        >
          <div class="flex justify-between items-start">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              </div>
              <div>
                <div class="flex items-center gap-2 mb-0.5">
                  <h3 class="font-bold text-gray-900 dark:text-white">{{ breach.borrower }}</h3>
                  <span class="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-semibold">BREACHED</span>
                  <span v-if="breach.cureExpiry" class="px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs">Cure expires: {{ breach.cureExpiry }}</span>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400">{{ breach.covenant }}</p>
                <p class="text-xs text-gray-500 mt-1">Facility: {{ breach.facilityId }} · Detected: {{ breach.detectedDate }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold text-red-600">{{ breach.actual }} vs {{ breach.threshold }}</p>
              <p class="text-xs text-gray-500">Actual vs Threshold</p>
            </div>
          </div>

          <!-- Cure Timeline -->
          <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-3">
              <p class="text-xs font-semibold text-gray-600 uppercase">Cure Workflow</p>
              <span :class="['px-2 py-0.5 rounded text-xs font-semibold', breach.cureStatus === 'pending' ? 'bg-amber-100 text-amber-700' : breach.cureStatus === 'in_progress' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700']">{{ breach.cureStatus.replace('_', ' ') }}</span>
            </div>
            <div class="flex gap-2 items-center">
              <div v-for="(step, idx) in breach.cureSteps" :key="idx" class="flex items-center gap-2">
                <div :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold', step.done ? 'bg-green-500 text-white' : step.active ? 'bg-orange-500 text-white' : 'bg-gray-200 text-gray-500']">
                  {{ step.done ? '✓' : idx + 1 }}
                </div>
                <span :class="['text-xs', step.done ? 'text-green-600' : step.active ? 'text-orange-600 font-medium' : 'text-gray-400']">{{ step.label }}</span>
                <span v-if="idx < breach.cureSteps.length - 1" class="text-gray-300">→</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 mt-4">
            <button @click="openCureModal(breach)" class="px-4 py-1.5 bg-orange-600 text-white rounded text-sm font-medium hover:bg-orange-700">Update Cure Status</button>
            <button class="px-4 py-1.5 border border-gray-300 text-gray-600 rounded text-sm hover:bg-gray-50">Waiver Request</button>
            <button class="px-4 py-1.5 border border-red-300 text-red-600 rounded text-sm hover:bg-red-50">Escalate</button>
            <button class="px-4 py-1.5 border border-gray-300 text-gray-600 rounded text-sm hover:bg-gray-50">Add Note</button>
          </div>
        </div>

        <!-- Warning Zone -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-amber-200 dark:border-gray-700 p-5">
          <h3 class="text-sm font-semibold text-amber-700 mb-4">⚠ Warning Zone (approaching breach)</h3>
          <div class="space-y-3">
            <div v-for="w in warningItems" :key="w.id" class="flex items-center gap-4 py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ w.borrower }}</p>
                <p class="text-xs text-gray-500">{{ w.covenant }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-amber-600">{{ w.actual }}</p>
                <p class="text-xs text-gray-400">Threshold: {{ w.threshold }}</p>
              </div>
              <div class="w-24">
                <div class="flex justify-between text-xs mb-0.5">
                  <span class="text-gray-400">Headroom</span>
                  <span class="text-amber-600 font-medium">{{ w.headroom }}</span>
                </div>
                <div class="h-1.5 bg-gray-200 rounded-full">
                  <div class="h-full bg-amber-400 rounded-full" :style="{ width: (100 - w.headroomPct) + '%' }"></div>
                </div>
              </div>
              <button @click="openCovenantAlert(w)" class="px-3 py-1 border border-amber-300 text-amber-600 rounded text-xs hover:bg-amber-50 flex-shrink-0">Alert</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Analytics ───── -->
      <div v-if="activeTab === 'analytics'">
        <div class="grid grid-cols-4 gap-4 mb-6">
          <div v-for="kpi in analyticsKPIs" :key="kpi.label" class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <p class="text-xs text-gray-500 mb-1">{{ kpi.label }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ kpi.value }}</p>
            <p :class="['text-xs mt-1', kpi.up ? 'text-green-600' : 'text-red-600']">{{ kpi.up ? '↑' : '↓' }} {{ kpi.change }} vs prev quarter</p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <!-- Breach History -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Monthly Breach History</h3>
            <div class="flex items-end gap-2 h-36">
              <div v-for="bar in breachHistory" :key="bar.month" class="flex-1 flex flex-col items-center gap-1">
                <span class="text-xs text-gray-500">{{ bar.count }}</span>
                <div class="w-full rounded-t" :class="bar.count > 3 ? 'bg-red-500' : bar.count > 1 ? 'bg-amber-400' : 'bg-green-500'" :style="{ height: (bar.count / 8 * 100) + '%', minHeight: '4px' }"></div>
                <span class="text-xs text-gray-400">{{ bar.month }}</span>
              </div>
            </div>
          </div>

          <!-- Breach by Type -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Breaches by Covenant Type</h3>
            <div class="space-y-3">
              <div v-for="t in breachByType" :key="t.type">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-gray-700 dark:text-gray-300">{{ t.type }}</span>
                  <span class="font-semibold text-gray-900 dark:text-white">{{ t.count }}</span>
                </div>
                <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full bg-orange-500 rounded-full" :style="{ width: (t.count / 12 * 100) + '%' }"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Cure Success Rate -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Cure Outcome Tracking</h3>
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div class="text-center p-4 bg-green-50 rounded-xl">
                <p class="text-3xl font-bold text-green-600">78%</p>
                <p class="text-xs text-gray-500 mt-1">Cured Within Period</p>
              </div>
              <div class="text-center p-4 bg-red-50 rounded-xl">
                <p class="text-3xl font-bold text-red-600">22%</p>
                <p class="text-xs text-gray-500 mt-1">Escalated / Waived</p>
              </div>
            </div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between text-gray-600 dark:text-gray-400">
                <span>Avg Cure Time</span>
                <span class="font-semibold text-gray-900 dark:text-white">18 days</span>
              </div>
              <div class="flex justify-between text-gray-600 dark:text-gray-400">
                <span>Waivers Granted</span>
                <span class="font-semibold text-gray-900 dark:text-white">3 this quarter</span>
              </div>
              <div class="flex justify-between text-gray-600 dark:text-gray-400">
                <span>Escalated to Legal</span>
                <span class="font-semibold text-red-600">2 this quarter</span>
              </div>
            </div>
          </div>

          <!-- Risk Sector Concentration -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Breach by Industry Sector</h3>
            <div class="space-y-3">
              <div v-for="sec in sectorBreaches" :key="sec.sector" class="flex items-center gap-3">
                <span class="text-xs text-gray-500 w-28">{{ sec.sector }}</span>
                <div class="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full" :class="sec.color" :style="{ width: (sec.count / 5 * 100) + '%' }"></div>
                </div>
                <span class="text-xs font-semibold text-gray-700 dark:text-gray-300 w-4">{{ sec.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ───── MODALS ───── -->

    <!-- Add Covenant Modal -->
    <div v-if="showCovenantModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCovenantModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-5">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">Add Covenant</h2>
          <button @click="showCovenantModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Covenant Name</label>
            <input type="text" placeholder="e.g. Minimum DSCR Ratio" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Type</label>
              <select class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                <option>Financial</option>
                <option>Non-Financial</option>
                <option>Reporting</option>
                <option>Operational</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Direction</label>
              <select class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                <option>Minimum (≥ threshold)</option>
                <option>Maximum (≤ threshold)</option>
                <option>Exact (= threshold)</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Threshold Value</label>
              <input type="text" placeholder="e.g. 1.25x or 60%" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Monitoring Frequency</label>
              <select class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                <option>Monthly</option>
                <option>Quarterly</option>
                <option>Semi-annually</option>
                <option>Annually</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Cure Period (days)</label>
            <input type="number" value="30" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
            <textarea rows="2" placeholder="What this covenant monitors..." class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showCovenantModal = false" class="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">Cancel</button>
          <button @click="saveCovenant" class="flex-1 py-2 bg-orange-600 text-white rounded-lg text-sm font-medium hover:bg-orange-700">Add Covenant</button>
        </div>
      </div>
    </div>

    <!-- Cure Workflow Modal -->
    <div v-if="showCureModal && selectedBreach" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCureModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-5">
          <div>
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">Update Cure Status</h2>
            <p class="text-sm text-gray-500">{{ selectedBreach.borrower }} — {{ selectedBreach.covenant }}</p>
          </div>
          <button @click="showCureModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="space-y-4">
          <div class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm">
            <p class="font-semibold text-red-800">Breach: {{ selectedBreach.actual }} vs threshold {{ selectedBreach.threshold }}</p>
            <p class="text-red-600 text-xs mt-0.5">Detected: {{ selectedBreach.detectedDate }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Cure Action</label>
            <select class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
              <option>Borrower Notification Sent</option>
              <option>Remediation Plan Submitted</option>
              <option>Partial Cure Achieved</option>
              <option>Full Cure — Covenant Restored</option>
              <option>Request Waiver</option>
              <option>Escalate to Legal</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">New Actual Value</label>
            <input type="text" :placeholder="selectedBreach.actual" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Evidence / Supporting Document</label>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center text-sm text-gray-400 cursor-pointer hover:border-orange-400 hover:text-orange-500">
              Click to upload or drag &amp; drop
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Notes</label>
            <textarea rows="2" placeholder="Cure actions taken..." class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showCureModal = false" class="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">Cancel</button>
          <button @click="saveCure" class="flex-1 py-2 bg-orange-600 text-white rounded-lg text-sm font-medium hover:bg-orange-700">Update Status</button>
        </div>
      </div>
    </div>

    <!-- Facility Detail Modal -->
    <div v-if="showFacilityModal && selectedFacility" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showFacilityModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-xl p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-5">
          <div>
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ selectedFacility.borrower }}</h2>
            <p class="text-sm text-gray-500">{{ selectedFacility.facility }} — {{ selectedFacility.outstanding }}</p>
          </div>
          <button @click="showFacilityModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="grid grid-cols-3 gap-3 mb-4">
          <div class="p-3 rounded-lg text-center" :class="selectedFacility.breached > 0 ? 'bg-red-50' : 'bg-gray-50'">
            <p class="text-xl font-bold" :class="selectedFacility.breached > 0 ? 'text-red-600' : 'text-gray-700'">{{ selectedFacility.breached }}</p>
            <p class="text-xs text-gray-500">Breached</p>
          </div>
          <div class="p-3 rounded-lg text-center" :class="selectedFacility.warning > 0 ? 'bg-amber-50' : 'bg-gray-50'">
            <p class="text-xl font-bold" :class="selectedFacility.warning > 0 ? 'text-amber-600' : 'text-gray-700'">{{ selectedFacility.warning }}</p>
            <p class="text-xs text-gray-500">Warning</p>
          </div>
          <div class="p-3 rounded-lg text-center bg-green-50">
            <p class="text-xl font-bold text-green-600">{{ selectedFacility.compliant }}</p>
            <p class="text-xs text-gray-500">Compliant</p>
          </div>
        </div>
        <p class="text-xs font-semibold text-gray-600 uppercase mb-2">Risk Level</p>
        <span :class="riskBadge(selectedFacility.risk)" class="text-sm mb-4 inline-block">{{ selectedFacility.risk }}</span>
        <div class="flex gap-3 mt-4">
          <button @click="showFacilityModal = false; activeTab = 'monitoring'" class="flex-1 py-2 bg-orange-600 text-white rounded-lg text-sm font-medium">View Monitoring Detail</button>
          <button @click="showFacilityModal = false" class="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-600">Close</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast" class="fixed bottom-6 right-6 bg-green-600 text-white px-5 py-3 rounded-xl shadow-lg text-sm font-medium z-50 flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
      {{ toast }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const activeTab = ref('dashboard')
const librarySearch = ref('')
const libraryFilter = ref('')
const monitorSearch = ref('')
const monitorFilterStatus = ref('')
const monitorFilterType = ref('')
const isRunning = ref(false)
const showCovenantModal = ref(false)
const showCureModal = ref(false)
const showFacilityModal = ref(false)
const selectedBreach = ref(null)
const selectedFacility = ref(null)
const toast = ref('')

const pageTabs = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'library', label: 'Covenant Library' },
  { id: 'monitoring', label: 'Monitoring' },
  { id: 'breaches', label: 'Breaches', badge: 4, badgeColor: 'bg-red-500 text-white' },
  { id: 'analytics', label: 'Analytics' },
]

const dashKPIs = [
  { label: 'Total Covenants', value: '142', sub: 'Across 38 facilities', color: 'text-gray-900 dark:text-white' },
  { label: 'Compliant', value: '121', sub: '85.2% compliance', color: 'text-green-600' },
  { label: 'Warning Zone', value: '17', sub: 'Approaching breach', color: 'text-amber-600', alert: true },
  { label: 'Active Breaches', value: '4', sub: 'Requires cure action', color: 'text-red-600', highlight: true, alert: true },
  { label: 'Cured This Month', value: '7', sub: 'Successfully resolved', color: 'text-blue-600' },
]

const covenantTypes = [
  { name: 'Financial Covenants', total: 62, compliant: 52, warning: 7, breached: 3 },
  { name: 'Non-Financial Covenants', total: 38, compliant: 34, warning: 3, breached: 1 },
  { name: 'Reporting Covenants', total: 28, compliant: 26, warning: 2, breached: 0 },
  { name: 'Operational Covenants', total: 14, compliant: 9, warning: 5, breached: 0 },
]

const recentAlerts = [
  { id: 1, severity: 'breach', borrower: 'PT Agri Sejahtera', message: 'DSCR 0.92x below minimum 1.25x', time: '2h ago' },
  { id: 2, severity: 'warning', borrower: 'CV Sukses Makmur', message: 'Debt-to-Equity approaching max 2.5x (current: 2.3x)', time: '5h ago' },
  { id: 3, severity: 'breach', borrower: 'PT Logistik Prima', message: 'Annual audit report overdue (30+ days)', time: '1d ago' },
  { id: 4, severity: 'warning', borrower: 'PT Bangun Graha Mandiri', message: 'Interest Coverage Ratio 1.55x, threshold 1.5x — tight', time: '1d ago' },
  { id: 5, severity: 'breach', borrower: 'Koperasi Citra Abadi', message: 'Minimum Cash Reserve IDR 500M not maintained', time: '2d ago' },
]

const watchlist = [
  { id: 1, borrower: 'PT Agri Sejahtera', facility: 'KUR Pertanian', outstanding: 'Rp 500M', rm: 'Rina Kartika', breached: 1, warning: 2, compliant: 4, risk: 'Critical', nextReview: '2026-05-30' },
  { id: 2, borrower: 'PT Logistik Prima', facility: 'Fleet Financing', outstanding: 'Rp 12B', rm: 'Wahyu Prasetyo', breached: 1, warning: 1, compliant: 5, risk: 'High', nextReview: '2026-06-01' },
  { id: 3, borrower: 'Koperasi Citra Abadi', facility: 'Linkage Syariah', outstanding: 'Rp 3.5B', rm: 'Siti Rahma', breached: 2, warning: 0, compliant: 3, risk: 'Critical', nextReview: '2026-05-28' },
  { id: 4, borrower: 'CV Sukses Makmur', facility: 'Kredit Investasi', outstanding: 'Rp 3.2B', rm: 'Sari Dewi', breached: 0, warning: 3, compliant: 4, risk: 'Medium', nextReview: '2026-06-15' },
  { id: 5, borrower: 'PT Bangun Graha Mandiri', facility: 'Property Financing', outstanding: 'Rp 65B', rm: 'Hendra Gunawan', breached: 0, warning: 2, compliant: 8, risk: 'Medium', nextReview: '2026-07-01' },
]

const covenantLibrary = ref([
  { id: 1, name: 'Minimum DSCR', type: 'financial', typeLabel: 'Financial', description: 'Debt Service Coverage Ratio must be maintained at minimum 1.25x on a quarterly basis.', threshold: '≥ 1.25x', frequency: 'Quarterly', curePeriod: '30 days', facilityCount: 24 },
  { id: 2, name: 'Maximum Debt-to-Equity', type: 'financial', typeLabel: 'Financial', description: 'Total debt-to-equity ratio must not exceed 2.5x at any reporting date.', threshold: '≤ 2.5x', frequency: 'Semi-annually', curePeriod: '45 days', facilityCount: 18 },
  { id: 3, name: 'Minimum Interest Coverage', type: 'financial', typeLabel: 'Financial', description: 'EBIT must cover interest expenses by at least 1.5x.', threshold: '≥ 1.5x', frequency: 'Quarterly', curePeriod: '30 days', facilityCount: 22 },
  { id: 4, name: 'Annual Audited Financial Statements', type: 'reporting', typeLabel: 'Reporting', description: 'Borrower must submit audited annual financial statements within 120 days of fiscal year-end.', threshold: '120 days after FY-end', frequency: 'Annually', curePeriod: '30 days', facilityCount: 38 },
  { id: 5, name: 'Quarterly Management Accounts', type: 'reporting', typeLabel: 'Reporting', description: 'Management accounts to be submitted within 45 days of quarter end.', threshold: '45 days after Q-end', frequency: 'Quarterly', curePeriod: '14 days', facilityCount: 30 },
  { id: 6, name: 'No Additional Indebtedness', type: 'non_financial', typeLabel: 'Non-Financial', description: 'Borrower may not incur additional debt beyond approved limits without prior written consent.', threshold: 'Consent required', frequency: 'Ongoing', curePeriod: 'Immediate', facilityCount: 28 },
  { id: 7, name: 'Cross-Default Clause', type: 'non_financial', typeLabel: 'Non-Financial', description: 'Default on any other financial obligation triggers default under this facility.', threshold: 'No other defaults', frequency: 'Ongoing', curePeriod: 'Immediate', facilityCount: 35 },
  { id: 8, name: 'Minimum Cash Reserve', type: 'operational', typeLabel: 'Operational', description: 'Minimum cash balance of IDR 500M must be maintained in designated BNI account.', threshold: '≥ Rp 500M', frequency: 'Monthly', curePeriod: '7 days', facilityCount: 8 },
])

const filteredLibrary = computed(() => {
  return covenantLibrary.value.filter((c) => {
    if (libraryFilter.value && c.type !== libraryFilter.value) return false
    if (librarySearch.value && !c.name.toLowerCase().includes(librarySearch.value.toLowerCase())) return false
    return true
  })
})

const monitoringItems = ref([
  { id: 1, borrower: 'PT Maju Bersama Tbk', facilityId: 'FAC-2024-001', covenant: 'Minimum DSCR', type: 'financial', typeLabel: 'Financial', threshold: '≥ 1.25x', actual: '1.82x', headroom: 46, status: 'compliant', nextCheck: 'Jun 30, 2026' },
  { id: 2, borrower: 'PT Teknologi Nusantara', facilityId: 'FAC-2024-002', covenant: 'Maximum Debt-to-Equity', type: 'financial', typeLabel: 'Financial', threshold: '≤ 2.5x', actual: '1.8x', headroom: 28, status: 'compliant', nextCheck: 'Jun 30, 2026' },
  { id: 3, borrower: 'PT Agri Sejahtera', facilityId: 'FAC-2024-003', covenant: 'Minimum DSCR', type: 'financial', typeLabel: 'Financial', threshold: '≥ 1.25x', actual: '0.92x', headroom: -26, status: 'breached', nextCheck: 'Immediate' },
  { id: 4, borrower: 'CV Sukses Makmur', facilityId: 'FAC-2024-004', covenant: 'Maximum Debt-to-Equity', type: 'financial', typeLabel: 'Financial', threshold: '≤ 2.5x', actual: '2.3x', headroom: 8, status: 'warning', nextCheck: 'Jun 15, 2026' },
  { id: 5, borrower: 'PT Logistik Prima', facilityId: 'FAC-2024-005', covenant: 'Annual Audited Financial Statements', type: 'reporting', typeLabel: 'Reporting', threshold: '120 days', actual: '152 days', headroom: -27, status: 'breached', nextCheck: 'Immediate' },
  { id: 6, borrower: 'PT Bangun Graha Mandiri', facilityId: 'FAC-2024-006', covenant: 'Minimum Interest Coverage', type: 'financial', typeLabel: 'Financial', threshold: '≥ 1.5x', actual: '1.55x', headroom: 3, status: 'warning', nextCheck: 'Jul 1, 2026' },
  { id: 7, borrower: 'Koperasi Sejahtera Bersama', facilityId: 'FAC-2024-007', covenant: 'Quarterly Management Accounts', type: 'reporting', typeLabel: 'Reporting', threshold: '45 days', actual: '12 days', headroom: 73, status: 'compliant', nextCheck: 'Jul 15, 2026' },
  { id: 8, borrower: 'Koperasi Citra Abadi', facilityId: 'FAC-2024-008', covenant: 'Minimum Cash Reserve', type: 'operational', typeLabel: 'Operational', threshold: '≥ Rp 500M', actual: 'Rp 280M', headroom: -44, status: 'breached', nextCheck: 'Immediate' },
  { id: 9, borrower: 'PT Herbal Nusantara', facilityId: 'FAC-2024-009', covenant: 'No Additional Indebtedness', type: 'non_financial', typeLabel: 'Non-Financial', threshold: 'Consent required', actual: 'Compliant', headroom: 100, status: 'compliant', nextCheck: 'Ongoing' },
  { id: 10, borrower: 'PT Bangun Graha Mandiri', facilityId: 'FAC-2024-006', covenant: 'Maximum Debt-to-Equity', type: 'financial', typeLabel: 'Financial', threshold: '≤ 2.5x', actual: '2.1x', headroom: 16, status: 'warning', nextCheck: 'Jul 1, 2026' },
])

const filteredMonitoring = computed(() => {
  return monitoringItems.value.filter((item) => {
    if (monitorFilterStatus.value && item.status !== monitorFilterStatus.value) return false
    if (monitorFilterType.value && item.type !== monitorFilterType.value) return false
    if (monitorSearch.value) {
      const q = monitorSearch.value.toLowerCase()
      if (!item.borrower.toLowerCase().includes(q) && !item.facilityId.toLowerCase().includes(q)) return false
    }
    return true
  })
})

const activeBreaches = ref([
  {
    id: 1, borrower: 'PT Agri Sejahtera', facilityId: 'FAC-2024-003', covenant: 'Minimum DSCR', threshold: '≥ 1.25x', actual: '0.92x', detectedDate: '2026-04-30', cureExpiry: '2026-05-30', cureStatus: 'in_progress',
    cureSteps: [
      { label: 'Notification', done: true, active: false },
      { label: 'Remediation Plan', done: true, active: false },
      { label: 'Cure Action', done: false, active: true },
      { label: 'Verification', done: false, active: false },
      { label: 'Resolution', done: false, active: false },
    ],
  },
  {
    id: 2, borrower: 'PT Logistik Prima', facilityId: 'FAC-2024-005', covenant: 'Annual Audited Financial Statements', threshold: '120 days after FY-end', actual: '152 days', detectedDate: '2026-05-10', cureExpiry: '2026-06-10', cureStatus: 'pending',
    cureSteps: [
      { label: 'Notification', done: true, active: false },
      { label: 'Remediation Plan', done: false, active: true },
      { label: 'Cure Action', done: false, active: false },
      { label: 'Verification', done: false, active: false },
      { label: 'Resolution', done: false, active: false },
    ],
  },
  {
    id: 3, borrower: 'Koperasi Citra Abadi', facilityId: 'FAC-2024-008', covenant: 'Minimum Cash Reserve', threshold: '≥ Rp 500M', actual: 'Rp 280M', detectedDate: '2026-05-20', cureExpiry: '2026-05-27', cureStatus: 'pending',
    cureSteps: [
      { label: 'Notification', done: true, active: false },
      { label: 'Remediation Plan', done: false, active: true },
      { label: 'Cure Action', done: false, active: false },
      { label: 'Verification', done: false, active: false },
      { label: 'Resolution', done: false, active: false },
    ],
  },
])

const warningItems = [
  { id: 1, borrower: 'CV Sukses Makmur', covenant: 'Max Debt-to-Equity', actual: '2.3x', threshold: '≤ 2.5x', headroom: '+8%', headroomPct: 8 },
  { id: 2, borrower: 'PT Bangun Graha Mandiri', covenant: 'Min Interest Coverage', actual: '1.55x', threshold: '≥ 1.5x', headroom: '+3%', headroomPct: 3 },
  { id: 3, borrower: 'PT Bangun Graha Mandiri', covenant: 'Max Debt-to-Equity', actual: '2.1x', threshold: '≤ 2.5x', headroom: '+16%', headroomPct: 16 },
  { id: 4, borrower: 'PT Logistik Prima', covenant: 'Min DSCR', actual: '1.32x', threshold: '≥ 1.25x', headroom: '+6%', headroomPct: 6 },
]

const breachSummary = [
  { label: 'Total Breaches', value: '4', color: 'text-red-600', red: true },
  { label: 'Pending Cure', value: '2', color: 'text-amber-600' },
  { label: 'In Progress', value: '1', color: 'text-blue-600' },
  { label: 'Cured (MTD)', value: '3', color: 'text-green-600' },
]

const analyticsKPIs = [
  { label: 'Compliance Rate', value: '85.2%', up: true, change: '2.1%' },
  { label: 'Avg Cure Time', value: '18 days', up: true, change: '3d faster' },
  { label: 'Waiver Rate', value: '4.2%', up: false, change: '1.1%' },
  { label: 'Breach Frequency', value: '2.1/month', up: true, change: '0.5' },
]

const breachHistory = [
  { month: 'Dec', count: 2 },
  { month: 'Jan', count: 4 },
  { month: 'Feb', count: 3 },
  { month: 'Mar', count: 6 },
  { month: 'Apr', count: 5 },
  { month: 'May', count: 4 },
]

const breachByType = [
  { type: 'Financial', count: 12 },
  { type: 'Non-Financial', count: 5 },
  { type: 'Reporting', count: 4 },
  { type: 'Operational', count: 3 },
]

const sectorBreaches = [
  { sector: 'Agriculture', count: 5, color: 'bg-red-500' },
  { sector: 'Property', count: 4, color: 'bg-orange-500' },
  { sector: 'Logistics', count: 3, color: 'bg-amber-400' },
  { sector: 'Manufacturing', count: 2, color: 'bg-yellow-400' },
  { sector: 'Cooperatives', count: 2, color: 'bg-green-400' },
  { sector: 'Technology', count: 1, color: 'bg-blue-400' },
]

function typeBadge(type) {
  return {
    financial: 'px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium',
    non_financial: 'px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-medium',
    reporting: 'px-2 py-0.5 bg-teal-100 text-teal-700 rounded text-xs font-medium',
    operational: 'px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs font-medium',
  }[type] || 'px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs'
}

function riskBadge(risk) {
  return {
    Critical: 'px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-bold',
    High: 'px-2 py-0.5 bg-orange-100 text-orange-700 rounded text-xs font-semibold',
    Medium: 'px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs font-medium',
    Low: 'px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs',
  }[risk] || 'px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs'
}

function monitorStatusBadge(status) {
  return {
    compliant: 'px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium',
    warning: 'px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs font-medium',
    breached: 'px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-semibold',
  }[status] || 'px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs'
}

function monitorStatusLabel(status) {
  return { compliant: 'Compliant', warning: 'Warning', breached: 'Breached' }[status] || status
}

function openFacility(f) {
  selectedFacility.value = f
  showFacilityModal.value = true
}

function openBreachDetail(item) {
  const breach = activeBreaches.value.find((b) => b.borrower === item.borrower)
  if (breach) {
    selectedBreach.value = breach
    showCureModal.value = true
  }
}

function openCureModal(breach) {
  selectedBreach.value = breach
  showCureModal.value = true
}

function openCovenantAlert(w) {
  showToast(`Alert sent to RM for ${w.borrower}`)
}

function saveCovenant() {
  showCovenantModal.value = false
  showToast('Covenant added to library')
}

function saveCure() {
  showCureModal.value = false
  showToast('Cure status updated successfully')
}

function runMonitoring() {
  isRunning.value = true
  setTimeout(() => {
    isRunning.value = false
    showToast('Monitoring run complete — 142 covenants checked')
  }, 3000)
}

function showToast(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 3000)
}
</script>
