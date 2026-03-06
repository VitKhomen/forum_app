<template>
  <!-- З посиланням на профіль -->
  <RouterLink
    v-if="linkable"
    :to="`/users/${username}`"
    class="inline-flex items-center rounded-full transition-all"
    :class="[badgeClass, sizeClasses]"
    :style="badgeStyle"
    :title="`${username} • Карма: ${karma} • Рівень ${level}`"
  >
    <span :class="textSizeClasses.username">{{ username }}</span>
    <span :class="textSizeClasses.icon">{{ levelIcon }}</span>
    <span :class="textSizeClasses.level">{{ level }} lvl</span>
  </RouterLink>

  <!-- Без посилання (оригінальний варіант) -->
  <div
    v-else
    class="inline-flex items-center rounded-full transition-all cursor-default"
    :class="[badgeClass, sizeClasses]"
    :style="badgeStyle"
    :title="`${username} • Карма: ${karma} • Рівень ${level}`"
  >
    <span :class="textSizeClasses.username">{{ username }}</span>
    <span :class="textSizeClasses.icon">{{ levelIcon }}</span>
    <span :class="textSizeClasses.level">{{ level }} lvl</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

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
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  // false = вимкнути посилання (напр. на своїй сторінці профілю)
  link: {
    type: Boolean,
    default: true
  }
})

// Показуємо посилання тільки якщо є username і link=true
const linkable = computed(() => props.link && !!props.username)

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm': return 'gap-1 px-2 py-0.5'
    case 'lg': return 'gap-2 px-4 py-2'
    default:   return 'gap-1.5 px-3 py-1.5'
  }
})

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
    default:
      return {
        username: 'font-medium text-sm',
        icon: 'text-sm',
        level: 'text-xs font-semibold whitespace-nowrap'
      }
  }
})

const levelIcon = computed(() => {
  const lvl = props.level
  if (lvl >= 10) return '👑'
  if (lvl >= 7)  return '🔥'
  if (lvl >= 5)  return '💎'
  if (lvl >= 3)  return '⭐'
  return '🌱'
})

const badgeClass = computed(() => {
  const lvl = props.level
  if (lvl >= 10) return 'text-white font-semibold shadow-md'
  if (lvl >= 7)  return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
  if (lvl >= 5)  return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
  if (lvl >= 3)  return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
  return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
})

const badgeStyle = computed(() => {
  if (props.level >= 10) {
    return { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }
  }
  return {}
})
</script>

<style scoped>
div, a {
  transition: all 0.2s ease;
}

div:hover, a:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
}
</style>