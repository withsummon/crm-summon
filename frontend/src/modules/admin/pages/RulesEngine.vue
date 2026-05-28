<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #FF6600, #FF944D)"
          >
            <FeatherIcon name="cpu" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Rules Engine') }}
            </h1>
            <p class="truncate text-xs text-crm-muted">
              {{ __('Decision Management & Automation') }}
            </p>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button :label="__('Import Rules')" variant="outline" @click="showToast(__('Import initiated'))" />
          <Button :label="__('New Rule')" variant="solid" @click="openNewRuleModal" />
        </div>
      </template>
    </LayoutHeader>

    <!-- Page tabs -->
    <div class="flex items-center gap-1 border-b border-crm-border bg-white px-4">
      <button
        v-for="tab in pageTabs"
        :key="tab.key"
        class="flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium transition-colors"
        :class="activeTab === tab.key ? 'border-b-2 border-[#FF6600] text-[#FF6600]' : 'text-ink-gray-5 hover:text-ink-gray-8'"
        @click="activeTab = tab.key"
      >
        {{ __(tab.label) }}
        <span
          v-if="tab.badge"
          class="rounded-full bg-[#FF6600] px-1.5 text-[10px] text-white"
        >{{ tab.badge }}</span>
      </button>
    </div>

    <!-- ── LIBRARY TAB ── -->
    <div v-if="activeTab === 'library'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <!-- KPI Strip -->
      <div class="grid grid-cols-5 gap-3">
        <div
          v-for="kpi in libraryKpis"
          :key="kpi.label"
          class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between">
            <div class="text-xs text-ink-gray-4">{{ __(kpi.label) }}</div>
            <FeatherIcon :name="kpi.icon" class="h-4 w-4" :class="kpi.iconColor" />
          </div>
          <div class="mt-1 text-2xl font-bold" :class="kpi.valueColor || 'text-ink-gray-9'">
            {{ kpi.value }}
          </div>
          <div class="mt-0.5 text-[11px]" :class="kpi.deltaColor || 'text-ink-gray-4'">
            {{ kpi.delta }}
          </div>
        </div>
      </div>

      <!-- Filter Bar -->
      <div class="flex flex-wrap items-center gap-2 rounded-[14px] border border-crm-border bg-white px-4 py-3 shadow-sm">
        <input
          v-model="listSearch"
          class="h-8 rounded-md border border-outline-gray-2 px-3 text-sm"
          style="width: 220px"
          :placeholder="__('Search rules...')"
        />
        <select v-model="filterCategory" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">{{ __('All Categories') }}</option>
          <option v-for="c in categories" :key="c" :value="c">{{ __(c) }}</option>
        </select>
        <select v-model="filterStatus" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">{{ __('All Status') }}</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ __(s) }}</option>
        </select>
        <select v-model="filterModule" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">{{ __('All Modules') }}</option>
          <option v-for="m in modules" :key="m" :value="m">{{ __(m) }}</option>
        </select>
        <div class="ml-auto text-xs text-ink-gray-4">{{ filteredRules.length }} {{ __('rules') }}</div>
      </div>

      <!-- Rules Table -->
      <div class="flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <div class="h-full overflow-y-auto">
          <table class="w-full text-xs">
            <thead class="sticky top-0 bg-surface-gray-1">
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Rule Name') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Category') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Module') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Status') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Version') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Last Modified') }}</th>
                <th class="px-4 py-2.5 text-right font-medium">{{ __('Hit Rate') }}</th>
                <th class="px-4 py-2.5 text-center font-medium">{{ __('Actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="rule in filteredRules"
                :key="rule.id"
                class="group cursor-pointer border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
              >
                <td class="px-4 py-2.5">
                  <div class="font-medium text-ink-gray-8">{{ rule.name }}</div>
                  <div class="mt-0.5 text-[10px] text-ink-gray-4">{{ rule.description }}</div>
                </td>
                <td class="px-4 py-2.5">
                  <Badge :label="__(rule.category)" variant="subtle" :theme="categoryTheme(rule.category)" />
                </td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ rule.module }}</td>
                <td class="px-4 py-2.5">
                  <Badge :label="__(rule.status)" variant="subtle" :theme="statusTheme(rule.status)" />
                </td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ rule.version }}</td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ rule.lastModified }}</td>
                <td class="px-4 py-2.5 text-right">
                  <span v-if="rule.hitRate !== null" class="font-semibold" :class="rule.hitRate >= 70 ? 'text-green-600' : rule.hitRate >= 40 ? 'text-amber-600' : 'text-ink-gray-5'">
                    {{ rule.hitRate }}%
                  </span>
                  <span v-else class="text-ink-gray-3">—</span>
                </td>
                <td class="px-4 py-2.5">
                  <div class="flex items-center justify-center gap-1 opacity-0 transition-opacity group-hover:opacity-100" @click.stop>
                    <Button icon="edit-2" variant="ghost" size="sm" :title="__('Edit')" @click="editRule(rule)" />
                    <Button icon="copy" variant="ghost" size="sm" :title="__('Clone')" @click="openCloneModal(rule)" />
                    <Button icon="play" variant="ghost" size="sm" :title="__('Test')" @click="testRule(rule)" />
                    <Button icon="archive" variant="ghost" size="sm" :title="__('Archive')" @click="archiveRule(rule)" />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── BUILDER TAB ── -->
    <div v-if="activeTab === 'builder'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="grid grid-cols-5 gap-4">
        <!-- Left Panel — Rule Configuration -->
        <div class="col-span-2 space-y-4">
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
            <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Rule Configuration') }}</div>
            <div class="space-y-3 text-sm">
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Rule Name') }}</label>
                <input v-model="builderForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Category') }}</label>
                <select v-model="builderForm.category" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                  <option v-for="c in categories" :key="c" :value="c">{{ __(c) }}</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Description') }}</label>
                <textarea v-model="builderForm.description" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Priority') }}</label>
                  <select v-model="builderForm.priority" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                    <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
                  </select>
                </div>
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Module') }}</label>
                  <select v-model="builderForm.module" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
                    <option v-for="m in modules" :key="m" :value="m">{{ __(m) }}</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Effective From') }}</label>
                  <input v-model="builderForm.effectiveFrom" type="date" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
                </div>
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Effective To') }}</label>
                  <input v-model="builderForm.effectiveTo" type="date" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
                </div>
              </div>
            </div>
          </div>

          <!-- IF Conditions -->
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm" style="border-left: 3px solid #0891b2">
            <div class="mb-3 flex items-center justify-between">
              <div class="text-sm font-semibold text-[#004D73]">{{ __('IF') }}</div>
              <div class="flex gap-1">
                <button
                  v-for="logic in ['AND', 'OR']"
                  :key="logic"
                  class="rounded px-2 py-0.5 text-[10px] font-semibold"
                  :class="builderForm.conditionLogic === logic ? 'bg-[#FF6600] text-white' : 'bg-surface-gray-2 text-ink-gray-5'"
                  @click="builderForm.conditionLogic = logic"
                >
                  {{ logic }}
                </button>
              </div>
            </div>
            <div class="space-y-2">
              <div
                v-for="(cond, idx) in builderForm.conditions"
                :key="idx"
                class="flex items-center gap-2 rounded-lg bg-surface-gray-1 p-2"
              >
                <select v-model="cond.field" class="h-7 flex-1 rounded border border-outline-gray-2 px-1 text-[11px]">
                  <option v-for="f in conditionFields" :key="f" :value="f">{{ f }}</option>
                </select>
                <select v-model="cond.operator" class="h-7 w-24 rounded border border-outline-gray-2 px-1 text-[11px]">
                  <option v-for="op in operators" :key="op.value" :value="op.value">{{ op.label }}</option>
                </select>
                <input v-model="cond.value" class="h-7 w-24 rounded border border-outline-gray-2 px-2 text-[11px]" :placeholder="__('Value')" />
                <button class="text-ink-gray-3 hover:text-red-500" @click="builderForm.conditions.splice(idx, 1)">✕</button>
              </div>
            </div>
            <div class="mt-2 flex gap-2">
              <button class="text-xs text-[#FF6600] hover:underline" @click="addCondition">+ {{ __('Add Condition') }}</button>
              <button class="text-xs text-[#FF6600] hover:underline" @click="addConditionGroup">+ {{ __('Add Group (OR)') }}</button>
            </div>
          </div>

          <!-- THEN Actions -->
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm" style="border-left: 3px solid #22c55e">
            <div class="mb-3 text-sm font-semibold text-green-700">{{ __('THEN') }}</div>
            <div class="space-y-2">
              <div
                v-for="(action, idx) in builderForm.thenActions"
                :key="idx"
                class="flex items-center gap-2 rounded-lg bg-surface-gray-1 p-2"
              >
                <select v-model="action.type" class="h-7 flex-1 rounded border border-outline-gray-2 px-1 text-[11px]">
                  <option v-for="at in actionTypes" :key="at" :value="at">{{ at }}</option>
                </select>
                <input v-model="action.params" class="h-7 flex-1 rounded border border-outline-gray-2 px-2 text-[11px]" :placeholder="__('Parameters')" />
                <button class="text-ink-gray-3 hover:text-red-500" @click="builderForm.thenActions.splice(idx, 1)">✕</button>
              </div>
            </div>
            <button class="mt-2 text-xs text-green-600 hover:underline" @click="addThenAction">+ {{ __('Add Action') }}</button>
          </div>

          <!-- ELSE Actions -->
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm" style="border-left: 3px solid #f59e0b">
            <button class="flex w-full items-center justify-between" @click="showElse = !showElse">
              <div class="text-sm font-semibold text-amber-700">{{ __('ELSE') }}</div>
              <FeatherIcon :name="showElse ? 'chevron-up' : 'chevron-down'" class="h-4 w-4 text-ink-gray-4" />
            </button>
            <div v-if="showElse" class="mt-3 space-y-2">
              <div
                v-for="(action, idx) in builderForm.elseActions"
                :key="idx"
                class="flex items-center gap-2 rounded-lg bg-surface-gray-1 p-2"
              >
                <select v-model="action.type" class="h-7 flex-1 rounded border border-outline-gray-2 px-1 text-[11px]">
                  <option v-for="at in actionTypes" :key="at" :value="at">{{ at }}</option>
                </select>
                <input v-model="action.params" class="h-7 flex-1 rounded border border-outline-gray-2 px-2 text-[11px]" :placeholder="__('Parameters')" />
                <button class="text-ink-gray-3 hover:text-red-500" @click="builderForm.elseActions.splice(idx, 1)">✕</button>
              </div>
              <button class="text-xs text-amber-600 hover:underline" @click="addElseAction">+ {{ __('Add Action') }}</button>
            </div>
          </div>

          <!-- Footer Buttons -->
          <div class="flex gap-2">
            <Button :label="__('Save Draft')" variant="subtle" class="flex-1" @click="showToast(__('Draft saved'))" />
            <Button :label="__('Submit for Approval')" variant="outline" class="flex-1" @click="showApprovalModal = true" />
            <Button :label="__('Publish')" variant="solid" class="flex-1" @click="showToast(__('Rule published'))" />
          </div>
        </div>

        <!-- Right Panel — Live Preview -->
        <div class="col-span-3 space-y-4">
          <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
            <div class="mb-4 text-sm font-semibold text-ink-gray-8">{{ __('Flow Diagram') }}</div>
            <!-- Flow diagram using CSS -->
            <div class="flex flex-col items-center gap-0">
              <!-- START node -->
              <div class="rounded-full bg-[#006699] px-6 py-2 text-xs font-semibold text-white shadow">{{ __('START') }}</div>
              <div class="h-6 w-px border-l-2 border-dashed border-[#0088BB]"></div>

              <!-- Condition block -->
              <div class="relative rounded-lg border-2 border-[#006699] bg-[#E0F0FF] px-6 py-3 text-center shadow-sm">
                <div class="text-[10px] font-semibold uppercase text-[#006699]">{{ __('Conditions') }} ({{ builderForm.conditionLogic }})</div>
                <div v-for="(cond, idx) in builderForm.conditions" :key="idx" class="mt-1 text-xs text-ink-gray-7">
                  <span class="font-mono text-[#004D73]">{{ cond.field }}</span>
                  <span class="mx-1 font-bold">{{ cond.operator }}</span>
                  <span class="font-mono text-[#004D73]">{{ cond.value }}</span>
                </div>
              </div>
              <div class="h-4 w-px border-l-2 border-dashed border-ink-gray-3"></div>

              <!-- Branch split -->
              <div class="flex w-full items-start justify-center gap-8">
                <!-- THEN branch -->
                <div class="flex flex-col items-center">
                  <div class="mb-1 text-[10px] font-semibold text-green-600">{{ __('TRUE') }} ✓</div>
                  <div class="h-4 w-px border-l-2 border-dashed border-green-300"></div>
                  <div class="rounded-lg border-2 border-green-400 bg-green-50 px-5 py-3 shadow-sm">
                    <div class="text-[10px] font-semibold uppercase text-green-600">{{ __('THEN') }}</div>
                    <div v-for="(action, idx) in builderForm.thenActions" :key="idx" class="mt-1 text-xs text-ink-gray-7">
                      <span class="font-semibold text-green-700">{{ action.type }}</span>: {{ action.params }}
                    </div>
                  </div>
                </div>

                <!-- ELSE branch -->
                <div class="flex flex-col items-center">
                  <div class="mb-1 text-[10px] font-semibold text-amber-600">{{ __('FALSE') }} ✗</div>
                  <div class="h-4 w-px border-l-2 border-dashed border-amber-300"></div>
                  <div class="rounded-lg border-2 border-amber-400 bg-amber-50 px-5 py-3 shadow-sm">
                    <div class="text-[10px] font-semibold uppercase text-amber-600">{{ __('ELSE') }}</div>
                    <div v-for="(action, idx) in builderForm.elseActions" :key="idx" class="mt-1 text-xs text-ink-gray-7">
                      <span class="font-semibold text-amber-700">{{ action.type }}</span>: {{ action.params }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-4 h-6 w-px border-l-2 border-dashed border-ink-gray-3"></div>
              <!-- END node -->
              <div class="rounded-full bg-ink-gray-5 px-6 py-2 text-xs font-semibold text-white shadow">{{ __('END') }}</div>
            </div>
          </div>

          <!-- Rule Summary -->
          <div class="rounded-[14px] border border-crm-border bg-white p-5 shadow-sm">
            <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Rule Summary') }}</div>
            <div class="rounded-lg bg-surface-gray-1 p-4 text-sm leading-relaxed text-ink-gray-7">
              <p>
                <span class="font-semibold text-ink-gray-8">{{ __('IF') }}</span>
                <span v-for="(cond, idx) in builderForm.conditions" :key="idx">
                  <span class="font-mono text-[#004D73]">{{ cond.field }}</span>
                  <span class="mx-1 font-bold">{{ cond.operator }}</span>
                  <span class="font-mono text-[#004D73]">{{ cond.value }}</span>
                  <span v-if="idx < builderForm.conditions.length - 1" class="mx-1 font-semibold text-ink-gray-5">{{ builderForm.conditionLogic }}</span>
                </span>
              </p>
              <p class="mt-2">
                <span class="font-semibold text-green-700">{{ __('THEN') }}:</span>
                <span v-for="(action, idx) in builderForm.thenActions" :key="idx" class="ml-1">
                  {{ action.type }}({{ action.params }})<span v-if="idx < builderForm.thenActions.length - 1">, </span>
                </span>
              </p>
              <p v-if="builderForm.elseActions.length" class="mt-1">
                <span class="font-semibold text-amber-700">{{ __('ELSE') }}:</span>
                <span v-for="(action, idx) in builderForm.elseActions" :key="idx" class="ml-1">
                  {{ action.type }}({{ action.params }})<span v-if="idx < builderForm.elseActions.length - 1">, </span>
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── DECISION TREES TAB ── -->
    <div v-if="activeTab === 'trees'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <!-- Toggle -->
      <div class="flex items-center gap-2">
        <button
          v-if="selectedTree"
          class="flex items-center gap-1 rounded-md border border-outline-gray-2 px-3 py-1.5 text-xs text-ink-gray-5 hover:bg-surface-gray-2"
          @click="selectedTree = null"
        >
          <FeatherIcon name="arrow-left" class="h-3 w-3" /> {{ __('Back to List') }}
        </button>
        <div v-else class="flex gap-1">
          <button
            class="rounded-md px-3 py-1.5 text-xs font-medium"
            :class="treeView === 'list' ? 'bg-\[#FF6600\] text-white' : 'bg-surface-gray-2 text-ink-gray-5'"
            @click="treeView = 'list'"
          >
            {{ __('Tree List') }}
          </button>
          <button
            class="rounded-md px-3 py-1.5 text-xs font-medium"
            :class="treeView === 'canvas' ? 'bg-\[#FF6600\] text-white' : 'bg-surface-gray-2 text-ink-gray-5'"
            @click="treeView = 'canvas'"
          >
            {{ __('Tree Canvas') }}
          </button>
        </div>
      </div>

      <!-- Tree List View -->
      <div v-if="!selectedTree && treeView === 'list'" class="grid grid-cols-3 gap-4">
        <div
          v-for="tree in decisionTrees"
          :key="tree.id"
          class="cursor-pointer rounded-[14px] border border-crm-border bg-white p-4 shadow-sm transition-all hover:shadow-md"
          @click="selectedTree = tree"
        >
          <div class="flex items-start justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ tree.name }}</div>
            <Badge :label="__(tree.type)" variant="subtle" :theme="categoryTheme(tree.type)" />
          </div>
          <div class="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span class="text-ink-gray-4">{{ __('Nodes') }}:</span>
              <span class="ml-1 font-medium text-ink-gray-7">{{ tree.nodes }}</span>
            </div>
            <div>
              <span class="text-ink-gray-4">{{ __('Depth') }}:</span>
              <span class="ml-1 font-medium text-ink-gray-7">{{ tree.depth }}</span>
            </div>
          </div>
          <div class="mt-2 flex items-center justify-between">
            <Badge :label="__(tree.status)" variant="subtle" :theme="statusTheme(tree.status)" />
            <span class="text-[10px] text-ink-gray-4">{{ tree.lastModified }}</span>
          </div>
          <Button :label="__('Open')" variant="subtle" size="sm" class="mt-3 w-full" @click.stop="selectedTree = tree" />
        </div>
      </div>

      <!-- Tree Canvas View (when no tree selected and canvas mode) -->
      <div v-if="!selectedTree && treeView === 'canvas'" class="flex flex-col items-center justify-center rounded-[14px] border border-crm-border bg-white py-20 shadow-sm">
        <FeatherIcon name="git-branch" class="mb-4 h-12 w-12 text-ink-gray-3" />
        <div class="text-sm font-medium text-ink-gray-5">{{ __('Select a decision tree to view') }}</div>
        <Button :label="__('Browse Trees')" variant="subtle" size="sm" class="mt-3" @click="treeView = 'list'" />
      </div>

      <!-- Tree Canvas Detail -->
      <div v-if="selectedTree" class="rounded-[14px] border border-crm-border bg-white p-6 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <div class="text-sm font-semibold text-ink-gray-8">{{ selectedTree.name }}</div>
            <div class="text-[10px] text-ink-gray-4">{{ selectedTree.nodes }} {{ __('nodes') }} · {{ __('Depth') }} {{ selectedTree.depth }}</div>
          </div>
          <Badge :label="__(selectedTree.status)" variant="subtle" :theme="statusTheme(selectedTree.status)" />
        </div>

        <!-- CSS Tree -->
        <div class="tree-container pl-4">
          <!-- Root node -->
          <div class="tree-node">
            <div class="inline-block cursor-pointer rounded-lg bg-[#006699] px-4 py-2 text-xs font-semibold text-white shadow hover:bg-[#004D73]">
              {{ __('Age >= 21?') }}
            </div>
            <div class="tree-children">
              <!-- No branch -->
              <div class="tree-node">
                <div class="inline-block cursor-pointer rounded-lg bg-red-100 px-4 py-2 text-xs font-medium text-red-700 shadow-sm hover:bg-red-200">
                  {{ __('REJECT: Under age') }}
                </div>
              </div>
              <!-- Yes branch -->
              <div class="tree-node">
                <div class="inline-block cursor-pointer rounded-lg bg-[#CCE5F5] px-4 py-2 text-xs font-medium text-[#004D73] shadow-sm hover:bg-[#B3D9F0]">
                  {{ __('SLIK Score >= 500?') }}
                </div>
                <div class="tree-children">
                  <div class="tree-node">
                    <div class="inline-block cursor-pointer rounded-lg bg-red-100 px-4 py-2 text-xs font-medium text-red-700 shadow-sm hover:bg-red-200">
                      {{ __('REJECT: Poor credit history') }}
                    </div>
                  </div>
                  <div class="tree-node">
                    <div class="inline-block cursor-pointer rounded-lg bg-[#CCE5F5] px-4 py-2 text-xs font-medium text-[#004D73] shadow-sm hover:bg-[#B3D9F0]">
                      {{ __('Monthly Income >= Rp 15M?') }}
                    </div>
                    <div class="tree-children">
                      <div class="tree-node">
                        <div class="inline-block cursor-pointer rounded-lg bg-amber-100 px-4 py-2 text-xs font-medium text-amber-700 shadow-sm hover:bg-amber-200">
                          {{ __('Manual Review: Low income') }}
                        </div>
                      </div>
                      <div class="tree-node">
                        <div class="inline-block cursor-pointer rounded-lg bg-[#CCE5F5] px-4 py-2 text-xs font-medium text-[#004D73] shadow-sm hover:bg-[#B3D9F0]">
                          {{ __('Loan Amount?') }}
                        </div>
                        <div class="tree-children">
                          <div class="tree-node">
                            <div class="inline-block cursor-pointer rounded-lg bg-green-100 px-4 py-2 text-xs font-medium text-green-700 shadow-sm hover:bg-green-200">
                              {{ __('AUTO APPROVE: Standard (≤ Rp 500M)') }}
                            </div>
                          </div>
                          <div class="tree-node">
                            <div class="inline-block cursor-pointer rounded-lg bg-blue-100 px-4 py-2 text-xs font-medium text-blue-700 shadow-sm hover:bg-blue-200">
                              {{ __('Committee Review: Large exposure (> Rp 500M)') }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SANDBOX TAB ── -->
    <div v-if="activeTab === 'sandbox'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <div class="grid grid-cols-2 gap-4">
        <!-- Left: Test Input Panel -->
        <div class="space-y-4">
          <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
            <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Simulation Parameters') }}</div>

            <!-- Select Rules -->
            <div class="mb-3">
              <label class="flex items-center gap-2 text-xs">
                <input v-model="sandboxForm.testAll" type="checkbox" class="rounded" />
                <span class="font-medium text-ink-gray-7">{{ __('Test All Active Rules') }}</span>
              </label>
            </div>
            <div v-if="!sandboxForm.testAll" class="mb-3 max-h-32 space-y-1 overflow-y-auto rounded-lg bg-surface-gray-1 p-2">
              <label
                v-for="rule in rules.filter(r => r.status === 'Active').slice(0, 8)"
                :key="rule.id"
                class="flex items-center gap-2 text-xs"
              >
                <input v-model="sandboxForm.selectedRules" type="checkbox" :value="rule.id" class="rounded" />
                <span class="text-ink-gray-6">{{ rule.name }}</span>
              </label>
            </div>

            <hr class="my-3 border-outline-gray-1" />

            <!-- Applicant Profile -->
            <div class="mb-2 text-xs font-semibold text-ink-gray-6">{{ __('Applicant Profile') }}</div>
            <div class="space-y-2 text-sm">
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Applicant Name') }}</label>
                <input v-model="sandboxForm.applicantName" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-3 text-xs" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Applicant Age') }}</label>
                  <input v-model.number="sandboxForm.applicantAge" type="number" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-3 text-xs" />
                </div>
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Credit Score') }}</label>
                  <input v-model.number="sandboxForm.creditScore" type="number" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-3 text-xs" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('SLIK Score') }}</label>
                  <input v-model.number="sandboxForm.slikScore" type="number" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-3 text-xs" />
                </div>
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Monthly Income (IDR)') }}</label>
                  <input v-model="sandboxForm.monthlyIncome" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-3 text-xs" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Employment Type') }}</label>
                  <select v-model="sandboxForm.employmentType" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-2 text-xs">
                    <option v-for="e in ['Employed', 'Self-Employed', 'Business Owner', 'Retired']" :key="e" :value="e">{{ __(e) }}</option>
                  </select>
                </div>
                <div>
                  <label class="flex items-center gap-2 pt-5 text-xs text-ink-gray-5">
                    <input v-model="sandboxForm.existingCustomer" type="checkbox" class="rounded" />
                    {{ __('Existing Customer') }}
                  </label>
                </div>
              </div>
            </div>

            <hr class="my-3 border-outline-gray-1" />

            <!-- Loan Details -->
            <div class="mb-2 text-xs font-semibold text-ink-gray-6">{{ __('Loan Details') }}</div>
            <div class="space-y-2 text-sm">
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Product Type') }}</label>
                <select v-model="sandboxForm.productType" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-2 text-xs">
                  <option v-for="p in ['KMK', 'KI', 'KPR', 'KKB', 'Personal Loan']" :key="p" :value="p">{{ p }}</option>
                </select>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Loan Amount (IDR)') }}</label>
                  <input v-model="sandboxForm.loanAmount" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-3 text-xs" />
                </div>
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Tenor (months)') }}</label>
                  <input v-model.number="sandboxForm.tenor" type="number" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-3 text-xs" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Collateral Type') }}</label>
                  <select v-model="sandboxForm.collateralType" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-2 text-xs">
                    <option v-for="c in ['Property', 'Vehicle', 'Deposit', 'Stock', 'None']" :key="c" :value="c">{{ __(c) }}</option>
                  </select>
                </div>
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('Collateral Value (IDR)') }}</label>
                  <input v-model="sandboxForm.collateralValue" class="mt-1 h-8 w-full rounded-md border border-outline-gray-2 px-3 text-xs" />
                </div>
              </div>
            </div>

            <!-- Preset Buttons -->
            <div class="mt-3 flex gap-2">
              <button class="flex-1 rounded-md bg-green-50 py-1.5 text-[10px] font-semibold text-green-700 hover:bg-green-100" @click="setPreset('good')">
                {{ __('Good Applicant') }}
              </button>
              <button class="flex-1 rounded-md bg-amber-50 py-1.5 text-[10px] font-semibold text-amber-700 hover:bg-amber-100" @click="setPreset('risky')">
                {{ __('Risky Applicant') }}
              </button>
              <button class="flex-1 rounded-md bg-blue-50 py-1.5 text-[10px] font-semibold text-blue-700 hover:bg-blue-100" @click="setPreset('edge')">
                {{ __('Edge Case') }}
              </button>
            </div>

            <!-- Run Simulation -->
            <Button
              :label="simulationRunning ? __('Running...') : __('Run Simulation')"
              variant="solid"
              class="mt-4 w-full"
              :loading="simulationRunning"
              @click="runSimulation"
            />
          </div>
        </div>

        <!-- Right: Results Panel -->
        <div>
          <!-- Empty state -->
          <div v-if="!simulationRun" class="flex flex-col items-center justify-center rounded-[14px] border border-crm-border bg-white py-24 shadow-sm">
            <FeatherIcon name="play-circle" class="mb-4 h-12 w-12 text-ink-gray-3" />
            <div class="text-sm font-medium text-ink-gray-5">{{ __('Run a simulation to see results') }}</div>
            <div class="mt-1 text-xs text-ink-gray-4">{{ __('Configure parameters and click Run Simulation') }}</div>
          </div>

          <!-- Results -->
          <div v-else class="space-y-4">
            <!-- Decision Banner -->
            <div
              class="rounded-[14px] border-2 p-5 text-center shadow-sm"
              :class="simResult.decision === 'APPROVED' ? 'border-green-400 bg-green-50' : simResult.decision === 'MANUAL REVIEW' ? 'border-amber-400 bg-amber-50' : 'border-red-400 bg-red-50'"
            >
              <div class="text-2xl font-bold" :class="simResult.decision === 'APPROVED' ? 'text-green-700' : simResult.decision === 'MANUAL REVIEW' ? 'text-amber-700' : 'text-red-700'">
                {{ __(simResult.decision) }}
              </div>
              <div class="mt-1 text-sm" :class="simResult.decision === 'APPROVED' ? 'text-green-600' : simResult.decision === 'MANUAL REVIEW' ? 'text-amber-600' : 'text-red-600'">
                {{ __('Confidence') }}: {{ simResult.confidence }}%
              </div>
            </div>

            <!-- Execution Timeline -->
            <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
              <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Execution Timeline') }}</div>
              <div class="space-y-2">
                <div
                  v-for="(entry, idx) in simResult.timeline"
                  :key="idx"
                  class="flex items-center gap-3 rounded-lg bg-surface-gray-1 px-3 py-2"
                >
                  <FeatherIcon
                    :name="entry.result === 'pass' ? 'check-circle' : entry.result === 'fail' ? 'x-circle' : 'minus-circle'"
                    class="h-4 w-4 shrink-0"
                    :class="entry.result === 'pass' ? 'text-green-500' : entry.result === 'fail' ? 'text-red-500' : 'text-ink-gray-4'"
                  />
                  <div class="min-w-0 flex-1">
                    <div class="text-xs font-medium text-ink-gray-7">{{ entry.rule }}</div>
                  </div>
                  <span class="text-[10px] text-ink-gray-4">{{ entry.duration }}ms</span>
                  <Badge
                    :label="__(entry.result)"
                    variant="subtle"
                    :theme="entry.result === 'pass' ? 'green' : entry.result === 'fail' ? 'red' : 'gray'"
                  />
                </div>
              </div>
            </div>

            <!-- Output Variables -->
            <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
              <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Output Variables') }}</div>
              <table class="w-full text-xs">
                <thead>
                  <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                    <th class="pb-2 text-left font-medium">{{ __('Variable') }}</th>
                    <th class="pb-2 text-left font-medium">{{ __('Value') }}</th>
                    <th class="pb-2 text-left font-medium">{{ __('Set By') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(v, idx) in simResult.outputVars" :key="idx" class="border-b border-outline-gray-1 last:border-0">
                    <td class="py-1.5 font-mono text-[#004D73]">{{ v.name }}</td>
                    <td class="py-1.5 font-medium text-ink-gray-7">{{ v.value }}</td>
                    <td class="py-1.5 text-ink-gray-5">{{ v.setBy }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Warnings -->
            <div v-if="simResult.warnings.length" class="rounded-[14px] border border-amber-300 bg-amber-50 p-4 shadow-sm">
              <div class="mb-2 text-sm font-semibold text-amber-800">{{ __('Warnings') }}</div>
              <div v-for="(w, idx) in simResult.warnings" :key="idx" class="flex items-start gap-2 text-xs text-amber-700">
                <FeatherIcon name="alert-triangle" class="mt-0.5 h-3 w-3 shrink-0" />
                <span>{{ w }}</span>
              </div>
            </div>

            <!-- Execution Summary -->
            <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
              <div class="mb-2 text-sm font-semibold text-ink-gray-8">{{ __('Execution Summary') }}</div>
              <div class="grid grid-cols-5 gap-2 text-center text-xs">
                <div class="rounded-lg bg-surface-gray-1 p-2">
                  <div class="text-lg font-bold text-ink-gray-8">{{ simResult.summary.total }}</div>
                  <div class="text-ink-gray-4">{{ __('Checked') }}</div>
                </div>
                <div class="rounded-lg bg-green-50 p-2">
                  <div class="text-lg font-bold text-green-600">{{ simResult.summary.passed }}</div>
                  <div class="text-green-500">{{ __('Passed') }}</div>
                </div>
                <div class="rounded-lg bg-red-50 p-2">
                  <div class="text-lg font-bold text-red-600">{{ simResult.summary.failed }}</div>
                  <div class="text-red-500">{{ __('Failed') }}</div>
                </div>
                <div class="rounded-lg bg-surface-gray-1 p-2">
                  <div class="text-lg font-bold text-ink-gray-5">{{ simResult.summary.skipped }}</div>
                  <div class="text-ink-gray-4">{{ __('Skipped') }}</div>
                </div>
                <div class="rounded-lg bg-[#FFF0E0] p-2">
                  <div class="text-lg font-bold text-[#FF6600]">{{ simResult.summary.totalTime }}ms</div>
                  <div class="text-[#FF6600]">{{ __('Total Time') }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── LOGS TAB ── -->
    <div v-if="activeTab === 'logs'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <!-- KPI Strip -->
      <div class="grid grid-cols-4 gap-3">
        <div v-for="kpi in logsKpis" :key="kpi.label" class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-xs text-ink-gray-4">{{ __(kpi.label) }}</div>
          <div class="mt-1 text-2xl font-bold" :class="kpi.color || 'text-ink-gray-9'">{{ kpi.value }}</div>
          <div v-if="kpi.sub" class="mt-0.5 text-[10px] text-ink-gray-4">{{ kpi.sub }}</div>
        </div>
      </div>

      <!-- Filter Bar -->
      <div class="flex flex-wrap items-center gap-2 rounded-[14px] border border-crm-border bg-white px-4 py-3 shadow-sm">
        <div class="flex gap-1">
          <button
            v-for="period in ['Today', '7d', '30d']"
            :key="period"
            class="rounded-md px-2.5 py-1 text-xs"
            :class="logsPeriod === period ? 'bg-\[#FF6600\] text-white' : 'bg-surface-gray-2 text-ink-gray-5'"
            @click="logsPeriod = period"
          >
            {{ __(period) }}
          </button>
        </div>
        <select v-model="logsRuleFilter" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">{{ __('All Rules') }}</option>
          <option v-for="r in rules.filter(r => r.status === 'Active')" :key="r.id" :value="r.name">{{ r.name }}</option>
        </select>
        <select v-model="logsStatusFilter" class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs">
          <option value="">{{ __('All Status') }}</option>
          <option v-for="s in ['Passed', 'Failed', 'Error', 'Skipped']" :key="s" :value="s">{{ __(s) }}</option>
        </select>
        <input v-model="logsSearch" class="h-8 rounded-md border border-outline-gray-2 px-3 text-xs" style="width: 180px" :placeholder="__('Search logs...')" />
      </div>

      <!-- Logs Table -->
      <div class="flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <div class="h-full overflow-y-auto">
          <table class="w-full text-xs">
            <thead class="sticky top-0 bg-surface-gray-1">
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Timestamp') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Rule Name') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Trigger') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Input Summary') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Decision') }}</th>
                <th class="px-4 py-2.5 text-right font-medium">{{ __('Duration') }}</th>
                <th class="px-4 py-2.5 text-left font-medium">{{ __('Status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="log in filteredLogs"
                :key="log.id"
                class="cursor-pointer border-b border-outline-gray-1 hover:bg-surface-gray-1 last:border-0"
                @click="openLogDetail(log)"
              >
                <td class="px-4 py-2.5 font-mono text-ink-gray-5">{{ log.timestamp }}</td>
                <td class="px-4 py-2.5 font-medium text-ink-gray-8">{{ log.ruleName }}</td>
                <td class="px-4 py-2.5 text-ink-gray-5">{{ log.trigger }}</td>
                <td class="max-w-[200px] truncate px-4 py-2.5 text-ink-gray-5">{{ log.inputSummary }}</td>
                <td class="px-4 py-2.5">
                  <span class="font-medium" :class="log.decision === 'Approved' ? 'text-green-600' : log.decision === 'Rejected' ? 'text-red-600' : 'text-amber-600'">
                    {{ __(log.decision) }}
                  </span>
                </td>
                <td class="px-4 py-2.5 text-right text-ink-gray-5">{{ log.duration }}ms</td>
                <td class="px-4 py-2.5">
                  <Badge :label="__(log.status)" variant="subtle" :theme="log.status === 'Passed' ? 'green' : log.status === 'Failed' ? 'red' : log.status === 'Error' ? 'red' : 'gray'" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── ANALYTICS TAB ── -->
    <div v-if="activeTab === 'analytics'" class="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-surface-gray-1 p-4">
      <!-- KPI Row -->
      <div class="grid grid-cols-4 gap-3">
        <div v-for="kpi in analyticsKpis" :key="kpi.label" class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-xs text-ink-gray-4">{{ __(kpi.label) }}</div>
          <div class="mt-1 text-2xl font-bold" :class="kpi.color || 'text-ink-gray-9'">{{ kpi.value }}</div>
          <div v-if="kpi.sub" class="mt-0.5 text-[10px] text-ink-gray-4">{{ kpi.sub }}</div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <!-- Rule Execution Volume (Top 10) -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Rule Execution Volume (Top 10)') }}</div>
          <div class="space-y-2">
            <div v-for="item in executionVolume" :key="item.name" class="flex items-center gap-2 text-xs">
              <div class="w-36 truncate text-ink-gray-6">{{ item.name }}</div>
              <div class="flex-1">
                <div class="h-5 overflow-hidden rounded bg-surface-gray-2">
                  <div class="flex h-5 items-center rounded bg-[#FF6600] px-2 text-[10px] font-medium text-white" :style="{ width: item.pct + '%' }">
                    {{ item.count }}
                  </div>
                </div>
              </div>
              <div class="w-10 text-right font-medium text-ink-gray-5">{{ item.pct }}%</div>
            </div>
          </div>
        </div>

        <!-- Hit Rate by Category -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Hit Rate by Category') }}</div>
          <div class="space-y-3">
            <div v-for="cat in hitRateByCategory" :key="cat.name" class="text-xs">
              <div class="mb-1 flex justify-between">
                <span class="text-ink-gray-6">{{ __(cat.name) }}</span>
                <span class="font-medium" :class="cat.rate >= 70 ? 'text-green-600' : 'text-amber-600'">{{ cat.rate }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-surface-gray-2">
                <div class="h-2 rounded-full" :class="cat.color" :style="{ width: cat.rate + '%' }" />
              </div>
            </div>
          </div>
        </div>

        <!-- Decision Distribution -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Decision Distribution') }}</div>
          <div class="space-y-3">
            <div class="h-8 overflow-hidden rounded-lg">
              <div class="flex h-8">
                <div class="flex items-center justify-center bg-green-500 text-[10px] font-medium text-white" style="width: 62%">
                  62% {{ __('Approved') }}
                </div>
                <div class="flex items-center justify-center bg-amber-400 text-[10px] font-medium text-white" style="width: 24%">
                  24% {{ __('Manual') }}
                </div>
                <div class="flex items-center justify-center bg-red-500 text-[10px] font-medium text-white" style="width: 12%">
                  12% {{ __('Rejected') }}
                </div>
                <div class="flex items-center justify-center bg-ink-gray-3 text-[10px] font-medium text-white" style="width: 2%">
                </div>
              </div>
            </div>
            <div class="flex gap-4 text-xs text-ink-gray-5">
              <span class="flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-full bg-green-500"></span> {{ __('Approved') }} 62%</span>
              <span class="flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-full bg-amber-400"></span> {{ __('Manual Review') }} 24%</span>
              <span class="flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-full bg-red-500"></span> {{ __('Rejected') }} 12%</span>
              <span class="flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-full bg-ink-gray-3"></span> {{ __('Error') }} 2%</span>
            </div>
          </div>
        </div>

        <!-- Monthly Execution Trend -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Monthly Execution Trend') }}</div>
          <div class="flex items-end gap-2 h-32">
            <div v-for="bar in monthlyTrend" :key="bar.month" class="flex flex-1 flex-col items-center gap-1">
              <span class="text-[10px] text-ink-gray-5">{{ bar.count }}</span>
              <div class="w-full rounded-t bg-[#FF6600]" :style="{ height: (bar.count / maxMonthly * 100) + '%' }"></div>
              <span class="text-[10px] text-ink-gray-4">{{ bar.month }}</span>
            </div>
          </div>
        </div>

        <!-- Top Exception Rules -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Top Exception Rules') }}</div>
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b border-outline-gray-1 text-ink-gray-4">
                <th class="pb-2 text-left font-medium">{{ __('Rule Name') }}</th>
                <th class="pb-2 text-right font-medium">{{ __('Exception Count') }}</th>
                <th class="pb-2 text-right font-medium">{{ __('Rate') }}</th>
                <th class="pb-2 text-right font-medium">{{ __('Last Exception') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ex in topExceptions" :key="ex.name" class="border-b border-outline-gray-1 last:border-0">
                <td class="py-1.5 text-ink-gray-7">{{ ex.name }}</td>
                <td class="py-1.5 text-right font-semibold text-red-600">{{ ex.count }}</td>
                <td class="py-1.5 text-right text-ink-gray-5">{{ ex.rate }}%</td>
                <td class="py-1.5 text-right text-ink-gray-4">{{ ex.lastDate }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Category Performance -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Category Performance') }}</div>
          <div class="grid grid-cols-2 gap-3">
            <div v-for="cat in categoryPerformance" :key="cat.name" class="rounded-lg border border-outline-gray-1 p-3">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-ink-gray-8">{{ __(cat.name) }}</span>
                <span class="text-[10px]" :class="cat.trend === 'up' ? 'text-green-600' : 'text-red-500'">{{ cat.trend === 'up' ? '↑' : '↓' }}</span>
              </div>
              <div class="mt-2 grid grid-cols-3 gap-1 text-[10px]">
                <div>
                  <div class="text-ink-gray-4">{{ __('Rules') }}</div>
                  <div class="font-semibold text-ink-gray-7">{{ cat.rules }}</div>
                </div>
                <div>
                  <div class="text-ink-gray-4">{{ __('Avg Latency') }}</div>
                  <div class="font-semibold text-ink-gray-7">{{ cat.avgLatency }}ms</div>
                </div>
                <div>
                  <div class="text-ink-gray-4">{{ __('Hit Rate') }}</div>
                  <div class="font-semibold" :class="cat.hitRate >= 70 ? 'text-green-600' : 'text-amber-600'">{{ cat.hitRate }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── MODALS ── -->

  <!-- New Rule Modal -->
  <div v-if="showNewRuleModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-2xl rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Create New Rule') }}</div>
        <button class="text-ink-gray-4 hover:text-ink-gray-7" @click="showNewRuleModal = false">✕</button>
      </div>

      <!-- Step indicator -->
      <div class="mb-5 flex items-center gap-2">
        <div
          v-for="(step, idx) in ['Metadata', 'Conditions', 'Review']"
          :key="step"
          class="flex items-center gap-2"
        >
          <div
            class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold"
            :class="newRuleStep === idx + 1 ? 'bg-[#FF6600] text-white' : newRuleStep > idx + 1 ? 'bg-green-500 text-white' : 'bg-surface-gray-2 text-ink-gray-4'"
          >
            {{ idx + 1 }}
          </div>
          <span class="text-xs" :class="newRuleStep === idx + 1 ? 'font-semibold text-[#CC5200]' : 'text-ink-gray-4'">{{ __(step) }}</span>
          <div v-if="idx < 2" class="mx-1 h-px w-8 bg-outline-gray-2"></div>
        </div>
      </div>

      <!-- Step 1: Metadata -->
      <div v-if="newRuleStep === 1" class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Rule Name') }}</label>
          <input v-model="newRuleForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" :placeholder="__('Enter rule name')" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Category') }}</label>
            <select v-model="newRuleForm.category" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="c in categories" :key="c" :value="c">{{ __(c) }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Module') }}</label>
            <select v-model="newRuleForm.module" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="m in modules" :key="m" :value="m">{{ __(m) }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Description') }}</label>
          <textarea v-model="newRuleForm.description" rows="3" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" :placeholder="__('Describe what this rule does...')" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Priority') }}</label>
            <select v-model="newRuleForm.priority" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Tags') }}</label>
            <input v-model="newRuleForm.tags" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" :placeholder="__('comma-separated')" />
          </div>
        </div>
      </div>

      <!-- Step 2: Conditions -->
      <div v-if="newRuleStep === 2" class="space-y-3 text-sm">
        <div class="text-xs font-semibold text-ink-gray-6">{{ __('Define Conditions') }}</div>
        <div class="space-y-2">
          <div
            v-for="(cond, idx) in newRuleForm.conditions"
            :key="idx"
            class="flex items-center gap-2 rounded-lg bg-surface-gray-1 p-2"
          >
            <select v-model="cond.field" class="h-8 flex-1 rounded border border-outline-gray-2 px-2 text-xs">
              <option v-for="f in conditionFields" :key="f" :value="f">{{ f }}</option>
            </select>
            <select v-model="cond.operator" class="h-8 w-28 rounded border border-outline-gray-2 px-2 text-xs">
              <option v-for="op in operators" :key="op.value" :value="op.value">{{ op.label }}</option>
            </select>
            <input v-model="cond.value" class="h-8 w-28 rounded border border-outline-gray-2 px-2 text-xs" />
            <button class="text-ink-gray-3 hover:text-red-500" @click="newRuleForm.conditions.splice(idx, 1)">✕</button>
          </div>
        </div>
        <button class="text-xs text-[#FF6600] hover:underline" @click="newRuleForm.conditions.push({ field: 'credit_score', operator: '>=', value: '' })">
          + {{ __('Add Condition') }}
        </button>
      </div>

      <!-- Step 3: Review -->
      <div v-if="newRuleStep === 3" class="space-y-3 text-sm">
        <div class="rounded-lg bg-surface-gray-1 p-4">
          <div class="mb-2 text-xs font-semibold text-ink-gray-6">{{ __('Review Summary') }}</div>
          <div class="space-y-1 text-xs text-ink-gray-7">
            <div><span class="font-medium">{{ __('Name') }}:</span> {{ newRuleForm.name }}</div>
            <div><span class="font-medium">{{ __('Category') }}:</span> {{ newRuleForm.category }}</div>
            <div><span class="font-medium">{{ __('Module') }}:</span> {{ newRuleForm.module }}</div>
            <div><span class="font-medium">{{ __('Priority') }}:</span> {{ newRuleForm.priority }}</div>
            <div><span class="font-medium">{{ __('Conditions') }}:</span> {{ newRuleForm.conditions.length }} {{ __('conditions defined') }}</div>
            <div><span class="font-medium">{{ __('Description') }}:</span> {{ newRuleForm.description }}</div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showNewRuleModal = false" />
        <Button v-if="newRuleStep > 1" :label="__('Back')" variant="outline" @click="newRuleStep--" />
        <Button
          v-if="newRuleStep < 3"
          :label="__('Next')"
          variant="solid"
          @click="newRuleStep++"
        />
        <Button
          v-if="newRuleStep === 3"
          :label="__('Create Rule')"
          variant="solid"
          @click="createNewRule"
        />
      </div>
    </div>
  </div>

  <!-- Rule Approval Modal -->
  <div v-if="showApprovalModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-lg rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Rule Approval Request') }}</div>
        <button class="text-ink-gray-4 hover:text-ink-gray-7" @click="showApprovalModal = false">✕</button>
      </div>

      <div class="space-y-3 text-sm">
        <div class="rounded-lg bg-surface-gray-1 p-3">
          <div class="text-xs text-ink-gray-4">{{ __('Rule') }}</div>
          <div class="font-medium text-ink-gray-8">{{ builderForm.name }}</div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-lg bg-surface-gray-1 p-3">
            <div class="text-xs text-ink-gray-4">{{ __('Requester') }}</div>
            <div class="font-medium text-ink-gray-8">Budi Santoso</div>
          </div>
          <div class="rounded-lg bg-surface-gray-1 p-3">
            <div class="text-xs text-ink-gray-4">{{ __('Submitted') }}</div>
            <div class="font-medium text-ink-gray-8">{{ __('Today') }}</div>
          </div>
        </div>
        <div class="rounded-lg bg-surface-gray-1 p-3">
          <div class="mb-2 text-xs text-ink-gray-4">{{ __('Changes Summary') }}</div>
          <div class="text-xs text-ink-gray-6">{{ builderForm.conditions.length }} {{ __('conditions') }} · {{ builderForm.thenActions.length }} {{ __('actions') }}</div>
        </div>

        <!-- Approval Chain -->
        <div>
          <div class="mb-2 text-xs font-semibold text-ink-gray-6">{{ __('Approval Chain') }}</div>
          <div class="flex items-center gap-3">
            <div v-for="approver in approvalChain" :key="approver.name" class="flex items-center gap-1">
              <div class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold text-white" :class="approver.status === 'approved' ? 'bg-green-500' : approver.status === 'pending' ? 'bg-amber-400' : 'bg-surface-gray-3'">
                {{ approver.name.charAt(0) }}
              </div>
              <div>
                <div class="text-[10px] font-medium text-ink-gray-7">{{ approver.name }}</div>
                <div class="text-[10px]" :class="approver.status === 'approved' ? 'text-green-600' : 'text-amber-600'">{{ __(approver.status) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Comment') }}</label>
          <textarea v-model="approvalComment" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" :placeholder="__('Add remarks...')" />
        </div>
      </div>

      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Reject')" variant="subtle" theme="red" @click="handleApproval('rejected')" />
        <Button :label="__('Request Changes')" variant="outline" @click="handleApproval('changes')" />
        <Button :label="__('Approve')" variant="solid" @click="handleApproval('approved')" />
      </div>
    </div>
  </div>

  <!-- Version History Modal -->
  <div v-if="showVersionModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-lg rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Version History') }} — {{ versionRuleName }}</div>
        <button class="text-ink-gray-4 hover:text-ink-gray-7" @click="showVersionModal = false">✕</button>
      </div>
      <div class="max-h-80 space-y-3 overflow-y-auto">
        <div
          v-for="ver in versionHistory"
          :key="ver.version"
          class="flex items-start gap-3 rounded-lg border border-outline-gray-1 p-3"
        >
          <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#CCE5F5] text-xs font-bold text-[#004D73]">
            v{{ ver.version }}
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-xs font-medium text-ink-gray-8">{{ ver.changes }}</div>
            <div class="mt-0.5 text-[10px] text-ink-gray-4">{{ ver.date }} · {{ ver.author }}</div>
          </div>
          <Badge :label="__(ver.status)" variant="subtle" :theme="ver.status === 'Active' ? 'green' : 'gray'" />
          <Button label="Restore" variant="ghost" size="sm" @click="showToast(__('Version restored'))" />
        </div>
      </div>
    </div>
  </div>

  <!-- Clone Rule Modal -->
  <div v-if="showCloneModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Clone Rule') }}</div>
        <button class="text-ink-gray-4 hover:text-ink-gray-7" @click="showCloneModal = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('New Rule Name') }}</label>
          <input v-model="cloneForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Target Category') }}</label>
          <select v-model="cloneForm.category" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="c in categories" :key="c" :value="c">{{ __(c) }}</option>
          </select>
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showCloneModal = false" />
        <Button :label="__('Clone Rule')" variant="solid" @click="cloneRule" />
      </div>
    </div>
  </div>

  <!-- Log Detail Modal -->
  <div v-if="showLogDetailModal && selectedLog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-2xl rounded-[16px] bg-white p-6 shadow-xl max-h-[85vh] overflow-y-auto">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <div class="text-lg font-semibold text-ink-gray-9">{{ selectedLog.ruleName }}</div>
          <div class="text-xs text-ink-gray-4">{{ selectedLog.timestamp }} · {{ selectedLog.duration }}ms</div>
        </div>
        <button class="text-ink-gray-4 hover:text-ink-gray-7" @click="showLogDetailModal = false">✕</button>
      </div>
      <div class="space-y-3">
        <div>
          <div class="mb-1 text-xs font-semibold text-ink-gray-6">{{ __('Input JSON') }}</div>
          <pre class="max-h-40 overflow-auto rounded-lg bg-surface-gray-1 p-3 text-xs text-ink-gray-7">{{ selectedLog.inputJson }}</pre>
        </div>
        <div>
          <div class="mb-1 text-xs font-semibold text-ink-gray-6">{{ __('Output JSON') }}</div>
          <pre class="max-h-40 overflow-auto rounded-lg bg-surface-gray-1 p-3 text-xs text-ink-gray-7">{{ selectedLog.outputJson }}</pre>
        </div>
        <div>
          <div class="mb-1 text-xs font-semibold text-ink-gray-6">{{ __('Decision Path') }}</div>
          <div class="rounded-lg bg-[#E0F0FF] p-3 text-xs text-[#00334D]">
            {{ selectedLog.decisionPath }}
          </div>
        </div>
      </div>
      <div class="mt-4 flex justify-end">
        <Button :label="__('Close')" variant="subtle" @click="showLogDetailModal = false" />
      </div>
    </div>
  </div>

  <!-- Toast notification -->
  <div v-if="toastMessage" class="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-xl bg-green-600 px-5 py-3 text-sm font-medium text-white shadow-lg">
    <FeatherIcon name="check-circle" class="h-4 w-4" />
    {{ toastMessage }}
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Badge, Button, FeatherIcon, usePageMeta } from 'frappe-ui'
import { ref, computed, reactive } from 'vue'

usePageMeta(() => ({ title: __('Rules Engine') }))

// ─── State ───
const activeTab = ref('library')
const listSearch = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const filterModule = ref('')

// Builder
const showElse = ref(true)

// Trees
const treeView = ref('list')
const selectedTree = ref(null)

// Sandbox
const simulationRun = ref(false)
const simulationRunning = ref(false)

// Logs
const logsPeriod = ref('Today')
const logsRuleFilter = ref('')
const logsStatusFilter = ref('')
const logsSearch = ref('')
const showLogDetailModal = ref(false)
const selectedLog = ref(null)

// Modals
const showNewRuleModal = ref(false)
const showApprovalModal = ref(false)
const showVersionModal = ref(false)
const showCloneModal = ref(false)
const newRuleStep = ref(1)
const approvalComment = ref('')
const versionRuleName = ref('')
const toastMessage = ref('')

// ─── Constants ───
const categories = ['Credit Risk', 'Pricing', 'Eligibility', 'Routing', 'Rejection', 'Exception']
const statuses = ['Active', 'Draft', 'Pending Approval', 'Archived']
const modules = ['CRM', 'LOS', 'Collections']

const conditionFields = [
  'applicant_age', 'credit_score', 'monthly_income', 'loan_amount',
  'employment_type', 'collateral_type', 'dti_ratio', 'slik_score',
  'dpd', 'product_type', 'region', 'existing_customer'
]

const operators = [
  { value: '==', label: 'equals' },
  { value: '!=', label: 'not equals' },
  { value: '>', label: 'greater than' },
  { value: '<', label: 'less than' },
  { value: '>=', label: 'greater than or equal' },
  { value: '<=', label: 'less than or equal' },
  { value: 'contains', label: 'contains' },
  { value: 'in', label: 'in' },
  { value: 'not_in', label: 'not in' },
  { value: 'is_set', label: 'is set' },
  { value: 'is_not_set', label: 'is not set' },
  { value: 'between', label: 'between' },
]

const actionTypes = [
  'Set Field', 'Send Notification', 'Route To', 'Assign To',
  'Auto Approve', 'Auto Reject', 'Score Adjustment', 'Add Tag',
  'Update Status', 'Trigger Workflow'
]

// ─── Page Tabs ───
const pageTabs = computed(() => [
  { key: 'library', label: 'Rule Library', badge: rules.value.length },
  { key: 'builder', label: 'Visual Builder' },
  { key: 'trees', label: 'Decision Trees' },
  { key: 'sandbox', label: 'Sandbox' },
  { key: 'logs', label: 'Execution Logs' },
  { key: 'analytics', label: 'Analytics' },
])

// ─── Demo Data: Rules ───
const rules = ref([
  {
    id: 1, name: 'SME Credit Eligibility — Basic', category: 'Eligibility', module: 'LOS',
    status: 'Active', version: 'v3.2', lastModified: '2026-05-22', hitRate: 89,
    description: 'Basic eligibility check for SME credit applications',
    priority: 1,
    conditions: [
      { field: 'applicant_age', operator: '>=', value: '21' },
      { field: 'credit_score', operator: '>=', value: '650' },
      { field: 'monthly_income', operator: '>=', value: '15000000' },
    ],
    thenActions: [{ type: 'Auto Approve', params: 'standard' }],
    elseActions: [{ type: 'Route To', params: 'manual_review' }],
  },
  {
    id: 2, name: 'KMK Interest Rate Pricing', category: 'Pricing', module: 'LOS',
    status: 'Active', version: 'v2.1', lastModified: '2026-05-20', hitRate: 76,
    description: 'Dynamic interest rate calculation for KMK products',
    priority: 2,
    conditions: [{ field: 'product_type', operator: '==', value: 'KMK' }],
    thenActions: [{ type: 'Set Field', params: 'interest_rate = 11.5' }],
    elseActions: [],
  },
  {
    id: 3, name: 'Auto-Reject: AML/PEP Screening', category: 'Rejection', module: 'CRM',
    status: 'Active', version: 'v1.5', lastModified: '2026-05-18', hitRate: 12,
    description: 'Automatic rejection for AML/PEP flagged applicants',
    priority: 1,
    conditions: [{ field: 'slik_score', operator: '<', value: '200' }],
    thenActions: [{ type: 'Auto Reject', params: 'aml_flag' }],
    elseActions: [],
  },
  {
    id: 4, name: 'RM Assignment by Region', category: 'Routing', module: 'CRM',
    status: 'Active', version: 'v4.0', lastModified: '2026-05-21', hitRate: 94,
    description: 'Route leads to RM based on geographic region',
    priority: 3,
    conditions: [{ field: 'region', operator: 'is_set', value: '' }],
    thenActions: [{ type: 'Assign To', params: 'regional_rm' }],
    elseActions: [{ type: 'Route To', params: 'default_pool' }],
  },
  {
    id: 5, name: 'Large Exposure Committee Routing', category: 'Routing', module: 'LOS',
    status: 'Active', version: 'v2.3', lastModified: '2026-05-19', hitRate: 34,
    description: 'Route large loans to committee for review',
    priority: 2,
    conditions: [{ field: 'loan_amount', operator: '>', value: '50000000000' }],
    thenActions: [{ type: 'Route To', params: 'credit_committee' }],
    elseActions: [],
  },
  {
    id: 6, name: 'KPR Eligibility — Employee', category: 'Eligibility', module: 'LOS',
    status: 'Active', version: 'v1.8', lastModified: '2026-05-17', hitRate: 82,
    description: 'KPR eligibility for salaried employees',
    priority: 2,
    conditions: [
      { field: 'employment_type', operator: '==', value: 'Employed' },
      { field: 'monthly_income', operator: '>=', value: '10000000' },
    ],
    thenActions: [{ type: 'Auto Approve', params: 'kpr_employee' }],
    elseActions: [{ type: 'Route To', params: 'manual_review' }],
  },
  {
    id: 7, name: 'Collection Escalation Trigger', category: 'Exception', module: 'Collections',
    status: 'Active', version: 'v2.0', lastModified: '2026-05-16', hitRate: 45,
    description: 'Trigger escalation for overdue accounts',
    priority: 1,
    conditions: [{ field: 'dpd', operator: '>=', value: '90' }],
    thenActions: [{ type: 'Trigger Workflow', params: 'escalation_flow' }],
    elseActions: [],
  },
  {
    id: 8, name: 'Covenant Breach Auto-Alert', category: 'Exception', module: 'LOS',
    status: 'Active', version: 'v1.2', lastModified: '2026-05-15', hitRate: 18,
    description: 'Notify risk team on covenant breach detection',
    priority: 1,
    conditions: [{ field: 'dti_ratio', operator: '>', value: '0.6' }],
    thenActions: [{ type: 'Send Notification', params: 'risk_team' }],
    elseActions: [],
  },
  {
    id: 9, name: 'SLIK Score Risk Grading', category: 'Credit Risk', module: 'LOS',
    status: 'Active', version: 'v3.0', lastModified: '2026-05-23', hitRate: 91,
    description: 'Risk grading based on SLIK credit bureau score',
    priority: 1,
    conditions: [{ field: 'slik_score', operator: '>=', value: '500' }],
    thenActions: [{ type: 'Set Field', params: 'risk_grade = Low' }],
    elseActions: [{ type: 'Set Field', params: 'risk_grade = High' }],
  },
  {
    id: 10, name: 'Personal Loan Quick Approval', category: 'Eligibility', module: 'LOS',
    status: 'Pending Approval', version: 'v1.0', lastModified: '2026-05-24', hitRate: null,
    description: 'Fast-track approval for personal loan existing customers',
    priority: 3,
    conditions: [
      { field: 'existing_customer', operator: '==', value: 'true' },
      { field: 'credit_score', operator: '>=', value: '750' },
    ],
    thenActions: [{ type: 'Auto Approve', params: 'quick_pl' }],
    elseActions: [],
  },
  {
    id: 11, name: 'NPL Early Warning Detection', category: 'Credit Risk', module: 'Collections',
    status: 'Active', version: 'v2.5', lastModified: '2026-05-14', hitRate: 67,
    description: 'Detect early warning signals for potential NPL',
    priority: 1,
    conditions: [{ field: 'dpd', operator: '>=', value: '30' }],
    thenActions: [{ type: 'Send Notification', params: 'early_warning_team' }],
    elseActions: [],
  },
  {
    id: 12, name: 'Dynamic Pricing — Collateral Adj', category: 'Pricing', module: 'LOS',
    status: 'Draft', version: 'v0.3', lastModified: '2026-05-23', hitRate: null,
    description: 'Interest rate adjustment based on collateral coverage ratio',
    priority: 4,
    conditions: [{ field: 'collateral_type', operator: '!=', value: 'None' }],
    thenActions: [{ type: 'Score Adjustment', params: '-0.5%' }],
    elseActions: [],
  },
  {
    id: 13, name: 'Branch Routing — Jakarta', category: 'Routing', module: 'CRM',
    status: 'Active', version: 'v1.1', lastModified: '2026-05-13', hitRate: 88,
    description: 'Route Jakarta-area leads to Jakarta branch team',
    priority: 5,
    conditions: [{ field: 'region', operator: '==', value: 'Jakarta' }],
    thenActions: [{ type: 'Route To', params: 'jakarta_branch' }],
    elseActions: [],
  },
  {
    id: 14, name: 'Restructuring Eligibility Check', category: 'Eligibility', module: 'Collections',
    status: 'Active', version: 'v1.4', lastModified: '2026-05-12', hitRate: 55,
    description: 'Check eligibility for loan restructuring program',
    priority: 2,
    conditions: [
      { field: 'dpd', operator: '>=', value: '60' },
      { field: 'existing_customer', operator: '==', value: 'true' },
    ],
    thenActions: [{ type: 'Update Status', params: 'restructure_eligible' }],
    elseActions: [],
  },
  {
    id: 15, name: 'Auto-Reject: Minimum Age', category: 'Rejection', module: 'LOS',
    status: 'Archived', version: 'v1.0', lastModified: '2026-03-10', hitRate: 8,
    description: 'Reject applicants below minimum age requirement',
    priority: 1,
    conditions: [{ field: 'applicant_age', operator: '<', value: '21' }],
    thenActions: [{ type: 'Auto Reject', params: 'underage' }],
    elseActions: [],
  },
])

// ─── Builder Form ───
const builderForm = reactive({
  name: 'SME Credit Eligibility — Basic',
  category: 'Eligibility',
  description: 'Basic eligibility screening for SME credit applications based on age, credit score, income, and loan amount thresholds.',
  priority: 1,
  module: 'LOS',
  effectiveFrom: '2026-01-01',
  effectiveTo: '2026-12-31',
  conditionLogic: 'AND',
  conditions: [
    { field: 'applicant_age', operator: '>=', value: '21' },
    { field: 'credit_score', operator: '>=', value: '650' },
    { field: 'monthly_income', operator: '>=', value: '15000000' },
    { field: 'loan_amount', operator: '<=', value: '500000000' },
  ],
  thenActions: [
    { type: 'Auto Approve', params: 'standard' },
    { type: 'Set Field', params: 'interest_rate = 12.5' },
    { type: 'Add Tag', params: 'eligible-sme' },
  ],
  elseActions: [
    { type: 'Route To', params: 'manual_review' },
    { type: 'Send Notification', params: 'Risk Team' },
  ],
})

// ─── New Rule Form ───
const newRuleForm = reactive({
  name: '',
  category: 'Eligibility',
  module: 'LOS',
  description: '',
  priority: 5,
  tags: '',
  conditions: [
    { field: 'credit_score', operator: '>=', value: '' },
  ],
})

// ─── Clone Form ───
const cloneForm = reactive({
  name: '',
  category: 'Eligibility',
})

// ─── Sandbox Form ───
const sandboxForm = reactive({
  testAll: true,
  selectedRules: [],
  applicantName: 'PT Maju Bersama',
  applicantAge: 35,
  creditScore: 720,
  slikScore: 650,
  monthlyIncome: '75,000,000',
  employmentType: 'Business Owner',
  existingCustomer: true,
  productType: 'KMK',
  loanAmount: '2,500,000,000',
  tenor: 60,
  collateralType: 'Property',
  collateralValue: '3,500,000,000',
})

// ─── Decision Trees ───
const decisionTrees = ref([
  { id: 1, name: 'Credit Eligibility Assessment', type: 'Eligibility', nodes: 12, depth: 5, status: 'Active', lastModified: '2026-05-22' },
  { id: 2, name: 'Loan Pricing Engine', type: 'Pricing', nodes: 8, depth: 4, status: 'Active', lastModified: '2026-05-20' },
  { id: 3, name: 'Auto-Rejection Screening', type: 'Rejection', nodes: 6, depth: 3, status: 'Active', lastModified: '2026-05-18' },
  { id: 4, name: 'RM Assignment Router', type: 'Routing', nodes: 10, depth: 4, status: 'Draft', lastModified: '2026-05-21' },
  { id: 5, name: 'Collection Escalation Path', type: 'Exception', nodes: 7, depth: 3, status: 'Pending Approval', lastModified: '2026-05-19' },
])

// ─── Simulation Result ───
const simResult = reactive({
  decision: 'APPROVED',
  confidence: 87,
  timeline: [
    { rule: 'Auto-Reject: Minimum Age', duration: 2, result: 'pass' },
    { rule: 'Auto-Reject: AML/PEP Screening', duration: 5, result: 'pass' },
    { rule: 'SLIK Score Risk Grading', duration: 3, result: 'pass' },
    { rule: 'SME Credit Eligibility — Basic', duration: 8, result: 'pass' },
    { rule: 'KMK Interest Rate Pricing', duration: 4, result: 'pass' },
    { rule: 'Large Exposure Committee Routing', duration: 2, result: 'skip' },
    { rule: 'RM Assignment by Region', duration: 3, result: 'pass' },
    { rule: 'Collection Escalation Trigger', duration: 1, result: 'skip' },
  ],
  outputVars: [
    { name: 'risk_grade', value: 'Low', setBy: 'SLIK Score Risk Grading' },
    { name: 'interest_rate', value: '12.5%', setBy: 'KMK Interest Rate Pricing' },
    { name: 'eligible', value: 'true', setBy: 'SME Credit Eligibility — Basic' },
    { name: 'assigned_rm', value: 'Jakarta Branch', setBy: 'RM Assignment by Region' },
  ],
  warnings: [
    'Loan amount is close to threshold (Rp 2.5B vs Rp 500M limit for auto-approval)',
    'Collateral coverage ratio below 150% recommended minimum',
  ],
  summary: { total: 8, passed: 6, failed: 0, skipped: 2, totalTime: 28 },
})

// ─── Approval Chain ───
const approvalChain = [
  { name: 'Budi Santoso', status: 'approved' },
  { name: 'Dewi Lestari', status: 'pending' },
  { name: 'Agus Prasetyo', status: 'waiting' },
]

// ─── Version History ───
const versionHistory = [
  { version: '3.2', date: '2026-05-22', author: 'Budi Santoso', changes: 'Updated income threshold from Rp 12M to Rp 15M', status: 'Active' },
  { version: '3.1', date: '2026-05-10', author: 'Dewi Lestari', changes: 'Added SLIK score condition', status: 'Archived' },
  { version: '3.0', date: '2026-04-15', author: 'Budi Santoso', changes: 'Major refactor: split into AND/OR groups', status: 'Archived' },
  { version: '2.5', date: '2026-03-20', author: 'Agus Prasetyo', changes: 'Added collateral check', status: 'Archived' },
  { version: '2.0', date: '2026-02-01', author: 'Budi Santoso', changes: 'Initial release for production', status: 'Archived' },
]

// ─── Execution Logs ───
const executionLogs = ref([
  { id: 1, timestamp: '2026-05-24 20:45:12', ruleName: 'SME Credit Eligibility — Basic', trigger: 'API', inputSummary: 'PT Maju Bersama, KMK Rp 2.5B, Score 720', decision: 'Approved', duration: 8, status: 'Passed', inputJson: '{\n  "applicant": "PT Maju Bersama",\n  "credit_score": 720,\n  "monthly_income": 75000000,\n  "loan_amount": 2500000000\n}', outputJson: '{\n  "decision": "approved",\n  "interest_rate": 12.5,\n  "risk_grade": "low"\n}', decisionPath: 'age_check → slik_check → income_check → amount_check → APPROVE' },
  { id: 2, timestamp: '2026-05-24 20:42:08', ruleName: 'SLIK Score Risk Grading', trigger: 'Workflow', inputSummary: 'CV Berkah Jaya, SLIK 480', decision: 'Rejected', duration: 3, status: 'Passed', inputJson: '{\n  "applicant": "CV Berkah Jaya",\n  "slik_score": 480\n}', outputJson: '{\n  "risk_grade": "high",\n  "decision": "manual_review"\n}', decisionPath: 'slik_score < 500 → HIGH_RISK → MANUAL_REVIEW' },
  { id: 3, timestamp: '2026-05-24 20:38:55', ruleName: 'KMK Interest Rate Pricing', trigger: 'API', inputSummary: 'PT Sentosa Makmur, KMK Rp 5B', decision: 'Approved', duration: 5, status: 'Passed', inputJson: '{\n  "product_type": "KMK",\n  "loan_amount": 5000000000,\n  "collateral_type": "Property"\n}', outputJson: '{\n  "interest_rate": 10.75,\n  "pricing_tier": "premium"\n}', decisionPath: 'product_KMK → collateral_check → premium_tier → RATE_10.75' },
  { id: 4, timestamp: '2026-05-24 20:35:21', ruleName: 'Auto-Reject: AML/PEP Screening', trigger: 'API', inputSummary: 'PT Abadi Nusantara, SLIK 180', decision: 'Rejected', duration: 2, status: 'Passed', inputJson: '{\n  "applicant": "PT Abadi Nusantara",\n  "slik_score": 180\n}', outputJson: '{\n  "decision": "rejected",\n  "reason": "aml_flag"\n}', decisionPath: 'slik_score < 200 → AML_FLAG → REJECT' },
  { id: 5, timestamp: '2026-05-24 20:31:45', ruleName: 'RM Assignment by Region', trigger: 'Workflow', inputSummary: 'PT Indo Pratama, Region: Surabaya', decision: 'Approved', duration: 3, status: 'Passed', inputJson: '{\n  "applicant": "PT Indo Pratama",\n  "region": "Surabaya"\n}', outputJson: '{\n  "assigned_rm": "Surabaya Branch",\n  "rm_name": "Andi Wijaya"\n}', decisionPath: 'region_set → surabaya → ASSIGN_RM' },
  { id: 6, timestamp: '2026-05-24 20:28:33', ruleName: 'Large Exposure Committee Routing', trigger: 'API', inputSummary: 'PT Mega Corp, KI Rp 75B', decision: 'Manual Review', duration: 4, status: 'Passed', inputJson: '{\n  "applicant": "PT Mega Corp",\n  "loan_amount": 75000000000\n}', outputJson: '{\n  "route_to": "credit_committee",\n  "committee_level": "CC-3"\n}', decisionPath: 'amount > 50B → ROUTE_TO_COMMITTEE → CC3' },
  { id: 7, timestamp: '2026-05-24 20:25:10', ruleName: 'KPR Eligibility — Employee', trigger: 'API', inputSummary: 'Andi Susanto, KPR Rp 800M, Employed', decision: 'Approved', duration: 6, status: 'Passed', inputJson: '{\n  "applicant": "Andi Susanto",\n  "employment_type": "Employed",\n  "monthly_income": 25000000\n}', outputJson: '{\n  "decision": "approved",\n  "product": "KPR"\n}', decisionPath: 'employed → income_check → APPROVE' },
  { id: 8, timestamp: '2026-05-24 20:22:44', ruleName: 'Collection Escalation Trigger', trigger: 'Scheduler', inputSummary: 'PT Sumber Jaya, DPD 95', decision: 'Manual Review', duration: 2, status: 'Passed', inputJson: '{\n  "applicant": "PT Sumber Jaya",\n  "dpd": 95\n}', outputJson: '{\n  "escalation_triggered": true,\n  "workflow": "escalation_flow"\n}', decisionPath: 'dpd >= 90 → TRIGGER_ESCALATION' },
  { id: 9, timestamp: '2026-05-24 20:18:30', ruleName: 'NPL Early Warning Detection', trigger: 'Scheduler', inputSummary: 'CV Harapan, DPD 35', decision: 'Manual Review', duration: 3, status: 'Passed', inputJson: '{\n  "applicant": "CV Harapan",\n  "dpd": 35\n}', outputJson: '{\n  "warning_sent": true,\n  "team": "early_warning"\n}', decisionPath: 'dpd >= 30 → EARLY_WARNING → NOTIFY' },
  { id: 10, timestamp: '2026-05-24 20:15:18', ruleName: 'Branch Routing — Jakarta', trigger: 'API', inputSummary: 'PT Mulia Sejahtera, Jakarta', decision: 'Approved', duration: 2, status: 'Passed', inputJson: '{\n  "applicant": "PT Mulia Sejahtera",\n  "region": "Jakarta"\n}', outputJson: '{\n  "route_to": "jakarta_branch"\n}', decisionPath: 'region == Jakarta → ROUTE_JAKARTA' },
  { id: 11, timestamp: '2026-05-24 20:12:05', ruleName: 'SME Credit Eligibility — Basic', trigger: 'API', inputSummary: 'CV Selaras, Score 580, Income Rp 8M', decision: 'Rejected', duration: 7, status: 'Failed', inputJson: '{\n  "applicant": "CV Selaras",\n  "credit_score": 580,\n  "monthly_income": 8000000\n}', outputJson: '{\n  "decision": "manual_review",\n  "reason": "low_score_and_income"\n}', decisionPath: 'credit_score < 650 → FAIL → MANUAL_REVIEW' },
  { id: 12, timestamp: '2026-05-24 20:08:50', ruleName: 'Covenant Breach Auto-Alert', trigger: 'Scheduler', inputSummary: 'PT Buana Raya, DTI 0.72', decision: 'Manual Review', duration: 4, status: 'Passed', inputJson: '{\n  "applicant": "PT Buana Raya",\n  "dti_ratio": 0.72\n}', outputJson: '{\n  "alert_sent": true,\n  "team": "risk_team"\n}', decisionPath: 'dti > 0.6 → COVENANT_BREACH → ALERT' },
  { id: 13, timestamp: '2026-05-24 20:05:33', ruleName: 'Restructuring Eligibility Check', trigger: 'API', inputSummary: 'PT Andalas Group, DPD 75', decision: 'Approved', duration: 5, status: 'Passed', inputJson: '{\n  "applicant": "PT Andalas Group",\n  "dpd": 75,\n  "existing_customer": true\n}', outputJson: '{\n  "restructure_eligible": true\n}', decisionPath: 'dpd >= 60 AND existing_customer → ELIGIBLE' },
  { id: 14, timestamp: '2026-05-24 20:02:15', ruleName: 'SLIK Score Risk Grading', trigger: 'API', inputSummary: 'PT Nuansa, SLIK 720', decision: 'Approved', duration: 2, status: 'Passed', inputJson: '{\n  "applicant": "PT Nuansa",\n  "slik_score": 720\n}', outputJson: '{\n  "risk_grade": "low"\n}', decisionPath: 'slik >= 500 → LOW_RISK' },
  { id: 15, timestamp: '2026-05-24 19:58:42', ruleName: 'RM Assignment by Region', trigger: 'Workflow', inputSummary: 'PT Global Mandiri, Region: Bandung', decision: 'Approved', duration: 3, status: 'Error', inputJson: '{\n  "applicant": "PT Global Mandiri",\n  "region": "Bandung"\n}', outputJson: '{\n  "error": "Region mapping not found for Bandung"\n}', decisionPath: 'region_set → bandung → ERROR: no mapping' },
])

// ─── KPI Data ───
const libraryKpis = [
  { label: 'Total Rules', value: '47', icon: 'layers', iconColor: 'text-[#FF6600]', delta: '+3 this month', deltaColor: 'text-green-500' },
  { label: 'Active', value: '38', icon: 'check-circle', iconColor: 'text-green-500', valueColor: 'text-green-600', delta: '80.9% of total' },
  { label: 'Pending Approval', value: '4', icon: 'clock', iconColor: 'text-amber-500', valueColor: 'text-amber-600', delta: 'Awaiting review' },
  { label: 'Failed (7d)', value: '2', icon: 'alert-triangle', iconColor: 'text-red-500', valueColor: 'text-red-600', delta: '-1 vs last week', deltaColor: 'text-green-500' },
  { label: 'Avg Exec Time', value: '12ms', icon: 'zap', iconColor: 'text-[#FF6600]', delta: '-3ms vs last month', deltaColor: 'text-green-500' },
]

const logsKpis = [
  { label: 'Executions (24h)', value: '1,247', color: 'text-[#FF6600]', sub: '+8.3% vs yesterday' },
  { label: 'Avg Latency', value: '8ms', color: 'text-green-600', sub: 'Within SLA' },
  { label: 'Error Rate', value: '0.3%', color: 'text-green-600', sub: 'Below threshold' },
  { label: 'Top Rule', value: 'Credit Eligibility Basic', color: 'text-ink-gray-9', sub: '312 executions' },
]

const analyticsKpis = [
  { label: 'Active Rules', value: '38', color: 'text-[#FF6600]', sub: '+3 this month' },
  { label: 'Avg Hit Rate', value: '73.2%', color: 'text-green-600', sub: '+2.1% vs last month' },
  { label: 'Avg Latency', value: '8ms', color: 'text-[#FF6600]', sub: '-2ms improved' },
  { label: 'Exception Rate', value: '2.4%', color: 'text-amber-600', sub: 'Within tolerance' },
]

// ─── Analytics Data ───
const executionVolume = [
  { name: 'SME Credit Eligibility', count: 450, pct: 100 },
  { name: 'SLIK Score Risk Grading', count: 380, pct: 84 },
  { name: 'RM Assignment by Region', count: 340, pct: 76 },
  { name: 'KMK Interest Rate Pricing', count: 290, pct: 64 },
  { name: 'Branch Routing — Jakarta', count: 245, pct: 54 },
  { name: 'KPR Eligibility — Employee', count: 210, pct: 47 },
  { name: 'NPL Early Warning', count: 165, pct: 37 },
  { name: 'Auto-Reject: AML/PEP', count: 120, pct: 27 },
  { name: 'Large Exposure Routing', count: 85, pct: 19 },
  { name: 'Collection Escalation', count: 45, pct: 10 },
]

const hitRateByCategory = [
  { name: 'Routing', rate: 89, color: 'bg-purple-500' },
  { name: 'Credit Risk', rate: 79, color: 'bg-red-500' },
  { name: 'Eligibility', rate: 75, color: 'bg-green-500' },
  { name: 'Pricing', rate: 72, color: 'bg-blue-500' },
  { name: 'Exception', rate: 42, color: 'bg-amber-500' },
  { name: 'Rejection', rate: 10, color: 'bg-red-400' },
]

const monthlyTrend = [
  { month: 'Dec', count: 890 },
  { month: 'Jan', count: 1050 },
  { month: 'Feb', count: 980 },
  { month: 'Mar', count: 1200 },
  { month: 'Apr', count: 1150 },
  { month: 'May', count: 1340 },
]

const maxMonthly = computed(() => Math.max(...monthlyTrend.map(b => b.count)))

const topExceptions = [
  { name: 'Covenant Breach Auto-Alert', count: 23, rate: 4.2, lastDate: '2026-05-24' },
  { name: 'Collection Escalation Trigger', count: 18, rate: 3.8, lastDate: '2026-05-23' },
  { name: 'NPL Early Warning Detection', count: 12, rate: 2.1, lastDate: '2026-05-22' },
  { name: 'Large Exposure Committee Routing', count: 8, rate: 1.5, lastDate: '2026-05-21' },
  { name: 'Auto-Reject: AML/PEP Screening', count: 5, rate: 0.9, lastDate: '2026-05-20' },
]

const categoryPerformance = [
  { name: 'Credit Risk', rules: 4, avgLatency: 6, hitRate: 79, trend: 'up' },
  { name: 'Pricing', rules: 3, avgLatency: 7, hitRate: 72, trend: 'up' },
  { name: 'Eligibility', rules: 8, avgLatency: 9, hitRate: 75, trend: 'up' },
  { name: 'Routing', rules: 6, avgLatency: 4, hitRate: 89, trend: 'up' },
  { name: 'Rejection', rules: 3, avgLatency: 3, hitRate: 10, trend: 'down' },
  { name: 'Exception', rules: 4, avgLatency: 5, hitRate: 42, trend: 'down' },
]

// ─── Computed ───
const filteredRules = computed(() => {
  let result = rules.value
  if (listSearch.value) {
    const q = listSearch.value.toLowerCase()
    result = result.filter(r =>
      r.name.toLowerCase().includes(q) || r.description.toLowerCase().includes(q)
    )
  }
  if (filterCategory.value) {
    result = result.filter(r => r.category === filterCategory.value)
  }
  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value)
  }
  if (filterModule.value) {
    result = result.filter(r => r.module === filterModule.value)
  }
  return result
})

const filteredLogs = computed(() => {
  let result = executionLogs.value
  if (logsRuleFilter.value) {
    result = result.filter(l => l.ruleName === logsRuleFilter.value)
  }
  if (logsStatusFilter.value) {
    result = result.filter(l => l.status === logsStatusFilter.value)
  }
  if (logsSearch.value) {
    const q = logsSearch.value.toLowerCase()
    result = result.filter(l =>
      l.ruleName.toLowerCase().includes(q) || l.inputSummary.toLowerCase().includes(q)
    )
  }
  return result
})

// ─── Helper Functions ───
function formatIDR(num) {
  if (num >= 1000000000) {
    return 'Rp ' + (num / 1000000000).toFixed(1) + 'B'
  }
  if (num >= 1000000) {
    return 'Rp ' + (num / 1000000).toFixed(0) + 'M'
  }
  return 'Rp ' + num.toLocaleString('id-ID')
}

function categoryTheme(category) {
  const themes = {
    'Credit Risk': 'red',
    'Pricing': 'blue',
    'Eligibility': 'green',
    'Routing': 'violet',
    'Rejection': 'red',
    'Exception': 'orange',
  }
  return themes[category] || 'gray'
}

function statusTheme(status) {
  const themes = {
    'Active': 'green',
    'Draft': 'gray',
    'Pending Approval': 'orange',
    'Archived': 'gray',
  }
  return themes[status] || 'gray'
}

function showToast(message) {
  toastMessage.value = message
  setTimeout(() => { toastMessage.value = '' }, 3000)
}

// ─── Actions ───
function openNewRuleModal() {
  newRuleStep.value = 1
  newRuleForm.name = ''
  newRuleForm.description = ''
  newRuleForm.category = 'Eligibility'
  newRuleForm.module = 'LOS'
  newRuleForm.priority = 5
  newRuleForm.tags = ''
  newRuleForm.conditions = [{ field: 'credit_score', operator: '>=', value: '' }]
  showNewRuleModal.value = true
}

function createNewRule() {
  const newId = Math.max(...rules.value.map(r => r.id)) + 1
  rules.value.unshift({
    id: newId,
    name: newRuleForm.name || 'Untitled Rule',
    category: newRuleForm.category,
    module: newRuleForm.module,
    description: newRuleForm.description,
    priority: newRuleForm.priority,
    status: 'Draft',
    version: 'v1.0',
    lastModified: new Date().toISOString().slice(0, 10),
    hitRate: null,
    conditions: newRuleForm.conditions.map(c => ({ ...c })),
    thenActions: [],
    elseActions: [],
  })
  showNewRuleModal.value = false
  showToast(__('Rule created successfully'))
}

function editRule(rule) {
  builderForm.name = rule.name
  builderForm.category = rule.category
  builderForm.description = rule.description
  builderForm.priority = rule.priority
  builderForm.module = rule.module
  builderForm.conditions = [...rule.conditions.map(c => ({ ...c }))]
  builderForm.thenActions = [...rule.thenActions.map(a => ({ ...a }))]
  builderForm.elseActions = [...rule.elseActions.map(a => ({ ...a }))]
  activeTab.value = 'builder'
}

function openCloneModal(rule) {
  cloneForm.name = 'Copy of ' + rule.name
  cloneForm.category = rule.category
  showCloneModal.value = true
}

function cloneRule() {
  showCloneModal.value = false
  showToast(__('Rule cloned successfully'))
}

function testRule(rule) {
  sandboxForm.applicantName = 'Test — ' + rule.name
  activeTab.value = 'sandbox'
}

function archiveRule(rule) {
  rule.status = 'Archived'
  showToast(__('Rule archived'))
}

function addCondition() {
  builderForm.conditions.push({ field: 'credit_score', operator: '>=', value: '' })
}

function addConditionGroup() {
  builderForm.conditions.push({ field: 'loan_amount', operator: '<=', value: '' })
}

function addThenAction() {
  builderForm.thenActions.push({ type: 'Set Field', params: '' })
}

function addElseAction() {
  builderForm.elseActions.push({ type: 'Send Notification', params: '' })
}

function handleApproval(action) {
  showApprovalModal.value = false
  if (action === 'approved') {
    showToast(__('Rule approved'))
  } else if (action === 'rejected') {
    showToast(__('Rule rejected'))
  } else {
    showToast(__('Changes requested'))
  }
}

function setPreset(type) {
  if (type === 'good') {
    sandboxForm.applicantName = 'PT Maju Bersama'
    sandboxForm.applicantAge = 42
    sandboxForm.creditScore = 780
    sandboxForm.slikScore = 720
    sandboxForm.monthlyIncome = '150,000,000'
    sandboxForm.employmentType = 'Business Owner'
    sandboxForm.existingCustomer = true
    sandboxForm.productType = 'KMK'
    sandboxForm.loanAmount = '1,000,000,000'
    sandboxForm.tenor = 36
    sandboxForm.collateralType = 'Property'
    sandboxForm.collateralValue = '2,000,000,000'
  } else if (type === 'risky') {
    sandboxForm.applicantName = 'CV Harapan Baru'
    sandboxForm.applicantAge = 23
    sandboxForm.creditScore = 620
    sandboxForm.slikScore = 450
    sandboxForm.monthlyIncome = '12,000,000'
    sandboxForm.employmentType = 'Self-Employed'
    sandboxForm.existingCustomer = false
    sandboxForm.productType = 'Personal Loan'
    sandboxForm.loanAmount = '500,000,000'
    sandboxForm.tenor = 60
    sandboxForm.collateralType = 'None'
    sandboxForm.collateralValue = '0'
  } else {
    sandboxForm.applicantName = 'PT Edge Case Corp'
    sandboxForm.applicantAge = 21
    sandboxForm.creditScore = 650
    sandboxForm.slikScore = 500
    sandboxForm.monthlyIncome = '15,000,000'
    sandboxForm.employmentType = 'Employed'
    sandboxForm.existingCustomer = true
    sandboxForm.productType = 'KI'
    sandboxForm.loanAmount = '500,000,000'
    sandboxForm.tenor = 120
    sandboxForm.collateralType = 'Vehicle'
    sandboxForm.collateralValue = '500,000,000'
  }
}

function runSimulation() {
  simulationRunning.value = true
  simulationRun.value = false
  setTimeout(() => {
    // Determine result based on credit score
    const score = sandboxForm.creditScore
    if (score >= 700) {
      simResult.decision = 'APPROVED'
      simResult.confidence = 87
    } else if (score >= 600) {
      simResult.decision = 'MANUAL REVIEW'
      simResult.confidence = 62
    } else {
      simResult.decision = 'REJECTED'
      simResult.confidence = 91
    }
    simResult.timeline[0].result = sandboxForm.applicantAge >= 21 ? 'pass' : 'fail'
    simResult.timeline[1].result = sandboxForm.slikScore >= 200 ? 'pass' : 'fail'
    simResult.timeline[2].result = sandboxForm.slikScore >= 500 ? 'pass' : 'fail'
    simResult.timeline[3].result = score >= 650 ? 'pass' : 'fail'
    simulationRunning.value = false
    simulationRun.value = true
  }, 800)
}

function openLogDetail(log) {
  selectedLog.value = log
  showLogDetailModal.value = true
}
</script>

<style scoped>
/* CSS Tree Layout */
.tree-container {
  --tree-indent: 32px;
  --tree-line-color: #d1d5db;
}

.tree-node {
  position: relative;
  padding-left: var(--tree-indent);
  margin-top: 8px;
}

.tree-node::before {
  content: '';
  position: absolute;
  left: 12px;
  top: 0;
  width: 20px;
  height: 16px;
  border-left: 2px solid var(--tree-line-color);
  border-bottom: 2px solid var(--tree-line-color);
  border-bottom-left-radius: 8px;
}

.tree-container > .tree-node::before {
  display: none;
}

.tree-container > .tree-node {
  padding-left: 0;
}

.tree-children {
  position: relative;
}

.tree-children::before {
  content: '';
  position: absolute;
  left: 12px;
  top: 0;
  bottom: 16px;
  border-left: 2px solid var(--tree-line-color);
}

.tree-node:last-child > .tree-children::before {
  display: none;
}
</style>
