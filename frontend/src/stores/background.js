import { defineStore } from 'pinia'
import { ref } from 'vue'

export const backgroundStore = defineStore('crm-background', () => {
  const isScraping = ref(false)
  const scrapingProgress = ref(0)
  const scrapingTotal = ref(0)
  const scrapingProcessed = ref(0)
  const lastScrapedLead = ref(null)

  function startScraping(total = 10) {
    isScraping.value = true
    scrapingProgress.value = 0
    scrapingTotal.value = total
    scrapingProcessed.value = 0
    lastScrapedLead.value = null
  }

  function updateProgress(processed, lead = null) {
    scrapingProcessed.value = processed
    scrapingProgress.value = Math.min(Math.floor((processed / scrapingTotal.value) * 100), 100)
    if (lead) {
      lastScrapedLead.value = lead
    }
  }

  function stopScraping() {
    isScraping.value = false
    scrapingProgress.value = 100
  }

  return {
    isScraping,
    scrapingProgress,
    scrapingTotal,
    scrapingProcessed,
    lastScrapedLead,
    startScraping,
    updateProgress,
    stopScraping,
  }
})
