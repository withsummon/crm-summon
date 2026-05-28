<template>
  <div class="flex h-full min-h-0 flex-col bg-surface-gray-1">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button
            class="flex h-8 w-8 items-center justify-center rounded-lg border border-crm-border bg-white text-crm-muted hover:text-purple-600 hover:border-purple-300 hover:bg-purple-50 transition-all"
            @click="router.push('/lending-risk/workflow-engine')"
          >
            <LucideArrowLeft class="h-4 w-4" />
          </button>
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px] shadow-sm"
            style="background: linear-gradient(135deg, #7c3aed, #c084fc)"
          >
            <LucideStore class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-base font-bold text-crm-text">{{ __('Workflow Marketplace') }}</h1>
        </div>
      </template>
    </LayoutHeader>

    <!-- Category Filter Bar & Search -->
    <div class="bg-white border-b border-crm-border px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      <div class="flex flex-wrap items-center gap-2 flex-1 min-w-0">
        <!-- Category Pills -->
        <button
          v-for="cat in categories"
          :key="cat"
          class="px-3 py-1.5 text-xs font-semibold rounded-full border transition-all"
          :class="[
            activeCategory === cat
              ? 'bg-purple-600 text-white border-purple-600 shadow-sm'
              : 'bg-white text-crm-muted border-crm-border hover:border-purple-300 hover:text-purple-600 hover:bg-purple-50'
          ]"
          @click="activeCategory = cat"
        >
          {{ __(cat) }}
        </button>
      </div>

      <!-- Search bar -->
      <div class="relative w-64">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="__('Search templates...')"
          class="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 bg-surface-gray-1"
        />
        <LucideSearch class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-crm-muted" />
      </div>
    </div>

    <!-- Template Grid -->
    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="filteredTemplates.length" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="tmpl in filteredTemplates"
          :key="tmpl.id"
          class="group relative flex flex-col rounded-xl bg-white shadow-sm border border-crm-border transition-all hover:shadow-md hover:border-purple-200"
        >
          <!-- Gradient Icon Header -->
          <div class="p-5 pb-0">
            <div class="flex items-start justify-between gap-3">
              <div
                class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br text-white shadow-sm"
                :class="tmpl.color"
              >
                <component :is="getIcon(tmpl.icon)" class="h-5 w-5" />
              </div>
              <div class="flex items-center gap-1.5">
                <!-- Category Badge -->
                <span class="rounded-full px-2.5 py-0.5 text-[10px] font-bold bg-purple-50 text-purple-700">
                  {{ __(tmpl.marketplaceCategory || 'Custom') }}
                </span>
                <!-- Node Count Badge -->
                <span class="rounded-full px-2 py-0.5 text-[10px] font-bold bg-gray-100 text-gray-600 flex items-center gap-1">
                  <LucideLayers class="h-2.5 w-2.5" />
                  {{ tmpl.nodes ? tmpl.nodes.length : 0 }}
                </span>
              </div>
            </div>

            <!-- Title -->
            <h3 class="mt-3 text-sm font-bold text-gray-800 group-hover:text-purple-600 transition-colors">
              {{ tmpl.title }}
            </h3>

            <!-- Description -->
            <p class="mt-1.5 text-[11px] text-crm-muted leading-normal line-clamp-2">
              {{ tmpl.description }}
            </p>
          </div>

          <!-- Footer -->
          <div class="mt-auto p-5 pt-4">
            <div class="pt-3 border-t border-gray-50">
              <button
                class="w-full flex items-center justify-center gap-2 px-4 py-2 text-xs font-bold text-white bg-gradient-to-r from-purple-600 to-violet-600 rounded-lg hover:from-purple-700 hover:to-violet-700 shadow-sm hover:shadow-md transition-all group-hover:translate-y-0 transform"
                @click="useTemplate(tmpl)"
              >
                <LucideDownload class="h-3.5 w-3.5" />
                {{ __('Use Template') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-crm-border shadow-sm p-8">
        <LucideStore class="h-16 w-16 text-purple-200 animate-bounce" />
        <h3 class="mt-4 text-sm font-bold text-gray-800">{{ __('No Templates Found') }}</h3>
        <p class="mt-1 text-xs text-crm-muted text-center max-w-sm">
          {{ __('Try adjusting your search query or category filter to find workflow templates.') }}
        </p>
        <button
          class="mt-6 px-4 py-2 text-xs font-bold text-purple-600 bg-purple-50 rounded-lg border border-purple-200 hover:bg-purple-100 transition-all"
          @click="activeCategory = 'All'; searchQuery = ''"
        >
          {{ __('Clear Filters') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePageMeta } from 'frappe-ui'

import LayoutHeader from '@/components/LayoutHeader.vue'
import { workflowTemplates as templates } from '../data/workflowTemplates'

// Lucide Icons
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideSearch from '~icons/lucide/search'
import LucideStore from '~icons/lucide/store'
import LucideDownload from '~icons/lucide/download'
import LucideLayers from '~icons/lucide/layers'
import LucideFile from '~icons/lucide/file'
import LucideUserCheck from '~icons/lucide/user-check'
import LucideShieldCheck from '~icons/lucide/shield-check'
import LucideFileText from '~icons/lucide/file-text'

const router = useRouter()

// Categories
const categories = ['All', 'Credit', 'Collection', 'KYC', 'Lead Management', 'Approval', 'Custom']
const activeCategory = ref('All')
const searchQuery = ref('')

// Icon resolver
function getIcon(iconName) {
  const iconMap = {
    LucideFile,
    LucideUserCheck,
    LucideShieldCheck,
    LucideFileText,
  }
  return iconMap[iconName] || LucideFile
}

// Filtered templates
const filteredTemplates = computed(() => {
  return templates.filter((tmpl) => {
    // Category filter
    if (activeCategory.value !== 'All') {
      const cat = tmpl.marketplaceCategory || 'Custom'
      if (cat !== activeCategory.value) return false
    }

    // Search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const titleMatch = (tmpl.title || '').toLowerCase().includes(query)
      const descMatch = (tmpl.description || '').toLowerCase().includes(query)
      const catMatch = (tmpl.marketplaceCategory || '').toLowerCase().includes(query)
      if (!titleMatch && !descMatch && !catMatch) return false
    }

    return true
  })
})

// Navigate with template pre-selected
function useTemplate(tmpl) {
  router.push(`/lending-risk/workflow-engine/new?template=${tmpl.id}`)
}

usePageMeta(() => ({ title: __('Workflow Marketplace') }))
</script>
