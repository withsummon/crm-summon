<template>
  <div class="bni-dashboard">
    <div class="bni-content">
      <!-- ═══ TOPBAR ═══ -->
      <header class="bni-topbar">
        <div class="bni-topbar-row1">
          <div class="bni-topbar-left">
            <span class="bni-title-icon">
              <FeatherIcon name="grid" class="h-[18px] w-[18px]" />
            </span>
            <h1>{{ __('Dashboard') }}</h1>
          </div>
          <div class="bni-topbar-right">
            <div class="bni-search-box">
              <FeatherIcon name="search" class="h-4 w-4 shrink-0 opacity-50" />
              <input v-model="aiSearch" :placeholder="__('Search AI Mode')" />
            </div>
            <button class="bni-icon-btn" :aria-label="__('Notifications')">
              <FeatherIcon name="bell" class="h-4 w-4" />
            </button>
              <span class="bni-icon-btn-wrap">
              <button class="bni-icon-btn" :aria-label="__('Inbox')">
                <FeatherIcon name="inbox" class="h-4 w-4" />
              </button>
              <span v-if="notifCount > 0" class="bni-notif-badge">{{ notifCount }}</span>
            </span>
            <button class="bni-icon-btn" :aria-label="__('Share')">
              <FeatherIcon name="share-2" class="h-4 w-4" />
            </button>
          </div>
        </div>
        <div class="bni-topbar-row2">
          <div class="bni-updated-pill">
            <FeatherIcon name="check-circle" class="h-3.5 w-3.5" />
            <span>{{ __('Last updated') }} {{ lastUpdated }}</span>
          </div>
          <div class="bni-action-buttons">
            <button class="bni-action-btn" @click="showCustomize = true">
              <FeatherIcon name="sliders" class="h-3.5 w-3.5" />
              {{ __('Customize Widget') }}
            </button>
            <button class="bni-action-btn" @click="showImport = true">
              {{ __('Imports') }}
              <FeatherIcon name="chevron-down" class="h-3 w-3" />
            </button>
            <button class="bni-export-btn" @click="showExport = true">
              {{ __('Exports') }}
              <FeatherIcon name="chevron-down" class="h-3 w-3" />
            </button>
          </div>
        </div>
      </header>

      <!-- ═══ CUSTOMIZE MODE TOGGLE ═══ -->
      <div v-if="showCustomize" class="bni-customize-banner">
        <FeatherIcon name="move" class="h-4 w-4" />
        <span>{{ __('Drag handle to reorder. Eye icon to show/hide.') }}</span>
        <button class="bni-customize-reset" @click="resetWidgets">{{ __('Reset') }}</button>
        <button class="bni-customize-done" @click="exitCustomize">{{ __('Done') }}</button>
      </div>

      <!-- ═══ DRAGGABLE WIDGETS ═══ -->
      <div ref="widgetsContainerRef" class="bni-widgets-container">
        <div
          v-for="(element, idx) in widgets"
          :key="element.key"
          :data-idx="idx"
          :class="['bni-widget', 'bni-widget-' + element.key, { 'bni-widget-dimmed': !element.visible, 'bni-customize-active': showCustomize }]"
          :style="(!element.visible && !showCustomize) ? { display: 'none' } : {}"
        >
          <!-- Drag Handle (visible only in customize mode) -->
          <div v-if="showCustomize" class="bni-widget-header">
            <span class="bni-drag-handle"><FeatherIcon name="menu" class="h-4 w-4" /></span>
            <span class="bni-widget-title">{{ element.label }}</span>
            <button class="bni-widget-toggle" :title="__('Toggle visibility')" @click="toggleWidget(element.key)">
              <FeatherIcon :name="element.visible ? 'eye' : 'eye-off'" class="h-3.5 w-3.5" />
            </button>
          </div>

            <!-- METRIC CARDS -->
            <section v-if="element.key === 'metrics'" class="bni-metric-grid">
              <article v-for="m in displayMetrics" :key="m.label" class="bni-metric-card">
                <div class="bni-mc-top">
                  <div class="bni-mc-icon"><FeatherIcon :name="m.icon" class="h-[16px] w-[16px]" /></div>
                  <span class="bni-mc-label">{{ m.label }}</span>
                  <FeatherIcon name="info" class="h-3.5 w-3.5 bni-mc-info" />
                </div>
                <div class="bni-mc-body">
                  <div class="bni-mc-bottom">
                    <strong class="bni-mc-value">{{ m.displayValue }}</strong>
                    <span :class="['bni-mc-change', m.isPositive ? 'up' : 'down']">{{ m.isPositive ? '↑' : '↓' }} {{ Math.abs(m.changeNum) }}%</span>
                  </div>
                  <span class="bni-mc-caption">{{ m.caption }}</span>
                </div>
              </article>
            </section>

            <!-- REVENUE CHART -->
            <article v-if="element.key === 'revenue'" class="bni-card bni-revenue-card">
              <div class="bni-rev-header">
                <div class="bni-rev-left">
                  <h2>{{ __('Top Bank / Company') }}</h2>
                  <div class="bni-rev-total">
                    <strong>{{ formatCount(chartSummary.total) }} {{ __('leads') }}</strong>
                    <span :class="['bni-badge-change', chartSummary.change >= 0 ? 'up' : 'down']">{{ chartSummary.change >= 0 ? '↑' : '↓' }} {{ Math.abs(chartSummary.change) }}%</span>
                    <span class="bni-vs">{{ __('vs periode sebelumnya') }}</span>
                  </div>
                </div>
                <div class="bni-rev-periods">
                  <button v-for="p in revenuePeriods" :key="p" :class="{ active: activeRevenuePeriod === p }" @click="activeRevenuePeriod = p">{{ p }}</button>
                </div>
              </div>
              <div class="bni-chart-wrap">
                <svg :viewBox="`0 0 ${svgW} ${svgH}`" preserveAspectRatio="none" class="bni-rev-svg">
                  <text v-for="yl in yLabels" :key="yl.label" :x="10" :y="yl.y + 4" class="y-label">{{ yl.label }}</text>
                  <line v-for="yl in yLabels" :key="'g'+yl.label" :x1="chartLeft" :y1="yl.y" :x2="svgW - 10" :y2="yl.y" class="grid-ln" />
                  <rect v-for="(bar, i) in chartBars" :key="bar.label" :x="bar.x" :y="bar.y" :width="bw" :height="bar.h" rx="5" :class="['bar', { hl: hoveredBar === i || (hoveredBar === null && i === defaultHighlight) }]" @mouseenter="hoveredBar = i" @mouseleave="hoveredBar = null" />
                  <line v-if="activeBar" :x1="activeBar.x + bw / 2" :y1="chartTop" :x2="activeBar.x + bw / 2" :y2="chartBottom" class="active-line" />
                  <text v-for="(bar, i) in chartBars" :key="'x'+i" :x="bar.x + bw / 2" :y="chartBottom + 16" text-anchor="middle" class="x-label" :class="{ hl: i === defaultHighlight }">{{ bar.label }}</text>
                </svg>
                <div v-if="activeBar" class="bni-tooltip" :style="{ left: tooltipLeft }">
                  <strong>{{ activeBar.label }}</strong>
                  <span>{{ formatCount(activeBar.value) }} leads</span>
                </div>
              </div>
            </article>

            <!-- CALENDAR -->
            <article v-if="element.key === 'calendar'" class="bni-card bni-cal-card">
              <div class="bni-card-head">
                <h2>{{ __('Kalender') }}</h2>
              </div>
              <div class="bni-cal-month-nav">
                <button class="bni-cal-arrow" @click="prevWeek"><FeatherIcon name="chevron-left" class="h-4 w-4" /></button>
                <strong>{{ currentMonthYearLabel }}</strong>
                <button class="bni-cal-arrow" @click="nextWeek"><FeatherIcon name="chevron-right" class="h-4 w-4" /></button>
              </div>
              <div class="bni-cal-daynames">
                <span v-for="d in dayNames" :key="d">{{ d }}</span>
              </div>
              <div class="bni-cal-dates">
                <span
                  v-for="dt in weekDates"
                  :key="dt.toISOString()"
                  :class="{ active: isDateSelected(dt) }"
                  @click="selectDate(dt)"
                >{{ dt.getDate() }}</span>
              </div>
              <div class="bni-cal-events">
                <template v-if="filteredEvents.length > 0">
                  <div v-for="evt in filteredEvents" :key="evt.name" class="bni-evt">
                    <div class="bni-evt-body">
                      <strong>{{ evt.subject }}</strong>
                      <span class="bni-evt-time">{{ formatEventTime(evt.starts_on, evt.ends_on) }}</span>
                    </div>
                    <div class="bni-evt-foot">
                      <div class="bni-avatars">
                        <span style="background:#3aaca8;color:#fff">{{ getEventInitials(evt.subject) }}</span>
                      </div>
                      <span class="bni-evt-loc">{{ evt.event_type || 'Di Google Meet' }} ›</span>
                    </div>
                  </div>
                </template>
                <div v-else class="bni-evt-empty">
                  <FeatherIcon name="calendar" class="h-6 w-6 opacity-40 mb-1" />
                  <span>{{ __('Tidak ada agenda hari ini') }}</span>
                </div>
              </div>
            </article>

            <!-- LEAD MANAGEMENT -->
            <article v-if="element.key === 'leadManagement'" class="bni-card">
              <div class="bni-card-head"><h2>{{ __('Manajemen Leads') }}</h2></div>
              <div class="bni-lead-tabs">
                <button v-for="tab in leadTabs" :key="tab" :class="{ active: activeLeadTab === tab }" @click="activeLeadTab = tab">{{ tab }}</button>
              </div>
              <div class="bni-lead-bars">
                <div v-for="item in displayLeadBars" :key="item.label" class="bni-lb-row">
                  <span class="bni-lb-label">{{ item.label }}</span>
                  <div class="bni-lb-track"><div class="bni-lb-fill" :style="{ width: `${item.percent}%` }"></div></div>
                </div>
              </div>
            </article>

            <!-- BANK BREAKDOWN (PIE) -->
            <article v-if="element.key === 'bankBreakdown'" class="bni-card">
              <div class="bni-card-head"><h2>{{ __('Bank Breakdown') }}</h2></div>
              <div class="bni-pie-wrap">
                <svg viewBox="0 0 100 100" class="bni-pie-svg">
                  <path v-for="s in pieChartData" :key="s.label" :d="s.path" :fill="s.color" stroke="#fff" stroke-width="1.5" />
                </svg>
                <div class="bni-pie-legend">
                  <div v-for="s in pieChartData.slice(0, 6)" :key="s.label" class="bni-pie-legend-item">
                    <span class="bni-pie-dot" :style="{ background: s.color }"></span>
                    <span class="bni-pie-lname">{{ s.label }}</span>
                    <span class="bni-pie-lpct">{{ s.percentLabel }}</span>
                  </div>
                </div>
              </div>
              <button class="bni-see-all" @click="goToLeads">{{ __('Most active organizations') }} <FeatherIcon name="arrow-right" class="h-3.5 w-3.5" /></button>
            </article>

            <!-- PIC OWNERSHIP -->
            <article v-if="element.key === 'picOwnership'" class="bni-card">
              <div class="bni-card-head"><h2>{{ __('PIC Ownership') }}</h2></div>
              <div class="bni-rank-list">
                <div v-for="(owner, i) in displayPicOwnership" :key="owner.label" class="bni-rank-row">
                  <span class="bni-rank-num">{{ i + 1 }}</span>
                  <span class="bni-rank-name">{{ owner.label }}</span>
                  <strong class="bni-rank-pct">{{ owner.count }}</strong>
                </div>
              </div>
              <button class="bni-see-all" @click="goToLeads">{{ __('Lead referrers / PIC') }} <FeatherIcon name="arrow-right" class="h-3.5 w-3.5" /></button>
            </article>

            <!-- FOLLOW-UP LOAD -->
            <article v-if="element.key === 'followUpLoad'" class="bni-card">
              <div class="bni-card-head"><h2>{{ __('Follow-up Load') }}</h2></div>
              <div class="bni-lead-bars">
                <div v-for="item in displayFollowUpLoad" :key="item.label" class="bni-lb-row">
                  <span class="bni-lb-label">{{ item.label }}</span>
                  <div class="bni-lb-track"><div class="bni-lb-fill" :style="{ width: `${item.percent}%` }"></div></div>
                </div>
              </div>
              <div class="mt-4 grid grid-cols-2 gap-3">
                <div class="rounded-lg border border-emerald-100 bg-emerald-50 px-3 py-3 text-center">
                  <div class="text-xl font-bold text-emerald-700">{{ followUpSummary.completed }}</div>
                  <div class="text-xs text-emerald-700">{{ __('Completed') }}</div>
                </div>
                <div class="rounded-lg border border-cyan-100 bg-cyan-50 px-3 py-3 text-center">
                  <div class="text-xl font-bold text-cyan-700">{{ followUpSummary.pending }}</div>
                  <div class="text-xs text-cyan-700">{{ __('Pending') }}</div>
                </div>
              </div>
            </article>
          </div>
      </div>
      <!-- end v-for widgets -->

    </div>

    <!-- ═══ Import Dialog ═══ -->
    <Dialog v-model="showImport" :options="{ title: __('Imports'), size: 'sm' }">
      <template #body-content>
        <div class="space-y-1 pt-3">
          <button v-for="opt in importOptions" :key="opt.label" class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm hover:bg-slate-50 text-left transition-colors" @click="runImport(opt)">
            <FeatherIcon :name="opt.icon" class="h-4 w-4 text-teal-600 shrink-0" />
            <span>{{ opt.label }}</span>
            <FeatherIcon name="external-link" class="h-3.5 w-3.5 text-slate-300 ml-auto" />
          </button>
        </div>
      </template>
    </Dialog>

    <!-- ═══ Export Dialog ═══ -->
    <Dialog v-model="showExport" :options="{ title: __('Exports'), size: 'sm' }">
      <template #body-content>
        <div class="space-y-1 pt-3">
          <button v-for="opt in exportOptions" :key="opt.label" class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm hover:bg-slate-50 text-left transition-colors" @click="runExport(opt)">
            <FeatherIcon :name="opt.icon" class="h-4 w-4 text-teal-600 shrink-0" />
            <span>{{ opt.label }}</span>
            <FeatherIcon name="external-link" class="h-3.5 w-3.5 text-slate-300 ml-auto" />
          </button>
        </div>
      </template>
    </Dialog>

  </div>
</template>

<script setup>
import { Dialog, FeatherIcon, call, createResource, usePageMeta, toast } from 'frappe-ui'
import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Sortable from 'sortablejs'
import html2pdf from 'html2pdf.js'

const router = useRouter()

// ─── Widget Configuration (draggable + toggleable) ─────────
const defaultWidgets = [
  { key: 'metrics', label: 'Metrics', icon: 'activity', visible: true },
  { key: 'revenue', label: 'Revenue Chart', icon: 'bar-chart-2', visible: true },
  { key: 'calendar', label: 'Calendar', icon: 'calendar', visible: true },
  { key: 'leadManagement', label: 'Lead Management', icon: 'users', visible: true },
  { key: 'bankBreakdown', label: 'Bank Breakdown', icon: 'building-2', visible: true },
  { key: 'picOwnership', label: 'PIC Ownership', icon: 'user-check', visible: true },
  { key: 'followUpLoad', label: 'Follow-up Load', icon: 'check-circle', visible: true },
]
const STORAGE_KEY = 'bni_dashboard_widgets'

function loadWidgets() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) return JSON.parse(saved)
  } catch {}
  return defaultWidgets.map(w => ({ ...w }))
}

const widgets = ref(loadWidgets())
const showCustomize = ref(false)

function saveWidgets() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(widgets.value))
}

function exitCustomize() {
  showCustomize.value = false
}

function widgetVisible(key) {
  const w = widgets.value.find(w => w.key === key)
  return w ? w.visible : true
}

function widgetOrder(key) {
  return widgets.value.findIndex(w => w.key === key)
}

function toggleWidget(key) {
  const w = widgets.value.find(w => w.key === key)
  if (w) { w.visible = !w.visible; saveWidgets() }
}

function onDragEnd() {
  saveWidgets()
}

function resetWidgets() {
  widgets.value = defaultWidgets.map(w => ({ ...w }))
  saveWidgets()
}

// ─── SortableJS (direct, no vuedraggable) ──────────────────
const widgetsContainerRef = ref(null)
let sortableInstance = null

function initSortable() {
  if (sortableInstance || !widgetsContainerRef.value) return
  sortableInstance = Sortable.create(widgetsContainerRef.value, {
    animation: 200,
    easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    ghostClass: 'bni-ghost',
    dragClass: 'bni-dragging',
    handle: '.bni-drag-handle',
    onEnd(evt) {
      if (evt.oldIndex === evt.newIndex) return
      const newOrder = [...widgets.value]
      const [moved] = newOrder.splice(evt.oldIndex, 1)
      newOrder.splice(evt.newIndex, 0, moved)
      widgets.value = newOrder
      saveWidgets()
    },
  })
}

function destroySortable() {
  if (sortableInstance) {
    sortableInstance.destroy()
    sortableInstance = null
  }
}

watch(showCustomize, async (val) => {
  if (val) {
    await nextTick()
    initSortable()
  } else {
    destroySortable()
  }
})

onMounted(() => {
  if (showCustomize.value) {
    nextTick(initSortable)
  }
})

onUnmounted(() => {
  destroySortable()
})

// ─── Import / Export Dialogs ───────────────────────────────
const showImport = ref(false)
const showExport = ref(false)

const importOptions = [
  { label: 'Import Leads', doctype: 'CRM Lead', icon: 'users' },
  { label: 'Import Customers', doctype: 'Customer', icon: 'briefcase' },
  { label: 'Import Credit Facilities', doctype: 'CRM Credit Facility', icon: 'dollar-sign' },
  { label: 'Import Risk Profiles', doctype: 'CRM Risk Profile', icon: 'activity' },
]
const exportOptions = [
  { label: 'Export Dashboard PDF', format: 'pdf', icon: 'file-text' },
  { label: 'Export Dashboard Excel', format: 'xlsx', icon: 'file' },
  { label: 'Export Leads', doctype: 'CRM Lead', icon: 'users' },
  { label: 'Export Portfolio Report', format: 'pdf', icon: 'bar-chart' },
]

async function runImport(opt) {
  showImport.value = false
  if (opt.doctype) {
    window.open(`/app/data-import?reference_doctype=${encodeURIComponent(opt.doctype)}`, '_blank')
  }
}

function downloadBlob(content, filename, mime) {
  const blob = new Blob([content], { type: mime })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

function jsonToCsv(rows) {
  if (!rows.length) return ''
  const keys = Object.keys(rows[0])
  const header = keys.join(',')
  const lines = rows.map(r =>
    keys.map(k => {
      const v = r[k]
      const s = v == null ? '' : String(v)
      return s.includes(',') || s.includes('"') || s.includes('\n') ? `"${s.replace(/"/g, '""')}"` : s
    }).join(',')
  )
  return [header, ...lines].join('\n')
}

function exportDashboardExcel() {
  const d = data.value
  const rows = []

  // Metrics
  if (d.metrics?.length) {
    d.metrics.forEach(m => rows.push({ Section: 'Metrics', Label: m.label, Value: m.value ?? 0, Change: `${m.change ?? 0}%` }))
  }

  // Revenue / Company Breakdown
  if (d.revenue?.months?.length) {
    d.revenue.months.forEach(m => rows.push({ Section: 'Revenue Breakdown', Label: m.label, Value: m.value ?? m.count ?? 0, Change: '' }))
  }

  // Lead Management
  const lm = d.lead_management
  if (lm) {
    ;['status', 'source', 'qualification'].forEach(tab => {
      if (lm[tab]?.length) {
        lm[tab].forEach(r => rows.push({ Section: `Lead Management - ${tab}`, Label: r.label, Value: r.percent ?? 0, Change: '' }))
      }
    })
  }

  // PIC Ownership
  if (d.lead_gen?.pic_ownership?.length) {
    d.lead_gen.pic_ownership.forEach(o => rows.push({ Section: 'PIC Ownership', Label: o.label, Value: o.count ?? 0, Change: '' }))
  }

  // Follow-up Load
  if (d.lead_gen?.follow_up_load?.status_rows?.length) {
    d.lead_gen.follow_up_load.status_rows.forEach(r => rows.push({ Section: 'Follow-up Load', Label: r.label, Value: r.percent ?? 0, Change: '' }))
    rows.push({ Section: 'Follow-up Load', Label: 'Completed', Value: d.lead_gen.follow_up_load.completed ?? 0, Change: '' })
    rows.push({ Section: 'Follow-up Load', Label: 'Pending', Value: d.lead_gen.follow_up_load.pending ?? 0, Change: '' })
  }

  if (!rows.length) {
    toast({ title: __('No dashboard data to export'), variant: 'warning' })
    return
  }

  const csv = jsonToCsv(rows)
  const bom = '\uFEFF'
  downloadBlob(bom + csv, `dashboard-${new Date().toISOString().slice(0, 10)}.csv`, 'text/csv;charset=utf-8;')
}

async function runExport(opt) {
  showExport.value = false

  if (opt.label === 'Export Dashboard PDF') {
    const el = document.querySelector('.bni-widgets-container')
    if (!el) { toast({ title: __('Dashboard content not found'), variant: 'warning' }); return }
    try {
      await html2pdf().set({
        margin: 8, filename: `dashboard-${new Date().toISOString().slice(0, 10)}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' },
      }).from(el).save()
      toast({ title: __('PDF exported successfully'), variant: 'success' })
    } catch (e) {
      toast({ title: __('PDF export failed'), variant: 'error' })
      console.error(e)
    }
    return
  }

  if (opt.label === 'Export Dashboard Excel') {
    exportDashboardExcel()
    return
  }

  if (opt.label === 'Export Portfolio Report') {
    try {
      const result = await call('crm.api.portfolio_monitoring.generate_report', {
        template: 'Committee Meeting Summary Package (PDF)',
        send_email: false,
      })
      if (result?.data) {
        const csv = jsonToCsv([result.data])
        const bom = '\uFEFF'
        downloadBlob(bom + csv, `portfolio-report-${new Date().toISOString().slice(0, 10)}.csv`, 'text/csv;charset=utf-8;')
        toast({ title: __('Portfolio report exported'), variant: 'success' })
      }
    } catch (e) {
      toast({ title: __('Portfolio report export failed'), variant: 'error' })
      console.error(e)
    }
    return
  }

  // Export Leads / other doctypes via API
  if (opt.doctype) {
    try {
      const result = await call('crm.api.lead_management.export_leads', { format: 'CSV' })
      if (result?.file_url) {
        window.open(result.file_url, '_blank')
      } else if (result?.async) {
        toast({ title: __('Export is being processed. You will be notified when ready.'), variant: 'info' })
      } else {
        toast({ title: __('Export failed'), variant: 'error' })
      }
    } catch (e) {
      toast({ title: __('Export failed'), variant: 'error' })
      console.error(e)
    }
  }
}

// ─── Reactive State ───────────────────────────────────────
const aiSearch = ref('')
const activeRevenuePeriod = ref('1T')
const hoveredBar = ref(null)
const activeLeadTab = ref('Status')

// ─── Dynamic Calendar Setup ──────────────────────────────
const currentAnchorDate = ref(new Date())
const selectedDate = ref(new Date())

const weekDates = computed(() => {
  const dates = []
  const startOfWeek = new Date(currentAnchorDate.value)
  const day = startOfWeek.getDay() // 0 = Sunday, 1 = Monday, etc.
  startOfWeek.setDate(startOfWeek.getDate() - day)

  for (let i = 0; i < 7; i++) {
    const d = new Date(startOfWeek)
    d.setDate(startOfWeek.getDate() + i)
    dates.push(d)
  }
  return dates
})

const currentMonthYearLabel = computed(() => {
  const d = weekDates.value[3] || currentAnchorDate.value
  const months = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
  ]
  return `${months[d.getMonth()]} ${d.getFullYear()}`
})

function selectDate(date) {
  selectedDate.value = date
}

function isDateSelected(date) {
  return date.getDate() === selectedDate.value.getDate() &&
         date.getMonth() === selectedDate.value.getMonth() &&
         date.getFullYear() === selectedDate.value.getFullYear()
}

function prevWeek() {
  const d = new Date(currentAnchorDate.value)
  d.setDate(d.getDate() - 7)
  currentAnchorDate.value = d
  
  const sel = new Date(selectedDate.value)
  sel.setDate(sel.getDate() - 7)
  selectedDate.value = sel
}

function nextWeek() {
  const d = new Date(currentAnchorDate.value)
  d.setDate(d.getDate() + 7)
  currentAnchorDate.value = d
  
  const sel = new Date(selectedDate.value)
  sel.setDate(sel.getDate() + 7)
  selectedDate.value = sel
}

const filteredEvents = computed(() => {
  const events = data.value.calendar || []
  const selY = selectedDate.value.getFullYear()
  const selM = selectedDate.value.getMonth()
  const selD = selectedDate.value.getDate()

  return events.filter(evt => {
    if (!evt.starts_on) return false
    const evtDate = new Date(evt.starts_on.replace(' ', 'T'))
    return evtDate.getFullYear() === selY &&
           evtDate.getMonth() === selM &&
           evtDate.getDate() === selD
  })
})

function formatEventTime(startStr, endStr) {
  if (!startStr) return ''
  try {
    const start = new Date(startStr.replace(' ', 'T'))
    const startH = String(start.getHours()).padStart(2, '0')
    const startM = String(start.getMinutes()).padStart(2, '0')
    
    let endPart = ''
    if (endStr) {
      const end = new Date(endStr.replace(' ', 'T'))
      const endH = String(end.getHours()).padStart(2, '0')
      const endM = String(end.getMinutes()).padStart(2, '0')
      endPart = ` - ${endH}.${endM}`
    }
    return `${startH}.${startM}${endPart} WIB`
  } catch {
    return startStr
  }
}

function getEventInitials(subject) {
  if (!subject) return 'E'
  return subject.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
}

// ─── Constants ────────────────────────────────────────────
const revenuePeriods = ['1H', '1M', '3M', '6M', '1T', 'SEMUA']
const leadTabs = ['Status', 'Sumber', 'Kualifikasi']
const dayNames = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab']

// ─── Chart Dimensions ─────────────────────────────────────
const svgW = 720
const svgH = 260
const chartLeft = 42
const chartBottom = 230
const chartTop = 20
const chartH = chartBottom - chartTop
const bw = 36
const barGap = 55
const defaultHighlight = 0

// ─── API ──────────────────────────────────────────────────
const toDate = computed(() => new Date().toISOString().slice(0, 10))
const fromDate = computed(() => {
  const d = new Date()
  const days = { '1H': 7, '1M': 30, '3M': 90, '6M': 180, '1T': 365, 'SEMUA': 3650 }[activeRevenuePeriod.value] || 365
  d.setDate(d.getDate() - days)
  return d.toISOString().slice(0, 10)
})

const dashboard = createResource({
  url: 'crm.api.dashboard.get_bni_crm_dashboard',
  auto: true,
  makeParams() { return { from_date: fromDate.value, to_date: toDate.value } },
})

const data = computed(() => dashboard.data || {})

// ─── Metrics ──────────────────────────────────────────────
const displayMetrics = computed(() => {
  const api = data.value.metrics || []
  return api.map(m => ({
    ...m,
    icon: m.icon || 'activity',
    displayValue: fmtMetric(m),
    changeNum: Number(m.change || 0),
    isPositive: Number(m.change || 0) >= 0,
  }))
})

function fmtMetric(m) {
  return `${Number(m.value || 0).toLocaleString('id-ID')}${m.suffix || ''}`
}

// ─── Company Breakdown Chart ──────────────────────────────
const chartSummary = computed(() => ({
  total: data.value.revenue?.total ?? 0,
  change: data.value.revenue?.change ?? 0,
}))

const revenueMonths = computed(() =>
  data.value.revenue?.months || []
)

const maxRev = computed(() => Math.max(...revenueMonths.value.map(m => Number(m.value || m.count || 0)), 1))

const yLabels = computed(() => {
  const maxValue = maxRev.value || 1
  return [1, 0.75, 0.5, 0.25, 0].map((ratio) => ({
    label: formatCount(Math.round(maxValue * ratio)),
    y: chartTop + (chartH * (1 - ratio)),
  }))
})

const chartBars = computed(() =>
  revenueMonths.value.map((m, i) => {
    const value = Number(m.value || m.count || 0)
    const pct = value / maxRev.value
    const h = Math.max(pct * chartH, 4)
    return { label: m.label, value, x: chartLeft + 10 + i * barGap, y: chartBottom - h, h }
  })
)

const activeBar = computed(() => {
  const idx = hoveredBar.value !== null ? hoveredBar.value : defaultHighlight
  return chartBars.value[idx] || null
})

const tooltipLeft = computed(() => {
  if (!activeBar.value) return '0%'
  return `${((activeBar.value.x + bw / 2) / svgW) * 100}%`
})

function formatCount(v) {
  return Number(v || 0).toLocaleString('id-ID')
}

// ─── Lead Management ─────────────────────────────────────
const displayLeadBars = computed(() => {
  const lm = data.value.lead_management
  if (lm) {
    const map = { Status: lm.status, Sumber: lm.source, Kualifikasi: lm.qualification }
    const rows = map[activeLeadTab.value]
    if (rows?.length) return rows.map(r => ({ label: r.label, percent: r.percent || 0 }))
  }
  return []
})

// ─── Supporting Lists ─────────────────────────────────────
const displayCompanies = computed(() => data.value.lead_gen?.company_breakdown || [])

const displayPicOwnership = computed(() => data.value.lead_gen?.pic_ownership || [])

const displayFollowUpLoad = computed(() => data.value.lead_gen?.follow_up_load?.status_rows || [])

const followUpSummary = computed(() => ({
  pending: data.value.lead_gen?.follow_up_load?.pending ?? 0,
  completed: data.value.lead_gen?.follow_up_load?.completed ?? 0,
}))

// ─── Last Updated ─────────────────────────────────────────
const notifCount = computed(() => data.value.lead_gen?.overview?.converted ?? 0)

const lastUpdated = computed(() => {
  if (data.value.last_updated) {
    return new Intl.DateTimeFormat('id-ID', { hour: '2-digit', minute: '2-digit' }).format(new Date(data.value.last_updated))
  }
  return __('now')
})

// ─── Navigation ────────────────────────────────────────────
function goToLeads() { router.push({ name: 'Lead' }) }
function goToCustomers() { router.push({ name: 'Customer' }) }

// ─── Bank Breakdown Pie Chart ──────────────────────────────
const pieColors = ['#008c95', '#0d9488', '#14b8a6', '#2dd4bf', '#5eead4', '#99f6e4', '#ccfbf1']
const pieChartData = computed(() => {
  const items = displayCompanies.value || []
  const total = items.reduce((s, i) => s + (Number(i.count) || 0), 0) || 1
  let angle = -90
  return items.map((item, idx) => {
    const pct = (Number(item.count) || 0) / total
    const startAngle = angle
    const endAngle = angle + pct * 360
    angle = endAngle
    const sx = 50 + 40 * Math.cos((startAngle * Math.PI) / 180)
    const sy = 50 + 40 * Math.sin((startAngle * Math.PI) / 180)
    const ex = 50 + 40 * Math.cos((endAngle * Math.PI) / 180)
    const ey = 50 + 40 * Math.sin((endAngle * Math.PI) / 180)
    const large = pct > 0.5 ? 1 : 0
    return {
      ...item,
      pct,
      percentLabel: `${(pct * 100).toFixed(1)}%`,
      path: pct >= 1
        ? `M 50 50 L 50 10 A 40 40 0 1 1 49.999 10 Z`
        : `M 50 50 L ${sx.toFixed(1)} ${sy.toFixed(1)} A 40 40 0 ${large} 1 ${ex.toFixed(1)} ${ey.toFixed(1)} Z`,
      color: pieColors[idx % pieColors.length],
    }
  })
})

// ─── Lifecycle ────────────────────────────────────────────
watch(activeRevenuePeriod, () => dashboard.fetch())
usePageMeta(() => ({ title: __('Dashboard') }))
</script>

<style scoped>
/* ═══ Design Tokens ═══════════════════════════════════════ */
.bni-dashboard {
  --bg: #f7fafb;
  --card: #ffffff;
  --border: #e6ecef;
  --border-soft: #edf2f4;
  --text: #101828;
  --text-2: #667085;
  --text-3: #98a2b3;
  --teal: #008c95;
  --teal-dark: #00747c;
  --teal-soft: #dff7f7;
  --teal-chart: #0e9298;
  --cyan-light: #d9f3f4;
  --green: #12b76a;
  --green-soft: #ecfdf3;
  --red: #f04438;
  --red-soft: #fff1f3;
  --orange: #f79009;
  --shadow: 0 8px 20px rgba(16,24,40,.05);
  --shadow-soft: 0 4px 12px rgba(16,24,40,.04);
  --radius: 16px;
  --radius-sm: 10px;

  background: var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
  height: 100%;
  overflow-y: auto;
}
.bni-content {
  max-width: 1480px;
  margin: 0 auto;
  padding: 18px 22px 28px;
}

/* ═══ TOPBAR ═════════════════════════════════════════════ */
.bni-topbar {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-soft);
  padding: 16px 20px;
  margin-bottom: 18px;
}
.bni-topbar-row1 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}
.bni-topbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bni-title-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: var(--teal-soft);
  color: var(--teal);
  display: flex;
  align-items: center;
  justify-content: center;
}
.bni-topbar-left h1 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}
.bni-topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.bni-search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  width: 220px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0 12px;
  background: var(--card);
}
.bni-search-box input {
  border: 0;
  outline: 0;
  font-size: 12px;
  flex: 1;
  min-width: 0;
  background: transparent;
  font-family: inherit;
}
.bni-icon-btn {
  height: 36px;
  width: 36px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text-2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color .15s, color .15s;
}
.bni-icon-btn:hover {
  border-color: var(--teal);
  color: var(--teal);
}
.bni-icon-btn-wrap {
  position: relative;
  display: inline-flex;
}
.bni-notif-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  height: 18px;
  min-width: 18px;
  border-radius: 999px;
  background: var(--red);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  pointer-events: none;
}
.bni-topbar-row2 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid var(--border-soft);
}
.bni-updated-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--green);
  font-size: 12px;
  font-weight: 600;
}
.bni-action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}
.bni-action-btn {
  height: 34px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card);
  padding: 0 14px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-family: inherit;
  transition: border-color .15s;
}
.bni-action-btn:hover {
  border-color: var(--teal);
}
.bni-export-btn {
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--teal);
  color: #fff;
  border: none;
  padding: 0 16px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-family: inherit;
  transition: background .15s;
}
.bni-export-btn:hover {
  background: var(--teal-dark);
}

/* ═══ METRIC CARDS ═══════════════════════════════════════ */
.bni-metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.bni-metric-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  box-shadow: var(--shadow);
  position: relative;
  transition: box-shadow .2s, transform .2s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.bni-metric-card:hover {
  box-shadow: 0 12px 28px rgba(16,24,40,.08);
  transform: translateY(-1px);
}
.bni-mc-top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.bni-mc-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--teal-soft);
  color: var(--teal);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.bni-mc-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-2);
  flex: 1;
}
.bni-mc-info {
  width: 14px;
  height: 14px;
  color: var(--text-3);
  opacity: .6;
  cursor: help;
}
.bni-mc-bottom {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 2px;
}
.bni-mc-value {
  font-size: 28px;
  font-weight: 800;
  line-height: 1.1;
  color: var(--text);
}
.bni-mc-change {
  font-size: 12px;
  font-weight: 700;
  border-radius: 6px;
  padding: 2px 6px;
}
.bni-mc-change.up {
  color: var(--green);
  background: var(--green-soft);
}
.bni-mc-change.down {
  color: var(--red);
  background: var(--red-soft);
}
.bni-mc-caption {
  font-size: 11px;
  color: var(--text-3);
  font-weight: 500;
}

/* ═══ SHARED CARD ════════════════════════════════════════ */
.bni-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: var(--shadow);
  min-width: 0;
}
.bni-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.bni-card-head h2 {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
}
.bni-dots {
  background: none;
  border: none;
  color: var(--text-3);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
}
.bni-dots:hover { background: var(--teal-soft); color: var(--teal); }

/* ═══ WIDGETS CONTAINER (draggable) ════════════════════ */
.bni-widgets-container {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  min-height: 100px;
}
.bni-widget {
  width: 100%;
}
.bni-widget-revenue { width: calc(66.666% - 8px); }
.bni-widget-calendar { width: calc(33.333% - 8px); }
.bni-widget-leadManagement { width: calc(25% - 12px); }
.bni-widget-bankBreakdown { width: calc(25% - 12px); }
.bni-widget-picOwnership { width: calc(25% - 12px); }
.bni-widget-followUpLoad { width: calc(25% - 12px); }
@media (max-width: 1000px) {
  .bni-widget-revenue,
  .bni-widget-calendar,
  .bni-widget-leadManagement,
  .bni-widget-bankBreakdown,
  .bni-widget-picOwnership,
  .bni-widget-followUpLoad {
    width: 100%;
  }
}
.bni-ghost {
  opacity: 0.3;
  outline: 2px dashed var(--teal);
  outline-offset: 2px;
  border-radius: var(--radius);
}
.bni-dragging {
  opacity: 0.8;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

/* ─── Customize Mode Banner ──────────────────────────── */
.bni-customize-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  margin-bottom: 16px;
  border-radius: var(--radius-sm);
  background: var(--teal-soft);
  color: var(--teal);
  font-size: 13px;
  font-weight: 500;
}
.bni-customize-done {
  margin-left: auto;
  padding: 4px 14px;
  border-radius: 6px;
  border: 1px solid var(--teal);
  background: var(--card);
  color: var(--teal);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.bni-customize-done:hover {
  background: var(--teal);
  color: #fff;
}
.bni-customize-reset {
  padding: 4px 14px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text-2);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}
.bni-customize-reset:hover {
  border-color: var(--red);
  color: var(--red);
}

/* ─── Widget Header (drag handle + title) ────────────── */
.bni-widget-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: var(--radius-sm);
  background: var(--bg);
  border: 1px solid var(--border);
  user-select: none;
}
.bni-drag-handle {
  cursor: grab;
  color: var(--text-2);
  display: inline-flex;
  align-items: center;
  touch-action: none;
}
.bni-drag-handle:hover { color: var(--teal); }
.bni-widget-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}
.bni-widget-toggle {
  margin-left: auto;
  border: 0;
  background: transparent;
  color: var(--text-2);
  cursor: pointer;
  padding: 2px;
}
.bni-widget-toggle:hover { color: var(--teal); }

/* ─── Customize mode: entire widget is draggable ────── */
.bni-customize-active {
  cursor: grab;
  user-select: none;
}
.bni-customize-active:active {
  cursor: grabbing;
}

/* ─── Hidden widget shown dimmed in customize mode ─── */
.bni-widget-dimmed {
  opacity: 0.45;
  transition: opacity 0.2s;
}
.bni-widget-dimmed:hover {
  opacity: 0.85;
}

/* ─── Revenue Card ───────────────────────────────────── */
.bni-revenue-card { min-height: 360px; }
.bni-rev-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.bni-rev-left h2 {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 6px;
}
.bni-rev-total {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.bni-rev-total strong {
  font-size: 22px;
  font-weight: 800;
}
.bni-badge-change {
  font-size: 12px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
}
.bni-badge-change.up { color: var(--green); background: var(--green-soft); }
.bni-badge-change.down { color: var(--red); background: var(--red-soft); }
.bni-vs {
  font-size: 12px;
  color: var(--text-3);
  font-weight: 500;
}
.bni-rev-periods {
  display: flex;
  background: var(--bg);
  border-radius: 8px;
  padding: 3px;
  gap: 2px;
}
.bni-rev-periods button {
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  padding: 5px 10px;
  color: var(--text-2);
  cursor: pointer;
  font-family: inherit;
  transition: all .15s;
}
.bni-rev-periods button.active {
  background: #1a2332;
  color: #fff;
}
.bni-rev-periods button:hover:not(.active) {
  background: var(--border-soft);
}

/* ─── Chart ──────────────────────────────────────────── */
.bni-chart-wrap {
  position: relative;
  height: 260px;
}
.bni-rev-svg {
  width: 100%;
  height: 100%;
}
.y-label {
  fill: var(--text-3);
  font-size: 10px;
  font-weight: 500;
}
.grid-ln {
  stroke: var(--border-soft);
  stroke-width: 1;
}
.bar {
  fill: var(--cyan-light);
  transition: fill .15s;
  cursor: pointer;
}
.bar.hl {
  fill: var(--teal-chart);
}
.dash-ln {
  stroke: var(--teal);
  stroke-width: 1.5;
  stroke-dasharray: 4 3;
  opacity: .5;
}
.x-label {
  fill: var(--text-3);
  font-size: 11px;
  font-weight: 500;
}
.x-label.bold {
  fill: var(--text);
  font-weight: 700;
}
.bni-tooltip {
  position: absolute;
  top: 8px;
  transform: translateX(-50%);
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px 14px;
  box-shadow: 0 6px 18px rgba(0,0,0,.1);
  white-space: nowrap;
  pointer-events: none;
  z-index: 5;
}
.bni-tooltip strong {
  display: block;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 2px;
}
.bni-tooltip span {
  font-size: 12px;
  color: var(--text-2);
}
.bni-tooltip .t-up {
  color: var(--green);
  font-style: normal;
  font-weight: 700;
}

/* ─── Calendar Card ──────────────────────────────────── */
.bni-cal-card { display: flex; flex-direction: column; }
.bni-cal-month-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.bni-cal-month-nav strong {
  font-size: 14px;
}
.bni-cal-arrow {
  background: none;
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-2);
  transition: border-color .15s;
}
.bni-cal-arrow:hover { border-color: var(--teal); color: var(--teal); }
.bni-cal-daynames,
.bni-cal-dates {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  gap: 0;
}
.bni-cal-daynames {
  margin-bottom: 6px;
}
.bni-cal-daynames span {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-3);
  padding: 4px 0;
}
.bni-cal-dates {
  margin-bottom: 16px;
}
.bni-cal-dates span {
  font-size: 13px;
  font-weight: 600;
  padding: 6px 0;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  cursor: pointer;
  transition: background .15s;
}
.bni-cal-dates span:hover:not(.active) {
  background: var(--teal-soft);
}
.bni-cal-dates span.active {
  background: var(--teal);
  color: #fff;
}
.bni-cal-events {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}
.bni-evt {
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 12px 14px;
  background: var(--bg);
  transition: border-color .15s;
}
.bni-evt:hover { border-color: var(--teal); }
.bni-evt-body strong {
  display: block;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 3px;
  color: var(--text);
}
.bni-evt-time {
  font-size: 12px;
  color: var(--text-2);
}
.bni-evt-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}
.bni-avatars {
  display: flex;
  align-items: center;
}
.bni-avatars span {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
  margin-left: -6px;
}
.bni-avatars span:first-child { margin-left: 0; }
.bni-av-more {
  background: var(--border) !important;
  color: var(--text-2) !important;
  font-size: 9px !important;
}
.bni-evt-loc {
  font-size: 11px;
  font-weight: 600;
  color: var(--teal);
  cursor: pointer;
}
.bni-evt-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--bg);
  border: 1px dashed var(--border);
  border-radius: 12px;
  color: var(--text-2);
  font-size: 12px;
  text-align: center;
  gap: 6px;
}

/* ═══ BOTTOM GRID ═══════════════════════════════════════ */
/* (replaced by .bni-widgets-container above) */

/* ─── Lead Management ────────────────────────────────── */
.bni-lead-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border-soft);
  margin-bottom: 16px;
}
.bni-lead-tabs button {
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  padding: 8px 14px;
  color: var(--text-3);
  cursor: pointer;
  font-family: inherit;
  border-bottom: 2px solid transparent;
  transition: color .15s, border-color .15s;
}
.bni-lead-tabs button.active {
  color: var(--teal);
  border-bottom-color: var(--teal);
}
.bni-lead-tabs button:hover:not(.active) {
  color: var(--text-2);
}
.bni-lead-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.bni-lb-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bni-lb-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-2);
  width: 80px;
  flex-shrink: 0;
}
.bni-lb-track {
  flex: 1;
  height: 12px;
  border-radius: 999px;
  background: var(--border-soft);
  overflow: hidden;
}
.bni-lb-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #0e9298, #15b8bd);
  transition: width .4s ease;
}

/* ─── Pie Chart ────────────────────────────────────────── */
.bni-pie-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 4px;
}
.bni-pie-svg {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}
.bni-pie-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.bni-pie-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  line-height: 1.3;
}
.bni-pie-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.bni-pie-lname {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-2);
}
.bni-pie-lpct {
  font-weight: 600;
  color: var(--text);
  flex-shrink: 0;
}

/* ─── Drag and Drop ────────────────────────────────────── */
.bni-drag-handle {
  touch-action: none;
}
.bni-ghost {
  opacity: 0.4;
  background: #f0fdfa;
  border-radius: 8px;
}

/* ─── Map ────────────────────────────────────────────── */
.bni-map-wrap {
  position: relative;
  background: var(--bg);
  border-radius: 12px;
  padding: 10px;
}
.bni-map-container {
  width: 100%;
  height: 180px;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg);
  z-index: 1;
}
.bni-map-zoom {
  position: absolute;
  bottom: 14px;
  left: 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.bni-map-zoom button {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--card);
  font-size: 14px;
  font-weight: 700;
  color: var(--text-2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ─── Top Cabang ─────────────────────────────────────── */
.bni-rank-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 16px;
}
.bni-rank-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bni-rank-num {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: var(--bg);
  font-size: 11px;
  font-weight: 700;
  color: var(--text-2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.bni-rank-name {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}
.bni-rank-pct {
  font-size: 13px;
  font-weight: 700;
  color: var(--teal);
}
.bni-see-all {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: var(--teal);
  cursor: pointer;
  font-family: inherit;
  transition: background .15s, border-color .15s;
}
.bni-see-all:hover {
  background: var(--teal-soft);
  border-color: var(--teal);
}

/* ─── Retention ──────────────────────────────────────── */
.bni-ret-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.bni-ret-val {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
}
.bni-ret-legend {
  display: flex;
  gap: 14px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.bni-ret-legend span {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-2);
}
.bni-ret-legend i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.dot-ukm { background: #0e9298; }
.dot-kor { background: #5cc5c8; }
.dot-kon { background: #b5e4e5; }

.bni-ret-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 120px;
  border-bottom: 1px solid var(--border-soft);
  padding-bottom: 4px;
}
.bni-ret-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
}
.bni-ret-bars {
  display: flex;
  gap: 3px;
  align-items: flex-end;
  height: 100%;
  width: 100%;
}
.bni-ret-bars span {
  flex: 1;
  border-radius: 4px 4px 0 0;
  min-height: 3px;
  transition: height .4s ease;
}
.r-ukm { background: #0e9298; }
.r-kor { background: #5cc5c8; }
.r-kon { background: #b5e4e5; }
.bni-ret-col small {
  font-size: 10px;
  color: var(--text-3);
  font-weight: 500;
}
.bni-ret-col small.bold {
  color: var(--text);
  font-weight: 700;
}

/* ═══ RESPONSIVE ════════════════════════════════════════ */
@media (max-width: 1280px) {
  .bni-metric-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .bni-widget-revenue { width: calc(60% - 8px); }
  .bni-widget-calendar { width: calc(40% - 8px); }
  .bni-widget-leadManagement { width: calc(50% - 8px); }
  .bni-widget-bankBreakdown { width: calc(50% - 8px); }
  .bni-widget-picOwnership { width: calc(50% - 8px); }
  .bni-widget-followUpLoad { width: calc(50% - 8px); }
}
@media (max-width: 1024px) {
  .bni-widget-revenue,
  .bni-widget-calendar {
    width: 100%;
  }
}
@media (max-width: 768px) {
  .bni-content { padding: 12px 14px 20px; }
  .bni-topbar-row1,
  .bni-topbar-row2 {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .bni-topbar-right {
    flex-wrap: wrap;
    justify-content: flex-end;
  }
  .bni-search-box { width: 100%; }
  .bni-metric-grid {
    grid-template-columns: 1fr;
  }
  .bni-widget-revenue,
  .bni-widget-calendar,
  .bni-widget-leadManagement,
  .bni-widget-bankBreakdown,
  .bni-widget-picOwnership,
  .bni-widget-followUpLoad {
    width: 100%;
  }
  .bni-action-buttons { flex-wrap: wrap; }
}
</style>
