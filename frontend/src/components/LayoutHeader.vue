<script setup>
import { ref, nextTick } from "vue";

const props = defineProps({
  stretchLeft: {
    type: Boolean,
    default: false,
  },
});

const showHeader = ref(false);

nextTick(() => {
  showHeader.value = true;
});
</script>

<template>
  <Teleport v-if="showHeader" to="#app-header">
    <slot>
      <header class="flex h-10.5 w-full items-center py-[7px] sm:pl-5 pl-2">
        <div :class="['flex items-center gap-2', props.stretchLeft && 'flex-1']">
          <slot name="left-header" />
        </div>

        <div class="ml-auto flex items-center gap-2">
          <slot name="right-header" />
        </div>
      </header>
    </slot>
  </Teleport>
</template>