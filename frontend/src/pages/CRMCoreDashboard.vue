<template>
  <div class="bni-dashboard" :data-theme="dashTheme" @click="handleDashClick">
    <div class="bni-content">
      <LayoutHeader>
        <template #left-header>
          <ViewBreadcrumbs routeName="CRM Core Dashboard" />
        </template>
        <template #right-header>
          <div class="bni-topbar-right">
            <div class="bni-search-box" @click.stop="cmdOpen = true">
              <FeatherIcon name="search" class="h-4 w-4 shrink-0 opacity-50" />
              <input v-model="aiSearch" :placeholder="__('Cari... ⌘K')" readonly />
              <kbd class="bni-kbd">⌘K</kbd>
            </div>

            <div class="bni-notif-wrap" style="position:relative">
              <button class="bni-icon-btn" :aria-label="__('Notifications')" @click.stop="notifOpen = !notifOpen">
                <FeatherIcon name="bell" class="h-4 w-4" />
                <span class="bni-bell-dot"></span>
              </button>
              <div v-if="notifOpen" class="bni-notif-drop" @click.stop>
                <div class="bni-notif-hd">
                  <strong>Notifikasi</strong>
                  <span class="bni-notif-pill">3 baru</span>
                </div>
                <div class="bni-notif-scroll">
                  <div v-for="n in bniNotifications" :key="n.id" :class="['bni-ni', { 'bni-ni--unread': n.unread }]">
                    <div class="bni-ni-dot" v-if="n.unread"></div>
                    <div class="bni-ni-body">
                      <strong>{{ n.title }}</strong>
                      <p>{{ n.body }}</p>
                      <small>{{ n.time }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
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
        </template>
      </LayoutHeader>

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
                  <text
                    v-for="(bar, i) in chartBars"
                    :key="'x'+i"
                    :x="bar.x + bw / 2"
                    :y="chartBottom + 12"
                    text-anchor="end"
                    :transform="`rotate(-30, ${bar.x + bw / 2}, ${chartBottom + 12})`"
                    class="x-label animate-fade-in"
                    :class="{ hl: i === defaultHighlight }"
                  >
                    {{ truncateLabel(bar.label, 12) }}
                  </text>
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

        <!-- Follow-up Load -->
        <article class="bni-card">
          <div class="bni-card-head">
            <h2>{{ __('Follow-up Load') }}</h2>
            <button class="bni-dots"><FeatherIcon name="more-vertical" class="h-4 w-4" /></button>
          </div>
          <div class="bni-lead-bars">
            <div v-for="item in displayFollowUpLoad" :key="item.label" class="bni-lb-row">
              <span class="bni-lb-label">{{ item.label }}</span>
              <div class="bni-lb-track">
                <div class="bni-lb-fill" :style="{ width: `${item.percent}%` }"></div>
              </div>
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
      </section>

      <!-- ═══ EXEC DIVIDER ═══ -->
      <div class="bni-exec-divider">
        <span>Dashboard</span>
      </div>

      <!-- ═══ EXEC KPI ROW ═══ -->
      <section v-if="widgets.kpi" class="bni-exec-kpi-grid">
        <article v-for="k in execKPIs" :key="k.label" class="bni-exec-kpi-card">
          <div class="bni-ekc-top">
            <div class="bni-ekc-icon"><FeatherIcon :name="k.icon" class="h-4 w-4" /></div>
            <span :class="['bni-ekc-change', k.up ? 'up' : 'down']">{{ k.change }}</span>
          </div>
          <strong class="bni-ekc-val">{{ k.value }}</strong>
          <span class="bni-ekc-label">{{ k.label }}</span>
          <span class="bni-ekc-cap">{{ k.caption }}</span>
        </article>
      </section>

      <!-- ═══ FILTER BAR ═══ -->
      <div class="bni-exec-filter">
        <span class="bni-exec-filter-label">Periode:</span>
        <button
          v-for="p in revenuePeriods" :key="p"
          :class="['bni-fp-btn', { active: activePeriod === p }]"
          @click="activePeriod = p"
        >{{ p }}</button>
      </div>

      <!-- ═══ CHARTS ROW ═══ -->
      <section v-if="widgets.charts" class="bni-exec-two-col">
        <article class="bni-card">
          <div class="bni-card-head">
            <h2>Disbursement per Segmen</h2>
            <button class="bni-dots"><FeatherIcon name="more-vertical" class="h-4 w-4" /></button>
          </div>
          <div style="height:220px;position:relative">
            <canvas ref="disbCanvas"></canvas>
          </div>
        </article>
        <article class="bni-card">
          <div class="bni-card-head">
            <h2>Trend NPL Ratio</h2>
            <button class="bni-dots"><FeatherIcon name="more-vertical" class="h-4 w-4" /></button>
          </div>
          <div style="height:220px;position:relative">
            <canvas ref="nplCanvas"></canvas>
          </div>
        </article>
      </section>

      <!-- ═══ FUNNEL + RM LEADERBOARD ═══ -->
      <section class="bni-exec-two-col">
        <article v-if="widgets.funnel" class="bni-card">
          <div class="bni-card-head"><h2>Pipeline Konversi</h2></div>
          <div class="bni-funnel">
            <div v-for="(step, i) in funnelSteps" :key="step.label" class="bni-funnel-row">
              <div class="bni-funnel-bar" :style="{ width: `${(step.value/funnelSteps[0].value)*100}%`, background: step.color }">
                <span class="bni-funnel-label">{{ step.label }}</span>
                <span class="bni-funnel-val">{{ step.value }}</span>
              </div>
              <div v-if="i < funnelSteps.length-1" class="bni-funnel-conv">
                ↓ {{ Math.round(funnelSteps[i+1].value/step.value*100) }}%
              </div>
            </div>
          </div>
        </article>
        <article v-if="widgets.leaderboard" class="bni-card">
          <div class="bni-card-head"><h2>RM Productivity Leaderboard</h2></div>
          <table class="bni-rm-table">
            <thead>
              <tr><th>#</th><th>Nama</th><th>Cabang</th><th>Deal</th><th>Nilai</th><th>Rate</th></tr>
            </thead>
            <tbody>
              <tr v-for="rm in rmLeaderboard" :key="rm.rank">
                <td><span :class="['bni-rm-rank', rm.rank===1?'gold':rm.rank===2?'silver':rm.rank===3?'bronze':'']">{{ rm.rank }}</span></td>
                <td class="bni-rm-name">{{ rm.name }}</td>
                <td class="bni-rm-branch">{{ rm.branch }}</td>
                <td class="bni-rm-deals">{{ rm.deals }}</td>
                <td class="bni-rm-val">{{ rm.value }}</td>
                <td><span class="bni-rm-rate">{{ rm.rate }}</span></td>
              </tr>
            </tbody>
          </table>
        </article>
      </section>

      <!-- ═══ RISK ALERTS + AI INSIGHTS ═══ -->
      <section class="bni-exec-two-col">
        <article v-if="widgets.risk" class="bni-card">
          <div class="bni-card-head"><h2>Risk Alerts</h2><span class="bni-risk-count">{{ riskAlerts.length }}</span></div>
          <div class="bni-risk-list">
            <div v-for="r in riskAlerts" :key="r.id" class="bni-risk-item">
              <span :class="['bni-risk-badge', 'bni-risk-'+r.color]">{{ r.severity }}</span>
              <div class="bni-risk-body">
                <strong>{{ r.title }}</strong>
                <p>{{ r.body }}</p>
              </div>
              <button class="bni-risk-action" @click="showAction(r.title,'Tindak lanjut untuk: '+r.body, ()=>{})">Tindak Lanjut</button>
            </div>
          </div>
        </article>
        <article v-if="widgets.ai" class="bni-card">
          <div class="bni-card-head">
            <h2>AI Insights</h2>
            <button class="bni-action-btn" style="height:28px;font-size:11px" @click="refreshAI" :disabled="aiRefreshing">
              <FeatherIcon name="refresh-cw" :class="['h-3 w-3', aiRefreshing?'bni-spin':'']" />
              {{ aiRefreshing ? 'Memuat...' : 'Refresh' }}
            </button>
          </div>
          <div class="bni-ai-list">
            <div v-for="(ins, i) in aiInsights" :key="i" class="bni-ai-item">
              <span class="bni-ai-icon">{{ ins.icon }}</span>
              <div>
                <strong>{{ ins.title }}</strong>
                <p>{{ ins.body }}</p>
              </div>
            </div>
          </div>
        </article>
      </section>

      <!-- ═══ PORTFOLIO HEATMAP ═══ -->
      <section v-if="widgets.heatmap" class="bni-card bni-exec-heatmap-card">
        <div class="bni-card-head"><h2>Portfolio Heatmap (NPL % per Segmen × Produk)</h2></div>
        <div class="bni-hm-wrap">
          <table class="bni-hm-table">
            <thead>
              <tr>
                <th></th>
                <th v-for="col in heatmapData.cols" :key="col">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in heatmapData.values" :key="ri">
                <td class="bni-hm-rowlabel">{{ heatmapData.rows[ri] }}</td>
                <td
                  v-for="(val, ci) in row" :key="ci"
                  :style="{ background: nplColor(val) }"
                  class="bni-hm-cell"
                  @mouseenter="e => showHmTip(heatmapData.rows[ri], heatmapData.cols[ci], val, e)"
                  @mouseleave="hmTip = null"
                >{{ val.toFixed(1) }}%</td>
              </tr>
            </tbody>
          </table>
          <div class="bni-hm-legend">
            <span>Rendah</span>
            <div class="bni-hm-grad"></div>
            <span>Tinggi</span>
          </div>
        </div>
      </section>

      <!-- ═══ PENDING APPROVALS + ACTIVITIES ═══ -->
      <section class="bni-exec-two-col">
        <article v-if="widgets.pending" class="bni-card bni-exec-pending">
          <div class="bni-card-head"><h2>Pending Approvals</h2><span class="bni-risk-count">{{ pendingApprovals.filter(p=>!p.status).length }}</span></div>
          <table class="bni-pa-table">
            <thead><tr><th>Debitur</th><th>Segmen</th><th>Nominal</th><th>RM</th><th>Hari</th><th>Aksi</th></tr></thead>
            <tbody>
              <tr v-for="p in pendingApprovals" :key="p.id" :class="{ 'bni-pa-done': p.status }">
                <td>{{ p.debitur }}</td>
                <td><span class="bni-seg-badge">{{ p.segmen }}</span></td>
                <td class="bni-pa-nom">{{ p.nominal }}</td>
                <td>{{ p.rm }}</td>
                <td><span :class="['bni-pa-days', p.hari >= 5 ? 'warn' : '']">{{ p.hari }}h</span></td>
                <td v-if="!p.status" class="bni-pa-acts">
                  <button class="bni-btn-approve" @click="pendingAct(p, 'approve')">✓</button>
                  <button class="bni-btn-reject" @click="pendingAct(p, 'reject')">✕</button>
                </td>
                <td v-else>
                  <span :class="['bni-pa-status', p.status]">{{ p.status === 'approve' ? 'Disetujui' : 'Ditolak' }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </article>
        <article v-if="widgets.activities" class="bni-card">
          <div class="bni-card-head"><h2>Aktivitas Terkini</h2></div>
          <div class="bni-act-feed">
            <div v-for="(act, i) in recentActivities" :key="i" class="bni-act-item">
              <span class="bni-act-icon">{{ act.icon }}</span>
              <div class="bni-act-body">
                <p>{{ act.text }}</p>
                <small>{{ act.time }}</small>
              </div>
            </div>
          </div>
        </article>
      </section>
    </div>

    <!-- ═══ FLOATING AI CHAT ═══ -->
    <div class="bni-ai-fab" @click.stop="aiChatOpen = !aiChatOpen">
      <FeatherIcon name="message-circle" class="h-5 w-5" />
    </div>
    <div v-if="aiChatOpen" class="bni-ai-chat" @click.stop>
      <div class="bni-ai-chat-hd">
        <strong>Summon AI</strong>
        <button @click="aiChatOpen = false"><FeatherIcon name="x" class="h-4 w-4" /></button>
      </div>
      <div class="bni-ai-chat-body" ref="aiBodyRef">
        <div v-for="(msg, i) in aiMessages" :key="i" :class="['bni-ai-msg', msg.from]">{{ msg.text }}</div>
      </div>
      <div class="bni-ai-chat-foot">
        <input v-model="aiInput" placeholder="Tanya sesuatu..." @keydown.enter="sendAI" />
        <button @click="sendAI"><FeatherIcon name="send" class="h-4 w-4" /></button>
      </div>
    </div>

    <!-- Heatmap tooltip -->
    <div v-if="hmTip" class="bni-hm-tip" :style="{ top: (hmTip.y+14)+'px', left: hmTip.x+'px' }">
      <strong>{{ hmTip.seg }} × {{ hmTip.prod }}</strong>
      <div>NPL: {{ hmTip.val.toFixed(1) }}%</div>
    </div>

    <!-- ═══ WIDGET MODAL ═══ -->
    <Teleport to="body">
      <div v-if="widgetModalOpen" class="bni-overlay" @click.self="widgetModalOpen = false">
        <div class="bni-modal">
          <div class="bni-modal-hd">
            <strong>Customize Widget</strong>
            <button @click="widgetModalOpen = false"><FeatherIcon name="x" class="h-4 w-4" /></button>
          </div>
          <div class="bni-modal-body">
            <p style="font-size:13px;color:var(--text-2);margin-bottom:14px">Pilih widget yang ingin ditampilkan di Dashboard.</p>
            <div class="bni-widget-list">
              <label v-for="w in widgetList" :key="w.key" class="bni-widget-row">
                <input type="checkbox" v-model="widgets[w.key]" />
                <span>{{ w.label }}</span>
              </label>
            </div>
          </div>
          <div class="bni-modal-ft">
            <button class="bni-btn-cancel" @click="widgetModalOpen = false">Batal</button>
            <button class="bni-btn-save" @click="saveWidgets">Simpan</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══ EXPORT MODAL ═══ -->
    <Teleport to="body">
      <div v-if="exportModalOpen" class="bni-overlay" @click.self="exportModalOpen = false">
        <div class="bni-modal">
          <div class="bni-modal-hd">
            <strong>Export Dashboard</strong>
            <button @click="exportModalOpen = false"><FeatherIcon name="x" class="h-4 w-4" /></button>
          </div>
          <div class="bni-modal-body">
            <p style="font-size:13px;color:var(--text-2);margin-bottom:14px">Pilih format export:</p>
            <div style="display:flex;gap:10px;margin-bottom:18px">
              <button
                v-for="fmt in ['PDF','Excel','PNG']" :key="fmt"
                :class="['bni-fmt-btn', { active: selectedExportFmt === fmt }]"
                @click="selectedExportFmt = fmt"
              >{{ fmt }}</button>
            </div>
            <div v-if="exportStatus" class="bni-export-status">{{ exportStatus }}</div>
          </div>
          <div class="bni-modal-ft">
            <button class="bni-btn-cancel" @click="exportModalOpen = false">Batal</button>
            <button class="bni-btn-save" @click="doExport(selectedExportFmt)">
              <FeatherIcon name="download" class="h-3.5 w-3.5" /> Download {{ selectedExportFmt }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══ ACTION CONFIRM MODAL ═══ -->
    <Teleport to="body">
      <div v-if="actionModal.open" class="bni-overlay" @click.self="actionModal.open = false">
        <div class="bni-modal bni-modal--sm">
          <div class="bni-modal-hd">
            <strong>{{ actionModal.title }}</strong>
            <button @click="actionModal.open = false"><FeatherIcon name="x" class="h-4 w-4" /></button>
          </div>
          <div class="bni-modal-body">
            <p style="font-size:13px;color:var(--text-2)">{{ actionModal.body }}</p>
          </div>
          <div class="bni-modal-ft">
            <button class="bni-btn-cancel" @click="actionModal.open = false">Batal</button>
            <button class="bni-btn-save" @click="confirmAction">Konfirmasi</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══ COMMAND PALETTE ═══ -->
    <Teleport to="body">
      <div v-if="cmdOpen" class="bni-overlay bni-cmd-overlay" @click.self="cmdOpen = false">
        <div class="bni-cmd">
          <div class="bni-cmd-search">
            <FeatherIcon name="search" class="h-4 w-4 opacity-50" />
            <input ref="cmdInputRef" v-model="cmdQuery" placeholder="Cari perintah..." @keydown.escape="cmdOpen = false" />
            <kbd class="bni-kbd">ESC</kbd>
          </div>
          <div class="bni-cmd-list">
            <button v-for="cmd in filteredCmds" :key="cmd.label" class="bni-cmd-item" @click="cmd.action">
              <FeatherIcon :name="cmd.icon" class="h-4 w-4 opacity-60" />
              <span>{{ cmd.label }}</span>
            </button>
            <div v-if="!filteredCmds.length" class="bni-cmd-empty">Tidak ada hasil</div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { FeatherIcon, createResource, usePageMeta } from 'frappe-ui'
import { computed, reactive, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
Chart.register(...registerables)

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
const svgH = 300
const chartLeft = 42
const chartBottom = 200
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
const hasDashboardData = computed(() => !!dashboard.data && Object.keys(dashboard.data).length > 0)

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

const revenueMonths = computed(() => {
  const months = data.value.revenue?.months
  if (Array.isArray(months)) return months
  return fallbackRevenueMonths
})

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
    return Array.isArray(rows) ? rows.map(r => ({ label: r.label, percent: r.percent || 0 })) : []
  }
  return []
})

// ─── Supporting Lists ─────────────────────────────────────
const displayCompanies = computed(() => {
  const rows = data.value.lead_gen?.company_breakdown
  if (Array.isArray(rows)) return rows
  return fallbackBranches.map(item => ({ label: item.name, count: item.percent, percent: item.percent }))
})

const displayPicOwnership = computed(() => {
  const rows = data.value.lead_gen?.pic_ownership
  if (Array.isArray(rows)) return rows
  return [
      { label: 'Unassigned', count: 12, percent: 40 },
      { label: 'RM Jakarta', count: 9, percent: 30 },
      { label: 'RM Bandung', count: 6, percent: 20 },
    ]
})

const displayFollowUpLoad = computed(() => {
  const rows = data.value.lead_gen?.follow_up_load?.status_rows
  if (Array.isArray(rows)) return rows
  return [
    { label: 'Todo', count: 14, percent: 58 },
    { label: 'In Progress', count: 7, percent: 29 },
    { label: 'Done', count: 3, percent: 13 },
  ]
})

const followUpSummary = computed(() => ({
  pending: data.value.lead_gen?.follow_up_load?.pending ?? (hasDashboardData.value ? 0 : 21),
  completed: data.value.lead_gen?.follow_up_load?.completed ?? (hasDashboardData.value ? 0 : 3),
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

// ─── Executive Dashboard State ────────────────────────────
// Dark mode is temporarily disabled/hidden — force light theme
const dashTheme = ref('light')
const notifOpen = ref(false)
const widgetModalOpen = ref(false)
const exportModalOpen = ref(false)
const exportStatus = ref(null)
const selectedExportFmt = ref('PDF')
const actionModal = reactive({ open: false, title: '', body: '', cb: null })
const activePeriod = ref('1M')
const aiRefreshing = ref(false)
const hmTip = ref(null)
const aiChatOpen = ref(false)
const aiInput = ref('')
const aiMessages = ref([{ from: 'bot', text: 'Halo! Saya Summon AI. Ada yang bisa saya bantu mengenai dashboard kredit BNI?' }])
const aiBodyRef = ref(null)
const cmdOpen = ref(false)
const cmdQuery = ref('')
const cmdInputRef = ref(null)
const disbCanvas = ref(null)
const nplCanvas = ref(null)
let disbChart = null, nplChart = null

const widgets = reactive(
  JSON.parse(localStorage.getItem('bni_widgets') || 'null') || {
    kpi: true, charts: true, funnel: true, leaderboard: true,
    risk: true, ai: true, heatmap: true, pending: true, activities: true,
  }
)
const widgetList = [
  { key: 'kpi', label: '8 KPI Utama' },
  { key: 'charts', label: 'Grafik Disbursement & NPL' },
  { key: 'funnel', label: 'Pipeline Konversi' },
  { key: 'leaderboard', label: 'RM Leaderboard' },
  { key: 'risk', label: 'Risk Alerts' },
  { key: 'ai', label: 'AI Insights' },
  { key: 'heatmap', label: 'Portfolio Heatmap' },
  { key: 'pending', label: 'Pending Approvals' },
  { key: 'activities', label: 'Aktivitas Terkini' },
]

// ─── Exec KPI Data ────────────────────────────────────────
const execKPIs = [
  { label: 'Pengajuan', value: '1.247', change: '+12%', up: true, icon: 'file-text', caption: 'Total pengajuan kredit' },
  { label: 'Portfolio Aktif', value: 'Rp 8,4T', change: '+5%', up: true, icon: 'briefcase', caption: 'Outstanding kredit aktif' },
  { label: 'NPL Ratio', value: '2,8%', change: '-0.3%', up: false, icon: 'alert-triangle', caption: 'Non-Performing Loan' },
  { label: 'Disbursement MTD', value: 'Rp 1,2T', change: '+18%', up: true, icon: 'trending-up', caption: 'Month-to-date disbursement' },
  { label: 'Portfolio Outstanding', value: 'Rp 12,6T', change: '+3%', up: true, icon: 'database', caption: 'Total portfolio outstanding' },
  { label: 'Approval Rate', value: '76%', change: '+4%', up: true, icon: 'check-circle', caption: 'Tingkat persetujuan kredit' },
  { label: 'Collection Recovery', value: '88%', change: '+2%', up: true, icon: 'refresh-cw', caption: 'Recovery rate koleksi' },
  { label: 'SLA Compliance', value: '94%', change: '-1%', up: false, icon: 'clock', caption: 'Kepatuhan SLA proses' },
]

// ─── Funnel + Leaderboard ─────────────────────────────────
const funnelSteps = [
  { label: 'Prospek', value: 320, color: '#0e9298' },
  { label: 'Pengajuan', value: 180, color: '#15b8bd' },
  { label: 'Analisis', value: 120, color: '#3acfd4' },
  { label: 'Approval', value: 88, color: '#5ddde1' },
  { label: 'Disbursement', value: 64, color: '#85e8eb' },
]
const rmLeaderboard = [
  { rank: 1, name: 'Budi Santoso', branch: 'Jakarta Pusat', deals: 28, value: 'Rp 145M', rate: '89%' },
  { rank: 2, name: 'Siti Rahayu', branch: 'Surabaya', deals: 24, value: 'Rp 132M', rate: '85%' },
  { rank: 3, name: 'Ahmad Fauzi', branch: 'Bandung', deals: 21, value: 'Rp 118M', rate: '82%' },
  { rank: 4, name: 'Dewi Kusuma', branch: 'Medan', deals: 19, value: 'Rp 95M', rate: '79%' },
  { rank: 5, name: 'Rizky Pratama', branch: 'Semarang', deals: 17, value: 'Rp 88M', rate: '76%' },
]

// ─── Risk Alerts ──────────────────────────────────────────
const riskAlerts = [
  { id: 1, severity: 'KRITIS', title: 'NPL Segmen Mikro Meningkat', body: 'NPL mikro naik 0.8% dalam 7 hari terakhir. Perlu tindakan segera.', color: 'red' },
  { id: 2, severity: 'TINGGI', title: 'Limit Konsentrasi Sektor Properti', body: 'Eksposur properti mencapai 28% dari total portfolio (batas 25%).', color: 'orange' },
  { id: 3, severity: 'SEDANG', title: 'Dokumen Jaminan Kadaluarsa', body: '34 debitur memiliki dokumen jaminan kadaluarsa < 30 hari.', color: 'yellow' },
  { id: 4, severity: 'RENDAH', title: 'SLA Review Terlampaui', body: '12 pengajuan melebihi SLA review 5 hari kerja.', color: 'blue' },
  { id: 5, severity: 'INFO', title: 'Jadwal Audit Internal', body: 'Audit internal dijadwalkan 15 Juni 2026. Persiapkan dokumen.', color: 'gray' },
]

// ─── AI Insights ──────────────────────────────────────────
const aiInsights = ref([
  { icon: '🎯', title: 'Peluang Cross-Sell', body: '127 nasabah segmen UKM berpotensi untuk produk KI berdasarkan pola transaksi.' },
  { icon: '⚠️', title: 'Risiko Churn', body: '23 debitur premium tidak ada aktivitas >60 hari. Disarankan outreach segera.' },
  { icon: '📈', title: 'Tren Positif', body: 'Approval rate minggu ini 82%, naik 6% dari rata-rata bulan lalu.' },
])

// ─── Heatmap ──────────────────────────────────────────────
const heatmapData = {
  rows: ['Mikro', 'UKM', 'Korporasi', 'Konsumer', 'Syariah'],
  cols: ['KTA', 'KPR', 'KI', 'KUR', 'KMK'],
  values: [
    [2.1, 1.4, 3.8, 4.2, 1.9],
    [1.8, 2.6, 1.2, 3.1, 2.4],
    [0.9, 1.1, 2.8, 0.7, 1.6],
    [3.4, 1.7, 0.8, 2.2, 3.9],
    [1.3, 2.9, 1.5, 1.8, 2.1],
  ],
}

// ─── Pending Approvals ────────────────────────────────────
const pendingApprovals = ref([
  { id: 1, debitur: 'PT Maju Bersama', segmen: 'Korporasi', nominal: 'Rp 12,5M', rm: 'Budi S.', hari: 3, status: null },
  { id: 2, debitur: 'CV Tekno Jaya', segmen: 'UKM', nominal: 'Rp 3,2M', rm: 'Siti R.', hari: 5, status: null },
  { id: 3, debitur: 'Yanto Surya', segmen: 'Mikro', nominal: 'Rp 850jt', rm: 'Ahmad F.', hari: 2, status: null },
  { id: 4, debitur: 'PT Karya Abadi', segmen: 'Korporasi', nominal: 'Rp 8,7M', rm: 'Dewi K.', hari: 7, status: null },
  { id: 5, debitur: 'UD Sumber Rezeki', segmen: 'UKM', nominal: 'Rp 1,5M', rm: 'Rizky P.', hari: 1, status: null },
])

// ─── Activities ───────────────────────────────────────────
const recentActivities = [
  { icon: '✅', time: '10 mnt lalu', text: 'Approval kredit PT Maju Bersama Rp 12,5M disetujui oleh Kepala Cabang Jakarta' },
  { icon: '📄', time: '25 mnt lalu', text: 'Pengajuan baru dari CV Tekno Jaya Rp 3,2M masuk oleh RM Siti Rahayu' },
  { icon: '⚠️', time: '1 jam lalu', text: 'Alert NPL: Debitur Ahmad Yusuf (KUR Mikro) masuk watchlist koleksi' },
  { icon: '📊', time: '2 jam lalu', text: 'Disbursement batch Mei 2026 selesai — total Rp 487M ke 34 debitur' },
  { icon: '🔔', time: '3 jam lalu', text: 'Jadwal review portfolio Q2 ditetapkan 28 Mei 2026 pukul 09:00' },
  { icon: '📞', time: '4 jam lalu', text: 'Follow-up call Yanto Surya berhasil — jadwal tatap muka Jumat' },
  { icon: '🏦', time: 'Kemarin', text: 'Pelunasan early dari PT Karya Abadi — penghematan bunga Rp 120jt' },
  { icon: '📋', time: 'Kemarin', text: 'Audit internal dokumen jaminan selesai — 34 item membutuhkan pembaruan' },
]

// ─── Notifications ────────────────────────────────────────
const bniNotifications = [
  { id: 1, title: 'Approval Kredit Menunggu', body: 'PT Maju Bersama - Rp 12,5M menunggu persetujuan Anda', time: '5 mnt lalu', unread: true },
  { id: 2, title: 'Alert NPL Kritis', body: 'Segmen Mikro NPL naik 0.8% dalam 7 hari', time: '12 mnt lalu', unread: true },
  { id: 3, title: 'Disbursement Selesai', body: 'Batch Mei 2026 berhasil — Rp 487M ke 34 debitur', time: '1 jam lalu', unread: true },
  { id: 4, title: 'Laporan SLA Tersedia', body: 'Laporan kepatuhan SLA April 2026 sudah dapat diunduh', time: '2 jam lalu', unread: false },
  { id: 5, title: 'Review Portfolio Q2', body: 'Jadwal review ditetapkan 28 Mei 2026 pukul 09:00', time: '3 jam lalu', unread: false },
  { id: 6, title: 'Limit Konsentrasi', body: 'Sektor properti mendekati batas 25% portfolio', time: '4 jam lalu', unread: false },
  { id: 7, title: 'Dokumen Kadaluarsa', body: '34 dokumen jaminan perlu diperbaharui segera', time: 'Kemarin', unread: false },
  { id: 8, title: 'Target Bulanan Tercapai', body: 'Target disbursement Mei 2026 tercapai 108%', time: 'Kemarin', unread: false },
  { id: 9, title: 'RM Baru Bergabung', body: 'Andi Wijaya mulai bertugas di Cabang Yogyakarta', time: '2 hari lalu', unread: false },
  { id: 10, title: 'Update Regulasi OJK', body: 'Surat edaran OJK No. 15/2026 perlu ditindaklanjuti', time: '3 hari lalu', unread: false },
]

// ─── Command Palette ──────────────────────────────────────
const cmdCommands = [
  { label: 'Dashboard Utama', icon: 'grid', action: () => { cmdOpen.value = false } },
  { label: 'Lihat Pending Approvals', icon: 'check-square', action: () => { cmdOpen.value = false; nextTick(() => document.querySelector('.bni-exec-pending')?.scrollIntoView({ behavior: 'smooth' })) } },
  { label: 'Export Dashboard', icon: 'download', action: () => { cmdOpen.value = false; exportModalOpen.value = true } },
  { label: 'Customize Widget', icon: 'sliders', action: () => { cmdOpen.value = false; widgetModalOpen.value = true } },

  { label: 'Refresh Data', icon: 'refresh-cw', action: () => { cmdOpen.value = false; dashboard.fetch() } },
]
const filteredCmds = computed(() =>
  cmdQuery.value
    ? cmdCommands.filter(c => c.label.toLowerCase().includes(cmdQuery.value.toLowerCase()))
    : cmdCommands
)

// ─── Executive Functions ──────────────────────────────────
function toggleTheme() {
  // Dark mode is temporarily disabled/hidden
}

function handleDashClick() {
  notifOpen.value = false
}

function nplColor(v) {
  if (v >= 4) return '#fecdca'
  if (v >= 3) return '#fedf89'
  if (v >= 2) return '#a9ecd6'
  return '#d1fadf'
}

function showHmTip(seg, prod, val, event) {
  hmTip.value = { seg, prod, val, x: event.clientX, y: event.clientY }
}

function showAction(title, body, cb) {
  actionModal.title = title
  actionModal.body = body
  actionModal.cb = cb
  actionModal.open = true
}

function confirmAction() {
  if (actionModal.cb) actionModal.cb()
  actionModal.open = false
}

function pendingAct(item, action) {
  showAction(
    action === 'approve' ? 'Konfirmasi Approval' : 'Konfirmasi Penolakan',
    `${action === 'approve' ? 'Setujui' : 'Tolak'} pengajuan ${item.debitur} senilai ${item.nominal}?`,
    () => { item.status = action }
  )
}

function saveWidgets() {
  localStorage.setItem('bni_widgets', JSON.stringify({ ...widgets }))
  widgetModalOpen.value = false
}

function doExport(fmt) {
  exportStatus.value = `Mengunduh ${fmt}...`
  setTimeout(() => {
    exportStatus.value = `${fmt} berhasil diunduh!`
    setTimeout(() => {
      exportStatus.value = null
      exportModalOpen.value = false
    }, 1500)
  }, 1200)
}

function refreshAI() {
  aiRefreshing.value = true
  setTimeout(() => {
    aiInsights.value = [
      { icon: '🎯', title: 'Peluang Baru', body: `${Math.floor(Math.random() * 50 + 100)} nasabah teridentifikasi untuk produk baru.` },
      { icon: '📉', title: 'Analisis Risiko', body: `Model prediksi: ${Math.floor(Math.random() * 10 + 15)} debitur berisiko tinggi perlu monitoring.` },
      { icon: '💡', title: 'Rekomendasi', body: 'Segmen Korporasi menunjukkan peluang KMK jangka pendek berdasarkan arus kas.' },
    ]
    aiRefreshing.value = false
  }, 1200)
}

function sendAI() {
  const msg = aiInput.value.trim()
  if (!msg) return
  aiMessages.value.push({ from: 'user', text: msg })
  aiInput.value = ''
  nextTick(() => { if (aiBodyRef.value) aiBodyRef.value.scrollTop = aiBodyRef.value.scrollHeight })
  setTimeout(() => {
    const lower = msg.toLowerCase()
    const reply = lower.includes('npl')
      ? 'NPL ratio saat ini 2,8% dengan tren menurun positif. Target akhir tahun 2,5%.'
      : lower.includes('disbursement')
      ? 'Disbursement MTD mencapai Rp 1,2T, 18% di atas target bulan ini.'
      : lower.includes('approval')
      ? 'Approval rate minggu ini 82%, naik 6% dari rata-rata bulan lalu.'
      : 'Saya sedang menganalisis data terkini. Coba tanya tentang NPL, disbursement, atau approval rate.'
    aiMessages.value.push({ from: 'bot', text: reply })
    nextTick(() => { if (aiBodyRef.value) aiBodyRef.value.scrollTop = aiBodyRef.value.scrollHeight })
  }, 800)
}

function handleKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    cmdOpen.value = true
    nextTick(() => cmdInputRef.value?.focus())
  }
  if (e.key === 'Escape') {
    cmdOpen.value = false
    notifOpen.value = false
    widgetModalOpen.value = false
    exportModalOpen.value = false
    actionModal.open = false
    aiChatOpen.value = false
  }
}

function initCharts() {
  const isDark = dashTheme.value === 'dark'
  const textColor = isDark ? '#8fa3b8' : '#667085'
  const gridColor = isDark ? '#2a3547' : '#edf2f4'

  if (disbCanvas.value) {
    disbChart?.destroy()
    disbChart = new Chart(disbCanvas.value, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
        datasets: [{ label: 'Disbursement (Rp M)', data: [420, 380, 510, 490, 620, 587], backgroundColor: '#0e9298', borderRadius: 6 }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor } },
        },
      },
    })
  }

  if (nplCanvas.value) {
    nplChart?.destroy()
    nplChart = new Chart(nplCanvas.value, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
        datasets: [{
          label: 'NPL Ratio (%)',
          data: [3.4, 3.2, 3.1, 2.9, 2.8, 2.8],
          borderColor: '#f04438',
          backgroundColor: 'rgba(240,68,56,0.08)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#f04438',
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor }, min: 2, max: 4 },
        },
      },
    })
  }
}

onMounted(() => {
  nextTick(() => initCharts())
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  disbChart?.destroy()
  nplChart?.destroy()
  document.removeEventListener('keydown', handleKeydown)
})
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
  height: 300px;
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
  .bni-metric-grid { grid-template-columns: repeat(2, 1fr); }
  .bni-bottom-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 1024px) {
  .bni-main-grid { grid-template-columns: 1fr; }
  .bni-exec-two-col { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .bni-content { padding: 12px 14px 20px; }
  .bni-topbar-row1, .bni-topbar-row2 { flex-direction: column; align-items: stretch; gap: 10px; }
  .bni-topbar-right { flex-wrap: wrap; justify-content: flex-end; }
  .bni-search-box { width: 100%; }
  .bni-metric-grid, .bni-bottom-grid, .bni-exec-kpi-grid { grid-template-columns: 1fr; }
  .bni-action-buttons { flex-wrap: wrap; }
}

/* ═══ DARK MODE ══════════════════════════════════════════ */
.bni-dashboard[data-theme="dark"] {
  --bg: #0f1623;
  --card: #1a2335;
  --border: #2a3547;
  --border-soft: #1e2d42;
  --text: #e9edf3;
  --text-2: #8fa3b8;
  --text-3: #56718a;
  --teal-soft: #0d2f32;
  --green-soft: #0d2e1c;
  --red-soft: #2e1118;
  --shadow: 0 8px 20px rgba(0,0,0,.3);
  --shadow-soft: 0 4px 12px rgba(0,0,0,.2);
}
.bni-dashboard[data-theme="dark"] input {
  color: var(--text);
  background: transparent;
}
.bni-dashboard[data-theme="dark"] .bni-rev-periods {
  background: #0d1b2a;
}
.bni-dashboard[data-theme="dark"] .bni-evt { background: #141e2e; }
.bni-dashboard[data-theme="dark"] .bni-evt-empty { background: #141e2e; }

/* ═══ TOPBAR EXTRAS ══════════════════════════════════════ */
.bni-kbd {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-3);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 5px;
  flex-shrink: 0;
}
.bni-search-box { cursor: pointer; }

/* ─── Bell notification ──────────────────────────────── */
.bni-bell-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--red);
  border: 2px solid var(--card);
}
.bni-notif-drop {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 12px 32px rgba(0,0,0,.12);
  z-index: 200;
}
.bni-notif-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--border-soft);
}
.bni-notif-hd strong { font-size: 13px; font-weight: 700; }
.bni-notif-pill {
  font-size: 11px;
  font-weight: 700;
  color: var(--teal);
  background: var(--teal-soft);
  padding: 2px 8px;
  border-radius: 999px;
}
.bni-notif-scroll {
  max-height: 320px;
  overflow-y: auto;
}
.bni-ni {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-soft);
  transition: background .15s;
}
.bni-ni:hover { background: var(--bg); }
.bni-ni--unread { background: var(--teal-soft); }
.bni-ni--unread:hover { background: #c8f0f0; }
.bni-ni-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--teal);
  flex-shrink: 0;
  margin-top: 6px;
}
.bni-ni-body strong { display: block; font-size: 12px; font-weight: 700; margin-bottom: 2px; }
.bni-ni-body p { font-size: 11px; color: var(--text-2); margin: 0 0 3px; }
.bni-ni-body small { font-size: 10px; color: var(--text-3); }

/* ═══ EXEC DIVIDER ═══════════════════════════════════════ */
.bni-exec-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 24px 0 16px;
}
.bni-exec-divider::before,
.bni-exec-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.bni-exec-divider span {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: .06em;
  white-space: nowrap;
}

/* ═══ EXEC KPI GRID ══════════════════════════════════════ */
.bni-exec-kpi-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 12px;
  margin-bottom: 14px;
}
@media (max-width: 1400px) {
  .bni-exec-kpi-grid { grid-template-columns: repeat(4, 1fr); }
}
.bni-exec-kpi-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 14px;
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 4px;
  transition: box-shadow .2s, transform .2s;
}
.bni-exec-kpi-card:hover { box-shadow: var(--shadow); transform: translateY(-1px); }
.bni-ekc-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.bni-ekc-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  background: var(--teal-soft);
  color: var(--teal);
  display: flex; align-items: center; justify-content: center;
}
.bni-ekc-change {
  font-size: 11px; font-weight: 700;
  padding: 2px 6px; border-radius: 6px;
}
.bni-ekc-change.up { color: var(--green); background: var(--green-soft); }
.bni-ekc-change.down { color: var(--red); background: var(--red-soft); }
.bni-ekc-val { font-size: 20px; font-weight: 800; line-height: 1.2; }
.bni-ekc-label { font-size: 12px; font-weight: 700; color: var(--text-2); }
.bni-ekc-cap { font-size: 10px; color: var(--text-3); }

/* ═══ FILTER BAR ═════════════════════════════════════════ */
.bni-exec-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.bni-exec-filter-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-2);
  margin-right: 4px;
}
.bni-fp-btn {
  height: 30px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-2);
  cursor: pointer;
  font-family: inherit;
  transition: all .15s;
}
.bni-fp-btn:hover { border-color: var(--teal); color: var(--teal); }
.bni-fp-btn.active { background: var(--teal); color: #fff; border-color: var(--teal); }

/* ═══ TWO COLUMN EXEC LAYOUT ═════════════════════════════ */
.bni-exec-two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 14px;
}

/* ═══ FUNNEL ════════════════════════════════════════════ */
.bni-funnel {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 0;
}
.bni-funnel-row { display: flex; flex-direction: column; gap: 2px; }
.bni-funnel-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  border-radius: 8px;
  min-width: 40%;
  transition: width .5s ease;
}
.bni-funnel-label { font-size: 12px; font-weight: 700; color: #fff; }
.bni-funnel-val { font-size: 14px; font-weight: 800; color: #fff; }
.bni-funnel-conv {
  font-size: 11px;
  color: var(--text-3);
  padding-left: 14px;
  margin-bottom: 2px;
}

/* ═══ RM TABLE ══════════════════════════════════════════ */
.bni-rm-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.bni-rm-table th {
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-3);
  padding: 6px 8px;
  border-bottom: 1px solid var(--border-soft);
}
.bni-rm-table td { padding: 8px 8px; border-bottom: 1px solid var(--border-soft); }
.bni-rm-rank {
  width: 22px; height: 22px;
  border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
  background: var(--bg); color: var(--text-2);
}
.bni-rm-rank.gold { background: #fef3c7; color: #d97706; }
.bni-rm-rank.silver { background: #f1f5f9; color: #64748b; }
.bni-rm-rank.bronze { background: #fef0e6; color: #c2613f; }
.bni-rm-name { font-weight: 700; color: var(--text); }
.bni-rm-branch { color: var(--text-2); font-size: 11px; }
.bni-rm-deals { font-weight: 700; color: var(--teal); }
.bni-rm-val { font-weight: 700; }
.bni-rm-rate {
  background: var(--green-soft); color: var(--green);
  padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;
}

/* ═══ RISK ALERTS ════════════════════════════════════════ */
.bni-risk-count {
  font-size: 11px; font-weight: 700;
  background: var(--red-soft); color: var(--red);
  padding: 2px 8px; border-radius: 999px;
}
.bni-risk-list { display: flex; flex-direction: column; gap: 10px; }
.bni-risk-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: var(--bg);
}
.bni-risk-badge {
  font-size: 9px; font-weight: 800;
  padding: 2px 6px; border-radius: 4px;
  white-space: nowrap; flex-shrink: 0; margin-top: 2px;
  letter-spacing: .03em;
}
.bni-risk-red { background: #fecdca; color: #c01048; }
.bni-risk-orange { background: #fedf89; color: #b54708; }
.bni-risk-yellow { background: #fef9c3; color: #854d0e; }
.bni-risk-blue { background: #dbeafe; color: #1d4ed8; }
.bni-risk-gray { background: var(--border-soft); color: var(--text-2); }
.bni-risk-body { flex: 1; }
.bni-risk-body strong { display: block; font-size: 12px; font-weight: 700; margin-bottom: 3px; }
.bni-risk-body p { font-size: 11px; color: var(--text-2); margin: 0; }
.bni-risk-action {
  font-size: 11px; font-weight: 600;
  color: var(--teal); border: 1px solid var(--teal);
  background: transparent; border-radius: 6px;
  padding: 4px 10px; cursor: pointer; white-space: nowrap;
  flex-shrink: 0; transition: background .15s;
}
.bni-risk-action:hover { background: var(--teal-soft); }

/* ═══ AI INSIGHTS ════════════════════════════════════════ */
.bni-ai-list { display: flex; flex-direction: column; gap: 12px; }
.bni-ai-item {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 12px 14px;
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
}
.bni-ai-icon { font-size: 20px; flex-shrink: 0; }
.bni-ai-item strong { display: block; font-size: 12px; font-weight: 700; margin-bottom: 3px; }
.bni-ai-item p { font-size: 12px; color: var(--text-2); margin: 0; }
@keyframes bni-spin { to { transform: rotate(360deg); } }
.bni-spin { animation: bni-spin .8s linear infinite; }

/* ═══ HEATMAP ════════════════════════════════════════════ */
.bni-exec-heatmap-card { margin-bottom: 14px; }
.bni-hm-wrap { overflow-x: auto; }
.bni-hm-table { width: 100%; border-collapse: collapse; }
.bni-hm-table th {
  font-size: 11px; font-weight: 700; color: var(--text-2);
  padding: 8px 12px; text-align: center;
}
.bni-hm-rowlabel {
  font-size: 12px; font-weight: 700; color: var(--text);
  padding: 8px 14px 8px 0; white-space: nowrap;
}
.bni-hm-cell {
  text-align: center;
  font-size: 12px; font-weight: 700;
  padding: 10px 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity .15s;
}
.bni-hm-cell:hover { opacity: .8; }
.bni-hm-legend {
  display: flex; align-items: center; gap: 10px;
  margin-top: 12px;
  font-size: 11px; color: var(--text-3);
}
.bni-hm-grad {
  flex: 1; max-width: 160px; height: 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, #d1fadf, #fedf89, #fecdca);
}
.bni-hm-tip {
  position: fixed;
  background: #1a2335; color: #fff;
  padding: 8px 12px; border-radius: 8px;
  font-size: 12px; pointer-events: none;
  z-index: 9999; white-space: nowrap;
  box-shadow: 0 4px 16px rgba(0,0,0,.2);
}
.bni-hm-tip strong { display: block; margin-bottom: 3px; }

/* ═══ PENDING APPROVALS ══════════════════════════════════ */
.bni-pa-table {
  width: 100%; border-collapse: collapse; font-size: 12px;
}
.bni-pa-table th {
  text-align: left; font-size: 11px; font-weight: 700;
  color: var(--text-3); padding: 6px 8px;
  border-bottom: 1px solid var(--border-soft);
}
.bni-pa-table td { padding: 8px; border-bottom: 1px solid var(--border-soft); }
.bni-pa-done td { opacity: .5; }
.bni-seg-badge {
  font-size: 10px; font-weight: 700;
  padding: 2px 6px; border-radius: 5px;
  background: var(--teal-soft); color: var(--teal);
}
.bni-pa-nom { font-weight: 700; }
.bni-pa-days {
  font-size: 11px; font-weight: 700;
  padding: 2px 7px; border-radius: 5px;
  background: var(--green-soft); color: var(--green);
}
.bni-pa-days.warn { background: var(--red-soft); color: var(--red); }
.bni-pa-acts { display: flex; gap: 6px; }
.bni-btn-approve, .bni-btn-reject {
  width: 26px; height: 26px; border-radius: 6px;
  border: none; cursor: pointer; font-size: 13px;
  display: flex; align-items: center; justify-content: center;
  transition: opacity .15s;
}
.bni-btn-approve { background: var(--green-soft); color: var(--green); }
.bni-btn-approve:hover { opacity: .75; }
.bni-btn-reject { background: var(--red-soft); color: var(--red); }
.bni-btn-reject:hover { opacity: .75; }
.bni-pa-status {
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 5px;
}
.bni-pa-status.approve { background: var(--green-soft); color: var(--green); }
.bni-pa-status.reject { background: var(--red-soft); color: var(--red); }

/* ═══ ACTIVITIES FEED ════════════════════════════════════ */
.bni-act-feed { display: flex; flex-direction: column; gap: 0; }
.bni-act-item {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-soft);
}
.bni-act-item:last-child { border-bottom: none; }
.bni-act-icon { font-size: 16px; flex-shrink: 0; margin-top: 2px; }
.bni-act-body p { font-size: 12px; color: var(--text); margin: 0 0 2px; line-height: 1.5; }
.bni-act-body small { font-size: 10px; color: var(--text-3); }

/* ═══ FLOATING AI CHAT ═══════════════════════════════════ */
.bni-ai-fab {
  position: fixed;
  bottom: 24px; right: 24px;
  width: 50px; height: 50px;
  border-radius: 50%;
  background: var(--teal);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(0,140,149,.35);
  z-index: 100;
  transition: background .15s, transform .15s;
}
.bni-ai-fab:hover { background: var(--teal-dark); transform: scale(1.05); }
.bni-ai-chat {
  position: fixed;
  bottom: 84px; right: 24px;
  width: 320px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: var(--radius, 16px);
  box-shadow: 0 16px 40px rgba(0,0,0,.15);
  z-index: 100;
  display: flex; flex-direction: column;
  overflow: hidden;
}
.bni-ai-chat-hd {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
  background: var(--teal);
  color: #fff;
}
.bni-ai-chat-hd strong { font-size: 13px; font-weight: 700; }
.bni-ai-chat-hd button { background: transparent; border: none; color: #fff; cursor: pointer; }
.bni-ai-chat-body {
  flex: 1; max-height: 240px; overflow-y: auto;
  padding: 12px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.bni-ai-msg {
  max-width: 88%; font-size: 12px; line-height: 1.5;
  padding: 8px 12px; border-radius: 12px;
}
.bni-ai-msg.bot { background: var(--teal-soft, #d9f3f4); color: var(--text, #111827); align-self: flex-start; border-bottom-left-radius: 2px; }
.bni-ai-msg.user { background: var(--teal); color: #fff; align-self: flex-end; border-bottom-right-radius: 2px; }
.bni-ai-chat-foot {
  display: flex; gap: 8px; padding: 10px 12px;
  border-top: 1px solid var(--border-soft, #eef2f6);
}
.bni-ai-chat-foot input {
  flex: 1; border: 1px solid var(--border, #e5e7eb); border-radius: 8px;
  padding: 6px 10px; font-size: 12px; outline: none;
  background: var(--bg, #f8fafc); color: var(--text, #111827); font-family: inherit;
}
.bni-ai-chat-foot input:focus { border-color: var(--teal); }
.bni-ai-chat-foot button {
  width: 32px; height: 32px;
  background: var(--teal); color: #fff; border: none;
  border-radius: 8px; cursor: pointer; display: flex;
  align-items: center; justify-content: center;
}

/* ═══ MODALS ═════════════════════════════════════════════ */
.bni-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 500;
}
.bni-cmd-overlay { align-items: flex-start; padding-top: 10vh; }
.bni-modal {
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: var(--radius, 16px);
  width: 440px; max-width: calc(100vw - 32px);
  box-shadow: 0 20px 60px rgba(0,0,0,.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.bni-modal--sm { width: 360px; }
.bni-modal-hd {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-soft, #eef2f6);
}
.bni-modal-hd strong { font-size: 14px; font-weight: 700; }
.bni-modal-hd button {
  background: none; border: none; cursor: pointer;
  color: var(--text-2, #475569); padding: 4px;
}
.bni-modal-body {
  padding: 16px 20px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}
.bni-modal-ft {
  position: sticky;
  bottom: 0;
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 12px 20px;
  border-top: 1px solid var(--border-soft, #eef2f6);
  background: var(--card, #fff);
}
.bni-widget-list { display: flex; flex-direction: column; gap: 10px; }
.bni-widget-row {
  display: flex; align-items: center; gap: 10px;
  font-size: 13px; font-weight: 600; cursor: pointer;
}
.bni-widget-row input { width: 16px; height: 16px; cursor: pointer; accent-color: var(--teal); }
.bni-btn-cancel {
  height: 34px; padding: 0 16px;
  border: 1px solid var(--border, #e5e7eb); border-radius: var(--radius-sm, 10px);
  background: var(--card, #fff); font-size: 12px; font-weight: 600;
  color: var(--text, #111827); cursor: pointer; font-family: inherit;
}
.bni-btn-save {
  height: 34px; padding: 0 16px;
  border: none; border-radius: var(--radius-sm);
  background: var(--teal); color: #fff;
  font-size: 12px; font-weight: 700;
  cursor: pointer; font-family: inherit;
  display: inline-flex; align-items: center; gap: 6px;
}
.bni-btn-save:hover { background: var(--teal-dark); }
.bni-fmt-btn {
  height: 38px; padding: 0 20px;
  border: 1px solid var(--border, #e5e7eb); border-radius: var(--radius-sm, 10px);
  background: var(--card, #fff); font-size: 13px; font-weight: 600;
  color: var(--text, #111827); cursor: pointer; font-family: inherit;
  transition: all .15s;
}
.bni-fmt-btn.active { background: var(--teal); color: #fff; border-color: var(--teal); }
.bni-export-status {
  padding: 10px 14px;
  background: var(--green-soft, #d1fadf); color: var(--green, #059669);
  border-radius: var(--radius-sm, 10px);
  font-size: 13px; font-weight: 600;
}

/* ─── Command Palette ────────────────────────────────── */
.bni-cmd {
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: var(--radius, 16px);
  width: 500px; max-width: calc(100vw - 32px);
  box-shadow: 0 24px 60px rgba(0,0,0,.25);
  overflow: hidden;
}
.bni-cmd-search {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border-soft, #eef2f6);
}
.bni-cmd-search input {
  flex: 1; border: none; outline: none;
  font-size: 15px; background: transparent;
  color: var(--text, #111827); font-family: inherit;
}
.bni-cmd-list { padding: 6px; max-height: 300px; overflow-y: auto; }
.bni-cmd-item {
  display: flex; align-items: center; gap: 12px;
  width: 100%; padding: 10px 14px;
  border: none; background: transparent;
  border-radius: var(--radius-sm, 10px);
  font-size: 13px; font-weight: 600; color: var(--text, #111827);
  cursor: pointer; text-align: left; font-family: inherit;
  transition: background .1s;
}
.bni-cmd-item:hover { background: var(--teal-soft, #d9f3f4); color: var(--teal, #008C95); }
.bni-cmd-empty { padding: 16px; text-align: center; color: var(--text-3, #64748b); font-size: 13px; }
</style>
