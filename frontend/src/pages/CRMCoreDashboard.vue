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
              <span class="bni-notif-badge">22</span>
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
            <button class="bni-action-btn">
              <FeatherIcon name="sliders" class="h-3.5 w-3.5" />
              {{ __('Customize Widget') }}
            </button>
            <button class="bni-action-btn">
              {{ __('Imports') }}
              <FeatherIcon name="chevron-down" class="h-3 w-3" />
            </button>
            <button class="bni-export-btn">
              {{ __('Exports') }}
              <FeatherIcon name="chevron-down" class="h-3 w-3" />
            </button>
          </div>
        </div>
      </header>

      <!-- ═══ METRIC CARDS ═══ -->
      <section class="bni-metric-grid">
        <article v-for="m in displayMetrics" :key="m.label" class="bni-metric-card">
          <div class="bni-mc-top">
            <div class="bni-mc-icon">
              <FeatherIcon :name="m.icon" class="h-[16px] w-[16px]" />
            </div>
            <span class="bni-mc-label">{{ m.label }}</span>
            <FeatherIcon name="info" class="h-3.5 w-3.5 bni-mc-info" />
          </div>
          <div class="bni-mc-body">
            <div class="bni-mc-bottom">
              <strong class="bni-mc-value">{{ m.displayValue }}</strong>
              <span :class="['bni-mc-change', m.isPositive ? 'up' : 'down']">
                {{ m.isPositive ? '↑' : '↓' }} {{ Math.abs(m.changeNum) }}%
              </span>
            </div>
            <span class="bni-mc-caption">{{ m.caption }}</span>
          </div>
        </article>
      </section>

      <!-- ═══ MAIN GRID: REVENUE + CALENDAR ═══ -->
      <section class="bni-main-grid">
        <!-- Revenue Card -->
        <article class="bni-card bni-revenue-card">
          <div class="bni-rev-header">
            <div class="bni-rev-left">
              <h2>{{ __('Pendapatan') }}</h2>
              <div class="bni-rev-total">
                <strong>{{ formatRupiah(displayRevenue.total) }}</strong>
                <span :class="['bni-badge-change', displayRevenue.change >= 0 ? 'up' : 'down']">
                  {{ displayRevenue.change >= 0 ? '↑' : '↓' }} {{ Math.abs(displayRevenue.change) }}%
                </span>
                <span class="bni-vs">{{ __('vs bulan lalu') }}</span>
              </div>
            </div>
            <div class="bni-rev-periods">
              <button
                v-for="p in revenuePeriods"
                :key="p"
                :class="{ active: activeRevenuePeriod === p }"
                @click="activeRevenuePeriod = p"
              >{{ p }}</button>
            </div>
          </div>
          <div class="bni-chart-wrap">
            <svg :viewBox="`0 0 ${svgW} ${svgH}`" preserveAspectRatio="none" class="bni-rev-svg">
              <!-- Y-axis labels -->
              <text v-for="yl in yLabels" :key="yl.label" :x="10" :y="yl.y + 4" class="y-label">{{ yl.label }}</text>
              <!-- Grid lines -->
              <line v-for="yl in yLabels" :key="'g'+yl.label" :x1="chartLeft" :y1="yl.y" :x2="svgW - 10" :y2="yl.y" class="grid-ln" />
              <!-- Bars -->
              <rect
                v-for="(bar, i) in chartBars"
                :key="bar.label"
                :x="bar.x"
                :y="bar.y"
                :width="bw"
                :height="bar.h"
                rx="5"
                :class="['bar', { hl: hoveredBar === i || (hoveredBar === null && i === defaultHighlight) }]"
                @mouseenter="hoveredBar = i"
                @mouseleave="hoveredBar = null"
              />
              <!-- Vertical dashed line for active bar -->
              <line
                v-if="activeBar"
                :x1="activeBar.x + bw/2" y1="15"
                :x2="activeBar.x + bw/2" :y2="chartBottom"
                class="dash-ln"
              />
              <!-- X labels -->
              <text
                v-for="(bar, i) in chartBars"
                :key="'xl'+bar.label"
                :x="bar.x + bw/2"
                :y="svgH - 2"
                text-anchor="middle"
                :class="['x-label', { bold: i === defaultHighlight }]"
              >{{ bar.label }}</text>
            </svg>
            <!-- Floating tooltip -->
            <div
              v-if="activeBar"
              class="bni-tooltip"
              :style="{ left: tooltipLeft }"
            >
              <strong>{{ activeBar.label }} 2025</strong>
              <span>{{ formatRupiah(activeBar.value) }} <em class="t-up">↑ 2%</em></span>
            </div>
          </div>
        </article>

        <!-- Calendar Card -->
        <article class="bni-card bni-cal-card">
          <div class="bni-card-head">
            <h2>{{ __('Kalender') }}</h2>
            <button class="bni-dots"><FeatherIcon name="more-vertical" class="h-4 w-4" /></button>
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
      </section>

      <!-- ═══ BOTTOM ANALYTICS GRID ═══ -->
      <section class="bni-bottom-grid">
        <!-- Manajemen Leads -->
        <article class="bni-card">
          <div class="bni-card-head">
            <h2>{{ __('Manajemen Leads') }}</h2>
            <button class="bni-dots"><FeatherIcon name="more-vertical" class="h-4 w-4" /></button>
          </div>
          <div class="bni-lead-tabs">
            <button
              v-for="tab in leadTabs"
              :key="tab"
              :class="{ active: activeLeadTab === tab }"
              @click="activeLeadTab = tab"
            >{{ tab }}</button>
          </div>
          <div class="bni-lead-bars">
            <div v-for="item in displayLeadBars" :key="item.label" class="bni-lb-row">
              <span class="bni-lb-label">{{ item.label }}</span>
              <div class="bni-lb-track">
                <div class="bni-lb-fill" :style="{ width: `${item.percent}%` }"></div>
              </div>
            </div>
          </div>
        </article>

        <!-- Cabang / Wilayah -->
        <article class="bni-card">
          <div class="bni-card-head">
            <h2>{{ __('Cabang / Wilayah') }}</h2>
            <button class="bni-dots"><FeatherIcon name="grid" class="h-4 w-4" /></button>
          </div>
          <div class="bni-map-wrap">
            <div :id="mapId" class="bni-map-container"></div>
            <div class="bni-map-zoom">
              <button @click="mapZoomIn">+</button>
              <button @click="mapZoomOut">−</button>
            </div>
          </div>
        </article>

        <!-- Top Cabang -->
        <article class="bni-card">
          <div class="bni-card-head">
            <h2>{{ __('Top Cabang') }}</h2>
            <button class="bni-dots"><FeatherIcon name="more-vertical" class="h-4 w-4" /></button>
          </div>
          <div class="bni-rank-list">
            <div v-for="(b, i) in displayBranches" :key="b.name" class="bni-rank-row">
              <span class="bni-rank-num">{{ i + 1 }}</span>
              <span class="bni-rank-name">{{ b.name }}</span>
              <strong class="bni-rank-pct">{{ b.percent }}%</strong>
            </div>
          </div>
          <button class="bni-see-all">
            {{ __('Lihat semua') }}
            <FeatherIcon name="arrow-right" class="h-3.5 w-3.5" />
          </button>
        </article>

        <!-- Tingkat Retensi -->
        <article class="bni-card">
          <div class="bni-card-head">
            <h2>{{ __('Tingkat Retensi') }}</h2>
            <button class="bni-dots"><FeatherIcon name="more-vertical" class="h-4 w-4" /></button>
          </div>
          <div class="bni-ret-header">
            <strong class="bni-ret-val">95%</strong>
            <span class="bni-badge-change up">↑ 12%</span>
            <span class="bni-vs">{{ __('vs bulan lalu') }}</span>
          </div>
          <div class="bni-ret-legend">
            <span><i class="dot-ukm"></i> UKM</span>
            <span><i class="dot-kor"></i> {{ __('Korporasi') }}</span>
            <span><i class="dot-kon"></i> {{ __('Konsumer') }}</span>
          </div>
          <div class="bni-ret-chart">
            <div v-for="m in retentionMonths" :key="m.label" class="bni-ret-col">
              <div class="bni-ret-bars">
                <span class="r-ukm" :style="{ height: `${m.ukm}%` }"></span>
                <span class="r-kor" :style="{ height: `${m.korporasi}%` }"></span>
                <span class="r-kon" :style="{ height: `${m.konsumer}%` }"></span>
              </div>
              <small :class="{ bold: m.label === 'Sep' }">{{ m.label }}</small>
            </div>
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon, createResource, usePageMeta } from 'frappe-ui'
import { computed, ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

// Static URL imports for Leaflet marker assets (so Vite bundles them correctly)
import leafletIconUrl from 'leaflet/dist/images/marker-icon.png?url'
import leafletIconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png?url'
import leafletShadowUrl from 'leaflet/dist/images/marker-shadow.png?url'

// ─── Reactive State ───────────────────────────────────────
const aiSearch = ref('')
const activeRevenuePeriod = ref('1T')
const hoveredBar = ref(null)
const activeLeadTab = ref('Status')

// ─── Leaflet Map Setup ─────────────────────────────────────
const mapId = `cabang-map-${Math.random().toString(36).slice(2)}`
let L = null
let mapInstance = null
let markersLayer = null

const territoryCoords = {
  'Jakarta': [-6.2088, 106.8456],
  'Surabaya': [-7.2575, 112.7521],
  'Bandung': [-6.9175, 107.6191],
  'Medan': [3.5952, 98.6722],
  'Makassar': [-5.1477, 119.4327],
  'Semarang': [-6.9667, 110.4167],
  'Yogyakarta': [-7.7956, 110.3695],
  'Palembang': [-2.9761, 104.7754],
  'Denpasar': [-8.6705, 115.2126],
  'Balikpapan': [-1.2654, 116.8312],
  'Manado': [1.4748, 124.8428],
  'Jayapura': [-2.5489, 140.7181],
  'Sumatera': [-0.5897, 101.3431],
  'Jawa': [-7.2754, 110.0044],
  'Kalimantan': [-1.2692, 114.3315],
  'Sulawesi': [-1.9022, 120.1219],
  'Papua': [-4.2699, 138.0803],
  'Default': [-2.5, 118.0]
}

function getCoordsForTerritory(name) {
  if (!name) return territoryCoords.Default
  const normalized = name.toLowerCase().trim()
  for (const [key, coords] of Object.entries(territoryCoords)) {
    if (normalized.includes(key.toLowerCase()) || key.toLowerCase().includes(normalized)) {
      return coords
    }
  }
  return [
    -2.5 + (Math.random() - 0.5) * 4,
    118.0 + (Math.random() - 0.5) * 10
  ]
}

async function initMap() {
  if (mapInstance) return

  await import('leaflet/dist/leaflet.css')
  const leafletModule = await import('leaflet')
  L = leafletModule.default ?? leafletModule

  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconUrl: leafletIconUrl,
    iconRetinaUrl: leafletIconRetinaUrl,
    shadowUrl: leafletShadowUrl,
  })

  const container = document.getElementById(mapId)
  if (!container) return

  mapInstance = L.map(mapId, {
    zoomControl: false,
    attributionControl: false
  }).setView([-2.5, 118.0], 4.5)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 18
  }).addTo(mapInstance)

  markersLayer = L.featureGroup().addTo(mapInstance)
  renderMapMarkers()
}

function renderMapMarkers() {
  if (!L || !markersLayer || !mapInstance) return
  markersLayer.clearLayers()

  const regions = data.value.regions || []
  if (regions.length === 0) {
    const fallbackList = [
      { region: 'Jakarta', customers: 240, percent: 24 },
      { region: 'Surabaya', customers: 180, percent: 18 },
      { region: 'Bandung', customers: 120, percent: 12 },
      { region: 'Medan', customers: 100, percent: 10 },
      { region: 'Makassar', customers: 80, percent: 8 }
    ]
    fallbackList.forEach(r => addRegionMarker(r))
  } else {
    regions.forEach(r => addRegionMarker(r))
  }
}

function addRegionMarker(region) {
  const name = region.region || region.name || 'Wilayah'
  const coords = getCoordsForTerritory(name)
  const customersStr = region.customers ? `${region.customers} Customers` : `${region.count || 0} Leads`
  const pctStr = region.percent ? ` (${region.percent}%)` : ''

  const marker = L.circleMarker(coords, {
    radius: 7 + (region.percent ? Math.min(region.percent / 5, 8) : 2),
    fillColor: '#008c95',
    color: '#ffffff',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.85
  })
  
  marker.bindPopup(`
    <div style="font-family: Inter, sans-serif; font-size: 11px; color: #101828; line-height: 1.4;">
      <strong style="color: #008c95; font-size: 12px; display: block; margin-bottom: 2px;">${name}</strong>
      <span>${customersStr}${pctStr}</span>
    </div>
  `)

  markersLayer.addLayer(marker)
}

function mapZoomIn() {
  if (mapInstance) mapInstance.zoomIn()
}

function mapZoomOut() {
  if (mapInstance) mapInstance.zoomOut()
}

function destroyMap() {
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
    markersLayer = null
  }
}

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
const defaultHighlight = 8 // Nov index

const yLabels = [
  { label: '40M', y: chartTop },
  { label: '30M', y: chartTop + chartH * 0.25 },
  { label: '20M', y: chartTop + chartH * 0.5 },
  { label: '10M', y: chartTop + chartH * 0.75 },
  { label: '0M', y: chartBottom },
]

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
const fallbackMetrics = [
  { label: 'Leads', value: 129, icon: 'users', change: 2, caption: 'vs minggu lalu', suffix: '' },
  { label: 'CLV', value: 14, icon: 'clock', change: -4, caption: 'vs minggu lalu', suffix: ' hari' },
  { label: 'Conversion Rate', value: 24, icon: 'trending-up', change: 2, caption: 'vs minggu lalu', suffix: '%' },
  { label: 'Pendapatan', value: 0, icon: 'dollar-sign', change: -4, caption: 'vs bulan lalu', suffix: '', displayOverride: 'Rp1,4 M' },
]

const displayMetrics = computed(() => {
  const api = data.value.metrics
  if (api?.length >= 4) {
    return api.map(m => ({
      ...m,
      icon: m.icon || 'activity',
      displayValue: fmtMetric(m),
      changeNum: Number(m.change || 0),
      isPositive: Number(m.change || 0) >= 0,
    }))
  }
  return fallbackMetrics.map(m => ({
    ...m,
    displayValue: m.displayOverride || `${m.value}${m.suffix}`,
    changeNum: m.change,
    isPositive: m.change >= 0,
  }))
})

function fmtMetric(m) {
  if (m.format === 'currency') return fmtCur(m.value)
  return `${Number(m.value || 0).toLocaleString('id-ID')}${m.suffix || ''}`
}
function fmtCur(v) {
  const a = Number(v || 0)
  if (a >= 1e12) return `Rp${(a/1e12).toFixed(1)}T`
  if (a >= 1e9) return `Rp${(a/1e9).toFixed(1)}B`
  if (a >= 1e6) return `Rp${(a/1e6).toFixed(1)}M`
  return new Intl.NumberFormat('id-ID', { style:'currency', currency:'IDR', maximumFractionDigits:0 }).format(a)
}

// ─── Revenue ──────────────────────────────────────────────
const fallbackRevenueMonths = [
  { label: 'Mar', value: 5200000000 },
  { label: 'Apr', value: 8100000000 },
  { label: 'Mei', value: 6500000000 },
  { label: 'Jun', value: 4800000000 },
  { label: 'Jul', value: 7200000000 },
  { label: 'Agu', value: 9500000000 },
  { label: 'Sep', value: 12800000000 },
  { label: 'Okt', value: 16500000000 },
  { label: 'Nov', value: 18202000000 },
  { label: 'Des', value: 25000000000 },
  { label: 'Jan', value: 30500000000 },
  { label: 'Feb', value: 38000000000 },
]

const displayRevenue = computed(() => ({
  total: data.value.revenue?.total || 32209000000,
  change: data.value.revenue?.change ?? 22,
}))

const revenueMonths = computed(() =>
  data.value.revenue?.months?.length ? data.value.revenue.months : fallbackRevenueMonths
)

const maxRev = computed(() => Math.max(...revenueMonths.value.map(m => m.value), 1))

const chartBars = computed(() =>
  revenueMonths.value.map((m, i) => {
    const pct = m.value / maxRev.value
    const h = Math.max(pct * chartH, 4)
    return { label: m.label, value: m.value, x: chartLeft + 10 + i * barGap, y: chartBottom - h, h }
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

function formatRupiah(v) {
  return 'Rp' + Number(v || 0).toLocaleString('id-ID')
}

// ─── Lead Management ─────────────────────────────────────
const fallbackLeads = {
  Status: [
    { label: 'Kualifikasi', percent: 88 },
    { label: 'Dihubungi', percent: 65 },
    { label: 'Prospek', percent: 48 },
    { label: 'Kalah', percent: 28 },
    { label: 'Menang', percent: 18 },
  ],
  Sumber: [
    { label: 'Website', percent: 72 },
    { label: 'Referral', percent: 55 },
    { label: 'Cold Call', percent: 38 },
    { label: 'Event', percent: 22 },
  ],
  Kualifikasi: [
    { label: 'Hot', percent: 32 },
    { label: 'Warm', percent: 55 },
    { label: 'Cold', percent: 75 },
  ],
}

const displayLeadBars = computed(() => {
  const lm = data.value.lead_management
  if (lm) {
    const map = { Status: lm.status, Sumber: lm.source, Kualifikasi: lm.qualification }
    const rows = map[activeLeadTab.value]
    if (rows?.length) return rows.map(r => ({ label: r.label, percent: r.percent || 0 }))
  }
  return fallbackLeads[activeLeadTab.value] || []
})

// ─── Branches ─────────────────────────────────────────────
const fallbackBranches = [
  { name: 'Jakarta', percent: 24 },
  { name: 'Surabaya', percent: 18 },
  { name: 'Bandung', percent: 12 },
  { name: 'Medan', percent: 10 },
]

const displayBranches = computed(() => {
  if (data.value.top_branches?.length) {
    return data.value.top_branches.map(b => ({ name: b.branch || b.name, percent: b.percent }))
  }
  return fallbackBranches
})

// ─── Retention ────────────────────────────────────────────
const retentionMonths = computed(() => {
  if (data.value.retention?.months?.length) return data.value.retention.months
  return [
    { label: 'Jun', ukm: 22, korporasi: 18, konsumer: 12 },
    { label: 'Jul', ukm: 32, korporasi: 25, konsumer: 18 },
    { label: 'Agu', ukm: 28, korporasi: 22, konsumer: 15 },
    { label: 'Sep', ukm: 42, korporasi: 34, konsumer: 25 },
    { label: 'Okt', ukm: 48, korporasi: 38, konsumer: 28 },
    { label: 'Nov', ukm: 52, korporasi: 42, konsumer: 30 },
    { label: 'Des', ukm: 78, korporasi: 58, konsumer: 42 },
  ]
})

// ─── Last Updated ─────────────────────────────────────────
const lastUpdated = computed(() => {
  if (data.value.last_updated) {
    return new Intl.DateTimeFormat('id-ID', { hour: '2-digit', minute: '2-digit' }).format(new Date(data.value.last_updated))
  }
  return __('now')
})

// ─── Lifecycle ────────────────────────────────────────────
watch(activeRevenuePeriod, () => dashboard.fetch())
usePageMeta(() => ({ title: __('Dashboard') }))

onMounted(() => {
  nextTick(() => {
    initMap()
  })
})

onBeforeUnmount(() => {
  destroyMap()
})

watch(
  () => data.value.regions,
  () => {
    renderMapMarkers()
  },
  { deep: true }
)
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
  height: 104px;
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

/* ═══ MAIN GRID ═════════════════════════════════════════ */
.bni-main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
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
.bni-bottom-grid {
  display: grid;
  grid-template-columns: 1.1fr 1.1fr 0.9fr 1fr;
  gap: 16px;
}

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
  .bni-bottom-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 1024px) {
  .bni-main-grid {
    grid-template-columns: 1fr;
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
  .bni-metric-grid,
  .bni-bottom-grid {
    grid-template-columns: 1fr;
  }
  .bni-action-buttons { flex-wrap: wrap; }
}
</style>
