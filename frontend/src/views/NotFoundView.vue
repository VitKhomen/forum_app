<template>
  <div class="text-center py-12">
    <div class="mb-8">
      <h1 class="text-9xl font-bold text-gray-900 dark:text-white mb-4">404</h1>
      <p class="text-2xl text-gray-600 dark:text-gray-400 mb-2">Сторінка не знайдена</p>
      <p class="text-gray-500 dark:text-gray-500">
        Вибачте, але сторінка, яку ви шукаєте, не існує
      </p>
    </div>
    
    <RouterLink
      to="/"
      class="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition font-medium"
    >
      Повернутися на головну
    </RouterLink>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>