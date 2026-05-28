import { watch } from 'vue'

export function loadPersisted(key, fallback) {
  if (typeof localStorage === 'undefined') return fallback
  try {
    const raw = localStorage.getItem(key)
    if (raw == null) return fallback
    const parsed = JSON.parse(raw)
    return parsed == null ? fallback : parsed
  } catch {
    return fallback
  }
}

export function persistRef(key, source) {
  watch(
    source,
    (val) => {
      try {
        localStorage.setItem(key, JSON.stringify(val))
      } catch {}
    },
    { deep: true },
  )
}

export function clearPersisted(key) {
  try {
    localStorage.removeItem(key)
  } catch {}
}
