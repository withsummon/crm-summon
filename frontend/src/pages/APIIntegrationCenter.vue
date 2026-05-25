<template>
  <div class="flex flex-1 flex-col min-h-0 bg-gray-50 font-sans select-none">
    <LayoutHeader stretch-left>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-[12px] bg-gradient-to-br from-teal-500 to-teal-700">
            <FeatherIcon name="link" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-ink-gray-9">API & Integration Center</h1>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <button @click="runHealthCheck" class="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-50 transition-colors bg-white">
            <FeatherIcon name="activity" class="h-3.5 w-3.5" />
            Health Check
          </button>
          <button @click="showAddModal = true" class="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 transition-colors">
            <FeatherIcon name="plus" class="h-3.5 w-3.5" />
            Add Integration
          </button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex flex-1 min-h-0 overflow-hidden">
      <!-- Sidebar -->
      <div class="w-56 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col overflow-y-auto">
        <div class="p-3 space-y-0.5">
          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider px-2 pt-2 pb-1">API Core</p>
          <button v-for="item in apiCoreNav" :key="item.id"
            @click="activeSection = item.id"
            class="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs transition-colors"
            :class="activeSection === item.id ? 'bg-teal-50 text-teal-700 font-medium' : 'text-gray-600 hover:bg-gray-50'">
            <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 flex-shrink-0" />
            <span class="truncate">{{ item.label }}</span>
            <span v-if="item.badge" class="ml-auto text-[10px] font-medium px-1.5 py-0.5 rounded-full" :class="item.badgeColor">{{ item.badge }}</span>
          </button>

          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider px-2 pt-3 pb-1">Integrations</p>
          <button v-for="item in integrationsNav" :key="item.id"
            @click="activeSection = item.id"
            class="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs transition-colors"
            :class="activeSection === item.id ? 'bg-teal-50 text-teal-700 font-medium' : 'text-gray-600 hover:bg-gray-50'">
            <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 flex-shrink-0" />
            <span class="truncate">{{ item.label }}</span>
            <span v-if="item.badge" class="ml-auto text-[10px] font-medium px-1.5 py-0.5 rounded-full" :class="item.badgeColor">{{ item.badge }}</span>
          </button>

          <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider px-2 pt-3 pb-1">Operations</p>
          <button v-for="item in operationsNav" :key="item.id"
            @click="activeSection = item.id"
            class="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs transition-colors"
            :class="activeSection === item.id ? 'bg-teal-50 text-teal-700 font-medium' : 'text-gray-600 hover:bg-gray-50'">
            <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 flex-shrink-0" />
            <span class="truncate">{{ item.label }}</span>
            <span v-if="item.badge" class="ml-auto text-[10px] font-medium px-1.5 py-0.5 rounded-full" :class="item.badgeColor">{{ item.badge }}</span>
          </button>
        </div>

        <!-- Health Summary -->
        <div class="mt-auto p-3 border-t border-gray-100">
          <p class="text-[10px] text-gray-500 font-medium mb-2">Integration Health</p>
          <div class="flex items-center justify-between text-[10px] mb-1">
            <span class="text-green-600 font-medium">● Active</span><span class="text-gray-600 font-semibold">14</span>
          </div>
          <div class="flex items-center justify-between text-[10px] mb-1">
            <span class="text-amber-500 font-medium">● Warning</span><span class="text-gray-600 font-semibold">3</span>
          </div>
          <div class="flex items-center justify-between text-[10px]">
            <span class="text-red-500 font-medium">● Error</span><span class="text-gray-600 font-semibold">1</span>
          </div>
          <div class="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden flex">
            <div class="bg-green-500 h-full" style="width:77.8%"></div>
            <div class="bg-amber-400 h-full" style="width:16.7%"></div>
            <div class="bg-red-400 h-full" style="width:5.5%"></div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="flex-1 overflow-y-auto p-6">

        <!-- 1. API Management Console -->
        <div v-if="activeSection === 'api-management'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">API Management Console</h2>
              <p class="text-xs text-gray-500 mt-0.5">Manage API endpoints, keys, versioning, and usage metrics</p>
            </div>
            <button @click="openGenKeyModal" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-teal-700 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors">
              <FeatherIcon name="key" class="h-3.5 w-3.5" />Generate Key
            </button>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-4 gap-4 mb-5">
            <div v-for="s in apiStats" :key="s.label" class="bg-white rounded-xl border border-gray-200 p-4">
              <p class="text-xs text-gray-500">{{ s.label }}</p>
              <p class="text-xl font-bold text-gray-800 mt-1">{{ s.value }}</p>
              <p class="text-[10px] mt-1" :class="s.up ? 'text-green-600' : 'text-red-500'">{{ s.change }}</p>
            </div>
          </div>

          <!-- Endpoints Table -->
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
              <h3 class="text-sm font-medium text-gray-700">API Endpoints</h3>
              <div class="flex items-center gap-2">
                <input v-model="apiSearch" placeholder="Search endpoints..." class="text-xs border border-gray-200 rounded-lg px-3 py-1.5 w-48 focus:outline-none focus:ring-1 focus:ring-teal-400" />
                <select class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none">
                  <option>All Versions</option><option>v1</option><option>v2</option>
                </select>
              </div>
            </div>
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Endpoint</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Method</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Version</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Calls/Day</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Latency</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Status</th>
                  <th class="px-4 py-2.5"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ep in filteredEndpoints" :key="ep.id" class="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td class="px-4 py-3 font-mono text-teal-700">{{ ep.path }}</td>
                  <td class="px-4 py-3">
                    <span class="px-1.5 py-0.5 rounded text-[10px] font-bold" :class="methodColor(ep.method)">{{ ep.method }}</span>
                  </td>
                  <td class="px-4 py-3 text-gray-600">{{ ep.version }}</td>
                  <td class="px-4 py-3 text-gray-700 font-medium">{{ ep.calls }}</td>
                  <td class="px-4 py-3">
                    <span :class="ep.latency > 200 ? 'text-amber-600' : 'text-green-600'" class="font-medium">{{ ep.latency }}ms</span>
                  </td>
                  <td class="px-4 py-3">
                    <button @click="toggleEndpoint(ep)" class="flex items-center gap-1.5">
                      <div class="w-7 h-4 rounded-full transition-colors relative" :class="ep.enabled ? 'bg-teal-500' : 'bg-gray-200'">
                        <div class="w-3 h-3 bg-white rounded-full absolute top-0.5 transition-all" :class="ep.enabled ? 'left-3.5' : 'left-0.5'"></div>
                      </div>
                      <span :class="ep.enabled ? 'text-teal-600' : 'text-gray-400'">{{ ep.enabled ? 'Active' : 'Off' }}</span>
                    </button>
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-1">
                      <button @click="showToast('Endpoint copied')" class="p-1 text-gray-400 hover:text-teal-600 rounded"><FeatherIcon name="copy" class="h-3.5 w-3.5" /></button>
                      <button v-if="ep.deprecate" class="px-2 py-0.5 text-[10px] text-amber-600 bg-amber-50 rounded border border-amber-200">Deprecated</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Custom Integrations CRUD -->
          <div class="mt-5 bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
              <h3 class="text-sm font-medium text-gray-700">Custom Integrations</h3>
              <button @click="showAddModal = true" class="flex items-center gap-1.5 text-xs font-medium text-teal-600 hover:text-teal-700">
                <FeatherIcon name="plus" class="h-3.5 w-3.5" />Add New
              </button>
            </div>
            <div v-if="userIntegrations.length === 0" class="flex flex-col items-center justify-center py-10 text-gray-400">
              <FeatherIcon name="link" class="h-8 w-8 mb-2 opacity-30" />
              <p class="text-xs">No custom integrations yet. Click "Add Integration" to get started.</p>
            </div>
            <div v-else class="divide-y divide-gray-50">
              <div v-for="intg in userIntegrations" :key="intg.id" class="flex items-center gap-4 px-4 py-3 hover:bg-gray-50 transition-colors group">
                <div class="w-8 h-8 rounded-lg bg-teal-50 flex items-center justify-center shrink-0">
                  <FeatherIcon name="link-2" class="h-4 w-4 text-teal-600" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-semibold text-gray-800">{{ intg.name }}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded-full font-medium bg-green-100 text-green-700">Active</span>
                    <span class="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded font-medium">{{ intg.type }}</span>
                  </div>
                  <p class="text-[10px] font-mono text-gray-400 truncate mt-0.5">{{ intg.baseUrl }}</p>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <span class="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-medium">{{ intg.authType }}</span>
                  <button @click="editIntegration(intg)" class="p-1 text-gray-300 hover:text-teal-600 rounded hover:bg-teal-50 transition-colors opacity-0 group-hover:opacity-100">
                    <FeatherIcon name="edit-2" class="h-3.5 w-3.5" />
                  </button>
                  <button @click="deleteTarget = intg; showDeleteIntg = true" class="p-1 text-gray-300 hover:text-red-500 rounded hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100">
                    <FeatherIcon name="trash-2" class="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Webhook Management -->
        <div v-if="activeSection === 'webhooks'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Webhook Management</h2>
              <p class="text-xs text-gray-500 mt-0.5">Register, test, and monitor webhook deliveries</p>
            </div>
            <button @click="showAddWebhook = true" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="plus" class="h-3.5 w-3.5" />Register Webhook
            </button>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-5">
            <div class="bg-white rounded-xl border border-gray-200 p-4">
              <p class="text-xs text-gray-500 mb-3">Delivery Success Rate (7d)</p>
              <div class="flex items-end gap-1 h-16">
                <div v-for="(h,i) in [88,92,95,91,96,98,99]" :key="i" class="flex-1 bg-teal-100 rounded-t" :style="`height:${h}%`" :title="`${h}%`"></div>
              </div>
              <div class="flex justify-between text-[10px] text-gray-400 mt-1">
                <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-4 grid grid-cols-2 gap-3">
              <div class="text-center"><p class="text-2xl font-bold text-teal-600">4,821</p><p class="text-[10px] text-gray-500">Total Sent (7d)</p></div>
              <div class="text-center"><p class="text-2xl font-bold text-green-600">4,763</p><p class="text-[10px] text-gray-500">Delivered</p></div>
              <div class="text-center"><p class="text-2xl font-bold text-amber-500">42</p><p class="text-[10px] text-gray-500">Retried</p></div>
              <div class="text-center"><p class="text-2xl font-bold text-red-500">16</p><p class="text-[10px] text-gray-500">Failed</p></div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
              <h3 class="text-sm font-medium text-gray-700">Registered Webhooks</h3>
            </div>
            <div v-for="wh in webhooks" :key="wh.id" class="border-b border-gray-50 last:border-0 px-4 py-3 hover:bg-gray-50 transition-colors">
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-medium text-gray-800">{{ wh.name }}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded-full" :class="wh.active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">{{ wh.active ? 'Active' : 'Paused' }}</span>
                  </div>
                  <p class="text-[11px] font-mono text-teal-600 mt-0.5 truncate">{{ wh.url }}</p>
                  <div class="flex items-center gap-3 mt-1">
                    <span class="text-[10px] text-gray-400">Events: <span class="text-gray-600">{{ wh.events.join(', ') }}</span></span>
                  </div>
                </div>
                <div class="flex items-center gap-2 ml-4">
                  <span class="text-[10px] text-green-600 font-medium">{{ wh.successRate }}% success</span>
                  <button @click="testWebhook(wh)" class="px-2.5 py-1 text-[10px] font-medium text-teal-700 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors">Test</button>
                  <button @click="showToast('Delivery log opened')" class="px-2.5 py-1 text-[10px] font-medium text-gray-600 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">Logs</button>
                  <button @click="wh.active = !wh.active; showToast(wh.active ? 'Webhook activated' : 'Webhook paused')" class="p-1 text-gray-400 hover:text-gray-600"><FeatherIcon :name="wh.active ? 'pause' : 'play'" class="h-3.5 w-3.5" /></button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. OAuth 2.0 Provider -->
        <div v-if="activeSection === 'oauth'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">OAuth 2.0 Provider</h2>
              <p class="text-xs text-gray-500 mt-0.5">Manage client applications, scopes, and token lifecycle</p>
            </div>
            <button @click="showToast('New OAuth client created')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="plus" class="h-3.5 w-3.5" />Register App
            </button>
          </div>
          <div class="grid grid-cols-3 gap-4 mb-5">
            <div class="bg-white rounded-xl border border-gray-200 p-4 text-center"><p class="text-2xl font-bold text-gray-800">8</p><p class="text-xs text-gray-500 mt-1">Registered Apps</p></div>
            <div class="bg-white rounded-xl border border-gray-200 p-4 text-center"><p class="text-2xl font-bold text-teal-600">1,247</p><p class="text-xs text-gray-500 mt-1">Active Tokens</p></div>
            <div class="bg-white rounded-xl border border-gray-200 p-4 text-center"><p class="text-2xl font-bold text-gray-800">98.4%</p><p class="text-xs text-gray-500 mt-1">Auth Success Rate</p></div>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-100"><h3 class="text-sm font-medium text-gray-700">Client Applications</h3></div>
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Application</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Client ID</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Scopes</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Tokens</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Status</th>
                  <th class="px-4 py-2.5"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in oauthApps" :key="app.id" class="border-b border-gray-50 hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-800">{{ app.name }}</td>
                  <td class="px-4 py-3 font-mono text-gray-500 text-[10px]">{{ app.clientId }}</td>
                  <td class="px-4 py-3">
                    <div class="flex flex-wrap gap-1">
                      <span v-for="s in app.scopes" :key="s" class="px-1.5 py-0.5 bg-teal-50 text-teal-700 rounded text-[10px]">{{ s }}</span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-gray-700">{{ app.tokens }}</td>
                  <td class="px-4 py-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-medium" :class="app.active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">{{ app.active ? 'Active' : 'Inactive' }}</span></td>
                  <td class="px-4 py-3">
                    <button @click="showToast('Tokens revoked')" class="text-[10px] text-red-600 hover:text-red-700">Revoke</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 4. API Documentation -->
        <div v-if="activeSection === 'api-docs'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Open API Documentation</h2>
              <p class="text-xs text-gray-500 mt-0.5">Interactive Swagger docs, playground, and multi-language samples</p>
            </div>
            <div class="flex gap-2">
              <select class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none">
                <option>v2.1.0</option><option>v2.0.0</option><option>v1.5.0</option>
              </select>
              <button @click="showToast('Docs exported')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <FeatherIcon name="download" class="h-3.5 w-3.5" />Export
              </button>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div class="col-span-1 bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div class="px-4 py-3 border-b border-gray-100">
                <input placeholder="Search endpoints..." class="text-xs w-full border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-teal-400" />
              </div>
              <div class="p-2">
                <div v-for="group in apiDocGroups" :key="group.tag" class="mb-1">
                  <button @click="group.open = !group.open" class="w-full flex items-center justify-between px-2 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 rounded-lg">
                    <span>{{ group.tag }}</span>
                    <FeatherIcon :name="group.open ? 'chevron-up' : 'chevron-down'" class="h-3 w-3 text-gray-400" />
                  </button>
                  <div v-if="group.open" class="ml-2 space-y-0.5">
                    <button v-for="ep in group.endpoints" :key="ep.path" @click="selectedDocEp = ep" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-[11px] hover:bg-gray-50 text-left">
                      <span class="w-10 text-[10px] font-bold" :class="methodColor(ep.method)">{{ ep.method }}</span>
                      <span class="font-mono text-gray-600 truncate">{{ ep.path }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-span-2 bg-white rounded-xl border border-gray-200 p-5">
              <div v-if="selectedDocEp">
                <div class="flex items-center gap-2 mb-4">
                  <span class="px-2 py-0.5 rounded text-xs font-bold" :class="methodColor(selectedDocEp.method)">{{ selectedDocEp.method }}</span>
                  <code class="text-sm font-mono text-gray-800">{{ selectedDocEp.path }}</code>
                </div>
                <p class="text-xs text-gray-600 mb-4">{{ selectedDocEp.desc }}</p>
                <div class="mb-4">
                  <p class="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Code Sample</p>
                  <div class="flex gap-2 mb-2">
                    <button v-for="lang in ['cURL','Python','JavaScript','Go']" :key="lang" @click="docLang = lang" class="px-2.5 py-1 text-[10px] rounded-lg font-medium transition-colors" :class="docLang === lang ? 'bg-teal-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">{{ lang }}</button>
                  </div>
                  <div class="bg-gray-900 rounded-lg p-4 text-[11px] font-mono text-green-400 whitespace-pre">{{ codeSample }}</div>
                </div>
                <button @click="showToast('Request sent — 200 OK')" class="px-4 py-2 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
                  Try it out
                </button>
              </div>
              <div v-else class="flex flex-col items-center justify-center h-48 text-gray-400">
                <FeatherIcon name="file-text" class="h-8 w-8 mb-2 opacity-40" />
                <p class="text-xs">Select an endpoint to view docs</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 5. Integration Marketplace -->
        <div v-if="activeSection === 'marketplace'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Integration Marketplace</h2>
              <p class="text-xs text-gray-500 mt-0.5">Browse and install pre-built connectors</p>
            </div>
            <input v-model="marketSearch" placeholder="Search connectors..." class="text-xs border border-gray-200 rounded-lg px-3 py-1.5 w-52 focus:outline-none focus:ring-1 focus:ring-teal-400" />
          </div>
          <div class="flex gap-2 mb-4">
            <button v-for="cat in ['All','Banking','Communication','E-Signature','Analytics','ERP']" :key="cat"
              @click="marketCat = cat"
              class="px-3 py-1 text-xs rounded-full font-medium transition-colors"
              :class="marketCat === cat ? 'bg-teal-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'">
              {{ cat }}
            </button>
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div v-for="conn in filteredConnectors" :key="conn.id" class="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-sm transition-shadow">
              <div class="flex items-start justify-between mb-3">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-lg" :class="conn.bgColor">{{ conn.logo }}</div>
                <div class="flex items-center gap-1">
                  <span v-if="conn.installed" class="text-[10px] px-2 py-0.5 bg-green-100 text-green-700 rounded-full font-medium">Installed</span>
                  <span v-else class="text-[10px] px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full">Available</span>
                </div>
              </div>
              <h4 class="text-sm font-medium text-gray-800">{{ conn.name }}</h4>
              <p class="text-[11px] text-gray-500 mt-1 mb-3">{{ conn.desc }}</p>
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-0.5">
                  <span v-for="i in 5" :key="i" class="text-xs" :class="i <= conn.rating ? 'text-amber-400' : 'text-gray-200'">★</span>
                  <span class="text-[10px] text-gray-400 ml-1">{{ conn.rating }}.0</span>
                </div>
                <button @click="installConnector(conn)" class="px-3 py-1 text-[10px] font-medium rounded-lg transition-colors" :class="conn.installed ? 'text-gray-500 bg-gray-50 border border-gray-200' : 'text-white bg-teal-600 hover:bg-teal-700'">
                  {{ conn.installed ? 'Configure' : 'Install' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 6. WhatsApp Integration -->
        <div v-if="activeSection === 'whatsapp'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">WhatsApp Business API</h2>
              <p class="text-xs text-gray-500 mt-0.5">Send, receive, template messaging, and conversation history</p>
            </div>
            <span class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 rounded-lg">
              <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>Connected
            </span>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Configuration</h3>
              <div class="space-y-3">
                <div v-for="f in waFields" :key="f.label">
                  <label class="text-[11px] text-gray-500 font-medium">{{ f.label }}</label>
                  <input :value="f.value" class="mt-1 w-full text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-teal-400" />
                </div>
              </div>
              <div class="flex gap-2 mt-4">
                <button @click="showToast('WhatsApp config saved')" class="px-4 py-2 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">Save</button>
                <button @click="showToast('Test message sent to +62812-XXXX-XXXX')" class="px-4 py-2 text-xs font-medium text-gray-600 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors">Send Test</button>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Recent Activity</h3>
              <div class="space-y-2">
                <div v-for="log in waLogs" :key="log.time" class="flex items-start gap-2 py-2 border-b border-gray-50 last:border-0">
                  <div class="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0" :class="log.status === 'success' ? 'bg-green-500' : 'bg-red-500'"></div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs text-gray-700">{{ log.event }}</p>
                    <p class="text-[10px] text-gray-400 mt-0.5">{{ log.time }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 7. Email Integration -->
        <div v-if="activeSection === 'email'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Email Integration</h2>
              <p class="text-xs text-gray-500 mt-0.5">SMTP configuration, templates, and delivery tracking</p>
            </div>
            <span class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 rounded-lg">
              <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>Connected
            </span>
          </div>
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">SMTP Configuration</h3>
              <div class="space-y-3">
                <div v-for="f in smtpFields" :key="f.label">
                  <label class="text-[11px] text-gray-500 font-medium">{{ f.label }}</label>
                  <input :type="f.type || 'text'" :value="f.value" class="mt-1 w-full text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-teal-400" />
                </div>
                <div class="flex gap-2 pt-1">
                  <label class="flex items-center gap-1.5 text-xs text-gray-600"><input type="checkbox" checked class="rounded" /> TLS/SSL</label>
                  <label class="flex items-center gap-1.5 text-xs text-gray-600"><input type="checkbox" checked class="rounded" /> DKIM</label>
                  <label class="flex items-center gap-1.5 text-xs text-gray-600"><input type="checkbox" class="rounded" /> DMARC</label>
                </div>
              </div>
              <div class="flex gap-2 mt-4">
                <button @click="showToast('SMTP config saved')" class="px-4 py-2 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">Save</button>
                <button @click="showToast('Test email sent')" class="px-4 py-2 text-xs font-medium text-gray-600 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors">Send Test</button>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Delivery Statistics</h3>
              <div class="space-y-3">
                <div v-for="stat in emailStats" :key="stat.label" class="flex items-center gap-3">
                  <div class="flex-1">
                    <div class="flex justify-between text-xs mb-1">
                      <span class="text-gray-600">{{ stat.label }}</span>
                      <span class="font-medium text-gray-800">{{ stat.value }}%</span>
                    </div>
                    <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div class="h-full rounded-full transition-all" :class="stat.color" :style="`width:${stat.value}%`"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 8. Core Banking Integration -->
        <div v-if="activeSection === 'core-banking'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Core Banking Integration</h2>
              <p class="text-xs text-gray-500 mt-0.5">Account sync, disbursement, repayment, and reconciliation</p>
            </div>
            <button @click="runSync" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="syncing ? 'animate-spin' : ''" />{{ syncing ? 'Syncing...' : 'Sync Now' }}
            </button>
          </div>
          <div class="grid grid-cols-4 gap-4 mb-5">
            <div v-for="s in bankingStats" :key="s.label" class="bg-white rounded-xl border border-gray-200 p-4 text-center">
              <p class="text-xl font-bold" :class="s.color">{{ s.value }}</p>
              <p class="text-[10px] text-gray-500 mt-1">{{ s.label }}</p>
            </div>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
              <h3 class="text-sm font-medium text-gray-700">Sync Jobs</h3>
              <div class="flex gap-2">
                <span v-for="t in ['All','Account','Disbursement','Repayment','Reconciliation']" :key="t"
                  @click="syncFilter = t"
                  class="cursor-pointer px-2 py-0.5 text-[10px] rounded-full" :class="syncFilter === t ? 'bg-teal-600 text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'">
                  {{ t }}
                </span>
              </div>
            </div>
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Job Name</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Type</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Records</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Last Run</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Duration</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="job in syncJobs" :key="job.id" class="border-b border-gray-50 hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-800">{{ job.name }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ job.type }}</td>
                  <td class="px-4 py-3 text-gray-700 font-medium">{{ job.records }}</td>
                  <td class="px-4 py-3 text-gray-500">{{ job.lastRun }}</td>
                  <td class="px-4 py-3 text-gray-500">{{ job.duration }}</td>
                  <td class="px-4 py-3">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-medium" :class="statusClass(job.status)">{{ job.status }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 9. Credit Bureau -->
        <div v-if="activeSection === 'credit-bureau'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Credit Bureau Integration</h2>
              <p class="text-xs text-gray-500 mt-0.5">SLIK OJK, Pefindo connector with on-demand pull and cache policy</p>
            </div>
            <button @click="showToast('Bureau pull initiated')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="search" class="h-3.5 w-3.5" />Pull Report
            </button>
          </div>
          <div class="grid grid-cols-2 gap-4 mb-5">
            <div v-for="bureau in bureaus" :key="bureau.name" class="bg-white rounded-xl border border-gray-200 p-5">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-lg bg-teal-50 flex items-center justify-center"><FeatherIcon name="shield" class="h-4 w-4 text-teal-600" /></div>
                  <span class="text-sm font-medium text-gray-800">{{ bureau.name }}</span>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded-full font-medium" :class="bureau.status === 'Connected' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">{{ bureau.status }}</span>
              </div>
              <div class="grid grid-cols-2 gap-3 text-center">
                <div class="bg-gray-50 rounded-lg p-3"><p class="text-lg font-bold text-gray-800">{{ bureau.pulls }}</p><p class="text-[10px] text-gray-500">Pulls (30d)</p></div>
                <div class="bg-gray-50 rounded-lg p-3"><p class="text-lg font-bold text-gray-800">{{ bureau.cached }}</p><p class="text-[10px] text-gray-500">Cached</p></div>
              </div>
              <div class="mt-3 flex items-center justify-between text-[11px] text-gray-500">
                <span>Cache TTL: {{ bureau.cacheTTL }}</span>
                <button @click="showToast('Cache cleared')" class="text-teal-600 hover:text-teal-700">Clear Cache</button>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-100"><h3 class="text-sm font-medium text-gray-700">Verification History</h3></div>
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Customer</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Bureau</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Score</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Pulled At</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Source</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in bureauHistory" :key="r.id" class="border-b border-gray-50 hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-800">{{ r.customer }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ r.bureau }}</td>
                  <td class="px-4 py-3"><span class="font-semibold" :class="r.score > 700 ? 'text-green-600' : r.score > 500 ? 'text-amber-600' : 'text-red-600'">{{ r.score }}</span></td>
                  <td class="px-4 py-3 text-gray-500">{{ r.pulledAt }}</td>
                  <td class="px-4 py-3"><span class="px-1.5 py-0.5 rounded text-[10px]" :class="r.source === 'Cache' ? 'bg-blue-50 text-blue-700' : 'bg-teal-50 text-teal-700'">{{ r.source }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 10-11. ERP & Accounting -->
        <div v-if="activeSection === 'erp' || activeSection === 'accounting'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">{{ activeSection === 'erp' ? 'ERP Integration' : 'Accounting System Integration' }}</h2>
              <p class="text-xs text-gray-500 mt-0.5">{{ activeSection === 'erp' ? 'SAP / Oracle connector, GL sync, and reconciliation' : 'Accurate / Jurnal / QuickBooks, auto-post journal entries' }}</p>
            </div>
            <button @click="showToast('Sync triggered')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" />Sync GL
            </button>
          </div>
          <div class="grid grid-cols-3 gap-4 mb-5">
            <div v-for="sys in (activeSection === 'erp' ? erpSystems : accountingSystems)" :key="sys.name" class="bg-white rounded-xl border border-gray-200 p-4">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-medium text-gray-800">{{ sys.name }}</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full font-medium" :class="sys.connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">{{ sys.connected ? 'Connected' : 'Not configured' }}</span>
              </div>
              <p class="text-[11px] text-gray-500 mb-3">{{ sys.desc }}</p>
              <button @click="showToast(sys.connected ? 'Configuration opened' : `${sys.name} connection initiated`)" class="w-full py-1.5 text-xs font-medium rounded-lg transition-colors" :class="sys.connected ? 'bg-teal-50 text-teal-700 hover:bg-teal-100' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'">
                {{ sys.connected ? 'Configure' : 'Connect' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 12. E-Signature -->
        <div v-if="activeSection === 'esign'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">E-Signature Integration</h2>
              <p class="text-xs text-gray-500 mt-0.5">Privy / Tilaka / DocuSign with send-for-sign workflow and status callbacks</p>
            </div>
            <button @click="showToast('Document sent for signing')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="send" class="h-3.5 w-3.5" />Send for Sign
            </button>
          </div>
          <div class="grid grid-cols-3 gap-4 mb-5">
            <div v-for="p in esignProviders" :key="p.name" class="bg-white rounded-xl border-2 p-4 cursor-pointer transition-all" :class="esignActive === p.name ? 'border-teal-500 bg-teal-50' : 'border-gray-200 hover:border-teal-200'" @click="esignActive = p.name; showToast(`${p.name} selected as active provider`)">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-semibold text-gray-800">{{ p.name }}</span>
                <span v-if="esignActive === p.name" class="text-[10px] px-2 py-0.5 bg-teal-600 text-white rounded-full">Active</span>
              </div>
              <div class="grid grid-cols-2 gap-2 text-center">
                <div class="bg-white rounded-lg p-2"><p class="text-base font-bold text-gray-800">{{ p.sent }}</p><p class="text-[10px] text-gray-500">Sent</p></div>
                <div class="bg-white rounded-lg p-2"><p class="text-base font-bold text-green-600">{{ p.signed }}</p><p class="text-[10px] text-gray-500">Signed</p></div>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-100"><h3 class="text-sm font-medium text-gray-700">Recent Signing Requests</h3></div>
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Document</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Signatory</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Provider</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Sent</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in esignRequests" :key="r.id" class="border-b border-gray-50 hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-800">{{ r.doc }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ r.signatory }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ r.provider }}</td>
                  <td class="px-4 py-3 text-gray-500">{{ r.sent }}</td>
                  <td class="px-4 py-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-medium" :class="statusClass(r.status)">{{ r.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 13. Dukcapil -->
        <div v-if="activeSection === 'dukcapil'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Dukcapil Integration</h2>
              <p class="text-xs text-gray-500 mt-0.5">e-KTP verification with match score and audit logging</p>
            </div>
            <button @click="showVerifyModal = true" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="user-check" class="h-3.5 w-3.5" />Verify e-KTP
            </button>
          </div>
          <div class="grid grid-cols-4 gap-4 mb-5">
            <div v-for="s in dukcapilStats" :key="s.label" class="bg-white rounded-xl border border-gray-200 p-4 text-center">
              <p class="text-2xl font-bold" :class="s.color">{{ s.value }}</p>
              <p class="text-[10px] text-gray-500 mt-1">{{ s.label }}</p>
            </div>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-100"><h3 class="text-sm font-medium text-gray-700">Verification History</h3></div>
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">NIK</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Name</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Match Score</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Verified At</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Result</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Requested By</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="v in dukcapilHistory" :key="v.id" class="border-b border-gray-50 hover:bg-gray-50">
                  <td class="px-4 py-3 font-mono text-gray-700">{{ v.nik }}</td>
                  <td class="px-4 py-3 font-medium text-gray-800">{{ v.name }}</td>
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                      <div class="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden"><div class="h-full rounded-full" :class="v.score > 90 ? 'bg-green-500' : 'bg-amber-400'" :style="`width:${v.score}%`"></div></div>
                      <span class="font-medium" :class="v.score > 90 ? 'text-green-600' : 'text-amber-600'">{{ v.score }}%</span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-gray-500">{{ v.verifiedAt }}</td>
                  <td class="px-4 py-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-medium" :class="v.result === 'Valid' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">{{ v.result }}</span></td>
                  <td class="px-4 py-3 text-gray-500">{{ v.by }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 14. Payment Gateway -->
        <div v-if="activeSection === 'payment-gw'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Payment Gateway Integration</h2>
              <p class="text-xs text-gray-500 mt-0.5">Midtrans / Xendit / Doku — VA, e-wallet, QRIS, and reconciliation</p>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-4 mb-5">
            <div v-for="gw in paymentGateways" :key="gw.name" class="bg-white rounded-xl border border-gray-200 p-4">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-semibold text-gray-800">{{ gw.name }}</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full font-medium" :class="gw.active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">{{ gw.active ? 'Active' : 'Inactive' }}</span>
              </div>
              <div class="space-y-1.5 mb-3">
                <div v-for="m in gw.methods" :key="m" class="flex items-center gap-1.5">
                  <FeatherIcon name="check" class="h-3 w-3 text-teal-500" />
                  <span class="text-[11px] text-gray-600">{{ m }}</span>
                </div>
              </div>
              <div class="text-center pt-3 border-t border-gray-100">
                <p class="text-base font-bold text-teal-600">{{ gw.volume }}</p>
                <p class="text-[10px] text-gray-500">Volume (30d)</p>
              </div>
              <button @click="showToast(`${gw.name} configured`)" class="mt-3 w-full py-1.5 text-xs font-medium bg-gray-50 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">Configure</button>
            </div>
          </div>
        </div>

        <!-- 15. SMS Gateway -->
        <div v-if="activeSection === 'sms-gw'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">SMS Gateway Integration</h2>
              <p class="text-xs text-gray-500 mt-0.5">OTP delivery, alert campaigns, and delivery tracking</p>
            </div>
            <span class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 rounded-lg">
              <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>Connected
            </span>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Configuration</h3>
              <div class="space-y-3">
                <div v-for="f in smsFields" :key="f.label">
                  <label class="text-[11px] text-gray-500 font-medium">{{ f.label }}</label>
                  <input :value="f.value" class="mt-1 w-full text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-teal-400" />
                </div>
              </div>
              <div class="flex gap-2 mt-4">
                <button @click="showToast('SMS config saved')" class="px-4 py-2 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">Save</button>
                <button @click="showToast('Test SMS sent')" class="px-4 py-2 text-xs font-medium text-gray-600 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors">Send Test SMS</button>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Recent Activity</h3>
              <div class="space-y-2">
                <div v-for="log in smsLogs" :key="log.time" class="flex items-start gap-2 py-2 border-b border-gray-50 last:border-0">
                  <div class="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0" :class="log.status === 'success' ? 'bg-green-500' : 'bg-red-500'"></div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs text-gray-700">{{ log.event }}</p>
                    <p class="text-[10px] text-gray-400 mt-0.5">{{ log.time }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 16. Rate Limiting -->
        <div v-if="activeSection === 'rate-limiting'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">API Rate Limiting</h2>
              <p class="text-xs text-gray-500 mt-0.5">Per-key and endpoint rate limits with partner override settings</p>
            </div>
            <button @click="showToast('Rate limit policy saved')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="save" class="h-3.5 w-3.5" />Save Policy
            </button>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Default Limits</h3>
              <div class="space-y-4">
                <div v-for="limit in rateLimits" :key="limit.label">
                  <div class="flex justify-between text-xs mb-1">
                    <span class="text-gray-600 font-medium">{{ limit.label }}</span>
                    <span class="text-gray-800 font-semibold">{{ limit.value }} req/{{ limit.window }}</span>
                  </div>
                  <input type="range" :min="limit.min" :max="limit.max" v-model="limit.value" class="w-full accent-teal-600" />
                  <div class="flex justify-between text-[10px] text-gray-400"><span>{{ limit.min }}</span><span>{{ limit.max }}</span></div>
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <h3 class="text-sm font-medium text-gray-700">Partner Overrides</h3>
                <button @click="showToast('Override added')" class="text-xs text-teal-600 hover:text-teal-700">+ Add Override</button>
              </div>
              <table class="w-full text-xs">
                <thead class="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Partner</th>
                    <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Limit</th>
                    <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Window</th>
                    <th class="px-4 py-2.5"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="ov in partnerOverrides" :key="ov.partner" class="border-b border-gray-50 hover:bg-gray-50">
                    <td class="px-4 py-3 font-medium text-gray-800">{{ ov.partner }}</td>
                    <td class="px-4 py-3 text-teal-600 font-semibold">{{ ov.limit.toLocaleString() }}</td>
                    <td class="px-4 py-3 text-gray-600">{{ ov.window }}</td>
                    <td class="px-4 py-3"><button @click="showToast('Override removed')" class="text-red-500 hover:text-red-600"><FeatherIcon name="trash-2" class="h-3.5 w-3.5" /></button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 17. API Analytics -->
        <div v-if="activeSection === 'analytics'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">API Analytics</h2>
              <p class="text-xs text-gray-500 mt-0.5">Usage dashboard, endpoint monitoring, error rates, and latency</p>
            </div>
            <div class="flex gap-2">
              <button v-for="p in ['24h','7d','30d']" :key="p" @click="analyticsPeriod = p" class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors" :class="analyticsPeriod === p ? 'bg-teal-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'">{{ p }}</button>
            </div>
          </div>
          <div class="grid grid-cols-4 gap-4 mb-5">
            <div v-for="s in analyticsStats" :key="s.label" class="bg-white rounded-xl border border-gray-200 p-4">
              <p class="text-xs text-gray-500">{{ s.label }}</p>
              <p class="text-2xl font-bold text-gray-800 mt-1">{{ s.value }}</p>
              <p class="text-[10px] mt-1 text-green-600">{{ s.trend }}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Request Volume (24h)</h3>
              <div class="flex items-end gap-1 h-32">
                <div v-for="(v,i) in requestVolume" :key="i" class="flex-1 rounded-t transition-all" :class="i === requestVolume.length-1 ? 'bg-teal-500' : 'bg-teal-100'" :style="`height:${(v/Math.max(...requestVolume))*100}%`" :title="`${v} req`"></div>
              </div>
              <div class="flex justify-between text-[10px] text-gray-400 mt-2">
                <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Top Endpoints by Usage</h3>
              <div class="space-y-3">
                <div v-for="ep in topEndpoints" :key="ep.path" class="flex items-center gap-3">
                  <span class="font-mono text-[10px] text-gray-500 w-36 truncate">{{ ep.path }}</span>
                  <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div class="h-full bg-teal-500 rounded-full" :style="`width:${ep.pct}%`"></div>
                  </div>
                  <span class="text-[10px] font-semibold text-gray-700 w-12 text-right">{{ ep.calls.toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 18. Webhook Reliability -->
        <div v-if="activeSection === 'reliability'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Webhook Reliability</h2>
              <p class="text-xs text-gray-500 mt-0.5">Retry mechanism, dead-letter queue, and delivery guarantee</p>
            </div>
            <button @click="showToast('Manual retry triggered for all failed')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors">
              <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" />Retry All Failed
            </button>
          </div>
          <div class="grid grid-cols-3 gap-4 mb-5">
            <div class="bg-white rounded-xl border border-gray-200 p-4">
              <h3 class="text-sm font-medium text-gray-700 mb-3">Retry Policy</h3>
              <div class="space-y-2 text-xs">
                <div class="flex justify-between"><span class="text-gray-500">Max Retries</span><span class="font-medium text-gray-800">5</span></div>
                <div class="flex justify-between"><span class="text-gray-500">Initial Delay</span><span class="font-medium text-gray-800">5s</span></div>
                <div class="flex justify-between"><span class="text-gray-500">Backoff</span><span class="font-medium text-gray-800">Exponential</span></div>
                <div class="flex justify-between"><span class="text-gray-500">Max Delay</span><span class="font-medium text-gray-800">10min</span></div>
                <div class="flex justify-between"><span class="text-gray-500">Timeout</span><span class="font-medium text-gray-800">30s</span></div>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-4">
              <h3 class="text-sm font-medium text-gray-700 mb-3">Dead Letter Queue</h3>
              <div class="flex items-center justify-center h-16">
                <div class="text-center"><p class="text-3xl font-bold text-red-500">7</p><p class="text-xs text-gray-500 mt-1">Messages in DLQ</p></div>
              </div>
              <div class="grid grid-cols-2 gap-2 mt-3">
                <button @click="showToast('DLQ replayed')" class="py-1.5 text-xs font-medium text-teal-700 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors">Replay All</button>
                <button @click="showToast('DLQ cleared')" class="py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">Clear DLQ</button>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-4">
              <h3 class="text-sm font-medium text-gray-700 mb-3">Delivery Guarantee</h3>
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer"><input type="radio" name="dlvr" checked class="accent-teal-600" /> At-least-once delivery</label>
                <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer"><input type="radio" name="dlvr" class="accent-teal-600" /> Exactly-once (idempotency key)</label>
                <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer"><input type="radio" name="dlvr" class="accent-teal-600" /> Best-effort</label>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-100"><h3 class="text-sm font-medium text-gray-700">Failed Deliveries</h3></div>
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Webhook</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Event</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Attempts</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Last Error</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Next Retry</th>
                  <th class="px-4 py-2.5"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="f in failedDeliveries" :key="f.id" class="border-b border-gray-50 hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-800">{{ f.webhook }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ f.event }}</td>
                  <td class="px-4 py-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700">{{ f.attempts }}/5</span></td>
                  <td class="px-4 py-3 text-red-500 font-mono text-[10px]">{{ f.error }}</td>
                  <td class="px-4 py-3 text-gray-500">{{ f.nextRetry }}</td>
                  <td class="px-4 py-3"><button @click="showToast('Manual retry triggered')" class="px-2.5 py-1 text-[10px] font-medium text-teal-700 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors">Retry</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 19. Sandbox -->
        <div v-if="activeSection === 'sandbox'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">Sandbox Environment</h2>
              <p class="text-xs text-gray-500 mt-0.5">Test API keys, mock external services, and reset sandbox data</p>
            </div>
            <button @click="resetSandbox" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-amber-700 bg-amber-50 border border-amber-200 rounded-lg hover:bg-amber-100 transition-colors">
              <FeatherIcon name="rotate-ccw" class="h-3.5 w-3.5" />Reset Sandbox
            </button>
          </div>
          <div class="grid grid-cols-2 gap-4 mb-5">
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Sandbox API Keys</h3>
              <div class="space-y-3">
                <div v-for="key in sandboxKeys" :key="key.label">
                  <label class="text-[11px] text-gray-500 font-medium">{{ key.label }}</label>
                  <div class="flex gap-2 mt-1">
                    <input :value="key.value" readonly class="flex-1 text-[11px] font-mono bg-gray-50 border border-gray-200 rounded-lg px-3 py-2" />
                    <button @click="showToast('Copied to clipboard')" class="px-2.5 py-1.5 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"><FeatherIcon name="copy" class="h-3.5 w-3.5 text-gray-500" /></button>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl border border-gray-200 p-5">
              <h3 class="text-sm font-medium text-gray-700 mb-4">Mock External Services</h3>
              <div class="space-y-2">
                <div v-for="svc in mockServices" :key="svc.name" class="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <div>
                    <p class="text-xs font-medium text-gray-700">{{ svc.name }}</p>
                    <p class="text-[10px] text-gray-400">{{ svc.desc }}</p>
                  </div>
                  <button @click="svc.enabled = !svc.enabled; showToast(svc.enabled ? `${svc.name} mock enabled` : `${svc.name} mock disabled`)" class="flex items-center gap-1.5">
                    <div class="w-8 h-4 rounded-full transition-colors relative" :class="svc.enabled ? 'bg-teal-500' : 'bg-gray-200'">
                      <div class="w-3 h-3 bg-white rounded-full absolute top-0.5 transition-all" :class="svc.enabled ? 'left-4' : 'left-0.5'"></div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 20. API Audit & Compliance -->
        <div v-if="activeSection === 'audit'">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h2 class="text-base font-semibold text-gray-800">API Audit & Compliance</h2>
              <p class="text-xs text-gray-500 mt-0.5">Immutable API audit log with sensitive data masking and retention policy</p>
            </div>
            <button @click="showToast('Audit report exported')" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <FeatherIcon name="download" class="h-3.5 w-3.5" />Export Report
            </button>
          </div>
          <div class="grid grid-cols-4 gap-4 mb-5">
            <div v-for="s in auditStats" :key="s.label" class="bg-white rounded-xl border border-gray-200 p-4 text-center">
              <p class="text-xl font-bold" :class="s.color">{{ s.value }}</p>
              <p class="text-[10px] text-gray-500 mt-1">{{ s.label }}</p>
            </div>
          </div>
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-100 flex items-center gap-3">
              <h3 class="text-sm font-medium text-gray-700 flex-1">API Audit Log</h3>
              <input placeholder="Search by key or path..." class="text-xs border border-gray-200 rounded-lg px-3 py-1.5 w-52 focus:outline-none focus:ring-1 focus:ring-teal-400" />
              <select class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none"><option>All Methods</option><option>GET</option><option>POST</option><option>DELETE</option></select>
            </div>
            <table class="w-full text-xs">
              <thead class="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Timestamp</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">API Key</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Method</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Path</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Status</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">IP</th>
                  <th class="text-left px-4 py-2.5 text-gray-500 font-medium">Latency</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in auditLogs" :key="log.id" class="border-b border-gray-50 hover:bg-gray-50">
                  <td class="px-4 py-2.5 text-gray-500 font-mono text-[10px]">{{ log.ts }}</td>
                  <td class="px-4 py-2.5 font-mono text-[10px] text-teal-700">{{ log.key }}</td>
                  <td class="px-4 py-2.5"><span class="px-1.5 py-0.5 rounded text-[10px] font-bold" :class="methodColor(log.method)">{{ log.method }}</span></td>
                  <td class="px-4 py-2.5 font-mono text-gray-600">{{ log.path }}</td>
                  <td class="px-4 py-2.5"><span class="font-semibold" :class="log.status < 400 ? 'text-green-600' : 'text-red-500'">{{ log.status }}</span></td>
                  <td class="px-4 py-2.5 text-gray-400 font-mono text-[10px]">{{ log.ip }}</td>
                  <td class="px-4 py-2.5 text-gray-600">{{ log.latency }}ms</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>

    <!-- Add / Edit Integration Modal -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="closeIntgModal">
      <div class="w-full max-w-sm bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-base font-bold text-gray-800">{{ editingIntg ? 'Edit Integration' : 'Add Integration' }}</h3>
          <button @click="closeIntgModal"><FeatherIcon name="x" class="h-4 w-4 text-gray-400" /></button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1.5">Integration Name <span class="text-red-400">*</span></label>
            <input v-model="intgForm.name" type="text" placeholder="e.g. SLIK OJK Connector" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500" @keyup.enter="saveIntegration" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1.5">Base URL <span class="text-red-400">*</span></label>
            <input v-model="intgForm.baseUrl" type="url" placeholder="https://api.example.com" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-teal-500" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1.5">Type</label>
            <select v-model="intgForm.type" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 bg-white">
              <option value="Banking">Banking</option>
              <option value="Communication">Communication</option>
              <option value="E-Signature">E-Signature</option>
              <option value="Analytics">Analytics</option>
              <option value="ERP">ERP</option>
              <option value="Custom">Custom</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1.5">Auth Type</label>
            <select v-model="intgForm.authType" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 bg-white">
              <option value="Bearer Token">Bearer Token</option>
              <option value="API Key">API Key</option>
              <option value="OAuth 2.0">OAuth 2.0</option>
              <option value="None">None</option>
            </select>
          </div>
        </div>
        <div class="mt-5 flex gap-2">
          <button @click="closeIntgModal" class="flex-1 rounded-lg border border-gray-200 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50">Cancel</button>
          <button @click="saveIntegration" :disabled="!intgForm.name || !intgForm.baseUrl" class="flex-1 rounded-lg bg-teal-600 py-2 text-sm font-semibold text-white hover:bg-teal-700 disabled:opacity-50 transition-colors">
            {{ editingIntg ? 'Save Changes' : 'Add Integration' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Integration Confirmation -->
    <div v-if="showDeleteIntg" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showDeleteIntg = false">
      <div class="w-full max-w-sm bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0">
            <FeatherIcon name="trash-2" class="h-5 w-5 text-red-500" />
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-800">Delete Integration</h3>
            <p class="text-xs text-gray-500 mt-0.5">This action cannot be undone.</p>
          </div>
        </div>
        <div class="rounded-lg bg-gray-50 border border-gray-200 px-4 py-3 mb-5">
          <p class="text-xs font-semibold text-gray-800">{{ deleteTarget?.name }}</p>
          <p class="text-[10px] font-mono text-gray-400 mt-0.5">{{ deleteTarget?.baseUrl }}</p>
        </div>
        <div class="flex gap-2">
          <button @click="showDeleteIntg = false; deleteTarget = null" class="flex-1 rounded-lg border border-gray-200 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50">Cancel</button>
          <button @click="deleteIntegration" class="flex-1 rounded-lg bg-red-500 py-2 text-sm font-semibold text-white hover:bg-red-600 transition-colors">Delete</button>
        </div>
      </div>
    </div>

    <!-- Generate Key Modal -->
    <div v-if="showGenKeyModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showGenKeyModal = false">
      <div class="w-full max-w-sm bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-base font-bold text-gray-800">API Key Generated</h3>
          <button @click="showGenKeyModal = false"><FeatherIcon name="x" class="h-4 w-4 text-gray-400" /></button>
        </div>
        <div class="space-y-3">
          <div class="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2.5">
            <p class="text-[10px] text-gray-400 font-semibold uppercase tracking-wide mb-0.5">Key Name</p>
            <p class="text-xs font-semibold text-gray-800">{{ generatedKeyName }}</p>
          </div>
          <div>
            <p class="text-[10px] text-gray-400 font-semibold uppercase tracking-wide mb-1.5">API Key <span class="text-amber-500 normal-case font-normal">(copy now — shown once)</span></p>
            <div class="flex items-center gap-2 rounded-lg bg-teal-50 border border-teal-200 px-3 py-2.5">
              <code class="text-[11px] font-mono text-teal-800 flex-1 break-all select-all">{{ generatedKey }}</code>
              <button @click="copyGeneratedKey" class="shrink-0 text-[10px] font-bold text-teal-700 hover:underline whitespace-nowrap">{{ keyCopied ? '✓ Copied' : 'Copy' }}</button>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="rounded-lg bg-gray-50 border border-gray-200 p-2.5">
              <p class="text-[10px] text-gray-400">Prefix</p>
              <p class="font-semibold text-gray-700 font-mono mt-0.5">sk_live_****</p>
            </div>
            <div class="rounded-lg bg-gray-50 border border-gray-200 p-2.5">
              <p class="text-[10px] text-gray-400">Created</p>
              <p class="font-semibold text-gray-700 mt-0.5">Just now</p>
            </div>
            <div class="rounded-lg bg-gray-50 border border-gray-200 p-2.5">
              <p class="text-[10px] text-gray-400">Expires</p>
              <p class="font-semibold text-gray-700 mt-0.5">Never</p>
            </div>
            <div class="rounded-lg bg-gray-50 border border-gray-200 p-2.5">
              <p class="text-[10px] text-gray-400">Scope</p>
              <p class="font-semibold text-gray-700 mt-0.5">Full Access</p>
            </div>
          </div>
        </div>
        <button @click="showGenKeyModal = false" class="mt-5 w-full rounded-lg border border-gray-200 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50">Close</button>
      </div>
    </div>

    <!-- Toast -->
    <transition enter-active-class="transition duration-200 ease-out" enter-from-class="translate-y-2 opacity-0" enter-to-class="translate-y-0 opacity-100" leave-active-class="transition duration-150 ease-in" leave-from-class="translate-y-0 opacity-100" leave-to-class="translate-y-2 opacity-0">
      <div v-if="toast" class="fixed bottom-6 right-6 bg-gray-900 text-white text-xs px-4 py-2.5 rounded-xl shadow-lg z-50 flex items-center gap-2">
        <FeatherIcon name="check-circle" class="h-3.5 w-3.5 text-teal-400" />{{ toast }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { FeatherIcon } from 'frappe-ui'

// ── Toast ──────────────────────────────────────
const toast = ref('')
let toastTimer = null
function showToast(msg) {
  toast.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = '' }, 2500)
}

// ── Nav ────────────────────────────────────────
const activeSection = ref('api-management')

const apiCoreNav = [
  { id: 'api-management', label: 'API Management', icon: 'terminal' },
  { id: 'webhooks', label: 'Webhook Management', icon: 'zap', badge: '3', badgeColor: 'bg-amber-100 text-amber-700' },
  { id: 'oauth', label: 'OAuth 2.0 Provider', icon: 'lock' },
  { id: 'api-docs', label: 'API Documentation', icon: 'book-open' },
]
const integrationsNav = [
  { id: 'marketplace', label: 'Marketplace', icon: 'grid' },
  { id: 'whatsapp', label: 'WhatsApp', icon: 'message-circle' },
  { id: 'email', label: 'Email', icon: 'mail' },
  { id: 'core-banking', label: 'Core Banking', icon: 'database' },
  { id: 'credit-bureau', label: 'Credit Bureau', icon: 'shield' },
  { id: 'erp', label: 'ERP', icon: 'layers' },
  { id: 'accounting', label: 'Accounting', icon: 'book' },
  { id: 'esign', label: 'E-Signature', icon: 'pen-tool' },
  { id: 'dukcapil', label: 'Dukcapil', icon: 'user-check' },
  { id: 'payment-gw', label: 'Payment Gateway', icon: 'credit-card' },
  { id: 'sms-gw', label: 'SMS Gateway', icon: 'smartphone' },
]
const operationsNav = [
  { id: 'rate-limiting', label: 'Rate Limiting', icon: 'sliders' },
  { id: 'analytics', label: 'API Analytics', icon: 'bar-chart-2' },
  { id: 'reliability', label: 'Webhook Reliability', icon: 'repeat', badge: '7', badgeColor: 'bg-red-100 text-red-700' },
  { id: 'sandbox', label: 'Sandbox', icon: 'box' },
  { id: 'audit', label: 'Audit & Compliance', icon: 'file-text' },
]

// ── API Management ─────────────────────────────
const apiSearch = ref('')
const apiStats = [
  { label: 'Total Endpoints', value: '47', change: '+2 this week', up: true },
  { label: 'Active API Keys', value: '128', change: '+12 this month', up: true },
  { label: 'Calls Today', value: '84.2K', change: '+5.3% vs yesterday', up: true },
  { label: 'Avg Latency', value: '112ms', change: '-8ms vs last week', up: true },
]
const endpoints = ref([
  { id: 1, path: '/api/v2/customers', method: 'GET', version: 'v2', calls: '18,420', latency: 85, enabled: true },
  { id: 2, path: '/api/v2/loans', method: 'GET', version: 'v2', calls: '12,310', latency: 110, enabled: true },
  { id: 3, path: '/api/v2/loans', method: 'POST', version: 'v2', calls: '3,240', latency: 190, enabled: true },
  { id: 4, path: '/api/v2/disbursement', method: 'POST', version: 'v2', calls: '892', latency: 240, enabled: true },
  { id: 5, path: '/api/v1/customers', method: 'GET', version: 'v1', calls: '4,100', latency: 95, enabled: true, deprecate: true },
  { id: 6, path: '/api/v2/credit-score', method: 'POST', version: 'v2', calls: '2,180', latency: 320, enabled: true },
  { id: 7, path: '/api/v2/webhooks', method: 'POST', version: 'v2', calls: '1,450', latency: 72, enabled: false },
  { id: 8, path: '/api/v2/documents', method: 'DELETE', version: 'v2', calls: '210', latency: 130, enabled: true },
])
const filteredEndpoints = computed(() => {
  if (!apiSearch.value) return endpoints.value
  const q = apiSearch.value.toLowerCase()
  return endpoints.value.filter(e => e.path.includes(q) || e.method.toLowerCase().includes(q))
})
function toggleEndpoint(ep) {
  ep.enabled = !ep.enabled
  showToast(ep.enabled ? 'Endpoint enabled' : 'Endpoint disabled')
}
function methodColor(m) {
  return { GET: 'bg-blue-100 text-blue-700', POST: 'bg-green-100 text-green-700', PUT: 'bg-amber-100 text-amber-700', DELETE: 'bg-red-100 text-red-700', PATCH: 'bg-purple-100 text-purple-700' }[m] || 'bg-gray-100 text-gray-600'
}

// ── Webhooks ───────────────────────────────────
const showAddWebhook = ref(false)
const webhooks = ref([
  { id: 1, name: 'Loan Status Notify', url: 'https://partner.bank.co.id/hooks/loan-status', events: ['loan.approved', 'loan.rejected'], successRate: 99.2, active: true },
  { id: 2, name: 'Payment Callback', url: 'https://erp.internal/api/payment-callback', events: ['payment.received', 'payment.failed'], successRate: 97.8, active: true },
  { id: 3, name: 'KYC Verification', url: 'https://kyc.partner.com/webhook', events: ['kyc.completed'], successRate: 95.1, active: true },
  { id: 4, name: 'Document Upload Alert', url: 'https://dms.internal/hooks/upload', events: ['document.uploaded'], successRate: 88.4, active: false },
])
function testWebhook(wh) { showToast(`Test delivery sent to ${wh.name}`) }

// ── OAuth ──────────────────────────────────────
const oauthApps = [
  { id: 1, name: 'Mobile Banking App', clientId: 'mb_cli_x7k2p9q', scopes: ['read:loans', 'read:profile'], tokens: 412, active: true },
  { id: 2, name: 'Partner Portal', clientId: 'pp_cli_m3n8r1s', scopes: ['read:*', 'write:loans'], tokens: 284, active: true },
  { id: 3, name: 'Analytics Dashboard', clientId: 'ad_cli_b5t7v2w', scopes: ['read:reports'], tokens: 89, active: true },
  { id: 4, name: 'Legacy Integration', clientId: 'lg_cli_c1d4e6f', scopes: ['read:customers'], tokens: 12, active: false },
]

// ── API Docs ───────────────────────────────────
const selectedDocEp = ref(null)
const docLang = ref('cURL')
const apiDocGroups = ref([
  { tag: 'Customers', open: true, endpoints: [
    { method: 'GET', path: '/api/v2/customers', desc: 'List all customers with pagination and filtering support.' },
    { method: 'POST', path: '/api/v2/customers', desc: 'Create a new customer record.' },
    { method: 'GET', path: '/api/v2/customers/{id}', desc: 'Retrieve a single customer by ID.' },
  ]},
  { tag: 'Loans', open: false, endpoints: [
    { method: 'GET', path: '/api/v2/loans', desc: 'List loan applications.' },
    { method: 'POST', path: '/api/v2/loans', desc: 'Submit a new loan application.' },
  ]},
  { tag: 'Disbursement', open: false, endpoints: [
    { method: 'POST', path: '/api/v2/disbursement', desc: 'Trigger loan disbursement to borrower account.' },
  ]},
])
const codeSample = computed(() => {
  if (!selectedDocEp.value) return ''
  const ep = selectedDocEp.value
  const samples = {
    'cURL': `curl -X ${ep.method} https://api.summon.id${ep.path} \\\n  -H "Authorization: Bearer sk_live_xxxx" \\\n  -H "Content-Type: application/json"`,
    'Python': `import requests\n\nres = requests.${ep.method.toLowerCase()}(\n  "https://api.summon.id${ep.path}",\n  headers={"Authorization": "Bearer sk_live_xxxx"}\n)\nprint(res.json())`,
    'JavaScript': `const res = await fetch("https://api.summon.id${ep.path}", {\n  method: "${ep.method}",\n  headers: { "Authorization": "Bearer sk_live_xxxx" }\n})\nconst data = await res.json()`,
    'Go': `req, _ := http.NewRequest("${ep.method}",\n  "https://api.summon.id${ep.path}", nil)\nreq.Header.Set("Authorization", "Bearer sk_live_xxxx")\nclient.Do(req)`,
  }
  return samples[docLang.value] || ''
})

// ── Marketplace ────────────────────────────────
const marketSearch = ref('')
const marketCat = ref('All')
const connectors = ref([
  { id: 1, name: 'Midtrans', desc: 'Payment gateway for VA, e-wallet, QRIS', logo: '💳', bgColor: 'bg-blue-50', rating: 5, installed: true, cat: 'Banking' },
  { id: 2, name: 'Privy', desc: 'Digital e-signature platform', logo: '✍️', bgColor: 'bg-purple-50', rating: 5, installed: true, cat: 'E-Signature' },
  { id: 3, name: 'Pefindo', desc: 'Credit scoring and bureau services', logo: '📊', bgColor: 'bg-teal-50', rating: 4, installed: true, cat: 'Banking' },
  { id: 4, name: 'Accurate', desc: 'Accounting and ERP integration', logo: '📒', bgColor: 'bg-green-50', rating: 4, installed: false, cat: 'ERP' },
  { id: 5, name: 'Dukcapil API', desc: 'e-KTP verification service', logo: '🪪', bgColor: 'bg-orange-50', rating: 4, installed: true, cat: 'Banking' },
  { id: 6, name: 'Twilio SMS', desc: 'SMS OTP and campaign messaging', logo: '📱', bgColor: 'bg-red-50', rating: 5, installed: false, cat: 'Communication' },
  { id: 7, name: 'WhatsApp Business', desc: 'Official WhatsApp Business API', logo: '💬', bgColor: 'bg-green-50', rating: 5, installed: true, cat: 'Communication' },
  { id: 8, name: 'DocuSign', desc: 'Enterprise e-signature solution', logo: '📄', bgColor: 'bg-yellow-50', rating: 4, installed: false, cat: 'E-Signature' },
  { id: 9, name: 'Tableau', desc: 'Advanced analytics and BI', logo: '📈', bgColor: 'bg-blue-50', rating: 4, installed: false, cat: 'Analytics' },
])
const filteredConnectors = computed(() => {
  let list = connectors.value
  if (marketCat.value !== 'All') list = list.filter(c => c.cat === marketCat.value)
  if (marketSearch.value) list = list.filter(c => c.name.toLowerCase().includes(marketSearch.value.toLowerCase()))
  return list
})
function installConnector(conn) {
  if (conn.installed) { showToast(`${conn.name} configuration opened`); return }
  conn.installed = true
  showToast(`${conn.name} installed successfully`)
}

// ── WhatsApp ───────────────────────────────────
const waFields = [
  { label: 'Account SID', value: 'WA_SID_xxxxxxxxxxxxxxxx' },
  { label: 'API Token', value: '••••••••••••••••' },
  { label: 'Phone Number ID', value: '+62811-SUMMON-01' },
  { label: 'Webhook URL', value: 'https://api.summon.id/hooks/wa' },
]
const waLogs = [
  { time: '10:42:15', event: 'Message sent to +62812-3456-7890', status: 'success' },
  { time: '10:38:02', event: 'Template approval: loan_reminder', status: 'success' },
  { time: '09:55:44', event: 'Delivery failed: +62813-XXXX', status: 'error' },
]

// ── Email ──────────────────────────────────────
const smtpFields = [
  { label: 'SMTP Host', value: 'smtp.mailgun.org' },
  { label: 'Port', value: '587' },
  { label: 'Username', value: 'noreply@summon.co.id' },
  { label: 'Password', type: 'password', value: 'super-secret-pass' },
  { label: 'From Name', value: 'SUMMON CRM' },
]
const emailStats = [
  { label: 'Delivery Rate', value: 98.2, color: 'bg-teal-500' },
  { label: 'Open Rate', value: 42.5, color: 'bg-blue-500' },
  { label: 'Click Rate', value: 18.3, color: 'bg-purple-500' },
  { label: 'Bounce Rate', value: 1.8, color: 'bg-red-400' },
]

// ── Core Banking ───────────────────────────────
const syncing = ref(false)
const syncFilter = ref('All')
const bankingStats = [
  { label: 'Accounts Synced', value: '12,847', color: 'text-teal-600' },
  { label: 'Disbursements', value: '284', color: 'text-green-600' },
  { label: 'Repayments', value: '1,429', color: 'text-blue-600' },
  { label: 'Recon Errors', value: '3', color: 'text-red-500' },
]
const syncJobs = [
  { id: 1, name: 'Account Balance Sync', type: 'Account', records: '12,847', lastRun: '10 min ago', duration: '2m 14s', status: 'Success' },
  { id: 2, name: 'Loan Disbursement Push', type: 'Disbursement', records: '284', lastRun: '1h ago', duration: '0m 42s', status: 'Success' },
  { id: 3, name: 'Repayment Pull', type: 'Repayment', records: '1,429', lastRun: '30 min ago', duration: '1m 08s', status: 'Success' },
  { id: 4, name: 'Daily Reconciliation', type: 'Reconciliation', records: '14,560', lastRun: '6h ago', duration: '8m 31s', status: 'Warning' },
  { id: 5, name: 'Real-time Account Update', type: 'Account', records: '12', lastRun: '2 min ago', duration: '0m 03s', status: 'Success' },
]
function runSync() {
  syncing.value = true
  setTimeout(() => { syncing.value = false; showToast('Sync completed: 12,847 records updated') }, 2000)
}

// ── Credit Bureau ──────────────────────────────
const bureaus = [
  { name: 'SLIK OJK', status: 'Connected', pulls: 842, cached: 213, cacheTTL: '30 days' },
  { name: 'Pefindo', status: 'Connected', pulls: 428, cached: 97, cacheTTL: '14 days' },
]
const bureauHistory = [
  { id: 1, customer: 'PT Maju Bersama', bureau: 'SLIK OJK', score: 742, pulledAt: '2026-05-24 09:15', source: 'Live' },
  { id: 2, customer: 'Budi Santoso', bureau: 'Pefindo', score: 681, pulledAt: '2026-05-24 08:42', source: 'Cache' },
  { id: 3, customer: 'CV Teknik Jaya', bureau: 'SLIK OJK', score: 524, pulledAt: '2026-05-23 16:30', source: 'Live' },
  { id: 4, customer: 'Rina Marlina', bureau: 'Pefindo', score: 789, pulledAt: '2026-05-23 14:10', source: 'Cache' },
  { id: 5, customer: 'PT Surya Abadi', bureau: 'SLIK OJK', score: 632, pulledAt: '2026-05-23 11:05', source: 'Live' },
]

// ── ERP & Accounting ───────────────────────────
const erpSystems = [
  { name: 'SAP ERP', desc: 'GL sync and master data integration', connected: true },
  { name: 'Oracle Fusion', desc: 'Enterprise financial suite connector', connected: false },
  { name: 'Microsoft Dynamics', desc: 'ERP and CRM unified platform', connected: false },
]
const accountingSystems = [
  { name: 'Accurate', desc: 'Auto-post journal entries, multi-currency', connected: true },
  { name: 'Jurnal', desc: 'Cloud accounting with real-time sync', connected: false },
  { name: 'QuickBooks', desc: 'SMB accounting with reconciliation', connected: false },
]

// ── E-Signature ────────────────────────────────
const esignActive = ref('Privy')
const esignProviders = [
  { name: 'Privy', sent: 284, signed: 271 },
  { name: 'Tilaka', sent: 42, signed: 39 },
  { name: 'DocuSign', sent: 18, signed: 17 },
]
const esignRequests = [
  { id: 1, doc: 'Perjanjian Kredit - PT Maju', signatory: 'Budi Santoso', provider: 'Privy', sent: '2026-05-24 09:00', status: 'Signed' },
  { id: 2, doc: 'Akad Pembiayaan #FA-2024', signatory: 'Rina Marlina', provider: 'Privy', sent: '2026-05-24 08:30', status: 'Pending' },
  { id: 3, doc: 'Addendum Fasilitas', signatory: 'PT Surya Abadi', provider: 'Tilaka', sent: '2026-05-23 16:00', status: 'Signed' },
  { id: 4, doc: 'SKMHT Jaminan', signatory: 'Ahmad Fauzi', provider: 'Privy', sent: '2026-05-23 14:00', status: 'Expired' },
]

// ── Dukcapil ───────────────────────────────────
const showVerifyModal = ref(false)
const dukcapilStats = [
  { label: 'Total Verifications', value: '4,821', color: 'text-teal-600' },
  { label: 'Valid (30d)', value: '4,692', color: 'text-green-600' },
  { label: 'Invalid', value: '129', color: 'text-red-500' },
  { label: 'Avg Match Score', value: '94.2%', color: 'text-gray-800' },
]
const dukcapilHistory = [
  { id: 1, nik: '3174****1234', name: 'Budi Santoso', score: 97, verifiedAt: '2026-05-24 09:10', result: 'Valid', by: 'Ahmad R.' },
  { id: 2, nik: '3201****5678', name: 'Rina Marlina', score: 95, verifiedAt: '2026-05-24 08:45', result: 'Valid', by: 'Siti N.' },
  { id: 3, nik: '3273****9012', name: 'Dian Purnama', score: 62, verifiedAt: '2026-05-23 15:30', result: 'Invalid', by: 'Ahmad R.' },
  { id: 4, nik: '3501****3456', name: 'Hendra Wijaya', score: 99, verifiedAt: '2026-05-23 14:00', result: 'Valid', by: 'Reza K.' },
]

// ── Payment Gateway ────────────────────────────
const paymentGateways = [
  { name: 'Midtrans', active: true, methods: ['Virtual Account', 'e-Wallet (GoPay, OVO)', 'QRIS', 'Credit Card'], volume: 'Rp 4.2M' },
  { name: 'Xendit', active: true, methods: ['Virtual Account', 'Dana', 'LinkAja', 'QRIS'], volume: 'Rp 1.8M' },
  { name: 'Doku', active: false, methods: ['Virtual Account', 'Alfamart', 'Indomaret'], volume: 'Rp 0' },
]

// ── SMS Gateway ────────────────────────────────
const smsFields = [
  { label: 'Provider', value: 'Twilio' },
  { label: 'Account SID', value: 'AC_xxxxxxxxxxxxxxxxxxxx' },
  { label: 'Auth Token', value: '••••••••••••••••' },
  { label: 'Sender ID', value: 'SUMMON' },
]
const smsLogs = [
  { time: '10:40:00', event: 'OTP sent to +62812-XXXX', status: 'success' },
  { time: '10:35:22', event: 'Alert SMS batch: 48 recipients', status: 'success' },
  { time: '09:58:11', event: 'Delivery failed: invalid number', status: 'error' },
]

// ── Rate Limiting ──────────────────────────────
const rateLimits = ref([
  { label: 'Standard (per key)', value: 1000, min: 100, max: 5000, window: 'min' },
  { label: 'Burst Allowance', value: 200, min: 50, max: 1000, window: 'sec' },
  { label: 'Daily Limit', value: 100000, min: 10000, max: 500000, window: 'day' },
])
const partnerOverrides = ref([
  { partner: 'Bank BCA Integration', limit: 10000, window: 'per minute' },
  { partner: 'Partner Portal A', limit: 5000, window: 'per minute' },
  { partner: 'Analytics Service', limit: 50000, window: 'per day' },
])

// ── Analytics ──────────────────────────────────
const analyticsPeriod = ref('24h')
const analyticsStats = [
  { label: 'Total Requests', value: '84,210', trend: '↑ 5.3% vs yesterday' },
  { label: 'Error Rate', value: '0.42%', trend: '↓ 0.08% improved' },
  { label: 'P95 Latency', value: '284ms', trend: '↓ 12ms improved' },
  { label: 'Unique Consumers', value: '128', trend: '↑ 4 new today' },
]
const requestVolume = [1200, 980, 720, 540, 480, 820, 1840, 3200, 4100, 3800, 3500, 3700, 3900, 4200, 4100, 3800, 3600, 3900, 4300, 4500, 4200, 3100, 2100, 1400]
const topEndpoints = [
  { path: '/api/v2/customers', calls: 18420, pct: 100 },
  { path: '/api/v2/loans', calls: 12310, pct: 67 },
  { path: '/api/v2/loans (POST)', calls: 3240, pct: 18 },
  { path: '/api/v2/credit-score', calls: 2180, pct: 12 },
  { path: '/api/v1/customers', calls: 4100, pct: 22 },
]

// ── Reliability ────────────────────────────────
const failedDeliveries = [
  { id: 1, webhook: 'Loan Status Notify', event: 'loan.approved', attempts: 3, error: 'HTTP 503 timeout', nextRetry: '5 min' },
  { id: 2, webhook: 'Payment Callback', event: 'payment.failed', attempts: 5, error: 'Connection refused', nextRetry: 'DLQ' },
  { id: 3, webhook: 'KYC Verification', event: 'kyc.completed', attempts: 2, error: 'HTTP 502', nextRetry: '15 min' },
]

// ── Sandbox ────────────────────────────────────
const sandboxKeys = [
  { label: 'Sandbox Public Key', value: 'pk_sandbox_SUMMONx7k2p9qm3n8r1s' },
  { label: 'Sandbox Secret Key', value: 'sk_sandbox_b5t7v2wc1d4e6fg8h9i0' },
  { label: 'Webhook Secret', value: 'whsec_sandbox_j1k2l3m4n5o6p7q8r9s' },
]
const mockServices = ref([
  { name: 'SLIK OJK Mock', desc: 'Returns test credit bureau data', enabled: true },
  { name: 'Dukcapil Mock', desc: 'Returns test KTP verification', enabled: true },
  { name: 'Core Banking Mock', desc: 'Simulates account and disbursement', enabled: true },
  { name: 'Payment Gateway Mock', desc: 'Fake VA and e-wallet responses', enabled: false },
  { name: 'E-Signature Mock', desc: 'Auto-signs documents in sandbox', enabled: true },
])
function resetSandbox() { showToast('Sandbox data reset to defaults') }

// ── Audit ──────────────────────────────────────
const auditStats = [
  { label: 'API Calls (24h)', value: '84,210', color: 'text-teal-600' },
  { label: 'Flagged Requests', value: '12', color: 'text-amber-600' },
  { label: 'Masked Fields', value: '3,481', color: 'text-gray-800' },
  { label: 'Retention Policy', value: '90 days', color: 'text-gray-800' },
]
const auditLogs = [
  { id: 1, ts: '2026-05-24 10:42:11', key: 'sk_***4j2k', method: 'POST', path: '/api/v2/loans', status: 201, ip: '10.0.0.12', latency: 184 },
  { id: 2, ts: '2026-05-24 10:41:58', key: 'sk_***9m3n', method: 'GET', path: '/api/v2/customers/C-001', status: 200, ip: '10.0.0.8', latency: 72 },
  { id: 3, ts: '2026-05-24 10:41:32', key: 'sk_***7p5q', method: 'GET', path: '/api/v2/loans', status: 200, ip: '172.16.0.4', latency: 95 },
  { id: 4, ts: '2026-05-24 10:40:44', key: 'sk_***2r8s', method: 'DELETE', path: '/api/v2/documents/D-209', status: 403, ip: '192.168.1.55', latency: 43 },
  { id: 5, ts: '2026-05-24 10:39:12', key: 'sk_***4j2k', method: 'POST', path: '/api/v2/disbursement', status: 200, ip: '10.0.0.12', latency: 241 },
  { id: 6, ts: '2026-05-24 10:38:50', key: 'sk_***6t0u', method: 'GET', path: '/api/v2/credit-score', status: 200, ip: '10.0.1.3', latency: 318 },
]

// ── Status helper ──────────────────────────────
function statusClass(s) {
  const m = { 'Success': 'bg-green-100 text-green-700', 'Signed': 'bg-green-100 text-green-700', 'Warning': 'bg-amber-100 text-amber-700', 'Pending': 'bg-amber-100 text-amber-700', 'Error': 'bg-red-100 text-red-700', 'Expired': 'bg-red-100 text-red-700' }
  return m[s] || 'bg-gray-100 text-gray-600'
}

// ── Health check ───────────────────────────────
function runHealthCheck() { showToast('Health check complete: 14 OK, 3 warnings, 1 error') }

// ── Custom Integrations CRUD ───────────────────
const showAddModal = ref(false)
const showDeleteIntg = ref(false)
const editingIntg = ref(null)
const deleteTarget = ref(null)
const intgForm = ref({ name: '', baseUrl: '', type: 'Custom', authType: 'Bearer Token' })

const userIntegrations = ref([
  { id: 1, name: 'BI Reporting Connector', baseUrl: 'https://bi.internal/api', type: 'Analytics', authType: 'Bearer Token' },
  { id: 2, name: 'BPJS Health API', baseUrl: 'https://api.bpjs-kesehatan.go.id', type: 'Custom', authType: 'API Key' },
])

function editIntegration(intg) {
  editingIntg.value = intg
  intgForm.value = { name: intg.name, baseUrl: intg.baseUrl, type: intg.type, authType: intg.authType }
  showAddModal.value = true
}

function saveIntegration() {
  if (!intgForm.value.name || !intgForm.value.baseUrl) return
  if (editingIntg.value) {
    Object.assign(editingIntg.value, intgForm.value)
    showToast('Integration updated')
  } else {
    userIntegrations.value.unshift({ id: Date.now(), ...intgForm.value })
    showToast('Integration added successfully')
  }
  closeIntgModal()
}

function closeIntgModal() {
  showAddModal.value = false
  editingIntg.value = null
  intgForm.value = { name: '', baseUrl: '', type: 'Custom', authType: 'Bearer Token' }
}

function deleteIntegration() {
  if (!deleteTarget.value) return
  userIntegrations.value = userIntegrations.value.filter(i => i.id !== deleteTarget.value.id)
  showToast('Integration deleted')
  showDeleteIntg.value = false
  deleteTarget.value = null
}

// ── Generate Key Modal ──────────────────────────
const showGenKeyModal = ref(false)
const generatedKey = ref('')
const generatedKeyName = ref('')
const keyCopied = ref(false)

function openGenKeyModal() {
  generatedKeyName.value = `Live API Key ${new Date().toLocaleDateString('id-ID')}`
  generatedKey.value = 'sk_live_' + [...Array(32)].map(() => Math.random().toString(36)[2]).join('')
  keyCopied.value = false
  showGenKeyModal.value = true
}

function copyGeneratedKey() {
  navigator.clipboard?.writeText(generatedKey.value).catch(() => {})
  keyCopied.value = true
  setTimeout(() => { keyCopied.value = false }, 2000)
}
</script>
