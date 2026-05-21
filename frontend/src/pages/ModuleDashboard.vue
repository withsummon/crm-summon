<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-9 w-9 items-center justify-center rounded-[12px]"
            :style="{ background: groupGradient }"
          >
            <FeatherIcon :name="groupIcon" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-ink-gray-9">
              {{ __(moduleGroup) }} {{ __('Dashboard') }}
            </h1>
          </div>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto">
      <div class="mx-auto max-w-5xl px-6 py-10">
        <!-- Hero Section -->
        <div
          class="rounded-[22px] p-8 text-center"
          :style="{ background: heroBg }"
        >
          <div
            class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/30 backdrop-blur-sm"
          >
            <FeatherIcon :name="groupIcon" class="h-8 w-8 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-white">
            {{ __(moduleGroup) }}
          </h2>
          <p class="mt-2 text-base text-white/80">
            {{ __('Dashboard for this module is coming soon.') }}
          </p>
          <p class="mt-1 text-sm text-white/60">
            {{
              __(
                'Explore the available modules below while we build your dashboard experience.',
              )
            }}
          </p>
        </div>

        <!-- Module List -->
        <div class="mt-8">
          <h3 class="mb-4 text-base font-semibold text-ink-gray-8">
            {{ __('Available Modules') }}
          </h3>
          <div class="grid gap-3 sm:grid-cols-2">
            <a
              v-for="mod in groupModules"
              :key="mod.sheet"
              :href="mod.href"
              class="flex items-center gap-4 rounded-[14px] border border-outline-gray-1 p-4 transition-all duration-200 hover:border-primary-300 hover:shadow-md"
            >
              <div
                class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-surface-gray-2"
              >
                <FeatherIcon :name="mod.icon || 'grid'" class="h-5 w-5 text-ink-gray-6" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <span class="truncate text-sm font-medium text-ink-gray-9">
                    {{ __(mod.label) }}
                  </span>
                  <Badge
                    v-if="mod.status !== 'available'"
                    :label="
                      mod.status === 'partial' ? __('Partial') : __('Planned')
                    "
                    variant="subtle"
                    :theme="mod.status === 'partial' ? 'blue' : 'gray'"
                  />
                </div>
                <p class="mt-0.5 truncate text-xs text-ink-gray-5">
                  {{ __(mod.description) }}
                </p>
              </div>
              <FeatherIcon name="chevron-right" class="h-4 w-4 text-ink-gray-4" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { summonModules } from '@/data/summonModules'
import { Badge, FeatherIcon } from 'frappe-ui'
import { usePageMeta } from 'frappe-ui'
import { computed } from 'vue'

const props = defineProps({
  moduleGroup: {
    type: String,
    required: true,
  },
})

const groupModules = computed(() =>
  summonModules.filter((m) => m.group === props.moduleGroup),
)

const groupConfig = {
  'Lending & Risk': {
    icon: 'dollar-sign',
    gradient: 'linear-gradient(135deg, #6676ff, #b77cff)',
    heroBg: 'linear-gradient(135deg, #6676ff 0%, #b77cff 100%)',
  },
  Operations: {
    icon: 'settings',
    gradient: 'linear-gradient(135deg, #22c55e, #4ade80)',
    heroBg: 'linear-gradient(135deg, #22c55e 0%, #86efac 100%)',
  },
  'Admin & Platform': {
    icon: 'shield',
    gradient: 'linear-gradient(135deg, #8b5cf6, #c084fc)',
    heroBg: 'linear-gradient(135deg, #7c3aed 0%, #c084fc 100%)',
  },
  'Channels & Portal': {
    icon: 'message-square',
    gradient: 'linear-gradient(135deg, #f472b6, #ff5ec4)',
    heroBg: 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)',
  },
}

const config = computed(
  () =>
    groupConfig[props.moduleGroup] || {
      icon: 'grid',
      gradient: 'linear-gradient(135deg, #64748b, #94a3b8)',
      heroBg: 'linear-gradient(135deg, #475569 0%, #94a3b8 100%)',
    },
)

const groupIcon = computed(() => config.value.icon)
const groupGradient = computed(() => config.value.gradient)
const heroBg = computed(() => config.value.heroBg)

usePageMeta(() => {
  return { title: `${props.moduleGroup} Dashboard` }
})
</script>
