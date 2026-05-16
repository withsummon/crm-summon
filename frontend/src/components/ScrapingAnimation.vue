<template>
  <Dialog
    v-model="show"
    :options="{
      title: __('Lead Generation in Progress'),
      size: 'md',
    }"
  >
    <template #body-content>
      <div class="flex flex-col items-center gap-6 py-8">
        <!-- Animated Icon Container -->
        <div class="relative h-24 w-24 flex items-center justify-center">
          <div class="absolute inset-0 animate-ping rounded-full bg-indigo-100 opacity-75"></div>
          <div class="relative flex h-20 w-20 items-center justify-center rounded-full bg-indigo-50 shadow-sm border border-indigo-100">
            <FeatherIcon 
              name="cpu" 
              class="h-10 w-10 text-indigo-600 animate-pulse" 
            />
          </div>
        </div>

        <div class="w-full space-y-4">
          <div class="text-center">
            <h3 class="text-lg font-bold text-ink-gray-9 tracking-tight">
              {{ statusMessage }}
            </h3>
            <p class="mt-1 text-sm text-ink-gray-5 font-medium">
              {{ subMessage }}
            </p>
          </div>

          <!-- Progress Bar Container -->
          <div class="relative pt-1">
            <div class="flex mb-2 items-center justify-between">
              <div>
                <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-100">
                  {{ Math.round(progress) }}%
                </span>
              </div>
              <div class="text-right">
                <span class="text-xs font-semibold inline-block text-indigo-600">
                  {{ processedCount }} / {{ totalCount || '...' }} Leads
                </span>
              </div>
            </div>
            <div class="overflow-hidden h-2 mb-4 text-xs flex rounded-full bg-indigo-50 border border-indigo-100/50">
              <div
                :style="`width: ${progress}%`"
                class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500 transition-all duration-500 ease-out relative"
              >
                <!-- Animated highlight -->
                <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-[shimmer_2s_infinite]"></div>
              </div>
            </div>
          </div>

          <!-- Status Ticker -->
          <div class="flex items-center justify-center gap-3 py-2 px-4 rounded-xl bg-surface-gray-2 border border-gray-100 shadow-inner">
            <div class="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
            <p class="text-xs font-mono text-ink-gray-7 truncate">
              {{ tickerMessage }}
            </p>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Dialog, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  modelValue: Boolean,
  progress: {
    type: Number,
    default: 0
  },
  totalCount: {
    type: Number,
    default: 0
  },
  processedCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue'])

const show = ref(props.modelValue)
watch(() => props.modelValue, (val) => show.value = val)
watch(show, (val) => emit('update:modelValue', val))

const statusMessage = ref('Initializing Engine...')
const subMessage = ref('Connecting to high-speed data nodes')
const tickerMessage = ref('BOOT_SYSTEM_OK')

const tickers = [
  'SCANNING_LINKEDIN_GRAPH...',
  'EXTRACTING_COMPANY_META...',
  'RESOLVING_CONTACT_IDENTITIES...',
  'VALIDATING_EMAIL_REPUTATION...',
  'BYPASSING_GATEKEEPERS...',
  'FETCHING_INDUSTRY_TRENDS...',
  'SYNCING_TO_SUMMON_DB...',
  'OPTIMIZING_DATA_STRUCTURE...',
]

const statusFlow = [
  { status: 'Searching Nodes', sub: 'Scanning global lead databases' },
  { status: 'Scraping Data', sub: 'Extracting contact and organization info' },
  { status: 'AI Enrichment', sub: 'Enhancing profiles with intelligent data' },
  { status: 'Syncing Leads', sub: 'Storing validated leads into your CRM' },
]

let tickerInterval
let statusInterval

onMounted(() => {
  tickerInterval = setInterval(() => {
    tickerMessage.value = tickers[Math.floor(Math.random() * tickers.length)]
  }, 1200)

  statusInterval = setInterval(() => {
    const flowIdx = Math.floor((props.progress / 100) * (statusFlow.length - 1))
    statusMessage.value = statusFlow[flowIdx].status
    subMessage.value = statusFlow[flowIdx].sub
  }, 3000)
})

onUnmounted(() => {
  clearInterval(tickerInterval)
  clearInterval(statusInterval)
})
</script>

<style scoped>
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>
