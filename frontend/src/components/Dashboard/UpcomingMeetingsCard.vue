<template>
  <div
    class="crm-card crm-animate-in"
    :style="{ animationDelay: '200ms' }"
  >
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-[16px] font-semibold text-crm-text">
        {{ __('Upcoming Meeting') }}
      </h3>
      <Tooltip :text="__('View all meetings')">
        <button
          class="text-[13px] text-crm-teal font-medium hover:underline transition-colors"
        >
          {{ __('See All') }}
        </button>
      </Tooltip>
    </div>

    <!-- Meeting Groups -->
    <div v-for="(group, gIdx) in meetingGroups" :key="group.time" class="mb-4 last:mb-0">
      <!-- Time label -->
      <div class="flex items-center gap-2 mb-1">
        <span class="text-[12px] font-semibold text-crm-muted uppercase tracking-wide">
          {{ __(group.time) }}
        </span>
        <div class="flex-1 h-px bg-crm-border" />
      </div>

      <!-- Meeting items -->
      <div
        v-for="(meeting, mIdx) in group.meetings"
        :key="meeting.name"
        class="crm-meeting-item crm-animate-in"
        :style="{ animationDelay: `${(gIdx * 2 + mIdx) * 80 + 300}ms` }"
      >
        <!-- Icon -->
        <div
          class="flex items-center justify-center w-9 h-9 rounded-xl shrink-0"
          :class="meeting.iconBg"
        >
          <component
            :is="meeting.iconComponent"
            class="w-4 h-4"
            :class="meeting.iconColor"
          />
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <div class="text-[14px] font-semibold text-crm-text truncate">
            {{ __(meeting.name) }}
          </div>
          <div class="text-[12px] text-crm-muted truncate">
            {{ __(meeting.subtitle) }}
          </div>
        </div>

        <!-- Time badge -->
        <Badge
          :label="__(group.time)"
          variant="outline"
          size="sm"
          class="shrink-0"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Tooltip } from 'frappe-ui'
import { markRaw } from 'vue'
import LucideVideo from '~icons/lucide/video'
import LucideCalendar from '~icons/lucide/calendar'

const meetingGroups = [
  {
    time: 'In 30min',
    meetings: [
      {
        name: "Sam Saltman's Meeting",
        subtitle: 'Sales Team',
        iconComponent: markRaw(LucideVideo),
        iconBg: 'bg-crm-surface',
        iconColor: 'text-crm-teal',
      },
      {
        name: "Tom Harris's Meeting",
        subtitle: 'Product Development',
        iconComponent: markRaw(LucideCalendar),
        iconBg: 'bg-purple-50',
        iconColor: 'text-crm-purple',
      },
    ],
  },
  {
    time: 'In 2hr',
    meetings: [
      {
        name: "Rachel Nguyen's Meeting",
        subtitle: 'Client Success Review',
        iconComponent: markRaw(LucideVideo),
        iconBg: 'bg-blue-50',
        iconColor: 'text-crm-blue',
      },
      {
        name: "Emma Foster's Meeting",
        subtitle: 'Team Performance Update',
        iconComponent: markRaw(LucideCalendar),
        iconBg: 'bg-green-50',
        iconColor: 'text-crm-green',
      },
    ],
  },
]
</script>
