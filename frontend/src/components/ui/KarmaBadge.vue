<template>
  <!-- ✅ Username + Icon + Level з динамічним розміром -->
  <div
    class="inline-flex items-center rounded-full transition-all cursor-default"
    :class="[badgeClass, sizeClasses]"
    :style="badgeStyle"
    :title="`${username} • Карма: ${karma} • Рівень ${level}`"
  >
    <!-- Username -->
    <span :class="textSizeClasses.username">
      {{ username }}
    </span>
    
    <!-- ✅ Іконка залежно від рівня -->
    <span :class="textSizeClasses.icon">{{ levelIcon }}</span>
    
    <!-- Level -->
    <span :class="textSizeClasses.level">
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
  },
  // ✅ Новий пропс для розміру
  size: {
    type: String,
    default: 'md', // 'sm' | 'md' | 'lg'
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

// ✅ Класи розмірів для контейнера
const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'gap-1 px-2 py-0.5'  // Для карток/слайдера
    case 'lg':
      return 'gap-2 px-4 py-2'    // Для деталей
    case 'md':
    default:
      return 'gap-1.5 px-3 py-1.5' // Стандартний
  }
})

// ✅ Класи розмірів для тексту
const textSizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return {
        username: 'font-medium text-xs',
        icon: 'text-xs',
        level: 'text-[10px] font-semibold whitespace-nowrap'
      }
    case 'lg':
      return {
        username: 'font-semibold text-base',
        icon: 'text-base',
        level: 'text-sm font-bold whitespace-nowrap'
      }
    case 'md':
    default:
      return {
        username: 'font-medium text-sm',
        icon: 'text-sm',
        level: 'text-xs font-semibold whitespace-nowrap'
      }
  }
})

// Іконка залежно від рівня
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