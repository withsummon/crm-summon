<template>
  <div class="committee-approval flex flex-col h-full bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-purple-600 flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">Committee Approval System</h1>
            <p class="text-sm text-gray-500">Multi-level credit committee voting &amp; decision management</p>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            @click="showScheduleModal = true"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            Schedule Meeting
          </button>
          <button
            @click="showSetupModal = true"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
            New Committee
          </button>
        </div>
      </div>

      <!-- Page Tabs -->
      <div class="flex gap-1 mt-4">
        <button
          v-for="tab in pageTabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
            activeTab === tab.id
              ? 'bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
              : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400'
          ]"
        >
          {{ tab.label }}
          <span v-if="tab.badge" class="px-1.5 py-0.5 text-xs bg-purple-600 text-white rounded-full">{{ tab.badge }}</span>
        </button>
      </div>
    </div>

    <!-- Body -->
    <div class="flex-1 overflow-auto p-6">

      <!-- ───── TAB: Queue ───── -->
      <div v-if="activeTab === 'queue'">
        <!-- KPI Strip -->
        <div class="grid grid-cols-5 gap-4 mb-6">
          <div v-for="kpi in queueKPIs" :key="kpi.label" class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <p class="text-xs text-gray-500 mb-1">{{ kpi.label }}</p>
            <p class="text-2xl font-bold" :class="kpi.color">{{ kpi.value }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ kpi.sub }}</p>
          </div>
        </div>

        <!-- Filters -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 mb-4 p-4">
          <div class="flex gap-3 flex-wrap items-center">
            <input v-model="queueSearch" type="text" placeholder="Search applicant, facility..." class="flex-1 min-w-48 px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
            <select v-model="queueFilterType" class="px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
              <option value="">All Committees</option>
              <option value="CC1">CC-1 (≤ Rp 10B)</option>
              <option value="CC2">CC-2 (≤ Rp 50B)</option>
              <option value="CC3">CC-3 (&gt; Rp 50B)</option>
            </select>
            <select v-model="queueFilterStatus" class="px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="in_session">In Session</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="deferred">Deferred</option>
            </select>
            <select v-model="queueFilterPriority" class="px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
              <option value="">All Priority</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="normal">Normal</option>
            </select>
          </div>
        </div>

        <!-- Queue Table -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Case</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Applicant</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Facility</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Amount</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Committee</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">SLA</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Priority</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr
                v-for="item in filteredQueue"
                :key="item.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer"
                @click="openCaseDetail(item)"
              >
                <td class="px-4 py-3">
                  <span class="font-mono text-xs text-purple-700 font-semibold">{{ item.caseId }}</span>
                </td>
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900 dark:text-white">{{ item.applicant }}</div>
                  <div class="text-xs text-gray-500">RM: {{ item.rm }}</div>
                </td>
                <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ item.facility }}</td>
                <td class="px-4 py-3 text-right font-semibold text-gray-900 dark:text-white">{{ item.amount }}</td>
                <td class="px-4 py-3">
                  <span class="px-2 py-0.5 rounded text-xs font-semibold bg-purple-100 text-purple-700">{{ item.committee }}</span>
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
                    class="px-3 py-1 bg-purple-600 text-white rounded text-xs font-medium hover:bg-purple-700"
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
      <div v-if="activeTab === 'meetings'" class="space-y-4">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">Scheduled Committee Meetings</h2>
          <div class="flex gap-2">
            <button @click="meetingView = 'list'" :class="['px-3 py-1 rounded text-sm', meetingView==='list' ? 'bg-purple-600 text-white' : 'bg-white border text-gray-600']">List</button>
            <button @click="meetingView = 'calendar'" :class="['px-3 py-1 rounded text-sm', meetingView==='calendar' ? 'bg-purple-600 text-white' : 'bg-white border text-gray-600']">Calendar</button>
          </div>
        </div>

        <!-- Meeting Cards -->
        <div v-if="meetingView === 'list'" class="space-y-3">
          <div
            v-for="mtg in meetings"
            :key="mtg.id"
            class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-4">
                <div :class="['w-12 h-12 rounded-xl flex flex-col items-center justify-center text-white text-xs font-bold', mtg.color]">
                  <span class="text-lg leading-none">{{ mtg.day }}</span>
                  <span>{{ mtg.month }}</span>
                </div>
                <div>
                  <div class="font-semibold text-gray-900 dark:text-white text-base">{{ mtg.title }}</div>
                  <div class="text-sm text-gray-500 mt-0.5">{{ mtg.time }} · {{ mtg.location }}</div>
                  <div class="flex gap-2 mt-2 flex-wrap">
                    <span class="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">{{ mtg.committee }}</span>
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
                  class="px-4 py-1.5 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700"
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
              </div>
            </div>

            <!-- Members -->
            <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
              <p class="text-xs text-gray-500 mb-2 uppercase tracking-wide font-semibold">Committee Members</p>
              <div class="flex gap-2 flex-wrap">
                <div
                  v-for="member in mtg.members"
                  :key="member.name"
                  class="flex items-center gap-2 px-3 py-1.5 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white', avatarColor(member.name)]">
                    {{ member.name.charAt(0) }}
                  </div>
                  <span class="text-xs text-gray-700 dark:text-gray-300">{{ member.name }}</span>
                  <span class="text-xs text-gray-400">·</span>
                  <span class="text-xs text-gray-500">{{ member.role }}</span>
                  <span v-if="member.confirmed" class="text-green-500 text-xs">✓</span>
                  <span v-else class="text-amber-500 text-xs">⏳</span>
                </div>
              </div>
            </div>

            <!-- Agenda Items -->
            <div class="mt-3">
              <p class="text-xs text-gray-500 mb-2 uppercase tracking-wide font-semibold">Agenda Items ({{ mtg.agenda.length }})</p>
              <div class="space-y-1">
                <div v-for="(item, idx) in mtg.agenda" :key="idx" class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <span class="w-5 h-5 rounded-full bg-purple-100 text-purple-700 text-xs flex items-center justify-center font-semibold">{{ idx + 1 }}</span>
                  {{ item }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Calendar View (simplified) -->
        <div v-else class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <div class="text-center mb-4">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white">May 2026</h3>
          </div>
          <div class="grid grid-cols-7 gap-1 text-center text-xs text-gray-500 mb-2">
            <div v-for="d in ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']" :key="d">{{ d }}</div>
          </div>
          <div class="grid grid-cols-7 gap-1">
            <div v-for="cell in calendarCells" :key="cell.key" :class="['aspect-square rounded-lg flex flex-col items-center justify-center text-sm', cell.today ? 'bg-purple-600 text-white font-bold' : cell.hasEvent ? 'bg-purple-100 text-purple-700 font-semibold cursor-pointer hover:bg-purple-200' : 'text-gray-500']">
              <span>{{ cell.day }}</span>
              <span v-if="cell.hasEvent" class="w-1.5 h-1.5 rounded-full bg-purple-600 mt-0.5" :class="cell.today ? 'bg-white' : ''"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Voting ───── -->
      <div v-if="activeTab === 'voting'">
        <!-- Active Session Banner -->
        <div v-if="activeSession" class="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6 flex items-center justify-between">
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
          <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <p class="text-gray-500 mb-4">No active session. Start a meeting from the Meetings tab.</p>
          <button @click="activeTab = 'meetings'" class="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm">View Meetings</button>
        </div>

        <div v-else class="grid grid-cols-3 gap-6">
          <!-- Case Navigator -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
              <p class="text-xs font-semibold text-gray-600 uppercase">Cases in Session</p>
            </div>
            <div class="divide-y divide-gray-100 dark:divide-gray-700">
              <div
                v-for="(cas, idx) in activeSession.cases"
                :key="cas.id"
                @click="activeSessionCaseIdx = idx"
                :class="['p-4 cursor-pointer', activeSessionCaseIdx === idx ? 'bg-purple-50 dark:bg-purple-900/20' : 'hover:bg-gray-50']"
              >
                <div class="flex justify-between items-start">
                  <div>
                    <p class="font-mono text-xs text-purple-700 font-semibold">{{ cas.caseId }}</p>
                    <p class="text-sm font-medium text-gray-900 dark:text-white mt-0.5">{{ cas.applicant }}</p>
                    <p class="text-xs text-gray-500">{{ cas.amount }}</p>
                  </div>
                  <span v-if="cas.voted" class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">Voted</span>
                  <span v-else class="px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs">Pending</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Voting Interface -->
          <div class="col-span-2 space-y-4">
            <div v-if="currentCase" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
              <!-- Case Header -->
              <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <div class="flex justify-between items-start">
                  <div>
                    <span class="font-mono text-sm text-purple-700 font-semibold">{{ currentCase.caseId }}</span>
                    <h2 class="text-lg font-bold text-gray-900 dark:text-white mt-1">{{ currentCase.applicant }}</h2>
                    <p class="text-sm text-gray-500">{{ currentCase.facility }} · RM: {{ currentCase.rm }}</p>
                  </div>
                  <div class="text-right">
                    <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ currentCase.amount }}</p>
                    <p class="text-xs text-gray-500">Requested Amount</p>
                  </div>
                </div>
              </div>

              <!-- Case Summary -->
              <div class="px-6 py-4 grid grid-cols-4 gap-4 border-b border-gray-100 dark:border-gray-700">
                <div v-for="metric in currentCase.metrics" :key="metric.label">
                  <p class="text-xs text-gray-500">{{ metric.label }}</p>
                  <p class="font-semibold text-sm" :class="metric.color || 'text-gray-900 dark:text-white'">{{ metric.value }}</p>
                </div>
              </div>

              <!-- AI Recommendation -->
              <div class="px-6 py-3 bg-blue-50 dark:bg-blue-900/20 flex items-start gap-3 border-b border-blue-100">
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
                <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Cast Your Vote</p>
                <div class="grid grid-cols-3 gap-3 mb-5">
                  <button
                    @click="castVote(currentCase, 'approve')"
                    :class="['py-3 rounded-xl border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'approve' ? 'border-green-500 bg-green-50 text-green-700' : 'border-gray-200 hover:border-green-300 text-gray-600']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                    Approve
                  </button>
                  <button
                    @click="castVote(currentCase, 'reject')"
                    :class="['py-3 rounded-xl border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'reject' ? 'border-red-500 bg-red-50 text-red-700' : 'border-gray-200 hover:border-red-300 text-gray-600']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    Reject
                  </button>
                  <button
                    @click="castVote(currentCase, 'defer')"
                    :class="['py-3 rounded-xl border-2 text-sm font-semibold transition-all flex flex-col items-center gap-1', currentCase.myVote === 'defer' ? 'border-amber-500 bg-amber-50 text-amber-700' : 'border-gray-200 hover:border-amber-300 text-gray-600']"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    Defer
                  </button>
                </div>

                <textarea v-model="currentCase.voteComment" rows="2" placeholder="Voting remarks (optional)..." class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none mb-4"></textarea>

                <!-- Vote Tally -->
                <div>
                  <p class="text-xs font-semibold text-gray-600 uppercase mb-3">Current Tally</p>
                  <div class="space-y-2">
                    <div v-for="member in activeSession.members" :key="member.name" class="flex items-center gap-3">
                      <div :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0', avatarColor(member.name)]">
                        {{ member.name.charAt(0) }}
                      </div>
                      <span class="text-sm text-gray-700 dark:text-gray-300 flex-1">{{ member.name }}</span>
                      <span class="text-xs text-gray-500">{{ member.role }}</span>
                      <span v-if="member.vote" :class="['px-2 py-0.5 rounded text-xs font-semibold', member.vote === 'approve' ? 'bg-green-100 text-green-700' : member.vote === 'reject' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700']">
                        {{ member.vote }}
                      </span>
                      <span v-else class="px-2 py-0.5 bg-gray-100 text-gray-400 rounded text-xs">Pending</span>
                    </div>
                  </div>
                </div>

                <!-- Quorum Progress -->
                <div class="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div class="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1.5">
                    <span>Quorum Progress</span>
                    <span>{{ activeSession.votedCount }}/{{ activeSession.members.length }} voted · need {{ activeSession.quorum }}</span>
                  </div>
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-purple-500 rounded-full transition-all" :style="{ width: (activeSession.votedCount / activeSession.members.length * 100) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Committees ───── -->
      <div v-if="activeTab === 'committees'" class="space-y-4">
        <div class="grid grid-cols-3 gap-4">
          <div
            v-for="committee in committees"
            :key="committee.id"
            class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5"
          >
            <div class="flex justify-between items-start mb-3">
              <div>
                <h3 class="font-bold text-gray-900 dark:text-white">{{ committee.name }}</h3>
                <p class="text-xs text-gray-500 mt-0.5">{{ committee.code }}</p>
              </div>
              <span class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium">Active</span>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mb-3">{{ committee.description }}</div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">Authority</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ committee.authority }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Quorum</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ committee.quorum }} members</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">SLA</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ committee.sla }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Approval Rule</span>
                <span class="font-medium text-gray-900 dark:text-white">{{ committee.approvalRule }}</span>
              </div>
            </div>
            <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
              <p class="text-xs text-gray-500 mb-2">Members ({{ committee.members.length }})</p>
              <div class="flex -space-x-1">
                <div
                  v-for="m in committee.members.slice(0,5)"
                  :key="m"
                  :class="['w-7 h-7 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white', avatarColor(m)]"
                  :title="m"
                >
                  {{ m.charAt(0) }}
                </div>
                <div v-if="committee.members.length > 5" class="w-7 h-7 rounded-full border-2 border-white bg-gray-200 flex items-center justify-center text-xs text-gray-600 font-semibold">
                  +{{ committee.members.length - 5 }}
                </div>
              </div>
            </div>
            <div class="flex gap-2 mt-4">
              <button class="flex-1 py-1.5 border border-gray-300 rounded text-xs text-gray-600 hover:bg-gray-50">Edit</button>
              <button class="flex-1 py-1.5 border border-purple-300 text-purple-600 rounded text-xs hover:bg-purple-50">Members</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ───── TAB: Analytics ───── -->
      <div v-if="activeTab === 'analytics'">
        <!-- KPI Row -->
        <div class="grid grid-cols-4 gap-4 mb-6">
          <div v-for="kpi in analyticsKPIs" :key="kpi.label" class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <p class="text-xs text-gray-500 mb-1">{{ kpi.label }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ kpi.value }}</p>
            <p :class="['text-xs mt-1', kpi.trend >= 0 ? 'text-green-600' : 'text-red-600']">{{ kpi.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(kpi.trend) }}% vs last month</p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <!-- Approval Rate by Committee -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Approval Rate by Committee</h3>
            <div class="space-y-4">
              <div v-for="row in approvalByCommittee" :key="row.name">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-gray-700 dark:text-gray-300">{{ row.name }}</span>
                  <span class="font-semibold text-gray-900 dark:text-white">{{ row.rate }}%</span>
                </div>
                <div class="flex gap-1 h-3 rounded-full overflow-hidden">
                  <div class="bg-green-500 rounded-full" :style="{ width: row.approvedPct + '%' }"></div>
                  <div class="bg-red-400" :style="{ width: row.rejectedPct + '%' }"></div>
                  <div class="bg-amber-400" :style="{ width: row.deferredPct + '%' }"></div>
                </div>
                <div class="flex gap-4 text-xs text-gray-400 mt-1">
                  <span>✓ {{ row.approved }}</span>
                  <span>✗ {{ row.rejected }}</span>
                  <span>⏳ {{ row.deferred }}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-4 mt-4 text-xs text-gray-500">
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-green-500 inline-block"></span>Approved</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-400 inline-block"></span>Rejected</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-400 inline-block"></span>Deferred</span>
            </div>
          </div>

          <!-- TAT Distribution -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">TAT Distribution (Days)</h3>
            <div class="space-y-3">
              <div v-for="bucket in tatBuckets" :key="bucket.label" class="flex items-center gap-3">
                <span class="text-xs text-gray-500 w-20">{{ bucket.label }}</span>
                <div class="flex-1 h-6 bg-gray-100 rounded overflow-hidden">
                  <div :class="['h-full rounded flex items-center px-2 text-xs text-white font-medium', bucket.color]" :style="{ width: (bucket.count / 50 * 100) + '%' }">
                    {{ bucket.count }}
                  </div>
                </div>
                <span class="text-xs text-gray-400 w-12 text-right">{{ bucket.pct }}%</span>
              </div>
            </div>
          </div>

          <!-- Member Participation -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Member Participation</h3>
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-100 dark:border-gray-700">
                  <th class="text-left pb-2 text-xs text-gray-500">Member</th>
                  <th class="text-center pb-2 text-xs text-gray-500">Meetings</th>
                  <th class="text-center pb-2 text-xs text-gray-500">Attendance</th>
                  <th class="text-center pb-2 text-xs text-gray-500">Votes</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50 dark:divide-gray-700">
                <tr v-for="member in memberParticipation" :key="member.name">
                  <td class="py-2">
                    <div class="flex items-center gap-2">
                      <div :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white', avatarColor(member.name)]">{{ member.name.charAt(0) }}</div>
                      <span class="text-gray-700 dark:text-gray-300">{{ member.name }}</span>
                    </div>
                  </td>
                  <td class="py-2 text-center text-gray-600">{{ member.meetings }}</td>
                  <td class="py-2 text-center">
                    <span :class="['font-semibold', member.attendance >= 90 ? 'text-green-600' : member.attendance >= 70 ? 'text-amber-600' : 'text-red-600']">{{ member.attendance }}%</span>
                  </td>
                  <td class="py-2 text-center text-gray-600">{{ member.votes }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Monthly Volume -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Monthly Case Volume</h3>
            <div class="flex items-end gap-2 h-32">
              <div v-for="bar in monthlyVolume" :key="bar.month" class="flex-1 flex flex-col items-center gap-1">
                <span class="text-xs text-gray-500">{{ bar.count }}</span>
                <div class="w-full bg-purple-500 rounded-t" :style="{ height: (bar.count / 25 * 100) + '%' }"></div>
                <span class="text-xs text-gray-400">{{ bar.month }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ───── MODALS ───── -->

    <!-- Schedule Meeting Modal -->
    <div v-if="showScheduleModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showScheduleModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-5">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">Schedule Committee Meeting</h2>
          <button @click="showScheduleModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Committee</label>
            <select class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
              <option>Credit Committee Level 1 (CC-1)</option>
              <option>Credit Committee Level 2 (CC-2)</option>
              <option>Risk Management Committee (RMC)</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date</label>
              <input type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Time</label>
              <input type="time" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Location / Room</label>
            <input type="text" placeholder="e.g. BNI HQ - Board Room 3" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Agenda Notes</label>
            <textarea rows="3" placeholder="Meeting agenda..." class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showScheduleModal = false" class="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">Cancel</button>
          <button @click="saveMeeting" class="flex-1 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700">Schedule Meeting</button>
        </div>
      </div>
    </div>

    <!-- Committee Setup Modal -->
    <div v-if="showSetupModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showSetupModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-5">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">Create New Committee</h2>
          <button @click="showSetupModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Committee Name</label>
            <input type="text" placeholder="e.g. Credit Committee Level 3" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Code</label>
              <input type="text" placeholder="CC-3" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Quorum Required</label>
              <input type="number" value="3" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Credit Authority</label>
            <input type="text" placeholder="e.g. > Rp 50 Billion" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Approval Rule</label>
            <select class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
              <option>Simple Majority (>50%)</option>
              <option>Supermajority (≥2/3)</option>
              <option>Unanimous</option>
              <option>Chair Casts Deciding Vote</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">SLA (days)</label>
            <input type="number" value="5" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showSetupModal = false" class="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">Cancel</button>
          <button @click="saveCommittee" class="flex-1 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700">Create Committee</button>
        </div>
      </div>
    </div>

    <!-- Case Detail Modal -->
    <div v-if="showCaseModal && selectedCase" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCaseModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-2xl p-6 shadow-2xl max-h-[85vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-5">
          <div>
            <span class="font-mono text-sm text-purple-700 font-semibold">{{ selectedCase.caseId }}</span>
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ selectedCase.applicant }}</h2>
          </div>
          <button @click="showCaseModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="grid grid-cols-2 gap-4 mb-5">
          <div v-for="f in caseDetailFields(selectedCase)" :key="f.label" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
            <p class="text-xs text-gray-500 mb-0.5">{{ f.label }}</p>
            <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ f.value }}</p>
          </div>
        </div>
        <div class="mb-4">
          <p class="text-xs font-semibold text-gray-600 uppercase mb-2">Supporting Documents</p>
          <div class="space-y-1">
            <div v-for="doc in selectedCase.documents" :key="doc" class="flex items-center gap-2 text-sm text-blue-600 cursor-pointer hover:underline">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              {{ doc }}
            </div>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="showCaseModal = false; openVoting(selectedCase)" class="flex-1 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium">Open Voting</button>
          <button @click="showCaseModal = false" class="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-600">Close</button>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <div v-if="toast" class="fixed bottom-6 right-6 bg-green-600 text-white px-5 py-3 rounded-xl shadow-lg text-sm font-medium z-50 flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
      {{ toast }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

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

const pageTabs = [
  { id: 'queue', label: 'Case Queue', badge: 8 },
  { id: 'meetings', label: 'Meetings' },
  { id: 'voting', label: 'Voting' },
  { id: 'committees', label: 'Committees' },
  { id: 'analytics', label: 'Analytics' },
]

const queueKPIs = [
  { label: 'Pending Cases', value: '8', sub: 'Awaiting committee', color: 'text-amber-600' },
  { label: 'In Session', value: '3', sub: 'Active deliberation', color: 'text-purple-600' },
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
    color: 'bg-purple-600',
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
    normal: 'px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs',
  }[p] || 'px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs'
}

function statusBadge(s) {
  return {
    pending: 'px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs font-medium',
    in_session: 'px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-medium',
    approved: 'px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium',
    rejected: 'px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-medium',
    deferred: 'px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium',
  }[s] || 'px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs'
}

function statusLabel(s) {
  return { pending: 'Pending', in_session: 'In Session', approved: 'Approved', rejected: 'Rejected', deferred: 'Deferred' }[s] || s
}

function mtgStatusBadge(s) {
  return {
    upcoming: 'px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium',
    in_progress: 'px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-medium',
    completed: 'px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium',
  }[s] || 'px-2 py-1 bg-gray-100 text-gray-500 rounded text-xs'
}

function avatarColor(name) {
  const colors = ['bg-purple-500', 'bg-blue-500', 'bg-green-500', 'bg-amber-500', 'bg-red-500', 'bg-indigo-500', 'bg-pink-500', 'bg-teal-500']
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
  showSetupModal.value = false
  showToast('Committee created successfully')
}

function showToast(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 3000)
}
</script>
