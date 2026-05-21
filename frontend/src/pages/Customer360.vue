<template>
  <div class="flex h-full bg-slate-50 font-sans">
    <!-- Sidebar: Customer List -->
    <div class="w-80 border-r border-slate-200 bg-white flex flex-col shrink-0">
      <div class="p-4 border-b border-slate-200">
        <h2 class="text-lg font-bold text-slate-800 mb-3">{{ __('Customer Directory') }}</h2>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search Customer (Global)')"
            class="w-full pl-9 pr-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-600 focus:bg-white transition-all"
          />
          <span class="absolute left-3 top-2.5 text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
        </div>
      </div>

      <!-- Customer List -->
      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div
          v-for="cust in filteredCustomers"
          :key="cust.name"
          @click="selectCustomer(cust)"
          class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all hover:bg-slate-50"
          :class="selectedCustomerName === cust.name ? 'bg-teal-50 border border-teal-100' : ''"
        >
          <div class="w-10 h-10 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center font-bold text-sm shrink-0">
            {{ cust.customer_name ? cust.customer_name.slice(0, 2).toUpperCase() : 'CU' }}
          </div>
          <div class="min-w-0 flex-1">
            <div class="font-semibold text-sm text-slate-800 truncate">{{ cust.customer_name }}</div>
            <div class="text-xs text-slate-500 truncate flex items-center gap-2 mt-0.5">
              <span>{{ cust.customer_type || 'Company' }}</span>
              <span class="w-1 h-1 rounded-full bg-slate-300"></span>
              <span>{{ cust.territory || 'Default' }}</span>
            </div>
          </div>
        </div>
        <div v-if="filteredCustomers.length === 0" class="text-center p-6 text-slate-400 text-sm">
          {{ __('No customers found') }}
        </div>
      </div>

      <div class="p-3 border-t border-slate-200 flex gap-2">
        <Button class="w-full" variant="solid" :label="__('Add Customer')" @click="showAddModal = true">
          <template #prefix>
            <FeatherIcon name="plus" class="h-4 w-4" />
          </template>
        </Button>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <div v-if="!selectedCustomer" class="flex-1 flex flex-col items-center justify-center text-slate-400 p-8">
        <div class="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center mb-4">
          <FeatherIcon name="user" class="h-10 w-10 text-slate-300" />
        </div>
        <h3 class="text-lg font-semibold text-slate-700">{{ __('No Customer Selected') }}</h3>
        <p class="text-sm text-slate-500 mt-1 max-w-sm text-center">
          {{ __('Please search and select a customer from the left directory to view their unified 360 profile.') }}
        </p>
      </div>

      <div v-else class="flex-1 flex flex-col overflow-hidden">
        <!-- Unified Customer Header -->
        <div class="bg-white border-b border-slate-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shrink-0 shadow-sm">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-xl bg-teal-600 text-white flex items-center justify-center font-black text-2xl shadow-md shadow-teal-600/10 shrink-0">
              {{ selectedCustomer.customer_name ? selectedCustomer.customer_name.slice(0, 2).toUpperCase() : 'CU' }}
            </div>
            <div>
              <div class="flex items-center gap-3">
                <h1 class="text-2xl font-bold text-slate-800">{{ selectedCustomer.customer_name }}</h1>
                <Badge :label="selectedCustomer.customer_type || 'Corporate'" theme="teal" variant="subtle" />
                <Badge v-if="watchlist.enabled" label="Watchlist" theme="red" variant="subtle" />
              </div>
              <div class="text-sm text-slate-500 flex flex-wrap items-center gap-4 mt-1.5">
                <span class="flex items-center gap-1">
                  <FeatherIcon name="hash" class="h-3.5 w-3.5 text-slate-400" />
                  ID: {{ selectedCustomer.name }}
                </span>
                <span class="flex items-center gap-1">
                  <FeatherIcon name="map-pin" class="h-3.5 w-3.5 text-slate-400" />
                  {{ selectedCustomer.territory || __('National') }}
                </span>
                <span class="flex items-center gap-1">
                  <FeatherIcon name="users" class="h-3.5 w-3.5 text-slate-400" />
                  Group: {{ selectedCustomer.customer_group || __('Corporate Clients') }}
                </span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <Button variant="solid" :label="__('New Application')" @click="triggerNewApplication">
              <template #prefix>
                <FeatherIcon name="file-plus" class="h-4 w-4" />
              </template>
            </Button>
            <Button variant="outline" :label="__('Communicate')" @click="triggerCommunicate">
              <template #prefix>
                <FeatherIcon name="message-square" class="h-4 w-4" />
              </template>
            </Button>
            <Button variant="outline" :label="__('Export Profile')" @click="triggerExport">
              <template #prefix>
                <FeatherIcon name="download" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>

        <!-- Quick Stats Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 px-6 pt-6 shrink-0">
          <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center gap-4">
            <div class="w-10 h-10 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center shrink-0">
              <FeatherIcon name="dollar-sign" class="h-5 w-5" />
            </div>
            <div>
              <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">{{ __('Total Outstanding') }}</div>
              <div class="text-lg font-bold text-slate-800 mt-0.5">Rp 24.8M</div>
              <div class="text-xs text-slate-500 mt-0.5">6 active facilities</div>
            </div>
          </div>

          <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center gap-4">
            <div class="w-10 h-10 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
              <FeatherIcon name="activity" class="h-5 w-5" />
            </div>
            <div>
              <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">{{ __('Risk Grade') }}</div>
              <div class="text-lg font-bold text-slate-800 mt-0.5">B+ (Stable)</div>
              <div class="text-xs text-slate-500 mt-0.5">Score: 782 / 1000</div>
            </div>
          </div>

          <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center gap-4">
            <div class="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <FeatherIcon name="globe" class="h-5 w-5" />
            </div>
            <div>
              <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">{{ __('Group Exposure') }}</div>
              <div class="text-lg font-bold text-slate-800 mt-0.5">Rp 41.2M</div>
              <div class="text-xs text-slate-500 mt-0.5">4 related entities</div>
            </div>
          </div>

          <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center gap-4">
            <div class="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
              <FeatherIcon name="shield" class="h-5 w-5" />
            </div>
            <div>
              <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">{{ __('KYC Review Status') }}</div>
              <div class="text-lg font-bold text-slate-800 mt-0.5">Verified</div>
              <div class="text-xs text-slate-500 mt-0.5">Next: 18 Jun 2026</div>
            </div>
          </div>
        </div>

        <!-- Custom Tabs Component -->
        <div class="px-6 pt-4 shrink-0">
          <div class="flex border-b border-slate-200 gap-6">
            <button
              v-for="t in tabs"
              :key="t.key"
              @click="activeTab = t.key"
              class="pb-3 text-sm font-semibold border-b-2 transition-all"
              :class="activeTab === t.key ? 'border-teal-600 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <!-- Scrollable Tab Content Panels -->
        <div class="flex-1 overflow-y-auto p-6 min-h-0">
          <!-- 1. Overview Tab -->
          <div v-if="activeTab === 'overview'" class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <!-- AI generated summary -->
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm lg:col-span-2">
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center gap-2">
                    <FeatherIcon name="cpu" class="h-5 w-5 text-teal-600 animate-pulse" />
                    <h3 class="font-bold text-slate-800">{{ __('AI Customer Summary') }}</h3>
                  </div>
                  <Button variant="outline" size="sm" :label="__('Refresh AI')" @click="regenerateSummary" />
                </div>
                <textarea
                  v-model="aiSummary"
                  rows="4"
                  class="w-full p-4 bg-teal-50/30 border border-teal-100 rounded-lg text-sm text-slate-700 focus:outline-none focus:border-teal-400"
                ></textarea>
                <div class="mt-3 flex justify-between items-center text-xs text-slate-400">
                  <span>Last updated: Just Now</span>
                  <Button variant="subtle" size="sm" :label="__('Save Summary')" @click="saveSummary" />
                </div>
              </div>

              <!-- General Score Card Quick View -->
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 class="font-bold text-slate-800 mb-4">{{ __('Bureau Rating') }}</h3>
                <div class="flex items-center gap-4 mb-4">
                  <div class="w-16 h-16 rounded-full border-4 border-teal-500 flex flex-col items-center justify-center bg-teal-50/50">
                    <span class="text-lg font-extrabold text-teal-700">7.2</span>
                    <span class="text-[9px] uppercase font-bold text-slate-400">Pefindo</span>
                  </div>
                  <div>
                    <div class="text-sm font-semibold text-slate-700">SLIK / OJK Status</div>
                    <div class="text-xs text-emerald-600 font-semibold flex items-center gap-1 mt-0.5">
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                      KOL-1 (Lancar / Healthy)
                    </div>
                  </div>
                </div>
                <div class="text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">
                  No default recorded in past 24 months. Outstanding loan is fully secured by collateral (LTV ~62%).
                </div>
              </div>
            </div>

            <!-- Relationship Graph & Timeline View -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Node relationship graph -->
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="font-bold text-slate-800">{{ __('Network & Relationships') }}</h3>
                  <select v-model="relationFilter" class="text-xs border border-slate-200 rounded px-2 py-1 focus:outline-none bg-slate-50">
                    <option value="all">All Relations</option>
                    <option value="shareholder">Shareholders</option>
                    <option value="group">Group Companies</option>
                  </select>
                </div>
                <div class="h-64 border border-slate-100 rounded-lg bg-slate-50/50 relative overflow-hidden flex items-center justify-center">
                  <!-- SVG relationship graph representation -->
                  <svg width="100%" height="100%" class="absolute inset-0">
                    <!-- Lines connecting center node to others -->
                    <line x1="50%" y1="50%" x2="20%" y2="25%" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4" />
                    <line x1="50%" y1="50%" x2="80%" y2="25%" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4" />
                    <line x1="50%" y1="50%" x2="20%" y2="75%" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4" />
                    <line x1="50%" y1="50%" x2="80%" y2="75%" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4" />

                    <!-- Center Customer Node -->
                    <circle cx="50%" cy="50%" r="28" fill="#008C95" />
                    <text x="50%" y="52%" text-anchor="middle" fill="#ffffff" font-size="9" font-weight="bold">CUSTOMER</text>

                    <!-- Spokes Nodes -->
                    <circle cx="20%" cy="25%" r="20" fill="#f8fafc" stroke="#64748b" stroke-width="2" />
                    <text x="20%" y="27%" text-anchor="middle" fill="#334155" font-size="8" font-weight="bold">UBO</text>

                    <circle cx="80%" cy="25%" r="20" fill="#f8fafc" stroke="#64748b" stroke-width="2" />
                    <text x="80%" y="27%" text-anchor="middle" fill="#334155" font-size="8" font-weight="bold">Directors</text>

                    <circle cx="20%" cy="75%" r="20" fill="#f8fafc" stroke="#64748b" stroke-width="2" />
                    <text x="20%" y="77%" text-anchor="middle" fill="#334155" font-size="8" font-weight="bold">Group</text>

                    <circle cx="80%" cy="75%" r="20" fill="#f8fafc" stroke="#64748b" stroke-width="2" />
                    <text x="80%" y="77%" text-anchor="middle" fill="#334155" font-size="8" font-weight="bold">RMs</text>
                  </svg>
                  <div class="absolute bottom-2 right-2 flex gap-1">
                    <button class="w-6 h-6 rounded bg-white shadow border border-slate-200 text-xs flex items-center justify-center hover:bg-slate-50 font-bold">+</button>
                    <button class="w-6 h-6 rounded bg-white shadow border border-slate-200 text-xs flex items-center justify-center hover:bg-slate-50 font-bold">-</button>
                  </div>
                </div>
              </div>

              <!-- Unified timeline view -->
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col h-[330px]">
                <h3 class="font-bold text-slate-800 mb-4">{{ __('Customer History Timeline') }}</h3>
                <div class="flex-1 overflow-y-auto space-y-4 pr-2">
                  <div v-for="event in timelineEvents" :key="event.time" class="flex gap-3 relative">
                    <div class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center shrink-0 z-10">
                      <FeatherIcon :name="event.icon" class="h-4 w-4 text-slate-600" />
                    </div>
                    <div class="flex-1 bg-slate-50 rounded-lg p-3 border border-slate-100">
                      <div class="flex justify-between items-center">
                        <span class="font-semibold text-xs text-slate-700">{{ event.title }}</span>
                        <span class="text-[10px] text-slate-400">{{ event.time }}</span>
                      </div>
                      <p class="text-xs text-slate-500 mt-1">{{ event.desc }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. Personal/Company Data Tab -->
          <div v-if="activeTab === 'profile'" class="space-y-6">
            <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <div class="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
                <h3 class="font-bold text-slate-800 text-lg">{{ __('Corporate Profile & Identity') }}</h3>
                <div class="flex gap-2">
                  <Button v-if="!isEditing" variant="outline" size="sm" :label="__('Edit Profile')" @click="isEditing = true" />
                  <Button v-if="isEditing" variant="solid" size="sm" :label="__('Save Changes')" @click="saveProfileData" />
                  <Button v-if="isEditing" variant="outline" size="sm" :label="__('Cancel')" @click="isEditing = false" />
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Editable form -->
                <div class="space-y-4">
                  <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">{{ __('Customer Name') }}</label>
                    <input
                      v-model="editForm.customer_name"
                      :disabled="!isEditing"
                      type="text"
                      class="w-full px-3 py-2 border rounded-lg text-sm bg-slate-50 disabled:opacity-75 focus:outline-none focus:border-teal-500 focus:bg-white border-slate-200"
                    />
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs font-bold text-slate-500 uppercase mb-1">{{ __('NPWP Number (Tax ID)') }}</label>
                      <input
                        v-model="editForm.npwp"
                        :disabled="!isEditing"
                        type="text"
                        placeholder="00.000.000.0-000.000"
                        class="w-full px-3 py-2 border rounded-lg text-sm bg-slate-50 disabled:opacity-75 focus:outline-none focus:border-teal-500 focus:bg-white"
                        :class="npwpError ? 'border-red-400' : 'border-slate-200'"
                      />
                      <span v-if="npwpError" class="text-[10px] text-red-500 block mt-1">{{ npwpError }}</span>
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-slate-500 uppercase mb-1">{{ __('KTP (Primary Contact)') }}</label>
                      <input
                        v-model="editForm.ktp"
                        :disabled="!isEditing"
                        type="text"
                        placeholder="16-digit ID"
                        class="w-full px-3 py-2 border rounded-lg text-sm bg-slate-50 disabled:opacity-75 focus:outline-none focus:border-teal-500 focus:bg-white"
                        :class="ktpError ? 'border-red-400' : 'border-slate-200'"
                      />
                      <span v-if="ktpError" class="text-[10px] text-red-500 block mt-1">{{ ktpError }}</span>
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">{{ __('Registered Address') }}</label>
                    <textarea
                      v-model="editForm.address"
                      :disabled="!isEditing"
                      rows="3"
                      class="w-full px-3 py-2 border rounded-lg text-sm bg-slate-50 disabled:opacity-75 focus:outline-none focus:border-teal-500 focus:bg-white border-slate-200"
                    ></textarea>
                  </div>
                </div>

                <!-- KYC and Metadata controls -->
                <div class="space-y-6">
                  <!-- e-KYC integration status -->
                  <div class="bg-slate-50 rounded-xl p-5 border border-slate-200">
                    <div class="flex items-center justify-between mb-4">
                      <span class="font-bold text-sm text-slate-700 flex items-center gap-1.5">
                        <FeatherIcon name="check-circle" class="h-4.5 w-4.5 text-emerald-500" />
                        {{ __('Dukcapil e-KYC Status') }}
                      </span>
                      <Badge label="Verified" theme="emerald" />
                    </div>
                    <p class="text-xs text-slate-500 mb-4">Verified against central civil database with NPWP & KTP hash match.</p>
                    <Button class="w-full" variant="outline" :label="__('Trigger Re-Verification')" @click="verifyKyc" />
                  </div>

                  <!-- Tagging system -->
                  <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-2">{{ __('Segmentation Tags') }}</label>
                    <div class="flex flex-wrap gap-1.5 items-center">
                      <div
                        v-for="tag in currentTags"
                        :key="tag.label"
                        class="px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5"
                        :style="{ backgroundColor: tag.bg, color: tag.fg }"
                      >
                        {{ tag.label }}
                        <span class="cursor-pointer font-bold text-slate-500 hover:text-slate-800" @click="removeTag(tag)">×</span>
                      </div>
                      <button
                        @click="showAddTag = true"
                        class="px-3 py-1 rounded-full text-xs font-medium border border-dashed border-slate-300 text-slate-500 hover:border-slate-400 hover:bg-slate-50"
                      >
                        + Add Tag
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. Shareholders & Directors Tab -->
          <div v-if="activeTab === 'structure'" class="space-y-6">
            <!-- Shareholder structure -->
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-slate-800 text-base">{{ __('Shareholders Structure') }}</h3>
                <span class="text-xs font-semibold" :class="shareholderSum === 100 ? 'text-emerald-600' : 'text-red-500'">
                  Total Ownership: {{ shareholderSum }}% (Validator: must equal 100%)
                </span>
              </div>
              <table class="w-full text-sm">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left font-bold">{{ __('Shareholder Name') }}</th>
                    <th class="py-3 px-4 text-center font-bold">{{ __('Ownership %') }}</th>
                    <th class="py-3 px-4 text-center font-bold">{{ __('Ultimate Beneficial Owner (UBO)') }}</th>
                    <th class="py-3 px-4 text-center font-bold">{{ __('Action') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="sh in shareholders" :key="sh.name" class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ sh.name }}</td>
                    <td class="py-3 px-4 text-center">
                      <input
                        type="number"
                        v-model.number="sh.share"
                        class="w-16 px-2 py-1 text-center border border-slate-200 rounded focus:outline-none focus:border-teal-500"
                      />
                    </td>
                    <td class="py-3 px-4 text-center">
                      <span v-if="sh.ubo" class="px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 font-bold text-[10px]">UBO</span>
                      <span v-else class="text-slate-300">-</span>
                    </td>
                    <td class="py-3 px-4 text-center">
                      <Button variant="subtle" size="sm" :label="__('Profile')" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Directors and PEP/AML check -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('Directors & Commissioners') }}</h3>
                <div class="space-y-3">
                  <div v-for="dir in directors" :key="dir.name" class="flex items-center justify-between p-3 border border-slate-100 rounded-lg hover:bg-slate-50">
                    <div>
                      <div class="font-semibold text-slate-800 text-sm">{{ dir.name }}</div>
                      <div class="text-xs text-slate-500 mt-0.5">Role: {{ dir.role }} • Tenure: {{ dir.tenure }}</div>
                    </div>
                    <div class="flex items-center gap-2">
                      <Badge :label="dir.pepStatus || 'AML Cleared'" :theme="dir.pepStatus === 'AML Warning' ? 'red' : 'emerald'" />
                      <Button variant="subtle" size="sm" @click="checkAml(dir)">
                        <template #prefix>
                          <FeatherIcon name="shield" class="h-3.5 w-3.5" />
                        </template>
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Related Entities & Group Exposure -->
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('Related Entities & Group Exposure') }}</h3>
                <div class="space-y-4">
                  <div v-for="ent in relatedEntities" :key="ent.name" class="flex justify-between items-center p-3 bg-slate-50 border border-slate-100 rounded-lg">
                    <div>
                      <span class="font-bold text-sm text-slate-800">{{ ent.name }}</span>
                      <span class="text-xs text-slate-500 block mt-0.5">Relation: {{ ent.relation }}</span>
                    </div>
                    <div class="text-right">
                      <div class="font-bold text-sm text-slate-800">Rp {{ ent.exposure }}B</div>
                      <span class="text-xs text-slate-400">Total Limit</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 4. Financing & Credit Tab -->
          <div v-if="activeTab === 'financing'" class="space-y-6">
            <!-- Active Facilities snapshot -->
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
              <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('Active Financing Facilities') }}</h3>
              <table class="w-full text-sm">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left font-bold">{{ __('Facility Type') }}</th>
                    <th class="py-3 px-4 text-right font-bold">{{ __('Outstanding') }}</th>
                    <th class="py-3 px-4 text-right font-bold">{{ __('Limit') }}</th>
                    <th class="py-3 px-4 text-center font-bold">{{ __('LTV %') }}</th>
                    <th class="py-3 px-4 text-center font-bold">{{ __('Health') }}</th>
                    <th class="py-3 px-4 text-center font-bold">{{ __('Quick Actions') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="fac in facilities" :key="fac.type" class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ fac.type }}</td>
                    <td class="py-3 px-4 text-right font-mono">Rp {{ fac.outstanding }}M</td>
                    <td class="py-3 px-4 text-right font-mono">Rp {{ fac.limit }}M</td>
                    <td class="py-3 px-4 text-center font-mono">{{ Math.round((fac.outstanding / fac.limit) * 100) }}%</td>
                    <td class="py-3 px-4 text-center">
                      <Badge :label="fac.health" :theme="fac.health === 'KOL-1' ? 'emerald' : 'red'" />
                    </td>
                    <td class="py-3 px-4 text-center flex justify-center gap-1.5">
                      <Button variant="subtle" size="sm" :label="__('Top-up')" @click="triggerAction('Top-up')" />
                      <Button variant="subtle" size="sm" :label="__('Restructure')" @click="triggerAction('Restructure')" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Credit score trend + bureau -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('Credit Bureau Trend (SLIK)') }}</h3>
                <div class="h-48 border border-slate-100 rounded-lg p-4 flex flex-col justify-between">
                  <!-- Score Trend SVG representation -->
                  <div class="flex-1 flex items-end gap-6 px-4">
                    <div class="flex-1 flex flex-col items-center gap-2">
                      <div class="w-full bg-teal-100 rounded-t h-28 flex items-end justify-center"><span class="text-[10px] text-teal-800 font-bold mb-1">680</span></div>
                      <span class="text-xs text-slate-400">Oct 25</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center gap-2">
                      <div class="w-full bg-teal-200 rounded-t h-32 flex items-end justify-center"><span class="text-[10px] text-teal-800 font-bold mb-1">710</span></div>
                      <span class="text-xs text-slate-400">Dec 25</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center gap-2">
                      <div class="w-full bg-teal-500 rounded-t h-40 flex items-end justify-center"><span class="text-[10px] text-white font-bold mb-1">782</span></div>
                      <span class="text-xs text-slate-500 font-semibold">Feb 26</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Collateral registry details -->
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('Collateral & Appraisals') }}</h3>
                <div class="space-y-3">
                  <div v-for="col in collaterals" :key="col.asset" class="flex justify-between items-center p-3 border border-slate-100 rounded-lg">
                    <div>
                      <div class="font-semibold text-slate-800 text-sm">{{ col.asset }}</div>
                      <div class="text-xs text-slate-500 mt-0.5">Value: Rp {{ col.value }}M • Expiry: {{ col.expiry }}</div>
                    </div>
                    <div class="text-right">
                      <Badge :label="col.status" theme="emerald" />
                      <span class="text-[11px] text-slate-400 block mt-1">Re-appraisal done</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 5. Statements & Visits Tab -->
          <div v-if="activeTab === 'statements'" class="space-y-6">
            <!-- Financial statements spreading Pl/Bs -->
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
              <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('Financial Statement Spreading') }}</h3>
              <table class="w-full text-sm">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left font-bold">{{ __('Key Metric') }}</th>
                    <th class="py-3 px-4 text-right font-bold">{{ __('2023 Audited (Rp)') }}</th>
                    <th class="py-3 px-4 text-right font-bold">{{ __('2024 Audited (Rp)') }}</th>
                    <th class="py-3 px-4 text-right font-bold">{{ __('2025 Forecast (Rp)') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ __('Total Revenue') }}</td>
                    <td class="py-3 px-4 text-right font-mono">112.4B</td>
                    <td class="py-3 px-4 text-right font-mono">128.9B</td>
                    <td class="py-3 px-4 text-right font-mono text-teal-600">144.5B</td>
                  </tr>
                  <tr class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ __('EBITDA') }}</td>
                    <td class="py-3 px-4 text-right font-mono">18.5B</td>
                    <td class="py-3 px-4 text-right font-mono">22.1B</td>
                    <td class="py-3 px-4 text-right font-mono text-teal-600">26.8B</td>
                  </tr>
                  <tr class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ __('Net Profit') }}</td>
                    <td class="py-3 px-4 text-right font-mono">10.2B</td>
                    <td class="py-3 px-4 text-right font-mono">12.8B</td>
                    <td class="py-3 px-4 text-right font-mono text-teal-600">15.1B</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Site Visits Logs -->
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
              <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('Site Visit History (RM due diligence)') }}</h3>
              <div class="space-y-4">
                <div v-for="visit in siteVisits" :key="visit.date" class="p-4 border border-slate-100 rounded-xl bg-slate-50/50">
                  <div class="flex justify-between items-start">
                    <div>
                      <div class="font-semibold text-slate-800 text-sm">{{ visit.rm }}</div>
                      <div class="text-xs text-slate-500 mt-0.5">Date: {{ visit.date }} • Coordinates: {{ visit.gps }}</div>
                    </div>
                    <Button variant="outline" size="sm" :label="__('Download PDF Report')" />
                  </div>
                  <p class="text-xs text-slate-600 mt-3 border-t border-slate-200/60 pt-3">
                    {{ visit.notes }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- 6. Engagement & Governance Tab -->
          <div v-if="activeTab === 'engagement'" class="space-y-6">
            <!-- Watchlist reason, NPL controls -->
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
              <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('Governance & Risk Controls') }}</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Watchlist Toggle -->
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <span class="font-bold text-sm text-slate-800">Watchlist Status</span>
                      <span class="text-xs text-slate-500 block mt-0.5">Alert credit team to monitor closely</span>
                    </div>
                    <input
                      type="checkbox"
                      v-model="watchlist.enabled"
                      class="w-10 h-6 bg-slate-200 checked:bg-teal-600 rounded-full transition-all cursor-pointer accent-teal-600"
                    />
                  </div>
                  <div v-if="watchlist.enabled">
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">{{ __('Mandatory Watchlist Reason') }}</label>
                    <textarea
                      v-model="watchlist.reason"
                      rows="2"
                      placeholder="Reason for placing on watchlist..."
                      class="w-full px-3 py-2 border rounded-lg text-sm bg-slate-50 border-slate-200 focus:outline-none focus:border-teal-500 focus:bg-white"
                    ></textarea>
                  </div>
                </div>

                <!-- Early warning risk triggers -->
                <div class="bg-slate-50 rounded-xl p-4 border border-slate-200">
                  <span class="font-bold text-sm text-slate-800 block mb-3">Early Warning Triggers</span>
                  <div class="space-y-2">
                    <div class="flex items-center gap-2 text-xs text-slate-600">
                      <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                      No payment delays in past 180 days.
                    </div>
                    <div class="flex items-center gap-2 text-xs text-slate-600">
                      <span class="w-2 h-2 rounded-full bg-orange-500"></span>
                      One insurance expiry certificate nearing due date.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Customer Tasks -->
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
              <h3 class="font-bold text-slate-800 text-base mb-4">{{ __('RM Follow-up Tasks') }}</h3>
              <div class="flex gap-2 mb-4">
                <input
                  v-model="newTaskText"
                  type="text"
                  placeholder="New task description..."
                  class="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-500"
                />
                <Button variant="solid" :label="__('Add Task')" @click="addTask" />
              </div>
              <div class="space-y-2">
                <div v-for="task in tasks" :key="task.id" class="flex items-center justify-between p-3 border border-slate-100 rounded-lg hover:bg-slate-50">
                  <div class="flex items-center gap-3">
                    <input type="checkbox" v-model="task.done" class="accent-teal-600" />
                    <span :class="task.done ? 'line-through text-slate-400' : 'text-slate-800 font-semibold'" class="text-sm">
                      {{ task.text }}
                    </span>
                  </div>
                  <Badge :label="task.priority" :theme="task.priority === 'High' ? 'red' : 'gray'" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Dialog for Add Customer -->
  <Dialog v-model="showAddModal" :options="{ title: 'Add New Customer' }">
    <template #body-content>
      <div class="space-y-4 pt-3">
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Customer Name</label>
          <input v-model="newCustomerName" type="text" placeholder="e.g. PT Budi Jaya" class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-500" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Segment</label>
          <select v-model="newCustomerType" class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-500 bg-white">
            <option value="Company">Company (Corporate)</option>
            <option value="Individual">Individual (UKM / Retail)</option>
          </select>
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex gap-2 justify-end">
        <Button variant="outline" label="Cancel" @click="showAddModal = false" />
        <Button variant="solid" label="Save" @click="addCustomer" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Button, FeatherIcon, Badge, Dialog, usePageMeta, createListResource, toast } from 'frappe-ui'

// State variables
const activeTab = ref('overview')
const searchQuery = ref('')
const selectedCustomerName = ref('')
const selectedCustomer = ref(null)
const relationFilter = ref('all')
const isEditing = ref(false)
const showAddModal = ref(false)
const showAddTag = ref(false)

// Custom customer registration state
const newCustomerName = ref('')
const newCustomerType = ref('Company')

// Task state
const newTaskText = ref('')
const tasks = ref([
  { id: 1, text: 'Collect financial report audited for 2025', priority: 'High', done: false },
  { id: 2, text: 'Confirm site visit coordinates with commissioner', priority: 'Medium', done: false },
])

// Edit profile form
const editForm = ref({
  customer_name: '',
  npwp: '',
  ktp: '',
  address: '',
})
const npwpError = ref('')
const ktpError = ref('')

// Watchlist and risk
const watchlist = ref({
  enabled: false,
  reason: '',
})

// Current segmentation tags
const currentTags = ref([
  { label: 'Blue-Chip Corporate', bg: '#e0f2fe', fg: '#0369a1' },
  { label: 'Priority Account', bg: '#fef3c7', fg: '#b45309' },
])

// Mocked features data representing typical core fields from excel
const timelineEvents = ref([
  { title: 'Credit Application Received', time: '2 hours ago', desc: 'Applied for Working Capital facility upgrade.', icon: 'file-text' },
  { title: 'AML Clear Status', time: '1 day ago', desc: 'Directors and Ultimate Beneficial Owners passed PEP check.', icon: 'shield' },
  { title: 'Site Visit Completed', time: '3 days ago', desc: 'RM conducted site verification, photos and GPS captured.', icon: 'camera' },
])

const editFormSummaryDefault = 'Stable payment behavior, clean KYC, one collateral insurance document nearing expiry, and a medium-confidence working capital top-up opportunity.'
const aiSummary = ref(editFormSummaryDefault)

const shareholders = ref([
  { name: 'PT Investama Sejahtera', share: 60, ubo: true },
  { name: 'Hadi Wijaya (Founder)', share: 30, ubo: false },
  { name: 'Rian Pratama', share: 10, ubo: false },
])

const shareholderSum = computed(() => {
  return shareholders.value.reduce((sum, sh) => sum + (sh.share || 0), 0)
})

const directors = ref([
  { name: 'Hadi Wijaya', role: 'President Director', tenure: '5 years', pepStatus: 'AML Cleared' },
  { name: 'Indra Permana', role: 'Director of Finance', tenure: '3 years', pepStatus: 'AML Cleared' },
])

const relatedEntities = ref([
  { name: 'PT Investama Logistik', relation: 'Subsidiary', exposure: 12.5 },
  { name: 'PT Investama Property', relation: 'Sister Company', exposure: 4.8 },
])

const facilities = ref([
  { type: 'Working Capital Facility (PRK)', outstanding: 18.5, limit: 20.0, health: 'KOL-1' },
  { type: 'Investment Loan (Kinvest)', outstanding: 6.3, limit: 10.0, health: 'KOL-1' },
])

const collaterals = ref([
  { asset: 'Shophouse Certificate - Sudirman Blok C', value: 32.0, expiry: '12 Dec 2028', status: 'Active' },
  { asset: 'Corporate Guarantee - PT Investama Sejahtera', value: 15.0, expiry: 'N/A', status: 'Active' },
])

const siteVisits = ref([
  { rm: 'Budi Santoso (Senior RM)', date: '12 Feb 2026', gps: '-6.2088, 106.8456', notes: 'Verified active warehouse operation. Inventory storage matches audit book. Recommendation: Approve facility extension.' }
])

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'profile', label: 'Profile & KYC' },
  { key: 'structure', label: 'Ownership & Structure' },
  { key: 'financing', label: 'Financing & Credit' },
  { key: 'statements', label: 'Statements & Visits' },
  { key: 'engagement', label: 'Engagement & Governance' },
]

// Query live customers from Customer DocType
const customersResource = createListResource({
  type: 'list',
  doctype: 'Customer',
  fields: ['name', 'customer_name', 'customer_type', 'customer_group', 'territory', 'website', 'tax_id'],
  limit: 100,
  auto: true,
})

const filteredCustomers = computed(() => {
  if (!customersResource.data) return []
  const query = searchQuery.value.toLowerCase()
  return customersResource.data.filter(c =>
    (c.customer_name || '').toLowerCase().includes(query) ||
    (c.name || '').toLowerCase().includes(query)
  )
})

function selectCustomer(cust) {
  selectedCustomer.value = cust
  selectedCustomerName.value = cust.name
  isEditing.value = false

  // Populate editable form
  editForm.value.customer_name = cust.customer_name
  editForm.value.npwp = cust.tax_id || '00.000.000.0-000.000'
  editForm.value.ktp = '3271010000000000' // mock default
  editForm.value.address = 'Jl. Jend. Sudirman No. 12, Jakarta Selatan'

  // Reset errors
  npwpError.value = ''
  ktpError.value = ''
}

// AI summary regenerate
function regenerateSummary() {
  aiSummary.value = 'AI SUMMARY REGENERATED: Customer has shown a stable loan utilization trend. Group corporate structure presents strong backing by PT Investama Sejahtera. Early watch list trigger resolved.'
  toast.success('AI summary updated')
}

function saveSummary() {
  toast.success('AI Summary notes saved successfully')
}

// Validation function
function validateNpwp(val) {
  // Simple Indonesian NPWP format: 15 or 16 numeric digits
  const clean = val.replace(/[^0-9]/g, '')
  if (clean.length !== 15 && clean.length !== 16) {
    return 'Invalid NPWP length. Indonesian NPWP must be 15 or 16 numeric digits.'
  }
  return ''
}

function validateKtp(val) {
  const clean = val.replace(/[^0-9]/g, '')
  if (clean.length !== 16) {
    return 'Invalid KTP format. Indonesian NIK must be exactly 16 numeric digits.'
  }
  return ''
}

function saveProfileData() {
  npwpError.value = validateNpwp(editForm.value.npwp)
  ktpError.value = validateKtp(editForm.value.ktp)

  if (npwpError.value || ktpError.value) {
    toast.error('Validation errors found')
    return
  }

  // Save via frappe-ui (mock writing back to selectedCustomer)
  if (selectedCustomer.value) {
    selectedCustomer.value.customer_name = editForm.value.customer_name
    selectedCustomer.value.tax_id = editForm.value.npwp
    toast.success('Customer Profile Identity updated')
  }
  isEditing.value = false
}

function verifyKyc() {
  toast.success('Dukcapil e-KYC Verification successful')
}

// AML check method
function checkAml(dir) {
  dir.pepStatus = 'AML Checked & Cleared'
  toast.success(`PEP/AML Check cleared for Director: ${dir.name}`)
}

function removeTag(tag) {
  currentTags.value = currentTags.value.filter(t => t.label !== tag.label)
}

function triggerNewApplication() {
  toast.success('New Loan Origination Application form created')
}

function triggerCommunicate() {
  toast.success('Omnichannel communication compose interface opened')
}

function triggerExport() {
  toast.success('Generating password-protected watermarked PDF profile...')
}

function triggerAction(action) {
  toast.success(`Action: ${action} triggered for selected facility`)
}

function addTask() {
  if (!newTaskText.value.trim()) return
  tasks.value.unshift({
    id: Date.now(),
    text: newTaskText.value,
    priority: 'Medium',
    done: false,
  })
  newTaskText.value = ''
  toast.success('RM Follow-up task added')
}

// Add customer record
async function addCustomer() {
  if (!newCustomerName.value.trim()) {
    toast.error('Customer name is required')
    return
  }
  // Standard call to insert Customer
  try {
    const listRes = customersResource
    await listRes.insert.submit({
      customer_name: newCustomerName.value,
      customer_type: newCustomerType.value,
      customer_group: 'All Customer Groups',
      territory: 'All Territories',
    })
    toast.success('Customer added successfully')
    showAddModal.value = false
    newCustomerName.value = ''
    listRes.reload()
  } catch (err) {
    console.error(err)
    toast.error('Failed to create customer record')
  }
}

// Setup Page Meta
usePageMeta(() => ({ title: 'Customer 360' }))

// Initialize page
onMounted(async () => {
  await customersResource.promise
  if (filteredCustomers.value.length > 0) {
    selectCustomer(filteredCustomers.value[0])
  }
})
</script>

<style scoped>
/* Scrollbar tweaks */
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
