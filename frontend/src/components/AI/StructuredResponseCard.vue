<template>
  <div class="space-y-3 text-sm leading-6" :class="{ 'text-xs': compact }">
    <section class="rounded-lg border border-teal-100 bg-teal-50/60 p-3">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <div class="text-sm font-bold text-slate-900">{{ resolved.title || __('Analisis AI') }}</div>
          <p class="mt-1 whitespace-pre-wrap text-slate-700">{{ resolved.executive_summary || '-' }}</p>
        </div>
        <span class="inline-flex items-center rounded-md border border-teal-200 bg-white px-2 py-0.5 text-[11px] font-semibold text-teal-700">
          {{ confidence }}%
        </span>
      </div>
    </section>

    <section v-for="section in resolved.sections || []" :key="section.title" class="rounded-lg border border-slate-200 bg-white p-3">
      <div class="text-xs font-bold uppercase tracking-wide text-slate-500">{{ section.title || __('Analisis') }}</div>
      <p v-if="section.summary" class="mt-2 whitespace-pre-wrap text-slate-700">{{ section.summary }}</p>
      <div v-if="section.metrics?.length" class="mt-3 grid gap-2 sm:grid-cols-2">
        <div v-for="metric in section.metrics" :key="`${section.title}-${metric.label}`" class="rounded-md border border-slate-100 bg-slate-50 p-2">
          <div class="text-[11px] font-semibold uppercase tracking-wide text-slate-500">{{ metric.label || __('Metrik') }}</div>
          <div class="mt-1 font-bold text-slate-900">{{ metric.value || '-' }}</div>
        </div>
      </div>
      <ul v-if="section.items?.length" class="mt-3 space-y-1.5">
        <li v-for="item in section.items" :key="item" class="flex gap-2 text-slate-700">
          <FeatherIcon name="check-circle" class="mt-1 h-3.5 w-3.5 shrink-0 text-teal-600" />
          <span>{{ item }}</span>
        </li>
      </ul>
    </section>

    <section v-if="resolved.recommendations?.length" class="rounded-lg border border-emerald-100 bg-emerald-50/50 p-3">
      <div class="text-xs font-bold uppercase tracking-wide text-emerald-700">{{ __('Rekomendasi') }}</div>
      <div class="mt-2 space-y-2">
        <div v-for="item in resolved.recommendations" :key="item.title || item.recommendation" class="rounded-md bg-white p-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-semibold text-slate-900">{{ item.title || item.recommendation || __('Rekomendasi') }}</span>
            <span class="inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold" :class="priorityTheme(item.priority)">
              {{ item.priority || 'medium' }}
            </span>
          </div>
          <p v-if="item.rationale" class="mt-1 text-slate-600">{{ item.rationale }}</p>
          <p v-if="item.next_step" class="mt-1 font-medium text-emerald-800">{{ __('Langkah berikut') }}: {{ item.next_step }}</p>
        </div>
      </div>
    </section>

    <section v-if="resolved.risks?.length" class="rounded-lg border border-red-100 bg-red-50/50 p-3">
      <div class="text-xs font-bold uppercase tracking-wide text-red-700">{{ __('Risiko') }}</div>
      <div class="mt-2 space-y-2">
        <div v-for="risk in resolved.risks" :key="risk.title || risk.description" class="rounded-md bg-white p-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-semibold text-slate-900">{{ risk.title || __('Risiko') }}</span>
            <span class="inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold" :class="priorityTheme(risk.severity)">
              {{ risk.severity || 'medium' }}
            </span>
          </div>
          <p v-if="risk.description" class="mt-1 text-slate-600">{{ risk.description }}</p>
          <p v-if="risk.mitigation" class="mt-1 font-medium text-red-800">{{ __('Mitigasi') }}: {{ risk.mitigation }}</p>
        </div>
      </div>
    </section>

    <section v-if="resolved.actions?.length" class="rounded-lg border border-blue-100 bg-blue-50/50 p-3">
      <div class="text-xs font-bold uppercase tracking-wide text-blue-700">{{ __('Action Plan') }}</div>
      <div class="mt-2 space-y-2">
        <div v-for="action in resolved.actions" :key="action._action || action.title" class="rounded-md bg-white p-2">
          <div class="flex items-center justify-between gap-2">
            <span class="font-semibold text-slate-900">{{ actionLabel(action) }}</span>
            <span class="inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold" :class="priorityTheme(action.risk_level || 'low')">
              {{ action.risk_level || 'low' }}
            </span>
          </div>
          <p v-if="action.payload?.title" class="mt-1 text-slate-600">{{ action.payload.title }}</p>
          <p v-if="action.payload?.description" class="mt-1 text-slate-500">{{ action.payload.description }}</p>
        </div>
      </div>
    </section>

    <section v-if="resolved.sources?.length" class="rounded-lg border border-slate-200 bg-white p-3">
      <div class="text-xs font-bold uppercase tracking-wide text-slate-500">{{ __('Sumber') }}</div>
      <div class="mt-2 space-y-2">
        <div v-for="source in resolved.sources.slice(0, 4)" :key="source.id || source.title" class="rounded-md border border-slate-100 bg-slate-50 p-2">
          <div class="font-semibold text-slate-900">{{ source.title || source.id || __('Sumber') }}</div>
          <div v-if="source.doctype || source.docname" class="mt-0.5 text-[11px] font-medium text-slate-500">
            {{ [source.doctype, source.docname].filter(Boolean).join(' · ') }}
          </div>
          <p v-if="source.excerpt" class="mt-1 line-clamp-3 text-slate-600">{{ source.excerpt }}</p>
        </div>
      </div>
    </section>

    <section v-if="resolved.limitations?.length" class="rounded-lg border border-amber-100 bg-amber-50 p-3 text-amber-900">
      <div class="text-xs font-bold uppercase tracking-wide">{{ __('Batasan Data') }}</div>
      <ul class="mt-2 space-y-1">
        <li v-for="item in resolved.limitations" :key="item">- {{ item }}</li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  response: { type: Object, default: null },
  fallback: { type: String, default: '' },
  compact: { type: Boolean, default: false },
})

function cleanDisplayText(text) {
  if (!text) return text
  // If it looks like JSON, format as readable text
  if (text.trim().startsWith('{') || text.trim().startsWith('[')) {
    try {
      const obj = JSON.parse(text)
      return formatJsonAsText(obj)
    } catch {
      // not valid JSON, continue
    }
  }
  // Strip markdown syntax
  return text
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/^-\s+/gm, '')
    .replace(/^\d+\.\s+/gm, '')
    .replace(/^>\s+/gm, '')
    .replace(/`(.+?)`/g, '$1')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function formatJsonAsText(obj) {
  if (typeof obj === 'string') return obj
  if (typeof obj !== 'object' || obj === null) return String(obj)
  const parts = []
  for (const [key, value] of Object.entries(obj)) {
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    if (Array.isArray(value)) {
      parts.push(`${label}: ${value.join(', ')}`)
    } else if (typeof value === 'object' && value !== null) {
      // skip nested objects for brevity; include reasoning directly
      if (key === 'reasoning') parts.push(`${label}: ${value}`)
    } else {
      parts.push(`${label}: ${value}`)
    }
  }
  return parts.join('\n')
}

const resolved = computed(() => {
  if (!props.response) {
    return {
      title: __('Output AI'),
      executive_summary: props.fallback || __('Tidak ada output terstruktur.'),
      confidence: 0,
      sections: [],
      recommendations: [],
      risks: [],
      actions: [],
      sources: [],
      limitations: props.fallback ? [__('Output ini berasal dari fallback plain text.')] : [],
    }
  }
  const raw = props.response
  return {
    ...raw,
    executive_summary: cleanDisplayText(raw.executive_summary),
    sections: (raw.sections || []).map((s) => ({
      ...s,
      summary: cleanDisplayText(s.summary),
    })),
  }
})

const confidence = computed(() => {
  const value = Math.round(Number(resolved.value.confidence || 0) * 100)
  return Number.isFinite(value) ? value : 0
})

function priorityTheme(value) {
  const normalized = String(value || '').toLowerCase()
  if (['high', 'tinggi', 'urgent', 'kritis'].includes(normalized)) return 'bg-red-50 text-red-700 border-red-100'
  if (['medium', 'sedang'].includes(normalized)) return 'bg-amber-50 text-amber-700 border-amber-100'
  if (['low', 'rendah'].includes(normalized)) return 'bg-slate-50 text-slate-600 border-slate-100'
  return 'bg-teal-50 text-teal-700 border-teal-100'
}

function actionLabel(action) {
  return String(action._action || action.title || __('Action')).replaceAll('_', ' ')
}
</script>
