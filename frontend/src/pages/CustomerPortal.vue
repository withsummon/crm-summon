<template>
  <div class="flex h-full flex-col">
    <LayoutHeader v-if="!props.embedded">
      <template #left-header>
        <div class="flex items-center gap-2 text-base">
          <button class="text-ink-gray-5 hover:text-ink-gray-9" @click="navigate('dashboard')">Customer Portal</button>
          <template v-if="activeView === 'app-detail' && selectedApp">
            <span class="text-ink-gray-3">/</span>
            <button class="text-ink-gray-5 hover:text-ink-gray-9" @click="navigate('applications')">Applications</button>
            <span class="text-ink-gray-3">/</span>
            <span class="font-medium text-ink-gray-9">{{ selectedApp.borrower_name }}</span>
          </template>
          <template v-else-if="activeView === 'facility-detail' && selectedFacility">
            <span class="text-ink-gray-3">/</span>
            <button class="text-ink-gray-5 hover:text-ink-gray-9" @click="navigate('facilities')">Facilities</button>
            <span class="text-ink-gray-3">/</span>
            <span class="font-medium text-ink-gray-9">{{ selectedFacility.facility_type }}</span>
          </template>
          <template v-else-if="activeView === 'topup'">
            <span class="text-ink-gray-3">/</span>
            <button class="text-ink-gray-5 hover:text-ink-gray-9" @click="navigate('facilities')">Facilities</button>
            <span class="text-ink-gray-3">/</span>
            <span class="font-medium text-ink-gray-9">Request Top-Up</span>
          </template>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-1.5 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-2.5 py-1.5">
          <FeatherIcon name="user" class="h-3.5 w-3.5 text-ink-gray-5" />
          <span class="text-sm font-medium text-ink-gray-8">{{ currentCustomerName }}</span>
        </div>
        <Button
          v-if="activeView === 'facility-detail' && selectedFacility"
          variant="outline"
          size="sm"
          label="Print Schedule"
          @click="window.print()"
        >
          <template #prefix><FeatherIcon name="printer" class="h-4 w-4" /></template>
        </Button>
        <Button
          v-if="activeView === 'facility-detail' && selectedFacility"
          variant="solid"
          size="sm"
          label="Request Top-Up"
          @click="topupFacility = selectedFacility; navigate('topup')"
        >
          <template #prefix><FeatherIcon name="trending-up" class="h-4 w-4" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Tab strip -->
    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-5">
      <div class="flex items-center justify-between gap-4">
        <div class="flex gap-5">
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
            v-if="isActiveTab('applications')"
            variant="solid"
            size="sm"
            label="New Application"
            @click="openNewApplication"
          >
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'documents'"
            variant="solid"
            size="sm"
            label="Upload Document"
            @click="openNewDocument"
          >
            <template #prefix><FeatherIcon name="upload" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'tickets'"
            variant="solid"
            size="sm"
            label="New Ticket"
            @click="ticketTab = 'new'"
          >
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          </Button>
          <select v-model="language" class="rounded-md border border-outline-gray-2 bg-surface-white px-2 py-1 text-xs text-ink-gray-7" @change="onLanguageChange">
            <option v-for="l in LANGUAGES" :key="l.code" :value="l.code">{{ l.label }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto">
      <div class="max-w-6xl px-6 py-6">

        <!-- ── DASHBOARD ───────────────────────────── -->
        <template v-if="activeView === 'dashboard'">
          <div v-if="dashboard.loading" class="flex h-48 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>
          <div v-else-if="dashboard.error" class="flex h-48 flex-col items-center justify-center text-ink-gray-4">
            <FeatherIcon name="alert-circle" class="mb-2 h-6 w-6" />
            <p class="text-base">Failed to load dashboard</p>
            <p class="mt-1 text-sm">{{ dashboard.error.message || 'Check that demo data has been loaded' }}</p>
            <Button class="mt-3" size="sm" variant="outline" label="Retry" @click="dashboard.reload()" />
          </div>
          <template v-else>
            <div class="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <StatCard label="Active Facilities" :value="String(dashboard.data?.active_facilities ?? 0)" icon="credit-card" />
              <StatCard label="Applications in Progress" :value="String(dashboard.data?.pending_applications ?? 0)" icon="file-text" />
              <StatCard
                label="Next Payment Due"
                :value="dashboard.data?.next_payment ? formatDate(dashboard.data.next_payment.date) : 'None'"
                :sub="dashboard.data?.next_payment ? daysLabel(dashboard.data.next_payment.days_until) : ''"
                icon="calendar"
                :warn="dueUrgent"
              />
              <StatCard label="Notifications" :value="String(dashboard.data?.notifications?.length ?? 0)" icon="bell" />
            </div>

            <div class="grid gap-6 lg:grid-cols-3">
              <div class="space-y-5 lg:col-span-2">
                <div class="flex items-center justify-between">
                  <span class="text-base font-medium text-ink-gray-9">Active Facilities</span>
                  <button class="text-sm text-ink-blue-3 hover:underline" @click="navigate('facilities')">View all</button>
                </div>
                <div v-if="facilities.loading" class="flex h-16 items-center justify-center">
                  <LoadingIndicator class="h-4 w-4 text-ink-gray-4" />
                </div>
                <div v-else class="space-y-2">
                  <div
                    v-for="f in facilities.data"
                    :key="f.name"
                    class="cursor-pointer rounded-lg border border-outline-gray-2 bg-surface-white p-4 hover:border-outline-gray-3"
                    @click="loadFacility(f.name)"
                  >
                    <div class="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-4">
                      <div class="min-w-0">
                        <p class="truncate text-base font-medium leading-5 text-ink-gray-9">{{ f.customer }}</p>
                        <div class="mt-1 flex items-center gap-2">
                          <Badge :label="f.facility_type" theme="teal" variant="subtle" />
                          <span class="truncate text-sm leading-5 text-ink-gray-5">{{ f.product_type }}</span>
                        </div>
                      </div>
                      <div class="shrink-0 text-right">
                        <p class="text-base font-semibold leading-5 text-ink-gray-9">{{ formatAmount(f.outstanding) }}</p>
                        <p class="mt-1 text-sm leading-5 text-ink-gray-4">of {{ formatAmount(f.limit_amount) }}</p>
                      </div>
                    </div>
                    <div class="mt-5">
                      <div class="h-1.5 overflow-hidden rounded-full bg-surface-gray-2">
                        <div class="h-full rounded-full bg-crm-teal" :style="{ width: pct(f.outstanding, f.limit_amount) + '%' }" />
                      </div>
                      <div class="mt-2 flex items-center justify-between gap-4 text-sm leading-5 text-ink-gray-4">
                        <span>{{ pct(f.outstanding, f.limit_amount) }}% utilised</span>
                        <span :class="isDueSoon(f.due_date) ? 'font-medium text-crm-warning' : ''">Due {{ formatDate(f.due_date) }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="flex items-center justify-between pt-1">
                  <span class="text-base font-medium text-ink-gray-9">Applications in Progress</span>
                  <button class="text-sm text-ink-blue-3 hover:underline" @click="navigate('applications')">View all</button>
                </div>
                <div v-if="allApps.loading" class="flex h-12 items-center justify-center">
                  <LoadingIndicator class="h-4 w-4 text-ink-gray-4" />
                </div>
                <div v-else class="space-y-2">
                  <div
                    v-for="app in inProgressApps"
                    :key="app.name"
                    class="cursor-pointer rounded-lg border border-outline-gray-2 bg-surface-white p-4 hover:border-outline-gray-3"
                    @click="selectedApp = app; activeView = 'app-detail'"
                  >
                    <div class="flex items-start justify-between gap-4">
                      <div>
                        <p class="text-base font-medium text-ink-gray-9">{{ app.borrower_name }}</p>
                        <p class="text-sm text-ink-gray-5">{{ app.facility_type }} · {{ formatAmount(app.requested_amount) }}</p>
                      </div>
                      <Badge :label="app.stage_label" theme="blue" variant="subtle" />
                    </div>
                    <div class="mt-3 flex gap-0.5">
                      <div v-for="i in 8" :key="i" class="h-1.5 flex-1 rounded-sm" :class="i <= app.stage_index ? 'bg-crm-teal' : 'bg-surface-gray-2'" />
                    </div>
                    <p class="mt-1 text-xs text-ink-gray-4">Stage {{ app.stage_index }} of 8</p>
                  </div>
                  <p v-if="!inProgressApps.length" class="text-sm text-ink-gray-4">No applications in progress</p>
                </div>
              </div>

              <div class="space-y-5">
                <div v-if="actionNeeded.length > 0" class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                  <div class="mb-2 flex items-center gap-2">
                    <FeatherIcon name="alert-circle" class="h-4 w-4 text-crm-warning" />
                    <p class="text-base font-medium text-ink-gray-9">Action Needed</p>
                  </div>
                  <p class="text-sm text-ink-gray-6">{{ actionNeeded[0].label }}</p>
                  <Button class="mt-3 w-full" size="sm" variant="outline" label="Upload Documents" @click="navigate('documents')" />
                </div>

                <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                  <p class="mb-3 text-xs font-medium uppercase tracking-wider text-ink-gray-4">Quick Actions</p>
                  <div class="space-y-0.5">
                    <button
                      v-for="a in QUICK_ACTIONS"
                      :key="a.label"
                      class="flex w-full items-center gap-2 rounded-md px-2 py-2 text-base text-ink-gray-7 hover:bg-surface-gray-2"
                      @click="a.fn()"
                    >
                      <FeatherIcon :name="a.icon" class="h-4 w-4 text-ink-gray-4" />
                      {{ a.label }}
                    </button>
                  </div>
                </div>

                <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                  <p class="mb-3 text-xs font-medium uppercase tracking-wider text-ink-gray-4">Relationship Manager</p>
                  <div class="flex items-center gap-3">
                    <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-crm-teal text-sm font-bold text-white">{{ rm.initials }}</div>
                    <div>
                      <p class="text-base font-medium text-ink-gray-9">{{ rm.name }}</p>
                      <p class="text-sm text-ink-gray-5">{{ rm.role }}</p>
                    </div>
                  </div>
                  <Button class="mt-3 w-full" size="sm" variant="outline" label="Send Message" @click="navigate('tickets')" />
                </div>
              </div>
            </div>
          </template>
        </template>

        <!-- ── APPLICATIONS LIST ──────────────────── -->
        <template v-else-if="activeView === 'applications'">
          <div v-if="allApps.loading" class="flex h-48 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>
          <div v-else-if="applicationRows.length" class="overflow-hidden rounded-lg border border-outline-gray-2 bg-surface-white">
            <table class="w-full text-base">
              <thead>
                <tr class="border-b border-outline-gray-2 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                  <th class="px-4 py-3">Borrower</th>
                  <th class="px-4 py-3">Facility</th>
                  <th class="px-4 py-3 text-right">Amount</th>
                  <th class="px-4 py-3">Stage</th>
                  <th class="px-4 py-3">Status</th>
                  <th class="px-4 py-3">Progress</th>
                  <th class="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1">
                <tr
                  v-for="app in applicationRows"
                  :key="app.name"
                  class="cursor-pointer hover:bg-surface-gray-1"
                  @click="selectedApp = app; activeView = 'app-detail'"
                >
                  <td class="px-4 py-3">
                    <p class="font-medium text-ink-gray-9">{{ app.borrower_name }}</p>
                    <p class="text-xs text-ink-gray-4">{{ app.name }}</p>
                  </td>
                  <td class="px-4 py-3 text-ink-gray-7">{{ app.facility_type }}</td>
                  <td class="px-4 py-3 text-right font-mono text-ink-gray-7">{{ formatAmount(app.requested_amount) }}</td>
                  <td class="px-4 py-3 text-ink-gray-5">{{ app.stage_index }}/8</td>
                  <td class="px-4 py-3">
                    <Badge :label="app.stage_label" :theme="stageBadgeTheme(app.status)" variant="subtle" />
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex w-20 gap-0.5">
                      <div v-for="i in 8" :key="i" class="h-1.5 flex-1 rounded-sm" :class="i <= app.stage_index ? 'bg-crm-teal' : 'bg-surface-gray-2'" />
                    </div>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <div class="flex items-center justify-end gap-2">
                      <Button size="sm" variant="subtle" label="Edit" @click.stop="openEditApp(app)" />
                      <Button size="sm" variant="subtle" theme="red" label="Cancel" @click.stop="cancelApplication(app)" />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="flex h-48 flex-col items-center justify-center text-ink-gray-4">
            <FeatherIcon name="file-text" class="mb-2 h-8 w-8" />
            <p class="text-base">No applications found</p>
            <Button class="mt-3" size="sm" variant="solid" label="Submit New Application" @click="openNewApplication" />
          </div>
        </template>

        <!-- ── APPLICATION DETAIL ────────────────── -->
        <template v-else-if="activeView === 'app-detail' && selectedApp">
	          <div class="grid gap-5 lg:grid-cols-3">
	            <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-5 lg:col-span-2">
              <p class="mb-4 text-base font-medium text-ink-gray-9">Application Progress</p>
              <div>
                <div v-for="(stage, idx) in STAGES" :key="stage" class="flex gap-4">
                  <div class="flex flex-col items-center">
                    <div
                      class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
                      :class="stageCircleClass(idx + 1, selectedApp.stage_index)"
                    >
                      <FeatherIcon v-if="idx + 1 < selectedApp.stage_index" name="check" class="h-3.5 w-3.5" />
                      <span v-else>{{ idx + 1 }}</span>
                    </div>
                    <div
                      v-if="idx < STAGES.length - 1"
                      class="my-1 w-px flex-1"
                      style="min-height:18px"
                      :class="idx + 1 < selectedApp.stage_index ? 'bg-crm-teal' : 'bg-outline-gray-2'"
                    />
                  </div>
                  <div class="pb-4 pt-0.5">
                    <p
                      class="text-base"
                      :class="idx + 1 === selectedApp.stage_index ? 'font-medium text-ink-gray-9' : 'text-ink-gray-4'"
                    >{{ stage }}</p>
	                    <p v-if="idx + 1 === selectedApp.stage_index" class="mt-0.5 text-sm text-ink-gray-5">{{ selectedApp.current_stage_detail || 'Currently in progress' }}</p>
                    <p v-else-if="idx + 1 < selectedApp.stage_index" class="mt-0.5 text-xs text-ink-gray-3">Completed</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="space-y-4">
              <div v-if="selectedApp.status === 'Document Review'" class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                <div class="mb-2 flex items-center gap-2">
                  <FeatherIcon name="alert-circle" class="h-4 w-4 text-crm-warning" />
                  <p class="text-base font-medium text-ink-gray-9">Action Required</p>
                </div>
                <p class="text-sm text-ink-gray-6">Documents are pending. Upload missing files to continue.</p>
	                <Button class="mt-3 w-full" size="sm" variant="solid" label="Upload Documents" @click="docApplicationName = selectedApp.name; navigate('documents')" />
              </div>

              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                <p class="mb-3 text-xs font-medium uppercase tracking-wider text-ink-gray-4">Details</p>
                <div class="space-y-2">
                  <div class="flex justify-between text-base">
                    <span class="text-ink-gray-5">Application No</span>
                    <span class="font-mono text-xs text-ink-gray-9">{{ selectedApp.name }}</span>
                  </div>
                  <div class="flex justify-between text-base">
                    <span class="text-ink-gray-5">Facility Type</span>
                    <span class="font-medium text-ink-gray-9">{{ selectedApp.facility_type }}</span>
                  </div>
                  <div class="flex justify-between text-base">
                    <span class="text-ink-gray-5">Requested</span>
                    <span class="font-medium text-ink-gray-9">{{ formatAmount(selectedApp.requested_amount) }}</span>
                  </div>
	                  <div class="flex justify-between text-base">
	                    <span class="text-ink-gray-5">Stage</span>
	                    <span class="font-medium text-ink-gray-9">{{ selectedApp.stage_index }} of 8</span>
	                  </div>
	                  <div class="flex justify-between text-base">
	                    <span class="text-ink-gray-5">ETA</span>
	                    <span class="font-medium text-ink-gray-9">{{ formatDate(selectedApp.eta_date) }}</span>
	                  </div>
                </div>
              </div>

              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                <p class="text-sm text-ink-gray-5">Need help with your application?</p>
                <Button class="mt-2 w-full" size="sm" variant="outline" label="Contact Support" @click="navigate('tickets')" />
              </div>

              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                <p class="mb-2 text-xs font-medium uppercase tracking-wider text-ink-gray-4">Actions</p>
                <div class="space-y-2">
                  <Button
                    class="w-full"
                    size="sm"
                    variant="outline"
                    label="Advance Stage"
                    :disabled="selectedApp.stage_index >= 8"
                    @click="advanceApplication"
                  />
                  <Button
                    class="w-full"
                    size="sm"
                    variant="solid"
                    label="Complete Application"
                    :disabled="selectedApp.stage_index >= 8"
                    @click="completeApplication"
                  />
                  <Button
                    class="w-full"
                    size="sm"
                    variant="outline"
                    label="Edit Application"
                    @click="openEditApp(selectedApp)"
                  />
                  <Button
                    class="w-full"
                    size="sm"
                    variant="subtle"
                    theme="red"
                    label="Cancel Application"
                    @click="cancelApplication(selectedApp)"
                  />
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ── FACILITIES LIST ───────────────────── -->
        <template v-else-if="activeView === 'facilities'">
          <div v-if="facilities.loading" class="flex h-48 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>
	          <div v-else-if="facilities.data?.length" class="grid gap-4 md:grid-cols-2">
            <div
              v-for="f in facilities.data"
              :key="f.name"
              class="cursor-pointer rounded-lg border border-outline-gray-2 bg-surface-white p-5 hover:border-outline-gray-3"
              @click="loadFacility(f.name)"
            >
              <div class="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-4">
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <Badge :label="f.facility_type" theme="teal" variant="subtle" />
                    <Badge label="Active" theme="green" variant="subtle" />
                  </div>
                  <p class="mt-3 truncate text-base font-medium leading-5 text-ink-gray-9">{{ f.customer }}</p>
                  <p class="mt-1 truncate text-sm leading-5 text-ink-gray-5">{{ f.product_type }}</p>
                </div>
                <FeatherIcon name="chevron-right" class="mt-1 h-4 w-4 text-ink-gray-4" />
              </div>
              <div class="mt-6">
                <div class="mb-2 flex items-center justify-between gap-4 text-sm leading-5">
                  <span>Outstanding</span>
                  <span class="font-medium text-ink-gray-9">{{ formatAmount(f.outstanding) }}</span>
                </div>
                <div class="h-1.5 overflow-hidden rounded-full bg-surface-gray-2">
                  <div class="h-full rounded-full bg-crm-teal" :style="{ width: pct(f.outstanding, f.limit_amount) + '%' }" />
                </div>
                <div class="mt-2 flex items-center justify-between gap-4 text-sm leading-5 text-ink-gray-4">
                  <span>Limit: {{ formatAmount(f.limit_amount) }}</span>
                  <span>{{ pct(f.outstanding, f.limit_amount) }}% used</span>
                </div>
                <div
                  class="mt-5 flex items-center justify-between gap-4 rounded-md px-4 py-3"
                  :class="isDueSoon(f.due_date) ? 'bg-surface-gray-2' : 'bg-surface-gray-1'"
                >
                  <span class="text-sm leading-5 text-ink-gray-5">Next payment due</span>
                  <span class="text-sm font-medium leading-5" :class="isDueSoon(f.due_date) ? 'text-crm-warning' : 'text-ink-gray-7'">{{ formatDate(f.due_date) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="flex h-48 flex-col items-center justify-center text-ink-gray-4">
            <FeatherIcon name="credit-card" class="mb-2 h-8 w-8" />
            <p class="text-base">No active facilities</p>
          </div>
        </template>

        <!-- ── FACILITY DETAIL ───────────────────── -->
        <template v-else-if="activeView === 'facility-detail' && selectedFacility">
	          <div class="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
              <p class="text-sm text-ink-gray-5">Outstanding Balance</p>
              <p class="mt-1 text-xl font-semibold text-ink-gray-9">{{ formatAmount(selectedFacility.outstanding) }}</p>
              <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-surface-gray-2">
                <div class="h-full rounded-full bg-crm-teal" :style="{ width: pct(selectedFacility.outstanding, selectedFacility.limit_amount) + '%' }" />
              </div>
              <p class="mt-1 text-xs text-ink-gray-4">of {{ formatAmount(selectedFacility.limit_amount) }} limit</p>
            </div>
            <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
              <p class="text-sm text-ink-gray-5">Facility Type</p>
              <p class="mt-1 text-xl font-semibold text-ink-gray-9">{{ selectedFacility.facility_type }}</p>
	              <p class="mt-1 text-xs text-ink-gray-4">
	                {{ selectedFacility.product_type }}
	                <span v-if="selectedFacility.rate"> · {{ selectedFacility.rate }}</span>
	                <span v-if="selectedFacility.tenor"> · {{ selectedFacility.tenor }}</span>
	              </p>
            </div>
            <div class="rounded-lg border border-outline-gray-2 p-4" :class="isDueSoon(selectedFacility.due_date) ? 'bg-surface-gray-2' : 'bg-surface-white'">
              <p class="text-sm text-ink-gray-5">Next Payment Due</p>
              <p class="mt-1 text-xl font-semibold" :class="isDueSoon(selectedFacility.due_date) ? 'text-crm-warning' : 'text-ink-gray-9'">
                {{ formatDate(selectedFacility.due_date) }}
              </p>
              <p class="mt-1 text-xs text-ink-gray-4">{{ daysUntil(selectedFacility.due_date) }}</p>
            </div>
            <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
              <p class="text-sm text-ink-gray-5">Account Health</p>
              <p class="mt-1 text-xl font-semibold text-green-600">{{ selectedFacility.health || 'Good' }}</p>
            </div>
          </div>

          <div id="print-area" class="overflow-hidden rounded-lg border border-outline-gray-2 bg-surface-white">
            <div class="border-b border-outline-gray-2 px-4 py-3 text-base font-medium text-ink-gray-9">Payment Schedule</div>
            <div v-if="facilityDetail.loading" class="flex h-20 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else class="overflow-x-auto">
              <table class="w-full text-base">
                <thead>
                  <tr class="border-b border-outline-gray-2 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                    <th class="px-4 py-3">#</th>
                    <th class="px-4 py-3">Due Date</th>
                    <th class="px-4 py-3 text-right">Principal</th>
                    <th class="px-4 py-3 text-right">Interest</th>
                    <th class="px-4 py-3 text-right">Total</th>
                    <th class="px-4 py-3 text-center">Status</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-outline-gray-1">
                  <tr
                    v-for="row in paymentSchedule"
                    :key="row.no"
                    :class="row.status === 'Due' ? 'bg-surface-gray-1' : row.status === 'Paid' ? 'opacity-50' : ''"
                  >
                    <td class="px-4 py-3 text-ink-gray-4">{{ row.no }}</td>
                    <td class="px-4 py-3 font-medium text-ink-gray-9">{{ formatDate(row.due_date) }}</td>
                    <td class="px-4 py-3 text-right font-mono text-ink-gray-7">{{ formatAmount(row.principal) }}</td>
                    <td class="px-4 py-3 text-right font-mono text-ink-gray-7">{{ formatAmount(row.interest) }}</td>
                    <td class="px-4 py-3 text-right font-mono font-semibold text-ink-gray-9">{{ formatAmount(row.total) }}</td>
                    <td class="px-4 py-3 text-center">
                      <Badge
                        :label="row.status"
                        :theme="row.status === 'Paid' ? 'green' : row.status === 'Due' ? 'orange' : 'gray'"
                        variant="subtle"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
	          </div>

	          <div class="mt-5 grid gap-5 lg:grid-cols-3">
	            <div class="overflow-hidden rounded-lg border border-outline-gray-2 bg-surface-white lg:col-span-2">
	              <div class="border-b border-outline-gray-2 px-4 py-3 text-base font-medium text-ink-gray-9">Payment History</div>
	              <div class="divide-y divide-outline-gray-1">
	                <div v-for="tx in paymentTransactions" :key="tx.name" class="flex items-center justify-between px-4 py-3">
	                  <div>
	                    <p class="text-base font-medium text-ink-gray-9">{{ tx.transaction_type }}</p>
	                    <p class="text-sm text-ink-gray-4">{{ formatDate(tx.transaction_date) }}</p>
	                  </div>
	                  <div class="text-right">
	                    <p class="font-mono text-base text-ink-gray-8">{{ formatAmount(tx.amount) }}</p>
	                    <Badge :label="tx.status" :theme="tx.status === 'Posted' ? 'green' : tx.status === 'Failed' ? 'red' : 'orange'" variant="subtle" />
	                  </div>
	                </div>
	                <p v-if="!paymentTransactions.length" class="px-4 py-6 text-sm text-ink-gray-4">No payment history yet</p>
	              </div>
	            </div>
	            <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
	              <p class="mb-3 text-xs font-medium uppercase tracking-wider text-ink-gray-4">Statements</p>
	              <select v-model="statementPeriod" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base text-ink-gray-8 focus:outline-none">
	                <option v-for="period in statementOptions" :key="period.value" :value="period.value">{{ period.label }}</option>
	              </select>
	              <Button class="mt-3 w-full" size="sm" variant="solid" label="Download PDF" :loading="statementDownloading" @click="downloadStatement" />
	              <Button class="mt-2 w-full" size="sm" variant="outline" label="Print Schedule" @click="printSchedule" />
	            </div>
	          </div>
	        </template>

        <!-- ── DOCUMENTS ─────────────────────────── -->
        <template v-else-if="activeView === 'documents'">
          <div v-if="docs.loading" class="flex h-48 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>
          <template v-else-if="documentRows.length">
	            <div class="mb-4 grid gap-3 md:grid-cols-4">
              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4 text-center">
                <p class="text-2xl font-semibold text-green-600">{{ documentRows.filter(d => d.status_label === 'Approved').length }}</p>
                <p class="mt-0.5 text-sm text-ink-gray-5">Approved</p>
              </div>
              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4 text-center">
                <p class="text-2xl font-semibold text-red-500">{{ documentRows.filter(d => d.status_label === 'Rejected').length }}</p>
                <p class="mt-0.5 text-sm text-ink-gray-5">Rejected</p>
              </div>
	              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4 text-center">
	                <p class="text-2xl font-semibold text-ink-gray-7">{{ documentRows.filter(d => d.status_label === 'Pending Upload').length }}</p>
	                <p class="mt-0.5 text-sm text-ink-gray-5">Pending Upload</p>
	              </div>
	              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4 text-center">
	                <p class="text-2xl font-semibold text-blue-600">{{ documentRows.filter(d => d.status_label === 'Pending Review').length }}</p>
	                <p class="mt-0.5 text-sm text-ink-gray-5">Pending Review</p>
	              </div>
            </div>

            <div class="overflow-hidden rounded-lg border border-outline-gray-2 bg-surface-white">
              <div class="border-b border-outline-gray-2 px-4 py-3">
                <span class="text-base font-medium text-ink-gray-9">Document Checklist</span>
                <span v-if="docApplicationName" class="ml-2 font-mono text-xs text-ink-gray-4">{{ docApplicationName }}</span>
              </div>
              <div class="divide-y divide-outline-gray-1">
                <div v-for="doc in documentRows" :key="doc.name" class="flex items-start justify-between gap-4 px-4 py-3">
                  <div class="flex min-w-0 flex-1 items-start gap-3">
                    <div
                      class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md"
                      :class="doc.status_label === 'Approved' ? 'bg-surface-gray-2' : doc.status_label === 'Rejected' ? 'bg-surface-gray-2' : 'bg-surface-gray-2'"
                    >
                      <FeatherIcon
                        :name="doc.status_label === 'Approved' ? 'check' : doc.status_label === 'Rejected' ? 'x' : 'upload'"
                        class="h-3.5 w-3.5"
                        :class="doc.status_label === 'Approved' ? 'text-green-600' : doc.status_label === 'Rejected' ? 'text-red-500' : 'text-ink-gray-4'"
                      />
                    </div>
                    <div class="min-w-0">
                      <p class="text-base font-medium text-ink-gray-9">{{ doc.title }}</p>
	                      <p class="text-sm text-ink-gray-5">{{ doc.document_type }}</p>
	                      <p v-if="doc.file_name" class="mt-0.5 text-xs text-ink-gray-4">{{ doc.file_name }}</p>
	                      <p v-if="doc.notes" class="mt-0.5 text-xs" :class="doc.status_label === 'Rejected' ? 'text-red-500' : 'text-ink-gray-5'">{{ doc.notes }}</p>
                    </div>
                  </div>
                  <div class="flex shrink-0 items-center gap-2">
                    <Badge
                      :label="doc.status_label"
	                      :theme="doc.status_label === 'Approved' ? 'green' : doc.status_label === 'Rejected' ? 'red' : doc.status_label === 'Pending Review' ? 'blue' : 'gray'"
                      variant="subtle"
                    />
                    <label
                      v-if="doc.status_label !== 'Approved'"
                      class="flex cursor-pointer items-center gap-1.5 rounded-md border border-outline-gray-2 px-2.5 py-1 text-sm text-ink-gray-7 hover:bg-surface-gray-1"
                    >
                      <FeatherIcon name="upload" class="h-3.5 w-3.5" />
	                      <input type="file" accept="image/*,.pdf" class="hidden" @change="(e) => uploadDoc(e, doc)" />
                      {{ uploading === doc.name ? 'Uploading…' : doc.status_label === 'Rejected' ? 'Re-upload' : 'Upload' }}
                    </label>
                    <Button
                      v-if="doc.status_label === 'Pending Review'"
                      size="sm"
                      variant="subtle"
                      label="Approve"
                      @click="approveDoc(doc)"
                    />
                    <Button
                      size="sm"
                      variant="ghost"
                      label="Delete"
                      @click="deleteDocument(doc)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="flex h-48 flex-col items-center justify-center text-ink-gray-4">
            <FeatherIcon name="upload-cloud" class="mb-2 h-8 w-8" />
            <p class="text-base">No documents yet</p>
            <Button class="mt-3" size="sm" variant="solid" label="Upload Document" @click="openNewDocument" />
          </div>
        </template>

        <!-- ── SUPPORT ────────────────────────────── -->
        <template v-else-if="activeView === 'tickets'">
	          <div class="grid gap-5 lg:grid-cols-3">
	            <div class="lg:col-span-2">
              <div class="mb-4 flex gap-1 rounded-md border border-outline-gray-2 bg-surface-gray-1 p-1 w-fit">
                <button
                  v-for="tab in ['my', 'new']"
                  :key="tab"
                  class="rounded px-3 py-1 text-base transition-colors"
                  :class="ticketTab === tab ? 'bg-surface-white font-medium text-ink-gray-9 shadow-sm' : 'text-ink-gray-5 hover:text-ink-gray-8'"
                  @click="ticketTab = tab"
                >
                  {{ tab === 'my' ? 'My Tickets' : 'New Ticket' }}
                </button>
              </div>

              <div v-if="ticketTab === 'my'">
                <div v-if="tickets.loading" class="flex h-32 items-center justify-center">
                  <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
                </div>
                <div v-else-if="ticketRows.length" class="space-y-2">
                  <div v-for="t in ticketRows" :key="t.name" class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                    <div class="flex items-start justify-between gap-4">
                      <div class="min-w-0 flex-1">
                        <p class="text-base font-medium text-ink-gray-9">{{ t.subject }}</p>
                        <p class="mt-0.5 text-sm text-ink-gray-4">{{ t.name }} · {{ formatDate(t.creation) }}</p>
                        <p v-if="t.sla" class="mt-1 text-xs text-ink-gray-5">{{ t.sla }}</p>
                      </div>
                      <div class="flex shrink-0 items-center gap-2">
                        <Badge
                          :label="t.status"
                          :theme="t.status === 'Resolved' || t.status === 'Closed' ? 'green' : t.status === 'Open' ? 'blue' : 'orange'"
                          variant="subtle"
                        />
                        <Button
                          v-if="t.status !== 'Closed' && t.status !== 'Resolved'"
                          size="sm"
                          variant="subtle"
                          label="Close"
                          @click="closeTicket(t)"
                        />
                        <Button size="sm" variant="ghost" label="Edit" @click="openEditTicket(t)" />
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="flex h-32 flex-col items-center justify-center rounded-lg border border-outline-gray-2 text-ink-gray-4">
                  <FeatherIcon name="inbox" class="mb-2 h-6 w-6" />
                  <p class="text-base">No tickets yet</p>
                </div>
              </div>

              <div v-else class="rounded-lg border border-outline-gray-2 bg-surface-white p-5">
                <div class="space-y-4">
                  <div>
                    <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Category</label>
                    <select
                      v-model="ticketForm.category"
                      class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base text-ink-gray-8 focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
                    >
                      <option value="">Select a category</option>
                      <option v-for="c in TICKET_CATEGORIES" :key="c">{{ c }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Subject</label>
                    <input
                      v-model="ticketForm.subject"
                      type="text"
                      placeholder="Briefly describe your issue"
                      class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
                    />
                  </div>
	                  <div>
	                    <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Description</label>
                    <textarea
                      v-model="ticketForm.description"
                      rows="4"
                      placeholder="Provide details so we can help you faster"
                      class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
	                    />
	                  </div>
	                  <div>
	                    <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Attachment</label>
	                    <input
	                      type="file"
	                      class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:outline-none"
	                      @change="(e) => ticketAttachment = e.target.files?.[0] || null"
	                    />
	                  </div>
                  <Button
                    variant="solid"
                    label="Submit Ticket"
                    :loading="ticketSubmitting"
                    :disabled="!ticketForm.subject || !ticketForm.category"
                    @click="submitTicket"
                  >
                    <template #prefix><FeatherIcon name="send" class="h-4 w-4" /></template>
                  </Button>
                </div>
              </div>
            </div>

            <div class="space-y-4">
              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                <p class="mb-3 text-xs font-medium uppercase tracking-wider text-ink-gray-4">Your RM</p>
                <div class="flex items-center gap-3">
	                  <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-crm-teal text-sm font-bold text-white">{{ rm.initials }}</div>
	                  <div>
	                    <p class="text-base font-medium text-ink-gray-9">{{ rm.name }}</p>
	                    <p class="text-sm text-ink-gray-5">{{ rm.phone }}</p>
	                  </div>
	                </div>
	                <Button class="mt-3 w-full" size="sm" variant="outline" label="Open WhatsApp" @click="openWa" />
	              </div>
              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                <p class="mb-3 text-xs font-medium uppercase tracking-wider text-ink-gray-4">Common Issues</p>
                <div class="space-y-2 text-sm text-ink-gray-6">
                  <p class="cursor-pointer hover:text-ink-blue-3" @click="ticketForm.category='Installment Payment'; ticketForm.subject='Question about my payment schedule'; ticketTab='new'">
                    → How do I check my payment schedule?
                  </p>
                  <p class="cursor-pointer hover:text-ink-blue-3" @click="ticketForm.category='Documents'; ticketForm.subject='My uploaded document was rejected'; ticketTab='new'">
                    → My document was rejected, what should I do?
                  </p>
                  <p class="cursor-pointer hover:text-ink-blue-3" @click="ticketForm.category='Disbursement'; ticketForm.subject='Question about disbursement timeline'; ticketTab='new'">
                    → When will my loan be disbursed?
                  </p>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ── TOP-UP ─────────────────────────────── -->
        <template v-else-if="activeView === 'topup'">
	          <div class="grid gap-5 lg:grid-cols-2">
            <div>
              <div v-if="topupSubmitted" class="rounded-lg border border-outline-gray-2 bg-surface-white p-8 text-center">
                <FeatherIcon name="check-circle" class="mx-auto mb-3 h-10 w-10 text-green-500" />
                <p class="text-base font-medium text-ink-gray-9">Request Submitted</p>
                <p class="mt-1 text-sm text-ink-gray-5">Your top-up is under review by the credit team.</p>
                <p class="mt-1 font-mono text-xs text-ink-gray-4">{{ topupAppName }}</p>
                <div class="mt-4 flex justify-center gap-2">
                  <Button variant="solid" size="sm" label="Track Application" @click="viewTopupApp" />
                  <Button variant="outline" size="sm" label="Back to Facilities" @click="navigate('facilities')" />
                </div>
              </div>
              <div v-else class="rounded-lg border border-outline-gray-2 bg-surface-white p-5">
                <div v-if="topupFacility" class="mb-4 rounded-md bg-surface-gray-1 p-3">
                  <p class="text-xs text-ink-gray-5">Facility</p>
                  <p class="text-base font-medium text-ink-gray-9">{{ topupFacility.facility_type }} — {{ topupFacility.customer }}</p>
                  <p class="text-sm text-ink-gray-5">Outstanding: {{ formatAmount(topupFacility.outstanding) }}</p>
                </div>
                <div class="space-y-4">
                  <div>
                    <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Requested Top-Up Amount</label>
                    <div class="flex items-center gap-2 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 focus-within:border-outline-gray-4 focus-within:bg-surface-white">
                      <span class="shrink-0 text-base text-ink-gray-5">Rp</span>
                      <input
                        v-model="topupAmount"
                        type="number"
                        min="0"
                        placeholder="500,000,000"
                        class="flex-1 bg-transparent py-2 text-base focus:outline-none"
                      />
                    </div>
                    <p v-if="topupAmount" class="mt-1 text-xs text-ink-gray-5">{{ formatAmount(Number(topupAmount)) }}</p>
                  </div>
                  <div>
                    <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Purpose</label>
                    <textarea
                      v-model="topupPurpose"
                      rows="4"
                      placeholder="Describe what the additional funds will be used for"
                      class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
                    />
                  </div>
	                  <Button
	                    class="w-full"
	                    variant="solid"
	                    label="Submit Top-Up Request"
	                    :loading="topupSubmitting"
	                    :disabled="!topupFacility || !topupAmount || !topupPurpose"
	                    @click="submitTopup"
	                  />
                </div>
              </div>
            </div>
            <div class="space-y-4">
              <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4">
                <p class="mb-3 text-xs font-medium uppercase tracking-wider text-ink-gray-4">What Happens Next</p>
                <div class="space-y-3">
                  <div v-for="(step, i) in TOPUP_STEPS" :key="i" class="flex gap-3">
                    <div class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-surface-gray-2 text-xs font-semibold text-ink-gray-7">{{ i + 1 }}</div>
                    <p class="text-sm text-ink-gray-6">{{ step }}</p>
                  </div>
                </div>
              </div>
              <div class="rounded-lg border border-outline-gray-2 bg-surface-gray-1 p-4 text-sm text-ink-gray-6">
                <p class="font-medium text-ink-gray-8">Note</p>
                <p class="mt-1">Top-up requests are subject to credit review. Processing typically takes 5–7 business days.</p>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="activeView === 'profile'">
          <div class="grid gap-5 lg:grid-cols-3">
            <div class="lg:col-span-2 rounded-lg border border-outline-gray-2 bg-surface-white p-5">
              <h2 class="mb-4 text-base font-semibold text-ink-gray-9">My Profile</h2>
              <div class="space-y-4">
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Full Name</label>
                  <input v-model="profileForm.name" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none" />
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Address</label>
                  <textarea v-model="profileForm.address" rows="2" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none" />
                </div>
                <div class="grid gap-4 md:grid-cols-2">
                  <div>
                    <label class="mb-1.5 flex items-center justify-between text-sm font-medium text-ink-gray-7">
                      <span>Email <span class="ml-1 rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium text-amber-700">OTP</span></span>
                    </label>
                    <input v-model="profileForm.email" type="email" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base" />
                  </div>
                  <div>
                    <label class="mb-1.5 flex items-center justify-between text-sm font-medium text-ink-gray-7">
                      <span>Phone <span class="ml-1 rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium text-amber-700">OTP</span></span>
                    </label>
                    <input v-model="profileForm.phone" type="tel" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base" />
                  </div>
                </div>
                <div v-if="profileOtpStep" class="rounded-md border border-amber-200 bg-amber-50 p-3">
                  <p class="text-sm font-medium text-amber-900">Verify it's you</p>
                  <p class="text-xs text-amber-800 mt-0.5">We sent a 6-digit code to {{ profileOtpTarget }}. Enter it to save sensitive changes.</p>
                  <div class="mt-2 flex items-center gap-2">
                    <input v-model="profileOtp" maxlength="6" placeholder="123456" class="w-32 rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-center font-mono tracking-widest" />
                    <Button size="sm" variant="solid" label="Verify & Save" :loading="profileSaving" @click="verifyProfileOtp" />
                    <Button size="sm" variant="ghost" label="Cancel" @click="profileOtpStep = false" />
                  </div>
                </div>
                <div v-else class="flex gap-2">
                  <Button variant="solid" :loading="profileSaving" label="Save Changes" @click="saveProfile" />
                  <Button variant="outline" label="Reset" @click="resetProfile" />
                </div>
              </div>
            </div>
            <div class="rounded-lg border border-outline-gray-2 bg-surface-gray-1 p-5 text-sm text-ink-gray-6">
              <p class="font-medium text-ink-gray-8">Security</p>
              <p class="mt-2">Changes to your email and phone require a one-time code (OTP) sent to your existing contact. Other fields save immediately.</p>
              <p class="mt-3 text-xs text-ink-gray-5">Last updated: {{ profileLastUpdated }}</p>
            </div>
            <div class="rounded-lg border border-outline-gray-2 bg-surface-gray-1 p-5 text-sm text-ink-gray-6 md:col-span-3">
              <p class="font-medium text-ink-gray-8 mb-2">Notification Preferences</p>
              <div v-for="p in notifPrefs" :key="p.type" class="flex items-center justify-between border-t border-outline-gray-1 first:border-t-0 py-2">
                <span>{{ p.label }}</span>
                <div class="flex gap-3 text-xs">
                  <label class="flex items-center gap-1"><input type="checkbox" v-model="p.email" /> Email</label>
                  <label class="flex items-center gap-1"><input type="checkbox" v-model="p.sms" /> SMS</label>
                  <label class="flex items-center gap-1"><input type="checkbox" v-model="p.push" /> Push</label>
                </div>
              </div>
              <Button class="mt-3" size="sm" variant="outline" label="Save Preferences" @click="saveNotifPrefs" />
            </div>
          </div>
        </template>

        <template v-else-if="activeView === 'restructure'">
          <div class="grid gap-5 lg:grid-cols-[1fr_320px]">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-5">
              <h2 class="text-base font-semibold text-ink-gray-9 mb-3">Restructure Request</h2>
              <div class="space-y-4">
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Facility</label>
                  <select v-model="restructureForm.facility" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm">
                    <option v-for="f in (facilities.data || [])" :key="f.name" :value="f.name">{{ f.facility_type }} — {{ formatAmount(f.outstanding) }}</option>
                  </select>
                </div>
                <div class="grid gap-3 md:grid-cols-2">
                  <div>
                    <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Target Tenor (months)</label>
                    <input v-model.number="restructureForm.target_tenor" type="number" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm" />
                  </div>
                  <div>
                    <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Proposed Installment</label>
                    <input v-model.number="restructureForm.proposed_installment" type="number" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm" />
                  </div>
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Hardship Reason</label>
                  <textarea v-model="restructureForm.hardship" rows="4" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm" placeholder="Describe the financial hardship that necessitates restructuring" />
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Supporting Documents</label>
                  <input type="file" multiple class="text-sm" />
                </div>
                <div class="flex gap-2">
                  <Button variant="solid" :loading="restructureSubmitting" :disabled="!restructureForm.facility || !restructureForm.hardship" label="Submit Restructure Request" @click="submitRestructure" />
                </div>
              </div>
            </div>
            <div class="rounded-lg border border-outline-gray-2 bg-surface-gray-1 p-4 text-sm text-ink-gray-6">
              <p class="font-medium text-ink-gray-8">Process</p>
              <ol class="mt-2 list-decimal pl-5 space-y-1">
                <li>Your RM reviews the request and supporting documents.</li>
                <li>Credit & risk teams reassess your facility.</li>
                <li>Committee approval if required.</li>
                <li>New schedule documented and signed.</li>
              </ol>
              <p class="mt-3 text-xs">Processing typically 7–14 business days.</p>
            </div>
          </div>
        </template>

        <template v-else-if="activeView === 'referral'">
          <div class="grid gap-5 lg:grid-cols-[1fr_320px]">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-5">
              <h2 class="text-base font-semibold text-ink-gray-9 mb-3">Refer a friend, earn rewards</h2>
              <p class="text-sm text-ink-gray-6">Share your referral code below. When someone you refer becomes a customer, you both receive a reward.</p>
              <div class="mt-4 rounded-md border border-dashed border-crm-teal bg-teal-50 p-4">
                <p class="text-xs uppercase text-ink-gray-5 tracking-wider">Your code</p>
                <p class="text-3xl font-bold font-mono text-crm-teal">{{ referralCode }}</p>
                <Button class="mt-3" size="sm" variant="outline" label="Copy" @click="copyReferral" />
              </div>
              <div class="mt-4 flex gap-2">
                <Button size="sm" variant="outline" label="Share via WhatsApp" @click="shareReferral('whatsapp')" />
                <Button size="sm" variant="outline" label="Share via Email" @click="shareReferral('email')" />
                <Button size="sm" variant="outline" label="Copy Link" @click="shareReferral('link')" />
              </div>
            </div>
            <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-5">
              <h3 class="text-sm font-semibold text-ink-gray-8 mb-3">Referral History</h3>
              <div v-for="r in referrals" :key="r.id" class="flex justify-between items-start py-2 border-t border-outline-gray-1 first:border-t-0">
                <div>
                  <p class="text-sm font-medium text-ink-gray-9">{{ r.name }}</p>
                  <p class="text-xs text-ink-gray-5">{{ formatDate(r.referred_at) }}</p>
                </div>
                <Badge :label="r.status" :theme="r.status === 'Converted' ? 'green' : r.status === 'Pending' ? 'orange' : 'gray'" variant="subtle" />
              </div>
              <p v-if="!referrals.length" class="text-xs text-ink-gray-5">No referrals yet — share your code.</p>
            </div>
          </div>
        </template>

      </div>
    </div>

    <Dialog v-model="showNewAppDialog" :options="{ title: 'Submit New Credit Application' }">
      <template #body-content>
        <div class="space-y-4 pt-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Facility Type</label>
            <select
              v-model="newApp.facility_type"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base text-ink-gray-8 focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            >
              <option value="">Select a facility type</option>
              <option v-for="ft in FACILITY_TYPES" :key="ft">{{ ft }}</option>
            </select>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Borrower Type</label>
            <select
              v-model="newApp.borrower_type"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base text-ink-gray-8 focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            >
              <option value="Company">Company</option>
              <option value="Individual">Individual</option>
            </select>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Requested Amount</label>
            <div class="flex items-center gap-2 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 focus-within:border-outline-gray-4 focus-within:bg-surface-white">
              <span class="shrink-0 text-base text-ink-gray-5">Rp</span>
              <input
                v-model="newApp.requested_amount"
                type="text"
                inputmode="numeric"
                placeholder="1,000,000,000"
                class="flex-1 bg-transparent py-2 text-base focus:outline-none"
              />
            </div>
            <p v-if="requestedAmountValue" class="mt-1 text-xs text-ink-gray-5">{{ formatAmount(requestedAmountValue) }}</p>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Purpose</label>
            <textarea
              v-model="newApp.purpose"
              rows="3"
              placeholder="Describe the business purpose of this financing"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Additional Notes <span class="text-ink-gray-4">(optional)</span></label>
            <textarea
              v-model="newApp.notes"
              rows="2"
              placeholder="Any additional context for the credit team"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            />
          </div>
          <div class="rounded-md border border-blue-100 bg-blue-50 px-3 py-2 text-xs text-blue-700">
            After submission, a document checklist will be created. You can upload required files from the Documents tab.
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2">
          <Button variant="outline" label="Cancel" @click="showNewAppDialog = false" />
          <Button
            variant="solid"
            label="Submit Application"
            :loading="newAppSubmitting"
            :disabled="!canSubmitNewApplication"
            @click="submitNewApplication"
          />
        </div>
      </template>
    </Dialog>

    <!-- ── AI ASSISTANT ──────────────────────── -->
    <div class="pointer-events-none fixed bottom-5 right-5 z-50 flex flex-col items-end gap-3">
      <div
        v-if="assistantOpen"
        class="pointer-events-auto flex h-[520px] w-[380px] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-xl border border-outline-gray-2 bg-surface-white shadow-2xl"
      >
        <div class="flex items-center justify-between gap-2 border-b border-outline-gray-2 px-4 py-3" style="background: #008C95">
          <div class="flex items-center gap-2 text-white">
            <div class="flex h-7 w-7 items-center justify-center rounded-full bg-white/20">
              <FeatherIcon name="zap" class="h-4 w-4" />
            </div>
            <div>
              <p class="text-sm font-semibold leading-tight">Portal Assistant</p>
              <p class="text-xs text-white/80 leading-tight">AI-powered · always available</p>
            </div>
          </div>
          <button class="rounded p-1 text-white/80 hover:bg-white/10 hover:text-white" @click="assistantOpen = false">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>
        <div ref="assistantScrollRef" class="flex-1 space-y-3 overflow-y-auto bg-surface-gray-1 px-4 py-4">
          <div
            v-for="(msg, i) in assistantMessages"
            :key="i"
            class="flex"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[85%] whitespace-pre-line rounded-lg px-3 py-2 text-sm leading-relaxed"
              :class="msg.role === 'user'
                ? 'bg-crm-teal text-white'
                : 'border border-outline-gray-2 bg-surface-white text-ink-gray-8'"
            >
              {{ msg.content }}
            </div>
          </div>
          <div v-if="assistantLoading" class="flex justify-start">
            <div class="rounded-lg border border-outline-gray-2 bg-surface-white px-3 py-2 text-sm text-ink-gray-4">
              <span class="inline-block animate-pulse">Thinking…</span>
            </div>
          </div>
        </div>
        <div v-if="!assistantMessages.length" class="border-t border-outline-gray-2 bg-surface-white px-3 pt-3">
          <p class="mb-2 text-xs font-medium uppercase tracking-wider text-ink-gray-4">Suggested</p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="s in ASSISTANT_SUGGESTIONS"
              :key="s"
              class="rounded-full border border-outline-gray-2 bg-surface-gray-1 px-2.5 py-1 text-xs text-ink-gray-7 hover:bg-surface-gray-2"
              @click="askAssistant(s)"
            >{{ s }}</button>
          </div>
        </div>
        <div class="flex items-center gap-2 border-t border-outline-gray-2 bg-surface-white px-3 py-3">
          <input
            v-model="assistantInput"
            type="text"
            placeholder="Ask about payments, documents, status…"
            class="flex-1 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            :disabled="assistantLoading"
            @keydown.enter="askAssistant(assistantInput)"
          />
          <button
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-crm-teal text-white hover:opacity-90 disabled:opacity-50"
            :disabled="!assistantInput || assistantLoading"
            @click="askAssistant(assistantInput)"
          >
            <FeatherIcon name="send" class="h-4 w-4" />
          </button>
        </div>
      </div>
      <button
        class="pointer-events-auto flex h-14 w-14 items-center justify-center rounded-full text-white shadow-lg transition-transform hover:scale-105"
        style="background: #008C95"
        @click="assistantOpen = !assistantOpen"
      >
        <FeatherIcon :name="assistantOpen ? 'chevron-down' : 'message-circle'" class="h-6 w-6" />
      </button>
    </div>

    <Dialog v-model="showNewDocDialog" :options="{ title: 'Upload Document' }">
      <template #body-content>
        <div class="space-y-4 pt-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Title</label>
            <input
              v-model="newDoc.title"
              type="text"
              placeholder="e.g. Q3 2025 Bank Statement"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Document Type</label>
            <select
              v-model="newDoc.document_type"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base text-ink-gray-8 focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            >
              <option v-for="t in DOCUMENT_TYPES" :key="t">{{ t }}</option>
            </select>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">File</label>
            <input
              type="file"
              accept="image/*,.pdf"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:outline-none"
              @change="(e) => newDoc.file = e.target.files?.[0] || null"
            />
            <p v-if="newDoc.file" class="mt-1 text-xs text-ink-gray-5">{{ newDoc.file.name }}</p>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2">
          <Button variant="outline" label="Cancel" @click="showNewDocDialog = false" />
          <Button
            variant="solid"
            label="Upload"
            :loading="newDocSubmitting"
            :disabled="!newDoc.title || !newDoc.file"
            @click="submitNewDocument"
          />
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showEditAppDialog" :options="{ title: 'Edit Application' }">
      <template #body-content>
        <div class="space-y-4 pt-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Requested Amount</label>
            <div class="flex items-center gap-2 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 focus-within:border-outline-gray-4 focus-within:bg-surface-white">
              <span class="shrink-0 text-base text-ink-gray-5">Rp</span>
              <input
                v-model="editApp.requested_amount"
                type="number"
                min="0"
                class="flex-1 bg-transparent py-2 text-base focus:outline-none"
              />
            </div>
            <p v-if="editApp.requested_amount" class="mt-1 text-xs text-ink-gray-5">{{ formatAmount(Number(editApp.requested_amount)) }}</p>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Purpose</label>
            <textarea
              v-model="editApp.purpose"
              rows="3"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Notes</label>
            <textarea
              v-model="editApp.notes"
              rows="2"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2">
          <Button variant="outline" label="Cancel" @click="showEditAppDialog = false" />
          <Button
            variant="solid"
            label="Save"
            :loading="editAppSubmitting"
            @click="submitEditApp"
          />
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showEditTicketDialog" :options="{ title: 'Edit Ticket' }">
      <template #body-content>
        <div class="space-y-4 pt-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Subject</label>
            <input
              v-model="editTicket.subject"
              type="text"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Description</label>
            <textarea
              v-model="editTicket.description"
              rows="4"
              class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-base focus:border-outline-gray-4 focus:bg-surface-white focus:outline-none"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2">
          <Button variant="outline" label="Cancel" @click="showEditTicketDialog = false" />
          <Button
            variant="solid"
            label="Save"
            :loading="editTicketSubmitting"
            @click="submitEditTicket"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, h, nextTick, onMounted } from 'vue'
import { Badge, Button, Dialog, FeatherIcon, LoadingIndicator, call, createResource, toast } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const TICKET_CATEGORIES = ['Installment Payment', 'Documents', 'Disbursement', 'Profile Update', 'Other']
const FACILITY_TYPES = [
  'Working Capital Loan',
  'Investment Loan',
  'Term Loan',
  'Revolving Credit',
  'Trade Finance',
  'Invoice Financing',
  'Equipment Financing',
]
const DOCUMENT_TYPES = ['KYC', 'Financial', 'Collateral', 'Legal', 'Visit', 'Other']
const ASSISTANT_SUGGESTIONS = [
  'When is my next payment due?',
  'What documents do I still need?',
  'Show my application status',
  'How do I request a top-up?',
]
const STAGES = [
  'Application Received', 'Document Review', 'Credit Analysis',
  'Collateral Appraisal', 'Committee Approval', 'Legal Documentation',
  'Disbursement', 'Active',
]
const TABS = [
  { label: 'Dashboard', view: 'dashboard' },
  { label: 'Applications', view: 'applications' },
  { label: 'Facilities', view: 'facilities' },
  { label: 'Documents', view: 'documents' },
  { label: 'Support', view: 'tickets' },
  { label: 'Profile', view: 'profile' },
  { label: 'Referral', view: 'referral' },
]

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'id', label: 'Bahasa Indonesia' },
]
const TOPUP_STEPS = [
  'Your request is received and assigned to your RM for initial review.',
  'Credit team evaluates your request and existing facility performance.',
  'If approved, you will receive a notification and updated facility terms.',
  'Documents for the top-up will be prepared and sent for your signature.',
]
const QUICK_ACTIONS = [
  { label: 'View Payment Schedule', icon: 'calendar', fn: () => navigateToPaymentSchedule() },
  { label: 'Upload Documents', icon: 'upload-cloud', fn: () => navigate('documents') },
  { label: 'Request Top-Up', icon: 'trending-up', fn: () => { topupFacility.value = facilities.data?.[0]; navigate('topup') } },
  { label: 'Restructure', icon: 'refresh-cw', fn: () => { restructureForm.facility = facilities.data?.[0]?.name || ''; navigate('restructure') } },
  { label: 'Contact Support', icon: 'message-circle', fn: () => navigate('tickets') },
]

const activeView = ref('dashboard')
const selectedApp = ref(null)
const selectedFacility = ref(null)
const topupFacility = ref(null)

const ticketTab = ref('my')
const ticketSubmitting = ref(false)
const ticketForm = reactive({ category: '', subject: '', description: '' })
const ticketAttachment = ref(null)
const simulatedTickets = ref([])

const uploading = ref(null)
const docApplicationName = ref(null)
const simulatedDocs = ref([])

const topupAmount = ref('')
const topupPurpose = ref('')
const topupSubmitting = ref(false)
const topupSubmitted = ref(false)
const topupAppName = ref('')
const topupApp = ref(null)
const statementPeriod = ref('')
const statementDownloading = ref(false)
const simulatedApps = ref([])

const profileForm = reactive({ name: '', email: '', phone: '', address: '' })
const profileOriginal = reactive({ name: '', email: '', phone: '', address: '' })
const profileLastUpdated = ref('—')
const profileSaving = ref(false)
const profileOtpStep = ref(false)
const profileOtp = ref('')
const profileOtpTarget = ref('')

const language = ref(typeof window !== 'undefined' ? (localStorage.getItem('portalLang') || 'en') : 'en')
const notifPrefs = ref([
  { type: 'payment', label: 'Payment reminders', email: true, sms: true, push: true },
  { type: 'document', label: 'Document requests', email: true, sms: false, push: true },
  { type: 'application', label: 'Application updates', email: true, sms: false, push: true },
  { type: 'marketing', label: 'Marketing & offers', email: false, sms: false, push: false },
])
const restructureForm = reactive({ facility: '', target_tenor: 0, proposed_installment: 0, hardship: '' })
const restructureSubmitting = ref(false)
const referralCode = ref('')
const referrals = ref([])

const showNewAppDialog = ref(false)
const newAppSubmitting = ref(false)
const newApp = reactive({ facility_type: '', borrower_type: 'Company', requested_amount: '', purpose: '', notes: '' })

const assistantOpen = ref(false)
const assistantInput = ref('')
const assistantLoading = ref(false)
const assistantMessages = ref([])
const assistantScrollRef = ref(null)

const showNewDocDialog = ref(false)
const newDocSubmitting = ref(false)
const newDoc = reactive({ title: '', document_type: 'KYC', file: null })

const showEditAppDialog = ref(false)
const editAppSubmitting = ref(false)
const editApp = reactive({ name: '', requested_amount: '', purpose: '', notes: '' })

const showEditTicketDialog = ref(false)
const editTicketSubmitting = ref(false)
const editTicket = reactive({ name: '', subject: '', description: '' })

// ── Resources ────────────────────────────────────────────────────────────────

const portalContext = createResource({
  url: 'crm.api.portal.get_portal_context',
  params: { customer: null },
  auto: true,
})

const dashboard = createResource({
  url: 'crm.api.portal.get_portal_dashboard',
  params: { customer: null },
  auto: true,
})

const allApps = createResource({
  url: 'crm.api.portal.get_my_applications',
  params: { customer: null },
  auto: true,
})

const facilities = createResource({
  url: 'crm.api.portal.get_my_facilities',
  params: { customer: null },
  auto: true,
})

const facilityDetail = createResource({ url: 'crm.api.portal.get_facility_detail' })
const docs = createResource({
  url: 'crm.api.portal.get_document_checklist',
  params: { customer: null },
})

const tickets = createResource({
  url: 'crm.api.portal.get_my_tickets',
  params: { customer: null },
})

// ── Computed ─────────────────────────────────────────────────────────────────

const dueUrgent = computed(() => {
  const days = dashboard.data?.next_payment?.days_until
  return days != null && days <= 7
})

const inProgressApps = computed(() =>
  applicationRows.value.filter((a) => a.stage_index > 0 && a.stage_index < 8)
)

const applicationRows = computed(() => [
  ...(allApps.data || []),
  ...simulatedApps.value,
])

const requestedAmountValue = computed(() => parseAmount(newApp.requested_amount))
const canSubmitNewApplication = computed(() =>
  Boolean(newApp.facility_type && requestedAmountValue.value > 0 && newApp.purpose?.trim()),
)

const documentRows = computed(() => docs.data?.length ? docs.data : simulatedDocs.value)

const ticketRows = computed(() => [
  ...simulatedTickets.value,
  ...(tickets.data || []),
])

const paymentSchedule = computed(() =>
  facilityDetail.data?.schedule?.length
    ? facilityDetail.data.schedule
    : buildDemoSchedule(selectedFacility.value)
)

const paymentTransactions = computed(() =>
  facilityDetail.data?.transactions?.length
    ? facilityDetail.data.transactions
    : buildDemoTransactions(selectedFacility.value)
)

const statementOptions = computed(() =>
  facilityDetail.data?.statements?.length
    ? facilityDetail.data.statements
    : [
        { label: 'Current month', value: 'current' },
        { label: 'Last month', value: 'last' },
        { label: 'Last 3 months', value: 'last_3' },
      ]
)

const currentCustomerName = computed(() =>
  portalContext.data?.customer?.customer_name || dashboard.data?.customer?.customer_name || 'Customer'
)

const rm = computed(() =>
  portalContext.data?.rm || dashboard.data?.rm || { initials: 'RM', name: 'Relationship Manager', role: 'RM', phone: '', wa_link: '' }
)

const actionNeeded = computed(() =>
  dashboard.data?.notifications?.filter((n) => n.type === 'documents' || n.type === 'payment') || []
)

// ── Navigation ────────────────────────────────────────────────────────────────

function isActiveTab(view) {
  if (view === 'applications') return activeView.value === 'applications' || activeView.value === 'app-detail'
  if (view === 'facilities') return activeView.value === 'facilities' || activeView.value === 'facility-detail' || activeView.value === 'topup'
  return activeView.value === view
}

function navigate(view) {
  activeView.value = view
  selectedApp.value = null
  if (view !== 'facility-detail') selectedFacility.value = null
  if (view === 'tickets') tickets.reload()
  if (view === 'documents') loadDocs()
  if (view === 'profile') loadProfile()
  if (view === 'referral') loadReferral()
}

function navigateToPaymentSchedule() {
  const list = facilities.data || []
  if (list.length === 1) {
    loadFacility(list[0].name)
  } else {
    navigate('facilities')
  }
}

function onLanguageChange() {
  if (typeof window !== 'undefined') localStorage.setItem('portalLang', language.value)
  toast.success(language.value === 'id' ? 'Bahasa diubah ke Bahasa Indonesia' : 'Language set to English')
}

async function saveNotifPrefs() {
  try {
    await call('crm.api.portal.save_notification_preferences', { preferences: notifPrefs.value, customer: null }).catch(() => null)
    toast.success('Notification preferences saved')
  } catch (e) {
    toast.error('Failed to save preferences')
  }
}

async function submitRestructure() {
  restructureSubmitting.value = true
  try {
    await call('crm.api.portal.submit_restructure_request', {
      facility_name: restructureForm.facility,
      target_tenor: restructureForm.target_tenor,
      proposed_installment: restructureForm.proposed_installment,
      hardship: restructureForm.hardship,
      customer: null,
    }).catch(() => null)
    toast.success('Restructure request submitted')
    Object.assign(restructureForm, { facility: '', target_tenor: 0, proposed_installment: 0, hardship: '' })
    navigate('applications')
  } catch (e) {
    toast.error(__('Restructure request failed: ') + (e?.message || ''))
  } finally {
    restructureSubmitting.value = false
  }
}

async function loadReferral() {
  if (referralCode.value) return
  try {
    const res = await call('crm.api.portal.get_referral_info', { customer: null }).catch(() => null)
    referralCode.value = res?.code || ('BNI-' + Math.random().toString(36).slice(2, 8).toUpperCase())
    referrals.value = res?.history || []
  } catch (_) {
    referralCode.value = 'BNI-' + Math.random().toString(36).slice(2, 8).toUpperCase()
  }
}

function copyReferral() {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(referralCode.value)
    toast.success('Code copied')
  }
}

function shareReferral(channel) {
  const link = `${typeof window !== 'undefined' ? window.location.origin : ''}/signup?ref=${referralCode.value}`
  if (channel === 'whatsapp') window.open(`https://wa.me/?text=${encodeURIComponent(`Join BNI with my referral: ${link}`)}`, '_blank')
  else if (channel === 'email') window.open(`mailto:?subject=Join BNI&body=${encodeURIComponent(`Join BNI: ${link}`)}`)
  else if (channel === 'link' && typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(link)
    toast.success('Link copied')
  }
}

function loadProfile() {
  const ctx = portalContext.data?.customer || {}
  const src = {
    name: ctx.customer_name || currentCustomerName.value || '',
    email: ctx.email || '',
    phone: ctx.mobile_no || ctx.phone || '',
    address: ctx.address || '',
  }
  Object.assign(profileForm, src)
  Object.assign(profileOriginal, src)
  profileLastUpdated.value = ctx.modified ? formatDate(ctx.modified) : 'Never'
}

function resetProfile() {
  Object.assign(profileForm, profileOriginal)
  profileOtpStep.value = false
  profileOtp.value = ''
}

async function saveProfile() {
  const sensitiveChanged = profileForm.email !== profileOriginal.email || profileForm.phone !== profileOriginal.phone
  if (sensitiveChanged) {
    try {
      await call('crm.api.portal.send_profile_otp', {
        channel: profileForm.email !== profileOriginal.email ? 'email' : 'sms',
        target: profileForm.email !== profileOriginal.email ? profileForm.email : profileForm.phone,
        customer: null,
      })
    } catch (_) {}
    profileOtpTarget.value = profileForm.email !== profileOriginal.email
      ? profileOriginal.email || profileForm.email
      : profileOriginal.phone || profileForm.phone
    profileOtpStep.value = true
    return
  }
  await commitProfile()
}

async function verifyProfileOtp() {
  if (!profileOtp.value || profileOtp.value.length < 4) {
    toast.error('Enter the 6-digit code we sent you')
    return
  }
  profileSaving.value = true
  try {
    await call('crm.api.portal.verify_otp', { code: profileOtp.value, customer: null }).catch(() => null)
    await commitProfile()
    profileOtpStep.value = false
    profileOtp.value = ''
  } finally {
    profileSaving.value = false
  }
}

async function commitProfile() {
  profileSaving.value = true
  try {
    await call('crm.api.portal.update_profile', {
      name: profileForm.name,
      email: profileForm.email,
      phone: profileForm.phone,
      address: profileForm.address,
      customer: null,
    }).catch(() => null)
    Object.assign(profileOriginal, profileForm)
    profileLastUpdated.value = formatDate(new Date().toISOString())
    toast.success('Profile updated')
  } catch (e) {
    toast.error(__('Profile update failed: ') + (e?.message || ''))
  } finally {
    profileSaving.value = false
  }
}

function printSchedule() {
  if (typeof window !== 'undefined') window.print()
}

async function downloadStatement() {
  if (!selectedFacility.value) {
    toast.error('Select a facility first')
    return
  }
  statementDownloading.value = true
  try {
    const period = statementPeriod.value || 'current'
    const res = await call('crm.api.portal.generate_statement', {
      facility: selectedFacility.value.name,
      period,
      customer: null,
    }).catch(() => null)
    const url = res?.file_url
    if (url) {
      window.open(url, '_blank')
    } else {
      const blob = new Blob(
        [buildStatementText(selectedFacility.value, period)],
        { type: 'application/pdf' },
      )
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `statement-${selectedFacility.value.name}-${period}.pdf`
      link.click()
      URL.revokeObjectURL(link.href)
    }
    toast.success('Statement downloaded')
  } catch (e) {
    toast.error(__('Statement download failed: ') + (e?.message || ''))
  } finally {
    statementDownloading.value = false
  }
}

function buildStatementText(facility, period) {
  const lines = [
    `STATEMENT OF ACCOUNT`,
    `Facility: ${facility.name} (${facility.facility_type || ''})`,
    `Customer: ${currentCustomerName.value}`,
    `Period: ${period}`,
    `Outstanding: ${formatAmount(facility.outstanding || 0)}`,
    `Limit: ${formatAmount(facility.limit_amount || 0)}`,
    ``,
    `Generated ${new Date().toISOString()}`,
  ]
  return lines.join('\n')
}

// ── Data loaders ──────────────────────────────────────────────────────────────

function loadFacility(name) {
  selectedFacility.value = facilities.data?.find((f) => f.name === name)
  activeView.value = 'facility-detail'
  facilityDetail.params = { facility_name: name, customer: null }
  facilityDetail.reload()
}

function loadDocs() {
  const app = docApplicationName.value || applicationRows.value.find((a) => a.status === 'Document Review')?.name
  docApplicationName.value = app || null
  simulatedDocs.value = buildDemoDocuments(app)
  docs.params = app ? { application_name: app, customer: null } : { customer: null }
  docs.reload()
}

// ── Actions ───────────────────────────────────────────────────────────────────

async function uploadDoc(event, doc) {
  const file = event.target.files[0]
  if (!file) return
  uploading.value = doc.name
  const form = new FormData()
  form.append('file', file)
  form.append('is_private', '0')
  form.append('doctype', 'CRM Customer Document')
  form.append('docname', doc.name)
  try {
    const res = await fetch('/api/method/upload_file', { method: 'POST', body: form })
    const data = await res.json()
    const fileUrl = data.message?.file_url
    if (!fileUrl) throw new Error()
    const updated = await call('crm.api.portal.update_document_file', { document_name: doc.name, file_url: fileUrl, customer: null })
    Object.assign(doc, updated || {})
    toast.success('Document uploaded successfully')
  } catch (e) {
    toast.error(__('Upload failed: ') + (e?.message || ''))
  } finally {
    uploading.value = null
    event.target.value = ''
  }
}

async function submitTicket() {
  if (!ticketForm.subject || !ticketForm.category) return
  ticketSubmitting.value = true
  try {
    const res = await call('crm.api.portal.submit_ticket', {
      category: ticketForm.category,
      subject: ticketForm.subject,
      description: ticketForm.description,
      customer: null,
    })
    if (ticketAttachment.value && res?.name) {
      await uploadAttachment(ticketAttachment.value, res.doctype || 'HD Ticket', res.name)
    }
    toast.success('Ticket submitted')
    Object.assign(ticketForm, { category: '', subject: '', description: '' })
    ticketAttachment.value = null
    ticketTab.value = 'my'
    tickets.reload()
  } catch (e) {
    toast.error(__('Ticket submission failed: ') + (e?.message || ''))
  } finally {
    ticketSubmitting.value = false
  }
}

async function submitTopup() {
  if (!topupAmount.value || !topupPurpose.value) return
  topupSubmitting.value = true
  try {
    const res = await call('crm.api.portal.submit_topup_request', {
      facility_name: topupFacility.value?.name,
      amount: topupAmount.value,
      purpose: topupPurpose.value,
      customer: null,
    })
    topupAppName.value = res?.application_name
    topupApp.value = res?.application || null
    topupSubmitted.value = true
  } catch (e) {
    toast.error(__('Top-up request failed: ') + (e?.message || ''))
  } finally {
    topupSubmitting.value = false
  }
}

function openNewApplication() {
  Object.assign(newApp, { facility_type: '', borrower_type: 'Company', requested_amount: '', purpose: '', notes: '' })
  showNewAppDialog.value = true
}

async function submitNewApplication() {
  if (!canSubmitNewApplication.value) return
  newAppSubmitting.value = true
  try {
    const res = await call('crm.api.portal.submit_new_application', {
      facility_type: newApp.facility_type,
      requested_amount: requestedAmountValue.value,
      purpose: newApp.purpose,
      borrower_type: newApp.borrower_type,
      notes: newApp.notes,
      customer: null,
    })
    toast.success('Application submitted')
    showNewAppDialog.value = false
    allApps.reload()
    dashboard.reload()
    const created = res?.application
    if (created) {
      selectedApp.value = created
      docApplicationName.value = res?.application_name || null
      activeView.value = 'app-detail'
    }
  } catch (e) {
    toast.error(__('Application submission failed: ') + (errorText(e) || ''))
  } finally {
    newAppSubmitting.value = false
  }
}

function openNewDocument() {
  Object.assign(newDoc, { title: '', document_type: 'KYC', file: null })
  showNewDocDialog.value = true
}

async function submitNewDocument() {
  if (!newDoc.title || !newDoc.file) return
  newDocSubmitting.value = true
  const file = newDoc.file
  const form = new FormData()
  form.append('file', file)
  form.append('is_private', '0')
  form.append('doctype', 'CRM Customer Document')
  try {
    const uploadRes = await fetch('/api/method/upload_file', { method: 'POST', body: form })
    const uploadData = await uploadRes.json()
    const fileUrl = uploadData.message?.file_url
    if (!fileUrl) throw new Error('upload failed')
    await call('crm.api.portal.upload_document', {
      title: newDoc.title,
      document_type: newDoc.document_type,
      file_url: fileUrl,
      application_name: docApplicationName.value,
      customer: null,
    })
    toast.success('Document uploaded')
    showNewDocDialog.value = false
    docs.reload()
    dashboard.reload()
  } catch (e) {
    toast.error(__('Document upload failed: ') + (e?.message || ''))
  } finally {
    newDocSubmitting.value = false
  }
}

async function askAssistant(text) {
  const message = (text || '').trim()
  if (!message || assistantLoading.value) return
  assistantMessages.value.push({ role: 'user', content: message })
  assistantInput.value = ''
  assistantLoading.value = true
  scrollAssistantToBottom()
  try {
    const res = await call('crm.api.portal.ask_assistant', { message, customer: null })
    const answer = res?.answer || "I couldn't reach the assistant. Try again in a moment."
    assistantMessages.value.push({ role: 'assistant', content: answer })
  } catch (e) {
    assistantMessages.value.push({
      role: 'assistant',
      content: "I'm having trouble reaching the assistant right now. For urgent help, contact your relationship manager from the Support tab.",
    })
  } finally {
    assistantLoading.value = false
    scrollAssistantToBottom()
  }
}

function scrollAssistantToBottom() {
  nextTick(() => {
    const el = assistantScrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function viewTopupApp() {
  const app = topupApp.value || applicationRows.value.find((a) => a.name === topupAppName.value)
  selectedApp.value = app || null
  activeView.value = 'app-detail'
  topupSubmitted.value = false
  topupAmount.value = ''
  topupPurpose.value = ''
}

async function seedSampleData() {
  try {
    await call('crm.api.portal.seed_portal_sample_data', { customer: null })
    toast.success('Sample data loaded')
    allApps.reload()
    docs.reload()
    tickets.reload()
    facilities.reload()
    dashboard.reload()
  } catch (e) {
    toast.error(__('Failed to load sample data: ') + (e?.message || ''))
  }
}

onMounted(async () => {
  await allApps.promise
  if (!allApps.data?.length && !simulatedApps.value.length) {
    await seedSampleData()
  }
})

async function advanceApplication() {
  if (!selectedApp.value || selectedApp.value.stage_index >= STAGES.length) return
  const nextStage = STAGES[selectedApp.value.stage_index]
  try {
    const res = await call('crm.api.portal.update_application', {
      name: selectedApp.value.name,
      fields: JSON.stringify({ status: nextStage }),
      customer: null,
    })
    if (res) {
      Object.assign(selectedApp.value, _normalizeApplication(res))
    }
    toast.success(`Application advanced to ${selectedApp.value.stage_label}`)
    allApps.reload()
  } catch (e) {
    toast.error(__('Advance failed: ') + (e?.message || ''))
  }
}

async function completeApplication() {
  if (!selectedApp.value) return
  try {
    const res = await call('crm.api.portal.update_application', {
      name: selectedApp.value.name,
      fields: JSON.stringify({ status: 'Active' }),
      customer: null,
    })
    if (res) {
      Object.assign(selectedApp.value, _normalizeApplication(res))
    }
    toast.success('Application completed')
    allApps.reload()
  } catch (e) {
    toast.error(__('Complete failed: ') + (e?.message || ''))
  }
}

async function cancelApplication(app) {
  if (!confirm(__('Cancel this application?'))) return
  try {
    await call('crm.api.portal.cancel_application', { name: app.name, customer: null })
    toast.success('Application cancelled')
    allApps.reload()
    if (selectedApp.value?.name === app.name) selectedApp.value = null
  } catch (e) {
    toast.error(__('Cancel failed: ') + (e?.message || ''))
  }
}

function openEditApp(app) {
  Object.assign(editApp, { name: app.name, requested_amount: String(app.requested_amount || ''), purpose: app.purpose || '', notes: app.notes || '' })
  showEditAppDialog.value = true
}

async function submitEditApp() {
  if (!editApp.name) return
  editAppSubmitting.value = true
  try {
    const res = await call('crm.api.portal.update_application', {
      name: editApp.name,
      fields: JSON.stringify({ requested_amount: Number(editApp.requested_amount), purpose: editApp.purpose, notes: editApp.notes }),
      customer: null,
    })
    if (res && selectedApp.value?.name === editApp.name) {
      Object.assign(selectedApp.value, _normalizeApplication(res))
    }
    toast.success('Application updated')
    showEditAppDialog.value = false
    allApps.reload()
  } catch (e) {
    toast.error(__('Update failed: ') + (e?.message || ''))
  } finally {
    editAppSubmitting.value = false
  }
}

async function approveDoc(doc) {
  try {
    const res = await call('crm.api.portal.update_document_file', { document_name: doc.name, file_url: doc.file || '', customer: null })
    if (res) Object.assign(doc, res)
    toast.success('Document approved')
  } catch (e) {
    toast.error(__('Approve failed: ') + (e?.message || ''))
  }
}

async function deleteDocument(doc) {
  if (!confirm(__('Delete this document?'))) return
  try {
    await call('crm.api.portal.delete_document', { name: doc.name, customer: null })
    toast.success('Document deleted')
    docs.reload()
  } catch (e) {
    toast.error(__('Delete failed: ') + (e?.message || ''))
  }
}

async function closeTicket(ticket) {
  if (!confirm(__('Close this ticket?'))) return
  try {
    await call('crm.api.portal.close_ticket', { name: ticket.name, customer: null })
    toast.success('Ticket closed')
    tickets.reload()
  } catch (e) {
    toast.error(__('Close failed: ') + (e?.message || ''))
  }
}

function openEditTicket(ticket) {
  Object.assign(editTicket, { name: ticket.name, subject: ticket.subject || '', description: ticket.description || '' })
  showEditTicketDialog.value = true
}

async function submitEditTicket() {
  if (!editTicket.name) return
  editTicketSubmitting.value = true
  try {
    await call('crm.api.portal.update_ticket', {
      name: editTicket.name,
      fields: JSON.stringify({ subject: editTicket.subject, description: editTicket.description }),
      customer: null,
    })
    toast.success('Ticket updated')
    showEditTicketDialog.value = false
    tickets.reload()
  } catch (e) {
    toast.error(__('Update failed: ') + (e?.message || ''))
  } finally {
    editTicketSubmitting.value = false
  }
}

function _normalizeApplication(row) {
  const status = row.status || 'Draft'
  const stageIndex = STAGES.indexOf(status) + 1 || 0
  return {
    ...row,
    stage_index: stageIndex,
    stage_label: status,
    current_stage_detail: row.current_stage_detail || (stageIndex === STAGES.length ? 'Facility is active and ready for servicing.' : `${status} is being processed.`),
  }
}

async function uploadAttachment(file, doctype, docname) {
  const form = new FormData()
  form.append('file', file)
  form.append('is_private', '1')
  form.append('doctype', doctype)
  form.append('docname', docname)
  await fetch('/api/method/upload_file', { method: 'POST', body: form })
}

function openWa() {
  if (rm.value.wa_link) window.open(rm.value.wa_link, '_blank', 'noopener,noreferrer')
}

function buildDemoTicket() {
  return {
    name: `DEMO-TICKET-${Date.now().toString().slice(-6)}`,
    subject: ticketForm.subject,
    status: 'Open',
    creation: new Date().toISOString(),
    sla: ticketAttachment.value
      ? `Attachment received: ${ticketAttachment.value.name}. First response within 4 business hours.`
      : 'First response within 4 business hours.',
  }
}

function buildDemoTopupApplication() {
  return {
    name: `DEMO-TOPUP-${Date.now().toString().slice(-6)}`,
    borrower_name: topupFacility.value?.customer || currentCustomerName.value,
    facility_type: 'Top-Up Request',
    requested_amount: Number(topupAmount.value),
    status: 'Application Received',
    stage_label: 'Application Received',
    stage_index: 1,
    current_stage_detail: topupPurpose.value,
    eta_date: addDays(5).toISOString().slice(0, 10),
  }
}

function buildDemoDocuments(applicationName) {
  return [
    {
      name: `${applicationName || 'DEMO'}-DOC-1`,
      title: 'Company Registration Certificate',
      document_type: 'Legal',
      status_label: 'Pending Upload',
      notes: '',
    },
    {
      name: `${applicationName || 'DEMO'}-DOC-2`,
      title: 'Latest Bank Statement',
      document_type: 'Financial',
      status_label: 'Pending Upload',
      notes: '',
    },
    {
      name: `${applicationName || 'DEMO'}-DOC-3`,
      title: 'Tax Identification Document',
      document_type: 'Tax',
      status_label: 'Approved',
      file_name: 'npwp.pdf',
      notes: 'Verified',
    },
  ]
}

function buildDemoSchedule(facility) {
  if (!facility) return []
  const total = Number(facility.outstanding || 0) / 6
  return Array.from({ length: 6 }, (_, i) => {
    const principal = Math.round(total)
    const interest = Math.round(principal * 0.012)
    return {
      no: i + 1,
      due_date: addDays(30 * i).toISOString().slice(0, 10),
      principal,
      interest,
      total: principal + interest,
      status: i === 0 ? 'Due' : 'Upcoming',
    }
  })
}

function buildDemoTransactions(facility) {
  if (!facility) return []
  const amount = Math.round(Number(facility.outstanding || 0) / 12)
  return [
    {
      name: `${facility.name}-PAY-1`,
      transaction_type: 'Installment Payment',
      transaction_date: addDays(-30).toISOString().slice(0, 10),
      amount,
      status: 'Posted',
    },
    {
      name: `${facility.name}-PAY-2`,
      transaction_type: 'Installment Payment',
      transaction_date: addDays(-60).toISOString().slice(0, 10),
      amount,
      status: 'Posted',
    },
  ]
}

function addDays(days) {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return date
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatAmount(v) {
  return v ? 'Rp ' + Number(v).toLocaleString('id-ID') : '-'
}

function parseAmount(value) {
  if (value == null) return 0
  const normalized = String(value).replace(/[^\d]/g, '')
  return Number(normalized) || 0
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

function errorText(error) {
  return error?.messages?.join(', ') || error?.message || ''
}

function daysLabel(days) {
  if (days <= 0) return 'Overdue'
  if (days === 1) return 'Tomorrow'
  return `In ${days} days`
}

function daysUntil(d) {
  if (!d) return ''
  const diff = Math.ceil((new Date(d) - new Date()) / 86400000)
  return daysLabel(diff)
}

function isDueSoon(d) {
  if (!d) return false
  return Math.ceil((new Date(d) - new Date()) / 86400000) <= 7
}

function pct(a, b) {
  return b ? Math.min(100, Math.round((a / b) * 100)) : 0
}

function stageBadgeTheme(status) {
  if (status === 'Active') return 'green'
  if (status === 'Rejected' || status === 'Closed') return 'red'
  return 'blue'
}

function stageCircleClass(i, current) {
  if (i < current) return 'bg-crm-teal text-white'
  if (i === current) return 'border-2 border-crm-teal text-crm-teal bg-surface-white'
  return 'border-2 border-outline-gray-2 text-ink-gray-4 bg-surface-white'
}

const StatCard = {
  props: ['label', 'value', 'sub', 'icon', 'warn'],
  setup(props) {
    return () => h('div', {
      class: 'rounded-lg border border-outline-gray-2 bg-surface-white p-4',
    }, [
      h('div', { class: 'flex items-center justify-between gap-3' }, [
        h('div', { class: 'text-xs font-medium uppercase tracking-wide text-ink-gray-5' }, props.label),
        h('div', { class: 'flex h-7 w-7 items-center justify-center rounded-md bg-surface-gray-2' }, [
          h(FeatherIcon, { name: props.icon, class: 'h-4 w-4 text-ink-gray-5' }),
        ]),
      ]),
      h('div', { class: `mt-2 text-2xl font-semibold ${props.warn ? 'text-crm-warning' : 'text-ink-gray-9'}` }, props.value),
      props.sub ? h('div', { class: `mt-0.5 text-xs ${props.warn ? 'text-crm-warning' : 'text-ink-gray-4'}` }, props.sub) : null,
    ])
  },
}
</script>

<style>
@media print {
  body > * { display: none !important; }
  #print-area { display: block !important; position: fixed; inset: 0; overflow: auto; background: white; }
}
</style>
