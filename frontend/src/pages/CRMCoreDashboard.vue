<template>
  <div class="bni-dashboard h-full overflow-y-auto font-sans">
    <div class="bni-shell">
      <header class="bni-topbar">
        <div>
          <h1>{{ __('Dashboard') }}</h1>
          <p>{{ __('Last updated') }} {{ lastUpdated }}</p>
        </div>
        <div class="bni-topbar-actions">
          <div class="bni-ai-search">
            <FeatherIcon name="search" class="h-4 w-4" />
            <input v-model="aiSearch" :placeholder="__('Search AI Mode')" />
          </div>
          <button class="bni-icon-btn" :aria-label="__('Notifications')"><FeatherIcon name="bell" class="h-4 w-4" /></button>
          <button class="bni-icon-btn" :aria-label="__('Inbox')"><FeatherIcon name="inbox" class="h-4 w-4" /></button>
          <button class="bni-icon-btn" :aria-label="__('Share')"><FeatherIcon name="share-2" class="h-4 w-4" /></button>
          <Button variant="outline" :label="__('Customize Widget')" />
          <Button variant="outline" :label="__('Imports')" />
          <Button variant="solid" :label="__('Exports')" />
        </div>
      </header>

      <section class="bni-filterbar">
        <div class="bni-segments">
          <button
            v-for="period in periods"
            :key="period.key"
            :class="{ active: activePeriod === period.key }"
            @click="activePeriod = period.key"
          >
            {{ period.label }}
          </button>
        </div>
        <Button variant="outline" :loading="dashboard.loading" :label="__('Refresh')" @click="dashboard.fetch()" />
      </section>

      <section class="bni-metrics">
        <MetricCard v-for="metric in metrics" :key="metric.label" :metric="metric" />
      </section>

      <section class="bni-main-grid">
        <article class="bni-card bni-revenue-card">
          <div class="bni-card-head">
            <div>
              <h2>{{ __('Pendapatan') }}</h2>
              <p>{{ formatCurrency(data.revenue?.total || 0) }} · {{ formatDelta(data.revenue?.change) }}</p>
            </div>
            <FeatherIcon name="bar-chart-2" class="h-5 w-5 text-teal-600" />
          </div>
          <div class="bni-chart">
            <svg viewBox="0 0 720 260" preserveAspectRatio="none">
              <line x1="20" y1="225" x2="700" y2="225" class="grid-line" />
              <line x1="20" y1="165" x2="700" y2="165" class="grid-line" />
              <line x1="20" y1="105" x2="700" y2="105" class="grid-line" />
              <polyline :points="revenueLinePoints" fill="none" class="revenue-line" />
              <template v-for="(item, index) in revenueMonths" :key="item.label">
                <rect
                  :x="38 + index * 56"
                  :y="225 - barHeight(item)"
                  width="24"
                  :height="barHeight(item)"
                  rx="6"
                  class="revenue-bar"
                />
                <circle :cx="50 + index * 56" :cy="lineY(item)" r="4" class="revenue-dot" />
                <text :x="50 + index * 56" y="250" text-anchor="middle">{{ item.label }}</text>
              </template>
            </svg>
          </div>
        </article>

        <article class="bni-card">
          <div class="bni-card-head">
            <div>
              <h2>{{ __('Kalender') }}</h2>
              <p>{{ __('Upcoming customer events') }}</p>
            </div>
            <Button variant="subtle" size="sm" :label="__('View')" />
          </div>
          <div class="bni-calendar-list">
            <div v-for="event in calendarEvents" :key="event.name" class="bni-calendar-item">
              <div class="date-pill">{{ eventDay(event.starts_on) }}</div>
              <div>
                <strong>{{ event.subject || __('Untitled Event') }}</strong>
                <span>{{ eventTime(event.starts_on) }} · {{ event.event_type || __('Event') }}</span>
              </div>
            </div>
            <div v-if="calendarEvents.length === 0" class="bni-empty">{{ __('No events in this period') }}</div>
          </div>
        </article>
      </section>

      <section class="bni-bottom-grid">
        <article class="bni-card">
          <div class="bni-card-head">
            <div>
              <h2>{{ __('Manajemen Leads') }}</h2>
              <p>{{ __('Status, source, and qualification') }}</p>
            </div>
          </div>
          <LeadGroup :title="__('Status')" :rows="leadManagement.status" />
          <LeadGroup :title="__('Source')" :rows="leadManagement.source" />
          <LeadGroup :title="__('Qualification')" :rows="leadManagement.qualification" />
        </article>

        <article class="bni-card">
          <div class="bni-card-head">
            <div>
              <h2>{{ __('Cabang / Wilayah') }}</h2>
              <p>{{ __('Customer distribution by territory') }}</p>
            </div>
          </div>
          <div class="bni-map">
            <svg viewBox="0 0 340 190">
              <path d="M28 94 C80 40, 126 44, 164 82 S266 40, 314 92 C282 142, 218 142, 174 116 S76 148, 28 94Z" />
              <circle v-for="(region, index) in regions" :key="region.region" :cx="52 + index * 48" :cy="88 + (index % 2) * 28" :r="7 + region.percent / 8" />
            </svg>
          </div>
          <div class="bni-region-list">
            <div v-for="region in regions" :key="region.region">
              <span>{{ region.region }}</span>
              <strong>{{ region.customers }} {{ __('customers') }}</strong>
            </div>
            <div v-if="regions.length === 0" class="bni-empty">{{ __('No regional data yet') }}</div>
          </div>
        </article>

        <article class="bni-card">
          <div class="bni-card-head">
            <div>
              <h2>{{ __('Top Cabang') }}</h2>
              <p>{{ __('Best performing territories') }}</p>
            </div>
          </div>
          <div class="bni-branch-list">
            <div v-for="branch in topBranches" :key="branch.branch" class="bni-branch-row">
              <div>
                <strong>{{ branch.branch }}</strong>
                <span>{{ branch.customers }} {{ __('customers') }}</span>
              </div>
              <div class="bni-progress"><span :style="{ width: `${branch.percent}%` }"></span></div>
              <em>{{ branch.percent }}%</em>
            </div>
            <div v-if="topBranches.length === 0" class="bni-empty">{{ __('No branch ranking yet') }}</div>
          </div>
        </article>

        <article class="bni-card">
          <div class="bni-card-head">
            <div>
              <h2>{{ __('Tingkat Retensi') }}</h2>
              <p>{{ __('Activity-based customer retention') }}</p>
            </div>
          </div>
          <div class="bni-retention-chart">
            <div v-for="item in retentionMonths" :key="item.label" class="bni-retention-bar">
              <span :style="{ height: `${Math.max(item.value, 4)}%` }"></span>
              <small>{{ item.label }}</small>
            </div>
          </div>
          <div class="bni-segment-list">
            <div v-for="segment in retentionSegments" :key="segment.label">
              <span>{{ segment.label }}</span>
              <strong>{{ segment.percent }}%</strong>
            </div>
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { Button, FeatherIcon, createResource, usePageMeta } from 'frappe-ui'
import { computed, h, ref, watch } from 'vue'

const aiSearch = ref('')
const activePeriod = ref('month')

const periods = [
  { key: 'week', label: __('Week') },
  { key: 'month', label: __('Month') },
  { key: 'quarter', label: __('Quarter') },
  { key: 'year', label: __('Year') },
]

const dashboard = createResource({
  url: 'crm.api.dashboard.get_bni_crm_dashboard',
  auto: true,
  makeParams() {
    return { from_date: fromDate.value, to_date: toDate.value }
  },
})

const data = computed(() => dashboard.data || {})
const metrics = computed(() => data.value.metrics || [])
const revenueMonths = computed(() => data.value.revenue?.months || [])
const calendarEvents = computed(() => data.value.calendar || [])
const leadManagement = computed(() => data.value.lead_management || { status: [], source: [], qualification: [] })
const regions = computed(() => data.value.regions || [])
const topBranches = computed(() => data.value.top_branches || [])
const retentionMonths = computed(() => data.value.retention?.months || [])
const retentionSegments = computed(() => data.value.retention?.segments || [])
const lastUpdated = computed(() => data.value.last_updated ? eventTime(data.value.last_updated) : __('now'))

const toDate = computed(() => new Date().toISOString().slice(0, 10))
const fromDate = computed(() => {
  const date = new Date()
  const days = { week: 7, month: 30, quarter: 90, year: 365 }[activePeriod.value] || 30
  date.setDate(date.getDate() - days)
  return date.toISOString().slice(0, 10)
})

const maxRevenue = computed(() => Math.max(...revenueMonths.value.map((item) => Number(item.value || 0)), 1))
const revenueLinePoints = computed(() => revenueMonths.value.map((item, index) => `${50 + index * 56},${lineY(item)}`).join(' '))

function barHeight(item) {
  return Math.max((Number(item.value || 0) / maxRevenue.value) * 150, item.value ? 8 : 2)
}

function lineY(item) {
  return 220 - Math.max((Number(item.value || 0) / maxRevenue.value) * 150, item.value ? 8 : 2)
}

function formatCurrency(value) {
  const amount = Number(value || 0)
  if (amount >= 1_000_000_000_000) return `Rp ${(amount / 1_000_000_000_000).toFixed(1)}T`
  if (amount >= 1_000_000_000) return `Rp ${(amount / 1_000_000_000).toFixed(1)}B`
  if (amount >= 1_000_000) return `Rp ${(amount / 1_000_000).toFixed(1)}M`
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(amount)
}

function metricValue(metric) {
  if (metric.format === 'currency') return formatCurrency(metric.value)
  return `${Number(metric.value || 0).toLocaleString('id-ID')}${metric.suffix || ''}`
}

function formatDelta(value) {
  const amount = Number(value || 0)
  if (!amount) return '0%'
  return `${amount > 0 ? '+' : ''}${amount.toFixed(1)}%`
}

function deltaClass(metric) {
  const value = Number(metric.change || 0)
  const positive = metric.negative_is_better ? value <= 0 : value >= 0
  return positive ? 'positive' : 'negative'
}

function eventDay(value) {
  if (!value) return '--'
  return new Intl.DateTimeFormat('id-ID', { day: '2-digit' }).format(new Date(value))
}

function eventTime(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('id-ID', { hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

watch(activePeriod, () => dashboard.fetch())

usePageMeta(() => ({ title: __('Dashboard') }))

const MetricCard = {
  props: ['metric'],
  setup(props) {
    return () => h('article', { class: 'bni-metric-card' }, [
      h('div', { class: 'bni-metric-icon' }, [h(FeatherIcon, { name: props.metric.icon || 'activity', class: 'h-5 w-5' })]),
      h('div', { class: 'bni-metric-body' }, [
        h('span', props.metric.label),
        h('strong', metricValue(props.metric)),
        h('small', { class: deltaClass(props.metric) }, `${formatDelta(props.metric.change)} ${props.metric.caption || ''}`),
      ]),
    ])
  },
}

const LeadGroup = {
  props: ['title', 'rows'],
  setup(props) {
    return () => h('div', { class: 'bni-lead-group' }, [
      h('h3', props.title),
      ...(props.rows || []).map((row) => h('div', { class: 'bni-lead-row' }, [
        h('span', row.label),
        h('div', { class: 'bni-progress' }, [h('span', { style: { width: `${row.percent || 0}%` } })]),
        h('strong', row.count),
      ])),
      !(props.rows || []).length ? h('div', { class: 'bni-empty' }, __('No data')) : null,
    ])
  },
}
</script>

<style scoped>
.bni-dashboard {
  background: #f7fafb;
  color: #17262b;
}
.bni-shell {
  max-width: 1500px;
  margin: 0 auto;
  padding: 24px;
}
.bni-topbar,
.bni-filterbar,
.bni-card,
.bni-metric-card {
  border: 1px solid #e6ecef;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(20, 50, 58, 0.05);
}
.bni-topbar {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  padding: 18px 20px;
  border-radius: 8px;
}
.bni-topbar h1 {
  font-size: 24px;
  font-weight: 800;
  margin: 0;
}
.bni-topbar p,
.bni-card-head p {
  margin: 4px 0 0;
  color: #6b7d85;
  font-size: 13px;
}
.bni-topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.bni-ai-search {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  min-width: 260px;
  border: 1px solid #d9e3e7;
  border-radius: 8px;
  padding: 0 12px;
  color: #789099;
}
.bni-ai-search input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  font-size: 13px;
}
.bni-icon-btn {
  height: 36px;
  width: 36px;
  border-radius: 8px;
  border: 1px solid #d9e3e7;
  background: white;
  color: #556970;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.bni-filterbar {
  margin-top: 16px;
  padding: 10px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}
.bni-segments {
  display: flex;
  gap: 4px;
}
.bni-segments button {
  border: 0;
  background: transparent;
  border-radius: 7px;
  color: #647780;
  font-size: 13px;
  font-weight: 700;
  padding: 8px 14px;
}
.bni-segments button.active {
  background: #008c95;
  color: white;
}
.bni-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}
.bni-metric-card {
  display: flex;
  gap: 14px;
  align-items: center;
  border-radius: 8px;
  padding: 16px;
}
.bni-metric-icon {
  height: 42px;
  width: 42px;
  border-radius: 8px;
  background: #e7f8f9;
  color: #008c95;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.bni-metric-body {
  min-width: 0;
  display: grid;
  gap: 2px;
}
.bni-metric-body span {
  font-size: 12px;
  color: #6d7c82;
  font-weight: 700;
}
.bni-metric-body strong {
  color: #14262d;
  font-size: 22px;
  line-height: 1.1;
}
.bni-metric-body small.positive {
  color: #008c95;
}
.bni-metric-body small.negative {
  color: #d05b32;
}
.bni-main-grid,
.bni-bottom-grid {
  display: grid;
  gap: 16px;
  margin-top: 16px;
}
.bni-main-grid {
  grid-template-columns: 2fr 1fr;
}
.bni-bottom-grid {
  grid-template-columns: 1.15fr 1.05fr 1fr 1fr;
}
.bni-card {
  border-radius: 8px;
  padding: 18px;
  min-width: 0;
}
.bni-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}
.bni-card-head h2 {
  font-size: 16px;
  font-weight: 800;
  margin: 0;
}
.bni-chart {
  height: 290px;
}
.bni-chart svg {
  width: 100%;
  height: 100%;
}
.bni-chart text {
  fill: #74878f;
  font-size: 12px;
}
.grid-line {
  stroke: #edf2f4;
  stroke-width: 1;
}
.revenue-bar {
  fill: #cbecee;
}
.revenue-line {
  stroke: #008c95;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.revenue-dot {
  fill: #008c95;
  stroke: #ffffff;
  stroke-width: 3;
}
.bni-calendar-list,
.bni-branch-list,
.bni-region-list,
.bni-segment-list {
  display: grid;
  gap: 12px;
}
.bni-calendar-item {
  display: flex;
  gap: 12px;
  align-items: center;
  border: 1px solid #eef3f4;
  border-radius: 8px;
  padding: 12px;
}
.date-pill {
  height: 42px;
  width: 42px;
  border-radius: 8px;
  background: #e9f8f9;
  color: #008c95;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bni-calendar-item strong,
.bni-branch-row strong {
  display: block;
  color: #17262b;
  font-size: 13px;
}
.bni-calendar-item span,
.bni-branch-row span {
  color: #6f7f86;
  font-size: 12px;
}
.bni-lead-group + .bni-lead-group {
  margin-top: 16px;
}
.bni-lead-group h3 {
  margin: 0 0 8px;
  font-size: 12px;
  color: #667982;
  text-transform: uppercase;
}
.bni-lead-row,
.bni-branch-row,
.bni-region-list > div,
.bni-segment-list > div {
  display: grid;
  grid-template-columns: minmax(80px, 1fr) 1.2fr auto;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}
.bni-region-list > div,
.bni-segment-list > div {
  grid-template-columns: minmax(80px, 1fr) auto;
}
.bni-progress {
  height: 8px;
  border-radius: 999px;
  background: #edf3f5;
  overflow: hidden;
}
.bni-progress span {
  display: block;
  height: 100%;
  background: #008c95;
  border-radius: inherit;
}
.bni-map {
  border-radius: 8px;
  background: #f4fafb;
  margin-bottom: 14px;
  padding: 10px;
}
.bni-map svg {
  width: 100%;
  height: 180px;
}
.bni-map path {
  fill: #d8eff1;
  stroke: #a8d9dd;
  stroke-width: 2;
}
.bni-map circle {
  fill: #008c95;
  opacity: 0.8;
}
.bni-retention-chart {
  display: flex;
  align-items: end;
  gap: 10px;
  height: 150px;
  padding: 12px 4px 4px;
  border-bottom: 1px solid #eef3f4;
}
.bni-retention-bar {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: end;
  gap: 6px;
  align-items: center;
}
.bni-retention-bar span {
  display: block;
  width: 100%;
  max-width: 28px;
  border-radius: 8px 8px 0 0;
  background: #008c95;
}
.bni-retention-bar small {
  font-size: 11px;
  color: #78888e;
}
.bni-segment-list {
  margin-top: 14px;
}
.bni-empty {
  color: #94a3ad;
  font-size: 13px;
  padding: 8px 0;
}
@media (max-width: 1180px) {
  .bni-metrics,
  .bni-bottom-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .bni-main-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 760px) {
  .bni-shell {
    padding: 16px;
  }
  .bni-topbar,
  .bni-filterbar {
    align-items: stretch;
    flex-direction: column;
  }
  .bni-metrics,
  .bni-bottom-grid {
    grid-template-columns: 1fr;
  }
  .bni-ai-search {
    min-width: 100%;
  }
}
</style>
