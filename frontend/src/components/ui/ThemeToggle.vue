<template>
  <button
    @click="handleClick"
    class="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
    :title="currentTheme === 'dark' ? 'Світла тема' : 'Темна тема'"
  >
    {{ currentTheme === 'dark' ? '🌙' : '☀️' }}
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const currentTheme = computed(() => themeStore.currentTheme)

const handleClick = () => {
  console.log('🖱️ Button clicked') // ✅ DEBUG
  console.log('Current theme before toggle:', currentTheme.value) // ✅ DEBUG
  themeStore.toggleTheme()
  console.log('Current theme after toggle:', themeStore.currentTheme) // ✅ DEBUG
}
</script>