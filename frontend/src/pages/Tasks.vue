<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Tasks" />
      </template>
      <template #right-header>
        <div
          v-if="ctx.data?.user_full_name"
          class="ml-6 flex items-center gap-1.5 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-2.5 py-1.5"
        >
          <FeatherIcon name="user" class="h-3.5 w-3.5 text-ink-gray-5" />
          <span class="text-sm font-medium text-ink-gray-8">{{ ctx.data.user_full_name }}</span>
        </div>
      </template>
    </LayoutHeader>

    <!-- Tab strip -->
    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-4">
      <div class="flex items-center justify-between gap-3">
        <div class="flex gap-3 overflow-x-auto">
          <button
            v-for="tab in TABS"
            :key="tab.view"
            class="border-b-2 py-2 text-base transition-colors whitespace-nowrap"
            :class="activeView === tab.view
              ? 'border-ink-gray-8 font-medium text-ink-gray-9'
              : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
            @click="activeView = tab.view"
          >
            {{ tab.label }}
          </button>
        </div>
        <div class="flex shrink-0 items-center gap-2 py-1.5">
          <Button
            v-if="activeView === 'analytics'"
            variant="outline"
            size="sm"
            label="Export CSV"
            @click="exportAnalytics"
          >
            <template #prefix><FeatherIcon name="download" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'templates'"
            variant="solid"
            size="sm"
            label="New Template"
            @click="openTemplateDialog(null)"
          >
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'setup'"
            variant="solid"
            size="sm"
            label="New Type"
            @click="openTypeDialog(null)"
          >
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'inbox' || activeView === 'board'"
            variant="solid"
            size="sm"
            label="Create"
            @click="openCreateDialog"
          >
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          </Button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto bg-surface-gray-1">
      <div class="w-full px-3 py-2">

        <!-- ── INBOX ───────────────────────────────────────────── -->
        <template v-if="activeView === 'inbox'">
          <!-- KPI strip -->
          <div class="mb-3 grid gap-3 md:grid-cols-5">
            <KpiCard label="My Open" :value="ctx.data?.counters?.open ?? 0" icon="inbox" />
            <KpiCard label="Due Today" :value="ctx.data?.counters?.due_today ?? 0" icon="calendar" theme="blue" />
            <KpiCard label="Overdue" :value="ctx.data?.counters?.overdue ?? 0" icon="alert-circle" theme="red" />
            <KpiCard label="Blocked" :value="ctx.data?.counters?.blocked ?? 0" icon="slash" theme="orange" />
            <KpiCard label="Due This Week" :value="ctx.data?.counters?.this_week ?? 0" icon="trending-up" />
          </div>

          <!-- Filter strip -->
          <div class="mb-3 flex flex-wrap items-center gap-2">
            <div class="flex flex-1 items-center gap-2 rounded-md border border-outline-gray-2 bg-white px-3 py-1.5">
              <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-4" />
              <input
                v-model="inboxFilters.search"
                type="text"
                :placeholder="__('Search tasks…')"
                class="flex-1 bg-transparent text-sm outline-none"
                @input="debouncedReload"
              />
            </div>
            <select
              v-model="inboxFilters.scope"
              class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8"
              @change="inbox.reload()"
            >
              <option value="me">{{ __('My tasks') }}</option>
              <option value="team">{{ __('All team') }}</option>
              <option value="following">{{ __('Created by me') }}</option>
            </select>
            <select
              v-model="inboxFilters.task_type"
              class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8"
              @change="inbox.reload()"
            >
              <option value="">{{ __('All types') }}</option>
              <option v-for="t in ctx.data?.task_types || []" :key="t.name" :value="t.name">{{ t.type_name }}</option>
            </select>
            <select
              v-model="inboxFilters.priority"
              class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8"
              @change="inbox.reload()"
            >
              <option value="">{{ __('All priorities') }}</option>
              <option v-for="p in PRIORITIES" :key="p" :value="p">{{ p }}</option>
            </select>
            <select
              v-model="inboxFilters.sort_by"
              class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8"
              @change="inbox.reload()"
            >
              <option value="sla">{{ __('Sort: SLA urgency') }}</option>
              <option value="due">{{ __('Sort: Due date') }}</option>
              <option value="priority">{{ __('Sort: Priority') }}</option>
              <option value="updated">{{ __('Sort: Recently updated') }}</option>
            </select>
          </div>

          <!-- Bulk action bar -->
          <div v-if="selected.length" class="mb-3 flex items-center justify-between rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 shadow-sm">
            <span class="text-sm text-ink-gray-7">{{ selected.length }} {{ __('selected') }}</span>
            <div class="flex gap-2">
              <Button size="sm" variant="outline" label="Complete" @click="bulkComplete" />
              <Button size="sm" variant="ghost" label="Clear" @click="selected = []" />
            </div>
          </div>

          <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
            <div v-if="inbox.loading" class="flex h-40 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else-if="!inboxRows.length" class="flex flex-col items-center justify-center px-6 py-16 text-center">
              <FeatherIcon name="inbox" class="mb-3 h-8 w-8 text-ink-gray-3" />
              <p class="text-base font-medium text-ink-gray-8">{{ __('Inbox zero') }}</p>
              <p class="mt-1 text-sm text-ink-gray-5">{{ __('No tasks match your filters.') }}</p>
            </div>
            <div v-else>
              <div
                v-for="t in inboxRows"
                :key="t.name"
                class="flex min-w-0 items-center gap-3 border-b border-outline-gray-1 px-3 py-1.5 last:border-b-0 hover:bg-surface-gray-1 cursor-pointer"
                @click="openDrawer(t.name)"
              >
                <input
                  type="checkbox"
                  :checked="selected.includes(t.name)"
                  class="h-4 w-4 shrink-0 rounded border-outline-gray-3"
                  @click.stop
                  @change="toggleSelect(t.name)"
                />
                <PriorityIcon :priority="t.priority" />
                <div class="min-w-0 flex-1">
                  <div class="flex min-w-0 items-center gap-2">
                    <span class="truncate text-sm font-medium text-ink-gray-9">
                      {{ t.title || __('Untitled task') }}
                    </span>
                    <Badge v-if="t.reference_label" :label="t.reference_label" theme="gray" variant="subtle" />
                    <Badge
                      v-if="t.status === 'Blocked'"
                      label="Blocked"
                      theme="orange"
                      variant="subtle"
                    />
                  </div>
                  <div class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-ink-gray-5">
                    <span v-if="t.task_type" class="truncate">{{ t.task_type }}</span>
                    <span v-if="t.due_date" class="inline-flex items-center gap-1"
                          :class="t.sla_state === 'Breached' ? 'text-red-600 font-medium' : ''">
                      <FeatherIcon name="clock" class="h-3 w-3" />
                      {{ formatRelativeDue(t.due_date) }}
                    </span>
                  </div>
                </div>
                <SlaRibbon :task="t" class="hidden w-40 shrink-0 md:block" />
                <div class="flex shrink-0 items-center gap-2">
                  <div class="flex -space-x-2">
                    <Avatar
                      v-for="a in (t.assignees || []).slice(0, 3)"
                      :key="a.user"
                      :image="a.user_image"
                      :label="a.full_name"
                      size="sm"
                      class="ring-2 ring-white"
                    />
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    @click.stop="quickComplete(t)"
                  >
                    <FeatherIcon name="check" class="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    @click.stop="deleteTask(t)"
                  >
                    <FeatherIcon name="trash-2" class="h-4 w-4 text-ink-gray-4 hover:text-red-500" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ── BOARD ───────────────────────────────────────────── -->
        <template v-else-if="activeView === 'board'">
          <div class="mb-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <h2 class="text-base font-semibold text-ink-gray-9">{{ __('Status Board') }}</h2>
              <span class="text-xs text-ink-gray-5">{{ __('Drag a card to change its status.') }}</span>
            </div>
            <div class="flex items-center gap-1 rounded-md border border-outline-gray-2 bg-white p-1">
              <button
                v-for="opt in SWIMLANE_OPTIONS"
                :key="opt.value"
                class="rounded px-2 py-1 text-xs"
                :class="swimlane === opt.value ? 'bg-surface-gray-2 font-medium text-ink-gray-8' : 'text-ink-gray-5'"
                @click="swimlane = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <div class="grid gap-3" :style="`grid-template-columns: repeat(${BOARD_COLUMNS.length}, minmax(0, 1fr))`">
            <div
              v-for="col in BOARD_COLUMNS"
              :key="col.status"
              class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm"
              @dragover.prevent
              @drop="onDropToColumn($event, col.status)"
            >
              <div class="flex items-center justify-between border-b border-outline-gray-1 px-3 py-2">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-semibold uppercase tracking-wide text-ink-gray-7">{{ col.label }}</span>
                  <Badge :label="String(boardByStatus[col.status]?.length || 0)" theme="gray" variant="subtle" />
                </div>
                <span v-if="col.wip" class="text-xs text-ink-gray-4">WIP {{ col.wip }}</span>
              </div>
              <div class="p-2 space-y-2 min-h-[120px]">
                <div
                  v-for="t in boardByStatus[col.status] || []"
                  :key="t.name"
                  class="cursor-pointer rounded-md border border-outline-gray-2 bg-surface-white p-3 hover:border-outline-gray-3"
                  draggable="true"
                  @dragstart="onDragStart($event, t.name)"
                  @click="openDrawer(t.name)"
                >
                  <div class="flex items-start gap-2">
                    <PriorityIcon :priority="t.priority" />
                    <span class="flex-1 truncate text-sm text-ink-gray-8">{{ t.title }}</span>
                  </div>
                  <div class="mt-2 flex items-center justify-between">
                    <SlaRibbon :task="t" class="w-24" />
                    <div class="flex items-center gap-2">
                      <Avatar
                        v-if="t.assignees?.[0]"
                        :image="t.assignees[0].user_image"
                        :label="t.assignees[0].full_name"
                        size="xs"
                      />
                      <button class="text-ink-gray-4 hover:text-red-500" @click.stop="deleteTask(t)">
                        <FeatherIcon name="trash-2" class="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="!(boardByStatus[col.status]?.length)" class="py-4 text-center text-xs text-ink-gray-4">
                  {{ __('Empty') }}
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ── CALENDAR ───────────────────────────────────────── -->
        <template v-else-if="activeView === 'calendar'">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm p-3">
            <div class="mb-3 flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold text-ink-gray-9">{{ monthLabel }}</h2>
                <p class="mt-0.5 text-xs text-ink-gray-5">{{ __('Tasks rendered by due date. Click to open.') }}</p>
              </div>
              <div class="flex items-center gap-1">
                <Button size="sm" variant="outline" @click="shiftMonth(-1)">
                  <FeatherIcon name="chevron-left" class="h-4 w-4" />
                </Button>
                <Button size="sm" variant="outline" label="Today" @click="anchorMonth = today" />
                <Button size="sm" variant="outline" @click="shiftMonth(1)">
                  <FeatherIcon name="chevron-right" class="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div class="grid grid-cols-7 gap-px overflow-hidden rounded-md border border-outline-gray-2 bg-outline-gray-2 text-xs">
              <div v-for="d in WEEKDAYS" :key="d" class="bg-surface-gray-1 px-2 py-1.5 text-center text-[11px] font-medium uppercase tracking-wide text-ink-gray-5">{{ d }}</div>
              <div
                v-for="cell in calendarCells"
                :key="cell.iso"
                class="min-h-[88px] bg-white p-1.5"
                :class="cell.inMonth ? '' : 'bg-surface-gray-1'"
              >
                <div class="flex items-center justify-between">
                  <span :class="cell.isToday ? 'flex h-5 w-5 items-center justify-center rounded-full text-white text-[11px] font-medium' : 'text-[11px] text-ink-gray-6'"
                        :style="cell.isToday ? 'background: #FF6600' : ''">
                    {{ cell.day }}
                  </span>
                </div>
                <div class="mt-1 space-y-0.5">
                  <button
                    v-for="t in cell.tasks"
                    :key="t.name"
                    class="block w-full truncate rounded px-1.5 py-0.5 text-left text-[11px] hover:opacity-90"
                    :style="`background: ${prioritySoft(t.priority)}; color: ${priorityInk(t.priority)}`"
                    @click="openDrawer(t.name)"
                  >
                    {{ t.title }}
                  </button>
                </div>
              </div>
            </div>
            <p class="mt-3 text-xs text-ink-gray-4">{{ __('Tip: Google / Outlook calendar sync — coming soon.') }}</p>
          </div>
        </template>

        <!-- ── GANTT ───────────────────────────────────────────── -->
        <template v-else-if="activeView === 'gantt'">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
            <div class="border-b border-outline-gray-1 px-3 py-2">
              <h2 class="text-base font-semibold text-ink-gray-9">{{ __('Timeline & Dependencies') }}</h2>
              <p class="mt-0.5 text-xs text-ink-gray-5">{{ __('Bars sized by start → due; critical path highlighted in red.') }}</p>
            </div>
            <div v-if="gantt.loading" class="flex h-32 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else-if="!gantt.data?.tasks?.length" class="px-4 py-12 text-center text-sm text-ink-gray-4">
              {{ __('No tasks to plot.') }}
            </div>
            <div v-else class="overflow-x-auto px-4 py-4">
              <div class="min-w-[720px]">
                <div class="mb-2 flex border-b border-outline-gray-1 text-[11px] text-ink-gray-5">
                  <div class="w-64 shrink-0 pb-1">{{ __('Task') }}</div>
                  <div class="relative flex-1 pb-1">
                    <div class="flex justify-between">
                      <span v-for="(d, i) in ganttScale" :key="i">{{ d }}</span>
                    </div>
                  </div>
                </div>
                <div
                  v-for="t in ganttRows"
                  :key="t.name"
                  class="flex items-center border-b border-outline-gray-1 py-1.5"
                >
                  <div class="flex w-64 shrink-0 cursor-pointer items-center gap-2 pr-3 text-sm text-ink-gray-8 hover:underline" @click="openDrawer(t.name)">
                    <PriorityIcon :priority="t.priority" />
                    <span class="min-w-0 truncate">{{ t.title }}</span>
                  </div>
                  <div class="relative h-5 flex-1 rounded bg-surface-gray-1">
                    <div
                      class="absolute top-0 bottom-0 rounded"
                      :style="`left: ${t.barLeft}%; width: ${t.barWidth}%; background: ${t.isCritical ? '#dc2626' : '#FF6600'}`"
                    />
                    <FeatherIcon
                      v-if="t.is_milestone"
                      name="flag"
                      class="absolute top-0.5 h-4 w-4 text-amber-500"
                      :style="`left: calc(${t.barLeft + t.barWidth}% - 8px)`"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ── WORKLOAD ────────────────────────────────────────── -->
        <template v-else-if="activeView === 'workload'">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
            <div class="border-b border-outline-gray-1 px-3 py-2">
              <h2 class="text-base font-semibold text-ink-gray-9">{{ __('Team Workload') }}</h2>
              <p class="mt-0.5 text-xs text-ink-gray-5">{{ __('Open tasks per user — colour-coded by load.') }}</p>
            </div>
            <div v-if="workloadRes.loading" class="flex h-32 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <table v-else class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-3 py-1.5 font-medium">{{ __('User') }}</th>
                  <th class="px-3 py-1.5 font-medium text-center">{{ __('Open') }}</th>
                  <th class="px-3 py-1.5 font-medium text-center">{{ __('Overdue') }}</th>
                  <th class="px-3 py-1.5 font-medium text-center">{{ __('Blocked') }}</th>
                  <th class="px-3 py-1.5 font-medium text-center">{{ __('Capacity') }}</th>
                  <th class="px-3 py-1.5 font-medium text-center">{{ __('Logged') }}</th>
                  <th class="px-3 py-1.5 font-medium">{{ __('Load') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in workloadRes.data || []"
                  :key="row.user"
                  class="border-b border-outline-gray-1 last:border-b-0"
                >
                  <td class="px-3 py-2">
                    <div class="flex items-center gap-2">
                      <Avatar :image="row.user_image" :label="row.full_name" size="sm" />
                      <div>
                        <div class="font-medium text-ink-gray-9">{{ row.full_name }}</div>
                        <div class="text-xs text-ink-gray-4">{{ row.user }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-3 py-2 text-center text-ink-gray-7">{{ row.open }}</td>
                  <td class="px-3 py-2 text-center">
                    <Badge :label="String(row.overdue)" :theme="row.overdue ? 'red' : 'gray'" variant="subtle" />
                  </td>
                  <td class="px-3 py-2 text-center">
                    <Badge :label="String(row.blocked)" :theme="row.blocked ? 'orange' : 'gray'" variant="subtle" />
                  </td>
                  <td class="px-3 py-2 text-center text-ink-gray-7">{{ row.capacity }}</td>
                  <td class="px-3 py-2 text-center text-ink-gray-7">{{ row.logged_hours != null ? row.logged_hours + 'h' : (row.logged_minutes ? Math.round(row.logged_minutes / 60) + 'h' : '—') }}</td>
                  <td class="px-3 py-2">
                    <div class="h-2 w-32 overflow-hidden rounded-full bg-surface-gray-2">
                      <div
                        class="h-full rounded-full"
                        :style="`width: ${Math.min(100, Math.round((row.open / row.capacity) * 100))}%; background: ${loadColor(row.open, row.capacity)}`"
                      />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- ── ANALYTICS ──────────────────────────────────────── -->
        <template v-else-if="activeView === 'analytics'">
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-base font-semibold text-ink-gray-9">{{ __('SLA Analytics') }}</h2>
            <div class="flex items-center gap-2">
              <select v-model="analyticsDays" class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm" @change="analytics.reload()">
                <option value="14">{{ __('Last 14 days') }}</option>
                <option value="30">{{ __('Last 30 days') }}</option>
              </select>
              <select v-model="analyticsGroup" class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm" @change="analytics.reload()">
                <option value="task_type">{{ __('Group by: Type') }}</option>
                <option value="assigned_to">{{ __('Group by: User') }}</option>
                <option value="priority">{{ __('Group by: Priority') }}</option>
              </select>
            </div>
          </div>

          <div v-if="analytics.loading" class="flex h-40 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>
          <template v-else>
            <div class="mb-3 grid gap-3 md:grid-cols-4">
              <KpiCard label="SLA Compliance" :value="`${analytics.data?.compliance_pct ?? 0}%`" icon="check-circle" theme="teal" />
              <KpiCard label="Avg Resolve" :value="formatMinutes(analytics.data?.avg_resolve_minutes ?? 0)" icon="clock" />
              <KpiCard label="Breaches" :value="String(analytics.data?.breached ?? 0)" icon="alert-circle" theme="red" />
              <KpiCard label="Escalations" :value="String(analytics.data?.escalation_count ?? 0)" icon="trending-up" theme="orange" />
            </div>

            <div class="grid gap-3 lg:grid-cols-3">
              <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm lg:col-span-2">
                <h3 class="mb-3 text-sm font-medium text-ink-gray-7">{{ __('Daily breach vs completion') }}</h3>
                <div class="flex h-40 items-end gap-1">
                  <div
                    v-for="(d, i) in analytics.data?.trend || []"
                    :key="i"
                    class="flex flex-1 flex-col justify-end"
                    :title="`${d.date}: ${d.breached} breach / ${d.completed} done`"
                  >
                    <div
                      class="rounded-t"
                      :style="`height: ${Math.min(100, d.breached * 14)}%; background: #dc2626; opacity: 0.85`"
                    />
                    <div
                      class="rounded-b"
                      :style="`height: ${Math.min(100, d.completed * 8)}%; background: #FF6600`"
                    />
                  </div>
                </div>
                <div class="mt-2 flex gap-3 text-xs text-ink-gray-5">
                  <span><span class="mr-1 inline-block h-2 w-2 rounded-full" style="background:#dc2626"></span>Breached</span>
                  <span><span class="mr-1 inline-block h-2 w-2 rounded-full" style="background:#FF6600"></span>Completed</span>
                </div>
              </div>
              <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
                <h3 class="mb-3 text-sm font-medium text-ink-gray-7">{{ __('Bottleneck groups') }}</h3>
                <div class="space-y-3">
                  <div v-for="g in (analytics.data?.groups || []).slice(0, 6)" :key="g.key">
                    <div class="flex justify-between text-xs text-ink-gray-6">
                      <span class="truncate">{{ g.key }}</span>
                      <span :class="g.compliance < 80 ? 'text-red-600 font-medium' : ''">{{ g.compliance }}%</span>
                    </div>
                    <div class="mt-1 h-1.5 overflow-hidden rounded-full bg-surface-gray-2">
                      <div
                        class="h-full rounded-full"
                        :style="`width: ${g.compliance}%; background: ${g.compliance < 80 ? '#dc2626' : '#FF6600'}`"
                      />
                    </div>
                  </div>
                  <p v-if="!(analytics.data?.groups || []).length" class="text-sm text-ink-gray-4">{{ __('No data yet.') }}</p>
                </div>
              </div>
            </div>
          </template>
        </template>

        <!-- ── TEMPLATES ──────────────────────────────────────── -->
        <template v-else-if="activeView === 'templates'">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
            <div class="border-b border-outline-gray-1 px-3 py-2">
              <h2 class="text-base font-semibold text-ink-gray-9">{{ __('Task Templates') }}</h2>
              <p class="mt-0.5 text-xs text-ink-gray-5">{{ __('Reusable bundles of subtasks + checklist applied to leads, deals, or applications.') }}</p>
            </div>
            <div v-if="templates.loading" class="flex h-24 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else>
              <div v-for="tpl in templates.data || []" :key="tpl.name" class="border-b border-outline-gray-1 px-4 py-4 last:border-b-0">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <div class="flex items-center gap-2">
                      <h4 class="text-base font-medium text-ink-gray-9">{{ tpl.template_name }}</h4>
                      <Badge :label="`v${tpl.version}`" theme="gray" variant="subtle" />
                      <Badge v-if="tpl.default_type" :label="tpl.default_type" theme="teal" variant="subtle" />
                      <Badge :label="tpl.default_priority" :theme="priorityTheme(tpl.default_priority)" variant="subtle" />
                    </div>
                    <p v-if="tpl.description" class="mt-1 text-sm text-ink-gray-5">{{ tpl.description }}</p>
                    <p class="mt-1 text-xs text-ink-gray-4">
                      {{ (tpl.subtasks || []).length }} {{ __('subtasks') }} · {{ (tpl.checklist || []).length }} {{ __('checklist items') }}
                    </p>
                  </div>
                  <div class="flex shrink-0 gap-2">
                    <Button size="sm" variant="outline" label="Apply" @click="openApplyDialog(tpl)" />
                    <Button size="sm" variant="ghost" label="Edit" @click="openTemplateDialog(tpl)" />
                    <Button size="sm" variant="ghost" @click="deleteTemplate(tpl)">
                      <FeatherIcon name="trash-2" class="h-4 w-4 text-ink-gray-4 hover:text-red-500" />
                    </Button>
                  </div>
                </div>
              </div>
              <div v-if="!(templates.data || []).length" class="px-4 py-10 text-center text-sm text-ink-gray-5">
                {{ __('No templates yet.') }}
              </div>
            </div>
          </div>
        </template>

        <!-- ── SETUP ──────────────────────────────────────────── -->
        <template v-else-if="activeView === 'setup'">
          <div class="mb-3 rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
            <div class="border-b border-outline-gray-1 px-3 py-2">
              <h3 class="text-base font-semibold text-ink-gray-9">{{ __('Task Types — SLA Matrix') }}</h3>
            </div>
            <div v-if="taskTypes.loading" class="flex h-24 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <table v-else class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-3 py-1.5 font-medium">{{ __('Type') }}</th>
                  <th class="px-3 py-1.5 font-medium text-right">{{ __('Critical') }}</th>
                  <th class="px-3 py-1.5 font-medium text-right">{{ __('High') }}</th>
                  <th class="px-3 py-1.5 font-medium text-right">{{ __('Medium') }}</th>
                  <th class="px-3 py-1.5 font-medium text-right">{{ __('Low') }}</th>
                  <th class="px-3 py-1.5 font-medium text-center">{{ __('Business hours') }}</th>
                  <th class="px-3 py-1.5 font-medium text-right">{{ __('Actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in taskTypes.data || []" :key="t.name" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-3 py-1.5">
                    <span class="inline-flex h-2 w-2 rounded-full mr-2" :style="`background: ${t.color || '#FF6600'}`" />
                    <span class="text-ink-gray-8">{{ t.type_name }}</span>
                  </td>
                  <td class="px-3 py-1.5 text-right text-ink-gray-7">{{ formatMinutes(t.sla_matrix?.Critical) }}</td>
                  <td class="px-3 py-1.5 text-right text-ink-gray-7">{{ formatMinutes(t.sla_matrix?.High) }}</td>
                  <td class="px-3 py-1.5 text-right text-ink-gray-7">{{ formatMinutes(t.sla_matrix?.Medium) }}</td>
                  <td class="px-3 py-1.5 text-right text-ink-gray-7">{{ formatMinutes(t.sla_matrix?.Low) }}</td>
                  <td class="px-3 py-1.5 text-center">
                    <Badge :label="t.business_hours_only ? 'Yes' : 'No'" :theme="t.business_hours_only ? 'green' : 'gray'" variant="subtle" />
                  </td>
                  <td class="px-3 py-1.5 text-right">
                    <Button size="sm" variant="ghost" label="Edit" @click="openTypeDialog(t)" />
                    <Button size="sm" variant="ghost" @click="deleteTaskType(t)">
                      <FeatherIcon name="trash-2" class="h-4 w-4 text-ink-gray-4 hover:text-red-500" />
                    </Button>
                  </td>
                </tr>
                <tr v-if="!(taskTypes.data || []).length"><td colspan="7" class="px-4 py-10 text-center text-sm text-ink-gray-5">{{ __('No task types.') }}</td></tr>
              </tbody>
            </table>
          </div>

          <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
            <div class="border-b border-outline-gray-1 px-3 py-2 flex items-center justify-between">
              <h3 class="text-base font-semibold text-ink-gray-9">{{ __('Escalation Rules') }}</h3>
              <Button size="sm" variant="outline" label="New Rule" @click="openRuleDialog(null)">
                <template #prefix><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
              </Button>
            </div>
            <div v-if="rules.loading" class="flex h-24 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <table v-else class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-3 py-1.5 font-medium">{{ __('Rule') }}</th>
                  <th class="px-3 py-1.5 font-medium">{{ __('Type') }}</th>
                  <th class="px-3 py-1.5 font-medium text-center">{{ __('Level') }}</th>
                  <th class="px-3 py-1.5 font-medium text-right">{{ __('Past Due') }}</th>
                  <th class="px-3 py-1.5 font-medium">{{ __('Action') }}</th>
                  <th class="px-3 py-1.5 font-medium">{{ __('Recipient') }}</th>
                  <th class="px-3 py-1.5 font-medium text-right">{{ __('Actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in rules.data || []" :key="r.name" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-3 py-1.5 text-ink-gray-8">{{ r.rule_name }}</td>
                  <td class="px-3 py-1.5 text-ink-gray-7">{{ r.task_type || '—' }}</td>
                  <td class="px-3 py-1.5 text-center text-ink-gray-7">{{ r.level }}</td>
                  <td class="px-3 py-1.5 text-right text-ink-gray-7">{{ formatMinutes(r.after_minutes_past_due) }}</td>
                  <td class="px-3 py-1.5">
                    <Badge :label="r.action" :theme="r.action === 'reassign' ? 'orange' : r.action === 'flag' ? 'red' : 'blue'" variant="subtle" />
                  </td>
                  <td class="px-3 py-1.5 text-ink-gray-7">{{ r.recipient_user || r.recipient_role || '—' }}</td>
                  <td class="px-3 py-1.5 text-right">
                    <Button size="sm" variant="ghost" @click="deleteEscalationRule(r)">
                      <FeatherIcon name="trash-2" class="h-4 w-4 text-ink-gray-4 hover:text-red-500" />
                    </Button>
                  </td>
                </tr>
                <tr v-if="!(rules.data || []).length"><td colspan="6" class="px-4 py-10 text-center text-sm text-ink-gray-5">{{ __('No rules yet.') }}</td></tr>
              </tbody>
            </table>
          </div>
        </template>

      </div>
    </div>

    <!-- ── Drawer ──────────────────────────────────────────────── -->
    <TaskDetailDrawer
      v-if="drawer.open"
      v-model:open="drawer.open"
      :task-name="drawer.taskName"
      :team-users="ctx.data?.team_users || []"
      :task-types="ctx.data?.task_types || []"
      @changed="onTaskChanged"
    />

    <!-- ── Quick-create dialog ─────────────────────────────────── -->
    <Dialog v-model="createDialog" :options="{ title: __('New Task') }">
      <template #body-content>
        <div class="space-y-3">
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Title') }}</label>
            <input
              v-model="createForm.title"
              class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm focus:border-ink-gray-7 focus:outline-none"
              placeholder="What needs doing?"
            />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Priority') }}</label>
              <select v-model="createForm.priority" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option v-for="p in PRIORITIES" :key="p">{{ p }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Type') }}</label>
              <select v-model="createForm.task_type" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option value="">—</option>
                <option v-for="t in ctx.data?.task_types || []" :key="t.name" :value="t.name">{{ t.type_name }}</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Assignee') }}</label>
              <select v-model="createForm.assigned_to" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option v-for="u in ctx.data?.team_users || []" :key="u.name" :value="u.name">{{ u.full_name || u.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Due') }}</label>
              <input type="datetime-local" v-model="createForm.due_date" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
            </div>
          </div>
          <div class="rounded-md border border-outline-gray-1 p-3">
            <label class="flex items-center gap-2 text-sm font-medium text-ink-gray-7">
              <input type="checkbox" v-model="createForm.recurring" class="rounded" />
              {{ __('Repeat this task') }}
            </label>
            <div v-if="createForm.recurring" class="mt-3 grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs uppercase tracking-wide text-ink-gray-5">Frequency</label>
                <select v-model="createForm.recurrence_freq" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                  <option>Daily</option>
                  <option>Weekly</option>
                  <option>Monthly</option>
                  <option>Custom</option>
                </select>
              </div>
              <div>
                <label class="text-xs uppercase tracking-wide text-ink-gray-5">Every</label>
                <input type="number" min="1" v-model.number="createForm.recurrence_interval" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="text-xs uppercase tracking-wide text-ink-gray-5">Ends</label>
                <select v-model="createForm.recurrence_end_type" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                  <option value="never">Never</option>
                  <option value="date">On date</option>
                  <option value="count">After N occurrences</option>
                </select>
              </div>
              <div v-if="createForm.recurrence_end_type === 'date'">
                <label class="text-xs uppercase tracking-wide text-ink-gray-5">End Date</label>
                <input type="date" v-model="createForm.recurrence_end_date" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
              </div>
              <div v-else-if="createForm.recurrence_end_type === 'count'">
                <label class="text-xs uppercase tracking-wide text-ink-gray-5">Count</label>
                <input type="number" min="1" v-model.number="createForm.recurrence_end_count" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Create')" :disabled="!createForm.title" @click="submitCreate().then(close)" />
        </div>
      </template>
    </Dialog>

    <!-- ── Apply template dialog ───────────────────────────────── -->
    <Dialog v-model="applyDialog.open" :options="{ title: __('Apply Template') }">
      <template #body-content>
        <div class="space-y-3">
          <p class="text-sm text-ink-gray-7">{{ __('Applying') }}: <span class="font-medium">{{ applyDialog.template?.template_name }}</span></p>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Target Doctype') }}</label>
            <select v-model="applyDialog.target_doctype" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
              <option value="">—</option>
              <option value="CRM Lead">CRM Lead</option>
              <option value="CRM Deal">CRM Deal</option>
              <option value="CRM Credit Application">CRM Credit Application</option>
              <option value="CRM Committee Item">CRM Committee Item</option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Target Name') }}</label>
            <input v-model="applyDialog.target_name" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" placeholder="e.g. CRM-LEAD-2026-0001" />
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Due in days') }}</label>
            <input v-model.number="applyDialog.due_in_days" type="number" min="1" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Apply')" @click="submitApply().then(close)" />
        </div>
      </template>
    </Dialog>

    <!-- ── Template edit dialog ───────────────────────────────── -->
    <Dialog v-model="templateDialog.open" :options="{ title: templateDialog.data?.template_name ? __('Edit Template') : __('New Template') }">
      <template #body-content>
        <div class="space-y-3">
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Name') }}</label>
            <input v-model="templateDialog.data.template_name" :disabled="templateDialog.editing" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Type') }}</label>
              <select v-model="templateDialog.data.default_type" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option value="">—</option>
                <option v-for="t in taskTypes.data || []" :key="t.name" :value="t.name">{{ t.type_name }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Priority') }}</label>
              <select v-model="templateDialog.data.default_priority" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option v-for="p in PRIORITIES" :key="p">{{ p }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Description') }}</label>
            <textarea v-model="templateDialog.data.description" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Checklist (one per line)') }}</label>
            <textarea v-model="templateDialog.checklistText" rows="4" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Subtasks (one title per line)') }}</label>
            <textarea v-model="templateDialog.subtasksText" rows="4" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Save')" @click="submitTemplate().then(close)" />
        </div>
      </template>
    </Dialog>

    <!-- ── Task type dialog ───────────────────────────────────── -->
    <Dialog v-model="typeDialog.open" :options="{ title: typeDialog.editing ? __('Edit Task Type') : __('New Task Type') }">
      <template #body-content>
        <div class="space-y-3">
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Name') }}</label>
            <input v-model="typeDialog.data.type_name" :disabled="typeDialog.editing" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div v-for="p in PRIORITIES" :key="p">
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ p }} (min)</label>
              <input type="number" min="0" v-model.number="typeDialog.sla[p]" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
            </div>
          </div>
          <label class="flex items-center gap-2 text-sm">
            <input type="checkbox" v-model="typeDialog.data.business_hours_only" class="rounded border-outline-gray-3" />
            {{ __('Business hours only') }}
          </label>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Save')" @click="submitType().then(close)" />
        </div>
      </template>
    </Dialog>

    <!-- ── Escalation rule dialog ─────────────────────────────── -->
    <Dialog v-model="ruleDialog.open" :options="{ title: ruleDialog.editing ? __('Edit Rule') : __('New Rule') }">
      <template #body-content>
        <div class="space-y-3">
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Rule Name') }}</label>
            <input v-model="ruleDialog.data.rule_name" :disabled="ruleDialog.editing" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Type') }}</label>
              <select v-model="ruleDialog.data.task_type" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option value="">—</option>
                <option v-for="t in taskTypes.data || []" :key="t.name" :value="t.name">{{ t.type_name }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Level') }}</label>
              <input type="number" min="1" v-model.number="ruleDialog.data.level" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Past due (min)') }}</label>
              <input type="number" min="0" v-model.number="ruleDialog.data.after_minutes_past_due" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Action') }}</label>
              <select v-model="ruleDialog.data.action" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option value="notify">Notify</option>
                <option value="reassign">Reassign</option>
                <option value="flag">Flag</option>
              </select>
            </div>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Recipient User') }}</label>
            <select v-model="ruleDialog.data.recipient_user" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
              <option value="">—</option>
              <option v-for="u in ctx.data?.team_users || []" :key="u.name" :value="u.name">{{ u.full_name || u.name }}</option>
            </select>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Save')" @click="submitRule().then(close)" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, h, defineComponent, onMounted, watch } from 'vue'
import { Avatar, Badge, Button, Dialog, FeatherIcon, LoadingIndicator, createResource, toast } from 'frappe-ui'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import TaskDetailDrawer from '@/components/TaskDetailDrawer.vue'

// ── Constants ───────────────────────────────────────────────────────
const TABS = [
  { label: 'Inbox', view: 'inbox' },
  { label: 'Board', view: 'board' },
  { label: 'Calendar', view: 'calendar' },
  { label: 'Gantt', view: 'gantt' },
  { label: 'Workload', view: 'workload' },
  { label: 'Analytics', view: 'analytics' },
  { label: 'Templates', view: 'templates' },
  { label: 'Setup', view: 'setup' },
]

const PRIORITIES = ['Critical', 'High', 'Medium', 'Low']

const BOARD_COLUMNS = [
  { status: 'Backlog', label: 'Backlog' },
  { status: 'Todo', label: 'Todo', wip: 8 },
  { status: 'In Progress', label: 'In Progress', wip: 4 },
  { status: 'Blocked', label: 'Blocked' },
  { status: 'Done', label: 'Done' },
]

const SWIMLANE_OPTIONS = [
  { value: 'off', label: 'Off' },
  { value: 'assignee', label: 'Assignee' },
  { value: 'priority', label: 'Priority' },
  { value: 'type', label: 'Type' },
]

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

// ── Reactive state ──────────────────────────────────────────────────
const activeView = ref('inbox')
const viewControls = ref(null)
const inboxFilters = reactive({ scope: 'me', task_type: '', priority: '', sort_by: 'sla', search: '' })
const selected = ref([])
const swimlane = ref('off')
const drawer = reactive({ open: false, taskName: null })

const createDialog = ref(false)
const createForm = reactive({
  title: '',
  priority: 'Medium',
  task_type: '',
  assigned_to: '',
  due_date: '',
  recurring: false,
  recurrence_freq: 'Weekly',
  recurrence_interval: 1,
  recurrence_end_type: 'never',
  recurrence_end_date: '',
  recurrence_end_count: 10,
})

const applyDialog = reactive({ open: false, template: null, target_doctype: '', target_name: '', due_in_days: 7 })
const templateDialog = reactive({ open: false, editing: false, data: {}, checklistText: '', subtasksText: '' })
const typeDialog = reactive({ open: false, editing: false, data: { business_hours_only: 1 }, sla: { Critical: 240, High: 1440, Medium: 4320, Low: 10080 } })
const ruleDialog = reactive({ open: false, editing: false, data: {} })

const analyticsDays = ref('30')
const analyticsGroup = ref('task_type')

const today = new Date()
const anchorMonth = ref(new Date(today.getFullYear(), today.getMonth(), 1))

// ── Resources ───────────────────────────────────────────────────────
const ctx = createResource({ url: 'crm.api.tasks.get_context', auto: true })

const inbox = createResource({
  url: 'crm.api.tasks.get_inbox',
  params: () => ({
    scope: inboxFilters.scope,
    task_type: inboxFilters.task_type || null,
    priority: inboxFilters.priority || null,
    search: inboxFilters.search || null,
    sort_by: inboxFilters.sort_by,
  }),
  auto: true,
})

const board = createResource({
  url: 'crm.api.tasks.get_inbox',
  params: () => ({ scope: 'team', sort_by: 'updated' }),
  auto: false,
})

const calendar = createResource({
  url: 'crm.api.tasks.calendar_feed',
  params: () => ({
    start: calendarStart.value.toISOString().slice(0, 10),
    end: calendarEnd.value.toISOString().slice(0, 10),
  }),
  auto: false,
})

const gantt = createResource({ url: 'crm.api.tasks.gantt_feed', auto: false })
const workloadRes = createResource({ url: 'crm.api.tasks.workload', auto: false })
const analytics = createResource({
  url: 'crm.api.tasks.sla_analytics',
  params: () => ({ days: analyticsDays.value, group_by: analyticsGroup.value }),
  auto: false,
})
const templates = createResource({ url: 'crm.api.tasks.list_templates', auto: false })
const taskTypes = createResource({ url: 'crm.api.tasks.list_task_types', auto: true })
const rules = createResource({ url: 'crm.api.tasks.list_escalation_rules', auto: false })

watch(activeView, (v) => {
  if (v === 'board') board.reload()
  if (v === 'calendar') calendar.reload()
  if (v === 'gantt') gantt.reload()
  if (v === 'workload') workloadRes.reload()
  if (v === 'analytics') analytics.reload()
  if (v === 'templates') templates.reload()
  if (v === 'setup') { taskTypes.reload(); rules.reload() }
})

// ── Computed ────────────────────────────────────────────────────────
const inboxRows = computed(() => inbox.data || [])

const boardByStatus = computed(() => {
  const groups = {}
  for (const col of BOARD_COLUMNS) groups[col.status] = []
  for (const t of board.data || []) {
    if (groups[t.status]) groups[t.status].push(t)
  }
  return groups
})

const calendarStart = computed(() => {
  const first = new Date(anchorMonth.value.getFullYear(), anchorMonth.value.getMonth(), 1)
  const offset = (first.getDay() + 6) % 7
  const d = new Date(first); d.setDate(first.getDate() - offset)
  return d
})
const calendarEnd = computed(() => {
  const d = new Date(calendarStart.value); d.setDate(d.getDate() + 42); return d
})
const monthLabel = computed(() => anchorMonth.value.toLocaleString('en', { month: 'long', year: 'numeric' }))
const calendarCells = computed(() => {
  const cells = []
  const todayIso = new Date().toISOString().slice(0, 10)
  const tasksByDay = {}
  for (const t of calendar.data || []) {
    if (!t.due_date) continue
    const iso = String(t.due_date).slice(0, 10)
    ;(tasksByDay[iso] ||= []).push(t)
  }
  const start = calendarStart.value
  for (let i = 0; i < 42; i++) {
    const d = new Date(start); d.setDate(start.getDate() + i)
    const iso = d.toISOString().slice(0, 10)
    cells.push({
      iso,
      day: d.getDate(),
      inMonth: d.getMonth() === anchorMonth.value.getMonth(),
      isToday: iso === todayIso,
      tasks: tasksByDay[iso] || [],
    })
  }
  return cells
})

const ganttRows = computed(() => {
  const tasks = gantt.data?.tasks || []
  if (!tasks.length) return []
  const dates = tasks.map((t) => [t.start_date || t.creation, t.due_date]).flat().filter(Boolean).map((d) => new Date(d))
  const min = new Date(Math.min(...dates))
  const max = new Date(Math.max(...dates))
  const span = Math.max(1, (max - min) / (1000 * 60 * 60 * 24))
  const deps = gantt.data?.dependencies || []
  const blockedSet = new Set(deps.filter((d) => d.kind === 'blocked_by').map((d) => d.parent))
  return tasks.map((t) => {
    const s = new Date(t.start_date || t.creation)
    const e = new Date(t.due_date || t.creation)
    const left = Math.max(0, ((s - min) / (1000 * 60 * 60 * 24)) / span) * 100
    const width = Math.max(1, ((e - s) / (1000 * 60 * 60 * 24)) / span) * 100
    return { ...t, barLeft: left, barWidth: width, isCritical: blockedSet.has(t.name) || t.priority === 'Critical' }
  })
})

const ganttScale = computed(() => {
  const tasks = gantt.data?.tasks || []
  if (!tasks.length) return []
  const dates = tasks.map((t) => [t.start_date || t.creation, t.due_date]).flat().filter(Boolean).map((d) => new Date(d))
  const min = new Date(Math.min(...dates))
  const max = new Date(Math.max(...dates))
  const labels = []
  for (let i = 0; i < 5; i++) {
    const t = new Date(min.getTime() + ((max - min) * i) / 4)
    labels.push(t.toLocaleDateString('en', { day: '2-digit', month: 'short' }))
  }
  return labels
})

// ── Helpers ─────────────────────────────────────────────────────────
function formatMinutes(min) {
  if (!min) return '—'
  if (min < 60) return `${Math.round(min)}m`
  if (min < 60 * 24) return `${Math.round(min / 60)}h`
  return `${Math.round(min / (60 * 24))}d`
}

function formatRelativeDue(d) {
  if (!d) return ''
  const now = new Date()
  const target = new Date(d)
  const delta = Math.round((target - now) / (1000 * 60))
  if (delta < -1440) return `${Math.round(-delta / 1440)}d overdue`
  if (delta < 0) return `${Math.round(-delta / 60)}h overdue`
  if (delta < 60) return `in ${delta}m`
  if (delta < 1440) return `in ${Math.round(delta / 60)}h`
  return target.toLocaleDateString('en', { day: '2-digit', month: 'short' })
}

function priorityTheme(p) {
  return p === 'Critical' ? 'red' : p === 'High' ? 'orange' : p === 'Medium' ? 'blue' : 'gray'
}
function prioritySoft(p) {
  return p === 'Critical' ? '#fee2e2' : p === 'High' ? '#ffedd5' : p === 'Medium' ? '#dbeafe' : '#e5e7eb'
}
function priorityInk(p) {
  return p === 'Critical' ? '#991b1b' : p === 'High' ? '#9a3412' : p === 'Medium' ? '#1e3a8a' : '#374151'
}
function loadColor(open, capacity) {
  const r = open / Math.max(1, capacity)
  if (r > 1) return '#dc2626'
  if (r > 0.7) return '#d97706'
  return '#FF6600'
}

let searchTimer = null
function debouncedReload() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => inbox.reload(), 300)
}

function toggleSelect(name) {
  const i = selected.value.indexOf(name)
  if (i >= 0) selected.value.splice(i, 1)
  else selected.value.push(name)
}

// ── Actions ─────────────────────────────────────────────────────────
function openDrawer(name) {
  drawer.taskName = name
  drawer.open = true
}

function onTaskChanged() {
  inbox.reload()
  if (activeView.value === 'board') board.reload()
  if (activeView.value === 'workload') workloadRes.reload()
  ctx.reload()
}

async function quickComplete(t) {
  try {
    await createResource({ url: 'crm.api.tasks.transition', makeParams: () => ({ task: t.name, new_status: 'Done' }) }).submit()
    toast.success(__('Task completed'))
    onTaskChanged()
  } catch (e) {
    toast.error(__('Failed'))
  }
}

async function bulkComplete() {
  try {
    await createResource({ url: 'crm.api.tasks.bulk_complete', makeParams: () => ({ task_ids: JSON.stringify(selected.value) }) }).submit()
    toast.success(__('Completed ') + selected.value.length)
    selected.value = []
    onTaskChanged()
  } catch (e) {
    toast.error(__('Failed'))
  }
}

function openCreateDialog() {
  createForm.title = ''
  createForm.priority = 'Medium'
  createForm.task_type = ''
  createForm.assigned_to = ctx.data?.user || ''
  createForm.due_date = ''
  createForm.recurring = false
  createForm.recurrence_freq = 'Weekly'
  createForm.recurrence_interval = 1
  createForm.recurrence_end_type = 'never'
  createForm.recurrence_end_date = ''
  createForm.recurrence_end_count = 10
  createDialog.value = true
}

async function submitCreate() {
  try {
    const payload = { ...createForm }
    if (!payload.due_date) delete payload.due_date
    if (!payload.task_type) delete payload.task_type
    if (payload.recurring) {
      payload.recurrence_rule = {
        freq: payload.recurrence_freq,
        interval: payload.recurrence_interval,
        end_type: payload.recurrence_end_type,
        end_date: payload.recurrence_end_date || null,
        end_count: payload.recurrence_end_count || null,
      }
    }
    delete payload.recurring
    delete payload.recurrence_freq
    delete payload.recurrence_interval
    delete payload.recurrence_end_type
    delete payload.recurrence_end_date
    delete payload.recurrence_end_count
    await createResource({ url: 'crm.api.tasks.create_task', makeParams: () => ({ payload: JSON.stringify(payload) }) }).submit()
    toast.success(__('Task created'))
    onTaskChanged()
  } catch (e) {
    toast.error(__('Failed'))
  }
}

let dragName = null
function onDragStart(e, name) { dragName = name; e.dataTransfer.effectAllowed = 'move' }
async function onDropToColumn(_e, status) {
  if (!dragName) return
  try {
    await createResource({ url: 'crm.api.tasks.transition', makeParams: () => ({ task: dragName, new_status: status }) }).submit()
    toast.success(__('Moved to ') + status)
    board.reload()
  } catch (e) {
    if (status === 'Blocked') {
      const reason = prompt(__('Reason for blocking:'))
      if (reason) {
        try {
          await createResource({ url: 'crm.api.tasks.transition', makeParams: () => ({ task: dragName, new_status: status, blocked_reason: reason }) }).submit()
          toast.success(__('Blocked'))
          board.reload()
        } catch (_) { toast.error(__('Failed')) }
      }
    } else {
      toast.error(__('Failed'))
    }
  }
  dragName = null
}

function shiftMonth(d) {
  const m = new Date(anchorMonth.value)
  m.setMonth(m.getMonth() + d)
  anchorMonth.value = m
}

watch(anchorMonth, () => { if (activeView.value === 'calendar') calendar.reload() })

async function exportAnalytics() {
  try {
    const csv = await createResource({ url: 'crm.api.tasks.export_analytics_csv', makeParams: () => ({ days: analyticsDays.value, group_by: analyticsGroup.value }) }).submit()
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `sla-analytics-${new Date().toISOString().slice(0, 10)}.csv`; a.click()
    URL.revokeObjectURL(url)
  } catch (e) { toast.error(__('Export failed')) }
}

function openApplyDialog(tpl) {
  applyDialog.template = tpl
  applyDialog.target_doctype = ''
  applyDialog.target_name = ''
  applyDialog.due_in_days = 7
  applyDialog.open = true
}
async function submitApply() {
  try {
    await createResource({
      url: 'crm.api.tasks.apply_template',
      makeParams: () => ({
        template: applyDialog.template.name,
        target_doctype: applyDialog.target_doctype || null,
        target_name: applyDialog.target_name || null,
        due_in_days: applyDialog.due_in_days || 7,
      }),
    }).submit()
    toast.success(__('Template applied'))
    inbox.reload()
  } catch (e) { toast.error(__('Failed')) }
}

function openTemplateDialog(tpl) {
  templateDialog.editing = !!tpl
  templateDialog.data = tpl ? { template_name: tpl.template_name, default_type: tpl.default_type, default_priority: tpl.default_priority, description: tpl.description, active: tpl.active } : { template_name: '', default_priority: 'Medium', active: 1 }
  templateDialog.checklistText = (tpl?.checklist || []).map((c) => typeof c === 'string' ? c : c.label).join('\n')
  templateDialog.subtasksText = (tpl?.subtasks || []).map((s) => typeof s === 'string' ? s : s.title).join('\n')
  templateDialog.open = true
}
async function submitTemplate() {
  const payload = {
    ...templateDialog.data,
    checklist: templateDialog.checklistText.split('\n').map((l) => l.trim()).filter(Boolean),
    subtasks: templateDialog.subtasksText.split('\n').map((l) => l.trim()).filter(Boolean).map((title) => ({ title })),
  }
  try {
    await createResource({ url: 'crm.api.tasks.upsert_template', makeParams: () => ({ payload: JSON.stringify(payload) }) }).submit()
    toast.success(__('Template saved'))
    templates.reload()
  } catch (e) { toast.error(__('Failed')) }
}

function openTypeDialog(t) {
  typeDialog.editing = !!t
  typeDialog.data = t ? { type_name: t.type_name, business_hours_only: !!t.business_hours_only, color: t.color, active: t.active } : { type_name: '', business_hours_only: 1, active: 1 }
  typeDialog.sla = t?.sla_matrix ? { Critical: 240, High: 1440, Medium: 4320, Low: 10080, ...t.sla_matrix } : { Critical: 240, High: 1440, Medium: 4320, Low: 10080 }
  typeDialog.open = true
}
async function submitType() {
  const payload = { ...typeDialog.data, sla_matrix: typeDialog.sla, business_hours_only: typeDialog.data.business_hours_only ? 1 : 0 }
  try {
    await createResource({ url: 'crm.api.tasks.upsert_task_type', makeParams: () => ({ payload: JSON.stringify(payload) }) }).submit()
    toast.success(__('Type saved'))
    taskTypes.reload()
  } catch (e) { toast.error(__('Failed')) }
}

function openRuleDialog(r) {
  ruleDialog.editing = !!r
  ruleDialog.data = r ? { ...r } : { rule_name: '', task_type: '', level: 1, after_minutes_past_due: 0, action: 'notify', recipient_user: '' }
  ruleDialog.open = true
}
async function submitRule() {
  try {
    await createResource({ url: 'crm.api.tasks.upsert_escalation_rule', makeParams: () => ({ payload: JSON.stringify(ruleDialog.data) }) }).submit()
    toast.success(__('Rule saved'))
    rules.reload()
  } catch (e) { toast.error(__('Failed')) }
}

async function deleteTask(t) {
  if (!confirm(__('Delete task "%1"?', [t.title]))) return
  try {
    await createResource({ url: 'crm.api.tasks.delete_task', makeParams: () => ({ name: t.name }) }).submit()
    toast.success(__('Task canceled'))
    onTaskChanged()
  } catch (e) { toast.error(__('Failed')) }
}

async function deleteTemplate(tpl) {
  if (!confirm(__('Delete template "%1"?', [tpl.template_name]))) return
  try {
    await createResource({ url: 'crm.api.tasks.delete_template', makeParams: () => ({ name: tpl.name }) }).submit()
    toast.success(__('Template deleted'))
    templates.reload()
  } catch (e) { toast.error(__('Failed')) }
}

async function deleteTaskType(t) {
  if (!confirm(__('Delete type "%1"?', [t.type_name]))) return
  try {
    await createResource({ url: 'crm.api.tasks.delete_task_type', makeParams: () => ({ name: t.name }) }).submit()
    toast.success(__('Type deleted'))
    taskTypes.reload()
  } catch (e) { toast.error(__('Failed')) }
}

async function deleteEscalationRule(r) {
  if (!confirm(__('Delete rule "%1"?', [r.rule_name]))) return
  try {
    await createResource({ url: 'crm.api.tasks.delete_escalation_rule', makeParams: () => ({ name: r.name }) }).submit()
    toast.success(__('Rule deleted'))
    rules.reload()
  } catch (e) { toast.error(__('Failed')) }
}

async function maybeSeedTasks() {
  try {
    const r = await createResource({ url: 'crm.api.tasks.seed_task_sample_data' }).submit()
    if (r.created) {
      toast.success(__('Sample tasks created'))
      onTaskChanged()
    }
  } catch (e) {
    // ignore if module not ready
  }
}

// ── Inline components ───────────────────────────────────────────────
const KpiCard = defineComponent({
  name: 'KpiCard',
  props: ['label', 'value', 'icon', 'theme'],
  setup(props) {
    return () => h('div', { class: 'rounded-[12px] border border-outline-gray-2 bg-white px-3.5 py-3 shadow-sm' }, [
      h('div', { class: 'flex items-center justify-between' }, [
        h('span', { class: 'text-[11px] font-medium uppercase tracking-wide text-ink-gray-5' }, props.label),
        h(FeatherIcon, { name: props.icon || 'circle', class: 'h-3.5 w-3.5 text-ink-gray-4' }),
      ]),
      h('div', { class: 'mt-1.5 text-xl font-semibold leading-tight', style: props.theme === 'red' ? 'color:#dc2626' : props.theme === 'orange' ? 'color:#d97706' : props.theme === 'blue' ? 'color:#1d4ed8' : props.theme === 'teal' ? 'color:#FF6600' : 'color:#111827' }, props.value),
    ])
  },
})

const PriorityIcon = defineComponent({
  name: 'PriorityIcon',
  props: ['priority'],
  setup(props) {
    return () => {
      const map = { Critical: '#dc2626', High: '#d97706', Medium: '#1d4ed8', Low: '#9ca3af' }
      const label = { Critical: '!', High: '↑', Medium: '=', Low: '↓' }[props.priority] || '·'
      return h('span', {
        class: 'flex h-5 w-5 shrink-0 items-center justify-center rounded text-[10px] font-bold text-white',
        style: `background: ${map[props.priority] || '#9ca3af'}`,
        title: props.priority,
      }, label)
    }
  },
})

const SlaRibbon = defineComponent({
  name: 'SlaRibbon',
  props: ['task'],
  setup(props) {
    return () => {
      const t = props.task || {}
      const pct = Math.min(100, Math.max(0, t.sla_consumed_pct ?? 0))
      const colors = { OK: '#16a34a', Approaching: '#d97706', Breached: '#dc2626', Paused: '#6b7280', Completed: '#94a3b8' }
      const c = colors[t.sla_state] || '#6b7280'
      const remaining = formatRemaining(t.sla_remaining_seconds)
      return h('div', { class: 'min-w-0' }, [
        h('div', { class: 'flex items-center justify-between text-[11px] text-ink-gray-6' }, [
          h('span', { class: 'truncate pr-2', style: `color:${c}; font-weight:500` }, t.sla_state || 'OK'),
          h('span', { class: 'shrink-0' }, remaining),
        ]),
        h('div', { class: 'mt-1 h-1.5 w-full overflow-hidden rounded-full bg-surface-gray-2' }, [
          h('div', { class: 'h-full rounded-full transition-all', style: `width: ${pct}%; background: ${c}` }),
        ]),
      ])
    }
    function formatRemaining(s) {
      if (s == null) return ''
      if (s <= 0) return 'Breached'
      if (s < 3600) return `${Math.round(s / 60)}m left`
      if (s < 86400) return `${Math.round(s / 3600)}h left`
      return `${Math.round(s / 86400)}d left`
    }
  },
})

onMounted(() => {
  // Open ?task= from URL if provided
  const params = new URLSearchParams(window.location.search)
  const t = params.get('task')
  if (t) openDrawer(t)
  maybeSeedTasks()
})
</script>
