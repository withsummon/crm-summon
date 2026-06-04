<template>
  <Button
    :label="__(label)"
    :theme="buttonTheme"
    :variant="variant"
    :icon-left="icon"
    :disabled="disabled"
    v-bind="$attrs"
    @click.stop="emit('click', $event)"
    :class="{ 'btn-brand-primary': props.theme == 'brand' }"
  />
</template>
<script>
export function getButtonTheme(buttonColor) {
  const themeMap = {
    Primary: 'brand',
    Info: 'blue',
    Success: 'brand',
    Warning: 'gray',
    Danger: 'red',
  }
  return themeMap[buttonColor] || 'gray'
}

export function getButtonVariant(buttonColor) {
  const variantMap = {
    Primary: 'solid',
    Info: 'subtle',
    Success: 'solid',
    Warning: 'subtle',
    Danger: 'solid',
  }
  return variantMap[buttonColor] || 'subtle'
}
</script>

<script setup>
import { Button } from 'frappe-ui'
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  icon: { type: String, default: null },
  theme: { type: String, default: 'gray' },
  variant: { type: String, default: 'subtle' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])

const buttonTheme = computed(() =>
  props.theme == 'brand' ? 'gray' : props.theme
)
</script>
