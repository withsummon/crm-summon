<template>
  <div class="ed" :data-theme="theme" @click="handleGlobalClick">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs routeName="Executive Dashboard" />
      </template>
      <template #right-header>
        <div class="ed-header-right">
          <button class="ed-btn" @click.stop="openCmd">
            ⌘&nbsp;Cari...&nbsp;<kbd class="ed-kbd">⌘K</kbd>
          </button>
          <button class="ed-btn" @click.stop="openWidgetModal">⊞ Customize Widget</button>
          <button class="ed-btn" @click="exportModalOpen = true; exportStatus = null">⬇ Export</button>
          <div class="ed-notif-wrap" ref="notifWrapRef">
            <button class="ed-btn ed-btn-icon" @click.stop="notifOpen = !notifOpen">
              🔔
              <span class="ed-notif-badge">22</span>
            </button>
            <div v-if="notifOpen" class="ed-notif-drop bg-white">
              <div class="ed-notif-hdr ">
                Notifikasi
                <span class="ed-notif-count">22 belum dibaca</span>
              </div>
              <div v-for="(n, i) in NOTIFS" :key="i" class="ed-notif-item">
                <span class="ed-notif-dot"></span>
                <span>{{ n }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </LayoutHeader>

    <!-- ══════════════════ KPI GRID ══════════════════ -->
    <div v-show="widgets.kpi" class="ed-kpi-grid ed-mb">
      <div v-for="k in KPI_DATA" :key="k.label" class="ed-kpi-card">
        <div class="ed-kpi-icon" :style="{ background: k.iconBg }">{{ k.icon }}</div>
        <div class="ed-kpi-label">{{ k.label }}</div>
        <div class="ed-kpi-value">{{ k.value }}</div>
        <div :class="['ed-kpi-trend', k.trendClass]">{{ k.trend }}</div>
      </div>
    </div>

    <!-- ══════════════════ FILTER BAR ══════════════════ -->
    <div v-show="widgets.charts" class="ed-filter-bar ed-mb">
      <span class="ed-filter-label">Periode:</span>
      <button
        v-for="p in PERIODS"
        :key="p.key"
        :class="['ed-filter-btn', { active: activePeriod === p.key }]"
        @click="setPeriod(p.key)"
      >{{ p.key }}</button>
      <span class="ed-filter-info">Aktif: <strong>{{ PERIOD_NAMES[activePeriod] }}</strong></span>
    </div>

    <!-- ══════════════════ CHARTS ROW ══════════════════ -->
    <div v-show="widgets.charts" class="ed-two-col ed-mb">
      <div class="ed-card">
        <div class="ed-card-head">
          <span class="ed-card-title">📊 Disbursement per Segmen</span>
          <span class="ed-card-sub">MTD — Miliar IDR</span>
        </div>
        <div class="ed-chart-area">
          <canvas ref="disbCanvas" height="220"></canvas>
        </div>
      </div>
      <div class="ed-card">
        <div class="ed-card-head">
          <span class="ed-card-title">📈 Trend NPL Ratio</span>
          <span class="ed-card-sub">{{ PERIOD_NAMES[activePeriod] }}</span>
        </div>
        <div class="ed-chart-area">
          <canvas ref="nplCanvas" height="220"></canvas>
        </div>
      </div>
    </div>

    <!-- ══════════════════ FUNNEL + RM ══════════════════ -->
    <div class="ed-two-col ed-mb">
      <div v-show="widgets.funnel" class="ed-card">
        <div class="ed-card-head">
          <span class="ed-card-title">🔽 Pipeline Conversion Funnel</span>
        </div>
        <div class="ed-funnel">
          <div
            v-for="(f, i) in FUNNEL_DATA"
            :key="f.label"
            class="ed-funnel-row"
            @click="showAction(`Stage: ${f.label}`, `Terdapat ${f.count} pengajuan di stage ${f.label}.`, null)"
          >
            <div class="ed-funnel-lbl">{{ f.label }}</div>
            <div class="ed-funnel-track">
              <div
                class="ed-funnel-bar"
                :style="{ width: Math.round(f.count / FUNNEL_DATA[0].count * 100) + '%', background: f.color }"
              >
                <span>{{ f.count }}</span>
              </div>
            </div>
            <div class="ed-funnel-cnt">{{ f.count }}</div>
            <div class="ed-funnel-pct">{{ i > 0 ? Math.round(f.count / FUNNEL_DATA[i-1].count * 100) + '% conv' : '' }}</div>
          </div>
        </div>
      </div>
      <div v-show="widgets.leaderboard" class="ed-card">
        <div class="ed-card-head">
          <span class="ed-card-title">🏆 RM Productivity Leaderboard</span>
          <span class="ed-card-sub">Top 5 bulan ini</span>
        </div>
        <table class="ed-table">
          <thead>
            <tr>
              <th>Nama RM</th><th>Pengajuan</th><th>Approval</th><th>Disbursement</th><th>Score</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(rm, i) in RM_DATA" :key="rm.name" class="ed-tr">
              <td><strong>{{ ['🥇','🥈','🥉','',''][i] }} {{ rm.name }}</strong></td>
              <td>{{ rm.peng }}</td>
              <td :style="{ color: rmScoreColor(rm.score), fontWeight: 700 }">{{ rm.appr }}</td>
              <td>{{ rm.disb }}</td>
              <td>
                <div class="ed-score-row">
                  <div class="ed-score-dots">
                    <span
                      v-for="j in 5" :key="j"
                      class="ed-dot"
                      :style="{ background: j <= Math.round(rm.score/20) ? rmScoreColor(rm.score) : 'var(--ed-border)' }"
                    ></span>
                  </div>
                  <strong :style="{ color: rmScoreColor(rm.score) }">{{ rm.score }}</strong>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══════════════════ RISK + AI ══════════════════ -->
    <div class="ed-two-col ed-mb">
      <div v-show="widgets.risk" class="ed-card">
        <div class="ed-card-head">
          <span class="ed-card-title">⚠️ Risk Alerts</span>
          <span class="ed-badge ed-badge-red">5 Aktif</span>
        </div>
        <div v-for="r in RISK_DATA" :key="r.txt" class="ed-risk-item">
          <span class="ed-risk-ico">{{ r.ico }}</span>
          <div class="ed-risk-body">
            <div class="ed-risk-title">{{ r.txt }}</div>
            <div class="ed-risk-meta">
              Severity: <span :class="['ed-badge', `ed-badge-${r.cls}`]">{{ r.sev }}</span>
            </div>
          </div>
          <button class="ed-btn-tl" @click="showAction('Tindak Lanjut', `Tindak lanjut akan dikirim ke tim terkait: ${r.txt}`, null)">
            Tindak Lanjut
          </button>
        </div>
      </div>
      <div v-show="widgets.ai" class="ed-card">
        <div class="ed-card-head">
          <span class="ed-card-title">🤖 AI Insights</span>
          <button class="ed-btn ed-btn-sm" :disabled="aiRefreshing" @click="refreshAI">
            <span v-if="aiRefreshing" class="ed-spin"></span>
            <span v-else>↻ Refresh</span>
          </button>
        </div>
        <div v-if="aiLoading" class="ed-ai-loading">
          <span class="ed-spin"></span> Menganalisis data terbaru...
        </div>
        <div v-else class="ed-insight-list">
          <div v-for="(ins, i) in INSIGHTS" :key="i" class="ed-insight-item">
            <div class="ed-insight-ico" :style="{ background: INSIGHT_COLORS[i] }">{{ INSIGHT_ICONS[i] }}</div>
            <div class="ed-insight-txt">{{ ins }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════ HEATMAP ══════════════════ -->
    <div v-show="widgets.heatmap" class="ed-card ed-mb" ref="heatmapRef">
      <div class="ed-card-head">
        <span class="ed-card-title">🗺 Portfolio Heatmap — NPL Intensity by Segmen &amp; Produk</span>
        <div class="ed-hm-legend">
          <span class="ed-hm-grad"></span>Rendah → Tinggi NPL
        </div>
      </div>
      <div class="ed-hm-grid" :style="{ gridTemplateColumns: `120px repeat(${HM_PRODS.length}, 1fr)` }">
        <!-- Header row -->
        <div class="ed-hm-hdr"></div>
        <div v-for="p in HM_PRODS" :key="p" class="ed-hm-hdr">{{ p }}</div>
        <!-- Data rows -->
        <template v-for="(seg, r) in HM_SEGS" :key="seg">
          <div class="ed-hm-seg">{{ seg }}</div>
          <div
            v-for="(val, c) in HM_VALS[r]"
            :key="c"
            class="ed-hm-cell"
            :style="{ background: nplColor(val) }"
            @mouseenter="showHmTip($event, seg, HM_PRODS[c], val)"
            @mouseleave="hmTip = null"
          >
            {{ val }}%
          </div>
        </template>
      </div>
      <!-- Heatmap tooltip -->
      <div
        v-if="hmTip"
        class="ed-hm-tip"
        :style="{ left: hmTip.x + 'px', top: hmTip.y + 'px' }"
      >
        <strong>{{ hmTip.seg }} — {{ hmTip.prod }}</strong><br>
        NPL: <strong :style="{ color: hmTip.val >= 3 ? '#ef4444' : hmTip.val >= 2 ? '#f59e0b' : '#10b981' }">{{ hmTip.val }}%</strong><br>
        {{ hmTip.val >= 3 ? '⚠️ Tinggi' : hmTip.val >= 2 ? '⚡ Sedang' : '✅ Rendah' }}
      </div>
    </div>

    <!-- ══════════════════ PENDING + ACTIVITIES ══════════════════ -->
    <div class="ed-two-col ed-mb">
      <div v-show="widgets.pending" class="ed-card">
        <div class="ed-card-head">
          <span class="ed-card-title">⏳ Pending Approvals</span>
          <span class="ed-badge ed-badge-yellow">5 menunggu</span>
        </div>
        <table class="ed-table">
          <thead>
            <tr><th>Debitur</th><th>Produk</th><th>Plafon</th><th>RM</th><th>Tunggu</th><th>Aksi</th></tr>
          </thead>
          <tbody>
            <tr
              v-for="(p, i) in PENDING_DATA"
              :key="p.deb"
              class="ed-tr"
              :style="{ opacity: pendingStatus[i] ? 0.65 : 1 }"
            >
              <td><strong>{{ p.deb }}</strong></td>
              <td><span class="ed-badge ed-badge-blue">{{ p.prod }}</span></td>
              <td>{{ p.plafon }}</td>
              <td>{{ p.rm }}</td>
              <td>
                <span :class="['ed-badge', p.days >= 4 ? 'ed-badge-red' : p.days >= 2 ? 'ed-badge-yellow' : 'ed-badge-green']">
                  {{ p.wait }}
                </span>
              </td>
              <td>
                <span v-if="pendingStatus[i]" :class="pendingStatus[i] === 'approve' ? 'ed-st-approve' : 'ed-st-reject'">
                  {{ pendingStatus[i] === 'approve' ? '✓ Disetujui' : '✗ Ditolak' }}
                </span>
                <div v-else class="ed-act-btns">
                  <button class="ed-btn-approve" @click="pendingAct(i, 'approve')">Approve</button>
                  <button class="ed-btn-reject" @click="pendingAct(i, 'reject')">Reject</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-show="widgets.activities" class="ed-card">
        <div class="ed-card-head">
          <span class="ed-card-title">📌 Recent Activities</span>
        </div>
        <div v-for="a in ACTS" :key="a.txt" class="ed-act-item">
          <!-- <span class="ed-act-ico">{{ a.ico }}</span> -->
          <span class="ed-act-txt">{{ a.txt }}</span>
          <span class="ed-act-time">{{ a.time }}</span>
        </div>
      </div>
    </div>

    <!-- ══════════════════ FLOATING AI ══════════════════ -->
    <div class="ed-ai-float">
      <div v-show="aiChatOpen" class="ed-ai-panel">
        <div class="ed-ai-panel-hdr">
          🤖 SUMMON AI Assistant
          <button @click="aiChatOpen = false" class="ed-ai-close">✕</button>
        </div>
        <div class="ed-ai-body" ref="aiBodyRef">
          <div v-for="(m, i) in aiMessages" :key="i" :class="['ed-ai-msg', m.from === 'bot' ? 'ed-ai-bot' : 'ed-ai-user']">
            {{ m.text }}
          </div>
        </div>
        <div class="ed-ai-inp">
          <input
            v-model="aiInput"
            placeholder="Tanya sesuatu..."
            @keydown.enter="sendAI"
          />
          <button @click="sendAI">Kirim</button>
        </div>
      </div>
      <button class="ed-ai-fab" @click="aiChatOpen = !aiChatOpen">🤖</button>
    </div>

    <!-- ══════════════════ COMMAND PALETTE ══════════════════ -->
    <Teleport to="body">
      <div v-if="cmdOpen" class="ed-cmd-overlay" @click="cmdOpen = false"></div>
      <div v-if="cmdOpen" class="ed-cmd-palette" @click.stop>
        <div class="ed-cmd-inp-row">
          <span class="ed-cmd-search-ico">🔍</span>
          <input
            ref="cmdInputRef"
            v-model="cmdQuery"
            placeholder="Cari halaman, aksi, debitur..."
            @keydown.escape="cmdOpen = false"
          />
          <kbd class="ed-kbd" style="cursor:pointer" @click="cmdOpen = false">ESC</kbd>
        </div>
        <div class="ed-cmd-results">
          <div
            v-for="item in filteredCmdItems"
            :key="item.lbl"
            class="ed-cmd-item"
            @click="runCmd(item)"
          >
            <span class="ed-cmd-ico">{{ item.ico }}</span>
            <span>{{ item.lbl }}</span>
            <span class="ed-cmd-type">{{ item.type }}</span>
          </div>
          <div v-if="filteredCmdItems.length === 0" class="ed-cmd-empty">
            Tidak ada hasil untuk "{{ cmdQuery }}"
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ══════════════════ WIDGET MODAL ══════════════════ -->
    <Teleport to="body">
      <div v-if="widgetModalOpen" class="ed-overlay" @click.self="widgetModalOpen = false">
        <div class="ed-modal">
          <div class="ed-modal-hdr">
            <h3>⊞ Customize Widget</h3>
            <button class="ed-close-x" @click="widgetModalOpen = false">✕</button>
          </div>
          <div class="ed-modal-body">
            <p class="ed-modal-hint">Pilih widget yang ditampilkan di dashboard. Tersimpan otomatis di browser.</p>
            <div v-for="w in WIDGET_LIST" :key="w.id" class="ed-widget-row">
              <input type="checkbox" :id="`wc_${w.id}`" v-model="widgets[w.id]" @change="saveWidgets" />
              <label :for="`wc_${w.id}`">{{ w.label }}</label>
            </div>
          </div>
          <div class="ed-modal-foot">
            <button class="ed-btn" @click="widgetModalOpen = false">Tutup</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ══════════════════ EXPORT MODAL ══════════════════ -->
    <Teleport to="body">
      <div v-if="exportModalOpen" class="ed-overlay" @click.self="exportModalOpen = false">
        <div class="ed-modal">
          <div class="ed-modal-hdr">
            <h3>⬇ Export Dashboard</h3>
            <button class="ed-close-x" @click="exportModalOpen = false">✕</button>
          </div>
          <div class="ed-modal-body">
            <p class="ed-modal-hint">Pilih format ekspor:</p>
            <div
              v-for="fmt in ['PDF','Excel','PNG']"
              :key="fmt"
              class="ed-export-opt"
              :style="{ pointerEvents: exportStatus ? 'none' : 'auto' }"
              @click="doExport(fmt)"
            >
              <!-- <span class="ed-export-ico">{{ { PDF: '📄', Excel: '📊', PNG: '🖼' }[fmt] }}</span> -->
              <div>
                <strong>{{ { PDF: 'PDF Report', Excel: 'Excel Spreadsheet', PNG: 'PNG Screenshot' }[fmt] }}</strong>
                <div class="ed-export-desc">{{ { PDF: 'Executive summary dengan semua chart', Excel: 'Data tabular semua KPI dan tabel', PNG: 'Gambar dashboard saat ini' }[fmt] }}</div>
              </div>
            </div>
            <div v-if="exportStatus" class="ed-export-status">
              <template v-if="exportStatus === 'loading'">
                <span class="ed-spin"></span>
                <span>Mengunduh...</span>
              </template>
              <template v-else>
                <span style="font-size:28px">✅</span>
                <span>Selesai! {{ exportStatus }} berhasil diunduh.</span>
              </template>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ══════════════════ ACTION MODAL ══════════════════ -->
    <Teleport to="body">
      <div v-if="actionModal.open" class="ed-overlay" @click.self="actionModal.open = false">
        <div class="ed-modal ed-modal-sm">
          <div class="ed-modal-hdr">
            <h3>{{ actionModal.title }}</h3>
            <button class="ed-close-x" @click="actionModal.open = false">✕</button>
          </div>
          <div class="ed-modal-body">
            <p class="ed-modal-body-txt">{{ actionModal.body }}</p>
          </div>
          <div class="ed-modal-foot">
            <button class="ed-btn" @click="actionModal.open = false">Batal</button>
            <button class="ed-btn " @click="confirmAction">Konfirmasi</button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { usePageMeta } from 'frappe-ui'
import { Chart, registerables } from 'chart.js'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'

Chart.register(...registerables)

usePageMeta(() => ({ title: 'Dashboard' }))

// ══════════════════════════════════════════════════════
// STATIC DATA
// ══════════════════════════════════════════════════════
const NOTIFS = [
  'Pengajuan kredit PT Maju Bersama menunggu approval',
  'NPL Alert: CV Teknik Jaya DPD 45 hari',
  'SLA breach: Modul Collections — 3 kasus',
  'Disbursement batch Rp 45M telah diproses',
  'RM Ahmad Santoso mencapai target bulan ini',
  'Pengajuan baru: PT Sinar Gemilang — KMK Rp 2.5M',
  'Covenant breach terdeteksi: PT Delta Konstruksi',
  'Jadwal review kredit: 5 debitur jatuh tempo minggu ini',
  'Approval pending >48 jam: 7 pengajuan',
  'Laporan NPL Q2 siap diunduh',
]

const KPI_DATA = [
  { label: 'Pengajuan Kredit Hari Ini', value: '47 pengajuan', trend: '↑ 12% vs bulan lalu', trendClass: 'up', icon: '📋', iconBg: '#dbeafe' },
  { label: 'Portfolio Aktif', value: 'Rp 1,84 T', trend: '↑ 3.2% vs bulan lalu', trendClass: 'up', icon: '💼', iconBg: '#dcfce7' },
  { label: 'NPL Ratio', value: '2,14%', trend: '↓ 0.3% vs bulan lalu (baik)', trendClass: 'down-good', icon: '📉', iconBg: '#dcfce7' },
  { label: 'Disbursement MTD', value: 'Rp 186 M', trend: '↑ 8.7% vs bulan lalu', trendClass: 'up', icon: '💰', iconBg: '#fef3c7' },
  { label: 'Portfolio Outstanding', value: 'Rp 2,1 T', trend: '↑ 1.4% vs bulan lalu', trendClass: 'up', icon: '🏦', iconBg: '#ede9fe' },
  { label: 'Approval Rate', value: '73,5%', trend: '↑ 2.1% vs bulan lalu', trendClass: 'up', icon: '✅', iconBg: '#dcfce7' },
  { label: 'Collection Recovery Rate', value: '67,2%', trend: '↑ 4.5% vs bulan lalu', trendClass: 'up', icon: '🔄', iconBg: '#fce7f3' },
  { label: 'SLA Compliance', value: '89,3%', trend: '↓ 1.1% vs bulan lalu ⚠', trendClass: 'warn', icon: '⏱', iconBg: '#fef3c7' },
]

const RM_DATA = [
  { name: 'Ahmad Santoso', peng: 24, appr: '83%', disb: 'Rp 48M', score: 94 },
  { name: 'Dewi Pratama', peng: 21, appr: '79%', disb: 'Rp 41M', score: 88 },
  { name: 'Rizky Andalan', peng: 18, appr: '75%', disb: 'Rp 35M', score: 82 },
  { name: 'Siti Rahayu', peng: 16, appr: '81%', disb: 'Rp 31M', score: 79 },
  { name: 'Budi Setiawan', peng: 14, appr: '71%', disb: 'Rp 27M', score: 73 },
]

const RISK_DATA = [
  { sev: 'High', cls: 'red', ico: '🔴', txt: 'PT Delta Konstruksi — covenant breach, DPD 67 hari' },
  { sev: 'High', cls: 'red', ico: '🔴', txt: 'CV Teknik Jaya — NPL alert, outstanding Rp 3.2M' },
  { sev: 'Medium', cls: 'yellow', ico: '🟡', txt: 'PT Sinar Nusantara — jatuh tempo dalam 7 hari' },
  { sev: 'Medium', cls: 'yellow', ico: '🟡', txt: '5 debitur KPR — cicilan tertunggak >2 bulan' },
  { sev: 'Low', cls: 'green', ico: '🟢', txt: 'Laporan SLA collections bulan ini di bawah target' },
]

const INSIGHTS = [
  'Portofolio KMK segmen manufacturing menunjukkan tren NPL naik 0.4% — rekomendasi review kredit 12 debitur',
  'RM productivity tertinggi minggu ini: Ahmad Santoso dengan conversion rate 83%',
  'Proyeksi disbursement bulan depan: Rp 210M berdasarkan pipeline saat ini',
]
const INSIGHT_ICONS = ['📊', '⭐', '🔮']
const INSIGHT_COLORS = ['#3b82f6', '#f59e0b', '#8b5cf6']

const FUNNEL_DATA = [
  { label: 'Prospek', count: 320, color: '#3b82f6' },
  { label: 'Pengajuan', count: 180, color: '#8b5cf6' },
  { label: 'Analisis', count: 120, color: '#f59e0b' },
  { label: 'Approval', count: 88, color: '#10b981' },
  { label: 'Disbursement', count: 64, color: '#ef4444' },
]

const HM_SEGS = ['Manufaktur', 'Perdagangan', 'Konstruksi', 'Properti', 'Jasa']
const HM_PRODS = ['KMK', 'KI', 'KPR', 'KUR', 'Multiguna']
const HM_VALS = [
  [2.1, 1.8, 0.9, 1.2, 2.4],
  [1.5, 2.3, 1.1, 0.8, 1.7],
  [3.2, 2.8, 1.4, 0.6, 2.1],
  [1.2, 1.5, 3.8, 1.9, 1.3],
  [0.9, 1.1, 0.7, 0.5, 1.4],
]

const PENDING_DATA = [
  { deb: 'PT Maju Bersama', prod: 'KMK', plafon: 'Rp 5M', rm: 'Ahmad S', wait: '2 hari', days: 2 },
  { deb: 'CV Berkah Jaya', prod: 'KI', plafon: 'Rp 12M', rm: 'Dewi P', wait: '3 hari', days: 3 },
  { deb: 'Sdr. Rudi Hartono', prod: 'KPR', plafon: 'Rp 800jt', rm: 'Rizky A', wait: '1 hari', days: 1 },
  { deb: 'PT Global Tech', prod: 'KMK', plafon: 'Rp 8.5M', rm: 'Siti R', wait: '4 hari', days: 4 },
  { deb: 'UD Makmur', prod: 'KUR', plafon: 'Rp 250jt', rm: 'Budi S', wait: '5 hari', days: 5 },
]

const ACTS = [
  { ico: '📋', txt: 'Pengajuan baru: PT Sinar Gemilang — KMK Rp 2.5M', time: '5 menit lalu' },
  { ico: '✅', txt: 'Approval: CV Berkah Teknik disetujui oleh Kepala Kredit', time: '23 menit lalu' },
  { ico: '📝', txt: 'PTP recorded: Bpk. Hendra Wijaya — Rp 15jt, 3 Jun 2026', time: '1 jam lalu' },
  { ico: '⚠️', txt: 'NPL flag: PT Delta Konstruksi masuk watchlist', time: '2 jam lalu' },
  { ico: '💸', txt: 'Disbursement: PT Maju Nusantara Rp 4.5M telah dicairkan', time: '3 jam lalu' },
  { ico: '🤖', txt: 'Rule triggered: Auto-reject AML — 1 pengajuan ditolak', time: '4 jam lalu' },
  { ico: '⏰', txt: 'SLA breach: Collections modul — 3 kasus', time: '5 jam lalu' },
  { ico: '🏢', txt: 'New vendor: PT Nusantara Appraisal onboarding selesai', time: 'kemarin' },
]

const CMD_DATA = [
  { ico: '📊', lbl: 'Dashboard', type: 'halaman' },
  { ico: '👥', lbl: 'Leads — Daftar Prospek', type: 'halaman' },
  { ico: '💼', lbl: 'Deals — Pipeline Kredit', type: 'halaman' },
  { ico: '📋', lbl: 'Pengajuan Kredit Baru', type: 'aksi' },
  { ico: '⚠️', lbl: 'Risk Management', type: 'halaman' },
  { ico: '🏦', lbl: 'Collections & NPL', type: 'halaman' },
  { ico: '👤', lbl: 'RM Performance Report', type: 'halaman' },
  { ico: '⬇', lbl: 'Export Dashboard PDF', type: 'aksi' },
  { ico: '🔔', lbl: 'Semua Notifikasi', type: 'halaman' },
  { ico: '⚙️', lbl: 'Pengaturan Sistem', type: 'halaman' },
  { ico: '📈', lbl: 'Laporan Disbursement', type: 'halaman' },
]

const WIDGET_LIST = [
  { id: 'kpi', label: 'KPI Cards (8 metrik)' },
  { id: 'charts', label: 'Charts — Disbursement & NPL Trend' },
  { id: 'funnel', label: 'Pipeline Conversion Funnel' },
  { id: 'leaderboard', label: 'RM Productivity Leaderboard' },
  { id: 'risk', label: 'Risk Alerts Panel' },
  { id: 'ai', label: 'AI Insights Panel' },
  { id: 'heatmap', label: 'Portfolio Heatmap' },
  { id: 'pending', label: 'Pending Approvals' },
  { id: 'activities', label: 'Recent Activities Feed' },
]

const PERIODS = [
  { key: '1H' }, { key: '1M' }, { key: '3M' }, { key: '6M' }, { key: '1T' }, { key: 'SEMUA' },
]
const PERIOD_NAMES = { '1H': '1 Jam', '1M': '1 Bulan', '3M': '3 Bulan', '6M': '6 Bulan', '1T': '1 Tahun', 'SEMUA': 'Semua Waktu' }
const PERIOD_LABELS = {
  '1H': ['09:00','10:00','11:00','12:00','13:00','14:00'],
  '1M': ['Mg1','Mg2','Mg3','Mg4'],
  '3M': ['Jan','Feb','Mar'],
  '6M': ['Des','Jan','Feb','Mar','Apr','Mei'],
  '1T': ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'],
  'SEMUA': ['2021','2022','2023','2024','2025','2026'],
}

const AI_REPLIES = [
  'Berdasarkan data terkini, NPL ratio segmen konstruksi meningkat 0.6% dibanding bulan lalu. Disarankan review 8 debitur prioritas.',
  'Pipeline disbursement bulan ini masih di bawah target 15%. Ahmad Santoso memiliki 3 pengajuan yang siap diproses.',
  'Tingkat approval rate tertinggi ada di produk KMK dengan 76.3%. KPR memerlukan perhatian dengan approval rate 61.2%.',
  'Terdapat 7 pengajuan pending lebih dari 48 jam. Ini berpotensi melanggar SLA commitment kepada nasabah.',
  'Rekomendasi: Fokus collection pada 5 debitur teratas dengan outstanding Rp 18.5M untuk meningkatkan recovery rate.',
]

// ══════════════════════════════════════════════════════
// REACTIVE STATE
// ══════════════════════════════════════════════════════
// Dark mode is temporarily disabled/hidden — force light theme
const theme = ref('light')
const lastUpdated = ref('just now')
const notifOpen = ref(false)
const notifWrapRef = ref(null)

const activePeriod = ref('1M')

const widgets = reactive(
  Object.fromEntries(
    WIDGET_LIST.map(w => [w.id, JSON.parse(localStorage.getItem('ed_widgets') || '{}')[w.id] !== false])
  )
)

const widgetModalOpen = ref(false)
const exportModalOpen = ref(false)
const exportStatus = ref(null)

const actionModal = reactive({ open: false, title: '', body: '', cb: null })
const pendingStatus = reactive({})

const aiLoading = ref(false)
const aiRefreshing = ref(false)

const hmTip = ref(null)
const heatmapRef = ref(null)

const aiChatOpen = ref(false)
const aiInput = ref('')
const aiMessages = ref([
  { from: 'bot', text: 'Halo! Saya SUMMON AI. Ada yang bisa saya bantu mengenai portofolio atau analisis kredit hari ini?' }
])
const aiBodyRef = ref(null)

const cmdOpen = ref(false)
const cmdQuery = ref('')
const cmdInputRef = ref(null)

// Chart refs
const disbCanvas = ref(null)
const nplCanvas = ref(null)
let disbChart = null
let nplChart = null

// ══════════════════════════════════════════════════════
// COMPUTED
// ══════════════════════════════════════════════════════
const filteredCmdItems = computed(() => {
  const q = cmdQuery.value.toLowerCase()
  return q ? CMD_DATA.filter(c => c.lbl.toLowerCase().includes(q)) : CMD_DATA
})

function chartTextColor() {
  return theme.value === 'dark' ? '#94a3b8' : '#718096'
}
function chartGridColor() {
  return theme.value === 'dark' ? '#334155' : '#e2e8f0'
}

// ══════════════════════════════════════════════════════
// THEME
// ══════════════════════════════════════════════════════
function toggleTheme() {
  // Dark mode is temporarily disabled/hidden
}

// ══════════════════════════════════════════════════════
// CHARTS
// ══════════════════════════════════════════════════════
function buildChartOptions() {
  const tc = chartTextColor()
  const gc = chartGridColor()
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: tc, font: { size: 10 } } },
      tooltip: { backgroundColor: '#1e293b', titleColor: '#f1f5f9', bodyColor: '#cbd5e1' },
    },
    scales: {
      x: { grid: { color: gc }, ticks: { color: tc, font: { size: 10 } } },
      y: { grid: { color: gc }, ticks: { color: tc, font: { size: 10 } } },
    },
  }
}

function initCharts() {
  if (!disbCanvas.value || !nplCanvas.value) return

  if (disbChart) disbChart.destroy()
  if (nplChart) nplChart.destroy()

  disbChart = new Chart(disbCanvas.value, {
    type: 'bar',
    data: {
      labels: ['KMK', 'KI', 'KPR', 'Multiguna', 'KUR'],
      datasets: [{
        label: 'Miliar IDR',
        data: [58, 42, 35, 28, 23],
        backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'],
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      ...buildChartOptions(),
      plugins: {
        ...buildChartOptions().plugins,
        legend: { display: false },
        tooltip: {
          ...buildChartOptions().plugins.tooltip,
          callbacks: { label: ctx => `Rp ${ctx.parsed.y} Miliar` },
        },
      },
      onClick: (e, els) => {
        if (!els.length) return
        const i = els[0].index
        const labs = ['KMK', 'KI', 'KPR', 'Multiguna', 'KUR']
        const vals = [58, 42, 35, 28, 23]
        showAction(`Detail Disbursement — ${labs[i]}`, `Total disbursement ${labs[i]} bulan ini: Rp ${vals[i]} Miliar. Debitur aktif: ${vals[i] * 2} nasabah.`, null)
      },
    },
  })

  const labels = PERIOD_LABELS[activePeriod.value]
  const n = labels.length
  nplChart = new Chart(nplCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'NPL Ratio (%)',
          data: [2.8, 2.6, 2.5, 2.3, 2.2, 2.14].slice(-n),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59,130,246,.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 5,
          pointBackgroundColor: '#3b82f6',
        },
        {
          label: 'Threshold (3%)',
          data: Array(n).fill(3),
          borderColor: '#ef4444',
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: buildChartOptions(),
  })
}

function refreshChartColors() {
  if (!disbChart || !nplChart) return
  const tc = chartTextColor()
  const gc = chartGridColor()
  for (const chart of [disbChart, nplChart]) {
    chart.options.scales.x.grid.color = gc
    chart.options.scales.x.ticks.color = tc
    chart.options.scales.y.grid.color = gc
    chart.options.scales.y.ticks.color = tc
    if (chart.options.plugins.legend.labels) chart.options.plugins.legend.labels.color = tc
    chart.update()
  }
}

function setPeriod(key) {
  activePeriod.value = key
  if (!nplChart) return
  const labels = PERIOD_LABELS[key]
  const n = labels.length
  nplChart.data.labels = labels
  nplChart.data.datasets[0].data = Array.from({ length: n }, (_, i) =>
    +(3.2 - i * (1.0 / n) + Math.random() * 0.12).toFixed(2)
  )
  nplChart.data.datasets[1].data = Array(n).fill(3)
  nplChart.update()
}

// ══════════════════════════════════════════════════════
// HEATMAP
// ══════════════════════════════════════════════════════
function nplColor(v) {
  if (v < 1.5) return `hsl(${120 - v * 8},65%,42%)`
  if (v < 2.5) return `hsl(${50 - (v - 1.5) * 30},70%,42%)`
  return `hsl(${Math.max(0, 20 - (v - 2.5) * 15)},75%,42%)`
}

function showHmTip(e, seg, prod, val) {
  const container = heatmapRef.value?.getBoundingClientRect()
  if (!container) return
  hmTip.value = {
    seg, prod, val,
    x: e.clientX - container.left + 12,
    y: e.clientY - container.top - 10,
  }
}

// ══════════════════════════════════════════════════════
// RISK / RM HELPERS
// ══════════════════════════════════════════════════════
function rmScoreColor(score) {
  return score >= 90 ? '#059669' : score >= 80 ? '#3b82f6' : '#f59e0b'
}

// ══════════════════════════════════════════════════════
// AI INSIGHTS
// ══════════════════════════════════════════════════════
function refreshAI() {
  aiRefreshing.value = true
  aiLoading.value = true
  setTimeout(() => {
    aiLoading.value = false
    aiRefreshing.value = false
  }, 1500)
}

// ══════════════════════════════════════════════════════
// PENDING APPROVALS
// ══════════════════════════════════════════════════════
function pendingAct(i, action) {
  const p = PENDING_DATA[i]
  showAction(
    action === 'approve' ? '✅ Konfirmasi Approve' : '❌ Konfirmasi Reject',
    `${action === 'approve' ? 'Setujui' : 'Tolak'} pengajuan ${p.deb} — ${p.prod} ${p.plafon}?`,
    () => { pendingStatus[i] = action }
  )
}

// ══════════════════════════════════════════════════════
// MODALS
// ══════════════════════════════════════════════════════
function showAction(title, body, cb) {
  actionModal.title = title
  actionModal.body = body
  actionModal.cb = cb
  actionModal.open = true
}

function confirmAction() {
  actionModal.cb?.()
  actionModal.open = false
}

function openWidgetModal() {
  widgetModalOpen.value = true
}

function saveWidgets() {
  const s = {}
  WIDGET_LIST.forEach(w => { s[w.id] = widgets[w.id] })
  localStorage.setItem('ed_widgets', JSON.stringify(s))
}

function doExport(fmt) {
  exportStatus.value = 'loading'
  setTimeout(() => { exportStatus.value = fmt }, 2000)
}

// ══════════════════════════════════════════════════════
// COMMAND PALETTE
// ══════════════════════════════════════════════════════
function openCmd() {
  cmdOpen.value = true
  cmdQuery.value = ''
  nextTick(() => cmdInputRef.value?.focus())
}

function runCmd(item) {
  cmdOpen.value = false
  if (item.lbl === 'Export Dashboard PDF') {
    exportModalOpen.value = true
    exportStatus.value = null
  }
}

// ══════════════════════════════════════════════════════
// AI CHAT
// ══════════════════════════════════════════════════════
function sendAI() {
  const msg = aiInput.value.trim()
  if (!msg) return
  aiMessages.value.push({ from: 'user', text: msg })
  aiInput.value = ''
  aiMessages.value.push({ from: 'bot', text: '...' })
  nextTick(() => { if (aiBodyRef.value) aiBodyRef.value.scrollTop = aiBodyRef.value.scrollHeight })
  setTimeout(() => {
    aiMessages.value[aiMessages.value.length - 1].text = AI_REPLIES[Math.floor(Math.random() * AI_REPLIES.length)]
    nextTick(() => { if (aiBodyRef.value) aiBodyRef.value.scrollTop = aiBodyRef.value.scrollHeight })
  }, 1200)
}

// ══════════════════════════════════════════════════════
// GLOBAL CLICK / KEYBOARD
// ══════════════════════════════════════════════════════
function handleGlobalClick() {
  notifOpen.value = false
}

function handleKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    openCmd()
  }
  if (e.key === 'Escape') {
    cmdOpen.value = false
    notifOpen.value = false
  }
}

// ══════════════════════════════════════════════════════
// LIFECYCLE
// ══════════════════════════════════════════════════════
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  nextTick(initCharts)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  disbChart?.destroy()
  nplChart?.destroy()
})
</script>

<style scoped>
/* ── VARIABLES ──────────────────────────────────────── */
.ed {
  --ed-bg: #f0f4f8;
  --ed-surface: #fff;
  --ed-surface2: #f8fafc;
  --ed-border: #e2e8f0;
  --ed-text: #1a202c;
  --ed-text2: #4a5568;
  --ed-text3: #718096;
  --ed-primary: #003F8C;
  --ed-primary-light: #e8f0fc;
  --ed-shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.05);
  --ed-shadow-lg: 0 10px 25px -3px rgba(0,0,0,.1);
  --ed-r: 8px;
  --ed-r-lg: 12px;

  background: var(--ed-bg);
  color: var(--ed-text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 14px;
  line-height: 1.5;
  min-height: 100%;
  overflow-y: auto;
  padding: 20px 24px 40px;
}
.ed[data-theme="dark"] {
  --ed-bg: #0f172a;
  --ed-surface: #1e293b;
  --ed-surface2: #1a2535;
  --ed-border: #334155;
  --ed-text: #f1f5f9;
  --ed-text2: #cbd5e1;
  --ed-text3: #94a3b8;
  --ed-primary: #3b82f6;
  --ed-primary-light: #1e3a5f;
  --ed-shadow: 0 1px 3px rgba(0,0,0,.3);
  --ed-shadow-lg: 0 10px 25px -3px rgba(0,0,0,.5);
}

/* ── LAYOUT ─────────────────────────────────────────── */
.ed-mb { margin-bottom: 18px; }
.ed-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 18px; }
@media (max-width: 1100px) { .ed-two-col { grid-template-columns: 1fr; } }

/* ── HEADER ─────────────────────────────────────────── */
.ed-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.ed-header-left {
  flex: 1;
  min-width: 200px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.ed-bni-logo {
  width: 32px;
  height: 32px;
  border-radius: 7px;
  background: linear-gradient(135deg, #003F8C, #E87722);
  color: #fff;
  font-weight: 900;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ed-title { font-size: 20px; font-weight: 700; margin: 0; }
.ed-subtitle { font-size: 11px; color: var(--ed-text3); margin: 2px 0 0; }
.ed-header-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

/* ── BUTTONS ────────────────────────────────────────── */
.ed-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: var(--ed-r);
  border: 1px solid var(--ed-border);
  background: var(--ed-surface);
  color: var(--ed-text);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all .15s;
  white-space: nowrap;
  font-family: inherit;
}
.ed-btn:hover { background: var(--ed-primary-light); border-color: var(--ed-primary); color: var(--ed-primary); }
.ed-btn:disabled { opacity: .5; cursor: not-allowed; }
.ed-btn-primary { background: var(--ed-primary); color: #fff; border-color: var(--ed-primary); }
.ed-btn-primary:hover { background: #002d6b; color: #fff; border-color: #002d6b; }
.ed-btn-sm { padding: 4px 9px; font-size: 11px; }
.ed-btn-icon { padding: 6px 8px; position: relative; }
.ed-kbd {
  font-size: 10px;
  color: var(--ed-text3, #718096);
  background: var(--ed-surface2, #f8fafc);
  border: 1px solid var(--ed-border, #e2e8f0);
  padding: 1px 4px;
  border-radius: 3px;
}

/* ── NOTIFICATIONS ──────────────────────────────────── */
.ed-notif-wrap { position: relative; }
.ed-notif-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #e53e3e;
  color: #fff;
  font-size: 9px;
  font-weight: 700;
  border-radius: 10px;
  padding: 1px 5px;
  pointer-events: none;
}
.ed-notif-drop {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 340px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: var(--ed-r-lg);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12), 0 2px 6px rgba(15, 23, 42, 0.08);
  z-index: 100;
  max-height: 380px;
  overflow-y: auto;
}
.ed[data-theme="dark"] .ed-notif-drop {
  background: #1f2a3b;
  border-color: #475569;
}
.ed-notif-hdr {
  padding: 11px 14px;
  border-bottom: 1px solid var(--ed-border);
  font-weight: 600;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: var(--ed-surface2);
}
.ed-notif-count { font-size: 10px; font-weight: 400; color: var(--ed-text3); }
.ed-notif-item {
  padding: 9px 14px;
  border-bottom: 1px solid var(--ed-border);
  font-size: 11px;
  cursor: pointer;
  display: flex;
  gap: 9px;
  align-items: flex-start;
  transition: background .1s;
}
.ed-notif-item:hover { background: var(--ed-surface2); }
.ed-notif-item:last-child { border-bottom: none; }
.ed-notif-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--ed-primary);
  flex-shrink: 0;
  margin-top: 3px;
}

/* ── CARDS ──────────────────────────────────────────── */
.ed-card {
  background: var(--ed-surface);
  border: 1px solid var(--ed-border);
  border-radius: var(--ed-r-lg);
  padding: 18px;
  box-shadow: var(--ed-shadow);
  position: relative;
}
.ed-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.ed-card-title { font-size: 13px; font-weight: 600; }
.ed-card-sub { font-size: 10px; color: var(--ed-text3); }

/* ── KPI GRID ───────────────────────────────────────── */
.ed-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
@media (max-width: 1200px) { .ed-kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .ed-kpi-grid { grid-template-columns: 1fr 1fr; } }
.ed-kpi-card {
  background: var(--ed-surface);
  border: 1px solid var(--ed-border);
  border-radius: var(--ed-r-lg);
  padding: 16px;
  box-shadow: var(--ed-shadow);
  cursor: pointer;
  transition: transform .15s, box-shadow .15s;
}
.ed-kpi-card:hover { transform: translateY(-2px); box-shadow: var(--ed-shadow-lg); }
.ed-kpi-icon {
  width: 36px;
  height: 36px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-bottom: 10px;
}
.ed-kpi-label { font-size: 10px; color: var(--ed-text3); font-weight: 500; margin-bottom: 5px; }
.ed-kpi-value { font-size: 19px; font-weight: 700; line-height: 1.2; margin-bottom: 4px; }
.ed-kpi-trend { font-size: 11px; }
.ed-kpi-trend.up { color: #38a169; }
.ed-kpi-trend.down-good { color: #38a169; }
.ed-kpi-trend.warn { color: #d69e2e; }
.ed-kpi-trend.down-bad { color: #e53e3e; }

/* ── FILTER BAR ─────────────────────────────────────── */
.ed-filter-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--ed-surface);
  border: 1px solid var(--ed-border);
  border-radius: var(--ed-r);
  padding: 7px 12px;
  box-shadow: var(--ed-shadow);
  flex-wrap: wrap;
}
.ed-filter-label { font-size: 11px; color: var(--ed-text3); font-weight: 500; margin-right: 2px; }
.ed-filter-btn {
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ed-text2);
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: all .15s;
  font-family: inherit;
}
.ed-filter-btn:hover { background: var(--ed-primary-light); color: var(--ed-primary); }
.ed-filter-btn.active { background: var(--ed-primary); color: #fff; }
.ed-filter-info { margin-left: auto; font-size: 10px; color: var(--ed-text3); }

/* ── CHART AREA ─────────────────────────────────────── */
.ed-chart-area { position: relative; height: 240px; }
.ed-chart-area canvas { width: 100% !important; height: 100% !important; }

/* ── TABLE ──────────────────────────────────────────── */
.ed-table { width: 100%; border-collapse: collapse; }
.ed-table th {
  text-align: left;
  font-size: 10px;
  font-weight: 700;
  color: var(--ed-text3);
  text-transform: uppercase;
  letter-spacing: .4px;
  padding: 7px 10px;
  border-bottom: 1px solid var(--ed-border);
}
.ed-table td {
  padding: 9px 10px;
  font-size: 12px;
  border-bottom: 1px solid var(--ed-border);
  vertical-align: middle;
}
.ed-tr:last-child td { border-bottom: none; }
.ed-tr:hover td { background: var(--ed-surface2); }

/* ── BADGES ─────────────────────────────────────────── */
.ed-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
}
.ed-badge-red { background: #fee2e2; color: #dc2626; }
.ed-badge-yellow { background: #fef3c7; color: #d97706; }
.ed-badge-green { background: #d1fae5; color: #059669; }
.ed-badge-blue { background: #dbeafe; color: #2563eb; }
.ed[data-theme="dark"] .ed-badge-red { background: #450a0a; color: #f87171; }
.ed[data-theme="dark"] .ed-badge-yellow { background: #451a03; color: #fbbf24; }
.ed[data-theme="dark"] .ed-badge-green { background: #052e16; color: #4ade80; }
.ed[data-theme="dark"] .ed-badge-blue { background: #0c1a3d; color: #60a5fa; }

/* ── SCORE DOTS ─────────────────────────────────────── */
.ed-score-row { display: flex; align-items: center; gap: 6px; }
.ed-score-dots { display: flex; gap: 2px; }
.ed-dot { width: 8px; height: 8px; border-radius: 2px; }

/* ── FUNNEL ─────────────────────────────────────────── */
.ed-funnel { display: flex; flex-direction: column; gap: 6px; }
.ed-funnel-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background .15s;
}
.ed-funnel-row:hover { background: var(--ed-surface2); }
.ed-funnel-lbl { width: 88px; font-size: 11px; color: var(--ed-text2); font-weight: 500; flex-shrink: 0; }
.ed-funnel-track { flex: 1; }
.ed-funnel-bar {
  height: 30px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  transition: width .4s;
  min-width: 40px;
}
.ed-funnel-cnt { width: 36px; font-size: 12px; font-weight: 700; text-align: right; flex-shrink: 0; }
.ed-funnel-pct { width: 60px; font-size: 10px; color: var(--ed-text3); text-align: right; flex-shrink: 0; }

/* ── RISK ALERTS ────────────────────────────────────── */
.ed-risk-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--ed-border);
}
.ed-risk-item:last-child { border-bottom: none; }
.ed-risk-ico { font-size: 16px; flex-shrink: 0; margin-top: 1px; }
.ed-risk-body { flex: 1; }
.ed-risk-title { font-size: 12px; font-weight: 500; margin-bottom: 2px; }
.ed-risk-meta { font-size: 10px; color: var(--ed-text3); }
.ed-btn-tl {
  background: none;
  border: 1px solid var(--ed-border);
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 10px;
  cursor: pointer;
  color: var(--ed-text2);
  transition: all .15s;
  font-family: inherit;
  flex-shrink: 0;
}
.ed-btn-tl:hover { border-color: var(--ed-primary); color: var(--ed-primary); }

/* ── AI INSIGHTS ────────────────────────────────────── */
.ed-ai-loading { display: flex; align-items: center; gap: 10px; padding: 16px 0; font-size: 12px; color: var(--ed-text3); }
.ed-insight-list { display: flex; flex-direction: column; gap: 8px; }
.ed-insight-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: var(--ed-surface2);
  border-radius: var(--ed-r);
  border: 1px solid var(--ed-border);
}
.ed-insight-ico {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 13px;
  flex-shrink: 0;
}
.ed-insight-txt { font-size: 11px; color: var(--ed-text2); line-height: 1.6; }

/* ── HEATMAP ────────────────────────────────────────── */
.ed-hm-legend {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 10px;
  color: var(--ed-text3);
}
.ed-hm-grad {
  display: inline-block;
  width: 70px;
  height: 7px;
  border-radius: 4px;
  background: linear-gradient(to right, #22c55e, #eab308, #ef4444);
}
.ed-hm-grid { display: grid; gap: 4px; }
.ed-hm-hdr {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: var(--ed-text3);
  padding: 4px 2px;
  text-align: center;
}
.ed-hm-seg {
  display: flex;
  align-items: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--ed-text2);
  padding: 0 6px;
}
.ed-hm-cell {
  border-radius: 4px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  transition: transform .15s;
  text-shadow: 0 1px 2px rgba(0,0,0,.3);
}
.ed-hm-cell:hover { transform: scale(1.06); z-index: 1; position: relative; }
.ed-hm-tip {
  position: absolute;
  background: var(--ed-surface);
  border: 1px solid var(--ed-border);
  border-radius: 8px;
  padding: 9px 13px;
  box-shadow: var(--ed-shadow-lg);
  font-size: 11px;
  line-height: 1.6;
  pointer-events: none;
  z-index: 50;
}

/* ── ACTIVITIES ─────────────────────────────────────── */
.ed-act-item {
  display: flex;
  gap: 9px;
  padding: 8px 0;
  border-bottom: 1px solid var(--ed-border);
}
.ed-act-item:last-child { border-bottom: none; }
.ed-act-ico { font-size: 14px; flex-shrink: 0; margin-top: 1px; }
.ed-act-txt { flex: 1; font-size: 11px; color: var(--ed-text2); line-height: 1.5; }
.ed-act-time { font-size: 10px; color: var(--ed-text3); white-space: nowrap; flex-shrink: 0; }

/* ── PENDING APPROVALS ──────────────────────────────── */
.ed-act-btns { display: flex; gap: 5px; }
.ed-btn-approve {
  background: #d1fae5;
  color: #059669;
  border: 1px solid #a7f3d0;
  padding: 3px 9px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 10px;
  font-weight: 700;
  transition: all .15s;
  font-family: inherit;
}
.ed-btn-approve:hover { background: #059669; color: #fff; }
.ed-btn-reject {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
  padding: 3px 9px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 10px;
  font-weight: 700;
  transition: all .15s;
  font-family: inherit;
}
.ed-btn-reject:hover { background: #dc2626; color: #fff; }
.ed[data-theme="dark"] .ed-btn-approve { background: #052e16; color: #4ade80; border-color: #065f46; }
.ed[data-theme="dark"] .ed-btn-reject { background: #450a0a; color: #f87171; border-color: #7f1d1d; }
.ed-st-approve { background: #d1fae5; color: #059669; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; }
.ed-st-reject { background: #fee2e2; color: #dc2626; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; }
.ed[data-theme="dark"] .ed-st-approve { background: #052e16; color: #4ade80; }
.ed[data-theme="dark"] .ed-st-reject { background: #450a0a; color: #f87171; }

/* ── FLOATING AI ────────────────────────────────────── */
.ed-ai-float { position: fixed; bottom: 24px; right: 24px; z-index: 200; }
.ed-ai-fab {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(102,126,234,.5);
  transition: transform .2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ed-ai-fab:hover { transform: scale(1.1); }
.ed-ai-panel {
  position: absolute;
  bottom: 62px;
  right: 0;
  width: 300px;
  background: var(--ed-surface);
  border: 1px solid var(--ed-border);
  border-radius: var(--ed-r-lg);
  box-shadow: var(--ed-shadow-lg);
  display: flex;
  flex-direction: column;
  max-height: 360px;
}
.ed-ai-panel-hdr {
  padding: 11px 14px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-radius: var(--ed-r-lg) var(--ed-r-lg) 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
}
.ed-ai-close { background: none; border: none; color: #fff; cursor: pointer; font-size: 15px; line-height: 1; }
.ed-ai-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.ed-ai-msg { padding: 7px 10px; border-radius: 8px; font-size: 11px; max-width: 88%; line-height: 1.5; }
.ed-ai-bot { background: var(--ed-primary-light); color: var(--ed-text); align-self: flex-start; }
.ed-ai-user { background: var(--ed-primary); color: #fff; align-self: flex-end; }
.ed-ai-inp {
  display: flex;
  gap: 6px;
  padding: 8px;
  border-top: 1px solid var(--ed-border);
}
.ed-ai-inp input {
  flex: 1;
  border: 1px solid var(--ed-border);
  border-radius: 6px;
  padding: 5px 8px;
  font-size: 11px;
  background: var(--ed-bg);
  color: var(--ed-text);
  outline: none;
  font-family: inherit;
}
.ed-ai-inp button {
  padding: 5px 10px;
  background: var(--ed-primary);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 11px;
  font-family: inherit;
}

/* ── COMMAND PALETTE ────────────────────────────────── */
.ed-cmd-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 399; backdrop-filter: blur(2px); }
.ed-cmd-palette {
  position: fixed;
  top: 70px;
  left: 50%;
  transform: translateX(-50%);
  width: 520px;
  max-width: 95vw;
  background: var(--ed-surface, #fff);
  border: 1px solid var(--ed-border, #e2e8f0);
  border-radius: var(--ed-r-lg, 12px);
  box-shadow: var(--ed-shadow-lg, 0 10px 25px -3px rgba(0,0,0,.1));
  z-index: 400;
}
.ed-cmd-inp-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--ed-border, #e2e8f0);
}
.ed-cmd-search-ico { color: var(--ed-text3, #718096); font-size: 15px; }
.ed-cmd-inp-row input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--ed-text, #1a202c);
  outline: none;
  font-family: inherit;
}
.ed-cmd-results { max-height: 280px; overflow-y: auto; }
.ed-cmd-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  cursor: pointer;
  font-size: 12px;
  transition: background .1s;
}
.ed-cmd-item:hover { background: var(--ed-primary-light, #e8f0fc); color: var(--ed-primary, #003F8C); }
.ed-cmd-ico { font-size: 14px; width: 20px; text-align: center; flex-shrink: 0; }
.ed-cmd-type {
  margin-left: auto;
  font-size: 9px;
  color: var(--ed-text3, #718096);
  background: var(--ed-surface2, #f8fafc);
  border: 1px solid var(--ed-border, #e2e8f0);
  padding: 1px 5px;
  border-radius: 3px;
}
.ed-cmd-empty { padding: 20px; text-align: center; color: var(--ed-text3); font-size: 12px; }

/* ── MODALS ─────────────────────────────────────────── */
.ed-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.45);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
}
.ed-modal {
  background: var(--ed-surface, #fff);
  border: 1px solid var(--ed-border, #e2e8f0);
  border-radius: var(--ed-r-lg, 12px);
  box-shadow: var(--ed-shadow-lg, 0 10px 25px -3px rgba(0,0,0,.1));
  width: 480px;
  max-width: 95vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.ed-modal-sm { width: 400px; }
.ed-modal-hdr {
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--ed-border, #e2e8f0);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ed-modal-hdr h3 { font-size: 14px; font-weight: 700; margin: 0; }
.ed-close-x {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--ed-text3, #718096);
  padding: 3px;
  border-radius: 4px;
  line-height: 1;
}
.ed-close-x:hover { background: var(--ed-surface2, #f8fafc); color: var(--ed-text, #1a202c); }
.ed-modal-body {
  padding: 16px 20px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}
.ed-modal-foot {
  position: sticky;
  bottom: 0;
  padding: 12px 20px;
  border-top: 1px solid var(--ed-border, #e2e8f0);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  background: var(--ed-surface, #fff);
}
.ed-modal-hint { font-size: 11px; color: var(--ed-text3, #718096); margin-bottom: 14px; }
.ed-modal-body-txt { font-size: 12px; color: var(--ed-text2, #4a5568); line-height: 1.6; }

/* Widget modal */
.ed-widget-row { display: flex; align-items: center; gap: 10px; padding: 9px 0; border-bottom: 1px solid var(--ed-border, #e2e8f0); }
.ed-widget-row:last-child { border-bottom: none; }
.ed-widget-row input { width: 15px; height: 15px; cursor: pointer; accent-color: var(--ed-primary); }
.ed-widget-row label { cursor: pointer; font-size: 12px; }

/* Export modal */
.ed-export-opt {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--ed-border, #e2e8f0);
  border-radius: var(--ed-r, 8px);
  cursor: pointer;
  margin-bottom: 8px;
  transition: all .15s;
}
.ed-export-opt:hover { border-color: var(--ed-primary, #003F8C); background: var(--ed-primary-light, #e8f0fc); }
.ed-export-opt:last-of-type { margin-bottom: 0; }
.ed-export-ico { font-size: 24px; }
.ed-export-desc { font-size: 10px; color: var(--ed-text3, #718096); }
.ed-export-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  margin-top: 10px;
  font-size: 12px;
  color: var(--ed-text2, #4a5568);
  border-top: 1px solid var(--ed-border, #e2e8f0);
}

/* ── SPINNER ────────────────────────────────────────── */
@keyframes ed-spin { to { transform: rotate(360deg); } }
.ed-spin {
  width: 14px;
  height: 14px;
  border: 2px solid var(--ed-border, #e2e8f0);
  border-top-color: var(--ed-primary, #003F8C);
  border-radius: 50%;
  animation: ed-spin .6s linear infinite;
  display: inline-block;
  flex-shrink: 0;
}
</style>
