<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Редагувати пост</h1>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <p class="text-gray-600 dark:text-gray-400">Форма редагування поста буде доступна незабаром...</p>
      <RouterLink
        to="/profile/posts"
        class="inline-block mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Назад до постів
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>