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

    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-4">
      <div class="flex gap-3 overflow-x-auto">
        <button
          v-for="tab in pageTabs"
          :key="tab.id"
          class="border-b-2 py-2 text-base transition-colors whitespace-nowrap"
          :class="activeTab === tab.id
            ? 'border-ink-gray-8 font-medium text-ink-gray-9'
            : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          @click="activeTab = tab.id"
        >
          {{ __(tab.label) }}
          <Badge v-if="tab.badge" :label="String(tab.badge)" theme="primary" variant="subtle" size="sm" class="ml-1" />
        </button>
      </div>
    </div>

    <!-- Body -->
    <div class="flex-1 overflow-auto bg-surface-gray-1 p-3">

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
        <div class="bg-surface-white rounded-[10px] border border-outline-gray-2 mb-3 p-3">
          <div class="flex gap-3 flex-wrap items-center">
            <input v-model="queueSearch" type="text" placeholder="Search applicant, facility..." class="flex-1 min-w-48 px-3 py-2 border border-outline-gray-2 rounded-lg text-sm" />
            <select v-model="queueFilterType" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm">
              <option value="">All Committees</option>
              <option v-for="committee in committees" :key="committee.id" :value="committee.id">{{ committee.name }}</option>
            </select>
            <select v-model="queueFilterStatus" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="in_session">In Session</option>
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
        <div class="bg-surface-white rounded-[10px] border border-outline-gray-2 overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-surface-gray-1 border-b border-outline-gray-2">
              <tr>
                <th class="text-left px-3 py-2 text-xs font-semibold text-ink-gray-5 uppercase">Case</th>
                <th class="text-left px-3 py-2 text-xs font-semibold text-ink-gray-5 uppercase">Applicant</th>
                <th class="text-left px-3 py-2 text-xs font-semibold text-ink-gray-5 uppercase">Facility</th>
                <th class="text-right px-3 py-2 text-xs font-semibold text-ink-gray-5 uppercase">Amount</th>
                <th class="text-left px-3 py-2 text-xs font-semibold text-ink-gray-5 uppercase">Committee</th>
                <th class="text-left px-3 py-2 text-xs font-semibold text-ink-gray-5 uppercase">SLA</th>
                <th class="text-left px-3 py-2 text-xs font-semibold text-ink-gray-5 uppercase">Priority</th>
                <th class="text-left px-3 py-2 text-xs font-semibold text-ink-gray-5 uppercase">Status</th>
                <th class="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1">
              <tr
                v-for="item in filteredQueue"
                :key="item.id"
                class="hover:bg-surface-gray-1 cursor-pointer"
                @click="openCaseDetail(item)"
              >
                <td class="px-3 py-2">
                  <span class="font-mono text-xs text-[#980000] font-semibold">{{ item.caseId }}</span>
                </td>
                <td class="px-3 py-2">
                  <div class="font-medium text-ink-gray-9">{{ item.applicant }}</div>
                  <div class="text-xs text-ink-gray-5">RM: {{ item.rm }}</div>
                </td>
                <td class="px-3 py-2 text-ink-gray-7">{{ item.facility }}</td>
                <td class="px-3 py-2 text-right font-semibold text-ink-gray-9">{{ item.amount }}</td>
                <td class="px-3 py-2">
                  <span class="px-2 py-0.5 rounded text-xs font-semibold bg-[#980000]/10 text-[#980000]">{{ item.committee }}</span>
                </td>
                <td class="px-3 py-2">
                  <span :class="['text-xs font-medium', item.slaBreached ? 'text-red-600' : 'text-green-600']">
                    {{ item.slaDue }}
                  </span>
                </td>
                <td class="px-3 py-2">
                  <span :class="priorityBadge(item.priority)">{{ item.priority }}</span>
                </td>
                <td class="px-3 py-2">
                  <span :class="statusBadge(item.status)">{{ statusLabel(item.status) }}</span>
                </td>
                <td class="px-3 py-2">
                  <button
                    v-if="item.status === 'pending'"
                    @click.stop="openVoting(item)"
                    class="px-3 py-1 bg-[#980000] text-white rounded text-xs font-medium hover:bg-[#E55A00]"
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

      <!-- ───── TAB: Meetings ───── -->
      <div v-if="activeTab === 'meetings'" class="space-y-3">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-base font-semibold text-ink-gray-9">Scheduled Committee Meetings</h2>
          <div class="flex gap-2">
            <button @click="meetingView = 'list'" :class="['px-3 py-1 rounded text-sm', meetingView==='list' ? 'bg-[#980000] text-white' : 'bg-surface-white border text-ink-gray-6']">List</button>
            <button @click="meetingView = 'calendar'" :class="['px-3 py-1 rounded text-sm', meetingView==='calendar' ? 'bg-[#980000] text-white' : 'bg-surface-white border text-ink-gray-6']">Calendar</button>
          </div>
        </div>

        <!-- Meeting Cards -->
        <div v-if="meetingView === 'list'" class="space-y-3">
          <div
            v-for="mtg in meetings"
            :key="mtg.id"
            class="bg-surface-white rounded-[10px] border border-outline-gray-2 p-3"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-3">
                <div :class="['w-12 h-12 rounded-[10px] flex flex-col items-center justify-center text-white text-xs font-bold', mtg.color]">
                  <span class="text-lg leading-none">{{ mtg.day }}</span>
                  <span>{{ mtg.month }}</span>
                </div>
                <div>
                  <div class="font-semibold text-ink-gray-9 text-base">{{ mtg.title }}</div>
                  <div class="text-sm text-ink-gray-5 mt-0.5">{{ mtg.time }} · {{ mtg.location }}</div>
                  <div class="flex gap-2 mt-2 flex-wrap">
                    <span class="px-2 py-0.5 bg-surface-gray-2 rounded text-xs text-ink-gray-6">{{ mtg.committee }}</span>
                    <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">{{ mtg.cases }} cases</span>
                    <span v-if="mtg.quorum" class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">{{ mtg.members.length }}/{{ mtg.quorum }} quorum</span>
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span :class="mtgStatusBadge(mtg.status)">{{ mtg.status }}</span>
                <button
                  v-if="mtg.status === 'upcoming'"
                  @click="startSession(mtg)"
                  class="px-4 py-1.5 bg-[#980000] text-white rounded-lg text-sm font-medium hover:bg-[#E55A00]"
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
                  class="px-3 py-1.5 border border-[#980000] text-[#980000] rounded-lg text-sm hover:bg-[#980000]/10"
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
                  <span class="w-5 h-5 rounded-full bg-[#980000]/10 text-[#980000] text-xs flex items-center justify-center font-semibold">{{ idx + 1 }}</span>
                  {{ item }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Calendar View (simplified) -->
        <div v-else class="bg-surface-white rounded-[10px] border border-outline-gray-2 p-3">
          <div class="text-center mb-3">
            <h3 class="text-base font-semibold text-ink-gray-9">{{ new Date().toLocaleString('en-US', { month: 'long', year: 'numeric' }) }}</h3>
          </div>
          <div class="grid grid-cols-7 gap-1 text-center text-xs text-ink-gray-5 mb-2">
            <div v-for="d in ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']" :key="d">{{ d }}</div>
          </div>
          <div class="grid grid-cols-7 gap-1">
            <div v-for="cell in calendarCells" :key="cell.key" :class="['aspect-square rounded-lg flex flex-col items-center justify-center text-sm', cell.today ? 'bg-[#980000] text-white font-bold' : cell.hasEvent ? 'bg-[#980000]/10 text-[#980000] font-semibold cursor-pointer hover:bg-[#980000]/15' : 'text-ink-gray-5']">
              <span>{{ cell.day }}</span>
              <span v-if="cell.hasEvent" class="w-1.5 h-1.5 rounded-full bg-[#980000] mt-0.5" :class="cell.today ? 'bg-surface-white' : ''"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Voting ───── -->
      <div v-if="activeTab === 'voting'">
        <!-- Active Session Banner -->
        <div v-if="activeSession" class="bg-amber-50 border border-amber-200 rounded-[10px] p-3 mb-3 flex items-center justify-between">
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
          <div class="flex items-center gap-3 text-sm text-amber-800">
            <span>Quorum: <strong>{{ activeSession.votedCount }}/{{ activeSession.members.length }}</strong></span>
            <span>Cases: <strong>{{ activeSessionCaseIdx + 1 }}/{{ activeSession.cases.length }}</strong></span>
            <button @click="activeSession = null" class="px-3 py-1 bg-amber-600 text-white rounded text-sm">End Session</button>
          </div>
        </div>

        <div v-if="!activeSession" class="text-center py-20">
          <div class="w-16 h-16 rounded-full bg-surface-gray-2 flex items-center justify-center mx-auto mb-3">
            <svg class="w-8 h-8 text-ink-gray-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <p class="text-ink-gray-5 mb-3">No active session. Start a meeting from the Meetings tab.</p>
          <button @click="activeTab = 'meetings'" class="px-3 py-1.5 bg-[#980000] text-white rounded-lg text-sm">View Meetings</button>
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
                :class="['p-4 cursor-pointer', activeSessionCaseIdx === idx ? 'bg-primary-50' : 'hover:bg-surface-gray-1']"
              >
                <div class="flex justify-between items-start">
                  <div>
                    <p class="font-mono text-xs text-[#980000] font-semibold">{{ cas.caseId }}</p>
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
                  class="inline-flex items-center gap-1.5 text-xs font-extrabold text-primary-600 hover:underline mb-3"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                  <span>{{ __('Back to Agenda Cases') }}</span>
                </button>
                <div class="flex justify-between items-start">
                  <div>
                    <span class="font-mono text-sm text-[#980000] font-semibold">{{ currentCase.caseId }}</span>
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
              <div class="px-6 py-4 grid grid-cols-4 gap-3 border-b border-outline-gray-1">
                <div v-for="metric in currentCase.metrics" :key="metric.label">
                  <p class="text-xs text-ink-gray-5">{{ metric.label }}</p>
                  <p class="font-semibold text-sm" :class="metric.color || 'text-ink-gray-9'">{{ metric.value }}</p>
                </div>
              </div>

              <!-- AI Recommendation -->
              <div v-if="currentCase.aiRec" class="px-6 py-3 bg-blue-50 flex items-start gap-3 border-b border-blue-100">
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
              <div class="px-6 py-3">
                <p class="text-sm font-semibold text-ink-gray-7 mb-3">Cast Your Vote</p>
                <div class="grid grid-cols-3 gap-3 mb-3">
                  <button
                    @click="castVote(currentCase, 'approve')"
                    :class="['py-3 rounded-[10px] border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'approve' ? 'border-green-500 bg-green-50 text-green-700' : 'border-outline-gray-2 hover:border-green-300 text-ink-gray-6']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                    Approve
                  </button>
                  <button
                    @click="castVote(currentCase, 'reject')"
                    :class="['py-3 rounded-[10px] border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'reject' ? 'border-red-500 bg-red-50 text-red-700' : 'border-outline-gray-2 hover:border-red-300 text-ink-gray-6']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    Reject
                  </button>
                  <button
                    @click="castVote(currentCase, 'defer')"
                    :class="['py-3 rounded-[10px] border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'defer' ? 'border-amber-500 bg-amber-50 text-amber-700' : 'border-outline-gray-2 hover:border-amber-300 text-ink-gray-6']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    Defer
                  </button>
                </div>

                <textarea v-model="currentCase.voteComment" rows="2" placeholder="Voting remarks (optional)..." class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm resize-none mb-3"></textarea>
                <label class="mb-3 flex items-center gap-2 text-xs text-ink-gray-6">
                  <input v-model="voteSignatureAck" type="checkbox" /> I confirm this vote as my electronic signature.
                </label>

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
                    <div class="h-full bg-[#980000] rounded-full transition-all" :style="{ width: (activeSession.votedCount / activeSession.members.length * 100) + '%' }"></div>
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
            class="bg-surface-white rounded-[10px] border border-outline-gray-2 p-3"
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
              <button @click="openEditCommittee(committee, true)" class="flex-1 py-1.5 border border-[#980000] text-[#980000] rounded text-xs hover:bg-[#980000]/10">Members</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Calendar ───── -->
      <div v-if="activeTab === 'calendar'" class="space-y-3">
        <div class="flex items-center gap-3">
          <select v-model="calendarFilter" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm">
            <option value="">All committees</option>
            <option v-for="committee in committees" :key="committee.id" :value="committee.id">{{ committee.name }}</option>
          </select>
          <input v-model="calendarMonth" type="month" class="px-3 py-2 border border-outline-gray-2 rounded-lg text-sm" />
          <span class="text-sm text-ink-gray-5">{{ calendarEvents.length }} events</span>
        </div>
        <div class="bg-surface-white rounded-[10px] border border-outline-gray-2 p-3">
          <div v-for="ev in calendarEvents" :key="ev.label + ev.date" class="flex items-center gap-3 border-b border-outline-gray-1 last:border-b-0 py-2">
            <div :class="['w-2 h-2 rounded-full', ev.color || 'bg-[#980000]']"></div>
            <span class="text-sm font-mono text-ink-gray-5 w-28">{{ ev.date }}</span>
            <span class="text-xs px-2 py-0.5 rounded bg-surface-gray-2 text-ink-gray-6">{{ ev.committee }}</span>
            <span class="text-sm text-ink-gray-8">{{ ev.label }}</span>
          </div>
          <p v-if="!calendarEvents.length" class="text-sm text-ink-gray-5 text-center py-8">No events for current filter.</p>
        </div>
      </div>

      <!-- ───── TAB: Live Meeting ───── -->
      <div v-if="activeTab === 'live'" class="space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-outline-gray-2 bg-white p-4">
          <div>
            <h2 class="text-lg font-semibold text-ink-gray-9">Transkrip langsung rapat</h2>
            <p class="text-sm text-ink-gray-5">Ikuti pembahasan, pertanyaan, dan hasil rapat dalam satu ruang kerja.</p>
          </div>
          <select v-model="liveMeetingId" :disabled="capturing" aria-label="Pilih rapat" class="min-w-56 rounded-lg border border-outline-gray-2 px-3 py-2 text-sm">
            <option :value="null">Pilih rapat</option>
            <option v-for="m in meetings" :key="m.id" :value="m.id">{{ m.title }}</option>
          </select>
        </div>

        <div v-if="liveCurrentMeeting" class="overflow-hidden rounded-xl border border-outline-gray-2 bg-white">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-outline-gray-2 bg-white px-5 py-4">
            <div class="flex items-center gap-3">
              <span class="size-2.5 rounded-full" :class="capturing ? 'animate-pulse bg-[#980000]' : 'bg-gray-400'"></span>
              <div>
                <h3 class="font-semibold text-ink-gray-9">{{ liveCurrentMeeting.title }}</h3>
                <p class="text-xs text-ink-gray-5">{{ capturing ? 'Transkrip berjalan' : liveStarted ? 'Sesi aktif · siap menangkap audio' : 'Sesi belum dimulai' }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="font-mono text-sm tabular-nums text-ink-gray-7">{{ liveElapsedLabel }}</span>
              <button v-if="!liveStarted" @click="startLiveMeeting(liveMeetingId)" class="rounded-lg bg-[#980000] px-3 py-2 text-sm font-medium text-white">Mulai sesi</button>
              <button v-else @click="endLiveMeeting" :disabled="startingCapture" class="rounded-lg border border-outline-gray-2 px-3 py-2 text-sm text-ink-gray-8 disabled:opacity-50">Akhiri sesi</button>
            </div>
          </div>

          <div class="grid lg:grid-cols-[minmax(0,1.6fr)_minmax(300px,0.8fr)]">
            <section class="flex min-h-[560px] flex-col border-b border-outline-gray-2 lg:border-b-0 lg:border-r" aria-label="Transkrip langsung">
              <div class="flex items-center justify-between gap-3 border-b border-outline-gray-2 px-5 py-4">
                <div>
                  <h4 class="font-semibold text-ink-gray-9">Live transcript</h4>
                  <p class="text-xs text-ink-gray-5">Audio rapat dan suara Anda tampil sebagai sumber terpisah.</p>
                </div>
                <span class="rounded-full bg-[#980000]/10 px-2.5 py-1 text-xs font-semibold text-[#980000]">{{ transcriptSegments.length }} segmen</span>
              </div>
              <p v-if="transcriptStatus" role="status" class="mx-5 mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">{{ transcriptStatus }}</p>
              <div class="max-h-[560px] min-h-[380px] flex-1 space-y-4 overflow-y-auto p-5" aria-live="polite">
                <div v-if="!transcriptSegments.length && !partialTranscript.meeting && !partialTranscript.mic" class="flex h-full min-h-[280px] flex-col items-center justify-center text-center">
                  <FeatherIcon name="mic" class="mb-3 h-8 w-8 text-[#980000]" />
                  <p class="font-medium text-ink-gray-8">Siap mengikuti rapat</p>
                  <p class="mt-2 max-w-sm text-sm text-ink-gray-5">Klik Mulai tangkap, pilih tab Zoom atau Google Meet, lalu aktifkan Bagikan audio tab. Mikrofon Anda juga akan ditangkap jika diizinkan.</p>
                </div>
                <article v-for="(segment, index) in transcriptSegments" :key="index" class="flex gap-3">
                  <span class="flex size-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold" :class="segment.source === 'mic' ? 'bg-gray-100 text-gray-700' : 'bg-[#980000]/10 text-[#980000]'">{{ segment.source === 'mic' ? 'IN' : 'ME' }}</span>
                  <div class="min-w-0 flex-1">
                    <div class="flex flex-wrap items-center gap-2 text-xs"><strong class="text-ink-gray-8">{{ segment.speaker || (segment.source === 'mic' ? 'Anda' : 'Belum dikenali') }}</strong><span class="text-ink-gray-5">{{ formatLiveOffset(segment.offset_ms) }}</span></div>
                    <p class="mt-1 whitespace-pre-wrap text-sm leading-6 text-ink-gray-8">{{ segment.text }}</p>
                    <div class="mt-2 flex flex-wrap items-center gap-3">
                      <select :value="speakerOptions.includes(segment.speaker) ? segment.speaker : ''" :aria-label="`Nama pembicara segmen ${index + 1}`" @change="setTranscriptSpeaker(index, $event)" class="rounded-md border border-outline-gray-2 px-2 py-1 text-xs">
                        <option value="">Pilih nama pembicara</option>
                        <option v-for="name in speakerOptions" :key="name" :value="name">{{ name }}</option>
                      </select>
                      <button @click="toggleTranscriptBookmark(index)" :aria-pressed="!!segment.bookmarked" class="text-xs font-medium" :class="segment.bookmarked ? 'text-amber-700' : 'text-ink-gray-5'">{{ segment.bookmarked ? '★ Ditandai' : '☆ Tandai bagian ini' }}</button>
                    </div>
                  </div>
                </article>
                <p v-if="partialTranscript.meeting" class="ml-11 text-sm italic text-ink-gray-5">{{ pendingRemoteSpeaker || activeRemoteSpeaker || 'Belum dikenali' }} · {{ partialTranscript.meeting }}</p>
                <p v-if="partialTranscript.mic" class="ml-11 text-sm italic text-ink-gray-5">{{ speakerRoster.selfName || 'Anda' }} · {{ partialTranscript.mic }}</p>
              </div>
              <div class="flex flex-wrap items-center justify-center gap-2 border-t border-outline-gray-2 p-4">
                <label class="flex items-center gap-2 text-sm text-ink-gray-7">Sedang berbicara
                  <select v-model="activeRemoteSpeaker" aria-label="Pembicara dari tab rapat" class="max-w-48 rounded-lg border border-outline-gray-2 px-2 py-2 text-sm">
                    <option value="">Belum dikenali</option>
                    <option v-for="name in speakerParticipants" :key="name" :value="name">{{ name }}</option>
                  </select>
                </label>
                <button v-if="!capturing" @click="startTranscription" :disabled="!liveStarted || startingCapture" class="rounded-lg bg-[#980000] px-4 py-2 text-sm font-medium text-white disabled:opacity-50">{{ startingCapture ? 'Menyiapkan…' : 'Mulai tangkap' }}</button>
                <button v-else @click="stopTranscription" class="rounded-lg bg-[#980000] px-4 py-2 text-sm font-medium text-white">Hentikan transkrip</button>
                <button v-if="capturing && microphoneAvailable" @click="toggleMicrophone" :aria-pressed="microphoneEnabled" class="rounded-lg border border-outline-gray-2 px-3 py-2 text-sm">{{ microphoneEnabled ? 'Matikan mikrofon' : 'Aktifkan mikrofon' }}</button>
              </div>
            </section>

            <aside class="space-y-4 bg-surface-gray-1 p-4">
              <section class="rounded-xl border border-outline-gray-2 bg-white p-4">
                <h4 class="font-semibold text-ink-gray-9">Nama pembicara</h4>
                <p class="mt-1 text-xs text-ink-gray-5">Isi sebelum rapat. Saat pembicara berganti, pilih namanya di bawah transkrip. Nama setiap segmen bisa diperbaiki.</p>
                <label class="mt-3 block text-xs font-medium text-ink-gray-7">Nama Anda
                  <input v-model="speakerRoster.selfName" maxlength="80" placeholder="Nama yang digunakan saat rapat" class="mt-1 w-full rounded-lg border border-outline-gray-2 px-3 py-2 text-sm" />
                </label>
                <label class="mt-3 block text-xs font-medium text-ink-gray-7">Peserta lain (satu nama per baris)
                  <textarea v-model="speakerRoster.participantsText" rows="3" class="mt-1 w-full resize-y rounded-lg border border-outline-gray-2 px-3 py-2 text-sm"></textarea>
                </label>
                <button @click="saveSpeakerRoster" :disabled="savingSpeakerRoster || !speakerRosterDirty || !speakerRoster.selfName.trim()" class="mt-3 rounded-lg bg-[#980000] px-3 py-2 text-sm font-medium text-white disabled:opacity-50">{{ savingSpeakerRoster ? 'Menyimpan…' : 'Simpan nama' }}</button>
              </section>
              <section class="rounded-xl border border-outline-gray-2 bg-white p-4">
                <h4 class="font-semibold text-ink-gray-9">Agenda rapat</h4>
                <p class="mt-1 text-xs text-ink-gray-5">{{ liveCurrentMeeting.committee }} · {{ liveCurrentMeeting.members.length }} anggota</p>
                <ol v-if="liveCurrentMeeting.agenda.length" class="mt-3 space-y-2">
                  <li v-for="(item, index) in liveCurrentMeeting.agenda" :key="index" class="rounded-lg border p-2.5 text-sm" :class="index === liveAgendaIdx ? 'border-[#980000]/40 bg-[#980000]/5 text-ink-gray-9' : 'border-outline-gray-2 text-ink-gray-6'">{{ index + 1 }}. {{ item }}</li>
                </ol>
                <p v-else class="mt-3 text-sm text-ink-gray-5">Belum ada agenda tersimpan.</p>
                <button v-if="liveStarted && liveCurrentMeeting.agenda.length > 1" @click="nextLiveItem" class="mt-3 text-sm font-medium text-[#980000]">Agenda berikutnya →</button>
              </section>
              <section v-for="item in meetingContentSections" :key="item.kind" class="rounded-xl border border-outline-gray-2 bg-white p-4">
                <div class="flex items-start justify-between gap-2">
                  <h4 class="font-semibold text-ink-gray-9">{{ item.title }}</h4>
                  <button @click="generateMeetingContent(item.kind)" :disabled="!!generatingContent || (item.kind === 'analysis' && !transcriptSegments.length)" class="rounded-lg bg-[#980000] px-2.5 py-1.5 text-xs font-medium text-white disabled:opacity-50">{{ generatingContent === item.kind ? 'Menyusun…' : meetingContent[item.kind] ? 'Buat ulang' : 'Buat' }}</button>
                </div>
                <p v-if="meetingContent[item.kind]?.transcript_count < transcriptSegments.length" class="mt-2 text-xs text-amber-700">Transkrip bertambah. Buat ulang untuk memperbarui hasil.</p>
                <p v-if="meetingContent[item.kind]" class="mt-3 whitespace-pre-wrap text-sm leading-6 text-ink-gray-8">{{ meetingText(meetingContent[item.kind].content) }}</p>
                <p v-else class="mt-3 text-sm text-ink-gray-5">{{ item.empty }}</p>
              </section>
            </aside>
          </div>
        </div>
        <p v-else class="rounded-xl border border-outline-gray-2 bg-white p-8 text-center text-sm text-ink-gray-5">Belum ada rapat yang dapat dipilih. Jadwalkan rapat terlebih dahulu.</p>
      </div>

      <!-- ───── TAB: Decisions ───── -->
      <div v-if="activeTab === 'decisions'">
        <div class="bg-surface-white rounded-[10px] border border-outline-gray-2 p-3">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-ink-gray-7">{{ __('Decisions') }}</h3>
            <Button variant="outline" size="sm" label="Reload" @click="loadDecisions" />
          </div>
          <div v-if="decisionsLoading" class="flex h-40 items-center justify-center"><LoadingIndicator class="h-5 w-5 text-ink-gray-4" /></div>
          <table v-else class="w-full text-sm">
            <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
              <tr><th class="px-3 py-2">Application</th><th class="px-3 py-2">Committee</th><th class="px-3 py-2">Outcome</th><th class="px-3 py-2">Date</th><th class="px-3 py-2">Signatures</th><th class="px-3 py-2 text-right"></th></tr>
            </thead>
            <tbody>
              <tr v-for="d in decisionsList" :key="d.name" class="border-b border-outline-gray-1 last:border-b-0">
                <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ d.applicant_name }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7">{{ d.committee_name }}</td>
                <td class="px-3 py-1.5"><Badge :label="d.outcome" :theme="d.outcome === 'Approved' ? 'green' : 'red'" variant="subtle" size="sm" /></td>
                <td class="px-3 py-1.5 text-xs text-ink-gray-5">{{ fmtDate(d.decided_at) }}</td>
                <td class="px-3 py-1.5 text-xs text-ink-gray-7">{{ d.approve_count + d.reject_count + d.abstain_count }} / {{ d.quorum }}</td>
                <td class="px-3 py-1.5 text-right"><Button size="sm" variant="ghost" @click="openAuditDrawer(d)">Audit</Button></td>
              </tr>
              <tr v-if="!decisionsList.length"><td colspan="6" class="px-3 py-8 text-center text-ink-gray-5">No decisions yet.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- ───── MODALS ───── -->

    <!-- Schedule Meeting Modal -->
    <div v-if="showScheduleModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showScheduleModal = false">
      <div class="bg-surface-white rounded-[14px] w-full max-w-lg p-3 shadow-2xl">
        <div class="flex justify-between items-center mb-3">
          <h2 class="text-lg font-bold text-ink-gray-9">Schedule Committee Meeting</h2>
          <button @click="showScheduleModal = false" class="text-ink-gray-4 hover:text-ink-gray-6">✕</button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Meeting title</label>
            <input v-model="meetingForm.title" type="text" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Committee</label>
            <select v-model="meetingForm.committee" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm">
              <option value="">Select committee</option>
              <option v-for="committee in committees" :key="committee.id" :value="committee.id">{{ committee.name }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">Date</label>
              <input v-model="meetingForm.date" type="date" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">Time</label>
              <input v-model="meetingForm.time" type="time" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Location / Room</label>
            <input v-model="meetingForm.location" type="text" placeholder="Meeting room or link" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Agenda Notes</label>
            <textarea v-model="meetingForm.agenda" rows="3" placeholder="One agenda item per line" class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm resize-none"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showScheduleModal = false" class="flex-1 py-2 border border-outline-gray-2 rounded-lg text-sm text-ink-gray-7 hover:bg-surface-gray-1">Cancel</button>
          <button @click="saveMeeting" class="flex-1 py-2 bg-[#980000] text-white rounded-lg text-sm font-medium hover:bg-[#E55A00]">Schedule Meeting</button>
        </div>
      </div>
    </div>

    <!-- Committee Setup Modal -->
    <div v-if="showSetupModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="closeSetupModal">
      <div class="bg-surface-white rounded-[14px] w-full max-w-lg p-3 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-3">
          <h2 class="text-lg font-bold text-ink-gray-9">{{ committeeForm.id ? 'Edit Committee' : 'Create New Committee' }}</h2>
          <button @click="closeSetupModal" class="text-ink-gray-4 hover:text-ink-gray-6">✕</button>
        </div>
        <div class="space-y-3">
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
              <button type="button" @click="addMember" class="text-[#980000] hover:text-[#980000] text-sm font-medium">+ Add Member</button>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input id="chairTieBreak" v-model="committeeForm.chairTieBreak" type="checkbox" class="w-4 h-4" />
            <label for="chairTieBreak" class="text-sm text-ink-gray-7">Chairman has tie-break vote</label>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="closeSetupModal" class="flex-1 py-2 border border-outline-gray-2 rounded-lg text-sm text-ink-gray-7 hover:bg-surface-gray-1">Cancel</button>
          <button @click="saveCommittee" class="flex-1 py-2 bg-[#980000] text-white rounded-lg text-sm font-medium hover:bg-[#E55A00]">{{ committeeForm.id ? 'Save Changes' : 'Create Committee' }}</button>
        </div>
      </div>
    </div>

    <!-- Case Detail Modal -->
    <div v-if="showCaseModal && selectedCase" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCaseModal = false">
      <div class="bg-surface-white rounded-[14px] w-full max-w-2xl p-3 shadow-2xl max-h-[85vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-3">
          <div>
            <span class="font-mono text-sm text-[#980000] font-semibold">{{ selectedCase.caseId }}</span>
            <h2 class="text-lg font-bold text-ink-gray-9">{{ selectedCase.applicant }}</h2>
          </div>
          <button @click="showCaseModal = false" class="text-ink-gray-4 hover:text-ink-gray-6">✕</button>
        </div>
        <div class="grid grid-cols-2 gap-3 mb-3">
          <div v-for="f in caseDetailFields(selectedCase)" :key="f.label" class="bg-surface-gray-1 rounded-lg p-3">
            <p class="text-xs text-ink-gray-5 mb-0.5">{{ f.label }}</p>
            <p class="text-sm font-semibold text-ink-gray-9">{{ f.value }}</p>
          </div>
        </div>
        <div class="mb-3">
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
          <button v-if="selectedCase.status === 'pending'" @click="showCaseModal = false; openVoting(selectedCase)" class="flex-1 py-2 bg-[#980000] text-white rounded-lg text-sm font-medium">Open Voting</button>
          <button @click="showCaseModal = false" class="px-3 py-1.5 border border-outline-gray-2 rounded-lg text-sm text-ink-gray-6">Close</button>
        </div>
      </div>
    </div>

    <!-- Audit Drawer -->
    <div v-if="auditDrawer.open" class="fixed inset-0 z-50 flex justify-end">
      <div class="absolute inset-0 bg-black/30" @click="auditDrawer.open = false" />
      <aside class="relative flex h-full w-full max-w-[520px] flex-col bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-outline-gray-2 px-5 py-4">
          <div class="text-base font-semibold text-ink-gray-9">{{ __('Audit Trail') }}</div>
          <Button variant="ghost" icon="x" @click="auditDrawer.open = false" />
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="auditDrawer.loading" class="flex h-20 items-center justify-center"><LoadingIndicator class="h-4 w-4 text-ink-gray-4" /></div>
          <div v-else-if="!auditDrawer.events.length" class="text-sm text-ink-gray-4">No audit events.</div>
          <div v-else class="space-y-2">
            <div v-for="e in auditDrawer.events" :key="e.name" class="rounded border border-outline-gray-1 p-2 text-sm">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <Badge :label="e.event" theme="gray" variant="subtle" size="sm" />
                  <span class="text-xs text-ink-gray-5">{{ e.actor_name }}</span>
                </div>
                <span class="text-xs text-ink-gray-4">{{ fmtDate(e.event_at) }}</span>
              </div>
              <div v-if="e.payload_json" class="mt-1 text-[11px] text-ink-gray-5">{{ e.payload_json.slice(0, 120) }}</div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Success Toast -->
    <div v-if="toast" class="fixed bottom-6 right-6 bg-green-600 text-white px-3 py-2 rounded-[10px] shadow-lg text-sm font-medium z-50 flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
      {{ toast }}
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import { Badge, Button, FeatherIcon, LoadingIndicator, usePageMeta, call } from 'frappe-ui'
import { Scribe, RealtimeEvents, CommitStrategy, AudioFormat } from '@elevenlabs/client'
import { startMeetingAudioCapture, pcmFrameToBase64 } from '@/lib/committeeAudioCapture'
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'

const viewControls = ref(null)

usePageMeta(() => ({ title: __('Committee Approval') }))

const activeTab = ref('queue')
const voteSignatureAck = ref(false)
const queueSearch = ref('')
const queueFilterType = ref('')
const queueFilterStatus = ref('')
const queueFilterPriority = ref('')
const meetingView = ref('list')
const activeSession = ref(null)
const activeSessionCaseIdx = ref(0)
const showScheduleModal = ref(false)
const meetingForm = reactive({ title: '', committee: '', date: '', time: '', location: '', agenda: '' })
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
  stopTranscription()
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

const pageTabs = computed(() => [
  { id: 'queue', label: 'Case Queue', badge: queueItems.value.length },
  { id: 'meetings', label: 'Meetings' },
  { id: 'voting', label: 'Voting' },
  { id: 'decisions', label: 'Decisions' },
  { id: 'calendar', label: 'Calendar' },
  { id: 'live', label: 'Live Mode' },
  { id: 'committees', label: 'Committees' },
])

const calendarFilter = ref('')
const calendarMonth = ref(new Date().toISOString().slice(0, 7))

const decisionsList = ref([])
const decisionsLoading = ref(false)
const auditDrawer = ref({ open: false, item: null, events: [], loading: false })

async function loadDecisions() {
  decisionsLoading.value = true
  try {
    const res = await call('crm.api.committee.get_decisions', { limit: 100 })
    decisionsList.value = res || []
  } catch (e) {}
  finally { decisionsLoading.value = false }
}

async function openAuditDrawer(d) {
  auditDrawer.value = { open: true, item: d, events: [], loading: true }
  try {
    const res = await call('crm.api.committee.get_audit_trail', { item: d.item })
    auditDrawer.value.events = res.events || []
  } catch (e) {}
  finally { auditDrawer.value.loading = false }
}

watch(activeTab, (t) => {
  if (t === 'decisions') loadDecisions()
})

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

const agendaItems = ref([])
const liveMeetingId = ref(null)
const liveAgendaIdx = ref(0)
const liveStarted = ref(false)
const capturing = ref(false)
const startingCapture = ref(false)
const microphoneAvailable = ref(false)
const microphoneEnabled = ref(false)
const partialTranscript = reactive({ meeting: '', mic: '' })
const transcriptStatus = ref('')
const transcriptSegments = ref([])
const speakerRoster = reactive({ selfName: '', participantsText: '' })
const speakerParticipants = ref([])
const activeRemoteSpeaker = ref('')
const savingSpeakerRoster = ref(false)
const savedSpeakerRoster = ref('')
const speakerRosterDirty = computed(() => JSON.stringify(speakerRoster) !== savedSpeakerRoster.value)
const speakerOptions = computed(() => [...new Set([speakerRoster.selfName, ...speakerParticipants.value].filter(Boolean))])
const liveElapsedSeconds = ref(0)
const liveElapsedLabel = computed(() => `${String(Math.floor(liveElapsedSeconds.value / 60)).padStart(2, '0')}:${String(liveElapsedSeconds.value % 60).padStart(2, '0')}`)
const meetingContent = ref({})
const generatingContent = ref('')
const meetingContentSections = [
  { kind: 'topics', title: 'Bahasan rapat', empty: 'Buat bahasan dari agenda rapat.' },
  { kind: 'questions', title: 'Pertanyaan rapat', empty: 'Buat pertanyaan dari agenda dan transkrip yang tersedia.' },
  { kind: 'analysis', title: 'Analisis hasil rapat', empty: 'Simpan transkrip sebelum membuat analisis.' },
]
let audioCapture = null
let transcriptConnections = {}
let readySources = new Set()
let captureStartedAt = 0
let elapsedTimer = null
let saveQueue = Promise.resolve()
let stopPromise = null
let pendingRemoteSpeaker = ''

function formatLiveOffset(offset) {
  const seconds = Math.floor(Number(offset || 0) / 1000)
  return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`
}

function meetingText(content) {
  return content.replace(/^#{1,6}\s+/gm, '').replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*\n]+)\*/g, '$1')
}

async function loadMeetingWorkspace(meetingId) {
  transcriptStatus.value = ''
  transcriptSegments.value = []
  meetingContent.value = {}
  speakerRoster.selfName = ''
  speakerRoster.participantsText = ''
  speakerParticipants.value = []
  activeRemoteSpeaker.value = ''
  savedSpeakerRoster.value = ''
  if (!meetingId) return
  liveStarted.value = meetings.value.find((meeting) => meeting.id === meetingId)?.status === 'in_progress'
  try {
    const [segments, content, speakers] = await Promise.all([
      call('crm.api.committee.get_live_transcript', { meeting: meetingId }),
      call('crm.api.committee.get_meeting_content', { meeting: meetingId }),
      call('crm.api.committee.get_meeting_speakers', { meeting: meetingId }),
    ])
    if (liveMeetingId.value !== meetingId) return
    transcriptSegments.value = segments || []
    meetingContent.value = content || {}
    speakerRoster.selfName = speakers.self_name || ''
    speakerParticipants.value = speakers.participants || []
    speakerRoster.participantsText = speakerParticipants.value.join('\n')
    activeRemoteSpeaker.value = speakerParticipants.value.length === 1 ? speakerParticipants.value[0] : ''
    savedSpeakerRoster.value = speakers.configured ? JSON.stringify(speakerRoster) : ''
  } catch {
    if (liveMeetingId.value === meetingId) transcriptStatus.value = 'Data rapat belum dapat dimuat. Pilih rapat kembali untuk mencoba lagi.'
  }
}

watch(liveMeetingId, loadMeetingWorkspace)

async function saveSpeakerRoster() {
  if (!liveMeetingId.value || savingSpeakerRoster.value) return
  const meetingId = liveMeetingId.value
  savingSpeakerRoster.value = true
  try {
    const result = await call('crm.api.committee.set_meeting_speakers', {
      meeting: meetingId,
      self_name: speakerRoster.selfName,
      participants: JSON.stringify(speakerRoster.participantsText.split('\n').map((name) => name.trim()).filter(Boolean)),
    })
    if (liveMeetingId.value !== meetingId) return
    speakerRoster.selfName = result.self_name
    speakerParticipants.value = result.participants
    speakerRoster.participantsText = result.participants.join('\n')
    if (!speakerParticipants.value.includes(activeRemoteSpeaker.value)) activeRemoteSpeaker.value = speakerParticipants.value.length === 1 ? speakerParticipants.value[0] : ''
    savedSpeakerRoster.value = JSON.stringify(speakerRoster)
    transcriptStatus.value = ''
  } catch (error) {
    transcriptStatus.value = error?.message || 'Nama pembicara belum tersimpan. Coba lagi.'
  } finally {
    savingSpeakerRoster.value = false
  }
}

async function generateMeetingContent(kind) {
  if (!liveMeetingId.value || generatingContent.value) return
  const meetingId = liveMeetingId.value
  generatingContent.value = kind
  try {
    const result = await call('crm.api.committee.generate_meeting_content', { meeting: meetingId, kind })
    if (liveMeetingId.value === meetingId) meetingContent.value = { ...meetingContent.value, [kind]: result }
  } catch {
    if (liveMeetingId.value === meetingId) transcriptStatus.value = 'Hasil rapat belum dapat dibuat. Coba lagi beberapa saat.'
  } finally {
    generatingContent.value = ''
  }
}

async function startLiveMeeting(meetingId) {
  try {
    await call('crm.api.committee.set_meeting_status', { meeting: meetingId, status: 'In Progress' })
    await loadMeetings()
  } catch (error) {
    showToast(error?.message || 'Meeting could not be started')
    return
  }
  liveMeetingId.value = meetingId
  liveAgendaIdx.value = 0
  liveStarted.value = true
  activeTab.value = 'live'
  transcriptStatus.value = ''
}

async function startTranscription() {
  if (capturing.value || startingCapture.value || !liveMeetingId.value || !liveStarted.value) return
  if (speakerRosterDirty.value) {
    transcriptStatus.value = 'Simpan nama pembicara sebelum mulai menangkap audio.'
    return
  }
  transcriptStatus.value = ''
  startingCapture.value = true
  const meetingId = liveMeetingId.value
  try {
    audioCapture = await startMeetingAudioCapture({
      onFrame(source, buffer) {
        if (!readySources.has(source)) return
        try {
          transcriptConnections[source]?.send({ audioBase64: pcmFrameToBase64(buffer) })
        } catch {
          transcriptStatus.value = 'Aliran audio terputus. Mulai tangkap kembali.'
          stopTranscription()
        }
      },
      onEnded() {
        transcriptStatus.value = 'Berbagi tab dihentikan. Transkrip sedang disimpan.'
        stopTranscription()
      },
    })
    microphoneAvailable.value = audioCapture.microphoneAvailable
    microphoneEnabled.value = audioCapture.microphoneAvailable
    const sources = microphoneAvailable.value ? ['meeting', 'mic'] : ['meeting']
    const tokens = await Promise.all(sources.map(() => call('crm.api.committee.create_live_transcript_token', { meeting: meetingId })))
    captureStartedAt = Date.now()
    for (const [index, source] of sources.entries()) {
      const connection = Scribe.connect({
        token: tokens[index].token,
        modelId: 'scribe_v2_realtime',
        commitStrategy: CommitStrategy.VAD,
        languageCode: 'id',
        audioFormat: AudioFormat.PCM_16000,
        sampleRate: 16000,
      })
      transcriptConnections[source] = connection
      connection.on(RealtimeEvents.OPEN, () => readySources.add(source))
      connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, ({ text }) => {
        if (source === 'meeting' && text && !partialTranscript.meeting) pendingRemoteSpeaker = activeRemoteSpeaker.value
        partialTranscript[source] = text || ''
      })
      connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, ({ text }) => {
        partialTranscript[source] = ''
        if (!text?.trim()) return
        const offset_ms = Date.now() - captureStartedAt
        const speaker = source === 'meeting' ? (pendingRemoteSpeaker || activeRemoteSpeaker.value) : ''
        if (source === 'meeting') pendingRemoteSpeaker = ''
        saveQueue = saveQueue.then(async () => {
          const saved = await call('crm.api.committee.save_live_transcript_segment', { meeting: meetingId, text, source, offset_ms, speaker })
          if (liveMeetingId.value === meetingId) transcriptSegments.value.push(saved)
        }).catch(() => { transcriptStatus.value = 'Sebagian transkrip gagal disimpan. Periksa koneksi lalu mulai ulang.' })
      })
      connection.on(RealtimeEvents.ERROR, () => {
        transcriptStatus.value = source === 'meeting' ? 'Audio rapat terputus. Mulai tangkap kembali.' : 'Mikrofon terputus; audio rapat tetap ditangkap.'
        if (source === 'meeting') stopTranscription()
      })
    }
    capturing.value = true
    liveElapsedSeconds.value = 0
    elapsedTimer = window.setInterval(() => { liveElapsedSeconds.value = Math.floor((Date.now() - captureStartedAt) / 1000) }, 1000)
    if (!microphoneAvailable.value) transcriptStatus.value = 'Mikrofon tidak diizinkan. Audio rapat tetap ditangkap.'
  } catch (error) {
    transcriptStatus.value = error?.message || 'Audio rapat belum dapat ditangkap. Coba lagi.'
    await stopTranscription()
  } finally {
    startingCapture.value = false
  }
}

function stopTranscription() {
  if (stopPromise) return stopPromise
  stopPromise = (async () => {
    capturing.value = false
    window.clearInterval(elapsedTimer)
    elapsedTimer = null
    readySources.clear()
    const capture = audioCapture
    audioCapture = null
    try { await capture?.stop() } catch { /* Continue closing transcript connections. */ }
    const connections = Object.values(transcriptConnections)
    transcriptConnections = {}
    await Promise.all(connections.map((connection) => new Promise((resolve) => {
      let finished = false
      const finish = () => {
        if (finished) return
        finished = true
        try { connection.close() } finally { resolve() }
      }
      const timeout = window.setTimeout(finish, 2000)
      connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, () => {
        window.clearTimeout(timeout)
        window.setTimeout(finish, 300)
      })
      try { connection.commit() } catch { window.clearTimeout(timeout); finish() }
    })))
    await saveQueue
    partialTranscript.meeting = ''
    partialTranscript.mic = ''
    pendingRemoteSpeaker = ''
  })().finally(() => { stopPromise = null })
  return stopPromise
}

async function setTranscriptSpeaker(index, event) {
  if (!liveMeetingId.value || !event.target.value) return
  const meetingId = liveMeetingId.value
  const previous = transcriptSegments.value[index]?.speaker
  const speaker = event.target.value
  saveQueue = saveQueue.then(async () => {
    const segment = await call('crm.api.committee.set_live_transcript_speaker', { meeting: meetingId, index, speaker })
    if (liveMeetingId.value === meetingId) transcriptSegments.value[index] = segment
  }).catch(() => {
    event.target.value = speakerOptions.value.includes(previous) ? previous : ''
    transcriptStatus.value = 'Nama pembicara belum tersimpan. Coba lagi.'
  })
  await saveQueue
}

function toggleMicrophone() {
  microphoneEnabled.value = !microphoneEnabled.value
  audioCapture?.setMicrophoneEnabled(microphoneEnabled.value)
}

async function toggleTranscriptBookmark(index) {
  if (!liveMeetingId.value) return
  const meetingId = liveMeetingId.value
  const bookmarked = !transcriptSegments.value[index]?.bookmarked
  saveQueue = saveQueue.then(async () => {
    const segment = await call('crm.api.committee.set_live_transcript_bookmark', { meeting: meetingId, index, bookmarked })
    if (liveMeetingId.value === meetingId) transcriptSegments.value[index] = segment
  }).catch(() => { transcriptStatus.value = 'Penanda belum tersimpan. Coba lagi.' })
  await saveQueue
}

async function endLiveMeeting() {
  await stopTranscription()
  try {
    await call('crm.api.committee.set_meeting_status', { meeting: liveMeetingId.value, status: 'Completed' })
    await loadMeetings()
  } catch (error) {
    showToast(error?.message || 'Meeting could not be completed')
    return
  }
  liveStarted.value = false
}

function nextLiveItem() {
  const items = agendaItems.value.filter((a) => a.meetingId === liveMeetingId.value)
  if (liveAgendaIdx.value < items.length - 1) {
    liveAgendaIdx.value++
  } else {
    showToast('Ini agenda terakhir. Akhiri sesi setelah pembahasan selesai.')
  }
}

const liveCurrentMeeting = computed(() => meetings.value.find((m) => m.id === liveMeetingId.value))
const queueItems = ref([])
const queueKPIs = computed(() => [
  { label: 'Pending Cases', value: String(queueItems.value.length), sub: 'Awaiting committee', color: 'text-amber-600' },
  { label: 'In Session', value: String(meetings.value.filter((m) => m.status === 'in_progress').length), sub: 'Active meetings', color: 'text-[#980000]' },
  { label: 'Approved', value: String(decisionsList.value.filter((d) => d.outcome === 'Approved').length), sub: 'Recorded decisions', color: 'text-green-600' },
  { label: 'Rejected', value: String(decisionsList.value.filter((d) => d.outcome === 'Rejected').length), sub: 'Recorded decisions', color: 'text-red-600' },
])

async function loadQueue() {
  try {
    const rows = await call('crm.api.committee.get_queue')
    queueItems.value = (rows || []).map((item) => ({
      id: item.name,
      caseId: item.name,
      applicant: item.applicant_name || item.application || item.name,
      facility: item.facility_type || '',
      amount: item.requested_amount == null ? '—' : new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(item.requested_amount),
      committee: item.committee,
      slaDue: item.sla_due || '—',
      slaBreached: item.sla_state === 'breached',
      priority: item.sla_state === 'breached' ? 'urgent' : item.sla_state === 'amber' ? 'high' : 'normal',
      status: item.status === 'Pending' ? 'pending' : 'in_session',
      rm: '',
      myVote: item.my_vote?.decision?.toLowerCase() || null,
      voteComment: '',
      voted: !!item.my_vote,
      aiScore: null,
      aiRec: '',
      aiReason: '',
      metrics: [],
      documents: [],
    }))
  } catch {
    showToast('Committee queue could not be loaded')
  }
}

onMounted(() => { loadQueue(); loadDecisions() })

const filteredQueue = computed(() => {
  return queueItems.value.filter((item) => {
    if (queueSearch.value && !item.applicant.toLowerCase().includes(queueSearch.value.toLowerCase()) && !item.caseId.toLowerCase().includes(queueSearch.value.toLowerCase())) return false
    if (queueFilterType.value && item.committee !== queueFilterType.value) return false
    if (queueFilterStatus.value && item.status !== queueFilterStatus.value) return false
    if (queueFilterPriority.value && item.priority !== queueFilterPriority.value) return false
    return true
  })
})

const meetings = ref([])

async function loadMeetings() {
  try {
    const rows = await call('crm.api.committee.list_meetings')
    meetings.value = (rows || []).map((m) => {
      const date = new Date(m.scheduled_at)
      return {
        id: m.name,
        scheduledAt: m.scheduled_at,
        title: m.title,
        committee: m.committee,
        day: String(date.getDate()),
        month: date.toLocaleString('en-US', { month: 'short' }).toUpperCase(),
        time: date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
        location: m.location || '',
        color: 'bg-[#980000]',
        status: m.status === 'In Progress' ? 'in_progress' : m.status?.toLowerCase() || 'scheduled',
        cases: m.agenda?.length || 0,
        members: Array.isArray(m.attendees) ? m.attendees.map((a) => typeof a === 'string' ? { name: a, role: '', confirmed: false } : { name: a.name || a.user || '', role: a.role || '', confirmed: a.response === 'yes' }) : [],
        agenda: (m.agenda || []).map((a) => typeof a === 'string' ? a : a.item || a.title || ''),
      }
    })
    agendaItems.value = meetings.value.flatMap((meeting) => meeting.agenda.map((item, index) => ({
      id: `${meeting.id}-${index}`,
      meetingId: meeting.id,
      order: index + 1,
      caseId: '',
      applicant: item,
      timebox: 15,
      attachments: [],
    })))
    liveMeetingId.value ||= meetings.value[0]?.id || null
  } catch {
    showToast('Meetings could not be loaded')
  }
}

onMounted(loadMeetings)

const committees = ref([])

async function loadCommittees() {
  try {
    const rows = await call('crm.api.committee.list_committees')
    committees.value = (rows || []).map((c) => ({
      id: c.name,
      name: c.committee_name,
      code: c.name,
      description: c.description || '',
      authority: '',
      quorumPct: c.quorum_pct,
      quorum: Math.ceil((c.members?.length || 0) * (c.quorum_pct || 0) / 100),
      sla: '',
      approvalRule: c.majority_rule,
      chairTieBreak: !!c.chairman_tie_break,
      members: (c.members || []).map((m) => m.member_name || m.member),
    }))
  } catch {
    showToast('Committees could not be loaded')
  }
}

onMounted(loadCommittees)

const calendarCells = computed(() => {
  const cells = []
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const firstDay = new Date(year, month, 1).getDay()
  const lastDay = new Date(year, month + 1, 0).getDate()
  const meetingDays = new Set(meetings.value.map((meeting) => new Date(meeting.scheduledAt)).filter((date) => date.getFullYear() === year && date.getMonth() === month).map((date) => date.getDate()))
  for (let i = 0; i < firstDay; i++) cells.push({ key: 'pre' + i, day: '', hasEvent: false, today: false })
  for (let d = 1; d <= lastDay; d++) {
    cells.push({ key: d, day: d, hasEvent: meetingDays.has(d), today: d === now.getDate() })
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
    in_session: 'px-2 py-0.5 bg-[#980000]/10 text-[#980000] rounded text-xs font-medium',
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
  const colors = ['bg-[#980000]', 'bg-blue-500', 'bg-green-500', 'bg-amber-500', 'bg-red-500', 'bg-indigo-500', 'bg-pink-500', 'bg-[#980000]']
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
    members: session?.members || [],
    cases: queueItems.value.filter((q) => ['pending', 'in_session'].includes(q.status)),
    votedCount: 0,
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

async function castVote(cas, vote) {
  if (!voteSignatureAck.value) return showToast('Confirm your electronic signature before voting')
  const decision = { approve: 'Approve', reject: 'Reject', defer: 'Refer Back' }[vote]
  try {
    await call('crm.api.committee.submit_vote', {
      item: cas.id,
      decision,
      comment: cas.voteComment,
      signature_ack: 1,
    })
    voteSignatureAck.value = false
    showToast('Vote recorded')
    await loadQueue()
    await loadDecisions()
  } catch (error) {
    showToast(error?.message || 'Vote could not be recorded')
  }
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
    { label: 'Risk Score', value: cas.aiScore == null ? '—' : cas.aiScore + '/100' },
  ]
}

async function saveMeeting() {
  if (!meetingForm.title.trim() || !meetingForm.committee || !meetingForm.date || !meetingForm.time) {
    showToast('Title, committee, date, and time are required')
    return
  }
  try {
    await call('crm.api.committee.create_meeting', {
      title: meetingForm.title.trim(),
      committee: meetingForm.committee,
      scheduled_at: `${meetingForm.date} ${meetingForm.time}:00`,
      location: meetingForm.location,
      agenda: JSON.stringify(meetingForm.agenda.split('\n').map((item) => item.trim()).filter(Boolean).map((item) => ({ item }))),
    })
    showScheduleModal.value = false
    Object.assign(meetingForm, { title: '', committee: '', date: '', time: '', location: '', agenda: '' })
    await loadMeetings()
    showToast('Meeting scheduled')
  } catch (error) {
    showToast(error?.message || 'Meeting could not be scheduled')
  }
}

async function saveCommittee() {
  const f = committeeForm.value
  if (!f.name) {
    showToast('Committee name is required')
    return
  }
  const members = f.members.filter((m) => m.name && m.name.trim())
  try {
    await call('crm.api.committee.upsert_committee', {
      committee_name: f.name,
      quorum_pct: f.quorumPct,
      majority_rule: f.approvalRule,
      chairman_tie_break: Number(f.chairTieBreak),
      description: f.description,
      members: JSON.stringify(members.map((m) => ({ member: m.name, role: m.role, weight: m.weight }))),
    })
    await loadCommittees()
    closeSetupModal()
    showToast('Committee saved')
  } catch (error) {
    showToast(error?.message || 'Committee could not be saved')
  }
}

function fmtDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return isNaN(dt) ? '' : dt.toLocaleDateString()
}

function showToast(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 3000)
}
</script>
