<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #ef4444, #f97316)"
          >
            <FeatherIcon name="repeat" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Collections') }}
            </h1>
            <p class="truncate text-xs text-crm-muted">
              {{ __('Delinquency Management & Recovery') }}
            </p>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button :label="__('Record PTP')" variant="solid" @click="openPtpForm(null)" />
          <Button :label="__('Log Payment')" variant="outline" @click="openPaymentForm(null)" />
          <Button :label="__('Legal Escalation')" variant="outline" theme="red" @click="showLegalModal = true" />
        </div>
      </template>
    </LayoutHeader>

    <!-- Page tabs -->
    <div class="flex items-center gap-1 border-b border-crm-border bg-white px-4">
      <button
        v-for="tab in pageTabs"
        :key="tab.key"
        class="flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium transition-colors"
        :class="activeTab === tab.key ? 'border-b-2 border-red-500 text-red-600' : 'text-ink-gray-5 hover:text-ink-gray-8'"
        @click="activeTab = tab.key"
      >
        {{ __(tab.label) }}
        <span
          v-if="tab.badge"
          class="rounded-full bg-red-500 px-1.5 text-[10px] text-white"
        >{{ tab.badge }}</span>
      </button>
    </div>

    <!-- ── DASHBOARD TAB ── -->
    <div v-if="activeTab === 'dashboard'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <!-- KPI Row -->
      <div class="grid grid-cols-5 gap-3">
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
        <!-- Aging Bucket Chart -->
        <div class="col-span-2 rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Aging Bucket Overview') }}</div>
            <div class="flex gap-2 text-xs">
              <button
                v-for="m in ['Count', 'Amount']"
                :key="m"
                class="rounded-md px-2 py-1"
                :class="agingMetric === m ? 'bg-red-500 text-white' : 'bg-surface-gray-2 text-ink-gray-5'"
                @click="agingMetric = m"
              >
                {{ __(m) }}
              </button>
            </div>
          </div>
          <div class="space-y-3">
            <div
              v-for="bucket in agingBuckets"
              :key="bucket.label"
              class="flex cursor-pointer items-center gap-3 rounded-lg p-2 transition-colors hover:bg-surface-gray-1"
              @click="drillToBucket(bucket)"
            >
              <div class="w-28 text-xs font-medium" :class="bucket.textColor">{{ bucket.label }}</div>
              <div class="flex-1">
                <div class="h-6 overflow-hidden rounded-md bg-surface-gray-2">
                  <div
                    class="flex h-6 items-center justify-end pr-2 text-[10px] text-white font-medium transition-all duration-500 rounded-md"
                    :class="bucket.color"
                    :style="{ width: agingMetric === 'Count' ? bucket.countPct + '%' : bucket.amountPct + '%' }"
                  >
                    {{ agingMetric === 'Count' ? bucket.count : bucket.amountDisplay }}
                  </div>
                </div>
              </div>
              <div class="w-20 text-right text-xs text-ink-gray-5">
                {{ agingMetric === 'Count' ? bucket.count + ' accts' : bucket.amountDisplay }}
              </div>
              <FeatherIcon name="chevron-right" class="h-3 w-3 text-ink-gray-3" />
            </div>
          </div>
        </div>

        <!-- AI Prioritization -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center gap-2">
            <FeatherIcon name="zap" class="h-4 w-4 text-amber-500" />
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('AI Priority Queue') }}</div>
          </div>
          <div class="mb-2 text-[11px] text-ink-gray-4">
            {{ __('Ranked by recovery probability — refreshed daily') }}
          </div>
          <div class="space-y-2">
            <div
              v-for="(acct, idx) in aiPriorityList"
              :key="acct.id"
              class="flex cursor-pointer items-center gap-2 rounded-lg border border-outline-gray-1 p-2 hover:bg-surface-gray-1"
              @click="openAccountDetail(acct)"
            >
              <div
                class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
                :class="idx === 0 ? 'bg-red-500' : idx === 1 ? 'bg-orange-500' : 'bg-amber-500'"
              >
                {{ idx + 1 }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="truncate text-xs font-medium text-ink-gray-8">{{ acct.customer }}</div>
                <div class="text-[10px] text-ink-gray-4">DPD {{ acct.dpd }} · {{ acct.outstanding }}</div>
              </div>
              <div class="text-right">
                <div class="text-xs font-semibold" :class="acct.score >= 70 ? 'text-green-600' : acct.score >= 40 ? 'text-amber-600' : 'text-red-600'">
                  {{ acct.score }}%
                </div>
                <div class="text-[10px] text-ink-gray-4">{{ __('recovery') }}</div>
              </div>
            </div>
          </div>
          <Button class="mt-3 w-full" :label="__('View Full AI List')" variant="subtle" size="sm" @click="activeTab = 'delinquency'" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <!-- Top Defaulters -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Top Defaulters') }}</div>
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="pb-2 text-left font-medium">{{ __('Customer') }}</th>
                <th class="pb-2 text-right font-medium">{{ __('Outstanding') }}</th>
                <th class="pb-2 text-right font-medium">{{ __('DPD') }}</th>
                <th class="pb-2 text-right font-medium">{{ __('Status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="d in topDefaulters"
                :key="d.id"
                class="cursor-pointer border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
                @click="openAccountDetail(d)"
              >
                <td class="py-2 font-medium text-ink-gray-8">{{ d.customer }}</td>
                <td class="py-2 text-right text-red-600 font-semibold">{{ d.outstanding }}</td>
                <td class="py-2 text-right">
                  <span class="rounded-full px-2 py-0.5 font-medium" :class="dpdClass(d.dpd)">{{ d.dpd }}d</span>
                </td>
                <td class="py-2 text-right">
                  <Badge :label="d.status" variant="subtle" :theme="d.status === 'Legal' ? 'red' : d.status === 'PTP' ? 'orange' : 'gray'" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Officer Leaderboard -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Officer Leaderboard') }}</div>
          <div class="space-y-2">
            <div
              v-for="(officer, idx) in officerLeaderboard"
              :key="officer.name"
              class="flex items-center gap-3 rounded-lg p-2 hover:bg-surface-gray-1"
            >
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold"
                :class="idx === 0 ? 'bg-amber-100 text-amber-700' : idx === 1 ? 'bg-gray-100 text-gray-600' : idx === 2 ? 'bg-orange-100 text-orange-600' : 'bg-surface-gray-2 text-ink-gray-5'"
              >
                {{ idx + 1 }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-xs font-medium text-ink-gray-8">{{ officer.name }}</div>
                <div class="mt-0.5 h-1.5 w-full overflow-hidden rounded-full bg-surface-gray-2">
                  <div class="h-1.5 rounded-full bg-green-500" :style="{ width: officer.pct + '%' }" />
                </div>
              </div>
              <div class="text-right text-xs">
                <div class="font-semibold text-green-600">{{ officer.recovered }}</div>
                <div class="text-ink-gray-4">{{ officer.ptpKept }}% PTP</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── DELINQUENCY LIST TAB ── -->
    <div v-if="activeTab === 'delinquency'" class="flex min-h-0 flex-1 flex-col gap-3 bg-surface-gray-1 p-4">
      <!-- Filter bar -->
      <div class="flex flex-wrap items-center gap-2 rounded-[14px] border border-crm-border bg-white px-4 py-3 shadow-sm">
        <input
          v-model="listSearch"
          class="h-8 rounded-md border border-outline-gray-2 px-3 text-sm"
          style="width: 200px"
          placeholder="Search customer..."
        />
        <select v-model="filterBucket" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">All Buckets</option>
          <option v-for="b in agingBuckets" :key="b.label" :value="b.label">{{ b.label }}</option>
        </select>
        <select v-model="filterProduct" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">All Products</option>
          <option v-for="p in products" :key="p" :value="p">{{ p }}</option>
        </select>
        <select v-model="filterOfficer" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">All Officers</option>
          <option v-for="o in officers" :key="o" :value="o">{{ o }}</option>
        </select>
        <select v-model="sortField" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="dpd">Sort: DPD</option>
          <option value="outstanding">Sort: Outstanding</option>
          <option value="aiScore">Sort: AI Score</option>
          <option value="lastAction">Sort: Last Action</option>
        </select>
        <div class="ml-auto text-xs text-ink-gray-4">{{ filteredAccounts.length }} accounts</div>
      </div>

      <!-- Accounts table -->
      <div class="flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <div class="overflow-y-auto h-full">
          <table class="w-full text-xs">
            <thead class="sticky top-0 bg-surface-gray-1">
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Customer') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Product') }}</th>
                <th class="px-4 py-2.5 text-right font-medium">{{ __('Outstanding') }}</th>
                <th class="px-4 py-2.5 text-right font-medium">{{ __('DPD') }}</th>
                <th class="px-4 py-2.5 text-right font-medium">{{ __('AI Score') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('PTP Date') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Last Action') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Officer') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Status') }}</th>
                <th class="px-4 py-2.5 text-center font-medium">{{ __('Actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="acct in filteredAccounts"
                :key="acct.id"
                class="cursor-pointer border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
                @click="openAccountDetail(acct)"
              >
                <td class="px-4 py-2.5 font-medium text-ink-gray-8">{{ acct.customer }}</td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ acct.product }}</td>
                <td class="px-4 py-2.5 text-right font-semibold text-red-600">{{ acct.outstanding }}</td>
                <td class="px-4 py-2.5 text-right">
                  <span class="rounded-full px-2 py-0.5 font-medium" :class="dpdClass(acct.dpd)">{{ acct.dpd }}</span>
                </td>
                <td class="px-4 py-2.5 text-right">
                  <span class="font-semibold" :class="acct.aiScore >= 70 ? 'text-green-600' : acct.aiScore >= 40 ? 'text-amber-600' : 'text-red-600'">
                    {{ acct.aiScore }}%
                  </span>
                </td>
                <td class="px-4 py-2.5" :class="isPtpBreached(acct.ptpDate) ? 'text-red-500 font-medium' : 'text-ink-gray-6'">
                  {{ acct.ptpDate || '—' }}
                </td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ acct.lastAction }}</td>
                <td class="px-4 py-2.5 text-ink-gray-6">{{ acct.officer }}</td>
                <td class="px-4 py-2.5">
                  <Badge :label="acct.status" variant="subtle" :theme="statusTheme(acct.status)" />
                </td>
                <td class="px-4 py-2.5">
                  <div class="flex items-center justify-center gap-1" @click.stop>
                    <Button icon="phone" variant="ghost" size="sm" :title="__('Call')" @click="quickAction('call', acct)" />
                    <Button icon="message-square" variant="ghost" size="sm" :title="__('WhatsApp')" @click="quickAction('wa', acct)" />
                    <Button icon="map-pin" variant="ghost" size="sm" :title="__('Visit')" @click="quickAction('visit', acct)" />
                    <Button icon="edit-2" variant="ghost" size="sm" :title="__('Note')" @click="openNoteForm(acct)" />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── PTP TAB ── -->
    <div v-if="activeTab === 'ptp'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="grid grid-cols-4 gap-3">
        <div v-for="m in ptpMetrics" :key="m.label" class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-xs text-ink-gray-4">{{ __(m.label) }}</div>
          <div class="mt-1 text-2xl font-bold" :class="m.color || 'text-ink-gray-9'">{{ m.value }}</div>
        </div>
      </div>

      <div class="flex items-center justify-between">
        <div class="flex gap-2">
          <button
            v-for="f in ['All', 'Pending', 'Kept', 'Broken', 'Today']"
            :key="f"
            class="rounded-full border px-3 py-1 text-xs"
            :class="ptpFilter === f ? 'border-red-500 bg-red-50 text-red-700' : 'border-outline-gray-2 text-ink-gray-5'"
            @click="ptpFilter = f"
          >
            {{ __(f) }}
          </button>
        </div>
        <Button :label="__('New PTP')" variant="solid" size="sm" @click="openPtpForm(null)" />
      </div>

      <div class="rounded-[14px] border border-crm-border bg-white shadow-sm overflow-hidden">
        <table class="w-full text-xs">
          <thead class="bg-surface-gray-1">
            <tr class="border-b border-outline-gray-1 text-ink-gray-4">
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Customer') }}</th>
              <th class="px-4 py-2.5 text-right font-medium">{{ __('PTP Amount') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('PTP Date') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Channel') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Officer') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Status') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Notes') }}</th>
              <th class="px-4 py-2.5 text-center font-medium">{{ __('Actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="ptp in filteredPtps"
              :key="ptp.id"
              class="border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
            >
              <td class="px-4 py-2.5 font-medium text-ink-gray-8">{{ ptp.customer }}</td>
              <td class="px-4 py-2.5 text-right font-semibold text-ink-gray-8">{{ ptp.amount }}</td>
              <td class="px-4 py-2.5" :class="isPtpBreached(ptp.date) && ptp.status === 'Pending' ? 'text-red-500 font-medium' : 'text-ink-gray-6'">
                {{ ptp.date }}
              </td>
              <td class="px-4 py-2.5 text-ink-gray-5">{{ ptp.channel }}</td>
              <td class="px-4 py-2.5 text-ink-gray-5">{{ ptp.officer }}</td>
              <td class="px-4 py-2.5">
                <Badge :label="ptp.status" variant="subtle" :theme="ptp.status === 'Kept' ? 'green' : ptp.status === 'Broken' ? 'red' : 'orange'" />
              </td>
              <td class="px-4 py-2.5 text-ink-gray-5 max-w-[160px] truncate">{{ ptp.notes }}</td>
              <td class="px-4 py-2.5">
                <div class="flex justify-center gap-1">
                  <Button v-if="ptp.status === 'Pending'" label="Kept" variant="ghost" size="sm" @click="updatePtp(ptp, 'Kept')" />
                  <Button v-if="ptp.status === 'Pending'" label="Broken" variant="ghost" size="sm" @click="updatePtp(ptp, 'Broken')" />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── WORKFLOWS TAB ── -->
    <div v-if="activeTab === 'workflows'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <!-- Dunning Ladder -->
      <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
        <div class="mb-4 text-sm font-semibold text-ink-gray-8">{{ __('Dunning Ladder — Automated Collection Workflow') }}</div>
        <div class="flex items-start gap-0">
          <div
            v-for="(stage, idx) in dunningStages"
            :key="stage.label"
            class="flex flex-1 flex-col items-center"
          >
            <div class="relative flex flex-col items-center">
              <div
                class="flex h-12 w-12 items-center justify-center rounded-full text-white text-lg shadow-md"
                :class="stage.color"
              >
                {{ stage.icon }}
              </div>
              <div v-if="idx < dunningStages.length - 1" class="absolute top-6 left-1/2 h-0.5 w-full" :class="stage.lineColor" />
            </div>
            <div class="mt-3 text-center">
              <div class="text-xs font-semibold text-ink-gray-8">{{ stage.label }}</div>
              <div class="mt-0.5 text-[10px] text-ink-gray-4">DPD {{ stage.dpd }}</div>
              <div class="mt-1 text-[10px] text-ink-gray-5">{{ stage.desc }}</div>
              <div class="mt-2 rounded-md bg-surface-gray-1 px-2 py-1 text-[10px] font-medium" :class="stage.countColor">
                {{ stage.count }} {{ __('accounts') }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Workflows -->
      <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('Active Workflow Instances') }}</div>
          <Badge :label="activeWorkflows.length + ' running'" variant="subtle" theme="blue" />
        </div>
        <div class="space-y-2">
          <div
            v-for="wf in activeWorkflows"
            :key="wf.id"
            class="flex items-center gap-3 rounded-lg border border-outline-gray-1 px-3 py-2 hover:bg-surface-gray-1"
          >
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm" :class="wf.stageColor">
              {{ wf.stageIcon }}
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-xs font-medium text-ink-gray-8">{{ wf.customer }}</div>
              <div class="text-[10px] text-ink-gray-4">Stage: {{ wf.stage }} · Next: {{ wf.nextAction }}</div>
            </div>
            <div class="text-right text-xs">
              <div :class="dpdClass(wf.dpd)" class="rounded-full px-2 py-0.5 font-medium">DPD {{ wf.dpd }}</div>
            </div>
            <Button label="Pause" variant="ghost" size="sm" @click="() => {}" />
          </div>
        </div>
      </div>

      <!-- Restructuring & Write-off -->
      <div class="grid grid-cols-2 gap-4">
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Restructuring Queue') }}</div>
            <Button :label="__('New Proposal')" variant="subtle" size="sm" @click="showRestructureModal = true" />
          </div>
          <div class="space-y-2 text-xs">
            <div
              v-for="r in restructuringList"
              :key="r.id"
              class="flex items-center gap-2 rounded-lg border border-outline-gray-1 px-3 py-2"
            >
              <div class="min-w-0 flex-1">
                <div class="font-medium text-ink-gray-8">{{ r.customer }}</div>
                <div class="text-ink-gray-4">{{ r.proposed }} · {{ r.submittedDate }}</div>
              </div>
              <Badge :label="r.status" variant="subtle" :theme="r.status === 'Approved' ? 'green' : r.status === 'Pending' ? 'orange' : 'red'" />
            </div>
          </div>
        </div>

        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Write-Off Queue') }}</div>
            <Button :label="__('Propose Write-Off')" variant="subtle" size="sm" @click="showWriteOffModal = true" />
          </div>
          <div class="space-y-2 text-xs">
            <div
              v-for="wo in writeOffList"
              :key="wo.id"
              class="flex items-center gap-2 rounded-lg border border-outline-gray-1 px-3 py-2"
            >
              <div class="min-w-0 flex-1">
                <div class="font-medium text-ink-gray-8">{{ wo.customer }}</div>
                <div class="text-ink-gray-4">{{ wo.amount }} · {{ wo.reason }}</div>
              </div>
              <Badge :label="wo.status" variant="subtle" :theme="wo.status === 'Approved' ? 'green' : 'orange'" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── ANALYTICS TAB ── -->
    <div v-if="activeTab === 'analytics'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <!-- Recovery KPIs -->
      <div class="grid grid-cols-4 gap-3">
        <div v-for="m in recoveryMetrics" :key="m.label" class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-xs text-ink-gray-4">{{ __(m.label) }}</div>
          <div class="mt-1 text-2xl font-bold" :class="m.color">{{ m.value }}</div>
          <div class="mt-0.5 text-[10px] text-ink-gray-4">{{ m.sub }}</div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <!-- Recovery by Bucket -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Recovery Rate by Bucket') }}</div>
          <div class="space-y-2">
            <div v-for="b in recoveryByBucket" :key="b.label" class="flex items-center gap-2 text-xs">
              <span class="w-20 text-ink-gray-5">{{ b.label }}</span>
              <div class="flex-1 h-4 rounded-full bg-surface-gray-2 overflow-hidden">
                <div class="h-4 rounded-full" :class="b.color" :style="{ width: b.pct + '%' }" />
              </div>
              <span class="w-10 text-right font-medium" :class="b.textColor">{{ b.pct }}%</span>
            </div>
          </div>
        </div>

        <!-- Officer Productivity -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Officer Productivity') }}</div>
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b border-outline-gray-1 text-ink-gray-4 text-[10px]">
                <th class="pb-1 text-left">{{ __('Officer') }}</th>
                <th class="pb-1 text-right">{{ __('Calls') }}</th>
                <th class="pb-1 text-right">{{ __('PTP%') }}</th>
                <th class="pb-1 text-right">{{ __('Recovered') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="o in officerProductivity" :key="o.name" class="border-b border-outline-gray-1 last:border-0">
                <td class="py-1.5 text-ink-gray-7">{{ o.name }}</td>
                <td class="py-1.5 text-right text-ink-gray-5">{{ o.calls }}</td>
                <td class="py-1.5 text-right" :class="o.ptpKept >= 70 ? 'text-green-600' : 'text-amber-600'">{{ o.ptpKept }}%</td>
                <td class="py-1.5 text-right font-medium text-green-600">{{ o.recovered }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Channel Performance -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Channel Performance') }}</div>
          <div class="space-y-3">
            <div v-for="ch in channelPerformance" :key="ch.name" class="text-xs">
              <div class="flex justify-between mb-1">
                <span class="text-ink-gray-6">{{ ch.name }}</span>
                <span class="font-medium" :class="ch.pct >= 70 ? 'text-green-600' : 'text-amber-600'">{{ ch.pct }}% {{ __('response') }}</span>
              </div>
              <div class="h-2 rounded-full bg-surface-gray-2 overflow-hidden">
                <div class="h-2 rounded-full" :class="ch.color" :style="{ width: ch.pct + '%' }" />
              </div>
              <div class="mt-0.5 text-ink-gray-4">{{ ch.sent }} {{ __('sent') }} · {{ ch.responded }} {{ __('responded') }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Collection Letter Templates -->
      <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('Collection Letter Templates') }}</div>
          <Button :label="__('New Template')" variant="subtle" size="sm" @click="showLetterTemplateModal = true" />
        </div>
        <div class="grid grid-cols-4 gap-3">
          <div
            v-for="lt in letterTemplates"
            :key="lt.id"
            class="rounded-lg border border-outline-gray-1 p-3 hover:bg-surface-gray-1"
          >
            <div class="flex items-start justify-between gap-1">
              <div class="text-xs font-semibold text-ink-gray-8">{{ lt.name }}</div>
              <Badge :label="lt.type" variant="subtle" :theme="lt.type === 'Legal' ? 'red' : lt.type === 'Final' ? 'orange' : 'gray'" size="sm" />
            </div>
            <div class="mt-1 text-[10px] text-ink-gray-4">DPD trigger: {{ lt.dpd }}</div>
            <div class="mt-1 text-[10px] text-ink-gray-4">{{ lt.language }}</div>
            <div class="mt-2 flex gap-1">
              <Button label="Preview" variant="ghost" size="sm" @click="() => {}" />
              <Button label="Send" variant="ghost" size="sm" @click="() => {}" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── STRATEGY TAB ── -->
    <div v-if="activeTab === 'strategy'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="grid grid-cols-2 gap-4">
        <!-- Strategy Builder -->
        <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
          <div class="mb-4 text-sm font-semibold text-ink-gray-8">{{ __('Collection Strategy Builder') }}</div>
          <div class="space-y-3 text-sm">
            <div>
              <label class="text-xs text-ink-gray-5">{{ __('Strategy Name') }}</label>
              <input v-model="strategyForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="e.g. SME DPD 30-60 Strategy" />
            </div>
            <div>
              <label class="text-xs text-ink-gray-5">{{ __('Target Segment') }}</label>
              <select v-model="strategyForm.segment" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                <option v-for="s in ['SME', 'Commercial', 'Enterprise', 'Retail', 'All']" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-ink-gray-5">{{ __('DPD Range') }}</label>
              <div class="mt-1 flex gap-2">
                <input v-model="strategyForm.dpdMin" type="number" class="h-9 flex-1 rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Min" />
                <input v-model="strategyForm.dpdMax" type="number" class="h-9 flex-1 rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="Max" />
              </div>
            </div>
            <div>
              <label class="text-xs text-ink-gray-5">{{ __('Primary Channel') }}</label>
              <select v-model="strategyForm.channel" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                <option v-for="c in ['WhatsApp', 'SMS', 'Email', 'Call', 'Visit']" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-ink-gray-5">{{ __('Test Group') }}</label>
              <div class="mt-1 flex items-center gap-2">
                <input v-model="strategyForm.testPct" type="range" min="10" max="50" class="flex-1" />
                <span class="w-12 text-right text-xs text-ink-gray-6">{{ strategyForm.testPct }}%</span>
              </div>
              <div class="mt-0.5 text-[10px] text-ink-gray-4">A/B split: {{ strategyForm.testPct }}% test · {{ 100 - strategyForm.testPct }}% control</div>
            </div>
            <Button :label="__('Launch Strategy')" variant="solid" class="w-full" @click="launchStrategy" />
          </div>
        </div>

        <!-- Active Strategies -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Active Strategies & A/B Results') }}</div>
          <div class="space-y-3">
            <div
              v-for="s in activeStrategies"
              :key="s.id"
              class="rounded-lg border border-outline-gray-1 p-3"
            >
              <div class="flex items-start justify-between gap-2 mb-2">
                <div>
                  <div class="text-xs font-semibold text-ink-gray-8">{{ s.name }}</div>
                  <div class="text-[10px] text-ink-gray-4">{{ s.segment }} · DPD {{ s.dpd }} · {{ s.channel }}</div>
                </div>
                <Badge :label="s.status" variant="subtle" :theme="s.status === 'Active' ? 'green' : 'gray'" />
              </div>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="rounded bg-primary-50 p-2 text-center">
                  <div class="font-semibold text-primary-700">Test ({{ s.testPct }}%)</div>
                  <div class="text-primary-600">{{ s.testRecovery }}% recovery</div>
                </div>
                <div class="rounded bg-surface-gray-1 p-2 text-center">
                  <div class="font-semibold text-ink-gray-6">Control</div>
                  <div class="text-ink-gray-5">{{ s.controlRecovery }}% recovery</div>
                </div>
              </div>
              <div class="mt-1.5 text-[10px]" :class="s.testRecovery > s.controlRecovery ? 'text-green-600' : 'text-red-500'">
                {{ s.testRecovery > s.controlRecovery ? '↑ Test outperforming control by ' + (s.testRecovery - s.controlRecovery) + '%' : '↓ Test underperforming control' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── MODALS ── -->

  <!-- Account Detail -->
  <div v-if="selectedAccount" class="fixed inset-0 z-40 flex items-end justify-center bg-black/40 p-4 sm:items-center">
    <div class="w-full max-w-2xl rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-start justify-between gap-2">
        <div>
          <div class="text-lg font-semibold text-ink-gray-9">{{ selectedAccount.customer }}</div>
          <div class="text-xs text-ink-gray-5">{{ selectedAccount.product }} · DPD {{ selectedAccount.dpd }} · Outstanding: <span class="font-semibold text-red-600">{{ selectedAccount.outstanding }}</span></div>
        </div>
        <button class="text-ink-gray-4" @click="selectedAccount = null">✕</button>
      </div>
      <div class="grid grid-cols-3 gap-3 mb-4">
        <div class="rounded-lg bg-surface-gray-1 p-3 text-xs">
          <div class="text-ink-gray-4">AI Score</div>
          <div class="mt-1 text-lg font-bold" :class="selectedAccount.aiScore >= 70 ? 'text-green-600' : selectedAccount.aiScore >= 40 ? 'text-amber-600' : 'text-red-600'">{{ selectedAccount.aiScore }}%</div>
          <div class="text-ink-gray-4">recovery probability</div>
        </div>
        <div class="rounded-lg bg-surface-gray-1 p-3 text-xs">
          <div class="text-ink-gray-4">PTP Date</div>
          <div class="mt-1 text-sm font-semibold text-ink-gray-8">{{ selectedAccount.ptpDate || 'None' }}</div>
        </div>
        <div class="rounded-lg bg-surface-gray-1 p-3 text-xs">
          <div class="text-ink-gray-4">Officer</div>
          <div class="mt-1 text-sm font-semibold text-ink-gray-8">{{ selectedAccount.officer }}</div>
        </div>
      </div>
      <div class="mb-3 text-xs font-semibold text-ink-gray-6">{{ __('Collection History') }}</div>
      <div class="max-h-40 overflow-y-auto space-y-2 text-xs">
        <div v-for="note in selectedAccount.notes || []" :key="note.id" class="flex gap-2 rounded-lg bg-surface-gray-1 p-2">
          <div class="font-medium text-ink-gray-8 min-w-[80px]">{{ note.date }}</div>
          <div class="flex-1 text-ink-gray-6">{{ note.body }}</div>
          <Badge :label="note.outcome" variant="subtle" theme="gray" />
        </div>
      </div>
      <div class="mt-4 flex gap-2 flex-wrap">
        <Button :label="__('Record PTP')" variant="solid" size="sm" @click="openPtpForm(selectedAccount)" />
        <Button :label="__('Log Payment')" variant="outline" size="sm" @click="openPaymentForm(selectedAccount)" />
        <Button :label="__('Add Note')" variant="outline" size="sm" @click="openNoteForm(selectedAccount)" />
        <Button :label="__('Schedule Visit')" variant="outline" size="sm" @click="showVisitModal = true" />
        <Button :label="__('Legal Escalation')" variant="outline" size="sm" @click="showLegalModal = true" />
      </div>
    </div>
  </div>

  <!-- PTP Form -->
  <div v-if="showPtpModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Record Promise to Pay') }}</div>
        <button class="text-ink-gray-4" @click="showPtpModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Customer') }}</label>
          <input v-model="ptpForm.customer" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('PTP Amount (IDR)') }}</label>
            <input v-model="ptpForm.amount" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="e.g. 25,000,000" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('PTP Date') }}</label>
            <input v-model="ptpForm.date" type="date" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
          </div>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Channel of Commitment') }}</label>
          <select v-model="ptpForm.channel" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="c in ['Phone Call', 'WhatsApp', 'Visit', 'Email']" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Notes') }}</label>
          <textarea v-model="ptpForm.notes" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showPtpModal = false" />
        <Button :label="__('Save PTP')" variant="solid" @click="savePtp" />
      </div>
    </div>
  </div>

  <!-- Payment Form -->
  <div v-if="showPaymentModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Record Payment') }}</div>
        <button class="text-ink-gray-4" @click="showPaymentModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Customer') }}</label>
          <input v-model="paymentForm.customer" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Amount (IDR)') }}</label>
            <input v-model="paymentForm.amount" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Payment Date') }}</label>
            <input v-model="paymentForm.date" type="date" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
          </div>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Payment Mode') }}</label>
          <select v-model="paymentForm.mode" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="m in ['Transfer Bank', 'Cash', 'Virtual Account', 'Cek/Giro', 'Auto-debit']" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Allocation') }}</label>
          <div class="mt-1 grid grid-cols-3 gap-2">
            <div>
              <input v-model="paymentForm.principal" class="h-8 w-full rounded-md border border-outline-gray-2 px-2 text-xs" placeholder="Principal" />
            </div>
            <div>
              <input v-model="paymentForm.interest" class="h-8 w-full rounded-md border border-outline-gray-2 px-2 text-xs" placeholder="Interest" />
            </div>
            <div>
              <input v-model="paymentForm.charges" class="h-8 w-full rounded-md border border-outline-gray-2 px-2 text-xs" placeholder="Charges" />
            </div>
          </div>
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showPaymentModal = false" />
        <Button :label="__('Record & Generate Receipt')" variant="solid" @click="savePayment" />
      </div>
    </div>
  </div>

  <!-- Note Form -->
  <div v-if="showNoteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Log Collection Note') }}</div>
        <button class="text-ink-gray-4" @click="showNoteModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Outcome') }}</label>
          <select v-model="noteForm.outcome" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="o in ['Contacted — Promised', 'Contacted — Refused', 'No Answer', 'Left Message', 'Visit Completed', 'Legal Notice Sent']" :key="o" :value="o">{{ o }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Notes') }}</label>
          <textarea v-model="noteForm.body" rows="3" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" placeholder="Detail discussion..." />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Next Follow-up') }}</label>
          <input v-model="noteForm.followUp" type="date" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showNoteModal = false" />
        <Button :label="__('Save Note')" variant="solid" @click="saveNote" />
      </div>
    </div>
  </div>

  <!-- Legal Escalation -->
  <div v-if="showLegalModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-lg rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Legal Escalation') }}</div>
        <button class="text-ink-gray-4" @click="showLegalModal = false">✕</button>
      </div>
      <div class="mb-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
        ⚠️ {{ __('Legal escalation will generate a formal legal notice and assign to the legal officer. This action is logged and cannot be undone without approval.') }}
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Customer') }}</label>
          <input v-model="legalForm.customer" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Trigger Condition') }}</label>
            <select v-model="legalForm.trigger" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option>DPD > 90</option>
              <option>3x Broken PTP</option>
              <option>Unresponsive > 60 days</option>
              <option>Manual escalation</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Assign Legal Officer') }}</label>
            <select v-model="legalForm.officer" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="o in ['Hendra Wijaya', 'Putri Kusuma', 'Faisal Rahman']" :key="o">{{ o }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Letter Type') }}</label>
          <select v-model="legalForm.letterType" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option>Surat Peringatan 1 (SP1)</option>
            <option>Surat Peringatan 2 (SP2)</option>
            <option>Surat Peringatan 3 / Final</option>
            <option>Somasi</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Notes') }}</label>
          <textarea v-model="legalForm.notes" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showLegalModal = false" />
        <Button :label="__('Generate Legal Notice')" variant="solid" theme="red" @click="saveLegal" />
      </div>
    </div>
  </div>

  <!-- Visit Scheduling -->
  <div v-if="showVisitModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Schedule Visit') }}</div>
        <button class="text-ink-gray-4" @click="showVisitModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Visit Date') }}</label>
            <input v-model="visitForm.date" type="date" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Time') }}</label>
            <input v-model="visitForm.time" type="time" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
          </div>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Field Officer') }}</label>
          <select v-model="visitForm.officer" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="o in officers" :key="o">{{ o }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Visit Address') }}</label>
          <textarea v-model="visitForm.address" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Purpose') }}</label>
          <select v-model="visitForm.purpose" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option>Collection Visit</option>
            <option>Restructuring Discussion</option>
            <option>Asset Verification</option>
            <option>Legal Notice Delivery</option>
          </select>
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showVisitModal = false" />
        <Button :label="__('Schedule')" variant="solid" @click="saveVisit" />
      </div>
    </div>
  </div>

  <!-- Restructure Modal (simplified) -->
  <div v-if="showRestructureModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Restructuring Proposal') }}</div>
        <button class="text-ink-gray-4" @click="showRestructureModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div><label class="text-xs text-ink-gray-5">{{ __('Customer') }}</label><input v-model="restructureForm.customer" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" /></div>
        <div><label class="text-xs text-ink-gray-5">{{ __('Proposed Terms') }}</label><textarea v-model="restructureForm.terms" rows="3" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" placeholder="e.g. Extend tenor 12 months, reduce rate to 8%..." /></div>
        <div><label class="text-xs text-ink-gray-5">{{ __('Rationale') }}</label><textarea v-model="restructureForm.rationale" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" /></div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showRestructureModal = false" />
        <Button :label="__('Submit for Approval')" variant="solid" @click="saveRestructure" />
      </div>
    </div>
  </div>

  <!-- Write-Off Modal (simplified) -->
  <div v-if="showWriteOffModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Write-Off Proposal') }}</div>
        <button class="text-ink-gray-4" @click="showWriteOffModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div><label class="text-xs text-ink-gray-5">{{ __('Customer') }}</label><input v-model="writeOffForm.customer" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" /></div>
        <div><label class="text-xs text-ink-gray-5">{{ __('Amount (IDR)') }}</label><input v-model="writeOffForm.amount" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" /></div>
        <div><label class="text-xs text-ink-gray-5">{{ __('Reason') }}</label>
          <select v-model="writeOffForm.reason" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="r in ['Bankruptcy', 'Deceased', 'Uncontactable > 2 years', 'Legal settlement', 'Business closure']" :key="r">{{ r }}</option>
          </select>
        </div>
        <div><label class="text-xs text-ink-gray-5">{{ __('Supporting Evidence') }}</label><input type="file" class="mt-1 w-full text-xs text-ink-gray-5" /></div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showWriteOffModal = false" />
        <Button :label="__('Submit Write-Off')" variant="solid" @click="saveWriteOff" />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Badge, Button, FeatherIcon, usePageMeta } from 'frappe-ui'
import { computed, ref } from 'vue'

// ── Page tabs ────────────────────────────────────────────────
const pageTabs = computed(() => [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'delinquency', label: 'Delinquency List', badge: filteredAccounts.value.filter((a) => a.dpd > 30).length },
  { key: 'ptp', label: 'Promise to Pay', badge: ptps.value.filter((p) => p.status === 'Pending').length },
  { key: 'workflows', label: 'Workflows' },
  { key: 'analytics', label: 'Analytics' },
  { key: 'strategy', label: 'Strategy Builder' },
])
const activeTab = ref('dashboard')
const agingMetric = ref('Count')

// ── Filter state ─────────────────────────────────────────────
const listSearch = ref('')
const filterBucket = ref('')
const filterProduct = ref('')
const filterOfficer = ref('')
const sortField = ref('dpd')
const ptpFilter = ref('All')

// ── Modal state ──────────────────────────────────────────────
const selectedAccount = ref(null)
const showPtpModal = ref(false)
const showPaymentModal = ref(false)
const showNoteModal = ref(false)
const showLegalModal = ref(false)
const showVisitModal = ref(false)
const showRestructureModal = ref(false)
const showWriteOffModal = ref(false)

// ── Form state ───────────────────────────────────────────────
const ptpForm = ref({ customer: '', amount: '', date: '', channel: 'Phone Call', notes: '' })
const paymentForm = ref({ customer: '', amount: '', date: '', mode: 'Transfer Bank', principal: '', interest: '', charges: '' })
const noteForm = ref({ outcome: 'Contacted — Promised', body: '', followUp: '' })
const legalForm = ref({ customer: '', trigger: 'DPD > 90', officer: 'Hendra Wijaya', letterType: 'Surat Peringatan 1 (SP1)', notes: '' })
const visitForm = ref({ date: '', time: '', officer: '', address: '', purpose: 'Collection Visit' })
const restructureForm = ref({ customer: '', terms: '', rationale: '' })
const writeOffForm = ref({ customer: '', amount: '', reason: 'Bankruptcy' })
const strategyForm = ref({ name: '', segment: 'SME', dpdMin: 30, dpdMax: 60, channel: 'WhatsApp', testPct: 20 })

// ── Reference data ───────────────────────────────────────────
const officers = ['Rina Susilawati', 'Bagas Nugroho', 'Desi Fitriani', 'Yusuf Pratama', 'Eka Wulandari']
const products = ['Working Capital Loan', 'Term Loan', 'Invoice Financing', 'KPR Korporat', 'Revolving Credit']

// ── Dashboard data ───────────────────────────────────────────
const dashKpis = [
  { label: 'Total Overdue', value: 'IDR 48.2B', icon: 'alert-triangle', iconColor: 'text-red-500', delta: '+IDR 3.1B vs last month', deltaColor: 'text-red-500' },
  { label: 'Accounts in Arrears', value: '342', icon: 'users', iconColor: 'text-orange-500', delta: '28 new this week', deltaColor: 'text-orange-500' },
  { label: 'Recovery Rate MTD', value: '67%', icon: 'trending-up', iconColor: 'text-green-500', valueColor: 'text-green-600', delta: '+5% vs target', deltaColor: 'text-green-600' },
  { label: 'Recovered MTD', value: 'IDR 12.4B', icon: 'dollar-sign', iconColor: 'text-green-500', valueColor: 'text-green-600', delta: 'Target: IDR 15B' },
  { label: 'SLA Compliance', value: '89%', icon: 'clock', iconColor: 'text-blue-500', delta: '38 SLA breaches' },
]

const agingBuckets = [
  { label: 'Current (0d)', count: 1240, countPct: 100, amountDisplay: 'IDR 210B', amountPct: 100, color: 'bg-green-500', textColor: 'text-green-700' },
  { label: 'DPD 1–30', count: 198, countPct: 16, amountDisplay: 'IDR 22.1B', amountPct: 11, color: 'bg-yellow-400', textColor: 'text-yellow-700' },
  { label: 'DPD 31–60', count: 87, countPct: 7, amountDisplay: 'IDR 14.8B', amountPct: 7, color: 'bg-orange-500', textColor: 'text-orange-700' },
  { label: 'DPD 61–90', count: 42, countPct: 3.4, amountDisplay: 'IDR 7.3B', amountPct: 3.5, color: 'bg-red-500', textColor: 'text-red-700' },
  { label: 'DPD 91–180', count: 28, countPct: 2.3, amountDisplay: 'IDR 4.2B', amountPct: 2, color: 'bg-red-700', textColor: 'text-red-800' },
  { label: 'DPD 180+', count: 15, countPct: 1.2, amountDisplay: 'IDR 2.9B', amountPct: 1.4, color: 'bg-gray-800', textColor: 'text-gray-800' },
]

const aiPriorityList = [
  { id: 'p1', customer: 'PT Nusantara Jaya', dpd: 47, outstanding: 'IDR 8.2B', score: 78 },
  { id: 'p2', customer: 'CV Arjuna Perkasa', dpd: 33, outstanding: 'IDR 3.4B', score: 65 },
  { id: 'p3', customer: 'Sari Logistics', dpd: 62, outstanding: 'IDR 5.1B', score: 42 },
  { id: 'p4', customer: 'Mega Teknik Group', dpd: 29, outstanding: 'IDR 2.8B', score: 81 },
  { id: 'p5', customer: 'Berkah Abadi', dpd: 91, outstanding: 'IDR 1.9B', score: 18 },
]

const topDefaulters = [
  { id: 'd1', customer: 'PT Global Makmur', outstanding: 'IDR 12.4B', dpd: 95, status: 'Legal' },
  { id: 'd2', customer: 'Sari Logistics', outstanding: 'IDR 5.1B', dpd: 62, status: 'PTP' },
  { id: 'd3', customer: 'PT Nusantara Jaya', outstanding: 'IDR 8.2B', dpd: 47, status: 'Active' },
  { id: 'd4', customer: 'CV Arjuna Perkasa', outstanding: 'IDR 3.4B', dpd: 33, status: 'PTP' },
  { id: 'd5', customer: 'Berkah Abadi', outstanding: 'IDR 1.9B', dpd: 91, status: 'Legal' },
]

const officerLeaderboard = [
  { name: 'Rina Susilawati', recovered: 'IDR 3.2B', ptpKept: 84, pct: 90 },
  { name: 'Bagas Nugroho', recovered: 'IDR 2.8B', ptpKept: 79, pct: 80 },
  { name: 'Desi Fitriani', recovered: 'IDR 2.1B', ptpKept: 72, pct: 65 },
  { name: 'Yusuf Pratama', recovered: 'IDR 1.9B', ptpKept: 68, pct: 55 },
  { name: 'Eka Wulandari', recovered: 'IDR 1.4B', ptpKept: 61, pct: 40 },
]

// ── Accounts data ────────────────────────────────────────────
const accounts = ref([
  { id: 'a1', customer: 'PT Nusantara Jaya', product: 'Working Capital Loan', outstanding: 'IDR 8.2B', dpd: 47, aiScore: 78, ptpDate: '2026-05-28', lastAction: '2026-05-22', officer: 'Rina Susilawati', status: 'PTP', bucket: 'DPD 31–60', notes: [{ id: 'n1', date: '2026-05-22', body: 'Customer contacted, promised to pay by end of May.', outcome: 'Contacted — Promised' }] },
  { id: 'a2', customer: 'Sari Logistics', product: 'Revolving Credit', outstanding: 'IDR 5.1B', dpd: 62, aiScore: 42, ptpDate: '2026-05-15', lastAction: '2026-05-20', officer: 'Bagas Nugroho', status: 'Active', bucket: 'DPD 61–90', notes: [{ id: 'n2', date: '2026-05-20', body: 'No answer. Left voicemail.', outcome: 'No Answer' }] },
  { id: 'a3', customer: 'CV Arjuna Perkasa', product: 'Invoice Financing', outstanding: 'IDR 3.4B', dpd: 33, aiScore: 65, ptpDate: '2026-05-30', lastAction: '2026-05-23', officer: 'Desi Fitriani', status: 'PTP', bucket: 'DPD 31–60', notes: [] },
  { id: 'a4', customer: 'Mega Teknik Group', product: 'Term Loan', outstanding: 'IDR 2.8B', dpd: 29, aiScore: 81, ptpDate: '', lastAction: '2026-05-24', officer: 'Yusuf Pratama', status: 'Active', bucket: 'DPD 1–30', notes: [] },
  { id: 'a5', customer: 'Berkah Abadi', product: 'KPR Korporat', outstanding: 'IDR 1.9B', dpd: 91, aiScore: 18, ptpDate: '', lastAction: '2026-05-10', officer: 'Eka Wulandari', status: 'Legal', bucket: 'DPD 91–180', notes: [{ id: 'n3', date: '2026-05-10', body: 'SP2 sudah dikirim. Tidak ada respon.', outcome: 'Legal Notice Sent' }] },
  { id: 'a6', customer: 'PT Global Makmur', product: 'Working Capital Loan', outstanding: 'IDR 12.4B', dpd: 95, aiScore: 12, ptpDate: '', lastAction: '2026-05-05', officer: 'Rina Susilawati', status: 'Legal', bucket: 'DPD 91–180', notes: [] },
  { id: 'a7', customer: 'Maju Sejahtera', product: 'Term Loan', outstanding: 'IDR 1.2B', dpd: 18, aiScore: 87, ptpDate: '2026-05-25', lastAction: '2026-05-23', officer: 'Bagas Nugroho', status: 'PTP', bucket: 'DPD 1–30', notes: [] },
])

// ── PTPs data ────────────────────────────────────────────────
const ptps = ref([
  { id: 'ptp1', customer: 'PT Nusantara Jaya', amount: 'IDR 500M', date: '2026-05-28', channel: 'Phone Call', officer: 'Rina Susilawati', status: 'Pending', notes: 'Dijanjikan transfer sebelum jam 15.00' },
  { id: 'ptp2', customer: 'CV Arjuna Perkasa', amount: 'IDR 200M', date: '2026-05-30', channel: 'WhatsApp', officer: 'Desi Fitriani', status: 'Pending', notes: '' },
  { id: 'ptp3', customer: 'Maju Sejahtera', amount: 'IDR 120M', date: '2026-05-25', channel: 'Visit', officer: 'Bagas Nugroho', status: 'Kept', notes: 'Sudah transfer pukul 10.30' },
  { id: 'ptp4', customer: 'Sari Logistics', amount: 'IDR 350M', date: '2026-05-15', channel: 'Email', officer: 'Bagas Nugroho', status: 'Broken', notes: 'Tidak ada transfer sesuai janji' },
  { id: 'ptp5', customer: 'Mega Teknik Group', amount: 'IDR 800M', date: '2026-05-26', channel: 'Phone Call', officer: 'Yusuf Pratama', status: 'Pending', notes: 'Konfirmasi via telepon pukul 11.00' },
])

// ── Dunning workflow ─────────────────────────────────────────
const dunningStages = [
  { label: 'SMS Reminder', dpd: '1–7', icon: '📱', desc: 'Auto SMS 3x', count: 198, color: 'bg-green-500', lineColor: 'bg-green-300', countColor: 'text-green-700' },
  { label: 'WA Message', dpd: '8–14', icon: '💬', desc: 'WhatsApp + template', count: 124, color: 'bg-yellow-500', lineColor: 'bg-yellow-300', countColor: 'text-yellow-700' },
  { label: 'Phone Call', dpd: '15–30', icon: '📞', desc: 'Officer calls', count: 87, color: 'bg-orange-500', lineColor: 'bg-orange-300', countColor: 'text-orange-700' },
  { label: 'Field Visit', dpd: '31–60', icon: '🚗', desc: 'Physical visit', count: 42, color: 'bg-red-500', lineColor: 'bg-red-300', countColor: 'text-red-700' },
  { label: 'Legal Notice', dpd: '61–90', icon: '⚖️', desc: 'SP1 / SP2', count: 28, color: 'bg-red-700', lineColor: 'bg-red-500', countColor: 'text-red-800' },
  { label: 'Court / Auction', dpd: '90+', icon: '🏛️', desc: 'Litigation / KPKNL', count: 15, color: 'bg-gray-800', lineColor: '', countColor: 'text-gray-700' },
]

const activeWorkflows = ref([
  { id: 'wf1', customer: 'PT Nusantara Jaya', stage: 'WA Message', nextAction: 'Auto-WA at 14:00', dpd: 47, stageColor: 'bg-yellow-100 text-yellow-700', stageIcon: '💬' },
  { id: 'wf2', customer: 'Sari Logistics', stage: 'Phone Call', nextAction: 'Officer call tomorrow 09:00', dpd: 62, stageColor: 'bg-orange-100 text-orange-700', stageIcon: '📞' },
  { id: 'wf3', customer: 'CV Arjuna Perkasa', stage: 'SMS Reminder', nextAction: 'SMS #2 at 10:00', dpd: 33, stageColor: 'bg-green-100 text-green-700', stageIcon: '📱' },
])

const restructuringList = ref([
  { id: 'r1', customer: 'Sari Logistics', proposed: 'Tenor +12m, rate 8%', submittedDate: '2026-05-20', status: 'Pending' },
  { id: 'r2', customer: 'PT Nusantara Jaya', proposed: 'Grace period 3m', submittedDate: '2026-05-18', status: 'Approved' },
])

const writeOffList = ref([
  { id: 'w1', customer: 'PT Global Makmur', amount: 'IDR 12.4B', reason: 'Bankruptcy', status: 'Pending' },
])

// ── Analytics data ───────────────────────────────────────────
const recoveryMetrics = [
  { label: 'Total Recovered MTD', value: 'IDR 12.4B', color: 'text-green-600', sub: 'Target: IDR 15B' },
  { label: 'Write-Off MTD', value: 'IDR 1.2B', color: 'text-red-600', sub: '3 accounts' },
  { label: 'Cost to Collect', value: '3.2%', color: 'text-ink-gray-9', sub: 'per IDR recovered' },
  { label: 'Avg Collection Cycle', value: '22 days', color: 'text-ink-gray-9', sub: 'from first contact' },
]

const recoveryByBucket = [
  { label: 'DPD 1–30', pct: 91, color: 'bg-green-500', textColor: 'text-green-600' },
  { label: 'DPD 31–60', pct: 74, color: 'bg-yellow-400', textColor: 'text-yellow-700' },
  { label: 'DPD 61–90', pct: 52, color: 'bg-orange-500', textColor: 'text-orange-700' },
  { label: 'DPD 91–180', pct: 28, color: 'bg-red-500', textColor: 'text-red-600' },
  { label: 'DPD 180+', pct: 8, color: 'bg-red-800', textColor: 'text-red-800' },
]

const officerProductivity = [
  { name: 'Rina Susilawati', calls: 142, ptpKept: 84, recovered: 'IDR 3.2B' },
  { name: 'Bagas Nugroho', calls: 118, ptpKept: 79, recovered: 'IDR 2.8B' },
  { name: 'Desi Fitriani', calls: 97, ptpKept: 72, recovered: 'IDR 2.1B' },
  { name: 'Yusuf Pratama', calls: 84, ptpKept: 68, recovered: 'IDR 1.9B' },
  { name: 'Eka Wulandari', calls: 71, ptpKept: 61, recovered: 'IDR 1.4B' },
]

const channelPerformance = [
  { name: 'SMS Reminder', sent: 842, responded: 614, pct: 73, color: 'bg-green-500' },
  { name: 'WhatsApp', sent: 521, responded: 418, pct: 80, color: 'bg-green-600' },
  { name: 'Phone Call', sent: 284, responded: 171, pct: 60, color: 'bg-amber-500' },
  { name: 'Field Visit', sent: 98, responded: 87, pct: 89, color: 'bg-blue-500' },
]

const letterTemplates = [
  { id: 'lt1', name: 'Surat Peringatan 1', type: 'Reminder', dpd: '30+', language: 'Bahasa Indonesia' },
  { id: 'lt2', name: 'Surat Peringatan 2', type: 'Warning', dpd: '60+', language: 'Bahasa Indonesia' },
  { id: 'lt3', name: 'Final Reminder', type: 'Final', dpd: '90+', language: 'Bahasa Indonesia' },
  { id: 'lt4', name: 'Somasi / Legal Notice', type: 'Legal', dpd: '90+', language: 'Bahasa Indonesia + English' },
]

const showLetterTemplateModal = ref(false)

// ── Strategy data ────────────────────────────────────────────
const activeStrategies = ref([
  { id: 's1', name: 'SME DPD 30–60 WA-first', segment: 'SME', dpd: '30–60', channel: 'WhatsApp', status: 'Active', testPct: 30, testRecovery: 78, controlRecovery: 64 },
  { id: 's2', name: 'Enterprise SMS vs Call', segment: 'Enterprise', dpd: '1–30', channel: 'SMS', status: 'Active', testPct: 20, testRecovery: 82, controlRecovery: 85 },
])

// ── PTP Metrics ──────────────────────────────────────────────
const ptpMetrics = computed(() => {
  const all = ptps.value
  const kept = all.filter((p) => p.status === 'Kept').length
  const broken = all.filter((p) => p.status === 'Broken').length
  const pending = all.filter((p) => p.status === 'Pending').length
  const total = all.length
  return [
    { label: 'Total PTPs', value: total },
    { label: 'Pending', value: pending, color: 'text-amber-600' },
    { label: 'Kept', value: kept, color: 'text-green-600' },
    { label: 'PTP Success Rate', value: total ? Math.round((kept / (kept + broken)) * 100) + '%' : '—', color: 'text-green-600' },
  ]
})

// ── Computed filters ─────────────────────────────────────────
const filteredAccounts = computed(() => {
  let list = accounts.value
  if (listSearch.value) list = list.filter((a) => a.customer.toLowerCase().includes(listSearch.value.toLowerCase()))
  if (filterBucket.value) list = list.filter((a) => a.bucket === filterBucket.value)
  if (filterProduct.value) list = list.filter((a) => a.product === filterProduct.value)
  if (filterOfficer.value) list = list.filter((a) => a.officer === filterOfficer.value)
  return [...list].sort((a, b) => {
    if (sortField.value === 'outstanding') return b.outstanding.localeCompare(a.outstanding)
    if (sortField.value === 'aiScore') return b.aiScore - a.aiScore
    if (sortField.value === 'lastAction') return b.lastAction.localeCompare(a.lastAction)
    return b.dpd - a.dpd
  })
})

const filteredPtps = computed(() => {
  if (ptpFilter.value === 'All') return ptps.value
  if (ptpFilter.value === 'Today') return ptps.value.filter((p) => p.date === new Date().toISOString().slice(0, 10))
  return ptps.value.filter((p) => p.status === ptpFilter.value)
})

// ── Helpers ──────────────────────────────────────────────────
function dpdClass(dpd) {
  if (dpd > 90) return 'bg-gray-800 text-white'
  if (dpd > 60) return 'bg-red-100 text-red-700'
  if (dpd > 30) return 'bg-orange-100 text-orange-700'
  if (dpd > 0) return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}
function statusTheme(status) {
  return status === 'Legal' ? 'red' : status === 'PTP' ? 'orange' : status === 'Closed' ? 'green' : 'gray'
}
function isPtpBreached(date) {
  if (!date) return false
  return new Date(date) < new Date()
}

// ── Actions ──────────────────────────────────────────────────
function drillToBucket(bucket) {
  filterBucket.value = bucket.label
  activeTab.value = 'delinquency'
}

function openAccountDetail(acct) {
  selectedAccount.value = acct
}

function openPtpForm(acct) {
  ptpForm.value = { customer: acct?.customer || '', amount: '', date: '', channel: 'Phone Call', notes: '' }
  showPtpModal.value = true
  selectedAccount.value = null
}

function openPaymentForm(acct) {
  paymentForm.value = { customer: acct?.customer || '', amount: '', date: '', mode: 'Transfer Bank', principal: '', interest: '', charges: '' }
  showPaymentModal.value = true
  selectedAccount.value = null
}

function openNoteForm(acct) {
  noteForm.value = { outcome: 'Contacted — Promised', body: '', followUp: '' }
  if (acct) selectedAccount.value = acct
  showNoteModal.value = true
}

function savePtp() {
  if (!ptpForm.value.customer || !ptpForm.value.date) return
  ptps.value.unshift({ id: `ptp-${Date.now()}`, ...ptpForm.value, status: 'Pending' })
  showPtpModal.value = false
}

function updatePtp(ptp, status) {
  ptp.status = status
}

function savePayment() {
  showPaymentModal.value = false
}

function saveNote() {
  if (selectedAccount.value && noteForm.value.body) {
    selectedAccount.value.notes = selectedAccount.value.notes || []
    selectedAccount.value.notes.push({
      id: `n-${Date.now()}`,
      date: new Date().toISOString().slice(0, 10),
      body: noteForm.value.body,
      outcome: noteForm.value.outcome,
    })
    selectedAccount.value.lastAction = new Date().toISOString().slice(0, 10)
  }
  showNoteModal.value = false
}

function saveLegal() {
  showLegalModal.value = false
}

function saveVisit() {
  showVisitModal.value = false
}

function saveRestructure() {
  if (!restructureForm.value.customer) return
  restructuringList.value.unshift({ id: `r-${Date.now()}`, customer: restructureForm.value.customer, proposed: restructureForm.value.terms.slice(0, 40), submittedDate: new Date().toISOString().slice(0, 10), status: 'Pending' })
  showRestructureModal.value = false
}

function saveWriteOff() {
  if (!writeOffForm.value.customer) return
  writeOffList.value.unshift({ id: `wo-${Date.now()}`, customer: writeOffForm.value.customer, amount: writeOffForm.value.amount, reason: writeOffForm.value.reason, status: 'Pending' })
  showWriteOffModal.value = false
}

function quickAction(type, acct) {
  if (type === 'call') openPtpForm(acct)
  else if (type === 'wa') openNoteForm(acct)
  else if (type === 'visit') { selectedAccount.value = acct; showVisitModal.value = true }
  else if (type === 'note') openNoteForm(acct)
}

function launchStrategy() {
  if (!strategyForm.value.name) return
  activeStrategies.value.unshift({
    id: `s-${Date.now()}`,
    name: strategyForm.value.name,
    segment: strategyForm.value.segment,
    dpd: `${strategyForm.value.dpdMin}–${strategyForm.value.dpdMax}`,
    channel: strategyForm.value.channel,
    status: 'Active',
    testPct: strategyForm.value.testPct,
    testRecovery: 0,
    controlRecovery: 0,
  })
}

usePageMeta(() => ({ title: __('Collections') }))
</script>
