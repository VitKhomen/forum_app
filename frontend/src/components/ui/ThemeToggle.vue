<template>
  <button
    @click="toggleTheme"
    class="p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all duration-300"
    :aria-label="isDark ? 'Увімкнути світлу тему' : 'Увімкнути темну тему'"
    :title="isDark ? 'Світла тема' : 'Темна тема'"
  >
    <Transition name="theme-switch" mode="out-in">
      <SunIconSolid v-if="!isDark" key="sun" class="w-6 h-6" />
      <MoonIconSolid v-else key="moon" class="w-6 h-6" />
    </Transition>
  </button>
</template>

<script setup>
import { SunIcon as SunIconSolid, MoonIcon as MoonIconSolid } from '@heroicons/vue/24/solid'
import { useTheme } from '@/composables/useTheme'

const { isDark, toggleTheme } = useTheme()
</script>

<style scoped>
/* Плавна анімація зміни іконки */
.theme-switch-enter-active,
.theme-switch-leave-active {
  transition: all 0.4s ease;
  transform-origin: center;
}

.theme-switch-enter-from,
.theme-switch-leave-to {
  opacity: 0;
  transform: scale(0.8) rotate(-90deg);
}

.theme-switch-enter-to,
.theme-switch-leave-from {
  opacity: 1;
  transform: scale(1) rotate(0deg);
}
</style>