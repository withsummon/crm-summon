import { createDocumentResource } from 'frappe-ui'
import { reactive, ref } from 'vue'

const settings = ref({})
const brand = reactive({})

const _settings = createDocumentResource({
  doctype: 'FCRM Settings',
  name: 'FCRM Settings',
  onSuccess: (data) => {
    settings.value = data
    getSettings().setupBrand()
    return data
  },
})

export function getSettings() {
  function setupBrand() {
    brand.name = settings.value?.brand_name || 'BNI CRM'
    brand.logo = settings.value?.brand_logo || '/assets/crm/images/bni-logo.png'
    brand.favicon = settings.value?.favicon || '/assets/crm/images/bni-logo.png'
  }

  return {
    _settings,
    settings,
    brand,
    setupBrand,
  }
}
