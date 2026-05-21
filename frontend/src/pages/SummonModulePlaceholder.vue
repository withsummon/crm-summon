<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-9 w-9 items-center justify-center rounded bg-summon-charcoal text-white"
          >
            <FeatherIcon :name="module?.icon || 'grid'" class="h-4 w-4" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-base font-semibold text-ink-gray-9">
              {{ module?.label || __('Module') }}
            </h1>
            <p class="mt-0.5 text-sm text-ink-gray-5">
              {{ module?.sheet || __('SUMMON Module') }}
            </p>
          </div>
        </div>
      </template>
      <template #right-header>
        <Badge
          v-if="module"
          :label="statusLabel"
          :theme="statusTheme"
          variant="subtle"
        />
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto">
      <div v-if="module" class="mx-auto flex max-w-4xl flex-col gap-8 px-6 py-8">
        <section class="space-y-4 border-b border-outline-gray-1 pb-8">
          <div class="flex flex-wrap items-center gap-2">
            <Badge :label="module.priority" variant="subtle" />
            <Badge :label="module.group" variant="subtle" theme="gray" />
          </div>
          <div class="space-y-3">
            <h2 class="text-2xl font-semibold text-ink-gray-9">
              {{ module.label }}
            </h2>
            <p class="max-w-3xl text-base leading-6 text-ink-gray-6">
              {{ module.description }}
            </p>
          </div>
          <div
            class="rounded border border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-sm text-ink-gray-6"
          >
            {{
              __(
                'This module is listed in the SUMMON feature workbook. Navigation is available now; full business implementation follows the detailed sheet specification.',
              )
            }}
          </div>
        </section>

        <section class="space-y-4">
          <div>
            <h3 class="text-base font-semibold text-ink-gray-9">
              {{ __('Feature Scope') }}
            </h3>
            <p class="mt-1 text-sm text-ink-gray-5">
              {{ __('First-level features captured from the module sheet.') }}
            </p>
          </div>
          <div class="grid gap-2 sm:grid-cols-2">
            <div
              v-for="feature in module.features"
              :key="feature"
              class="flex items-center gap-2 rounded border border-outline-gray-1 px-3 py-2 text-sm text-ink-gray-7"
            >
              <FeatherIcon name="check-circle" class="h-4 w-4 text-ink-gray-4" />
              <span>{{ feature }}</span>
            </div>
          </div>
        </section>

        <section class="flex flex-wrap items-center gap-3 pt-2">
          <Button
            v-if="module.status !== 'planned'"
            :label="__('Open Module')"
            variant="solid"
            @click="openModule"
          />
          <Button
            :label="__('Back to Dashboard')"
            variant="subtle"
            @click="$router.push({ name: 'CRM Core Dashboard' })"
          />
        </section>
      </div>

      <div
        v-else
        class="grid h-full place-items-center px-6 py-16 text-center text-ink-gray-5"
      >
        <div class="space-y-4">
          <h2 class="text-xl font-semibold text-ink-gray-8">
            {{ __('Module not found') }}
          </h2>
          <Button
            :label="__('Back to Dashboard')"
            variant="solid"
            @click="$router.push({ name: 'CRM Core Dashboard' })"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { getSummonModule } from '@/data/summonModules'
import { Badge, FeatherIcon } from 'frappe-ui'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const module = computed(() => getSummonModule(route.params.moduleSlug))

const statusLabel = computed(() => {
  if (module.value?.status === 'available') return __('Available')
  if (module.value?.status === 'partial') return __('Partial')
  return __('Planned')
})

const statusTheme = computed(() => {
  if (module.value?.status === 'available') return 'green'
  if (module.value?.status === 'partial') return 'blue'
  return 'gray'
})

function openModule() {
  if (!module.value?.href) return
  window.location.href = module.value.href
}
</script>
