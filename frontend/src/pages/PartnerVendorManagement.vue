<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #FF6600, #006699)"
          >
            <FeatherIcon name="truck" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Partner & Vendor Management') }}
            </h1>
            <p class="truncate text-xs text-crm-muted">
              {{ __('Vendor governance, SLA tracking, and partner performance') }}
            </p>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button :label="__('New Vendor')" variant="solid" @click="openVendorForm" />
          <Button :label="__('Create Request')" variant="outline" @click="openRequestForm" />
          <Button :label="__('Vendor Portal')" variant="outline" icon="external-link" @click="activeTab = 'portal'" />
        </div>
      </template>
    </LayoutHeader>

    <!-- Tabs -->
    <div class="flex items-center gap-1 border-b border-crm-border bg-white px-4">
      <button
        v-for="tab in pageTabs"
        :key="tab.key"
        class="flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium transition-colors"
        :class="activeTab === tab.key ? 'border-b-2 border-[#FF6600] text-[#FF6600]' : 'text-ink-gray-5 hover:text-ink-gray-8'"
        @click="activeTab = tab.key"
      >
        {{ __(tab.label) }}
        <span
          v-if="tab.badge"
          class="rounded-full bg-[#FF6600] px-1.5 text-[10px] text-white"
        >{{ tab.badge }}</span>
      </button>
    </div>

    <!-- ── DASHBOARD ── -->
    <div v-if="activeTab === 'dashboard'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="grid grid-cols-6 gap-3">
        <div
          v-for="kpi in dashKpis"
          :key="kpi.label"
          class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between">
            <div class="text-xs text-ink-gray-4">{{ __(kpi.label) }}</div>
            <FeatherIcon :name="kpi.icon" class="h-4 w-4" :class="kpi.iconColor" />
          </div>
          <div class="mt-1 text-2xl font-bold" :class="kpi.valueColor || 'text-ink-gray-9'">
            {{ kpi.value }}
          </div>
          <div class="mt-0.5 text-[11px]" :class="kpi.deltaColor || 'text-ink-gray-4'">
            {{ kpi.delta }}
          </div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div class="col-span-2 rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('SLA Health by Vendor Type') }}</div>
            <Badge :label="slaOverviewLabel" variant="subtle" theme="orange" />
          </div>
          <div class="space-y-3">
            <div v-for="row in slaOverview" :key="row.category" class="flex items-center gap-3 text-xs">
              <div class="w-32 text-ink-gray-6">{{ row.category }}</div>
              <div class="flex-1 h-3 rounded-full bg-surface-gray-2 overflow-hidden">
                <div
                  class="h-3 rounded-full"
                  :class="row.color"
                  :style="{ width: row.compliance + '%' }"
                />
              </div>
              <div class="w-20 text-right font-medium" :class="row.textColor">
                {{ row.compliance }}%
              </div>
              <div class="w-24 text-right text-ink-gray-4">
                {{ row.breaches }} breaches
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Operational Alerts') }}</div>
            <Badge :label="alerts.length + ' alerts'" variant="subtle" theme="red" />
          </div>
          <div class="space-y-2 text-xs">
            <div
              v-for="alert in alerts"
              :key="alert.id"
              class="rounded-lg border border-outline-gray-1 p-2"
            >
              <div class="flex items-start justify-between">
                <div>
                  <div class="text-ink-gray-8 font-semibold">{{ alert.title }}</div>
                  <div class="text-ink-gray-4">{{ alert.detail }}</div>
                </div>
                <span :class="alertBadge(alert.severity)">{{ alert.severity }}</span>
              </div>
              <div class="mt-1 text-[10px] text-ink-gray-4">{{ alert.time }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Top Performing Partners') }}</div>
          <div class="space-y-2 text-xs">
            <div
              v-for="(partner, idx) in topPartners"
              :key="partner.name"
              class="flex items-center gap-3 rounded-lg border border-outline-gray-1 px-3 py-2"
            >
              <div class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold"
                :class="idx === 0 ? 'bg-[#FFE0CC] text-[#CC5200]' : idx === 1 ? 'bg-[#CCE5F5] text-[#004D73]' : 'bg-amber-100 text-amber-700'"
              >
                {{ idx + 1 }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-ink-gray-8 font-semibold truncate">{{ partner.name }}</div>
                <div class="text-[10px] text-ink-gray-4">{{ partner.category }} · {{ partner.tier }}</div>
              </div>
              <div class="text-right">
                <div class="text-xs font-semibold" :class="scoreColor(partner.score)">{{ partner.score }}</div>
                <div class="text-[10px] text-ink-gray-4">score</div>
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Active Service Requests') }}</div>
          <div class="space-y-2 text-xs">
            <div
              v-for="req in activeRequests"
              :key="req.id"
              class="flex items-start gap-3 rounded-lg border border-outline-gray-1 px-3 py-2"
            >
              <div class="flex h-8 w-8 items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-6">
                <FeatherIcon :name="req.icon" class="h-4 w-4" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-ink-gray-8 font-semibold">{{ req.type }}</div>
                <div class="text-[10px] text-ink-gray-4">{{ req.vendor }} · {{ req.requester }}</div>
                <div class="mt-1 text-[10px]" :class="req.slaBreached ? 'text-red-600' : 'text-[#FF6600]'">
                  SLA due {{ req.slaDue }}
                </div>
              </div>
              <Badge :label="req.status" variant="subtle" :theme="statusTheme(req.status)" />
            </div>
          </div>
        </div>

        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Upcoming Contract Renewals') }}</div>
          <div class="space-y-2 text-xs">
            <div
              v-for="contract in upcomingRenewals"
              :key="contract.vendor"
              class="flex items-center justify-between rounded-lg border border-outline-gray-1 px-3 py-2"
            >
              <div>
                <div class="text-ink-gray-8 font-semibold">{{ contract.vendor }}</div>
                <div class="text-[10px] text-ink-gray-4">{{ contract.type }} · {{ contract.owner }}</div>
              </div>
              <div class="text-right">
                <div class="text-xs font-semibold" :class="contract.urgency === 'High' ? 'text-red-600' : 'text-amber-600'">
                  {{ contract.renewal }}
                </div>
                <div class="text-[10px] text-ink-gray-4">{{ contract.urgency }} priority</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── VENDOR DIRECTORY ── -->
    <div v-if="activeTab === 'directory'" class="flex min-h-0 flex-1 flex-col gap-3 bg-surface-gray-1 p-4">
      <div class="flex flex-wrap items-center gap-2 rounded-[14px] border border-crm-border bg-white px-4 py-3 shadow-sm">
        <input
          v-model="vendorSearch"
          class="h-8 rounded-md border border-outline-gray-2 px-3 text-sm"
          style="width: 220px"
          placeholder="Search vendor, service..."
        />
        <select v-model="vendorCategory" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">All Categories</option>
          <option v-for="cat in vendorCategories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
        <select v-model="vendorTier" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">All Tiers</option>
          <option v-for="tier in vendorTiers" :key="tier" :value="tier">{{ tier }}</option>
        </select>
        <select v-model="vendorStatus" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">All Status</option>
          <option v-for="status in vendorStatuses" :key="status" :value="status">{{ status }}</option>
        </select>
        <div class="ml-auto text-xs text-ink-gray-4">{{ filteredVendors.length }} vendors</div>
      </div>

      <div class="flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <div class="overflow-y-auto h-full">
          <table class="w-full text-xs">
            <thead class="sticky top-0 bg-surface-gray-1">
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="px-4 py-2.5 text-left font-medium">Vendor</th>
                <th class="px-4 py-2.5 text-left font-medium">Category</th>
                <th class="px-4 py-2.5 text-left font-medium">Tier</th>
                <th class="px-4 py-2.5 text-right font-medium">SLA</th>
                <th class="px-4 py-2.5 text-right font-medium">Score</th>
                <th class="px-4 py-2.5 text-left font-medium">Contract End</th>
                <th class="px-4 py-2.5 text-left font-medium">Risk</th>
                <th class="px-4 py-2.5 text-left font-medium">Status</th>
                <th class="px-4 py-2.5 text-center font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="vendor in filteredVendors"
                :key="vendor.id"
                class="cursor-pointer border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
                @click="openVendorProfile(vendor)"
              >
                <td class="px-4 py-2.5">
                  <div class="font-semibold text-ink-gray-8">{{ vendor.name }}</div>
                  <div class="text-[10px] text-ink-gray-4">{{ vendor.owner }} · {{ vendor.region }}</div>
                </td>
                <td class="px-4 py-2.5 text-ink-gray-6">{{ vendor.category }}</td>
                <td class="px-4 py-2.5">
                  <Badge :label="vendor.tier" variant="subtle" theme="orange" />
                </td>
                <td class="px-4 py-2.5 text-right">
                  <span class="font-semibold" :class="vendor.slaCompliance >= 95 ? 'text-[#FF6600]' : vendor.slaCompliance >= 90 ? 'text-amber-600' : 'text-red-600'">
                    {{ vendor.slaCompliance }}%
                  </span>
                </td>
                <td class="px-4 py-2.5 text-right">
                  <span class="font-semibold" :class="scoreColor(vendor.score)">{{ vendor.score }}</span>
                </td>
                <td class="px-4 py-2.5 text-ink-gray-6">{{ vendor.contractEnd }}</td>
                <td class="px-4 py-2.5">
                  <Badge :label="vendor.risk" variant="subtle" :theme="riskTheme(vendor.risk)" />
                </td>
                <td class="px-4 py-2.5">
                  <Badge :label="vendor.status" variant="subtle" :theme="statusTheme(vendor.status)" />
                </td>
                <td class="px-4 py-2.5 text-center">
                  <Button label="View" variant="ghost" size="sm" @click.stop="openVendorProfile(vendor)" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── ONBOARDING ── -->
    <div v-if="activeTab === 'onboarding'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
        <div class="mb-4 text-sm font-semibold text-ink-gray-8">{{ __('Vendor Onboarding Pipeline') }}</div>
        <div class="flex items-start gap-0">
          <div v-for="(stage, idx) in onboardingStages" :key="stage.label" class="flex flex-1 flex-col items-center">
            <div class="relative flex flex-col items-center">
              <div class="flex h-10 w-10 items-center justify-center rounded-full text-xs font-semibold text-white shadow-md" :class="stage.color">
                {{ stage.count }}
              </div>
            </div>
            <div class="mt-3 text-center">
              <div class="text-xs font-semibold text-ink-gray-8">{{ stage.label }}</div>
              <div class="mt-0.5 text-[10px] text-ink-gray-4">{{ stage.desc }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-[14px] border border-crm-border bg-white shadow-sm overflow-hidden">
        <table class="w-full text-xs">
          <thead class="bg-surface-gray-1">
            <tr class="border-b border-outline-gray-1 text-ink-gray-4">
              <th class="px-4 py-2.5 text-left font-medium">Vendor</th>
              <th class="px-4 py-2.5 text-left font-medium">Stage</th>
              <th class="px-4 py-2.5 text-left font-medium">Owner</th>
              <th class="px-4 py-2.5 text-left font-medium">SLA Due</th>
              <th class="px-4 py-2.5 text-left font-medium">Missing Docs</th>
              <th class="px-4 py-2.5 text-center font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in onboardingList" :key="item.id" class="border-b border-outline-gray-1 last:border-0">
              <td class="px-4 py-2.5 font-semibold text-ink-gray-8">{{ item.vendor }}</td>
              <td class="px-4 py-2.5">
                <Badge :label="item.stage" variant="subtle" theme="orange" />
              </td>
              <td class="px-4 py-2.5 text-ink-gray-6">{{ item.owner }}</td>
              <td class="px-4 py-2.5" :class="item.slaBreached ? 'text-red-600 font-semibold' : 'text-ink-gray-6'">
                {{ item.slaDue }}
              </td>
              <td class="px-4 py-2.5 text-ink-gray-5">{{ item.missingDocs }}</td>
              <td class="px-4 py-2.5 text-center">
                <Button label="Review" variant="ghost" size="sm" @click="() => {}" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── SERVICE REQUESTS ── -->
    <div v-if="activeTab === 'requests'" class="flex min-h-0 flex-1 flex-col gap-3 bg-surface-gray-1 p-4">
      <div class="flex items-center justify-between rounded-[14px] border border-crm-border bg-white px-4 py-3 shadow-sm">
        <div class="text-sm font-semibold text-ink-gray-8">{{ __('Service Request Workflow') }}</div>
        <Button :label="__('New Request')" variant="solid" size="sm" @click="openRequestForm" />
      </div>
      <div class="flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <div class="overflow-y-auto h-full">
          <table class="w-full text-xs">
            <thead class="sticky top-0 bg-surface-gray-1">
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="px-4 py-2.5 text-left font-medium">Request</th>
                <th class="px-4 py-2.5 text-left font-medium">Vendor</th>
                <th class="px-4 py-2.5 text-left font-medium">Requester</th>
                <th class="px-4 py-2.5 text-left font-medium">SLA</th>
                <th class="px-4 py-2.5 text-left font-medium">Priority</th>
                <th class="px-4 py-2.5 text-left font-medium">Status</th>
                <th class="px-4 py-2.5 text-left font-medium">Owner</th>
                <th class="px-4 py-2.5 text-center font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in requests" :key="req.id" class="border-b border-outline-gray-1 last:border-0">
                <td class="px-4 py-2.5">
                  <div class="font-semibold text-ink-gray-8">{{ req.type }}</div>
                  <div class="text-[10px] text-ink-gray-4">{{ req.caseId }}</div>
                </td>
                <td class="px-4 py-2.5 text-ink-gray-6">{{ req.vendor }}</td>
                <td class="px-4 py-2.5 text-ink-gray-6">{{ req.requester }}</td>
                <td class="px-4 py-2.5" :class="req.slaBreached ? 'text-red-600 font-semibold' : 'text-ink-gray-6'">
                  {{ req.slaDue }}
                </td>
                <td class="px-4 py-2.5">
                  <Badge :label="req.priority" variant="subtle" :theme="req.priority === 'Urgent' ? 'red' : req.priority === 'High' ? 'orange' : 'blue'" />
                </td>
                <td class="px-4 py-2.5">
                  <Badge :label="req.status" variant="subtle" :theme="statusTheme(req.status)" />
                </td>
                <td class="px-4 py-2.5 text-ink-gray-6">{{ req.owner }}</td>
                <td class="px-4 py-2.5 text-center">
                  <Button label="Track" variant="ghost" size="sm" @click="() => {}" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── SLA & CONTRACTS ── -->
    <div v-if="activeTab === 'sla'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
        <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('SLA Tracking per Vendor') }}</div>
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-outline-gray-1 text-ink-gray-4">
              <th class="pb-2 text-left font-medium">Vendor</th>
              <th class="pb-2 text-left font-medium">Response SLA</th>
              <th class="pb-2 text-left font-medium">Resolution SLA</th>
              <th class="pb-2 text-right font-medium">Compliance</th>
              <th class="pb-2 text-left font-medium">Last Breach</th>
              <th class="pb-2 text-left font-medium">Next Review</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sla in slaTracking" :key="sla.vendor" class="border-b border-outline-gray-1 last:border-0">
              <td class="py-2.5 text-ink-gray-8 font-semibold">{{ sla.vendor }}</td>
              <td class="py-2.5 text-ink-gray-5">{{ sla.response }}</td>
              <td class="py-2.5 text-ink-gray-5">{{ sla.resolution }}</td>
              <td class="py-2.5 text-right font-semibold" :class="sla.compliance >= 95 ? 'text-[#FF6600]' : sla.compliance >= 90 ? 'text-amber-600' : 'text-red-600'">
                {{ sla.compliance }}%
              </td>
              <td class="py-2.5 text-ink-gray-5">{{ sla.lastBreach }}</td>
              <td class="py-2.5 text-ink-gray-5">{{ sla.nextReview }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Contract Management') }}</div>
            <Button :label="__('New Contract')" variant="subtle" size="sm" @click="showContractForm = true" />
          </div>
          <div class="space-y-2 text-xs">
            <div v-for="contract in contracts" :key="contract.id" class="rounded-lg border border-outline-gray-1 p-3">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <div class="text-ink-gray-8 font-semibold">{{ contract.vendor }}</div>
                  <div class="text-[10px] text-ink-gray-4">{{ contract.type }} · {{ contract.term }}</div>
                </div>
                <Badge :label="contract.status" variant="subtle" :theme="contract.status === 'Renewal' ? 'orange' : contract.status === 'Pending' ? 'gray' : 'green'" />
              </div>
              <div class="mt-2 flex items-center justify-between text-[10px] text-ink-gray-4">
                <span>{{ contract.start }} → {{ contract.end }}</span>
                <span>{{ contract.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Invoice & Payment Tracking') }}</div>
            <Badge :label="invoices.length + ' invoices'" variant="subtle" theme="orange" />
          </div>
          <div class="space-y-2 text-xs">
            <div v-for="invoice in invoices" :key="invoice.id" class="flex items-center justify-between rounded-lg border border-outline-gray-1 px-3 py-2">
              <div>
                <div class="text-ink-gray-8 font-semibold">{{ invoice.vendor }}</div>
                <div class="text-[10px] text-ink-gray-4">{{ invoice.number }} · Due {{ invoice.due }}</div>
              </div>
              <div class="text-right">
                <div class="text-xs font-semibold text-ink-gray-8">{{ invoice.amount }}</div>
                <Badge :label="invoice.status" variant="subtle" :theme="invoice.status === 'Overdue' ? 'red' : invoice.status === 'Processing' ? 'orange' : 'green'" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── PERFORMANCE & COMPLIANCE ── -->
    <div v-if="activeTab === 'performance'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="grid grid-cols-3 gap-4">
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Performance Scorecards') }}</div>
          <div class="space-y-2 text-xs">
            <div v-for="perf in performanceScores" :key="perf.vendor" class="rounded-lg border border-outline-gray-1 px-3 py-2">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-ink-gray-8 font-semibold">{{ perf.vendor }}</div>
                  <div class="text-[10px] text-ink-gray-4">{{ perf.review }} · {{ perf.reviewer }}</div>
                </div>
                <div class="text-right">
                  <div class="text-xs font-semibold" :class="scoreColor(perf.score)">{{ perf.score }}</div>
                  <div class="text-[10px]" :class="perf.trend >= 0 ? 'text-[#FF6600]' : 'text-red-500'">
                    {{ perf.trend >= 0 ? '+' : '' }}{{ perf.trend }} pts
                  </div>
                </div>
              </div>
              <div class="mt-2 flex items-center justify-between text-[10px] text-ink-gray-4">
                <span>{{ perf.tier }}</span>
                <span>{{ perf.status }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Compliance Monitoring') }}</div>
          <div class="space-y-2 text-xs">
            <div v-for="check in complianceChecks" :key="check.id" class="rounded-lg border border-outline-gray-1 px-3 py-2">
              <div class="flex items-start justify-between">
                <div>
                  <div class="text-ink-gray-8 font-semibold">{{ check.vendor }}</div>
                  <div class="text-[10px] text-ink-gray-4">{{ check.type }}</div>
                </div>
                <Badge :label="check.status" variant="subtle" :theme="check.status === 'Due' ? 'orange' : check.status === 'Failed' ? 'red' : 'green'" />
              </div>
              <div class="mt-1 text-[10px] text-ink-gray-4">Due {{ check.due }} · Owner {{ check.owner }}</div>
            </div>
          </div>
        </div>

        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Partner Tier Program') }}</div>
          <div class="space-y-2 text-xs">
            <div v-for="tier in tierProgram" :key="tier.name" class="flex items-center justify-between rounded-lg border border-outline-gray-1 px-3 py-2">
              <div>
                <div class="text-ink-gray-8 font-semibold">{{ tier.name }}</div>
                <div class="text-[10px] text-ink-gray-4">{{ tier.requirement }}</div>
              </div>
              <div class="text-right">
                <div class="text-xs font-semibold text-ink-gray-8">{{ tier.count }} vendors</div>
                <div class="text-[10px] text-ink-gray-4">{{ tier.benefit }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Vendor Blacklist') }}</div>
          <div class="space-y-2 text-xs">
            <div v-for="item in blacklist" :key="item.vendor" class="rounded-lg border border-outline-gray-1 px-3 py-2">
              <div class="flex items-start justify-between">
                <div>
                  <div class="text-ink-gray-8 font-semibold">{{ item.vendor }}</div>
                  <div class="text-[10px] text-ink-gray-4">{{ item.reason }}</div>
                </div>
                <Badge :label="item.since" variant="subtle" theme="red" />
              </div>
              <div class="mt-1 text-[10px] text-ink-gray-4">Risk: {{ item.risk }} · Action: {{ item.action }}</div>
            </div>
          </div>
        </div>

        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Vendor Audit Trail') }}</div>
          <div class="space-y-2 text-xs">
            <div v-for="log in auditTrail" :key="log.id" class="flex items-start justify-between rounded-lg border border-outline-gray-1 px-3 py-2">
              <div>
                <div class="text-ink-gray-8 font-semibold">{{ log.event }}</div>
                <div class="text-[10px] text-ink-gray-4">{{ log.vendor }} · {{ log.user }}</div>
              </div>
              <div class="text-[10px] text-ink-gray-4">{{ log.time }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
        <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Vendor Analytics Overview') }}</div>
        <div class="grid grid-cols-3 gap-4 text-xs">
          <div>
            <div class="mb-2 text-ink-gray-5">Spend by Category</div>
            <div class="space-y-2">
              <div v-for="row in spendByCategory" :key="row.name" class="flex items-center gap-2">
                <span class="w-24 text-ink-gray-6">{{ row.name }}</span>
                <div class="flex-1 h-2 rounded-full bg-surface-gray-2 overflow-hidden">
                  <div class="h-2 rounded-full" :class="row.color" :style="{ width: row.pct + '%' }" />
                </div>
                <span class="w-10 text-right font-medium">{{ row.pct }}%</span>
              </div>
            </div>
          </div>
          <div>
            <div class="mb-2 text-ink-gray-5">SLA Compliance Trend</div>
            <div class="space-y-2">
              <div v-for="month in slaTrend" :key="month.label" class="flex items-center gap-2">
                <span class="w-10 text-ink-gray-6">{{ month.label }}</span>
                <div class="flex-1 h-2 rounded-full bg-surface-gray-2 overflow-hidden">
                  <div class="h-2 rounded-full bg-[#FF6600]" :style="{ width: month.value + '%' }" />
                </div>
                <span class="w-10 text-right font-medium">{{ month.value }}%</span>
              </div>
            </div>
          </div>
          <div>
            <div class="mb-2 text-ink-gray-5">Referral Partner Pipeline</div>
            <div class="space-y-2">
              <div v-for="ref in referralPipeline" :key="ref.stage" class="flex items-center justify-between rounded-lg border border-outline-gray-1 px-3 py-2">
                <div class="text-ink-gray-6">{{ ref.stage }}</div>
                <div class="text-ink-gray-8 font-semibold">{{ ref.count }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── PORTAL ── -->
    <div v-if="activeTab === 'portal'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
        <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Vendor Portal Adoption') }}</div>
        <div class="grid grid-cols-3 gap-4 text-xs">
          <div class="rounded-lg border border-outline-gray-1 p-3">
            <div class="text-ink-gray-5">Active Accounts</div>
            <div class="mt-1 text-2xl font-bold text-[#FF6600]">48</div>
            <div class="text-[10px] text-ink-gray-4">+6 activated this month</div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 p-3">
            <div class="text-ink-gray-5">Pending Invitations</div>
            <div class="mt-1 text-2xl font-bold text-amber-600">9</div>
            <div class="text-[10px] text-ink-gray-4">Awaiting KYC verification</div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 p-3">
            <div class="text-ink-gray-5">Portal Usage</div>
            <div class="mt-1 text-2xl font-bold text-[#006699]">72%</div>
            <div class="text-[10px] text-ink-gray-4">SLA updates via portal</div>
          </div>
        </div>
        <div class="mt-4 grid grid-cols-2 gap-4 text-xs">
          <div class="rounded-lg border border-outline-gray-1 p-3">
            <div class="mb-2 text-ink-gray-6">Recent Portal Activity</div>
            <div class="space-y-2">
              <div v-for="activity in portalActivity" :key="activity.id" class="flex items-center justify-between">
                <div>
                  <div class="text-ink-gray-8 font-semibold">{{ activity.vendor }}</div>
                  <div class="text-[10px] text-ink-gray-4">{{ activity.action }}</div>
                </div>
                <div class="text-[10px] text-ink-gray-4">{{ activity.time }}</div>
              </div>
            </div>
          </div>
          <div class="rounded-lg border border-outline-gray-1 p-3">
            <div class="mb-2 text-ink-gray-6">Portal Feature Usage</div>
            <div class="space-y-2">
              <div v-for="feature in portalUsage" :key="feature.name" class="flex items-center gap-2">
                <span class="w-32 text-ink-gray-6">{{ feature.name }}</span>
                <div class="flex-1 h-2 rounded-full bg-surface-gray-2 overflow-hidden">
                  <div class="h-2 rounded-full bg-[#006699]" :style="{ width: feature.pct + '%' }" />
                </div>
                <span class="w-10 text-right font-medium">{{ feature.pct }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── Vendor Profile Modal ── -->
  <div v-if="selectedVendor" class="fixed inset-0 z-40 flex items-end justify-center bg-black/40 p-4 sm:items-center">
    <div class="w-full max-w-3xl rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-start justify-between gap-2">
        <div>
          <div class="text-lg font-semibold text-ink-gray-9">{{ selectedVendor.name }}</div>
          <div class="text-xs text-ink-gray-5">
            {{ selectedVendor.category }} · {{ selectedVendor.tier }} · Owner {{ selectedVendor.owner }}
          </div>
        </div>
        <button class="text-ink-gray-4" @click="selectedVendor = null">✕</button>
      </div>

      <div class="grid grid-cols-3 gap-3 mb-4 text-xs">
        <div class="rounded-lg bg-surface-gray-1 p-3">
          <div class="text-ink-gray-4">SLA Compliance</div>
          <div class="mt-1 text-lg font-bold" :class="selectedVendor.slaCompliance >= 95 ? 'text-[#FF6600]' : 'text-amber-600'">
            {{ selectedVendor.slaCompliance }}%
          </div>
          <div class="text-ink-gray-4">Last breach: {{ selectedVendor.lastBreach }}</div>
        </div>
        <div class="rounded-lg bg-surface-gray-1 p-3">
          <div class="text-ink-gray-4">Performance Score</div>
          <div class="mt-1 text-lg font-bold" :class="scoreColor(selectedVendor.score)">{{ selectedVendor.score }}</div>
          <div class="text-ink-gray-4">Last review: {{ selectedVendor.lastReview }}</div>
        </div>
        <div class="rounded-lg bg-surface-gray-1 p-3">
          <div class="text-ink-gray-4">Contract</div>
          <div class="mt-1 text-sm font-semibold text-ink-gray-8">{{ selectedVendor.contractType }}</div>
          <div class="text-ink-gray-4">{{ selectedVendor.contractStart }} → {{ selectedVendor.contractEnd }}</div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 text-xs">
        <div>
          <div class="mb-2 text-ink-gray-6 font-semibold">Primary Contact</div>
          <div class="rounded-lg border border-outline-gray-1 p-3 space-y-1">
            <div class="text-ink-gray-8 font-medium">{{ selectedVendor.contact.name }}</div>
            <div class="text-ink-gray-4">{{ selectedVendor.contact.email }}</div>
            <div class="text-ink-gray-4">{{ selectedVendor.contact.phone }}</div>
          </div>
        </div>
        <div>
          <div class="mb-2 text-ink-gray-6 font-semibold">Services & Coverage</div>
          <div class="rounded-lg border border-outline-gray-1 p-3">
            <div class="flex flex-wrap gap-2">
              <span
                v-for="service in selectedVendor.services"
                :key="service"
                class="rounded-full bg-surface-gray-1 px-2 py-1 text-[10px] text-ink-gray-6"
              >
                {{ service }}
              </span>
            </div>
            <div class="mt-2 text-[10px] text-ink-gray-4">Coverage: {{ selectedVendor.coverage }}</div>
          </div>
        </div>
      </div>

      <div class="mt-4 grid grid-cols-3 gap-3 text-xs">
        <div class="rounded-lg border border-outline-gray-1 p-3">
          <div class="text-ink-gray-4">Invoice Status</div>
          <div class="mt-1 text-sm font-semibold text-ink-gray-8">{{ selectedVendor.invoiceOutstanding }}</div>
          <div class="text-[10px] text-ink-gray-4">{{ selectedVendor.invoiceNote }}</div>
        </div>
        <div class="rounded-lg border border-outline-gray-1 p-3">
          <div class="text-ink-gray-4">Compliance</div>
          <div class="mt-1 text-sm font-semibold text-ink-gray-8">{{ selectedVendor.complianceStatus }}</div>
          <div class="text-[10px] text-ink-gray-4">Next audit: {{ selectedVendor.nextAudit }}</div>
        </div>
        <div class="rounded-lg border border-outline-gray-1 p-3">
          <div class="text-ink-gray-4">Portal Access</div>
          <div class="mt-1 text-sm font-semibold text-ink-gray-8">{{ selectedVendor.portalStatus }}</div>
          <div class="text-[10px] text-ink-gray-4">Last login: {{ selectedVendor.portalLastLogin }}</div>
        </div>
      </div>

      <div class="mt-4 flex gap-2 flex-wrap">
        <Button :label="__('Send SLA Review')" variant="outline" size="sm" />
        <Button :label="__('Renew Contract')" variant="outline" size="sm" />
        <Button :label="__('Log Engagement')" variant="outline" size="sm" />
        <Button :label="__('Open Request')" variant="solid" size="sm" />
      </div>
    </div>
  </div>

  <!-- ── New Vendor Modal ── -->
  <div v-if="showVendorForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-2xl rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('New Vendor') }}</div>
        <button class="text-ink-gray-4" @click="closeVendorForm">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Vendor Name') }}</label>
          <input v-model="vendorForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="e.g. PT Nusantara Appraisal" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Category') }}</label>
            <select v-model="vendorForm.category" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="cat in ['Appraiser', 'Insurance Provider', 'Legal Counsel', 'Technology Vendor', 'Referral Partner']" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Tier') }}</label>
            <select v-model="vendorForm.tier" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="tier in ['Strategic', 'Platinum', 'Gold', 'Silver']" :key="tier" :value="tier">{{ tier }}</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Owner') }}</label>
            <input v-model="vendorForm.owner" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Ops Team" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Region') }}</label>
            <input v-model="vendorForm.region" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Jakarta / National" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Primary Contact') }}</label>
            <input v-model="vendorForm.contactName" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Contact name" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Email') }}</label>
            <input v-model="vendorForm.contactEmail" type="email" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="email@vendor.com" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Phone') }}</label>
            <input v-model="vendorForm.contactPhone" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="+62 8xx" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Risk Level') }}</label>
            <select v-model="vendorForm.risk" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="risk in ['Low', 'Medium', 'High']" :key="risk" :value="risk">{{ risk }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Services (comma-separated)') }}</label>
          <input v-model="vendorForm.services" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Appraisal, Site inspection" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Coverage') }}</label>
            <input v-model="vendorForm.coverage" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Java · Sumatra" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Status') }}</label>
            <select v-model="vendorForm.status" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="status in ['Onboarding', 'Active', 'Suspended']" :key="status" :value="status">{{ status }}</option>
            </select>
          </div>
        </div>
        <p v-if="vendorFormError" class="text-xs text-red-600">{{ vendorFormError }}</p>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="closeVendorForm" />
        <Button :label="__('Create Vendor')" variant="solid" @click="createVendor" />
      </div>
    </div>
  </div>

  <!-- ── Create Request Modal ── -->
  <div v-if="showRequestForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-xl rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Create Service Request') }}</div>
        <button class="text-ink-gray-4" @click="closeRequestForm">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Request Type') }}</label>
          <input v-model="requestForm.type" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="e.g. Collateral Appraisal" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Vendor') }}</label>
          <select v-model="requestForm.vendor" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option value="" disabled>Select vendor</option>
            <option v-for="vendor in vendorOptions" :key="vendor" :value="vendor">{{ vendor }}</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Requester') }}</label>
            <input v-model="requestForm.requester" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Ops Lending" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Owner') }}</label>
            <input v-model="requestForm.owner" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Assigned ops user" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Priority') }}</label>
            <select v-model="requestForm.priority" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="priority in ['Urgent', 'High', 'Normal']" :key="priority" :value="priority">{{ priority }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Status') }}</label>
            <select v-model="requestForm.status" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="status in ['Pending', 'Assigned', 'In Progress', 'Escalated', 'Completed']" :key="status" :value="status">{{ status }}</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('SLA Due') }}</label>
            <input v-model="requestForm.slaDue" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="e.g. 8h / 2 days" />
          </div>
          <div class="flex items-center gap-2 pt-6">
            <input id="slaBreached" v-model="requestForm.slaBreached" type="checkbox" class="h-4 w-4 rounded border-outline-gray-2" />
            <label for="slaBreached" class="text-xs text-ink-gray-5">{{ __('SLA breached') }}</label>
          </div>
        </div>
        <p v-if="requestFormError" class="text-xs text-red-600">{{ requestFormError }}</p>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="closeRequestForm" />
        <Button :label="__('Create Request')" variant="solid" @click="createRequest" />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Badge, Button, FeatherIcon, usePageMeta } from 'frappe-ui'
import { computed, ref } from 'vue'

usePageMeta(() => ({ title: __('Partner & Vendor Management') }))

const activeTab = ref('dashboard')
const showVendorForm = ref(false)
const showRequestForm = ref(false)
const showContractForm = ref(false)
const selectedVendor = ref(null)
const vendorFormError = ref('')
const requestFormError = ref('')

const vendorForm = ref({
  name: '',
  category: 'Appraiser',
  tier: 'Silver',
  owner: 'Ops Lending',
  region: 'Jakarta',
  risk: 'Low',
  contactName: '',
  contactEmail: '',
  contactPhone: '',
  services: '',
  coverage: 'Java · Sumatra',
  status: 'Onboarding',
})

const requestForm = ref({
  type: '',
  vendor: '',
  requester: 'Ops Lending',
  owner: 'Ops Team',
  priority: 'Normal',
  status: 'Pending',
  slaDue: '8h',
  slaBreached: false,
})

const pageTabs = computed(() => [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'directory', label: 'Vendor Directory', badge: vendors.value.length },
  { key: 'onboarding', label: 'Onboarding', badge: onboardingList.value.length },
  { key: 'requests', label: 'Service Requests', badge: requests.value.length },
  { key: 'sla', label: 'SLA & Contracts' },
  { key: 'performance', label: 'Performance & Compliance' },
  { key: 'portal', label: 'Vendor Portal' },
])

const dashKpis = [
  {
    label: 'Total Vendors',
    value: '62',
    delta: '+4 new this quarter',
    icon: 'users',
    iconColor: 'text-[#006699]',
  },
  {
    label: 'Active Contracts',
    value: '47',
    delta: '8 renewals due',
    icon: 'file-text',
    iconColor: 'text-[#FF6600]',
  },
  {
    label: 'SLA Compliance',
    value: '93%',
    delta: '↓ 2% vs last month',
    icon: 'clock',
    iconColor: 'text-amber-500',
    valueColor: 'text-amber-600',
  },
  {
    label: 'Open Requests',
    value: '18',
    delta: '5 high priority',
    icon: 'activity',
    iconColor: 'text-indigo-500',
  },
  {
    label: 'Compliance Flags',
    value: '6',
    delta: '2 critical',
    icon: 'shield',
    iconColor: 'text-red-500',
    valueColor: 'text-red-600',
  },
  {
    label: 'Portal Adoption',
    value: '72%',
    delta: '48 active users',
    icon: 'external-link',
    iconColor: 'text-teal-500',
  },
]

const slaOverview = [
  { category: 'Appraiser', compliance: 96, breaches: 2, color: 'bg-[#FF6600]', textColor: 'text-[#FF6600]' },
  { category: 'Insurance Provider', compliance: 92, breaches: 5, color: 'bg-amber-500', textColor: 'text-amber-600' },
  { category: 'Legal Counsel', compliance: 94, breaches: 3, color: 'bg-[#006699]', textColor: 'text-[#006699]' },
  { category: 'Technology Vendor', compliance: 89, breaches: 7, color: 'bg-orange-500', textColor: 'text-orange-600' },
  { category: 'Referral Partner', compliance: 98, breaches: 1, color: 'bg-[#CC5200]', textColor: 'text-[#FF6600]' },
]
const slaOverviewLabel = '93% overall'

const alerts = [
  {
    id: 'ALT-001',
    title: 'SLA breach — PT Nusantara Appraisal',
    detail: '4 cases overdue > 48 hours',
    severity: 'Critical',
    time: '2h ago',
  },
  {
    id: 'ALT-002',
    title: 'Compliance renewal overdue — Garuda Insurance',
    detail: 'License expiry in 10 days',
    severity: 'High',
    time: 'Today',
  },
  {
    id: 'ALT-003',
    title: 'Invoice mismatch — Lex & Co Legal',
    detail: 'Rp 320M variance detected',
    severity: 'Medium',
    time: 'Yesterday',
  },
]

const topPartners = [
  { name: 'Garuda Insurance Tbk', category: 'Insurance Provider', tier: 'Platinum', score: 92 },
  { name: 'Kredivo Tech Services', category: 'Technology Vendor', tier: 'Strategic', score: 90 },
  { name: 'PT Nusantara Appraisal', category: 'Appraiser', tier: 'Gold', score: 88 },
]

const activeRequests = ref([
  {
    id: 'REQ-1042',
    type: 'Collateral Appraisal',
    vendor: 'PT Nusantara Appraisal',
    requester: 'Ops Lending',
    slaDue: '6h',
    status: 'In Progress',
    slaBreached: false,
    icon: 'map',
  },
  {
    id: 'REQ-1043',
    type: 'Insurance Verification',
    vendor: 'Garuda Insurance Tbk',
    requester: 'Ops Risk',
    slaDue: 'Overdue 3h',
    status: 'Escalated',
    slaBreached: true,
    icon: 'shield',
  },
  {
    id: 'REQ-1044',
    type: 'Legal Review',
    vendor: 'Lex & Co Legal',
    requester: 'Credit Admin',
    slaDue: '12h',
    status: 'Assigned',
    slaBreached: false,
    icon: 'file-text',
  },
])

const upcomingRenewals = [
  { vendor: 'Lex & Co Legal', type: 'Legal Retainer', owner: 'Ops Legal', renewal: '14 days', urgency: 'High' },
  { vendor: 'Nimbus Cloud', type: 'Cloud Services', owner: 'IT Ops', renewal: '21 days', urgency: 'Medium' },
  { vendor: 'Sakura Surveyors', type: 'Appraisal Contract', owner: 'Ops Lending', renewal: '30 days', urgency: 'Medium' },
]

const vendors = ref([
  {
    id: 'V-001',
    name: 'PT Nusantara Appraisal',
    category: 'Appraiser',
    tier: 'Gold',
    status: 'Active',
    owner: 'Ops Lending',
    region: 'Jakarta',
    risk: 'Low',
    score: 88,
    slaCompliance: 96,
    lastBreach: 'Mar 12, 2026',
    contractType: 'Master Appraisal Agreement',
    contractStart: 'Apr 01, 2025',
    contractEnd: 'Mar 31, 2026',
    lastReview: 'Mar 2026',
    contact: { name: 'Anita Pramudita', email: 'anita@nusantara.co.id', phone: '+62 812 4481 0021' },
    services: ['Collateral Valuation', 'Site Inspection', 'Market Pricing'],
    coverage: 'Java · Sumatra',
    invoiceOutstanding: 'Rp 180,000,000 outstanding',
    invoiceNote: '2 invoices overdue',
    complianceStatus: 'Compliant',
    nextAudit: 'Jun 2026',
    portalStatus: 'Active',
    portalLastLogin: '2 days ago',
  },
  {
    id: 'V-002',
    name: 'Garuda Insurance Tbk',
    category: 'Insurance Provider',
    tier: 'Platinum',
    status: 'Active',
    owner: 'Ops Risk',
    region: 'National',
    risk: 'Medium',
    score: 92,
    slaCompliance: 92,
    lastBreach: 'Apr 02, 2026',
    contractType: 'Insurance Framework',
    contractStart: 'Jan 01, 2025',
    contractEnd: 'Dec 31, 2026',
    lastReview: 'Apr 2026',
    contact: { name: 'Rizky Aditya', email: 'rizky@garudainsurance.co.id', phone: '+62 813 7766 4411' },
    services: ['Credit Life Insurance', 'Collateral Coverage'],
    coverage: 'National',
    invoiceOutstanding: 'Rp 0 outstanding',
    invoiceNote: 'All invoices paid',
    complianceStatus: 'Due - License Renewal',
    nextAudit: 'May 2026',
    portalStatus: 'Active',
    portalLastLogin: 'Today',
  },
  {
    id: 'V-003',
    name: 'Lex & Co Legal Partners',
    category: 'Legal Counsel',
    tier: 'Gold',
    status: 'Active',
    owner: 'Ops Legal',
    region: 'Jakarta',
    risk: 'Medium',
    score: 85,
    slaCompliance: 94,
    lastBreach: 'Feb 18, 2026',
    contractType: 'Legal Retainer',
    contractStart: 'Jul 01, 2024',
    contractEnd: 'Jun 30, 2026',
    lastReview: 'Feb 2026',
    contact: { name: 'Dimas Wicaksono', email: 'dimas@lexco.id', phone: '+62 811 3377 9898' },
    services: ['Credit Agreement', 'Collateral Registration'],
    coverage: 'Java · Kalimantan',
    invoiceOutstanding: 'Rp 320,000,000 under review',
    invoiceNote: 'Billing variance flagged',
    complianceStatus: 'Compliant',
    nextAudit: 'Aug 2026',
    portalStatus: 'Invited',
    portalLastLogin: '—',
  },
  {
    id: 'V-004',
    name: 'Kredivo Tech Services',
    category: 'Technology Vendor',
    tier: 'Strategic',
    status: 'Active',
    owner: 'IT Ops',
    region: 'National',
    risk: 'Low',
    score: 90,
    slaCompliance: 89,
    lastBreach: 'Apr 10, 2026',
    contractType: 'Platform Integration',
    contractStart: 'Jan 15, 2025',
    contractEnd: 'Jan 14, 2027',
    lastReview: 'Apr 2026',
    contact: { name: 'Maya Siregar', email: 'maya@kredivotech.id', phone: '+62 812 3012 9900' },
    services: ['API Integration', 'Workflow Automation', 'Monitoring'],
    coverage: 'National',
    invoiceOutstanding: 'Rp 90,000,000 outstanding',
    invoiceNote: 'Awaiting PO confirmation',
    complianceStatus: 'Compliant',
    nextAudit: 'Oct 2026',
    portalStatus: 'Active',
    portalLastLogin: 'Yesterday',
  },
  {
    id: 'V-005',
    name: 'Sakura Surveyors',
    category: 'Appraiser',
    tier: 'Silver',
    status: 'Onboarding',
    owner: 'Ops Lending',
    region: 'Sulawesi',
    risk: 'Medium',
    score: 74,
    slaCompliance: 0,
    lastBreach: '—',
    contractType: 'Draft Agreement',
    contractStart: '—',
    contractEnd: '—',
    lastReview: '—',
    contact: { name: 'Rahmat Budi', email: 'rahmat@sakura.co.id', phone: '+62 812 4412 3088' },
    services: ['Field Survey', 'Collateral Check'],
    coverage: 'Sulawesi',
    invoiceOutstanding: '—',
    invoiceNote: 'Awaiting onboarding',
    complianceStatus: 'KYC in progress',
    nextAudit: '—',
    portalStatus: 'Invited',
    portalLastLogin: '—',
  },
  {
    id: 'V-006',
    name: 'BNI Referral Network',
    category: 'Referral Partner',
    tier: 'Gold',
    status: 'Active',
    owner: 'Ops Growth',
    region: 'National',
    risk: 'Low',
    score: 82,
    slaCompliance: 98,
    lastBreach: 'Jan 05, 2026',
    contractType: 'Referral Partnership',
    contractStart: 'Sep 01, 2024',
    contractEnd: 'Aug 31, 2026',
    lastReview: 'Mar 2026',
    contact: { name: 'Nadia Firda', email: 'nadia@bni.co.id', phone: '+62 812 4455 3322' },
    services: ['Lead Referrals', 'Co-marketing'],
    coverage: 'National',
    invoiceOutstanding: 'Rp 0 outstanding',
    invoiceNote: 'Revenue share settled',
    complianceStatus: 'Compliant',
    nextAudit: 'Dec 2026',
    portalStatus: 'Active',
    portalLastLogin: '3 days ago',
  },
])

const vendorSearch = ref('')
const vendorCategory = ref('')
const vendorTier = ref('')
const vendorStatus = ref('')

const vendorCategories = computed(() => Array.from(new Set(vendors.value.map((v) => v.category))))
const vendorTiers = computed(() => Array.from(new Set(vendors.value.map((v) => v.tier))))
const vendorStatuses = computed(() => Array.from(new Set(vendors.value.map((v) => v.status))))
const vendorOptions = computed(() => vendors.value.map((v) => v.name))

const filteredVendors = computed(() =>
  vendors.value.filter((v) => {
    const matchesSearch =
      !vendorSearch.value ||
      [v.name, v.category, v.owner, v.region, ...v.services]
        .join(' ')
        .toLowerCase()
        .includes(vendorSearch.value.toLowerCase())
    const matchesCategory = !vendorCategory.value || v.category === vendorCategory.value
    const matchesTier = !vendorTier.value || v.tier === vendorTier.value
    const matchesStatus = !vendorStatus.value || v.status === vendorStatus.value
    return matchesSearch && matchesCategory && matchesTier && matchesStatus
  })
)

const onboardingStages = [
  { label: 'Pre-screen', count: 4, desc: 'Vendor intake & pre-qualify', color: 'bg-[#FF6600]', lineColor: 'bg-[#FFD9B3]' },
  { label: 'Due Diligence', count: 6, desc: 'KYC, compliance, checks', color: 'bg-[#006699]', lineColor: 'bg-[#B3D9F0]' },
  { label: 'Contracting', count: 3, desc: 'Negotiation & legal review', color: 'bg-amber-500', lineColor: 'bg-amber-200' },
  { label: 'Integration', count: 2, desc: 'Portal & workflow setup', color: 'bg-indigo-500', lineColor: 'bg-indigo-200' },
  { label: 'Activated', count: 8, desc: 'Ready for engagement', color: 'bg-[#CC5200]', lineColor: 'bg-[#FFD9B3]' },
]

const onboardingList = ref([
  { id: 'ONB-221', vendor: 'Sakura Surveyors', stage: 'Due Diligence', owner: 'Ops Lending', slaDue: '3 days', missingDocs: 'Tax clearance, ISO cert', slaBreached: false },
  { id: 'ONB-222', vendor: 'Nimbus Cloud', stage: 'Contracting', owner: 'IT Ops', slaDue: 'Overdue 2 days', missingDocs: 'MSA signature', slaBreached: true },
  { id: 'ONB-223', vendor: 'Sumatra Legal Advisory', stage: 'Pre-screen', owner: 'Ops Legal', slaDue: '5 days', missingDocs: 'Company profile', slaBreached: false },
])

const requests = ref([
  { id: 'REQ-1042', caseId: 'REQ-1042', type: 'Collateral Appraisal', vendor: 'PT Nusantara Appraisal', requester: 'Ops Lending', slaDue: '6h', priority: 'High', status: 'In Progress', owner: 'Fina (Ops)', slaBreached: false },
  { id: 'REQ-1043', caseId: 'REQ-1043', type: 'Insurance Verification', vendor: 'Garuda Insurance Tbk', requester: 'Ops Risk', slaDue: 'Overdue 3h', priority: 'Urgent', status: 'Escalated', owner: 'Ardi (Risk)', slaBreached: true },
  { id: 'REQ-1044', caseId: 'REQ-1044', type: 'Legal Review', vendor: 'Lex & Co Legal', requester: 'Credit Admin', slaDue: '12h', priority: 'High', status: 'Assigned', owner: 'Doni (Legal)', slaBreached: false },
  { id: 'REQ-1045', caseId: 'REQ-1045', type: 'API Integration Support', vendor: 'Kredivo Tech Services', requester: 'IT Ops', slaDue: '1 day', priority: 'Normal', status: 'Pending', owner: 'Mira (IT)', slaBreached: false },
  { id: 'REQ-1046', caseId: 'REQ-1046', type: 'Referral Lead Validation', vendor: 'BNI Referral Network', requester: 'Ops Growth', slaDue: '8h', priority: 'Normal', status: 'In Progress', owner: 'Aulia (Growth)', slaBreached: false },
])

const slaTracking = [
  { vendor: 'PT Nusantara Appraisal', response: '≤ 2h', resolution: '≤ 48h', compliance: 96, lastBreach: 'Mar 12, 2026', nextReview: 'Jun 2026' },
  { vendor: 'Garuda Insurance Tbk', response: '≤ 4h', resolution: '≤ 24h', compliance: 92, lastBreach: 'Apr 02, 2026', nextReview: 'May 2026' },
  { vendor: 'Lex & Co Legal', response: '≤ 8h', resolution: '≤ 72h', compliance: 94, lastBreach: 'Feb 18, 2026', nextReview: 'Aug 2026' },
  { vendor: 'Kredivo Tech Services', response: '≤ 1h', resolution: '≤ 12h', compliance: 89, lastBreach: 'Apr 10, 2026', nextReview: 'Jul 2026' },
]

const contracts = [
  { id: 'CTR-201', vendor: 'Garuda Insurance Tbk', type: 'Insurance Framework', term: '2 years', start: 'Jan 2025', end: 'Dec 2026', value: 'Rp 14.2B', status: 'Active' },
  { id: 'CTR-202', vendor: 'Lex & Co Legal', type: 'Legal Retainer', term: '2 years', start: 'Jul 2024', end: 'Jun 2026', value: 'Rp 4.5B', status: 'Renewal' },
  { id: 'CTR-203', vendor: 'Nimbus Cloud', type: 'Cloud Services', term: '1 year', start: 'Jun 2025', end: 'May 2026', value: 'Rp 3.2B', status: 'Pending' },
]

const invoices = [
  { id: 'INV-5501', vendor: 'PT Nusantara Appraisal', number: 'INV-5501', amount: 'Rp 120,000,000', due: 'May 30', status: 'Overdue' },
  { id: 'INV-5502', vendor: 'Kredivo Tech Services', number: 'INV-5502', amount: 'Rp 90,000,000', due: 'Jun 04', status: 'Processing' },
  { id: 'INV-5503', vendor: 'Garuda Insurance Tbk', number: 'INV-5503', amount: 'Rp 240,000,000', due: 'Jun 10', status: 'Paid' },
]

const performanceScores = [
  { vendor: 'Garuda Insurance Tbk', score: 92, trend: 3, review: 'Apr 2026', reviewer: 'Risk Ops', tier: 'Platinum', status: 'Reviewed' },
  { vendor: 'Kredivo Tech Services', score: 90, trend: 1, review: 'Apr 2026', reviewer: 'IT Ops', tier: 'Strategic', status: 'Reviewed' },
  { vendor: 'PT Nusantara Appraisal', score: 88, trend: -2, review: 'Mar 2026', reviewer: 'Ops Lending', tier: 'Gold', status: 'Action Plan' },
  { vendor: 'Lex & Co Legal', score: 85, trend: 0, review: 'Feb 2026', reviewer: 'Ops Legal', tier: 'Gold', status: 'Reviewed' },
]

const complianceChecks = [
  { id: 'CMP-01', vendor: 'Garuda Insurance Tbk', type: 'License Renewal', status: 'Due', due: 'May 30', owner: 'Risk Ops' },
  { id: 'CMP-02', vendor: 'Kredivo Tech Services', type: 'SOC2 Evidence', status: 'Passed', due: 'Apr 18', owner: 'IT Ops' },
  { id: 'CMP-03', vendor: 'Lex & Co Legal', type: 'Conflict Check', status: 'Passed', due: 'Mar 02', owner: 'Ops Legal' },
  { id: 'CMP-04', vendor: 'Sakura Surveyors', type: 'KYC Verification', status: 'Failed', due: 'Apr 28', owner: 'Ops Lending' },
]

const tierProgram = [
  { name: 'Platinum', requirement: 'Score ≥ 90 & SLA ≥ 95%', count: 6, benefit: 'Priority allocation' },
  { name: 'Gold', requirement: 'Score ≥ 80 & SLA ≥ 90%', count: 14, benefit: 'Preferred vendor' },
  { name: 'Silver', requirement: 'Score ≥ 70', count: 19, benefit: 'Standard allocation' },
]

const blacklist = [
  { vendor: 'PT Cakra Survey', reason: 'Repeated SLA breach & fraud flag', since: 'Feb 2026', risk: 'High', action: 'Contract terminated' },
  { vendor: 'Sentosa Legal', reason: 'Compliance violation', since: 'Jan 2026', risk: 'High', action: 'Blacklisted 12 months' },
]

const auditTrail = [
  { id: 'AUD-01', vendor: 'Garuda Insurance Tbk', event: 'SLA penalty applied', user: 'Ops Risk', time: '2h ago' },
  { id: 'AUD-02', vendor: 'Lex & Co Legal', event: 'Contract renewed', user: 'Ops Legal', time: 'Yesterday' },
  { id: 'AUD-03', vendor: 'Kredivo Tech Services', event: 'Performance review submitted', user: 'IT Ops', time: 'Apr 18' },
]

const spendByCategory = [
  { name: 'Insurance', pct: 32, color: 'bg-[#006699]' },
  { name: 'Appraisal', pct: 24, color: 'bg-[#FF6600]' },
  { name: 'Technology', pct: 28, color: 'bg-indigo-500' },
  { name: 'Legal', pct: 16, color: 'bg-amber-500' },
]

const slaTrend = [
  { label: 'Jan', value: 91 },
  { label: 'Feb', value: 93 },
  { label: 'Mar', value: 94 },
  { label: 'Apr', value: 92 },
  { label: 'May', value: 93 },
]

const referralPipeline = [
  { stage: 'Leads Received', count: 42 },
  { stage: 'Qualified', count: 27 },
  { stage: 'Converted', count: 12 },
  { stage: 'Active Facilities', count: 7 },
]

const portalActivity = [
  { id: 'PA-01', vendor: 'Garuda Insurance Tbk', action: 'Updated SLA response report', time: '1h ago' },
  { id: 'PA-02', vendor: 'PT Nusantara Appraisal', action: 'Uploaded appraisal report', time: '4h ago' },
  { id: 'PA-03', vendor: 'BNI Referral Network', action: 'Submitted new lead pack', time: 'Yesterday' },
]

const portalUsage = [
  { name: 'SLA Updates', pct: 76 },
  { name: 'Document Upload', pct: 68 },
  { name: 'Invoice Submission', pct: 54 },
  { name: 'Performance Review', pct: 41 },
]

function openVendorProfile(vendor) {
  selectedVendor.value = vendor
}

function resetVendorForm() {
  vendorForm.value = {
    name: '',
    category: 'Appraiser',
    tier: 'Silver',
    owner: 'Ops Lending',
    region: 'Jakarta',
    risk: 'Low',
    contactName: '',
    contactEmail: '',
    contactPhone: '',
    services: '',
    coverage: 'Java · Sumatra',
    status: 'Onboarding',
  }
  vendorFormError.value = ''
}

function resetRequestForm() {
  requestForm.value = {
    type: '',
    vendor: vendorOptions.value[0] || '',
    requester: 'Ops Lending',
    owner: 'Ops Team',
    priority: 'Normal',
    status: 'Pending',
    slaDue: '8h',
    slaBreached: false,
  }
  requestFormError.value = ''
}

function openVendorForm() {
  resetVendorForm()
  showVendorForm.value = true
}

function openRequestForm() {
  resetRequestForm()
  showRequestForm.value = true
}

function closeVendorForm() {
  showVendorForm.value = false
  resetVendorForm()
}

function closeRequestForm() {
  showRequestForm.value = false
  resetRequestForm()
}

function createVendor() {
  if (!vendorForm.value.name.trim()) {
    vendorFormError.value = 'Vendor name is required.'
    return
  }

  const idSuffix = String(Date.now()).slice(-4)
  const services = vendorForm.value.services
    ? vendorForm.value.services.split(',').map((s) => s.trim()).filter(Boolean)
    : []

  const newVendor = {
    id: `V-${idSuffix}`,
    name: vendorForm.value.name.trim(),
    category: vendorForm.value.category,
    tier: vendorForm.value.tier,
    status: vendorForm.value.status,
    owner: vendorForm.value.owner.trim() || 'Ops Team',
    region: vendorForm.value.region.trim() || 'National',
    risk: vendorForm.value.risk,
    score: 0,
    slaCompliance: 0,
    lastBreach: '—',
    contractType: 'Draft Agreement',
    contractStart: '—',
    contractEnd: '—',
    lastReview: '—',
    contact: {
      name: vendorForm.value.contactName.trim() || 'Pending',
      email: vendorForm.value.contactEmail.trim() || '—',
      phone: vendorForm.value.contactPhone.trim() || '—',
    },
    services: services.length ? services : ['Service scope pending'],
    coverage: vendorForm.value.coverage.trim() || 'National',
    invoiceOutstanding: '—',
    invoiceNote: 'Awaiting onboarding',
    complianceStatus: 'KYC in progress',
    nextAudit: '—',
    portalStatus: 'Invited',
    portalLastLogin: '—',
  }

  vendors.value.unshift(newVendor)
  onboardingList.value.unshift({
    id: `ONB-${idSuffix}`,
    vendor: newVendor.name,
    stage: 'Pre-screen',
    owner: newVendor.owner,
    slaDue: '5 days',
    missingDocs: 'Company profile',
    slaBreached: false,
  })
  showVendorForm.value = false
  resetVendorForm()
  activeTab.value = 'directory'
  selectedVendor.value = newVendor
}

function createRequest() {
  if (!requestForm.value.type.trim() || !requestForm.value.vendor) {
    requestFormError.value = 'Request type and vendor are required.'
    return
  }

  const idSuffix = String(Date.now()).slice(-4)
  const request = {
    id: `REQ-${idSuffix}`,
    caseId: `REQ-${idSuffix}`,
    type: requestForm.value.type.trim(),
    vendor: requestForm.value.vendor,
    requester: requestForm.value.requester.trim() || 'Ops Team',
    slaDue: requestForm.value.slaDue.trim() || '8h',
    priority: requestForm.value.priority,
    status: requestForm.value.status,
    owner: requestForm.value.owner.trim() || 'Ops Team',
    slaBreached: requestForm.value.slaBreached,
  }

  requests.value.unshift(request)
  activeRequests.value.unshift({
    id: request.id,
    type: request.type,
    vendor: request.vendor,
    requester: request.requester,
    slaDue: request.slaDue,
    status: request.status,
    slaBreached: request.slaBreached,
    icon: 'activity',
  })
  showRequestForm.value = false
  resetRequestForm()
  activeTab.value = 'requests'
}

function scoreColor(score) {
  if (score >= 90) return 'text-[#FF6600]'
  if (score >= 80) return 'text-amber-600'
  return 'text-red-600'
}

function riskTheme(risk) {
  if (risk === 'High') return 'red'
  if (risk === 'Medium') return 'orange'
  return 'green'
}

function statusTheme(status) {
  if (status === 'Active' || status === 'Completed') return 'green'
  if (status === 'Onboarding' || status === 'Assigned' || status === 'Pending') return 'orange'
  if (status === 'Escalated' || status === 'Suspended') return 'red'
  return 'blue'
}

function alertBadge(severity) {
  if (severity === 'Critical') return 'rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-semibold text-red-700'
  if (severity === 'High') return 'rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-700'
  return 'rounded-full bg-surface-gray-1 px-2 py-0.5 text-[10px] font-semibold text-ink-gray-5'
}
</script>
