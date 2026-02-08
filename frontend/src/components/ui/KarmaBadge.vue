<template>
  <span 
    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
    :class="badgeClass"
    :style="badgeStyle"
    :title="`Карма: ${karma}`"
  >
    {{ level }} lvl
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  karma: {
    type: Number,
    default: 0
  },
  level: {
    type: Number,
    default: 1
  }
})

// Колір залежно від рівня
const badgeClass = computed(() => {
  const lvl = props.level
  
  // Для високих рівнів використовуємо градієнт
  if (lvl >= 10) {
    return 'text-white font-semibold shadow-sm'
  } else if (lvl >= 7) {
    return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
  } else if (lvl >= 5) {
    return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
  } else if (lvl >= 3) {
    return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
  } else {
    return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
  }
})

// Градієнт для високих рівнів
const badgeStyle = computed(() => {
  if (props.level >= 10) {
    return {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }
  }
  return {}
})
</script>

<style scoped>
span {
  transition: all 0.2s ease;
}

span:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
}
</style>