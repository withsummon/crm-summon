<template>
  <div
    class="crm-card crm-animate-in"
    :style="{ animationDelay: '300ms' }"
  >
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-[16px] font-semibold text-crm-text">
        {{ __('Most Leads Channels') }}
      </h3>
    </div>

    <!-- Today Section -->
    <div class="mb-5">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-[12px] font-semibold text-crm-muted uppercase tracking-wide">
          {{ __('Today') }}
        </span>
        <div class="flex-1 h-px bg-crm-border" />
      </div>

      <div
        v-for="(channel, idx) in todayChannels"
        :key="'today-' + channel.name"
        class="crm-channel-item crm-animate-in"
        :style="{ animationDelay: `${idx * 60 + 400}ms` }"
      >
        <!-- Icon + Name -->
        <div class="flex items-center gap-3">
          <div
            class="flex items-center justify-center w-9 h-9 rounded-xl shrink-0"
            :style="{ backgroundColor: channel.bgColor }"
          >
            <FeatherIcon
              :name="channel.icon"
              class="w-4 h-4"
              :style="{ color: channel.iconColor }"
            />
          </div>
          <span class="text-[14px] font-medium text-crm-text">
            {{ __(channel.name) }}
          </span>
        </div>

        <!-- Value -->
        <span class="text-[14px] font-bold text-crm-text">
          {{ channel.value.toLocaleString() }}
        </span>
      </div>
    </div>

    <!-- All Time Section -->
    <div>
      <div class="flex items-center gap-2 mb-3">
        <span class="text-[12px] font-semibold text-crm-muted uppercase tracking-wide">
          {{ __('All Time') }}
        </span>
        <div class="flex-1 h-px bg-crm-border" />
      </div>

      <div
        v-for="(channel, idx) in allTimeChannels"
        :key="'alltime-' + channel.name"
        class="crm-channel-item crm-animate-in"
        :style="{ animationDelay: `${idx * 60 + 650}ms` }"
      >
        <!-- Icon + Name -->
        <div class="flex items-center gap-3">
          <div
            class="flex items-center justify-center w-9 h-9 rounded-xl shrink-0"
            :style="{ backgroundColor: channel.bgColor }"
          >
            <FeatherIcon
              :name="channel.icon"
              class="w-4 h-4"
              :style="{ color: channel.iconColor }"
            />
          </div>
          <span class="text-[14px] font-medium text-crm-text">
            {{ __(channel.name) }}
          </span>
        </div>

        <!-- Value -->
        <span class="text-[14px] font-bold text-crm-text">
          {{ channel.value.toLocaleString() }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

const channelConfigs = [
  {
    name: 'Messenger',
    icon: 'message-circle',
    bgColor: '#D9F3F4',
    iconColor: '#008C95',
  },
  {
    name: 'Viber',
    icon: 'phone',
    bgColor: '#f3e8ff',
    iconColor: '#b77cff',
  },
  {
    name: 'WhatsApp',
    icon: 'message-square',
    bgColor: '#ecfdf5',
    iconColor: '#22c55e',
  },
  {
    name: 'Telegram',
    icon: 'send',
    bgColor: '#eef2ff',
    iconColor: '#6676ff',
  },
]

const todayChannels = channelConfigs.map((ch) => ({
  ...ch,
  value:
    ch.name === 'Messenger'
      ? 49789
      : ch.name === 'Viber'
        ? 57890
        : ch.name === 'WhatsApp'
          ? 44901
          : 53678,
}))

const allTimeChannels = channelConfigs.map((ch) => ({
  ...ch,
  value:
    ch.name === 'Messenger'
      ? 149789
      : ch.name === 'Viber'
        ? 257890
        : ch.name === 'WhatsApp'
          ? 344901
          : 153678,
}))
</script>
