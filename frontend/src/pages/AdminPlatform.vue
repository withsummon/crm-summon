<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #7c3aed, #c084fc)"
          >
            <FeatherIcon name="shield" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Admin & Platform') }}
            </h1>
            <p class="truncate text-xs text-crm-muted">
              {{ __('Enterprise Control Center') }}
            </p>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <div
            v-if="maintenanceMode"
            class="flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700"
          >
            <span class="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-amber-500" />
            {{ __('Maintenance Mode Active') }}
          </div>
          <Button
            :label="__('Invite User')"
            variant="solid"
            @click="showInviteModal = true"
          />
          <Button
            icon="settings"
            variant="ghost"
            :title="__('System Settings')"
            @click="activeTab = 'platform'"
          />
        </div>
      </template>
    </LayoutHeader>

    <!-- Tabs -->
    <div class="flex items-center gap-1 border-b border-crm-border bg-white px-4">
      <button
        v-for="tab in pageTabs"
        :key="tab.key"
        class="px-4 py-2.5 text-sm font-medium transition-colors"
        :class="
          activeTab === tab.key
            ? 'border-b-2 border-violet-500 text-violet-600'
            : 'text-ink-gray-5 hover:text-ink-gray-8'
        "
        @click="activeTab = tab.key"
      >
        {{ __(tab.label) }}
      </button>
    </div>

    <!-- ── OVERVIEW TAB ── -->
    <div
      v-if="activeTab === 'overview'"
      class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4"
    >
      <!-- Platform Health Strip -->
      <div class="grid grid-cols-5 gap-3">
        <div
          v-for="h in platformHealth"
          :key="h.label"
          class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm"
        >
          <div class="flex items-center justify-between">
            <div class="text-xs text-ink-gray-4">{{ __(h.label) }}</div>
            <span
              class="h-2 w-2 rounded-full"
              :class="h.status === 'ok' ? 'bg-green-500' : h.status === 'warn' ? 'bg-amber-400' : 'bg-red-500'"
            />
          </div>
          <div class="mt-1 text-xl font-bold" :class="h.color || 'text-ink-gray-9'">
            {{ h.value }}
          </div>
          <div class="text-[11px] text-ink-gray-4">{{ h.sub }}</div>
        </div>
      </div>

      <!-- Feature Cards Grid -->
      <div class="text-sm font-semibold text-ink-gray-7 px-1">{{ __('Platform Modules') }}</div>
      <div class="grid grid-cols-4 gap-3">
        <div
          v-for="feat in featureCards"
          :key="feat.key"
          class="group cursor-pointer rounded-[14px] border border-crm-border bg-white p-4 shadow-sm transition-all hover:border-violet-300 hover:shadow-md"
          @click="navigate(feat)"
        >
          <div class="flex items-start justify-between gap-2">
            <div
              class="flex h-9 w-9 items-center justify-center rounded-xl text-white text-base"
              :style="{ background: feat.gradient }"
            >
              {{ feat.emoji }}
            </div>
            <Badge
              v-if="feat.badge"
              :label="feat.badge"
              variant="subtle"
              :theme="feat.badgeTheme || 'gray'"
            />
          </div>
          <div class="mt-3 text-sm font-semibold text-ink-gray-8 group-hover:text-violet-700">
            {{ __(feat.label) }}
          </div>
          <div class="mt-0.5 text-[11px] text-ink-gray-4 leading-relaxed">
            {{ __(feat.desc) }}
          </div>
          <div class="mt-2 text-[10px] text-violet-500 font-medium">
            {{ feat.stat }}
          </div>
        </div>
      </div>

      <!-- Recent Admin Activity -->
      <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('Recent Admin Activity') }}</div>
          <button
            class="text-xs text-violet-500 hover:underline"
            @click="activeTab = 'audit'"
          >
            {{ __('View Full Audit Log →') }}
          </button>
        </div>
        <div class="space-y-2">
          <div
            v-for="act in recentActivity"
            :key="act.id"
            class="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-surface-gray-1"
          >
            <div
              class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm"
              :class="act.iconBg"
            >
              {{ act.emoji }}
            </div>
            <div class="min-w-0 flex-1 text-xs">
              <span class="font-medium text-ink-gray-8">{{ act.actor }}</span>
              <span class="text-ink-gray-5"> {{ act.action }}</span>
            </div>
            <div class="shrink-0 text-[10px] text-ink-gray-4">{{ act.time }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── USERS & ORG TAB ── -->
    <div
      v-if="activeTab === 'users'"
      class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4"
    >
      <!-- Sub-tabs -->
      <div class="flex gap-2">
        <button
          v-for="st in userSubTabs"
          :key="st"
          class="rounded-full border px-3 py-1 text-xs transition-colors"
          :class="
            userSubTab === st
              ? 'border-violet-500 bg-violet-50 text-violet-700'
              : 'border-outline-gray-2 text-ink-gray-5 hover:border-ink-gray-4'
          "
          @click="userSubTab = st"
        >
          {{ __(st) }}
        </button>
      </div>

      <!-- Users -->
      <div v-if="userSubTab === 'Users'">
        <div class="mb-3 flex items-center gap-2">
          <input
            v-model="userSearch"
            class="h-8 rounded-md border border-outline-gray-2 px-3 text-sm"
            style="width: 220px"
            placeholder="Search users..."
          />
          <select
            v-model="userRoleFilter"
            class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs"
          >
            <option value="">All Roles</option>
            <option v-for="r in allRoles" :key="r">{{ r }}</option>
          </select>
          <select
            v-model="userStatusFilter"
            class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs"
          >
            <option value="">All Status</option>
            <option>Active</option>
            <option>Inactive</option>
            <option>Invited</option>
          </select>
          <div class="ml-auto">
            <Button
              :label="__('Invite User')"
              variant="solid"
              size="sm"
              @click="showInviteModal = true"
            />
          </div>
        </div>
        <div class="rounded-[14px] border border-crm-border bg-white shadow-sm overflow-hidden">
          <table class="w-full text-xs">
            <thead class="bg-surface-gray-1">
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Name') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Email') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Role') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Branch') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Last Login') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Status') }}</th>
                <th class="px-4 py-2.5 text-center font-medium">{{ __('Actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="u in filteredUsers"
                :key="u.id"
                class="border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
              >
                <td class="px-4 py-2.5">
                  <div class="flex items-center gap-2">
                    <div
                      class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
                      :style="{ background: avatarGradient(u.name) }"
                    >
                      {{ u.name.slice(0, 2).toUpperCase() }}
                    </div>
                    <span class="font-medium text-ink-gray-8">{{ u.name }}</span>
                  </div>
                </td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ u.email }}</td>
                <td class="px-4 py-2.5">
                  <Badge :label="u.role" variant="subtle" theme="purple" />
                </td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ u.branch }}</td>
                <td class="px-4 py-2.5 text-ink-gray-4">{{ u.lastLogin }}</td>
                <td class="px-4 py-2.5">
                  <Badge
                    :label="u.status"
                    variant="subtle"
                    :theme="
                      u.status === 'Active'
                        ? 'green'
                        : u.status === 'Invited'
                          ? 'blue'
                          : 'gray'
                    "
                  />
                </td>
                <td class="px-4 py-2.5">
                  <div class="flex justify-center gap-1">
                    <Button
                      icon="edit-2"
                      variant="ghost"
                      size="sm"
                      @click="editUser(u)"
                    />
                    <Button
                      icon="key"
                      variant="ghost"
                      size="sm"
                      :title="__('Reset Password')"
                      @click="() => {}"
                    />
                    <Button
                      :icon="u.status === 'Active' ? 'slash' : 'check-circle'"
                      variant="ghost"
                      size="sm"
                      @click="toggleUserStatus(u)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Branches -->
      <div v-if="userSubTab === 'Branches'">
        <div class="mb-3 flex justify-between items-center">
          <div class="text-xs text-ink-gray-5">{{ branches.length }} {{ __('branches configured') }}</div>
          <Button :label="__('Add Branch')" variant="solid" size="sm" @click="showBranchModal = true" />
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div
            v-for="b in branches"
            :key="b.id"
            class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm"
          >
            <div class="flex items-start justify-between gap-2 mb-3">
              <div>
                <div class="text-sm font-semibold text-ink-gray-8">{{ b.name }}</div>
                <div class="text-xs text-ink-gray-4">{{ b.code }} · {{ b.region }}</div>
              </div>
              <Badge
                :label="b.type"
                variant="subtle"
                :theme="b.type === 'Head Office' ? 'purple' : b.type === 'Regional' ? 'blue' : 'gray'"
              />
            </div>
            <div class="space-y-1 text-xs text-ink-gray-5">
              <div class="flex justify-between">
                <span>{{ __('Users') }}</span>
                <span class="font-medium text-ink-gray-7">{{ b.userCount }}</span>
              </div>
              <div class="flex justify-between">
                <span>{{ __('Active Facilities') }}</span>
                <span class="font-medium text-ink-gray-7">{{ b.facilities }}</span>
              </div>
              <div class="flex justify-between">
                <span>{{ __('Manager') }}</span>
                <span class="font-medium text-ink-gray-7">{{ b.manager }}</span>
              </div>
            </div>
            <div class="mt-3 flex gap-1">
              <Button label="Edit" variant="ghost" size="sm" @click="() => {}" />
              <Button label="Users" variant="ghost" size="sm" @click="() => {}" />
            </div>
          </div>
        </div>
      </div>

      <!-- Sessions -->
      <div v-if="userSubTab === 'Sessions'">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-xs text-ink-gray-5">{{ activeSessions.length }} {{ __('active sessions') }}</div>
          <Button :label="__('Terminate All')" variant="outline" size="sm" @click="() => {}" />
        </div>
        <div class="rounded-[14px] border border-crm-border bg-white shadow-sm overflow-hidden">
          <table class="w-full text-xs">
            <thead class="bg-surface-gray-1">
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="px-4 py-2.5 text-left font-medium">{{ __('User') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('IP Address') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Device') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Location') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Login Time') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Last Active') }}</th>
                <th class="px-4 py-2.5 text-center font-medium">{{ __('Action') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="s in activeSessions"
                :key="s.id"
                class="border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
              >
                <td class="px-4 py-2.5 font-medium text-ink-gray-8">{{ s.user }}</td>
                <td class="px-4 py-2.5 text-ink-gray-5 font-mono">{{ s.ip }}</td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ s.device }}</td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ s.location }}</td>
                <td class="px-4 py-2.5 text-ink-gray-4">{{ s.loginTime }}</td>
                <td class="px-4 py-2.5 text-ink-gray-4">{{ s.lastActive }}</td>
                <td class="px-4 py-2.5 text-center">
                  <Button label="Terminate" variant="ghost" size="sm" @click="terminateSession(s)" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── SECURITY TAB ── -->
    <div
      v-if="activeTab === 'security'"
      class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4"
    >
      <div class="grid grid-cols-3 gap-4">
        <!-- Password Policy -->
        <div class="col-span-1 rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
          <div class="mb-4 text-sm font-semibold text-ink-gray-8">
            {{ __('Password Policy') }}
          </div>
          <div class="space-y-3">
            <div
              v-for="policy in passwordPolicies"
              :key="policy.key"
              class="flex items-center justify-between text-xs"
            >
              <span class="text-ink-gray-6">{{ __(policy.label) }}</span>
              <div>
                <input
                  v-if="policy.type === 'toggle'"
                  type="checkbox"
                  v-model="policy.value"
                  class="h-4 w-4 rounded"
                />
                <input
                  v-else-if="policy.type === 'number'"
                  v-model="policy.value"
                  type="number"
                  class="h-7 w-16 rounded-md border border-outline-gray-2 px-2 text-right text-xs"
                />
                <span v-else class="text-ink-gray-8 font-medium">{{ policy.value }}</span>
              </div>
            </div>
          </div>
          <Button
            class="mt-4 w-full"
            :label="__('Save Policy')"
            variant="solid"
            size="sm"
            @click="savePasswordPolicy"
          />
        </div>

        <!-- RBAC Summary -->
        <div class="col-span-2 rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">
              {{ __('Role & Permission Summary') }}
            </div>
            <div class="flex gap-2">
              <a href="/crm/admin-platform/roles" class="text-xs text-violet-500 hover:underline">
                {{ __('Manage Roles →') }}
              </a>
              <a href="/crm/admin-platform/role-permissions" class="text-xs text-violet-500 hover:underline">
                {{ __('Permission Matrix →') }}
              </a>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-3 mb-4">
            <div
              v-for="r in rolesSummary"
              :key="r.role"
              class="rounded-lg border border-outline-gray-1 p-3 text-xs"
            >
              <div class="font-semibold text-ink-gray-8">{{ r.role }}</div>
              <div class="mt-1 text-ink-gray-4">{{ r.users }} {{ __('users') }}</div>
              <div class="mt-2 flex flex-wrap gap-1">
                <span
                  v-for="perm in r.permissions.slice(0, 3)"
                  :key="perm"
                  class="rounded bg-violet-50 px-1.5 py-0.5 text-[10px] text-violet-700"
                >
                  {{ perm }}
                </span>
                <span v-if="r.permissions.length > 3" class="text-[10px] text-ink-gray-4">
                  +{{ r.permissions.length - 3 }} more
                </span>
              </div>
            </div>
          </div>
          <!-- Permission Matrix Preview -->
          <div class="overflow-x-auto">
            <table class="w-full text-[10px]">
              <thead>
                <tr class="border-b border-outline-gray-1">
                  <th class="py-1.5 pr-3 text-left text-ink-gray-4 font-medium">
                    {{ __('Module') }}
                  </th>
                  <th
                    v-for="role in permMatrixRoles"
                    :key="role"
                    class="py-1.5 px-2 text-center text-ink-gray-4 font-medium"
                  >
                    {{ role }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in permMatrix"
                  :key="row.module"
                  class="border-b border-outline-gray-1 last:border-0"
                >
                  <td class="py-1.5 pr-3 text-ink-gray-6">{{ row.module }}</td>
                  <td
                    v-for="role in permMatrixRoles"
                    :key="role"
                    class="py-1.5 px-2 text-center"
                  >
                    <span :title="row[role]">
                      {{ permIcon(row[role]) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- API Credentials -->
      <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('API Credential Management') }}</div>
          <Button :label="__('Generate Key')" variant="solid" size="sm" @click="generateApiKey" />
        </div>
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-outline-gray-1 text-ink-gray-4">
              <th class="pb-2 text-left font-medium">{{ __('Name') }}</th>
              <th class="pb-2 text-left font-medium">{{ __('Key') }}</th>
              <th class="pb-2 text-left font-medium">{{ __('Scopes') }}</th>
              <th class="pb-2 text-left font-medium">{{ __('Created') }}</th>
              <th class="pb-2 text-left font-medium">{{ __('Last Used') }}</th>
              <th class="pb-2 text-left font-medium">{{ __('Status') }}</th>
              <th class="pb-2 text-center font-medium">{{ __('Action') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="key in apiKeys"
              :key="key.id"
              class="border-b border-outline-gray-1 last:border-0"
            >
              <td class="py-2 font-medium text-ink-gray-8">{{ key.name }}</td>
              <td class="py-2 font-mono text-ink-gray-5">{{ key.preview }}</td>
              <td class="py-2">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="scope in key.scopes"
                    :key="scope"
                    class="rounded bg-surface-gray-2 px-1.5 py-0.5 text-[10px]"
                  >
                    {{ scope }}
                  </span>
                </div>
              </td>
              <td class="py-2 text-ink-gray-4">{{ key.created }}</td>
              <td class="py-2 text-ink-gray-4">{{ key.lastUsed }}</td>
              <td class="py-2">
                <Badge :label="key.status" variant="subtle" :theme="key.status === 'Active' ? 'green' : 'gray'" />
              </td>
              <td class="py-2 text-center">
                <Button icon="trash-2" variant="ghost" size="sm" @click="revokeKey(key)" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── CONFIGURATION TAB ── -->
    <div
      v-if="activeTab === 'config'"
      class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4"
    >
      <!-- Sub-tabs -->
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="st in configSubTabs"
          :key="st"
          class="rounded-full border px-3 py-1 text-xs transition-colors"
          :class="
            configSubTab === st
              ? 'border-violet-500 bg-violet-50 text-violet-700'
              : 'border-outline-gray-2 text-ink-gray-5 hover:border-ink-gray-4'
          "
          @click="configSubTab = st"
        >
          {{ __(st) }}
        </button>
      </div>

      <!-- SLA Configuration -->
      <div v-if="configSubTab === 'SLA'">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-xs text-ink-gray-5">{{ __('Define response & resolution SLAs per module and priority') }}</div>
          <Button :label="__('Add SLA Rule')" variant="solid" size="sm" @click="showSlaModal = true" />
        </div>
        <div class="rounded-[14px] border border-crm-border bg-white shadow-sm overflow-hidden">
          <table class="w-full text-xs">
            <thead class="bg-surface-gray-1">
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Module') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Priority') }}</th>
                <th class="px-4 py-2.5 text-right font-medium">{{ __('First Response') }}</th>
                <th class="px-4 py-2.5 text-right font-medium">{{ __('Resolution') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Business Hours') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Escalation') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Status') }}</th>
                <th class="px-4 py-2.5 text-center font-medium">{{ __('Actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="sla in slaRules"
                :key="sla.id"
                class="border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
              >
                <td class="px-4 py-2.5 font-medium text-ink-gray-8">{{ sla.module }}</td>
                <td class="px-4 py-2.5">
                  <Badge :label="sla.priority" variant="subtle" :theme="sla.priority === 'High' ? 'red' : sla.priority === 'Medium' ? 'orange' : 'gray'" />
                </td>
                <td class="px-4 py-2.5 text-right font-medium text-ink-gray-7">{{ sla.firstResponse }}</td>
                <td class="px-4 py-2.5 text-right font-medium text-ink-gray-7">{{ sla.resolution }}</td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ sla.businessHours }}</td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ sla.escalateTo }}</td>
                <td class="px-4 py-2.5">
                  <button
                    class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                    :class="sla.active ? 'bg-green-500' : 'bg-surface-gray-3'"
                    @click="sla.active = !sla.active"
                  >
                    <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                      :class="sla.active ? 'translate-x-4' : 'translate-x-0.5'" />
                  </button>
                </td>
                <td class="px-4 py-2.5 text-center">
                  <Button icon="edit-2" variant="ghost" size="sm" @click="() => {}" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Notification Templates -->
      <div v-if="configSubTab === 'Notifications'">
        <div class="mb-3 flex justify-between">
          <div class="text-xs text-ink-gray-5">{{ __('System notification templates for email, SMS, in-app, and push') }}</div>
          <Button :label="__('New Template')" variant="solid" size="sm" @click="showNotifModal = true" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div
            v-for="nt in notifTemplates"
            :key="nt.id"
            class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm"
          >
            <div class="flex items-start justify-between gap-2 mb-2">
              <div>
                <div class="text-sm font-semibold text-ink-gray-8">{{ nt.name }}</div>
                <div class="text-[11px] text-ink-gray-4">{{ nt.trigger }} · {{ nt.channels.join(', ') }}</div>
              </div>
              <button
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                :class="nt.active ? 'bg-green-500' : 'bg-surface-gray-3'"
                @click="nt.active = !nt.active"
              >
                <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                  :class="nt.active ? 'translate-x-4' : 'translate-x-0.5'" />
              </button>
            </div>
            <div class="rounded bg-surface-gray-1 p-2 text-[11px] text-ink-gray-6 leading-relaxed">
              {{ nt.body }}
            </div>
            <div class="mt-2 flex flex-wrap gap-1">
              <span
                v-for="ch in nt.channels"
                :key="ch"
                class="rounded bg-violet-50 px-1.5 py-0.5 text-[10px] text-violet-700"
              >
                {{ ch }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Holiday Calendar -->
      <div v-if="configSubTab === 'Holidays'">
        <div class="mb-3 flex justify-between">
          <div class="text-xs text-ink-gray-5">{{ __('Public holidays affect SLA business-hours calculations') }}</div>
          <Button :label="__('Add Holiday')" variant="solid" size="sm" @click="showHolidayModal = true" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
            <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('2026 Holiday Calendar') }}</div>
            <div class="space-y-1.5 text-xs">
              <div
                v-for="h in holidays"
                :key="h.id"
                class="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-surface-gray-1"
              >
                <div class="w-24 font-medium text-ink-gray-8">{{ h.date }}</div>
                <div class="flex-1 text-ink-gray-6">{{ h.name }}</div>
                <Badge :label="h.type" variant="subtle" :theme="h.type === 'National' ? 'blue' : 'gray'" />
                <button class="text-ink-gray-3 hover:text-red-500" @click="removeHoliday(h)">✕</button>
              </div>
            </div>
          </div>
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
            <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Working Hours Configuration') }}</div>
            <div class="space-y-3 text-xs">
              <div
                v-for="day in workingHours"
                :key="day.day"
                class="flex items-center gap-3"
              >
                <div class="w-24 text-ink-gray-6">{{ day.day }}</div>
                <button
                  class="relative inline-flex h-5 w-9 items-center rounded-full"
                  :class="day.active ? 'bg-green-500' : 'bg-surface-gray-3'"
                  @click="day.active = !day.active"
                >
                  <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                    :class="day.active ? 'translate-x-4' : 'translate-x-0.5'" />
                </button>
                <span v-if="day.active" class="text-ink-gray-5">{{ day.start }} – {{ day.end }}</span>
                <span v-else class="text-ink-gray-3">{{ __('Closed') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Custom Field Builder -->
      <div v-if="configSubTab === 'Custom Fields'">
        <div class="mb-3 flex justify-between">
          <div class="text-xs text-ink-gray-5">{{ __('Add custom fields to any CRM doctype without code changes') }}</div>
          <Button :label="__('Add Field')" variant="solid" size="sm" @click="showFieldModal = true" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
            <div class="mb-3 flex items-center justify-between">
              <div class="text-sm font-semibold text-ink-gray-8">{{ __('Custom Fields') }}</div>
              <select v-model="fieldDoctype" class="h-7 rounded-md border border-outline-gray-2 px-2 text-xs">
                <option v-for="dt in ['CRM Lead', 'CRM Deal', 'Contact', 'CRM Organization', 'CRM Task']" :key="dt" :value="dt">{{ dt }}</option>
              </select>
            </div>
            <div class="space-y-2 text-xs">
              <div
                v-for="cf in customFields.filter((f) => f.doctype === fieldDoctype)"
                :key="cf.id"
                class="flex items-center gap-3 rounded-lg border border-outline-gray-1 px-3 py-2"
              >
                <FeatherIcon name="menu" class="h-3 w-3 text-ink-gray-3 cursor-grab" />
                <div class="flex-1">
                  <span class="font-medium text-ink-gray-7">{{ cf.label }}</span>
                  <span class="ml-2 text-ink-gray-4">{{ cf.fieldType }}</span>
                </div>
                <Badge :label="cf.required ? 'Required' : 'Optional'" variant="subtle" :theme="cf.required ? 'red' : 'gray'" />
                <button class="text-ink-gray-3 hover:text-red-500" @click="removeCustomField(cf)">✕</button>
              </div>
              <div v-if="!customFields.filter((f) => f.doctype === fieldDoctype).length" class="py-4 text-center text-ink-gray-4">
                {{ __('No custom fields for this doctype') }}
              </div>
            </div>
          </div>
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
            <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Add Custom Field') }}</div>
            <div class="space-y-3 text-sm">
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Doctype') }}</label>
                <select v-model="newField.doctype" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                  <option v-for="dt in ['CRM Lead', 'CRM Deal', 'Contact', 'CRM Organization', 'CRM Task']" :key="dt" :value="dt">{{ dt }}</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Field Label') }}</label>
                <input v-model="newField.label" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="e.g. NPWP Number" />
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Field Type') }}</label>
                <select v-model="newField.fieldType" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                  <option v-for="t in ['Text', 'Number', 'Date', 'Select', 'Checkbox', 'File', 'Currency']" :key="t" :value="t">{{ t }}</option>
                </select>
              </div>
              <div class="flex items-center gap-2">
                <input v-model="newField.required" type="checkbox" class="h-4 w-4 rounded" />
                <label class="text-xs text-ink-gray-5">{{ __('Required field') }}</label>
              </div>
              <Button :label="__('Add Field')" variant="solid" class="w-full" size="sm" @click="addCustomField" />
            </div>
          </div>
        </div>
      </div>

      <!-- Localization -->
      <div v-if="configSubTab === 'Localization'">
        <div class="grid grid-cols-2 gap-4">
          <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
            <div class="mb-4 text-sm font-semibold text-ink-gray-8">{{ __('Language & Regional Settings') }}</div>
            <div class="space-y-4 text-sm">
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Default Language') }}</label>
                <select v-model="locale.language" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                  <option value="id">Bahasa Indonesia</option>
                  <option value="en">English</option>
                  <option value="both">Bilingual (ID + EN)</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Date Format') }}</label>
                <select v-model="locale.dateFormat" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                  <option>DD/MM/YYYY</option>
                  <option>YYYY-MM-DD</option>
                  <option>MM/DD/YYYY</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Currency') }}</label>
                <select v-model="locale.currency" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                  <option>IDR</option>
                  <option>USD</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Timezone') }}</label>
                <select v-model="locale.timezone" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                  <option>Asia/Jakarta (WIB, UTC+7)</option>
                  <option>Asia/Makassar (WITA, UTC+8)</option>
                  <option>Asia/Jayapura (WIT, UTC+9)</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Number Format') }}</label>
                <select v-model="locale.numberFormat" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                  <option>1.000.000,00 (ID)</option>
                  <option>1,000,000.00 (EN)</option>
                </select>
              </div>
              <Button :label="__('Save Settings')" variant="solid" class="w-full" @click="() => {}" />
            </div>
          </div>
          <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
            <div class="mb-4 text-sm font-semibold text-ink-gray-8">{{ __('Installed Languages') }}</div>
            <div class="space-y-2 text-xs">
              <div v-for="lang in installedLanguages" :key="lang.code" class="flex items-center gap-3 rounded-lg border border-outline-gray-1 px-3 py-2">
                <span class="text-base">{{ lang.flag }}</span>
                <div class="flex-1">
                  <div class="font-medium text-ink-gray-8">{{ lang.name }}</div>
                  <div class="text-ink-gray-4">{{ lang.coverage }}% {{ __('translated') }}</div>
                </div>
                <div class="h-1.5 w-20 rounded-full bg-surface-gray-2 overflow-hidden">
                  <div class="h-1.5 rounded-full bg-violet-500" :style="{ width: lang.coverage + '%' }" />
                </div>
                <Badge :label="lang.default ? 'Default' : 'Installed'" variant="subtle" :theme="lang.default ? 'purple' : 'gray'" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── PLATFORM TAB ── -->
    <div
      v-if="activeTab === 'platform'"
      class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4"
    >
      <div class="grid grid-cols-3 gap-4">
        <!-- System Settings -->
        <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
          <div class="mb-4 text-sm font-semibold text-ink-gray-8">{{ __('System Settings') }}</div>
          <div class="space-y-3">
            <div
              v-for="setting in systemSettings"
              :key="setting.key"
              class="flex items-center justify-between text-xs"
            >
              <div>
                <div class="font-medium text-ink-gray-7">{{ __(setting.label) }}</div>
                <div v-if="setting.desc" class="text-ink-gray-4">{{ __(setting.desc) }}</div>
              </div>
              <button
                v-if="setting.type === 'toggle'"
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                :class="setting.value ? 'bg-violet-500' : 'bg-surface-gray-3'"
                @click="setting.value = !setting.value"
              >
                <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                  :class="setting.value ? 'translate-x-4' : 'translate-x-0.5'" />
              </button>
              <select v-else-if="setting.type === 'select'" v-model="setting.value" class="h-7 rounded-md border border-outline-gray-2 px-2 text-xs">
                <option v-for="o in setting.options" :key="o" :value="o">{{ o }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- License & Branding -->
        <div class="flex flex-col gap-4">
          <!-- License -->
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
            <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('License') }}</div>
            <div class="space-y-2 text-xs">
              <div class="flex justify-between">
                <span class="text-ink-gray-5">{{ __('Plan') }}</span>
                <Badge label="Enterprise" variant="subtle" theme="purple" />
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-5">{{ __('Licensed To') }}</span>
                <span class="font-medium text-ink-gray-7">PT Bank BNI</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-5">{{ __('Users') }}</span>
                <span class="font-medium text-ink-gray-7">{{ users.length }} / 500</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-5">{{ __('Expires') }}</span>
                <span class="font-medium text-green-600">2027-12-31</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-5">{{ __('Modules') }}</span>
                <span class="font-medium text-ink-gray-7">All (26)</span>
              </div>
            </div>
            <div class="mt-2 h-1.5 w-full rounded-full bg-surface-gray-2 overflow-hidden">
              <div class="h-1.5 rounded-full bg-violet-500" :style="{ width: (users.length / 500 * 100) + '%' }" />
            </div>
            <div class="mt-1 text-[10px] text-ink-gray-4">{{ users.length }}/500 {{ __('seats used') }}</div>
          </div>

          <!-- Maintenance Mode -->
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm" :class="maintenanceMode ? 'border-amber-300 bg-amber-50' : ''">
            <div class="flex items-center justify-between mb-2">
              <div class="text-sm font-semibold text-ink-gray-8">{{ __('Maintenance Mode') }}</div>
              <button
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                :class="maintenanceMode ? 'bg-amber-500' : 'bg-surface-gray-3'"
                @click="maintenanceMode = !maintenanceMode"
              >
                <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                  :class="maintenanceMode ? 'translate-x-4' : 'translate-x-0.5'" />
              </button>
            </div>
            <div v-if="maintenanceMode" class="text-[11px] text-amber-700">
              ⚠️ {{ __('System is in maintenance mode. Users cannot login.') }}
            </div>
            <div v-else class="text-[11px] text-ink-gray-4">
              {{ __('Enable to block all user access during maintenance.') }}
            </div>
            <div v-if="maintenanceMode" class="mt-2">
              <textarea v-model="maintenanceMessage" rows="2" class="w-full rounded-md border border-amber-300 bg-white px-2 py-1 text-[11px]" placeholder="Maintenance message..." />
            </div>
          </div>
        </div>

        <!-- Branding -->
        <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
          <div class="mb-4 text-sm font-semibold text-ink-gray-8">{{ __('Branding & White Label') }}</div>
          <div class="space-y-3 text-xs">
            <div>
              <label class="text-ink-gray-5">{{ __('Platform Name') }}</label>
              <input v-model="branding.platformName" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-2 text-sm" />
            </div>
            <div>
              <label class="text-ink-gray-5">{{ __('Logo') }}</label>
              <div class="mt-1 flex items-center gap-2">
                <div class="flex h-10 w-10 items-center justify-center rounded-lg border border-outline-gray-2 bg-surface-gray-1 text-xs text-ink-gray-4">
                  {{ branding.platformName.slice(0, 2).toUpperCase() }}
                </div>
                <Button label="Upload" variant="subtle" size="sm" @click="() => {}" />
              </div>
            </div>
            <div>
              <label class="text-ink-gray-5">{{ __('Primary Color') }}</label>
              <div class="mt-1 flex items-center gap-2">
                <input v-model="branding.primaryColor" type="color" class="h-8 w-10 rounded-md border border-outline-gray-2 cursor-pointer" />
                <span class="font-mono text-ink-gray-6">{{ branding.primaryColor }}</span>
              </div>
            </div>
            <div>
              <label class="text-ink-gray-5">{{ __('Accent Color') }}</label>
              <div class="mt-1 flex items-center gap-2">
                <input v-model="branding.accentColor" type="color" class="h-8 w-10 rounded-md border border-outline-gray-2 cursor-pointer" />
                <span class="font-mono text-ink-gray-6">{{ branding.accentColor }}</span>
              </div>
            </div>
            <div>
              <label class="text-ink-gray-5">{{ __('Favicon URL') }}</label>
              <input v-model="branding.faviconUrl" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-2 text-xs" placeholder="/assets/favicon.ico" />
            </div>
            <div>
              <label class="text-ink-gray-5">{{ __('Footer Text') }}</label>
              <input v-model="branding.footer" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-2 text-xs" />
            </div>
            <!-- Preview -->
            <div class="rounded-lg border border-outline-gray-2 p-2">
              <div class="text-[10px] text-ink-gray-4 mb-1">{{ __('Preview') }}</div>
              <div class="flex items-center gap-2 rounded px-2 py-1" :style="{ background: branding.primaryColor }">
                <div class="h-5 w-5 rounded bg-white/20 flex items-center justify-center text-[10px] text-white font-bold">
                  {{ branding.platformName.slice(0, 2) }}
                </div>
                <span class="text-xs font-semibold text-white">{{ branding.platformName }}</span>
              </div>
            </div>
            <Button :label="__('Save Branding')" variant="solid" class="w-full" size="sm" @click="() => {}" />
          </div>
        </div>
      </div>

      <!-- Multi-Tenant -->
      <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('Multi-Tenant Configuration') }}</div>
          <Button :label="__('Add Tenant')" variant="solid" size="sm" @click="showTenantModal = true" />
        </div>
        <div class="grid grid-cols-4 gap-3">
          <div
            v-for="t in tenants"
            :key="t.id"
            class="rounded-lg border border-outline-gray-1 p-3 text-xs"
          >
            <div class="flex items-center gap-1.5 mb-2">
              <div class="h-6 w-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold" :style="{ background: t.color }">
                {{ t.name.slice(0, 2) }}
              </div>
              <span class="font-semibold text-ink-gray-8">{{ t.name }}</span>
            </div>
            <div class="space-y-1 text-ink-gray-4">
              <div>{{ t.subdomain }}</div>
              <div>{{ t.users }} users · {{ t.plan }}</div>
            </div>
            <Badge :label="t.status" variant="subtle" :theme="t.status === 'Active' ? 'green' : 'gray'" class="mt-2" />
          </div>
        </div>
      </div>

      <!-- Backup & Restore -->
      <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('Backup & Restore') }}</div>
          <div class="flex gap-2">
            <Button :label="__('Run Backup Now')" variant="solid" size="sm" @click="runBackup" />
            <Button :label="__('Schedule')" variant="outline" size="sm" @click="() => {}" />
          </div>
        </div>
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-outline-gray-1 text-ink-gray-4">
              <th class="pb-2 text-left font-medium">{{ __('Backup Name') }}</th>
              <th class="pb-2 text-left font-medium">{{ __('Date & Time') }}</th>
              <th class="pb-2 text-right font-medium">{{ __('Size') }}</th>
              <th class="pb-2 text-left font-medium">{{ __('Type') }}</th>
              <th class="pb-2 text-left font-medium">{{ __('Status') }}</th>
              <th class="pb-2 text-center font-medium">{{ __('Actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="bk in backups"
              :key="bk.id"
              class="border-b border-outline-gray-1 last:border-0"
            >
              <td class="py-2 font-mono text-ink-gray-7">{{ bk.name }}</td>
              <td class="py-2 text-ink-gray-5">{{ bk.datetime }}</td>
              <td class="py-2 text-right text-ink-gray-5">{{ bk.size }}</td>
              <td class="py-2">
                <Badge :label="bk.type" variant="subtle" :theme="bk.type === 'Full' ? 'blue' : 'gray'" />
              </td>
              <td class="py-2">
                <Badge :label="bk.status" variant="subtle" :theme="bk.status === 'Completed' ? 'green' : bk.status === 'Running' ? 'orange' : 'gray'" />
              </td>
              <td class="py-2 text-center">
                <div class="flex justify-center gap-1">
                  <Button icon="download" variant="ghost" size="sm" @click="() => {}" />
                  <Button label="Restore" variant="ghost" size="sm" @click="() => {}" />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── AUDIT TAB ── -->
    <div
      v-if="activeTab === 'audit'"
      class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4"
    >
      <div class="flex items-center gap-3">
        <input v-model="auditSearch" class="h-8 rounded-md border border-outline-gray-2 px-3 text-sm flex-1 max-w-xs" placeholder="Search audit logs..." />
        <select v-model="auditModule" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">All Modules</option>
          <option v-for="m in ['Users', 'RBAC', 'System', 'Backup', 'API', 'Branding']" :key="m">{{ m }}</option>
        </select>
        <select v-model="auditAction" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">All Actions</option>
          <option v-for="a in ['Create', 'Update', 'Delete', 'Login', 'Logout', 'Export']" :key="a">{{ a }}</option>
        </select>
        <div class="ml-auto">
          <a href="/crm/admin-platform/audit-trail" class="text-xs text-violet-500 hover:underline">{{ __('Full Audit Trail →') }}</a>
        </div>
      </div>
      <div class="rounded-[14px] border border-crm-border bg-white shadow-sm overflow-hidden">
        <table class="w-full text-xs">
          <thead class="bg-surface-gray-1">
            <tr class="border-b border-outline-gray-1 text-ink-gray-4">
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Timestamp') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Actor') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Action') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Module') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Resource') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('IP') }}</th>
              <th class="px-4 py-2.5 text-left font-medium">{{ __('Result') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="log in filteredAuditLogs"
              :key="log.id"
              class="border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
            >
              <td class="px-4 py-2.5 font-mono text-ink-gray-4">{{ log.timestamp }}</td>
              <td class="px-4 py-2.5 font-medium text-ink-gray-8">{{ log.actor }}</td>
              <td class="px-4 py-2.5">
                <Badge :label="log.action" variant="subtle"
                  :theme="log.action === 'Delete' ? 'red' : log.action === 'Create' ? 'green' : log.action === 'Login' ? 'blue' : 'gray'" />
              </td>
              <td class="px-4 py-2.5 text-ink-gray-5">{{ log.module }}</td>
              <td class="px-4 py-2.5 text-ink-gray-6">{{ log.resource }}</td>
              <td class="px-4 py-2.5 font-mono text-ink-gray-4">{{ log.ip }}</td>
              <td class="px-4 py-2.5">
                <Badge :label="log.result" variant="subtle" :theme="log.result === 'Success' ? 'green' : 'red'" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ── MODALS ── -->

  <!-- Invite User -->
  <div v-if="showInviteModal" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Invite User') }}</div>
        <button class="text-ink-gray-4" @click="showInviteModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Full Name') }}</label>
          <input v-model="inviteForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Email Address') }}</label>
          <input v-model="inviteForm.email" type="email" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Role') }}</label>
          <select v-model="inviteForm.role" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="r in allRoles" :key="r">{{ r }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Branch') }}</label>
          <select v-model="inviteForm.branch" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="b in branches" :key="b.id">{{ b.name }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Send Invitation via') }}</label>
          <div class="mt-1 flex gap-3 text-xs">
            <label class="flex items-center gap-1"><input type="checkbox" checked class="h-3.5 w-3.5" /> Email</label>
            <label class="flex items-center gap-1"><input type="checkbox" class="h-3.5 w-3.5" /> WhatsApp</label>
          </div>
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showInviteModal = false" />
        <Button :label="__('Send Invitation')" variant="solid" @click="sendInvite" />
      </div>
    </div>
  </div>

  <!-- Branch Modal -->
  <div v-if="showBranchModal" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Add Branch') }}</div>
        <button class="text-ink-gray-4" @click="showBranchModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Branch Name') }}</label>
            <input v-model="branchForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Branch Code') }}</label>
            <input v-model="branchForm.code" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="e.g. JKT-001" />
          </div>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Type') }}</label>
          <select v-model="branchForm.type" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option>Head Office</option><option>Regional</option><option>Sub-Branch</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Region') }}</label>
          <input v-model="branchForm.region" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Branch Manager') }}</label>
          <select v-model="branchForm.manager" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="u in users" :key="u.id">{{ u.name }}</option>
          </select>
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showBranchModal = false" />
        <Button :label="__('Create Branch')" variant="solid" @click="addBranch" />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Badge, Button, FeatherIcon, usePageMeta } from 'frappe-ui'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ── Tabs ─────────────────────────────────────────────────────
const pageTabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'users', label: 'Users & Org' },
  { key: 'security', label: 'Security' },
  { key: 'config', label: 'Configuration' },
  { key: 'platform', label: 'Platform' },
  { key: 'audit', label: 'Audit' },
]
const activeTab = ref('overview')

// ── Sub-tabs ─────────────────────────────────────────────────
const userSubTabs = ['Users', 'Branches', 'Sessions']
const userSubTab = ref('Users')
const configSubTabs = ['SLA', 'Notifications', 'Holidays', 'Custom Fields', 'Localization']
const configSubTab = ref('SLA')

// ── Modal state ──────────────────────────────────────────────
const showInviteModal = ref(false)
const showBranchModal = ref(false)
const showSlaModal = ref(false)
const showNotifModal = ref(false)
const showHolidayModal = ref(false)
const showFieldModal = ref(false)
const showTenantModal = ref(false)

// ── Form state ───────────────────────────────────────────────
const inviteForm = ref({ name: '', email: '', role: 'RM', branch: '' })
const branchForm = ref({ name: '', code: '', type: 'Sub-Branch', region: '', manager: '' })
const newField = ref({ doctype: 'CRM Lead', label: '', fieldType: 'Text', required: false })
const fieldDoctype = ref('CRM Lead')

// ── Platform state ───────────────────────────────────────────
const maintenanceMode = ref(false)
const maintenanceMessage = ref('System maintenance in progress. Please try again later.')

// ── Branding ─────────────────────────────────────────────────
const branding = ref({
  platformName: 'SUMMON OS',
  primaryColor: '#7c3aed',
  accentColor: '#14b8a6',
  faviconUrl: '/assets/favicon.ico',
  footer: '© 2026 SUMMON OS — Powered by AI',
})

// ── Locale ───────────────────────────────────────────────────
const locale = ref({
  language: 'id',
  dateFormat: 'DD/MM/YYYY',
  currency: 'IDR',
  timezone: 'Asia/Jakarta (WIB, UTC+7)',
  numberFormat: '1.000.000,00 (ID)',
})

// ── Filters ──────────────────────────────────────────────────
const userSearch = ref('')
const userRoleFilter = ref('')
const userStatusFilter = ref('')
const auditSearch = ref('')
const auditModule = ref('')
const auditAction = ref('')

// ── Platform Health ──────────────────────────────────────────
const platformHealth = [
  { label: 'Active Users', value: '24', sub: '8 online now', status: 'ok', color: 'text-green-600' },
  { label: 'System Uptime', value: '99.8%', sub: '30-day avg', status: 'ok', color: 'text-green-600' },
  { label: 'API Calls Today', value: '12,842', sub: 'vs 11,200 yesterday', status: 'ok' },
  { label: 'DB Size', value: '4.2 GB', sub: 'of 50 GB limit', status: 'ok' },
  { label: 'Failed Logins', value: '3', sub: 'last 24h', status: 'warn', color: 'text-amber-600' },
]

// ── Feature Cards ────────────────────────────────────────────
const featureCards = [
  { key: 'users', label: 'User Management', desc: 'Invite, manage, and deactivate users across branches', emoji: '👥', gradient: 'linear-gradient(135deg, #7c3aed, #c084fc)', stat: '24 active users', tab: 'users', subTab: 'Users' },
  { key: 'branches', label: 'Branch Management', desc: 'Configure organizational branches and hierarchy', emoji: '🏢', gradient: 'linear-gradient(135deg, #2563eb, #60a5fa)', stat: '5 branches', tab: 'users', subTab: 'Branches' },
  { key: 'rbac', label: 'Role & Permissions', desc: 'Granular RBAC with permission matrix', emoji: '🔐', gradient: 'linear-gradient(135deg, #dc2626, #f87171)', stat: '7 roles configured', route: '/admin-platform/roles' },
  { key: 'sla', label: 'SLA Configuration', desc: 'Response and resolution SLA per module and priority', emoji: '⏱️', gradient: 'linear-gradient(135deg, #0891b2, #22d3ee)', stat: '12 SLA rules', tab: 'config', subTab: 'SLA' },
  { key: 'workflow', label: 'Workflow Engine', desc: 'No-code drag-drop workflow builder', emoji: '🔀', gradient: 'linear-gradient(135deg, #059669, #34d399)', stat: '8 active workflows', route: '/admin-platform/workflow-engine' },
  { key: 'notif', label: 'Notification Templates', desc: 'System notification templates across channels', emoji: '🔔', gradient: 'linear-gradient(135deg, #d97706, #fbbf24)', stat: '15 templates', tab: 'config', subTab: 'Notifications' },
  { key: 'holiday', label: 'Holiday Calendar', desc: 'Public holidays for SLA business-hours calculation', emoji: '📅', gradient: 'linear-gradient(135deg, #e11d48, #fb7185)', stat: '18 holidays', tab: 'config', subTab: 'Holidays' },
  { key: 'settings', label: 'System Settings', desc: 'Platform-wide configuration toggles', emoji: '⚙️', gradient: 'linear-gradient(135deg, #475569, #94a3b8)', stat: '20 settings', tab: 'platform' },
  { key: 'api', label: 'API Credentials', desc: 'API key management and OAuth configuration', emoji: '🔑', gradient: 'linear-gradient(135deg, #7c3aed, #a78bfa)', stat: '4 active keys', tab: 'security' },
  { key: 'audit', label: 'Audit Trail', desc: 'Full activity logs and compliance tracking', emoji: '📋', gradient: 'linear-gradient(135deg, #1e3a5f, #3b82f6)', stat: '2,847 events', route: '/admin-platform/audit-trail' },
  { key: 'tenant', label: 'Multi-Tenant', desc: 'Manage platform tenants and subdomain configuration', emoji: '🏗️', gradient: 'linear-gradient(135deg, #0f766e, #2dd4bf)', stat: '1 tenant active', tab: 'platform' },
  { key: 'branding', label: 'Branding & White Label', desc: 'Custom logo, colors, and platform identity', emoji: '🎨', gradient: 'linear-gradient(135deg, #c026d3, #e879f9)', stat: 'BNI theme applied', tab: 'platform' },
  { key: 'backup', label: 'Backup & Restore', desc: 'Automated backups with point-in-time restore', emoji: '💾', gradient: 'linear-gradient(135deg, #1d4ed8, #60a5fa)', stat: 'Last: 2h ago', tab: 'platform' },
  { key: 'maintenance', label: 'Maintenance Mode', desc: 'Block user access during system maintenance', emoji: '🔧', gradient: 'linear-gradient(135deg, #92400e, #fbbf24)', stat: 'Currently off', tab: 'platform' },
  { key: 'license', label: 'License', desc: 'Enterprise license management and seat tracking', emoji: '📜', gradient: 'linear-gradient(135deg, #065f46, #34d399)', stat: '24/500 seats', tab: 'platform' },
  { key: 'session', label: 'Session Management', desc: 'View and terminate active user sessions', emoji: '🖥️', gradient: 'linear-gradient(135deg, #7c3aed, #c084fc)', stat: '8 sessions', tab: 'users', subTab: 'Sessions' },
  { key: 'password', label: 'Password Policy', desc: 'Enforce password strength and rotation rules', emoji: '🛡️', gradient: 'linear-gradient(135deg, #b91c1c, #f87171)', stat: 'Policy active', tab: 'security' },
  { key: 'fields', label: 'Custom Field Builder', desc: 'Add custom fields to CRM doctypes', emoji: '🧩', gradient: 'linear-gradient(135deg, #0369a1, #38bdf8)', stat: '6 custom fields', tab: 'config', subTab: 'Custom Fields' },
  { key: 'locale', label: 'Localization', desc: 'Language, currency, timezone, and date format', emoji: '🌐', gradient: 'linear-gradient(135deg, #0f766e, #34d399)', stat: 'ID + EN', tab: 'config', subTab: 'Localization' },
]

// ── Recent Activity ──────────────────────────────────────────
const recentActivity = [
  { id: 1, emoji: '👤', iconBg: 'bg-violet-100 text-violet-700', actor: 'Admin', action: 'invited user Siti Rahayu (RM role)', time: '5m ago' },
  { id: 2, emoji: '🔐', iconBg: 'bg-red-100 text-red-700', actor: 'Admin', action: 'updated Role Permissions for Credit Analyst', time: '1h ago' },
  { id: 3, emoji: '⚙️', iconBg: 'bg-gray-100 text-gray-700', actor: 'System', action: 'automated backup completed — 4.2 GB', time: '2h ago' },
  { id: 4, emoji: '🔑', iconBg: 'bg-amber-100 text-amber-700', actor: 'IT Admin', action: 'generated new API key for BNI Integration', time: '3h ago' },
  { id: 5, emoji: '🌐', iconBg: 'bg-blue-100 text-blue-700', actor: 'Admin', action: 'updated locale settings to Bahasa Indonesia', time: 'Yesterday' },
  { id: 6, emoji: '⏱️', iconBg: 'bg-cyan-100 text-cyan-700', actor: 'Admin', action: 'added SLA rule — Omnichannel High Priority 15m', time: 'Yesterday' },
]

// ── Users ────────────────────────────────────────────────────
const allRoles = ['Super Admin', 'IT Admin', 'RM', 'Credit Analyst', 'Operations', 'Collection Officer', 'Compliance', 'Read Only']
const users = ref([
  { id: 'u1', name: 'Ahmad Santoso', email: 'ahmad@bni.co.id', role: 'Super Admin', branch: 'Head Office', lastLogin: '2026-05-24 09:15', status: 'Active' },
  { id: 'u2', name: 'Dewi Pratama', email: 'dewi@bni.co.id', role: 'RM', branch: 'Jakarta Pusat', lastLogin: '2026-05-24 08:42', status: 'Active' },
  { id: 'u3', name: 'Rizky Andalan', email: 'rizky@bni.co.id', role: 'RM', branch: 'Surabaya', lastLogin: '2026-05-23 17:30', status: 'Active' },
  { id: 'u4', name: 'Maya Lestari', email: 'maya@bni.co.id', role: 'Collection Officer', branch: 'Bandung', lastLogin: '2026-05-24 07:55', status: 'Active' },
  { id: 'u5', name: 'Budi Santoso', email: 'budi@bni.co.id', role: 'Credit Analyst', branch: 'Head Office', lastLogin: '2026-05-22 16:00', status: 'Active' },
  { id: 'u6', name: 'Siti Rahayu', email: 'siti@bni.co.id', role: 'Operations', branch: 'Jakarta Selatan', lastLogin: '—', status: 'Invited' },
  { id: 'u7', name: 'Hendra Wijaya', email: 'hendra@bni.co.id', role: 'Compliance', branch: 'Head Office', lastLogin: '2026-05-20 14:22', status: 'Inactive' },
])

const filteredUsers = computed(() => {
  return users.value.filter((u) => {
    const q = userSearch.value.toLowerCase()
    const matchQ = !q || u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    const matchRole = !userRoleFilter.value || u.role === userRoleFilter.value
    const matchStatus = !userStatusFilter.value || u.status === userStatusFilter.value
    return matchQ && matchRole && matchStatus
  })
})

// ── Branches ─────────────────────────────────────────────────
const branches = ref([
  { id: 'b1', name: 'Head Office', code: 'HO-001', type: 'Head Office', region: 'Jakarta', userCount: 8, facilities: 142, manager: 'Ahmad Santoso' },
  { id: 'b2', name: 'Jakarta Pusat', code: 'JKT-001', type: 'Regional', region: 'DKI Jakarta', userCount: 5, facilities: 67, manager: 'Dewi Pratama' },
  { id: 'b3', name: 'Jakarta Selatan', code: 'JKT-002', type: 'Sub-Branch', region: 'DKI Jakarta', userCount: 3, facilities: 41, manager: 'Siti Rahayu' },
  { id: 'b4', name: 'Surabaya', code: 'SBY-001', type: 'Regional', region: 'Jawa Timur', userCount: 4, facilities: 55, manager: 'Rizky Andalan' },
  { id: 'b5', name: 'Bandung', code: 'BDG-001', type: 'Sub-Branch', region: 'Jawa Barat', userCount: 3, facilities: 38, manager: 'Maya Lestari' },
])

// ── Sessions ─────────────────────────────────────────────────
const activeSessions = ref([
  { id: 's1', user: 'Ahmad Santoso', ip: '192.168.1.10', device: 'Chrome / macOS', location: 'Jakarta, ID', loginTime: '2026-05-24 09:15', lastActive: '2 min ago' },
  { id: 's2', user: 'Dewi Pratama', ip: '192.168.1.45', device: 'Safari / iPhone', location: 'Jakarta, ID', loginTime: '2026-05-24 08:42', lastActive: '15 min ago' },
  { id: 's3', user: 'Rizky Andalan', ip: '10.0.0.8', device: 'Chrome / Windows', location: 'Surabaya, ID', loginTime: '2026-05-24 08:00', lastActive: '1h ago' },
  { id: 's4', user: 'Maya Lestari', ip: '192.168.2.12', device: 'Firefox / Linux', location: 'Bandung, ID', loginTime: '2026-05-24 07:55', lastActive: '30 min ago' },
])

// ── Password Policy ──────────────────────────────────────────
const passwordPolicies = ref([
  { key: 'min_length', label: 'Minimum Length', type: 'number', value: 10 },
  { key: 'uppercase', label: 'Require Uppercase', type: 'toggle', value: true },
  { key: 'number', label: 'Require Number', type: 'toggle', value: true },
  { key: 'special', label: 'Require Special Char', type: 'toggle', value: true },
  { key: 'expiry', label: 'Expiry (days)', type: 'number', value: 90 },
  { key: 'history', label: 'Password History', type: 'number', value: 5 },
  { key: 'lockout', label: 'Lockout Attempts', type: 'number', value: 5 },
  { key: 'mfa', label: 'Require MFA', type: 'toggle', value: false },
])

// ── RBAC ─────────────────────────────────────────────────────
const permMatrixRoles = ['Super Admin', 'RM', 'Credit Analyst', 'Collections', 'Read Only']
const permMatrix = [
  { module: 'Leads & Deals', 'Super Admin': 'full', RM: 'full', 'Credit Analyst': 'read', Collections: 'none', 'Read Only': 'read' },
  { module: 'Customer 360', 'Super Admin': 'full', RM: 'full', 'Credit Analyst': 'full', Collections: 'read', 'Read Only': 'read' },
  { module: 'LOS', 'Super Admin': 'full', RM: 'write', 'Credit Analyst': 'full', Collections: 'none', 'Read Only': 'read' },
  { module: 'Credit Analysis', 'Super Admin': 'full', RM: 'read', 'Credit Analyst': 'full', Collections: 'none', 'Read Only': 'read' },
  { module: 'Collections', 'Super Admin': 'full', RM: 'read', 'Credit Analyst': 'none', Collections: 'full', 'Read Only': 'read' },
  { module: 'Admin Platform', 'Super Admin': 'full', RM: 'none', 'Credit Analyst': 'none', Collections: 'none', 'Read Only': 'none' },
]
const rolesSummary = [
  { role: 'Super Admin', users: 1, permissions: ['All Modules', 'RBAC', 'System Settings', 'Audit', 'Backup'] },
  { role: 'RM', users: 8, permissions: ['Leads', 'Deals', 'Customer 360', 'LOS', 'Omnichannel'] },
  { role: 'Credit Analyst', users: 3, permissions: ['Credit Analysis', 'LOS', 'Customer 360', 'Portfolio'] },
  { role: 'Collection Officer', users: 5, permissions: ['Collections', 'Customer 360 (Read)', 'Omnichannel'] },
  { role: 'IT Admin', users: 2, permissions: ['Admin Platform', 'API Keys', 'Backup', 'Audit'] },
  { role: 'Operations', users: 4, permissions: ['LOS (Ops steps)', 'Documents', 'Notifications', 'Tasks'] },
]

// ── API Keys ─────────────────────────────────────────────────
const apiKeys = ref([
  { id: 'k1', name: 'BNI Core Banking Integration', preview: 'sk_live_bniBNI****8x2k', scopes: ['Read', 'Write'], created: '2026-01-15', lastUsed: '2026-05-24', status: 'Active' },
  { id: 'k2', name: 'WhatsApp Business API', preview: 'sk_live_wa****m9qp', scopes: ['Messaging'], created: '2026-02-10', lastUsed: '2026-05-24', status: 'Active' },
  { id: 'k3', name: 'Privy e-Signature', preview: 'sk_live_privy****k3pl', scopes: ['Signing', 'Audit'], created: '2026-03-01', lastUsed: '2026-05-20', status: 'Active' },
  { id: 'k4', name: 'Legacy Report Export (deprecated)', preview: 'sk_test_dep****00x1', scopes: ['Read'], created: '2025-10-01', lastUsed: '2026-04-01', status: 'Inactive' },
])

// ── SLA Rules ────────────────────────────────────────────────
const slaRules = ref([
  { id: 'sla1', module: 'Omnichannel', priority: 'High', firstResponse: '15m', resolution: '2h', businessHours: 'Mon–Fri 08–17', escalateTo: 'Branch Manager', active: true },
  { id: 'sla2', module: 'Omnichannel', priority: 'Medium', firstResponse: '30m', resolution: '4h', businessHours: 'Mon–Fri 08–17', escalateTo: 'Team Lead', active: true },
  { id: 'sla3', module: 'Collections', priority: 'High', firstResponse: '1h', resolution: '24h', businessHours: 'Mon–Sat 08–18', escalateTo: 'Collection Head', active: true },
  { id: 'sla4', module: 'LOS — Credit Review', priority: 'High', firstResponse: '4h', resolution: '3d', businessHours: 'Mon–Fri 08–17', escalateTo: 'Credit Head', active: true },
  { id: 'sla5', module: 'LOS — Disbursement', priority: 'Medium', firstResponse: '2h', resolution: '1d', businessHours: 'Mon–Fri 08–17', escalateTo: 'Ops Manager', active: true },
  { id: 'sla6', module: 'Customer 360 — KYC Renewal', priority: 'Low', firstResponse: '1d', resolution: '7d', businessHours: 'Mon–Fri 08–17', escalateTo: 'Compliance', active: false },
])

// ── Notification Templates ───────────────────────────────────
const notifTemplates = ref([
  { id: 'nt1', name: 'Lead Assigned', trigger: 'Lead.Assigned', channels: ['Email', 'In-App'], active: true, body: 'Hi {{assignee}}, lead {{lead_name}} has been assigned to you. Please follow up within {{sla_hours}} hours.' },
  { id: 'nt2', name: 'SLA Breach Warning', trigger: 'SLA.AtRisk', channels: ['In-App', 'Push'], active: true, body: '⚠️ SLA for {{resource}} is about to breach in {{minutes}} minutes. Please take action.' },
  { id: 'nt3', name: 'LOS Step Approval', trigger: 'LOS.ApprovalRequired', channels: ['Email', 'In-App', 'Push'], active: true, body: 'Action required: Application {{app_id}} for {{customer}} is pending your approval at step {{step}}.' },
  { id: 'nt4', name: 'Collection PTP Reminder', trigger: 'Collection.PTPDue', channels: ['WhatsApp', 'SMS'], active: true, body: 'Reminder: PTP from {{customer}} of {{amount}} is due today.' },
  { id: 'nt5', name: 'Password Expiry', trigger: 'User.PasswordExpiringSoon', channels: ['Email'], active: true, body: 'Your password will expire in {{days}} days. Please update it at {{reset_url}}' },
  { id: 'nt6', name: 'Daily Digest', trigger: 'Schedule.Daily.08:00', channels: ['Email'], active: false, body: 'Good morning {{name}}, here is your daily summary: {{summary}}.' },
])

// ── Holidays ─────────────────────────────────────────────────
const holidays = ref([
  { id: 'h1', date: '01 Jan 2026', name: "New Year's Day", type: 'National' },
  { id: 'h2', date: '29 Jan 2026', name: 'Chinese New Year', type: 'National' },
  { id: 'h3', date: '17 Apr 2026', name: 'Good Friday', type: 'National' },
  { id: 'h4', date: '29–30 Mar 2026', name: 'Eid al-Fitr', type: 'National' },
  { id: 'h5', date: '01 May 2026', name: 'Labor Day', type: 'National' },
  { id: 'h6', date: '21 May 2026', name: 'Ascension of Jesus', type: 'National' },
  { id: 'h7', date: '17 Aug 2026', name: 'Independence Day', type: 'National' },
  { id: 'h8', date: '25 Dec 2026', name: 'Christmas Day', type: 'National' },
])

const workingHours = ref([
  { day: 'Monday', active: true, start: '08:00', end: '17:00' },
  { day: 'Tuesday', active: true, start: '08:00', end: '17:00' },
  { day: 'Wednesday', active: true, start: '08:00', end: '17:00' },
  { day: 'Thursday', active: true, start: '08:00', end: '17:00' },
  { day: 'Friday', active: true, start: '08:00', end: '17:00' },
  { day: 'Saturday', active: false, start: '09:00', end: '13:00' },
  { day: 'Sunday', active: false, start: '', end: '' },
])

// ── Custom Fields ────────────────────────────────────────────
const customFields = ref([
  { id: 'cf1', doctype: 'CRM Lead', label: 'NPWP Number', fieldType: 'Text', required: true },
  { id: 'cf2', doctype: 'CRM Lead', label: 'Business Sector', fieldType: 'Select', required: false },
  { id: 'cf3', doctype: 'CRM Deal', label: 'Collateral Type', fieldType: 'Select', required: false },
  { id: 'cf4', doctype: 'Contact', label: 'KTP Number', fieldType: 'Text', required: true },
  { id: 'cf5', doctype: 'CRM Organization', label: 'SIUP Number', fieldType: 'Text', required: false },
  { id: 'cf6', doctype: 'CRM Organization', label: 'Annual Revenue', fieldType: 'Currency', required: false },
])

// ── Localization ─────────────────────────────────────────────
const installedLanguages = [
  { code: 'id', flag: '🇮🇩', name: 'Bahasa Indonesia', coverage: 100, default: true },
  { code: 'en', flag: '🇬🇧', name: 'English', coverage: 94, default: false },
]

// ── System Settings ──────────────────────────────────────────
const systemSettings = ref([
  { key: 'dark_mode', label: 'Dark Mode Support', desc: 'Allow users to toggle dark theme', type: 'toggle', value: true },
  { key: 'mfa', label: 'MFA Required', desc: 'Force 2FA for all users', type: 'toggle', value: false },
  { key: 'session_timeout', label: 'Session Timeout', type: 'select', value: '60 min', options: ['15 min', '30 min', '60 min', '4h', '8h', 'Never'] },
  { key: 'audit_all', label: 'Full Audit Logging', desc: 'Log all read operations', type: 'toggle', value: true },
  { key: 'api_rate', label: 'API Rate Limit', type: 'select', value: '1000 req/min', options: ['100 req/min', '500 req/min', '1000 req/min', '5000 req/min'] },
  { key: 'email_notif', label: 'Email Notifications', type: 'toggle', value: true },
  { key: 'debug', label: 'Debug Mode', desc: 'Show error stack traces', type: 'toggle', value: false },
  { key: 'data_retention', label: 'Log Retention', type: 'select', value: '2 years', options: ['6 months', '1 year', '2 years', '5 years', 'Unlimited'] },
])

// ── Tenants ──────────────────────────────────────────────────
const tenants = ref([
  { id: 't1', name: 'BNI Production', subdomain: 'bni.summonos.id', users: 24, plan: 'Enterprise', status: 'Active', color: '#ea580c' },
  { id: 't2', name: 'BNI Staging', subdomain: 'bni-stg.summonos.id', users: 5, plan: 'Dev', status: 'Active', color: '#2563eb' },
])

// ── Backups ──────────────────────────────────────────────────
const backups = ref([
  { id: 'bk1', name: 'backup_20260524_0700.tar.gz', datetime: '2026-05-24 07:00', size: '4.2 GB', type: 'Full', status: 'Completed' },
  { id: 'bk2', name: 'backup_20260523_0700.tar.gz', datetime: '2026-05-23 07:00', size: '4.1 GB', type: 'Full', status: 'Completed' },
  { id: 'bk3', name: 'backup_20260522_0700.tar.gz', datetime: '2026-05-22 07:00', size: '4.0 GB', type: 'Full', status: 'Completed' },
  { id: 'bk4', name: 'backup_20260521_1800.tar.gz', datetime: '2026-05-21 18:00', size: '1.1 GB', type: 'Incremental', status: 'Completed' },
])

// ── Audit Logs ───────────────────────────────────────────────
const auditLogs = [
  { id: 'al1', timestamp: '2026-05-24 09:15:02', actor: 'Ahmad Santoso', action: 'Login', module: 'Users', resource: 'User Session', ip: '192.168.1.10', result: 'Success' },
  { id: 'al2', timestamp: '2026-05-24 09:20:14', actor: 'Ahmad Santoso', action: 'Create', module: 'Users', resource: 'User: Siti Rahayu', ip: '192.168.1.10', result: 'Success' },
  { id: 'al3', timestamp: '2026-05-24 08:42:00', actor: 'Dewi Pratama', action: 'Login', module: 'Users', resource: 'User Session', ip: '192.168.1.45', result: 'Success' },
  { id: 'al4', timestamp: '2026-05-24 08:05:30', actor: 'System', action: 'Create', module: 'Backup', resource: 'backup_20260524_0700.tar.gz', ip: 'localhost', result: 'Success' },
  { id: 'al5', timestamp: '2026-05-23 17:55:11', actor: 'Ahmad Santoso', action: 'Update', module: 'RBAC', resource: 'Role: Credit Analyst', ip: '192.168.1.10', result: 'Success' },
  { id: 'al6', timestamp: '2026-05-23 16:30:44', actor: 'IT Admin', action: 'Create', module: 'API', resource: 'API Key: BNI Core Banking', ip: '192.168.1.88', result: 'Success' },
  { id: 'al7', timestamp: '2026-05-23 14:12:08', actor: 'Unknown', action: 'Login', module: 'Users', resource: 'User: hacker@test.com', ip: '45.83.21.12', result: 'Failed' },
  { id: 'al8', timestamp: '2026-05-23 11:00:00', actor: 'Ahmad Santoso', action: 'Update', module: 'System', resource: 'System Settings', ip: '192.168.1.10', result: 'Success' },
  { id: 'al9', timestamp: '2026-05-22 10:44:22', actor: 'Ahmad Santoso', action: 'Export', module: 'Users', resource: 'User List (24 records)', ip: '192.168.1.10', result: 'Success' },
  { id: 'al10', timestamp: '2026-05-22 09:30:15', actor: 'Ahmad Santoso', action: 'Delete', module: 'API', resource: 'API Key: Legacy Report', ip: '192.168.1.10', result: 'Success' },
]

const filteredAuditLogs = computed(() => {
  return auditLogs.filter((log) => {
    const q = auditSearch.value.toLowerCase()
    const matchQ = !q || log.actor.toLowerCase().includes(q) || log.resource.toLowerCase().includes(q)
    const matchModule = !auditModule.value || log.module === auditModule.value
    const matchAction = !auditAction.value || log.action === auditAction.value
    return matchQ && matchModule && matchAction
  })
})

// ── Helpers ──────────────────────────────────────────────────
function avatarGradient(name) {
  const colors = ['#7c3aed', '#2563eb', '#059669', '#dc2626', '#d97706', '#0891b2', '#c026d3']
  return colors[name.charCodeAt(0) % colors.length]
}
function permIcon(level) {
  return level === 'full' ? '✅' : level === 'write' ? '✏️' : level === 'read' ? '👁️' : '🚫'
}

// ── Actions ──────────────────────────────────────────────────
function navigate(feat) {
  if (feat.route) {
    router.push(feat.route)
  } else if (feat.tab) {
    activeTab.value = feat.tab
    if (feat.subTab) {
      userSubTab.value = feat.subTab
      configSubTab.value = feat.subTab
    }
  }
}

function editUser(u) {
  inviteForm.value = { name: u.name, email: u.email, role: u.role, branch: u.branch }
  showInviteModal.value = true
}

function toggleUserStatus(u) {
  u.status = u.status === 'Active' ? 'Inactive' : 'Active'
}

function terminateSession(s) {
  activeSessions.value = activeSessions.value.filter((sess) => sess.id !== s.id)
}

function sendInvite() {
  if (!inviteForm.value.email || !inviteForm.value.name) return
  users.value.push({
    id: `u-${Date.now()}`,
    name: inviteForm.value.name,
    email: inviteForm.value.email,
    role: inviteForm.value.role,
    branch: inviteForm.value.branch,
    lastLogin: '—',
    status: 'Invited',
  })
  inviteForm.value = { name: '', email: '', role: 'RM', branch: '' }
  showInviteModal.value = false
}

function addBranch() {
  if (!branchForm.value.name) return
  branches.value.push({
    id: `b-${Date.now()}`,
    name: branchForm.value.name,
    code: branchForm.value.code,
    type: branchForm.value.type,
    region: branchForm.value.region,
    userCount: 0,
    facilities: 0,
    manager: branchForm.value.manager,
  })
  branchForm.value = { name: '', code: '', type: 'Sub-Branch', region: '', manager: '' }
  showBranchModal.value = false
}

function generateApiKey() {
  const id = `k-${Date.now()}`
  apiKeys.value.unshift({
    id,
    name: 'New API Key',
    preview: 'sk_live_new****' + Math.random().toString(36).slice(2, 6),
    scopes: ['Read'],
    created: new Date().toISOString().slice(0, 10),
    lastUsed: '—',
    status: 'Active',
  })
}

function revokeKey(key) {
  key.status = 'Inactive'
}

function removeHoliday(h) {
  holidays.value = holidays.value.filter((hol) => hol.id !== h.id)
}

function addCustomField() {
  if (!newField.value.label) return
  customFields.value.push({ id: `cf-${Date.now()}`, ...newField.value })
  newField.value = { doctype: fieldDoctype.value, label: '', fieldType: 'Text', required: false }
}

function removeCustomField(cf) {
  customFields.value = customFields.value.filter((f) => f.id !== cf.id)
}

function runBackup() {
  const name = `backup_${new Date().toISOString().slice(0, 10).replace(/-/g, '')}_manual.tar.gz`
  backups.value.unshift({ id: `bk-${Date.now()}`, name, datetime: new Date().toLocaleString('id-ID'), size: 'Running...', type: 'Full', status: 'Running' })
  setTimeout(() => {
    backups.value[0].status = 'Completed'
    backups.value[0].size = '4.3 GB'
  }, 3000)
}

function savePasswordPolicy() {}

usePageMeta(() => ({ title: __('Admin & Platform') }))
</script>
