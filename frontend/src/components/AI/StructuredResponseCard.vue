<template>
  <div class="space-y-3 text-sm leading-6" :class="{ 'text-xs': compact }">
    <section class="rounded-lg border border-primary-100 bg-primary-50/60 p-3">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <div class="text-sm font-bold text-slate-900">{{ resolved.title || __('Analisis AI') }}</div>
          <p class="mt-1 whitespace-pre-wrap text-slate-700">{{ resolved.executive_summary || '-' }}</p>
        </div>
        <span class="inline-flex items-center rounded-md border border-primary-200 bg-white px-2 py-0.5 text-[11px] font-semibold text-primary-700">
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
          <FeatherIcon name="check-circle" class="mt-1 h-3.5 w-3.5 shrink-0 text-primary-600" />
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

const PREFERRED_TEXT_KEYS = [
  'title',
  'summary',
  'executive_summary',
  'description',
  'rationale',
  'reasoning',
  'recommendation',
  'next_step',
  'mitigation',
  'content',
  'text',
  'value',
  'label',
]

function cleanDisplayText(value) {
  if (value === null || value === undefined) return ''
  if (typeof value === 'object') return formatJsonAsText(value)

  const text = String(value).trim()
  if (!text) return ''

  const parsed = parseEmbeddedJson(text)
  if (parsed) return formatJsonAsText(parsed)

  return stripMarkdown(text)
}

function stripMarkdown(text) {
  return String(text || '')
    .replace(/```(?:json)?\s*/gi, '')
    .replace(/```/g, '')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/^>\s+/gm, '')
    .replace(/`(.+?)`/g, '$1')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function parseEmbeddedJson(text) {
  const trimmed = String(text || '').trim()
  if (!trimmed) return null

  const fenced = trimmed.match(/```(?:json)?\s*([\s\S]*?)\s*```/i)
  if (fenced) {
    const parsed = parseJsonCandidate(fenced[1])
    if (parsed) return parsed
  }

  return parseJsonCandidate(trimmed)
}

function parseJsonCandidate(candidate) {
  const text = String(candidate || '').trim()
  if (!text) return null
  try {
    const parsed = JSON.parse(text)
    if (parsed && typeof parsed === 'object') return parsed
  } catch {
    // continue with embedded object extraction
  }

  const objectStart = text.indexOf('{')
  const arrayStart = text.indexOf('[')
  const starts = [objectStart, arrayStart].filter((index) => index >= 0)
  if (!starts.length) return null

  const start = Math.min(...starts)
  const opener = text[start]
  const closer = opener === '{' ? '}' : ']'
  let depth = 0
  let inString = false
  let escape = false

  for (let index = start; index < text.length; index += 1) {
    const char = text[index]
    if (escape) {
      escape = false
      continue
    }
    if (char === '\\') {
      escape = true
      continue
    }
    if (char === '"') {
      inString = !inString
      continue
    }
    if (inString) continue
    if (char === opener) depth += 1
    if (char === closer) depth -= 1
    if (depth === 0) {
      try {
        const parsed = JSON.parse(text.slice(start, index + 1))
        return parsed && typeof parsed === 'object' ? parsed : null
      } catch {
        return null
      }
    }
  }
  return null
}

function formatJsonAsText(value) {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return stripMarkdown(value)
  if (typeof value !== 'object') return String(value)
  if (Array.isArray(value)) {
    return value.map((item) => formatJsonAsText(item)).filter(Boolean).join('\n')
  }

  const preferred = PREFERRED_TEXT_KEYS
    .filter((key) => value[key] !== undefined && value[key] !== null && value[key] !== '')
    .map((key) => formatJsonAsText(value[key]))
    .filter(Boolean)
  const meaningfulKeys = Object.entries(value)
    .filter(([key, itemValue]) => !key.startsWith('_') && itemValue !== null && itemValue !== undefined && itemValue !== '')
    .map(([key]) => key)
  if (preferred.length && meaningfulKeys.every((key) => PREFERRED_TEXT_KEYS.includes(key))) {
    return preferred.join('\n')
  }

  const parts = []
  for (const [key, itemValue] of Object.entries(value)) {
    if (key.startsWith('_') || itemValue === null || itemValue === undefined || itemValue === '') continue
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    const formatted = formatJsonAsText(itemValue)
    if (formatted) parts.push(`${label}: ${formatted}`)
  }
  return parts.join('\n')
}

function cleanList(value) {
  if (!value) return []
  const list = Array.isArray(value) ? value : [value]
  return list.map((item) => cleanDisplayText(item)).filter(Boolean)
}

function cleanRecord(record) {
  const cleaned = {}
  for (const [key, value] of Object.entries(record || {})) {
    if (Array.isArray(value)) {
      cleaned[key] = cleanList(value)
    } else if (value && typeof value === 'object') {
      cleaned[key] = cleanDisplayText(value)
    } else {
      cleaned[key] = cleanDisplayText(value)
    }
  }
  return cleaned
}

function cleanAction(action) {
  return {
    ...action,
    title: cleanDisplayText(action?.title),
    risk_level: cleanDisplayText(action?.risk_level || 'low'),
    payload: {
      ...(action?.payload || {}),
      title: cleanDisplayText(action?.payload?.title),
      description: cleanDisplayText(action?.payload?.description),
    },
  }
}

const resolved = computed(() => {
  if (!props.response) {
    return {
      title: __('Output AI'),
      executive_summary: cleanDisplayText(props.fallback) || __('Tidak ada output terstruktur.'),
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
    title: cleanDisplayText(raw.title),
    executive_summary: cleanDisplayText(raw.executive_summary),
    sections: (raw.sections || []).map((s) => ({
      ...s,
      title: cleanDisplayText(s.title),
      summary: cleanDisplayText(s.summary),
      items: cleanList(s.items),
      metrics: (s.metrics || []).map((metric) => ({
        ...metric,
        label: cleanDisplayText(metric.label),
        value: cleanDisplayText(metric.value),
      })),
    })),
    recommendations: (raw.recommendations || []).map(cleanRecord),
    risks: (raw.risks || []).map(cleanRecord),
    actions: (raw.actions || []).map(cleanAction),
    sources: (raw.sources || []).map((source) => ({
      ...source,
      title: cleanDisplayText(source.title),
      excerpt: cleanDisplayText(source.excerpt),
    })),
    limitations: cleanList(raw.limitations),
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
  return 'bg-primary-50 text-primary-700 border-primary-100'
}

function actionLabel(action) {
  return String(action._action || action.title || __('Action')).replaceAll('_', ' ')
}
</script>
