<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Omnichannel Chat') }}
        </h1>
        <button
          class="flex size-8 items-center justify-center rounded-lg hover:bg-crm-surface"
          @click="showNewChat = true"
        >
          <FeatherIcon name="plus" class="size-4 text-crm-teal" />
        </button>
      </div>
    </div>

    <div class="flex gap-1 px-4 pb-2">
      <button
        v-for="ch in channels"
        :key="ch.key"
        class="flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium transition-colors"
        :class="activeChannel === ch.key
          ? 'bg-crm-teal text-white'
          : 'bg-white text-crm-text-secondary border border-crm-border hover:border-crm-teal/50'"
        @click="activeChannel = ch.key"
      >
        <FeatherIcon :name="ch.icon" class="size-3.5" />
        {{ ch.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-1">
      <div v-if="loading" class="space-y-3 pt-2">
        <div class="animate-pulse rounded-xl bg-crm-surface h-16 w-full" />
        <div class="animate-pulse rounded-xl bg-crm-surface h-14 w-full" />
        <div class="animate-pulse rounded-xl bg-crm-surface h-16 w-full" />
      </div>

      <div v-else-if="error" class="py-16 text-center">
        <FeatherIcon name="alert-circle" class="size-10 text-red-400 mx-auto mb-2" />
        <p class="text-sm font-medium text-crm-text">{{ error }}</p>
        <button class="mt-3 text-xs text-crm-teal font-medium" @click="loadConversations">
          {{ __('Coba lagi') }}
        </button>
      </div>

      <template v-else>
        <div
          v-for="chat in filteredChats"
          :key="chat.id"
          class="rounded-xl bg-white p-3 border border-crm-border cursor-pointer active:scale-[0.99] transition-transform"
          @click="openChat(chat)"
        >
          <div class="flex items-start gap-3">
            <div
              class="flex size-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold"
              :class="chat.avatarBg"
            >
              {{ chat.initials }}
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center justify-between">
                <p class="text-sm font-semibold text-crm-text truncate">{{ chat.name }}</p>
                <p class="text-[10px] text-crm-muted shrink-0">{{ chat.lastTime }}</p>
              </div>
              <p class="text-xs text-crm-text-secondary truncate mt-0.5">{{ chat.lastMessage }}</p>
              <div class="flex items-center gap-2 mt-1">
                <span class="rounded-full px-1.5 py-0.5 text-[9px] font-medium" :class="channelBadge(chat.channel)">
                  {{ chat.channel }}
                </span>
                <span v-if="chat.unread" class="size-5 rounded-full bg-crm-teal text-[9px] font-semibold text-white flex items-center justify-center">
                  {{ chat.unread }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!filteredChats.length" class="py-16 text-center">
          <FeatherIcon name="message-circle" class="size-10 text-crm-muted mx-auto mb-2" />
          <p class="text-sm font-medium text-crm-text">{{ __('Tidak ada percakapan') }}</p>
          <p class="text-xs text-crm-text-secondary mt-1">{{ __('Mulai percakapan baru dengan nasabah') }}</p>
        </div>
      </template>
    </div>

    <TransitionRoot :show="showNewChat">
      <div class="fixed inset-0 z-50 flex items-end">
        <TransitionChild
          as="template"
          enter="transition-opacity duration-200"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="transition-opacity duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black/30" @click="showNewChat = false" />
        </TransitionChild>
        <TransitionChild
          as="template"
          enter="transition-transform duration-300 ease-out"
          enter-from="translate-y-full"
          enter-to="translate-y-0"
          leave="transition-transform duration-200 ease-in"
          leave-from="translate-y-0"
          leave-to="translate-y-full"
        >
          <div class="relative w-full rounded-t-2xl bg-white px-4 pb-8 pt-5 shadow-xl">
            <div class="mx-auto mb-4 h-1 w-10 rounded-full bg-gray-300" />
            <h2 class="text-base font-semibold text-crm-text mb-4">{{ __('Percakapan Baru') }}</h2>
            <div class="space-y-3">
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('Channel') }}</label>
                <select v-model="newChat.channel" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal">
                  <option v-for="ch in channels" :key="ch.key" :value="ch.key">{{ ch.label }}</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('Nasabah') }}</label>
                <input v-model="newChat.contact" type="text" :placeholder="__('Nama atau nomor telepon')" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal" />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('Pesan') }}</label>
                <textarea v-model="newChat.message" rows="3" :placeholder="__('Tulis pesan...')" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal resize-none" />
              </div>
              <Button variant="solid" class="w-full" :disabled="!newChat.contact || sending" @click="sendNewChat">
                {{ __('Kirim') }}
              </Button>
            </div>
          </div>
        </TransitionChild>
      </div>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'
import { TransitionRoot, TransitionChild } from '@headlessui/vue'
import { timeAgo } from '@/utils'

const activeChannel = ref('all')
const showNewChat = ref(false)
const chats = ref([])
const newChat = ref({ channel: 'WhatsApp', contact: '', message: '' })
const loading = ref(true)
const error = ref('')
const sending = ref(false)

const channels = [
  { key: 'all', label: __('Semua'), icon: 'message-circle' },
  { key: 'WhatsApp', label: 'WhatsApp', icon: 'message-circle' },
  { key: 'Telegram', label: 'Telegram', icon: 'send' },
  { key: 'Email', label: 'Email', icon: 'mail' },
]

const filteredChats = computed(() => {
  if (activeChannel.value === 'all') return chats.value
  return chats.value.filter((c) => c.channel === activeChannel.value)
})

async function loadConversations() {
  loading.value = true
  error.value = ''
  try {
    const result = await call('crm.api.omnichannel.get_conversations', {
      channel: activeChannel.value === 'all' ? null : activeChannel.value,
      limit: 50,
    })
    chats.value = (result.rows || []).map(c => ({
      id: c.name,
      name: c.subject || c.customer_name || c.reference_name || __('Unknown'),
      channel: c.channel || 'WhatsApp',
      lastMessage: c.last_message_preview || '',
      lastTime: c.last_message_at ? timeAgo(c.last_message_at) : '',
      unread: c.unread_count || 0,
      initials: (c.customer_name || c.subject || '?').substring(0, 2).toUpperCase(),
      avatarBg: channelBg(c.channel || 'WhatsApp'),
    }))
  } catch (err) {
    error.value = err.messages?.[0] || __('Gagal memuat percakapan')
  } finally {
    loading.value = false
  }
}

function channelBg(channel) {
  const map = { WhatsApp: 'bg-green-50 text-green-600', Telegram: 'bg-blue-50 text-blue-600', Email: 'bg-amber-50 text-amber-600' }
  return map[channel] || 'bg-gray-50 text-gray-700'
}

function channelBadge(channel) {
  const map = { WhatsApp: 'bg-green-50 text-green-700', Telegram: 'bg-blue-50 text-blue-700', Email: 'bg-amber-50 text-amber-700' }
  return map[channel] || 'bg-gray-50 text-gray-700'
}

function openChat(chat) {
  toast.info(__('Membuka chat dengan {0}', [chat.name]))
}

async function sendNewChat() {
  if (!newChat.value.contact) return
  sending.value = true
  try {
    await call('crm.api.omnichannel.send_message', {
      channel: newChat.value.channel,
      to: newChat.value.contact,
      content: newChat.value.message || '',
    })
    showNewChat.value = false
    newChat.value = { channel: 'WhatsApp', contact: '', message: '' }
    toast.success(__('Pesan berhasil dikirim'))
    loadConversations()
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal mengirim pesan'))
  } finally {
    sending.value = false
  }
}

onMounted(loadConversations)

watch(activeChannel, loadConversations)
</script>
