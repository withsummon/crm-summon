<template>
  <div
    class="crm-card crm-animate-in"
    :style="{ animationDelay: '250ms' }"
  >
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-[16px] font-semibold text-crm-text">
        {{ __('Latest Leads') }}
      </h3>
      <button
        class="text-[13px] text-crm-teal font-medium hover:underline transition-colors"
      >
        {{ __('See All') }}
      </button>
    </div>

    <!-- Lead items -->
    <div
      v-for="(lead, idx) in leads"
      :key="lead.name"
      class="crm-lead-item crm-animate-in"
      :style="{ animationDelay: `${idx * 60 + 350}ms` }"
    >
      <!-- Left: Avatar + Name -->
      <div class="flex items-center gap-3 min-w-0">
        <div
          class="flex items-center justify-center w-8 h-8 rounded-full text-[12px] font-bold text-white shrink-0"
          :style="{ backgroundColor: lead.color }"
        >
          {{ lead.initials }}
        </div>
        <span class="text-[14px] font-medium text-crm-text truncate">
          {{ __(lead.name) }}
        </span>
      </div>

      <!-- Right: Time -->
      <span class="text-[12px] text-crm-muted whitespace-nowrap shrink-0">
        {{ __(lead.time) }}
      </span>
    </div>
  </div>
</template>

<script setup>
const avatarColors = [
  '#ff8a1f',
  '#b77cff',
  '#6676ff',
  '#22c55e',
  '#ff5ec4',
  '#f59e0b',
]

function getInitials(name) {
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const leadsData = [
  { name: 'Silvia Zieme', time: 'Just Now' },
  { name: 'Luke King', time: '1 Minute Ago' },
  { name: 'Kim Ortiz', time: '2 Minute Ago' },
  { name: 'Ethan Carter', time: '4 Minute Ago' },
  { name: 'Liam Johnson', time: '8 Minute Ago' },
  { name: 'Noah Smith', time: '12 Minute Ago' },
]

const leads = leadsData.map((lead, idx) => ({
  ...lead,
  initials: getInitials(lead.name),
  color: avatarColors[idx % avatarColors.length],
}))
</script>
