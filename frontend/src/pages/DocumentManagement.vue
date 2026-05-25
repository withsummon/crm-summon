<template>
  <div class="flex h-full flex-col bg-gray-50 font-sans select-none">
    <LayoutHeader stretch-left>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-[12px] bg-gradient-to-br from-teal-500 to-teal-700">
            <FeatherIcon name="folder" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-ink-gray-9">{{ __("Document Management") }}</h1>
          </div>
        </div>
      </template>
      <template #right-header>
        <button
          @click="showUpload = true"
          class="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 transition-colors"
        >
          <FeatherIcon name="upload" class="h-3.5 w-3.5" />
          {{ __("Upload") }}
        </button>
      </template>
    </LayoutHeader>
    <div class="flex flex-1 min-h-0 overflow-hidden">
    <!-- ── Folder Sidebar ── -->
    <div class="w-56 bg-white border-r border-gray-200 flex flex-col shrink-0">
      <div class="px-4 py-3 border-b border-gray-200">
        <span class="text-sm font-bold text-gray-800">{{ __("Documents") }}</span>
      </div>

      <div class="flex-1 overflow-y-auto p-2">
        <!-- Quick access -->
        <div class="mb-2 space-y-0.5">
          <button
            v-for="qa in quickAccess"
            :key="qa.id"
            @click="
              activeFolder = qa.id;
              activeView = 'docs';
            "
            class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-all"
            :class="
              activeFolder === qa.id
                ? 'bg-teal-50 text-teal-700 font-semibold'
                : 'text-gray-600 hover:bg-gray-50'
            "
          >
            <FeatherIcon :name="qa.icon" class="h-3.5 w-3.5 shrink-0" />
            <span class="truncate">{{ qa.label }}</span>
            <span
              v-if="qa.count"
              class="ml-auto text-[9px] bg-teal-100 text-teal-700 rounded-full px-1.5 font-bold"
              >{{ qa.count }}</span
            >
          </button>
        </div>

        <div class="border-t border-gray-100 pt-2 mb-1">
          <p
            class="px-3 text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1"
          >
            {{ __("Folders") }}
          </p>
        </div>

        <!-- Folder tree -->
        <div class="space-y-0.5">
          <FolderNode
            v-for="f in folderTree"
            :key="f.id"
            :node="f"
            :active="activeFolder"
            @select="
              activeFolder = $event;
              activeView = 'docs';
            "
          />
        </div>
      </div>

      <!-- Storage quota -->
      <div class="p-3 border-t border-gray-200">
        <div class="flex justify-between text-[10px] text-gray-500 mb-1.5">
          <span>Storage</span
          ><span class="font-semibold text-gray-700"
            >{{ storageUsed }} / {{ storageTotal }}</span
          >
        </div>
        <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full"
            :class="storagePercent >= 80 ? 'bg-amber-400' : 'bg-teal-500'"
            :style="{ width: storagePercent + '%' }"
          />
        </div>
        <p
          v-if="storagePercent >= 80"
          class="text-[9px] text-amber-600 mt-1 font-semibold"
        >
          ⚠ {{ storagePercent }}% used — approaching limit
        </p>
      </div>
    </div>

    <!-- ── Main Content ── -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Top Bar -->
      <div
        class="bg-white border-b border-gray-200 px-5 py-3 flex items-center gap-3 shrink-0 shadow-sm"
      >
        <!-- Breadcrumb -->
        <div class="flex items-center gap-1 text-xs text-gray-500 min-w-0 flex-1">
          <FeatherIcon name="folder" class="h-3.5 w-3.5 text-teal-500 shrink-0" />
          <span v-for="(crumb, i) in breadcrumb" :key="i" class="flex items-center gap-1">
            <span v-if="i > 0" class="text-gray-300">/</span>
            <button
              @click="crumb.folderId && (activeFolder = crumb.folderId)"
              class="hover:text-teal-600 transition-colors"
              :class="i === breadcrumb.length - 1 ? 'font-semibold text-gray-800' : ''"
            >
              {{ crumb.label }}
            </button>
          </span>
        </div>

        <!-- Search -->
        <div class="relative w-56">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search documents, OCR text...')"
            class="w-full pl-8 pr-3 py-1.5 bg-gray-100 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
          />
          <FeatherIcon
            name="search"
            class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400"
          />
        </div>

        <!-- View tabs -->
        <div class="flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            v-for="v in views"
            :key="v.id"
            @click="activeView = v.id"
            class="px-3 py-1.5 text-xs font-medium transition-colors flex items-center gap-1.5"
            :class="
              activeView === v.id
                ? 'bg-teal-600 text-white'
                : 'bg-white text-gray-500 hover:bg-gray-50'
            "
          >
            <FeatherIcon :name="v.icon" class="h-3 w-3" />{{ v.label }}
          </button>
        </div>
      </div>

      <!-- Filter Bar (docs view) -->
      <div
        v-if="activeView === 'docs'"
        class="bg-white border-b border-gray-100 px-5 py-2 flex items-center gap-3 shrink-0"
      >
        <div class="flex gap-2">
          <button
            v-for="f in typeFilters"
            :key="f.id"
            @click="toggleTypeFilter(f.id)"
            class="rounded-full px-3 py-1 text-[11px] font-semibold transition-colors border"
            :class="
              activeTypeFilters.includes(f.id)
                ? 'bg-teal-600 text-white border-teal-600'
                : 'bg-white text-gray-500 border-gray-200 hover:border-teal-300'
            "
          >
            {{ f.label }}
          </button>
        </div>
        <div class="ml-auto flex items-center gap-2 text-[11px] text-gray-500">
          <button
            @click="sortBy = 'name'"
            :class="
              sortBy === 'name' ? 'text-teal-600 font-semibold' : 'hover:text-gray-700'
            "
          >
            Name
          </button>
          <button
            @click="sortBy = 'date'"
            :class="
              sortBy === 'date' ? 'text-teal-600 font-semibold' : 'hover:text-gray-700'
            "
          >
            Date
          </button>
          <button
            @click="sortBy = 'size'"
            :class="
              sortBy === 'size' ? 'text-teal-600 font-semibold' : 'hover:text-gray-700'
            "
          >
            Size
          </button>
          <span class="text-gray-300">|</span>
          <span>{{ filteredDocs.length }} files</span>
        </div>
      </div>

      <!-- ── DOCUMENTS VIEW ── -->
      <div v-if="activeView === 'docs'" class="flex flex-1 min-h-0 overflow-hidden">
        <!-- Doc List -->
        <div
          class="flex-1 overflow-y-auto"
          :class="selectedDoc ? 'border-r border-gray-200' : ''"
        >
          <table class="w-full text-xs">
            <thead class="bg-gray-50 border-b border-gray-200 sticky top-0">
              <tr>
                <th class="px-4 py-2.5 text-left text-gray-600 w-8">
                  <input type="checkbox" class="rounded" @change="toggleAll" />
                </th>
                <th class="px-4 py-2.5 text-left text-gray-600">{{ __("Document") }}</th>
                <th class="px-4 py-2.5 text-center text-gray-600">{{ __("Type") }}</th>
                <th class="px-4 py-2.5 text-center text-gray-600">{{ __("OCR") }}</th>
                <th class="px-4 py-2.5 text-center text-gray-600">
                  {{ __("AI Class") }}
                </th>
                <th class="px-4 py-2.5 text-right text-gray-600">{{ __("Size") }}</th>
                <th class="px-4 py-2.5 text-center text-gray-600">{{ __("Version") }}</th>
                <th class="px-4 py-2.5 text-center text-gray-600">{{ __("Expiry") }}</th>
                <th class="px-4 py-2.5 text-center text-gray-600">{{ __("Status") }}</th>
                <th class="px-4 py-2.5 text-center text-gray-600"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr
                v-for="doc in filteredDocs"
                :key="doc.id"
                @click="selectedDoc = doc"
                class="cursor-pointer hover:bg-gray-50 transition-colors"
                :class="selectedDoc?.id === doc.id ? 'bg-teal-50' : ''"
              >
                <td class="px-4 py-3" @click.stop>
                  <input type="checkbox" v-model="doc.selected" class="rounded" />
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2.5">
                    <div
                      class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                      :class="fileIconBg(doc.ext)"
                    >
                      <span
                        class="text-[9px] font-black"
                        :class="fileIconColor(doc.ext)"
                        >{{ doc.ext.toUpperCase() }}</span
                      >
                    </div>
                    <div class="min-w-0">
                      <div class="font-semibold text-gray-800 truncate max-w-[180px]">
                        {{ doc.name }}
                      </div>
                      <div class="text-[10px] text-gray-400">
                        {{ doc.customer }} · {{ doc.uploaded }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 text-center">
                  <span
                    class="rounded px-2 py-0.5 text-[9px] font-bold"
                    :class="docTypeBadge(doc.doc_type)"
                    >{{ doc.doc_type }}</span
                  >
                </td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1">
                    <div
                      class="w-2 h-2 rounded-full"
                      :class="
                        doc.ocr === 'Done'
                          ? 'bg-green-500'
                          : doc.ocr === 'Processing'
                          ? 'bg-amber-400'
                          : 'bg-gray-200'
                      "
                    />
                    <span
                      class="text-[10px]"
                      :class="doc.ocr === 'Done' ? 'text-green-600' : 'text-gray-400'"
                      >{{ doc.ocr }}</span
                    >
                  </div>
                </td>
                <td class="px-4 py-3 text-center">
                  <span
                    v-if="doc.ai_class"
                    class="text-[10px] text-teal-600 font-semibold"
                    >{{ doc.ai_class }}</span
                  >
                  <span v-else class="text-[10px] text-gray-300">—</span>
                </td>
                <td class="px-4 py-3 text-right font-mono text-gray-500">
                  {{ doc.size }}
                </td>
                <td class="px-4 py-3 text-center">
                  <span class="text-[10px] text-gray-500">v{{ doc.version }}</span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span
                    v-if="doc.expiry"
                    class="text-[10px] font-semibold"
                    :class="expiryClass(doc.expiry)"
                    >{{ doc.expiry }}</span
                  >
                  <span v-else class="text-[10px] text-gray-300">—</span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span
                    class="rounded-full px-2 py-0.5 text-[9px] font-semibold"
                    :class="statusBadge(doc.status)"
                    >{{ doc.status }}</span
                  >
                </td>
                <td class="px-4 py-3 text-center" @click.stop>
                  <div class="flex items-center justify-center gap-1">
                    <button
                      @click="previewDoc(doc)"
                      class="p-1 rounded hover:bg-teal-100 text-gray-400 hover:text-teal-600 transition-colors"
                    >
                      <FeatherIcon name="eye" class="h-3.5 w-3.5" />
                    </button>
                    <button
                      @click="shareDoc(doc)"
                      class="p-1 rounded hover:bg-teal-100 text-gray-400 hover:text-teal-600 transition-colors"
                    >
                      <FeatherIcon name="share-2" class="h-3.5 w-3.5" />
                    </button>
                    <button
                      @click="downloadDoc(doc)"
                      class="p-1 rounded hover:bg-teal-100 text-gray-400 hover:text-teal-600 transition-colors"
                    >
                      <FeatherIcon name="download" class="h-3.5 w-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div
            v-if="filteredDocs.length === 0"
            class="flex flex-col items-center justify-center py-16 text-gray-400"
          >
            <FeatherIcon name="folder-open" class="h-10 w-10 text-gray-200 mb-3" />
            <p class="text-sm font-medium">{{ __("No documents found") }}</p>
          </div>

          <!-- Bulk actions bar -->
          <div
            v-if="selectedCount > 0"
            class="sticky bottom-0 bg-white border-t border-gray-200 px-5 py-2.5 flex items-center gap-3 shadow-lg"
          >
            <span class="text-xs font-semibold text-gray-700"
              >{{ selectedCount }} selected</span
            >
            <button
              class="text-xs text-teal-600 font-semibold hover:underline flex items-center gap-1"
            >
              <FeatherIcon name="download" class="h-3.5 w-3.5" />Download ZIP
            </button>
            <button
              class="text-xs text-teal-600 font-semibold hover:underline flex items-center gap-1"
            >
              <FeatherIcon name="tag" class="h-3.5 w-3.5" />Bulk Tag
            </button>
            <button
              class="text-xs text-red-500 font-semibold hover:underline flex items-center gap-1"
            >
              <FeatherIcon name="trash-2" class="h-3.5 w-3.5" />Delete
            </button>
            <button
              @click="clearSelection"
              class="ml-auto text-xs text-gray-400 hover:text-gray-600"
            >
              ✕ Clear
            </button>
          </div>
        </div>

        <!-- ── Document Detail Panel ── -->
        <div
          v-if="selectedDoc"
          class="w-80 shrink-0 bg-white flex flex-col overflow-hidden"
        >
          <div
            class="px-4 py-3 border-b border-gray-200 flex items-center justify-between"
          >
            <span class="text-xs font-bold text-gray-800">{{
              __("Document Details")
            }}</span>
            <button @click="selectedDoc = null" class="text-gray-400 hover:text-gray-600">
              <FeatherIcon name="x" class="h-4 w-4" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto">
            <!-- Preview area -->
            <div
              class="h-40 bg-gray-100 flex items-center justify-center border-b border-gray-200 relative cursor-pointer"
              @click="showPreviewModal = true"
            >
              <div class="text-center">
                <div
                  class="w-14 h-14 rounded-xl mx-auto flex items-center justify-center mb-2"
                  :class="fileIconBg(selectedDoc.ext)"
                >
                  <span
                    class="text-base font-black"
                    :class="fileIconColor(selectedDoc.ext)"
                    >{{ selectedDoc.ext.toUpperCase() }}</span
                  >
                </div>
                <div class="text-xs text-gray-500">{{ __("Click to preview") }}</div>
              </div>
              <div class="absolute top-2 right-2 flex gap-1">
                <button
                  @click.stop="downloadDoc(selectedDoc)"
                  class="w-7 h-7 rounded-lg bg-white border border-gray-200 flex items-center justify-center hover:bg-teal-50 transition-colors shadow-sm"
                >
                  <FeatherIcon name="download" class="h-3.5 w-3.5 text-teal-600" />
                </button>
                <button
                  @click.stop="shareDoc(selectedDoc)"
                  class="w-7 h-7 rounded-lg bg-white border border-gray-200 flex items-center justify-center hover:bg-teal-50 transition-colors shadow-sm"
                >
                  <FeatherIcon name="share-2" class="h-3.5 w-3.5 text-teal-600" />
                </button>
              </div>
            </div>

            <!-- Tabs inside panel -->
            <div class="flex border-b border-gray-200 bg-white sticky top-0 z-10">
              <button
                v-for="t in panelTabs"
                :key="t.id"
                @click="panelTab = t.id"
                class="flex-1 py-2 text-[10px] font-semibold transition-colors border-b-2"
                :class="
                  panelTab === t.id
                    ? 'border-teal-600 text-teal-600'
                    : 'border-transparent text-gray-400 hover:text-gray-600'
                "
              >
                {{ t.label }}
              </button>
            </div>

            <!-- Info tab -->
            <div v-if="panelTab === 'info'" class="p-4 space-y-3">
              <div>
                <p
                  class="text-[10px] text-gray-400 font-semibold uppercase tracking-wide mb-2"
                >
                  {{ __("File Info") }}
                </p>
                <div class="space-y-2">
                  <div
                    v-for="row in docInfo"
                    :key="row.label"
                    class="flex justify-between text-xs"
                  >
                    <span class="text-gray-500">{{ row.label }}</span>
                    <span class="font-semibold text-gray-800 text-right ml-2">{{
                      row.value
                    }}</span>
                  </div>
                </div>
              </div>
              <!-- Tags -->
              <div>
                <p
                  class="text-[10px] text-gray-400 font-semibold uppercase tracking-wide mb-2"
                >
                  {{ __("Tags") }}
                </p>
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="tag in selectedDoc.tags"
                    :key="tag"
                    class="rounded-full bg-teal-50 border border-teal-200 text-teal-700 text-[10px] px-2.5 py-0.5 font-medium"
                    >{{ tag }}</span
                  >
                  <button
                    class="rounded-full border border-dashed border-gray-300 text-gray-400 text-[10px] px-2 py-0.5 hover:border-teal-400 hover:text-teal-600 transition-colors"
                  >
                    + Add
                  </button>
                </div>
              </div>
              <!-- Expiry -->
              <div
                v-if="selectedDoc.expiry"
                class="rounded-lg p-3 border"
                :class="
                  isExpiringSoon(selectedDoc.expiry)
                    ? 'bg-amber-50 border-amber-200'
                    : 'bg-gray-50 border-gray-200'
                "
              >
                <div class="flex items-center gap-2">
                  <FeatherIcon
                    name="clock"
                    class="h-3.5 w-3.5 shrink-0"
                    :class="
                      isExpiringSoon(selectedDoc.expiry)
                        ? 'text-amber-500'
                        : 'text-gray-400'
                    "
                  />
                  <div>
                    <div
                      class="text-[10px] font-semibold"
                      :class="
                        isExpiringSoon(selectedDoc.expiry)
                          ? 'text-amber-700'
                          : 'text-gray-700'
                      "
                    >
                      Expires {{ selectedDoc.expiry }}
                    </div>
                    <div
                      class="text-[9px]"
                      :class="
                        isExpiringSoon(selectedDoc.expiry)
                          ? 'text-amber-600'
                          : 'text-gray-400'
                      "
                    >
                      {{
                        isExpiringSoon(selectedDoc.expiry)
                          ? "Reminder sent H-14"
                          : "Renewal reminder active"
                      }}
                    </div>
                  </div>
                </div>
              </div>
              <!-- AI Classification -->
              <div
                v-if="selectedDoc.ai_class"
                class="rounded-lg bg-teal-50 border border-teal-200 p-3"
              >
                <div class="flex items-center gap-2 mb-1.5">
                  <FeatherIcon name="cpu" class="h-3.5 w-3.5 text-teal-600" />
                  <span
                    class="text-[10px] font-bold text-teal-700 uppercase tracking-wide"
                    >AI Classification</span
                  >
                </div>
                <div class="text-xs font-bold text-teal-800">
                  {{ selectedDoc.ai_class }}
                </div>
                <div class="text-[10px] text-teal-600 mt-0.5">
                  Confidence: {{ selectedDoc.ai_conf }}% ·
                  <button class="underline hover:text-teal-800">Override</button>
                </div>
                <div class="text-[10px] text-teal-500 mt-1">
                  Suggested folder: {{ selectedDoc.ai_folder }}
                </div>
              </div>
            </div>

            <!-- OCR tab -->
            <div v-if="panelTab === 'ocr'" class="p-4">
              <div v-if="selectedDoc.ocr === 'Done'" class="space-y-3">
                <div class="flex items-center justify-between mb-2">
                  <span
                    class="text-[10px] font-semibold text-gray-700 uppercase tracking-wide"
                    >Extracted Text</span
                  >
                  <span
                    class="text-[9px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold"
                    >Confidence: 94%</span
                  >
                </div>
                <div
                  class="rounded-lg bg-gray-50 border border-gray-200 p-3 text-[10px] text-gray-700 font-mono leading-relaxed max-h-48 overflow-y-auto"
                >
                  {{ selectedDoc.ocr_text || demoOcrText }}
                </div>
                <div class="space-y-2">
                  <div
                    v-for="field in ocrFields"
                    :key="field.key"
                    class="flex items-center justify-between rounded bg-white border border-gray-200 px-2.5 py-2"
                  >
                    <span class="text-[10px] text-gray-500">{{ field.key }}</span>
                    <div class="flex items-center gap-2">
                      <span class="text-[10px] font-semibold text-gray-800">{{
                        field.value
                      }}</span>
                      <span
                        class="text-[9px] rounded px-1.5 font-bold"
                        :class="
                          field.conf >= 90
                            ? 'bg-green-100 text-green-600'
                            : 'bg-amber-100 text-amber-600'
                        "
                        >{{ field.conf }}%</span
                      >
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="flex flex-col items-center py-8 text-gray-400">
                <FeatherIcon name="cpu" class="h-8 w-8 text-gray-200 mb-2" />
                <p class="text-xs">OCR not yet processed</p>
                <button
                  @click="
                    selectedDoc.ocr = 'Processing';
                    setTimeout(() => (selectedDoc.ocr = 'Done'), 1500);
                  "
                  class="mt-3 text-xs bg-teal-600 text-white px-3 py-1.5 rounded-lg font-semibold hover:bg-teal-700 transition-colors"
                >
                  Run OCR
                </button>
              </div>
            </div>

            <!-- Versions tab -->
            <div v-if="panelTab === 'versions'" class="p-4">
              <div class="space-y-2">
                <div
                  v-for="v in docVersions"
                  :key="v.v"
                  class="flex items-center gap-3 p-3 rounded-lg border"
                  :class="
                    v.v === selectedDoc.version
                      ? 'bg-teal-50 border-teal-200'
                      : 'bg-white border-gray-200'
                  "
                >
                  <div
                    class="w-7 h-7 rounded-full flex items-center justify-center shrink-0"
                    :class="
                      v.v === selectedDoc.version
                        ? 'bg-teal-600 text-white'
                        : 'bg-gray-100 text-gray-500'
                    "
                  >
                    <span class="text-[10px] font-bold">v{{ v.v }}</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-[10px] font-semibold text-gray-800">{{ v.by }}</div>
                    <div class="text-[9px] text-gray-400">
                      {{ v.date }} · {{ v.note }}
                    </div>
                  </div>
                  <div class="flex items-center gap-1 shrink-0">
                    <span
                      v-if="v.v === selectedDoc.version"
                      class="text-[9px] bg-teal-100 text-teal-700 px-1.5 rounded font-bold"
                      >Active</span
                    >
                    <button
                      v-else
                      class="text-[9px] text-teal-600 hover:underline font-semibold"
                    >
                      Restore
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Audit tab -->
            <div v-if="panelTab === 'audit'" class="p-4">
              <div class="space-y-2">
                <div v-for="a in docAudit" :key="a.id" class="flex gap-2.5">
                  <div
                    class="w-6 h-6 rounded-full shrink-0 flex items-center justify-center"
                    :class="auditColor(a.action)"
                  >
                    <FeatherIcon :name="auditIcon(a.action)" class="h-3 w-3 text-white" />
                  </div>
                  <div class="flex-1 min-w-0 pb-3 border-b border-gray-100">
                    <div class="text-[10px] font-semibold text-gray-800">
                      {{ a.user }}
                      <span class="font-normal text-gray-500">{{ a.action }}</span>
                    </div>
                    <div class="text-[9px] text-gray-400">{{ a.time }}</div>
                    <div v-if="a.note" class="text-[9px] text-gray-500 italic mt-0.5">
                      {{ a.note }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── HEALTH DASHBOARD ── -->
      <div v-if="activeView === 'health'" class="flex-1 overflow-y-auto p-5 space-y-5">
        <!-- KPI Row -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            v-for="kpi in healthKpis"
            :key="kpi.label"
            class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 text-center"
          >
            <div
              class="w-9 h-9 rounded-xl mx-auto mb-3 flex items-center justify-center"
              :class="kpi.bg"
            >
              <FeatherIcon :name="kpi.icon" class="h-5 w-5" :class="kpi.iconColor" />
            </div>
            <div class="text-2xl font-black" :class="kpi.color">{{ kpi.value }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ kpi.label }}</div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Completeness by customer -->
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
            <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wide mb-4">
              {{ __("Completeness by Customer") }}
            </h4>
            <div class="space-y-3">
              <div v-for="c in completeness" :key="c.name">
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="font-medium text-gray-700 truncate">{{ c.name }}</span>
                  <span
                    class="font-bold shrink-0 ml-2"
                    :class="
                      c.pct >= 80
                        ? 'text-teal-600'
                        : c.pct >= 60
                        ? 'text-amber-600'
                        : 'text-red-500'
                    "
                    >{{ c.pct }}%</span
                  >
                </div>
                <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all"
                    :class="
                      c.pct >= 80
                        ? 'bg-teal-500'
                        : c.pct >= 60
                        ? 'bg-amber-400'
                        : 'bg-red-400'
                    "
                    :style="{ width: c.pct + '%' }"
                  />
                </div>
                <div class="flex justify-between text-[9px] text-gray-400 mt-0.5">
                  <span>{{ c.received }}/{{ c.total }} docs</span>
                  <span v-if="c.missing > 0" class="text-red-400 font-semibold"
                    >{{ c.missing }} missing</span
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- Expiring soon -->
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wide">
                {{ __("Expiring Documents") }}
              </h4>
              <button class="text-[10px] text-teal-600 font-semibold hover:underline">
                {{ __("Send All Reminders") }}
              </button>
            </div>
            <div class="space-y-2">
              <div
                v-for="ex in expiringDocs"
                :key="ex.id"
                class="flex items-center gap-3 p-3 rounded-lg border"
                :class="
                  ex.days <= 14
                    ? 'bg-red-50 border-red-200'
                    : 'bg-amber-50 border-amber-200'
                "
              >
                <FeatherIcon
                  name="alert-circle"
                  class="h-4 w-4 shrink-0"
                  :class="ex.days <= 14 ? 'text-red-500' : 'text-amber-500'"
                />
                <div class="flex-1 min-w-0">
                  <div class="text-xs font-semibold text-gray-800 truncate">
                    {{ ex.name }}
                  </div>
                  <div class="text-[10px] text-gray-500">{{ ex.customer }}</div>
                </div>
                <div class="text-right shrink-0">
                  <div
                    class="text-xs font-bold"
                    :class="ex.days <= 14 ? 'text-red-600' : 'text-amber-600'"
                  >
                    {{ ex.days }}d
                  </div>
                  <button class="text-[9px] text-teal-600 hover:underline">Remind</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Missing docs by type -->
        <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wide mb-4">
            {{ __("Missing by Document Type") }}
          </h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div
              v-for="mt in missingTypes"
              :key="mt.type"
              class="text-center p-4 rounded-xl bg-gray-50 border border-gray-200"
            >
              <div class="text-2xl font-black text-red-500">{{ mt.count }}</div>
              <div class="text-xs text-gray-600 mt-1 font-medium">{{ mt.type }}</div>
              <button
                class="mt-2 text-[10px] text-teal-600 hover:underline font-semibold"
              >
                Request All
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ── AUDIT LOG ── -->
      <div v-if="activeView === 'audit'" class="flex-1 overflow-y-auto p-5">
        <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div
            class="px-5 py-3 border-b border-gray-100 flex items-center justify-between"
          >
            <h4 class="text-xs font-bold text-gray-700 uppercase tracking-wide">
              {{ __("System Audit Log") }}
            </h4>
            <button
              class="text-xs text-teal-600 font-semibold flex items-center gap-1 hover:underline"
            >
              <FeatherIcon name="download" class="h-3.5 w-3.5" />{{ __("Export CSV") }}
            </button>
          </div>
          <table class="w-full text-xs">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2.5 text-left text-gray-600">{{ __("Time") }}</th>
                <th class="px-4 py-2.5 text-left text-gray-600">{{ __("User") }}</th>
                <th class="px-4 py-2.5 text-left text-gray-600">{{ __("Action") }}</th>
                <th class="px-4 py-2.5 text-left text-gray-600">{{ __("Document") }}</th>
                <th class="px-4 py-2.5 text-left text-gray-600">
                  {{ __("IP Address") }}
                </th>
                <th class="px-4 py-2.5 text-center text-gray-600">{{ __("Result") }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-mono text-gray-500">{{ log.time }}</td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div
                      class="w-5 h-5 rounded-full bg-teal-600 text-white flex items-center justify-center text-[9px] font-black"
                    >
                      {{ log.user[0] }}
                    </div>
                    <span class="text-gray-700">{{ log.user }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span
                    class="rounded px-2 py-0.5 text-[9px] font-bold"
                    :class="auditActionBadge(log.action)"
                    >{{ log.action }}</span
                  >
                </td>
                <td class="px-4 py-3 text-gray-700 truncate max-w-[180px]">
                  {{ log.doc }}
                </td>
                <td class="px-4 py-3 font-mono text-gray-500">{{ log.ip }}</td>
                <td class="px-4 py-3 text-center">
                  <span
                    class="rounded-full px-2 py-0.5 text-[9px] font-semibold"
                    :class="
                      log.result === 'Success'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-600'
                    "
                    >{{ log.result }}</span
                  >
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── TEMPLATES ── -->
      <div v-if="activeView === 'templates'" class="flex-1 overflow-y-auto p-5">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="tpl in templates"
            :key="tpl.id"
            class="bg-white rounded-xl border border-gray-200 shadow-sm p-5 hover:border-teal-300 transition-colors"
          >
            <div class="flex items-start justify-between mb-3">
              <div
                class="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center"
              >
                <FeatherIcon name="file-text" class="h-5 w-5 text-teal-600" />
              </div>
              <span
                class="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-semibold"
                >v{{ tpl.version }}</span
              >
            </div>
            <h4 class="text-sm font-bold text-gray-800 mb-1">{{ tpl.name }}</h4>
            <p class="text-[11px] text-gray-500 mb-3">{{ tpl.desc }}</p>
            <div class="flex flex-wrap gap-1 mb-3">
              <span
                v-for="field in tpl.merge_fields"
                :key="field"
                class="text-[9px] bg-teal-50 text-teal-700 px-1.5 py-0.5 rounded font-mono"
                v-text="'{{' + field + '}}'"
              ></span>
            </div>
            <div class="flex gap-2">
              <button
                @click="generateDoc(tpl)"
                class="flex-1 rounded-lg bg-teal-600 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 transition-colors"
              >
                {{ __("Generate") }}
              </button>
              <button
                class="px-3 rounded-lg border border-gray-200 py-1.5 text-xs text-gray-600 hover:bg-gray-50 transition-colors"
              >
                {{ __("Edit") }}
              </button>
            </div>
          </div>
          <!-- New template -->
          <div
            class="rounded-xl border-2 border-dashed border-gray-300 p-5 flex flex-col items-center justify-center text-center hover:border-teal-400 transition-colors cursor-pointer min-h-[180px]"
          >
            <FeatherIcon name="plus-circle" class="h-8 w-8 text-gray-300 mb-2" />
            <p class="text-sm font-semibold text-gray-500">{{ __("New Template") }}</p>
            <p class="text-xs text-gray-400 mt-1">
              {{ __("Upload DOCX or create from scratch") }}
            </p>
          </div>
        </div>
      </div>
    </div>
    </div>

    <!-- ── Upload Modal ── -->
    <div
      v-if="showUpload"
      class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 backdrop-blur-sm"
      @click.self="showUpload = false"
    >
      <div class="w-full max-w-lg bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-base font-bold text-gray-800">{{ __("Upload Documents") }}</h3>
          <button @click="showUpload = false">
            <FeatherIcon name="x" class="h-5 w-5 text-gray-400" />
          </button>
        </div>

        <div
          class="border-2 border-dashed border-teal-300 rounded-xl p-8 text-center cursor-pointer hover:border-teal-500 bg-teal-50/30 transition-colors"
          @click="triggerFakeUploads"
        >
          <FeatherIcon name="upload-cloud" class="h-10 w-10 text-teal-300 mx-auto mb-3" />
          <p class="text-sm font-semibold text-gray-700">
            {{ __("Drop files here or click") }}
          </p>
          <p class="text-xs text-gray-400 mt-1">PDF, JPG, PNG, XLSX, DOCX — max 25 MB</p>
        </div>

        <div v-if="uploads.length" class="mt-4 space-y-2 max-h-40 overflow-y-auto">
          <div
            v-for="u in uploads"
            :key="u.name"
            class="flex items-center gap-3 p-3 rounded-lg bg-gray-50 border border-gray-200"
          >
            <FeatherIcon name="file" class="h-4 w-4 text-teal-500 shrink-0" />
            <div class="flex-1 min-w-0">
              <div class="text-xs font-semibold text-gray-800 truncate">{{ u.name }}</div>
              <div class="mt-1 h-1 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full bg-teal-500 rounded-full transition-all duration-200"
                  :style="{ width: u.progress + '%' }"
                />
              </div>
            </div>
            <span
              class="text-[10px] font-bold shrink-0"
              :class="u.progress === 100 ? 'text-green-600' : 'text-teal-600'"
              >{{ u.progress === 100 ? "✓ Done" : u.progress + "%" }}</span
            >
          </div>
        </div>

        <div class="mt-4 grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1.5">{{
              __("Assign to Customer")
            }}</label>
            <select class="field-select">
              <option v-for="c in customerOptions" :key="c">{{ c }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1.5">{{
              __("Document Type")
            }}</label>
            <select class="field-select">
              <option v-for="t in docTypeOptions" :key="t">{{ t }}</option>
            </select>
          </div>
        </div>

        <div class="mt-3 flex items-center gap-2">
          <input type="checkbox" id="autoOcr" checked class="rounded" />
          <label for="autoOcr" class="text-xs text-gray-700">{{
            __("Auto-run OCR after upload")
          }}</label>
          <input type="checkbox" id="autoClass" checked class="ml-3 rounded" />
          <label for="autoClass" class="text-xs text-gray-700">{{
            __("AI auto-classify")
          }}</label>
        </div>

        <div class="mt-5 flex gap-2">
          <button
            @click="showUpload = false"
            class="flex-1 border border-gray-200 rounded-lg py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50"
          >
            {{ __("Cancel") }}
          </button>
          <button
            @click="confirmUpload"
            class="flex-1 bg-teal-600 rounded-lg py-2 text-sm font-semibold text-white hover:bg-teal-700 transition-colors"
          >
            {{ __("Upload & Process") }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Share Modal ── -->
    <div
      v-if="showShareModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      @click.self="showShareModal = false"
    >
      <div class="w-full max-w-sm bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-gray-800">{{ __("Secure Share Link") }}</h3>
          <button @click="showShareModal = false">
            <FeatherIcon name="x" class="h-4 w-4 text-gray-400" />
          </button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1.5">{{
              __("Password Protection")
            }}</label>
            <input
              v-model="shareForm.password"
              type="text"
              placeholder="Leave blank for no password"
              class="field-input"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1.5">{{
              __("Expires In")
            }}</label>
            <select v-model="shareForm.expiry" class="field-select">
              <option value="1h">1 hour</option>
              <option value="24h">24 hours</option>
              <option value="7d">7 days</option>
              <option value="30d">30 days</option>
            </select>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-1.5">
              <input
                type="checkbox"
                v-model="shareForm.allow_download"
                class="rounded"
              /><label class="text-xs text-gray-700">Allow download</label>
            </div>
            <div class="flex items-center gap-1.5">
              <input
                type="checkbox"
                v-model="shareForm.watermark"
                class="rounded"
              /><label class="text-xs text-gray-700">Watermark</label>
            </div>
          </div>
        </div>
        <div
          v-if="shareLink"
          class="mt-4 flex items-center gap-2 bg-teal-50 border border-teal-200 rounded-lg px-3 py-2"
        >
          <span class="text-[10px] font-mono text-teal-700 flex-1 truncate">{{
            shareLink
          }}</span>
          <button
            @click="copyLink"
            class="shrink-0 text-[10px] text-teal-700 font-bold hover:underline"
          >
            {{ copied ? "✓ Copied" : "Copy" }}
          </button>
        </div>
        <button
          @click="generateLink"
          class="mt-4 w-full bg-teal-600 rounded-lg py-2 text-sm font-semibold text-white hover:bg-teal-700 transition-colors"
        >
          {{ __("Generate Link") }}
        </button>
      </div>
    </div>

    <!-- ── Preview Modal ── -->
    <div
      v-if="showPreviewModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
      @click.self="showPreviewModal = false"
    >
      <div class="w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden flex flex-col bg-gray-800" style="max-height: 90vh">
        <!-- Header -->
        <div class="px-5 py-3 flex items-center gap-3 shrink-0">
          <FeatherIcon name="file-text" class="h-4 w-4 text-gray-400 shrink-0" />
          <span class="text-sm font-semibold text-white truncate flex-1">{{ selectedDoc?.name }}</span>
          <div class="flex items-center gap-2 shrink-0">
            <button @click="downloadDoc(selectedDoc)" class="text-gray-400 hover:text-white transition-colors">
              <FeatherIcon name="download" class="h-4 w-4" />
            </button>
            <button @click="showPreviewModal = false" class="text-gray-400 hover:text-white transition-colors">
              <FeatherIcon name="x" class="h-4 w-4" />
            </button>
          </div>
        </div>

        <!-- Viewer toolbar -->
        <div class="bg-gray-700 px-4 py-1.5 flex items-center gap-2 shrink-0 border-t border-gray-600">
          <button @click="previewPage = Math.max(1, previewPage - 1)" :disabled="previewPage === 1" class="p-1 rounded text-gray-400 hover:text-white disabled:opacity-30 transition-colors">
            <FeatherIcon name="chevron-left" class="h-3.5 w-3.5" />
          </button>
          <span class="text-xs text-gray-300 w-24 text-center">Page {{ previewPage }} of {{ previewTotalPages }}</span>
          <button @click="previewPage = Math.min(previewTotalPages, previewPage + 1)" :disabled="previewPage === previewTotalPages" class="p-1 rounded text-gray-400 hover:text-white disabled:opacity-30 transition-colors">
            <FeatherIcon name="chevron-right" class="h-3.5 w-3.5" />
          </button>
          <div class="ml-auto flex items-center gap-1.5 text-[10px] text-gray-400">
            <FeatherIcon name="shield" class="h-3 w-3" />Confidential · Watermarked preview
          </div>
        </div>

        <!-- PDF paper area -->
        <div class="flex-1 overflow-y-auto bg-gray-600 flex justify-center py-6 px-4">
          <div class="w-full max-w-[520px] bg-white shadow-2xl relative" style="min-height: 720px">

            <!-- Watermark -->
            <div class="absolute inset-0 pointer-events-none select-none overflow-hidden flex items-center justify-center z-10">
              <span class="text-[52px] font-black text-gray-400 opacity-[0.06] tracking-[0.3em] whitespace-nowrap" style="transform:rotate(-30deg)">CONFIDENTIAL</span>
            </div>

            <!-- Page footer -->
            <div class="absolute bottom-3 left-0 right-0 flex items-center justify-between px-8 text-[9px] text-gray-300 z-10">
              <span>Bank Summon — Internal Use Only</span>
              <span>{{ previewPage }} / {{ previewTotalPages }}</span>
            </div>

            <!-- Content -->
            <div class="p-10 pb-12">

              <!-- ── AGREEMENT ── -->
              <template v-if="selectedDoc?.doc_type === 'Agreement'">
                <!-- Page 1 -->
                <div v-if="previewPage === 1">
                  <div class="flex items-start justify-between mb-6 pb-4 border-b-2 border-teal-600">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-lg bg-teal-600 flex items-center justify-center shrink-0"><span class="text-white text-xs font-black">BS</span></div>
                      <div>
                        <div class="text-sm font-black text-gray-800 tracking-wide">BANK SUMMON</div>
                        <div class="text-[9px] text-gray-400">Jl. Sudirman Kav. 45, Jakarta 10220</div>
                      </div>
                    </div>
                    <div class="text-right text-[9px] text-gray-500">
                      <div>No: PKR/2026/0547/WC</div>
                      <div>Tgl: 24 Mei 2026</div>
                    </div>
                  </div>
                  <div class="text-center mb-6">
                    <p class="text-sm font-black text-gray-800 tracking-widest uppercase">Perjanjian Kredit</p>
                    <p class="text-xs text-gray-500 mt-1">Nomor: PKR/2026/0547/WC</p>
                    <div class="mt-3 h-px bg-gray-200" />
                  </div>
                  <div class="text-[11px] text-gray-700 leading-relaxed space-y-3 mb-6">
                    <p>Yang bertanda tangan di bawah ini:</p>
                    <div class="space-y-2 ml-3">
                      <p><span class="font-bold">I. BANK SUMMON</span>, badan hukum Perseroan Terbatas berkedudukan di Jakarta, diwakili oleh <span class="font-semibold">Dewi Kusuma</span>, Kepala Divisi Kredit Korporat — selanjutnya disebut <span class="font-bold">"BANK"</span>.</p>
                      <p><span class="font-bold">II. PT MAJU BERSAMA</span>, NPWP 01.234.567.8-001.000, diwakili oleh <span class="font-semibold">Budi Santoso</span>, Direktur Utama — selanjutnya disebut <span class="font-bold">"DEBITUR"</span>.</p>
                    </div>
                    <p>Kedua belah pihak telah sepakat untuk membuat dan menandatangani Perjanjian Kredit ini dengan syarat dan ketentuan sebagai berikut:</p>
                  </div>
                  <div class="mb-5">
                    <p class="text-[11px] font-bold text-gray-800 uppercase tracking-wide mb-2 border-b border-gray-100 pb-1">Pasal 1 — Fasilitas Kredit</p>
                    <div class="text-[11px] text-gray-600 leading-relaxed">
                      <p class="mb-2">1.1 BANK menyetujui Fasilitas Kredit Modal Kerja dengan ketentuan:</p>
                      <div class="ml-3 rounded-lg border border-gray-200 overflow-hidden">
                        <table class="w-full text-[10px]">
                          <tr class="bg-teal-50 border-b border-gray-100"><td class="px-3 py-1.5 text-gray-500 w-2/5">Jenis Fasilitas</td><td class="px-3 py-1.5 font-bold text-gray-800">Kredit Modal Kerja (KMK)</td></tr>
                          <tr class="border-b border-gray-100"><td class="px-3 py-1.5 text-gray-500">Plafond</td><td class="px-3 py-1.5 font-bold text-gray-800">Rp 5.000.000.000,-</td></tr>
                          <tr class="bg-gray-50 border-b border-gray-100"><td class="px-3 py-1.5 text-gray-500">Suku Bunga</td><td class="px-3 py-1.5 font-bold text-gray-800">10,5% p.a. floating</td></tr>
                          <tr class="border-b border-gray-100"><td class="px-3 py-1.5 text-gray-500">Jangka Waktu</td><td class="px-3 py-1.5 font-bold text-gray-800">36 Bulan</td></tr>
                          <tr class="bg-gray-50"><td class="px-3 py-1.5 text-gray-500">Provisi</td><td class="px-3 py-1.5 font-bold text-gray-800">1% (sekali bayar)</td></tr>
                        </table>
                      </div>
                    </div>
                  </div>
                  <div>
                    <p class="text-[11px] font-bold text-gray-800 uppercase tracking-wide mb-2 border-b border-gray-100 pb-1">Pasal 2 — Jaminan</p>
                    <div class="text-[11px] text-gray-600 space-y-1">
                      <p>2.1 Sebagai jaminan, DEBITUR menyerahkan agunan:</p>
                      <div class="ml-3 text-[10px] space-y-0.5">
                        <p>a) SHM Gudang Bekasi 2.500 m² — nilai appraisal Rp 8,5 M</p>
                        <p>b) Mesin CNC Haas VF-4 (3 unit) — nilai appraisal Rp 3,2 M</p>
                        <p>c) Deposito BCA No. 00128xxx — Rp 1,5 M</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Page 2 -->
                <div v-if="previewPage === 2">
                  <div class="text-[10px] text-gray-400 font-semibold mb-5 pb-3 border-b border-gray-200">Perjanjian Kredit No. PKR/2026/0547/WC — Lanjutan</div>
                  <div class="mb-5">
                    <p class="text-[11px] font-bold text-gray-800 uppercase tracking-wide mb-2 border-b border-gray-100 pb-1">Pasal 3 — Covenant Keuangan</p>
                    <p class="text-[11px] text-gray-600 mb-2">3.1 Selama fasilitas berjalan, DEBITUR wajib memenuhi kondisi berikut:</p>
                    <div class="rounded-lg border border-gray-200 overflow-hidden">
                      <table class="w-full text-[10px]">
                        <thead><tr class="bg-gray-50 border-b border-gray-200"><th class="px-3 py-1.5 text-left text-gray-500">Covenant</th><th class="px-3 py-1.5 text-left text-gray-500">Threshold</th><th class="px-3 py-1.5 text-left text-gray-500">Frekuensi</th></tr></thead>
                        <tbody>
                          <tr class="border-b border-gray-100"><td class="px-3 py-1.5 font-semibold text-gray-800">DSCR</td><td class="px-3 py-1.5 text-gray-600">≥ 1,25x</td><td class="px-3 py-1.5 text-gray-600">Bulanan</td></tr>
                          <tr class="bg-gray-50 border-b border-gray-100"><td class="px-3 py-1.5 font-semibold text-gray-800">DER</td><td class="px-3 py-1.5 text-gray-600">≤ 3,0x</td><td class="px-3 py-1.5 text-gray-600">Triwulan</td></tr>
                          <tr class="border-b border-gray-100"><td class="px-3 py-1.5 font-semibold text-gray-800">Current Ratio</td><td class="px-3 py-1.5 text-gray-600">≥ 1,0x</td><td class="px-3 py-1.5 text-gray-600">Bulanan</td></tr>
                          <tr class="bg-gray-50"><td class="px-3 py-1.5 font-semibold text-gray-800">Asuransi Agunan</td><td class="px-3 py-1.5 text-gray-600">Valid / Aktif</td><td class="px-3 py-1.5 text-gray-600">Tahunan</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div class="mb-5">
                    <p class="text-[11px] font-bold text-gray-800 uppercase tracking-wide mb-2 border-b border-gray-100 pb-1">Pasal 4 — Events of Default</p>
                    <div class="text-[11px] text-gray-600 space-y-1">
                      <p>4.1 Cidera janji terjadi apabila:</p>
                      <div class="ml-3 text-[10px] space-y-0.5 text-gray-600">
                        <p>a) Gagal bayar pokok atau bunga lebih dari 30 hari kalender;</p>
                        <p>b) Melanggar covenant keuangan selama 2 periode berturut-turut;</p>
                        <p>c) Perubahan material yang berdampak negatif pada kemampuan bayar;</p>
                        <p>d) DEBITUR dinyatakan pailit atau mengajukan permohonan PKPU;</p>
                        <p>e) Agunan mengalami kerusakan material tanpa penggantian dalam 30 hari.</p>
                      </div>
                    </div>
                  </div>
                  <div>
                    <p class="text-[11px] font-bold text-gray-800 uppercase tracking-wide mb-2 border-b border-gray-100 pb-1">Pasal 5 — Kondisi Pencairan</p>
                    <div class="text-[11px] text-gray-600 space-y-1">
                      <p>5.1 Pencairan dapat dilakukan setelah seluruh condition precedent terpenuhi:</p>
                      <div class="ml-3 text-[10px] space-y-0.5 text-gray-600">
                        <p>a) Perjanjian ini telah ditandatangani oleh seluruh pihak;</p>
                        <p>b) Seluruh agunan telah diikat sempurna sesuai peraturan berlaku;</p>
                        <p>c) Asuransi agunan aktif dengan BANK sebagai loss payee;</p>
                        <p>d) Seluruh dokumen persyaratan pencairan telah diserahkan.</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Page 3: Signatures -->
                <div v-if="previewPage === 3">
                  <div class="text-[10px] text-gray-400 font-semibold mb-5 pb-3 border-b border-gray-200">Perjanjian Kredit No. PKR/2026/0547/WC — Halaman Penandatanganan</div>
                  <p class="text-[11px] text-gray-600 leading-relaxed mb-8">Demikian Perjanjian Kredit ini dibuat dan ditandatangani dalam keadaan sadar dan tanpa paksaan dari siapapun pada hari dan tanggal tersebut di atas.</p>
                  <div class="grid grid-cols-2 gap-10 mt-6">
                    <div class="text-center">
                      <p class="text-[10px] font-semibold text-gray-700 mb-14">BANK SUMMON</p>
                      <div class="border-b border-gray-400 mb-1.5" />
                      <p class="text-[10px] font-bold text-gray-800">Dewi Kusuma</p>
                      <p class="text-[9px] text-gray-500">Kepala Divisi Kredit Korporat</p>
                      <div class="mt-4 flex justify-center">
                        <div class="w-16 h-16 rounded-full border-2 border-teal-400 flex items-center justify-center">
                          <span class="text-[8px] text-teal-600 font-bold text-center leading-tight">e-SIGN<br/>✓ VALID</span>
                        </div>
                      </div>
                      <p class="text-[9px] text-gray-400 mt-1.5">24 Mei 2026 · 10:15 WIB</p>
                    </div>
                    <div class="text-center">
                      <p class="text-[10px] font-semibold text-gray-700 mb-14">PT MAJU BERSAMA</p>
                      <div class="border-b border-gray-400 mb-1.5" />
                      <p class="text-[10px] font-bold text-gray-800">Budi Santoso</p>
                      <p class="text-[9px] text-gray-500">Direktur Utama</p>
                      <div class="mt-4 flex justify-center">
                        <div class="w-16 h-16 rounded-full border-2 border-teal-400 flex items-center justify-center">
                          <span class="text-[8px] text-teal-600 font-bold text-center leading-tight">e-SIGN<br/>✓ VALID</span>
                        </div>
                      </div>
                      <p class="text-[9px] text-gray-400 mt-1.5">24 Mei 2026 · 14:32 WIB</p>
                    </div>
                  </div>
                  <div class="mt-10 text-center border-t border-gray-200 pt-5">
                    <p class="text-[10px] font-semibold text-gray-700 mb-1">Disaksikan oleh Notaris:</p>
                    <p class="text-[10px] font-bold text-gray-800">Dr. Hendra Pratama, S.H., M.Kn.</p>
                    <p class="text-[9px] text-gray-500">Notaris dan PPAT Jakarta Selatan · SK AHU-123/KN.01.2024</p>
                  </div>
                  <div class="flex justify-center mt-6">
                    <div class="w-24 h-24 rounded-full border-4 border-dashed border-teal-300 flex items-center justify-center opacity-30">
                      <span class="text-[8px] text-teal-700 font-bold text-center">BANK<br/>SUMMON</span>
                    </div>
                  </div>
                </div>
              </template>

              <!-- ── FINANCIAL ── -->
              <template v-else-if="selectedDoc?.doc_type === 'Financial'">
                <!-- Page 1: P&L -->
                <div v-if="previewPage === 1">
                  <div class="flex items-start justify-between mb-5 pb-4 border-b-2 border-blue-600">
                    <div>
                      <p class="text-sm font-black text-gray-800">PT MAJU BERSAMA</p>
                      <p class="text-[9px] text-gray-500">NPWP: 01.234.567.8-001.000</p>
                    </div>
                    <div class="text-right">
                      <p class="text-xs font-bold text-gray-700">Laporan Keuangan Audited</p>
                      <p class="text-[9px] text-gray-500">Tahun Fiskal 2024</p>
                      <p class="text-[9px] text-gray-400">KAP: Purwantono, Sungkoro &amp; Surja (EY)</p>
                    </div>
                  </div>
                  <div class="grid grid-cols-3 gap-2 mb-5">
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-2 text-center">
                      <p class="text-sm font-black text-blue-700">Rp 28,4M</p>
                      <p class="text-[9px] text-blue-600">Revenue</p>
                      <p class="text-[8px] text-green-600 font-semibold">↑ 12% YoY</p>
                    </div>
                    <div class="bg-green-50 border border-green-200 rounded-lg p-2 text-center">
                      <p class="text-sm font-black text-green-700">Rp 4,2M</p>
                      <p class="text-[9px] text-green-600">Net Profit</p>
                      <p class="text-[8px] text-green-600 font-semibold">↑ 20% YoY</p>
                    </div>
                    <div class="bg-teal-50 border border-teal-200 rounded-lg p-2 text-center">
                      <p class="text-sm font-black text-teal-700">Rp 52,1M</p>
                      <p class="text-[9px] text-teal-600">Total Assets</p>
                      <p class="text-[8px] text-green-600 font-semibold">↑ 5% YoY</p>
                    </div>
                  </div>
                  <p class="text-[11px] font-bold text-gray-800 uppercase tracking-wide mb-2 border-b border-gray-100 pb-1">Laporan Laba Rugi Komprehensif</p>
                  <table class="w-full text-[10px] mb-1">
                    <thead><tr class="bg-gray-50 border-b border-gray-200"><th class="px-3 py-1.5 text-left text-gray-500">Pos</th><th class="px-3 py-1.5 text-right text-gray-500">FY2024</th><th class="px-3 py-1.5 text-right text-gray-500">FY2023</th><th class="px-3 py-1.5 text-right text-gray-500">Δ%</th></tr></thead>
                    <tbody>
                      <tr class="border-b border-gray-100"><td class="px-3 py-1.5 font-semibold text-gray-800">Pendapatan Bersih</td><td class="px-3 py-1.5 text-right">28.432</td><td class="px-3 py-1.5 text-right text-gray-400">25.390</td><td class="px-3 py-1.5 text-right text-green-600 font-semibold">+12,0%</td></tr>
                      <tr class="bg-gray-50 border-b border-gray-100"><td class="px-3 py-1.5 text-gray-600">Beban Pokok</td><td class="px-3 py-1.5 text-right">(18.120)</td><td class="px-3 py-1.5 text-right text-gray-400">(16.504)</td><td class="px-3 py-1.5 text-right text-red-400">+9,8%</td></tr>
                      <tr class="border-b border-gray-100"><td class="px-3 py-1.5 font-semibold text-gray-800">Laba Bruto</td><td class="px-3 py-1.5 text-right font-bold">10.312</td><td class="px-3 py-1.5 text-right font-bold text-gray-400">8.886</td><td class="px-3 py-1.5 text-right text-green-600 font-semibold">+16,1%</td></tr>
                      <tr class="bg-gray-50 border-b border-gray-100"><td class="px-3 py-1.5 text-gray-600">Beban Operasional</td><td class="px-3 py-1.5 text-right">(4.890)</td><td class="px-3 py-1.5 text-right text-gray-400">(4.210)</td><td class="px-3 py-1.5 text-right text-red-400">+16,2%</td></tr>
                      <tr class="border-b border-gray-100"><td class="px-3 py-1.5 font-semibold text-gray-800">EBITDA</td><td class="px-3 py-1.5 text-right font-bold text-teal-700">5.422</td><td class="px-3 py-1.5 text-right font-bold text-gray-400">4.676</td><td class="px-3 py-1.5 text-right text-green-600 font-semibold">+16,0%</td></tr>
                      <tr class="bg-gray-50 border-b border-gray-100"><td class="px-3 py-1.5 text-gray-600">Beban Bunga &amp; Pajak</td><td class="px-3 py-1.5 text-right">(1.228)</td><td class="px-3 py-1.5 text-right text-gray-400">(1.192)</td><td class="px-3 py-1.5 text-right text-red-400">+3,0%</td></tr>
                      <tr class="bg-blue-50"><td class="px-3 py-2 font-black text-gray-800">Laba Bersih</td><td class="px-3 py-2 text-right font-black text-blue-700">4.194</td><td class="px-3 py-2 text-right font-black text-gray-500">3.484</td><td class="px-3 py-2 text-right text-green-600 font-bold">+20,4%</td></tr>
                    </tbody>
                  </table>
                  <p class="text-[8px] text-gray-400">*dalam juta rupiah</p>
                </div>

                <!-- Page 2: Neraca -->
                <div v-if="previewPage === 2">
                  <div class="text-[10px] text-gray-500 font-semibold mb-4 pb-3 border-b border-gray-200">PT Maju Bersama — Neraca per 31 Desember 2024 (Rp Juta)</div>
                  <div class="grid grid-cols-2 gap-5 text-[10px]">
                    <div>
                      <p class="font-bold text-gray-700 mb-2 text-[9px] uppercase tracking-wide">ASET</p>
                      <p class="font-semibold text-gray-700 mb-1">Aset Lancar</p>
                      <div class="space-y-0.5 ml-2 mb-3">
                        <div class="flex justify-between"><span class="text-gray-500">Kas &amp; Setara Kas</span><span>4.832</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Piutang Usaha</span><span>8.215</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Persediaan</span><span>6.120</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Aset Lancar Lain</span><span>1.443</span></div>
                        <div class="flex justify-between border-t border-gray-200 pt-0.5 font-bold"><span>Total Aset Lancar</span><span class="text-blue-700">20.610</span></div>
                      </div>
                      <p class="font-semibold text-gray-700 mb-1">Aset Tidak Lancar</p>
                      <div class="space-y-0.5 ml-2">
                        <div class="flex justify-between"><span class="text-gray-500">Aset Tetap (Net)</span><span>28.320</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Aset Lain-lain</span><span>3.170</span></div>
                        <div class="flex justify-between border-t border-gray-200 pt-0.5 font-bold"><span>Total Tidak Lancar</span><span class="text-blue-700">31.490</span></div>
                      </div>
                      <div class="flex justify-between border-t-2 border-gray-300 pt-1 mt-2 font-black"><span>TOTAL ASET</span><span class="text-blue-800">52.100</span></div>
                    </div>
                    <div>
                      <p class="font-bold text-gray-700 mb-2 text-[9px] uppercase tracking-wide">LIABILITAS &amp; EKUITAS</p>
                      <p class="font-semibold text-gray-700 mb-1">Liabilitas Jangka Pendek</p>
                      <div class="space-y-0.5 ml-2 mb-3">
                        <div class="flex justify-between"><span class="text-gray-500">Utang Usaha</span><span>5.240</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Utang Bank (&lt;1 th)</span><span>4.500</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Liabilitas Lain</span><span>1.830</span></div>
                        <div class="flex justify-between border-t border-gray-200 pt-0.5 font-bold"><span>Total Liab. Pendek</span><span class="text-red-600">11.570</span></div>
                      </div>
                      <p class="font-semibold text-gray-700 mb-1">Liabilitas Jangka Panjang</p>
                      <div class="space-y-0.5 ml-2 mb-3">
                        <div class="flex justify-between"><span class="text-gray-500">Utang Bank (&gt;1 th)</span><span>14.200</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Liabilitas Lain</span><span>2.100</span></div>
                        <div class="flex justify-between border-t border-gray-200 pt-0.5 font-bold"><span>Total Liab. Panjang</span><span class="text-red-600">16.300</span></div>
                      </div>
                      <p class="font-semibold text-gray-700 mb-1">Ekuitas</p>
                      <div class="space-y-0.5 ml-2">
                        <div class="flex justify-between"><span class="text-gray-500">Modal Disetor</span><span>10.000</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Saldo Laba</span><span>14.230</span></div>
                        <div class="flex justify-between border-t border-gray-200 pt-0.5 font-bold"><span>Total Ekuitas</span><span class="text-green-700">24.230</span></div>
                      </div>
                      <div class="flex justify-between border-t-2 border-gray-300 pt-1 mt-2 font-black"><span>TOTAL L+E</span><span class="text-blue-800">52.100</span></div>
                    </div>
                  </div>
                  <p class="text-[8px] text-gray-400 mt-3">Diaudit oleh KAP Purwantono, Sungkoro &amp; Surja — Opini Wajar Tanpa Pengecualian</p>
                </div>

                <!-- Pages 3-4: placeholder -->
                <div v-if="previewPage >= 3">
                  <div class="text-[10px] text-gray-500 font-semibold mb-4 pb-3 border-b border-gray-200">{{ previewPage === 3 ? 'Laporan Arus Kas FY2024' : 'Catatan atas Laporan Keuangan' }}</div>
                  <div class="space-y-2">
                    <div v-for="i in 18" :key="i" class="h-2.5 rounded bg-gray-100" :style="{ width: (45 + (i * 11 % 50)) + '%' }" />
                  </div>
                </div>
              </template>

              <!-- ── IDENTITY / KTP ── -->
              <template v-else-if="selectedDoc?.doc_type === 'Identity'">
                <div v-if="previewPage === 1">
                  <div class="text-center mb-5">
                    <p class="text-[9px] text-gray-400 uppercase tracking-widest">Dokumen Kependudukan — Salinan Digital Terverifikasi</p>
                  </div>
                  <div class="mx-auto max-w-[370px] rounded-xl overflow-hidden border-2 border-gray-300 shadow-xl mb-6">
                    <div class="bg-gradient-to-r from-blue-800 to-blue-900 px-4 py-2.5 flex items-center justify-between">
                      <div>
                        <p class="text-[8px] text-blue-200 tracking-widest uppercase font-semibold">Republik Indonesia</p>
                        <p class="text-[11px] text-white font-black tracking-wider">KARTU TANDA PENDUDUK</p>
                      </div>
                      <div class="flex gap-1.5">
                        <div class="w-5 h-5 rounded-full bg-red-500 opacity-80" />
                        <div class="w-5 h-5 rounded-full bg-white opacity-80" />
                      </div>
                    </div>
                    <div class="bg-white px-4 py-3 grid grid-cols-[64px_1fr] gap-3 text-[9px]">
                      <div class="w-16 h-20 bg-gray-200 border border-gray-300 flex items-center justify-center rounded">
                        <FeatherIcon name="user" class="h-7 w-7 text-gray-400" />
                      </div>
                      <div class="space-y-0.5">
                        <div><span class="text-gray-400">NIK</span><span class="ml-2 font-black text-gray-800">3171 0203 1503 8500 1</span></div>
                        <div><span class="text-gray-400">Nama</span><span class="ml-2 font-semibold text-gray-800">BUDI SANTOSO</span></div>
                        <div><span class="text-gray-400">TTL</span><span class="ml-2 text-gray-700">Jakarta, 15-03-1985</span></div>
                        <div><span class="text-gray-400">Kelamin</span><span class="ml-2 text-gray-700">Laki-laki</span></div>
                        <div><span class="text-gray-400">Alamat</span><span class="ml-2 text-gray-700">Jl. Sudirman No. 12, RT.003/RW.005</span></div>
                        <div><span class="text-gray-400">Agama</span><span class="ml-2 text-gray-700">Islam · Kawin</span></div>
                      </div>
                    </div>
                    <div class="bg-gray-50 px-4 py-1.5 border-t border-gray-200 flex justify-between text-[8px] text-gray-400">
                      <span>Kel. Senayan, Kec. Kebayoran Baru, Jak-Sel</span>
                      <span>Berlaku seumur hidup</span>
                    </div>
                  </div>
                  <div class="flex gap-3 justify-center">
                    <div class="flex items-center gap-1.5 bg-green-50 border border-green-200 rounded-full px-3 py-1">
                      <FeatherIcon name="check-circle" class="h-3 w-3 text-green-600" />
                      <span class="text-[10px] font-semibold text-green-700">OCR Verified · 98%</span>
                    </div>
                    <div class="flex items-center gap-1.5 bg-teal-50 border border-teal-200 rounded-full px-3 py-1">
                      <FeatherIcon name="cpu" class="h-3 w-3 text-teal-600" />
                      <span class="text-[10px] font-semibold text-teal-700">AI: KTP / ID Card</span>
                    </div>
                    <div class="flex items-center gap-1.5 bg-purple-50 border border-purple-200 rounded-full px-3 py-1">
                      <FeatherIcon name="shield" class="h-3 w-3 text-purple-600" />
                      <span class="text-[10px] font-semibold text-purple-700">Dukcapil: Valid</span>
                    </div>
                  </div>
                </div>
                <div v-if="previewPage === 2">
                  <div class="text-[10px] text-gray-500 font-semibold mb-4 pb-3 border-b border-gray-200">Hasil Verifikasi KYC — {{ selectedDoc?.customer }}</div>
                  <div class="space-y-3 text-[11px]">
                    <div class="bg-green-50 border border-green-200 rounded-lg p-3 space-y-1.5">
                      <p class="font-semibold text-green-800 mb-1">Verifikasi Dukcapil</p>
                      <div class="flex items-center gap-2 text-green-700"><FeatherIcon name="check-circle" class="h-3.5 w-3.5" /><span>NIK valid — terdaftar Dukcapil DKI Jakarta</span></div>
                      <div class="flex items-center gap-2 text-green-700"><FeatherIcon name="check-circle" class="h-3.5 w-3.5" /><span>Status kependudukan: Aktif</span></div>
                      <div class="flex items-center gap-2 text-green-700"><FeatherIcon name="check-circle" class="h-3.5 w-3.5" /><span>Tidak terdaftar dalam daftar kematian</span></div>
                    </div>
                    <div class="bg-green-50 border border-green-200 rounded-lg p-3 space-y-1.5">
                      <p class="font-semibold text-green-800 mb-1">AML / PEP Screening</p>
                      <div class="flex items-center gap-2 text-green-700"><FeatherIcon name="check-circle" class="h-3.5 w-3.5" /><span>OFAC: Clear</span></div>
                      <div class="flex items-center gap-2 text-green-700"><FeatherIcon name="check-circle" class="h-3.5 w-3.5" /><span>UN Sanctions: Clear</span></div>
                      <div class="flex items-center gap-2 text-green-700"><FeatherIcon name="check-circle" class="h-3.5 w-3.5" /><span>Local Watchlist: Clear</span></div>
                    </div>
                  </div>
                </div>
              </template>

              <!-- ── DEFAULT (KYC / Collateral / etc.) ── -->
              <template v-else>
                <div v-if="previewPage === 1">
                  <div class="flex items-start justify-between mb-6 pb-4 border-b border-gray-200">
                    <div>
                      <p class="text-sm font-black text-gray-800 truncate max-w-[300px]">{{ selectedDoc?.name }}</p>
                      <p class="text-[9px] text-gray-500 mt-0.5">{{ selectedDoc?.customer }} · {{ selectedDoc?.doc_type }}</p>
                    </div>
                    <span class="text-[9px] bg-teal-100 text-teal-700 px-2 py-0.5 rounded font-semibold shrink-0">v{{ selectedDoc?.version }}</span>
                  </div>
                  <div class="space-y-2 mb-6">
                    <div v-for="i in 5" :key="i" class="h-2.5 rounded bg-gray-100" :style="{ width: [80, 100, 75, 95, 65][i-1] + '%' }" />
                  </div>
                  <div class="border border-gray-200 rounded-lg overflow-hidden mb-5">
                    <div class="bg-gray-50 px-3 py-2 border-b border-gray-200 flex gap-6">
                      <div class="h-2.5 bg-gray-300 rounded w-24" />
                      <div class="h-2.5 bg-gray-300 rounded w-20" />
                      <div class="h-2.5 bg-gray-300 rounded w-16" />
                    </div>
                    <div v-for="j in 5" :key="j" class="px-3 py-2 flex gap-6 border-b border-gray-100 last:border-0" :class="j % 2 === 0 ? 'bg-gray-50' : 'bg-white'">
                      <div class="h-2 bg-gray-200 rounded w-24" />
                      <div class="h-2 bg-gray-100 rounded w-20" />
                      <div class="h-2 bg-gray-100 rounded w-16" />
                    </div>
                  </div>
                  <div class="space-y-1.5">
                    <div v-for="k in 6" :key="k" class="h-2.5 rounded bg-gray-100" :style="{ width: (50 + (k * 9 % 45)) + '%' }" />
                  </div>
                </div>
                <div v-if="previewPage === 2">
                  <div class="text-[10px] text-gray-500 font-semibold mb-4 pb-3 border-b border-gray-200">{{ selectedDoc?.name }} — Lanjutan</div>
                  <div class="space-y-2">
                    <div v-for="i in 20" :key="i" class="h-2.5 rounded bg-gray-100" :style="{ width: (40 + (i * 13 % 55)) + '%' }" />
                  </div>
                </div>
              </template>

            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="fade">
      <div
        v-if="toast"
        class="fixed bottom-5 right-5 z-50 bg-gray-800 text-white text-sm font-medium px-4 py-2.5 rounded-xl shadow-xl flex items-center gap-2"
      >
        <FeatherIcon name="check-circle" class="h-4 w-4 text-teal-400" />{{ toast }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, defineComponent, h } from "vue";
import { FeatherIcon } from "frappe-ui";
import LayoutHeader from "@/components/LayoutHeader.vue";

// ── Recursive folder node component ──
const FolderNode = defineComponent({
  name: "FolderNode",
  props: { node: Object, active: String },
  emits: ["select"],
  setup(props, { emit }) {
    const open = ref(props.node.open || false);
    return () =>
      h("div", [
        h(
          "button",
          {
            class: `w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs transition-all ${
              props.active === props.node.id
                ? "bg-teal-50 text-teal-700 font-semibold"
                : "text-gray-600 hover:bg-gray-50"
            }`,
            onClick: () => {
              emit("select", props.node.id);
              if (props.node.children?.length) open.value = !open.value;
            },
          },
          [
            props.node.children?.length
              ? h(FeatherIcon, {
                  name: open.value ? "chevron-down" : "chevron-right",
                  class: "h-3 w-3 text-gray-400 shrink-0",
                })
              : h("span", { class: "w-3 shrink-0" }),
            h(FeatherIcon, {
              name: "folder",
              class: `h-3.5 w-3.5 shrink-0 ${
                props.active === props.node.id ? "text-teal-500" : "text-gray-400"
              }`,
            }),
            h("span", { class: "truncate flex-1 text-left" }, props.node.label),
            props.node.count
              ? h(
                  "span",
                  { class: "text-[9px] text-gray-400 shrink-0" },
                  props.node.count
                )
              : null,
          ]
        ),
        open.value && props.node.children?.length
          ? h(
              "div",
              { class: "ml-4" },
              props.node.children.map((child) =>
                h(FolderNode, {
                  node: child,
                  active: props.active,
                  onSelect: (id) => emit("select", id),
                })
              )
            )
          : null,
      ]);
  },
});

// ── State ──
const activeFolder = ref("all");
const activeView = ref("docs");
const searchQuery = ref("");
const sortBy = ref("date");
const selectedDoc = ref(null);
const panelTab = ref("info");
const showUpload = ref(false);
const showShareModal = ref(false);
const showPreviewModal = ref(false);
const previewPage = ref(1);
const previewTotalPages = computed(() => {
  const t = selectedDoc.value?.doc_type;
  if (t === 'Agreement') return 3;
  if (t === 'Financial') return 4;
  return 2;
});
const shareLink = ref("");
const copied = ref(false);
const toast = ref("");
const uploads = ref([]);
const activeTypeFilters = ref([]);

const shareForm = ref({
  password: "",
  expiry: "7d",
  allow_download: true,
  watermark: true,
});

// ── Static data ──
const quickAccess = [
  { id: "all", icon: "grid", label: "All Documents", count: 47 },
  { id: "recent", icon: "clock", label: "Recently Uploaded", count: null },
  { id: "expiring", icon: "alert-circle", label: "Expiring Soon", count: 8 },
  { id: "missing", icon: "x-circle", label: "Missing Docs", count: 12 },
  { id: "pending-approval", icon: "check-square", label: "Pending Approval", count: 5 },
];

const folderTree = [
  {
    id: "credit",
    label: "Credit Applications",
    count: 18,
    open: true,
    children: [
      { id: "credit-fy26", label: "FY 2026", count: 11, children: [] },
      { id: "credit-fy25", label: "FY 2025", count: 7, children: [] },
    ],
  },
  {
    id: "kyc",
    label: "KYC Documents",
    count: 14,
    children: [
      { id: "kyc-identity", label: "Identity", count: 8, children: [] },
      { id: "kyc-corporate", label: "Corporate Docs", count: 6, children: [] },
    ],
  },
  { id: "collateral", label: "Collateral", count: 7, children: [] },
  { id: "agreements", label: "Agreements & Legal", count: 5, children: [] },
  { id: "templates", label: "Templates", count: 3, children: [] },
];

const typeFilters = [
  { id: "KYC", label: "KYC" },
  { id: "Financial", label: "Financial" },
  { id: "Agreement", label: "Agreement" },
  { id: "Collateral", label: "Collateral" },
  { id: "Identity", label: "Identity" },
];

const allDocs = ref([
  {
    id: 1,
    name: "KTP_Budi_Santoso.pdf",
    ext: "pdf",
    customer: "Budi Santoso",
    doc_type: "Identity",
    ocr: "Done",
    ai_class: "KTP / ID Card",
    ai_conf: 97,
    ai_folder: "KYC / Identity",
    size: "1.2 MB",
    version: 1,
    expiry: "2028-03",
    status: "Active",
    uploaded: "Today 09:15",
    tags: ["KYC", "Individual", "2026"],
    selected: false,
  },
  {
    id: 2,
    name: "NPWP_PT_Maju_Bersama.pdf",
    ext: "pdf",
    customer: "PT Maju Bersama",
    doc_type: "KYC",
    ocr: "Done",
    ai_class: "NPWP",
    ai_conf: 95,
    ai_folder: "KYC / Corporate",
    size: "645 KB",
    version: 2,
    expiry: null,
    status: "Active",
    uploaded: "Today 09:20",
    tags: ["KYC", "Corporate", "Tax"],
    selected: false,
  },
  {
    id: 3,
    name: "Laporan_Keuangan_2024_Audit.xlsx",
    ext: "xlsx",
    customer: "PT Maju Bersama",
    doc_type: "Financial",
    ocr: "Processing",
    ai_class: "Financial Statement",
    ai_conf: 88,
    ai_folder: "Credit Applications/FY2026",
    size: "3.4 MB",
    version: 1,
    expiry: null,
    status: "Pending Approval",
    uploaded: "23 May",
    tags: ["Financial", "Audit", "FY2024"],
    selected: false,
  },
  {
    id: 4,
    name: "Rekening_Koran_BCA_Jan-Jun2026.pdf",
    ext: "pdf",
    customer: "Budi Santoso",
    doc_type: "Financial",
    ocr: "Done",
    ai_class: "Bank Statement",
    ai_conf: 92,
    ai_folder: "Credit Applications/FY2026",
    size: "8.1 MB",
    version: 1,
    expiry: null,
    status: "Active",
    uploaded: "22 May",
    tags: ["Bank Statement", "BCA"],
    selected: false,
  },
  {
    id: 5,
    name: "SHM_Gudang_Bekasi.pdf",
    ext: "pdf",
    customer: "PT Maju Bersama",
    doc_type: "Collateral",
    ocr: "Done",
    ai_class: "Property Certificate",
    ai_conf: 91,
    ai_folder: "Collateral",
    size: "2.2 MB",
    version: 1,
    expiry: "2026-06",
    status: "Active",
    uploaded: "20 May",
    tags: ["Collateral", "Properti", "SHM"],
    selected: false,
  },
  {
    id: 6,
    name: "Perjanjian_Kredit_v2.1.docx",
    ext: "docx",
    customer: "PT Maju Bersama",
    doc_type: "Agreement",
    ocr: "N/A",
    ai_class: "Loan Agreement",
    ai_conf: 99,
    ai_folder: "Agreements & Legal",
    size: "512 KB",
    version: 3,
    expiry: null,
    status: "Signed",
    uploaded: "24 May",
    tags: ["Agreement", "PK", "Signed"],
    selected: false,
  },
  {
    id: 7,
    name: "SIUP_CV_Teknik_Jaya.pdf",
    ext: "pdf",
    customer: "CV Teknik Jaya",
    doc_type: "KYC",
    ocr: "Done",
    ai_class: "Business License",
    ai_conf: 89,
    ai_folder: "KYC / Corporate",
    size: "780 KB",
    version: 1,
    expiry: "2026-07",
    status: "Active",
    uploaded: "18 May",
    tags: ["SIUP", "License", "UMKM"],
    selected: false,
  },
  {
    id: 8,
    name: "Akta_Pendirian_PT_Maju.pdf",
    ext: "pdf",
    customer: "PT Maju Bersama",
    doc_type: "KYC",
    ocr: "Done",
    ai_class: "Deed of Establishment",
    ai_conf: 93,
    ai_folder: "KYC / Corporate",
    size: "1.8 MB",
    version: 2,
    expiry: null,
    status: "Active",
    uploaded: "15 May",
    tags: ["Akta", "Corporate", "Pendirian"],
    selected: false,
  },
  {
    id: 9,
    name: "Asuransi_Jiwa_BCA_Life.pdf",
    ext: "pdf",
    customer: "Budi Santoso",
    doc_type: "Collateral",
    ocr: "Done",
    ai_class: "Insurance Policy",
    ai_conf: 86,
    ai_folder: "Collateral",
    size: "1.1 MB",
    version: 1,
    expiry: "2026-08",
    status: "Active",
    uploaded: "10 May",
    tags: ["Insurance", "Life", "Collateral"],
    selected: false,
  },
  {
    id: 10,
    name: "BPKB_Mesin_CNC_Haas.pdf",
    ext: "pdf",
    customer: "CV Teknik Jaya",
    doc_type: "Collateral",
    ocr: "Done",
    ai_class: "Vehicle / Asset Certificate",
    ai_conf: 90,
    ai_folder: "Collateral",
    size: "955 KB",
    version: 1,
    expiry: null,
    status: "Active",
    uploaded: "8 May",
    tags: ["BPKB", "Mesin", "Collateral"],
    selected: false,
  },
]);

const storageUsed = "38.2 GB";
const storageTotal = "50 GB";
const storagePercent = 76;

const panelTabs = [
  { id: "info", label: "Info" },
  { id: "ocr", label: "OCR" },
  { id: "versions", label: "Versions" },
  { id: "audit", label: "Audit" },
];

const views = [
  { id: "docs", icon: "list", label: "Documents" },
  { id: "health", icon: "activity", label: "Health" },
  { id: "audit", icon: "shield", label: "Audit Log" },
  { id: "templates", icon: "layout", label: "Templates" },
];

const demoOcrText = `KARTU TANDA PENDUDUK
NIK: 3171xxxxxxxxxxxx
Nama: Budi Santoso
Tempat/Tgl Lahir: Jakarta, 15-03-1985
Jenis Kelamin: Laki-laki
Alamat: Jl. Sudirman No. 12
Kel/Desa: Senayan
Kecamatan: Kebayoran Baru
Agama: Islam
Status Perkawinan: Kawin
Berlaku Hingga: Seumur Hidup`;

const ocrFields = [
  { key: "NIK", value: "3171xxxxxxxxxxxx", conf: 98 },
  { key: "Nama", value: "Budi Santoso", conf: 97 },
  { key: "TTL", value: "Jakarta, 15 Mar 1985", conf: 94 },
  { key: "Alamat", value: "Jl. Sudirman No. 12", conf: 89 },
  { key: "Berlaku", value: "Seumur Hidup", conf: 99 },
];

const docVersions = [
  {
    v: 3,
    by: "Dewi Kusuma",
    date: "24 May 2026",
    note: "Updated after committee review",
  },
  {
    v: 2,
    by: "Ahmad Fauzi",
    date: "22 May 2026",
    note: "Minor corrections to clause 12",
  },
  { v: 1, by: "System", date: "20 May 2026", note: "Initial upload" },
];

const docAudit = [
  {
    id: 1,
    user: "Dewi Kusuma",
    action: "Downloaded",
    time: "24 May 11:32",
    note: "Watermarked copy",
  },
  { id: 2, user: "Ahmad Fauzi", action: "Approved", time: "24 May 10:15", note: null },
  {
    id: 3,
    user: "System (OCR)",
    action: "Processed",
    time: "24 May 09:16",
    note: "Confidence: 94%",
  },
  { id: 4, user: "Budi Santoso", action: "Uploaded", time: "24 May 09:15", note: null },
];

const healthKpis = [
  {
    label: "Total Documents",
    value: "247",
    bg: "bg-teal-100",
    icon: "file",
    iconColor: "text-teal-600",
    color: "text-teal-600",
  },
  {
    label: "OCR Processed",
    value: "198",
    bg: "bg-green-100",
    icon: "cpu",
    iconColor: "text-green-600",
    color: "text-green-600",
  },
  {
    label: "Expiring ≤ 30d",
    value: "8",
    bg: "bg-amber-100",
    icon: "clock",
    iconColor: "text-amber-600",
    color: "text-amber-600",
  },
  {
    label: "Missing Critical",
    value: "12",
    bg: "bg-red-100",
    icon: "alert-circle",
    iconColor: "text-red-500",
    color: "text-red-500",
  },
];

const completeness = [
  { name: "PT Maju Bersama", received: 9, total: 10, missing: 1, pct: 90 },
  { name: "Budi Santoso", received: 6, total: 8, missing: 2, pct: 75 },
  { name: "CV Teknik Jaya", received: 5, total: 9, missing: 4, pct: 56 },
  { name: "Siti Rahmawati", received: 3, total: 7, missing: 4, pct: 43 },
];

const expiringDocs = [
  { id: 1, name: "SIUP_CV_Teknik_Jaya.pdf", customer: "CV Teknik Jaya", days: 7 },
  { id: 2, name: "SHM_Gudang_Bekasi.pdf", customer: "PT Maju Bersama", days: 12 },
  { id: 3, name: "Asuransi_Jiwa_BCA.pdf", customer: "Budi Santoso", days: 21 },
  { id: 4, name: "KTP_Siti_Rahmawati.pdf", customer: "Siti Rahmawati", days: 28 },
];

const missingTypes = [
  { type: "Rekening Koran", count: 4 },
  { type: "Lap. Keuangan", count: 3 },
  { type: "Sertifikat Jaminan", count: 3 },
  { type: "Asuransi", count: 2 },
];

const auditLogs = [
  {
    id: 1,
    time: "2026-05-24 11:32",
    user: "Dewi Kusuma",
    action: "Download",
    doc: "Perjanjian_Kredit_v2.1.docx",
    ip: "192.168.1.45",
    result: "Success",
  },
  {
    id: 2,
    time: "2026-05-24 10:15",
    user: "Ahmad Fauzi",
    action: "Approve",
    doc: "Laporan_Keuangan_2024.xlsx",
    ip: "192.168.1.32",
    result: "Success",
  },
  {
    id: 3,
    time: "2026-05-24 09:50",
    user: "Sari Indrawati",
    action: "View",
    doc: "SHM_Gudang_Bekasi.pdf",
    ip: "10.0.0.88",
    result: "Success",
  },
  {
    id: 4,
    time: "2026-05-24 09:20",
    user: "Unknown",
    action: "Login Attempt",
    doc: "—",
    ip: "203.x.x.x",
    result: "Blocked",
  },
  {
    id: 5,
    time: "2026-05-24 09:15",
    user: "Budi Santoso",
    action: "Upload",
    doc: "KTP_Budi_Santoso.pdf",
    ip: "192.168.2.10",
    result: "Success",
  },
  {
    id: 6,
    time: "2026-05-23 16:40",
    user: "System (OCR)",
    action: "OCR Process",
    doc: "Rekening_Koran_BCA.pdf",
    ip: "internal",
    result: "Success",
  },
];

const templates = [
  {
    id: 1,
    name: "Perjanjian Kredit (PK)",
    desc: "Standard loan agreement with variable terms",
    version: "2.1",
    merge_fields: ["borrower_name", "amount", "tenor", "rate", "date"],
  },
  {
    id: 2,
    name: "Surat Penawaran Fasilitas",
    desc: "Credit offer letter for approved applications",
    version: "1.3",
    merge_fields: ["borrower_name", "facility_type", "amount", "conditions"],
  },
  {
    id: 3,
    name: "Notifikasi Jatuh Tempo",
    desc: "Payment reminder notification letter",
    version: "1.0",
    merge_fields: ["borrower_name", "due_date", "amount", "account"],
  },
  {
    id: 4,
    name: "Berita Acara Pencairan",
    desc: "Disbursement acknowledgment document",
    version: "1.1",
    merge_fields: ["borrower_name", "disbursement_date", "amount", "bank"],
  },
  {
    id: 5,
    name: "Surat Peringatan (SP1/2/3)",
    desc: "Collections warning letter (SP1, SP2, SP3)",
    version: "2.0",
    merge_fields: ["borrower_name", "overdue_amount", "days_past_due", "sp_level"],
  },
];

const customerOptions = [
  "PT Maju Bersama",
  "Budi Santoso",
  "CV Teknik Jaya",
  "Siti Rahmawati",
];
const docTypeOptions = [
  "Identity",
  "KYC",
  "Financial",
  "Collateral",
  "Agreement",
  "Correspondence",
  "Other",
];

// ── Computed ──
const filteredDocs = computed(() => {
  let docs = allDocs.value;
  if (activeTypeFilters.value.length)
    docs = docs.filter((d) => activeTypeFilters.value.includes(d.doc_type));
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    docs = docs.filter(
      (d) =>
        d.name.toLowerCase().includes(q) ||
        d.customer.toLowerCase().includes(q) ||
        d.doc_type.toLowerCase().includes(q)
    );
  }
  if (sortBy.value === "name")
    return [...docs].sort((a, b) => a.name.localeCompare(b.name));
  return docs;
});

const selectedCount = computed(() => allDocs.value.filter((d) => d.selected).length);

const breadcrumb = computed(() => {
  const map = {
    all: "All Documents",
    recent: "Recently Uploaded",
    expiring: "Expiring Soon",
    missing: "Missing Docs",
    "pending-approval": "Pending Approval",
    credit: "Credit Applications",
    kyc: "KYC Documents",
    collateral: "Collateral",
    agreements: "Agreements & Legal",
    templates: "Templates",
    "credit-fy26": "FY 2026",
    "credit-fy25": "FY 2025",
    "kyc-identity": "Identity",
    "kyc-corporate": "Corporate Docs",
  };
  const label = map[activeFolder.value] || activeFolder.value;
  return [
    { label: "DMS", folderId: "all" },
    { label, folderId: null },
  ];
});

const docInfo = computed(() => {
  if (!selectedDoc.value) return [];
  const d = selectedDoc.value;
  return [
    { label: "File Name", value: d.name },
    { label: "Document Type", value: d.doc_type },
    { label: "Customer", value: d.customer },
    { label: "File Size", value: d.size },
    { label: "Version", value: "v" + d.version },
    { label: "Uploaded", value: d.uploaded },
    { label: "Status", value: d.status },
    { label: "OCR", value: d.ocr },
  ];
});

// ── Methods ──
function __(s) {
  return s;
}
function fileIconBg(ext) {
  const m = {
    pdf: "bg-red-100",
    xlsx: "bg-green-100",
    docx: "bg-blue-100",
    jpg: "bg-purple-100",
    png: "bg-purple-100",
  };
  return m[ext] || "bg-gray-100";
}
function fileIconColor(ext) {
  const m = {
    pdf: "text-red-600",
    xlsx: "text-green-700",
    docx: "text-blue-700",
    jpg: "text-purple-700",
    png: "text-purple-700",
  };
  return m[ext] || "text-gray-600";
}
function docTypeBadge(type) {
  const m = {
    KYC: "bg-teal-100 text-teal-700",
    Financial: "bg-blue-100 text-blue-700",
    Agreement: "bg-purple-100 text-purple-700",
    Collateral: "bg-amber-100 text-amber-700",
    Identity: "bg-green-100 text-green-700",
  };
  return m[type] || "bg-gray-100 text-gray-600";
}
function statusBadge(s) {
  const m = {
    Active: "bg-green-100 text-green-700",
    Signed: "bg-teal-100 text-teal-700",
    "Pending Approval": "bg-amber-100 text-amber-700",
    Expired: "bg-red-100 text-red-600",
  };
  return m[s] || "bg-gray-100 text-gray-600";
}
function expiryClass(exp) {
  if (!exp) return "";
  const m = new Date(exp + "-01"),
    d = Math.round((m - Date.now()) / 86400000);
  return d <= 14 ? "text-red-500" : d <= 30 ? "text-amber-500" : "text-gray-500";
}
function isExpiringSoon(exp) {
  if (!exp) return false;
  const d = Math.round((new Date(exp + "-01") - Date.now()) / 86400000);
  return d <= 30;
}
function auditColor(a) {
  const m = {
    Download: "bg-blue-500",
    Approve: "bg-teal-600",
    View: "bg-gray-400",
    Upload: "bg-green-500",
    "OCR Process": "bg-purple-500",
    "Login Attempt": "bg-red-500",
  };
  return m[a] || "bg-gray-400";
}
function auditIcon(a) {
  const m = {
    Download: "download",
    Approve: "check",
    View: "eye",
    Upload: "upload",
    "OCR Process": "cpu",
    "Login Attempt": "alert-triangle",
  };
  return m[a] || "activity";
}
function auditActionBadge(a) {
  const m = {
    Download: "bg-blue-100 text-blue-700",
    Approve: "bg-green-100 text-green-700",
    View: "bg-gray-100 text-gray-600",
    Upload: "bg-teal-100 text-teal-700",
    "OCR Process": "bg-purple-100 text-purple-700",
    "Login Attempt": "bg-red-100 text-red-600",
  };
  return m[a] || "bg-gray-100 text-gray-600";
}

function toggleTypeFilter(id) {
  const i = activeTypeFilters.value.indexOf(id);
  if (i > -1) activeTypeFilters.value.splice(i, 1);
  else activeTypeFilters.value.push(id);
}

function toggleAll(e) {
  allDocs.value.forEach((d) => (d.selected = e.target.checked));
}
function clearSelection() {
  allDocs.value.forEach((d) => (d.selected = false));
}

function previewDoc(doc) {
  selectedDoc.value = doc;
  previewPage.value = 1;
  showPreviewModal.value = true;
}

function shareDoc(doc) {
  selectedDoc.value = doc;
  shareLink.value = "";
  copied.value = false;
  showShareModal.value = true;
}

function generateLink() {
  shareLink.value = `https://dms.crm.id/s/${btoa(selectedDoc.value.name).slice(
    0,
    12
  )}?exp=${shareForm.value.expiry}${shareForm.value.password ? "&pwd=***" : ""}`;
}

function copyLink() {
  navigator.clipboard?.writeText(shareLink.value).catch(() => {});
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 2000);
}

function downloadDoc(doc) {
  showToast(`Downloading "${doc?.name || "document"}" with watermark`);
}

function showToast(msg) {
  toast.value = msg;
  setTimeout(() => {
    toast.value = "";
  }, 3000);
}

function triggerFakeUploads() {
  const files = [
    "Laporan_Keuangan_2024.pdf",
    "Rekening_Koran_Mandiri.pdf",
    "SIUP_2026.pdf",
  ];
  uploads.value = files.map((name) => ({ name, progress: 0 }));
  uploads.value.forEach((u, i) => {
    let p = 0;
    const iv = setInterval(() => {
      p += Math.random() * 30 + 10;
      u.progress = Math.min(Math.round(p), 100);
      if (u.progress === 100) clearInterval(iv);
    }, 200 + i * 100);
  });
}

function confirmUpload() {
  const done = uploads.value.filter((u) => u.progress === 100);
  if (done.length) {
    done.forEach((u) => {
      allDocs.value.unshift({
        id: Date.now() + Math.random(),
        name: u.name,
        ext: u.name.split(".").pop(),
        customer: "PT Maju Bersama",
        doc_type: "Financial",
        ocr: "Processing",
        ai_class: null,
        ai_conf: null,
        ai_folder: null,
        size: (Math.random() * 4 + 0.5).toFixed(1) + " MB",
        version: 1,
        expiry: null,
        status: "Active",
        uploaded: "Just now",
        tags: ["New"],
        selected: false,
      });
    });
    showUpload.value = false;
    uploads.value = [];
    showToast(`${done.length} file(s) uploaded — OCR processing started`);
  }
}

function generateDoc(tpl) {
  showToast(`Generating "${tpl.name}" — merging customer data...`);
  setTimeout(
    () => showToast(`"${tpl.name}" generated and saved to Agreements folder`),
    1500
  );
}
</script>

<style scoped>
.field-select {
  @apply w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 bg-white transition-colors;
}
.field-input {
  @apply w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-colors;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
