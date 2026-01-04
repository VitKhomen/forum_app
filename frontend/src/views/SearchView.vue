<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Пошук</h1>
    
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <input
        v-model="searchQuery"
        type="search"
        placeholder="Введіть запит для пошуку..."
        class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      
      <p class="text-gray-600 dark:text-gray-400 mt-4">
        Функція пошуку буде доступна незабаром...
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const searchQuery = ref('')
</script>