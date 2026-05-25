<template>
  <div class="flex h-full min-h-0 flex-col">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px]" style="background: linear-gradient(135deg, #6366f1, #818cf8)">
            <LucideShield class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-crm-text">RBAC Administration</h1>
        </div>
      </template>
    </LayoutHeader>

    <div v-if="error" class="flex flex-1 items-center justify-center min-h-0">
      <div class="text-center">
        <LucideAlertCircle class="mx-auto h-12 w-12 text-red-400" />
        <p class="mt-3 text-sm text-crm-muted">{{ error }}</p>
        <button class="mt-4 rounded-lg bg-crm-purple px-4 py-2 text-sm font-medium text-white hover:bg-crm-purple/90" @click="fetchSummary">
          Retry
        </button>
      </div>
    </div>

    <div v-else class="flex-1 overflow-y-auto p-6 min-h-0">
      <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div v-for="i in 8" :key="i" class="h-24 animate-pulse rounded-[14px] bg-white shadow-sm" />
      </div>

      <div v-else>
        <div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-[14px] bg-white p-5 shadow-sm border border-crm-border">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-xs font-medium text-crm-muted uppercase tracking-wide">Roles</div>
                <div class="mt-1 text-2xl font-bold text-crm-text">{{ summary.roles?.total || 0 }}</div>
              </div>
              <div class="flex h-10 w-10 items-center justify-center rounded-[10px] bg-indigo-50">
                <LucideShieldCheck class="h-5 w-5 text-indigo-500" />
              </div>
            </div>
            <div class="mt-2 text-xs text-crm-muted">
              <span class="font-medium text-crm-purple">{{ summary.roles?.fcrm || 0 }}</span> FCRM roles
            </div>
          </div>

          <div class="rounded-[14px] bg-white p-5 shadow-sm border border-crm-border">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-xs font-medium text-crm-muted uppercase tracking-wide">Users</div>
                <div class="mt-1 text-2xl font-bold text-crm-text">{{ summary.users || 0 }}</div>
              </div>
              <div class="flex h-10 w-10 items-center justify-center rounded-[10px] bg-blue-50">
                <LucideUsers class="h-5 w-5 text-blue-500" />
              </div>
            </div>
          </div>

          <div class="rounded-[14px] bg-white p-5 shadow-sm border border-crm-border">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-xs font-medium text-crm-muted uppercase tracking-wide">Branches</div>
                <div class="mt-1 text-2xl font-bold text-crm-text">{{ summary.branches?.total || 0 }}</div>
              </div>
              <div class="flex h-10 w-10 items-center justify-center rounded-[10px] bg-emerald-50">
                <LucideBuilding2 class="h-5 w-5 text-emerald-500" />
              </div>
            </div>
            <div class="mt-2 text-xs text-crm-muted">
              <span class="font-medium text-crm-green">{{ summary.branches?.assignments || 0 }}</span> assignments
            </div>
          </div>

          <div class="rounded-[14px] bg-white p-5 shadow-sm border border-crm-border">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-xs font-medium text-crm-muted uppercase tracking-wide">Approvals</div>
                <div class="mt-1 text-2xl font-bold text-crm-text">{{ summary.approval_rules || 0 }}</div>
              </div>
              <div class="flex h-10 w-10 items-center justify-center rounded-[10px] bg-amber-50">
                <LucideFileSignature class="h-5 w-5 text-amber-500" />
              </div>
            </div>
          </div>
        </div>

        <h2 class="mb-4 text-base font-semibold text-crm-text">Management</h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <router-link
            v-for="card in managementCards"
            :key="card.route.name"
            :to="card.route"
            class="group rounded-[14px] bg-white p-5 shadow-sm border border-crm-border transition-all hover:shadow-md hover:border-crm-purple/20"
          >
            <div class="flex items-center gap-4">
              <div class="flex h-12 w-12 items-center justify-center rounded-[12px] transition-colors" :class="card.bgClass">
                <component :is="card.icon" class="h-6 w-6" :class="card.iconClass" />
              </div>
              <div>
                <div class="text-sm font-semibold text-crm-text group-hover:text-crm-purple transition-colors">
                  {{ card.title }}
                </div>
                <div class="mt-0.5 text-xs text-crm-muted">{{ card.description }}</div>
              </div>
            </div>
          </router-link>
        </div>

        <h2 class="mb-4 mt-8 text-base font-semibold text-crm-text">Recent Activity</h2>
        <div class="rounded-[14px] bg-white shadow-sm border border-crm-border overflow-hidden">
          <table v-if="summary.recent_audit_entries?.length" class="w-full text-sm">
            <thead>
              <tr class="border-b border-crm-border bg-crm-surface-light">
                <th class="px-4 py-3 text-left font-medium text-crm-muted">User</th>
                <th class="px-4 py-3 text-left font-medium text-crm-muted">Event</th>
                <th class="px-4 py-3 text-left font-medium text-crm-muted">Target</th>
                <th class="px-4 py-3 text-right font-medium text-crm-muted">Time</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in summary.recent_audit_entries" :key="entry.name" class="border-b border-crm-border/50 hover:bg-crm-surface-light transition-colors">
                <td class="px-4 py-3 font-medium text-crm-text">{{ entry.user }}</td>
                <td class="px-4 py-3">
                  <Badge :label="entry.event_type" variant="subtle" theme="blue" />
                </td>
                <td class="px-4 py-3 text-crm-muted">{{ entry.target_doctype || '-' }}</td>
                <td class="px-4 py-3 text-right text-crm-muted">{{ timeAgo(entry.timestamp) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="py-8 text-center text-sm text-crm-muted">
            No recent activity
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideShield from '~icons/lucide/shield'
import LucideShieldCheck from '~icons/lucide/shield-check'
import LucideUsers from '~icons/lucide/users'
import LucideBuilding2 from '~icons/lucide/building-2'
import LucideFileSignature from '~icons/lucide/file-signature'
import LucideUserCog from '~icons/lucide/user-cog'
import LucideKeyRound from '~icons/lucide/key-round'
import LucideShieldEllipsis from '~icons/lucide/shield-ellipsis'
import LucideGitBranch from '~icons/lucide/git-branch'
import LucideScale from '~icons/lucide/scale'
import LucideClock from '~icons/lucide/clock'
import LucideFileSearch from '~icons/lucide/file-search'
import LucideUserPlus from '~icons/lucide/user-plus'
import LucideListChecks from '~icons/lucide/list-checks'
import { Badge, call } from 'frappe-ui'
import { ref, onMounted } from 'vue'
import LucideAlertCircle from '~icons/lucide/alert-circle'

const loading = ref(true)
const error = ref('')
const summary = ref({})

const managementCards = [
  { title: 'Users', description: 'Manage user accounts and roles', route: { name: 'User List' }, icon: LucideUsers, bgClass: 'bg-blue-50', iconClass: 'text-blue-500' },
  { title: 'Roles', description: 'View and manage system roles', route: { name: 'Role List' }, icon: LucideShieldCheck, bgClass: 'bg-indigo-50', iconClass: 'text-indigo-500' },
  { title: 'Role Permissions', description: 'Configure DocType permissions per role', route: { name: 'Role Permissions' }, icon: LucideKeyRound, bgClass: 'bg-amber-50', iconClass: 'text-amber-500' },
  { title: 'User Permissions', description: 'Restrict document access by user', route: { name: 'User Permissions' }, icon: LucideShieldEllipsis, bgClass: 'bg-purple-50', iconClass: 'text-purple-500' },
  { title: 'Branches', description: 'Manage branch hierarchy and assignments', route: { name: 'RBAC Branches' }, icon: LucideGitBranch, bgClass: 'bg-emerald-50', iconClass: 'text-emerald-500' },
  { title: 'Approval Matrix', description: 'Configure Delegation of Authority rules', route: { name: 'RBAC Approval Matrix' }, icon: LucideFileSignature, bgClass: 'bg-rose-50', iconClass: 'text-rose-500' },
  { title: 'Field Permissions', description: 'Field-level visibility per role', route: { name: 'RBAC Field Permissions' }, icon: LucideUserCog, bgClass: 'bg-cyan-50', iconClass: 'text-cyan-500' },
  { title: 'Delegations', description: 'Temporary authority delegation', route: { name: 'RBAC Delegations' }, icon: LucideUserPlus, bgClass: 'bg-teal-50', iconClass: 'text-teal-500' },
  { title: 'SoD Rules', description: 'Segregation of Duties conflict matrix', route: { name: 'RBAC SoD' }, icon: LucideScale, bgClass: 'bg-orange-50', iconClass: 'text-orange-500' },
  { title: 'JIT Access', description: 'Just-in-Time elevated access requests', route: { name: 'RBAC JIT' }, icon: LucideClock, bgClass: 'bg-yellow-50', iconClass: 'text-yellow-600' },
  { title: 'Audit Trail', description: 'Permission change audit log', route: { name: 'Audit Trail' }, icon: LucideFileSearch, bgClass: 'bg-slate-50', iconClass: 'text-slate-500' },
  { title: 'RBAC Overview', description: 'Full RBAC system overview report', route: { name: 'RBAC Admin' }, icon: LucideListChecks, bgClass: 'bg-violet-50', iconClass: 'text-violet-500' },
]

async function fetchSummary() {
  loading.value = true
  error.value = ''
  try {
    const result = await call('crm.api.rbac.get_permission_summary')
    summary.value = result || {}
  } catch (err) {
    console.error('Error loading RBAC summary:', err)
    error.value = err?.messages?.[0] || err?.message || 'Failed to load RBAC summary'
  } finally {
    loading.value = false
  }
}

function timeAgo(dateStr) {
  if (!dateStr) return '-'
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

onMounted(fetchSummary)
</script>
