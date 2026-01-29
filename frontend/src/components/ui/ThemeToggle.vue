<template>
  <button
    @click="toggleTheme"
    class="p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all duration-300"
    :aria-label="isDark ? 'Увімкнути світлу тему' : 'Увімкнути темну тему'"
    :title="isDark ? 'Світла тема' : 'Темна тема'"
  >
    <!-- Іконка сонця (світла тема) -->
    <Transition name="fade" mode="out-in">
      <SunIcon v-if="!isDark" key="sun" class="w-6 h-6 transition-transform hover:rotate-180 duration-500" />
      <!-- Іконка місяця (темна тема) -->
      <MoonIcon v-else key="moon" class="w-6 h-6 transition-transform hover:-rotate-12 duration-300" />
    </Transition>
  </button>
</template>

<script setup>
import { SunIcon, MoonIcon } from '@heroicons/vue/24/outline'
import { useTheme } from '@/composables/useTheme'

const { isDark, toggleTheme } = useTheme()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>