<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Committee Approval" />
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button variant="outline" size="sm" :label="__('Schedule Meeting')" @click="showScheduleModal = true">
            <template #prefix><FeatherIcon name="calendar" class="h-4 w-4" /></template>
          </Button>
          <Button variant="solid" size="sm" :label="__('New Committee')" @click="openNewCommittee">
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-5">
      <div class="flex gap-5 overflow-x-auto">
        <button
          v-for="tab in pageTabs"
          :key="tab.id"
          class="border-b-2 py-2.5 text-base transition-colors whitespace-nowrap"
          :class="activeTab === tab.id
            ? 'border-ink-gray-8 font-medium text-ink-gray-9'
            : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          @click="activeTab = tab.id"
        >
          {{ __(tab.label) }}
          <Badge v-if="tab.badge" :label="String(tab.badge)" theme="teal" variant="subtle" size="sm" class="ml-1" />
        </button>
      </div>
    </div>

    <!-- Body -->
    <div class="flex-1 overflow-auto bg-surface-gray-1 p-6">

      <!-- ───── TAB: Queue ───── -->
      <div v-if="activeTab === 'queue'">
        <!-- KPI Strip -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 mb-6">
          <div v-for="kpi in queueKPIs" :key="kpi.label" class="bg-surface-white rounded-[14px] p-4 border border-outline-gray-2">
            <p class="text-xs text-ink-gray-5 mb-1">{{ kpi.label }}</p>
            <p class="text-2xl font-bold" :class="kpi.color">{{ kpi.value }}</p>
            <p class="text-xs text-ink-gray-4 mt-1">{{ kpi.sub }}</p>
          </div>
        </div>

        <!-- Filters -->
        <div class="bg-surface-white rounded-[14px] border border-outline-gray-2 mb-4 p-4">
          <div class="flex gap-3 flex-wrap items-center">
            <input v-model="queueSearch" type="text" placeholder="Search applicant, facility..." class="flex-1 min-w-48 px-3 py-2 border border-outline-gray-2 rounded-lg text-sm" />
            <select v-model="queueFilterType" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm">
              <option value="">All Committees</option>
              <option value="CC1">CC-1 (≤ Rp 10B)</option>
              <option value="CC2">CC-2 (≤ Rp 50B)</option>
              <option value="CC3">CC-3 (&gt; Rp 50B)</option>
            </select>
            <select v-model="queueFilterStatus" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="in_session">In Session</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="deferred">Deferred</option>
            </select>
            <select v-model="queueFilterPriority" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm">
              <option value="">All Priority</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="normal">Normal</option>
            </select>
          </div>
        </div>

        <!-- Queue Table -->
        <div class="bg-surface-white rounded-[14px] border border-outline-gray-2 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm min-w-[800px]">
            <thead class="bg-surface-gray-1 border-b border-outline-gray-2">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-semibold text-ink-gray-5 uppercase">Case</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-ink-gray-5 uppercase">Applicant</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-ink-gray-5 uppercase">Facility</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-ink-gray-5 uppercase">Amount</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-ink-gray-5 uppercase">Committee</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-ink-gray-5 uppercase">SLA</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-ink-gray-5 uppercase">Priority</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-ink-gray-5 uppercase">Status</th>
                <th class="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1">
              <tr
                v-for="item in filteredQueue"
                :key="item.id"
                class="hover:bg-surface-gray-1 cursor-pointer"
                @click="openCaseDetail(item)"
              >
                <td class="px-4 py-3">
                  <span class="font-mono text-xs text-crm-teal font-semibold">{{ item.caseId }}</span>
                </td>
                <td class="px-4 py-3">
                  <div class="font-medium text-ink-gray-9">{{ item.applicant }}</div>
                  <div class="text-xs text-ink-gray-5">RM: {{ item.rm }}</div>
                </td>
                <td class="px-4 py-3 text-ink-gray-7">{{ item.facility }}</td>
                <td class="px-4 py-3 text-right font-semibold text-ink-gray-9">{{ item.amount }}</td>
                <td class="px-4 py-3">
                  <span class="px-2 py-0.5 rounded text-xs font-semibold bg-teal-50 text-crm-teal">{{ item.committee }}</span>
                </td>
                <td class="px-4 py-3">
                  <span :class="['text-xs font-medium', item.slaBreached ? 'text-red-600' : 'text-green-600']">
                    {{ item.slaDue }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span :class="priorityBadge(item.priority)">{{ item.priority }}</span>
                </td>
                <td class="px-4 py-3">
                  <span :class="statusBadge(item.status)">{{ statusLabel(item.status) }}</span>
                </td>
                <td class="px-4 py-3">
                  <button
                    v-if="item.status === 'pending'"
                    @click.stop="openVoting(item)"
                    class="px-3 py-1 bg-crm-teal text-white rounded text-xs font-medium hover:bg-crm-teal/90"
                  >
                    Vote
                  </button>
                  <button
                    v-else-if="item.status === 'in_session'"
                    @click.stop="openVoting(item)"
                    class="px-3 py-1 bg-amber-500 text-white rounded text-xs font-medium hover:bg-amber-600"
                  >
                    In Session
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

      <!-- ───── TAB: Meetings ───── -->
      <div v-if="activeTab === 'meetings'" class="space-y-4">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-base font-semibold text-ink-gray-9">Scheduled Committee Meetings</h2>
          <div class="flex gap-2">
            <button @click="meetingView = 'list'" :class="['px-3 py-1 rounded text-sm', meetingView==='list' ? 'bg-crm-teal text-white' : 'bg-surface-white border text-ink-gray-6']">List</button>
            <button @click="meetingView = 'calendar'" :class="['px-3 py-1 rounded text-sm', meetingView==='calendar' ? 'bg-crm-teal text-white' : 'bg-surface-white border text-ink-gray-6']">Calendar</button>
          </div>
        </div>

        <!-- Meeting Cards -->
        <div v-if="meetingView === 'list'" class="space-y-3">
          <div
            v-for="mtg in meetings"
            :key="mtg.id"
            class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-5"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-4">
                <div :class="['w-12 h-12 rounded-[14px] flex flex-col items-center justify-center text-white text-xs font-bold', mtg.color]">
                  <span class="text-lg leading-none">{{ mtg.day }}</span>
                  <span>{{ mtg.month }}</span>
                </div>
                <div>
                  <div class="font-semibold text-ink-gray-9 text-base">{{ mtg.title }}</div>
                  <div class="text-sm text-ink-gray-5 mt-0.5">{{ mtg.time }} · {{ mtg.location }}</div>
                  <div class="flex gap-2 mt-2 flex-wrap">
                    <span class="px-2 py-0.5 bg-surface-gray-2 rounded text-xs text-ink-gray-6">{{ mtg.committee }}</span>
                    <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">{{ mtg.cases }} cases</span>
                    <span class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">{{ mtg.members.length }}/{{ mtg.quorum }} quorum</span>
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span :class="mtgStatusBadge(mtg.status)">{{ mtg.status }}</span>
                <button
                  v-if="mtg.status === 'upcoming'"
                  @click="startSession(mtg)"
                  class="px-4 py-1.5 bg-crm-teal text-white rounded-lg text-sm font-medium hover:bg-crm-teal/90"
                >
                  Start Session
                </button>
                <button
                  v-else-if="mtg.status === 'in_progress'"
                  @click="activeTab = 'voting'"
                  class="px-4 py-1.5 bg-amber-500 text-white rounded-lg text-sm font-medium hover:bg-amber-600"
                >
                  Continue
                </button>
                <button
                  @click="startLiveMeeting(mtg.id)"
                  class="px-3 py-1.5 border border-crm-teal text-crm-teal rounded-lg text-sm hover:bg-teal-50"
                >
                  Go Live
                </button>
              </div>
            </div>

            <!-- Members -->
            <div class="mt-4 pt-4 border-t border-outline-gray-1">
              <p class="text-xs text-ink-gray-5 mb-2 uppercase tracking-wide font-semibold">Committee Members</p>
              <div class="flex gap-2 flex-wrap">
                <div
                  v-for="member in mtg.members"
                  :key="member.name"
                  class="flex items-center gap-2 px-3 py-1.5 bg-surface-gray-1 rounded-lg"
                >
                  <div :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white', avatarColor(member.name)]">
                    {{ member.name.charAt(0) }}
                  </div>
                  <span class="text-xs text-ink-gray-7">{{ member.name }}</span>
                  <span class="text-xs text-ink-gray-4">·</span>
                  <span class="text-xs text-ink-gray-5">{{ member.role }}</span>
                  <span v-if="member.confirmed" class="text-green-500 text-xs">✓</span>
                  <span v-else class="text-amber-500 text-xs">⏳</span>
                </div>
              </div>
            </div>

            <!-- Agenda Items -->
            <div class="mt-3">
              <p class="text-xs text-ink-gray-5 mb-2 uppercase tracking-wide font-semibold">Agenda Items ({{ mtg.agenda.length }})</p>
              <div class="space-y-1">
                <div v-for="(item, idx) in mtg.agenda" :key="idx" class="flex items-center gap-2 text-sm text-ink-gray-6">
                  <span class="w-5 h-5 rounded-full bg-teal-50 text-crm-teal text-xs flex items-center justify-center font-semibold">{{ idx + 1 }}</span>
                  {{ item }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Calendar View (simplified) -->
        <div v-else class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-6">
          <div class="text-center mb-4">
            <h3 class="text-base font-semibold text-ink-gray-9">May 2026</h3>
          </div>
          <div class="grid grid-cols-7 gap-1 text-center text-xs text-ink-gray-5 mb-2">
            <div v-for="d in ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']" :key="d">{{ d }}</div>
          </div>
          <div class="grid grid-cols-7 gap-1">
            <div v-for="cell in calendarCells" :key="cell.key" :class="['aspect-square rounded-lg flex flex-col items-center justify-center text-sm', cell.today ? 'bg-crm-teal text-white font-bold' : cell.hasEvent ? 'bg-teal-50 text-crm-teal font-semibold cursor-pointer hover:bg-teal-100' : 'text-ink-gray-5']">
              <span>{{ cell.day }}</span>
              <span v-if="cell.hasEvent" class="w-1.5 h-1.5 rounded-full bg-crm-teal mt-0.5" :class="cell.today ? 'bg-surface-white' : ''"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Voting ───── -->
      <div v-if="activeTab === 'voting'">
        <!-- Active Session Banner -->
        <div v-if="activeSession" class="bg-amber-50 border border-amber-200 rounded-[14px] p-4 mb-6 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="flex h-3 w-3 relative">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
            </span>
            <div>
              <p class="font-semibold text-amber-900">{{ activeSession.title }} — Live Session</p>
              <p class="text-sm text-amber-700">{{ activeSession.time }} · {{ activeSession.location }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4 text-sm text-amber-800">
            <span>Quorum: <strong>{{ activeSession.votedCount }}/{{ activeSession.members.length }}</strong></span>
            <span>Cases: <strong>{{ activeSessionCaseIdx + 1 }}/{{ activeSession.cases.length }}</strong></span>
            <button @click="activeSession = null" class="px-3 py-1 bg-amber-600 text-white rounded text-sm">End Session</button>
          </div>
        </div>

        <div v-if="!activeSession" class="text-center py-20">
          <div class="w-16 h-16 rounded-full bg-surface-gray-2 flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-ink-gray-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <p class="text-ink-gray-5 mb-4">No active session. Start a meeting from the Meetings tab.</p>
          <button @click="activeTab = 'meetings'" class="px-4 py-2 bg-crm-teal text-white rounded-lg text-sm">View Meetings</button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Case Navigator -->
          <div 
            v-if="!isMobile || !mobileShowDetails"
            class="md:col-span-1 bg-surface-white rounded-[14px] border border-outline-gray-2 overflow-hidden"
          >
            <div class="px-4 py-3 border-b border-outline-gray-2 bg-surface-gray-1">
              <p class="text-xs font-semibold text-ink-gray-6 uppercase">{{ __('Cases in Session') }}</p>
            </div>
            <div class="divide-y divide-outline-gray-1">
              <div
                v-for="(cas, idx) in activeSession.cases"
                :key="cas.id"
                @click="activeSessionCaseIdx = idx; if(isMobile) mobileShowDetails = true"
                :class="['p-4 cursor-pointer', activeSessionCaseIdx === idx ? 'bg-teal-50' : 'hover:bg-surface-gray-1']"
              >
                <div class="flex justify-between items-start">
                  <div>
                    <p class="font-mono text-xs text-crm-teal font-semibold">{{ cas.caseId }}</p>
                    <p class="text-sm font-medium text-ink-gray-9 mt-0.5">{{ cas.applicant }}</p>
                    <p class="text-xs text-ink-gray-5">{{ cas.amount }}</p>
                  </div>
                  <span v-if="cas.voted" class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">Voted</span>
                  <span v-else class="px-2 py-0.5 bg-surface-gray-2 text-ink-gray-5 rounded text-xs">Pending</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Voting Interface -->
          <div 
            v-if="!isMobile || mobileShowDetails"
            class="col-span-1 md:col-span-2 space-y-4"
          >
            <div v-if="currentCase" class="bg-surface-white rounded-[14px] border border-outline-gray-2">
              <!-- Case Header -->
              <div class="px-6 py-4 border-b border-outline-gray-2">
                <button 
                  v-if="isMobile" 
                  @click="mobileShowDetails = false"
                  class="inline-flex items-center gap-1.5 text-xs font-extrabold text-crm-teal hover:underline mb-3"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                  <span>{{ __('Back to Agenda Cases') }}</span>
                </button>
                <div class="flex justify-between items-start">
                  <div>
                    <span class="font-mono text-sm text-crm-teal font-semibold">{{ currentCase.caseId }}</span>
                    <h2 class="text-lg font-bold text-ink-gray-9 mt-1">{{ currentCase.applicant }}</h2>
                    <p class="text-sm text-ink-gray-5">{{ currentCase.facility }} · RM: {{ currentCase.rm }}</p>
                  </div>
                  <div class="text-right">
                    <p class="text-2xl font-bold text-ink-gray-9">{{ currentCase.amount }}</p>
                    <p class="text-xs text-ink-gray-5">Requested Amount</p>
                  </div>
                </div>
              </div>

              <!-- Case Summary -->
              <div class="px-6 py-4 grid grid-cols-4 gap-4 border-b border-outline-gray-1">
                <div v-for="metric in currentCase.metrics" :key="metric.label">
                  <p class="text-xs text-ink-gray-5">{{ metric.label }}</p>
                  <p class="font-semibold text-sm" :class="metric.color || 'text-ink-gray-9'">{{ metric.value }}</p>
                </div>
              </div>

              <!-- AI Recommendation -->
              <div class="px-6 py-3 bg-blue-50 flex items-start gap-3 border-b border-blue-100">
                <div class="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.362.362A3.001 3.001 0 0112 21a3 3 0 01-2.774-4.1l-.362-.362z" /></svg>
                </div>
                <div class="flex-1">
                  <p class="text-sm font-semibold text-blue-900">AI Recommendation: {{ currentCase.aiRec }}</p>
                  <p class="text-xs text-blue-700 mt-0.5">{{ currentCase.aiReason }}</p>
                </div>
                <span :class="['px-3 py-1 rounded-full text-xs font-bold', currentCase.aiScore >= 70 ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700']">Score {{ currentCase.aiScore }}</span>
              </div>

              <!-- Voting Panel -->
              <div class="px-6 py-5">
                <p class="text-sm font-semibold text-ink-gray-7 mb-4">Cast Your Vote</p>
                <div class="grid grid-cols-3 gap-3 mb-5">
                  <button
                    @click="castVote(currentCase, 'approve')"
                    :class="['py-3 rounded-[14px] border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'approve' ? 'border-green-500 bg-green-50 text-green-700' : 'border-outline-gray-2 hover:border-green-300 text-ink-gray-6']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                    Approve
                  </button>
                  <button
                    @click="castVote(currentCase, 'reject')"
                    :class="['py-3 rounded-[14px] border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'reject' ? 'border-red-500 bg-red-50 text-red-700' : 'border-outline-gray-2 hover:border-red-300 text-ink-gray-6']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    Reject
                  </button>
                  <button
                    @click="castVote(currentCase, 'defer')"
                    :class="['py-3 rounded-[14px] border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'defer' ? 'border-amber-500 bg-amber-50 text-amber-700' : 'border-outline-gray-2 hover:border-amber-300 text-ink-gray-6']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    Defer
                  </button>
                </div>

                <textarea v-model="currentCase.voteComment" rows="2" placeholder="Voting remarks (optional)..." class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm resize-none mb-4"></textarea>

                <!-- Vote Tally -->
                <div>
                  <p class="text-xs font-semibold text-ink-gray-6 uppercase mb-3">Current Tally</p>
                  <div class="space-y-2">
                    <div v-for="member in activeSession.members" :key="member.name" class="flex items-center gap-3">
                      <div :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0', avatarColor(member.name)]">
                        {{ member.name.charAt(0) }}
                      </div>
                      <span class="text-sm text-ink-gray-7 flex-1">{{ member.name }}</span>
                      <span class="text-xs text-ink-gray-5">{{ member.role }}</span>
                      <span v-if="member.vote" :class="['px-2 py-0.5 rounded text-xs font-semibold', member.vote === 'approve' ? 'bg-green-100 text-green-700' : member.vote === 'reject' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700']">
                        {{ member.vote }}
                      </span>
                      <span v-else class="px-2 py-0.5 bg-surface-gray-2 text-ink-gray-4 rounded text-xs">Pending</span>
                    </div>
                  </div>
                </div>

                <!-- Quorum Progress -->
                <div class="mt-4 p-3 bg-surface-gray-1 rounded-lg">
                  <div class="flex justify-between text-xs text-ink-gray-6 mb-1.5">
                    <span>Quorum Progress</span>
                    <span>{{ activeSession.votedCount }}/{{ activeSession.members.length }} voted · need {{ activeSession.quorum }}</span>
                  </div>
                  <div class="h-2 bg-surface-gray-2 rounded-full overflow-hidden">
                    <div class="h-full bg-teal-500 rounded-full transition-all" :style="{ width: (activeSession.votedCount / activeSession.members.length * 100) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Committees ───── -->
      <div v-if="activeTab === 'committees'" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="committee in committees"
            :key="committee.id"
            class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-5"
          >
            <div class="flex justify-between items-start mb-3">
              <div>
                <h3 class="font-bold text-ink-gray-9">{{ committee.name }}</h3>
                <p class="text-xs text-ink-gray-5 mt-0.5">{{ committee.code }}</p>
              </div>
              <span class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">Active</span>
            </div>
            <div class="text-sm text-ink-gray-6 mb-3">{{ committee.description }}</div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-ink-gray-5">Authority</span>
                <span class="font-medium text-ink-gray-9">{{ committee.authority }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-5">Quorum</span>
                <span class="font-medium text-ink-gray-9">{{ committee.quorum }} members</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-5">SLA</span>
                <span class="font-medium text-ink-gray-9">{{ committee.sla }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-5">Approval Rule</span>
                <span class="font-medium text-ink-gray-9">{{ committee.approvalRule }}</span>
              </div>
            </div>
            <div class="mt-4 pt-4 border-t border-outline-gray-1">
              <p class="text-xs text-ink-gray-5 mb-2">Members ({{ committee.members.length }})</p>
              <div class="flex -space-x-1">
                <div
                  v-for="m in committee.members.slice(0,5)"
                  :key="m"
                  :class="['w-7 h-7 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white', avatarColor(m)]"
                  :title="m"
                >
                  {{ m.charAt(0) }}
                </div>
                <div v-if="committee.members.length > 5" class="w-7 h-7 rounded-full border-2 border-white bg-surface-gray-2 flex items-center justify-center text-xs text-ink-gray-6 font-semibold">
                  +{{ committee.members.length - 5 }}
                </div>
              </div>
            </div>
            <div class="flex gap-2 mt-4">
              <button @click="openEditCommittee(committee)" class="flex-1 py-1.5 border border-outline-gray-2 rounded text-xs text-ink-gray-6 hover:bg-surface-gray-1">Edit</button>
              <button @click="openEditCommittee(committee, true)" class="flex-1 py-1.5 border border-crm-teal text-crm-teal rounded text-xs hover:bg-teal-50">Members</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Calendar ───── -->
      <div v-if="activeTab === 'calendar'" class="space-y-4">
        <div class="flex items-center gap-3">
          <select v-model="calendarFilter" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm">
            <option value="">All committees</option>
            <option value="CC-1">CC-1</option>
            <option value="CC-2">CC-2</option>
            <option value="CC-3">CC-3</option>
            <option value="RMC">RMC</option>
          </select>
          <input v-model="calendarMonth" type="month" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm" />
          <span class="text-sm text-ink-gray-5">{{ calendarEvents.length }} events</span>
        </div>
        <div class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-4">
          <div v-for="ev in calendarEvents" :key="ev.label + ev.date" class="flex items-center gap-3 border-b border-outline-gray-1 last:border-b-0 py-2">
            <div :class="['w-2 h-2 rounded-full', ev.color || 'bg-teal-500']"></div>
            <span class="text-sm font-mono text-ink-gray-5 w-28">{{ ev.date }}</span>
            <span class="text-xs px-2 py-0.5 rounded bg-surface-gray-2 text-ink-gray-6">{{ ev.committee }}</span>
            <span class="text-sm text-ink-gray-8">{{ ev.label }}</span>
          </div>
          <p v-if="!calendarEvents.length" class="text-sm text-ink-gray-5 text-center py-8">No events for current filter.</p>
        </div>
      </div>

      <!-- ───── TAB: Agenda ───── -->
      <div v-if="activeTab === 'agenda'" class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <label class="text-sm font-medium text-ink-gray-7">Meeting:</label>
            <select v-model="agendaMeetingId" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm">
              <option v-for="m in meetings" :key="m.id" :value="m.id">{{ m.title }}</option>
            </select>
          </div>
          <div class="flex gap-2">
            <button @click="addAgendaItem" class="px-3 py-1.5 border border-crm-teal text-crm-teal rounded text-sm">+ Add Item</button>
            <button @click="sendAgenda" class="px-3 py-1.5 bg-crm-teal text-white rounded text-sm">Send to Members</button>
          </div>
        </div>
        <div class="bg-surface-white rounded-[14px] border border-outline-gray-2 overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-surface-gray-1 border-b border-outline-gray-2">
              <tr>
                <th class="px-4 py-2 text-left text-xs uppercase font-semibold text-ink-gray-5">#</th>
                <th class="px-4 py-2 text-left text-xs uppercase font-semibold text-ink-gray-5">Case ID</th>
                <th class="px-4 py-2 text-left text-xs uppercase font-semibold text-ink-gray-5">Applicant</th>
                <th class="px-4 py-2 text-left text-xs uppercase font-semibold text-ink-gray-5">Time-box (min)</th>
                <th class="px-4 py-2 text-right text-xs uppercase font-semibold text-ink-gray-5">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(it, i) in filteredAgenda" :key="it.id" class="border-b border-outline-gray-1 last:border-b-0">
                <td class="px-4 py-2 text-ink-gray-5">{{ i + 1 }}</td>
                <td class="px-4 py-2"><input v-model="it.caseId" class="border border-outline-gray-2 rounded px-2 py-1 text-sm w-32 font-mono" /></td>
                <td class="px-4 py-2"><input v-model="it.applicant" class="border border-outline-gray-2 rounded px-2 py-1 text-sm w-64" /></td>
                <td class="px-4 py-2"><input v-model.number="it.timebox" type="number" min="1" class="border border-outline-gray-2 rounded px-2 py-1 text-sm w-20" /></td>
                <td class="px-4 py-2 text-right">
                  <button @click="moveAgendaItem(it, -1)" class="text-ink-gray-5 hover:text-ink-gray-7 px-1">↑</button>
                  <button @click="moveAgendaItem(it, 1)" class="text-ink-gray-5 hover:text-ink-gray-7 px-1">↓</button>
                  <button @click="removeAgendaItem(it)" class="text-red-500 hover:text-red-700 px-1">✕</button>
                </td>
              </tr>
              <tr v-if="!filteredAgenda.length">
                <td colspan="5" class="px-4 py-8 text-center text-ink-gray-5">No agenda items yet for this meeting.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ───── TAB: Live Meeting ───── -->
      <div v-if="activeTab === 'live'" class="space-y-4">
        <div v-if="!liveStarted" class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-6 text-center">
          <p class="text-ink-gray-7 mb-3">Start a live meeting to broadcast a real-time tally to attendees.</p>
          <select v-model="liveMeetingId" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm mr-2">
            <option v-for="m in meetings" :key="m.id" :value="m.id">{{ m.title }}</option>
          </select>
          <button @click="liveMeetingId && startLiveMeeting(liveMeetingId)" class="px-4 py-2 bg-crm-teal text-white rounded-lg text-sm font-medium">Start Live Mode</button>
        </div>
        <div v-else class="bg-gray-900 text-white rounded-[18px] p-8">
          <div class="flex items-center justify-between mb-6">
            <div>
              <p class="text-xs uppercase tracking-widest text-ink-gray-4">LIVE · {{ liveCurrentMeeting?.title }}</p>
              <p class="text-2xl font-bold mt-1">{{ liveCurrentAgenda?.caseId }} — {{ liveCurrentAgenda?.applicant }}</p>
            </div>
            <button @click="liveStarted = false" class="px-3 py-1.5 border border-white/30 rounded text-sm">End Session</button>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-green-700 rounded-[14px] p-6 text-center">
              <p class="text-xs uppercase">Approve</p>
              <p class="text-5xl font-bold mt-2">{{ liveTally.approve }}</p>
              <button @click="liveVote('approve')" class="mt-3 px-3 py-1 bg-green-900 rounded text-sm">+1</button>
            </div>
            <div class="bg-red-700 rounded-[14px] p-6 text-center">
              <p class="text-xs uppercase">Reject</p>
              <p class="text-5xl font-bold mt-2">{{ liveTally.reject }}</p>
              <button @click="liveVote('reject')" class="mt-3 px-3 py-1 bg-red-900 rounded text-sm">+1</button>
            </div>
            <div class="bg-amber-700 rounded-[14px] p-6 text-center">
              <p class="text-xs uppercase">Defer</p>
              <p class="text-5xl font-bold mt-2">{{ liveTally.defer }}</p>
              <button @click="liveVote('defer')" class="mt-3 px-3 py-1 bg-amber-900 rounded text-sm">+1</button>
            </div>
            <div class="bg-surface-gray-2 rounded-[14px] p-6 text-center">
              <p class="text-xs uppercase">Abstain</p>
              <p class="text-5xl font-bold mt-2">{{ liveTally.abstain }}</p>
              <button @click="liveVote('abstain')" class="mt-3 px-3 py-1 bg-gray-900 rounded text-sm">+1</button>
            </div>
          </div>
          <div class="bg-surface-white/5 rounded-[14px] p-4">
            <p class="text-xs uppercase tracking-widest text-ink-gray-4 mb-2">Members Present</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="m in (liveCurrentMeeting?.members || [])" :key="m.name" class="px-3 py-1 rounded-full text-xs" :class="m.confirmed ? 'bg-green-700' : 'bg-surface-gray-2'">
                {{ m.name }}
              </span>
            </div>
          </div>
          <div class="mt-4 flex justify-end">
            <button @click="nextLiveItem" class="px-4 py-2 bg-crm-teal rounded text-sm font-medium">Next Item →</button>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Analytics ───── -->
      <div v-if="activeTab === 'analytics'">
        <!-- KPI Row -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div v-for="kpi in analyticsKPIs" :key="kpi.label" class="bg-surface-white rounded-[14px] p-4 border border-outline-gray-2">
            <p class="text-xs text-ink-gray-5 mb-1">{{ kpi.label }}</p>
            <p class="text-2xl font-bold text-ink-gray-9">{{ kpi.value }}</p>
            <p :class="['text-xs mt-1', kpi.trend >= 0 ? 'text-green-600' : 'text-red-600']">{{ kpi.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(kpi.trend) }}% vs last month</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Approval Rate by Committee -->
          <div class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-5">
            <h3 class="text-sm font-semibold text-ink-gray-7 mb-4">Approval Rate by Committee</h3>
            <div class="space-y-4">
              <div v-for="row in approvalByCommittee" :key="row.name">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-ink-gray-7">{{ row.name }}</span>
                  <span class="font-semibold text-ink-gray-9">{{ row.rate }}%</span>
                </div>
                <div class="flex gap-1 h-3 rounded-full overflow-hidden">
                  <div class="bg-green-500 rounded-full" :style="{ width: row.approvedPct + '%' }"></div>
                  <div class="bg-red-400" :style="{ width: row.rejectedPct + '%' }"></div>
                  <div class="bg-amber-400" :style="{ width: row.deferredPct + '%' }"></div>
                </div>
                <div class="flex gap-4 text-xs text-ink-gray-4 mt-1">
                  <span>✓ {{ row.approved }}</span>
                  <span>✗ {{ row.rejected }}</span>
                  <span>⏳ {{ row.deferred }}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-4 mt-4 text-xs text-ink-gray-5">
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-green-500 inline-block"></span>Approved</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-400 inline-block"></span>Rejected</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-400 inline-block"></span>Deferred</span>
            </div>
          </div>

          <!-- TAT Distribution -->
          <div class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-5">
            <h3 class="text-sm font-semibold text-ink-gray-7 mb-4">TAT Distribution (Days)</h3>
            <div class="space-y-3">
              <div v-for="bucket in tatBuckets" :key="bucket.label" class="flex items-center gap-3">
                <span class="text-xs text-ink-gray-5 w-20">{{ bucket.label }}</span>
                <div class="flex-1 h-6 bg-surface-gray-2 rounded overflow-hidden">
                  <div :class="['h-full rounded flex items-center px-2 text-xs text-white font-medium', bucket.color]" :style="{ width: (bucket.count / 50 * 100) + '%' }">
                    {{ bucket.count }}
                  </div>
                </div>
                <span class="text-xs text-ink-gray-4 w-12 text-right">{{ bucket.pct }}%</span>
              </div>
            </div>
          </div>

          <!-- Member Participation -->
          <div class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-5">
            <h3 class="text-sm font-semibold text-ink-gray-7 mb-4">Member Participation</h3>
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-outline-gray-1">
                  <th class="text-left pb-2 text-xs text-ink-gray-5">Member</th>
                  <th class="text-center pb-2 text-xs text-ink-gray-5">Meetings</th>
                  <th class="text-center pb-2 text-xs text-ink-gray-5">Attendance</th>
                  <th class="text-center pb-2 text-xs text-ink-gray-5">Votes</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1">
                <tr v-for="member in memberParticipation" :key="member.name">
                  <td class="py-2">
                    <div class="flex items-center gap-2">
                      <div :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white', avatarColor(member.name)]">{{ member.name.charAt(0) }}</div>
                      <span class="text-ink-gray-7">{{ member.name }}</span>
                    </div>
                  </td>
                  <td class="py-2 text-center text-ink-gray-6">{{ member.meetings }}</td>
                  <td class="py-2 text-center">
                    <span :class="['font-semibold', member.attendance >= 90 ? 'text-green-600' : member.attendance >= 70 ? 'text-amber-600' : 'text-red-600']">{{ member.attendance }}%</span>
                  </td>
                  <td class="py-2 text-center text-ink-gray-6">{{ member.votes }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Monthly Volume -->
          <div class="bg-surface-white rounded-[14px] border border-outline-gray-2 p-5">
            <h3 class="text-sm font-semibold text-ink-gray-7 mb-4">Monthly Case Volume</h3>
            <div class="flex items-end gap-2 h-32">
              <div v-for="bar in monthlyVolume" :key="bar.month" class="flex-1 flex flex-col items-center gap-1">
                <span class="text-xs text-ink-gray-5">{{ bar.count }}</span>
                <div class="w-full bg-teal-500 rounded-t" :style="{ height: (bar.count / 25 * 100) + '%' }"></div>
                <span class="text-xs text-ink-gray-4">{{ bar.month }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ───── MODALS ───── -->

    <!-- Schedule Meeting Modal -->
    <div v-if="showScheduleModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showScheduleModal = false">
      <div class="bg-surface-white rounded-[18px] w-full max-w-lg p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-5">
          <h2 class="text-lg font-bold text-ink-gray-9">Schedule Committee Meeting</h2>
          <button @click="showScheduleModal = false" class="text-ink-gray-4 hover:text-ink-gray-6">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Committee</label>
            <select class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm">
              <option>Credit Committee Level 1 (CC-1)</option>
              <option>Credit Committee Level 2 (CC-2)</option>
              <option>Risk Management Committee (RMC)</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">Date</label>
              <input type="date" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">Time</label>
              <input type="time" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Location / Room</label>
            <input type="text" placeholder="e.g. BNI HQ - Board Room 3" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Agenda Notes</label>
            <textarea rows="3" placeholder="Meeting agenda..." class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm resize-none"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showScheduleModal = false" class="flex-1 py-2 border border-outline-gray-2 rounded-lg text-sm text-ink-gray-7 hover:bg-surface-gray-1">Cancel</button>
          <button @click="saveMeeting" class="flex-1 py-2 bg-crm-teal text-white rounded-lg text-sm font-medium hover:bg-crm-teal/90">Schedule Meeting</button>
        </div>
      </div>
    </div>

    <!-- Committee Setup Modal -->
    <div v-if="showSetupModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="closeSetupModal">
      <div class="bg-surface-white rounded-[18px] w-full max-w-lg p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-5">
          <h2 class="text-lg font-bold text-ink-gray-9">{{ committeeForm.id ? 'Edit Committee' : 'Create New Committee' }}</h2>
          <button @click="closeSetupModal" class="text-ink-gray-4 hover:text-ink-gray-6">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Committee Name</label>
            <input v-model="committeeForm.name" type="text" placeholder="e.g. Credit Committee Level 3" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Description</label>
            <textarea v-model="committeeForm.description" rows="2" placeholder="Purpose and remit of the committee…" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">Code</label>
              <input v-model="committeeForm.code" type="text" placeholder="CC-3" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">Quorum %</label>
              <input v-model.number="committeeForm.quorumPct" type="number" min="1" max="100" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Credit Authority</label>
            <input v-model="committeeForm.authority" type="text" placeholder="e.g. > Rp 50 Billion" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">Majority Type</label>
              <select v-model="committeeForm.approvalRule" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm">
                <option>Simple Majority (&gt;50%)</option>
                <option>Supermajority (≥2/3)</option>
                <option>Unanimous</option>
                <option>Chair Casts Deciding Vote</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">SLA (days)</label>
              <input v-model.number="committeeForm.slaDays" type="number" min="1" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Members</label>
            <div class="space-y-2">
              <div v-for="(m, idx) in committeeForm.members" :key="idx" class="flex gap-2 items-center">
                <input v-model="m.name" type="text" placeholder="Member name" class="flex-1 border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
                <select v-model="m.role" class="w-32 border border-outline-gray-2 rounded-lg px-2 py-2 text-sm">
                  <option>Chair</option>
                  <option>Member</option>
                  <option>Risk Officer</option>
                  <option>Compliance</option>
                  <option>Legal</option>
                  <option>Observer</option>
                </select>
                <input v-model.number="m.weight" type="number" min="0" step="0.1" placeholder="Wt" class="w-16 border border-outline-gray-2 rounded-lg px-2 py-2 text-sm" />
                <button type="button" @click="removeMember(idx)" class="text-red-500 hover:text-red-700 text-sm px-2">✕</button>
              </div>
              <button type="button" @click="addMember" class="text-crm-teal hover:text-crm-teal text-sm font-medium">+ Add Member</button>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input id="chairTieBreak" v-model="committeeForm.chairTieBreak" type="checkbox" class="w-4 h-4" />
            <label for="chairTieBreak" class="text-sm text-ink-gray-7">Chairman has tie-break vote</label>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="closeSetupModal" class="flex-1 py-2 border border-outline-gray-2 rounded-lg text-sm text-ink-gray-7 hover:bg-surface-gray-1">Cancel</button>
          <button @click="saveCommittee" class="flex-1 py-2 bg-crm-teal text-white rounded-lg text-sm font-medium hover:bg-crm-teal/90">{{ committeeForm.id ? 'Save Changes' : 'Create Committee' }}</button>
        </div>
      </div>
    </div>

    <!-- Case Detail Modal -->
    <div v-if="showCaseModal && selectedCase" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCaseModal = false">
      <div class="bg-surface-white rounded-[18px] w-full max-w-2xl p-6 shadow-2xl max-h-[85vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-5">
          <div>
            <span class="font-mono text-sm text-crm-teal font-semibold">{{ selectedCase.caseId }}</span>
            <h2 class="text-lg font-bold text-ink-gray-9">{{ selectedCase.applicant }}</h2>
          </div>
          <button @click="showCaseModal = false" class="text-ink-gray-4 hover:text-ink-gray-6">✕</button>
        </div>
        <div class="grid grid-cols-2 gap-4 mb-5">
          <div v-for="f in caseDetailFields(selectedCase)" :key="f.label" class="bg-surface-gray-1 rounded-lg p-3">
            <p class="text-xs text-ink-gray-5 mb-0.5">{{ f.label }}</p>
            <p class="text-sm font-semibold text-ink-gray-9">{{ f.value }}</p>
          </div>
        </div>
        <div class="mb-4">
          <p class="text-xs font-semibold text-ink-gray-6 uppercase mb-2">Supporting Documents</p>
          <div class="space-y-1">
            <div v-for="doc in selectedCase.documents" :key="doc" class="flex items-center gap-2 text-sm text-blue-600 cursor-pointer hover:underline">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              {{ doc }}
            </div>
          </div>
        </div>
        <div v-if="selectedCase.overridden" class="mb-3 rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-700">
          <p class="font-semibold">Decision overridden</p>
          <p>Was: {{ selectedCase.overridden.previous }} · By: {{ selectedCase.overridden.by }}</p>
          <p>Reason: {{ selectedCase.overridden.reason }}</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button v-if="selectedCase.status === 'pending'" @click="showCaseModal = false; openVoting(selectedCase)" class="flex-1 py-2 bg-crm-teal text-white rounded-lg text-sm font-medium">Open Voting</button>
          <button v-if="selectedCase.status === 'pending'" @click="startCircularApproval(selectedCase)" class="px-3 py-2 border border-crm-teal text-crm-teal rounded-lg text-sm">Circular Approval</button>
          <button v-if="['approved', 'rejected', 'deferred'].includes(selectedCase.status)" @click="generateMinutes(selectedCase)" class="px-3 py-2 border border-outline-gray-2 text-ink-gray-7 rounded-lg text-sm">Generate Minutes</button>
          <button v-if="['approved', 'rejected'].includes(selectedCase.status) && canOverride" @click="overrideDecision(selectedCase)" class="px-3 py-2 border border-red-300 text-red-700 rounded-lg text-sm">Override Decision</button>
          <button @click="showCaseModal = false" class="px-4 py-2 border border-outline-gray-2 rounded-lg text-sm text-ink-gray-6">Close</button>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <div v-if="toast" class="fixed bottom-6 right-6 bg-green-600 text-white px-5 py-3 rounded-[14px] shadow-lg text-sm font-medium z-50 flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
      {{ toast }}
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import { Badge, Button, FeatherIcon, usePageMeta } from 'frappe-ui'
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'

const viewControls = ref(null)

usePageMeta(() => ({ title: __('Committee Approval') }))

const activeTab = ref('queue')
const queueSearch = ref('')
const queueFilterType = ref('')
const queueFilterStatus = ref('')
const queueFilterPriority = ref('')
const meetingView = ref('list')
const activeSession = ref(null)
const activeSessionCaseIdx = ref(0)
const showScheduleModal = ref(false)
const showSetupModal = ref(false)
const showCaseModal = ref(false)
const selectedCase = ref(null)
const toast = ref('')

const isMobile = ref(false)
const mobileShowDetails = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

const emptyCommitteeForm = () => ({
  id: null,
  name: '',
  code: '',
  description: '',
  authority: '',
  quorumPct: 60,
  slaDays: 5,
  approvalRule: 'Simple Majority (>50%)',
  chairTieBreak: false,
  members: [{ name: '', role: 'Chair', weight: 1 }],
})
const committeeForm = ref(emptyCommitteeForm())

function openNewCommittee() {
  committeeForm.value = emptyCommitteeForm()
  showSetupModal.value = true
}
function openEditCommittee(c) {
  committeeForm.value = {
    id: c.id,
    name: c.name,
    code: c.code,
    description: c.description || '',
    authority: c.authority || '',
    quorumPct: c.quorumPct || Math.round(((c.quorum || 3) / Math.max(c.members?.length || 1, 1)) * 100),
    slaDays: parseInt(String(c.sla || '5').match(/\d+/)?.[0] || '5'),
    approvalRule: c.approvalRule || 'Simple Majority (>50%)',
    chairTieBreak: !!c.chairTieBreak,
    members: (c.members || []).map((m) => (typeof m === 'string' ? { name: m, role: 'Member', weight: 1 } : { ...m })),
  }
  if (!committeeForm.value.members.length) committeeForm.value.members.push({ name: '', role: 'Member', weight: 1 })
  showSetupModal.value = true
}
function addMember() {
  committeeForm.value.members.push({ name: '', role: 'Member', weight: 1 })
}
function removeMember(idx) {
  committeeForm.value.members.splice(idx, 1)
  if (!committeeForm.value.members.length) addMember()
}
function closeSetupModal() {
  showSetupModal.value = false
  committeeForm.value = emptyCommitteeForm()
}

const pageTabs = [
  { id: 'queue', label: 'Case Queue', badge: 8 },
  { id: 'meetings', label: 'Meetings' },
  { id: 'voting', label: 'Voting' },
  { id: 'calendar', label: 'Calendar' },
  { id: 'agenda', label: 'Agenda' },
  { id: 'live', label: 'Live Mode' },
  { id: 'committees', label: 'Committees' },
  { id: 'analytics', label: 'Analytics' },
]

const calendarFilter = ref('')
const calendarMonth = ref(new Date().toISOString().slice(0, 7))
const calendarEvents = computed(() => {
  const events = []
  meetings.value.forEach((m) => {
    events.push({ kind: 'meeting', committee: m.committee, label: m.title, date: monthDay(m.month, m.day), color: m.color })
  })
  queueItems.value.forEach((q) => {
    if (!q.slaBreached && /\d+/.test(String(q.slaDue))) {
      const days = parseInt(String(q.slaDue).match(/\d+/)?.[0] || '0')
      const d = new Date()
      d.setDate(d.getDate() + days)
      events.push({ kind: 'sla', committee: q.committee, label: `SLA Due · ${q.caseId}`, date: d.toISOString().slice(0, 10), color: 'bg-amber-500' })
    }
  })
  return events.filter((e) => !calendarFilter.value || e.committee === calendarFilter.value)
})

function monthDay(monthAbbr, day) {
  const months = { JAN: 0, FEB: 1, MAR: 2, APR: 3, MAY: 4, JUN: 5, JUL: 6, AUG: 7, SEP: 8, OCT: 9, NOV: 10, DEC: 11 }
  const year = new Date().getFullYear()
  const d = new Date(year, months[String(monthAbbr).toUpperCase()] ?? 0, Number(day) || 1)
  return d.toISOString().slice(0, 10)
}

const agendaItems = ref([
  { id: 1, meetingId: 1, order: 1, caseId: 'CC-2026-0187', applicant: 'PT Maju Bersama Tbk', timebox: 20, attachments: [] },
  { id: 2, meetingId: 1, order: 2, caseId: 'CC-2026-0186', applicant: 'CV Sukses Makmur', timebox: 15, attachments: [] },
  { id: 3, meetingId: 1, order: 3, caseId: 'CC-2026-0184', applicant: 'PT Agri Sejahtera', timebox: 20, attachments: [] },
])
const agendaMeetingId = ref(1)
const filteredAgenda = computed(() =>
  agendaItems.value.filter((a) => a.meetingId === agendaMeetingId.value).sort((a, b) => a.order - b.order),
)

function addAgendaItem() {
  const order = filteredAgenda.value.length + 1
  agendaItems.value.push({ id: Date.now(), meetingId: agendaMeetingId.value, order, caseId: '', applicant: '', timebox: 15, attachments: [] })
}

function removeAgendaItem(it) {
  agendaItems.value = agendaItems.value.filter((a) => a.id !== it.id)
}

function moveAgendaItem(it, dir) {
  const list = filteredAgenda.value
  const idx = list.findIndex((a) => a.id === it.id)
  const targetIdx = idx + dir
  if (targetIdx < 0 || targetIdx >= list.length) return
  const other = list[targetIdx]
  ;[it.order, other.order] = [other.order, it.order]
}

function sendAgenda() {
  showToast('Agenda sent to members')
}

const liveMeetingId = ref(null)
const liveAgendaIdx = ref(0)
const livePresence = ref({})
const liveTally = reactive({ approve: 0, reject: 0, defer: 0, abstain: 0 })
const liveStarted = ref(false)

function startLiveMeeting(meetingId) {
  liveMeetingId.value = meetingId
  liveAgendaIdx.value = 0
  Object.assign(liveTally, { approve: 0, reject: 0, defer: 0, abstain: 0 })
  livePresence.value = {}
  liveStarted.value = true
  activeTab.value = 'live'
}

function liveVote(action) {
  liveTally[action] = (liveTally[action] || 0) + 1
}

function nextLiveItem() {
  const items = agendaItems.value.filter((a) => a.meetingId === liveMeetingId.value)
  if (liveAgendaIdx.value < items.length - 1) {
    liveAgendaIdx.value++
    Object.assign(liveTally, { approve: 0, reject: 0, defer: 0, abstain: 0 })
  } else {
    showToast('Live meeting completed')
    liveStarted.value = false
  }
}

const liveCurrentMeeting = computed(() => meetings.value.find((m) => m.id === liveMeetingId.value))
const liveCurrentAgenda = computed(() => {
  const items = agendaItems.value.filter((a) => a.meetingId === liveMeetingId.value)
  return items[liveAgendaIdx.value]
})

const userRoles = ref(['Committee Member', 'Committee Override'])
const canOverride = computed(() => userRoles.value.includes('Committee Override'))

function startCircularApproval(cas) {
  cas.circular = true
  cas.circularVotes = (cas.circularVotes || [])
  showToast(`Circular ballot dispatched for ${cas.caseId}`)
}

function overrideDecision(cas) {
  if (!canOverride.value) {
    showToast('You lack Committee Override role')
    return
  }
  const reason = window.prompt(`Override decision for ${cas.caseId}. Reason (mandatory):`)
  if (!reason || !reason.trim()) {
    showToast('Override cancelled — reason required')
    return
  }
  cas.overridden = { previous: cas.status, by: 'Current User', reason, at: new Date().toISOString() }
  cas.status = cas.status === 'approved' ? 'rejected' : 'approved'
  showToast(`${cas.caseId} overridden`)
}

function generateMinutes(cas) {
  const text = [
    `MINUTES OF DECISION`,
    `Case: ${cas.caseId}`,
    `Applicant: ${cas.applicant}`,
    `Facility: ${cas.facility}`,
    `Committee: ${cas.committee}`,
    `Decision: ${cas.status.toUpperCase()}`,
    cas.overridden ? `Override: by ${cas.overridden.by} — ${cas.overridden.reason}` : '',
    ``,
    `Members present: (from agenda)`,
    `Votes recorded: see attached voting log`,
    ``,
    `Generated ${new Date().toISOString()}`,
  ].filter(Boolean).join('\n')
  const blob = new Blob([text], { type: 'application/pdf' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `minutes-${cas.caseId}.pdf`
  link.click()
  URL.revokeObjectURL(link.href)
  showToast(`Minutes generated for ${cas.caseId}`)
}

const queueKPIs = [
  { label: 'Pending Cases', value: '8', sub: 'Awaiting committee', color: 'text-amber-600' },
  { label: 'In Session', value: '3', sub: 'Active deliberation', color: 'text-crm-teal' },
  { label: 'Approved MTD', value: '24', sub: 'This month', color: 'text-green-600' },
  { label: 'Rejected MTD', value: '6', sub: 'This month', color: 'text-red-600' },
  { label: 'Avg TAT', value: '3.2d', sub: 'vs SLA 5 days', color: 'text-blue-600' },
]

const queueItems = ref([
  { id: 1, caseId: 'CC-2026-0187', applicant: 'PT Maju Bersama Tbk', facility: 'Kredit Modal Kerja', amount: 'Rp 8.5B', committee: 'CC-1', slaDue: 'Due in 2d', slaBreached: false, priority: 'urgent', status: 'pending', rm: 'Budi Santoso', myVote: null, voteComment: '', voted: false, aiScore: 78, aiRec: 'Approve with Conditions', aiReason: 'Strong cash flow ratio (1.8x), minor covenant concern on DSCR.', metrics: [{ label: 'LTV', value: '62%' }, { label: 'DSCR', value: '1.82x' }, { label: 'Credit Score', value: '720', color: 'text-green-600' }, { label: 'Industry Risk', value: 'Medium', color: 'text-amber-600' }], documents: ['Credit Application Form.pdf', 'Financial Statements 2025.pdf', 'Collateral Appraisal.pdf', 'BI Checking Report.pdf'] },
  { id: 2, caseId: 'CC-2026-0186', applicant: 'CV Sukses Makmur', facility: 'Kredit Investasi', amount: 'Rp 3.2B', committee: 'CC-1', slaDue: 'Due in 1d', slaBreached: false, priority: 'urgent', status: 'in_session', rm: 'Sari Dewi', myVote: null, voteComment: '', voted: false, aiScore: 65, aiRec: 'Approve with Conditions', aiReason: 'Moderate risk. Owner guarantee required.', metrics: [{ label: 'LTV', value: '70%' }, { label: 'DSCR', value: '1.45x' }, { label: 'Credit Score', value: '685', color: 'text-amber-600' }, { label: 'Industry Risk', value: 'Medium' }], documents: ['Credit Application Form.pdf', 'Business Plan 2025.pdf', 'SKMHT Notarial Deed.pdf'] },
  { id: 3, caseId: 'CC-2026-0185', applicant: 'PT Teknologi Nusantara', facility: 'Term Loan', amount: 'Rp 28B', committee: 'CC-2', slaDue: 'Due in 4d', slaBreached: false, priority: 'high', status: 'pending', rm: 'Andi Wahyudi', myVote: null, voteComment: '', voted: false, aiScore: 82, aiRec: 'Approve', aiReason: 'Excellent financials, low NPL risk sector.', metrics: [{ label: 'LTV', value: '55%' }, { label: 'DSCR', value: '2.1x' }, { label: 'Credit Score', value: '755', color: 'text-green-600' }, { label: 'Industry Risk', value: 'Low', color: 'text-green-600' }], documents: ['Credit Application Form.pdf', 'Financial Statements 2023-2025.pdf', 'Collateral Appraisal.pdf'] },
  { id: 4, caseId: 'CC-2026-0184', applicant: 'PT Agri Sejahtera', facility: 'KUR Pertanian', amount: 'Rp 500M', committee: 'CC-1', slaDue: 'BREACHED', slaBreached: true, priority: 'urgent', status: 'pending', rm: 'Rina Kartika', myVote: null, voteComment: '', voted: false, aiScore: 55, aiRec: 'Reject', aiReason: 'Multiple outstanding obligations. Debt burden ratio exceeds threshold.', metrics: [{ label: 'LTV', value: '85%', color: 'text-red-600' }, { label: 'DSCR', value: '0.92x', color: 'text-red-600' }, { label: 'Credit Score', value: '610', color: 'text-red-600' }, { label: 'Industry Risk', value: 'High', color: 'text-red-600' }], documents: ['Credit Application Form.pdf', 'Income Statement.pdf'] },
  { id: 5, caseId: 'CC-2026-0183', applicant: 'PT Bangun Graha Mandiri', facility: 'Property Financing', amount: 'Rp 65B', committee: 'CC-3', slaDue: 'Due in 7d', slaBreached: false, priority: 'high', status: 'pending', rm: 'Hendra Gunawan', myVote: null, voteComment: '', voted: false, aiScore: 75, aiRec: 'Approve with Conditions', aiReason: 'Large exposure requires board-level authorization. Adequate collateral coverage.', metrics: [{ label: 'LTV', value: '68%' }, { label: 'DSCR', value: '1.65x' }, { label: 'Credit Score', value: '730', color: 'text-green-600' }, { label: 'Industry Risk', value: 'Medium' }], documents: ['Credit Application Form.pdf', 'AMDAL Certificate.pdf', 'Title Certificate.pdf', 'Appraisal Report.pdf'] },
  { id: 6, caseId: 'CC-2026-0182', applicant: 'Koperasi Sejahtera Bersama', facility: 'Linkage Program', amount: 'Rp 2.1B', committee: 'CC-1', slaDue: 'Due in 3d', slaBreached: false, priority: 'normal', status: 'approved', rm: 'Dewi Susanti', myVote: 'approve', voteComment: '', voted: true, aiScore: 80, aiRec: 'Approve', aiReason: 'Well-established cooperative, clean credit history.', metrics: [{ label: 'LTV', value: '60%' }, { label: 'DSCR', value: '1.9x' }, { label: 'Credit Score', value: '745', color: 'text-green-600' }, { label: 'Industry Risk', value: 'Low', color: 'text-green-600' }], documents: ['Credit Application Form.pdf', 'Cooperative Deed.pdf'] },
  { id: 7, caseId: 'CC-2026-0181', applicant: 'PT Logistik Prima', facility: 'Fleet Financing', amount: 'Rp 12B', committee: 'CC-2', slaDue: 'Due in 5d', slaBreached: false, priority: 'normal', status: 'deferred', rm: 'Wahyu Prasetyo', myVote: null, voteComment: '', voted: false, aiScore: 60, aiRec: 'Defer', aiReason: 'Pending environmental clearance certificate for new routes.', metrics: [{ label: 'LTV', value: '72%' }, { label: 'DSCR', value: '1.5x' }, { label: 'Credit Score', value: '700' }, { label: 'Industry Risk', value: 'Medium' }], documents: ['Credit Application Form.pdf', 'Fleet Inventory.pdf'] },
  { id: 8, caseId: 'CC-2026-0180', applicant: 'PT Herbal Nusantara', facility: 'Export Financing', amount: 'Rp 4.8B', committee: 'CC-1', slaDue: 'Due in 6d', slaBreached: false, priority: 'normal', status: 'rejected', rm: 'Fikri Hakim', myVote: 'reject', voteComment: '', voted: true, aiScore: 40, aiRec: 'Reject', aiReason: 'Insufficient export license, high concentration risk in single buyer.', metrics: [{ label: 'LTV', value: '80%', color: 'text-red-600' }, { label: 'DSCR', value: '1.1x' }, { label: 'Credit Score', value: '640', color: 'text-amber-600' }, { label: 'Industry Risk', value: 'High', color: 'text-red-600' }], documents: ['Credit Application Form.pdf', 'Export Invoice.pdf'] },
])

const filteredQueue = computed(() => {
  return queueItems.value.filter((item) => {
    if (queueSearch.value && !item.applicant.toLowerCase().includes(queueSearch.value.toLowerCase()) && !item.caseId.toLowerCase().includes(queueSearch.value.toLowerCase())) return false
    if (queueFilterType.value && item.committee !== queueFilterType.value) return false
    if (queueFilterStatus.value && item.status !== queueFilterStatus.value) return false
    if (queueFilterPriority.value && item.priority !== queueFilterPriority.value) return false
    return true
  })
})

const meetings = ref([
  {
    id: 1,
    title: 'Credit Committee Level 1 — May Session',
    committee: 'CC-1',
    day: '28',
    month: 'MAY',
    time: '09:00 – 11:00 WIB',
    location: 'Board Room 1, BNI HQ Jakarta',
    color: 'bg-crm-teal',
    status: 'upcoming',
    cases: 3,
    quorum: 3,
    members: [
      { name: 'Budi Hartono', role: 'Chair', confirmed: true },
      { name: 'Siti Rahma', role: 'Risk Officer', confirmed: true },
      { name: 'Agus Setiawan', role: 'Credit Analyst', confirmed: true },
      { name: 'Lina Permata', role: 'Compliance', confirmed: false },
    ],
    agenda: ['Review CC-2026-0187 PT Maju Bersama Tbk', 'Review CC-2026-0186 CV Sukses Makmur', 'Review CC-2026-0184 PT Agri Sejahtera', 'AOB'],
  },
  {
    id: 2,
    title: 'Credit Committee Level 2 — Emergency Session',
    committee: 'CC-2',
    day: '26',
    month: 'MAY',
    time: '14:00 – 16:00 WIB',
    location: 'Video Conference (Teams)',
    color: 'bg-amber-600',
    status: 'in_progress',
    cases: 2,
    quorum: 4,
    members: [
      { name: 'Direktur Kredit', role: 'Chair', confirmed: true },
      { name: 'Divisi Risiko', role: 'Risk Officer', confirmed: true },
      { name: 'Divisi Kepatuhan', role: 'Compliance', confirmed: true },
      { name: 'Branch Manager', role: 'Proposing RM', confirmed: true },
      { name: 'Legal Counsel', role: 'Legal', confirmed: false },
    ],
    agenda: ['Review CC-2026-0185 PT Teknologi Nusantara', 'Review CC-2026-0181 PT Logistik Prima'],
  },
  {
    id: 3,
    title: 'Risk Management Committee — Monthly Review',
    committee: 'RMC',
    day: '30',
    month: 'MAY',
    time: '10:00 – 12:00 WIB',
    location: 'Executive Floor, BNI HQ',
    color: 'bg-blue-600',
    status: 'upcoming',
    cases: 5,
    quorum: 5,
    members: [
      { name: 'Direktur Utama', role: 'Chair', confirmed: true },
      { name: 'Direktur Kredit', role: 'Member', confirmed: true },
      { name: 'Direktur Risiko', role: 'Member', confirmed: true },
      { name: 'Direktur Kepatuhan', role: 'Member', confirmed: false },
      { name: 'Komisaris Independen', role: 'Observer', confirmed: true },
    ],
    agenda: ['Portfolio NPL Review Q1 2026', 'Sector Concentration Review', 'Large Exposure Report', 'Early Warning System Update', 'New Credit Policy Endorsement'],
  },
])

const committees = ref([
  {
    id: 1, name: 'Credit Committee Level 1', code: 'CC-1',
    description: 'Handles credit facilities up to Rp 10 Billion per borrower/group.',
    authority: '≤ Rp 10 Billion',
    quorum: 3,
    sla: '3 business days',
    approvalRule: 'Simple Majority (>50%)',
    members: ['Budi Hartono', 'Siti Rahma', 'Agus Setiawan', 'Lina Permata', 'Wahyu Prasetyo'],
  },
  {
    id: 2, name: 'Credit Committee Level 2', code: 'CC-2',
    description: 'Handles credit facilities from Rp 10B to Rp 50 Billion per borrower/group.',
    authority: 'Rp 10B – Rp 50B',
    quorum: 4,
    sla: '5 business days',
    approvalRule: 'Supermajority (≥2/3)',
    members: ['Direktur Kredit', 'Divisi Risiko', 'Divisi Kepatuhan', 'Branch Manager', 'Legal Counsel', 'Komisaris'],
  },
  {
    id: 3, name: 'Credit Committee Level 3', code: 'CC-3',
    description: 'Board-level committee for large exposures exceeding Rp 50 Billion.',
    authority: '> Rp 50 Billion',
    quorum: 5,
    sla: '7 business days',
    approvalRule: 'Unanimous',
    members: ['Direktur Utama', 'Direktur Kredit', 'Direktur Risiko', 'Direktur Kepatuhan', 'Komisaris Independen', 'Komisaris Utama'],
  },
  {
    id: 4, name: 'Risk Management Committee', code: 'RMC',
    description: 'Enterprise-wide risk oversight including NPL policy and portfolio concentration.',
    authority: 'Policy & Oversight',
    quorum: 5,
    sla: '10 business days',
    approvalRule: 'Simple Majority (>50%)',
    members: ['Direktur Utama', 'Direktur Kredit', 'Direktur Risiko', 'Direktur Kepatuhan', 'Komisaris Independen'],
  },
])

const analyticsKPIs = [
  { label: 'Approval Rate', value: '79.2%', trend: 3.1 },
  { label: 'Avg TAT', value: '3.2 days', trend: -8.5 },
  { label: 'SLA Compliance', value: '94.1%', trend: 1.8 },
  { label: 'Quorum Met Rate', value: '96.7%', trend: 0.5 },
]

const approvalByCommittee = [
  { name: 'CC-1', rate: 82, approved: 41, rejected: 7, deferred: 2, approvedPct: 82, rejectedPct: 14, deferredPct: 4 },
  { name: 'CC-2', rate: 74, approved: 22, rejected: 6, deferred: 2, approvedPct: 74, rejectedPct: 20, deferredPct: 7 },
  { name: 'CC-3', rate: 67, approved: 4, rejected: 2, deferred: 0, approvedPct: 67, rejectedPct: 33, deferredPct: 0 },
  { name: 'RMC', rate: 90, approved: 9, rejected: 1, deferred: 0, approvedPct: 90, rejectedPct: 10, deferredPct: 0 },
]

const tatBuckets = [
  { label: '0–1 days', count: 12, pct: 24, color: 'bg-green-500' },
  { label: '2–3 days', count: 22, pct: 44, color: 'bg-green-400' },
  { label: '4–5 days', count: 10, pct: 20, color: 'bg-amber-400' },
  { label: '6–7 days', count: 4, pct: 8, color: 'bg-orange-500' },
  { label: '> 7 days', count: 2, pct: 4, color: 'bg-red-500' },
]

const memberParticipation = [
  { name: 'Budi Hartono', meetings: 12, attendance: 100, votes: 48 },
  { name: 'Siti Rahma', meetings: 12, attendance: 92, votes: 44 },
  { name: 'Agus Setiawan', meetings: 12, attendance: 83, votes: 40 },
  { name: 'Direktur Kredit', meetings: 8, attendance: 88, votes: 32 },
  { name: 'Direktur Risiko', meetings: 8, attendance: 100, votes: 30 },
]

const monthlyVolume = [
  { month: 'Dec', count: 14 },
  { month: 'Jan', count: 18 },
  { month: 'Feb', count: 16 },
  { month: 'Mar', count: 22 },
  { month: 'Apr', count: 20 },
  { month: 'May', count: 25 },
]

const calendarCells = computed(() => {
  const cells = []
  for (let i = 0; i < 4; i++) cells.push({ key: 'pre' + i, day: '', hasEvent: false, today: false })
  for (let d = 1; d <= 31; d++) {
    cells.push({ key: d, day: d, hasEvent: [6, 13, 20, 26, 28, 30].includes(d), today: d === 24 })
  }
  return cells
})

const currentCase = computed(() => {
  if (!activeSession.value) return null
  return activeSession.value.cases[activeSessionCaseIdx.value]
})

function priorityBadge(p) {
  return {
    urgent: 'px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-semibold',
    high: 'px-2 py-0.5 bg-orange-100 text-orange-700 rounded text-xs font-semibold',
    normal: 'px-2 py-0.5 bg-surface-gray-2 text-ink-gray-6 rounded text-xs',
  }[p] || 'px-2 py-0.5 bg-surface-gray-2 text-ink-gray-5 rounded text-xs'
}

function statusBadge(s) {
  return {
    pending: 'px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs font-medium',
    in_session: 'px-2 py-0.5 bg-teal-50 text-crm-teal rounded text-xs font-medium',
    approved: 'px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium',
    rejected: 'px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-medium',
    deferred: 'px-2 py-0.5 bg-surface-gray-2 text-ink-gray-6 rounded text-xs font-medium',
  }[s] || 'px-2 py-0.5 bg-surface-gray-2 text-ink-gray-5 rounded text-xs'
}

function statusLabel(s) {
  return { pending: 'Pending', in_session: 'In Session', approved: 'Approved', rejected: 'Rejected', deferred: 'Deferred' }[s] || s
}

function mtgStatusBadge(s) {
  return {
    upcoming: 'px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium',
    in_progress: 'px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-medium',
    completed: 'px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium',
  }[s] || 'px-2 py-1 bg-surface-gray-2 text-ink-gray-5 rounded text-xs'
}

function avatarColor(name) {
  const colors = ['bg-teal-500', 'bg-blue-500', 'bg-green-500', 'bg-amber-500', 'bg-red-500', 'bg-indigo-500', 'bg-pink-500', 'bg-teal-500']
  return colors[(name?.charCodeAt(0) || 0) % colors.length]
}

function openCaseDetail(item) {
  selectedCase.value = item
  showCaseModal.value = true
}

function openVoting(item) {
  const session = meetings.value.find((m) => m.status === 'in_progress') || meetings.value[0]
  activeSession.value = {
    ...session,
    cases: queueItems.value.filter((q) => ['pending', 'in_session'].includes(q.status)),
    votedCount: 2,
  }
  const idx = activeSession.value.cases.findIndex((c) => c.id === item.id)
  activeSessionCaseIdx.value = idx >= 0 ? idx : 0
  activeTab.value = 'voting'
}

function startSession(mtg) {
  mtg.status = 'in_progress'
  activeSession.value = {
    ...mtg,
    cases: queueItems.value.filter((q) => ['pending', 'in_session'].includes(q.status)).slice(0, mtg.cases),
    votedCount: 0,
  }
  activeSessionCaseIdx.value = 0
  activeTab.value = 'voting'
}

function castVote(cas, vote) {
  cas.myVote = vote
  cas.voted = true
  if (activeSession.value) {
    activeSession.value.votedCount = Math.min(activeSession.value.votedCount + 1, activeSession.value.members.length)
    const member = activeSession.value.members.find((m) => m.name === 'Budi Hartono')
    if (member) member.vote = vote
  }
  showToast(`Vote recorded: ${vote.charAt(0).toUpperCase() + vote.slice(1)}`)
}

function caseDetailFields(cas) {
  return [
    { label: 'Case ID', value: cas.caseId },
    { label: 'Facility Type', value: cas.facility },
    { label: 'Requested Amount', value: cas.amount },
    { label: 'Committee', value: cas.committee },
    { label: 'Relationship Manager', value: cas.rm },
    { label: 'Status', value: statusLabel(cas.status) },
    { label: 'SLA Due', value: cas.slaDue },
    { label: 'AI Score', value: cas.aiScore + '/100' },
  ]
}

function saveMeeting() {
  showScheduleModal.value = false
  showToast('Meeting scheduled successfully')
}

function saveCommittee() {
  const f = committeeForm.value
  if (!f.name || !f.code) {
    showToast('Name and code are required')
    return
  }
  const members = f.members.filter((m) => m.name && m.name.trim())
  const quorumCount = Math.max(1, Math.ceil((members.length || 1) * (f.quorumPct / 100)))
  const payload = {
    id: f.id || (committees.value.length ? Math.max(...committees.value.map((c) => c.id)) + 1 : 1),
    name: f.name,
    code: f.code,
    description: f.description,
    authority: f.authority,
    quorum: quorumCount,
    quorumPct: f.quorumPct,
    sla: `${f.slaDays} business days`,
    slaDays: f.slaDays,
    approvalRule: f.approvalRule,
    chairTieBreak: f.chairTieBreak,
    members,
  }
  if (f.id) {
    const idx = committees.value.findIndex((c) => c.id === f.id)
    if (idx >= 0) committees.value.splice(idx, 1, { ...committees.value[idx], ...payload, members: members.map((m) => m.name) })
    showToast('Committee updated')
  } else {
    committees.value.push({ ...payload, members: members.map((m) => m.name) })
    showToast('Committee created successfully')
  }
  closeSetupModal()
}

function showToast(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 3000)
}
</script>
