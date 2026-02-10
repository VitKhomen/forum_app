<template>
  <!-- ✅ Username + Icon + Level в одному кольоровому овалі -->
  <div
    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all cursor-default"
    :class="badgeClass"
    :style="badgeStyle"
    :title="`${username} • Карма: ${karma} • Рівень ${level}`"
  >
    <!-- Username -->
    <span class="font-medium text-sm">
      {{ username }}
    </span>
    
    <!-- ✅ Іконка залежно від рівня -->
    <span class="text-sm">{{ levelIcon }}</span>
    
    <!-- Level -->
    <span class="text-xs font-semibold whitespace-nowrap">
      {{ level }} lvl
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  username: {
    type: String,
    required: true
  },
  karma: {
    type: Number,
    default: 0
  },
  level: {
    type: Number,
    default: 1
  }
})

// ✅ Іконка залежно від рівня
const levelIcon = computed(() => {
  const lvl = props.level
  
  if (lvl >= 10) {
    return '👑'  // Корона - легенда
  } else if (lvl >= 7) {
    return '🔥'  // Вогонь - експерт
  } else if (lvl >= 5) {
    return '💎'  // Діамант - досвідчений
  } else if (lvl >= 3) {
    return '⭐'  // Зірка - активний
  } else {
    return '🌱'  // Паросток - новачок
  }
})

// Колір залежно від рівня
const badgeClass = computed(() => {
  const lvl = props.level
  
  if (lvl >= 10) {
    return 'text-white font-semibold shadow-md'
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
div {
  transition: all 0.2s ease;
}

div:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
}
</style>