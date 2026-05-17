<template>
  <Dialog
    v-model="show"
    :options="{
      title: __('Lead Generation in Progress'),
      size: 'md',
    }"
  >
    <template #body-content>
      <div class="flex flex-col items-center gap-8 py-10">
        <!-- Animated Icon Container with Ripples -->
        <div class="relative h-32 w-32 flex items-center justify-center">
          <div class="absolute inset-0 animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite] rounded-full bg-primary-400 opacity-20"></div>
          <div class="absolute inset-2 animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite_0.5s] rounded-full bg-primary-500 opacity-30"></div>
          
          <div class="relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-primary-50 to-primary-100 shadow-xl shadow-primary-500/20 border border-primary-200 z-10 overflow-hidden">
            <!-- Shimmer effect across the circle -->
            <div class="absolute inset-0 bg-gradient-to-tr from-transparent via-white to-transparent opacity-50 animate-[shimmer_2s_infinite]"></div>
            
            <FeatherIcon 
              name="cpu" 
              class="h-10 w-10 text-primary-600 animate-pulse relative z-20" 
            />
          </div>
        </div>

        <div class="w-full space-y-6 px-4">
          <div class="text-center transition-all duration-300">
            <h3 class="text-xl font-bold text-gray-900 tracking-tight">
              {{ statusMessage }}
            </h3>
            <p class="mt-1.5 text-sm text-gray-500 font-medium">
              {{ subMessage }}
            </p>
          </div>

          <!-- Premium Progress Bar -->
          <div class="relative pt-2">
            <div class="flex mb-3 items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="flex h-6 w-6 items-center justify-center rounded-full bg-primary-100">
                  <FeatherIcon name="zap" class="h-3 w-3 text-primary-600 animate-pulse" />
                </div>
                <span class="text-sm font-bold text-gray-800">
                  {{ Math.round(progress) }}%
                </span>
              </div>
              <div class="text-right">
                <span class="text-sm font-bold text-primary-600 bg-primary-50 px-3 py-1 rounded-full border border-primary-100">
                  {{ processedCount }} <span class="text-primary-400 font-medium mx-0.5">/</span> {{ totalCount || '...' }} Leads
                </span>
              </div>
            </div>
            <div class="overflow-hidden h-3 mb-4 text-xs flex rounded-full bg-gray-100 shadow-inner">
              <div
                :style="`width: ${progress}%`"
                class="flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-700 ease-out relative"
              >
                <!-- Animated highlight inside progress bar -->
                <div class="absolute top-0 left-0 bottom-0 w-full bg-gradient-to-r from-transparent via-white/30 to-transparent animate-[shimmer_1.5s_infinite]"></div>
              </div>
            </div>
          </div>

          <!-- Terminal-style Status Ticker -->
          <div class="flex items-center gap-3 py-3 px-5 rounded-xl bg-gray-900 border border-gray-800 shadow-lg relative overflow-hidden">
            <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-primary-400 to-primary-600"></div>
            <div class="h-2 w-2 rounded-full bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.8)] animate-pulse"></div>
            <p class="text-xs font-mono text-green-400/90 truncate tracking-wide">
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
  'SCANNING_WEB_GRAPH...',
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
  }, 1000)

  statusInterval = setInterval(() => {
    const progressFactor = props.progress > 0 ? (props.progress / 100) : 0
    const flowIdx = Math.min(Math.floor(progressFactor * statusFlow.length), statusFlow.length - 1)
    statusMessage.value = statusFlow[flowIdx].status
    subMessage.value = statusFlow[flowIdx].sub
  }, 2500)
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
